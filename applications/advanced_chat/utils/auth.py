"""
Authentication module for Advanced Chat.
Self-contained authentication with bcrypt password hashing.
"""
import base64
import bcrypt
from pathlib import Path

from utils.config import AUTH_FILE

DEFAULT_ENCODING = 'utf-8'


# Core authentication functions (copied from components/auth/fn_auth.py for self-containment)

def bc_hash_string(string: str) -> str:
    """Hash a string using bcrypt and return the hash."""
    byte_string = string.encode(DEFAULT_ENCODING)
    salt = bcrypt.gensalt()
    hashed_byte_string = bcrypt.hashpw(byte_string, salt)
    return hashed_byte_string.decode(DEFAULT_ENCODING)


def bc_check_string(string: str, stored_hash: str) -> bool:
    """Check if a string matches the given bcrypt hash."""
    byte_string = string.encode(DEFAULT_ENCODING)
    stored_hash_bytes = stored_hash.encode(DEFAULT_ENCODING)
    return bcrypt.checkpw(byte_string, stored_hash_bytes)


def encode_64(string: str) -> str:
    """Encode a string to base64."""
    byte_string = string.encode(DEFAULT_ENCODING)
    encoded_bytes = base64.b64encode(byte_string)
    return encoded_bytes.decode(DEFAULT_ENCODING)


def decode_64(encoded_string: str) -> str:
    """Decode a base64-encoded string."""
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes.decode(DEFAULT_ENCODING)


def auth_method(username: str, password: str, users_file: str) -> bool:
    """
    Authenticate user by checking username and password against stored credentials.
    Returns True if credentials match, else False.
    """
    if not Path(users_file).exists():
        return False

    encoded_username = encode_64(username)
    with open(users_file, 'r') as log_file:
        users_list = log_file.read().splitlines()

    for user in users_list:
        if user.startswith(encoded_username):
            stored_password = user.split(f'{encoded_username}|')[1]
            return bc_check_string(password, stored_password)
    return False


def add_user(username: str, password: str, users_file: str) -> None:
    """Add a new user with hashed password to the credentials file."""
    encoded_username = encode_64(username.strip())
    hashed_password = bc_hash_string(password.strip())
    user_line = f'{encoded_username}|{hashed_password}\n'
    with open(users_file, 'a') as log_file:
        log_file.write(user_line)


def list_all_users(users_file: str) -> list[str]:
    """Return a list of all decoded usernames in the credentials file."""
    if not Path(users_file).exists():
        return []

    with open(users_file, 'r') as log_file:
        user_lines = log_file.read().splitlines()

    user_list = []
    for entry in user_lines:
        if '|' in entry:
            user_enc = entry.split('|')[0]
            username = decode_64(user_enc)
            user_list.append(username)
    return user_list


# Public API for application

def authenticate(username: str, password: str) -> bool:
    """
    Authenticate user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        True if authenticated, False otherwise
    """
    # Check if auth file exists
    if not AUTH_FILE.exists():
        # Create default user if no auth file exists
        _create_default_auth()

    return auth_method(username, password, str(AUTH_FILE))


def _create_default_auth():
    """Create default auth file with a test user."""
    # Create auth file with a default user (username: test, password: test)
    try:
        add_user('test', 'test', str(AUTH_FILE))
    except Exception as e:
        print(f"Warning: Could not create default auth: {e}")
        # Create empty auth file
        AUTH_FILE.touch(exist_ok=True)


def register_user(username: str, password: str) -> bool:
    """
    Register a new user.

    Args:
        username: Username
        password: Password

    Returns:
        True if registered, False if user already exists
    """
    if not AUTH_FILE.exists():
        AUTH_FILE.touch()

    # Check if user already exists
    existing_users = list_all_users(str(AUTH_FILE))
    if username in existing_users:
        return False

    try:
        add_user(username, password, str(AUTH_FILE))
        return True
    except Exception:
        return False


def get_all_users() -> list:
    """Get list of all users."""
    if not AUTH_FILE.exists():
        return []

    return list_all_users(str(AUTH_FILE))
