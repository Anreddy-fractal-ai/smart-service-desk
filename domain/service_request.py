"""
domain/service_request.py

This file holds the ServiceRequest class - the HEART of the whole project.

WHY IS THIS IN THE "DOMAIN" LAYER?
    "Domain" means "the real-world business idea". In a real help desk, a
    support ticket is a thing that has an ID, an employee, a problem, a
    priority and a status - and it can be resolved. That is pure business
    knowledge. It has nothing to do with menus, screens or files, so it lives
    in the domain layer and does NOT know that JSON files even exist.

    Rule of thumb:  if you can explain it to a non-programmer manager,
                    it belongs in the domain.
"""

from datetime import datetime

from domain.exceptions import AlreadyResolvedError, InvalidPriorityError


# The only values the business allows. Keeping them in one place means that
# if the company adds "URGENT" tomorrow, we change just ONE line.

ALLOWED_PRIORITIES = ("LOW", "MEDIUM", "HIGH")

STATUS_OPEN = "OPEN"
STATUS_RESOLVED = "RESOLVED"

# EXTRA WORK: a simple, readable date-time format for our time stamps.
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def clean_priority(text):
    """
    Turn whatever the user typed into a proper priority word.

        "high"   -> "HIGH"     (we forgive small/capital letter mistakes)
        " Low "  -> "LOW"      (we forgive extra spaces)
        "urgent" -> raises InvalidPriorityError

    Business rule: only LOW, MEDIUM or HIGH are allowed.
    """
    # .strip() removes spaces at both ends, .upper() makes ALL CAPITALS.
    # If text is None we use an empty string so the code does not crash.
    word = (text or "").strip().upper()

    if word not in ALLOWED_PRIORITIES:
        raise InvalidPriorityError("Priority must be LOW, MEDIUM or HIGH")

    return word


class ServiceRequest:
    """
    One support ticket raised by an employee.

    Example:
        ticket = ServiceRequest("SR101", "shannu", "Laptop is not starting", "HIGH")
        ticket.resolve()          # status becomes RESOLVED
    """

    def __init__(self, request_id, employee_name, issue, priority,
                 status=STATUS_OPEN, created_on=None, resolved_on=None):
        """
        The CONSTRUCTOR. Python runs this automatically the moment we write
        ServiceRequest(...). Its job is to fill the ticket's fields.

        The first four values are the ones the assignment asks for.
        The last three have default values, so:
          - a brand new ticket automatically starts as OPEN, and
          - when we LOAD an old ticket from the file we can pass in its
            saved status and dates.
        """
        self.request_id = request_id.strip().upper()   # "sr101" becomes "SR101"
        self.employee_name = employee_name.strip()
        self.issue = issue.strip()

        # clean_priority() checks the value. A bad priority stops right here,
        # so a ticket with a wrong priority can NEVER exist in our program.
        self.priority = clean_priority(priority)

        self.status = status

        # EXTRA WORK: remember when the ticket was raised and when it was fixed.
        # If no time was given, the ticket is new, so "now" is its birth time.
        self.created_on = created_on or datetime.now().strftime(TIME_FORMAT)
        self.resolved_on = resolved_on        # stays None until resolved

    
    # BEHAVIOUR (what a ticket can DO)
    
    def is_open(self):
        """Quick yes/no helper: is this ticket still waiting to be fixed?"""
        return self.status == STATUS_OPEN

    def resolve(self):
        """
        THE BUSINESS RULE:   OPEN  ->  RESOLVED

        This is the ONLY place in the whole project where a ticket's status
        is changed. Nobody else is allowed to write  ticket.status = ...
        That is called "encapsulation": the object protects its own rules.

        If the ticket is already RESOLVED we refuse and raise an error
        (a resolved ticket cannot be resolved twice).
        """
        if self.status == STATUS_RESOLVED:
            raise AlreadyResolvedError(
                f"Request {self.request_id} is already RESOLVED."
            )

        self.status = STATUS_RESOLVED
        self.resolved_on = datetime.now().strftime(TIME_FORMAT)

    
    # CONVERTING to / from a plain dictionary
    
    # JSON can only store simple things (text, numbers, lists, dictionaries).
    # It cannot store a "ServiceRequest object" directly. So the object
    # offers a way to turn itself into a dictionary and back.
    # NOTE: this only reshapes data. It does NOT touch any file - file work
    # belongs to the infrastructure layer.
    def to_dict(self):
        """Pack this ticket into a plain dictionary (ready for JSON)."""
        return {
            "request_id": self.request_id,
            "employee_name": self.employee_name,
            "issue": self.issue,
            "priority": self.priority,
            "status": self.status,
            "created_on": self.created_on,
            "resolved_on": self.resolved_on,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Rebuild a ticket from a dictionary that was read from JSON.
        (@classmethod means we call it on the class itself:
            ServiceRequest.from_dict({...}) )
        """
        return cls(
            request_id=data["request_id"],
            employee_name=data["employee_name"],
            issue=data["issue"],
            priority=data["priority"],
            status=data.get("status", STATUS_OPEN),
            created_on=data.get("created_on"),
            resolved_on=data.get("resolved_on"),
        )

    
    # PRINTING
    
    def short_line(self):
        """One line in the exact format the assignment shows for 'View All'."""
        return (f"{self.request_id} | {self.employee_name} | {self.issue} | "
                f"{self.priority} | {self.status}")

    def __str__(self):
        """What print(ticket) shows. We reuse the short line."""
        return self.short_line()