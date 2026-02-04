from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import uvicorn
import urllib.parse
import json

app = FastAPI()

CLIENT_ID = "demo_client"
CLIENT_SECRET = "demo_secret"
PROVIDER_URL = "http://localhost:8000"
REDIRECT_URI = "http://localhost:3000/callback"

CSS = """
<style>
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background: #f3f4f6; color: #1f2937; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    .card { background: white; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); max-width: 480px; width: 100%; box-sizing: border-box; }
    h1 { margin-top: 0; font-size: 1.5rem; font-weight: 700; color: #111827; }
    p { color: #6b7280; line-height: 1.5; }
    .btn { display: inline-block; background-color: #2563eb; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; text-align: center; transition: background-color 0.2s; width: 100%; box-sizing: border-box; margin-top: 1rem; }
    .btn:hover { background-color: #1d4ed8; }
    .btn-secondary { background-color: #e5e7eb; color: #374151; }
    .btn-secondary:hover { background-color: #d1d5db; }
    .box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; overflow-x: auto; font-family: 'Menlo', 'Monaco', monospace; font-size: 0.875rem; color: #374151; margin-bottom: 1.5rem; }
    .label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.05em; margin-bottom: 0.5rem; display: block; }
</style>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read",
        "state": "xyz", 
    }
    auth_url = f"{PROVIDER_URL}/authorize?{urllib.parse.urlencode(params)}"
    
    return f"""
    <html>
        <head><title>Demo Client</title>{CSS}</head>
        <body>
            <div class="card" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
                <h1>Demo Client App</h1>
                <p>This application mimics a 3rd party service using OAuth2 to connect to your account.</p>
                <a href="{auth_url}" class="btn">Connect with OAuth2 Provider</a>
            </div>
        </body>
    </html>
    """

@app.get("/callback", response_class=HTMLResponse)
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return "Error: No code returned"
        
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI
        }
        token_res = await client.post(f"{PROVIDER_URL}/token", data=data)
        token_data = token_res.json()
        
        access_token = token_data.get("access_token")
        
        protected_data = None
        if access_token:
            # Access protected resource
            protected_res = await client.get(f"{PROVIDER_URL}/protected", headers={"Authorization": f"Bearer {access_token}"})
            if protected_res.status_code == 200:
                protected_data = protected_res.json()
            else:
                protected_data = {"error": f"Failed to fetch: {protected_res.status_code}"}
                
    return f"""
    <html>
        <head><title>Success</title>{CSS}</head>
        <body>
            <div class="card">
                <div style="text-align: center; margin-bottom: 2rem;">
                     <div style="background: #d1fae5; color: #065f46; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">✓</div>
                     <h1>Authorization Complete</h1>
                     <p>Successfully exchanged code for token and accessed resource.</p>
                </div>

                <span class="label">Access Token Response</span>
                <div class="box">{json.dumps(token_data, indent=2)}</div>
                
                <span class="label">Protected Resource Data</span>
                <div class="box" style="background: #eff6ff; border-color: #bfdbfe; color: #1e3a8a;">{json.dumps(protected_data, indent=2)}</div>
                
                <a href="/" class="btn btn-secondary">Back to Home</a>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
