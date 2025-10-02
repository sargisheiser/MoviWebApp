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
    try:
        users = dm.get_users()
        return render_template("index.html", users=users)
    except Exception as e:
        print(f"Error rendering index: {e}")
        return render_template("500.html"), 500


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def user_movies_page(user_id):
    try:
        movies = dm.get_movies(user_id)
        user = User.query.get_or_404(user_id)
        return render_template("movies.html", username=user.name, movies=movies, user_id=user_id)
    except Exception as e:
        print(f"Error loading movies for user {user_id}: {e}")
        return render_template("500.html"), 500


@app.route("/api/users", methods=["GET"])
def api_get_users():
    try:
        users = dm.get_users()
        return jsonify([{"id": u.id, "name": u.name} for u in users])
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500


@app.route("/api/users", methods=["POST"])
def api_create_user():
    try:
        data = request.get_json()
        name = data.get("name")
        if not name:
            return jsonify({"error": "Name is required"}), 400
        user = dm.create_user(name)
        if not user:
            return jsonify({"error": "Failed to create user"}), 500
        return jsonify({"id": user.id, "name": user.name}), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({"id": user.id, "name": user.name})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user {user_id}: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def api_update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        new_name = data.get("name")
        if new_name:
            user.name = new_name
            db.session.commit()
        return jsonify({"id": user.id, "name": user.name})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user {user_id}: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>/delete", methods=["DELETE"])
def api_delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {user_id} deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user {user_id}: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>/movies", methods=["GET"])
def api_get_user_movies(user_id):
    try:
        movies = dm.get_movies(user_id)
        return jsonify([{
            "id": m.id,
            "name": m.name,
            "director": m.director,
            "year": m.year,
            "poster_url": m.poster_url
        } for m in movies])
    except Exception as e:
        return jsonify({"error": f"Failed to fetch movies for user {user_id}: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>/movies", methods=["POST"])
def api_add_movie(user_id):
    try:
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

        if not movie:
            return jsonify({"error": "Failed to add movie"}), 500

        return jsonify({
            "id": movie.id,
            "name": movie.name,
            "director": movie.director,
            "year": movie.year,
            "poster_url": movie.poster_url
        }), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error adding movie: {str(e)}"}), 500


@app.route("/api/movies/<int:movie_id>", methods=["GET"])
def api_get_movie(movie_id):
    try:
        movie = Movie.query.get_or_404(movie_id)
        return jsonify({
            "id": movie.id,
            "name": movie.name,
            "director": movie.director,
            "year": movie.year,
            "poster_url": movie.poster_url,
            "user_id": movie.user_id
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch movie {movie_id}: {str(e)}"}), 500


@app.route("/api/movies/<int:movie_id>", methods=["PUT"])
def api_update_movie(movie_id):
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update movie {movie_id}: {str(e)}"}), 500


@app.route("/api/movies/<int:movie_id>", methods=["DELETE"])
def api_delete_movie(movie_id):
    try:
        deleted = dm.delete_movie(movie_id)
        if deleted:
            return jsonify({"message": f"Movie {movie_id} deleted"}), 200
        return jsonify({"error": f"Movie {movie_id} not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete movie {movie_id}: {str(e)}"}), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("instance/moviweb.sqlite"):
            db.create_all()
    app.run(debug=True)
