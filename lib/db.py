import mysql.connector as mysql


class NoDatabaseException(Exception):
    pass


class DBHelper():

    def __init__(self, db_host, db_user, db_pw, dry_run=True):

        self.db_host = db_host
        self.db_user = db_user
        self.db_pw = db_pw
        self.dry_run = dry_run

        self.db_connection = self.create_db_connection(
            self.db_host, self.db_user, self.db_pw)

    def get_db_connection(self):
        return self.db_connection

    def create_db_connection(self, host, user, password) -> mysql.MySQLConnection:

        return mysql.connect(
            host=host,
            user=user,
            passwd=password
        )

    def delete_db(self, db_name: str, db_connection: mysql.MySQLConnection):

        if not self.dry_run:

            sql = self.db_connection.cursor()

            sql.execute(f'SHOW DATABASES LIKE \'{db_name}\'')

            if not sql.fetchone():
                raise NoDatabaseException()

            sql.execute(f'DROP DATABASE {db_name}')
            sql.execute(f'DROP USER IF EXISTS {db_name}')
            sql.close()

            return True

        return False
