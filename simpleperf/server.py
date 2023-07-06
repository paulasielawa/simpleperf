# Import necessary packages, variable, method and dictionary
import socket
import time
import threading
from utils import BUFFER_SIZE, unit_conversion, calculate_bandwidth


# Class: Server
# Description: A class that represents a simpleperf server that listens for incoming client connections
# and counts data transfer and bandwidth
class Server:
    # Function: __init__
    # Description: Initializes a new instance of the Server class
    # Arguments:
    # - port: The port number on which the server listens for incoming connections
    # - bind: The IP address of the server
    # - format: The format of the output data from [B, KB, MB]
    def __init__(self, port, bind, format):
        self.port = port
        self.bind = bind
        self.format = format

    # Function: start
    # Description: Starts the server, listens for incoming client connections, and creates
    # a new thread for each connection
    def start(self):
        # create a socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the IP address and port specified by the user
        server_socket.bind((self.bind, self.port))

        # Listen for incoming client connections
        server_socket.listen()

        # Print a message indicating that the server is ready
        print(f'{"-"*55}\nA simpleperf server is listening on port {self.port}\n{"-"*55}')

        # Accept incoming client connections and create a new thread for each connection
        # Infinite loop that keeps running until the server is manually stopped. It ensures that the server continuously
        # listens for and accepts incoming client connections.
        while True:
            # Method waits for an incoming client and returns a new socket object with 'conn' and 'address'
            conn, address = server_socket.accept()
            # Print a message indicating that a client has connected to the server
            print(f"A simpleperf client with {address[0]}:{address[1]} is connected with {self.bind}:{self.port}")
            # New thread is created for each client connection
            thread = threading.Thread(target=self.handle_client, args=(conn, address))
            # Start thread
            thread.start()

    # Function: handle_client
    # Description: Handles the data transfer for an individual client connection and calculates
    # the data transfer rate and bandwidth
    # Arguments:
    # - conn: The socket object representing the client connection.
    # - address: The client's IP address and port number.
    def handle_client(self, conn, address):
        # Initialize variable (received_bytes)
        received_bytes = 0
        # Record the start time
        start_time = time.time()

        # Process incoming data from client connection
        while True:
            data = conn.recv(BUFFER_SIZE)
            # Break the loop if there's no more data or the client sends a 'BYE' message
            if not data or 'BYE' in data.decode():
                break
            # Increment the received_bytes counter by the length of the received data
            received_bytes += len(data)

        # Record the end time after the data transfer is complete
        end_time = time.time()

        # Calculate the total time used during data transfer
        total_duration = end_time - start_time
        # Calculate the total data transfer in the user-specified format
        transfer = received_bytes / unit_conversion[self.format]
        # Convert the data transfer rate (in Mbps)
        rate = calculate_bandwidth(received_bytes, total_duration)

        # Send an acknowledgment to the client that the server is closing the connection
        conn.sendall(b'ACK: BYE')

        # Print a summary of the data transfer (first header and statistics), including the client ID, interval,
        # transfer size, and rate
        print(f"ID{'':<15}Interval{'':<4}Transfer{'':<5}Rate")
        print(f"{address[0]}:{address[1]}  0.0 - {total_duration:.1f}  {transfer:.2f} {self.format}  {rate:.2f} Mbps")

        # Close the connection with the client
        conn.close()
