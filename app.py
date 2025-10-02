from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

users = {"Deb": [{"title": "Titanic", "year": 1997, "director": "James Cameron"}]}


@app.route("/")
def index():
    return render_template("index.html", users=users.keys())


@app.route("/movies/<username>")
def movies(username):
    return render_template("movies.html", username=username, movies=users.get(username, []))


if __name__ == "__main__":
    app.run(debug=True)
