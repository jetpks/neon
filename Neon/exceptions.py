import logging
import traceback

class NeonInstallFail(Exception):
    def __init__(self, message):
        logging.error(traceback.print_exc())
