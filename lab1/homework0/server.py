import socket
import sys
import threading
from message import Message
import signal


class Server:
    def __init__(self, tcp_socket: socket.socket, udp_socket: socket.socket):
        self.socket = tcp_socket
        self.udp_socket = udp_socket

        self.client_sockets: list[socket.socket] = []
        self.client_thread_events: list[threading.Event] = []
        self.first_free_thread = -1
        self.client_count = 0

    def create_new_client_thread(self, client):
        self.client_sockets.append(client)
        self.client_count += 1

        client_idx = len(self.client_sockets) - 1
        thread = threading.Thread(target=self.handle_client, args=(client_idx, ), daemon=True)
        self.client_thread_events.append(threading.Event())
        self.client_thread_events[client_idx].set()
        thread.start()

    def add_client_to_thread(self, client):
        self.client_sockets[self.first_free_thread] = client
        self.client_count += 1
        self.client_thread_events[self.first_free_thread].set()
        free_idx = self.first_free_thread
        self.first_free_thread = -1
        for i in range(free_idx + 1, self.client_count):
            if self.client_thread_events[i].is_set():
                self.first_free_thread = i
                break

    def accept(self):
        client, addr = self.socket.accept()
        if self.first_free_thread == -1:
            self.create_new_client_thread(client)
        else:
            self.add_client_to_thread(client)

    def broadcast(self, client_idx, client_bytes):
        for i in range(self.client_count):
            if i == client_idx or not self.client_thread_events[i].is_set():
                continue
            self.client_sockets[i].send(client_bytes)

    def leave_chat(self, client_idx, client_name):
        print(f"[{client_name}] is leaving")
        msg = Message.exit_message(client_name).encode()
        self.broadcast(client_idx, msg)
        self.client_thread_events[client_idx].clear()

    def enter_chat(self, client_idx, client_name):
        print(f"[{client_name}] is entering")
        msg = Message.enter_message(client_name).encode()
        self.broadcast(client_idx, msg)
        self.client_sockets[client_idx].send(Message.welcome_message(client_name).encode())

    def handle_client(self, client_idx):
        while True:
            init_message = Message.from_bytes(self.client_sockets[client_idx].recv(Message.MAXIMUM_MESSAGE_LENGTH))
            self.enter_chat(client_idx, init_message.sender_name)

            while self.client_thread_events[client_idx].is_set():
                client_bytes = self.client_sockets[client_idx].recv(Message.MAXIMUM_MESSAGE_LENGTH).rstrip()
                client_msg = Message.from_bytes(client_bytes)

                if client_msg.state == Message.EXIT:
                    self.leave_chat(client_idx, client_msg.sender_name)
                    break

                # print(f"[{client_msg.sender_name}] broadcasts: {client_msg.message}")
                self.broadcast(client_idx, client_bytes)

            self.client_thread_events[client_idx].wait()

    def find_client_idx(self, client_addr):
        for i, client in enumerate(self.client_sockets):
            if client.getpeername() == client_addr:
                return i
        return -1

    def handle_udp_channel(self):
        while True:
            msg, addr = self.udp_socket.recvfrom(Message.MAXIMUM_MESSAGE_LENGTH)
            client_idx = self.find_client_idx(addr)
            print(msg)
            if client_idx == -1:
                continue
            self.broadcast(client_idx, msg)


def main():
    tcp_socket = None
    udp_socket = None
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind(('localhost', 8008))
        tcp_socket.listen(5)
        print("Server listening on port 8008")

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('localhost', 8008))
        server = Server(tcp_socket, udp_socket)

        threading.Thread(target=server.handle_udp_channel, daemon=True).start()
        while True:
            server.accept()

    except Exception as e:
        print(e)
    finally:
        if tcp_socket is not None:
            print("Socket closing")
            tcp_socket.close()
        if udp_socket is not None:
            print("Socket closing")


if __name__ == '__main__':
    main()
