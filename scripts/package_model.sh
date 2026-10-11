#!/bin/bash
# Package reconstruction artefacts (prototypes + JSON). No photos, no embeddings.npy.
set -e
OUTDIR="./model_package"
rm -rf "$OUTDIR"
mkdir -p "$OUTDIR/patterns" "$OUTDIR/data"
cp -a data/calibration.json data/target_species.json data/geo_priors.json "$OUTDIR/data/" 2>/dev/null || true
find data/patterns -name prototype.npy | while read -r f; do
  species=$(basename "$(dirname "$f")")
  mkdir -p "$OUTDIR/patterns/$species"
  cp "$f" "$OUTDIR/patterns/$species/"
done
tar -czf biofauna_prototypes.tar.gz -C "$OUTDIR" .
echo "Done: biofauna_prototypes.tar.gz ($(du -h biofauna_prototypes.tar.gz | cut -f1))"
