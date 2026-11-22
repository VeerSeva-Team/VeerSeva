"""
VeerSeva OS Module - CPU Scheduling Algorithms
Simulates concurrent server processing of welfare application tasks
(Document OCR, Aadhaar Biometric Validation, DBMS Rules Check, DBT Payment Disbursal, Audit Logging).
Supported Algorithms:
1. FCFS (First Come First Served)
2. SJF (Shortest Job First - Non-preemptive)
3. SRTF (Shortest Remaining Time First - Preemptive SJF)
4. Priority Scheduling (Non-preemptive, lower number = higher priority)
5. Round Robin (Time-shared preemptive with configurable Quantum)
"""

def solve_fcfs(processes, burst):
    n = len(processes)
    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    for i in range(1, n):
        waiting[i] = waiting[i - 1] + burst[i - 1]

    for i in range(n):
        turnaround[i] = waiting[i] + burst[i]
        response[i] = waiting[i]

    gantt = []
    curr = 0
    for p, d in zip(processes, burst):
        gantt.append({"process": p, "duration": d, "start": curr, "end": curr + d})
        curr += d

    return {
        "algorithm": "FCFS",
        "total_time": curr,
        "gantt": gantt,
        "waiting": waiting,
        "turnaround": turnaround,
        "response": response,
        "avg_waiting": round(sum(waiting) / n, 2),
        "avg_turnaround": round(sum(turnaround) / n, 2),
        "avg_response": round(sum(response) / n, 2)
    }


def solve_sjf(processes, burst):
    n = len(processes)
    order = sorted(range(n), key=lambda i: burst[i])
    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    curr = 0
    gantt = []
    for i in order:
        waiting[i] = curr
        response[i] = curr
        gantt.append({"process": processes[i], "duration": burst[i], "start": curr, "end": curr + burst[i]})
        curr += burst[i]
        turnaround[i] = curr

    return {
        "algorithm": "SJF (Non-preemptive)",
        "total_time": curr,
        "gantt": gantt,
        "waiting": waiting,
        "turnaround": turnaround,
        "response": response,
        "avg_waiting": round(sum(waiting) / n, 2),
        "avg_turnaround": round(sum(turnaround) / n, 2),
        "avg_response": round(sum(response) / n, 2)
    }


def solve_priority(processes, burst, priority):
    n = len(processes)
    order = sorted(range(n), key=lambda i: priority[i])
    waiting = [0] * n
    turnaround = [0] * n
    response = [0] * n

    curr = 0
    gantt = []
    for i in order:
        waiting[i] = curr
        response[i] = curr
        gantt.append({"process": processes[i], "duration": burst[i], "start": curr, "end": curr + burst[i]})
        curr += burst[i]
        turnaround[i] = curr

    return {
        "algorithm": "Priority (Non-preemptive)",
        "total_time": curr,
        "gantt": gantt,
        "waiting": waiting,
        "turnaround": turnaround,
        "response": response,
        "avg_waiting": round(sum(waiting) / n, 2),
        "avg_turnaround": round(sum(turnaround) / n, 2),
        "avg_response": round(sum(response) / n, 2)
    }


def solve_round_robin(processes, burst, quantum=2):
    n = len(processes)
    remaining = list(burst)
    waiting = [0] * n
    turnaround = [0] * n
    response = [-1] * n

    curr = 0
    gantt = []

    while any(r > 0 for r in remaining):
        for i in range(n):
            if remaining[i] > 0:
                if response[i] == -1:
                    response[i] = curr
                run_dur = min(quantum, remaining[i])
                gantt.append({"process": processes[i], "duration": run_dur, "start": curr, "end": curr + run_dur})
                curr += run_dur
                remaining[i] -= run_dur
                if remaining[i] == 0:
                    turnaround[i] = curr
                    waiting[i] = turnaround[i] - burst[i]

    return {
        "algorithm": f"Round Robin (Quantum={quantum})",
        "total_time": curr,
        "gantt": gantt,
        "waiting": waiting,
        "turnaround": turnaround,
        "response": response,
        "avg_waiting": round(sum(waiting) / n, 2),
        "avg_turnaround": round(sum(turnaround) / n, 2),
        "avg_response": round(sum(response) / n, 2)
    }


