import logging

logger = logging.getLogger("Inkra")


class Terminal:
    """Interface for pretty terminal colours"""

    header = "\033[95m"
    good = "\033[32m"
    warning = "\033[93m"
    fail = "\033[91m"
    blue = "\033[34m"
    end_colours = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"

    class ConfigError(Exception):
        """Error in the config.yml file."""

    @classmethod
    def warn(cls, message):
        logger.warning(f"\n{cls.warning}Warning: {message}{cls.end_colours}")

    @classmethod
    def error(cls, message):
        logger.error(f"\n{cls.fail}Non-fatal error: {message}{cls.end_colours}")

    @classmethod
    def debug(cls, message):
        logger.debug(f"\n{cls.blue}DEBUG: {message}{cls.end_colours}")

    @classmethod
    def print(cls, message):
        logger.info(f"{cls.end_colours}{message}")

    @classmethod
    def fatal(cls, message):
        # It's easier on the eyes than an exception trace
        logger.error(f"\n{cls.fail}Fatal error: {message}{cls.end_colours}")
        exit(255)
