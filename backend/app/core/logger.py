import logging
import json


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def info(self, **kwargs):
        self.logger.info(json.dumps(kwargs))

    def error(self, **kwargs):
        self.logger.error(json.dumps(kwargs))
