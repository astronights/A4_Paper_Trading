from app import run
import sys
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__=='__main__':
    logging.info(f'Starting app')
    run.run()