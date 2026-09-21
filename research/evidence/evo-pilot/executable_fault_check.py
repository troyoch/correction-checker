import json
import sqlite3
import hashlib
from pathlib import Path
from evidence_gate import revise

def diagnose(trace):
    for stage in ('accepted_gate_output','storage','retrieval'):
        values=trace[stage]
        if len(values)!=1:
            return 'indeterminate'
        if values[0]!=trace['expected']:
            return stage
    return 'no_observed_divergence'

def main():
    out=Path(__file__).resolve().parent/'executable-fault-results'
    out.mkdir(exist_ok=False)
    results=[]
    for case,old,new in [('schedule','Friday','Tuesday'),('format','prose','bullets')]:
        for fault in ('healthy','skip_commit','old_retrieval'):
            run_id=f'{case}-{len(results):02d}'
            db=out/(run_id+'.sqlite')
            con=sqlite3.connect(db)
            con.execute('CREATE TABLE memory (sequence INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
            state={'rows':[dict(id='original',user_id=7,memory_type='preference',title=case,memory_key=case,detail=old,active=True)],'memory_summaries':{}}
            con.execute('INSERT INTO memory(payload) VALUES (?)',(json.dumps(state['rows'][0]),))
            con.commit()
            proposal=dict(user_id=7,target_id='original',memory_type='preference',detail=new,evidence_ref='e1')
            evidence=dict(proposal,previous_detail=old,subject_id=7,kind='self_preference',source='authenticated_user',issued_at=1,expires_at=100)
            revised,status=revise(state,proposal,actor_user=7,registry={'e1':evidence},authorities={},now=10)
            if not status['accepted']:
                raise RuntimeError('Unexpected gate rejection; preserve partial evidence for review')
            if fault!='skip_commit':
                with con:
                    con.execute('DELETE FROM memory')
                    con.executemany('INSERT INTO memory(payload) VALUES (?)',[(json.dumps(r),) for r in revised['rows']])
            con.close()
            # Evidence read back from an independently reopened connection.
            con=sqlite3.connect(db)
            persisted=[json.loads(r[0]) for r in con.execute('SELECT payload FROM memory ORDER BY sequence')]
            if fault=='old_retrieval':
                selected=[json.loads(con.execute('SELECT payload FROM memory ORDER BY sequence LIMIT 1').fetchone()[0])]
            else:
                selected=[r for r in persisted if r['active']]
            con.close()
            trace={'expected':new,
                   'accepted_gate_output':[r['detail'] for r in revised['rows'] if r['active']],
                   'storage':[r['detail'] for r in persisted if r['active']],
                   'retrieval':[r['detail'] for r in selected]}
            predicted=diagnose(trace)
            expected={'healthy':'no_observed_divergence','skip_commit':'storage','old_retrieval':'retrieval'}[fault]
            record={'id':run_id,'trace':trace,'gate_status':status,'gate_rows':revised['rows'],
                    'reopened_rows':persisted,'selected_rows':selected,'diagnosis':predicted,
                    'injected_condition':fault,'expected_diagnosis':expected,'diagnosis_matches':predicted==expected,
                    'retrieval_correct':trace['retrieval']==[new],'model_response':'not_tested'}
            (out/(run_id+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
            results.append(record)
    summary={'runs':len(results),'diagnosis_matches':sum(r['diagnosis_matches'] for r in results),
             'retrieval_correct':sum(r['retrieval_correct'] for r in results),'api_calls':0,
             'scope':'Candidate gate plus SQLite adapter; two development cases; single injected faults; no model'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if not all(r['diagnosis_matches'] for r in results):
        raise SystemExit(1)

if __name__=='__main__':
    main()
