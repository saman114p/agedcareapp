import socket

service_name = "acc1-dev-srch-ae.search.windows.net"
try:
    ip = socket.gethostbyname(service_name)
    print(f"IP address of {service_name} is {ip}")
except socket.gaierror as e:
    print(f"Failed to get IP address for {service_name}: {e}")