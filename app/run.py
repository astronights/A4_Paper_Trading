import sys
import time
import threading
from app.controller import Controller

def run():
    try:
        controller = Controller()
        controller.register_agents()
        controller.start_agents()
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        controller.stop_agents()
        print('The server has been shutdown gracefully')
        sys.exit()