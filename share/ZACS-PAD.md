# Zac's Pad — QR launchers (public + per-client)

Two scannable landing pages, each behind a QR:

## 1. Public "Zac's Pad"
Someone scans your QR (card, sticker, phone) → a clean, mobile-friendly page with
**all your public links** (GhostGrid, socials, shop, contact, booking, etc.).
Think "link-in-bio," but yours and nicer.

## 2. Client launcher (tailorable)
A **per-client** page you grow with the engagement. For a client: their chosen
plan(s), a status line, how to reach you, maybe a "what's deployed" list. Each
client gets their **own** page + own QR; you edit it as the work grows.

## How it'll be built
- **Page:** a self-contained, theme-aware HTML launcher (loads fast, no tracking).
  Fastest path = publish as an **Artifact** → real shareable URL. Or host on your
  own GhostGrid/Caddy domain if you'd rather the link be `zacs.pad`-style.
- **QR:** generated locally with `qrencode` (offline, no third‑party QR service =
  "secure"). Helper: `deploy/make-qr.sh "<url>" "<name>"` → PNG + SVG in
  `deploy/qr/`. Re-run any time a link changes (the QR only holds the URL, so the
  page contents can change without reprinting the code).

## "Secure" notes (what that means here)
- QR encodes **only a URL** — no data leaks in the code itself.
- Generated **offline** (no sending your links to a QR website).
- Public page = only what you choose to make public. Client page = share the URL
  privately (unlisted); optionally gate it later.
- HTTPS on whatever host we use.

## What I need from you to build it
- [ ] The **public links** list (URL + label each) for Zac's Pad.
- [ ] Brand look: name to show ("Zac's Pad"? GhostGrid?), color vibe, a logo/emoji.
- [ ] Host choice: **Artifact URL** (fastest) or **your own domain**.
- [ ] For the client template: fields you want on every client page.

## Pipeline is ready
`deploy/make-qr.sh` is in place and a demo QR is generated — once you give me the
links + host choice, it's: build page → get URL → `make-qr.sh` → hand you the PNGs.
