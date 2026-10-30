# HelpDesk Lite

HelpDesk Lite is a lightweight IT support ticket management application built with Python, Flask, SQLite, HTML, CSS, Bootstrap, and Jinja templates.

The project was created to demonstrate a complete support workflow where users can submit technical issues, view existing tickets, update ticket status, and document how issues were resolved.

The application is intentionally kept simple so the complete project can be understood, explained, tested, and maintained.

---

## Project Purpose

The goal of HelpDesk Lite is to simulate a small internal IT help desk system.

The application demonstrates how a web application can:

- Accept user input through forms
- Validate submitted information
- Store data in a relational database
- Retrieve and display database records
- Update existing records
- Track ticket status
- Document troubleshooting and resolution information
- Handle invalid pages and missing tickets
- Use parameterized SQL queries for user-supplied data

---

## Features

### Create Support Tickets

Users can submit a new support ticket containing:

- Ticket title
- Issue description
- Category
- Priority
- Submitted by

New tickets automatically begin with the status:

```text
Open
```

Available categories include:

```text
Software
Hardware
Network
Account Access
Other
```

Available priorities include:

```text
Low
Medium
High
Critical
```

---

## View All Tickets

The Tickets page displays existing support tickets in a table.

The table includes:

- Ticket ID
- Issue title
- Category
- Priority
- Status
- Creation date

Priority and status values are displayed using Bootstrap badges to make the ticket list easier to read.

Clicking a ticket title opens the full ticket details.

---

## Ticket Details

Each support ticket has its own detail page.

The page displays:

- Ticket ID
- Ticket title
- Full description
- Category
- Priority
- Current status
- Submitted by
- Assigned technician
- Creation date
- Last updated date
- Resolution notes

---

## Ticket Workflow

Tickets move through a simple support workflow:

```text
Open
  |
  v
In Progress
  |
  v
Resolved
```

A support ticket can be changed between Open and In Progress.

Before a ticket can be resolved, a resolution note must be entered.

The resolution note provides documentation explaining what troubleshooting or corrective action was performed.

Once resolved, the ticket displays its resolution information and no longer shows the normal update controls.

---

## Input Validation

HelpDesk Lite validates ticket information before saving it.

Required information includes:

- Title
- Description
- Category
- Priority
- Submitted by

The application uses both:

- HTML form validation
- Server-side Flask validation

Server-side validation helps prevent incomplete or invalid information from being stored even if browser validation is bypassed.

---

## Database

HelpDesk Lite uses SQLite for local data storage.

The main database table is:

```text
tickets
```

The current ticket structure includes:

```text
id
title
description
category
priority
status
submitted_by
assigned_to
created_at
updated_at
resolution_notes
```

SQLite was selected because it provides a relational database without requiring a separate database server.

The local database file is not included in the GitHub repository.

---

## SQL Safety

Database operations involving user-supplied information use parameterized SQL queries.

For example, values are passed separately from the SQL statement instead of combining raw form input directly into SQL.

This helps reduce the risk of SQL injection.

---

## Technologies

The project currently uses:

```text
Python
Flask
SQLite
HTML
CSS
Bootstrap
Jinja
pytest
Git
GitHub
```

### Python

Used for application logic and database interaction.

### Flask

Used for:

- Web routes
- Form handling
- Application logic
- Template rendering
- HTTP requests and redirects

### SQLite

Used to store and update support ticket information.

### Jinja

Used to display dynamic Python and database information inside HTML templates.

### Bootstrap

Used to provide responsive layout, tables, buttons, cards, alerts, badges, and form styling.

### pytest

Used for application testing.

---

## Project Structure

```text
helpdesk-ticket-tracker/
|
|-- app.py
|-- database.py
|-- schema.sql
|-- seed.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- static/
|   |-- styles.css
|
|-- templates/
|   |-- base.html
|   |-- dashboard.html
|   |-- tickets.html
|   |-- ticket_detail.html
|   |-- new_ticket.html
|   |-- 404.html
|   |-- 500.html
|
|-- tests/
    |-- test_app.py
```

