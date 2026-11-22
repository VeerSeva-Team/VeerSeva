"""
VeerSeva OS Module - Deadlock Management & Banker's Algorithm
Simulates deadlock detection and prevention for allocating welfare administrative resources
(Verification Officers [A], Biometric Authentication Kits [B], DBT Grant Disbursal Slots [C]).
"""

def is_safe_state(available, allocation, max_demand, process_names=None):
    n_processes = len(allocation)
    n_resources = len(available)

    if process_names is None:
        process_names = [f"P{i}" for i in range(n_processes)]

    # Calculate Need Matrix: Need[i][j] = Max[i][j] - Allocation[i][j]
    need = []
    for i in range(n_processes):
        need.append([max_demand[i][j] - allocation[i][j] for j in range(n_resources)])

    work = list(available)
    finish = [False] * n_processes
    safe_sequence = []
    execution_steps = []

    while len(safe_sequence) < n_processes:
        found = False
        for i in range(n_processes):
            if not finish[i]:
                # Check if Need[i] <= Work
                if all(need[i][j] <= work[j] for j in range(n_resources)):
                    # Process can finish
                    before_work = list(work)
                    for j in range(n_resources):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(process_names[i])
                    execution_steps.append({
                        "process": process_names[i],
                        "need": need[i],
                        "allocated": allocation[i],
                        "available_before": before_work,
                        "available_after": list(work)
                    })
                    found = True
                    break

        if not found:
            # Deadlock detected - system is not in a safe state
            return {
                "is_safe": False,
                "safe_sequence": [],
                "need_matrix": need,
                "execution_steps": execution_steps,
                "message": "Deadlock Warning: System is in an UNSAFE state. No safe execution sequence exists!"
            }

    return {
        "is_safe": True,
        "safe_sequence": safe_sequence,
        "need_matrix": need,
        "execution_steps": execution_steps,
        "message": f"Safe State Verified: System can satisfy all welfare task demands without deadlock. Safe Sequence: {' -> '.join(safe_sequence)}"
    }


def request_resources(available, allocation, max_demand, process_idx, request, process_names=None):
    n_resources = len(available)
    need = [max_demand[process_idx][j] - allocation[process_idx][j] for j in range(n_resources)]

    # Check 1: Request <= Need
    if any(request[j] > need[j] for j in range(n_resources)):
        return {"granted": False, "message": "Error: Process has exceeded its maximum declared claim."}

    # Check 2: Request <= Available
    if any(request[j] > available[j] for j in range(n_resources)):
        return {"granted": False, "message": "Resources not available: Process must wait."}

    # Pretend to allocate
    new_avail = [available[j] - request[j] for j in range(n_resources)]
    new_alloc = [list(row) for row in allocation]
    for j in range(n_resources):
        new_alloc[process_idx][j] += request[j]

    # Evaluate safety
    safety_result = is_safe_state(new_avail, new_alloc, max_demand, process_names)
    if safety_result["is_safe"]:
        return {
            "granted": True,
            "message": f"Request granted safely. New Safe Sequence: {' -> '.join(safety_result['safe_sequence'])}",
            "safety": safety_result
        }
    else:
        return {
            "granted": False,
            "message": "Request denied: Granting this request would lead the system into an unsafe/deadlock state.",
            "safety": safety_result
        }


if __name__ == "__main__":
    avail = [3, 3, 2]
    alloc = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
    maximum = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ]
    res = is_safe_state(avail, alloc, maximum)
    print("Is safe:", res["is_safe"])
    print("Safe sequence:", res["safe_sequence"])
