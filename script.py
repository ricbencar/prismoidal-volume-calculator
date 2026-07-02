#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Prismoidal and Classical Solid Volume Calculator
================================================

Purpose
-------
This file is a self-contained graphical Tkinter application for calculating
volumes of classical solids, prismoids, prismatoids, frusta, average end-area
volumes, general prismoidal corrections, and homothetic irregular-polygon
frusta/corrections.

The GUI is intentionally split into two fixed halves:
    - left half: solid selection, input data, calculated volume, correction
      line, and the full text report;
    - right half: large 3D view of the selected solid with dimension labels.

The report displayed in the GUI is the same text that is saved to output.txt
through the Save TXT button.

Supported solids and methods
----------------------------
    1. Cube
    2. Triangular prism
    3. Regular hexagonal prism
    4. Oblique prism / parallelepiped
    5. Right rectangular prism / cuboid
    6. Cylinder
    7. Square pyramid
    8. Right circular cone
    9. Frustum of a square pyramid / similar-base frustum
    10. Frustum of a cone
    11. Triangular wedge
    12. General prismoid / prismatoid
    13. Sphere
    14. Average end-area volume
    15. General prismoidal correction
    16. Homothetic irregular polygonal frustum / correction

Clean Python environment — Windows
----------------------------------
Open Command Prompt or PowerShell in the folder containing this script:

    py -m venv .venv
    .venv\Scripts\activate
    py -m pip install --upgrade pip
    py -m pip install matplotlib numpy

Run the GUI:

    python script.py

or, if this file keeps its distributed name:

    python script.py

Clean Python environment — Linux/macOS
--------------------------------------

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install matplotlib numpy
    python script.py

PyInstaller one-file stand-alone executable — Windows
-----------------------------------------------------
Inside the activated virtual environment:

    py -m pip install pyinstaller
    pyinstaller --clean --onefile --windowed --name script --collect-all matplotlib script.py

The stand-alone executable will be created in:

    dist\script.exe

If you prefer to see console errors during testing, replace --windowed by
--console. After validation, build again with --windowed.

PyInstaller one-file stand-alone executable — Linux/macOS
---------------------------------------------------------

    python -m pip install pyinstaller
    pyinstaller --clean --onefile --windowed --name script --collect-all matplotlib script.py

Notes
-----
- Length dimensions must be positive.
- Area inputs must be positive unless a specific formula explicitly permits
  another condition.
- The homothetic irregular-polygon correction is exact only when the two end
  polygons are the same plane shape, lie in parallel planes, and differ only by
  a uniform linear scale.
- The general prismoid formula requires the real middle area Am. If Am is not
  known and the end areas are not homothetic, no unique correction can be
  obtained from A1 and A2 alone.
- The GUI window is fixed-size by design. Its height has been deliberately kept
  slightly lower than the previous version to fit more comfortably on ordinary
  laptop screens.

Author: generated for technical engineering use.
"""

import math
import os
import sys
import textwrap
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

try:
    import numpy as np
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except Exception as exc:  # pragma: no cover - GUI dependency guard
    raise SystemExit(
        "This application requires matplotlib and numpy.\n\n"
        "Install them with:\n"
        "    python -m pip install matplotlib numpy\n\n"
        f"Original import error: {exc}"
    )


APP_TITLE = "Prismoidal and Classical Solid Volume Calculator"
VERSION = "2026-07-02"
APP_SUBTITLE = "Graphical calculator for prismoids, frusta, prisms, cones, cylinders, wedges, spheres and homothetic irregular polygons"


# This text is shown by the GUI "Usage / build" button and is also mirrored in
# the module header above. Keeping it in one explicit constant makes the script
# easier to maintain when installation or compilation commands change.
USAGE_TEXT = """Prismoidal and Classical Solid Volume Calculator

Windows virtual environment:
    py -m venv .venv
    .venv\\Scripts\\activate
    py -m pip install --upgrade pip
    py -m pip install matplotlib numpy

Run:
    python script.py

Windows PyInstaller one-file executable:
    py -m pip install pyinstaller
    pyinstaller --clean --onefile --windowed --name script --collect-all matplotlib script.py

Executable output:
    dist\\script.exe

Linux/macOS virtual environment:
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install matplotlib numpy
    python script.py
"""

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 11
FONT_SIZE_LARGE = 13
FONT_SIZE_TITLE = 20
FONT_SIZE_RESULT = 19


# Fixed-window sizing policy.
# The previous version used a taller window. These limits keep the application
# fixed and graphical, but reduce height so the title bar, bottom buttons and
# taskbar are less likely to be clipped on 900p/1080p screens.
WINDOW_WIDTH_RATIO = 0.92
WINDOW_HEIGHT_RATIO = 0.82
WINDOW_MIN_WIDTH = 1320
WINDOW_MIN_HEIGHT = 760
WINDOW_MAX_WIDTH = 1700
WINDOW_MAX_HEIGHT = 920
WINDOW_SCREEN_MARGIN_X = 50
WINDOW_SCREEN_MARGIN_Y = 70

# Visual palette: blue technical theme with warm solid accents.
COLORS = {
    "bg": "#eaf3fb",
    "panel": "#ffffff",
    "panel2": "#f5faff",
    "header": "#0b3d66",
    "header2": "#145c91",
    "accent": "#1f78b4",
    "accent2": "#2a9fd6",
    "accent_dark": "#0a2f4f",
    "text": "#102a43",
    "muted": "#52616b",
    "ok": "#0b3d66",
    "warn": "#b35c00",
    "danger": "#a8201a",
}


def fmt(x, nd=6):
    """Compact engineering-style number formatter."""
    if x is None:
        return ""
    if abs(x) < 1e-12:
        return "0"
    if abs(x) >= 1e7 or abs(x) < 1e-4:
        return f"{x:.{nd}e}"
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return s


def parse_float(value, name):
    """Parse float accepting decimal comma."""
    raw = str(value).strip().replace(" ", "").replace(",", ".")
    if raw == "":
        raise ValueError(f"Missing value for {name}.")
    try:
        x = float(raw)
    except ValueError:
        raise ValueError(f"Invalid numeric value for {name}: {value!r}.")
    if not math.isfinite(x):
        raise ValueError(f"Invalid non-finite value for {name}: {value!r}.")
    return x


def polygon_area_xy(points):
    """Shoelace area for points with x,y coordinates."""
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i][0], points[i][1]
        x2, y2 = points[(i + 1) % n][0], points[(i + 1) % n][1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def set_axes_clean(ax, title=None):
    """Apply a clean technical 3D style."""
    ax.set_facecolor("#ffffff")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlabel("x", labelpad=-8, color=COLORS["muted"])
    ax.set_ylabel("y", labelpad=-8, color=COLORS["muted"])
    ax.set_zlabel("z", labelpad=-8, color=COLORS["muted"])
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#d7e3ef")
    if title:
        ax.set_title(title, pad=10, color=COLORS["header"], fontsize=15, fontweight="bold")


def equalize_3d(ax, xs, ys, zs, pad=0.04):
    """Set compact equal 3D limits so the solid fills the available view."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    zs = np.asarray(zs, dtype=float)
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    zmin, zmax = zs.min(), zs.max()
    cx, cy, cz = (xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2
    span = max(xmax - xmin, ymax - ymin, zmax - zmin, 1.0)
    span *= (1 + pad)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(cx - span / 2, cx + span / 2)
    ax.set_ylim(cy - span / 2, cy + span / 2)
    ax.set_zlim(cz - span / 2, cz + span / 2)


def add_dim_line(ax, p1, p2, label, color="#0b3d66", text_offset=(0, 0, 0), lw=1.8):
    """Draw a simple dimension line with endpoints and label."""
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, lw=lw)
    ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color=color, s=18)
    mid = (p1 + p2) / 2 + np.asarray(text_offset, dtype=float)
    ax.text(mid[0], mid[1], mid[2], label, color=color, fontsize=12, fontweight="bold")


