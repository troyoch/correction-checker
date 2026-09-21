"""Verify preserved evidence and repeat only standard-library synthetic checks.
No network, credential access, API client, Evo invocation or model generation.
"""
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def require(condition,message):
    if not condition:raise RuntimeError(message)
def check_manifest():
    manifest=read(ROOT/'MANIFEST_SHA256.json')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST_SHA256.json' and '__pycache__' not in p.parts}
    require(actual==set(manifest),'Manifest inventory differs from package')
    for name,digest in manifest.items():require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Hash mismatch: '+name)
    return len(manifest)
def records():
    counts={}
    for suite,count in [('context-path-v1',12),('portable-behavior-v1',6)]:
        prepared=EVIDENCE/'evo-pilot'/(suite+'-prepared');results=EVIDENCE/'evo-pilot'/(suite+'-results')
        text=(prepared/'requests.jsonl').read_text(encoding='utf-8')
        meta=read(prepared/'manifest.json')
        # Historical request digests used newline-normalized Python text, not on-disk CRLF bytes.
        require(hashlib.sha256(text.encode('utf-8')).hexdigest()==meta['request_sha256'],suite+' request manifest')
        jobs=[json.loads(line) for line in text.splitlines()]
        require(len(jobs)==count and len({j['id'] for j in jobs})==count,'Unexpected request count')
        answers=[];input_tokens=output_tokens=0
        for job in jobs:
            r=read(results/(job['id']+'.json'));response=r['response']
            require(r['request']['input']==job['messages'],'Prompt mismatch: '+job['id'])
            require(response['status']=='completed','Incomplete response: '+job['id'])
            require(response.get('previous_response_id') is None and response.get('tools')==[],'Unexpected context/tools')
            answer=''.join(c['text'] for o in response['output'] for c in o.get('content',[]) if c.get('type')=='output_text')
            answers.append({'id':job['id'],'answer':answer})
            input_tokens+=response['usage']['input_tokens'];output_tokens+=response['usage']['output_tokens']
        if (results/'answers.json').exists():
            require(sorted(answers,key=lambda x:x['id'])==sorted(read(results/'answers.json'),key=lambda x:x['id']),'Extracted answers mismatch')
        counts[suite]={'recorded_outputs_verified':count,'input_tokens':input_tokens,'output_tokens':output_tokens}
    return counts
def run(script):subprocess.run([sys.executable,str(script)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def normalize_ids(obj):
    # Each six-fault execution generates one replacement UUID. Preserve all other fields.
    return re.sub(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b','<generated-uuid>',json.dumps(obj,sort_keys=True))
def offline():
    with tempfile.TemporaryDirectory(prefix='correction-reproduction-') as temp:
        root=Path(temp);pilot=root/'evo-pilot';pilot.mkdir()
        for name in ['evidence_gate.py','memory_candidate.py','executable_fault_check.py','portable_memory.py','demo_portable_memory.py','prepare_context_path.py','prepare_portable_behavior.py','local-path-diagnostic-results.json']:
            shutil.copy2(EVIDENCE/'evo-pilot'/name,pilot/name)
        (pilot/'restart-trace-results').mkdir()
        shutil.copy2(EVIDENCE/'evo-pilot/restart-trace-results/accepted-retrieve.json',pilot/'restart-trace-results/accepted-retrieve.json')
        run(pilot/'executable_fault_check.py')
        generated=pilot/'executable-fault-results';original=EVIDENCE/'evo-pilot/executable-fault-results'
        require(read(generated/'summary.json')==read(original/'summary.json'),'Six-fault summary mismatch')
        cases=[p for p in original.glob('*.json') if p.name not in ('summary.json','hashes.json')]
        require(len(cases)==6,'Expected six recorded fault cases')
        for p in cases:require(normalize_ids(read(p))==normalize_ids(read(generated/p.name)),'Fault trace mismatch: '+p.name)
        run(pilot/'demo_portable_memory.py')
        portable=root/'Evo_Portable_Memory_Demo'
        for name in ['verification.json','memory-package.json','restored-state.json']:
            require(read(portable/name)==read(EVIDENCE/'Evo_Portable_Memory_Demo'/name),'Portable mismatch: '+name)
        run(pilot/'prepare_context_path.py');run(pilot/'prepare_portable_behavior.py')
        for suite in ['context-path-v1','portable-behavior-v1']:
            for name in ['requests.jsonl','manifest.json']:
                left=(pilot/(suite+'-prepared')/name).read_text(encoding='utf-8')
                right=(EVIDENCE/'evo-pilot'/(suite+'-prepared')/name).read_text(encoding='utf-8')
                require(left==right,'Prepared inputs mismatch: '+suite+'/'+name)
        compare=root/'comparison';compare.mkdir()
        for name in ['run.py','PROTOCOL.md']:shutil.copy2(EVIDENCE/'diagnostic-comparison'/name,compare/name)
        run(compare/'run.py')
        for name in ['executions.json','summary.json']:
            require(read(compare/'results-v1'/name)==read(EVIDENCE/'diagnostic-comparison/results-v1'/name),'64-execution mismatch: '+name)
    return {'fault_executions':6,'comparison_executions':64,'portable_assertions':12,'prepared_request_records':18,'model_responses_generated':0}
def main():
    p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true',help='Also rerun the standard-library synthetic experiments in temporary directories');args=p.parse_args()
    result={'manifest_files_verified':check_manifest(),'recorded_responses':records()}
    if args.offline:result['offline_reproduction']=offline()
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
