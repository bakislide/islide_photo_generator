from flask import Flask
from blueprints.main.routes import main
from blueprints.image_processing.image_processing import image_processing

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'ai'}

app.register_blueprint(main)
app.register_blueprint(image_processing)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

