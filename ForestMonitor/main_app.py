import io
import logging
import monitor.server as ms
from base64 import b64encode
from threading import Thread
from lib.sensor_status import SensorService
import flask
from flask import Flask, request, render_template, redirect, url_for

logging.disable(logging.DEBUG)
app = Flask(__name__) 

sensor_service = SensorService()
monitor_server = ms.MonitorServer(sensor_service)

@app.route('/home',methods = ['GET'])
def home():
    sensor_info = monitor_server.get_all_sensor_stats()
    return render_template("index.html",sensor_info = sensor_info)


@app.route("/sensor_data",methods = ['GET'])
def send_all_sensor_info():
    response = flask.jsonify(monitor_server.get_all_sensor_stats())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/sensor_data/<sensor_id>",methods = ['GET'])
def send_sensor_info(sensor_id):
    return monitor_server.get_sensor_stats(sensor_id), 200
    
# SELECT SENSOR
@app.route("/choose_stream", methods=["GET"]) 
def choose_stream(): 
    
    command_params = dict(request.args)
    selected_id = command_params.get("id")
    if selected_id is not None:
        monitor_server.make_request_from_client(int(selected_id), ms.SEND_REQUEST)
    
    response = flask.jsonify({"status":"accepted"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

# RENDERING IMAGE
@app.route("/render_stream", methods=["GET"]) 
def render_stream():
    original_image = monitor_server.get_monitor_image()
    file_object = io.BytesIO(original_image)
    
    return  "data:image/png;base64," + b64encode(file_object.getvalue()).decode('ascii')
    


# REDIRECT TO LOGIN
@app.route('/')
def base():
    return redirect(url_for('login'))

# LOGIN SCREEN 
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get('username') != 'admin' or request.form.get('password') != 'admin':
            error = "Invalid Credentials, pleas try again"
        else:
            return redirect(url_for("home"))
    return render_template("main/login.html", error=error)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('main/404.html'), 404

if __name__ == "__main__":

    server_process = Thread(target=monitor_server.run_info_server, daemon=True)
    server_process.start()
    
    app.run(debug = True,use_reloader=False)