def solve_srtf(processes, burst, arrival=None):
    """Shortest Remaining Time First (Preemptive SJF)"""
    n = len(processes)
    if arrival is None:
        arrival = [0] * n

    remaining = list(burst)
    waiting = [0] * n
    turnaround = [0] * n
    response = [-1] * n

    curr = 0
    completed = 0
    raw_execution = []

    while completed < n:
        # Find process available with minimum remaining time > 0
        available = [i for i in range(n) if arrival[i] <= curr and remaining[i] > 0]
        if not available:
            curr += 1
            continue

        shortest_idx = min(available, key=lambda i: remaining[i])

        if response[shortest_idx] == -1:
            response[shortest_idx] = curr

        raw_execution.append((processes[shortest_idx], curr))
        remaining[shortest_idx] -= 1
        curr += 1

        if remaining[shortest_idx] == 0:
            completed += 1
            turnaround[shortest_idx] = curr - arrival[shortest_idx]
            waiting[shortest_idx] = turnaround[shortest_idx] - burst[shortest_idx]

    # Compress raw execution ticks into gantt blocks
    gantt = []
    if raw_execution:
        curr_p, start_t = raw_execution[0]
        curr_dur = 1
        for p, t in raw_execution[1:]:
            if p == curr_p:
                curr_dur += 1
            else:
                gantt.append({"process": curr_p, "duration": curr_dur, "start": start_t, "end": start_t + curr_dur})
                curr_p = p
                start_t = t
                curr_dur = 1
        gantt.append({"process": curr_p, "duration": curr_dur, "start": start_t, "end": start_t + curr_dur})

    return {
        "algorithm": "SRTF (Preemptive SJF)",
        "total_time": curr,
        "gantt": gantt,
        "waiting": waiting,
        "turnaround": turnaround,
        "response": response,
        "avg_waiting": round(sum(waiting) / n, 2),
        "avg_turnaround": round(sum(turnaround) / n, 2),
        "avg_response": round(sum(response) / n, 2)
    }


def compare_all_schedulers(processes, burst, priority, quantum=2):
    return {
        "fcfs": solve_fcfs(processes, burst),
        "sjf": solve_sjf(processes, burst),
        "srtf": solve_srtf(processes, burst),
        "priority": solve_priority(processes, burst, priority),
        "round_robin": solve_round_robin(processes, burst, quantum)
    }


# Backward compatibility with CLI run
def display_results(processes, burst, waiting, turnaround, response):
    n = len(processes)
    print("\nProcess\tBurst\tWaiting\tTurnaround\tResponse")
    for i in range(n):
        print(f"{processes[i]}\t{burst[i]}\t{waiting[i]}\t{turnaround[i]}\t\t{response[i]}")
    print("\nAverage Waiting Time:", round(sum(waiting) / n, 2))
    print("Average Turnaround Time:", round(sum(turnaround) / n, 2))
    print("Average Response Time:", round(sum(response) / n, 2))


def fcfs(processes, burst):
    res = solve_fcfs(processes, burst)
    print("\n--- FCFS Scheduling ---")
    display_results(processes, burst, res["waiting"], res["turnaround"], res["response"])


def sjf(processes, burst):
    res = solve_sjf(processes, burst)
    print("\n--- SJF Scheduling ---")
    display_results(processes, burst, res["waiting"], res["turnaround"], res["response"])


def priority_scheduling(processes, burst, priority):
    res = solve_priority(processes, burst, priority)
    print("\n--- Priority Scheduling ---")
    display_results(processes, burst, res["waiting"], res["turnaround"], res["response"])


def round_robin(processes, burst, quantum):
    res = solve_round_robin(processes, burst, quantum)
    print("\n--- Round Robin Scheduling ---")
    display_results(processes, burst, res["waiting"], res["turnaround"], res["response"])


if __name__ == "__main__":
    procs = ["P1 (OCR)", "P2 (Biometric)", "P3 (CheckEligibility)"]
    bursts = [5, 3, 2]
    prios = [2, 1, 3]
    fcfs(procs, bursts)
    sjf(procs, bursts)
    priority_scheduling(procs, bursts, prios)
    round_robin(procs, bursts, 2)