def add_faces(ax, faces, facecolors=None, alpha=0.86, edgecolor="#17212b"):
    """Add polyhedral faces."""
    if facecolors is None:
        facecolors = ["#8ecae6"] * len(faces)
    poly = Poly3DCollection(
        faces,
        facecolors=facecolors,
        edgecolors=edgecolor,
        linewidths=1.15,
        alpha=alpha,
    )
    ax.add_collection3d(poly)


# -----------------------------------------------------------------------------
# Calculation definitions
# -----------------------------------------------------------------------------

def calc_prism(p):
    """Calculate the volume and report lines for a right rectangular prism/cuboid."""
    a, b, h = p["a"], p["b"], p["h"]
    B = a * b
    V = B * h
    return {
        "title": "Right rectangular prism / cuboid",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = B h = a b h",
            "",
            "Substitution:",
            f"  B = a b = ({fmt(a)})({fmt(b)}) = {fmt(B)}",
            f"  V = B h = ({fmt(B)})({fmt(h)}) = {fmt(V)}",
        ],
    }


def calc_cylinder(p):
    """Calculate the volume and report lines for a circular cylinder."""
    r, h = p["r"], p["h"]
    A = math.pi * r * r
    V = A * h
    return {
        "title": "Cylinder",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = π r² h",
            "",
            "Substitution:",
            f"  A = π r² = π({fmt(r)})² = {fmt(A)}",
            f"  V = A h = ({fmt(A)})({fmt(h)}) = {fmt(V)}",
        ],
    }


def calc_square_pyramid(p):
    """Calculate the volume and prismoidal check for a square pyramid."""
    a, h = p["a"], p["h"]
    B = a * a
    Am = B / 4
    V = B * h / 3
    Vp = h / 6 * (0 + 4 * Am + B)
    return {
        "title": "Square pyramid",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = (1/3) B h = (1/3) a² h",
            "",
            "Prismoidal interpretation:",
            "  A₁ = 0,  A₂ = B,  Aₘ = B/4",
            "  V = h/6 (A₁ + 4Aₘ + A₂)",
            "",
            "Substitution:",
            f"  B = a² = ({fmt(a)})² = {fmt(B)}",
            f"  Aₘ = B/4 = {fmt(Am)}",
            f"  V = (1/3)({fmt(B)})({fmt(h)}) = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
        ],
    }


def calc_cone(p):
    """Calculate the volume and prismoidal check for a right circular cone."""
    r, h = p["r"], p["h"]
    B = math.pi * r * r
    Am = B / 4
    V = B * h / 3
    Vp = h / 6 * (0 + 4 * Am + B)
    return {
        "title": "Right circular cone",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = (1/3) π r² h",
            "",
            "Prismoidal interpretation:",
            "  A₁ = 0,  A₂ = πr²,  Aₘ = π(r/2)² = A₂/4",
            "",
            "Substitution:",
            f"  A₂ = πr² = π({fmt(r)})² = {fmt(B)}",
            f"  Aₘ = A₂/4 = {fmt(Am)}",
            f"  V = (1/3)({fmt(B)})({fmt(h)}) = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
        ],
    }


def calc_pyramid_frustum(p):
    """Calculate a similar-base pyramid frustum using the area frustum formula."""
    A1, A2, h = p["A1"], p["A2"], p["h"]
    root = math.sqrt(A1 * A2)
    Am = ((math.sqrt(A1) + math.sqrt(A2)) / 2.0) ** 2
    V = h / 3 * (A1 + root + A2)
    Vp = h / 6 * (A1 + 4 * Am + A2)
    Vea = h / 2 * (A1 + A2)
    C = Vea - V
    return {
        "title": "Frustum of a pyramid / similar-base frustum",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = h/3 (A₁ + √(A₁A₂) + A₂)",
            "",
            "Equivalent prismoidal middle area:",
            "  Aₘ = ((√A₁ + √A₂)/2)²",
            "",
            "Substitution:",
            f"  √(A₁A₂) = √(({fmt(A1)})({fmt(A2)})) = {fmt(root)}",
            f"  Aₘ = ((√{fmt(A1)} + √{fmt(A2)})/2)² = {fmt(Am)}",
            f"  V = ({fmt(h)})/3 ({fmt(A1)} + {fmt(root)} + {fmt(A2)}) = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
            "",
            "Average end-area comparison:",
            f"  V_EA = h/2 (A₁ + A₂) = {fmt(Vea)}",
            f"  Correction to subtract C = V_EA − V = {fmt(C)}",
        ],
    }


def calc_cone_frustum(p):
    """Calculate a conical frustum using radii and perpendicular height."""
    R, r, h = p["R"], p["r"], p["h"]
    V = math.pi * h / 3 * (R * R + R * r + r * r)
    A1 = math.pi * R * R
    A2 = math.pi * r * r
    Am = math.pi * ((R + r) / 2) ** 2
    Vp = h / 6 * (A1 + 4 * Am + A2)
    return {
        "title": "Frustum of a cone",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = πh/3 (R² + Rr + r²)",
            "",
            "Area form:",
            "  A₁ = πR², A₂ = πr²",
            "  V = h/3 (A₁ + √(A₁A₂) + A₂)",
            "",
            "Substitution:",
            f"  A₁ = π({fmt(R)})² = {fmt(A1)}",
            f"  A₂ = π({fmt(r)})² = {fmt(A2)}",
            f"  Aₘ = π((R+r)/2)² = {fmt(Am)}",
            f"  V = π({fmt(h)})/3 [({fmt(R)})² + ({fmt(R)})({fmt(r)}) + ({fmt(r)})²] = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
        ],
    }


def calc_wedge(p):
    """Calculate the volume of a triangular wedge/prismatic component."""
    b, ht, L = p["b"], p["ht"], p["L"]
    tri = 0.5 * b * ht
    V = tri * L
    return {
        "title": "Triangular wedge",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = (1/2) b h L",
            "",
            "Substitution:",
            f"  triangular area = (1/2)({fmt(b)})({fmt(ht)}) = {fmt(tri)}",
            f"  V = ({fmt(tri)})({fmt(L)}) = {fmt(V)}",
        ],
    }


def calc_general_prismoid(p):
    """Calculate the general prismoidal volume from A1, Am, A2 and L."""
    A1, Am, A2, L = p["A1"], p["Am"], p["A2"], p["L"]
    V = L / 6 * (A1 + 4 * Am + A2)
    Vea = L / 2 * (A1 + A2)
    C = Vea - V
    C_general = L / 3 * (A1 + A2 - 2 * Am)
    return {
        "title": "General prismoid / prismatoid",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = L/6 (A₁ + 4Aₘ + A₂)",
            "",
            "Substitution:",
            f"  V = {fmt(L)}/6 ({fmt(A1)} + 4({fmt(Am)}) + {fmt(A2)}) = {fmt(V)}",
            "",
            "Average end-area comparison:",
            f"  V_EA = L/2(A₁ + A₂) = {fmt(Vea)}",
            f"  C = V_EA − V = {fmt(C)}",
            f"  C = L/3(A₁ + A₂ − 2Aₘ) = {fmt(C_general)}",
        ],
    }


