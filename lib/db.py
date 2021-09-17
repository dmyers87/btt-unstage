import mysql.connector as mysql


class NoDatabaseException(Exception):
    pass


class DBHelper():

    def __init__(self, host: str, user: str, pw: str, dry_run=True):

        self.host = host
        self.user = user
        self.pw = pw
        self.dry_run = dry_run

        self.connection = self.create_connection(
            self.host, self.user, self.pw)

    def get_connection(self):
        return self.connection

    def create_connection(self, host: str, user: str, password: str) -> mysql.MySQLConnection:

        return mysql.connect(
            host=host,
            user=user,
            passwd=password
        )

    def delete_db(self, name: str):

        if not self.dry_run:

            sql = self.connection.cursor()

            sql.execute(f'SHOW DATABASES LIKE \'{name}\'')

            if not sql.fetchone():
                raise NoDatabaseException()

            sql.execute(f'DROP DATABASE {name}')
            sql.execute(f'DROP USER IF EXISTS {name}')
            sql.close()

            return True

        return False
