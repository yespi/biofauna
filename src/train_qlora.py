"""
QLoRA fine-tuning de BioCLIP ViT-L para BioFauna.
- Cuantiza el backbone ViT a 4-bit (NF4) → ~2.5 GB en vez de ~9.6 GB.
- Inserta adaptadores LoRA manuales en los últimos 4 bloques del transformer.
- Proj head (1024→768) se mantiene en fp16 y se entrena.
- Entrena con triplet loss sobre crop embeddings.
- VRAM objetivo: <11 GB (entra en RTX 3060 12 GB).

Referencia: BIOFAUNA_PLAN_MAESTRO.md Sec.3.A
"""

import json, os, sys, time, math
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import open_clip
import bitsandbytes as bnb

ROOT = Path("/work")
DS = ROOT / "dataset"
PATTERNS = Path("/mnt/gpu/fotofauna-images")  # SSD con las imágenes completas
OUT = DS / "finetune_checkpoints"
OUT.mkdir(exist_ok=True)

# ── Config ──────────────────────────────────────────────────────────────────
BATCH_SIZE = 16
EPOCHS = 30
MARGIN = 0.8
LR = 1e-4
WEIGHT_DECAY = 1e-5
LORA_R = 8
LORA_ALPHA = 16
LORA_BLOCKS = 4
DEVICE = "cuda"

# ── Dataset de crops ────────────────────────────────────────────────────────
class CropDataset(Dataset):
    def __init__(self, patterns_dir, preprocess, max_per_sp=4):
        self.preprocess = preprocess
        self.pairs = []
        sp_idx = 0
        species_dirs = sorted(d for d in patterns_dir.iterdir() if d.is_dir())
        for d in species_dirs:
            jpgs = sorted(list(d.glob("*.jpg")) + list(d.glob("*.jpeg")) + list(d.glob("*.png")))
            if len(jpgs) < 2:
                continue
            jpgs = jpgs[:max_per_sp]
            for i in range(len(jpgs)):
                for j in range(i + 1, len(jpgs)):
                    self.pairs.append((str(jpgs[i]), str(jpgs[j]), sp_idx))
            sp_idx += 1
        print(f"[dataset] {len(self.pairs)} pares de {sp_idx} especies")
    
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        pa, pp, sp = self.pairs[idx]
        try:
            from PIL import Image
            img_a = self.preprocess(Image.open(pa).convert("RGB"))
            img_p = self.preprocess(Image.open(pp).convert("RGB"))
        except Exception:
            img_a = torch.zeros(3, 224, 224)
            img_p = torch.zeros(3, 224, 224)
        return img_a, img_p, sp

# ── Módulo Linear4bit + LoRA ────────────────────────────────────────────────
class Linear4bitLoRA(nn.Module):
    def __init__(self, in_features, out_features, bias=True, r=LORA_R, alpha=LORA_ALPHA):
        super().__init__()
        self.linear = bnb.nn.Linear4bit(in_features, out_features, bias=bias,
                                         quant_type="nf4")
        self.lora_A = nn.Linear(in_features, r, bias=False)
        self.lora_B = nn.Linear(r, out_features, bias=False)
        nn.init.kaiming_uniform_(self.lora_A.weight, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B.weight)
        self.scaling = alpha / r
    
    def forward(self, x):
        base = self.linear(x)
        lora = self.scaling * self.lora_B(self.lora_A(x.to(torch.float32)))
        return base + lora.to(base.dtype)
    
    @property
    def weight(self):
        return self.linear.weight
    
    @property
    def bias(self):
        return self.linear.bias
    
    def set_quantized_weight(self, weight_fp):
        self.linear.weight = bnb.nn.Params4bit(
            weight_fp.detach().cpu(),
            require_grad=False,
            quant_type="nf4",
        )

