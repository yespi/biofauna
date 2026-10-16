#!/usr/bin/env python3
"""Fig. 5 — Retraso ciudadano vs primera cita oficial/literatura (EXOCAT o fuente citada)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

M = Path(__file__).parent
F = M / "figuras"
CSV = M / "concordancia_exocat_oficial_20261016.csv"


def main():
    df = pd.read_csv(CSV)
    df = df.sort_values("anio_oficial")
    y = range(len(df))
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, row in df.iterrows():
        yi = list(y)[df.index.get_loc(i)]
        ax.plot(
            [row["anio_oficial"], row["anio_ciudadano"]],
            [yi, yi],
            "k-",
            lw=1.2,
        )
        ax.scatter(
            [row["anio_oficial"], row["anio_ciudadano"]],
            [yi, yi],
            c=["#2c3e50", "#e67e22"],
            s=36,
            zorder=3,
        )
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["especie"], style="italic", fontsize=8)
    ax.set_xlabel("Año")
    ax.set_title(
        "Fig. 5. Primera cita oficial o de inventario (EXOCAT/literatura) "
        "frente al primer registro ciudadano research en la caja de estudio"
    )
    ax.legend(
        handles=[
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#2c3e50", label="Oficial/literatura"),
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#e67e22", label="Ciudadano (caja CAT)"),
        ],
        loc="lower right",
        fontsize=7,
    )
    fig.tight_layout()
    out = F / "exocat_retraso_ciudadano_20261016.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
