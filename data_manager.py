from models import db, User, Movie


class DataManager:

    def create_user(self, name):
        """Add a new user to the DB."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self):
        """Return a list of all users."""
        return User.query.all()

    def get_movies(self, user_id):
        """Return all movies for a specific user."""
        user = User.query.get(user_id)
        return user.movies if user else []

    def add_movie(self, name=None, director=None, year=None, poster_url=None, user_id=None):
        """Add a new movie to a user's favorites."""
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

    def update_movie(self, movie_id, new_title):
        """Update the title of a movie."""
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = new_title
            db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        """Delete a movie by ID."""
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
        return movie
