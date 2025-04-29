#!/bin/bash

set -euo pipefail

FILTER_SOURCE=/etc/bird/peers.tsv
FILTER_OUTPUT=/etc/bird/filter_irr.conf

tmpfile="$(mktemp /tmp/bird-filter.XXXXXX)"
cleanup() {
  rm -f "$tmpfile"
}
trap cleanup EXIT

grep -v '^#' "$FILTER_SOURCE" | while IFS=$'\t ' read -r -a line; do
  name="${line[0]:-}"
  asset="${line[1]:-}"
  if [ -z "$name" ] || [ -z "$asset" ]; then
    echo "Malformed line found" 1>&2
    continue
  fi

  bgpq4 -4Ab -m24 -R24 "$asset" -l "define IRR_${name}_V4"
  bgpq4 -6Ab -m48 -R48 "$asset" -l "define IRR_${name}_V6"
  bgpq4 -tb "$asset" -l "define IRR_${name}_ASN"
done > "$tmpfile"

mv "$tmpfile" "$FILTER_OUTPUT"
chmod a+r "$FILTER_OUTPUT"
