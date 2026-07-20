import base64
import os

stats = [
    ("andrahijati@JuniorDevops", "--------------------------------"),
    (". OS:", "Macos, Linux, Windows"),
    (". Uptime:", "15 years, 5 months"),
    (". Host:", "Junior Devops"),
    (". Shell:", "Jakarta, Indonesia"),
    (". IDE:", "Antigravity IDE, Vim, Nvim, Lazygit"),
    (".", ""),
    (". Languages.Programming:", "Bash"),
    (". Languages.Computer:", "YAML"),
    (". Languages.Real:", "Indonesia, English"),
    (".", ""),
    (". Skills.System:", "LinuxSysAdmin, Network, Deploying"),
    (". Skills.WebDev:", "Basic Website, Git & GitHub"),
    (". Skills.Process:", "SDLC & Agile"),
    (".", ""),
    (". Hobbies.Software:", "Larping Linux"),
    (". Hobbies.Hardware:", "Arduino"),
    (".", ""),
    ("- Contact", "-----------------------------------------------"),
    (". Email.Personal:", "andrahijati@gmail.com"),
    (". Discord:", "legacyy5030")
]

# Read profile.png and encode to base64
try:
    with open("profile.png", "rb") as f:
        img_data = f.read()
        b64_img = base64.b64encode(img_data).decode('utf-8')
        img_href = f"data:image/png;base64,{b64_img}"
except Exception:
    # Fallback if profile.png is missing or unreadable
    img_href = ""

svg_lines = []
svg_lines.append('<svg width="900" height="480" viewBox="0 0 900 480" xmlns="http://www.w3.org/2000/svg">')
svg_lines.append('  <style>')
svg_lines.append('    .bg { fill: #0d1117; }')
svg_lines.append('    .text { font-family: "Menlo", "Monaco", "Consolas", monospace; font-size: 14px; fill: #c9d1d9; }')
svg_lines.append('    .key { fill: #e3b341; }')
svg_lines.append('    .dots { fill: #8b949e; }')
svg_lines.append('    .val { fill: #79c0ff; }')
svg_lines.append('    .title { fill: #c9d1d9; font-weight: bold; }')
svg_lines.append('  </style>')
svg_lines.append('  <rect width="900" height="480" rx="10" ry="10" class="bg" stroke="#30363d" stroke-width="1"/>')

if img_href:
    svg_lines.append(f'  <image href="{img_href}" x="30" y="30" width="300" height="420" preserveAspectRatio="xMidYMid meet" />')

y = 45
x_start = 360

for key, val in stats:
    if key == "andrahijati@JuniorDevops":
        svg_lines.append(f'  <text x="{x_start}" y="{y}" class="text"><tspan class="title">{key}</tspan> <tspan class="dots">{val}</tspan></text>')
    elif key.startswith("- "):
        svg_lines.append(f'  <text x="{x_start}" y="{y}" class="text"><tspan class="title">{key}</tspan> <tspan class="dots">{val}</tspan></text>')
    elif key == ".":
        pass # empty line, just increase y
    else:
        # Calculate dots based on length
        # Target length for key + dots is around 35 chars
        # wait, let's just use a fixed x for values to align perfectly!
        # key is at x_start, value is at x_start + 220
        # draw dots in between
        
        # let's format it as one string with dots
        total_len = 50
        dots_count = total_len - len(key) - len(val)
        if dots_count < 1: dots_count = 1
        dots = "." * dots_count
        
        svg_lines.append(f'  <text x="{x_start}" y="{y}" class="text"><tspan class="key">{key}</tspan> <tspan class="dots">{dots}</tspan> <tspan class="val">{val}</tspan></text>')
    
    y += 20

svg_lines.append('</svg>')

with open("readme.svg", "w") as f:
    f.write("\n".join(svg_lines))

# Update README to use the SVG
readme = """<div align="center">
  <img src="readme.svg" alt="Portfolio Terminal">
</div>
"""
with open("README.md", "w") as f:
    f.write(readme)
