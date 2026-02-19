import os
import json
from flask import Flask, render_template
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

def get_sheets_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_json = os.environ.get("GOOGLE_CREDS")
        
        if not creds_json:
            return [{"Name": "ERROR: GOOGLE_CREDS variable missing in Render", "Price": "0"}]

        info = json.loads(creds_json)
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # यहाँ ध्यान दें: क्या शीट का नाम सही है?
        spreadsheet = client.open("Geetai_Villa_Data")
        sheet = spreadsheet.get_worksheet(0)
        data = sheet.get_all_records()
        return data

    except Exception as e:
        # यह एरर अब सीधा आपकी वेबसाइट पर दिखेगा
        return [{"Name": f"CONNECTION ERROR: {str(e)}", "Price": "Check Sheet Name or Access"}]

@app.route('/')
def index():
    villas = get_sheets_data()
    return render_template('index.html', villas=villas)

@app.route('/villa/<int:villa_id>')
def villa_details(villa_id):
    villas = get_sheets_data()
    villa = next((v for v in villas if v.get('Villa_ID') == villa_id), None)
    if not villa: return "Villa not found", 404
    return render_template('villa_details.html', villa=villa)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    
