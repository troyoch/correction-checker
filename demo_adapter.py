"""Synthetic deterministic assistant. Not Evo; faults explicitly injected."""
import json, sqlite3, sys
from pathlib import Path
from contextlib import closing
mode=sys.argv[1] if len(sys.argv)>1 else 'healthy'
if mode not in ('healthy','skip_save','stale_summary','missing_storage'):raise ValueError('Unknown mode')
r=json.load(sys.stdin);op=r['operation'];root=Path(r['state_dir']);db=root/'demo.sqlite'
def obs(value,source,**extra):return {'status':'observed','value':value,'source':source,**extra}
reply={'schema':'correction-check/1','status':'completed'}
with closing(sqlite3.connect(db)) as c:
    c.execute('CREATE TABLE IF NOT EXISTS state(namespace TEXT PRIMARY KEY, current TEXT, summary TEXT, pending TEXT)')
    ns=r['namespace']
    if op=='capabilities':reply.update(isolated_test_namespace=True,implementation='Synthetic SQLite and deterministic response stub, not Evo',mode=mode)
    elif op=='teach':
        if r['text']!='My soccer practice is on Friday.':raise ValueError('Demo parser supports only documented fixture')
        c.execute('INSERT INTO state VALUES(?,?,?,?)',(ns,'Friday','Friday',None))
    elif op=='correct':
        if r['text']!='Correction: my soccer practice is now on Tuesday.':raise ValueError('Unsupported demo correction')
        c.execute('UPDATE state SET pending=? WHERE namespace=?',('Tuesday',ns))
        if mode!='skip_save':c.execute('UPDATE state SET current=? WHERE namespace=?',('Tuesday',ns))
        reply['observations']={'accepted':obs('Tuesday','exact fixture parser',raw_record={'captured_value':'Tuesday'})}
    elif op=='restart':reply['lifecycle']={'local_process_fresh':True,'backend':'SQLite reopened on every call; no resident server'}
    elif op=='refresh_summary':
        if mode!='stale_summary':c.execute('UPDATE state SET summary=current WHERE namespace=?',(ns,))
    elif op=='probe':
        if r['question']!='What day is my soccer practice?':raise ValueError('Unsupported demo probe')
        row=c.execute('SELECT current,summary,pending FROM state WHERE namespace=?',(ns,)).fetchone()
        current,summary,pending=row
        selected=summary if mode=='stale_summary' else current
        answer=pending if r['session']=='learning' and pending else selected
        reply['observations']={'storage':obs(current,'reopened SQLite current row',raw_record={'current':current,'summary':summary}),'retrieval':obs(selected,'selected memory context',raw_context=f'Soccer practice: {selected}.'),'answer':obs(answer,'deterministic response stub',raw_output=answer)}
        if mode=='missing_storage':reply['observations']['storage']={'status':'unavailable','reason':'Demonstration adapter deliberately withholds storage telemetry'}
        reply['lifecycle']={'session':r['session'],'conversation_history':[] if r['session']!='learning' else ['correction available'],'fresh_adapter_process':True}
    else:raise ValueError('Unknown operation')
    c.commit()
print(json.dumps(reply))
