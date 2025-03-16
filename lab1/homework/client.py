import socket
import sys
import threading
from message import Message
import struct
import re


def handle_incoming_messages(tcp_socket: socket.socket, event: threading.Event):
    while event.is_set():
        msg = Message.from_bytes(tcp_socket.recv(Message.MAXIMUM_MESSAGE_LENGTH).rstrip())
        msg.print()


def handle_multicast_messages(multicast_socket: socket.socket, event: threading.Event):
    while event.is_set():
        msg, addr = multicast_socket.recvfrom(Message.MAXIMUM_MESSAGE_LENGTH)
        msg = Message.from_bytes(msg)
        msg.print()


def welcome(tcp_socket, name):
    msg = Message.initial_message(name)
    tcp_socket.send(msg.encode())
    welcome_msg = tcp_socket.recv(Message.MAXIMUM_MESSAGE_LENGTH).rstrip()
    welcome_msg = Message.from_bytes(welcome_msg)
    print("Connection established!")
    welcome_msg.print()


def leave(tcp_socket, name):
    msg = Message.leaving_message(name)
    tcp_socket.send(msg.encode())
    print("Leaving the chat")


def send_udp(udp_socket: socket.socket, name: str, msg: str, server_host: str, server_port: int):
    msg = Message(name + ":UDP", msg)
    udp_socket.sendto(msg.encode(), (server_host, server_port))


def send_tcp(tcp_socket, name, msg):
    msg = Message(name, msg)
    tcp_socket.send(msg.encode())


def subscribe_multicast(multicast_socket: socket.socket, group_address: str):
    print("Subscribing to multicast group", group_address)
    group = struct.pack("4sL", socket.inet_aton(group_address), socket.INADDR_ANY)
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group)


def send_multicast(multicast_socket: socket.socket, address: str, port: int, name: str, msg: str):
    msg = Message(name + f": {address}", msg)
    print("Sending multicast message", msg.message)
    multicast_socket.sendto(msg.encode(), (address, port))


def fetch_multicast_ip(message: str):
    address = re.match(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", message.strip())[0]
    return address, len(address)


def main():
    tcp_socket = None
    udp_socket = None
    multicast_socket = None
    print("WELCOME TO THE DISTRIBUTED SYSTEM CHAT\nConfigure the settings listed below. Press enter with no"
          "response to keep the default value")
    name = input("\nEnter your name:\n")
    server_host = input("\nEnter the desired server IP address (default: 127.0.0.1):\n")
    server_port = input("\nEnter the desired server port (default: 8008):\n")
    server_address = ("localhost" if len(server_host) == 0 else server_host,
                      8008 if len(server_port) == 0 else int(server_port))

    multicast_port = 50142

    try:
        print("Connecting to server...")
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.connect(server_address)

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(tcp_socket.getsockname())

        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multicast_socket.bind(("", tcp_socket.getsockname()[1]))
        base_multicast_addr = "239.255.255.1"
        pack = struct.pack("4sL", socket.inet_aton(base_multicast_addr), socket.INADDR_ANY)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, pack)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

        welcome(tcp_socket, name)

        print("Messaging tutorial:\n"
              "Sending via UDP socket: opt:U <message>\n"
              "\texample: 'opt:U UDP rules' will send 'UDP rules' via a UDP socket)\n\n"
              "Sending a multicast message: opt:M <address> <message> \nexample: 'opt:M 224.0.0.1 Hello from MCAST'\n\n"
              "Quitting the chat: opt:Q\n\n"
              "Subscribing to a multicast group: opt:S <address>\n\texample: 'opt:S 224.0.0.1'\n\n"
              "Normal message via TCP socket: <message> OR opt:T <message> (examples: \n\t'Hello World'\n\t"
              "'opt:T opt:Q' will send the 'opt:Q' string via TCP socket and won't close the chat)\n")
        recv_event = threading.Event()
        recv_event.set()
        recv_thread = threading.Thread(target=handle_incoming_messages, args=(tcp_socket, recv_event), daemon=True)
        recv_thread.start()

        mcast_event = threading.Event()
        mcast_event.set()
        mcast_thread = threading.Thread(target=handle_multicast_messages, args=(multicast_socket, mcast_event), daemon=True)
        mcast_thread.start()

        while True:
            msg = input()
            match msg[:5]:
                case "opt:U":
                    send_udp(udp_socket, name, msg[5:].strip(), *server_address)
                case "opt:M":
                    addr, addr_len = fetch_multicast_ip(msg[5:])
                    send_multicast(multicast_socket, addr, multicast_port, name, msg[5 + addr_len:])
                case "opt:Q":
                    leave(tcp_socket, name)
                    break
                case "opt:T":
                    send_tcp(tcp_socket, name, msg[5:].strip())
                case "opt:S":
                    addr, _ = fetch_multicast_ip(msg[5:])
                    subscribe_multicast(multicast_socket, addr)
                case _:
                    send_tcp(tcp_socket, name, msg.strip())

    except Exception as e:
        print(e)
    finally:
        if tcp_socket is not None:
            tcp_socket.close()
        if udp_socket is not None:
            udp_socket.close()
        if multicast_socket is not None:
            multicast_socket.close()


if __name__ == '__main__':
    main()
