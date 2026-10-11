#!/usr/bin/env python3
"""Marca de agua BORRADOR para PDFs de papers BioFauna.

Texto diagonal suave + pie en cada página:
  BORRADOR · G. Zafra · <AAAA-MM-DD> · no citar ni difundir

Uso:
  from papers_watermark import watermark_pdf, watermark_pdfs_in_dir
  watermark_pdf(path)                       # in-place; fecha = hoy
  watermark_pdf(path, date="2026-10-11")
  watermark_pdf(src, dest=out)              # escribe en dest
"""
from __future__ import annotations

import argparse
import io
import sys
from datetime import date as date_cls
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas


WATERMARK_TMPL = "BORRADOR · G. Zafra · {date} · no citar ni difundir"

# Gris claro semitransparente
_COLOR = Color(0.55, 0.55, 0.55, alpha=0.14)
_FOOTER_COLOR = Color(0.45, 0.45, 0.45, alpha=0.45)


def _page_size(page) -> tuple[float, float]:
    box = page.mediabox
    return float(box.width), float(box.height)


def _overlay_pdf(width: float, height: float, text: str) -> PdfReader:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))

    # Diagonal across the page
    c.saveState()
    c.setFillColor(_COLOR)
    font_size = max(14, min(width, height) * 0.045)
    c.setFont("Helvetica", font_size)
    c.translate(width / 2, height / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, text)
    c.restoreState()

    # Footer
    c.setFillColor(_FOOTER_COLOR)
    foot_size = 7.5
    c.setFont("Helvetica", foot_size)
    c.drawCentredString(width / 2, 14, text)

    c.save()
    buf.seek(0)
    return PdfReader(buf)


def _already_watermarked(page, marker: str = "BORRADOR") -> bool:
    """Skip if page already carries our draft mark (content or overlay XObject)."""
    needle = marker.encode("latin-1", errors="ignore")
    try:
        # Flatten content streams
        contents = page.get_contents()
        chunks: list[bytes] = []
        if contents is None:
            pass
        elif isinstance(contents, list):
            for c in contents:
                chunks.append(c.get_data() if hasattr(c, "get_data") else bytes(c))
        else:
            chunks.append(contents.get_data() if hasattr(contents, "get_data") else b"")
        blob = b"".join(chunks)
        if needle in blob:
            return True
        # Also scan Resources / XObject streams (merge_page puts overlay there)
        resources = page.get("/Resources")
        if resources is not None:
            resources = resources.get_object()
            xobj = resources.get("/XObject") if resources else None
            if xobj is not None:
                xobj = xobj.get_object()
                for _name, ref in xobj.items():
                    try:
                        stream = ref.get_object()
                        data = stream.get_data() if hasattr(stream, "get_data") else b""
                        if needle in data:
                            return True
                    except Exception:
                        continue
    except Exception:
        return False
    return False


def watermark_pdf(
    src: Path | str,
    dest: Path | str | None = None,
    *,
    date: str | None = None,
    force: bool = False,
) -> Path:
    """Aplica marca de agua. Por defecto reescribe `src`."""
    src = Path(src)
    dest = Path(dest) if dest else src
    if not src.exists():
        raise FileNotFoundError(src)
    stamp_date = date or date_cls.today().isoformat()
    text = WATERMARK_TMPL.format(date=stamp_date)

    reader = PdfReader(str(src))
    writer = PdfWriter()

    # Cache overlays by page size (A4/A3/landscape mix)
    overlays: dict[tuple[float, float], PdfReader] = {}

    for page in reader.pages:
        w, h = _page_size(page)
        key = (round(w, 2), round(h, 2))
        if not force and _already_watermarked(page, "BORRADOR · G. Zafra"):
            writer.add_page(page)
            continue
        if key not in overlays:
            overlays[key] = _overlay_pdf(w, h, text)
        overlay_page = overlays[key].pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)

    # Preserve metadata lightly
    if reader.metadata:
        try:
            writer.add_metadata({k: v for k, v in reader.metadata.items() if v})
        except Exception:
            pass

    tmp = dest.with_suffix(dest.suffix + ".wm_tmp")
    with tmp.open("wb") as f:
        writer.write(f)
    tmp.replace(dest)
    return dest


def watermark_pdfs_in_dir(
    directory: Path | str,
    *,
    pattern: str = "*.pdf",
    recursive: bool = False,
    date: str | None = None,
    force: bool = False,
) -> list[Path]:
    d = Path(directory)
    paths = sorted(d.rglob(pattern) if recursive else d.glob(pattern))
    done = []
    for p in paths:
        if p.name.startswith("_tmp") or p.name.endswith(".wm_tmp"):
            continue
        watermark_pdf(p, date=date, force=force)
        done.append(p)
    return done


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Marca de agua BORRADOR en PDFs")
    ap.add_argument("paths", nargs="+", type=Path, help="PDF o directorio")
    ap.add_argument("--date", default=None, help="AAAA-MM-DD (default: hoy)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("-r", "--recursive", action="store_true")
    args = ap.parse_args(argv)
    n = 0
    for p in args.paths:
        if p.is_dir():
            done = watermark_pdfs_in_dir(
                p, recursive=args.recursive, date=args.date, force=args.force
            )
            n += len(done)
            for d in done:
                print("wm", d)
        else:
            watermark_pdf(p, date=args.date, force=args.force)
            print("wm", p)
            n += 1
    print(f"DONE {n} pdfs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
