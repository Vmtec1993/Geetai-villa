import os
import json
from flask import Flask, render_template
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

def get_sheets_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_raw = os.environ.get("GOOGLE_CREDS")
        
        if not creds_raw: return []

        # सफाई: फालतू कोट्स हटाना
        creds_raw = creds_raw.strip().strip("'").strip('"')
        info = json.loads(creds_raw)
        
        # Private Key की लाइनों को ठीक करना
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # सुनिश्चित करें कि शीट का नाम सही है
        spreadsheet = client.open("Geetai_Villa_Data")
        sheet = spreadsheet.get_worksheet(0)
        return sheet.get_all_records()
    except Exception as e:
        return [{"Name": f"Key Error: {str(e)}", "Price": "Fix JSON in Render"}]

@app.route('/')
def index():
    villas = get_sheets_data()
    return render_template('index.html', villas=villas)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
