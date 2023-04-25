import io
import logging
import monitor_server as ms
from base64 import b64encode
from threading import Thread
from sensor_status import SensorDatabase
from flask import Flask, request, render_template, redirect, url_for

logging.disable(logging.DEBUG)
app = Flask(__name__) 

server_database = SensorDatabase()
monitor_server = ms.MonitorServer(server_database)

#ALL TOGETHER
@app.route('/home',methods = ['POST', 'GET'])
def home():
    sensor_info = monitor_server.get_all_sensor_stats()
    return render_template("index.html",sensor_info = sensor_info)


#DISPLAY SENSOR DATA
@app.route("/sensor_data",methods = ['GET'])
def send_sensor_info():
    sensor_info = monitor_server.get_all_sensor_stats()
    return render_template("sensor_table.html",sensor_info = sensor_info)

# SELECT SENSOR
@app.route("/choose_stream", methods=["GET", 'POST']) 
def choose_stream(): 
    selected_id = request.form.get('sensor_id_selected')
    if selected_id is not None:
        monitor_server.make_request_from_client(int(selected_id), ms.SEND_REQUEST)
    
    sensor_info = monitor_server.get_all_sensor_stats()
    return render_template("index.html",sensor_info = sensor_info)

# RENDERING IMAGE
@app.route("/render_stream", methods=["GET"]) 
def render_stream():
    original_image = monitor_server.get_monitor_image()
    file_object = io.BytesIO(original_image)
    base64img = "data:image/png;base64," + b64encode(file_object.getvalue()).decode('ascii')
    return render_template("image-box.html", image = base64img, )
    


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
    return render_template("login.html", error=error)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":

    server_process = Thread(target=monitor_server.run_info_server, daemon=True)
    server_process.start()
    
    app.run(debug = True,use_reloader=False)