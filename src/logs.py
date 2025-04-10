import logging
from pythonjsonlogger import jsonlogger

class YcLoggingFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(YcLoggingFormatter, self).add_fields(log_record, record, message_dict)
        log_record['logger'] = record.name
        log_record['level'] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")


logHandler = logging.StreamHandler()
logHandler.setFormatter(YcLoggingFormatter('%(message)s %(level)s %(logger)s'))

custom_logger = logging.getLogger('custom')
custom_logger.addHandler(logHandler)
custom_logger.setLevel(logging.DEBUG)