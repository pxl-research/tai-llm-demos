# tools_fileio demo
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
    {
        'type': 'function',
        'function': {
            'name': 'delete_file',
            'description': 'Remove a single file from disk. '
                           'Always ask for confirmation from the user before doing this! ',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {
                        'type': 'string',
                        'description': 'The path to the file, this can be relative or absolute. '
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
            'name': 'delete_folder',
            'description': 'Remove a folder from disk. '
                           'Always ask for confirmation from the user before doing this! ',
            'parameters': {
                'type': 'object',
                'properties': {
                    'folder_path': {
                        'type': 'string',
                        'description': 'The path to the folder, this can be relative or absolute. '
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
            'name': 'current_working_folder',
            'description': 'Find out the directory we are currently working from. ',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_allowed_folder',
            'description': 'Find out the root directory we are allowed to write to. '
                           'You can read / write / edit in this folder and all of its subfolders. ',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
    }
]
