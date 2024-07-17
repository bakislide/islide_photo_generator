from flask import Blueprint, request, send_file, current_app
from PIL import Image
import io, os

image_processing = Blueprint('image_processing', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@image_processing.route('/generate', methods=['POST'])
def generate_image():
    left_image_path = None
    right_image_path = None

    # Handling different file uploads
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

    # Determine the base image
    base_choice = request.form.get('base', 'black')  # Default to 'black' if no base is provided
    base_image_path = os.path.join('static/Mantra-Mock-Templates', f'{base_choice}.png')
    base_image = Image.open(base_image_path)

    # Define the overlay positions for left and right images
    left_positions = [0, 2, 4]  # Indices for left images
    right_positions = [1, 3, 5]  # Indices for right images
    overlay_boxes = [
        (660, 1590, 1560, 2265),  # Left main overlay
        (2950, 1590, 3850, 2265), # Right main overlay


        (1850, 6350, 1900 + 250, 6350 + 150),  # Top left small overlay
       (2300, 6350, 2400 + 250, 6350 + 150), # Top right small overlay
        # (950, 6250, 1225, 6375),  # Top left small overlay
        # (3290, 6250, 3565, 6375), # Top right small overlay


        # (950, 6475, 1225, 6575),  # Bottom left small overlay
        # (3290, 6475, 3565, 6575)  # Bottom right small overlay

        # # (950, 7000, 1225, 7125),  # Bottom left small overlay
        # # (3290, 7000, 3565, 7125)  # Bottom right small overlay
    ]

    try:
        overlay_image_left = Image.open(left_image_path).convert("RGBA") if left_image_path else None
        overlay_image_right = Image.open(right_image_path).convert("RGBA") if right_image_path else None

        # Place each image according to its position
        for idx, box in enumerate(overlay_boxes):
            if idx in left_positions and overlay_image_left:
                overlay_image = overlay_image_left
            elif idx in right_positions and overlay_image_right:
                overlay_image = overlay_image_right
            else:
                continue  # Skip if no image is available for the position

            max_width = box[2] - box[0]
            max_height = box[3] - box[1]
            overlay_image.thumbnail((max_width, max_height), Image.ANTIALIAS)
            image_width, image_height = overlay_image.size
            position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
            base_image.paste(overlay_image, position, overlay_image)

    except Exception as e:
        return f"Error processing images: {e}", 500

    img_io = io.BytesIO()
    base_image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')