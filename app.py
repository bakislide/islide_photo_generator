import os
from flask import Flask, request, jsonify, send_file, send_from_directory, url_for
import requests
from PIL import Image
import io
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'generated_art'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'ai'}

def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def overlay_image(base_image, overlay_image_path, box):
    overlay_image = Image.open(overlay_image_path).convert("RGBA")
    max_width = box[2] - box[0]
    max_height = box[3] - box[1]
    overlay_image.thumbnail((max_width, max_height), Image.ANTIALIAS)
    image_width, image_height = overlay_image.size
    position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
    base_image.paste(overlay_image, position, overlay_image)

@app.route('/process-art', methods=['POST'])
def process_art():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    try:
        print(f"Downloading file from URL: {url}")
        # Download the file
        file_content = download_file(url)
        downloaded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'downloaded_image.png')
        with open(downloaded_image_path, 'wb') as f:
            f.write(file_content)
        print("File downloaded successfully")

        # Load the base image
        base_image_path = 'static/Mantra-Mock-Templates/greatwhite.png'  # Use greatwhite.png as the base template
        if not os.path.exists(base_image_path):
            return jsonify({'error': f"Base image {base_image_path} not found"}), 500
        base_image = Image.open(base_image_path).convert("RGBA")

        # Define the overlay boxes for the image
        overlay_boxes = [
            (660, 1590, 1560, 2265),  # Main overlay
            (2950, 1590, 3850, 2265), # Secondary overlay
            (1850, 6350, 1900 + 250, 6350 + 150),  # Top left small overlay
            (2300, 6350, 2400 + 250, 6350 + 150),  # Top right small overlay
        ]

        # Overlay the downloaded image on the base image
        for box in overlay_boxes:
            overlay_image(base_image, downloaded_image_path, box)
        print("Image overlay completed")

        # Save the processed image
        processed_filename = f"generated_{uuid.uuid4()}.png"
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        base_image.save(processed_filepath, 'PNG')
        print(f"Processed image saved at {processed_filepath}")

        # Generate a URL to access the generated image
        image_url = url_for('serve_image', filename=processed_filename, _external=True)

        return jsonify({'message': 'Art processed successfully', 'image_url': image_url}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/download_file/<filename>', methods=['GET'])
def download_file_route(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/serve_image/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
# import os
# import re
# import uuid
# import logging
# from flask import Flask, request, jsonify, send_file, send_from_directory, url_for, abort
# import requests
# from PIL import Image
# import magic

# app = Flask(__name__)

# UPLOAD_FOLDER = 'generated_art'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# def download_file(url):
#     if not re.match(r'^https?:\/\/', url):
#         raise ValueError("URL must start with http:// or https://")
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.content
#     else:
#         raise Exception(f"Failed to download file: {response.status_code}")

# def allowed_file(filename, file_content):
#     # Check extension
#     ext_allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
#     if not ext_allowed:
#         return False
#     # Check MIME type
#     mime = magic.Magic(mime=True)
#     mime_type = mime.from_buffer(file_content)
#     return mime_type in ['image/png', 'image/jpeg', 'image/gif']

# def sanitize_filename(filename):
#     return os.path.basename(filename)

# def overlay_image(base_image, overlay_image_path, box):
#     overlay_image = Image.open(overlay_image_path).convert("RGBA")
#     max_width = box[2] - box[0]
#     max_height = box[3] - box[1]
#     overlay_image.thumbnail((max_width, max_height), Image.LANCZOS)
#     image_width, image_height = overlay_image.size
#     position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
#     base_image.paste(overlay_image, position, overlay_image)

# @app.route('/process-art', methods=['POST'])
# def process_art():
#     data = request.json
#     if not data or 'url' not in data:
#         return jsonify({'error': 'No URL provided'}), 400

#     url = data['url']
#     try:
#         logging.info(f"Downloading file from URL: {url}")
#         # Download the file
#         file_content = download_file(url)
#         if not allowed_file('downloaded_image.png', file_content):
#             raise ValueError("Invalid file type")
#         downloaded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'downloaded_image.png')
#         with open(downloaded_image_path, 'wb') as f:
#             f.write(file_content)
#         logging.info("File downloaded successfully")

#         # Load the base image
#         base_image_path = 'static/Mantra-Mock-Templates/greatwhite.png'  # Use greatwhite.png as the base template
#         if not os.path.exists(base_image_path):
#             raise FileNotFoundError(f"Base image {base_image_path} not found")
#         base_image = Image.open(base_image_path).convert("RGBA")

#         # Define the overlay boxes for the image
#         overlay_boxes = [
#             (660, 1590, 1560, 2265),  # Main overlay
#             (2950, 1590, 3850, 2265), # Secondary overlay
#             (1850, 6350, 1900 + 250, 6350 + 150),  # Top left small overlay
#             (2300, 6350, 2400 + 250, 6350 + 150),  # Top right small overlay
#         ]

#         # Overlay the downloaded image on the base image
#         for box in overlay_boxes:
#             overlay_image(base_image, downloaded_image_path, box)
#         logging.info("Image overlay completed")

#         # Save the processed image
#         processed_filename = f"generated_{uuid.uuid4()}.png"
#         processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
#         base_image.save(processed_filepath, 'PNG')
#         logging.info(f"Processed image saved at {processed_filepath}")

#         # Generate a URL to access the generated image
#         image_url = url_for('serve_image', filename=processed_filename, _external=True)

#         return jsonify({'message': 'Art processed successfully', 'image_url': image_url}), 200
#     except Exception as e:
#         logging.error(f"Error: {e}")
#         return jsonify({'error': 'An error occurred while processing the art'}), 500

# @app.route('/list_files', methods=['GET'])
# def list_files():
#     try:
#         files = os.listdir(app.config['UPLOAD_FOLDER'])
#         return jsonify(files)
#     except Exception as e:
#         logging.error(f"Error listing files: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/download_file/<filename>', methods=['GET'])
# def download_file_route(filename):
#     try:
#         sanitized_filename = sanitize_filename(filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_filename)
#         if os.path.exists(file_path):
#             return send_file(file_path, as_attachment=True)
#         else:
#             return "File not found", 404
#     except Exception as e:
#         logging.error(f"Error downloading file: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/serve_image/<filename>', methods=['GET'])
# def serve_image(filename):
#     try:
#         sanitized_filename = sanitize_filename(filename)
#         return send_from_directory(app.config['UPLOAD_FOLDER'], sanitized_filename)
#     except Exception as e:
#         logging.error(f"Error serving image: {e}")
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080, debug=True)

# # import os
# # import re
# # import uuid
# # import logging
# # import time
# # import hashlib
# # from flask import Flask, request, jsonify, send_file, send_from_directory, url_for, abort
# # import requests
# # from PIL import Image
# # import filetype

# # app = Flask(__name__)

# # UPLOAD_FOLDER = 'generated_art'
# # if not os.path.exists(UPLOAD_FOLDER):
# #     os.makedirs(UPLOAD_FOLDER)

# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# # app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)

# # def generate_secure_token(filename, expiration=3600):
# #     expiration_time = int(time.time()) + expiration
# #     token = hashlib.sha256(f"{filename}{expiration_time}{app.config['SECRET_KEY']}".encode()).hexdigest()
# #     return f"{token}:{expiration_time}"

# # def validate_secure_token(token, filename):
# #     token_parts = token.split(':')
# #     if len(token_parts) != 2:
# #         return False
# #     token_hash, expiration_time = token_parts
# #     if int(expiration_time) < time.time():
# #         return False
# #     expected_hash = hashlib.sha256(f"{filename}{expiration_time}{app.config['SECRET_KEY']}".encode()).hexdigest()
# #     return expected_hash == token_hash

# # def download_file(url):
# #     if not re.match(r'^https?:\/\/', url):
# #         raise ValueError("URL must start with http:// or https://")
# #     response = requests.get(url)
# #     response.raise_for_status()  # Raise an exception for HTTP errors
# #     return response.content

# # def allowed_file(file_content):
# #     # Check MIME type using filetype
# #     kind = filetype.guess(file_content)
# #     return kind is not None and kind.mime in ['image/png', 'image/jpeg', 'image/gif']

# # def sanitize_filename(filename):
# #     return os.path.basename(filename)

# # def overlay_image(base_image, overlay_image_path, box):
# #     overlay_image = Image.open(overlay_image_path).convert("RGBA")
# #     max_width = box[2] - box[0]
# #     max_height = box[3] - box[1]
# #     overlay_image.thumbnail((max_width, max_height), Image.LANCZOS)
# #     image_width, image_height = overlay_image.size
# #     position = (box[0] + (max_width - image_width) // 2, box[1] + (max_height - image_height) // 2)
# #     base_image.paste(overlay_image, position, overlay_image)

# # @app.route('/process-art', methods=['POST'])
# # def process_art():
# #     data = request.json
# #     if not data or 'url' not in data:
# #         return jsonify({'error': 'No URL provided'}), 400

# #     url = data['url']
# #     try:
# #         logging.info(f"Downloading file from URL: {url}")
# #         # Download the file
# #         file_content = download_file(url)
# #         if not allowed_file(file_content):
# #             raise ValueError("Invalid file type")
# #         downloaded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'downloaded_image.png')
# #         with open(downloaded_image_path, 'wb') as f:
# #             f.write(file_content)
# #         logging.info("File downloaded successfully")

# #         # Load the base image
# #         base_image_path = 'static/Mantra-Mock-Templates/greatwhite.png'  # Use greatwhite.png as the base template
# #         if not os.path.exists(base_image_path):
# #             raise FileNotFoundError(f"Base image {base_image_path} not found")
# #         base_image = Image.open(base_image_path).convert("RGBA")

# #         # Define the overlay boxes for the image
# #         overlay_boxes = [
# #             (660, 1590, 1560, 2265),  # Main overlay
# #             (2950, 1590, 3850, 2265), # Secondary overlay
# #             (1850, 6350, 1900 + 250, 6350 + 150),  # Top left small overlay
# #             (2300, 6350, 2400 + 250, 6350 + 150),  # Top right small overlay
# #         ]

# #         # Overlay the downloaded image on the base image
# #         for box in overlay_boxes:
# #             overlay_image(base_image, downloaded_image_path, box)
# #         logging.info("Image overlay completed")

# #         # Save the processed image
# #         processed_filename = f"generated_{uuid.uuid4()}.png"
# #         processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
# #         base_image.save(processed_filepath, 'PNG')
# #         logging.info(f"Processed image saved at {processed_filepath}")

# #         # Generate a secure token and URL to access the generated image
# #         token = generate_secure_token(processed_filename)
# #         image_url = url_for('serve_image', filename=processed_filename, token=token, _external=True)

# #         return jsonify({'message': 'Art processed successfully', 'image_url': image_url}), 200
# #     except Exception as e:
# #         logging.error(f"Error: {e}")
# #         return jsonify({'error': 'An error occurred while processing the art'}), 500

# # @app.route('/serve_image/<filename>', methods=['GET'])
# # def serve_image(filename):
# #     token = request.args.get('token')
# #     if not token or not validate_secure_token(token, filename):
# #         abort(403)  # Forbidden

# #     try:
# #         sanitized_filename = sanitize_filename(filename)
# #         return send_from_directory(app.config['UPLOAD_FOLDER'], sanitized_filename)
# #     except Exception as e:
# #         logging.error(f"Error serving image: {e}")
# #         return jsonify({'error': str(e)}), 500

# # if __name__ == '__main__':
# #     app.run(host='0.0.0.0', port=8080, debug=True)
