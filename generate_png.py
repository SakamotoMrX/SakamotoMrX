from PIL import Image, ImageDraw, ImageFont
import os

stats = [
    ("andrahijati@JuniorDevops", "------------------------------"),
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
    (". Skills.System:", "LinuxSysAdmin, VM, Containerization"),
    (". Skills.WebDev:", "Basic Website, Git & GitHub, Deploying"),
    (". Skills.Process:", "SDLC & Agile"),
    (".", ""),
    (". Hobbies.Software:", "Larping Linux"),
    (". Hobbies.Hardware:", "Arduino"),
    (".", ""),
    ("- Contact", "----------------------------------------------"),
    (". Email.Personal:", "andrahijati@gmail.com"),
    (". Discord:", "legacyy5030")
]

scale = 2
W, H = 1000 * scale, 480 * scale
bg_color = (13, 17, 23)
border_color = (48, 54, 61)

im = Image.new('RGB', (W, H), bg_color)
draw = ImageDraw.Draw(im)
draw.rounded_rectangle([2, 2, W-4, H-4], radius=10*scale, outline=border_color, width=2)

FONT_SIZE = 13 * scale
try:
    font_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", FONT_SIZE, index=1)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", FONT_SIZE)
except:
    font_bold = ImageFont.load_default()
    font = ImageFont.load_default()

IMG_W = 380 * scale
IMG_H = 450 * scale
try:
    prof = Image.open("profile.png")
    prof.thumbnail((IMG_W, IMG_H), Image.Resampling.LANCZOS)
    prof = prof.convert("RGBA")
    x_off = 15 * scale + (IMG_W - prof.width) // 2
    y_off = 15 * scale + (IMG_H - prof.height) // 2
    im.paste(prof, (x_off, y_off), prof)
except Exception as e:
    print(f"Image error: {e}")

x_start = 400 * scale
y = 40 * scale
line_height = 19 * scale

# Fixed value column: 570px from left edge (170px from text start)
val_col = 570 * scale

for key, val in stats:
    if key == "andrahijati@JuniorDevops":
        draw.text((x_start, y), key, font=font_bold, fill=(201, 209, 217))
        offset = draw.textlength(key + " ", font=font_bold)
        draw.text((x_start + offset, y), val, font=font, fill=(139, 148, 158))
    elif key.startswith("- "):
        draw.text((x_start, y), key, font=font_bold, fill=(201, 209, 217))
        offset = draw.textlength(key + " ", font=font_bold)
        draw.text((x_start + offset, y), val, font=font, fill=(139, 148, 158))
    elif key == ".":
        pass
    else:
        draw.text((x_start, y), key, font=font, fill=(227, 179, 65))
        key_end = x_start + draw.textlength(key + " ", font=font)
        dot_width = draw.textlength(".", font=font)
        dots_count = max(1, int((val_col - key_end - 8 * scale) / dot_width))
        dots = "." * dots_count
        draw.text((key_end, y), dots, font=font, fill=(139, 148, 158))
        draw.text((val_col, y), val, font=font, fill=(121, 192, 255))
    y += line_height

im.save("readme-banner-v4.png")

with open("README.md", "w") as f:
    f.write('<div align="center">\n  <img src="readme-banner-v4.png" width="1000" alt="Portfolio Terminal">\n</div>\n')

