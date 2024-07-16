from flask import Blueprint, request, send_file, current_app
from PIL import Image, ImageDraw, ImageFont
import io, os
import math

image_processing = Blueprint('image_processing', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@image_processing.route('/generate', methods=['POST'])
def generate_image():
    left_image_path = None
    right_image_path = None

    if 'file_same' in request.files and allowed_file(request.files['file_same'].filename):
        file = request.files['file_same']
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'file_same.png')
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        left_image_path = right_image_path = file_path
    elif 'file_left' in request.files and 'file_right' in request.files:
        if allowed_file(request.files['file_left'].filename) and allowed_file(request.files['file_right'].filename):
            file_left = request.files['file_left']
            file_right = request.files['file_right']
            left_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'file_left.png')
            right_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'file_right.png')
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_left.save(left_image_path)
            file_right.save(right_image_path)
        else:
            return 'Invalid file type', 400
    else:
        return 'No file part', 400

    text1 = request.form.get('right_text', '').upper()[:16]
    text2 = request.form.get('left_text', '').upper()[:16]
    base_choice = request.form['base']
    top_text_option = request.form.get('top_text', 'no')
    right_top_text = request.form.get('right_top_text', '').upper()[:16]
    left_top_text = request.form.get('left_top_text', '').upper()[:16]
    right_text_color = request.form.get('right_text_color', '#000000')
    left_text_color = request.form.get('left_text_color', '#000000')
    right_top_text_color = request.form.get('right_top_text_color', '#000000')
    left_top_text_color = request.form.get('left_top_text_color', '#000000')
    
    if base_choice == 'white':
        base_image_path = 'static/Mantra-Mock-Templates/greatwhite.png'
        text_color = "black"
    elif base_choice == "guide":
        base_image_path = 'static/Mantra-Mock-Templates/white-guidelines.png'
        text_color = "black"
    elif base_choice == "black":
        base_image_path = 'static/Mantra-Mock-Templates/black.png'
        text_color = "white"
    elif base_choice == "greatwhite":
        base_image_path = 'static/Mantra-Mock-Templates/greatwhite.png'
        text_color = "black"
    elif base_choice == "grey":
        base_image_path = 'static/Mantra-Mock-Templates/grey.png'
        text_color = "black"
    elif base_choice == "navy":
        base_image_path = 'static/Mantra-Mock-Templates/navy.png'
        text_color = "white"
    elif base_choice == "red":
        base_image_path = 'static/Mantra-Mock-Templates/red.png'
        text_color = "white"
    elif base_choice == "royalblue":
        base_image_path = 'static/Mantra-Mock-Templates/royalblue.png'
        text_color = "white"
    else:
        # Default case if no valid base_choice is found
        base_image_path = 'static/Mantra-Mock-Templates/black.png'
        text_color = "white"
        
    overlay_boxes = [
        (660, 1590, 660 + 900, 1590 + 675),  # Left overlay
        (2950, 1590, 2950 + 900, 1590 + 675)   # Right overlay
    ]
    text1_box = (400, 4700, 400 + 900, 4700 + 675)
    text2_box = (3200, 4700, 3200 + 900, 4700 + 675)
    side_right_box = (950, 6350, 950 + 275, 6350 + 125)
    side_left_box = (3290, 6350, 3290 + 275, 6350 + 125)
    middle_left_box = (1800, 5400, 1800 + 225, 5400 + 125)
    middle_right_box = (2300, 5400, 2300 + 225, 5400 + 125)

    try:
        base_image = Image.open(base_image_path)
        overlay_image_left = Image.open(left_image_path)
        overlay_image_right = Image.open(right_image_path)
        
        for idx, box in enumerate(overlay_boxes):
            max_width = box[2] - box[0]
            max_height = box[3] - box[1]

            if top_text_option != 'no':
                max_height -= 250  # Adjust height to allow space for top text

            if idx == 0:
                overlay_image = overlay_image_left
            else:
                overlay_image = overlay_image_right

            overlay_image.thumbnail((max_width, max_height), Image.ANTIALIAS)
            image_width, image_height = overlay_image.size
            position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
            base_image.paste(overlay_image, position, overlay_image.convert("RGBA"))

        overlay_image_left.thumbnail((275, 200), Image.ANTIALIAS)
        base_image.paste(overlay_image_left, (1950, 6320), overlay_image_left.convert("RGBA"))
        overlay_image_right.thumbnail((275, 200), Image.ANTIALIAS)
        base_image.paste(overlay_image_right, (2330, 6320), overlay_image_right.convert("RGBA"))
        
    except Exception as e:
        return f"Error: {e}", 400

    draw = ImageDraw.Draw(base_image)
    font_path = os.path.join('static', 'College_Block.otf')

    try:
        font = ImageFont.truetype(font_path, 200)
    except Exception as e:
        return f"Error loading font: {e}", 500

    def draw_text_within_box(draw, text, box, font, fill):
        max_width = box[2] - box[0]
        max_height = box[3] - box[1]
        font_size = font.size
        text_width, text_height = draw.textsize(text, font=font)

        # Reduce font size until text fits within the box, but don't make it too small
        while (text_width > max_width or text_height > max_height) and font_size > 5:
            font_size -= 5
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = draw.textsize(text, font=font)

        # Position text below the image
        position = (box[0] + (max_width - text_width) // 2, box[3] -250)  # Adjust the 50 to move text closer or further from the image
        draw.text(position, text, fill=fill, font=font)

    def draw_curved_text(draw, text, position, radius, font, fill):
        angle_step = 180 / (len(text) - 1) if len(text) > 1 else 180
        angle = -90 - angle_step * ((len(text) - 1) / 2)  # Center the text
        for char in text:
            char_width, char_height = draw.textsize(char, font=font)
            x = position[0] + radius * math.cos(math.radians(angle)) - char_width / 2
            y = position[1] + radius * math.sin(math.radians(angle)) - char_height / 2
            draw.text((x, y), char, font=font, fill=fill)
            angle += angle_step

    draw_text_within_box(draw, text1, text1_box, font, right_text_color)
    draw_text_within_box(draw, text2, text2_box, font, left_text_color)
    draw_text_within_box(draw, text1, side_right_box, font, right_text_color)
    draw_text_within_box(draw, text2, side_left_box, font, left_text_color)

    right_image_center = ((overlay_boxes[1][0] + overlay_boxes[1][2]) / 2, overlay_boxes[1][3] - 125)
    left_image_center = ((overlay_boxes[0][0] + overlay_boxes[0][2]) / 2, overlay_boxes[0][3] - 125)

    if top_text_option == 'straight':
        # top_text_box_right = (overlay_boxes[1][0], overlay_boxes[1][3], overlay_boxes[1][2], overlay_boxes[1][3] + 50)
        top_text_box_left = (675, 1580, 675 + 900, 1580 + 675)
        top_text_box_right =(2950, 1580, 2950 + 900, 1580 + 675)
        # top_text_box_left = (overlay_boxes[0][0], overlay_boxes[0][3], overlay_boxes[0][2], overlay_boxes[0][3] + 50)
        draw_text_within_box(draw, right_top_text, top_text_box_right, font, right_top_text_color)
        draw_text_within_box(draw, left_top_text, top_text_box_left, font, left_top_text_color)
    elif top_text_option == 'curved':
        radius = 150  # Adjust as necessary
        draw_curved_text(draw, right_top_text, right_image_center, radius, font, right_top_text_color)
        draw_curved_text(draw, left_top_text, left_image_center, radius, font, left_top_text_color)

    img_io = io.BytesIO()
    base_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')



