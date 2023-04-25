import time
import json
from threading import Lock
from dbcontrol import DbControl


class SensorStatus():
    def __init__(self, sensor_id, timestamp=time.time(), status=0, is_sending_image=0):
        #dict.__init__(self, sensor_id, timestamp, status)
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.status = status
        self.is_sending_image = is_sending_image
    
    def __dict__(self):
        return {"sensor_id":self.sensor_id,
                "timestamp":self.timestamp,
                "status":self.status,
                "is_sending_image":self.is_sending_image}


class Singleton(type):
    _instances = {}
    _lock: Lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SensorDatabase(metaclass=Singleton):
    
    _data_info_lock = Lock()
    
    def __init__(self, database_path='./sensor_database.db') -> None:
        self._sensors={}
        self._dbc = DbControl(database_path)
        with self._data_info_lock:
            rows = self._dbc.get_all("RegisteredSensors")
            for data in rows: 
                self._sensors[data[0]] = SensorStatus(data[0], 'offline')
    
    
    def parse_status(self, info):
        if info == "":
            raise Exception("Message was empty") 
            
        if (type(info)==str): 
            info = info.replace("\'", "\"")
            info = json.loads(info)
        
        new_status = SensorStatus(**info)
        if new_status.sensor_id not in self._sensors:
            self.registerSensor(new_status.sensor_id)
        
        with self._data_info_lock:         
            self._sensors[new_status.sensor_id] = new_status
        return new_status
        
    @staticmethod
    def to_json(_sensors:dict):
        json_dict = {}
        for k, info in _sensors.items():
            json_dict[k] = info.__dict__()
        
        return json_dict

    def get_all_sensor_stats(self):       
        with self._data_info_lock:         
            return self.to_json(self._sensors)

    def stop_all_sending(self):
        for _, sens in self._sensors.items(): 
            sens.is_sending_image = 0 
        

    def registerSensor(self, sensor_id):
        if sensor_id not in self._sensors:
            with self._data_info_lock:         
                self._sensors[sensor_id] = SensorStatus(sensor_id)
                self._dbc.insert_into_table("RegisteredSensors", (sensor_id, "127.0.0.1:400"))

