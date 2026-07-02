# Prismoidal and Classical Solid Volume Calculator

A self-contained Python/Tkinter graphical calculator for classical solid volumes, prismoids, prismatoids, frusta, average end-area volumes, general prismoidal corrections, and homothetic irregular-polygon frusta.

The application is intended for technical geometry, surveying, earthworks, engineering volume checks, and teaching/verification of prismoidal and frustum formulae. It combines numerical volume calculation with a large 3D graphical view of the selected solid and a full text calculation report.

---

## Main capabilities

- Graphical fixed-size Tkinter interface.
- Left panel for solid selection, input data, calculated volume, correction line, and full calculation report.
- Right panel with a large Matplotlib 3D view of the selected solid.
- Dimension labels in the 3D view.
- Output report displayed directly in the GUI.
- Report export to `output.txt` using the **Save TXT** button.
- Decimal comma accepted in numeric inputs.
- Input validation for positive lengths, areas, and radii.
- Built-in usage/build instructions accessible from the GUI.
- Compatible with normal Python execution and PyInstaller one-file executable builds.

---

## Supported solids and calculation methods

The script includes the following solids and volume methods:

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
14. Average end-area method
15. General prismoidal correction
16. Homothetic irregular polygonal frustum / correction

---

## Formula reference

This section gives only the general formulae used by the program. No numerical worked examples are included.

### Cube

For cube edge length `a`:

$$
V = a^3
$$

### Right rectangular prism / cuboid

For base dimensions `a` and `b`, and perpendicular height `h`:

$$
B = ab
$$

$$
V = Bh = abh
$$

### Oblique prism / parallelepiped

For base area `B` and perpendicular distance `h` between the parallel bases:

$$
V = Bh
$$

When the base is rectangular:

$$
B = ab
$$

$$
V = abh
$$

The height must be the perpendicular height, not the sloping edge length.

### Triangular prism

For triangular base width `b`, triangular height `h`, and prism length `L`:

$$
B = \frac{1}{2}bh
$$

$$
V = BL = \frac{1}{2}bhL
$$

### Regular hexagonal prism

For regular hexagon side length `s` and prism length `L`:

$$
B = \frac{3\sqrt{3}}{2}s^2
$$

$$
V = BL
$$

### Cylinder

For radius `r` and height `h`:

$$
A = \pi r^2
$$

$$
V = \pi r^2 h
$$

### Square pyramid

For square base side `a` and height `h`:

$$
B = a^2
$$

$$
V = \frac{1}{3}Bh = \frac{1}{3}a^2h
$$

As a prismoidal limiting case:

$$
A_1 = 0, \quad A_2 = B, \quad A_m = \frac{B}{4}
$$

$$
V = \frac{h}{6}(A_1 + 4A_m + A_2)
$$

### Right circular cone

For base radius `r` and height `h`:

$$
V = \frac{1}{3}\pi r^2h
$$

As a prismoidal limiting case:

$$
A_1 = 0, \quad A_2 = \pi r^2, \quad A_m = \frac{A_2}{4}
$$

$$
V = \frac{h}{6}(A_1 + 4A_m + A_2)
$$

### Similar-base pyramid frustum

For lower area `A_1`, upper area `A_2`, and perpendicular height `h`:

$$
V = \frac{h}{3}\left(A_1 + \sqrt{A_1A_2} + A_2\right)
$$

The equivalent prismoidal middle area is:

$$
A_m = \left(\frac{\sqrt{A_1}+\sqrt{A_2}}{2}\right)^2
$$

The same volume may be written as:

$$
V = \frac{h}{6}(A_1 + 4A_m + A_2)
$$

### Conical frustum

For lower radius `R`, upper radius `r`, and height `h`:

$$
V = \frac{\pi h}{3}\left(R^2 + Rr + r^2\right)
$$

In area form:

$$
A_1 = \pi R^2
$$

$$
A_2 = \pi r^2
$$

$$
V = \frac{h}{3}\left(A_1 + \sqrt{A_1A_2} + A_2\right)
$$

### Triangular wedge

For triangular base width `b`, triangular height `h`, and extrusion length `L`:

$$
V = \frac{1}{2}bhL
$$

### General prismoid / prismatoid

For two parallel end areas `A_1` and `A_2`, middle area `A_m`, and perpendicular spacing `L`:

$$
V_P = \frac{L}{6}(A_1 + 4A_m + A_2)
$$

This formula requires the actual middle area `A_m`. For arbitrary non-similar irregular end sections, `A_m` cannot be inferred from `A_1` and `A_2` alone.

### Sphere

For sphere radius `r`:

$$
V = \frac{4}{3}\pi r^3
$$

The same result is obtained by Simpson/prismoidal integration across the diameter:

$$
A_1 = 0, \quad A_m = \pi r^2, \quad A_2 = 0, \quad L = 2r
$$

$$
V = \frac{L}{6}(A_1 + 4A_m + A_2)
$$

