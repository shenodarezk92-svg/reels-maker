from flask import Flask, request, jsonify
import subprocess
import requests
import os
import uuid

app = Flask(__name__)

MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

@app.route('/make-video', methods=['POST'])
def make_video():
    data = request.json
    image_url = data.get('image_url')
    
    img_path = f"/tmp/{uuid.uuid4()}.jpg"
    music_path = f"/tmp/music.mp3"
    out_path = f"/tmp/{uuid.uuid4()}.mp4"
    
    # Download image
    r = requests.get(image_url)
    with open(img_path, 'wb') as f:
        f.write(r.content)
    
    # Download music once
    if not os.path.exists(music_path):
        r = requests.get(MUSIC_URL)
        with open(music_path, 'wb') as f:
            f.write(r.content)
    
    # Make video
    subprocess.run([
        'ffmpeg', '-loop', '1', '-i', img_path,
        '-i', music_path,
        '-c:v', 'libx264', '-t', '15',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest',
        out_path
    ])
    
    return jsonify({'video_path': out_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
