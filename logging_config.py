import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('app.log')],
                    datefmt='%Y-%m-%d %H:%M:%S')  # date format without milliseconds

def do_nothing():
    return

