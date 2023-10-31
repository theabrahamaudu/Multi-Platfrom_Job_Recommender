"""
Configuration module for model building pipeline logs
"""

import logging
from logging import Logger


def logger_pipeline() -> Logger:
    """Format logger, configure file handler, stream handler and add handlers
    for pipeline logger.

    Returns:
        Logger: Logger for model building pipeline
    """
    pipeline_logger = logging.getLogger(__name__)
    pipeline_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s:')

    pipeline_file_handler = logging.FileHandler('./backend/logs/pipeline.log')
    pipeline_file_handler.setLevel(logging.DEBUG)
    pipeline_file_handler.setFormatter(formatter)
    pipeline_logger.addHandler(pipeline_file_handler)

    pipeline_stream_handler = logging.StreamHandler()
    pipeline_stream_handler.setLevel(logging.DEBUG)
    pipeline_stream_handler.setFormatter(formatter)
    pipeline_logger.addHandler(pipeline_stream_handler)

    return pipeline_logger


pipeline = logger_pipeline()