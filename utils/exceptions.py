class NotFound(Exception):
    """Exception raised for not found errors."""
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)