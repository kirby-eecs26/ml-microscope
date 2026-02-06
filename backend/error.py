#error.py
#Custom exceptions

class APIConnectionError(Exception):
    def __init__(self, code):
        self.message = "Microscope not found or could not connect"
        self.error_code = code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"


class CameraConnectionError(Exception):
    def __init__(self, code):
        self.message = "Microscope Camera not found or malfunction"
        self.error_code = code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"


class APIDisconnectionError(Exception):
    def __init__(self, code):
        self.message = "Microscope could not connect"
        self.error_code = code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"

class MoveMicroscopeError(Exception):
    def __init__(self):
        self.message = "Microscope couldn't move, out of bounds or motor error"
        self.error_code = 000
        super().__init__(self.message)

    def __str__(self):
        return self.message