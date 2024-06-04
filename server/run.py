import os
import dotenv
from flask import Flask
from flask_migrate import Migrate
from app import utils, db, home as home_blueprint, api as api_blueprint

dotenv.load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.register_blueprint(home_blueprint, url_prefix='/')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.config['SQLALCHEMY_DATABASE_URI'] = utils.make_DBURL(
        os.getenv('DB_USER'),       # type: ignore
        os.getenv('DB_PASSWORD'),   # type: ignore
        os.getenv('DB_HOST'),       # type: ignore
        os.getenv('DB_PORT'),       # type: ignore
        os.getenv('DB_NAME'),       # type: ignore
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)
    Migrate(app, db)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
