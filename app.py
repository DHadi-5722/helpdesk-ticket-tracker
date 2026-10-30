from flask import Flask, render_template, request, redirect, url_for
from database import get_connection

app = Flask(__name__)


VALID_CATEGORIES = [
    "Software",
    "Hardware",
    "Network",
    "Account Access",
    "Other"
]

VALID_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

VALID_STATUSES = [
    "Open",
    "In Progress",
    "Resolved"
]


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/tickets")
def tickets():
    connection = get_connection()

    tickets = connection.execute(
        """
        SELECT
            id,
            title,
            category,
            priority,
            status,
            created_at
        FROM tickets
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "tickets.html",
        tickets=tickets
    )


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()
        submitted_by = request.form.get("submitted_by", "").strip()

        if not title:
            error = "Ticket title is required."

        elif not description:
            error = "Description is required."

        elif category not in VALID_CATEGORIES:
            error = "Please select a valid category."

        elif priority not in VALID_PRIORITIES:
            error = "Please select a valid priority."

        elif not submitted_by:
            error = "Submitted By is required."

        if error is None:
            connection = get_connection()

            cursor = connection.execute(
                """
                INSERT INTO tickets (
                    title,
                    description,
                    category,
                    priority,
                    status,
                    submitted_by
                )
                VALUES (?, ?, ?, ?, 'Open', ?)
                """,
                (
                    title,
                    description,
                    category,
                    priority,
                    submitted_by
                )
            )

            connection.commit()

            ticket_id = cursor.lastrowid

            connection.close()

            return redirect(
                url_for(
                    "ticket_detail",
                    ticket_id=ticket_id
                )
            )

    return render_template(
        "new_ticket.html",
        error=error,
        categories=VALID_CATEGORIES,
        priorities=VALID_PRIORITIES
    )


@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):
    connection = get_connection()

    ticket = connection.execute(
        """
        SELECT
            id,
            title,
            description,
            category,
            priority,
            status,
            submitted_by,
            assigned_to,
            created_at,
            updated_at,
            resolution_notes
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    connection.close()

    if ticket is None:
        return render_template("404.html"), 404

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        error=None
    )


@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_ticket_status(ticket_id):
    new_status = request.form.get("status", "").strip()

    if new_status not in VALID_STATUSES:
        return render_template("404.html"), 404

    connection = get_connection()

    ticket = connection.execute(
        """
        SELECT id
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        connection.close()
        return render_template("404.html"), 404

    if new_status == "Resolved":
        connection.close()

        return redirect(
            url_for(
                "ticket_detail",
                ticket_id=ticket_id
            )
        )

    connection.execute(
        """
        UPDATE tickets
        SET
            status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            new_status,
            ticket_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket_id
        )
    )


@app.route("/tickets/<int:ticket_id>/resolve", methods=["POST"])
def resolve_ticket(ticket_id):
    resolution_notes = request.form.get(
        "resolution_notes",
        ""
    ).strip()

    connection = get_connection()

    ticket = connection.execute(
        """
        SELECT
            id,
            title,
            description,
            category,
            priority,
            status,
            submitted_by,
            assigned_to,
            created_at,
            updated_at,
            resolution_notes
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        connection.close()
        return render_template("404.html"), 404

    if not resolution_notes:
        connection.close()

        return render_template(
            "ticket_detail.html",
            ticket=ticket,
            error="A resolution note is required before resolving the ticket."
        )

    connection.execute(
        """
        UPDATE tickets
        SET
            status = 'Resolved',
            resolution_notes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            resolution_notes,
            ticket_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket_id
        )
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)