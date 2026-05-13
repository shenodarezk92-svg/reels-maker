import requests, subprocess, os, uuid
from flask import Flask, request

app = Flask(__name__)

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir('.')
    return {'files': files}

@app.route('/make-video', methods=['POST'])
def make_video():
    data = request.json
    image_url = data['image_url']

    uid = str(uuid.uuid4())[:8]
    img_path = f"/tmp/{uid}.png"
    out_path = f"/tmp/{uid}.mp4"

    img_data = requests.get(image_url, timeout=30)
    with open(img_path, 'wb') as f:
        f.write(img_data.content)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", "music.mp3",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-t", "15",
        "-vf", "scale=1080:1920,setsar=1",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True)

    with open(out_path, 'rb') as f:
        video_data = f.read()

    os.remove(img_path)
    os.remove(out_path)

    return app.response_class(
        response=video_data,
        mimetype='video/mp4'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
