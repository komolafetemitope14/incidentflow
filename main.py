
incidents = []


def create_incident():
    print("\n--- Create New Incident ---")

    title = input("Enter incident title: ").strip()
    description = input("Enter description: ").strip()
    severity = input(
        "Enter severity (Critical/High/Medium/Low): "
    ).strip().capitalize()

    if not title or not description:
        print("Title and description cannot be empty.")
        return

    allowed_severities = ["Critical", "High", "Medium", "Low"]

    if severity not in allowed_severities:
        print("Invalid severity. Please try again.")
        return

    incident_id = f"INC-{len(incidents) + 1:03d}"

    incident = {
        "id": incident_id,
        "title": title,
        "description": description,
        "severity": severity,
        "status": "Open"
    }

    incidents.append(incident)

    print("\nIncident created successfully!")
    print(f"ID: {incident['id']}")
    print(f"Title: {incident['title']}")
    print(f"Severity: {incident['severity']}")
    print(f"Status: {incident['status']}")


def view_incidents():
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
    while True:
        print("\n" + "=" * 40)
        print("WELCOME TO INCIDENTFLOW")
        print("Enterprise Incident Management System")
        print("=" * 40)

        print("1. Create Incident")
        print("2. View Incidents")
        print("3. Exit")

        choice = input("\nSelect an option: ")

        if choice == "1":
            create_incident()
        elif choice == "2":
            view_incidents()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()

