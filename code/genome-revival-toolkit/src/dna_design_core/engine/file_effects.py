"""Observe synchronous Python filesystem writes, then qualify after the call.

This is not a sandbox: observed operations have already run. Native/child-
process I/O outside the registered files is not globally monitored.
PROVISIONAL(C19): synchronous Python write observation plus known-file hash
readback is the v1 boundary; arbitrary reads and detached I/O remain uncovered.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import os
from pathlib import Path
import sys

from dna_design_core.kernel import ids

_ACTIVE=ContextVar('capability_file_effects',default=None)
_WRITE_FLAGS=os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND


def _path(value):
    if not isinstance(value,(str,bytes,os.PathLike)):return None
    return Path(os.fsdecode(value)).resolve()


def _observe(event,args):
    guard=_ACTIVE.get()
    if guard is None or not guard.enabled:return
    paths=()
    if event=='open':
        mode=args[1] or '';flags=args[2] if len(args)>2 else 0
        if any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&_WRITE_FLAGS:paths=args[:1]
    elif event in {'os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate','os.utime'}:paths=args[:1]
    elif event=='os.rename':paths=args[:2]
    elif event in {'os.link','os.symlink'}:paths=args[1:2]
    for value in paths:
        try:path=_path(value)
        except (OSError,TypeError,ValueError):
            guard.violations.append('unresolved file write intent');continue
        if path is not None and (not guard.writes_files or not path.is_relative_to(guard.workdir)):
            guard.violations.append('out-of-scope file write intent')


sys.addaudithook(_observe)


@contextmanager
def broker_io():
    """Nested Invoker bookkeeping is trusted; its capability body gets a guard.

    Keep the parent object so a child violation propagates even when user code
    catches that child's exception. Do not mask arbitrary capability code.
    """
    guard=_ACTIVE.get();previous=guard.enabled if guard is not None else None
    if guard is not None:guard.enabled=False
    try:yield
    finally:
        if guard is not None:guard.enabled=previous


def _files(directory):
    return {p:ids.file_sha256(p.read_bytes()) for p in Path(directory).rglob('*') if p.is_file()}


class FileEffects:
    """The existing work/input/store readback guard plus write observation."""
    def __init__(self,root,workdir,writes_files,*,candidate=None,artifacts=()):
        self.workdir=Path(workdir).resolve();self.writes_files=writes_files
        self.enabled=True;self.violations=[];self.parent=None
        self.before=_files(self.workdir)
        self.protected={p:d for name in ('inputs','store') for p,d in _files(Path(root)/name).items()}
        if candidate:self.protected.update(_files(candidate))
        self.protected.update({Path(p):ids.file_sha256(Path(p).read_bytes()) for p in artifacts})

    def __enter__(self):
        self.parent=_ACTIVE.get();self.token=_ACTIVE.set(self)
        # Interpreter cache files are not capability outputs. Suppress their
        # creation during loading AND lazy imports without exempting any path.
        self.bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
        return self

    def __exit__(self,kind,value,traceback):
        # This runs after ordinary returns AND exceptions. No rollback or
        # false claim that the operating system prevented the operation.
        self.enabled=False
        try:
            if not self.writes_files and _files(self.workdir)!=self.before:self.violations.append('undeclared work file change')
            for path,digest in self.protected.items():
                if not path.is_file() or ids.file_sha256(path.read_bytes())!=digest:
                    self.violations.append('protected file changed')
        except OSError:self.violations.append('protected file could not be re-read')
        finally:
            sys.dont_write_bytecode=self.bytecode
            _ACTIVE.reset(self.token)
            if self.parent is not None:self.parent.violations.extend(self.violations)
        return False
