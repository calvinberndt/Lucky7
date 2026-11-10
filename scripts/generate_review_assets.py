"""Rebuild the printable review card; development tooling never ships to visitors.

Run with: uv run --no-project --with qrcode==8.2 python scripts/generate_review_assets.py
Pass --check to verify reproducibility without writing files.
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = "https://lucky7towingtransport.com/review/"


def qr_document() -> str:
    """Keep four clear modules around an unmodified, high-contrast QR code."""
    import qrcode

    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    code.add_data(DESTINATION)
    code.make(fit=True)
    matrix = code.get_matrix()
    size = len(matrix)
    modules = "".join(f"M{x},{y}h1v1h-1z" for y, row in enumerate(matrix)
                      for x, dark in enumerate(row) if dark)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" id="review-qr-code" '
            f'viewBox="0 0 {size} {size}" role="img" aria-labelledby="qr-title qr-desc">\n'
            '<title id="qr-title">Lucky 7 Towing review page</title>\n'
            f'<desc id="qr-desc">Scan to open {DESTINATION}</desc>\n'
            f'<rect width="{size}" height="{size}" fill="#fff"/>\n'
            f'<path d="{modules}" fill="#000"/>\n</svg>\n')


def render_assets(root: Path) -> dict[str, str]:
    """Embed the approved badge so the downloaded 5 × 3 inch card is standalone."""
    qr = qr_document()
    badge = base64.b64encode((root / "images/brand-112.jpg").read_bytes()).decode("ascii")
    card_qr = qr.replace('id="review-qr-code"',
                         'id="review-qr-code" x="650" y="180" width="280" height="280"', 1)
    card = f'''<svg xmlns="http://www.w3.org/2000/svg" width="5in" height="3in" viewBox="0 0 1000 600" role="img" aria-labelledby="card-title card-desc">
<title id="card-title">Lucky 7 Towing review invitation</title>
<desc id="card-desc">Thanks for choosing Lucky 7 Towing. You are welcome to share an honest Google review. Scan the QR code or visit {DESTINATION}.</desc>
<rect width="1000" height="600" fill="#faf5e8"/>
<rect x="20" y="20" width="960" height="560" rx="8" fill="none" stroke="#2d5937" stroke-width="3"/>
<image x="60" y="60" width="112" height="112" href="data:image/jpeg;base64,{badge}"/>
<g fill="#1e3d26" font-family="Rockwell, Georgia, serif">
  <text x="200" y="102" font-size="48">Lucky 7 Towing</text>
  <text x="60" y="250" font-size="38">Thanks for choosing us.</text>
</g>
<g fill="#181f19" font-family="Trebuchet MS, Arial, sans-serif">
  <text x="200" y="145" font-size="25">(715) 853-8513 · Open 24/7</text>
  <text x="60" y="308" font-size="27">You're welcome to share an</text>
  <text x="60" y="347" font-size="27">honest review of your experience.</text>
  <text x="60" y="407" font-size="24">Scan to leave a Google review.</text>
  <text x="60" y="443" font-size="23">Leaving a review is optional.</text>
  <text x="60" y="530" font-size="28">lucky7towingtransport.com/review/</text>
</g>
{card_qr}</svg>
'''
    return {"review-qr.svg": qr, "review-card.svg": card}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare without writing")
    args = parser.parse_args(argv)
    assets = render_assets(ROOT)
    target = ROOT / "review"
    if args.check:
        changed = [name for name, data in assets.items()
                   if not (target / name).is_file()
                   or (target / name).read_text(encoding="utf-8") != data]
        if changed:
            print("Review assets need regeneration: " + ", ".join(changed))
            return 1
        print("Review assets match the canonical destination and approved badge.")
        return 0
    target.mkdir(exist_ok=True)
    for name, data in assets.items():
        (target / name).write_text(data, encoding="utf-8")
    print("Generated review QR and printable card.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
