#!/usr/bin/env python3
"""Triplet loss sobre embeddings para mejorar separación kNN."""
import os, sys, json, time, math, random
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

ROOT = Path('/work'); PATTERNS = ROOT / 'dataset/patterns'
DEVICE = torch.device('cuda')

# ── Dataset con triplet mining ──────────────────────────────────────────
class TripletDS(Dataset):
    def __init__(self, pat, max_sp=50):
        self.X=[]; self.Y=[]; self.sp_ranges={}
        dirs = sorted([d for d in pat.iterdir() if d.is_dir()])
        pos = 0
        for li, d in enumerate(dirs):
            ef = d/'embeddings.npy'
            if not ef.exists(): continue
            e = np.load(ef).astype('float32')
            e = e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)
            n = min(len(e), max_sp)
            if n < 5: continue
            idx = np.random.RandomState(li).permutation(len(e))[:n]
            self.X.append(e[idx]); self.Y.extend([li]*n)
            self.sp_ranges[li] = (pos, pos+n)
            pos += n
        self.X = np.concatenate(self.X); self.Y = np.array(self.Y)
        self.nc = len(self.sp_ranges)
        print(f'{len(self.X)} samples, {self.nc} classes', flush=True)
    
    def __len__(self): return len(self.X) * 3  # oversample triplets
    
    def __getitem__(self, i):
        # Anchors: random
        aidx = random.randint(0, len(self.X)-1)
        albl = int(self.Y[aidx])
        # Positive: same class
        sr, er = self.sp_ranges[albl]
        pidx = sr + random.randint(0, er-sr-1)
        while pidx == aidx: pidx = sr + random.randint(0, er-sr-1)
        # Negative: different class
        nidx = random.randint(0, len(self.X)-1)
        while int(self.Y[nidx]) == albl: nidx = random.randint(0, len(self.X)-1)
        return (torch.tensor(self.X[aidx]), torch.tensor(self.X[pidx]),
                torch.tensor(self.X[nidx]))

# ── Modelo ──────────────────────────────────────────────────────────────
class TripletProj(nn.Module):
    def __init__(self, dim=768, r=32):
        super().__init__()
        scale = 32/r
        self.A = nn.Parameter(torch.zeros(r, dim)); self.B = nn.Parameter(torch.zeros(dim, r))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5)); nn.init.zeros_(self.B)
        self.scale = scale
    def forward(self, x):
        return x + (x @ self.A.T @ self.B.T) * self.scale  # residual

# ── Train ───────────────────────────────────────────────────────────────
def main():
    ds = TripletDS(PATTERNS)
    ld = DataLoader(ds, 256, shuffle=True, num_workers=2)
    dim = ds.X.shape[1]; print(f"Embedding dim: {dim}", flush=True); model = TripletProj(dim, r=32).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    sch = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(opt, T_0=20, T_mult=2)
    
    margin = 0.3
    best_loss = float('inf')
    pat_cnt = 0
    
    for ep in range(200):
        model.train(); tl = 0; t0 = time.time()
        for a,p,n in ld:
            a,p,n = a.to(DEVICE), p.to(DEVICE), n.to(DEVICE)
            a = F.normalize(model(a), dim=1)
            p = F.normalize(model(p), dim=1)
            n = F.normalize(model(n), dim=1)
            pos_dist = (a-p).pow(2).sum(1)
            neg_dist = (a-n).pow(2).sum(1)
            loss = F.relu(pos_dist - neg_dist + margin).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            tl += loss.item()
        
        avg_loss = tl/len(ld)
        sch.step()
        if ep % 10 == 0:
            print(f'E{ep:3d} loss={avg_loss:.4f} lr={sch.get_last_lr()[0]:.2e} {time.time()-t0:.0f}s', flush=True)
        
        if avg_loss < best_loss - 0.0001:
            best_loss = avg_loss; pat_cnt = 0
            torch.save(model.state_dict(), ROOT/'dataset/triplet_best.pt')
        else:
            pat_cnt += 1
            if pat_cnt >= 30: 
                print(f'Early stop ep{ep}', flush=True); break
    
    print(f'Best loss: {best_loss:.4f}', flush=True)

if __name__=='__main__': main()
