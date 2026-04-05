import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def generate_content(topic):
    # 1. OpenAI Call for Output JSON
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are a viral YouTube scriptwriter optimizing for CTR and 50%+ Retention.
Output ONLY strict JSON with the following keys:
- 'titles': array of 3 viral titles using format [SHOCK] + [SPECIFIC] + [TIME FRAME]
- 'script': The actual 60-second video script using short sentences. Start with a 'Shock -> Question -> Promise' hook. Include curiosity loops.
- 'texts': array of 3 short texts (max 3 words) indicating threat/shock for the thumbnail (e.g. 'JOB LOSS').
"""
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}"}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        content = json.loads(data["choices"][0]["message"]["content"])
    except Exception as e:
        print(json.dumps({"error": f"OpenAI Error: {str(e)}"}))
        sys.exit(1)
        
    script_text = content.get("script", "Error generating script")
    
    # 2. ElevenLabs Call for Audio
    # Using a default premium voice (e.g., Rachel, Adam, or Antony)
    voice_id = "pNInz6obpgDQGcFmaJcg" # Default Adam voice
    el_headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    el_payload = {
        "text": script_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        audio_res = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", 
            headers=el_headers, 
            json=el_payload
        )
        audio_res.raise_for_status()
        
        # Save Audio to disk
        with open("audio.mp3", "wb") as f:
            f.write(audio_res.content)
            
    except Exception as e:
        print(json.dumps({"error": f"ElevenLabs Error: {str(e)}"}))
        sys.exit(1)

    # Print pure JSON to stdout so n8n can parse it
    print(json.dumps({
        "topic": topic,
        "titles": content.get("titles", []),
        "texts": content.get("texts", []),
        "script": script_text,
        "audio_path": "audio.mp3"
    }))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing topic argument"}))
        sys.exit(1)
    
    # join topic string if unquoted args were passed
    input_topic = " ".join(sys.argv[1:])
    generate_content(input_topic)
