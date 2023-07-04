import logging

logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google_auth_httplib2').setLevel(logging.WARNING)
logging.getLogger('oauth2client').setLevel(logging.WARNING)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('logs/app.log')],
                    datefmt='%Y-%m-%d %H:%M:%S')  # date format without milliseconds


def do_nothing():
    return

