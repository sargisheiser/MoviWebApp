import urllib
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, User, Movie
from data_manager import DataManager
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
dm = DataManager()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")


@app.route("/")
def index():
    users = dm.get_users()
    return render_template("index.html", users=users)


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def user_movies_page(user_id):
    movies = dm.get_movies(user_id)
    user = User.query.get(user_id)
    return render_template("movies.html", username=user.name, movies=movies, user_id=user_id)


@app.route("/api/users", methods=["GET"])
def api_get_users():
    users = dm.get_users()
    return jsonify([{"id": u.id, "name": u.name} for u in users])


@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    user = dm.create_user(name)
    return jsonify({"id": user.id, "name": user.name}), 201


@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "name": user.name})


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def api_update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_name = data.get("name")
    if new_name:
        user.name = new_name
        db.session.commit()
    return jsonify({"id": user.id, "name": user.name})


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user_id} deleted"}), 200


@app.route("/api/users/<int:user_id>/movies", methods=["GET"])
def api_get_user_movies(user_id):
    movies = dm.get_movies(user_id)
    return jsonify([{
        "id": m.id,
        "name": m.name,
        "director": m.director,
        "year": m.year,
        "poster_url": m.poster_url
    } for m in movies])


@app.route("/api/users/<int:user_id>/movies", methods=["POST"])
def api_add_movie(user_id):
    data = request.get_json()
    title = data.get("title")
    if not title:
        return jsonify({"error": "Movie title required"}), 400

    query = urllib.parse.quote(title)
    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") != "True":
        return jsonify({"error": "Movie not found in OMDb"}), 404

    movie = dm.add_movie(
        name=response.get("Title"),
        director=response.get("Director"),
        year=response.get("Year"),
        poster_url=response.get("Poster"),
        user_id=user_id
    )

    return jsonify({
        "id": movie.id,
        "name": movie.name,
        "director": movie.director,
        "year": movie.year,
        "poster_url": movie.poster_url
    }), 201


@app.route("/api/movies/<int:movie_id>", methods=["GET"])
def api_get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return jsonify({
        "id": movie.id,
        "name": movie.name,
        "director": movie.director,
        "year": movie.year,
        "poster_url": movie.poster_url,
        "user_id": movie.user_id
    })


@app.route("/api/movies/<int:movie_id>", methods=["PUT"])
def api_update_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    data = request.get_json()
    new_title = data.get("title")
    if new_title:
        movie.name = new_title
        db.session.commit()
    return jsonify({
        "id": movie.id,
        "name": movie.name,
        "director": movie.director,
        "year": movie.year,
        "poster_url": movie.poster_url
    })


@app.route("/api/movies/<int:movie_id>", methods=["DELETE"])
def api_delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": f"Movie {movie_id} deleted"}), 200


@app.route("/users/<int:user_id>/movies/add", methods=["GET"])
def add_movie_page(user_id):
    from models import User
    user = User.query.get_or_404(user_id)
    return render_template("add_movie.html", username=user.name, user_id=user_id)


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("instance/moviweb.sqlite"):
            db.create_all()
    app.run(debug=True)
