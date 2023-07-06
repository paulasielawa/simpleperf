# Import necessary packages and classes
import argparse
from server import Server
from client import Client

# # Create an argument parser with a description of the program
parser = argparse.ArgumentParser(description='A simplified version of iperf with multiple options')

# Common arguments for both server and client
# -p: port number (default: 8088), in the range [1024, 65535]
parser.add_argument('-p', '--port', type=int, default=8088, choices=range(1024, 65535),
                    help='Port number to use')
# -f: format of summary results (default: MB)
parser.add_argument('-f', '--format', type=str, default='MB',
                    help='Format of summary results (B, KB, or MB)')

# Server-specific arguments
server_group = parser.add_argument_group('Server mode')
# -s: enable server mode, 'store_true' on/off flag
server_group.add_argument('-s', '--server', action='store_true',
                          help='Enable server mode')
# -b: IP address of server interface (default: 0.0.0.0)
server_group.add_argument('-b', '--bind', type=str, default='0.0.0.0',
                          help='IP address of server interface')

# Client-specific arguments
client_group = parser.add_argument_group('Client mode')
# -c: enable client mode, 'store_true' on/off flag
client_group.add_argument('-c', '--client', action='store_true',
                          help='Enable client mode')
# -I: IP address of server (default: 127.0.0.1)
client_group.add_argument('-I', '--serverip', type=str, default='127.0.0.1',
                          help='IP address of server')
# -t: total duration of data generation (default: 25 seconds)
client_group.add_argument('-t', '--time', type=int, default=25,
                          help='Total duration of data generation')
# -n: transfer number of bytes specified by -n flag (e.g., 10B, 10KB, 10MB)
client_group.add_argument('-n', '--num', type=str, default=None,
                          help='Transfer number of bytes specified by -n flag (e.g., 10B, 10KB, 10MB)')
# -i: print statistics every X seconds
client_group.add_argument('-i', '--interval', type=int, default=None,
                          help='Print statistics every X seconds')
# -P: number of parallel connections (1 to 5, default: 1)
client_group.add_argument('-P', '--parallel', type=int, default=1, choices=range(1, 6),
                          help='Number of parallel connections (1 to 5, default: 1)')

# Parse command-line arguments
args = parser.parse_args()

# Main function
if __name__ == '__main__':
    # Must run either in client or server mode. Check if both server and client modes are enabled
    if args.server and args.client:
        exit("Error: Must run in either client or server mode")

    # If server mode is enabled
    if args.server:
        # Create a server instance with the specified arguments
        server = Server(args.port, args.bind, args.format)
        # Start the server
        server.start()

    # If client mode is enabled
    elif args.client:
        # Create a client instance with the specified arguments
        client = Client(args.serverip, args.port, args.time, args.num, args.interval, args.parallel, args.format)
        # Start the client
        client.start()



