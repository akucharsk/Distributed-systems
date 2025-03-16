import socket
import sys

port = int(sys.argv[1])
host = "127.0.0.1" if len(sys.argv) < 3 else sys.argv[2]
server_port = 8008 if len(sys.argv) < 4 else sys.argv[3]
server_addr = "127.0.0.1" if len(sys.argv) < 5 else sys.argv[4]
udp_socket = None

try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))

    while True:
        num_msg = int(input("Enter a number to send to the server:\n"))
        little_endian_num = num_msg.to_bytes(4, byteorder="little")

        udp_socket.sendto(little_endian_num, (server_addr, server_port))
        print("----Message sent----")
        buff, addr = udp_socket.recvfrom(1024)
        print(f"Received from {addr}:\n{int.from_bytes(buff, byteorder='big')}")
except Exception as e:
    print(e.with_traceback(None))

finally:
    if udp_socket is not None:
        udp_socket.close()
