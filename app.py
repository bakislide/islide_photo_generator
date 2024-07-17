from flask import Flask
from blueprints.main.routes import main
from blueprints.image_processing.image_processing import image_processing
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'ai'}

app.register_blueprint(main)
app.register_blueprint(image_processing)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
