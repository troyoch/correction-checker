"""Build fictional shareable package; independently restore it in a new process."""
import copy
import json
import subprocess
import sys
from pathlib import Path
from portable_memory import export_package, digest, restore

root = Path(__file__).resolve().parent
out = root.parent/'Evo_Portable_Memory_Demo'
out.mkdir(exist_ok=False)
state = json.loads((root/'restart-trace-results/accepted-retrieve.json').read_text())['state']
corrected = next(r['id'] for r in state['rows'] if r['active'])
state['rows'].extend([
    dict(id='project',user_id=7,active=True,memory_type='fact',title='Project',memory_key='project',detail='Rowan is building a miniature observatory.'),
    dict(id='private',user_id=7,active=True,memory_type='fact',title='Private note',memory_key='private',detail='PRIVATE_CANARY_7F19'),
    dict(id='other-user',user_id=8,active=True,memory_type='fact',title='Other user',memory_key='other',detail='OTHER_USER_CANARY_93AB')])
# The unselected private note is deleted from the outgoing scope only. Source
# records and prior backups are deliberately not erased by this export function.
package = export_package(state, 7, {corrected, 'project'})
path = out/'memory-package.json'
path.write_text(json.dumps(package, indent=2), encoding='utf-8')
subprocess.run([sys.executable, str(root/'portable_memory.py'), str(path),
                str(out/'restored-state.json'), '--owner','7'], check=True)
restored = json.loads((out/'restored-state.json').read_text())
context = '\n'.join(r['detail'] for r in restored['rows'])
(out/'restored-memory.txt').write_text(context+'\n', encoding='utf-8')
def rejected(value, owner=7):
    try:
        restore(value, owner)
    except ValueError:
        return True
    return False
tampered = copy.deepcopy(package)
tampered['payload']['records'][0]['detail'] = 'Changed without updating integrity hash.'
duplicate = copy.deepcopy(package)
duplicate['payload']['records'].append(duplicate['payload']['records'][0])
duplicate['sha256'] = digest(duplicate['payload'])
unsupported = copy.deepcopy(package)
unsupported['payload']['schema'] = 'unknown/99'
unsupported['sha256'] = digest(unsupported['payload'])
checks = {
 'corrected_preference_restored': 'Rowan prefers quiet concerts, not crowded concerts.' in context,
 'other_selected_detail_restored': 'Rowan is building a miniature observatory.' in context,
 'old_claim_absent': 'Rowan prefers crowded concerts.' not in json.dumps(package),
 'excluded_detail_absent_from_package_and_restore': all('PRIVATE_CANARY_7F19' not in text for text in [json.dumps(package), json.dumps(restored),context]),
 'other_user_absent': 'OTHER_USER_CANARY_93AB' not in json.dumps(package),
 'history_and_summaries_not_transported': set(package['payload']['records'][0]) == {'id','memory_type','title','memory_key','detail'},
 'exactly_two_records': len(restored['rows']) == 2,
 'tampering_rejected': rejected(tampered),
 'wrong_owner_rejected': rejected(package, 8),
 'duplicate_id_rejected': rejected(duplicate),
 'unsupported_schema_rejected': rejected(unsupported),
 'empty_selection_restores_empty': restore(export_package(state,7,set()),7)['rows'] == [],
}
report = {'checks': checks, 'passed':sum(checks.values()), 'total':len(checks), 'api_calls':0,
          'scope':'Local fresh-process export/restore. No model behavior tested. Exclusion from outgoing package is not global deletion.'}
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
if not all(checks.values()):
    raise SystemExit(1)
