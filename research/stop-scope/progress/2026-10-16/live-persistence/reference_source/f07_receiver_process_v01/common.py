"""Small IPC and journal primitives; no model/provider imports."""
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def require(value, message):
    if not value:
        raise ValueError(message)


class Journal:
    def __init__(self, path, actor):
        self.file = Path(path).open('x')
        self.actor, self.instance = actor, str(uuid.uuid4())
        self.seq, self.lock = 0, threading.RLock()

    def emit(self, kind, **fields):
        with self.lock:
            require(not set(fields).intersection({'seq','pid','instance','actor','monotonic_ns','kind'}), 'Reserved journal field')
            self.seq += 1
            row = dict(seq=self.seq, pid=os.getpid(), instance=self.instance,
                       actor=self.actor, monotonic_ns=time.monotonic_ns(), kind=kind, **fields)
            self.file.write(json.dumps(row, ensure_ascii=False)+'\n'); self.file.flush()
            return row

    def close(self):
        self.file.close()


def offline():
    """Children only use inherited local pipes; prevent new network/process use."""
    def guard(event, args):
        if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo', 'subprocess.Popen',
                     'os.system', 'os.exec', 'os.posix_spawn'}:
            raise PermissionError('Receiver qualification is provider-free and offline')
    sys.addaudithook(guard)


def call(conn, journal, action, **fields):
    rid = str(uuid.uuid4())
    request = dict(rpc_id=rid, action=action, **fields)
    journal.emit('rpc_sent', request=request)
    conn.send(request)
    require(conn.poll(10), 'RPC reply timeout: '+action)
    reply = conn.recv()
    journal.emit('rpc_returned', rpc_id=rid, reply=reply)
    require(reply['rpc_id'] == rid, 'RPC identity mismatch')
    require(reply.get('ok'), 'RPC failure: '+str(reply))
    return reply
