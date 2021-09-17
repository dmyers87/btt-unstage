from os import getenv


class EnvVarNotSuppliedException(Exception):
    pass


class EnvReader():
    vars = {}

    def __init__(self, *args):

        for arg in args:

            value = getenv(arg)

            if not value:
                raise EnvVarNotSuppliedException(f'{arg} not supplied')

            self.vars[arg] = value

    def get_var(self, var_name: str) -> dict:
        return self.vars[var_name]
