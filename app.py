"""Handle browser requests and connect ticket forms, SQLite data, and Jinja pages."""

from flask import Flask, render_template, request, redirect, url_for
from database import get_connection

app = Flask(__name__)


# These allowlists keep submitted values consistent with the form choices.
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
    """Count tickets by workflow state and show the five newest submissions."""
    connection = get_connection()

    open_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE status = ?
        """,
        ("Open",)
    ).fetchone()[0]

    in_progress_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE status = ?
        """,
        ("In Progress",)
    ).fetchone()[0]

    resolved_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE status = ?
        """,
        ("Resolved",)
    ).fetchone()[0]

    high_critical_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE priority IN (?, ?)
        AND status != ?
        """,
        (
            "High",
            "Critical",
            "Resolved"
        )
    ).fetchone()[0]

    recent_tickets = connection.execute(
        """
        SELECT
            id,
            title,
            priority,
            status,
            created_at
        FROM tickets
        ORDER BY created_at DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        open_count=open_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        high_critical_count=high_critical_count,
        recent_tickets=recent_tickets
    )


@app.route("/tickets")
def tickets():
    """Apply supported URL filters and render the matching tickets newest first."""
    selected_status = request.args.get("status", "").strip()
    selected_priority = request.args.get("priority", "").strip()
    selected_category = request.args.get("category", "").strip()

    # Clear unsupported filters before querying and before displaying active labels.
    if selected_status not in VALID_STATUSES:
        selected_status = ""
    if selected_priority not in VALID_PRIORITIES:
        selected_priority = ""
    if selected_category not in VALID_CATEGORIES:
        selected_category = ""

    query = """
        SELECT
            id,
            title,
            category,
            priority,
            status,
            created_at
        FROM tickets
    """

    # Build SQL from fixed clauses; user values travel separately as parameters.
    conditions = []
    parameters = []

    if selected_status in VALID_STATUSES:
        conditions.append("status = ?")
        parameters.append(selected_status)

    if selected_priority in VALID_PRIORITIES:
        conditions.append("priority = ?")
        parameters.append(selected_priority)

    if selected_category in VALID_CATEGORIES:
        conditions.append("category = ?")
        parameters.append(selected_category)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    connection = get_connection()

    tickets = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return render_template(
        "tickets.html",
        tickets=tickets,
        statuses=VALID_STATUSES,
        priorities=VALID_PRIORITIES,
        categories=VALID_CATEGORIES,
        selected_status=selected_status,
        selected_priority=selected_priority,
        selected_category=selected_category
    )


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    """Display the form or validate and save a new Open ticket on submission."""
    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()
        submitted_by = request.form.get("submitted_by", "").strip()

        if not title:
            error = "Ticket title is required."

        elif len(title) > 150:
            error = "Ticket title must be 150 characters or fewer."

        elif not description:
            error = "Description is required."

        elif category not in VALID_CATEGORIES:
            error = "Please select a valid category."

        elif priority not in VALID_PRIORITIES:
            error = "Please select a valid priority."

        elif not submitted_by:
            error = "Submitted By is required."

        # Save only after every server-side check passes, even if browser checks were bypassed.
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

            # Redirect to the saved ticket so refreshing the page does not resubmit the form.
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
    """Load a single ticket, or return the missing-page response if it does not exist."""
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
    """Change an active ticket between Open and In Progress; resolved tickets stay locked."""
    new_status = request.form.get("status", "").strip()

    if new_status not in VALID_STATUSES:
        return render_template("404.html"), 404

    connection = get_connection()

    ticket = connection.execute(
        """
        SELECT id, status
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        connection.close()

        return render_template("404.html"), 404

    # Resolution must use the dedicated endpoint, which requires a note.
    if ticket["status"] == "Resolved" or new_status == "Resolved":
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
        -- Recheck the state during the write in case another request resolved it first.
        WHERE id = ? AND status != 'Resolved'
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
    """Require a troubleshooting note and resolve an active ticket without overwriting completed work."""
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

    # Completed tickets are read-only, including when a request bypasses the hidden UI.
    if ticket["status"] == "Resolved":
        connection.close()
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

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
        -- Recheck the state during the write in case another request resolved it first.
        WHERE id = ? AND status != 'Resolved'
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
    """Show a friendly page while preserving the HTTP 404 response code."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Show a recovery page for unexpected errors with the HTTP 500 response code."""
    return render_template("500.html"), 500


# Start the local development server only when this file is executed directly.
if __name__ == "__main__":
    app.run(debug=True)