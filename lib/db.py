from lib.cli import is_dry_run
from lib.env import get_env_var
import mysql.connector as mysql

DB_HOST = get_env_var('DB_HOST') 
DB_USER = "root"
DB_PWD = "DXtUqdOg5L"

class NoDatabaseException(Exception):
    pass

def create_db_connection() -> mysql.MySQLConnection:
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
            raise NoDatabaseException()

        sql.execute(f'DROP DATABASE {db_name}')
        sql.execute(f'DROP USER IF EXISTS {db_name}')
                
        sql.close()


    