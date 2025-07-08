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
        try:
            used_data = json.load(f)
        except json.JSONDecodeError:
            used_data = {}
else:
    used_data = {}

# Remove entries older than cutoff
now = datetime.utcnow()
cutoff = now - timedelta(hours=MAX_MEMORY_HOURS)
used_data = {k: v for k, v in used_data.items() if datetime.fromisoformat(v) > cutoff}

# Get an unused quote
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

# Load font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
except:
    font = ImageFont.load_default()

# Wrap quote
max_width = image.width - 100
words = quote.split()
wrapped_lines = []
line = ""
for word in words:
    test_line = f"{line} {word}".strip()
    if draw.textlength(test_line, font=font) <= max_width:
        line = test_line
    else:
        wrapped_lines.append(line)
        line = word
wrapped_lines.append(line)

# Add handle line
wrapped_lines.append("")
wrapped_lines.append("Follow: @unfilteredquotes for more.")

# Center vertically
line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 10
total_text_height = line_height * len(wrapped_lines)
y_start = (image.height - total_text_height) // 2

# Draw text
for line in wrapped_lines:
    text_width = draw.textlength(line, font=font)
    x = (image.width - text_width) // 2
    draw.text((x, y_start), line, font=font, fill="white")
    y_start += line_height

# Save image
image.save(OUTPUT_IMAGE)

# Send to Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
files = {"photo": open(OUTPUT_IMAGE, "rb")}
data = {"chat_id": CHANNEL, "caption": "#Motivation #Quotes #StayInspired"}
res = requests.post(url, data=data, files=files)
print(f"✅ Sent Quote #{index + 1} at {now.isoformat()}")

# Save usage
used_data[str(index)] = now.isoformat()
with open(USED_QUOTES_FILE, "w") as f:
    json.dump(used_data, f)
