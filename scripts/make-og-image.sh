#!/bin/sh
set -eu

# Rebuild the social preview from the NMC3 poster.
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_image="$project_root/showcase/assets/posters/nmc3.jpg"
output_image="$project_root/showcase/assets/og-image.jpg"
tmp_image="${TMPDIR:-/tmp}/pdu-og-image.$$.jpg"
trap 'rm -f "$tmp_image"' EXIT

sips --resampleHeight 630 "$source_image" --out "$tmp_image" >/dev/null
sips --padToHeightWidth 630 1200 --padColor 111820 "$tmp_image" --out "$output_image" >/dev/null
sips -s formatOptions 82 "$output_image" >/dev/null
echo "wrote $output_image"
