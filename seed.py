from database import get_connection


def seed_database():
    connection = get_connection()
    cursor = connection.cursor()

    sample_tickets = [
        (
            "Unable to access email",
            "User reports that Outlook is asking for a password repeatedly and will not open the mailbox.",
            "Account Access",
            "High",
            "Open",
            "Sarah Johnson",
            None
        ),
        (
            "Printer not responding",
            "Office printer shows as offline and users are unable to print documents.",
            "Hardware",
            "Medium",
            "In Progress",
            "Michael Reed",
            None
        ),
        (
            "VPN connection fails",
            "Remote employee cannot connect to the company VPN and receives a connection timeout.",
            "Network",
            "High",
            "Open",
            "Jessica Lee",
            None
        ),
        (
            "Application crashes at startup",
            "The inventory application closes immediately after the user signs in.",
            "Software",
            "Critical",
            "In Progress",
            "Daniel Brooks",
            None
        ),
        (
            "Password reset completed",
            "User was unable to sign in after forgetting the account password.",
            "Account Access",
            "Low",
            "Resolved",
            "Emily Carter",
            "Verified the user's identity, reset the password, and confirmed successful login."
        )
    ]

    cursor.executemany(
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

    print("Sample HelpDesk tickets added successfully.")

    cursor.execute(
        """
        SELECT id, title, category, priority, status, submitted_by
        FROM tickets
        ORDER BY id
        """
    )

    tickets = cursor.fetchall()

    print()
    print("Current tickets:")
    print("-" * 80)

    for ticket in tickets:
        print(
            f"ID: {ticket['id']} | "
            f"{ticket['title']} | "
            f"{ticket['category']} | "
            f"{ticket['priority']} | "
            f"{ticket['status']} | "
            f"Submitted by: {ticket['submitted_by']}"
        )

    connection.close()


if __name__ == "__main__":
    seed_database()