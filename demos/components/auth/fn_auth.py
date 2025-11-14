import base64

import bcrypt

DEFAULT_PASSWD_FILE = '.passwd'  # Path to user credentials file
DEFAULT_ENCODING = 'utf-8'  # Encoding used for all string operations


def auth_method(username: str, password: str, users_file: str = DEFAULT_PASSWD_FILE) -> bool:
    """
    Authenticate user by checking username and password against stored credentials.
    Returns True if credentials match, else False.
    """
    encoded_username = encode_64(username)
    users_list = []
    with open(users_file, 'r') as log_file:
        users_list = log_file.read().splitlines()
    for user in users_list:
        if user.startswith(encoded_username):
            stored_password = user.split(f'{encoded_username}|')[1]
            return bc_check_string(password, stored_password)
    return False


def add_user(username: str, password: str, users_file: str = DEFAULT_PASSWD_FILE) -> None:
    """
    Add a new user with hashed password to the credentials file.
    """
    encoded_username = encode_64(username.strip())
    hashed_password = bc_hash_string(password.strip())
    user_line = f'{encoded_username}|{hashed_password}\n'
    with open(users_file, 'a') as log_file:
        log_file.write(user_line)


def list_all_users(users_file: str = DEFAULT_PASSWD_FILE) -> list[str]:
    """
    Return a list of all decoded usernames in the credentials file.
    """
    with open(users_file, 'r') as log_file:
        user_lines = log_file.read().splitlines()

    user_list = []
    for entry in user_lines:
        user_enc = entry.split('|')[0]
        username = decode_64(user_enc)
        user_list.append(username)
    return user_list


def remove_user_on_line(line_number: int, users_file: str = DEFAULT_PASSWD_FILE) -> str:
    """
    Remove user at the given line number from the credentials file.
    Returns the removed line.
    """
    with open(users_file, 'r') as log_file:
        users_list = log_file.read().splitlines()
    selected_line = users_list.pop(line_number)
    with open(users_file, 'wt') as log_file:
        for user_line in users_list:
            log_file.write(f'{user_line}\n')
    return selected_line


# UTILITY METHODS

def bc_hash_string(string: str) -> str:
    """
    Hash a string using bcrypt and return the hash.
    """
    byte_string = string.encode(DEFAULT_ENCODING)
    salt = bcrypt.gensalt()
    hashed_byte_string = bcrypt.hashpw(byte_string, salt)
    return hashed_byte_string.decode(DEFAULT_ENCODING)


def bc_check_string(string: str, stored_hash: str) -> bool:
    """
    Check if a string matches the given bcrypt hash.
    """
    byte_string = string.encode(DEFAULT_ENCODING)
    stored_hash_bytes = stored_hash.encode(DEFAULT_ENCODING)
    return bcrypt.checkpw(byte_string, stored_hash_bytes)


def encode_64(string: str) -> str:
    """
    Encode a string to base64.
    """
    byte_string = string.encode(DEFAULT_ENCODING)
    encoded_bytes = base64.b64encode(byte_string)
    return encoded_bytes.decode(DEFAULT_ENCODING)


def decode_64(encoded_string: str) -> str:
    """
    Decode a base64-encoded string.
    """
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes.decode(DEFAULT_ENCODING)

# Uncomment this line to manually add a user:
# add_user('pxl', 'YQhPEN826TJ4uey9sjDKWt')
