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

        r = requests.get(image_url, timeout=30)
        with open(img_path, 'wb') as f:
            f.write(r.content)

        if not os.path.exists(music_path):
            r = requests.get(MUSIC_URL, timeout=60)
            with open(music_path, 'wb') as f:
                f.write(r.content)

        result = subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-i', music_path,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black',
            '-c:v', 'libx264', '-t', '15',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-shortest',
            '-preset', 'ultrafast',
            out_path
        ], timeout=120, capture_output=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.decode()}), 500

        if not os.path.exists(out_path):
            return jsonify({"error": "Video file not created"}), 500

        return send_file(out_path, mimetype='video/mp4')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
