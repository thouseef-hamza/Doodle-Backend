import string
import random


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = "".join(random.choice(characters) for _ in range(length))
    return password
