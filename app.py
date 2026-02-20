import os
import json
import gspread
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- Google Sheets Setup ---
def get_sheet():
    creds_json = os.environ.get('GOOGLE_CREDS')
    if not creds_json:
        return None
    try:
        info = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        # आपकी शीट ID
        return client.open_by_key("1wXlMNAUuW2Fr4L05ahxvUNn0yvMedcVosTRJzZf_1ao").sheet1
    except:
        return None

@app.route('/gallery')
def gallery_main():
    sheet = get_sheet()
    villas = sheet.get_all_records() if sheet else []
    return render_template('gallery.html', villas=villas)

@app.route('/gallery/<villa_slug>')
def villa_gallery(villa_slug):
    sheet = get_sheet()
    all_data = sheet.get_all_records() if sheet else []
    # विला के नाम से फोटो फिल्टर करना
    villa_photos = [v for v in all_data if v.get('Name', '').lower().replace(' ', '') == villa_slug.lower()]
    
    # यहाँ से नाम और डेटा पास हो रहा है
    v_name = villa_photos[0].get('Name', 'Our Villa') if villa_photos else "Villa"
    return render_template('villa_gallery.html', photos=villa_photos, villa_name=v_name)

if __name__ == '__main__':
    # Render के लिए पोर्ट फिक्स: 0.0.0.0 का उपयोग अनिवार्य है
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
