from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Movie
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def index():
    users = User.query.all()  # get all users from DB
    return render_template("index.html", users=users)


@app.route("/movies/<int:user_id>")
def movies(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("movies.html", username=user.name, movies=user.movies)


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("instance/moviweb.sqlite"):
            db.create_all()
    app.run(debug=True)
