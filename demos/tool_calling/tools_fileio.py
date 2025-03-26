import datetime
import os
import stat

allowed_folder = './'


def list_files(folder_path: str):
    return os.listdir(folder_path)


def read_file_contents(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'rt') as fp_read:
            contents = fp_read.read()
            return contents

    return None


def write_file_contents(file_path: str, content: str = ''):
    if is_within_folder(file_path, allowed_folder):
        with open(file_path, 'wt') as fp_write:
            fp_write.write(content)
        return True

    print(f'Writing to {file_path} is not allowed.')
    return False


def append_file_contents(file_path: str, content: str = ''):
    with open(file_path, 'at') as fp_write:
        fp_write.write('\n')
        fp_write.write(content)


def create_folders(folder_path: str):
    if is_within_folder(folder_path, allowed_folder):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return True

    print(f'Writing to {folder_path} is not allowed.')
    return False


def get_fs_properties(path):
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
def is_within_folder(path: str, folder_path: str):
    try:
        # normalize paths
        inner_folder = os.path.abspath(path)
        outer_folder = os.path.abspath(folder_path)

        # check for common path
        common_path = os.path.commonpath([inner_folder, outer_folder])
        return common_path == outer_folder

    except ValueError:
        return False


# "weather" demo
tools_fileio_descriptor = [{
    'type': 'function',
    'function': {
        'name': 'list_files',
        'description': 'List the contents of a folder',
        'parameters': {
            'type': 'object',
            'properties': {
                'folder_path': {
                    'type': 'string',
                    'description': 'The path to the folder, this can be relative or absolute'
                }
            },
            'required': [
                'folder_path'
            ]
        }
    }
},
    {
        'type': 'function',
        'function': {
            'name': 'read_file_contents',
            'description': 'Read the (text) contents of a file',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {
                        'type': 'string',
                        'description': 'The path to the file, this can be relative or absolute'
                    }
                },
                'required': [
                    'file_path'
                ]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'write_file_contents',
            'description': 'Write text to a file',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {
                        'type': 'string',
                        'description': 'The path to the file, this can be relative or absolute'
                    },
                    'content': {
                        'type': 'string',
                        'description': 'The (text) content you want to write to the file'
                    }
                },
                'required': [
                    'file_path'
                ]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'append_file_contents',
            'description': 'Append text to the end of an existing file',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {
                        'type': 'string',
                        'description': 'The path to the file, this can be relative or absolute'
                    },
                    'content': {
                        'type': 'string',
                        'description': 'The (text) content you want to append to the file'
                    }
                },
                'required': [
                    'file_path'
                ]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_fs_properties',
            'description': 'Get some more details from a file or folder, such as type, size, last modified, etc.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string',
                        'description': 'The path to the file or folder, this can be relative or absolute'
                    }
                },
                'required': [
                    'path'
                ]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'create_folders',
            'description': 'Create one or more folders',
            'parameters': {
                'type': 'object',
                'properties': {
                    'folder_path': {
                        'type': 'string',
                        'description': 'The path to the file or folder, this can be relative or absolute. '
                                       'May contain multiple slashes to indicate multiple subfolders. '
                    }
                },
                'required': [
                    'folder_path'
                ]
            }
        }
    },
]
