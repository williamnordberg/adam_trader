import logging

# silence google module loggers
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google_auth_httplib2').setLevel(logging.WARNING)
logging.getLogger('oauth2client').setLevel(logging.WARNING)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class UTF8FileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    handlers=[logging.StreamHandler(), UTF8FileHandler('logs/app.log')],
                    datefmt='%Y-%m-%d %H:%M:%S')


def do_nothing():
    return
