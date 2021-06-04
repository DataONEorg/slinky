class UnsupportedFormatException(Exception):
    pass


class UnsupportedPackageScenario(Exception):
    pass


class CursorSetFailedException(Exception):
    pass


class ProcessingException(Exception):
    pass


class ChecksumAlgorithmNotSupportedException(ProcessingException):
    pass


class CLIException(Exception):
    pass


class SerializationFormatNotSupported(CLIException):
    pass
