"""Trusted lifecycle supervisor stays offline; only the source may call the provider."""
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import traceback
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from bridge_dependencies import common, durable, observer
from source_driver import main as source_main

Journal, require, save, call = common.Journal, common.require, common.save, common.call


def main(out):
    # No model runs here. Child targets are fixed below, never supplied by a task.
    def no_network(event,args):
        if event in {"socket.connect","socket.bind","socket.getaddrinfo"}:
            raise PermissionError("Persistent bridge supervisor is offline")
    sys.addaudithook(no_network)
    api_key = os.environ.pop("STOP_SCOPE_API_KEY", None)
    plan = json.loads((out/"PLAN.json").read_text())
    log = Journal(out/"supervisor.jsonl","supervisor")
    ctx = mp.get_context("spawn")
    processes, connections = {}, []
    epoch, receiver_conn, error, completed = 0, None, None, False
    source_conn, source_child = ctx.Pipe()
    observer_conn, observer_child = ctx.Pipe()
    connections += [source_conn,source_child,observer_conn,observer_child]

    def start_receiver():
        nonlocal receiver_conn, epoch
        epoch += 1
        parent,child = ctx.Pipe()
        connections.extend((parent,child))
        p=ctx.Process(target=durable.main,args=(child,out/"files",out/"queue.sqlite3",
            out/f"receiver-{epoch}.jsonl",plan["fault"]),name=f"persistent-receiver-{epoch}")
        processes[f"receiver-{epoch}"]=p
        p.start(); child.close()
        require(parent.poll(20),"Receiver startup timeout")
        ready=parent.recv()
        require(ready.get("ready"),"Receiver not ready")
        receiver_conn=parent
        log.emit("receiver_ready",epoch=epoch,receipt=ready)
        return ready

    def close_receiver():
        reply=call(receiver_conn,log,"close")
        p=processes[f"receiver-{epoch}"]
        p.join(10)
        require(not p.is_alive() and p.exitcode==0,"Unclean receiver closure")
        log.emit("receiver_reaped",epoch=epoch,child_pid=p.pid,exit_code=p.exitcode,receipt=reply)
        receiver_conn.close()
        return reply

    def snapshot(label,rid=None):
        rid=rid or str(uuid.uuid4())
        log.emit("observer_requested",label=label,request_id=rid)
        observer_conn.send(dict(action="snapshot",label=label,request_id=rid))
        require(observer_conn.poll(10),"Observer timeout")
        row=observer_conn.recv()
        require(row["request_id"]==rid and row["label"]==label,"Observer identity mismatch")
        log.emit("observer_returned",observation=row)
        return row

    try:
        p=ctx.Process(target=observer.main,args=(observer_child,out/"files",out/"observer.jsonl"),name="disk-observer")
        processes["observer"]=p; p.start(); observer_child.close()
        require(observer_conn.poll(10),"Observer startup timeout")
        log.emit("observer_ready",receipt=observer_conn.recv())
        first=start_receiver()
        p=ctx.Process(target=source_main,args=(out,source_child,api_key),name="openswe-source")
        processes["source"]=p; p.start(); source_child.close()
        log.emit("source_ready",child_pid=p.pid)
        while True:
            if not source_conn.poll(.2):
                require(processes["source"].is_alive(),"Source exited before source_done")
                continue
            q=source_conn.recv()
            log.emit("source_rpc_received",request=q,epoch=epoch)
            special=q["action"] in {"snapshot","restart","source_done"}
            if q["action"]=="restart":
                require(epoch==1,"Only one declared restart")
                before=call(receiver_conn,log,"status")
                require(set(q["targets"])=={"O","I"},"Restart target inventory")
                for role,op in q["targets"].items():
                    state=before["jobs"][op["operation_id"]]
                    require(state["role"]==role and state["state"]=="queued" and not state["done"],
                            "Restart target not queued")
                log.emit("before_restart_status",receipt=before,targets=q["targets"])
                snapshot("before_restart")
                close_receiver()
                (out/"queue-before-restart.sqlite3").write_bytes((out/"queue.sqlite3").read_bytes())
                save(out/"DATABASE_BEFORE_RESTART.json",durable.inspect_database(out/"queue-before-restart.sqlite3"))
                second=start_receiver()
                require(first["pid"]!=second["pid"] and first["instance"]!=second["instance"]
                    and first["database_id"]==second["database_id"],"Receiver recovery identity mismatch")
                after=call(receiver_conn,log,"status")
                log.emit("after_restart_status",receipt=after)
                snapshot("after_restart_before_execution")
                reply=dict(ok=True,before=before,after=after,receiver=second,restarted=True)
            elif q["action"]=="snapshot":
                reply=dict(ok=True,observation=snapshot(q["label"],q["rpc_id"]))
            elif q["action"]=="source_done":
                completed=q["completed"] is True
                reply=dict(ok=True,completed=completed)
            else:
                require(q["action"] in {"register","submit","execute","control","status"},"Unpermitted source RPC")
                # Forward exact IDs and payloads. Reconnection never invents a new job.
                log.emit("rpc_sent",request=q)
                receiver_conn.send(q)
                require(receiver_conn.poll(15),"Receiver RPC timeout")
                reply=receiver_conn.recv()
                log.emit("rpc_returned",rpc_id=q["rpc_id"],reply=reply)
                require(reply["rpc_id"]==q["rpc_id"],"Forwarded RPC identity changed")
            if special:
                reply.update(rpc_id=q["rpc_id"],supervisor_pid=os.getpid(),supervisor_instance=log.instance)
            log.emit("source_rpc_replied",rpc_id=q["rpc_id"],reply=reply,epoch=epoch)
            source_conn.send(reply)
            if q["action"]=="source_done": break
        processes["source"].join(10)
        require(not processes["source"].is_alive() and processes["source"].exitcode==0,"Source not cleanly closed")
        close_receiver()
        save(out/"DATABASE_FINAL.json",durable.inspect_database(out/"queue.sqlite3"))
        observer_conn.send(dict(action="close"))
        require(observer_conn.poll(10) and observer_conn.recv().get("closed"),"Observer not closed")
        processes["observer"].join(10)
        require(not processes["observer"].is_alive() and processes["observer"].exitcode==0,"Observer not reaped")
    except BaseException as exc:
        error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        log.emit("supervisor_error",error=error)
    finally:
        cleanup=[]
        for name,p in processes.items():
            if p.is_alive(): p.terminate(); p.join(5); cleanup.append(dict(process=name,action="terminate"))
            if p.is_alive(): p.kill(); p.join(5); cleanup.append(dict(process=name,action="kill"))
        status={name:dict(pid=p.pid,exit_code=p.exitcode,reaped=not p.is_alive()) for name,p in processes.items()}
        status.update(supervisor_pid=os.getpid(),episode_error=error,cleanup_actions=cleanup,completed=completed)
        save(out/"CHILD_PROCESSES.json",status)
        for conn in connections: conn.close()
        log.emit("supervisor_closed",completed=completed,error=error)
        log.close()
    return 0 if completed and error is None else 1


if __name__=="__main__":
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
