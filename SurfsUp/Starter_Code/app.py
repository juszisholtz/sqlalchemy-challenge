# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#Home Page
@app.route("/")
def home():
    #List of all available API routes.
 return (
        'Available Routes:<br>'
        '/<br>'
        'For the most recent 12 months of precipitation data: /api/v1.0/precipitation<br>'
        'For a list of all the stations: /api/v1.0/stations<br>'
        'Dates and temperature observations of the most-active station for the previous year of data: /api/v1.0/tobs<br>'
        'For temperature statistics from a start date (YYYY-MM-DD) or a start-end range: /api/v1.0/<start> or /api/v1.0/<start>/<end><br>'
    )

#Precipiation values for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Begin a session in sql alchemy to pull data
    session = Session(engine)
    #get the latest date, so we can pull the info from 365 days (12 months) before this date.
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    year_before = (np.datetime64(most_recent_date) - np.timedelta64(365, 'D')).astype(str)
    #get precipitation data for the last year
    precip_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= year_before).all()

    #End the query
    session.close()

    #convert info to dict
    precipitation_data = {date: prcp for date, prcp in precip_data}

    #jsonify the data
    return jsonify(precipitation_data)

#Make a list of the sations from the data
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    #Pull station data
    stations_all = session.query(station.station).all()
    session.close()
    #Create list
    stations_list = [station[0] for station in stations_all]
    #Make it into json format
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #start a session
    session = Session(engine)

    # Get the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    year_before = (np.datetime64(most_recent_date) - np.timedelta64(365, 'D')).astype(str)

    # Find the most active station
    most_active_station = session.query(measurement.station)\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station).desc())\
        .first()[0]

    # Query temperature observations
    results = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.date >= year_before)\
        .filter(measurement.station == most_active_station).all()
    
    session.close()

    # Convert to list of dictionaries
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in results]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    session = Session(engine)

    # If no end date is provided, get data from start date onward
    if not end:
        results = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)
        ).filter(measurement.date >= start).all()
    else:
        # If both start and end dates are provided, filter between them
        results = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)
        ).filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    # Convert query results into dictionary
    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temp_data)

#Run the API
if __name__ == '__main__':
    app.run(debug=True)
