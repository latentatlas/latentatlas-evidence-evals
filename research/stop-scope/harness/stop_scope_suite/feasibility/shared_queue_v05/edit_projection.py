"""Counterfactual candidate from request-time bytes; never a delivered effect."""
import hashlib
from deepagents.backends.utils import perform_string_replacement


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None


def project_edit(content,args):
    if content is None:
        return {"status":"missing_file","candidate_content":None,"candidate_sha256":None,"occurrences":0}
    # The pinned FilesystemBackend.edit reads in universal-newline text mode
    # and normalizes the supplied old/new strings before native replacement.
    normalize=lambda s:s.replace("\r\n","\n").replace("\r","\n")
    result=perform_string_replacement(normalize(content),normalize(args["old_string"]),
                                      normalize(args["new_string"]),args.get("replace_all",False))
    if isinstance(result,str):
        return {"status":"replacement_not_applicable","error":result,"candidate_content":None,
                "candidate_sha256":None,"occurrences":0}
    candidate,count=result
    return {"status":"projected","candidate_content":candidate,"candidate_sha256":sha(candidate),"occurrences":count}
