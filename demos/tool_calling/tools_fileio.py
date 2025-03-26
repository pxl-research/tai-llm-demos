import datetime
import os
import shutil
import stat

from dotenv import load_dotenv

load_dotenv()

allowed_folder = os.getenv("ALLOWED_FOLDER", "./")


def list_files(folder_path: str):
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


def read_file_contents(file_path: str):
    if is_within_folder(file_path, allowed_folder):
        if os.path.exists(file_path):
            with open(file_path, 'rt') as fp_read:
                contents = fp_read.read()
                return contents
    return None


def write_file_contents(file_path: str, content: str = '') -> bool:
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


def append_file_contents(file_path: str, content: str = '') -> bool:
    if is_within_folder(file_path, allowed_folder):
        try:
            with open(file_path, 'at') as fp_write:
                fp_write.write('\n')
                fp_write.write(content)
            return True
        except Exception as e:
            print(f"Problem appending to {file_path}: {type(e).__name__} - {str(e)}")
            return False

    print(f'Writing to {file_path} is not allowed.')
    return False


def create_folders(folder_path: str) -> bool:
    if is_within_folder(folder_path, allowed_folder):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return True

    print(f'Writing to {folder_path} is not allowed.')
    return False


def get_fs_properties(path: str):
    if not os.path.exists(path):
        return None

    properties = {'full_path': os.path.abspath(path)}

    if os.path.isfile(path):
        properties['type'] = 'file'
    elif os.path.isdir(path):
        properties['type'] = 'directory'
    else:
        properties['type'] = 'other'  # e.g., symlink, device file

    try:
        properties['size'] = os.path.getsize(path)
    except OSError:
        properties['size'] = None  # handle cases where size is not available (e.g. a broken symlink)

    try:
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

    except OSError as e:
        print(f"Error getting extended properties: {e}")
        return properties  # Return basic properties even if extended ones fail

    return properties


# helper method
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


def delete_file(file_path: str):
    if is_within_folder(file_path, allowed_folder):
        os.remove(file_path)
        return True

    print(f'Removing {file_path} is not allowed.')
    return False


def delete_folder(folder_path: str):
    if is_within_folder(folder_path, allowed_folder):
        shutil.rmtree(folder_path)
        return True

    print(f'Removing {folder_path} is not allowed.')
    return False
