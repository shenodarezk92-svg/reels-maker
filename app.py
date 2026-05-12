from flask import Flask, request, send_file, jsonify
import subprocess
import requests
import os
import uuid

app = Flask(__name__)
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

@app.route('/make-video', methods=['POST'])
def make_video():
    try:
        data = request.json
        image_url = data.get('image_url') or data.get('imageUrl')
        
        if not image_url:
            return jsonify({"error": "image_url is required"}), 400

        img_path = f"/tmp/{uuid.uuid4()}.jpg"
        music_path = "/tmp/music.mp3"
        out_path = f"/tmp/{uuid.uuid4()}.mp4"

        # تحميل الصورة
        r = requests.get(image_url, timeout=30)
        with open(img_path, 'wb') as f:
            f.write(r.content)

        # تحميل الموسيقى لو مش موجودة
        if not os.path.exists(music_path):
            r = requests.get(MUSIC_URL, timeout=60)
            with open(music_path, 'wb') as f:
                f.write(r.content)

        # عمل الفيديو
        result = subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-i', music_path,
            '-vf', 'scale=1080:
