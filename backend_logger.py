from fastapi import HTTPException
from loguru import logger
from threading import get_native_id
from time import time
from typing import Callable


logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time}</green> | <level>{level}</level> | {message} | thread={extra[thread_id]}"
)


class BackendLogger:
    @staticmethod
    def get_kwargs():
        return {
            "thread_id": get_native_id(),
        }

    def handler_logger(self, service_name: str):
        def wrapper_creator(func: Callable):
            async def wrapper(*args, **kwargs):
                self.info(f"Received task to {service_name}")
                start = time()

                try:
                    result = await func(*args, **kwargs)
                except Exception as e:
                    error_text = f"{service_name} task complete with error: {e}"
                    logger.bind(**self.get_kwargs()).exception(
                        f"{service_name} task failed:"
                    )
                    raise HTTPException(500, error_text)

                execution_time = time() - start
                self.info(f"{service_name} task complete for {execution_time} seconds")
                return result

            return wrapper
        return wrapper_creator

    def info(self, message: str):
        logger.bind(**self.get_kwargs()).info(message)

    def debug(self, message: str):
        logger.bind(**self.get_kwargs()).debug(message)

    def error(self, message: str):
        logger.bind(**self.get_kwargs()).error(message)

    def warning(self, message: str):
        logger.bind(**self.get_kwargs()).warning(message)


Logger = BackendLogger()
