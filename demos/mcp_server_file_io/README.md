# MCP Server for File I/O

This is a simple MCP server that provides tools for interacting with the file system.

## Setup

1.  Install uv:

    ```bash
    pip install uv
    ```

2.  Install the dependencies using uv:

    ```bash
    uv pip install -r requirements.txt
    ```

3.  Configure the `ALLOWED_FOLDER` environment variable. This variable specifies the folder that the server is allowed to access. By default, it is set to `./`, which means that the server can only access files in the current directory. You can set this variable in a `.env` file or as a system environment variable.

    Example `.env` file:

    ```
    ALLOWED_FOLDER=/path/to/allowed/folder
    ```

## Usage

1.  Run the server using uv:

    ```bash
    uv python file_io_server.py
    ```

2.  Connect to the server using an MCP client.

## Tools

The server provides the following tools:

- `list_files`: Lists the files and directories within a specified folder.

  - Parameters:
    - `folder_path` (str): The absolute path to the folder to list. Must be within the ALLOWED_FOLDER.
  - Returns:
    - `list[str]`: A list of strings, where each string is the name of a file or directory in the folder. Returns None if the folder does not exist or is not accessible.

- `read_file_contents`: Reads the entire contents of a file.

  - Parameters:
    - `file_path` (str): The absolute path to the file to read. Must be within the ALLOWED_FOLDER.
  - Returns:
    - `str`: The contents of the file as a string. Returns None if the file does not exist or cannot be read.

- `write_file_contents`: Writes content to a file, overwriting any existing content.

  - Parameters:
    - `file_path` (str): The absolute path to the file to write. Must be within the ALLOWED_FOLDER. If the file does not exist, it will be created. If it exists, its contents will be replaced.
    - `content` (str, optional): The content to write to the file. Defaults to an empty string.
  - Returns:
    - `bool`: True if the write was successful, False otherwise.

- `append_file_contents`: Appends content to the end of a file, adding a newline character after the appended content.

  - Parameters:
    - `file_path` (str): The absolute path to the file to append to. Must be within the ALLOWED_FOLDER. If the file does not exist, it will be created.
    - `content` (str, optional): The content to append to the file. Defaults to an empty string.
  - Returns:
    - `bool`: True if the append was successful, False otherwise.

- `create_folders`: Creates a folder (or directory) at the specified path, including any necessary parent folders.

  - Parameters:
    - `folder_path` (str): The absolute path to the folder to create. Must be within the ALLOWED_FOLDER.
  - Returns:
    - `bool`: True if the folder creation was successful, False otherwise.

- `get_fs_properties`: Gets file system properties of a file or folder, such as its type, size, modification date, and permissions.

  - Parameters:
    - `path` (str): The absolute path to the file or folder.
  - Returns:
    - `dict`: A dictionary containing file system properties, or None if the path does not exist.
      The dictionary includes the following keys: - 'full_path' (str): The absolute path to the file or folder. - 'type' (str): 'file', 'directory', or 'other'. - 'size' (int): The size of the file in bytes (only for files). - 'last_modified' (str): The last modification time in 'YYYY-MM-DD HH:MM:SS.ffffff' format (only for files). - 'last_accessed' (str): The last access time in 'YYYY-MM-DD HH:MM:SS.ffffff' format (only for files). - 'creation_time' (str): The creation time in 'YYYY-MM-DD HH:MM:SS.ffffff' format (only for files). - 'permissions' (str): The permissions string (e.g., 'drwxr-xr-x') (only for files). - 'uid' (int): The user ID (only for files). - 'gid' (int): The group ID (only for files).

- `delete_file`: Deletes the file at the specified path.

  - Parameters:
    - `file_path` (str): The absolute path to the file to delete. Must be within the ALLOWED_FOLDER.
  - Returns:
    - `bool`: True if the file deletion was successful, False otherwise.

- `replace_in_file`: Replaces the first occurrence of a string in a file with another string.
  - Parameters:
    - `file_path` (str): The absolute path to the file to modify. Must be within the ALLOWED_FOLDER.
    - `search_string` (str): The string to search for.
    - `replace_string` (str): The string to replace the search string with.
  - Returns:
    - `bool`: True if the replacement was successful, False otherwise.

## Security

The server uses the `is_within_folder` function to ensure that all file system operations are performed within the `ALLOWED_FOLDER`. This helps to prevent the server from accessing or modifying files outside of the allowed folder.

## Including in an MCP Client

To include this server in an MCP compatible tool or client, you need to configure the client to connect to the server. Here's an example configuration:

```json
{
  "mcpServers": {
    "file_io_server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/Users/stilkin/PycharmProjects/pxl-llm-1/demos/mcp_server_file_io",
        "run",
        "file_io_server.py"
      ],
      "env": {
        "ALLOWED_FOLDER": "/Users/stilkin/PycharmProjects/"
      }
    }
  }
}
```

- `"file_io_server"`: This is a unique name you choose to identify your server.
- `"type": "stdio"`: Specifies that the server uses standard input/output for communication.
- `"command": "uv"`: This specifies the command to run the server.
- `"args": ["--directory", "/Users/stilkin/PycharmProjects/pxl-llm-1/demos/mcp_server_file_io", "run", "file_io_server.py"]`: This provides the arguments to the command:
  - `"--directory", "/Users/stilkin/PycharmProjects/pxl-llm-1/demos/mcp_server_file_io"`: Tells `uv` the project directory.
  - `"run", "file_io_server.py"`: Tells `uv` to run the `file_io_server.py` script.
- `"env": { "ALLOWED_FOLDER": "/Users/stilkin/PycharmProjects/" }`: This sets the `ALLOWED_FOLDER` environment variable for the server process. **Important:** You **must** set the `ALLOWED_FOLDER` to a safe directory on your system.

Ensure that the paths are correct relative to the client's working directory. The client machine must have `uv` installed and the dependencies listed in `demos/mcp_server_file_io/requirements.txt` installed.

To install uv, you can use pip:

```bash
pip install uv
```

Then, install the dependencies using uv:

```bash
uv pip install -r requirements.txt
```
