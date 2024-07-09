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

        text1 = request.form['text1'][:16].upper()  # Limit text1 to 16 characters
        text2 = request.form['text2'][:16].upper()  # Limit text2 to 16 characters
        base_choice = request.form['base']
        
        # Determine the base image and text color based on user choice
        if base_choice == 'white':
            base_image_path = 'static/white_base.png'
            text_color = "black"
        elif base_choice == "guide":
            base_image_path = 'static/black_base_guards.png'
            text_color = "black"
        else:
            base_image_path = 'static/black_base.png'
            text_color = "white"
            
        # Define bounding boxes for the overlay images and text
        overlay_boxes = [
            (130, 309, 130 + 176, 309 + 127),  # Logo bounding box (left, top, right, bottom)
            (570, 309, 570 + 176, 309 + 127)   # Another logo bounding box
        ]
        text1_box = (80, 950, 80 + 176, 950 + 127)  # Text1 bounding box (left, top, right, bottom)
        text2_box = (620, 950, 620 + 176, 950 + 127)  # Text2 bounding box (left, top, right, bottom)

        # Smaller overlay boxes for side right and side left text
        side_right_box = (180, 1200, 180 + 55, 1200 + 25)  # Adjust these values based on the slide position
        side_left_box = (630, 1200, 630 + 55, 1200 + 25)   # Adjust these values based on the slide position

        # New overlay boxes for the middle slides
        middle_left_box = (350, 1200, 350 + 45, 1200 + 25)  # New overlay box for the middle left slide
        middle_right_box = (400, 1200, 600 + 45, 1200 + 25) # New overlay box for the middle right slide

        try:
            base_image = Image.open(base_image_path)
            overlay_image = Image.open(file_path)
            
            # Resize and paste the overlay image within each bounding box, centered
            for box in overlay_boxes:
                max_width = box[2] - box[0]
                max_height = box[3] - box[1]
                overlay_image.thumbnail((max_width, max_height), Image.ANTIALIAS)
                image_width, image_height = overlay_image.size
                position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
                base_image.paste(overlay_image, position, overlay_image.convert("RGBA"))

            # New overlays for the middle slides
            overlay_image.thumbnail((55, 40), Image.ANTIALIAS)
            base_image.paste(overlay_image, (375, 1215), overlay_image.convert("RGBA"))
            base_image.paste(overlay_image, (460, 1215), overlay_image.convert("RGBA"))
            
        except Exception as e:
            return f"Error: {e}", 400

        draw = ImageDraw.Draw(base_image)
        font_path = os.path.join('static', 'College_Block.otf')

        try:
            font = ImageFont.truetype(font_path, 40)  # Starting font size
        except Exception as e:
            return f"Error loading font: {e}", 500

        # Adjust the text size to fit within the bounding boxes
        def draw_text_within_box(draw, text, box, font, fill):
            max_width = box[2] - box[0]
            max_height = box[3] - box[1]
            font_size = font.size
            text_width, text_height = draw.textsize(text, font=font)

            # Reduce font size until text fits within the box
            while text_width > max_width or text_height > max_height:
                font_size -= 1
                if font_size < 1:  # Prevent font size from becoming non-positive
                    break
                font = ImageFont.truetype(font_path, font_size)
                text_width, text_height = draw.textsize(text, font=font)

            position = (box[0] + (max_width - text_width) // 2, box[1] + (max_height - text_height) // 2)
            draw.text(position, text, fill=fill, font=font)

        draw_text_within_box(draw, text1, text1_box, font, text_color)
        draw_text_within_box(draw, text2, text2_box, font, text_color)

        # Draw side right and side left text centered within their smaller bounding boxes
        draw_text_within_box(draw, text1, side_right_box, font, text_color)
        draw_text_within_box(draw, text2, side_left_box, font, text_color)

        img_io = io.BytesIO()
        base_image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True, port=5002)
