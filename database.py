import mysql.connector
from config import DB_CONFIG
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# Kết nối MySQL
def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["MYSQL"]["host"],
        user=DB_CONFIG["MYSQL"]["user"],
        password=DB_CONFIG["MYSQL"]["password"],
        database=DB_CONFIG["MYSQL"]["database"]
    )