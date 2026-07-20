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

W, H = 900, 480
bg_color = (13, 17, 23)
border_color = (48, 54, 61)

im = Image.new('RGB', (W, H), bg_color)
draw = ImageDraw.Draw(im)
draw.rounded_rectangle([1, 1, W-2, H-2], radius=10, outline=border_color, width=1)

try:
    font_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14, index=1)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
except:
    font_bold = ImageFont.load_default()
    font = ImageFont.load_default()

try:
    prof = Image.open("profile.png")
    prof.thumbnail((300, 420), Image.Resampling.LANCZOS)
    prof = prof.convert("RGBA")
    
    # create a transparent bg image for paste mask if needed
    tmp = Image.new("RGBA", (300, 420), (255,255,255,0))
    # calculate offset to center
    x_off = 30 + (300 - prof.width) // 2
    y_off = 30 + (420 - prof.height) // 2
    im.paste(prof, (x_off, y_off), prof)
except Exception as e:
    print(f"Image error: {e}")

x_start = 360
y = 45

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
        # key
        draw.text((x_start, y), key, font=font, fill=(227, 179, 65))
        
        # calculate dots
        total_len = 50
        dots_count = max(1, total_len - len(key) - len(val))
        dots = "." * dots_count
        
        # draw dots
        offset1 = draw.textlength(key + " ", font=font)
        draw.text((x_start + offset1, y), dots, font=font, fill=(139, 148, 158))
        
        # val
        offset2 = draw.textlength(key + " " + dots + " ", font=font)
        draw.text((x_start + offset2, y), val, font=font, fill=(121, 192, 255))
        
    y += 20

im.save("readme-banner.png")

with open("README.md", "w") as f:
    f.write('<div align="center">\n  <img src="readme-banner.png" alt="Portfolio Terminal">\n</div>\n')

