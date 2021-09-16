from lib.cli import is_dry_run
from os import getenv
import mysql.connector as mysql


DB_HOST = getenv('DB_HOST') 
if not DB_HOST:
    raise Exception("DB_HOST required")

DB_USER = "root"
DB_PWD = "DXtUqdOg5L"

def get_db_connection() -> mysql.MySQLConnection:
    return mysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PWD
    )


def delete_db(db_name: str, db_connection: mysql.MySQLConnection):

    if is_dry_run():
        print(f'dry run: db conection valid, would be deleting database {db_name}')
    else:
        sql = db_connection.cursor()

        sql.execute(f'SHOW DATABASES LIKE \'{db_name}\'')        
        existing_db = sql.fetchone()

        if existing_db is None:
            raise Exception("NO DATABASE")

        sql.execute(f'DROP DATABASE {db_name}')
        sql.execute(f'DROP USER IF EXISTS {db_name}')
                
        sql.close()