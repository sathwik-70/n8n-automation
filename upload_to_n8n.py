import urllib.request
import urllib.error
import json
import ssl
import sys

BASE_URL = "https://n8n-youtube-ai-factory.onrender.com"
EMAIL = "botmale01o@gmail.com"
PASSWORD = "7fbeSXca5Cs4CL4"

def make_request(method, endpoint, data=None, headers=None):
    if headers is None:
        headers = {}
    
    url = f"{BASE_URL}{endpoint}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    # Ignore SSL warnings for this script if any
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            resp_headers = dict(response.getheaders())
            try:
                resp_body = json.loads(response.read().decode())
            except:
                resp_body = response.read().decode()
            return response.status, resp_headers, resp_body
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode())
        except:
            err_body = e.read().decode()
        return e.code, dict(e.headers), err_body
    except Exception as e:
        print(f"Connection Error: {e}")
        return 0, {}, str(e)

print(f"Connecting to {BASE_URL}...")

# 1. Try to login
login_data = {
    "emailOrLdapLoginId": EMAIL,
    "password": PASSWORD
}
status, headers, body = make_request("POST", "/rest/login", data=login_data)

if status != 200:
    print(f"Failed to login. HTTP {status}")
    print(f"Response: {body}")
    
    if status == 401:
        print("This could be because Render Basic Auth is blocking the request.")
    sys.exit(1)

print("Login successful! Extracting authentication cookie...")
cookie = ""
auth_key = ""
for k, v in headers.items():
    if k.lower() == 'set-cookie':
        # n8n uses a cookie named n8n-auth
        cookie = v
        break

if 'data' in body and 'token' in body['data']:
    auth_key = body['data']['token']

auth_headers = {
    'Cookie': cookie,
    'browserId': 'automation-script'
}

# Load the workflows
workflows_to_upload = [
    "youtube-ai-factory-workflow.json",
    "youtube-ai-factory-analytics-loop.json"
]

for wf_file in workflows_to_upload:
    print(f"\nImporting {wf_file}...")
    try:
        with open(wf_file, 'r', encoding='utf-8') as f:
            wf_data = json.load(f)
            
        # Clean up IDs and timestamps to avoid conflicts
        if 'id' in wf_data:
            del wf_data['id']
        wf_data['createdAt'] = None
        wf_data['updatedAt'] = None
        
        status, resp_headers, resp_body = make_request("POST", "/rest/workflows", data=wf_data, headers=auth_headers)
        if status == 200:
            print(f"✅ Successfully uploaded '{wf_file}'")
        else:
            print(f"❌ Failed to upload '{wf_file}'. Status {status}")
            print(f"Response: {resp_body}")
    except Exception as e:
        print(f"Error reading or uploading {wf_file}: {e}")

print("\nDone!")
