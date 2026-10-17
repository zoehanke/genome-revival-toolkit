"""Test-only socket guard. Every attempted connection is counted and fails."""
import json
from pathlib import Path
import runpy
import socket
import sys

audit=Path(sys.argv[1]);entry=sys.argv[2];arguments=sys.argv[3:];attempts=[]
def blocked(*args,**kwargs):
    attempts.append('connection_attempt')
    raise RuntimeError('Network blocked by S1 test')
socket.socket.connect=blocked
socket.socket.connect_ex=blocked
socket.create_connection=blocked
socket.getaddrinfo=blocked
try:
    if entry=='probe':
        socket.create_connection(('127.0.0.1',9))
    else:
        sys.argv=[entry,*arguments]
        runpy.run_path(entry,run_name='__main__')
finally:
    audit.write_text(json.dumps({'attempts':len(attempts)})+'\n',encoding='utf-8',newline='\n')
