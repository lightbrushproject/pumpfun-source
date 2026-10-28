#!/usr/bin/env python3
"""Offline verifier for the Relay provenance package.

Re-checks every headline claim against the evidence retained in this
folder. Reads no repo files and no network. For a live re-read of the
chain state, see evidence/refresh_chain.py.
"""
import json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, 'evidence')
fails = []

def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)

def load(name, base=EV):
    with open(os.path.join(base, name)) as f:
        return json.load(f)

reg = json.load(open(os.path.join(HERE, 'register.json')))
cs = load('chain_state.json')
hist = load('history.json')
search = load('search_log.json')

# 1. Pin and identity agree across register and chain evidence.
check(reg['pin']['commit'] == '3719d910d297ad62497e2ef1b12e263d2059f2ae', 'register pin is 3719d910')
check(reg['identity']['program'] == cs['program_account']['address'], 'program address matches chain state')
check(reg['identity']['programdata'] == cs['programdata_account']['address'] == hist['programdata'],
      'ProgramData address matches chain state and history')
check(cs['program_account']['programdata'] == cs['programdata_account']['address'],
      'program account points at the ProgramData account')
check(cs['program_account']['executable'] is True and cs['program_account']['space'] == 36,
      'program account is an executable 36-byte loader account')

# 2. ProgramData header.
hdr = cs['programdata_account']['header']
check(hdr['variant_tag'] == 3, 'ProgramData header variant tag is 3 (ProgramData)')
check(hdr['last_deploy_slot'] == 415422992, 'last_deploy_slot is 415422992')
check(hdr['upgrade_authority'] == '9rmqZkmn3Bzd4jAL5uw3TXCgWvbHwH1VyW6fdFtimASu',
      'current upgrade authority matches the register basis')

# 3. Payload identity: deployed equals retained original.
pay = cs['programdata_account']['payload']
ref = cs['reference_values_from_repo']
check(pay['bytes'] == 830448, 'payload is 830,448 bytes')
check(pay['sha256'] == ref['scope_table_payload_sha256'] == ref['captured_payload_sha256'],
      'payload SHA-256 equals the SCOPE table and captured payload hashes')
check(pay['elf_extent_bytes'] == 818280 and pay['elf_extent_sha256'] == ref['retained_original_elf_extent_sha256'],
      'ELF extent SHA-256 equals the retained original')
check(pay['bytes'] - pay['elf_extent_bytes'] == pay['tail_bytes'] == 12168 and pay['tail_all_zero'] is True,
      'tail is 12,168 bytes and all zero')
check(cs['programdata_account']['space'] == pay['bytes'] + 45, 'account space is header (45) plus payload')
check(ref['scope_table_last_deployment_slot'] == hdr['last_deploy_slot'],
      'SCOPE table last deployment slot equals the fresh header read')

# 4. History: 13 events, counts, ladder, freshness, ordering.
evs = hist['events']
check(len(evs) == 13, 'history carries exactly 13 events')
counts = {}
for e in evs:
    counts[e['action']] = counts.get(e['action'], 0) + 1
check(counts == {'deploy': 1, 'upgrade': 6, 'extend': 5, 'set_authority': 1} == hist['counts'],
      'counts are deploy 1 / upgrade 6 / extend 5 / set_authority 1')
check(all(e['in_fresh_signature_list'] for e in evs) and hist['fresh_signature_rows_2026_10_28'] == 13
      and hist['fresh_set_equals_retained_set'] is True,
      'fresh signature set equals the retained 13')
check([e['slot'] for e in evs] == sorted(e['slot'] for e in evs), 'events are in slot order')
for e in evs:
    derived = datetime.fromtimestamp(e['block_time_unix'], timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    check(derived == e['block_time_utc'], f"block time at slot {e['slot']} converts to {e['block_time_utc']}")
ladder = [e['capacity_after'] for e in evs if 'capacity_after' in e]
check(ladder == [546944, 580448, 680448, 780448, 820448, 830448], 'capacity ladder is consistent')
check(ladder[-1] == pay['bytes'] and reg['inputs']['allocation_report']['events'] == 13
      and reg['inputs']['allocation_report']['last_upgrade_slot'] == 415422992,
      'ladder ends at the payload size and matches the allocation report binding')
upgrades = [e['slot'] for e in evs if e['action'] == 'upgrade']
check(upgrades[-1] == hdr['last_deploy_slot'] == 415422992, 'last upgrade slot equals header last_deploy_slot')
check(evs[-1]['action'] == 'set_authority' and evs[-1]['slot'] == 417994985 > upgrades[-1],
      'the authority change is the last event and follows the last upgrade')

# 5. Authority chain in the parsed endpoint transactions.
dep = hist['deploy_transaction']
auth = hist['set_authority_transaction']
check(dep['fee_payer'] == 'prodARfLWf9ch7yfzQr6Z8tqiee38BHyMi6TW7puYHJ', 'deploy fee payer is the original authority key')
deploy_ix = [i for i in dep['instructions'] if i['type'] == 'deployWithMaxDataLen'][0]['info']
check(deploy_ix['authority'] == dep['fee_payer'] and deploy_ix['programDataAccount'] == hist['programdata']
      and deploy_ix['programAccount'] == cs['program_account']['address'],
      'deploy instruction names the deployer as authority and binds program and ProgramData')
set_ix = [i for i in auth['instructions'] if i['type'] == 'setAuthority'][0]['info']
check(set_ix['authority'] == dep['fee_payer'] and set_ix['newAuthority'] == hdr['upgrade_authority']
      and auth['fee_payer'] == dep['fee_payer'],
      'setAuthority moves authority from the deployer to the current header authority')

# 6. Register verdicts: allowed labels only, unresolved items named.
allowed = ('established', 'strongly indicated', 'unresolved')
by_id = {v['id']: v for v in reg['verdicts']}
check(set(by_id) == {'Q1-program-identity', 'Q2-what-the-program-is', 'Q3-programdata-history',
                     'Q4-authority-history', 'Q5-deployed-equals-original', 'Q6-historical-build-recipe'},
      'register carries exactly Q1 to Q6')
for vid, v in by_id.items():
    lead = v['confidence'].split(';')[0].split(' for ')[0].strip()
    check(all(label in v['confidence'] for label in [lead]) and lead in allowed or
          any(v['confidence'].startswith(a) for a in allowed),
          f'{vid} confidence leads with an allowed label')
check(by_id['Q6-historical-build-recipe']['confidence'] == 'unresolved'
      and by_id['Q6-historical-build-recipe']['verdict'] == 'unresolved',
      'Q6 historical build recipe is labeled unresolved')
check('unresolved' in by_id['Q2-what-the-program-is']['verdict']
      and 'unresolved' in by_id['Q4-authority-history']['verdict'],
      'Q2 and Q4 name their unresolved organizational attribution')
check(search['verdict'] == 'unresolved' and 'what_would_close_it' in search,
      'search log verdict is unresolved and names what would close it')

print()
if fails:
    print(f'{len(fails)} CHECK(S) FAILED')
    sys.exit(1)
print('ALL CHECKS PASSED')
