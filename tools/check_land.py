"""Cerca nei tasselli land/ anelli sospetti: lunghi e sottilissimi, oppure con un salto enorme tra due vertici.

Uso: python -I tools/check_land.py cartella_land
"""
import json
import math
import os
import sys

SCALE = 1e4


def rings(block):
    for r in block:
        x, y = r[0], r[1]
        pts = [(x, y)]
        for i in range(2, len(r), 2):
            x += r[i]
            y += r[i + 1]
            pts.append((x, y))
        yield [(a / SCALE, b / SCALE) for a, b in pts]


def main(folder):
    total = 0
    for f in sorted(os.listdir(folder)):
        text = open(os.path.join(folder, f), encoding="utf8").read()
        body = text[text.index("{"): text.rindex("}") + 1]
        data = json.loads(body)
        groups = {"land": data.get("land", [])}
        for k, v in data.items():
            if k != "land" and isinstance(v, dict):
                groups.update({f"{k}:{c}": b for c, b in v.items()})
        for name, block in groups.items():
            for r in rings(block):
                total += 1
                xs, ys = [p[0] for p in r], [p[1] for p in r]
                if min(xs) < -180 or max(xs) > 180:
                    pass
                jump = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(r, r[1:] + r[:1]))
                diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
                area = abs(sum((a[0] - b[0]) * (a[1] + b[1]) / 2 for a, b in zip(r, r[1:] + r[:1])))
                if jump > 1 and (len(r) < 30 or area / max(diag ** 2, 1e-9) < 0.03):
                    print(f, name, "punti", len(r), "salto", round(jump, 2), "diag", round(diag, 2), "area", round(area, 4), "bbox", round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2))
    print("anelli", total)


if __name__ == "__main__":
    main(sys.argv[1])
