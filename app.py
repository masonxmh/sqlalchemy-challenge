import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from collections import defaultdict
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
 # define date
last_date='2017-08-23'
year_ago_last_date = dt.datetime.strptime(last_date,"%Y-%m-%d")-dt.timedelta(365)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
        
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   

    # Query all precipitation
    results = session.query( Measurement.date,Measurement.station, Measurement.prcp).\
        order_by(Measurement.date).all()
    
    session.close()

    prcp_dict={}
    for i in range(len(results)):
        if results[i][0] == results[i-1][0]:
            prcp_dict[results[i-1][0]][results[i][1]]=results[i][2]
        else:
            prcp_dict[results[i][0]]={}
            prcp_dict[results[i][0]][results[i][1]]=results[i][2]
    

    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    results = session.query(Station.station, Station.name).\
        group_by(Station.station).all()

    session.close()
    # Create a dictionary from the row data and append to a list of stations
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["Name"] = name
        station_data.append(station_dict)

    return jsonify(station_data)



@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    most_act_station=session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_act_station[0]).\
        filter(Measurement.date >= year_ago_last_date).\
        filter(Measurement.date <= last_date).\
        order_by(Measurement.date).all()
    
    session.close()

    tobs_data = []
    for d, temp in results:
        tobs_dict = {}
        tobs_dict["date"] = d
        tobs_dict["tobs"] = temp
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)



@app.route("/api/v1.0/<date>")
def temperature_s(date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
       
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date).\
        filter(Measurement.date <= last_date).all()

    session.close()

    start_tobs_dict = {}
    for s_tob_min,s_tob_ave,s_tob_max in results:
        
        start_tobs_dict["Minimum Temp"] = s_tob_min
        start_tobs_dict["Average Temp"] = s_tob_ave
        start_tobs_dict["Maximum Temp"] = s_tob_max
       

    return jsonify(start_tobs_dict)



@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
       
    def calc_temps(start_date,end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
    
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        
        Returns:
            TMIN, TAVE, and TMAX
        """
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

    results = calc_temps(start,end)

    session.close()
    
    start_end_data=[]
    for se_tobs_min, se_tobs_ave, se_tobs_max in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["Minimum Temperature"] = se_tobs_min
        start_end_tobs_dict["Average Temperature"] = se_tobs_ave
        start_end_tobs_dict["Maximum Temperature"] = se_tobs_max
        start_end_data.append(start_end_tobs_dict)
    
    return jsonify(start_end_data)
    

if __name__ == '__main__':
    app.run(debug=True)
