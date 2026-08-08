#!/usr/bin/env python3
"""Re-embebe con BioCLIP-2.5 ViT-H (1024-dim)."""
import os, time, numpy as np
from pathlib import Path
from PIL import Image
import torch, open_clip

ROOT = Path(os.environ.get("YOLOFAUNA_ROOT", "/work"))
IMAGES = Path(os.environ.get("IMAGES_DIR", "/mnt/gpu/fotofauna-images"))
PATTERNS = ROOT / "dataset/patterns"
BATCH = 32
DEVICE = "cuda"

print(f"[vith] ROOT={ROOT}, IMAGES={IMAGES}", flush=True)
print("[vith] Cargando BioCLIP-2.5 ViT-H...", flush=True)
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2.5-vith14")
model = model.to(DEVICE).eval()
print(f"[vith] VRAM: {torch.cuda.memory_allocated()/1e9:.1f} GB", flush=True)

species_dirs = sorted(d for d in IMAGES.iterdir() if d.is_dir())
print(f"[vith] {len(species_dirs)} species to process", flush=True)

def embed_images(paths):
    tensors, valid = [], []
    for p in paths:
        try:
            tensors.append(preprocess(Image.open(p).convert("RGB")))
            valid.append(p)
        except: pass
    if not tensors: return np.zeros((0,1024),dtype=np.float32), []
    batch = torch.stack(tensors).to(DEVICE)
    with torch.no_grad():
        emb = model.encode_image(batch)
        emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().astype(np.float32), valid

total_imgs, total_spp = 0, 0
t0 = time.time(); last = t0

for sp_dir in species_dirs:
    slug = sp_dir.name
    images = sorted(list(sp_dir.glob("*.jpg")) + list(sp_dir.glob("*.jpeg")) + list(sp_dir.glob("*.png")))
    if len(images) < 2: continue
    pat_dir = PATTERNS / slug; pat_dir.mkdir(parents=True, exist_ok=True)
    all_embs = []
    for i in range(0, len(images), BATCH):
        embs, _ = embed_images(images[i:i+BATCH])
        if len(embs) > 0: all_embs.append(embs)
    if not all_embs: continue
    all_embs = np.concatenate(all_embs, axis=0)
    np.save(pat_dir / "embeddings.npy", all_embs)
    proto = all_embs.mean(0); proto = proto / (np.linalg.norm(proto) + 1e-9)
    np.save(pat_dir / "prototype.npy", proto.astype(np.float32))
    total_imgs += len(all_embs); total_spp += 1
    now = time.time()
    if now - last > 30 or total_spp == len(species_dirs):
        e = now - t0; r = total_imgs/e if e>0 else 0
        eta = (len(species_dirs)-total_spp)*(e/max(1,total_spp))
        print(f"[vith] {total_spp}/{len(species_dirs)} spp, {total_imgs} imgs, {r:.0f} img/s, ETA {eta/60:.0f}min", flush=True)
        last = now

print(f"\n[vith] DONE: {total_spp} species, {total_imgs} images in {(time.time()-t0)/60:.0f} min", flush=True)
