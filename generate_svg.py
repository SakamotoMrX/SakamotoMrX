import html

# ─────────────────── CONFIG ────────────────────────────────────────────────
SVG_W    = 985
SVG_H    = 530
FONT_SZ  = 18          # bigger since full width
LINE_H   = 22
PAD_L    = 20          # left padding
TEXT_Y   = 35
BG       = "#161b22"
C_TITLE  = "#c9d1d9"
C_KEY    = "#ffa657"
C_VAL    = "#a5d6ff"
C_DOTS   = "#616e7f"

# ─────────────────── STATS ─────────────────────────────────────────────────
stats = [
    ("title", "andrahijati@JuniorDevops", ""),
    ("row",   ". OS:",                    "Macos, Linux, Windows"),
    ("row",   ". Uptime:",                "15 years, 5 months"),
    ("row",   ". Host:",                  "Junior Devops"),
    ("row",   ". Shell:",                 "Bogor, Indonesia"),
    ("row",   ". IDE:",                   "Antigravity IDE, Vim, Nvim, Lazygit, Arduino IDE"),
    ("sep",   "",                         ""),
    ("row",   ". Languages.Programming:", "Bash"),
    ("row",   ". Languages.Computer:",    "YAML"),
    ("row",   ". Languages.Real:",        "Indonesia, English"),
    ("sep",   "",                         ""),
    ("row",   ". Skills.System:",         "LinuxSysAdmin, VM, Containerization"),
    ("row",   ". Skills.WebDev:",         "Basic Website, Git & GitHub, Deploying"),
    ("row",   ". Skills.Process:",        "SDLC & Agile"),
    ("sep",   "",                         ""),
    ("row",   ". Hobbies.Software:",      "Larping Linux"),
    ("row",   ". Hobbies.Hardware:",      "Arduino"),
    ("sep",   "",                         ""),
    ("sect",  "- Contact",               ""),
    ("row",   ". Email.Personal:",        "andrahijati@gmail.com"),
    ("row",   ". Discord:",               "legacyy5030"),
    ("row",   ". Facebook:",              "https://web.facebook.com/andra.nugroho.921"),
]

# ─────────────────── SVG BUILD ─────────────────────────────────────────────
def esc(s): return html.escape(str(s))

# Consolas 18px: approx 10.8px per char
CHAR_W     = 10.8
RIGHT_EDGE = SVG_W - PAD_L

out = []
out.append(f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="Consolas,Menlo,monospace" width="{SVG_W}px" height="{SVG_H}px" font-size="{FONT_SZ}px">
<style>
@font-face {{
  src: local('Consolas'), local('Menlo');
  font-family: 'Consolas';
  font-display: swap;
}}
.key   {{fill: {C_KEY};}}
.val   {{fill: {C_VAL};}}
.title {{fill: {C_TITLE}; font-weight: bold;}}
.dots  {{fill: {C_DOTS};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{SVG_W}px" height="{SVG_H}px" fill="{BG}" rx="12"/>''')

y = TEXT_Y
for kind, key, val in stats:
    if kind == "sep":
        y += LINE_H
        continue

    if kind == "title":
        key_px   = PAD_L + len(key) * CHAR_W
        dashes_n = max(1, int((RIGHT_EDGE - key_px - CHAR_W) / CHAR_W))
        out.append(
            f'<text x="{PAD_L}" y="{y}">'
            f'<tspan class="title">{esc(key)}</tspan>'
            f'<tspan class="dots"> {"─" * dashes_n}</tspan>'
            f'</text>')
        y += LINE_H
        continue

    if kind == "sect":
        key_px   = PAD_L + len(key) * CHAR_W
        dashes_n = max(1, int((RIGHT_EDGE - key_px - CHAR_W) / CHAR_W))
        out.append(
            f'<text x="{PAD_L}" y="{y}">'
            f'<tspan class="title">{esc(key)} </tspan>'
            f'<tspan class="dots">{"─" * dashes_n}</tspan>'
            f'</text>')
        y += LINE_H
        continue

    # normal row — value right-aligned
    val_x   = RIGHT_EDGE - len(val) * CHAR_W
    key_end = PAD_L + (len(key) + 1) * CHAR_W
    gap     = val_x - key_end - CHAR_W
    dots_n  = max(1, int(gap / CHAR_W))
    out.append(
        f'<text x="{PAD_L}" y="{y}">'
        f'<tspan class="key">{esc(key)}</tspan>'
        f'<tspan class="dots"> {"." * dots_n} </tspan>'
        f'<tspan class="val">{esc(val)}</tspan>'
        f'</text>')
    y += LINE_H

out.append('</svg>')

with open("terminal_profile.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

with open("README.md", "w") as f:
    f.write(
        '<a href="https://github.com/SakamotoMrX/SakamotoMrX">\n'
        '  <picture>\n'
        '    <source media="(prefers-color-scheme: dark)" srcset="terminal_profile.svg">\n'
        '    <img src="terminal_profile.svg" alt="andrahijati terminal profile">\n'
        '  </picture>\n'
        '</a>\n'
    )
print(f"Done! Final y={y}, SVG_H={SVG_H}")
