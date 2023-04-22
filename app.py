#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_migrate import Migrate
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for,
    jsonify,abort
  )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
import sys
from datetime import datetime
from models import db, Genre,Venue,Artist,Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # get all distinct city and state combinations
  areas = db.session.query(Venue.city, Venue.state).distinct().all()

  data = []

  for area in areas:
      # find all venues in this city and state
      venues = Venue.query.filter_by(city=area.city, state=area.state).all()

      # create dictionary for each venue
      venue_data = []
      for venue in venues:
          num_upcoming_shows = 0
          for show in venue.shows:
              if show.start_time > datetime.now():
                  num_upcoming_shows += 1

          venue_data.append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": num_upcoming_shows
          })

      # add area dictionary to data list
      data.append({
          "city": area.city,
          "state": area.state,
          "venues": venue_data
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')

  # Search for venues by name
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  data = []
  for venue in search_results:
      # Filter upcoming shows
      upcoming_shows = Show.query.filter(
          Show.start_time > datetime.now(),
          Show.venue_id == venue.id
      ).all()

      data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows),
      })

  response = {
      "count": len(search_results),
      "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows = []
  current_time = datetime.utcnow()

  for show in venue.shows:
     artist = show.artist
     show_details = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link":artist.image_link,
        "start_time":format_datetime(str(show.start_time))
     }
     if show.start_time > current_time:
        upcoming_shows.append(show_details)
     else:
        past_shows.append(show_details)
  
  data = vars(venue)

  data["genres"]=[g.name for g in venue.genres]
  data["past_shows"]=past_shows
  data["upcoming_shows"]=upcoming_shows
  data["past_shows_count"]=len(past_shows)
  data["upcoming_shows_count"]=len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf':False})

  if form.validate():
     
    try:
      venue= Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
      genres = request.form.getlist('genres')
      for genre_name in genres:
          genre = Genre(name=genre_name, venue_id=venue.id)
          db.session.add(genre)
      db.session.commit()

    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('venues'))
  
  else:
    message=[]
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error=False
  try:
    Show.query.filter_by(venue_id=venue_id).delete()
    Genre.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  artists_list = [artist for artist in data]
  return render_template('pages/artists.html', artists=artists_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  # Search for venues by name
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  data = []
  for artist in search_results:
      # Filter upcoming shows
      upcoming_shows = Show.query.filter(
          Show.start_time > datetime.now(),
          Show.artist_id == artist.id
      ).all()

      data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(upcoming_shows),
      })

  response = {
      "count": len(search_results),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = []
  upcoming_shows = []
  current_time = datetime.utcnow()

  for show in artist.shows:
     venue = show.venue
     show_details = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link":venue.image_link,
        "start_time":format_datetime(str(show.start_time))
     }
     if show.start_time > current_time:
        upcoming_shows.append(show_details)
     else:
        past_shows.append(show_details)
  
  data = vars(artist)

  data["genres"]=[g.name for g in artist.genres]
  data["past_shows"]=past_shows
  data["upcoming_shows"]=upcoming_shows
  data["past_shows_count"]=len(past_shows)
  data["upcoming_shows_count"]=len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)

  form.state.data=artist.state
  form.genres.data = [g.name for g in artist.genres]
  form.seeking_venue.data = artist.seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error=False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    
    # update genres
    artist.genres = []
    genres = request.form.getlist('genres')
    for genre_name in genres:
        genre = Genre.query.filter_by(name=genre_name).one_or_none()
        if not genre:
            genre = Genre(name=genre_name)
        artist.genres.append(genre)
    
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website_link = request.form.get('website_link')
    artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error=True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error:
     abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  
  form.state.data=venue.state
  form.genres.data = [g.name for g in venue.genres]
  form.seeking_talent.data = venue.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error=False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    
    # update genres
    venue.genres = []
    genres = request.form.getlist('genres')
    for genre_name in genres:
        genre = Genre.query.filter_by(name=genre_name).one_or_none()
        if not genre:
            genre = Genre(name=genre_name)
        venue.genres.append(genre)
    
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website_link = request.form.get('website_link')
    venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error=True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error:
     abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      artist=Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()

      genres = request.form.getlist('genres')
      for genre_name in genres:
          genre = Genre(name=genre_name, artist_id=artist.id)
          db.session.add(genre)
      db.session.commit()

    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('artists'))

  else:
    message=[]
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_artist.html', form=form)
    

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(Show).join(Artist,Show.artist_id==Artist.id).join(Venue,Show.venue_id==Venue.id).all()
  data = []
  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # get artists and venues from the database and pass them to showform for options
  form = ShowForm()
  form.artist_id.choices = [(artist.id, f"{artist.id}: {artist.name}") for artist in Artist.query.all()]
  form.venue_id.choices = [(venue.id, f"{venue.id}: {venue.name}") for venue in Venue.query.all()]
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      show=Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(show)
      db.session.commit()

    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()
    
    flash('The new show was successfully listed!')
    return redirect(url_for('shows'))
  
  else:
    message=[]
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_show.html', form=form)
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
