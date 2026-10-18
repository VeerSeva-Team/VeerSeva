from collections import deque


class Application:
    def __init__(self, app_id, name, arrival_time, burst_time, priority):
        self.app_id = app_id
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0


def create_applications():
    return [
        Application(101, "Pension Assistance", 0, 5, 2),
        Application(102, "Medical Support", 1, 3, 1),
        Application(103, "Education Grant", 2, 4, 3),
        Application(104, "Housing Support", 3, 2, 2),
    ]


def display_results(title, applications):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)

    print(
        f"{'ID':<8}{'Application':<22}{'Priority':<10}"
        f"{'Completion':<12}{'Waiting':<10}{'Turnaround':<12}"
    )

    for app in sorted(applications, key=lambda item: item.app_id):
        print(
            f"{app.app_id:<8}{app.name:<22}{app.priority:<10}"
            f"{app.completion_time:<12}{app.waiting_time:<10}"
            f"{app.turnaround_time:<12}"
        )

    count = len(applications)
    avg_wait = sum(a.waiting_time for a in applications) / count
    avg_turnaround = sum(a.turnaround_time for a in applications) / count

    print(f"\nAverage waiting time: {avg_wait:.2f}")
    print(f"Average turnaround time: {avg_turnaround:.2f}")


def fcfs():
    applications = sorted(
        create_applications(),
        key=lambda app: (app.arrival_time, app.app_id)
    )

    current_time = 0

    for app in applications:
        current_time = max(current_time, app.arrival_time)
        current_time += app.burst_time

        app.completion_time = current_time
        app.turnaround_time = current_time - app.arrival_time
        app.waiting_time = app.turnaround_time - app.burst_time

    display_results("FCFS SCHEDULING", applications)


def priority_scheduling():
    applications = create_applications()
    pending = applications.copy()
    current_time = 0

    while pending:
        available = [
            app for app in pending
            if app.arrival_time <= current_time
        ]

        if not available:
            current_time = min(app.arrival_time for app in pending)
            available = [
                app for app in pending
                if app.arrival_time <= current_time
            ]

      
        selected = min(
            available,
            key=lambda app: (app.priority, app.arrival_time, app.app_id)
        )

        current_time += selected.burst_time
        selected.completion_time = current_time
        selected.turnaround_time = current_time - selected.arrival_time
        selected.waiting_time = (
            selected.turnaround_time - selected.burst_time
        )

        pending.remove(selected)

    display_results("NON-PREEMPTIVE PRIORITY SCHEDULING", applications)


def round_robin(quantum=2):
    applications = create_applications()
    pending = sorted(
        applications,
        key=lambda app: (app.arrival_time, app.app_id)
    )

    ready_queue = deque()
    current_time = 0
    next_app = 0

    while next_app < len(pending) or ready_queue:
        if not ready_queue and next_app < len(pending):
            current_time = max(
                current_time, pending[next_app].arrival_time
            )

        while (
            next_app < len(pending)
            and pending[next_app].arrival_time <= current_time
        ):
            ready_queue.append(pending[next_app])
            next_app += 1

        if not ready_queue:
            continue

        app = ready_queue.popleft()
        run_time = min(quantum, app.remaining_time)
        current_time += run_time
        app.remaining_time -= run_time

        while (
            next_app < len(pending)
            and pending[next_app].arrival_time <= current_time
        ):
            ready_queue.append(pending[next_app])
            next_app += 1

        if app.remaining_time > 0:
            ready_queue.append(app)
        else:
            app.completion_time = current_time
            app.turnaround_time = current_time - app.arrival_time
            app.waiting_time = app.turnaround_time - app.burst_time

    display_results(
        f"ROUND ROBIN SCHEDULING (TIME QUANTUM = {quantum})",
        applications
    )


def main():
    while True:
        print("\nVEERSEVA OS PROCESS SCHEDULER")
        print("1. First Come First Served (FCFS)")
        print("2. Priority Scheduling")
        print("3. Round Robin Scheduling")
        print("4. Run All Algorithms")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            fcfs()
        elif choice == "2":
            priority_scheduling()
        elif choice == "3":
            round_robin()
        elif choice == "4":
            fcfs()
            priority_scheduling()
            round_robin()
        elif choice == "5":
            print("Exiting VeerSeva OS Scheduler.")
            break
        else:
            print("Invalid choice. Please enter 1 to 5.")


if __name__ == "__main__":
    main()
