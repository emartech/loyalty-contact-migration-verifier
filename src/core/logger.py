# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: MIT

class Logger:
    def __init__(self, log_path):
        self.log_path = log_path
        self._buffer = []
        self._buffer_size = 0
        self._max_buffer_size = 1000  # Buffer up to 1000 messages for efficiency

    def log(self, message):
        if isinstance(message, list):
            message = "; ".join(message)
        
        # For large files, use buffering to improve performance
        self._buffer.append(message)
        self._buffer_size += 1
        
        # Flush buffer when it gets large or when explicitly requested
        if self._buffer_size >= self._max_buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        """Write all buffered messages to file."""
        if self._buffer:
            with open(self.log_path, 'a', encoding='utf-8') as log_file:
                for message in self._buffer:
                    log_file.write(message + '\n')
            self._buffer.clear()
            self._buffer_size = 0

    def flush_if_possible(self):
        """Public method to flush buffer - used for memory management."""
        self._flush_buffer()

    def __del__(self):
        """Ensure buffer is flushed when logger is destroyed."""
        try:
            self._flush_buffer()
        except:
            pass  # Ignore errors during cleanup
