from os import getenv


class EnvVarNotSuppliedException(Exception):
    pass


class EnvReader():
    vars = {}

    def __init__(self, *args):

        missing_vars = []

        for arg in args:

            value = getenv(arg)

            if not value:

                missing_vars.append(arg)

            self.vars[arg] = value

        if missing_vars:
            raise EnvVarNotSuppliedException(f'{missing_vars} not supplied')

    def get_var(self, var_name: str) -> dict:
        return self.vars[var_name]
