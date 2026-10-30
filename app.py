from flask import Flask, render_template
from database import get_connection

app = Flask(__name__)


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
        ticket=ticket
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
