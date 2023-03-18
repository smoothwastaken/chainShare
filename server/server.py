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


class Server():

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

        # Set main server variables
        self.main_server_host = self.config["main_server"]["host"]
        self.main_server_port = int(self.config["main_server"]["port"])

        # Set message variables
        self.header = self.config["header"]
        self.format = self.config["format"]

        # Set verbose variable
        self.verbose = self.config["verbose"]

    def create_socket(self):
        """Creates a socket and binds it to the provided host and port.
        """
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self):
        """Binds the socket to the provided host and port.
        """
        # Bind socket
        self.socket.bind((self.host, self.port))
        if self.verbose:
            print(
                f"Socket binded to the provided host ({self.host}) and port ({self.port}).")

    def register(self):
        """Registers the server to the main server.
        """
        self.socket.connect((self.main_server_host, self.main_server_port))
        self.send("register")
        print(self.handle_main_server_message())

    def listen(self):
        """Listens for incoming connections.
        """
        # Start listening
        self.socket.listen(self.max_connections)
        if self.verbose:
            print(
                f"Socket started listening with a maximum of {self.max_connections} connections.")

        # Accept connections
        while True:
            client, address = self.socket.accept()
            if self.verbose:
                print(
                    f"Connection from client {address[0]}:{address[1]} has been established.")

            # Start a new thread for each client
            start_new_thread(self.handle_clients, (client,))

    def handle_clients(self, client, address):
        """Handles the client servers.

        Args:
            client (): Client server object.
            address (list): Address of the client server.
        """
        print(client)

    def send(self, msg: str):
        """Send a message to a client.

        Args:
            msg (str): Message to send.
        """
        message = msg.encode(self.format)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        self.socket.send(send_length)
        self.socket.send(message)

    def handle_client_message(self, client):
        """Handles the message received from a client.

        Args:
            client (object): Client server object.

        Returns:
            str: Message received from the client.
        """
        msg_length = client.recv(self.header).decode(self.format)
        if msg_length:
            msg_length = int(msg_length)
            data = client.recv(msg_length)
            msg = data.decode(self.format)
            return msg

    def handle_main_server_message(self):
        """Handles the message received from the main server.

        Returns:
            str: Message received from the main server. 
        """
        msg_length = self.socket.recv(self.header).decode(self.format)
        if msg_length:
            msg_length = int(msg_length)
            data = self.socket.recv(msg_length)
            msg = data.decode(self.format)
            return msg


if __name__ == "__main__":
    server = Server()
    server.create_socket()
    server.bind()
    server.register()