def calc_sphere(p):
    """Calculate the sphere volume and show its Simpson/prismoidal interpretation."""
    r = p["r"]
    V = 4 / 3 * math.pi * r ** 3
    Am = math.pi * r * r
    Vp = (2 * r) / 6 * (0 + 4 * Am + 0)
    return {
        "title": "Sphere",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = (4/3)πr³",
            "",
            "Prismoidal/Simpson interpretation over a diameter:",
            "  A₁ = 0, Aₘ = πr², A₂ = 0, L = 2r",
            "",
            "Substitution:",
            f"  V = (4/3)π({fmt(r)})³ = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
        ],
    }


def calc_average_end_area(p):
    """Calculate the average end-area volume from two parallel section areas."""
    A1, A2, L = p["A1"], p["A2"], p["L"]
    V = L / 2 * (A1 + A2)
    return {
        "title": "Average end-area method",
        "volume": V,
        "lines": [
            "Formula:",
            "  V_EA = L/2 (A₁ + A₂)",
            "",
            "Substitution:",
            f"  V_EA = {fmt(L)}/2 ({fmt(A1)} + {fmt(A2)}) = {fmt(V)}",
            "",
            "Note:",
            "  This is exact when area varies linearly between sections.",
            "  It is generally only approximate for prismoidal/frustum geometry.",
        ],
    }


def calc_general_correction(p):
    """Calculate the general prismoidal correction relative to end-area volume."""
    A1, Am, A2, L = p["A1"], p["Am"], p["A2"], p["L"]
    Vea = L / 2 * (A1 + A2)
    Vp = L / 6 * (A1 + 4 * Am + A2)
    C = Vea - Vp
    C2 = L / 3 * (A1 + A2 - 2 * Am)
    return {
        "title": "General prismoidal correction",
        "volume": Vp,
        "lines": [
            "Formulae:",
            "  V_EA = L/2 (A₁ + A₂)",
            "  V_P  = L/6 (A₁ + 4Aₘ + A₂)",
            "  C = V_EA − V_P",
            "  C = L/3 (A₁ + A₂ − 2Aₘ)",
            "",
            "Substitution:",
            f"  V_EA = {fmt(Vea)}",
            f"  V_P = {fmt(Vp)}",
            f"  C = V_EA − V_P = {fmt(C)}",
            f"  C = L/3(A₁ + A₂ − 2Aₘ) = {fmt(C2)}",
            "",
            "Corrected volume:",
            f"  V = V_EA − C = {fmt(Vp)}",
        ],
    }


def calc_homothetic_irregular(p):
    """Calculate the exact homothetic irregular-polygon frustum volume/correction."""
    A1, A2, L = p["A1"], p["A2"], p["L"]
    s1 = math.sqrt(A1)
    s2 = math.sqrt(A2)
    Am = ((s1 + s2) / 2) ** 2
    V = L / 3 * (A1 + math.sqrt(A1 * A2) + A2)
    Vea = L / 2 * (A1 + A2)
    C = L / 6 * (s2 - s1) ** 2
    Vp = L / 6 * (A1 + 4 * Am + A2)
    k = s2 / s1 if s1 != 0 else math.nan
    return {
        "title": "Homothetic irregular polygonal frustum",
        "volume": V,
        "lines": [
            "Assumption:",
            "  A₁ and A₂ are irregular polygons of the same plane shape,",
            "  in parallel planes, differing only by uniform linear scale.",
            "",
            "Middle area:",
            "  Aₘ = ((√A₁ + √A₂)/2)²",
            "",
            "Volume:",
            "  V = L/3 (A₁ + √(A₁A₂) + A₂)",
            "",
            "Correction to average end-area volume:",
            "  C = L/6 (√A₂ − √A₁)²",
            "",
            "Substitution:",
            f"  √A₁ = {fmt(s1)}",
            f"  √A₂ = {fmt(s2)}",
            f"  linear scale ratio k = √(A₂/A₁) = {fmt(k)}",
            f"  Aₘ = (({fmt(s1)} + {fmt(s2)})/2)² = {fmt(Am)}",
            f"  V = {fmt(L)}/3 ({fmt(A1)} + {fmt(math.sqrt(A1*A2))} + {fmt(A2)}) = {fmt(V)}",
            f"  Check by prismoidal formula = {fmt(Vp)}",
            f"  V_EA = {fmt(Vea)}",
            f"  C = {fmt(L)}/6 ({fmt(s2)} − {fmt(s1)})² = {fmt(C)}",
            f"  V = V_EA − C = {fmt(Vea)} − {fmt(C)} = {fmt(Vea - C)}",
        ],
    }


# -----------------------------------------------------------------------------
# Drawing functions
# -----------------------------------------------------------------------------

def draw_prism(ax, p):
    """Draw a labelled cuboid representation on a Matplotlib 3D axis."""
    a, b, h = p["a"], p["b"], p["h"]
    verts = np.array([
        [0, 0, 0], [a, 0, 0], [a, b, 0], [0, b, 0],
        [0, 0, h], [a, 0, h], [a, b, h], [0, b, h],
    ], dtype=float)
    faces = [[verts[j] for j in ids] for ids in
             ([0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7])]
    add_faces(ax, faces, ["#8ecae6", "#bde0fe", "#219ebc", "#2a9fd6", "#1f78b4", "#90e0ef"])
    add_dim_line(ax, (0, -0.08*b, 0), (a, -0.08*b, 0), "a")
    add_dim_line(ax, (a*1.05, 0, 0), (a*1.05, b, 0), "b")
    add_dim_line(ax, (-0.08*a, 0, 0), (-0.08*a, 0, h), "h")
    equalize_3d(ax, verts[:, 0], verts[:, 1], verts[:, 2])


def draw_cylinder(ax, p):
    """Draw a labelled circular cylinder on a Matplotlib 3D axis."""
    r, h = p["r"], p["h"]
    u = np.linspace(0, 2 * math.pi, 120)
    z = np.linspace(0, h, 40)
    U, Z = np.meshgrid(u, z)
    X = r * np.cos(U)
    Y = r * np.sin(U)
    ax.plot_surface(X, Y, Z, color="#8ecae6", alpha=0.92, linewidth=0, shade=True)
    ax.plot(r * np.cos(u), r * np.sin(u), 0, color="#102a43", lw=1.4)
    ax.plot(r * np.cos(u), r * np.sin(u), h, color="#102a43", lw=1.4)
    add_dim_line(ax, (0, 0, 0), (r, 0, 0), "r")
    add_dim_line(ax, (r * 1.15, 0, 0), (r * 1.15, 0, h), "h")
    equalize_3d(ax, [-r, r], [-r, r], [0, h])


