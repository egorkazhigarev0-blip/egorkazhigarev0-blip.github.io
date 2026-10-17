#!/bin/bash
# Ставит шрифты Google (Oswald, Cormorant, Unbounded, Manrope и др.) для набросков. Повторный запуск безопасен.
set -e
DEST=/usr/share/fonts/truetype/gf
if fc-list | grep -q "$DEST/Geologica"; then echo "fonts ok"; exit 0; fi
TMP=$(mktemp -d)
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts "$TMP/gf"
git -C "$TMP/gf" sparse-checkout set ofl/oswald ofl/cormorant ofl/unbounded ofl/manrope ofl/golostext ofl/ptsans ofl/montserrat ofl/playfairdisplay ofl/geologica
mkdir -p "$DEST" && cp "$TMP"/gf/ofl/*/*.ttf "$DEST"/ && fc-cache -f >/dev/null
echo "fonts installed"
