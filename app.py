# To import the Flask dependency
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set Up the Database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into our classes.
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Set Up Flask
app = Flask(__name__)

# Define the welcome route
@app.route("/")

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# Precipitation route
@app.route("/api/v1.0/precipitation")

def precipitation():
    # Calculates the date one year ago from the most recent date in the database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Write a query to get the date and precipitation for the previous year
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    # Create a dictionary with the date as the key and the precipitation as the value
   precip = {date: prcp for date, prcp in precipitation}
    # Use jsonify() to format our results into a JSON structured file
   return jsonify(precip)

# Stations route
@app.route("/api/v1.0/stations")

def stations():
    results = session.query(Station.station).all()
    # We want to start by unraveling our results into a one-dimensional array.
    # To convert the results to a list, we will need to use the list function, which is list(), and then convert that array into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Monthly Temperature Route
@app.route("/api/v1.0/tobs")

def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


# Statistics Route provide both a starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")




def stats(start=None, end=None):
    # Create a query to select the minimum, average, and maximum temperatures from our SQLite database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Determine the starting and ending date, add an if-not
    if not end:
        # asterisk is used to indicate there will be multiple results for our query: minimum, average, and maximum temperatures
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    # Calculate the temperature minimum, average, and maximum with the start and end dates
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)