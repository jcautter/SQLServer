import pyodbc
import numpy as np
import pandas as pd

class SQLServer:
    
    string_connection_parts = {
        'driver': "DRIVER={SQL Server Native Client 11.0}"
        , 'server': "Server={dns}"
        , 'data_base': "Database={database_name}"
        , 'trusted_connection': "Trusted_Connection=yes"
        , 'port': "Port={port_number}"
        , 'user_id': "User ID={user_id}"
        , 'password': "Password={password}"
    }
    
    dns = None
    database_name = None
    port_number = None
    user_id = None
    password = None
    
    conn = None
    cur = None
    
    def __init__(self, dns, database_name, port_number=None, user_id=None, password=None):
        self.dns = dns
        self.database_name = database_name
        self.port_number = port_number
        self.user_id = user_id
        self.password = password
    
    def build_string_connection(self, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        if not dns:
            dns = self.dns
        if not database_name:
            database_name = self.database_name
        if not port_number:
            port_number = self.port_number
        if not user_id:
            user_id = self.user_id
        if not password:
            password = self.password
        
        str_conn_part = [
            self.string_connection_parts['driver']
            , self.string_connection_parts['server'].format(dns=dns)
            , self.string_connection_parts['data_base'].format(database_name=database_name)
        ]
        if port_number:
            str_conn_part.append(self.string_connection_parts['port'].format(port_number=port_number))
        if user_id and password:
            str_conn_part.append(self.string_connection_parts['user_id'].format(user_id=user_id))
            str_conn_part.append(self.string_connection_parts['password'].format(password=password))
        else:
            str_conn_part.append(self.string_connection_parts['trusted_connection'])
            
        return ';'.join(str_conn_part)
    
    def connection(self, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        self.conn = pyodbc.connect(
            self.build_string_connection(
                dns, database_name, port_number, user_id, password
            )
        )
        
    def check_connection(self, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        if not self.conn:
            self.connection(dns, database_name, port_number, user_id, password)
            
    def get_cursor(self, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        self.check_connection(dns, database_name, port_number, user_id, password)
        self.cur = self.conn.cursor()
        
    def check_cursor(self, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        if not self.cur:
            self.get_cursor(dns, database_name, port_number, user_id, password)
            
    def execute_query(self, query, commit=False, dns=None, database_name=None, port_number=None, user_id=None, password=None):          
        self.check_cursor(dns, database_name, port_number, user_id, password)
        res = self.cur.execute(query)
        if commit:
            self.commit()
            self.close()
        return res
    
    def select(self, query, frame=True, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        resp = self.execute_query(query, False, dns, database_name, port_number, user_id, password)
        if frame:
            df = self.to_frame(resp)
            self.close()
            return df
        else:
            return resp
    
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        self.conn = None
        self.cur = None
        
    def to_frame(self, resp):
        result = resp.fetchall()
        return pd.DataFrame(
            [list(l) for l in result]
            , columns = np.array(resp.description)[:,0]
        )
    
    def insert_many(self, sql, parms, dns=None, database_name=None, port_number=None, user_id=None, password=None):
        self.check_cursor(dns, database_name, port_number, user_id, password)
        self.cur.fast_executemany = True
        res = self.cur.executemany(sql, parms)
        self.commit()
        self.close()
