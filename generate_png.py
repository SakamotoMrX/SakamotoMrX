from PIL import Image, ImageDraw, ImageFont
import os

# Stats: (key, value) - values will be right-aligned
stats = [
    ("andrahijati@JuniorDevops", ""),       # title row, special
    (". OS:", "Macos, Linux, Windows"),
    (". Uptime:", "15 years, 5 months"),
    (". Host:", "Junior Devops"),
    (". Shell:", "Jakarta, Indonesia"),
    (". IDE:", "Antigravity IDE, Vim, Nvim, Lazygit"),
    ("", ""),
    (". Languages.Programming:", "Bash"),
    (". Languages.Computer:", "YAML"),
    (". Languages.Real:", "Indonesia, English"),
    ("", ""),
    (". Skills.System:", "LinuxSysAdmin, VM, Containerization"),
    (". Skills.WebDev:", "Basic Website, Git & GitHub, Deploying"),
    (". Skills.Process:", "SDLC & Agile"),
    ("", ""),
    (". Hobbies.Software:", "Larping Linux"),
    (". Hobbies.Hardware:", "Arduino"),
    ("", ""),
    ("- Contact", ""),                      # section header, special
    (". Email.Personal:", "andrahijati@gmail.com"),
    (". Discord:", "legacyy5030"),
]

SCALE = 2
# Canvas dimensions (will be displayed at 1x in README)
W  = 960  * SCALE
H  = 500  * SCALE
PAD_TOP   = 28 * SCALE
PAD_BOT   = 28 * SCALE
IMG_AREA_W = 360 * SCALE   # left section for image
TEXT_PAD_L = 20 * SCALE    # gap between image and text
TEXT_START = IMG_AREA_W + TEXT_PAD_L
TEXT_RIGHT = W - 28 * SCALE  # right edge of text

BG     = (13,  17,  23)
BORDER = (48,  54,  61)
C_TITLE = (201, 209, 217)   # white-ish
C_KEY   = (227, 179,  65)   # orange/yellow
C_DOTS  = (100, 110, 120)   # dark gray
C_VAL   = (201, 209, 217)   # white (like the reference)
C_DASH  = (100, 110, 120)   # section separator dashes

im   = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(im)
draw.rounded_rectangle([1, 1, W-2, H-2], radius=10*SCALE, outline=BORDER, width=2)

# Use Menlo bold for everything (terminal feel, bigger = 17px)
FSIZE = 17 * SCALE
try:
    font      = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", FSIZE, index=0)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", FSIZE, index=1)
except:
    font = font_bold = ImageFont.load_default()

# Paste profile image — fill the left area
try:
    prof = Image.open("profile.png").convert("RGBA")
    prof.thumbnail((IMG_AREA_W, H - PAD_TOP - PAD_BOT), Image.Resampling.LANCZOS)
    x_img = (IMG_AREA_W - prof.width) // 2
    y_img = PAD_TOP + (H - PAD_TOP - PAD_BOT - prof.height) // 2
    im.paste(prof, (x_img, y_img), prof)
except Exception as e:
    print(f"Image error: {e}")

# ---- measure dot width once ----
dot_w = draw.textlength(".", font=font)
sp_w  = draw.textlength(" ", font=font)

LINE_H = 21 * SCALE
y = PAD_TOP

for key, val in stats:
    # Empty separator line
    if key == "" and val == "":
        y += LINE_H
        continue

    # Title row: "andrahijati@JuniorDevops --------..."
    if key == "andrahijati@JuniorDevops":
        title_w = draw.textlength(key, font=font_bold)
        draw.text((TEXT_START, y), key, font=font_bold, fill=C_TITLE)
        # fill rest of line with dashes
        dash_start = TEXT_START + title_w + sp_w
        dash_count = max(1, int((TEXT_RIGHT - dash_start) / dot_w))
        draw.text((dash_start, y), "─" * dash_count, font=font, fill=C_DASH)
        y += LINE_H
        continue

    # Section header: "- Contact --------..."
    if key.startswith("- "):
        hdr_w = draw.textlength(key, font=font_bold)
        draw.text((TEXT_START, y), key, font=font_bold, fill=C_TITLE)
        dash_start = TEXT_START + hdr_w + sp_w
        dash_count = max(1, int((TEXT_RIGHT - dash_start) / dot_w))
        draw.text((dash_start, y), "─" * dash_count, font=font, fill=C_DASH)
        y += LINE_H
        continue

    # Normal row: key ... value (value right-aligned)
    key_w = draw.textlength(key + " ", font=font)
    val_w = draw.textlength(val,       font=font)

    # dots fill the middle
    dots_space = TEXT_RIGHT - (TEXT_START + key_w) - val_w - sp_w
    dots_count = max(1, int(dots_space / dot_w))
    dots = "." * dots_count

    draw.text((TEXT_START, y),                                   key,  font=font, fill=C_KEY)
    draw.text((TEXT_START + key_w, y),                           dots, font=font, fill=C_DOTS)
    draw.text((TEXT_RIGHT - val_w, y),                           val,  font=font, fill=C_VAL)

    y += LINE_H

im.save("readme-banner-v6.png")

with open("README.md", "w") as f:
    f.write('<div align="center">\n  <img src="readme-banner-v6.png" width="960" alt="Portfolio Terminal">\n</div>\n')

print("Done!")
