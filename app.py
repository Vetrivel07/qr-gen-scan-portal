from flask import Flask, render_template, request, send_from_directory
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import time
import cv2
from pyzbar.pyzbar import decode

app = Flask(__name__)
UPLOAD_FOLDER = "./static/qr_code"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    qr_path = None
    if request.method == 'POST':
        input_data = request.form['qrdata'].strip()
        is_link = input_data.startswith("http://") or input_data.startswith("https://")

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Add label below QR code
        label = "Scan to open link" if is_link else "Scan for message"
        font = ImageFont.load_default()
        img_w, img_h = img.size
        new_img = Image.new("RGB", (img_w, img_h + 30), "white")
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text(((img_w - bbox[2]) / 2, img_h + 5), label, font=font, fill="black")

        filename = f"qr_{int(time.time())}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        new_img.save(filepath)
        qr_path = f"/static/qr_code/{filename}"

    return render_template('generate.html', qr_path=qr_path)

# Route to download the QR code image
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Route to Scanner
@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

if __name__ == '__main__':
    app.run(debug=True)
