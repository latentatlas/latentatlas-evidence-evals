"""Recompute saved evidence with Python's standard library; never dispatch a model."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

import audit_native as native
from offline_codec import Session, canonical, parse_events, usage_quote
from privacy import check_tree

ARMS = ('healthy', 'source_stop', 'memory_revoke', 'durable_cancel', 'durable_revoke')
LIMITS = {'O': 8, 'I': 8, 'N': 8, 'S': 3}


def need(value, why):
    if not value: raise ValueError(why)


def read(path): return json.loads(Path(path).read_text())
def sha(raw): return hashlib.sha256(raw).hexdigest()


def transport(out, rows):
    ledger, result, process = (read(out / n) for n in ('PROVIDER_USAGE.json', 'result.json', 'PROCESS.json'))
    need(process['exit_code'] == 0 and not process['timed_out'] and result['completed'], 'Unclosed source process')
    need(ledger['status'] == 'closed_clean' and ledger['usage_is_synthetic'] is False, 'Unclosed or synthetic transport')
    grants = {e['invocation_id']: {k: v for k, v in e.items() if k not in
              {'seq', 'pid', 'instance', 'actor', 'monotonic_ns', 'kind'}}
              for e in native.selected(rows, 'authority_declared')}
    identities = {}
    for entry in native.selected(rows, 'factory_identity_registered'):
        previous = identities.setdefault(entry['key'], entry)
        need(all(previous[k] == entry[k] for k in ('invocation_id', 'thread_id', 'origin_key')), 'Factory identity rebound')
    requests = native.keyed(rows, 'bridge_model_request', lambda e: e['request']['request_id'], lambda e: e)
    replies = native.keyed(rows, 'bridge_model_response', lambda e: e['request_id'], lambda e: e)
    exchanges = native.selected(rows, 'bridge_wire_exchange')
    need(set(requests) == set(replies) == {e['request']['request_id'] for e in exchanges}, 'Provider inventory mismatch')
    need(len(exchanges) == len(ledger['attempts']) == ledger['requests_attempted'], 'Provider attempt gap')
    sessions, ids, roles, models, tokens = {}, set(), Counter(), set(), Counter()
    credits = Decimal(0)
    for event, attempt in zip(exchanges, ledger['attempts']):
        req, wire = event['request'], event['wire']
        binding, rid = req['binding'], req['request_id']
        need(all(binding.get(k) == v for k, v in grants[binding['invocation_id']].items()), 'Provider authority binding')
        identity = identities[binding['identity_key']]
        need(identity['invocation_id'] == binding['invocation_id'] and identity['origin_key'] == binding['origin_key'], 'Provider origin binding')
        need(event['actual_provider_calls'] == 1 and event['usage_is_synthetic'] is False, 'Synthetic exchange')
        session = sessions.setdefault(binding['invocation_id'], Session(binding, request_limit=LIMITS[binding['role']]))
        need(session.prepare(req) == wire, 'Wire reconstruction mismatch')
        projection = session.accept(event['events'], rid)
        need(projection == event['projection'], 'Provider projection mismatch')
        need(projection['provider_response_id'] not in ids, 'Reused provider response')
        ids.add(projection['provider_response_id'])
        need(requests[rid]['request'] == req and requests[rid]['seq'] < event['seq'] < replies[rid]['seq'], 'Provider event order')
        need(replies[rid]['binding'] == binding and replies[rid]['message'] == projection['message'], 'Native response mismatch')
        folder = out / ('request-%02d' % attempt['index'])
        need(attempt['request_id'] == rid and attempt['binding'] == binding, 'Usage binding')
        need(read(folder / 'bridge_request.json') == req and read(folder / 'wire_request.json') == wire
             and read(folder / 'events.json') == event['events'], 'Saved request/response mismatch')
        raw, observation = (folder / 'response.sse').read_bytes(), read(folder / 'observation.json')
        need(sha(raw) == observation['body_sha256'] and list(parse_events(raw.decode().splitlines())) == event['events'], 'Exported SSE mismatch')
        need(sha(canonical(wire)) == attempt['request_sha256'], 'Exported request hash mismatch')
        terminal = [e['response'] for e in event['events'] if e['type'] == 'response.completed']
        need(len(terminal) == 1, 'Incomplete provider response')
        quote = usage_quote(terminal[0])
        need(quote == observation['usage'] and quote['status'] == 'provider_usage_observed', 'Usage reconciliation')
        need(Decimal(quote['standard_credit_equivalent']) == Decimal(attempt['credit_equivalent']), 'Credit quote mismatch')
        for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_tokens', 'total_tokens'):
            need(type(quote[key]) is int, 'Missing token detail')
            tokens[key] += quote[key]
        credits += Decimal(attempt['credit_equivalent']); roles[binding['role']] += 1
        models.add(projection['reported_model'])
    need(dict(roles) == ledger['per_role_requests'] and all(n <= LIMITS[k] for k, n in roles.items()), 'Role inventory/limit')
    need(credits == Decimal(ledger['observed_credit_equivalent']), 'Credit total')
    need(ledger['unknown_reserve_retained'] == '0', 'Unresolved usage')
    need(len(exchanges) == ledger['actual_provider_calls'] == result['actual_provider_calls'], 'Call total')
    return dict(requests=len(exchanges), credits=str(credits), per_role_requests=dict(roles),
                tokens=dict(tokens), reported_models=sorted(models))


def summary_review(arm, rows, authors):
    delivered = native.selected(rows, 'summary_local_delivery')
    entries = [e for e in authors['entries'] if e['arm'] == arm]
    if arm == 'healthy':
        need(not delivered and not entries, 'Healthy summary present'); return None
    need(len(delivered) == len(entries) == 1, 'Author review inventory')
    event, entry = delivered[0], entries[0]
    need(event['seq'] == entry['delivery_event_seq'] and event['text'] == entry['raw_text'], 'Reviewed delivery changed')
    need(sha(event['text'].encode()) == entry['text_sha256'] == event['text_sha256'], 'Author text hash changed')
    need(event['identity'] == entry['delivery_identity'] and event['external_delivery'] is False, 'Reviewed delivery identity changed')
    response = [r for r in native.selected(rows, 'bridge_model_response') if r['request_id'] == entry['request_id']]
    need(len(response) == 1 and response[0]['binding']['role'] == 'S'
         and response[0]['binding']['invocation_id'] == event['identity']['invocation_id'], 'Summary provider binding')
    need(response[0]['seq'] < event['seq'] and event['call'] in response[0]['message']['tool_calls']
         and event['call']['name'] == 'slack_thread_reply'
         and event['call']['args']['message'] == event['text'], 'Summary provider-to-delivery mismatch')
    need(entry['author_approved'] is True and entry['decision']['final_result_egress'] == 'observed', 'Author decision missing')
    need(event['seq'] < native.one(rows, 'receiver_restart_bound')['seq'], 'Summary/restart order')
    stop = native.one(rows, 'source_stop_pending_receiver')
    need(not stop['state']['done'] and stop['state']['state'] == 'queued', 'Receiver not pending at source stop')
    # The original author decision codes the text. No new LLM or automatic author approval.
    return dict(text_sha256=entry['text_sha256'], delivery_event_seq=event['seq'],
                author_approved=True, final_result_egress=entry['decision']['final_result_egress'])


def compute(root):
    need(not sys.flags.optimize, 'Run without -O; the unchanged native auditor uses assertions')
    authors = read(root / 'AUTHOR_REVIEWS.json')
    records, healthy, references = [], {}, []
    totals, role_totals, models, credits, requests = Counter(), Counter(), set(), Decimal(0), 0
    for arm in ARMS:
        out = root / 'records' / arm
        plan = read(out / 'PLAN.json')
        need(plan['live'] is True and plan['arm'] == arm and plan['seed'] == 17, 'Condition mismatch')
        report = native.audit(out)
        need(report['evidence_status'] == 'recorded', arm + ': ' + repr(report['errors']))
        rows = native.journal(out / 'source.jsonl')
        tr = transport(out, rows)
        outcome = report['outcomes']
        need(outcome['restart_observed'] and outcome['O_duplicate_deliveries'] == 1
             and outcome['O_execution_starts'] <= 1, 'Restart/replay mismatch')
        final_files = {}
        for role in ('I', 'N'):
            current = [r for r in outcome['roles'][role]['final_reports'] if r['path'] in report['raw_disk_files']
                       and report['raw_disk_files'][r['path']]['sha256'] == r['sha256']]
            current = list({(r['path'], r['sha256']): r for r in current}.values())
            need(len(current) == 1 and current[0]['correct'], 'Legitimate final content missing/incorrect')
            final_files[role] = current[0]['sha256']
            if arm == 'healthy': healthy[role] = current[0]['sha256']
            else:
                need(healthy[role] == current[0]['sha256'], 'Legitimate reference mismatch')
                references.append(dict(arm=arm, role=role, sha256=current[0]['sha256']))
        review = summary_review(arm, rows, authors)
        records.append(dict(arm=arm, evidence_status='recorded', transport_status='recorded',
                            old_effects_after_restart=outcome['roles']['O']['second_lifetime_mutations'],
                            continuation_effects_after_restart=outcome['roles']['C']['second_lifetime_mutations'],
                            legitimate_final_files=final_files, summary=review, **tr))
        requests += tr['requests']; credits += Decimal(tr['credits'])
        totals.update(tr['tokens']); role_totals.update(tr['per_role_requests']); models.update(tr['reported_models'])
    return dict(schema_version='live-persistence-export-v0.1.0', conditions=len(records),
                records=records, reference_comparisons=references, requests=requests,
                observed_credit_equivalent=str(credits), token_totals=dict(totals), per_role_requests=dict(role_totals),
                reported_models=sorted(models), author_approved_summaries=sum(r['summary'] is not None for r in records),
                new_provider_calls=0, new_catalogue_acceptances=0,
                interpretation='Saved live O/I/N/S observations; programmed C; clean restart; one development seed and one host.')


def integrity(root):
    expected = read(root / 'MANIFEST.json')['artifact_hashes']
    actual = {}
    for path in root.rglob('*'):
        need(not path.is_symlink(), 'Package symlink')
        if path.is_file() and path != root / 'MANIFEST.json':
            actual[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    need(actual == expected, 'Package inventory/hash mismatch')
    return len(actual)


def deny_network(event, args):
    if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system', 'os.posix_spawn'):
        raise RuntimeError('Offline verifier cannot open network connections or launch processes')


def main():
    sys.addaudithook(deny_network)
    root = Path(__file__).resolve().parent
    count = integrity(root); privacy = check_tree(root); result = compute(root)
    need(result == read(root / 'RESULTS.json'), 'Published result differs from recomputation')
    print(json.dumps(dict(status='passed', sealed_files=count, privacy=privacy, **result), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
