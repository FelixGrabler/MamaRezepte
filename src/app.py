from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ
from models import init_db
from db_content import fill_database


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URL")
init_db(app)
# fill_database(app)


@app.route("/")
def hello():
    return "Hello World from the backend!"


if __name__ == "__main__":
    print("Starting backend server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
