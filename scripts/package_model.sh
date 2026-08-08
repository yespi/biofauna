#!/bin/bash
# Package YOLOFauna model for distribution (~75 MB)
# Output: yolofauna_model_v1.tar.gz
set -e

OUTDIR="./model_package"
rm -rf "$OUTDIR"
mkdir -p "$OUTDIR/patterns" "$OUTDIR/data"

echo "Packaging YOLOFauna model..."

# Copy calibration and taxonomy
cp data/calibration.json "$OUTDIR/data/" 2>/dev/null
cp data/target_species.json "$OUTDIR/data/" 2>/dev/null
cp data/geo_priors.json "$OUTDIR/data/" 2>/dev/null

# Copy QLoRA checkpoint
BEST=$(ls data/finetune_checkpoints/qlora_best.pt 2>/dev/null || ls data/finetune_checkpoints/qlora_e*.pt 2>/dev/null | tail -1)
if [ -n "$BEST" ]; then
    cp "$BEST" "$OUTDIR/data/qlora_model.pt"
fi

# Copy prototype embeddings (only .npy, not images)
find data/patterns -name "prototype.npy" | while read f; do
    species=$(basename $(dirname "$f"))
    mkdir -p "$OUTDIR/patterns/$species"
    cp "$f" "$OUTDIR/patterns/$species/"
done

# Create archive
tar -czf yolofauna_model_v1.tar.gz -C "$OUTDIR" .
SIZE=$(du -h yolofauna_model_v1.tar.gz | cut -f1)
echo "Done: yolofauna_model_v1.tar.gz ($SIZE)"
