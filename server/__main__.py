import os
import dotenv
from flask import Flask
from config import config
from flask_migrate import Migrate
from argparse import ArgumentParser
from paste.translogger import TransLogger
from logging import INFO, Formatter, getLogger
from logging.handlers import RotatingFileHandler
from server.models.base import db
from server.routes.home import home as home_blueprint
from server.routes.api import api as api_blueprint

dotenv.load_dotenv()

def create_app(use_waitress=False):
    app = Flask(__name__, template_folder='server/templates', static_folder='server/static')
    config_name = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    app.register_blueprint(home_blueprint, url_prefix='/')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    db.init_app(app)
    Migrate(app, db)

    # 設置日誌處理器
    if not os.path.exists('log'):
        os.makedirs('log')
    
    file_handler = RotatingFileHandler(os.getenv('LOG_PATH', 'log/access.log'), maxBytes=10000, backupCount=1)
    file_handler.setLevel(INFO)
    file_handler.setFormatter(Formatter('%(message)s'))

    app_logger = getLogger('wsgi')
    app_logger.setLevel(INFO)
    app_logger.addHandler(file_handler)

    if use_waitress:
        return TransLogger(app, setup_console_handler=False)

    return app

def waitress_entrypoint():
    return create_app(use_waitress = True)

if __name__ == '__main__':
    parser = ArgumentParser(description='Run the Flask app.')
    parser.add_argument('--port', type=int, default=int(os.getenv('FLASK_RUN_PORT', 3838)), help='Port to run this server on')
    args = parser.parse_args()
    
    # serve(create_app(use_waitress=True), host='0.0.0.0', port=args.port, threads=8)
    
    app = create_app()
    app.run(host='0.0.0.0', port=args.port, debug=True)