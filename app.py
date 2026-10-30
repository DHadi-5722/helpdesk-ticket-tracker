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


if __name__ == "__main__":
    app.run(debug=True)
