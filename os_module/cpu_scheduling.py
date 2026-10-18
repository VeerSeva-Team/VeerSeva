
# VeerSeva - OS Module
# CPU Scheduling Algorithms

def display_results(processes, burst, waiting, turnaround, response):
    n = len(processes)

    print("\nProcess\tBurst\tWaiting\tTurnaround\tResponse")
    for i in range(n):
        print(
            f"{processes[i]}\t{burst[i]}\t"
            f"{waiting[i]}\t{turnaround[i]}\t\t{response[i]}"
        )

    print("\nAverage Waiting Time:", round(sum(waiting) / n, 2))
    print("Average Turnaround Time:", round(sum(turnaround) / n, 2))
    print("Average Response Time:", round(sum(response) / n, 2))


def gantt_chart(order, durations):
    print("\nGantt Chart:")
    print("0", end="")
    time = 0

    for process, duration in zip(order, durations):
        time += duration
        print(f" -- {process} -- {time}", end="")

    print()


# 1. First Come First Serve
def fcfs(processes, burst):
    n = len(processes)
    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    for i in range(1, n):
        waiting[i] = waiting[i - 1] + burst[i - 1]

    for i in range(n):
        turnaround[i] = waiting[i] + burst[i]
        response[i] = waiting[i]

    print("\n--- FCFS Scheduling ---")
    gantt_chart(processes, burst)
    display_results(processes, burst, waiting, turnaround, response)


# 2. Shortest Job First (Non-preemptive)
def sjf(processes, burst):
    n = len(processes)
    order = sorted(range(n), key=lambda i: burst[i])

    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    time = 0
    chart_order = []
    chart_durations = []

    for i in order:
        waiting[i] = time
        response[i] = time
        time += burst[i]
        turnaround[i] = time
        chart_order.append(processes[i])
        chart_durations.append(burst[i])

    print("\n--- SJF Scheduling ---")
    gantt_chart(chart_order, chart_durations)
    display_results(processes, burst, waiting, turnaround, response)


# 3. Priority Scheduling (Non-preemptive)
# Smaller priority number means higher priority
def priority_scheduling(processes, burst, priority):
    n = len(processes)
    order = sorted(range(n), key=lambda i: priority[i])

    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    time = 0
    chart_order = []
    chart_durations = []

    for i in order:
        waiting[i] = time
        response[i] = time
        time += burst[i]
        turnaround[i] = time
        chart_order.append(processes[i])
        chart_durations.append(burst[i])

    print("\n--- Priority Scheduling ---")
    print("Process priorities:", priority)
    gantt_chart(chart_order, chart_durations)
    display_results(processes, burst, waiting, turnaround, response)


# 4. Round Robin Scheduling
def round_robin(processes, burst, quantum):
    n = len(processes)
    remaining = burst.copy()
    waiting = [0] * n
    turnaround = [0] * n
    response = [-1] * n

    time = 0
    order = []
    durations = []

    while any(remaining[i] > 0 for i in range(n)):
        for i in range(n):
            if remaining[i] > 0:
                if response[i] == -1:
                    response[i] = time

                run_time = min(quantum, remaining[i])
                order.append(processes[i])
                durations.append(run_time)

                time += run_time
                remaining[i] -= run_time

                if remaining[i] == 0:
                    turnaround[i] = time
                    waiting[i] = turnaround[i] - burst[i]

    print("\n--- Round Robin Scheduling ---")
    print("Time Quantum:", quantum)
    gantt_chart(order, durations)
    display_results(processes, burst, waiting, turnaround, response)


# Main program
processes = ["P1", "P2", "P3"]
burst = [5, 3, 2]
priority = [2, 1, 3]

while True:
    print("\n===== VeerSeva OS Module =====")
    print("1. FCFS")
    print("2. SJF")
    print("3. Priority Scheduling")
    print("4. Round Robin")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        fcfs(processes, burst)
    elif choice == "2":
        sjf(processes, burst)
    elif choice == "3":
        priority_scheduling(processes, burst, priority)
    elif choice == "4":
        quantum = int(input("Enter time quantum: "))
        if quantum > 0:
            round_robin(processes, burst, quantum)
        else:
            print("Time quantum must be positive.")
    elif choice == "5":
        print("Exiting VeerSeva OS Module.")
        break
    else:
        print("Invalid choice. Try again.")
