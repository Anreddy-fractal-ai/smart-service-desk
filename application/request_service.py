"""
application/request_service.py

This file is the "manager" of the app. It knows WHAT the app can do
(the use cases), but not HOW tickets are stored and not HOW things are shown.

    main.py (screen)  ->  RequestService (manager)  ->  FileRepository (filing clerk)
                                   |
                                   +-> ServiceRequest (the ticket itself)

The four use cases the assignment asks for:
    create_request(), view_requests(), search_request(), resolve_request()
plus two small extras (next_free_id and count_summary).

WHY DOES THIS CLASS NOT IMPORT FileRepository?
    The repository is handed to us from outside (see __init__). We only
    expect it to have two abilities: load_all() and save_all(). Whoever
    provides those two abilities can be plugged in - a JSON file today,
    a database tomorrow. That is Dependency Inversion in simple words.
"""

from domain.exceptions import (
    DuplicateRequestError,
    InvalidInputError,
    RequestNotFoundError,
)
from domain.service_request import ServiceRequest, STATUS_OPEN, STATUS_RESOLVED


class RequestService:
    """Coordinates the work: creating, listing, finding and resolving tickets."""

    def __init__(self, repository):
        # The "filing clerk" we were given.
        self.repository = repository

        # As soon as the service starts we load all saved tickets into memory.
        # We keep them in a dictionary: { "SR101": <ticket>, "SR102": <ticket> }
        # A dictionary lets us find a ticket by its ID instantly.
        self.tickets = {}
        for ticket in self.repository.load_all():
            self.tickets[ticket.request_id] = ticket

    
    # USE CASE 1: create a request
    
    def create_request(self, request_id, employee_name, issue, priority):
        """
        Make a new ticket, store it and save to the file.

        Business rules checked here:
          - the ID, name and issue must not be empty
          - the same ID cannot be used twice  (DuplicateRequestError)
          - the priority must be valid        (checked inside ServiceRequest)
        """
        # Check for empty typing first, so we can give a clear message.
        if not request_id.strip():
            raise InvalidInputError("Request ID cannot be empty.")
        if not employee_name.strip():
            raise InvalidInputError("Employee name cannot be empty.")
        if not issue.strip():
            raise InvalidInputError("Issue description cannot be empty.")

        # "sr101", "SR101" and " sr101 " must all count as the same ID.
        clean_id = request_id.strip().upper()

        if clean_id in self.tickets:
            raise DuplicateRequestError(
                f"Request ID {clean_id} already exists. Please use a different ID."
            )

        # Building the ServiceRequest also validates the priority.
        # (A new ticket automatically gets the status OPEN.)
        new_ticket = ServiceRequest(clean_id, employee_name, issue, priority)

        self.tickets[clean_id] = new_ticket
        self._save()            # assignment rule: save right after creating
        return new_ticket

    
    # USE CASE 2: view all requests
    
    def view_requests(self):
        """Return every ticket as a list (no sorting or filtering needed)."""
        return list(self.tickets.values())

    
    # USE CASE 3: search one request by ID
    
    def search_request(self, request_id):
        """Find one ticket by its ID or raise RequestNotFoundError."""
        clean_id = request_id.strip().upper()

        if clean_id not in self.tickets:
            raise RequestNotFoundError(f"Request {clean_id} not found.")

        return self.tickets[clean_id]

    
    # USE CASE 4: resolve a request
    
    def resolve_request(self, request_id):
        """
        Mark a ticket as RESOLVED and save.

        Notice: we do NOT change the status here ourselves.
        We ask the ticket to do it: ticket.resolve()
        The OPEN -> RESOLVED rule lives in the domain class, not here.
        """
        ticket = self.search_request(request_id)   # raises error if not found
        ticket.resolve()                           # raises error if already resolved
        self._save()                               # assignment rule: save after resolving
        return ticket

    
    # EXTRA WORK helpers (not required by the assignment)
    
    def next_free_id(self):
        """
        Suggest the next unused ID, e.g. if SR101 and SR102 exist -> "SR103".
        The menu uses this when the user just presses Enter on Request ID.
        """
        highest = 100       # so the very first suggestion becomes SR101
        for existing_id in self.tickets:
            # Only look at IDs shaped like "SR" + number.
            number_part = existing_id[2:]
            if existing_id.startswith("SR") and number_part.isdigit():
                highest = max(highest, int(number_part))
        return f"SR{highest + 1}"

    def count_summary(self):
        """Return (total, open_count, resolved_count) for the 'View All' footer."""
        total = len(self.tickets)
        open_count = sum(1 for t in self.tickets.values() if t.status == STATUS_OPEN)
        resolved_count = sum(1 for t in self.tickets.values() if t.status == STATUS_RESOLVED)
        return total, open_count, resolved_count

    
    # PRIVATE helper (the leading underscore means "for internal use only")
    
    def _save(self):
        """Hand the current list of tickets to the filing clerk to write down."""
        self.repository.save_all(self.view_requests())