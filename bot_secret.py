'''Secret functions tools'''
import random
import string
import bot_settings

_letters = string.ascii_lowercase + string.ascii_uppercase + string.digits


def generate_hash(sym_len: int = bot_settings.SECRET_HASH_LENGTH) -> str:
    '''Generate random string for getting secret'''
    return ''.join(random.choice(_letters) for i in range(sym_len))
