class Terminal:
    header = '\033[95m'
    good = '\033[32m'
    warning = '\033[93m'
    fail = '\033[91m'
    blue = '\033[34m'
    end_colours = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

    @classmethod
    def warn(cls, message):
        print(f"\n{cls.warning}{message}{cls.end_colours}")

    @classmethod
    def error(cls, message):
        print(f"\n{cls.fail}{message}{cls.end_colours}")

    @classmethod
    def debug(cls, message):
        print(f"\n{cls.blue}{message}{cls.end_colours}")

    @classmethod
    def print(cls, message):
        print(f"{cls.end_colours}{message}")
