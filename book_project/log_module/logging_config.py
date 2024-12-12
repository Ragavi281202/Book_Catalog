import logging
from decouple import config
import json
import traceback
from datetime import datetime

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.environment = config('ENVIRONMENT',default='dev')
        record.application = config('APPLICATION',default='Bookcatalog')
        if hasattr(record, 'taskName') and record.taskName is None:
            del record.taskName
        return True
    
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'environment': getattr(record, 'environment', 'dev'),
            'application': getattr(record, 'application', 'BookCatalog'),
        }

        if record.exc_info:
            log_record['traceback'] = self.format_exception(record.exc_info)

        return json.dumps(log_record)
    
    def format_exception(self, exc_info):
        return ''.join(traceback.format_exception(*exc_info))
    
def setup_logging():
    environment = config('ENVIRONMENT', default='dev')  
    application= config('APPLICATION', default='BookCatalog')

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.addFilter(ContextFilter())

    custom_logger = logging.getLogger('custom_logger')
    custom_logger.setLevel(logging.INFO) 
    custom_logger.addHandler(handler)

    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.WARNING)  
    urllib3_logger.addHandler(handler)

    matplotlib_logger = logging.getLogger('matplotlib')
    matplotlib_logger.setLevel(logging.WARNING)  
    matplotlib_logger.addHandler(handler)

    return custom_logger

