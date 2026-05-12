from flask import Flask, request, send_file
import subprocess
import requests
import os
import uuid

app = Flask(__name__)

MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

@app.route('/make-video', methods=['POST'])
def make_video():
    data = request.json
    image_url = data.get('image_url') or data.get('imageUrl')
    
    img_path = f"/tmp/{uuid.uuid4()}.jpg"
    music_path = "/tmp/music.mp3"
    out_path = f"/tmp/{uuid.uuid4()}.mp4"
    
    r = requests.get(image_url)
    with open(img_path, 'wb') as f:
        f.write(r.content)
    
    if not os.path.exists(music_path):
        r = requests.get(MUSIC_URL)
        with open(music_path, 'wb') as f:
            f.write(r.content)
    
    subprocess.run([
        'ffmpeg', '-loop', '1', '-i', img_path,
        '-i', music_path,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black',
        '-c:v', 'libx264', '-t', '15',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest',
        out_path
    ])
    
    return send_file(out_path, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
