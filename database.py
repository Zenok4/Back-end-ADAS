import mysql.connector
from config import DB_CONFIG
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL


db = SQLAlchemy()

# Tạo url đến Database
def get_db_url():
    return URL.create(
        "mysql+pymysql",
        username=DB_CONFIG["MYSQL"]["user"],
        password=DB_CONFIG["MYSQL"]["password"],
        host=DB_CONFIG["MYSQL"]["host"],
        port=DB_CONFIG["MYSQL"]["port"],
        database=DB_CONFIG["MYSQL"]["database"],
        query={"charset": "utf8mb4"},
    )

# Kết nối MySQL
def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["MYSQL"]["host"],
        port=DB_CONFIG["MYSQL"]["port"],
        user=DB_CONFIG["MYSQL"]["user"],
        password=DB_CONFIG["MYSQL"]["password"],
        database=DB_CONFIG["MYSQL"]["database"]
    )
