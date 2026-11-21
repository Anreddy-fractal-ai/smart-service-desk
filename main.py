"""
main.py
-------
The "front desk" of the app (the Presentation layer).

This file ONLY does three things:
    1. show the menu,
    2. ask the user to type things,
    3. print friendly messages.

All real work is handed over to RequestService. There are no business rules
and no file handling in here - that is on purpose (Single Responsibility).

Run the app with:      python main.py
"""

import os

from application.request_service import RequestService
from domain.exceptions import InvalidInputError, ServiceDeskError
from infrastructure.file_repository import FileRepository

# EXTRA WORK: build the data-file path from the location of THIS file, so the
# app finds its data even if you start it from a different folder.
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_FOLDER, "data", "requests.json")


# ----------------------------------------------------------------------
# SCREEN HELPERS
# ----------------------------------------------------------------------
def show_menu():
    """Print the menu exactly as the assignment shows it."""
    print()
    print("SMART SERVICE DESK SYSTEM")
    print("1. Create Service Request")
    print("2. View All Requests")
    print("3. Search Request")
    print("4. Resolve Request")
    print("5. Exit")


def ask_menu_choice():
    """
    Ask for a menu number. Returns the number as a string ("1" to "5").
    Raises InvalidInputError if the user types anything else.
    """
    choice = input("Enter your choice: ").strip()

    if choice not in ("1", "2", "3", "4", "5"):
        raise InvalidInputError("Invalid choice. Please enter a number from 1 to 5.")

    return choice


def print_full_details(ticket):
    """Show every detail of one ticket (used by Search and after Resolve)."""
    print("-" * 40)
    print(f"Request ID  : {ticket.request_id}")
    print(f"Employee    : {ticket.employee_name}")
    print(f"Issue       : {ticket.issue}")
    print(f"Priority    : {ticket.priority}")
    print(f"Status      : {ticket.status}")
    print(f"Created on  : {ticket.created_on}")          # extra
    if ticket.resolved_on:
        print(f"Resolved on : {ticket.resolved_on}")     # extra
    print("-" * 40)


# ----------------------------------------------------------------------
# ONE FUNCTION PER MENU OPTION
# ----------------------------------------------------------------------
def create_flow(service):
    """Menu option 1: ask the details and create a ticket."""
    suggestion = service.next_free_id()

    # EXTRA WORK: pressing Enter without typing uses the suggested ID.
    request_id = input(f"Enter Request ID (press Enter for {suggestion}): ")
    if request_id.strip() == "":
        request_id = suggestion

    employee_name = input("Enter Employee Name: ")
    issue = input("Enter Issue: ")
    priority = input("Enter Priority (LOW / MEDIUM / HIGH): ")

    service.create_request(request_id, employee_name, issue, priority)
    print("Service Request created successfully.")


def view_flow(service):
    """Menu option 2: list every ticket, one per line."""
    tickets = service.view_requests()

    if len(tickets) == 0:
        print("No service requests yet.")
        return

    for ticket in tickets:
        print(ticket.short_line())

    # EXTRA WORK: a small summary line under the list.
    total, open_count, resolved_count = service.count_summary()
    print(f"\nTotal: {total} | Open: {open_count} | Resolved: {resolved_count}")


def search_flow(service):
    """Menu option 3: find one ticket by ID and show all details."""
    request_id = input("Enter Request ID to search: ")
    ticket = service.search_request(request_id)
    print_full_details(ticket)


def resolve_flow(service):
    """Menu option 4: resolve one ticket by ID."""
    request_id = input("Enter Request ID to resolve: ")
    ticket = service.resolve_request(request_id)
    print(f"Request {ticket.request_id} has been marked as RESOLVED.")


# ----------------------------------------------------------------------
# THE MAIN LOOP
# ----------------------------------------------------------------------
def main():
    # Wire the layers together:  file clerk -> manager -> (this screen)
    repository = FileRepository(DATA_FILE)
    service = RequestService(repository)

    # Which function runs for which menu number.
    # (A dictionary of choices is tidier than a long if / elif chain.)
    actions = {
        "1": create_flow,
        "2": view_flow,
        "3": search_flow,
        "4": resolve_flow,
    }

    while True:
        show_menu()

        try:
            choice = ask_menu_choice()

            if choice == "5":
                print("Thank you for using Smart Service Desk. Goodbye!")
                break

            actions[choice](service)

        except ServiceDeskError as problem:
            # Every expected problem (duplicate ID, not found, bad priority,
            # already resolved, bad menu input...) lands here and becomes a
            # friendly one-line message. The program keeps running.
            print(f"Oops: {problem}")

        except (KeyboardInterrupt, EOFError):
            # EXTRA WORK: Ctrl+C or end of input should exit politely,
            # not dump a scary red error.
            print("\nExiting. Your saved requests are safe. Goodbye!")
            break


# This line means: "only start the app when this file is run directly",
# not when another file merely imports it (for example, in tests).
if __name__ == "__main__":
    main()