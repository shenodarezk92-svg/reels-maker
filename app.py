import subprocess, os, uuid
import cloudinary
import cloudinary.uploader
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import textwrap

app = Flask(name)
VIDEO_DIR = "/tmp/videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

cloudinary.config(
    cloud_name = "daphufs3c",
    api_key = "386948418168994",
    api_secret = "NpuA97HC5Iv4U496CS6AXWSmaY8"
)

def create_video(text, out_path):
    uid = str(uuid.uuid4())[:8]
    img_path = f"/tmp/{uid}.png"

    img = Image.open("bg.jpg").convert("RGB")
    img = img.resize((1080, 1920))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 100))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("font.otf", 70)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=20)
    total_height = len(lines) * 90
    y = (1920 - total_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (1080 - w) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += 90

    img.save(img_path)

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
    os.remove(img_path)

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir('.')
    return {'files': files}

@app.route('/make-video', methods=['POST'])
def make_video():
    data = request.json
    text = data['text']
    uid = str(uuid.uuid4())[:8]
    out_path = f"/tmp/{uid}.mp4"

    create_video(text, out_path)

    with open(out_path, 'rb') as f:
        video_data = f.read()
    os.remove(out_path)

    return app.response_class(
        response=video_data,
        mimetype='video/mp4'
    )

@app.route('/make-video-url', methods=['POST'])
def make_video_url():
    data = request.json
    text = data['text']
    uid = str(uuid.uuid4())[:8]
    out_path = f"/tmp/{uid}.mp4"

    create_video(text, out_path)

    result = cloudinary.uploader.upload(
        out_path,
        resource_type="video",
        public_id=uid,
        overwrite=True
    )

    os.remove(out_path)

    return {'url': result['secure_url']}

@app.route('/video/<filename>', methods=['GET'])
def serve_video(filename):
    path = os.path.join(VIDEO_DIR, filename)
    return send_file(path, mimetype='video/mp4')

if name == 'main':
    app.run(host='0.0.0.0', port=10000)
