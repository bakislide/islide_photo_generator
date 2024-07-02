from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    if 'file' not in request.files or not request.files['file']:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        print(f"File saved to: {file_path}")  # Debug print

        text1 = request.form['text1']
        text2 = request.form['text2']

        # Coordinates for the overlay images
        overlay_positions = [(130, 309), (570, 309)]

        # Text positions
        text1_positions = [(190, 1200), (170, 1000)]
        text2_positions = [(625, 1200), (650, 1000)]

        print(f"Text1 coordinates: {text1_positions}")  # Debug print
        print(f"Text2 coordinates: {text2_positions}")  # Debug print

        base_image_path = 'static/base_template.png'
        try:
            base_image = Image.open(base_image_path)
            overlay_image = Image.open(file_path)
            
            # Print dimensions of the images
            print(f"Base image size: {base_image.size}")  # Debug print
            print(f"Overlay image size: {overlay_image.size}")  # Debug print
            
            # Resize the overlay image to fit within a specified size
            max_size = (118, 200)  # Example maximum size
            overlay_image.thumbnail(max_size, Image.ANTIALIAS)
            print(f"Resized overlay image size: {overlay_image.size}")  # Debug print
            
            for pos in overlay_positions:
                base_image.paste(overlay_image, pos, overlay_image.convert("RGBA"))
        except Exception as e:
            return f"Error: {e}", 400

        draw = ImageDraw.Draw(base_image)
        font_path = os.path.join('static', 'arial.ttf')

        try:
            font = ImageFont.truetype(font_path, 20)  # Increased font size to 20
        except Exception as e:
            return f"Error loading font: {e}", 500

        for pos in text1_positions:
            draw.text(pos, text1, fill="red", font=font)
        for pos in text2_positions:
            draw.text(pos, text2, fill="red", font=font)

        img_io = io.BytesIO()
        base_image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True, port=5002)
