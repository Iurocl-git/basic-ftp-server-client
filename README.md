# FTP Server and Client Implementation

A simple FTP (File Transfer Protocol) server and client implementation in Python, allowing file transfers and directory navigation between connected clients and the server.

## Features

- File upload and download capabilities
- Directory navigation and listing
- User authentication system
- Support for multiple concurrent connections
- Secure file transfer using separate data connections
- Error handling and connection management

## Prerequisites

- Python 3.x
- Network connectivity between server and client machines

## Project Structure

```
FTP_server/
├── server.py           # FTP server implementation
├── client.py          # FTP client implementation
├── client/            # Directory for client files
│   ├── Public/       # Publicly accessible files
│   └── [username]/    # User-specific directories
└── utilizatori.txt    # User credentials file
```

## Server Setup

1. Run the server:
```bash
python server.py
```

The server will automatically:
- Determine its IP address
- Listen on port 5550
- Create necessary directories
- Handle incoming connections

## Client Usage

1. Run the client:
```bash
python client.py
```

2. When prompted:
   - Enter the server's IP address
   - Enter the server's port (default: 5550)

3. Available Commands:
   - `LIST` - List files in current directory
   - `CWD [directory]` - Change working directory
   - `RETR [filename]` - Download a file
   - `STOR [filename]` - Upload a file
   - `USER [username]` - Login with username
   - `PASS [password]` - Enter password
   - `!DISCONNECT` - Disconnect from server

## Security Features

- User authentication required for accessing private directories
- Separate data connections for file transfers
- Directory access restrictions
- Timeout handling for inactive connections

## Error Handling

The implementation includes error handling for:
- Connection issues
- File transfer errors
- Invalid commands
- Authentication failures
- Directory access violations

## Notes

- The server automatically creates necessary directories
- Default user credentials are stored in `utilizatori.txt`
- Public files are accessible to all users
- Private directories are user-specific
- File transfers use separate data connections for better reliability

## Limitations

- Basic FTP implementation without encryption
- No resume capability for interrupted transfers
- Limited to local network or direct IP connections
- No file compression

## Contributing

Feel free to submit issues and enhancement requests! 