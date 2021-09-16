from lib.env import in_cluster

import mysql.connector as mysql

DEV_GCP_DB_HOST = '35.226.23.238'
DB_USER = "root"
DB_PWD = "DXtUqdOg5L"

def delete_db(db_name: str):
    db = mysql.connect(
        host=DEV_GCP_DB_HOST,
        user=DB_USER,
        passwd=DB_PWD
    )

    if in_cluster():
        sql = db.cursor()
        sql.execute(f'DROP DATABASE IF EXISTS {db_name}')
        sql.execute(f'DROP USER IF EXISTS {db_name}')
        sql.close()
    else:
        print(f'test, would be deleting database {db_name}')

    db.close()