"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Movie, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/register', methods=['GET'])
def register_form():

    return render_template("register_form.html")

@app.route('/register', methods=['POST'])
def register_process():
    email = request.form["email"]
    password = request.form["password"]
    age = int(request.form["age"])
    zipcode = request.form["zipcode"]

    new_user = User(email=email, password=password, age=age, zipcode=zipcode)

    db.session.add(new_user)
    db.session.commit()

    flash(f"User {email} added.")
    return redirect("/")

@app.route('/login', methods=['GET'])
def login_form():
    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def login_process():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User does not exist.")
        return redirect("/login")
    
    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect(f"/users/{user.user_id}")

@app.route('/logout')
def logout():
    del session["user_id"]
    flash("Logged out")
    return redirect("/")

@app.route("/users")
def user_list():
    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/users/<int:user_id>")
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template("user.html", user=user)

@app.route("/movies")
def movie_list():
    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:movie_id>", methods=['GET'])
def movie_detail(movie_id):
    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None
    
    return render_template("movie.html",
    movie=movie, user_rating=user_rating)

@app.route("/movies/<int:movie_id>", methods=['POST'])
def movie_detail_process(movie_id):
    score = int(request.form["score"])
    user_id = session.get("user_id")
    if not user_id:
        raise Exception("No user logged in.")
    
    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if rating:
        rating.score = score
        flash("Rating added.")
    else:
        rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
        flash("Rating added.")
        db.session.add(rating)
    
    db.session.commit()

    return redirect(f"/movies/{movie_id}")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