# ── Construir modelo QLoRA ──────────────────────────────────────────────────
def build_qlora_model():
    print("[model] cargando BioCLIP-2...", flush=True)
    model, _, preprocess = open_clip.create_model_and_transforms(
        "hf-hub:imageomics/bioclip-2"
    )
    # Usar el modelo CLIP completo (incluye text y visual)
    # Solo modificamos model.visual (ViT-L)
    vit = model.visual
    
    # Congelar todo el modelo
    for p in model.parameters():
        p.requires_grad = False
    
    # Mantener proj head entrenable (es un Parameter, no un Linear)
    vit.proj.requires_grad = True
    print(f"[model] proj head: {vit.proj.shape} (entrenable)", flush=True)
    
    # Reemplazar lineales de los últimos LORA_BLOCKS con 4bit+LoRA
    blocks = vit.transformer.resblocks
    n_blocks = len(blocks)
    start_block = n_blocks - LORA_BLOCKS
    n_replaced = 0
    
    for bi in range(start_block, n_blocks):
        block = blocks[bi]
        
        # NOTA: out_proj NO se cuantiza — incompatible con MultiheadAttention
        # que pasa self.out_proj.weight a F.linear().
        
        # mlp.c_fc (FFN up)
        old = block.mlp.c_fc
        new = Linear4bitLoRA(old.in_features, old.out_features, bias=old.bias is not None)
        new.set_quantized_weight(old.weight.data)
        if old.bias is not None:
            new.linear.bias = nn.Parameter(old.bias.data.clone(), requires_grad=False)
        block.mlp.c_fc = new
        n_replaced += 1
        
        # mlp.c_proj (FFN down)
        old = block.mlp.c_proj
        new = Linear4bitLoRA(old.in_features, old.out_features, bias=old.bias is not None)
        new.set_quantized_weight(old.weight.data)
        if old.bias is not None:
            new.linear.bias = nn.Parameter(old.bias.data.clone(), requires_grad=False)
        block.mlp.c_proj = new
        n_replaced += 1
    
    print(f"[model] {n_replaced} capas reemplazadas en bloques {start_block}..{n_blocks-1}", flush=True)
    
    model = model.to(DEVICE)
    
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"[model] Parámetros: {trainable:,} entrenables / {total:,} totales ({trainable/total*100:.2f}%)", flush=True)
    
    # Verificar que encode_image funciona
    print("[model] verificando forward...", flush=True)
    model.eval()
    with torch.no_grad():
        dummy = torch.zeros(1, 3, 224, 224).to(DEVICE)
        out = model.encode_image(dummy)
    print(f"[model] encode_image output: {out.shape}", flush=True)
    
    return model, preprocess

# ── Triplet loss ─────────────────────────────────────────────────────────────
def triplet_loss(emb_a, emb_p, margin=MARGIN):
    batch = emb_a.shape[0]
    diff = emb_a.unsqueeze(1) - emb_p.unsqueeze(0)
    dist = (diff * diff).sum(dim=-1)
    pos = dist.diag()
    eye = torch.eye(batch, device=dist.device)
    neg = (dist + eye * 1e9).min(dim=1).values
    return (pos - neg + margin).clamp(min=0).mean()

# ── Training loop ────────────────────────────────────────────────────────────
def train():
    model, preprocess = build_qlora_model()
    
    dataset = CropDataset(PATTERNS, preprocess)
    if len(dataset) < BATCH_SIZE:
        print(f"[error] Dataset too small: {len(dataset)} pairs", flush=True)
        return
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True,
                        num_workers=2, pin_memory=True, drop_last=True)
    
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    print(f"\n[train] {EPOCHS} epochs, {len(loader)} batches/epoch", flush=True)
    print(f"[train] Initial VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB", flush=True)
    
    model.train()
    best_loss = float("inf")
    
    for epoch in range(1, EPOCHS + 1):
        epoch_loss = 0.0
        epoch_losses = []
        t0 = time.time()
        torch.cuda.reset_peak_memory_stats()
        
        for bi, (anchors, positives, _) in enumerate(loader):
            anchors = anchors.to(DEVICE)
            positives = positives.to(DEVICE)
            
            emb_a = model.encode_image(anchors)
            emb_p = model.encode_image(positives)
            
            emb_a = emb_a / emb_a.norm(dim=-1, keepdim=True)
            emb_p = emb_p / emb_p.norm(dim=-1, keepdim=True)
            
            loss = triplet_loss(emb_a, emb_p)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item(); epoch_losses.append(loss.item())
            
            if bi % 100 == 0:
                vram = torch.cuda.memory_allocated() / 1e9
                # Contar batches con loss=0 vs loss>0
                zero_frac = sum(1 for j in range(max(0, bi-100), bi+1) 
                               if j < len(epoch_losses) and epoch_losses[j] < 1e-6) / max(1, min(100, bi+1))
                print(f"  [{epoch:02d}] batch {bi:4d}/{len(loader):4d}  loss={loss.item():.4f}  ~{zero_frac:.0%} zeros  VRAM={vram:.2f} GB", flush=True)
        
        scheduler.step()
        avg_loss = epoch_loss / len(loader)
        elapsed = time.time() - t0
        vram = torch.cuda.memory_allocated() / 1e9
        peak = torch.cuda.max_memory_allocated() / 1e9
        print(f"[{epoch:02d}] loss={avg_loss:.4f}  VRAM={vram:.2f} GB (peak {peak:.2f} GB)  {elapsed:.0f}s", flush=True)
        
        ckpt = {
            "epoch": epoch,
            "loss": avg_loss,
            "model_state": model.state_dict(),
            "lora_config": {"r": LORA_R, "alpha": LORA_ALPHA, "blocks": LORA_BLOCKS}
        }
        torch.save(ckpt, OUT / f"qlora_e{epoch:02d}.pt")
        
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(ckpt, OUT / "qlora_best.pt")
    
    print(f"\n[done] best loss={best_loss:.4f}", flush=True)
    return best_loss

if __name__ == "__main__":
    train()
