"""
infrastructure/file_repository.py

This file is the app's "filing cabinet clerk".

Its ONE job: read tickets from the JSON file and write tickets to the JSON file.
It does not know any business rules (like OPEN -> RESOLVED) and it does not
print anything for the user.

WHY IS FILE HANDLING KEPT OUTSIDE THE DOMAIN CLASS?
    Imagine tomorrow the company wants to store tickets in a database instead
    of a JSON file. If ServiceRequest opened files itself, we would have to
    rewrite the business class. Because the file work lives HERE, we only
    swap this one file and the rest of the app stays untouched.
    (This is the "Dependency Inversion" idea from SOLID: the important code
    does not depend on the technical details.)
"""

import json
import os

from domain.service_request import ServiceRequest

# Default place where tickets are saved (the path the assignment asks for).
DEFAULT_FILE_PATH = os.path.join("data", "requests.json")


class FileRepository:
    """Reads and writes the list of ServiceRequest objects to a JSON file."""

    def __init__(self, file_path=DEFAULT_FILE_PATH):
        # We receive the path from outside so tests can use a throw-away file
        # instead of touching the real data.
        self.file_path = file_path

    
    # LOAD  (file -> list of tickets)
   
    def load_all(self):
        """
        Read every ticket from the file and return them as a list.

        Safe against the three "bad file" situations:
          1. File is missing        -> return an empty list (fresh start)
          2. File is empty          -> return an empty list
          3. File is damaged/broken -> keep a backup copy, return empty list
        so the program never crashes just because of the file.
        """
        # Situation 1: no file yet (e.g. very first run).
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Situation 2: file exists but contains nothing (or only spaces).
        if text.strip() == "":
            return []

        # Situation 3: the text is not valid JSON.
        try:
            raw_list = json.loads(text)
            return [ServiceRequest.from_dict(item) for item in raw_list]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError):
            # EXTRA WORK: don't silently destroy the user's broken data.
            # Move it aside to  requests.json.broken  so it can be inspected.
            os.replace(self.file_path, self.file_path + ".broken")
            return []

   
    # SAVE  (list of tickets -> file)
   
    def save_all(self, requests):
        """
        Write the whole list of tickets into the file.

        EXTRA WORK - "safe save":
        We first write into a temporary file, and only when that finished
        successfully do we swap it in place of the real file. If the
        computer crashes half-way, the old good file is still intact
        (instead of being left half-written and corrupted).
        """
        # Make sure the "data" folder exists (so save never fails because
        # the folder was deleted).
        folder = os.path.dirname(self.file_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        # Turn every ServiceRequest object into a plain dictionary.
        plain_list = [one.to_dict() for one in requests]

        temp_path = self.file_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            # indent=2 makes the JSON easy for humans to read.
            json.dump(plain_list, file, indent=2)

        # os.replace swaps the temp file in as the real one in a single step.
        os.replace(temp_path, self.file_path)