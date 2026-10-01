"""Generate a report from all planned evidence, retaining failed contracts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import audit_study
from run_matrix import plan

ROOT=Path(__file__).resolve().parent
OUTCOMES=['R_request_no_old_final_effect','V_withdrawal_no_old_native_start','C_quiescent_confirmation',
          'F_source_summary_verified_readout','F_old_completion_verified_readout',
          'F_source_summary_artifact_status_accuracy','F_old_completion_artifact_status_accuracy',
          'F_new_human_verified_readout','F_new_completion_verified_readout','F_independent_verified_readout',
          'F_new_human_both_artifacts','F_new_completion_both_artifacts','F_independent_both_artifacts',
          'duplicate_delivery_no_new_admission']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    with p.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--matrix',required=True);p.add_argument('--report-id',required=True);p.add_argument('--qa-id',required=True)
    p.add_argument('--delivery-counterexample',required=True)
    a=p.parse_args()
    if not all(re.fullmatch(r'[a-z][a-z0-9_-]{1,100}',v) for v in [a.matrix,a.report_id,a.qa_id,a.delivery_counterexample]):raise ValueError('Unsafe report identifier')
    target=ROOT/'reports'/a.report_id
    if target.exists():raise FileExistsError(target)
    matrix=ROOT/'matrices'/a.matrix
    frozen=json.loads((matrix/'PLAN.json').read_text())
    expected=plan(a.matrix)
    if frozen['cells']!=expected:raise RuntimeError('Frozen plan does not cover canonical26cells')
    executions=[json.loads(line) for line in (matrix/'EXECUTIONS.jsonl').read_text().splitlines()]
    if [r['run_id'] for r in executions]!=[r['run_id'] for r in expected]:raise RuntimeError('Missing/extra/reordered planned execution')
    if sha(ROOT/'PROTOCOL.md')!=frozen['protocol_sha256']:raise RuntimeError('Protocol changed during matrix')
    for n,h in frozen['source_sha256'].items():
        if sha(ROOT/n)!=h:raise RuntimeError('Frozen matrix code changed: '+n)
    qa_file=ROOT/'qa'/f'{a.qa_id}.json';qa=json.loads(qa_file.read_text())
    if qa['exit_code']!=0 or not qa['source_unchanged'] or qa['timeout'] or not qa.get('record_unchanged'):raise RuntimeError('Full unit/negative QA did not pass')
    record=ROOT/'runs'/expected[0]['run_id']
    if not qa.get('artifact_record') or Path(qa['artifact_record']).resolve()!=record.resolve():raise RuntimeError('Mutation QA must use first canonical baseline record')
    if 'skipped=' in qa.get('stderr',''):raise RuntimeError('Full QA cannot skip artifact tests')
    if {str(f.relative_to(record)):sha(f) for f in record.rglob('*') if f.is_file()}!=qa['record_sha256']:raise RuntimeError('Mutation QA source record changed')
    for n,h in qa['source_sha256'].items():
        if sha(ROOT/n)!=h:raise RuntimeError('Code changed after QA: '+n)
    rows=[];provenance=[];input_hashes={};invalid=[]
    fault_dir=ROOT/'runs'/a.delivery_counterexample
    fault=audit_study.audit_run(fault_dir,ROOT.parent/'application_probe/upstream')
    fault_manifest=json.loads((fault_dir/'manifest.json').read_text())
    if fault_manifest.get('receipt_fault')!='bypass':raise RuntimeError('Counterexample must be an explicit injected receipt fault, not selected natural outcome')
    for n in ['run_probe.py','child_probe.py','factory_support.py','workload.py','PROTOCOL.md']:
        if fault_manifest['source_sha256'][n]!=sha(ROOT/n):raise RuntimeError('Diagnostic instrumentation differs: '+n)
    if not fault['evidence_valid'] or fault['outcomes']['duplicate_delivery_no_new_admission']['status']!='fail':
        raise RuntimeError('Injected-duplicate detector calibration did not retain a valid failed outcome')
    for cell in expected:
        directory=ROOT/'runs'/cell['run_id']
        audit=audit_study.audit_run(directory,ROOT.parent/'application_probe/upstream')
        rows.append({'cell':cell,'audit':audit})
        if not audit['evidence_valid']:invalid.append({'run_id':cell['run_id'],'errors':audit['evidence_errors']})
        manifest=json.loads((directory/'manifest.json').read_text())
        if manifest.get('receipt_fault','none')!='none':raise RuntimeError('Injected fault cannot enter normal matrix')
        for n in ['run_probe.py','child_probe.py','factory_support.py','workload.py','PROTOCOL.md']:
            if manifest['source_sha256'][n]!=sha(ROOT/n):raise RuntimeError('Experiment instrumentation differs: '+cell['run_id']+'/'+n)
        for job in ['old','human','new_background','independent']:
            matches=list((directory/'files').rglob(f'incident-{job}.json'))
            if len(matches)!=1:
                invalid.append({'run_id':cell['run_id'],'errors':['missing or ambiguous source '+job]});continue
            pair=f"{cell['seed']}:{job}";digest=sha(matches[0])
            if pair in input_hashes and input_hashes[pair]!=digest:raise RuntimeError('Paired input byte mismatch')
            input_hashes[pair]=digest
        provenance.append({'run_id':cell['run_id'],'input_sha256':{n:sha(directory/n) for n in ['manifest.json','PROCESS.json','events.jsonl','result.json']}})
    target.mkdir(parents=True,exist_ok=False);(target/'audits').mkdir()
    save(target/'audits'/f'{a.delivery_counterexample}.json',fault)
    for row in rows:save(target/'audits'/f"{row['cell']['run_id']}.json",row['audit'])
    # Broken measurements remain visible; they cannot be converted into pass/fail.
    if invalid:
        save(target/'INCOMPLETE.json',{'invalid':invalid,'planned_cells':26,'evaluated_cells':len(rows)})
        print(json.dumps({'status':'incomplete','invalid_cells':len(invalid),'report':str(target)}));return 1
    totals=Counter()
    for row in rows:totals.update(row['audit']['counts'])
    counts=dict(totals)
    artifact_summary={};artifact_table=[]
    for role in ['source_summary','old_completion']:
        invocations=[item for row in rows for item in row['audit']['invocations'] if item['role']==role]
        claims=[claim for item in invocations for claim in item['artifact_claims'].values()]
        states=dict(Counter(c['observation'] for c in claims))
        truthful=sum(c['claim_correct'] is True for c in claims)
        terminals=sum(item['terminal_verified'] is True for item in invocations)
        artifact_summary[role]={'invocations':len(invocations),'verified_terminals':terminals,'claims':len(claims),
                                'correct_claims':truthful,'incorrect_claims':len(claims)-truthful,'observation_states':states}
        artifact_table.append(f'| {role} | {terminals}/{len(invocations)} | {truthful}/{len(claims)} | {len(claims)-truthful} | {states.get("verified",0)} | {states.get("observed_missing",0)} | {states.get("unverified",0)} |')
    overlap=sum(r['audit']['costs'].get('independent_native_work_overlapped_initial_worker') is True for r in rows)
    grouped=[];table=[];cost_table=[]
    for schedule in ['accepted_precommit','after_commit','unheld','drain_timeout']:
        for arm in ['cancel_summary','drain_summary','scoped_summary','scoped_no_summary']:
            items=[r for r in rows if r['cell']['schedule']==schedule and r['cell']['arm']==arm]
            if not items:continue
            outcomes={name:dict(Counter(r['audit']['outcomes'][name]['status'] for r in items)) for name in OUTCOMES}
            costs=[r['audit']['costs'] for r in items]
            grouped.append({'schedule':schedule,'arm':arm,'cells':len(items),'outcomes':outcomes,'costs':costs})
            def short(name):return ', '.join(f'{k}:{v}' for k,v in outcomes[name].items())
            late=sum(len([t for t in r['audit']['observations']['old_final_effect_times'] if t>r['audit']['observations']['stop_requested_ns']]) for r in items)
            useful=sum(all(r['audit']['outcomes'][f'F_{role}_both_artifacts']['status']=='pass' for role in ['new_human','new_completion','independent']) for r in items)
            ambiguous=sum(sum(i['start_ns']<=r['audit']['observations']['stop_requested_ns']<i['end_ns'] for i in r['audit']['observations']['old_final_effect_intervals']) for r in items)
            table.append(f'| {schedule} | {arm} | {late} | {ambiguous} | {short(OUTCOMES[0])} | {short(OUTCOMES[1])} | {short(OUTCOMES[2])} | {useful}/{len(items)} |')
            latencies=[c.get('stop_response_latency_ns') for c in costs]
            numeric=[v/1e6 for v in latencies if isinstance(v,(int,float))]
            observed=f'{min(numeric):.2f}–{max(numeric):.2f}' if numeric else 'unavailable'
            cost_table.append(f'| {schedule} | {arm} | {observed} | {sum(c.get("old_effects_after_reply",0) for c in costs)} |')
    cell_rows=[]
    for row in rows:
        cell,audit=row['cell'],row['audit']
        cell_rows.append(f'| {cell["seed"]} | {cell["schedule"]} | {cell["arm"]} | [audit](audits/{cell["run_id"]}.json) |')
    tests=re.search(r'Ran (\d+) tests',qa.get('stderr',''))
    tests=tests.group(1) if tests else 'kayıttaki'
    report=f'''# Durdurma sözleşmeleri: bütünleşik yerel araştırma sonucu

Üretim zamanı UTC: {datetime.now(timezone.utc).isoformat()}. Matris {a.matrix}. Bu bir iç araştırma raporu ve paper hazırlık kanıtıdır; yayımlanmış paper, yeni protokol veya üretim açığı değildir.

## Sonucun kapsamı

Önceden tanımlanan **26 koşulun tamamı** kanıt geçerliliği denetiminden geçti: dört müdahale × üç zamanlama × iki sabit veri kümesi ve iki ek drain-timeout koşulu. **{counts.get('accepted_runs',0)} gerçek yerel run kabulü**, **{counts.get('native_workers',0)} native worker**, **{counts.get('native_effects',0)} gözlenen native rapor etkisi**, **{counts.get('verified_readouts',0)} doğrulanmış sayısal terminal çıktı** kaydedildi. Sayılar bağımsız olay veya model güvenlik yüzdesi değildir. Test kaydında **{tests} test** bulunur; bu testler yeni bir saha örneklemi değildir.

Her native etkinin gerçek runtime caller kimliği, factory/run kabulü, araç çağrısı, okunan kaynak byte'ları, worker ve dosya hash'i ayrı kod yoluyla bağlandı. Bir müdahale başarısız olsa da tutarlı kaydı `evidence_valid=true` kalır; R/V/C/F sonuçları ayrıca değerlendirilir.

## Sözleşme matrisi

R: operatör isteğinden sonra eski-origin final dosya etkisi yok. V: etkili kapsam geri çekmeden sonra eski-origin native yazım başlangıcı yok. C: gerçekten worker-quiescent olduğu bildirilen onaydan sonra eski etki/başlamış worker yok. `na` o yanıtın böyle bir quiescence sözü vermediğini, `unknown` tamamlanmış onay/kanıt olmadığını gösterir. `fail` upstream açığı veya model direnci demek değildir; seçilmiş daha güçlü sözleşmeyle farktır.

| Zamanlama | Müdahale | İstek sonrası final tamamlanma gözlemi | İstekle çakışan etki aralığı | R | V | C | Üç yeni işin dosyaları korundu |
|---|---|---:|---:|---|---|---|---|
{chr(10).join(table)}

Her satır iki veri koşuludur. `after_commit` dosyası durdurmadan önce oluşmuştur; geri alınmaz ve otomatik olarak geç etki sayılmaz. `unheld` için native yazım bariyeri yoktur; stop final worker girişinin gözlenmesi üzerine tetiklenir. Gerçekte gözlenen sıra kullanılır, gecikme dağılımı veya olay olasılığı çıkarılmaz.

Fiziksel byte görünürlüğünün tek bir anını ölçmüyoruz: native yazım başlangıcı ile yazımdan sonra hash doğrulamasının dönüşü bir **etki aralığıdır**. Başlangıç stop'tan sonraysa kesin sonrası, bitiş stop'tan önceyse kesin öncesi; aralık stop'u kesiyorsa yalnız bu etkiden R-fail çıkarılmaz, `unknown` kalır. Tablodaki tamamlanma gözlemi sayısı fiziksel geç etki sayısı değildir. V, aynı origin kilidi altında doğrudan gözlenen native giriş sırasını kullanır.

## Fayda ve bedel

Görev gerçek yerel dosyadan 24 sentetik auth/egress olayı okur; ilk12 olay için partial, tüm24 için final rapor üretir. Başarılı terminal çıktı; olay sayımı, reddedilmiş kimlik doğrulamalarının ID'leri, başarılı dış egress byte toplamı ve önceki reddetmelerden sonra başarılı giriş yapan aktörün kanıt ID'lerini içerir. Durdurma sonrasında ham veriden yeni hesaplama serbesttir; bu, bütün hesaplamanın durdurulması sözleşmesi değildir. Analiz doğruluğu ile dosya-varlığı iddiaları ayrıca sayılır:

| Rol | Doğrulanan terminal | Doğru dosya iddiası / toplam | Yanlış iddia | Dosya doğrulandı | Eksikliği gözlendi | Doğrulanamadı |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(artifact_table)}

Bir `unverified` yanıtı bilinmezliği dürüst bildirebilir; doğru iddia sayılması dosya varlığı/yokluğu kanıtı değildir. Her sayım gerçek okuma yolu, hash, içerik, statü ve o run'ın terminal ifadesine bağlanır.

Faydalar ağırlıklı tek puana çevrilmedi: mevcut kaynak/partial dosyası, doğru readout, eski istenmeyen etki, yeni insan işi, yeni insan-origin completion ve bağımsız iş ayrı tutuldu. `scoped_no_summary` bir ablation'dır: normal sunulan araçların denenmesi ile native kapsam reddi ayrılır; gizli araç zorlanmaz. Yeni işlerin sonuç vermesi, hiçbir gecikme veya genel maliyet taşımadıkları anlamına gelmez.

| Zamanlama | Müdahale | Gözlenen stop yanıt gecikmesi, ms aralığı | Yanıt sonrası eski native tamamlanma gözlemi |
|---|---|---:|---:|
{chr(10).join(cost_table)}

Bu iki gözlemlik min–max aralığı güven aralığı/p95 değildir. Kontrollü kola eklenen 0.30 saniye ve timeout kontrolündeki1 saniye bekleme, **üretim overhead'i değildir**. Stop yanıtları farklı sözler verir: iptal gözlemi, kapsam geri çekme veya native worker drain. Farklı sözlerin süreleri tek performans sıralaması olarak kullanılamaz. Her hücrenin audit `costs` alanında controller süresi, kilit beklemesi, native okuma/yazım sayıları, yeni iş çıktısının alınmasına kadar geçen süre ve ek registry boyutları tutulur. `new_work_latency_ns`, kabul isteği → terminal cevabın alınmasıdır; özellikle bağımsız iş için hazırlık/hold ve join sıralaması dahildir, aktif hesap süresi değildir. Bellek byte'ı, CPU/para veya gerçek araştırma değeri ölçülmedi.

## Bütünleşik olay akışı

İlk partial → bekleyen/bitmiş final → gerçek source stop ve kendi summary çağrısı → eski completion → done bildirimin tekrar tick'i → aynı-thread açık yeni insan işi → yeni insanın completion'ı → eski bildirimin yeniden teslim edilmesi.

Bağımsız meşru görev, stop öncesinde hazırlanıp eski final hedefi gözlendikten sonra serbest bırakılır. İlk final worker yaşam süresi içinde bağımsız native işin gerçekten giriş yaptığı {overlap}/26 hücre ayrıca kaydedildi; tüm koşullarda örtüşme olduğu varsayılmaz. Model-final/araç dönüşünün gecikmesi ile native worker bitişi ayrı olaylardır. Yerel receipt sonucu audit'in `duplicate_delivery_no_new_admission` alanında gerçek kabul sayısından değerlendirilir; gerçek monitor kendi delivered sayacını yine artırabilir. **Delivered sayısı run sayısı değildir.** Bu receipt admission-once düzeyindedir; başarılı sonuç garantisi veya restart sonrası exactly-once değildir.

Matrisin dışında açıkça enjekte edilmiş receipt-bypass tanı koşulu da çalıştırıldı: [{a.delivery_counterexample}](audits/{a.delivery_counterexample}.json). Denetim, gerçek ek completion kabulünü **kanıt bakımından geçerli, tekrar-engelleme sonucu bakımından fail** olarak tuttu. Bu bir doğal arıza veya 27. karşılaştırma hücresi değildir; ölçümün olumsuz sonucu dışlamadığını kontrol eden tanı örneğidir.

Caller kimliği canlı RunnableConfig'ten gelir; hedef dosya adı bu yetkiyi seçemez. Origin, gerçek kabul edilmiş kök işten türetilen açık yerel task-creation/dispatch kaydıdır. Aynı-thread yanlış çağıran, bilinmeyen/cross-thread kimlik, write-first/revoke-first ve partial-only yanlış drain örnekleri unit/negative kontrollerde sınanır. Bunlar kötü niyetli model veya üretim ingress kimlik doğrulaması deneyi değildir.

## Literatür ve çıkarım

Drain, fencing ve scope revocation'ın öncülleri vardır. Bu çalışma yeni ilke ilan etmez. Katkı, güçlü bekleme alternatifi ile etki noktasındaki kapsam kontrolünü aynı uygulama zincirinde, açık sözleşme ve doğrulanabilir fayda/yan-etki profiliyle karşılaştırmaktır. Hedefli yakın çalışma incelemesi [LITERATURE_POSITIONING](../../LITERATURE_POSITIONING.md) ve sürümlü [kaynak defteri](../../SOURCE_LEDGER.json) içindedir. Başka bir yöntemin bu özel testinin makalede bulunamaması, o yöntemin başarısız olduğunu kanıtlamaz.

## Sınırlar ve tekrar üretim

Gerçek: pinlenmiş427 kaynak dosyası, local-dev API/Store/worker, değiştirilmemiş source factory/stop/monitor, gerçek araçlar ve yerel dosyalar. Sentetik: model, olay verileri, doğrulanmış varsayılan Slack girdisi, dış sağlayıcı cevapları ve arka plan task durumu. Kaynak dosyalar değiştirilmez; yerel adaptörler ve güvenilen sınırlar açıkça kaydedilir. Noop auth üretim yetkilendirmesi değildir; per-origin RLock dağıtık atomiklik veya fsync değildir.

Deney çocukları dış ağ/alt süreç çalıştırmaz. Özel veri, gerçek model/API kredisi, Slack mesajı veya submission yoktur. Kaynak/dev hata kayıtları korunur; worker ve istemciler ölçüm sonunda kapatılır. Aynı host'ta yeni kurulum ve taşınmış kaynakla yapılan tekrar ayrıca raporlanır; bu rapor tek başına ikinci ortam veya bağımsız insan review'u yapıldığını iddia etmez. Bilinen iki E2B dependency override çatışması ve PydanticV1/Python3.14 uyarısı saklanır.

## Hücre kayıtları

| Seed | Zamanlama | Kol | Ayrı kanıt denetimi |
|---|---|---|---|
{chr(10).join(cell_rows)}
'''
    with (target/'FINDINGS_TR.md').open('x') as f:f.write(report)
    save(target/'SUMMARY.json',{'matrix':a.matrix,'totals':counts,'groups':grouped,'paired_input_sha256':input_hashes,
                              'artifact_claims':artifact_summary,'independent_overlap_cells':overlap,
                              'injected_delivery_counterexample':a.delivery_counterexample,
                              'all_evidence_valid':True,'cells':26})
    save(target/'PROVENANCE.json',{'built_utc':datetime.now(timezone.utc).isoformat(),
        'matrix':a.matrix,'plan_sha256':sha(matrix/'PLAN.json'),'executions_sha256':sha(matrix/'EXECUTIONS.jsonl'),
        'qa_sha256':sha(qa_file),'qa_id':a.qa_id,'auditor_sha256':sha(ROOT/'audit_study.py'),
        'builder_sha256':sha(Path(__file__)),'runs':provenance,'paired_input_sha256':input_hashes,
        'delivery_counterexample':{'run_id':a.delivery_counterexample,'input_sha256':{n:sha(fault_dir/n) for n in ['manifest.json','PROCESS.json','events.jsonl','result.json']}},
        'report_sha256':sha(target/'FINDINGS_TR.md'),'summary_sha256':sha(target/'SUMMARY.json')})
    print(json.dumps({'report':str(target/'FINDINGS_TR.md'),'cells':26,'all_evidence_valid':True,'totals':counts}))
    return 0
if __name__=='__main__':raise SystemExit(main())
