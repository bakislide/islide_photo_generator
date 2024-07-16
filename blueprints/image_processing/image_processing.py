from flask import Blueprint, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import io, base64

image_processing = Blueprint('image_processing', __name__)

@image_processing.route('/process-image', methods=['POST'])
def process_image():
    file = request.files['image']
    text = request.form.get('text', '')
    
    # Process your image here (example)
    image = Image.open(file.stream)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 24)
    draw.text((10, 10), text, font=font, fill='red')
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    return jsonify({'image': 'data:image/png;base64,' + encoded_img})