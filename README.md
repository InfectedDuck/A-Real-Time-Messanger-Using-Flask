# Real-Time Web Messenger Application

This **Real-Time Web Messenger Application** is a Python-based chat platform built with **Flask** and **Flask-SocketIO** for real-time communication. It allows users to join or create chat rooms, send messages, and update their profiles with secure authentication. The application uses **SQLite** for database management, and profile photos can be uploaded and displayed via secure file handling. 

## Features

1. **User Authentication**: 
    - Login and registration system with password hashing (using `werkzeug.security`).
    - Ensures that only authenticated users can access certain functionalities like chat rooms or profile updates.

2. **Real-Time Communication**:
    - Chat rooms are created dynamically, and users can join existing rooms or create new ones.
    - Messages are broadcast in real-time using **WebSockets**, allowing users to instantly communicate.
    - Each room stores its own messages and displays them upon user re-entry.

3. **Profile Management**:
    - Users can update their profiles, including their usernames, emails, and passwords.
    - Profile photos can be uploaded securely with image validation for types (`png`, `jpg`, `jpeg`, `gif`).

4. **Database Management**:
    - User data is stored in a **SQLite** database.
    - The application fetches and updates user data securely when necessary.

5. **File Uploads**:
    - Users can upload profile photos, and the application verifies that the file type is allowed and securely saves the file.

## Secured HTTP Connection

The application uses a **secured HTTP connection** (HTTPS) for communication, enhancing the security of user interactions. 

- A **self-signed SSL certificate** is used to establish secure connections between the server and the client. The certificate (`cert.pem`) and private key (`key.pem`) are provided, ensuring that data transmitted between the client and server is encrypted.
- The Flask-SocketIO server runs with the `ssl_context` parameter configured, enforcing the use of **HTTPS**. This prevents man-in-the-middle attacks and ensures that sensitive data such as passwords and messages are encrypted during transmission.

The application runs with these certificates to provide HTTPS communication:
```
socketio.run(app, host='127.0.0.1', port=5000, ssl_context=(cert_path, key_path))
```
## Technology Stack

- **Flask**: Backend web framework.
- **Flask-SocketIO**: Enables real-time, bidirectional communication using WebSockets.
- **SQLite**: Database management for storing user information.
- **HTML/CSS**: For frontend templates.
- **Werkzeug**: Password hashing and request handling.
- **Socket.IO**: For handling real-time message delivery.
- **SSL (Secure Sockets Layer)**: For securing communications.

## Usage Instructions

1. Clone the repository and install the required dependencies.
2. Generate your SSL certificate and private key, or use the provided paths.
3. Run the application locally, ensuring the upload folder exists:
```
python app.py
```
4. Access the application at https://127.0.0.1:5000.

## Chat Application Status

The chat application is now **live** and secured via **HTTPS**!

## Future Improvements

- Implementing enhanced security features for password recovery.
- Adding more room management features (e.g., private rooms, room moderation).
- Implementing message history retrieval from the database.

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](LICENSE.txt) file for details.
