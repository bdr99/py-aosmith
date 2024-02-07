class AOSmithInvalidCredentialsException(Exception):
    """Raised when login fails due to invalid credentials"""

    def __init__(self, status):
        """Initialize exception"""
        super(AOSmithInvalidCredentialsException, self).__init__(status)
        self.status = status

class AOSmithInvalidParametersException(Exception):
    """Raised when invalid parameters are passed to the client library"""

    def __init__(self, status):
        """Initialize exception"""
        super(AOSmithInvalidParametersException, self).__init__(status)
        self.status = status

class AOSmithEnergyUsageDataUnavailableException(Exception):
    """Raised when there is no energy usage data available, such as when the device is newly installed. Only used internally."""

    def __init__(self, status):
        """Initialize exception"""
        super(AOSmithEnergyUsageDataUnavailableException, self).__init__(status)
        self.status = status

class AOSmithUnknownException(Exception):
    """Raised when an unknown error occurs"""

    def __init__(self, status):
        """Initialize exception"""
        super(AOSmithUnknownException, self).__init__(status)
        self.status = status
