class BaseDict:
    """Base class for dictionary models."""
    def __init__(self, label: str, pending_request: bool = False):
        self.label = label
        self.pending_request = pending_request

class DefaultDict:
    """Default dictionary for various statuses and tags."""
    OperateDict = {
        1: BaseDict('pending'),
        2: BaseDict('approved'),
        3: BaseDict('rejected'),
        4: BaseDict('deleted')
    }

    TagDict = {
        1: BaseDict('無', True),
    }