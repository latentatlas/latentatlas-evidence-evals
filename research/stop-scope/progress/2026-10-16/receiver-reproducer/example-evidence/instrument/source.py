"""Programmed publisher: acceptance is acknowledged before work is done."""
import os
from common import Journal, call, offline, require


def main(receiver, owner, log_path, op, holds):
    offline()
    log=Journal(log_path,'source')
    try:
        log.emit('source_started')
        receipt=call(receiver,log,'submit',op=op,holds=holds)
        require(receipt['status']=='accepted','Source submission rejected')
        log.emit('acceptance_received',receipt=receipt)
        owner.send(dict(accepted=True,receipt=receipt,pid=os.getpid()))
        command=owner.recv()
        require(command=={'finish':True},'Unexpected source command')
        log.emit('source_finished')
    finally:
        receiver.close(); owner.close(); log.close()
