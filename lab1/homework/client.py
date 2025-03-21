import socket
import threading
from message import Message
import re


def handle_incoming_messages(tcp_socket: socket.socket, event: threading.Event):
    while event.is_set():
        msg = Message.from_bytes(tcp_socket.recv(Message.MAXIMUM_MESSAGE_LENGTH).rstrip())
        if msg.sender_name == "Server" and msg.message.strip() == "SHUTDOWN":
            raise Exception("Shutdown received")
        if len(msg.message.strip()) > 0:
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


def fetch_multicast_ip(message: str):
    address = re.match(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", message.strip())[0]
    return address, len(address)


def main():
    tcp_socket = None
    udp_socket = None
    print("WELCOME TO THE DISTRIBUTED SYSTEM CHAT\nConfigure the settings listed below. Press enter with no"
          "response to keep the default value")
    name = input("\nEnter your name:\n")
    server_host = input("\nEnter the desired server IP address (default: 127.0.0.1):\n")
    server_port = input("\nEnter the desired server port (default: 8008):\n")
    server_address = ("localhost" if len(server_host) == 0 else server_host,
                      8008 if len(server_port) == 0 else int(server_port))

    try:
        print("Connecting to server...")
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.connect(server_address)

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(tcp_socket.getsockname())

        def handle_signal(sig, frame):
            leave(tcp_socket, name)
            if udp_socket is not None:
                udp_socket.close()

        welcome(tcp_socket, name)

        print("Messaging tutorial:\n"
              "Sending via UDP socket: opt:U <message>\n"
              "\texample: 'opt:U UDP rules' will send 'UDP rules' via a UDP socket)\n\n"
              "Quitting the chat: opt:Q\n\n"
              "Normal message via TCP socket: <message> OR opt:T <message> (examples: \n\t'Hello World'\n\t"
              "'opt:T opt:Q' will send the 'opt:Q' string via TCP socket and won't close the chat)\n")
        recv_event = threading.Event()
        recv_event.set()
        recv_thread = threading.Thread(target=handle_incoming_messages, args=(tcp_socket, recv_event), daemon=True)
        recv_thread.start()

        while True:
            msg = input()
            match msg[:5]:
                case "opt:U":
                    send_udp(udp_socket, name, msg[5:].strip(), *server_address)
                case "opt:Q":
                    leave(tcp_socket, name)
                    break
                case "opt:T":
                    send_tcp(tcp_socket, name, msg[5:].strip())
                case _:
                    send_tcp(tcp_socket, name, msg.strip())

    except Exception as e:
        print(e)
    finally:
        if tcp_socket is not None:
            tcp_socket.close()
        if udp_socket is not None:
            udp_socket.close()


if __name__ == '__main__':
    main()