def draw_square_pyramid(ax, p):
    """Draw a labelled square pyramid with base side and vertical height."""
    a, h = p["a"], p["h"]
    base = np.array([[0, 0, 0], [a, 0, 0], [a, a, 0], [0, a, 0]], dtype=float)
    apex = np.array([a/2, a/2, h], dtype=float)
    faces = [[base[0], base[1], base[2], base[3]]] + [[base[i], base[(i+1) % 4], apex] for i in range(4)]
    add_faces(ax, faces, ["#bde0fe", "#2a9fd6", "#1f78b4", "#48cae4", "#90e0ef"], alpha=0.88)
    add_dim_line(ax, (0, -0.08*a, 0), (a, -0.08*a, 0), "a")
    add_dim_line(ax, (a/2, a/2, 0), (a/2, a/2, h), "h", color="#a8201a")
    ax.plot([a/2, a/2], [a/2, a/2], [0, h], color="#a8201a", lw=1.6, ls="--")
    allp = np.vstack([base, apex])
    equalize_3d(ax, allp[:, 0], allp[:, 1], allp[:, 2])


def draw_cone(ax, p):
    """Draw a labelled cone with radius and height annotations."""
    r, h = p["r"], p["h"]
    u = np.linspace(0, 2 * math.pi, 120)
    v = np.linspace(0, 1, 60)
    U, V = np.meshgrid(u, v)
    Rad = (1 - V) * r
    X = Rad * np.cos(U)
    Y = Rad * np.sin(U)
    Z = V * h
    ax.plot_surface(X, Y, Z, color="#8ecae6", alpha=0.92, linewidth=0, shade=True)
    ax.plot(r * np.cos(u), r * np.sin(u), 0, color="#102a43", lw=1.4)
    add_dim_line(ax, (0, 0, 0), (r, 0, 0), "r")
    add_dim_line(ax, (0, 0, 0), (0, 0, h), "h", color="#a8201a")
    ax.plot([0, 0], [0, 0], [0, h], color="#a8201a", lw=1.6, ls="--")
    equalize_3d(ax, [-r, r], [-r, r], [0, h])


def draw_pyramid_frustum(ax, p):
    """Draw an equivalent square-base frustum using side lengths sqrt(A1), sqrt(A2)."""
    A1, A2, h = p["A1"], p["A2"], p["h"]
    # Represent as square frustum with equivalent square side lengths.
    s1 = math.sqrt(A1)
    s2 = math.sqrt(A2)
    offset = (s1 - s2) / 2
    base = np.array([[0, 0, 0], [s1, 0, 0], [s1, s1, 0], [0, s1, 0]], dtype=float)
    top = np.array([[offset, offset, h], [offset+s2, offset, h], [offset+s2, offset+s2, h], [offset, offset+s2, h]], dtype=float)
    faces = [[base[0], base[1], base[2], base[3]], [top[0], top[1], top[2], top[3]]] + \
            [[base[i], base[(i+1)%4], top[(i+1)%4], top[i]] for i in range(4)]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8", "#0096c7"], alpha=0.9)
    add_dim_line(ax, (0, -0.08*s1, 0), (s1, -0.08*s1, 0), "√A₁")
    add_dim_line(ax, (offset, offset-0.08*s1, h), (offset+s2, offset-0.08*s1, h), "√A₂", color="#a8201a")
    add_dim_line(ax, (-0.08*s1, 0, 0), (-0.08*s1, 0, h), "h")
    allp = np.vstack([base, top])
    equalize_3d(ax, allp[:,0], allp[:,1], allp[:,2])


def draw_cone_frustum(ax, p):
    """Draw a labelled conical frustum with upper and lower radii."""
    R, r, h = p["R"], p["r"], p["h"]
    u = np.linspace(0, 2 * math.pi, 120)
    v = np.linspace(0, 1, 60)
    U, V = np.meshgrid(u, v)
    Rad = R + (r - R) * V
    X = Rad * np.cos(U)
    Y = Rad * np.sin(U)
    Z = V * h
    ax.plot_surface(X, Y, Z, color="#90e0ef", alpha=0.93, linewidth=0, shade=True)
    ax.plot(R*np.cos(u), R*np.sin(u), 0, color="#102a43", lw=1.4)
    ax.plot(r*np.cos(u), r*np.sin(u), h, color="#102a43", lw=1.4)
    add_dim_line(ax, (0, 0, 0), (R, 0, 0), "R")
    add_dim_line(ax, (0, 0, h), (r, 0, h), "r", color="#a8201a")
    add_dim_line(ax, (R*1.12, 0, 0), (R*1.12, 0, h), "h")
    equalize_3d(ax, [-R, R], [-R, R], [0, h])


def draw_wedge(ax, p):
    """Draw a labelled triangular wedge extruded along length L."""
    b, ht, L = p["b"], p["ht"], p["L"]
    # Triangular cross-section in x-z, extruded along y.
    pts = np.array([
        [0, 0, 0], [b, 0, 0], [0, 0, ht],
        [0, L, 0], [b, L, 0], [0, L, ht],
    ], dtype=float)
    faces = [
        [pts[0], pts[1], pts[2]],
        [pts[3], pts[4], pts[5]],
        [pts[0], pts[1], pts[4], pts[3]],
        [pts[0], pts[2], pts[5], pts[3]],
        [pts[1], pts[2], pts[5], pts[4]],
    ]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8"], alpha=0.9)
    add_dim_line(ax, (0, -0.05*L, 0), (b, -0.05*L, 0), "b")
    add_dim_line(ax, (-0.05*b, 0, 0), (-0.05*b, 0, ht), "h", color="#a8201a")
    add_dim_line(ax, (b*1.05, 0, 0), (b*1.05, L, 0), "L")
    equalize_3d(ax, pts[:,0], pts[:,1], pts[:,2])


def draw_general_prismoid(ax, p):
    """Draw a generic irregular prismoid with a dashed middle section."""
    A1, Am, A2, L = p["A1"], p["Am"], p["A2"], p["L"]
    # Use equivalent irregular pentagons scaled roughly by square root of area.
    base_shape = np.array([[0, 0, 0], [1.8, 0.15, 0], [2.25, 1.15, 0], [1.2, 1.75, 0], [0.15, 1.3, 0]], dtype=float)
    base_area = polygon_area_xy(base_shape)
    scale1 = math.sqrt(A1 / base_area)
    scale2 = math.sqrt(A2 / base_area)
    b = base_shape * scale1
    c = np.array([b[:,0].mean(), b[:,1].mean(), 0])
    t = (base_shape * scale2)
    # shift top so centroids align reasonably
    t[:,0] += c[0] - t[:,0].mean()
    t[:,1] += c[1] - t[:,1].mean()
    t[:,2] = L
    faces = [b, t] + [[b[i], b[(i+1)%5], t[(i+1)%5], t[i]] for i in range(5)]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8", "#0096c7", "#0077b6"], alpha=0.88)
    # middle section visual, scaled to Am where possible
    scalem = math.sqrt(max(Am, 1e-12) / base_area)
    m = base_shape * scalem
    m[:,0] += c[0] - m[:,0].mean()
    m[:,1] += c[1] - m[:,1].mean()
    m[:,2] = L / 2
    mclose = np.vstack([m, m[0]])
    ax.plot(mclose[:,0], mclose[:,1], mclose[:,2], color="#a8201a", lw=2.2, ls="--")
    ax.text(m[:,0].mean(), m[:,1].mean(), L/2, "Aₘ", color="#a8201a", fontsize=12, fontweight="bold")
    add_dim_line(ax, (b[:,0].min()*0.9, b[:,1].min()*0.9, 0), (b[:,0].min()*0.9, b[:,1].min()*0.9, L), "L")
    allp = np.vstack([b, t, m])
    equalize_3d(ax, allp[:,0], allp[:,1], allp[:,2])


