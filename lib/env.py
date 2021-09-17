from os import getenv

class EnvVarNotSuppliedException(Exception):
    pass

def get_env_var(var: str):
    env_var = getenv(var)
    if not env_var:
        raise EnvVarNotSuppliedException(f'{var} not supplied')
    return env_var
        


