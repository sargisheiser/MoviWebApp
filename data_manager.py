from models import db, User, Movie


class DataManager:

    def create_user(self, name):
        """Add a new user to the DB."""
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return None

    def get_users(self):
        """Return a list of all users."""
        try:
            return User.query.all()
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def get_movies(self, user_id):
        """Return all movies for a specific user."""
        try:
            user = User.query.get(user_id)
            return user.movies if user else []
        except Exception as e:
            print(f"Error fetching movies for user {user_id}: {e}")
            return []

    def add_movie(self, name=None, director=None, year=None, poster_url=None, user_id=None):
        """Add a new movie to a user's favorites."""
        try:
            new_movie = Movie(
                name=name,
                director=director,
                year=year,
                poster_url=poster_url,
                user_id=user_id
            )
            db.session.add(new_movie)
            db.session.commit()
            return new_movie
        except Exception as e:
            db.session.rollback()
            print(f"Error adding movie for user {user_id}: {e}")
            return None

    def update_movie(self, movie_id, new_title):
        """Update the title of a movie."""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                movie.name = new_title
                db.session.commit()
            return movie
        except Exception as e:
            db.session.rollback()
            print(f"Error updating movie {movie_id}: {e}")
            return None

    def delete_movie(self, movie_id):
        """Delete a movie by ID."""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
                return movie
            return None
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting movie {movie_id}: {e}")
            return None
