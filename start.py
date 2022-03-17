from app import run
import sys
import logging

if __name__=='__main__':
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.info(f'Starting app...')
    run.run()