def draw_sphere(ax, p):
    """Draw a true sphere with radius and diameter labels."""
    r = p["r"]
    u = np.linspace(0, 2 * math.pi, 100)
    v = np.linspace(0, math.pi, 70)
    U, V = np.meshgrid(u, v)
    X = r * np.cos(U) * np.sin(V)
    Y = r * np.sin(U) * np.sin(V)
    Z = r * np.cos(V)
    ax.plot_surface(X, Y, Z, color="#90e0ef", alpha=0.93, linewidth=0, shade=True)
    ax.plot(r*np.cos(u), r*np.sin(u), 0, color="#102a43", lw=1.2)
    add_dim_line(ax, (0, 0, 0), (r, 0, 0), "r")
    add_dim_line(ax, (0, 0, -r), (0, 0, r), "2r", color="#a8201a")
    equalize_3d(ax, [-r, r], [-r, r], [-r, r])


def draw_average_end_area(ax, p):
    """Draw the average end-area case using a generic two-section prismoid."""
    # Draw two generic parallel sections
    p2 = {"A1": p["A1"], "Am": (p["A1"] + p["A2"]) / 2, "A2": p["A2"], "L": p["L"]}
    draw_general_prismoid(ax, p2)


def draw_general_correction(ax, p):
    """Draw the general correction case using the generic prismoid visual."""
    draw_general_prismoid(ax, p)


def draw_homothetic_irregular(ax, p):
    """Draw homothetic irregular polygons and the mean-linear-scale middle polygon."""
    A1, A2, L = p["A1"], p["A2"], p["L"]
    base_shape = np.array([[0, 0, 0], [2.1, 0.25, 0], [2.45, 1.0, 0], [1.65, 1.72, 0], [0.72, 1.46, 0], [0.15, 0.78, 0]], dtype=float)
    base_area = polygon_area_xy(base_shape)
    s1 = math.sqrt(A1 / base_area)
    s2 = math.sqrt(A2 / base_area)
    sm = (s1 + s2) / 2
    b = base_shape * s1
    c = np.array([b[:,0].mean(), b[:,1].mean(), 0])
    t = base_shape * s2
    t[:,0] += c[0] - t[:,0].mean()
    t[:,1] += c[1] - t[:,1].mean()
    t[:,2] = L
    m = base_shape * sm
    m[:,0] += c[0] - m[:,0].mean()
    m[:,1] += c[1] - m[:,1].mean()
    m[:,2] = L/2
    faces = [b, t] + [[b[i], b[(i+1)%len(b)], t[(i+1)%len(b)], t[i]] for i in range(len(b))]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8", "#0096c7", "#0077b6", "#023e8a"], alpha=0.88)
    mc = np.vstack([m, m[0]])
    ax.plot(mc[:,0], mc[:,1], mc[:,2], color="#a8201a", lw=2.4, ls="--")
    ax.text(m[:,0].mean(), m[:,1].mean(), L/2, "Aₘ at mean linear scale", color="#a8201a", fontsize=12, fontweight="bold")
    add_dim_line(ax, (b[:,0].min()*0.9, b[:,1].min()*0.9, 0), (b[:,0].min()*0.9, b[:,1].min()*0.9, L), "L")
    allp = np.vstack([b, t, m])
    equalize_3d(ax, allp[:,0], allp[:,1], allp[:,2])




def calc_cube(p):
    """Calculate the volume of a cube from edge a."""
    a = p["a"]
    V = a ** 3
    return {
        "title": "Cube",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = a³",
            "",
            "Substitution:",
            f"  V = ({fmt(a)})³ = {fmt(V)}",
        ],
    }


def calc_triangular_prism(p):
    """Calculate a triangular prism volume from triangular area and length."""
    b, ht, L = p["b"], p["ht"], p["L"]
    B = 0.5 * b * ht
    V = B * L
    return {
        "title": "Triangular prism",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = B L, with triangular base area B = (1/2) b h",
            "",
            "Substitution:",
            f"  B = (1/2)({fmt(b)})({fmt(ht)}) = {fmt(B)}",
            f"  V = B L = ({fmt(B)})({fmt(L)}) = {fmt(V)}",
        ],
    }


def calc_hex_prism(p):
    """Calculate a regular hexagonal prism from side length and prism length."""
    s, L = p["s"], p["L"]
    B = 3 * math.sqrt(3) / 2 * s ** 2
    V = B * L
    return {
        "title": "Regular hexagonal prism",
        "volume": V,
        "lines": [
            "Formula:",
            "  B = (3√3/2) s²",
            "  V = B L",
            "",
            "Substitution:",
            f"  B = (3√3/2)({fmt(s)})² = {fmt(B)}",
            f"  V = ({fmt(B)})({fmt(L)}) = {fmt(V)}",
        ],
    }


def calc_oblique_prism(p):
    """Calculate an oblique prism/parallelepiped using perpendicular height."""
    a, b, h = p["a"], p["b"], p["h"]
    B = a * b
    V = B * h
    return {
        "title": "Oblique prism / parallelepiped",
        "volume": V,
        "lines": [
            "Formula:",
            "  V = B h = a b h",
            "  where h is the perpendicular distance between the parallel bases.",
            "",
            "Substitution:",
            f"  B = ({fmt(a)})({fmt(b)}) = {fmt(B)}",
            f"  V = ({fmt(B)})({fmt(h)}) = {fmt(V)}",
        ],
    }


def draw_cube(ax, p):
    """Draw a cube by reusing the cuboid drawing routine."""
    draw_prism(ax, {"a": p["a"], "b": p["a"], "h": p["a"]})


def draw_triangular_prism(ax, p):
    """Draw a triangular prism with base, triangle height and length labels."""
    b, ht, L = p["b"], p["ht"], p["L"]
    pts = np.array([
        [0, 0, 0], [b, 0, 0], [0, ht, 0],
        [0, 0, L], [b, 0, L], [0, ht, L],
    ], dtype=float)
    faces = [
        [pts[0], pts[1], pts[2]],
        [pts[3], pts[4], pts[5]],
        [pts[0], pts[1], pts[4], pts[3]],
        [pts[1], pts[2], pts[5], pts[4]],
        [pts[2], pts[0], pts[3], pts[5]],
    ]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8"], alpha=0.9)
    add_dim_line(ax, (0, -0.07*ht, 0), (b, -0.07*ht, 0), "b")
    add_dim_line(ax, (-0.07*b, 0, 0), (-0.07*b, ht, 0), "h", color="#a8201a")
    add_dim_line(ax, (b*1.05, 0, 0), (b*1.05, 0, L), "L")
    equalize_3d(ax, pts[:,0], pts[:,1], pts[:,2])


def draw_hex_prism(ax, p):
    """Draw a regular hexagonal prism with side and length labels."""
    s, L = p["s"], p["L"]
    ang = np.linspace(0, 2*np.pi, 6, endpoint=False) + np.pi/6
    xb = s * np.cos(ang)
    yb = s * np.sin(ang)
    base = np.column_stack([xb, yb, np.zeros_like(xb)])
    top = np.column_stack([xb, yb, np.full_like(xb, L)])
    faces = [base, top] + [[base[i], base[(i+1)%6], top[(i+1)%6], top[i]] for i in range(6)]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8", "#0096c7", "#0077b6", "#023e8a"], alpha=0.88)
    add_dim_line(ax, (0, 0, 0), (xb[0], yb[0], 0), "s")
    add_dim_line(ax, (max(xb)*1.15, 0, 0), (max(xb)*1.15, 0, L), "L", color="#a8201a")
    equalize_3d(ax, np.r_[base[:,0], top[:,0]], np.r_[base[:,1], top[:,1]], np.r_[base[:,2], top[:,2]])


