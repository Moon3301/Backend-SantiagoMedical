import string
import random
from werkzeug.security import generate_password_hash, check_password_hash

def generar_codigo(password):
    pass_hash = generate_password_hash(password)

    print(f'Password: {pass_hash}')
    return pass_hash


generar_codigo('1234')