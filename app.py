import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
#Database Setup 
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Temperature from Start Date: /api/v1.0/&lt;start&gt;<br/>"
        f"Temperature from Start to End Dates: /api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values
    results = session.query(measurement.date, measurement.prcp).\
                order_by(measurement.date).all()

    session.close()

    # Jsonify results using date as the key and prcp as the value.
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(station.station, station.name).all()

    session.close()

    # Jsonify the list of stations
    station_name = []
    for stations,name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_name.append(station_dict)
 
    return jsonify(station_name)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get the most active station 
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
                        group_by(measurement.station).\
                        order_by(func.count(measurement.station).desc()).all()
    
    most_active_station = active_stations.station[0]

    # Get the last date contained in the dataset and date from one year ago
    most_recent_date = session.query(measurement.date).\
                     order_by(measurement.date.desc()).first()
    last_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Query for the dates and temperature values
    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.date >= last_year).\
                filter(measurement.station == most_active_station). all()

    session.close()

    # Convert to list of dictionaries to jsonify
    dates_tobs_list = []
    for date, tobs in results:
        new_dict = {}
        new_dict["Date"]= date
        new_dict["Temperature Obs"] = tobs
        dates_tobs_list.append(new_dict)

    return jsonify(dates_tobs_list)

@app.route("/api/v1.0/<start>")
def temp_range(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), \
                func.avg(measurement.tobs), \
                func.max(measurement.tobs)).\
                filter(measurement.date >= start).\
                group_by(measurement.date).all()

    session.close()   

    # Convert to list of dictionaries to jsonify
    return_list = []
    for min, avg, max in results:
        new_dict = {}
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), \
                func.avg(measurement.tobs), \
                func.max(measurement.tobs)).\
                filter(and_(measurement.date >= start, measurement.date <= end)).\
                group_by(measurement.date).all()

     session.close()  

    # Convert to list of dictionaries to jsonify
    return_list = []
    for min, avg, max in results:
        new_dict = {}
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)
