from dateutil.tz import tzutc, tzlocal

from logging.config import dictConfig


def utc_to_local(date):
    """
    Convert a naive utc datetime.datetime to a local datetime.datetime.
    """
    return date.replace(tzinfo=tzutc()).astimezone(tzlocal()).replace(tzinfo=None)


def local_to_utc(date):
    """
    Convert a naive local datetime.datetime to a utc datetime.datetime.
    """
    return date.replace(tzinfo=tzlocal()).astimezone(tzutc()).replace(tzinfo=None)



LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file_server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'poll.log',
            'mode': 'a',
            'maxBytes': 524288000, # 500 MB
            'backupCount': 50, # 50 files
        },
    },
    'loggers': {
        'poll': {
            'handlers': ['console', 'file_server'],
            'level': 'INFO',
        },
    }
}


dictConfig(LOGGING_SETTINGS)
