import os
import json
import gspread
import datetime
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

def get_gspread_client():
    creds_json = os.environ.get('GOOGLE_CREDS')
    if not creds_json:
        return None
    try:
        creds_dict = json.loads(creds_json.strip())
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        return None

@app.route('/')
def index():
    try:
        client = get_gspread_client()
        if not client:
            return "Connection Error: Please check Render Environment Variables."
        
        # शीट को नाम से खोलना
        spreadsheet = client.open("Geetai_Villa_Admin")
        # पक्का करें कि डेटा पहले टैब में है
        sheet = spreadsheet.get_worksheet(0) 
        villas = sheet.get_all_records()
        
        if not villas:
            return "Error: No data found in the Google Sheet. Please add some villas."
            
        return render_template('index.html', villas=villas)
    except Exception as e:
        # अगर अभी भी दिक्कत आए, तो यह साफ़ बताएगा कि क्या कमी है
        return f"Database Error: {str(e)}. Make sure the sheet is shared with the service account email."

# यह हिस्सा पोर्ट की समस्या को ठीक करेगा
if __name__ == "__main__":
    # रेंडर को इस खास पोर्ट की ज़रूरत होती है
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 
