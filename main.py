import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "incidents.json"

ALLOWED_SEVERITIES = ["Critical", "High", "Medium", "Low"]


def load_incidents():
    """Load existing incidents from the JSON file."""

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
    """Generate the next available incident ID."""

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


def main():
    incidents = load_incidents()

    while True:
        print("\n" + "=" * 40)
        print("WELCOME TO INCIDENTFLOW")
        print("Enterprise Incident Management System")
        print("=" * 40)

        print("1. Create Incident")
        print("2. View Incidents")
        print("3. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            create_incident(incidents)
        elif choice == "2":
            view_incidents(incidents)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
