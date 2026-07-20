from PIL import Image
import ascii_magic
import html

# ─────────────────── CONFIG ────────────────────────────────────────────────
SVG_W    = 985
SVG_H    = 530
FONT_SZ  = 16
LINE_H   = 20
ASCII_COLS = 38
ASCII_ROWS = 24
TEXT_X   = 405
TEXT_Y   = 30
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
    ("row",   ". Shell:",                 "Jakarta, Indonesia"),
    ("row",   ". IDE:",                   "Antigravity IDE, Vim, Nvim, Lazygit"),
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
]

# ─────────────────── ASCII art ─────────────────────────────────────────────
ascii_lines = []
try:
    art = ascii_magic.AsciiArt.from_image("profile.png")
    raw = art.to_ascii(columns=ASCII_COLS, width_ratio=2.2, monochrome=True)
    ascii_lines = raw.splitlines()[:ASCII_ROWS]
    while len(ascii_lines) < ASCII_ROWS:
        ascii_lines.append("")
    print(f"ASCII art generated: {len(ascii_lines)} lines")
except Exception as e:
    print(f"ASCII error: {e}")
    ascii_lines = ["" for _ in range(ASCII_ROWS)]

# ─────────────────── SVG BUILD ─────────────────────────────────────────────
def esc(s): return html.escape(str(s))

CHAR_W     = 9.62   # Consolas 16px char width
RIGHT_EDGE = SVG_W - 15

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

# ASCII left panel
out.append(f'<text x="15" y="{TEXT_Y}" fill="{C_TITLE}">')
for i, line in enumerate(ascii_lines):
    y = TEXT_Y + i * LINE_H
    out.append(f'  <tspan x="15" y="{y}">{esc(line)}</tspan>')
out.append('</text>')

# Right panel
y = TEXT_Y
for kind, key, val in stats:
    if kind == "sep":
        y += LINE_H
        continue

    if kind == "title":
        key_px   = TEXT_X + len(key) * CHAR_W
        dashes_n = max(1, int((RIGHT_EDGE - key_px - CHAR_W) / CHAR_W))
        out.append(
            f'<text x="{TEXT_X}" y="{y}">'
            f'<tspan class="title">{esc(key)}</tspan>'
            f'<tspan class="dots"> {"─" * dashes_n}</tspan>'
            f'</text>')
        y += LINE_H
        continue

    if kind == "sect":
        key_px   = TEXT_X + len(key) * CHAR_W
        dashes_n = max(1, int((RIGHT_EDGE - key_px - CHAR_W) / CHAR_W))
        out.append(
            f'<text x="{TEXT_X}" y="{y}">'
            f'<tspan class="title">{esc(key)} </tspan>'
            f'<tspan class="dots">{"─" * dashes_n}</tspan>'
            f'</text>')
        y += LINE_H
        continue

    # normal row — value right-aligned
    val_x    = RIGHT_EDGE - len(val) * CHAR_W
    key_end  = TEXT_X + (len(key) + 1) * CHAR_W
    gap      = val_x - key_end - CHAR_W
    dots_n   = max(1, int(gap / CHAR_W))
    out.append(
        f'<text x="{TEXT_X}" y="{y}">'
        f'<tspan class="key">{esc(key)}</tspan>'
        f'<tspan class="dots"> {"." * dots_n} </tspan>'
        f'<tspan class="val">{esc(val)}</tspan>'
        f'</text>')
    y += LINE_H

out.append('</svg>')

with open("dark_mode.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

with open("README.md", "w") as f:
    f.write(
        '<a href="https://github.com/SakamotoMrX/SakamotoMrX">\n'
        '  <picture>\n'
        '    <source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg">\n'
        '    <img src="dark_mode.svg" alt="andrahijati terminal profile">\n'
        '  </picture>\n'
        '</a>\n'
    )
print("Done — dark_mode.svg written!")
