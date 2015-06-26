class TransitionError(Exception):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        prev -- state at beginning of transition
        next -- attempted new state
    """

    def __init__(self, old_status, new_status):
        self.old_status = old_status
        self.new_status = new_status
        self.message = "New status " + new_status + " not reachable from " + old_status
