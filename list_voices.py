import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": "sk_59af4dee42cc0b1473cd1f1ea639b2aea631bc200e22e4a4"})
with urllib.request.urlopen(req, context=ctx) as r:
    data = json.loads(r.read())
    for v in data.get("voices", []):
        print(f"{v['voice_id']} - {v['name']}")
