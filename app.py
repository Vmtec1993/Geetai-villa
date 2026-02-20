import os
import json
import gspread
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials
import requests

app = Flask(__name__)

# --- Google Sheets Setup ---
creds_json = os.environ.get('GOOGLE_CREDS')
sheet = None

if creds_json:
    try:
        info = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        
        # आपकी शीट ID
        SHEET_ID = "1wXlMNAUuW2Fr4L05ahxvUNn0yvMedcVosTRJzZf_1ao"
        main_spreadsheet = client.open_by_key(SHEET_ID)
        sheet = main_spreadsheet.sheet1
    except Exception as e:
        print(f"Sheet Error: {e}")

# --- Routes ---

@app.route('/')
def index():
    if sheet:
        villas = sheet.get_all_records()
        return render_template('index.html', villas=villas)
    return "Database Error", 500

# 1. मुख्य गैलरी पेज (यहाँ हर विला का सिर्फ एक कार्ड दिखेगा)
@app.route('/gallery')
def gallery_main():
    if sheet:
        all_villas = sheet.get_all_records()
        return render_template('gallery.html', villas=all_villas)
    return "Database Error", 500

# 2. किसी एक विला की गैलरी (यहाँ उस विला के सभी फोटो दिखेंगे)
@app.route('/gallery/<villa_slug>')
def villa_gallery(villa_slug):
    if sheet:
        all_data = sheet.get_all_records()
        # विला के नाम से फोटो फिल्टर करना (बिना स्पेस के मैच करना)
        villa_photos = [v for v in all_data if v.get('Name', '').lower().replace(' ', '') == villa_slug.lower()]
        
        if villa_photos:
            v_name = villa_photos[0].get('Name', 'Our Villa')
            return render_template('villa_gallery.html', photos=villa_photos, villa_name=v_name)
    return "Gallery Not Found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
