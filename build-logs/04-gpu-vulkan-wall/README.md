# Build log 04 — Trying to GPU-accelerate Ragnar on a phone (and the wall I hit)

_Ragnar is my fully-local voice assistant (Whisper + a 7B model + Piper) — see Build log 01.
It runs on a rooted OnePlus 6T with 8GB of RAM, no cloud. This is the story of trying to make
it faster, and the honest wall I ran into._

---

## The itch

Ragnar's 7B model runs **CPU-only** on the phone. It works, but the 7B pegs all 8 cores and
takes the better part of half a minute to warm up. The phone has a GPU sitting right there —
an Adreno 630 — doing nothing for inference. So the plan: offload the model to the GPU with
**Vulkan** and get a free speed-up.

## What I found first (a good clue)

The phone's LLM runtime *already* had Vulkan support switched on — but it was silently falling
back to CPU. Turns out its GPU detection only ever looked for an NVIDIA card (which a phone
obviously doesn't have), failed, and quietly gave up. The actual Vulkan backend library was
never even installed. So step one wasn't "enable the GPU," it was "find out why it pretended
the GPU didn't exist."

Good news underneath that: the phone runs a full Linux (Kali/NetHunter), and the open-source
GPU driver stack (**Mesa's "Turnip" Vulkan driver**) was present and healthy — the GPU
enumerated cleanly as `Turnip Adreno (TM) 630`.

## Building the real thing

Rather than fight the existing runtime's missing pieces, I built the reference engine
(**llama.cpp**) from source on the phone itself, with the Vulkan backend turned on. That meant
installing a compiler toolchain, the Vulkan dev headers, a shader compiler, and the SPIR-V
headers — then a long compile on an 8-core phone. It built clean.

## The wall

Then I asked it to load the 7B model onto the GPU. It refused, with this:

> `ggml_vulkan: device Vulkan0 does not support 16-bit storage.`
> `error: failed to load model`

The model wouldn't even load, let alone run faster. (It was so insistent that just having the
Vulkan backend *loaded* broke the CPU path too, until I explicitly hid the GPU.)

## The twist — it's the *driver*, not the GPU

I almost wrote this off as "old GPU can't do it." Then I actually read the driver's feature
flags, and they contradicted themselves: the open-source **Turnip** driver advertises 16-bit
storage through the `VK_KHR_16bit_storage` *extension* (says **true**) but reports **false** in
the *core* Vulkan feature struct that llama.cpp checks. So llama.cpp sees "false" and bails —
even though the hardware can actually do it.

That reframed the whole thing. The Adreno 630 isn't the wall. **The wall is which driver you're
running:**

- On **Linux (NetHunter/Kali)**, where Ragnar lives, the GPU uses the open-source **Mesa
  Turnip** driver — and Turnip on this chip doesn't cleanly expose fp16 to apps.
- On **Android**, the exact same GPU uses **Qualcomm's proprietary driver**, which exposes fp16
  properly. That's how the phone-LLM apps that *do* use the GPU pull it off — they run on
  Android, not on the Linux side.

## Where it stands

**Ragnar stays on CPU for now** — it was already working. But "GPU is impossible on this phone"
turned out to be wrong: it's "GPU is impossible *on the driver my Linux slot uses*." The same
phone has an Android slot with the proprietary driver, which is worth testing as the place the
GPU actually earns its keep. The catch is the slots don't run at once, so it's a real
architecture question, not a flick of a switch.

Lesson filed: when a driver's feature flags disagree with each other, believe the failure but
question the *reason* — the wall moved from "hardware" to "driver," and that's a completely
different set of doors.

## Stack touched
`Vulkan / Mesa Turnip` · `Adreno 630` · `llama.cpp (from source)` · `GGUF` · `glslc / SPIR-V`
· `Kali / NetHunter` · `ollama`

---
_Filed under: walls worth hitting. A negative result is still a result._
