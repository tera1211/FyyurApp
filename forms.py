from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
import re
from enums import Genre, State

def is_valid_phone(number):
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id',
        coerce=int,
        validators=[DataRequired()]
    )
    venue_id = SelectField(
        'venue_id',
        coerce=int,
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent', default=False )

    seeking_description = StringField(
        'seeking_description'
    )

    def validate(self, **kwargs):
        # `**kwargs` to match the method's signature in the `FlaskForm` class.

        validated = Form.validate(self)

        if not validated:
            return False

        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False

        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False

        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False

        # if pass validation
        return True



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
    )

    def validate(self, **kwargs):
        # `**kwargs` to match the method's signature in the `FlaskForm` class.

        validated = Form.validate(self)

        if not validated:
            return False

        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False

        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False

        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False

        # if pass validation
        return True