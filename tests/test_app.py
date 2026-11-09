import sqlite3
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


import app as app_module


SCHEMA_FILE = PROJECT_ROOT / "schema.sql"


@pytest.fixture()
def test_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_helpdesk.db"

    connection = sqlite3.connect(database_path)

    with open(
        SCHEMA_FILE,
        "r",
        encoding="utf-8"
    ) as schema_file:
        connection.executescript(
            schema_file.read()
        )

    sample_tickets = [
        (
            "VPN connection fails",
            "User cannot connect to the company VPN.",
            "Network",
            "High",
            "Open",
            "Test User One",
            None
        ),
        (
            "Inventory application crashes",
            "The inventory program closes after login.",
            "Software",
            "Critical",
            "In Progress",
            "Test User Two",
            None
        ),
        (
            "Password reset completed",
            "User forgot the account password.",
            "Account Access",
            "Low",
            "Resolved",
            "Test User Three",
            "Password was reset and login was verified."
        )
    ]

    connection.executemany(
        """
        INSERT INTO tickets (
            title,
            description,
            category,
            priority,
            status,
            submitted_by,
            resolution_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        sample_tickets
    )

    connection.commit()
    connection.close()

    def test_get_connection():
        test_connection = sqlite3.connect(
            database_path
        )

        test_connection.row_factory = sqlite3.Row

        return test_connection

    monkeypatch.setattr(
        app_module,
        "get_connection",
        test_get_connection
    )

    yield database_path


@pytest.fixture()
def client(test_database):
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client


def get_database_connection(database_path):
    connection = sqlite3.connect(
        database_path
    )

    connection.row_factory = sqlite3.Row

    return connection


def test_dashboard_loads(client):
    response = client.get("/")

    assert response.status_code == 200

    assert b"HelpDesk Lite Dashboard" in response.data

    assert b"Open Tickets" in response.data

    assert b"In Progress" in response.data

    assert b"Resolved Tickets" in response.data

    assert b"High / Critical Active" in response.data


def test_ticket_list_loads(client):
    response = client.get("/tickets")

    assert response.status_code == 200

    assert b"VPN connection fails" in response.data

    assert b"Inventory application crashes" in response.data

    assert b"Password reset completed" in response.data


def test_ticket_filters_work(client):
    response = client.get(
        "/tickets"
        "?status=Open"
        "&priority=High"
        "&category=Network"
    )

    assert response.status_code == 200

    assert b"VPN connection fails" in response.data

    assert (
        b"Inventory application crashes"
        not in response.data
    )

    assert (
        b"Password reset completed"
        not in response.data
    )


def test_ticket_detail_loads(client):
    response = client.get(
        "/tickets/1"
    )

    assert response.status_code == 200

    assert b"VPN connection fails" in response.data

    assert (
        b"User cannot connect to the company VPN."
        in response.data
    )

    assert b"Network" in response.data

    assert b"High" in response.data

    assert b"Test User One" in response.data


def test_missing_ticket_returns_404(client):
    response = client.get(
        "/tickets/99999"
    )

    assert response.status_code == 404

    assert b"Page Not Found" in response.data


def test_create_ticket(
    client,
    test_database
):
    response = client.post(
        "/tickets/new",
        data={
            "title": "Unable to access shared drive",
            "description": (
                "User receives an access denied message "
                "when opening the shared drive."
            ),
            "category": "Account Access",
            "priority": "High",
            "submitted_by": "Test Employee"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Unable to access shared drive"
        in response.data
    )

    assert b"Test Employee" in response.data

    connection = get_database_connection(
        test_database
    )

    ticket = connection.execute(
        """
        SELECT
            title,
            category,
            priority,
            status,
            submitted_by
        FROM tickets
        WHERE title = ?
        """,
        (
            "Unable to access shared drive",
        )
    ).fetchone()

    connection.close()

    assert ticket is not None

    assert (
        ticket["category"]
        == "Account Access"
    )

    assert (
        ticket["priority"]
        == "High"
    )

    assert (
        ticket["status"]
        == "Open"
    )

    assert (
        ticket["submitted_by"]
        == "Test Employee"
    )


def test_create_ticket_rejects_blank_title(
    client,
    test_database
):
    connection = get_database_connection(
        test_database
    )

    original_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        """
    ).fetchone()[0]

    connection.close()

    response = client.post(
        "/tickets/new",
        data={
            "title": "",
            "description": (
                "Testing server-side validation."
            ),
            "category": "Software",
            "priority": "Medium",
            "submitted_by": "Test Employee"
        }
    )

    assert response.status_code == 200

    assert (
        b"Ticket title is required."
        in response.data
    )

    connection = get_database_connection(
        test_database
    )

    new_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        """
    ).fetchone()[0]

    connection.close()

    assert (
        new_count
        == original_count
    )


def test_create_ticket_rejects_invalid_category(
    client,
    test_database
):
    response = client.post(
        "/tickets/new",
        data={
            "title": "Invalid category test",
            "description": (
                "Testing invalid category handling."
            ),
            "category": "Fake Category",
            "priority": "Medium",
            "submitted_by": "Test Employee"
        }
    )

    assert response.status_code == 200

    assert (
        b"Please select a valid category."
        in response.data
    )

    connection = get_database_connection(
        test_database
    )

    ticket = connection.execute(
        """
        SELECT id
        FROM tickets
        WHERE title = ?
        """,
        (
            "Invalid category test",
        )
    ).fetchone()

    connection.close()

    assert ticket is None


def test_update_ticket_status(
    client,
    test_database
):
    response = client.post(
        "/tickets/1/status",
        data={
            "status": "In Progress"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"In Progress" in response.data

    connection = get_database_connection(
        test_database
    )

    ticket = connection.execute(
        """
        SELECT status
        FROM tickets
        WHERE id = ?
        """,
        (1,)
    ).fetchone()

    connection.close()

    assert (
        ticket["status"]
        == "In Progress"
    )


def test_invalid_status_returns_404(client):
    response = client.post(
        "/tickets/1/status",
        data={
            "status": "Invalid Status"
        }
    )

    assert response.status_code == 404


def test_resolution_requires_notes(
    client,
    test_database
):
    response = client.post(
        "/tickets/1/resolve",
        data={
            "resolution_notes": ""
        }
    )

    assert response.status_code == 200

    assert (
        b"A resolution note is required before "
        b"resolving the ticket."
        in response.data
    )

    connection = get_database_connection(
        test_database
    )

    ticket = connection.execute(
        """
        SELECT
            status,
            resolution_notes
        FROM tickets
        WHERE id = ?
        """,
        (1,)
    ).fetchone()

    connection.close()

    assert (
        ticket["status"]
        == "Open"
    )

    assert (
        ticket["resolution_notes"]
        is None
    )


def test_ticket_can_be_resolved(
    client,
    test_database
):
    resolution_text = (
        "Verified the VPN settings, recreated "
        "the connection profile, and confirmed "
        "connectivity."
    )

    response = client.post(
        "/tickets/1/resolve",
        data={
            "resolution_notes": resolution_text
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Resolved" in response.data

    assert (
        resolution_text.encode()
        in response.data
    )

    connection = get_database_connection(
        test_database
    )

    ticket = connection.execute(
        """
        SELECT
            status,
            resolution_notes
        FROM tickets
        WHERE id = ?
        """,
        (1,)
    ).fetchone()

    connection.close()

    assert (
        ticket["status"]
        == "Resolved"
    )

    assert (
        ticket["resolution_notes"]
        == resolution_text
    )

@pytest.mark.parametrize("status", ["Open", "In Progress"])
def test_resolved_ticket_cannot_change_status(client, test_database, status):
    response = client.post("/tickets/3/status", data={"status": status})
    assert response.status_code == 302
    with get_database_connection(test_database) as connection:
        ticket = connection.execute("SELECT * FROM tickets WHERE id = 3").fetchone()
    assert ticket["status"] == "Resolved"
    assert ticket["resolution_notes"] == "Password was reset and login was verified."


def test_resolved_ticket_notes_cannot_be_overwritten(client, test_database):
    response = client.post("/tickets/3/resolve", data={"resolution_notes": "Replacement"})
    assert response.status_code == 302
    with get_database_connection(test_database) as connection:
        ticket = connection.execute("SELECT * FROM tickets WHERE id = 3").fetchone()
    assert ticket["resolution_notes"] == "Password was reset and login was verified."


@pytest.mark.parametrize("length, accepted", [(150, True), (151, False)])
def test_ticket_title_length(client, test_database, length, accepted):
    title = "T" * length
    response = client.post("/tickets/new", data={
        "title": title, "description": "Test description", "category": "Software",
        "priority": "Low", "submitted_by": "Test User"
    })
    with get_database_connection(test_database) as connection:
        count = connection.execute("SELECT COUNT(*) FROM tickets WHERE title = ?", (title,)).fetchone()[0]
    assert count == int(accepted)
    assert response.status_code == (302 if accepted else 200)
    if not accepted:
        assert b"150 characters or fewer" in response.data


@pytest.mark.parametrize("field", ["status", "priority", "category"])
def test_invalid_filter_is_not_shown_as_active(client, field):
    response = client.get("/tickets", query_string={field: "InvalidFilter"})
    assert response.status_code == 200
    assert b"InvalidFilter" not in response.data
    assert b"Active Filters:" not in response.data
    assert b"VPN connection fails" in response.data


def test_valid_filter_remains_when_another_is_invalid(client):
    response = client.get("/tickets?status=Open&priority=InvalidFilter")
    assert b"Status: Open" in response.data
    assert b"InvalidFilter" not in response.data
    assert b"VPN connection fails" in response.data
    assert b"Inventory application crashes" not in response.data
