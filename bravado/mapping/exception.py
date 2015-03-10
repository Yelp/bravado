class SwaggerMappingError(Exception):
    """Raised when an error is encountered."""

    def __init__(self, msg, cause=None):
        """
        :param msg: String message for the error.
        :param cause: Optional exception that caused this one.
        """
        super(Exception, self).__init__(msg, cause)
