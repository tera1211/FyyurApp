from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Genre(db.Model):
   __tablename__ = 'genre'

   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, nullable=False)
   venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'))
   artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',backref='venue_genres',lazy='joined', cascade="all, delete")
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String())
    shows = db.relationship('Show', backref='venue_shows', lazy='joined', cascade="all, delete")

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',backref='artists_genres',lazy='joined', cascade="all, delete")
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist_shows', lazy='joined', cascade="all, delete")

class Show(db.Model):
   __tablename__ = 'show'

   id = db.Column(db.Integer, primary_key=True)
   artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
   venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'))
   start_time = db.Column(db.DateTime)
   venue = db.relationship('Venue', backref=db.backref('shows_venue', cascade='all, delete'))
   artist = db.relationship('Artist', backref=db.backref('shows_artist', cascade='all, delete'))