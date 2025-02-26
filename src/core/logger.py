class Logger:
    def __init__(self, log_path):
        self.log_path = log_path

    def log(self, message):
        if isinstance(message, list):
            message = "; ".join(message)
        with open(self.log_path, 'a') as log_file:
            log_file.write(message + '\n')
