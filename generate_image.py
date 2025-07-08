import os
import requests
import json
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Constants
QUOTES_FILE = "quotes.txt"
USED_QUOTES_FILE = "used_quotes.json"
BACKGROUND_IMAGE = "background.png"
OUTPUT_IMAGE = "quote_output.png"
MAX_MEMORY_HOURS = 24

# Telegram secrets
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]

# Load all quotes
with open(QUOTES_FILE, "r", encoding="utf-8") as f:
    quotes = [line.strip() for line in f if line.strip()]

# Load used quote memory
if os.path.exists(USED_QUOTES_FILE):
    with open(USED_QUOTES_FILE, "r") as f:
        used_data = json.load(f)
else:
    used_data = {}

now = datetime.utcnow()
cutoff = now - timedelta(hours=MAX_MEMORY_HOURS)
used_data = {k: v for k, v in used_data.items() if datetime.fromisoformat(v) > cutoff}

# Get available quotes
used_indices = set(map(int, used_data.keys()))
available_indices = list(set(range(len(quotes))) - used_indices)
if not available_indices:
    available_indices = list(range(len(quotes)))
    used_data = {}

index = random.choice(available_indices)
quote = quotes[index]

# Generate image
image = Image.open(BACKGROUND_IMAGE).convert("RGB")
draw = ImageDraw.Draw(image)

# Use a default font if custom not found
try:
    font = ImageFont.truetype("arial.ttf", 42)
except:
    font = ImageFont.load_default()

# Word wrap
max_width = image.width - 80
lines = []
words = quote.split()
line = ""
for word in words:
    test_line = f"{line} {word}".strip()
    if draw.textlength(test_line, font=font) <= max_width:
        line = test_line
    else:
        lines.append(line)
        line = word
lines.append(line)

y = image.height // 2 - (len(lines) * 30)
for line in lines:
    w = draw.textlength(line, font=font)
    x = (image.width - w) // 2
    draw.text((x, y), line, font=font, fill="white")
    y += 55

image.save(OUTPUT_IMAGE)

# Send to Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
files = {"photo": open(OUTPUT_IMAGE, "rb")}
data = {"chat_id": CHANNEL, "caption": "#Motivation #Quotes #StayInspired"}
res = requests.post(url, data=data, files=files)
print(f"✅ Sent Quote #{index + 1}")

# Save updated memory
used_data[str(index)] = now.isoformat()
with open(USED_QUOTES_FILE, "w") as f:
    json.dump(used_data, f)
