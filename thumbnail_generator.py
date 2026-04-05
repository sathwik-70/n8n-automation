import os
import sys
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_pexels_image(query="technology abstract"):
    """Fetch a high-quality relevant background image from Pexels."""
    if not PEXELS_API_KEY:
        print("⚠️ PEXELS_API_KEY not found. Falling back to local/dark background.")
        return None
        
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&size=large&per_page=1"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("photos") and len(data["photos"]) > 0:
            image_url = data["photos"][0]["src"]["original"]
            
            # Download the actual image bytes
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            return Image.open(BytesIO(img_response.content))
        else:
            print("No photos found on Pexels for query:", query)
            return None
    except Exception as e:
        print(f"Error fetching from Pexels API: {e}")
        return None

def generate_thumbnail(query, text, output_path):
    try:
        # Attempt to get a dynamic background from Pexels
        img = fetch_pexels_image(query)
        
        # Fallback if Pexels fails
        if img is None:
            base_image_path = "base.jpg"
            if os.path.exists(base_image_path):
                img = Image.open(base_image_path)
            else:
                img = Image.new('RGB', (1280, 720), color=(20, 20, 20))
                
        # Resize/Crop to 1280x720 (standard YouTube size)
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        
        # Darken the image slightly so text pops
        darker_layer = Image.new('RGBA', img.size, (0, 0, 0, 100))
        img.paste(darker_layer, (0, 0), darker_layer)

        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 150)
        except IOError:
            font = ImageFont.load_default()
            
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        x = (1280 - text_w) / 2
        y = (720 - text_h) / 2
        
        # Shadow / Highlight for pop
        draw.text((x + 6, y + 6), text, font=font, fill=(0, 0, 0)) # Drop shadow
        draw.text((x, y), text, font=font, fill=(255, 30, 30)) # Vibrant Red Text
        
        img.save(output_path)
        print(f"✅ Generated dynamic high-CTR thumbnail: {output_path}")

    except Exception as e:
        print(f"Error generating thumbnail: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate high CTR Thumbnails via Pexels")
    parser.add_argument("--query", default="technology abstract", help="Pexels search query (e.g. 'artificial intelligence')")
    parser.add_argument("--text", required=True, help="Text to overlay")
    parser.add_argument("--out", default="thumbnail.jpg", help="Output filename")
    
    args = parser.parse_args()
    generate_thumbnail(args.query, args.text, args.out)
