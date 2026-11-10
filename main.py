import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "incidents.json"

ALLOWED_SEVERITIES = ["Critical", "High", "Medium", "Low"]
ALLOWED_STATUSES = ["Open", "Investigating", "Resolved"]


def load_incidents():
    """Load incidents from the JSON file."""

    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            print("Invalid incident data format.")
            return []

        return data

    except (json.JSONDecodeError, OSError) as error:
        print(f"Unable to load incidents: {error}")
        return []


def save_incidents(incidents):
    """Save incidents to the JSON file."""

    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(incidents, file, indent=4)

        return True

    except OSError as error:
        print(f"Unable to save incidents: {error}")
        return False


def generate_incident_id(incidents):
    """Generate a unique incident ID."""

    existing_numbers = []

    for incident in incidents:
        incident_id = incident.get("id", "")

        if incident_id.startswith("INC-"):
            try:
                number = int(incident_id.split("-")[1])
                existing_numbers.append(number)
            except (ValueError, IndexError):
                continue

    next_number = max(existing_numbers, default=0) + 1

    return f"INC-{next_number:03d}"


def create_incident(incidents):
    print("\n--- Create New Incident ---")

    title = input("Enter incident title: ").strip()
    description = input("Enter description: ").strip()
    severity = input(
        "Enter severity (Critical/High/Medium/Low): "
    ).strip().capitalize()

    if not title or not description:
        print("Title and description cannot be empty.")
        return

    if severity not in ALLOWED_SEVERITIES:
        print("Invalid severity. Please try again.")
        return

    incident = {
        "id": generate_incident_id(incidents),
        "title": title,
        "description": description,
        "severity": severity,
        "status": "Open"
    }

    incidents.append(incident)

    if not save_incidents(incidents):
        incidents.pop()
        print("Incident was not saved. Please try again.")
        return

    print("\nIncident created successfully!")
    print(f"ID: {incident['id']}")
    print(f"Title: {incident['title']}")
    print(f"Severity: {incident['severity']}")
    print(f"Status: {incident['status']}")


def view_incidents(incidents):
    print("\n--- All Incidents ---")

    if not incidents:
        print("No incidents found.")
        return

    for incident in incidents:
        print(
            f"{incident['id']} | "
            f"{incident['title']} | "
            f"{incident['severity']} | "
            f"{incident['status']}"
        )


def update_incident_status(incidents):
    """Update the status of an existing incident."""

    print("\n--- Update Incident Status ---")

    if not incidents:
        print("No incidents available to update.")
        return

    incident_id = input(
        "Enter incident ID (e.g. INC-001): "
    ).strip().upper()

    incident = next(
        (item for item in incidents if item["id"] == incident_id),
        None
    )

    if incident is None:
        print("Incident not found.")
        return

    print(f"\nIncident: {incident['title']}")
    print(f"Current status: {incident['status']}")

    print("\nAvailable statuses:")
    for index, status in enumerate(ALLOWED_STATUSES, start=1):
        print(f"{index}. {status}")

    choice = input("\nSelect new status: ").strip()

    if not choice.isdigit():
        print("Invalid status selection.")
        return

    choice_number = int(choice)

    if not 1 <= choice_number <= len(ALLOWED_STATUSES):
        print("Invalid status selection.")
        return

    new_status = ALLOWED_STATUSES[choice_number - 1]
    old_status = incident["status"]

    if new_status == old_status:
        print("Incident already has that status.")
        return

    incident["status"] = new_status

    if not save_incidents(incidents):
        incident["status"] = old_status
        print("Status update was not saved.")
        return

    print(
        f"\nIncident {incident_id} updated successfully!"
    )
    print(f"Previous status: {old_status}")
    print(f"New status: {new_status}")


def main():
    incidents = load_incidents()

    while True:
        print("\n" + "=" * 40)
        print("WELCOME TO INCIDENTFLOW")
        print("Enterprise Incident Management System")
        print("=" * 40)

        print("1. Create Incident")
        print("2. View Incidents")
        print("3. Update Incident Status")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            create_incident(incidents)
        elif choice == "2":
            view_incidents(incidents)
        elif choice == "3":
            update_incident_status(incidents)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
