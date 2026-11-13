"""Preview aproximado das visões do modelo (NÃO substitui o PDF exportado do Archi).

Uso: python render_preview.py <pasta_com_modelo.json> [escala]
Gera preview-<n>.png para cada visão.
"""
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

pasta = Path(sys.argv[1])
S = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
M = json.loads((pasta / "modelo.json").read_text(encoding="utf-8"))
E, R, VIEWS = M["E"], M["R"], M["VIEWS"]

COR = {"motivation": (204, 204, 255), "business": (255, 255, 181), "application": (181, 255, 255),
       "technology": (201, 231, 183)}
LAYER_OF = {
    "Stakeholder": "motivation", "Driver": "motivation", "Assessment": "motivation", "Goal": "motivation",
    "Outcome": "motivation", "Principle": "motivation", "Requirement": "motivation", "Constraint": "motivation",
}
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", max(8, int(12 * S)))  # ~ Segoe UI 9pt do Archi
FONTB = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", max(9, int(14 * S)))


def color(t):
    if t in LAYER_OF:
        return COR["motivation"]
    if t.startswith("Business"):
        return COR["business"]
    if t.startswith("Application") or t == "DataObject":
        return COR["application"]
    return COR["technology"]


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wrap(text, width_px, font, d):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width_px:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(vname, layer, idx):
    keys = [k for k, e in E.items() if layer is None or e["layer"] == layer]
    ks = set(keys)
    top = min(E[k]["y"] for k in keys if not E[k]["parent"])
    dy = 20 - top if layer else 0
    maxx = max(E[k]["x"] + E[k]["w"] for k in keys) + 30
    maxy = max(E[k]["y"] + E[k]["h"] for k in keys) + dy + 30
    img = Image.new("RGB", (int(maxx * S), int(maxy * S)), "white")
    d = ImageDraw.Draw(img)

    def box(k):
        e = E[k]
        return (e["x"] * S, (e["y"] + dy) * S, (e["x"] + e["w"]) * S, (e["y"] + e["h"] + dy) * S)

    def depth(k):
        n = 0
        while E[k]["parent"]:
            k = E[k]["parent"]; n += 1
        return n

    order = sorted(keys, key=lambda k: (0 if E[k]["type"] == "Grouping" and E[k]["w"] > 1500 else 1, depth(k)))
    groups = [k for k in order if E[k]["type"] == "Grouping"]
    others = [k for k in order if E[k]["type"] != "Grouping"]
    for k in groups:
        x0, y0, x1, y1 = box(k)
        d.rectangle((x0, y0, x1, y1), fill=hexrgb(E[k]["fill"]) if E[k]["fill"] else None, outline=(90, 90, 90),
                    width=max(1, int(S)))
        d.text((x0 + 8 * S, y0 + 6 * S), E[k]["name"], fill=(40, 40, 40), font=FONTB)

    def anc(k):
        out = []
        while E[k]["parent"]:
            k = E[k]["parent"]; out.append(k)
        return out

    # conexões (antes das caixas para ficarem atrás)
    for r in R:
        if not r["show"] or (r["show"] == "layer" and layer is None) or r["src"] not in ks or r["tgt"] not in ks:
            continue
        if r["tgt"] in anc(r["src"]) or r["src"] in anc(r["tgt"]):
            continue
        a, b = box(r["src"]), box(r["tgt"])
        ca = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2)
        cb = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)

        def clip(c, bx, other):
            dx, dy_ = other[0] - c[0], other[1] - c[1]
            hw, hh = (bx[2] - bx[0]) / 2, (bx[3] - bx[1]) / 2
            if dx == 0 and dy_ == 0:
                return c
            t = min(hw / abs(dx) if dx else 1e9, hh / abs(dy_) if dy_ else 1e9)
            return (c[0] + dx * t, c[1] + dy_ * t)
        rt = [(x * S, y * S) for x, y in M.get("ROUTES", {}).get(vname, {}).get(r["id"], [])]
        if rt:
            path = [clip(ca, a, rt[0])] + rt + [clip(cb, b, rt[-1])]
        else:
            path = [clip(ca, a, cb), clip(cb, b, ca)]
        dashed = r["type"] in ("Influence", "Realization", "Access", "Flow")
        col = (70, 70, 70)
        for p0, p1 in zip(path, path[1:]):
            if dashed:
                L = math.dist(p0, p1); n = max(1, int(L / (6 * S)))
                for i in range(0, n, 2):
                    q0 = (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
                    q1 = (p0[0] + (p1[0] - p0[0]) * min(i + 1, n) / n, p0[1] + (p1[1] - p0[1]) * min(i + 1, n) / n)
                    d.line((q0, q1), fill=col, width=max(1, int(S)))
            else:
                d.line((p0, p1), fill=col, width=max(1, int(S)))
        p0, p1 = path[-2], path[-1]
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); s = 9 * S
        tri = [p1, (p1[0] - s * math.cos(ang - 0.4), p1[1] - s * math.sin(ang - 0.4)),
               (p1[0] - s * math.cos(ang + 0.4), p1[1] - s * math.sin(ang + 0.4))]
        if r["type"] in ("Serving", "Influence", "Triggering", "Flow"):
            d.line([tri[1], p1, tri[2]], fill=col, width=max(1, int(S)))
        elif r["type"] == "Realization":
            d.polygon(tri, fill="white", outline=col)
        elif r["type"] in ("Composition", "Aggregation", "Assignment"):
            r0 = 3 * S
            q = path[0]
            d.ellipse((q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0), fill=col)
            d.polygon(tri, fill=col)
        if r["name"]:
            m = path[len(path) // 2 - 1], path[len(path) // 2]
            d.text(((m[0][0] + m[1][0]) / 2 + 3, (m[0][1] + m[1][1]) / 2 + 2), r["name"], fill=(120, 0, 0), font=FONT)

    for k in others:
        e = E[k]
        x0, y0, x1, y1 = box(k)
        rad = 10 * S if "Service" in e["type"] or e["type"] in ("Goal", "Outcome") else 4 * S
        d.rounded_rectangle((x0, y0, x1, y1), radius=rad, fill=color(e["type"]), outline=(60, 60, 60),
                            width=max(1, int(S)))
        has_kids = any(E[c]["parent"] == k for c in ks)
        lines = wrap(e["name"], (e["w"] - 10) * S, FONT, d)
        lh = FONT.size + 2
        ty = y0 + 4 * S if has_kids else (y0 + y1) / 2 - lh * len(lines) / 2
        for ln in lines:
            tw = d.textlength(ln, font=FONT)
            d.text(((x0 + x1) / 2 - tw / 2, ty), ln, fill="black", font=FONT)
            ty += lh
    out = pasta / f"preview-{idx}.png"
    img.save(out)
    return out


for i, (vn, ly) in enumerate(VIEWS):
    print(render(vn, ly, i))
