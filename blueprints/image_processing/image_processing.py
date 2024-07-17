# from flask import Blueprint, request, send_file, current_app, jsonify, url_for
# from PIL import Image
# import io, os
# import uuid
# import logging

# image_processing = Blueprint('image_processing', __name__)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# @image_processing.route('/generate', methods=['POST'])
# def generate_image():
#     try:
#         left_image_path = None
#         right_image_path = None

#         # Use /tmp directory for uploads
#         upload_folder = '/tmp/uploads'
#         os.makedirs(upload_folder, exist_ok=True)

#         # Handling different file uploads
#         if 'file_same' in request.files and allowed_file(request.files['file_same'].filename):
#             file = request.files['file_same']
#             file_path = os.path.join(upload_folder, 'file_same.png')
#             file.save(file_path)
#             left_image_path = right_image_path = file_path
#         elif 'file_left' in request.files and 'file_right' in request.files:
#             if allowed_file(request.files['file_left'].filename) and allowed_file(request.files['file_right'].filename):
#                 file_left = request.files['file_left']
#                 file_right = request.files['file_right']
#                 left_image_path = os.path.join(upload_folder, 'file_left.png')
#                 right_image_path = os.path.join(upload_folder, 'file_right.png')
#                 file_left.save(left_image_path)
#                 file_right.save(right_image_path)
#             else:
#                 return 'Invalid file type', 400
#         else:
#             return 'No file part', 400

#         # Determine the base image
#         base_choice = request.form.get('base', 'black')  # Default to 'black' if no base is provided
#         base_image_path = os.path.join('static/Mantra-Mock-Templates', f'{base_choice}.png')
#         base_image = Image.open(base_image_path)

#         # Define the overlay positions for left and right images
#         left_positions = [0, 2, 4]  # Indices for left images
#         right_positions = [1, 3, 5]  # Indices for right images
#         overlay_boxes = [
#             (660, 1590, 1560, 2265),  # Left main overlay
#             (2950, 1590, 3850, 2265), # Right main overlay
#             (1850, 6350, 1900 + 250, 6350 + 150),  # Top left small overlay
#             (2300, 6350, 2400 + 250, 6350 + 150), # Top right small overlay
#         ]

#         try:
#             overlay_image_left = Image.open(left_image_path).convert("RGBA") if left_image_path else None
#             overlay_image_right = Image.open(right_image_path).convert("RGBA") if right_image_path else None

#             # Place each image according to its position
#             for idx, box in enumerate(overlay_boxes):
#                 if idx in left_positions and overlay_image_left:
#                     overlay_image = overlay_image_left
#                 elif idx in right_positions and overlay_image_right:
#                     overlay_image = overlay_image_right
#                 else:
#                     continue  # Skip if no image is available for the position

#                 max_width = box[2] - box[0]
#                 max_height = box[3] - box[1]
#                 overlay_image.thumbnail((max_width, max_height), Image.ANTIALIAS)
#                 image_width, image_height = overlay_image.size
#                 position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
#                 base_image.paste(overlay_image, position, overlay_image)

#         except Exception as e:
#             return f"Error processing images: {e}", 500

#         # Generate a unique filename for the output image
#         output_filename = f"generated_{uuid.uuid4()}.png"
#         output_path = os.path.join(upload_folder, output_filename)
#         base_image.save(output_path, 'PNG')

#         # Return a URL to access the generated image
#         image_url = url_for('image_processing.download_file', filename=output_filename, _external=True)
#         return jsonify({"image_url": image_url})
#     except Exception as e:
#         return f"Error: {e}", 500

# @image_processing.route('/list_files', methods=['GET'])
# def list_files():
#     upload_folder = '/tmp/uploads'
#     files = os.listdir(upload_folder)
#     return jsonify(files)

# @image_processing.route('/download_file/<filename>', methods=['GET'])
# def download_file(filename):
#     upload_folder = '/tmp/uploads'
#     file_path = os.path.join(upload_folder, filename)
#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     else:
#         return "File not found", 404
from flask import Blueprint, request, send_file, current_app, jsonify, url_for, send_from_directory, redirect
from PIL import Image
import io, os
import uuid
import logging

image_processing = Blueprint('image_processing', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@image_processing.route('/generate', methods=['POST'])
def generate_image():
    try:
        left_image_path = None
        right_image_path = None

        # Use /tmp directory for uploads
        upload_folder = '/tmp/uploads'
        os.makedirs(upload_folder, exist_ok=True)

        # Handling different file uploads
        if 'file_same' in request.files and allowed_file(request.files['file_same'].filename):
            file = request.files['file_same']
            file_path = os.path.join(upload_folder, 'file_same.png')
            file.save(file_path)
            left_image_path = right_image_path = file_path
        elif 'file_left' in request.files and 'file_right' in request.files:
            if allowed_file(request.files['file_left'].filename) and allowed_file(request.files['file_right'].filename):
                file_left = request.files['file_left']
                file_right = request.files['file_right']
                left_image_path = os.path.join(upload_folder, 'file_left.png')
                right_image_path = os.path.join(upload_folder, 'file_right.png')
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

        # Generate a unique filename for the output image
        output_filename = f"generated_{uuid.uuid4()}.png"
        output_path = os.path.join(upload_folder, output_filename)
        base_image.save(output_path, 'PNG')

        # Redirect to the generated image URL
        image_url = url_for('image_processing.serve_image', filename=output_filename, _external=True)
        return redirect(image_url)
    except Exception as e:
        return f"Error: {e}", 500

@image_processing.route('/list_files', methods=['GET'])
def list_files():
    upload_folder = '/tmp/uploads'
    files = os.listdir(upload_folder)
    return jsonify(files)

@image_processing.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    upload_folder = '/tmp/uploads'
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@image_processing.route('/serve_image/<filename>', methods=['GET'])
def serve_image(filename):
    upload_folder = '/tmp/uploads'
    return send_from_directory(upload_folder, filename)
