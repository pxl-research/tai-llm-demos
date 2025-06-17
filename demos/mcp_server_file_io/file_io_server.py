import datetime
import os
import shutil
import stat

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Annotated # Add this import
from pydantic import Field # Add this import

load_dotenv()

allowed_folder = os.getenv("ALLOWED_FOLDER", "./")

# Create an MCP server
mcp = FastMCP("file_io_server")


# Helper function
def is_within_folder(path: str, folder_path: str) -> bool:
    try:
        # normalize paths
        inner_folder = os.path.realpath(path)
        outer_folder = os.path.realpath(folder_path)

        # check for common path
        common_path = os.path.commonpath([inner_folder, outer_folder])
        return common_path == outer_folder

    except ValueError:
        return False


@mcp.tool()
def list_files(
    folder_path: Annotated[
        str,
        Field(
            description="The absolute path to the folder to list. This path must be within the server's configured ALLOWED_FOLDER.",
            examples=["/path/to/your/allowed/folder/documents", "/data/backups"]
        )
    ]
):
    """Lists the files and directories within a specified folder.

    Returns:
        list[str]: A list of strings, where each string is the name of a file or directory in the folder. Returns None if the folder does not exist or is not accessible.
    """
    if is_within_folder(folder_path, allowed_folder):
        try:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                return os.listdir(folder_path)
            else:
                print(f"Folder does not exist or is not a directory: {folder_path}")
                return None
        except Exception as e:
            print(f"Problem listing files in {folder_path}: {type(e).__name__} - {str(e)}")
            return None
    return None


@mcp.tool()
def read_file_contents(
    file_path: Annotated[
        str,
        Field(
            description="The absolute path to the file to read. This path must be within the server's configured ALLOWED_FOLDER.",
            examples=["/path/to/your/allowed/folder/document.txt", "/data/logs/server.log"]
        )
    ]
):
    """Reads the entire contents of a file.

    Returns:
        str: The contents of the file as a string. Returns None if the file does not exist or cannot be read.
    """
    if is_within_folder(file_path, allowed_folder) and os.path.exists(file_path):
        try:
            with open(file_path, 'rt') as fp_read:
                contents = fp_read.read()
                return contents
        except Exception as e:
            print(f"Problem reading from {file_path}: {type(e).__name__} - {str(e)}")
            return None
    return None


@mcp.tool()
def write_file_contents(
    file_path: Annotated[
        str,
        Field(
            description="The absolute path to the file to write. Must be within the ALLOWED_FOLDER. If the file does not exist, it will be created. If it exists, its contents will be replaced.",
            examples=["/path/to/your/allowed/folder/new_file.txt"]
        )
    ],
    content: Annotated[
        str,
        Field(
            description="The content to write to the file. Defaults to an empty string.",
            examples=["Hello, world!", "This is some text."]
        )
    ] = ''
):
    """Writes content to a file, overwriting any existing content.

    Returns:
        bool: True if the write was successful, False otherwise.
    """
    if is_within_folder(file_path, allowed_folder):
        try:
            with open(file_path, 'wt') as fp_write:
                fp_write.write(content)
            return True
        except Exception as e:
            print(f"Problem writing to {file_path}: {type(e).__name__} - {str(e)}")
            return False

    print(f'Writing to {file_path} is not allowed.')
    return False


@mcp.tool()
def append_file_contents(
    file_path: Annotated[
        str,
        Field(
            description="The absolute path to the file to append to. Must be within the ALLOWED_FOLDER. If the file does not exist, it will be created.",
            examples=["/path/to/your/allowed/folder/log.txt"]
        )
    ],
    content: Annotated[
        str,
        Field(
            description="The content to append to the file. Defaults to an empty string.",
            examples=["New log entry.", "Another line of text."]
        )
    ] = ''
):
    """Appends content to the end of a file, adding a newline character after the appended content.

    Returns:
        bool: True if the append was successful, False otherwise.
    """
    if is_within_folder(file_path, allowed_folder):
        try:
            with open(file_path, 'at') as fp_write:
                fp_write.write(content)
                fp_write.write('\n')
            return True
        except Exception as e:
            print(f"Problem appending to {file_path}: {type(e).__name__} - {str(e)}")
            return False

    print(f'Writing to {file_path} is not allowed.')
    return False


@mcp.tool()
def create_folders(
    folder_path: Annotated[
        str,
        Field(
            description="The absolute path to the folder to create. Must be within the ALLOWED_FOLDER.",
            examples=["/path/to/your/allowed/folder/new_directory", "/data/backups/2025-01-01"]
        )
    ]
):
    """Creates a folder (or directory) at the specified path, including any necessary parent folders.

    Returns:
        bool: True if the folder creation was successful, False otherwise.
    """
    if is_within_folder(folder_path, allowed_folder):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return True
        except Exception as e:
            print(f"Problem creating folder {folder_path}: {type(e).__name__} - {str(e)}")
            return False

    print(f'Writing to {folder_path} is not allowed.')
    return False


