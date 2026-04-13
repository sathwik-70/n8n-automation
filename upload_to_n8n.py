import urllib.request
import urllib.error
import json
import ssl
import sys
import base64

# Configuration
BASE_URL = "https://n8n-youtube-ai-factory.onrender.com"
N8N_EMAIL = "botmale01o@gmail.com"
N8N_PASSWORD = "7fbeSXca5Cs4CL4"

# If your Render service has N8N_BASIC_AUTH_ACTIVE=true, enter credentials below
# These are usually 'admin' and the auto-generated password from Render dashboard
BASIC_AUTH_USER = "admin"
BASIC_AUTH_PASS = "" # ENTER RENDER BASIC AUTH PASSWORD HERE

def make_request(method, endpoint, data=None, headers=None):
    if headers is None:
        headers = {}
    
    # Add Basic Auth if provided
    if BASIC_AUTH_USER and BASIC_AUTH_PASS:
        auth_str = f"{BASIC_AUTH_USER}:{BASIC_AUTH_PASS}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers['Authorization'] = f"Basic {encoded_auth}"

    url = f"{BASE_URL}{endpoint}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
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

if not BASIC_AUTH_PASS:
    print("Warning: Basic Auth password is empty. If Render Basic Auth is active, this will fail.")

# 1. Login to n8n
login_data = {
    "email": N8N_EMAIL,
    "password": N8N_PASSWORD
}
# n8n /rest/login expects emailOrLdapLoginId in some versions, email in others
# Let's try to be robust
login_data_alt = {
    "emailOrLdapLoginId": N8N_EMAIL,
    "password": N8N_PASSWORD
}

status, headers, body = make_request("POST", "/rest/login", data=login_data_alt)

if status != 200:
    print(f"Failed to login. HTTP {status}")
    print(f"Response: {body}")
    if status == 401:
        print("\n[HINT] This is likely because Render Basic Auth is enabled.")
        print("Please check your Render dashboard for the generated N8N_BASIC_AUTH_PASSWORD")
        print("and update BASIC_AUTH_PASS in this script.")
    sys.exit(1)

print("Login successful!")
cookie = headers.get('set-cookie', '')
# n8n often needs X-Requested-With for REST API
auth_headers = {
    'Cookie': cookie, 
    'X-Requested-With': 'XMLHttpRequest'
}

# 2. Upload Workflows
workflows_to_upload = [
    "youtube-ai-factory-workflow.json",
    "youtube-ai-factory-analytics-loop.json"
]

for wf_file in workflows_to_upload:
    print(f"\nProcessing {wf_file}...")
    try:
        with open(wf_file, 'r', encoding='utf-8') as f:
            wf_data = json.load(f)
            
        wf_id = wf_data.get('id')
        # Clean up session-specific fields
        if 'id' in wf_data: del wf_data['id']
        wf_data.pop('createdAt', None)
        wf_data.pop('updatedAt', None)
        
        status, _, resp_body = make_request("POST", "/rest/workflows", data=wf_data, headers=auth_headers)
        
        if status in [200, 201]:
            print(f"  [SUCCESS] Created '{wf_file}'")
        elif status == 409 and wf_id:
            print(f"  [INFO] Conflict detected, updating existing workflow '{wf_id}'...")
            status, _, resp_body = make_request("PUT", f"/rest/workflows/{wf_id}", data=wf_data, headers=auth_headers)
            if status == 200:
                print(f"  [SUCCESS] Updated '{wf_file}'")
            else:
                print(f"  [ERROR] Failed to update. Status {status}: {resp_body}")
        else:
            print(f"  [ERROR] Failed to upload. Status {status}: {resp_body}")
            
    except Exception as e:
        print(f"  Error processing {wf_file}: {e}")

print("\nDone!")
