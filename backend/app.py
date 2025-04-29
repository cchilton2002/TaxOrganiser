from flask import Flask
from routes.finance import finance_bp
from config import UPLOAD_FOLDER
import os

def create_app():
    app = Flask(__name__)
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Register blueprint
    app.register_blueprint(finance_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)