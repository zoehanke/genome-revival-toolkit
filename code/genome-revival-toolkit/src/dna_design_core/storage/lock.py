"""Single-writer OS lock. Process exit releases it; no stale-lock takeover."""
import os
from pathlib import Path
from dna_design_core.kernel.errors import ToolkitError


class RunLock:
    def __init__(self,root):self.path=Path(root)/'run.lock';self.stream=None

    def __enter__(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.stream=self.path.open('a+b')
        if self.path.stat().st_size==0:self.stream.write(b'0');self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error:
            self.stream.close();self.stream=None
            raise ToolkitError('RUN_LOCKED') from error
        return self

    def __exit__(self,*exc):
        if self.stream is not None:self.stream.close();self.stream=None
