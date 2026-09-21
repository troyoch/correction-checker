"""Standard-library correction persistence checker. No built-in API client."""
import argparse, hashlib, json, subprocess, sys, uuid
from pathlib import Path
STAGES=('accepted','storage','retrieval','answer')
RAW={'accepted':'raw_record','storage':'raw_record','retrieval':'raw_context','answer':'raw_output'}
DEFAULT_CASE={'initial':'Friday','corrected':'Tuesday','teach':'My soccer practice is on Friday.','correction':'Correction: my soccer practice is now on Tuesday.','probe':'What day is my soccer practice?'}
def observations_from(reply):
    if reply.get('status')!='completed':
        return {stage:{'status':'unavailable','reason':reply.get('reason','Operation not completed; any included values ignored')} for stage in STAGES}
    observations=reply.get('observations',{})
    if not isinstance(observations,dict):raise ValueError('observations must be an object')
    return observations

def assess(observations, expected, required=STAGES):
    checks={}; evidence={}; gap=False; location=None
    for stage in STAGES:
        if stage not in required:
            checks[stage]='not_applicable';evidence[stage]='not_applicable';continue
        item=observations.get(stage,{})
        if not isinstance(item,dict) or item.get('status')!='observed' or not isinstance(item.get('value'),str) or not item.get('source'):
            checks[stage]='not_checked';evidence[stage]='unavailable';gap=True
        else:
            raw=item.get(RAW[stage])
            inspectable=isinstance(raw,(str,dict,list)) and bool(raw)
            evidence[stage]='inspectable_adapter_evidence' if inspectable else 'connector_report_only'
            checks[stage]='pass' if item['value']==expected else 'fail'
            if checks[stage]=='fail' and location is None:
                location='indeterminate' if gap else stage
    return {'checks':checks,'evidence':evidence,'earliest_supported_divergence':location or ('indeterminate' if gap else 'none_observed'),
            'scope':'Adapter-reported exact-value comparison; attached evidence is inspectable, not independently verified.'}

def overall(reports,status):
    if any('assessment' in r and 'fail' in r['assessment']['checks'].values() for r in reports):return 'failed'
    if status!='completed' or any('assessment' not in r for r in reports):return 'inconclusive'
    if any('not_checked' in r['assessment']['checks'].values() or 'connector_report_only' in r['assessment']['evidence'].values() for r in reports):return 'inconclusive'
    return 'passed' if reports else 'inconclusive'

def run(command, out, case=None):
    case=dict(DEFAULT_CASE if case is None else case)
    if set(case)!=set(DEFAULT_CASE) or any(not isinstance(v,str) or not v.strip() for v in case.values()):raise ValueError("Case requires nonempty initial, corrected, teach, correction, probe strings")
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    state=out/'state';state.mkdir()
    namespace='correction-check-'+uuid.uuid4().hex
    config={'schema':'correction-check/1','namespace':namespace,'adapter_command':command,
      'case':case,
      'scope':'One synthetic case; sequential interventions, not isolated causal ablations.'}
    (out/'plan.json').write_text(json.dumps(config,indent=2))
    events=[]; reports=[]; accepted=None
    def call(op, **args):
        request={'schema':'correction-check/1','operation':op,'namespace':namespace,'state_dir':str(state.resolve()),**args}
        proc=subprocess.run(command,input=json.dumps(request),capture_output=True,text=True,timeout=60,shell=False)
        event={'request':request,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
        events.append(event)
        (out/'events.json').write_text(json.dumps(events,indent=2))
        if proc.returncode: raise RuntimeError('Adapter failed; partial events preserved.')
        response=json.loads(proc.stdout)
        if response.get('schema')!='correction-check/1': raise ValueError('Unsupported adapter schema')
        event['response']=response
        return response
    try:
        caps=call('capabilities')
        if caps.get('status')!='completed' or caps.get('isolated_test_namespace') is not True: raise ValueError('Adapter must support isolated test namespaces')
        taught=call('teach',session='learning',text=case['teach'])
        if taught.get('status')!='completed':raise ValueError('Teaching unavailable; no valid baseline')
        baseline=call('probe',session='baseline',question=config['case']['probe'])
        reports.append({'checkpoint':'baseline','assessment':assess(observations_from(baseline),case['initial'],required=('storage','retrieval','answer')),'lifecycle':baseline.get('lifecycle',{})})
        correction=call('correct',session='learning',text=case['correction'])
        accepted=observations_from(correction).get('accepted',{'status':'unavailable','reason':'Adapter did not expose acquisition'})
        for checkpoint, operation, session in [('current_conversation',None,'learning'),('fresh_conversation',None,'fresh-1'),('after_restart','restart','fresh-2'),('after_summary_update','refresh_summary','fresh-3')]:
            transition=call(operation) if operation else None
            if transition and transition.get('status')!='completed':
                reports.append({'checkpoint':checkpoint,'not_run':transition.get('reason','Transition unavailable')});continue
            reply=call('probe',session=session,question=config['case']['probe'])
            observations=dict(observations_from(reply))
            if reply.get('status')=='completed':observations['accepted']=accepted
            reports.append({'checkpoint':checkpoint,'observations':observations,'assessment':assess(observations,case['corrected']),'lifecycle':reply.get('lifecycle',{}),'transition':transition})
        status='completed'
    except Exception as exc:
        status='incomplete';reports.append({'error':str(exc)})
    (out/'events.json').write_text(json.dumps(events,indent=2))
    outcome=overall(reports,status)
    result={'status':status,'outcome':outcome,'reports':reports,'note':'Session/reset claims are adapter attestations. Inspect events and adapter; checker process isolation alone is not backend restart.'}
    (out/'result.json').write_text(json.dumps(result,indent=2))
    lines=['# Correction persistence report','',f'Status: {status}; outcome: {outcome}', '',result['note'],'','Exact-value development check, not a reliability estimate. Missing evidence is not a pass.','', '| Checkpoint | Accepted | Saved | Retrieved | Answer | Earliest supported divergence |','|---|---|---|---|---|---|']
    notes=[]
    for report in reports:
        if 'assessment' not in report:
            notes+=['',str(report)];continue
        a=report['assessment'];c=a['checks'];lines+=['| '+' | '.join([report['checkpoint']]+[c[k] for k in STAGES]+[a['earliest_supported_divergence']])+' |']
        notes+=['', report['checkpoint']+' evidence: '+', '.join(stage+'='+level for stage,level in a['evidence'].items())]
        for stage,obs in report.get('observations',{}).items():
            if obs.get('status')!='observed':notes+=['',f"Missing {stage} at {report['checkpoint']}: {obs.get('reason','No reason supplied')}"]
    lines+=['','## Evidence notes']+notes
    lines+=['','Pass means the adapter-reported canonical value equals the expected value. Raw context and output must remain available for audit. Automatic semantic interpretation is not implemented.','', 'Sequence: teach, baseline, correct, current conversation, fresh conversation, restart, summary refresh. Later checkpoints include earlier interventions.']
    (out/'REPORT.md').write_text('\n'.join(lines))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'hashes.json').write_text(json.dumps(hashes,indent=2))
    return outcome
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--case',help='JSON case file');p.add_argument('adapter',nargs=argparse.REMAINDER);args=p.parse_args()
    command=args.adapter[1:] if args.adapter[:1]==['--'] else args.adapter
    if not command:p.error('Supply an adapter command after --')
    case=json.loads(Path(args.case).read_text()) if args.case else None
    outcome=run(command,args.out,case)
    sys.exit({'passed':0,'failed':1,'inconclusive':2}[outcome])
