import os
import json
import gspread
import datetime
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- यहाँ पेस्ट करें ---
def get_gspread_client():
    creds_json = os.environ.get('GOOGLE_CREDS')
    
    if not creds_json:
        return "Error: No Credentials Found in Environment"
    
    try:
        # JSON डेटा को साफ़ करके लोड करना
        creds_dict = json.loads(creds_json.strip())
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Auth Error: {e}")
        raise e
# --- पेस्ट खत्म ---

# इसके नीचे आपके बाकी Routes (@app.route('/')) होने चाहिए...