@mcp.tool()
def get_fs_properties(
    path: Annotated[
        str,
        Field(
            description="The absolute path to the file or folder for which to retrieve properties.",
            examples=["/path/to/your/allowed/folder/document.txt", "/data/backups"]
        )
    ]
):
    """Gets file system properties of a file or folder, such as its type, size, modification date, and permissions.

    Returns:
        dict: A dictionary containing file system properties, or None if the path does not exist.
        The dictionary includes the following keys:
            - 'full_path' (str): The absolute path to the file or folder.
            - 'type' (str): 'file', 'directory', or 'other'.
            - 'size' (int): The size of the file in bytes (only for files).
            - 'last_modified' (str): The last modification time in 'YYYY-MM-DD HH:MM:S.ffffff' format (only for files).
            - 'last_accessed' (str): The last access time in 'YYYY-MM-DD HH:MM:S.ffffff' format (only for files).
            - 'creation_time' (str): The creation time in 'YYYY-MM-DD HH:MM:S.ffffff' format (only for files).
            - 'permissions' (str): The permissions string (e.g., 'drwxr-xr-x') (only for files).
            - 'uid' (int): The user ID (only for files).
            - 'gid' (int): The group ID (only for files).
    """
    if not os.path.exists(path):
        return None

    properties = {'full_path': os.path.abspath(path)}

    try:
        if os.path.isfile(path):
            properties['type'] = 'file'
            properties['size'] = os.path.getsize(path)
            stat_info = os.stat(path)
            # last modification time
            properties['last_modified'] = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            # last access time
            properties['last_accessed'] = datetime.datetime.fromtimestamp(stat_info.st_atime).strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            # creation time
            properties['creation_time'] = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            # permissions string (e.g., 'drwxr-xr-x')
            properties['permissions'] = stat.filemode(stat_info.st_mode)
            properties['uid'] = stat_info.st_uid  # user ID
            properties['gid'] = stat_info.st_gid  # group ID

        elif os.path.isdir(path):
            properties['type'] = 'directory'
        else:
            properties['type'] = 'other'  # e.g., symlink, device file
    except OSError as e:
        print(f"Error getting extended properties: {e}")
        return properties  # Return basic properties even if extended ones fail

    return properties


@mcp.tool()
def delete_file(
    file_path: Annotated[
        str,
        Field(
            description="The absolute path to the file to delete. Must be within the ALLOWED_FOLDER.",
            examples=["/path/to/your/allowed/folder/old_file.txt"]
        )
    ]
):
    """Deletes the file at the specified path.

    Returns:
        bool: True if the file deletion was successful, False otherwise.
    """
    if is_within_folder(file_path, allowed_folder):
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                return True
            else:
                print(f"File does not exist or is not a file: {file_path}")
                return False
        except Exception as e:
            print(f"Problem deleting file {file_path}: {type(e).__name__} - {str(e)}")
            return False

    print(f'Removing {file_path} is not allowed.')
    return False


@mcp.tool()
def replace_in_file(
    file_path: Annotated[
        str,
        Field(
            description="The absolute path to the file to modify. Must be within the ALLOWED_FOLDER.",
            examples=["/path/to/your/allowed/folder/config.ini"]
        )
    ],
    search_string: Annotated[
        str,
        Field(
            description="The string to search for.",
            examples=["old_value", "DEBUG=True"]
        )
    ],
    replace_string: Annotated[
        str,
        Field(
            description="The string to replace the search string with.",
            examples=["new_value", "DEBUG=False"]
        )
    ]
):
    """Replaces the first occurrence of a string in a file with another string.

    Returns:
        bool: True if the replacement was successful, False otherwise.
    """
    if is_within_folder(file_path, allowed_folder) and os.path.exists(file_path):
        try:
            with open(file_path, 'rt') as fp_read:
                contents = fp_read.read()

            modified_contents = contents.replace(search_string, replace_string, 1)

            with open(file_path, 'wt') as fp_write:
                fp_write.write(modified_contents)

            return True
        except Exception as e:
            print(f"Problem replacing in {file_path}: {type(e).__name__} - {str(e)}")
            return False
    print(f'Replacing in {file_path} is not allowed.')
    return False

if __name__ == "__main__":
    print('Initialize and run the server...')
    mcp.run(transport='stdio')
