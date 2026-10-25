"""Read actual store bytes in a separate process, never receiver decisions."""
import hashlib
import os
from pathlib import Path
from common import Journal, offline


def main(conn, root, log_path):
    offline()
    log=Journal(log_path,'observer')
    log.emit('observer_started')
    conn.send(dict(ready=True,pid=os.getpid(),observer_instance=log.instance))
    try:
        while True:
            request=conn.recv()
            if request['action']=='close':
                log.emit('observer_closed'); conn.send(dict(closed=True)); return
            if request['action']!='snapshot': raise ValueError('Unknown observer action')
            files=[]
            for path in sorted(Path(root).rglob('*')):
                if path.is_symlink(): raise ValueError('Unexpected symlink')
                if not path.is_file(): continue
                data=path.read_bytes()
                files.append(dict(path=str(path.relative_to(root)),bytes=len(data),
                                  sha256=hashlib.sha256(data).hexdigest(),content=data.decode()))
            row=log.emit('snapshot',label=request['label'],files=files,request_id=request['request_id'])
            conn.send(row)
    finally: conn.close(); log.close()
