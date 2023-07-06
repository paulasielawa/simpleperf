# Import necessary packages, variable, method and dictionary
import socket
import time
import threading
from utils import BUFFER_SIZE, unit_conversion, calculate_bandwidth


# Class: Client
# Description: A class that represents a simpleperf client mode that connects to a simpleperf server and sends data
class Client:
    # Function: __init__
    # Description: Initializes a new instance of the Client class
    # Arguments:
    # - serverip: IP address of the server to connect to
    # - port: Port number to connect to on the server
    # - time: Duration in seconds for sending data
    # - num_bytes: Total number of bytes to send (alternative to duration)
    # - interval:  Interval in seconds for creating statistics
    # - parallel: Number of parallel connections to the server
    # - format: Unit format for displaying transfer size
    def __init__(self, serverip, port, time, num_bytes, interval, parallel, format):
        self.serverip = serverip
        self.port = port
        self.time = time
        self.num_bytes = num_bytes
        self.interval = interval
        self.parallel = parallel
        self.format = format

    # Function: print_interval
    # Description: print interval statistics for data transfer
    # Arguments:
    # - interval_num: The current interval number (0-indexed)
    # - interval_bytes: The number of bytes sent in the current interval
    # - format: The unit format for displaying transfer size (B, KB, MB)
    def print_interval(self, interval_num, interval_bytes, format):
        # Start time of the current interval
        interval_start = interval_num * self.interval
        # End time of the current interval
        # It adds 1 because interval_num is 0-indexed
        interval_end = (interval_num + 1) * self.interval
        # Transfer size in the specified unit format
        transfer = interval_bytes / unit_conversion[format]
        # Convert to Mbps
        rate = calculate_bandwidth(interval_bytes, self.interval)

        # Print the statistics for the current interval
        print(f"{self.serverip}:{self.port}  {interval_start:.1f} - {interval_end:.1f}  {transfer:.2f} {format}  {rate:.2f} Mbps")

        # Method returns 0 to reset the interval_bytes value when it is called
        return 0

    # Function: start
    # Description: Start the client
    def start(self):
        # If both num_bytes and time are specified, raise an error
        # It doesn't always work perfectly, but it does most of the time. If I have more time, I'll try to solve this
        # if 'if statement' looks like that ->(if self.num_bytes and self.time) it doesnt working at all so i need to
        # specify -t flag
        if self.num_bytes and self.time != 25:
            exit("Error: Cannot use both -n and -t flags at the same time")

        # Initialize total_bytes variable
        total_bytes = None

        # If num_bytes is specified, convert it to bytes
        if self.num_bytes:
            try:
                # Extract the unit (B, KB, or MB) and the numerical value from the input,
                # upper() for make it case-insensitive
                unit = self.num_bytes[-2:].upper()
                num = int(self.num_bytes[:-2])
                # Calculate the total bytes based on the unit.
                total_bytes = num * unit_conversion[unit]
            except (ValueError, KeyError):
                # If an invalid unit is provided, raise a ValueError
                raise ValueError("Invalid size format. Please use 'B', 'KB', or 'MB' as the unit.")

        # Print the header for the client connection
        print(f'{"-"*70}\nA simpleperf client connecting to server {self.serverip}, port {self.port}\n{"-"*70}')

        # Create a list to store the client threads
        threads = []

        # Create and start the client threads based on the specified number of parallel connections
        for _ in range(self.parallel):
            thread = threading.Thread(target=self.client_thread, args=(total_bytes,))
            thread.start()
            threads.append(thread)

        # Wait for all client threads to finish
        for thread in threads:
            thread.join()

    # Function: client_thread
    # Description: handles data transfer between the client and server
    # Arguments:
    # - total_bytes (int): The total number of bytes to send if specified by the user. None if not specified
    # Exceptions: This function does not explicitly raise any exceptions. However, exceptions related to socket
    # operations (e.g., connection errors, sending/receiving data) may be raised implicitly by the
    # underlying socket library.
    def client_thread(self, total_bytes):
        # Create a new socket for the client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the client socket to the server
        client_socket.connect((self.serverip, self.port))

        # Print the connection information
        print(f"Client connected with {self.serverip} port {self.port}")

        # Initialize variables for tracking time, bytes sent, and intervals
        start_time = time.time()
        sent_bytes = 0
        interval_start = start_time
        interval_bytes = 0
        interval_num = 0

        # Create a 1000-byte data chunk to send
        data = b'0' * BUFFER_SIZE

        # If interval flag is set, print the headers for the interval statistics
        if self.interval:
            print(f"ID{'':<14}Interval{'':<3}Transfer{'':<4}Bandwidth")

        # If total_bytes is specified, send exactly total_bytes to the server
        if total_bytes:
            while sent_bytes < total_bytes:
                # Calculate the remaining bytes to send
                remaining_bytes = total_bytes - sent_bytes
                # Create the data to send based on remaining bytes
                data_to_send = data[:remaining_bytes]
                # Send the data to the server
                client_socket.sendall(data_to_send)
                # Update the sent_bytes counter
                sent_bytes += len(data_to_send)
            # Record the end time of the transfer
            end_time = time.time()
        # If total_bytes is not specified, send data for the specified duration
        else:
            while time.time() - start_time < self.time:
                # Send the 1000-byte data chunk to the server
                client_socket.sendall(data)
                # Update the sent_bytes and interval_bytes counters
                sent_bytes += len(data)
                interval_bytes += len(data)
                # Record the end time
                end_time = time.time()

                # Check if the interval is set (not None) and if the time elapsed since the last interval_start is
                # greater than or equal to the interval
                if self.interval is not None and end_time - interval_start >= self.interval:
                    # Print the interval statistics and set interval_bytes to 0 (since it's returned by
                    # print_interval method)
                    interval_bytes = self.print_interval(interval_num, interval_bytes, self.format)
                    # Update the interval_start time to the current end_time for the next interval
                    interval_start = end_time
                    # Increment the interval number for the next interval
                    interval_num += 1

        # If interval flag is set and there are remaining interval bytes, print the last interval statistics
        if interval_bytes and self.interval is not None:
            self.print_interval(interval_num, interval_bytes, self.format)

        # If interval flag is set, print a separator line
        if self.interval:
            print("-"*55)

        # Send a 'BYE' message to the server to signal the end of the data transfer
        client_socket.sendall(b'BYE')
        # Record the end time
        end_time = time.time()

        # Check if the server's response is 'ACK: BYE' (indicating the server received the 'BYE' message)
        if client_socket.recv(BUFFER_SIZE) == b'ACK: BYE':
            # Record the end time
            end_time = time.time()
            # Calculate the total duration of the transfer
            total_duration = end_time - start_time
            # If total_duration is less than 1 second to avoid division by zero errors
            if total_duration < 1:
                total_duration = 1
            # Calculate the total amount of data in the specified format
            transfer = sent_bytes / unit_conversion[self.format]
            # Calculate the transfer rate in Mbps
            rate = calculate_bandwidth(sent_bytes, total_duration)

            # Print the final transfer statistics headers
            print(f"ID{'':<14}Interval{'':<4}Transfer{'':<4}Bandwidth")
            # Print the final transfer statistics, including server IP and port and osv.
            print(f"{self.serverip}:{self.port}  0.0 - {total_duration:.1f}  {int(transfer)} {self.format}  {rate:.2f} Mbps")


        # Close the client connection
        client_socket.close()