### Average end-area method

For two end areas `A_1` and `A_2`, separated by distance `L`:

$$
V_{EA} = \frac{L}{2}(A_1 + A_2)
$$

This method is exact when the cross-sectional area varies linearly between the two sections. It is generally approximate for prismoidal or frustum geometry unless the geometry specifically satisfies the end-area assumption.

### General prismoidal correction

The prismoidal volume is:

$$
V_P = \frac{L}{6}(A_1 + 4A_m + A_2)
$$

The average end-area volume is:

$$
V_{EA} = \frac{L}{2}(A_1 + A_2)
$$

With the sign convention used in the script, the correction to subtract from the average end-area volume is:

$$
C = V_{EA} - V_P
$$

Therefore:

$$
C = \frac{L}{3}(A_1 + A_2 - 2A_m)
$$

and:

$$
V_P = V_{EA} - C
$$

### Homothetic irregular polygonal frustum / correction

This method applies when:

- the two end polygons have the same plane shape;
- the two polygons lie in parallel planes;
- the two polygons differ only by uniform linear scaling;
- corresponding vertices are joined by straight generatrices;
- `L` is the perpendicular spacing between the planes.

For end areas `A_1` and `A_2`, the middle area is not the arithmetic mean of the end areas. It is the area corresponding to the average linear scale:

$$
A_m = \left(\frac{\sqrt{A_1}+\sqrt{A_2}}{2}\right)^2
$$

The exact homothetic-frustum volume is:

$$
V = \frac{L}{3}\left(A_1 + \sqrt{A_1A_2} + A_2\right)
$$

The correction to subtract from the average end-area volume is:

$$
C = \frac{L}{6}\left(\sqrt{A_2} - \sqrt{A_1}\right)^2
$$

Therefore:

$$
V = V_{EA} - C
$$

This correction is not valid for arbitrary non-similar irregular polygons. If the end polygons have different shapes, different vertex ordering, twist, local distortion, or non-uniform scale change, the real middle area must be constructed, measured, or obtained by a more general geometric or numerical method.

---

## Installation

### Requirements

- Python 3.10 or later recommended.
- `numpy`
- `matplotlib`
- Tkinter, normally bundled with standard Python installations on Windows and macOS. On some Linux distributions it must be installed separately through the system package manager.

### Windows virtual environment

Open Command Prompt or PowerShell in the project folder:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install matplotlib numpy
```

### Linux/macOS virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install matplotlib numpy
```

---

## Usage

Place the Python file `script.py` in the project folder.

Run with:

```bash
python script.py
```

or:

```bash
python script.py
```

Typical workflow:

1. Select the solid or calculation method from the drop-down list.
2. Enter the required dimensions or areas.
3. Press **Calculate**.
4. Review the calculated volume and correction line.
5. Review the full report in the GUI output box.
6. Use **Save TXT** to write the displayed report to `output.txt`.

The report displayed in the GUI is the same report exported to the text file.

---

## Building a stand-alone executable

### Windows PyInstaller one-file build

Inside the activated virtual environment:

```powershell
py -m pip install pyinstaller
pyinstaller --clean --onefile --windowed --name script --collect-all matplotlib script.py
```

The executable will be created at:

```text
dist\script.exe
```

For debugging, replace `--windowed` with `--console` to show console errors. After validation, rebuild with `--windowed`.

### Linux/macOS PyInstaller one-file build

```bash
python -m pip install pyinstaller
pyinstaller --clean --onefile --windowed --name script --collect-all matplotlib script.py
```

The executable will be created in the `dist` folder.

---

## GUI layout

The interface is intentionally divided into two fixed halves:

- **Left half:** input fields, selected method, calculated volume, correction summary, and full text report.
- **Right half:** large 3D view of the selected solid, with dimension labels and a compact technical plotting style.

The window is non-resizable by design. The dimensions are selected to fit typical laptop and desktop screens while keeping the 3D view readable.

---

## Output files

The script can write the displayed calculation report to:

```text
output.txt
```

No database, external data file, or internet access is required.

---

## Notes and limitations

- All length, radius, spacing, and area inputs must be positive.
- The script assumes consistent units. If lengths are in metres and areas are in square metres, volumes are returned in cubic metres.
- For oblique prisms, the height input is the perpendicular distance between bases.
- For prismoids and prismatoids, the middle area `A_m` must be the real middle section area.
- The homothetic irregular-polygon correction is exact only under the stated same-shape, parallel-plane, uniform-scale assumptions.
- The average end-area method is included for comparison and practical use, but it is not generally equivalent to the prismoidal formula.
- The 3D view is a graphical aid for interpretation and does not replace the formula selected for calculation.

---

## Repository contents

Recommended minimal repository structure:

```text
.
├── README.md
├── script.py
└── output.txt        # created when the user saves a report
```

Optional executable build output:

```text
.
└── dist/
    └── script.exe
```

---