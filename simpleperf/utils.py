# Buffer size used for data transfer (in bytes)
BUFFER_SIZE = 1000

# A dictionary that maps unit names (B, KB, MB) to their conversion factor to bytes
unit_conversion = {
    'B': 1,
    'KB': 1000,
    'MB': 1000 * 1000
}

# Function: calculate_bandwidth
# Description: Calculates the bandwidth in Mbps (megabits per second) given size of data and duration of the transfer
# Arguments:
# - size: The size of the data transferred (in bytes)
# - duration: The duration of the data transfer (in seconds)
# Returns: The calculated bandwidth in Mbps
def calculate_bandwidth(size, duration):
    # To calculate bandwidth (in Mbps), multiply the size (in bytes) by 8 (to convert to bits),
    # then divide by the duration (in seconds) multiplied by 1,000,000 (to convert to megabits)
    return (size * 8) / (duration * 1000000)
