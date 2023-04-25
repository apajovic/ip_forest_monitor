import sqlite3


class DbControl():
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.tables = []

    def create_table(self, name, cols):
        sql = f"CREATE TABLE IF NOT EXISTS {name} (" + ','.join(cols) + ');'
        c = self.conn.cursor()
        c.execute(sql)
        self.tables.append(name)

    def get_tables(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [x[0] for x in c.fetchall()] #fetchall returns a weird format

    def insert_into_table(self, table_name, value:float):

        sql = f'INSERT INTO {table_name} VALUES(' + ("?,"*len(value))[:-1] +')'
        c = self.conn.cursor()
        c.execute(sql, value)
        self.conn.commit()

    def update_row(self, table_name, row_name, row_value,  **columns):  
        sql = f"UPDATE {table_name} \nSET "
        for key in columns:
            sql+=f"{key} = {columns[key]},\n"
        sql=sql[:-2]
        sql +=f" \nWHERE {row_name} = \'{row_value}\'\n"
        print(sql)

        c = self.conn.cursor()
        c.execute(sql)
        self.conn.commit()

    def get_all(self, table_name):
        sql = f'SELECT * FROM {table_name}'
        c = self.conn.cursor()
        c.execute(sql)
        return c.fetchall()

    
if __name__ == '__main__':
    dbc = DbControl('./sensor_database.db')
    #print(dbc.get_tables())                                    

    #dbc = DbControl('./tst.db')
    dbc.create_table("RegisteredSensors", ["SensorID", "Address"])
    dbc.insert_into_table("RegisteredSensors", (7, "127.0.0.1:400"))
    rows = dbc.get_all("RegisteredSensors")
    for r in rows:
        print(r)