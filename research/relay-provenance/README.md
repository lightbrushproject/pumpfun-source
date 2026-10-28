# Relay: historical provenance and ProgramData history

`docs/RECONSTRUCTION-STATUS.md` recommended order #1 asks to investigate
authentic source and build provenance for the Relay, and
`docs/REMAINING-WORK.md` carries "Relay historical provenance and broader
coverage" as an open requirement. The reconstructed layout already closes
byte identity; what it does not close is the history. This package
consolidates that history from primary sources: fresh finalized chain
reads taken on 2026-10-28, the repo's retained packets, and a documented
source-side search. It proposes no build, no execution, and no selection
change, and it enters no stopped lane (the current `docs/COMPLETION.md`
checkpoint stop list was re-checked at the pin).

Pinned at upstream main `3719d910d297ad62497e2ef1b12e263d2059f2ae` (merge
of PR #502, 2026-10-28).

## Identity

The Relay is the Solana program `RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu`,
held in ProgramData account `5QH8Ay11KgpRMyECYofHwAr6SzfFEGkbtPoM6eXv8V7B`
under the upgradeable loader. The program identifies itself in embedded
security metadata as the Donate.gg Donation Relay, with metadata pointing
to `https://github.com/CherryDevelopmentOrg/daas`; pump.fun's public docs
bind the same address as `donation_relay_program` in the Pump Fees IDL.
The auditor field in the embedded metadata names Halborn; that is a
publisher claim, not independent verification. Which organization owns
the program is unresolved: `docs/SCOPE.md` records organizational
ownership as unresolved and does not label the program first-party.

## ProgramData history: 13 transactions, complete

The ProgramData account has been touched by exactly 13 transactions.
The signature list re-fetched on 2026-10-28 is identical to the repo's
retained list; nothing has touched the account since the authority
change. Capacity derivation (deploy size plus five extensions summing
to 830,448 bytes) is the allocation-provenance packet's work and is
credited there; this package adds the dates and the actors.

| Slot | Date (UTC) | Action | Capacity after |
| ---: | --- | --- | ---: |
| 401117852 | 2026-02-18T15:38:48Z | deploy | 546,944 |
| 401119086 | 2026-02-18T15:46:50Z | upgrade | |
| 401119309 | 2026-02-18T15:48:15Z | upgrade | |
| 401120076 | 2026-02-18T15:53:15Z | upgrade | |
| 403116664 | 2026-02-27T18:23:58Z | extend (+33,504) | 580,448 |
| 403116709 | 2026-02-27T18:24:16Z | upgrade | |
| 407531758 | 2026-03-19T21:29:11Z | upgrade | |
| 415393334 | 2026-04-24T17:39:45Z | extend (+100,000) | 680,448 |
| 415393372 | 2026-04-24T17:40:00Z | extend (+100,000) | 780,448 |
| 415393402 | 2026-04-24T17:40:12Z | extend (+40,000) | 820,448 |
| 415393486 | 2026-04-24T17:40:44Z | extend (+10,000) | 830,448 |
| 415422992 | 2026-04-24T20:54:08Z | upgrade (last) | |
| 417994985 | 2026-05-06T15:46:56Z | set_authority | |

Counts: deploy 1, upgrade 6, extend 5, set_authority 1. Full signatures
and block times are in `evidence/history.json`. One note carried from
the allocation packet: the 33,504-byte extension transaction also
initializes a separate buffer; that initialization is decoded in the
retained records but is not part of the ProgramData capacity sum.

## Authority history

The deployment transaction (slot 401117852) was paid by
`prodARfLWf9ch7yfzQr6Z8tqiee38BHyMi6TW7puYHJ`, which was also the initial
upgrade authority named in its deployWithMaxDataLen instruction. At
slot 417994985 (2026-05-06) that key's setAuthority transaction moved
upgrade authority to `9rmqZkmn3Bzd4jAL5uw3TXCgWvbHwH1VyW6fdFtimASu`. A fresh
ProgramData header read confirms the second key as the current
authority. Which organizations these keys belong to is not established
by public evidence in hand, and this package does not speculate.

## Current state: the deployed program is the retained original

Fresh finalized reads on 2026-10-28 (context slots 462,524,450 to
462,524,660) re-derive every value in the `docs/SCOPE.md` dependency
table:

- ProgramData header: variant tag 3, last_deploy_slot 415,422,992,
  unchanged since the capture; upgrade authority
  `9rmqZkmn3Bzd4jAL5uw3TXCgWvbHwH1VyW6fdFtimASu`; account space 830,493.
- Payload: 830,448 bytes, SHA-256
  `367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563`,
  equal to the captured payload hash in `docs/SCOPE.md`.
- ELF extent: 818,280 bytes, SHA-256
  `56d81ec64a0ba070d3d23f3c1547b31d659e85716dfa2198ec4b0ce6cd355333`,
  equal to the retained original and to the canonical build.
- Tail: 12,168 bytes past the ELF extent, all zero.

The program deployed on mainnet today is the retained original, byte
for byte.

## Verdicts

| ID | Question | Verdict | Confidence |
| --- | --- | --- | --- |
| Q1 | Which on-chain program is the Relay, and which ProgramData account holds it? | identified | established |
| Q2 | What is the program, organizationally and by interface? | identified; ownership unresolved | established for self-identification and IDL naming; unresolved for ownership |
| Q3 | What is the complete ProgramData history? | complete at 13 transactions | established |
| Q4 | Who deployed it and who holds upgrade authority? | established on chain; organizational attribution unresolved | established |
| Q5 | Does the deployed program still equal the retained original? | equal, byte for byte | established |
| Q6 | What source revision, compiler, dependencies and invocation produced the deployed ELF historically? | unresolved | unresolved |

Q6 is the honest fence. The repo's recipe is a reconstruction and is
labeled as such by its own packet. The dependency-exactness follow-up
searched Donate.gg documentation, the CherryDevelopmentOrg public
inventory, exact searches, Software Heritage, the Wayback Machine and
Halborn's public catalog and recovered no artifact-linked source or
assessed commit; the embedded source URL returns 404 (a 404 does not
prove deletion). This package's 2026-10-28 searches
(`evidence/search_log.json`) extend that record without changing it:
GitHub code search binds the address only to the Pump Fees IDL and to
this repo's own packets, and no public source repository for the
program itself surfaced. The ELF carries 26 local Rust source paths
and no `.comment` section or exact compiler version string. What
would close Q6 is named in the search log: a publisher-owned source
revision or archived build manifest tied to this program, or a
published source whose fresh build reproduces the ELF extent hash.

## Bounds

- Chain facts are public-RPC finalized observations, not cryptographic
  inclusion proofs (the allocation packet's own caveat, kept).
- Runtime coverage (privileged successes, allocator and borrow
  behavior) is a separate REMAINING-WORK requirement and is out of
  scope here.
- No source attribution is manufactured to fill Q6, and no
  organizational attribution is guessed for Q2 or Q4.

## Verification

```sh
python3 research/relay-provenance/verify.py
```

The checker runs offline against the evidence in this folder: it
re-checks the register against the chain-state and history evidence,
the capacity ladder, the authority chain in the two parsed endpoint
transactions, and the pinned source values. Reviewers can re-run the
live reads with `evidence/refresh_chain.py`, which submits nothing.

## Sources (pinned at 3719d910)

| File | Blob SHA | Used for |
| --- | --- | --- |
| `docs/REMAINING-WORK.md` | `632c81b1907257eb1ee5d605ff8d51de83564b0c` | the open Relay provenance requirement |
| `docs/RECONSTRUCTION-STATUS.md` | `cc109483f62815beee023251bc47af83bc1ad3dd` | recommended order #1 |
| `docs/COMPLETION.md` | `45d0586ee6a007fa985457aa274772d0abddd89b` | current checkpoint; stopped-lane list (this item is not in it) |
| `docs/SCOPE.md` | `a43a2d1dd764f828e8fb2b0a1f5e8c43bd6451bb` | dependency table values; ownership unresolved |
| `localnet/relay/README.md` | `6ee45111d1e592b99e79088461c069dec2962f4b` | self-identification, IDL account, embedded metadata |
| `repro/donation-relay/allocation-provenance/README.md` | `1d0ba82893b02404aa86d3f38fff735439bb08c7` | the 13-event capacity history |
| `repro/donation-relay/allocation-provenance/report.json` | `ae4bf541e24a74ee804fc1b7b65d053e01f941e0` | retained event and capacity records |
| `repro/donation-relay/linked-elf-reproduction/README.md` | `30d3bb86afecaee66df1da8e200259d3a6257e5c` | reconstructed recipe; historical recipe unproved |
| `repro/donation-relay/canonical-exact-selection/README.md` | `30e6321c5cf7d1f15bd391415bb757a94084592f` | canonical selection; provenance not claimed |
| `repro/pump/dependency-exactness/donation-relay-provenance-followup/README.md` | `bd465dad30c54f675f3688c5538692f9e28366d1` | prior source-provenance search, negative result |
| `research/README.md` | `ee6c5b10b0e53ebfa8d6dbf1251846c6564777d7` | research folder conventions |

Prepared by TaoBot. All chain work was read-only finalized RPC reads.
