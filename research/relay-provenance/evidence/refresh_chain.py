#!/usr/bin/env python3
"""Refresh the Relay chain-state evidence from the public Solana RPC.

Re-runs the finalized read-only requests behind chain_state.json and
history.json and prints the derived fields: program and ProgramData
identity, ProgramData header (last deploy slot, upgrade authority),
payload length and SHA-256, ELF-extent SHA-256, tail check, and the
ProgramData signature count. Read-only: it submits nothing.

Requires curl. Usage:
    python3 evidence/refresh_chain.py
"""
import base64, hashlib, json, struct, subprocess, sys

RPC = 'https://api.mainnet-beta.solana.com'
PROGRAM = 'RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu'
EXTENT = 818280

def rpc(method, params):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})
    out = subprocess.run(['curl', '-s', '-X', 'POST', RPC, '-H', 'Content-Type: application/json',
                          '-d', body], capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def b58(b):
    alph = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(b, 'big'); s = ''
    while n:
        n, r = divmod(n, 58); s = alph[r] + s
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + s

pa = rpc('getAccountInfo', [PROGRAM, {'encoding': 'jsonParsed', 'commitment': 'finalized'}])['result']
pd_addr = pa['value']['data']['parsed']['info']['programData']
print('program:', PROGRAM, '| context slot:', pa['context']['slot'])
print('programdata:', pd_addr)

hdr = rpc('getAccountInfo', [pd_addr, {'encoding': 'base64', 'commitment': 'finalized',
                                       'dataSlice': {'offset': 0, 'length': 45}}])['result']['value']
raw = base64.b64decode(hdr['data'][0])
tag, last_slot = struct.unpack_from('<I Q', raw, 0)
authority = b58(raw[13:45]) if raw[12] == 1 else None
print('header: tag', tag, '| last_deploy_slot:', last_slot, '| upgrade authority:', authority)
print('account space:', hdr['space'])

pay = rpc('getAccountInfo', [pd_addr, {'encoding': 'base64', 'commitment': 'finalized',
                                       'dataSlice': {'offset': 45, 'length': 830448}}])['result']['value']
payload = base64.b64decode(pay['data'][0])
print('payload bytes:', len(payload))
print('payload sha256:', hashlib.sha256(payload).hexdigest())
print('elf extent sha256:', hashlib.sha256(payload[:EXTENT]).hexdigest())
print('tail bytes:', len(payload) - EXTENT, '| tail all zero:', set(payload[EXTENT:]) == {0})

sigs = rpc('getSignaturesForAddress', [pd_addr, {'limit': 100, 'commitment': 'finalized'}])['result']
print('programdata signature rows:', len(sigs), '| newest slot:', sigs[0]['slot'], '| oldest slot:', sigs[-1]['slot'])
