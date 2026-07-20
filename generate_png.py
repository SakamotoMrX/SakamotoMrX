from PIL import Image, ImageDraw, ImageFont
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
    (". Skills.System:", "LinuxSysAdmin, VM, Containerization"),
    (". Skills.WebDev:", "Basic Website, Git & GitHub, Deploying"),
    (". Skills.Process:", "SDLC & Agile"),
    (".", ""),
    (". Hobbies.Software:", "Larping Linux"),
    (". Hobbies.Hardware:", "Arduino"),
    (".", ""),
    ("- Contact", "-----------------------------------------------"),
    (". Email.Personal:", "andrahijati@gmail.com"),
    (". Discord:", "legacyy5030")
]

scale = 2
W, H = 900 * scale, 480 * scale
bg_color = (13, 17, 23)
border_color = (48, 54, 61)

im = Image.new('RGB', (W, H), bg_color)
draw = ImageDraw.Draw(im)
draw.rounded_rectangle([2, 2, W-4, H-4], radius=10*scale, outline=border_color, width=2)

try:
    font_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14 * scale, index=1)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14 * scale)
except:
    font_bold = ImageFont.load_default()
    font = ImageFont.load_default()

try:
    prof = Image.open("profile.png")
    prof.thumbnail((300 * scale, 420 * scale), Image.Resampling.LANCZOS)
    prof = prof.convert("RGBA")
    
    x_off = 30 * scale + (300 * scale - prof.width) // 2
    y_off = 30 * scale + (420 * scale - prof.height) // 2
    im.paste(prof, (x_off, y_off), prof)
except Exception as e:
    print(f"Image error: {e}")

x_start = 360 * scale
y = 45 * scale

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
        
        val_x = x_start + (240 * scale)
        key_width = draw.textlength(key + " ", font=font)
        dot_width = draw.textlength(".", font=font)
        
        dots_space = val_x - (x_start + key_width) - (10 * scale)
        dots_count = int(dots_space / dot_width)
        if dots_count < 1: dots_count = 1
        dots = "." * dots_count
        
        draw.text((x_start + key_width, y), dots, font=font, fill=(139, 148, 158))
        draw.text((val_x, y), val, font=font, fill=(121, 192, 255))
        
    y += 20 * scale

im.save("readme-banner-v2.png")

with open("README.md", "w") as f:
    f.write('<div align="center">\n  <img src="readme-banner-v2.png" width="900" alt="Portfolio Terminal">\n</div>\n')

