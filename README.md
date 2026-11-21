# Smart Service Desk

A small command-line help-desk app written in Python. Support staff can **create, view, search and resolve** IT service requests, and everything is **saved in a JSON file** so nothing is lost when the program is closed.

---

## 1. The problem in simple words

In a company, employees face problems like "my laptop won't start" or "I forgot my password". Today these requests are written down manually, which is slow and easy to lose. This app replaces that manual notebook with a simple program:

- a staff member types in a new request,
- the request stays saved even after the program is closed,
- later someone can find it by its ID and mark it as **RESOLVED**.

---

## 2. Features

### Required by the assignment

| # | Feature | What it does |
|---|---------|--------------|
| 1 | Create Service Request | Asks for ID, employee name, issue, priority. Status is set to `OPEN` automatically. A duplicate ID shows a friendly error. |
| 2 | View All Requests | Prints every request as `ID \| Name \| Issue \| Priority \| Status`. |
| 3 | Search Request | Finds one request by ID and shows all details, or says "not found". |
| 4 | Resolve Request | Changes `OPEN` to `RESOLVED` and saves. If already resolved, shows a message. |
| 5 | Exit | Closes the program. |
| - | Persistence | Everything is stored in `data/requests.json` and reloaded on start. |

### Extra work (added on top of the assignment)

Everything below is **not asked for** in the assignment. It was added to make the app more friendly and reliable. The required menu is unchanged (still options 1 to 5).

| Extra | Where | Why it is useful |
|-------|-------|------------------|
| Auto-suggested Request ID | `request_service.py` (`next_free_id`), `main.py` | While creating a request, just press **Enter** on the ID question and the app suggests the next free one (SR101, SR102...). |
| Forgiving input | `service_request.py` | `sr101`, `SR101` and ` sr101 ` are treated as the same ID. `high`, `High`, `HIGH` all work for priority. |
| Empty-input check | `request_service.py` | A blank ID, name or issue is refused with a clear message. |
| Time stamps | `service_request.py` | Each request remembers **when it was created** and **when it was resolved**. Shown in Search. |
| Summary line | `request_service.py` (`count_summary`), `main.py` | After "View All" you see `Total: 3 \| Open: 2 \| Resolved: 1`. |
| Safe saving | `file_repository.py` | The file is written to a temporary file first and then swapped in. A crash during saving cannot leave a half-written, broken data file. |
| Broken-file recovery | `file_repository.py` | If `requests.json` is damaged, the app does not crash. It renames the bad file to `requests.json.broken` (so nothing is lost) and starts fresh. |
| Path that always works | `main.py` | The data file location is calculated from where `main.py` lives, so the app works even if you start it from another folder. |
| Polite Ctrl+C | `main.py` | Pressing Ctrl+C exits with a friendly message instead of a scary error. |
| Automatic tests | `tests/` | 15 unit tests check the rules automatically (see section 7). |

---

## 3. Project folder structure

```
smart-service-desk/
|-- domain/                      <- the BUSINESS idea (no files, no screens)
|   |-- service_request.py       <- ServiceRequest class: fields + resolve() rule
|   `-- exceptions.py            <- all our custom errors
|-- application/                 <- WHAT the app can do (the manager)
|   `-- request_service.py       <- create / view / search / resolve use cases
|-- infrastructure/              <- HOW things are stored (technical details)
|   `-- file_repository.py       <- reads and writes the JSON file
|-- data/
|   `-- requests.json            <- where requests are saved
|-- tests/
|   `-- test_service_desk.py     <- extra: automatic tests
|-- main.py                      <- the menu: input and output only
|-- README.md
`-- .gitignore
```

(The empty `__init__.py` files inside the folders simply tell Python "this folder is a package". They contain no code.)

### How the pieces talk to each other

```
 You (keyboard)
      |
   main.py            shows menu, reads typing, prints messages
      |
 RequestService       the manager: runs the use cases
    |        |
    |   FileRepository     the filing clerk: reads/writes requests.json
    |
 ServiceRequest        the ticket itself: holds data + the resolve() rule
```

Each layer only talks to the one below it. `ServiceRequest` knows nothing about files or menus.

---

## 4. How to run

Requirements: Python 3.8 or newer. No extra libraries to install.

```bash
cd smart-service-desk
python main.py
```

On some systems the command is `python3 main.py`.

### Example session (using sample names)

```
SMART SERVICE DESK SYSTEM
1. Create Service Request
2. View All Requests
3. Search Request
4. Resolve Request
5. Exit
Enter your choice: 1
Enter Request ID (press Enter for SR101): SR101
Enter Employee Name: shannu
Enter Issue: Laptop is not starting
Enter Priority (LOW / MEDIUM / HIGH): HIGH
Service Request created successfully.
```

Sample data you can use to try the app:

| Request ID | Employee | Issue | Priority |
|-----------|----------|-------|----------|
| SR101 | shannu | Laptop is not starting | HIGH |
| SR102 | abhi | Wi-Fi keeps disconnecting | MEDIUM |
| SR103 | jay | Need password reset | LOW |
| SR104 | sha | VPN is not connecting | HIGH |

