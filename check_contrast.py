#!/usr/bin/env python3
"""Check WCAG 2.1 contrast ratios for every colour pairing used by StoryCast.

Reads hex values from sass/_colors.scss so the tokens stay the single source
of truth. Exits non-zero if any pair fails its required ratio.

    python3 check_contrast.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ROOT, "sass", "_colors.scss"), encoding="utf-8").read()
PALETTE = {m.group(1): m.group(2) for m in re.finditer(r'"([\w-]+)":\s*(#[0-9a-fA-F]{6})', src)}


def lum(hex_):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def ratio(a, b):
    la, lb = sorted((lum(PALETTE[a]), lum(PALETTE[b])), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (foreground, background, required ratio, where it is used)
PAIRS = [
    ("ink", "paper", 4.5, "Body text on page background"),
    ("ink", "surface", 4.5, "Body text on cards"),
    ("ink", "sand", 4.5, "Body text on tinted panels"),
    ("ink-soft", "paper", 4.5, "Secondary text on page background"),
    ("ink-soft", "surface", 4.5, "Secondary text on cards"),
    ("ink-soft", "sand", 4.5, "Secondary text on tinted panels"),
    ("brand", "paper", 4.5, "Links on page background"),
    ("brand", "surface", 4.5, "Links on cards"),
    ("brand", "sand", 4.5, "Links on tinted panels"),
    ("clay", "paper", 4.5, "Eyebrow / badge text on page background"),
    ("clay", "surface", 4.5, "Eyebrow / badge text on cards"),
    ("clay", "sand", 4.5, "Eyebrow / badge text on tinted panels"),
    ("on-dark", "night", 4.5, "Header / footer text"),
    ("on-dark-soft", "night", 4.5, "Footer secondary text"),
    ("on-dark", "brand", 4.5, "Primary button text"),
    ("on-dark", "clay", 4.5, "Active transcript marker text"),
    ("ink", "accent", 4.5, "Accent button text"),
    ("accent", "night", 3.0, "Focus ring on dark surfaces"),
    ("focus", "paper", 3.0, "Focus ring on light surfaces"),
    ("focus", "surface", 3.0, "Focus ring on cards"),
    ("focus", "sand", 3.0, "Focus ring on tinted panels"),
    ("line", "paper", 3.0, "Form control / card borders vs page"),
    ("line", "surface", 3.0, "Form control borders vs cards"),
    ("brand", "sand", 3.0, "Active transcript line indicator"),
]

failures = 0
print(f"{'Foreground':<14}{'Background':<10}{'Ratio':>8}{'Need':>6}  Result  Use")
for fg, bg, need, use in PAIRS:
    r = ratio(fg, bg)
    ok = r >= need
    failures += not ok
    print(f"{fg:<14}{bg:<10}{r:>7.2f}:1{need:>5}  {'PASS' if ok else 'FAIL'}    {use}")
print(f"\n{len(PAIRS) - failures}/{len(PAIRS)} pairs pass.")
sys.exit(1 if failures else 0)
