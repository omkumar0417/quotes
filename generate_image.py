import os
import requests
import json
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Constants
QUOTES_FILE = "quotes.txt"
USED_QUOTES_FILE = "used_quotes.json"
BACKGROUND_IMAGE = "background.jpg"
OUTPUT_IMAGE = "background.png"
MAX_MEMORY_HOURS = 24

# Telegram secrets
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

# Load all quotes
with open(QUOTES_FILE, "r", encoding="utf-8") as f:
    quotes = [line.strip() for line in f if line.strip()]

# Load used memory
if os.path.exists(USED_QUOTES_FILE):
    with open(USED_QUOTES_FILE, "r") as f:
        content = f.read().strip()
        used_data = json.loads(content) if content else {}
else:
    used_data = {}

now = datetime.utcnow()
cutoff = now - timedelta(hours=MAX_MEMORY_HOURS)
used_data = {k: v for k, v in used_data.items() if datetime.fromisoformat(v) > cutoff}

# Pick a quote
used_indices = set(map(int, used_data.keys()))
available_indices = list(set(range(len(quotes))) - used_indices)
if not available_indices:
    available_indices = list(range(len(quotes)))
    used_data = {}

index = random.choice(available_indices)
quote_text = quotes[index]

# Format final message
formatted_text = f"“{quote_text}”\n\nFollow 👉 @unfilteredquotes"

# Load image and draw object
image = Image.open(BACKGROUND_IMAGE).convert("RGB")
draw = ImageDraw.Draw(image)

# Load font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
except:
    font = ImageFont.load_default()

# Word-wrap the quote
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines

# Split and wrap
max_width = image.width - 100
wrapped_lines = []
for part in formatted_text.split('\n'):
    wrapped_lines.extend(wrap_text(part, font, max_width))

# Center vertically
line_height = font.getsize("A")[1] + 10
total_text_height = line_height * len(wrapped_lines)
y_start = (image.height - total_text_height) // 2

# Draw lines
for line in wrapped_lines:
    w = draw.textlength(line, font=font)
    x = (image.width - w) // 2
    # Optional: glow/shadow
    draw.text((x + 2, y_start + 2), line, font=font, fill="gray")
    draw.text((x, y_start), line, font=font, fill="white")
    y_start += line_height

# Save image
image.save(OUTPUT_IMAGE)

# Send to Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
files = {"photo": open(OUTPUT_IMAGE, "rb")}
data = {"chat_id": CHANNEL, "caption": "#Motivation #Quotes #StayInspired"}
res = requests.post(url, data=data, files=files)
print(f"✅ Sent Quote #{index + 1}")
print("Telegram Response:", res.status_code, res.text)

# Save memory
used_data[str(index)] = now.isoformat()
with open(USED_QUOTES_FILE, "w") as f:
    json.dump(used_data, f)