### The mandatory demonstration, step by step

1. Create `SR101` (shannu, HIGH)
2. Create `SR101` again -> `Oops: Request ID SR101 already exists. Please use a different ID.`
3. View all requests (option 2)
4. Search `SR101` (option 3)
5. Resolve `SR101` (option 4)
6. Resolve `SR101` again -> `Oops: Request SR101 is already RESOLVED.`
7. Exit (option 5) and start again with `python main.py`
8. Search `SR101` -> status is still `RESOLVED` (proof of persistence)
9. Show Git: `git branch`, `git log --oneline --graph --all`

---

## 5. Concepts used (explained simply)

### OOP (Object-Oriented Programming)
We model the real world with **classes**. `ServiceRequest` is a class (a blueprint); each actual ticket such as "shannu's laptop problem" is an **object** made from it.
- **Constructor** (`__init__`): fills in a new ticket's fields.
- **Attributes**: `request_id`, `employee_name`, `issue`, `priority`, `status`, ...
- **Methods**: things a ticket can do, like `resolve()` and `is_open()`.
- **Encapsulation**: the status change lives *inside* the ticket (`ticket.resolve()`). No other file writes `ticket.status = ...` directly, so the rule cannot be bypassed.

### Exception handling
When something goes wrong, the code *raises* a named error and the menu *catches* it and prints a friendly message. The app never crashes for expected problems.

| Problem | Exception | Message shown |
|---------|-----------|---------------|
| Same ID twice | `DuplicateRequestError` | Request ID SR101 already exists... |
| ID not found | `RequestNotFoundError` | Request SR999 not found. |
| Bad priority | `InvalidPriorityError` | Priority must be LOW, MEDIUM or HIGH |
| Resolving twice | `AlreadyResolvedError` | Request SR101 is already RESOLVED. |
| Bad menu input / empty field | `InvalidInputError` | Invalid choice. Please enter a number from 1 to 5. |

All of them inherit from one parent, `ServiceDeskError`, so `main.py` catches them with a single `except ServiceDeskError`. We never use a bare `except:`.

### File handling and persistence
Requests are stored as a list in `data/requests.json`.
- Loaded when the program **starts**.
- Saved right after **creating** and right after **resolving**.
- A missing file, an empty file, or a damaged file is handled safely (see Extra work).

### SOLID (focus: Single Responsibility and Dependency Inversion)
- **Single Responsibility**: every part does exactly one job.

  | Part | Its one job |
  |------|-------------|
  | `ServiceRequest` | Ticket data and ticket rules |
  | `RequestService` | Application operations (use cases) |
  | `FileRepository` | Reading and writing the JSON file |
  | `main.py` | Menu, input and output |

- **Dependency Inversion**: `RequestService` does not create or import the file repository. It is *given* one in its constructor and only relies on two abilities (`load_all`, `save_all`). So the JSON file could be swapped for a database without changing the service. The tests use this too: they hand the service a temporary file.

### DDD (basic Domain-Driven Design)
The code is split into layers by *meaning*:
- **Domain**: the business idea (what a ticket is, what "resolve" means). Knows nothing about files or screens.
- **Application**: the use cases that combine domain objects.
- **Infrastructure**: technical details such as JSON files.
- **Presentation** (`main.py`): talking to the human.

Domain code never opens the JSON file. Only the infrastructure layer does.

### Git
Two branches, `main` and `development`. All work was done on `development` in small commits, then merged into `main`. See the next section.

---

## 6. Git branches, commits and merge

- `main` holds the stable, final version. It started with only the project skeleton.
- `development` is where all coding happened.
- Work was saved in separate, meaningful commits (one per layer):

  1. Initial project structure
  2. Add ServiceRequest domain model and custom exceptions
  3. Add JSON file repository with safe save and broken-file recovery
  4. Add request service (use cases) with duplicate and not-found handling
  5. Complete CLI application (menu, input and friendly messages)
  6. Add unit tests for domain, service and file persistence
  7. Write full README

- After testing, `development` was merged into `main` using `git merge --no-ff development`. The `--no-ff` option forces a visible **merge commit**, so the branch history is clearly traceable in:

```bash
git log --oneline --graph --all
```

To merge and publish (what was done):

```bash
git checkout main
git merge --no-ff development
git push
```

---

## 7. Running the automatic tests (extra)

```bash
python -m unittest discover -s tests -t . -v
```

The tests use a temporary file, so your real `data/requests.json` is never changed. They check, among other things: new requests start as `OPEN`, duplicate IDs are refused, resolving twice is refused, bad priorities are refused, and a resolved request is still `RESOLVED` after a simulated restart.

---

### Screenshot of Git Commit History

The following screenshot shows the actual Git commit history,
including the development branch, merge commit, and final version.

![Git Commit History](git-commit-history.png)
