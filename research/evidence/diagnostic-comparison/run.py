import hashlib, itertools, json, sqlite3, tempfile
from contextlib import closing
from pathlib import Path
ROOT = Path(__file__).resolve().parent
STAGES = ('acquisition','storage','retrieval','response')
POLICIES = {'full': STAGES, 'no_storage': ('acquisition','retrieval','response'), 'no_retrieval': ('acquisition','storage','response'), 'answer_only': ('response',)}
def diagnose(visible, expected):
    gap = False
    for stage in STAGES:
        if stage not in visible:
            gap = True
        elif visible[stage] != expected:
            return 'indeterminate' if gap else stage
    return 'indeterminate' if gap else 'none_observed'
def execute(db, old, new, switches):
    acquisition_fault, storage_fault, retrieval_fault, response_fault, recovery = switches
    a = old if acquisition_fault else new
    with closing(sqlite3.connect(db)) as con:
        con.execute('CREATE TABLE memory(version INTEGER PRIMARY KEY, value TEXT, active INTEGER)')
        con.execute('INSERT INTO memory VALUES(0,?,1)', (old,))
        if not storage_fault:
            con.execute('UPDATE memory SET active=0')
            con.execute('INSERT INTO memory VALUES(1,?,1)', (a,))
        con.commit()
    with closing(sqlite3.connect(db)) as con:
        stored = con.execute('SELECT value FROM memory WHERE active=1').fetchone()[0]
        retrieved = con.execute('SELECT value FROM memory ORDER BY version LIMIT 1').fetchone()[0] if retrieval_fault else stored
        rows = list(con.execute('SELECT * FROM memory ORDER BY version'))
    if recovery:
        retrieved = new
    response = old if response_fault else retrieved
    return dict(zip(STAGES, (a, stored, retrieved, response))), rows

def main():
    output = ROOT/'results-v1'
    output.mkdir(exist_ok=False)
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for case,old,new in [('schedule','Friday','Tuesday'),('format','prose','bullets')]:
            for bits in itertools.product((False,True), repeat=5):
                ident = case+'-'+''.join(str(int(b)) for b in bits)
                trace, dbrows=execute(str(Path(tmp)/(ident+'.sqlite')),old,new,bits)
                truth=next((s for s in STAGES if trace[s]!=new),'none_observed')
                observations={}
                for policy, stages in POLICIES.items():
                    visible={s:trace[s] for s in stages}
                    log='\n'.join(s+'='+v for s,v in visible.items())
                    parsed=dict(line.split('=',1) for line in log.splitlines())
                    observations[policy]={'structured':visible,'ordinary_log':log,'trace_diagnosis':diagnose(visible,new),'log_diagnosis':diagnose(parsed,new)}
                rows.append({'id':ident,'old':old,'expected':new,'switches':dict(zip(('acquisition_fault','storage_fault','retrieval_fault','response_fault','retrieval_recovery'),bits)),'trace':trace,'reopened_database_rows':dbrows,'first_observed_divergence':truth,'observations':observations})
    summary={'executions':len(rows),'api_requests':0,'correct_final_answer_despite_prior_divergence':sum(r['trace']['response']==r['expected'] and r['first_observed_divergence']!='none_observed' for r in rows),'policies':{}}
    for policy in POLICIES:
        groups={}
        for r in rows:
            key=json.dumps({s: v==r['expected'] for s,v in r['observations'][policy]['structured'].items()},sort_keys=True)
            groups.setdefault(key,set()).add(r['first_observed_divergence'])
        summary['policies'][policy]={'correct_definite':sum(r['observations'][policy]['trace_diagnosis']==r['first_observed_divergence'] for r in rows),'indeterminate':sum(r['observations'][policy]['trace_diagnosis']=='indeterminate' for r in rows),'incorrect_definite':sum(r['observations'][policy]['trace_diagnosis'] not in ('indeterminate',r['first_observed_divergence']) for r in rows),'ordinary_log_agreement':sum(r['observations'][policy]['trace_diagnosis']==r['observations'][policy]['log_diagnosis'] for r in rows),'observable_patterns':len(groups),'patterns_with_multiple_possible_labels':sum(len(g)>1 for g in groups.values()),'pattern_labels':{k:sorted(v) for k,v in groups.items()}}
    (output/'executions.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'PROTOCOL.md',Path(__file__),output/'executions.json',output/'summary.json']}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({**summary,'policies':{k:{a:b for a,b in v.items() if a!='pattern_labels'} for k,v in summary['policies'].items()}},indent=2))
if __name__=='__main__': main()

