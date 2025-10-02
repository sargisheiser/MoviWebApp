from flask import Flask, render_template, request, redirect, url_for
from models import db
from data_manager import DataManager
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

dm = DataManager()


@app.route("/")
def index():
    users = dm.get_users()
    return render_template("index.html", users=users)


@app.route("/movies/<int:user_id>")
def movies(user_id):
    movies = dm.get_movies(user_id)
    user = None
    if movies:
        user = movies[0].user
    else:
        from models import User
        user = User.query.get(user_id)
    return render_template("movies.html", username=user.name, movies=movies)


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("instance/moviweb.sqlite"):
            db.create_all()
    app.run(debug=True)
