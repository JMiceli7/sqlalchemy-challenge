# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date_converted = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_previous = latest_date_converted - dt.timedelta(days=365)
    query = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_previous
    ).order_by(Measurement.date).all()
    precipitation_dict = {date: prcp for date, prcp in query}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List of Stations."""
    results = session.query(Station.station, Station.name).all()
    stations_list = [{'station': station, 'name': name} for station, name in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Dates and Temperature of Most Active Station"""
    most_active_station = session.query(Measurement.station, 
            func.count(Measurement.station).label('count')
            ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date_converted = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_previous = latest_date_converted - dt.timedelta(days=365)
    temperature_data = session.query(Measurement.tobs).filter(
    Measurement.station == most_active_station,
    Measurement.date >= one_year_previous
    ).all()
    tobs_list = [tob[0] for tob in temperature_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return list of the minimum, average, and maximum temperatures for a specified start date"""
    temperature_results = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.max(Measurement.tobs).label('TMAX'),
        func.avg(Measurement.tobs).label('TAVG')
    ).filter(Measurement.date >= start).all()
    temperature_stats = temperature_results[0]._asdict()
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return list of the minimum, average, and maximum temperatures for a specified start and end date."""
    temperature_results = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.max(Measurement.tobs).label('TMAX'),
        func.avg(Measurement.tobs).label('TAVG')
    ).filter(Measurement.date.between(start, end)).all()
    temperature_stats = temperature_results[0]._asdict()
    return jsonify(temperature_stats)

session.close()

if __name__ == '__main__':
    app.run(debug=True)
