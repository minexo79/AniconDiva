from logging.config import dictConfig

def log_init(debug = False):
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] [%(module)s] [%(levelname)s]: %(message)s',
            },
        },  
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            },
        },
        'root': {
            'handlers': ['wsgi'],
            'level': 'INFO' if debug else 'WARNING',
        },
    })