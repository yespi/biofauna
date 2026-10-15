#!/usr/bin/env python3
"""Figuras corregidas tras la revisión (15-oct-2026). Sin GPU ni APIs. Entrada: CSV locales."""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib, matplotlib.ticker
matplotlib.use("Agg"); import matplotlib.pyplot as plt
M = Path(__file__).parent; F = M / "figuras"
eff = pd.read_csv(M / "esfuerzo_bioquest_anual.csv")
fig, ax = plt.subplots(figsize=(9, 4.2))
cols = ["#2a7fba" if y < 2026 else "#b0c4d4" for y in eff.year]
ax.bar(eff.year, eff.n_obs_caja_cat, color=cols)
ax.set_yscale("log"); ax.set_xlabel("Año"); ax.set_ylabel("Observaciones en la base BioQuest (escala log)")
ax.set_title("Esfuerzo: observaciones BioQuest en la caja de Cataluña (todos los taxones del catálogo)")
ax.text(2026, eff.n_obs_caja_cat.iloc[-1] * 1.3, "2026\nparcial", ha="center", fontsize=8)
fig.text(0.01, 0.01, "Base interna BioQuest (694 taxones), no total de iNaturalist/Minka; 2008 anómalo (858) y salto 2021-2024 pendientes de auditar.", fontsize=7)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(F / "esfuerzo_bioquest_catalunya.png", dpi=160); plt.close(fig)

g = pd.read_csv(M / "glm_tendencias_20261015.csv"); g = g[(g.ventana == "2013-2025") & g.p.notna()].sort_values("RR_anual")
fig, ax = plt.subplots(figsize=(8, 6))
y = np.arange(len(g))
col = ["#c0392b" if (q < .05 and r < 1) else ("#1e8449" if (q < .05) else "#555") for q, r in zip(g.q_BH, g.RR_anual)]
ax.hlines(y, g.IC95_lo, g.IC95_hi, color=col); ax.scatter(g.RR_anual, y, color=col, zorder=3)
ax.axvline(1, ls="--", c="k", lw=.8); ax.set_yticks(y); ax.set_yticklabels(g.especie, style="italic", fontsize=8)
ax.set_xscale("log"); ax.set_xticks([.7,.8,.9,1,1.2,1.5,2.5]); ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter()); ax.minorticks_off(); ax.set_xlabel("Razón de tasas anual (GLM binomial negativa, offset log esfuerzo; IC 95 %)")
ax.set_title("Tendencia de detección 2013–2025, especies UE con ≥10 obs y ≥5 años\nrojo = descenso significativo (FDR<0,05); ninguna especie con aumento significativo", fontsize=9)
fig.tight_layout(); fig.savefig(F / "prosperan_panel_top8.png", dpi=160); plt.close(fig)

s = pd.read_csv(M / "serie_anual_normalizada.csv"); s = s[s.region == "Catalunya"]
sp = g.sort_values("n_obs", ascending=False).especie.head(8)
fig, axs = plt.subplots(2, 4, figsize=(14, 6), sharex=True)
for a, n in zip(axs.flat, sp):
    d = s[(s.especie == n) & (s.year.between(2013, 2025))]
    a.plot(d.year, d.obs_por_1000_esfuerzo, marker="o", ms=3); a.set_title(n, style="italic", fontsize=9); a.set_yscale("symlog", linthresh=1)
    a.set_xticks([2014, 2018, 2022])
fig.supylabel("obs por 1000 obs del esfuerzo total BioQuest"); fig.tight_layout(); fig.savefig(F / "prosperan_panel_small_multiples.png", dpi=150)
