
class Message:
    MAXIMUM_MESSAGE_LENGTH = 2 ** 16 - 1

    # Message states
    EXIT = 0
    ENTER = 1
    NORMAL = 255

    def __init__(self, sender_name: str, message: str, state=255):
        self.sender_name = sender_name
        self.message = message
        self._msg_start = len(self.sender_name)

        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state not in [Message.EXIT, Message.ENTER]:
            self._state = Message.NORMAL
            return
        self._state = state

    @classmethod
    def exit_message(cls, sender_name: str):
        return cls("Server", f"{sender_name} has left the chat")

    @classmethod
    def enter_message(cls, sender_name: str):
        return cls("Server", f"{sender_name} has entered the chat")

    @classmethod
    def welcome_message(cls, sender_name: str):
        return cls("Server", f"Welcome to the chat {sender_name}!")

    @classmethod
    def initial_message(cls, sender_name: str):
        return cls(sender_name, "", state=Message.ENTER)

    @classmethod
    def leaving_message(cls, sender_name: str):
        return cls(sender_name, "", state=Message.EXIT)

    @classmethod
    def from_bytes(cls, msg_bytes):
        offset_size = 3 # offset + state
        msg_start = int.from_bytes(msg_bytes[:offset_size - 1], byteorder='big')
        state = int.from_bytes(msg_bytes[offset_size - 1:offset_size], byteorder='big')
        sender_name = str(msg_bytes[offset_size:msg_start + offset_size], encoding='utf-8')
        message = str(msg_bytes[msg_start + offset_size:], encoding='utf-8')
        return cls(sender_name, message, state)

    def encode(self, charset="utf-8", int_byteorder="big") -> bytes:
        return (
                self._msg_start.to_bytes(2, byteorder=int_byteorder) +
                self._state.to_bytes(1, byteorder=int_byteorder) +
                bytes(self.sender_name, charset) +
                bytes(self.message, charset)
        )

    def print(self):
        print(f"[{self.sender_name}]: {self.message}")
