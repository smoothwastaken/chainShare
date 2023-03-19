"""
MIT License

Copyright (c) 2023 Cléry Arque-Ferradou

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import socket
from _thread import start_new_thread
import threading
import json


class MainServer():

    def __init__(self):
        """Initializes the main server.
        """
        # Load config file
        with open('./config.json', 'r') as config_file:
            self.config = json.load(config_file)
            config_file.close()

        # Set socket variables
        self.host = self.config["host"]
        self.port = int(self.config["port"])
        self.max_connections = self.config["max_connections"]

        # Set message variables
        self.header = self.config["header"]
        self.format = self.config["format"]

        # Set verbose variable
        self.verbose_logs = self.config["verbose"]

    def create_socket(self):
        """Creates a socket and binds it to the provided host and port.
        """
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.verbose(
            f"Socket binded to the provided host ({self.host}) and port ({self.port}).")

    def listen(self):
        """Listens for incoming connections.
        """
        # Start listening
        self.socket.listen(self.max_connections)
        self.verbose(
            f"Socket started listening with a maximum of {self.max_connections} connections.")

        # Accept connections
        while True:
            client_server, address = self.socket.accept()
            self.verbose(
                f"Connection from server client {address[0]}:{address[1]} has been established.")

            # Start a new thread for each client
            self.verbose("Starting new thread for the client server...")
            start_new_thread(self.handle_client_servers,
                             (client_server, address,))

    def handle_client_servers(self, client, address):
        """Handles the client servers.

        Args:
            client (): Client server object.
            address (list): Address of the client server.
        """
        connected = False
        # Waiting for the client server to send a register request
        register_request = self.handle_client_message(client)

        # Registering the client server
        if "$REGISTER" in register_request:
            self.verbose(
                f"Received register request from client server with id: '{register_request.split(' ')[1]}'.")

            # Verify if the client server id is valid
            id, valid_id = self.verify_client_id(
                register_request.split(' ')[1])
            if not valid_id:  # Send an error to the client server
                self.send(client, "#!INVALID_ID")
                self.close(client, address)
                return
            else:  # Send a confirmation to the client server
                self.send(client, "#VALID_ID")

            # Send the client server a request for its name
            self.send(client, "?NAME")
            # Receive the client server name
            client_server_name = self.handle_client_message(client)
            # Send the client server a confirmation
            self.send(client, "#VALID_NAME")

            # Send the client server registration confirmation
            self.send(client, "#REGISTERED @" + client_server_name)
            connected = True
            while connected:
                break

        self.close(client, address)

    def verbose(self, msg: str):
        if self.verbose_logs:
            print(msg)

    def send(self, client, msg: str):
        """Sends a message to the client.

        Args:
            client (object): Client server object.
            msg (str): Message to send.
        """
        message = msg.encode(self.format)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        client.send(send_length)
        client.send(message)

    def close(self, client, address):
        self.send(client, "#CLOSE")
        self.verbose(
            f"Closing connection for client server {address[0]}:{address[1]}...")
        client.close()
        self.verbose(
            f"Connection for client server {address[0]}:{address[1]} closed.")

    def handle_client_message(self, client):
        msg_length = client.recv(self.header).decode(self.format)
        if msg_length:
            msg_length = int(msg_length)
            data = client.recv(msg_length)
            msg = data.decode(self.format)
            return msg

    def verify_client_id(self, id):
        # Verify id's length
        self.verbose(f"Verifying client server id: '{id}'...")
        self.verbose(f"Verifying the length of the id...")
        if len(id) != 40:
            self.verbose(
                f"The id's length is not valid. (20 characters required, {len(id)} provided)")
            return id, False
        self.verbose(f"The id's length is valid.")

        # Verify id's characters
        self.verbose(f"Verifying the characters of the id...")
        authorized_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        i = 0
        for char in id:
            if char not in authorized_chars:
                self.verbose(f"The id contains an unauthorized character: '{char}' at index {i}.")
                return id, False
            i += 1
        self.verbose(f"The id's characters are valid.")
        self.verbose(f"Client server id verified.")
        return id, True


if __name__ == "__main__":
    main_server = MainServer()
    main_server.create_socket()
    main_server.listen()
