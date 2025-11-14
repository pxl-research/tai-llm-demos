import os
import re


def clean_up_string(string: str) -> str:
    """
    Normalize and sanitize a string: lowercase, replace underscores with dashes,
    keep only a-z, 0-9, spaces, and dashes, then convert spaces to dashes.
    """
    string = string.lower()
    string = string.replace('_', '-')
    string = re.sub(r'[^a-z0-9 -]+', ' ', string)  # keep only a-z 0-9 and space
    string = string.lstrip(' ')  # remove leading spaces
    return string.replace(' ', '-')


def sanitize_filename(full_file_path: str) -> str:
    """
    Create a safe filename from a file path: remove path and extension,
    sanitize, and crop to 60 characters.
    """
    cleaner_name = os.path.basename(full_file_path)  # remove path
    cleaner_name = os.path.splitext(cleaner_name)[0]  # remove extension
    cleaner_name = clean_up_string(cleaner_name)
    return cleaner_name[:60]  # crop it