def draw_oblique_prism(ax, p):
    """Draw an oblique prism/parallelepiped and its perpendicular height."""
    a, b, h = p["a"], p["b"], p["h"]
    dx = 0.45 * a
    dy = 0.25 * b
    base = np.array([[0,0,0],[a,0,0],[a,b,0],[0,b,0]], dtype=float)
    top = base + np.array([dx, dy, h], dtype=float)
    faces = [[base[0], base[1], base[2], base[3]],[top[0], top[1], top[2], top[3]]] + [[base[i], base[(i+1)%4], top[(i+1)%4], top[i]] for i in range(4)]
    add_faces(ax, faces, ["#caf0f8", "#ade8f4", "#90e0ef", "#48cae4", "#00b4d8", "#0096c7"], alpha=0.88)
    add_dim_line(ax, (0, -0.08*b, 0), (a, -0.08*b, 0), "a")
    add_dim_line(ax, (a*1.05, 0, 0), (a*1.05, b, 0), "b")
    add_dim_line(ax, (-0.08*a, 0, 0), (-0.08*a, 0, h), "h", color="#a8201a")
    allp = np.vstack([base, top])
    equalize_3d(ax, allp[:,0], allp[:,1], allp[:,2])


# Central registry of supported solids.  Each entry declares the GUI inputs,
# the calculation function, the drawing function, and the validity note shown
# in the report.  Adding a new solid normally only requires a calc_* function,
# a draw_* function, and one new dictionary entry here.
SOLIDS = {
    "Cube": {
        "params": [
            ("a", "Edge a", 4.0, "m"),
        ],
        "calc": calc_cube,
        "draw": draw_cube,
        "notes": "Special case of a prism with all edges equal.",
    },
    "Triangular prism": {
        "params": [
            ("b", "Triangle base b", 6.0, "m"),
            ("ht", "Triangle height h", 4.0, "m"),
            ("L", "Prism length L", 10.0, "m"),
        ],
        "calc": calc_triangular_prism,
        "draw": draw_triangular_prism,
        "notes": "Prism with triangular cross-section.",
    },
    "Regular hexagonal prism": {
        "params": [
            ("s", "Hexagon side s", 3.0, "m"),
            ("L", "Prism length L", 8.0, "m"),
        ],
        "calc": calc_hex_prism,
        "draw": draw_hex_prism,
        "notes": "Famous prism with a regular hexagonal base.",
    },
    "Oblique prism / parallelepiped": {
        "params": [
            ("a", "Base length a", 5.0, "m"),
            ("b", "Base width b", 3.0, "m"),
            ("h", "Perpendicular height h", 6.0, "m"),
        ],
        "calc": calc_oblique_prism,
        "draw": draw_oblique_prism,
        "notes": "Oblique prism volume still uses base area times perpendicular height.",
    },
    "Right rectangular prism / cuboid": {
        "params": [
            ("a", "Length a", 4.0, "m"),
            ("b", "Width b", 3.0, "m"),
            ("h", "Height h", 5.0, "m"),
        ],
        "calc": calc_prism,
        "draw": draw_prism,
        "notes": "Exact prism volume: V = a b h.",
    },
    "Cylinder": {
        "params": [
            ("r", "Radius r", 3.0, "m"),
            ("h", "Height h", 10.0, "m"),
        ],
        "calc": calc_cylinder,
        "draw": draw_cylinder,
        "notes": "Curved analogue of a prism. Exact because cross-sectional area is constant.",
    },
    "Square pyramid": {
        "params": [
            ("a", "Base side a", 6.0, "m"),
            ("h", "Height h", 9.0, "m"),
        ],
        "calc": calc_square_pyramid,
        "draw": draw_square_pyramid,
        "notes": "Pyramid as a prismoidal limiting case: one end area is zero.",
    },
    "Right circular cone": {
        "params": [
            ("r", "Base radius r", 3.0, "m"),
            ("h", "Height h", 8.0, "m"),
        ],
        "calc": calc_cone,
        "draw": draw_cone,
        "notes": "Cone as a curved prismoidal limiting case.",
    },
    "Frustum of a pyramid / similar bases": {
        "params": [
            ("A1", "Lower area A₁", 100.0, "m²"),
            ("A2", "Upper area A₂", 36.0, "m²"),
            ("h", "Height h", 12.0, "m"),
        ],
        "calc": calc_pyramid_frustum,
        "draw": draw_pyramid_frustum,
        "notes": "Exact for similar parallel polygonal bases.",
    },
    "Frustum of a cone": {
        "params": [
            ("R", "Lower radius R", 5.0, "m"),
            ("r", "Upper radius r", 2.0, "m"),
            ("h", "Height h", 10.0, "m"),
        ],
        "calc": calc_cone_frustum,
        "draw": draw_cone_frustum,
        "notes": "Exact conical frustum formula and equivalent area form.",
    },
    "Triangular wedge": {
        "params": [
            ("b", "Triangle base b", 6.0, "m"),
            ("ht", "Triangle height h", 4.0, "m"),
            ("L", "Extrusion length L", 10.0, "m"),
        ],
        "calc": calc_wedge,
        "draw": draw_wedge,
        "notes": "Wedges are basic components in prismoid decompositions.",
    },
    "General prismoid / prismatoid": {
        "params": [
            ("A1", "End area A₁", 20.0, "m²"),
            ("Am", "Middle area Aₘ", 26.0, "m²"),
            ("A2", "End area A₂", 40.0, "m²"),
            ("L", "Spacing L", 15.0, "m"),
        ],
        "calc": calc_general_prismoid,
        "draw": draw_general_prismoid,
        "notes": "Requires the real middle area Aₘ.",
    },
    "Sphere": {
        "params": [
            ("r", "Radius r", 4.0, "m"),
        ],
        "calc": calc_sphere,
        "draw": draw_sphere,
        "notes": "Exact by Simpson/prismoidal integration across the diameter.",
    },
    "Average end-area method": {
        "params": [
            ("A1", "End area A₁", 20.0, "m²"),
            ("A2", "End area A₂", 40.0, "m²"),
            ("L", "Spacing L", 15.0, "m"),
        ],
        "calc": calc_average_end_area,
        "draw": draw_average_end_area,
        "notes": "Useful approximation when the middle section is unknown.",
    },
    "General prismoidal correction": {
        "params": [
            ("A1", "End area A₁", 20.0, "m²"),
            ("Am", "Middle area Aₘ", 26.0, "m²"),
            ("A2", "End area A₂", 40.0, "m²"),
            ("L", "Spacing L", 15.0, "m"),
        ],
        "calc": calc_general_correction,
        "draw": draw_general_correction,
        "notes": "Correction C = V_EA − V_P; sign convention is explicit.",
    },
    "Homothetic irregular polygon correction": {
        "params": [
            ("A1", "Irregular polygon area A₁", 25.0, "m²"),
            ("A2", "Irregular polygon area A₂", 64.0, "m²"),
            ("L", "Plane spacing L", 9.0, "m"),
        ],
        "calc": calc_homothetic_irregular,
        "draw": draw_homothetic_irregular,
        "notes": "Exact only for same-shape irregular polygons with uniform scale change.",
    },
}


