from flask import Flask
from flask_cors import CORS

from db import db
from models import Book,BookWriter,CustomerBook,Customer,Writer



def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book-management.db"
    db.init_app(app)

    from routes import blp
    app.register_blueprint(blp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()




#  book
#  customer
#  writer