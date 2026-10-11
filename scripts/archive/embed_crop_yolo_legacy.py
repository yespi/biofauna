import os
os.environ["YOLO_SETTINGS_DIR"] = "/tmp"
os.environ["YOLO_CONFIG_DIR"] = "/tmp"  
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"
#!/usr/bin/env python3
"""Re-embed con recorte YOLO (+7.1pt en criticas). Lee del archive, guarda en patterns/."""
import os, sys, time, json, shutil
import numpy as np
from pathlib import Path
from datetime import datetime

ROOT = Path("/work")
PAT = ROOT / "dataset/patterns"
ARCHIVE = Path("/mnt/gpu/fotofauna-images")
CROP_MODEL = ROOT / "dataset/yolo26n-seg.pt"
MIN_IMGS = 10
BATCH = 20

def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)

log("Cargando detector YOLO...")
from ultralytics import YOLO
yolo = YOLO(str(CROP_MODEL))
log("YOLO listo")

def crop_organism(img_path, model):
    try:
        results = model(str(img_path), verbose=False)
        if not results or not results[0].boxes: return None
        box = results[0].boxes[0].xyxy[0].cpu().numpy()
        from PIL import Image
        img = Image.open(img_path).convert("RGB")
        W, H = img.size
        x1, y1, x2, y2 = box
        m = 0.10
        bw, bh = x2-x1, y2-y1
        x1 = max(0, x1 - bw*m); y1 = max(0, y1 - bh*m)
        x2 = min(W, x2 + bw*m); y2 = min(H, y2 + bh*m)
        return img.crop((int(x1), int(y1), int(x2), int(y2)))
    except:
        return None

log("Cargando BioCLIP...")
import torch
import open_clip
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2")
model = model.to("cuda").eval()
log(f"BioCLIP en GPU, {sum(p.numel() for p in model.parameters())/1e6:.0f}M params")

def embed_images(paths):
    from PIL import Image
    vecs = []
    for i in range(0, len(paths), BATCH):
        batch = []
        for p in paths[i:i+BATCH]:
            try:
                if isinstance(p, (str, Path)): img = Image.open(str(p)).convert("RGB")
                else: img = p
                batch.append(preprocess(img))
            except: pass
        if not batch: continue
        with torch.inference_mode():
            t = torch.stack(batch).to("cuda")
            f = model.encode_image(t); f = f / f.norm(dim=-1, keepdim=True)
        vecs.append(f.cpu().numpy().astype("float16"))
    return np.concatenate(vecs) if vecs else None

# Backup
BACKUP = ROOT / "dataset/patterns_full_backup"
if not BACKUP.exists():
    log("Backup patterns/...")
    shutil.copytree(PAT, BACKUP, dirs_exist_ok=True)
    log("Backup OK")

archive_dirs = sorted([d for d in ARCHIVE.iterdir() if d.is_dir()])
log(f"Archive: {len(archive_dirs)} especies")

total = total_imgs = total_crops = 0
t0 = time.time()

for d in archive_dirs:
    slug = d.name
    pd = PAT / slug
    if (pd / ".crop_done").exists(): continue
    
    jpgs = sorted(list(d.glob("*.jpg")) + list(d.glob("*.jpeg")))
    if len(jpgs) < MIN_IMGS: continue
    
    crops = []
    for jpg in jpgs:
        try:
            c = crop_organism(str(jpg), yolo)
            if c is not None:
                crops.append(c); total_crops += 1
            else:
                from PIL import Image; crops.append(Image.open(jpg).convert("RGB"))
        except: continue
    
    if not crops: continue
    
    emb = embed_images(crops)
    if emb is None: continue
    
    pd.mkdir(parents=True, exist_ok=True)
    np.save(str(pd/"embeddings.npy"), emb)
    proto = emb.astype("float32").mean(0)
    proto /= (np.linalg.norm(proto)+1e-9)
    np.save(str(pd/"prototype.npy"), proto.astype("float16"))
    (pd/".crop_done").touch()
    
    total += 1; total_imgs += len(jpgs)
    elapsed = time.time()-t0
    log(f"[{slug}] {len(crops)} embeds ({total} spp, {total/(elapsed/3600):.0f}/h)")

log(f"=== FIN: {total} spp, {total_imgs} imgs, {total_crops} crops ===")
