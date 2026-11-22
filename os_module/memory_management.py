"""
VeerSeva OS Module - Memory Management & Dynamic Partitioning
Implements Contiguous Memory Allocation algorithms:
1. First-Fit
2. Best-Fit
3. Worst-Fit
Scenario:
Allocating memory partitions (RAM blocks) to welfare verification batch processes
(e.g., P1: Biometric Engine 212KB, P2: Document OCR 417KB, P3: DB Query Pool 112KB, P4: Audit Logger 426KB).
Calculates allocated blocks, internal/external fragmentation, and unallocated processes.
"""

def allocate_first_fit(blocks, processes, block_labels=None, process_labels=None):
    """
    First-Fit: Allocates the FIRST hole that is big enough.
    """
    n_blocks = len(blocks)
    n_procs = len(processes)
    block_sizes = list(blocks)
    allocation = [-1] * n_procs
    remaining_blocks = list(block_sizes)

    steps = []

    for i in range(n_procs):
        p_size = processes[i]
        allocated = False
        for j in range(n_blocks):
            if remaining_blocks[j] >= p_size:
                allocation[i] = j
                internal_frag = remaining_blocks[j] - p_size
                steps.append({
                    "process_idx": i,
                    "process_name": process_labels[i] if process_labels else f"P{i+1}",
                    "process_size": p_size,
                    "allocated_block": j,
                    "block_name": block_labels[j] if block_labels else f"Block {j+1}",
                    "initial_block_size": block_sizes[j],
                    "remaining_block_size": internal_frag,
                    "status": "ALLOCATED"
                })
                remaining_blocks[j] -= p_size
                allocated = True
                break

        if not allocated:
            steps.append({
                "process_idx": i,
                "process_name": process_labels[i] if process_labels else f"P{i+1}",
                "process_size": p_size,
                "allocated_block": -1,
                "block_name": "None",
                "status": "NOT_ALLOCATED (Insufficient contiguous memory)"
            })

    total_allocated_mem = sum(processes[i] for i in range(n_procs) if allocation[i] != -1)
    total_frag = sum(remaining_blocks)

    return {
        "algorithm": "First-Fit",
        "initial_blocks": block_sizes,
        "processes": processes,
        "allocation": allocation,
        "remaining_blocks": remaining_blocks,
        "steps": steps,
        "total_allocated": total_allocated_mem,
        "total_free_memory": total_frag,
        "unallocated_count": allocation.count(-1)
    }


def allocate_best_fit(blocks, processes, block_labels=None, process_labels=None):
    """
    Best-Fit: Allocates the SMALLEST hole that is big enough.
    Minimizes leftover space in the allocated partition.
    """
    n_blocks = len(blocks)
    n_procs = len(processes)
    block_sizes = list(blocks)
    allocation = [-1] * n_procs
    remaining_blocks = list(block_sizes)

    steps = []

    for i in range(n_procs):
        p_size = processes[i]
        best_idx = -1

        for j in range(n_blocks):
            if remaining_blocks[j] >= p_size:
                if best_idx == -1 or remaining_blocks[j] < remaining_blocks[best_idx]:
                    best_idx = j

        if best_idx != -1:
            allocation[i] = best_idx
            remaining_blocks[best_idx] -= p_size
            steps.append({
                "process_idx": i,
                "process_name": process_labels[i] if process_labels else f"P{i+1}",
                "process_size": p_size,
                "allocated_block": best_idx,
                "block_name": block_labels[best_idx] if block_labels else f"Block {best_idx+1}",
                "remaining_block_size": remaining_blocks[best_idx],
                "status": "ALLOCATED"
            })
        else:
            steps.append({
                "process_idx": i,
                "process_name": process_labels[i] if process_labels else f"P{i+1}",
                "process_size": p_size,
                "allocated_block": -1,
                "block_name": "None",
                "status": "NOT_ALLOCATED (Insufficient contiguous memory)"
            })

    total_allocated_mem = sum(processes[i] for i in range(n_procs) if allocation[i] != -1)
    total_frag = sum(remaining_blocks)

    return {
        "algorithm": "Best-Fit",
        "initial_blocks": block_sizes,
        "processes": processes,
        "allocation": allocation,
        "remaining_blocks": remaining_blocks,
        "steps": steps,
        "total_allocated": total_allocated_mem,
        "total_free_memory": total_frag,
        "unallocated_count": allocation.count(-1)
    }


def allocate_worst_fit(blocks, processes, block_labels=None, process_labels=None):
    """
    Worst-Fit: Allocates the LARGEST hole.
    Leaves the largest leftover partition, which may be useful for other processes.
    """
    n_blocks = len(blocks)
    n_procs = len(processes)
    block_sizes = list(blocks)
    allocation = [-1] * n_procs
    remaining_blocks = list(block_sizes)

    steps = []

    for i in range(n_procs):
        p_size = processes[i]
        worst_idx = -1

        for j in range(n_blocks):
            if remaining_blocks[j] >= p_size:
                if worst_idx == -1 or remaining_blocks[j] > remaining_blocks[worst_idx]:
                    worst_idx = j

        if worst_idx != -1:
            allocation[i] = worst_idx
            remaining_blocks[worst_idx] -= p_size
            steps.append({
                "process_idx": i,
                "process_name": process_labels[i] if process_labels else f"P{i+1}",
                "process_size": p_size,
                "allocated_block": worst_idx,
                "block_name": block_labels[worst_idx] if block_labels else f"Block {worst_idx+1}",
                "remaining_block_size": remaining_blocks[worst_idx],
                "status": "ALLOCATED"
            })
        else:
            steps.append({
                "process_idx": i,
                "process_name": process_labels[i] if process_labels else f"P{i+1}",
                "process_size": p_size,
                "allocated_block": -1,
                "block_name": "None",
                "status": "NOT_ALLOCATED (Insufficient contiguous memory)"
            })

    total_allocated_mem = sum(processes[i] for i in range(n_procs) if allocation[i] != -1)
    total_frag = sum(remaining_blocks)

    return {
        "algorithm": "Worst-Fit",
        "initial_blocks": block_sizes,
        "processes": processes,
        "allocation": allocation,
        "remaining_blocks": remaining_blocks,
        "steps": steps,
        "total_allocated": total_allocated_mem,
        "total_free_memory": total_frag,
        "unallocated_count": allocation.count(-1)
    }


def compare_memory_algorithms(blocks, processes, block_labels=None, process_labels=None):
    return {
        "first_fit": allocate_first_fit(blocks, processes, block_labels, process_labels),
        "best_fit": allocate_best_fit(blocks, processes, block_labels, process_labels),
        "worst_fit": allocate_worst_fit(blocks, processes, block_labels, process_labels)
    }
