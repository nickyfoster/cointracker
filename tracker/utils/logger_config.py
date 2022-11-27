import multiprocessing
import os
from pathlib import Path

from tracker.utils.utils import get_config, create_dir

formatter = f'%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message).2000s'

LOG_DIR = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute() / "logs"
create_dir(LOG_DIR)

config = get_config().logging
queue = multiprocessing.Queue(0)

LOG_CONFIG = {'version': 1,
              'disable_existing_loggers': False,
              'objects': {
                  'queue': queue},
              'formatters': {
                  'default': {
                      'format': formatter}},
              'handlers': {
                  'console': {
                      'class': 'logging.StreamHandler',
                      'level': config.console_logging_level,
                      'formatter': 'default',
                      'stream': 'ext://sys.stdout'},
                  'file': {
                      'class': 'tracker.utils.utils.CustomRotatingFileHandler',
                      'level': config.file_logging_level,
                      'formatter': 'default',
                      'filename': os.path.join(LOG_DIR, 'app.main.log'),
                      'mode': 'a',
                      'maxBytes': 5000000,
                      'backupCount': 5},
                  'queue_listener': {
                      'class': 'tracker.services.QueueListenerHandler.QueueListenerHandler',
                      'handlers': ['cfg://handlers.file'],
                      'queue': 'cfg://objects.queue'}
              },
              'root': {
                  'level': config.root_logging_level,
                  'handlers': ['console', 'file']}
              }
