"""
tests/test_service_desk.py

EXTRA WORK: automatic tests.

A test is a small program that checks our app behaves correctly, so we do
not have to click through the menu by hand every time.

Run them from the project folder with:
        python -m unittest discover -s tests -t . -v

Every test uses a TEMPORARY file, so your real data/requests.json is never touched.
"""

import os
import tempfile
import unittest

from application.request_service import RequestService
from domain.exceptions import (
    AlreadyResolvedError,
    DuplicateRequestError,
    InvalidInputError,
    InvalidPriorityError,
    RequestNotFoundError,
)
from domain.service_request import ServiceRequest
from infrastructure.file_repository import FileRepository


class ServiceRequestTests(unittest.TestCase):
    """Tests for the ticket itself (domain layer)."""

    def test_new_ticket_starts_open(self):
        ticket = ServiceRequest("SR101", "shannu", "Laptop is not starting", "HIGH")
        self.assertEqual(ticket.status, "OPEN")

    def test_resolve_changes_status(self):
        ticket = ServiceRequest("SR101", "shannu", "Laptop is not starting", "HIGH")
        ticket.resolve()
        self.assertEqual(ticket.status, "RESOLVED")
        self.assertIsNotNone(ticket.resolved_on)

    def test_resolving_twice_is_refused(self):
        ticket = ServiceRequest("SR101", "shannu", "Laptop is not starting", "HIGH")
        ticket.resolve()
        with self.assertRaises(AlreadyResolvedError):
            ticket.resolve()

    def test_bad_priority_is_refused(self):
        with self.assertRaises(InvalidPriorityError):
            ServiceRequest("SR101", "abhi", "Wi-Fi issue", "URGENT")

    def test_priority_is_forgiving_about_case_and_spaces(self):
        ticket = ServiceRequest("sr7", "jay", "Password reset", "  low ")
        self.assertEqual(ticket.priority, "LOW")
        self.assertEqual(ticket.request_id, "SR7")


class ServiceDeskTests(unittest.TestCase):
    """Tests for the use cases + file saving (application + infrastructure)."""

    def setUp(self):
        # Runs before EVERY test: make a fresh temporary folder and service.
        self.folder = tempfile.mkdtemp()
        self.file_path = os.path.join(self.folder, "requests.json")
        self.service = RequestService(FileRepository(self.file_path))

    def restart_app(self):
        """Pretend the app was closed and opened again (reads the file afresh)."""
        return RequestService(FileRepository(self.file_path))

    def test_create_and_view(self):
        self.service.create_request("SR101", "shannu", "Laptop is not starting", "HIGH")
        self.service.create_request("SR102", "abhi", "Wi-Fi issue", "MEDIUM")
        self.assertEqual(len(self.service.view_requests()), 2)

    def test_duplicate_id_is_refused(self):
        self.service.create_request("SR101", "shannu", "Laptop is not starting", "HIGH")
        with self.assertRaises(DuplicateRequestError):
            self.service.create_request("sr101", "jay", "Other issue", "LOW")

    def test_search_unknown_id(self):
        with self.assertRaises(RequestNotFoundError):
            self.service.search_request("SR999")

    def test_empty_fields_are_refused(self):
        with self.assertRaises(InvalidInputError):
            self.service.create_request("SR1", "   ", "Issue", "LOW")

    def test_persistence_after_restart(self):
        # The assignment's own "persistence test".
        self.service.create_request("SR101", "sha", "VPN not connecting", "HIGH")
        self.service.resolve_request("SR101")

        reopened = self.restart_app()
        ticket = reopened.search_request("SR101")
        self.assertEqual(ticket.status, "RESOLVED")
        self.assertEqual(ticket.employee_name, "sha")

    def test_missing_file_is_safe(self):
        self.assertEqual(self.service.view_requests(), [])

    def test_empty_file_is_safe(self):
        with open(self.file_path, "w") as file:
            file.write("")
        self.assertEqual(self.restart_app().view_requests(), [])

    def test_broken_file_is_safe_and_backed_up(self):
        with open(self.file_path, "w") as file:
            file.write("{this is not json")
        self.assertEqual(self.restart_app().view_requests(), [])
        self.assertTrue(os.path.exists(self.file_path + ".broken"))

    def test_next_free_id(self):
        self.assertEqual(self.service.next_free_id(), "SR101")
        self.service.create_request("SR101", "jay", "Password reset", "LOW")
        self.assertEqual(self.service.next_free_id(), "SR102")

    def test_count_summary(self):
        self.service.create_request("SR101", "shannu", "A", "LOW")
        self.service.create_request("SR102", "abhi", "B", "LOW")
        self.service.resolve_request("SR102")
        self.assertEqual(self.service.count_summary(), (2, 1, 1))


if __name__ == "__main__":
    unittest.main()