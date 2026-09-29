#!/usr/bin/env bash
# make-qr.sh "<url>" "<name>"  -> PNG + SVG in ./qr/  (offline, via qrencode)
set -euo pipefail
url="${1:?usage: make-qr.sh <url> <name>}"
name="${2:?usage: make-qr.sh <url> <name>}"
out="$(dirname "$0")/qr"
mkdir -p "$out"
# high error-correction (-l H) so a logo can overlay later; margin 2, big modules
qrencode -o "$out/${name}.png" -s 12 -m 2 -l H "$url"
qrencode -t SVG -o "$out/${name}.svg" -m 2 -l H "$url"
echo "wrote $out/${name}.png  and  $out/${name}.svg  ->  $url"
