"""HTTP headers for iNaturalist / Minka (tokens from the environment)."""
from __future__ import annotations
import os

UA = "biofauna-public/1.0"


def inat_headers() -> dict[str, str]:
    h = {"User-Agent": UA}
    tok = os.environ.get("INAT_API_TOKEN") or os.environ.get("INAT_JWT", "")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def minka_headers() -> dict[str, str]:
    h = {"User-Agent": UA}
    tok = os.environ.get("MINKA_API_TOKEN", "")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h
