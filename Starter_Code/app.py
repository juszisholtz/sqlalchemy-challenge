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
        f'Available Routes: "/"'
        f'For the most recent 12 months of precipitation data: ""/api/v1.0/precipitation""'
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
@app.route()

#Run the API
if __name__ == '__main__':
    app.run(debug=True)
