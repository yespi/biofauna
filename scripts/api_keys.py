"""Public stub: read tokens from the environment only (no /mnt/utils)."""
from __future__ import annotations
import os
from pathlib import Path

def load_api_keys(force: bool = False) -> dict[str, str]:
    out = {}
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "INAT_API_TOKEN", "MINKA_API_TOKEN"):
        v = os.environ.get(k, "")
        if v:
            out[k] = v
    return out

def get_hf_token() -> str:
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN", "")

def bootstrap_hf_env(*, offline: bool | None = None, fatal: bool = False) -> bool:
    tok = get_hf_token()
    if tok:
        os.environ["HF_TOKEN"] = tok
        os.environ["HUGGING_FACE_HUB_TOKEN"] = tok
    root = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
    hf = Path(os.environ.get("HF_HOME", root / ".hf_cache"))
    os.environ.setdefault("HF_HOME", str(hf))
    if offline is True:
        os.environ["HF_HUB_OFFLINE"] = "1"
    if fatal and not tok:
        raise SystemExit("Set HF_TOKEN (Hugging Face) if the BioCLIP download is rate-limited.")
    return bool(tok)
