from flask import Flask
from flask_cors import CORS
from routes.finance_routes import finance_bp
# from frontend.routes.auth_views import auth_views
# from frontend.routes.finance_views import finance_views
from config.settings import UPLOAD_FOLDER
import os, logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        app.logger.debug("Debug logger is configured!")
    
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Register blueprint
    app.register_blueprint(finance_bp, url_prefix = '/api')
    # app.register_blueprint(auth_views)
    # app.register_blueprint(finance_views)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
