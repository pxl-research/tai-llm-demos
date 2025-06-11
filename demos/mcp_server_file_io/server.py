import datetime
import os
import shutil
import stat

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

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
def list_files(folder_path: str):
    """Lists the files in a folder."""
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
def read_file_contents(file_path: str):
    """Reads the contents of a file."""
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
def write_file_contents(file_path: str, content: str = ''):
    """Writes content to a file."""
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
def append_file_contents(file_path: str, content: str = ''):
    """Appends content to a file."""
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
def create_folders(folder_path: str):
    """Creates a folder."""
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
def get_fs_properties(path: str):
    """Gets file system properties of a file or folder."""
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
def delete_file(file_path: str):
    """Deletes a file."""
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
def replace_in_file(file_path: str, search_string: str, replace_string: str):
    """Replaces a string in a file."""
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