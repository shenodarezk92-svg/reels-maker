import subprocess, os, uuid
import cloudinary
import cloudinary.uploader
from flask import Flask, request, send_file
import logging
from PIL import Image, ImageDraw, ImageFont
import textwrap
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
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
    try:
        logger.info("Uploading to Cloudinary...")
        result = cloudinary.uploader.upload(
            out_path,
            resource_type="video",
            public_id=uid,
            overwrite=True
        )
        os.remove(out_path)
        logger.info(f"Cloudinary URL: {result['secure_url']}")
        return {'url': result['secure_url']}
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {str(e)}")
        if os.path.exists(out_path):
            os.remove(out_path)
        return {'error': str(e)}, 500

@app.route('/video/<filename>', methods=['GET'])
def serve_video(filename):
    path = os.path.join(VIDEO_DIR, filename)
    return send_file(path, mimetype='video/mp4')

@app.route('/tiktokvgq7fMlk6rVDTpCUyKwNOIONQ8IgEs4D.txt', methods=['GET'])
def tiktok_verify():
    return 'tiktokvgq7fMlk6rVDTpCUyKwNOIONQ8IgEs4D\n', 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/.well-known/tiktokvgq7fMlk6rVDTpCUyKwNOIONQ8IgEs4D.txt', methods=['GET'])
def tiktok_verify_wellknown():
    return 'tiktokvgq7fMlk6rVDTpCUyKwNOIONQ8IgEs4D\n', 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/', methods=['GET'])
def index():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
