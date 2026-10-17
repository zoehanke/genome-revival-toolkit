# S0 probe results

Measured 2026-10-16. Windows 11 build 26200, Python 3.12.4. Synthetic data only.
These scripts are development probes, excluded from runtime and any package.
Raw measurements: ignored `probes/runs/p1.json`, `p2.json`, `p3.json`.

## P1: process termination and journal tail

Command: `python -X utf8 -B probes/p1_journal.py`

Method: seed 20261016; 200 separate spawned children. Each serializes an event,
makes one write, flushes and fsyncs. Parent waits for the first acknowledged fsync,
then kills after a seeded random delay of 0–35 ms. Padding sizes: 64, 512, 4096,
65536 bytes. Reader recomputes sequence numbers, predecessors and event hashes;
only a damaged final line may be truncated, followed by `journal.recovered`.
Probe used an explicit zero digest as its initial boundary. D9 now fixes the
production initial prev to the same 64 zeroes; the original P1 measurements are retained. Serialization is an ASCII/safe-integer subset with
known JCS-equivalent bytes; stdlib JSON is **not** accepted as a general JCS library.

Acceptance: all 200 trials retain every acknowledged fsync, have an intact chain,
and either retain the complete tail or recover only the incomplete final event.

| Measurement | Result |
|---|---:|
| Killed child processes | 200 |
| Trial failures | 0 |
| Naturally torn tails observed | 0 |
| Bytes discarded in killed-process trials | 0 |
| Retained events per trial, min/max | 2 / 123 |
| Total trial wall time | 43.038155 s |
| Phase observed before kill: serialization / write / flush / fsync | 44 / 1 / 6 / 149 |

The observed phase is sampled before termination, not a guarantee of the precise
instruction at which the OS stopped the process. No power failure was tested.

Independent corruption controls: 20-byte partial tail discarded, one prior event
retained; bad final-event digest discarded 545 bytes, one prior event retained;
corrupt middle event rejected with file unchanged. All three behaved as constructed.
These controls simulate torn/corrupted bytes; none came from the 200 kill trials.

| Events | Bytes | Append, fsync every event | Whole-chain validation |
|---:|---:|---:|---:|
| 10,000 | 5,478,894 | 8.156259 s | 0.406910 s |
| 100,000 | 54,888,895 | 58.152182 s | 3.414747 s |

Outcome: **PASS for this process-crash probe**. Tail recovery has constructed
controls, but naturally torn-tail recovery and power-loss durability remain
unobserved. No storage backend was changed. This is not INV-E5 runtime acceptance.

## P2: Windows directory publication

Command: `python -X utf8 -B probes/p2_rename.py`

Method: stage and destination on the same local temporary filesystem; Windows
CreateFileW read handles; os rename. Acceptance: destination is never overwritten,
and publication after releasing a reader retains exact candidate bytes.

| Case | First attempt | After release / retry | Result |
|---|---|---|---|
| Existing destination | WinError 183 | No retry; both trees retained, destination bytes unchanged | PASS |
| Reader with FILE_SHARE_DELETE (flags 7) | WinError 5 | One retry after closing handle succeeded | PASS |
| Reader without delete sharing (flags 3) | WinError 5 | One retry after closing handle succeeded | PASS |
| Simulated 0.20 s antivirus-style lock | WinError 5 on first 9 attempts | Attempt 10 succeeded; 20 ms spacing; 0.201246 s total | PASS |

Even delete sharing did not permit parent-directory rename in this environment.
S1 must account for a failed publication while retaining staging files. A retry
after handle release was necessary here; this probe does not add retry policy to
runtime. The short lock is a simulation, not a test of installed antivirus or
power-loss atomicity.

## P3: JCS implementation

Command (reported execution by Claude): `python -X utf8 -B probes/p3_jcs.py`

rfc8785==0.1.4 由 Claude 在隔离虚拟环境里安装（用户授权，仅供探针），原样运行 p3_jcs.py：Windows 上 3 个向量（UTF-16 键序、RFC 数字、控制字符）通过；Linux 未测；Codex 未复现该运行。

Source: user's S0 follow-up report on 2026-10-16. This is attributed evidence,
not a Codex execution. No new Codex P3 run record was generated. The earlier
`probes/runs/p3.json` records Codex's original unavailable-dependency result;
it is preserved, not overwritten with another agent's measurements.

Library: rfc8785 0.1.4, Apache-2.0 (FACTS.md). Reported Windows vectors: 3 passed.
Linux vectors: 0 executed. Cross-platform byte equality remains unmeasured.
No dependency was downloaded or installed by Codex during this follow-up.

## Limits and decisions

| Verified | Simulated | Not done | Uncertain |
|---|---|---|---|
| Original Codex P1/P2 measurements; separately attributed Claude P3 Windows result | Constructed corruption; temporary antivirus-style handle lock | Codex P3 reproduction, Linux comparison, power loss, runtime implementation | Cross-platform JCS equality and behavior on other filesystems |

Official GitLab CI 未执行. No GitHub CI exists for this local-only branch.
