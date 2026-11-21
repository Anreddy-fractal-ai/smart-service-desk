"""
domain/exceptions.py

All the "something went wrong" messages of our app live here.

Think of an exception like a red flag a worker raises:
    "Stop! This is a problem and I cannot continue."
Somebody higher up (the menu in main.py) catches the flag and shows
a friendly message to the user instead of letting the program crash.

We create our OWN named exceptions (instead of using plain Exception)
so that the code reads like English:
    raise RequestNotFoundError(...)   <- instantly clear what went wrong.
"""


class ServiceDeskError(Exception):
    """
    The 'parent' of all our custom errors.

    Why have a parent? So main.py can catch every service-desk problem
    with ONE line (except ServiceDeskError) if it wants to.
    Every error below "inherits" from this one.
    """
    pass


class RequestNotFoundError(ServiceDeskError):
    """Raised when someone searches / resolves an ID that does not exist."""
    pass


class DuplicateRequestError(ServiceDeskError):
    """Raised when someone tries to create an ID that is already taken."""
    pass


class InvalidPriorityError(ServiceDeskError):
    """Raised when priority is anything other than LOW, MEDIUM or HIGH."""
    pass


class AlreadyResolvedError(ServiceDeskError):
    """Raised when someone tries to resolve a request that is already RESOLVED."""
    pass


class InvalidInputError(ServiceDeskError):
    """
    Raised for bad typing by the user, for example:
      - an empty Request ID
      - a menu choice that is not 1 to 5
    """
    pass