The local virtual environment and SQLite database are intentionally excluded from GitHub.

---

## Running the Project Locally

### 1. Clone the Repository

```powershell
git clone https://github.com/YOUR-USERNAME/helpdesk-ticket-tracker.git
```

Move into the project directory:

```powershell
cd helpdesk-ticket-tracker
```

---

### 2. Create a Python Virtual Environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

### 4. Initialize the Database

Run:

```powershell
python database.py
```

This creates the local SQLite database and the required tickets table.

---

### 5. Add Demo Tickets

Optional sample data can be added by running:

```powershell
python seed.py
```

The seed script inserts several example IT support tickets that can be used for development and testing.

---

### 6. Start the Application

Run:

```powershell
python app.py
```

The Flask development server should display:

```text
http://127.0.0.1:5000
```

Open that address in a web browser.

---

## Main Application Pages

Dashboard:

```text
http://127.0.0.1:5000/
```

All Tickets:

```text
http://127.0.0.1:5000/tickets
```

Create Ticket:

```text
http://127.0.0.1:5000/tickets/new
```

Individual ticket pages use the ticket ID:

```text
http://127.0.0.1:5000/tickets/1
```

---

## Error Handling

HelpDesk Lite includes custom error pages.

### 404

Displayed when a requested page or ticket cannot be found.

### 500

Displayed when the application encounters an unexpected internal error.

---

## Demo Data

The project includes a `seed.py` script containing sample technical support issues such as:

- Email access problems
- Printer problems
- VPN connectivity problems
- Application crashes
- Password reset requests

The demo data makes it easier to test ticket lists, ticket details, status changes, and resolution workflows.

---

## Git and GitHub

The repository uses Git for source control.

Development work is committed in small steps so the Git history shows how the application progressed.

Examples of project commits include:

```text
initial HelpDesk Lite project setup

add sample tickets and ticket list navigation

add ticket detail page, custom error handling, UI styling, and test setup

add ticket creation form and validation

add ticket status updates and resolution workflow
```

The following local files are excluded using `.gitignore`:

```text
.venv/
__pycache__/
*.pyc
*.db
.env
.pytest_cache/
.vscode/
```

---

## Screenshots

Screenshots will be added as the interface is finalized.

Recommended screenshots include:

1. Dashboard
2. All Tickets page
3. Create Ticket form
4. Ticket detail page
5. Resolved ticket with resolution notes

---

## Current Project Status

The current version supports:

- Flask application startup
- SQLite database initialization
- Demo ticket data
- Ticket creation
- Ticket listing
- Ticket detail pages
- Input validation
- Priority and status indicators
- Open ticket status
- In Progress ticket status
- Ticket resolution
- Required resolution notes
- Updated timestamps
- Custom 404 page
- Custom 500 page
- Basic Bootstrap styling

---

## Planned Improvements

The next planned improvements include:

- Filter tickets by status
- Filter tickets by priority
- Filter tickets by category
- Add dashboard ticket counts
- Improve automated tests
- Add screenshots
- Improve final UI polish

Additional features may be considered only after the core application is complete and stable.

---

## What I Learned

Building HelpDesk Lite provided practice with connecting several parts of a web application together.

Important concepts included:

- Creating Flask routes
- Handling GET and POST requests
- Processing HTML forms
- Performing server-side validation
- Using SQLite from Python
- Writing parameterized SQL statements
- Rendering database records using Jinja templates
- Updating existing database records
- Tracking application state
- Designing a simple support workflow
- Adding custom error handling
- Using Bootstrap for application layout
- Using Git and GitHub during development

One of the most important lessons from the project was understanding the complete application flow:

```text
User Request
    |
    v
Flask Route
    |
    v
Python Application Logic
    |
    v
SQLite Database
    |
    v
Jinja Template
    |
    v
Browser Response
```

---

## Project Goal

HelpDesk Lite is designed as a small but complete portfolio application.

The purpose is not to imitate a large enterprise help desk product.

The goal is to demonstrate the ability to:

```text
Build
Debug
Test
Document
Maintain
Explain
```

a useful application from beginning to end.