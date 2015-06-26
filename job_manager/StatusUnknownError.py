class StatusUnknownError(Exception):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        prev -- state at beginning of transition
        next -- attempted new state
    """

    def __init__(self, status):
        self.status = status
        self.message = "Status " + status + " not known"
