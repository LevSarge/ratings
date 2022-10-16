"""Utility file to seed ratings database from MovieLens data in seed_data/"""
import datetime
from sqlalchemy import func
from model import User, Rating, Movie, connect_to_db, db
from server import app


def load_users(user_filename):
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open(user_filename):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies(movie_filename):
    """Load movies from u.item into database."""

    print("Movies")

    for row in enumerate(open(movie_filename)):
        row = row.rstrip()

        movie_id, title, released_str, junk, imdb_url = row.split("|")[:5]

        if released_str:
            released_at = datetime.datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None
        
        title = title[:-7]

        movie = Movie(title=title,
        released_str = released_str,
        imdb_url = imdb_url)

        db.session.add(movie)
    
    db.session.commit()

def load_ratings(rating_filename):
    """Load ratings from u.data into database."""

    print("Ratings")

    for row in enumerate(open(rating_filename)):
        row = row.rstrip()

        user_id = int(user_id)
        movie_id = int(movie_id)
        score = int(score)

        rating = Rating(user_id=user_id, movie_id=movie_id, score=score)

        db.session.add(rating)

    db.session.commit()

def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    user_filename = "seed_data/u.user"
    movie_filename = "seed_data/u.item"
    rating_filename = "seed_data/u.data"
    load_users(user_filename)
    load_movies(movie_filename)
    load_ratings(rating_filename)
    set_val_user_id()
