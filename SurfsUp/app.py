# Import Flask
import numpy as np
import datetime as dt

# Import SQLAlchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask dependencies
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement 
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

    )
@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation analysis data as json list"""
    # Query all passengers
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year).all()

    # Close session
    session.close()

    # Create a dictionary from the precipitation analysis, append to a list of prcp_analysis
    prcp_analysis = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_analysis.append(prcp_dict)

    return jsonify(prcp_analysis)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations"""

    # Query for list of stations
    station_list = session.query(station.name, station.station).all()


    # Close session
    session.close()

    # Convert list of stations into normal list
    all_stations = list(np.ravel(station_list))
    
    return jsonify(all_stations) 

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json list of temperature observations for the previous year"""

    # Find most recent date from dataset and calculate a year from it 
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    date_limit = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for list of dates and temperatures observations of the most active station for the previous year of data
    previous_year_act_station = session.query(measurement.station, func.count(measurement.id)).\
    group_by(measurement.station).\
        filter(measurement.date >= date_limit).\
            order_by(func.count(measurement.id).desc()).first()
    
    # Use results from the previous query to print the tobs for last year
    tobs_previous_year_act_station = session.query(measurement.tobs).\
    filter(measurement.station == previous_year_act_station[0]).\
        filter(measurement.date >= date_limit).all()
    
    # Close session
    session.close()
    
    # Convert list of tobs for last year into normal list
    all_tobs = list(np.ravel(tobs_previous_year_act_station))
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def date_in_measurement(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json list of the minimum temperature, the average temperature, and the maximum temperature for a specified start"""

    dt_object = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the minimum, average and maximum temperatures in measurement class that is equal to or greater than the specified start
    # Create labels that will represent the different temperatures which will be used for converting the tuple into a dictionary
    temps = [func.min(measurement.tobs).label("tmin"),
            func.avg(measurement.tobs).label("tavg"),
            func.max(measurement.tobs).label("tmax")]
    print(dt_object)
    tobs_start_date = session.query(measurement.date, *temps).group_by(measurement.date).filter(measurement.date >= dt_object).all()

    # Convert previous tuple into dictionary for the dates equal to or greater than the start date
    tobs_start_date_dict = dict()
    for measurement.date, tmin, tavg, tmax in tobs_start_date:
        tobs_start_date_dict.setdefault(measurement.date, []).append(tmin)
        tobs_start_date_dict.setdefault(measurement.date, []).append(tavg)
        tobs_start_date_dict.setdefault(measurement.date, []).append(tmax)

    # Close session
    session.close()

    return jsonify(tobs_start_date_dict)

@app.route("/api/v1.0/<start>/<end>")
def date_in_measurement_se(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json list of the minimum temperature, the average temperature, and the maximum temperature for specific data range"""

    dt_object = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dt_object_2 = dt.date(2017, 8, 23)
    dt_start = dt.datetime.strptime(dt_object, '%Y-%m-%d')
    dt_end = dt.datetime.strptime(dt_object_2, '%Y-%m-%d') 

    # Query for the minimum, average and maximum temperatures in measurement class that is equal to or greater than the specified start
    # Create labels that will represent the different temperatures which will be used for converting the tuple into a dictionary
    temps = [func.min(measurement.tobs).label("tmin"),
            func.avg(measurement.tobs).label("tavg"),
            func.max(measurement.tobs).label("tmax")]
    
    tobs_specific_date_range = session.query(measurement.date, *temps).group_by(measurement.date).\
        filter(measurement.date >= dt.start).\
            filter(measurement.date <= dt_end).all()
    
    # Convert previous tuple into dictionary for the dates equal to or greater than the start date
    tobs_specific_date_range_dict = dict()
    for measurement.date, tmin, tavg, tmax in tobs_specific_date_range:
        tobs_specific_date_range_dict.setdefault(measurement.date, []).append(tmin)
        tobs_specific_date_range_dict.setdefault(measurement.date, []).append(tavg)
        tobs_specific_date_range_dict.setdefault(measurement.date, []).append(tmax)

    # Closing session
    session.close()

    return jsonify(tobs_specific_date_range_dict)


if __name__ == '__main__':
    app.run(debug=True)
