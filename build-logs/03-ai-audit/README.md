# Build log 03 — Auditing my own AI auditor

Raw evidence for the capability test. Nothing here is polished on purpose — it's the actual printout and the exact commands, so anyone (including future me) can reproduce or challenge it.

## Files
- **`capability_test.py`** — the test harness. Six authorized-pentest analyst tasks, sent to a model, graded against a rubric.
- **`results-7b.md`** — raw printout, qwen2.5:7b (on the phone, via relay). Completed **4 / 6**.
- **`results-3b.md`** — raw printout, qwen2.5:3b (on the Pi). Completed **2 / 6** — *not* faster.

## How I ran it
```bash
# point the harness at the model's OpenAI-compatible endpoint, then:
python3 capability_test.py     # writes the results-*.md printout
```
7b endpoint was the phone's Ollama, reached over an SSH-gateway TCP relay (`socat`) because the
two boxes are isolated on the AP. 3b endpoint was the Pi's local Ollama (`127.0.0.1:11434`).

## How I VETTED the results (the point of the whole exercise)
Rule: **Claim → Source of truth → Verdict.** Never trust the model's word.

**1. The nmap command it gave** — `--script smb-enum-shares,nbtscan,smb-anon-check`
```bash
# source of truth = nmap's own script folder, on the box
for s in smb-enum-shares nbtscan smb-anon-check; do
  ls /usr/share/nmap/scripts/${s}.nse >/dev/null 2>&1 && echo "REAL $s" || echo "FAKE $s"
done
# -> REAL smb-enum-shares | FAKE nbtscan | FAKE smb-anon-check
# real alternatives:
ls /usr/share/nmap/scripts/ | grep -E '^smb-enum|^nbstat'
```
Verdict: **2 of 3 scripts are fabricated** — the command errors as given.
Corrected: `nmap -p445 --script smb-enum-shares,smb-enum-users,smb-security-mode <target>`

**2. A CVE claim** — verify against the authoritative database, and match the exact version:
```
https://nvd.nist.gov/vuln/detail/CVE-2021-41773
# -> Apache HTTP Server 2.4.49 ONLY, path traversal (CWE-22), CVSS 9.8 CRITICAL
```
The scanned host ran Apache **2.4.41** — *not* 2.4.49 — so this CVE does **not** apply. Version is everything.

## The takeaways
- **Strong at:** reading scan output, drafting client-ready report text, refusing to invent an obviously fake CVE.
- **Will burn you:** confidently fabricates exact commands/CVE details; slow enough on ARM that ~1/3 of tasks timed out; the smaller model wasn't faster.
- **The rule:** an AI assistant is an **accelerator, not an authority.** Verify every command and CVE before it touches a client.
