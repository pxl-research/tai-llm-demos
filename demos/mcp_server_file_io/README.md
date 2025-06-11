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
    uv python server.py
    ```

2.  Connect to the server using an MCP client.

## Tools

The server provides the following tools:

- `list_files`: List files in a folder.
- `read_file_contents`: Read the contents of a file.
- `write_file_contents`: Write content to a file.
- `append_file_contents`: Append content to a file.
- `create_folders`: Create a folder.
- `get_fs_properties`: Get file system properties of a file or folder.
- `delete_file`: Delete a file.
- `delete_folder`: Delete a folder.
- `replace_in_file`: Replace a string in a file.

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
        "server.py"
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
- `"args": ["--directory", "/Users/stilkin/PycharmProjects/pxl-llm-1/demos/mcp_server_file_io", "run", "server.py"]`: This provides the arguments to the command:
  - `"--directory", "/Users/stilkin/PycharmProjects/pxl-llm-1/demos/mcp_server_file_io"`: Tells `uv` the project directory.
  - `"run", "server.py"`: Tells `uv` to run the `server.py` script.
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
