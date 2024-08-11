import mysql.connector
import os
from dotenv import load_dotenv

class Query:
    _instance = None

    def __new__(cls, pool_name="arcaea", pool_size=5):
        if cls._instance is None:
            load_dotenv()
            PWD = os.getenv('PASSWORD')
            cls._instance = super(Query, cls).__new__(cls)
            cls._instance.dbconfig = {
                "host": "localhost",
                "user": "discordbot",
                "password": PWD,
                "database": "arcaeaSongInfo"
            }
            cls._instance.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                **cls._instance.dbconfig
            )
        return cls._instance

    def execute(self, query, params=None):
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            conn.commit()
            return result
        except mysql.connector.Error as e:
            print(f"Error in SQL: {str(e)}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()