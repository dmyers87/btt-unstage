from lib.cli import is_dry_run
from os import getenv
import mysql.connector as mysql

DB_HOST = getenv('DB_HOST') 
if not DB_HOST:
    raise Exception("DB_HOST required")

DB_USER = "root"
DB_PWD = "DXtUqdOg5L"

def delete_db(db_name: str):
    db = mysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PWD
    )

    if is_dry_run():
        print(f'dry run: db conection valid, would be deleting database {db_name}')
    else:
        sql = db.cursor()

        sql.execute(f'SHOW DATABASES LIKE \'{db_name}\'')        
        existing_db = sql.fetchone()

        if existing_db is None:
            print('no database to delete!')
        else:
            print(f'dropping database {db_name}')
            sql.execute(f'DROP DATABASE {db_name}')
        
        print(f'dropping database user if exists')
        sql.execute(f'DROP USER IF EXISTS {db_name}')

        sql.close()
    db.close()