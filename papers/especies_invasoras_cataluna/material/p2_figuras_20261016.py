#!/usr/bin/env python3
"""Figuras P1/P2: esfuerzo GBIF por grupo y forest plot GLMM (con y sin los 3 observadores principales)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
M = Path(__file__).parent; F = M / "figuras"
e = pd.read_csv(M / "esfuerzo_grupo_gbif_20261016.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
for g, d in e[e.year.between(2008, 2025)].groupby("grupo"):
    ax.plot(d.year, d.n.clip(lower=1), marker="o", ms=3, label=g)
ax.set_yscale("log"); ax.set_xlabel("Año"); ax.set_ylabel("Observaciones research grade (log)")
ax.legend(fontsize=7, ncol=2); ax.set_title("Esfuerzo independiente por grupo (GBIF, dataset iNaturalist RG, Cataluña GADM)", fontsize=9)
fig.tight_layout(); fig.savefig(F / "esfuerzo_grupo_gbif_20261016.png", dpi=160); plt.close(fig)
g = pd.read_csv(M / "glm_tendencias_glmm_20261016.csv"); g = g[(g.ventana == "2013-2025") & g.p.notna()].sort_values("RR_anual").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(8, 5.5)); y = np.arange(len(g))
col = ["#c0392b" if c == "decreciente" else ("#1e8449" if c == "creciente" else "#555") for c in g.clase]
ax.hlines(y, g.IC95_lo, g.IC95_hi, color=col); ax.scatter(g.RR_anual, y, color=col, zorder=3, label="GLMM (observador aleatorio)")
ax.scatter(g.RR_sin_top3, y + .25, marker="x", color="k", s=18, zorder=3, label="sin los 3 observadores principales")
ax.axvline(1, ls="--", c="k", lw=.8); ax.set_yticks(y); ax.set_yticklabels(g.especie, style="italic", fontsize=8)
ax.set_xscale("log"); ax.set_xticks([.7, .8, .9, 1, 1.2, 1.5, 2]); ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter()); ax.minorticks_off()
ax.set_xlabel("Razón de tasas anual (GLMM Poisson, offset log esfuerzo del observador en el grupo)"); ax.legend(fontsize=7, loc="lower right")
ax.set_title("Tendencia de detección 2013–2025 (GBIF-iNaturalist RG, Cataluña)\nrojo = descenso (q<0,05); verde = aumento (q<0,05); gris = sin tendencia", fontsize=9)
fig.tight_layout(); fig.savefig(F / "tendencias_glmm_20261016.png", dpi=160); plt.close(fig)