def validate_parameters(solid_name, params):
    """Validation rules common to all supported solids."""
    for key, value in params.items():
        if value <= 0:
            raise ValueError(f"{key} must be positive. Current value: {value!r}.")
    if solid_name == "Frustum of a cone":
        if params["R"] <= 0 or params["r"] <= 0:
            raise ValueError("Both radii must be positive.")
    if solid_name == "Homothetic irregular polygon correction":
        if params["A1"] <= 0 or params["A2"] <= 0:
            raise ValueError("Both polygon areas must be positive.")
    return True


class VolumeCalculatorApp(tk.Tk):
    def __init__(self):
        """Create the fixed-size GUI, initialise state, and draw the first solid."""
        super().__init__()
        self.title(f"{APP_TITLE} — {VERSION}")
        # Determine a fixed, screen-aware window size.  The application remains
        # non-resizable, but the height is now slightly reduced compared with
        # the previous version and is capped below the physical screen height.
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        desired_w = max(WINDOW_MIN_WIDTH, int(sw * WINDOW_WIDTH_RATIO))
        desired_h = max(WINDOW_MIN_HEIGHT, int(sh * WINDOW_HEIGHT_RATIO))
        usable_w = max(900, sw - WINDOW_SCREEN_MARGIN_X)
        usable_h = max(680, sh - WINDOW_SCREEN_MARGIN_Y)
        w = min(WINDOW_MAX_WIDTH, desired_w, usable_w)
        h = min(WINDOW_MAX_HEIGHT, desired_h, usable_h)
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(w, h)
        self.maxsize(w, h)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        self.current_solid = tk.StringVar(value="Homothetic irregular polygon correction")
        self.entries = {}
        self.last_report = ""

        self._make_style()
        self._build_layout()
        self._populate_inputs()
        self.after(200, self.calculate)

    def _make_style(self):
        """Configure ttk styles, fonts, colours and button appearances."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"], relief="flat")
        style.configure("Header.TFrame", background=COLORS["header"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("Muted.Panel.TLabel", background=COLORS["panel"], foreground=COLORS["muted"])
        style.configure("Header.TLabel", background=COLORS["header"], foreground="white", font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"))
        style.configure("Subheader.TLabel", background=COLORS["header"], foreground="#d5ecff", font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TLabelframe", background=COLORS["panel"], foreground=COLORS["header"])
        style.configure("TLabelframe.Label", background=COLORS["panel"], foreground=COLORS["header"], font=(FONT_FAMILY, FONT_SIZE, "bold"))

        style.configure(
            "Accent.TButton",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            background=COLORS["accent"],
            foreground="white",
            borderwidth=0,
            focusthickness=3,
            focuscolor=COLORS["accent2"],
            padding=(10, 7),
        )
        style.map("Accent.TButton", background=[("active", COLORS["accent2"])])

        style.configure(
            "Soft.TButton",
            font=(FONT_FAMILY, FONT_SIZE),
            background="#d8ecfa",
            foreground=COLORS["header"],
            borderwidth=0,
            padding=(9, 6),
        )
        style.map("Soft.TButton", background=[("active", "#b9dcf4")])

        style.configure("TCombobox", fieldbackground="white", background="white", foreground=COLORS["text"])

    def _build_layout(self):
        """Build the fixed 50/50 GUI layout: inputs/report on left, 3D view on right."""
        header = ttk.Frame(self, style="Header.TFrame", padding=(18, 14, 18, 14))
        header.pack(fill="x")

        ttk.Label(header, text=APP_TITLE, style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text=f"{APP_SUBTITLE}   |   version: {VERSION}", style="Subheader.TLabel").pack(anchor="w", pady=(4, 0))

        # Fixed 50/50 split layout: no resizable panes, no draggable subwindows.
        content = ttk.Frame(self, padding=10, style="TFrame")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1, uniform="half")
        content.columnconfigure(1, weight=1, uniform="half")
        content.rowconfigure(0, weight=1)

        self.left = ttk.Frame(content, style="Panel.TFrame", padding=14)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.left.rowconfigure(4, weight=1)
        self.left.columnconfigure(0, weight=1)

        self.right_panel = ttk.Frame(content, style="Panel.TFrame", padding=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        # RIGHT HALF: large fixed solid view.  The figure request was reduced
        # slightly to match the lower application window height while preserving
        # a clear 3D view of the solid.
        self.figure = Figure(figsize=(7.7, 7.7), dpi=100, facecolor="white")
        self.ax = self.figure.add_subplot(111, projection="3d")
        self.figure.subplots_adjust(left=0.00, right=1.00, bottom=0.00, top=0.95)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        toolbar_frame = ttk.Frame(self.right_panel, style="Panel.TFrame", padding=(2, 2))
        toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="left")

        # LEFT HALF: inputs, visible result, and GUI report/output window.
        ttk.Label(self.left, text="Solid / method", style="Panel.TLabel", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold")).grid(row=0, column=0, sticky="ew")

        self.selector = ttk.Combobox(
            self.left,
            textvariable=self.current_solid,
            values=list(SOLIDS.keys()),
            state="readonly",
            width=42,
            font=(FONT_FAMILY, FONT_SIZE),
        )
        self.selector.grid(row=1, column=0, sticky="ew", pady=(6, 10))
        self.selector.bind("<<ComboboxSelected>>", self._on_solid_change)

        self.notes_label = ttk.Label(self.left, text="", style="Muted.Panel.TLabel", wraplength=620, justify="left")
        self.notes_label.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        top_input_area = ttk.Frame(self.left, style="Panel.TFrame")
        top_input_area.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        top_input_area.columnconfigure(0, weight=1)
        top_input_area.columnconfigure(1, weight=1)

        self.inputs_frame = ttk.LabelFrame(top_input_area, text="Geometric dimensions", padding=12)
        self.inputs_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        result_frame = ttk.LabelFrame(top_input_area, text="Calculated result", padding=12)
        result_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        result_frame.columnconfigure(0, weight=1)

        self.result_title = ttk.Label(result_frame, text="Volume", style="Panel.TLabel", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"))
        self.result_title.grid(row=0, column=0, sticky="w")

        self.result_value = ttk.Label(
            result_frame,
            text="—",
            style="Panel.TLabel",
            foreground=COLORS["ok"],
            font=(FONT_FAMILY, FONT_SIZE_RESULT, "bold"),
            wraplength=330,
            justify="left",
        )
        self.result_value.grid(row=1, column=0, sticky="ew", pady=(6, 4))

        self.correction_value = ttk.Label(
            result_frame,
            text="",
            style="Muted.Panel.TLabel",
            font=(FONT_FAMILY, FONT_SIZE),
            wraplength=330,
            justify="left",
        )
        self.correction_value.grid(row=2, column=0, sticky="ew")

        btns = ttk.Frame(result_frame, style="Panel.TFrame")
        btns.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(btns, text="Calculate", style="Accent.TButton", command=self.calculate).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btns, text="Reset", style="Soft.TButton", command=self._reset_current).pack(side="left", fill="x", expand=True, padx=(5, 0))

        ttk.Label(
            self.left,
            text="Results output",
            style="Panel.TLabel",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
        ).grid(row=4, column=0, sticky="nw", pady=(0, 0))

        self.output = ScrolledText(
            self.left,
            height=18,
            font=("Consolas", 12),
            bg="#fbfdff",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=1,
            wrap="word",
        )
        self.output.grid(row=4, column=0, sticky="nsew", pady=(26, 10))

        bottom_buttons = ttk.Frame(self.left, style="Panel.TFrame")
        bottom_buttons.grid(row=5, column=0, sticky="ew")
        bottom_buttons.columnconfigure(0, weight=1)
        bottom_buttons.columnconfigure(1, weight=1)
        bottom_buttons.columnconfigure(2, weight=1)
        bottom_buttons.columnconfigure(3, weight=1)
        ttk.Button(bottom_buttons, text="Copy report", style="Soft.TButton", command=self.copy_report).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(bottom_buttons, text="Save TXT", style="Soft.TButton", command=self.save_report).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(bottom_buttons, text="Redraw solid", style="Soft.TButton", command=self.calculate).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(bottom_buttons, text="Usage / build", style="Soft.TButton", command=self.show_usage).grid(row=0, column=3, sticky="ew", padx=(4, 0))

    def _populate_inputs(self):
        """Rebuild the input fields required by the currently selected solid."""
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        solid = SOLIDS[self.current_solid.get()]
        self.notes_label.configure(text=solid["notes"])

        for row, (key, label, default, unit) in enumerate(solid["params"]):
            ttk.Label(self.inputs_frame, text=label, style="Panel.TLabel", font=(FONT_FAMILY, FONT_SIZE)).grid(row=row, column=0, sticky="w", pady=6)
            var = tk.StringVar(value=fmt(default))
            entry = ttk.Entry(self.inputs_frame, textvariable=var, width=14, font=(FONT_FAMILY, FONT_SIZE_LARGE))
            entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(8, 6))
            ttk.Label(self.inputs_frame, text=unit, style="Muted.Panel.TLabel", font=(FONT_FAMILY, FONT_SIZE)).grid(row=row, column=2, sticky="w", pady=6)
            entry.bind("<Return>", lambda event: self.calculate())
            entry.bind("<FocusOut>", lambda event: self.calculate())
            self.entries[key] = (var, label)
        self.inputs_frame.columnconfigure(1, weight=1)

    def _on_solid_change(self, event=None):
        """Handle combobox changes by loading the new parameter set and recalculating."""
        self._populate_inputs()
        self.calculate()

    def _reset_current(self):
        """Restore default dimensions for the selected solid and recalculate."""
        self._populate_inputs()
        self.calculate()

    def _read_params(self):
        """Read, parse and validate all input values from the GUI entry widgets."""
        params = {}
        for key, (var, label) in self.entries.items():
            params[key] = parse_float(var.get(), label)
        validate_parameters(self.current_solid.get(), params)
        return params

    def calculate(self):
        """Run the selected formula, redraw the solid, and refresh the report output."""
        solid_name = self.current_solid.get()
        solid = SOLIDS[solid_name]

        # 1) Read/validate input values and execute the selected calculation.
        try:
            params = self._read_params()
            result = solid["calc"](params)
        except Exception as exc:
            self._show_error(str(exc))
            return

        # 2) Redraw the 3D panel from scratch so switching between solids never
        # leaves old geometry or labels on the canvas.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection="3d")
        self.figure.subplots_adjust(left=0.00, right=1.00, bottom=0.00, top=0.95)
        set_axes_clean(self.ax, result["title"])
        try:
            self.ax.set_proj_type("ortho")
        except Exception:
            pass
        self.ax.view_init(elev=21, azim=-52)

        try:
            solid["draw"](self.ax, params)
        except Exception as exc:
            self.ax.text2D(0.05, 0.95, f"Drawing error: {exc}", transform=self.ax.transAxes, color=COLORS["danger"])

        self.canvas.draw_idle()

        # 3) Update the prominent numerical result and, where available, expose
        # the correction line immediately below it.
        self.result_value.configure(text=f"{fmt(result['volume'])} m³")
        correction_line = ""
        for line in result.get("lines", []):
            if "Correction to subtract C" in line or line.strip().startswith("C =") or "C = V_EA" in line:
                correction_line = line.strip()
        self.correction_value.configure(text=correction_line)

        # 4) Build the detailed text report.  This single string is used both for
        # the GUI output area and for Save TXT, preventing inconsistencies.
        report = self._build_report(solid_name, params, result)
        self.last_report = report

        # Critical: the exact text that Save TXT writes is also visible here.
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", self.last_report)
        self.output.see("1.0")
        self.output.configure(state="normal")

    def _build_report(self, solid_name, params, result):
        """Assemble the complete text report shown in the GUI and saved to TXT."""
        lines = []
        lines.append("=" * 78)
        lines.append(result["title"].upper())
        lines.append("=" * 78)
        lines.append("")
        lines.append("INPUT DATA")
        lines.append("-" * 78)
        for key, (var, label) in self.entries.items():
            unit = next((u for k, _, _, u in SOLIDS[solid_name]["params"] if k == key), "")
            lines.append(f"{label:<34} = {fmt(params[key]):>14} {unit}")
        lines.append("")
        lines.extend(result["lines"])
        lines.append("")
        lines.append("RESULT")
        lines.append("-" * 78)
        lines.append(f"Volume = {fmt(result['volume'])} m³")
        lines.append("")
        lines.append("Validity note:")
        lines.append(textwrap.fill(SOLIDS[solid_name]["notes"], width=78))
        lines.append("")
        return "\n".join(lines)

    def _show_error(self, msg):
        """Display validation or calculation errors in both the plot area and report box."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.55, "Input error", ha="center", va="center", fontsize=18, color=COLORS["danger"], fontweight="bold")
        ax.text(0.5, 0.45, msg, ha="center", va="center", fontsize=11, color=COLORS["text"], wrap=True)
        self.canvas.draw_idle()
        if hasattr(self, "result_value"):
            self.result_value.configure(text="Input error")
        if hasattr(self, "correction_value"):
            self.correction_value.configure(text=msg)

        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", f"INPUT ERROR\n{'-'*78}\n{msg}\n")
        self.output.configure(state="normal")

    def copy_report(self):
        """Copy the current calculation report to the system clipboard."""
        if not self.last_report.strip():
            self.calculate()
        self.clipboard_clear()
        self.clipboard_append(self.last_report)
        self.update()
        messagebox.showinfo("Copied", "The calculation report was copied to the clipboard.")

    def show_usage(self):
        """Open a read-only window with installation, run and PyInstaller commands."""
        # A separate Toplevel window is used instead of a message box because the
        # command list is long and users often need to select/copy the commands.
        win = tk.Toplevel(self)
        win.title("Usage and build instructions")
        win.configure(bg=COLORS["bg"])
        win.resizable(False, False)
        win.geometry("780x520")
        txt = ScrolledText(
            win,
            font=("Consolas", 11),
            bg="#fbfdff",
            fg=COLORS["text"],
            relief="flat",
            borderwidth=1,
            wrap="word",
        )
        txt.pack(fill="both", expand=True, padx=12, pady=12)
        txt.insert("1.0", USAGE_TEXT)
        txt.configure(state="disabled")

    def save_report(self):
        """Save the exact GUI report text to a user-selected TXT file."""
        if not self.last_report.strip():
            self.calculate()
        filename = filedialog.asksaveasfilename(
            title="Save calculation report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="output.txt",
        )
        if not filename:
            return
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.last_report)  # same text displayed in the GUI output window
        messagebox.showinfo("Saved", f"Report saved to:\n{filename}")


def main():
    """Application entry point used when the script is run directly."""
    app = VolumeCalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
