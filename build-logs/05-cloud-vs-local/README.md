# GhostGrid Build Log 05 — Cloud vs Local AI (measured on the fleet)

**Date:** 2026-07-17
**Author:** Zach (stackzac22)
**Thesis:** Local AI isn't "worse cloud" — it's a different tool. This log measures
*my own* stack against cloud so the trade-off is real numbers, not vibes.

The rule GhostGrid runs on: **AI is an accelerator, not an authority. Verify every
command and CVE.** This log is the proof of why.

---

## What "local" is here (the box under test)
- **X1** — ThinkPad X1 Carbon, Intel i5-6200U, **4 threads, no usable GPU**, 7.6 GB RAM.
- Model: **qwen2.5:1.5b** (1.0 GB) via Ollama, CPU inference.
- Voice engines: **Whisper** (STT) + **Piper** (TTS) on `the Pi 4B node` (Pi, the private link a local address).
- Everything on **the private link**, zero cloud, zero internet dependency.

## What "cloud" is here
- A frontier hosted model (this assistant, Claude-class). Numbers below for cloud are
  **representative/typical**, not measured on-box (no API key wired in) — labeled as such.

---

## MEASURED: local qwen2.5:1.5b on X1 (CPU only)

| Prompt | Wall time | Throughput | Correct? |
|---|---|---|---|
| Factual — "default SSH port?" | 1.8 s | 13.3 tok/s | ✅ port 22 |
| Coding — "bash: files >100MB under /var" | 2.5 s | 13.4 tok/s | ✅ `find /var -type f -size +100M` |
| Reasoning — 3-switches/3-bulbs puzzle | 6.2 s | 13.0 tok/s | ❌ garbled, wrong method |
| Pentest — "what does nmap -sV do + a risk" | 51.7 s | 11.6 tok/s | ❌ **said "-sV = Script Version"** (false; it's service/**version** detection) + rambled 586 tokens |

- **Cold model load:** 4.0 s (first request after idle). Warm gen steady ~**13 tok/s**.
- **Verdict:** nails short factual/command tasks fast; **falls apart on reasoning and
  invents authoritative-sounding wrong facts** on domain questions. Exactly the failure
  mode that bites in pentest work — confident, wrong, verbose.

## MEASURED: local voice pipeline (all the private link, no cloud)
- **Whisper STT:** ~2.8 s for a short spoken command.
- **Brain (1.5b):** ~1–9 s depending on answer length.
- **Piper TTS:** connect 0.00 s, **first audio 0.82 s** over the private link (a local address).
- End-to-end press→speech is dominated by the brain, not the ears/voice.

## MEASURED: 1.5b vs 3b vs 7b head-to-head (2026-07-17, all the private link)
Ran the SAME four prompts across all three local models the moment the-one came back
on the private link (a local address). 1.5b on the X1 (x86); 3b + 7b on the-one (ARM, no GPU).

**Speed — wall seconds per prompt:**

| Prompt | 1.5b (x86) | 3b (ARM) | 7b (ARM) | Cloud* |
|---|--:|--:|--:|--:|
| Factual (SSH port) | 1.6 | 5.5 | 10.8 | 7.5 |
| Coding (find cmd) | 1.8 | 7.5 | 16.6 | 11.9 |
| Reasoning (puzzle) | 14.9 | 32.5 | 46.4 | 12.5 |
| Pentest (nmap -sV) | 38.2 | 44.1 | 71.6 | 12.3 |
| Cold load | 0.4 | 1.3 | **27.9** | — |
| Throughput | ~13 tok/s | ~5 tok/s | ~2.3 tok/s | — |

*Cloud measured live via the `claude` CLI (frontier model), same prompts. **Carries a
~7 s fixed CLI startup cost** — a trivial one-liner took 7.5 s — so these are an UPPER
BOUND; a raw API call would be ~1–3 s. Generation itself is fast: the long pentest answer
(~12.3 s) took about the same as the short factual one, so nearly all of cloud's time is
the fixed startup, not thinking.

**Quality — correct?**

| Prompt | 1.5b | 3b | 7b | Cloud |
|---|:--:|:--:|:--:|:--:|
| Factual | ✅ | ✅ | ✅ | ✅ |
| Coding | ✅ | ✅ | ✅ | ✅ |
| Reasoning puzzle | ❌ garbled | ⚠️ flawed (leaves 2 bulbs lit) | ✅ grasped heat trick | ✅ |
| Pentest fact | ❌ "-sV = OS detection" | ✅ correct | ✅ best + names legal risk | ✅ |

**Findings:**
1. **Easy tasks → tiny model wins.** All sizes correct on factual/coding, so 1.5b's
   speed makes it the pick. No reason to pay 7b's 71s for a port number.
2. **Hard tasks → quality climbs with size, as hoped.** 1.5b wrong on nmap, 3b right,
   7b right *and* volunteered the authorization risk. Only 7b cracked the logic puzzle.
3. **Speed collapses inversely — and CHIP matters as much as model.** 1.5b @ ~13 tok/s
   on x86; 3b/7b @ 5 / 2.3 tok/s on the ARM (no GPU). 1.5b gave a WRONG pentest answer
   in 38s; 7b gave the RIGHT one in 72s.
4. **Cloud owns the frontier — measured, correct on all four.** ~7.5–12.5s via CLI
   (mostly fixed startup; a raw API call ≈1–3s). The ~7s fixed cost means the tiny local
   1.5b actually BEATS cloud on trivial prompts (1.6s vs 7.5s for a port number) — but on
   the HARD prompts cloud is both faster AND right (12.3s + correct on nmap vs the 7b's
   71.6s, or the 1.5b's fast-but-wrong 38.2s). Local's real edge is privacy / offline /
   $0-per-request, not quality-per-second.

**Routing rule:** 1.5b = quick/factual/voice · 3b = the sweet spot when you want it right
without the 7b tax · 7b = genuinely hard / correctness-critical (expect 40–70s on ARM) ·
cloud = hard *and* online.

## Prior data note
- Earlier estimate of 7b (~39s / 72s cold) confirmed by the measured run above.
  7b stays on-demand only — too slow for interactive voice.

---

## The trade-off, straight

| Axis | Local (self-hosted) | Cloud (hosted frontier) |
|---|---|---|
| **Latency** | Low & predictable on small models (no network); slow if model too big for the CPU | ~1–3 s first token, then very fast streaming |
| **Quality / accuracy** | Small models miss reasoning, hallucinate facts | Strong reasoning, far fewer factual misses |
| **Cost** | Sunk hardware + electricity; **$0/marginal request** | Per-token billing; scales with usage |
| **Privacy** | **Data never leaves the network** | Prompt leaves your network to a third party |
| **Offline / resilience** | **Works with the internet down** | Dead without connectivity |
| **Control / customization** | Full — model, prompt, wiring, LEDs, voice | Limited to the API surface |
| **Maintenance** | You own the uptime (dead battery = dead brain) | Someone else's problem |
| **Ceiling** | Capped by your silicon (no GPU here = small models only) | Effectively frontier-class |

---

## When to use which (mapped to the fleet)

- **Local wins:** always-on house/Mom voice, quick commands, offline resilience,
  anything privacy-sensitive, cheap repetitive tasks. → small model, on-device.
- **Cloud wins:** hard reasoning, code review/planning, **anything correctness-critical**
  (CVEs, exploit logic, config you'll actually run). → escalate.
- **The GhostGrid pattern (hybrid):** local-first for speed + privacy, **escalate to a
  bigger model when the task is hard**, and *verify* whatever comes back. Local gives you
  a private, always-on floor; cloud is the ceiling you reach for on demand.

**One-line takeaway:** Local is a *fast, private, offline floor*. Cloud is the *smart
ceiling*. The 1.5b confidently told me `-sV` means "Script Version" — that's the whole
reason the rule is *verify, don't trust*.

---

## The verdict: cloud-first for the work that matters
After all the local pride — the honest call is **go cloud for real thinking.**

- **Default to cloud when it counts.** Learning, shipping code, pentest analysis, anything
  where a wrong answer costs you — cloud was right on all four prompts, fast, and caught
  what the local models fumbled. A hobbyist runs everything local to prove they can; a pro
  reaches for the sharpest tool and doesn't feel weird about it. That's the daily driver
  for real work.
- **Keep local for what local is FOR:** the always-on house/Mom voice, quick offline
  commands, and the private stuff that shouldn't leave the network. Not lesser — the right
  tool for those jobs, and it works when the grid's down.
- **The local build is the gym.** You don't run it because it's the best brain; you run it
  because doing it yourself is how you became the person who *can*. That's worth more to the
  career than the answers it spits out.

**One line:** use cloud without guilt for the real work, keep local because you own it and
it's teaching you — and either way, **verify.** Point your brain at cloud when it counts;
let local run the house and the reps.

---
*Raw benchmark: `scratchpad/bench_local.py`, `bench_multi.py`, `bench_cloud.py`. Local box:
X1 i5-6200U CPU-only (1.5b); the-one ARM (3b/7b). Cloud via `claude` CLI.*
