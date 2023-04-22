import os
# Grabs the folder where the script runs.
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://user@localhost:5432/fyyurapp'
SQLALCHEMY_TRACK_MODIFICATIONS = False
