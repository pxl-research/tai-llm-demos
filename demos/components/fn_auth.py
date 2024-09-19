import base64

import bcrypt

DEFAULT_PASSWD_FILE = '.passwd'
default_encoding = 'utf-8'


def auth_method(username, password, users_file=DEFAULT_PASSWD_FILE):
    encoded_username = encode_64(username)
    log_file = open(users_file, "r")
    users_list = log_file.read().splitlines()
    for user in users_list:
        if user.startswith(encoded_username):
            stored_password = user.split(f"{encoded_username}|")[1]
            return bc_check_string(password, stored_password)

    return False


def add_user(username, password, users_file=DEFAULT_PASSWD_FILE):
    encoded_username = encode_64(username.strip())
    hashed_password = bc_hash_string(password.strip())
    user_line = f"{encoded_username}|{hashed_password}\n"
    log_file = open(users_file, "a")
    log_file.write(user_line)
    log_file.close()


def list_all_users(users_file=DEFAULT_PASSWD_FILE):
    log_file = open(users_file, "r")
    user_lines = log_file.read().splitlines()

    user_list = []
    for entry in user_lines:
        user_enc = entry.split('|')[0]
        username = decode_64(user_enc)
        user_list.append(username)
    return user_list


# UTILITY METHODS

def bc_hash_string(string):
    byte_string = string.encode(default_encoding)
    salt = bcrypt.gensalt()
    hashed_byte_string = bcrypt.hashpw(byte_string, salt)
    return hashed_byte_string.decode(default_encoding)


def bc_check_string(string, stored_hash):
    byte_string = string.encode(default_encoding)
    stored_hash_bytes = stored_hash.encode(default_encoding)
    return bcrypt.checkpw(byte_string, stored_hash_bytes)


def encode_64(string):
    byte_string = string.encode(default_encoding)
    encoded_bytes = base64.b64encode(byte_string)
    return encoded_bytes.decode(default_encoding)


def decode_64(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes.decode(default_encoding)

# Uncomment this line to manually add a user:
# add_user("pxl", "YQhPEN826TJ4uey9sjDKWt")
