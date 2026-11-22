"""
VeerSeva OS Module - Disk Scheduling Algorithms
Simulates physical hard disk head movements when reading/writing welfare beneficiary records
and audit archives across disk cylinders/tracks.
Supported algorithms:
1. FCFS (First Come First Served)
2. SSTF (Shortest Seek Time First)
3. SCAN (Elevator Algorithm)
4. C-SCAN (Circular SCAN)
5. LOOK
6. C-LOOK
"""

def disk_fcfs(requests, initial_head):
    sequence = [initial_head] + list(requests)
    head_movement = 0
    diffs = []

    for i in range(1, len(sequence)):
        diff = abs(sequence[i] - sequence[i - 1])
        diffs.append(diff)
        head_movement += diff

    return {
        "algorithm": "FCFS",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def disk_sstf(requests, initial_head):
    pending = list(requests)
    current = initial_head
    sequence = [initial_head]
    head_movement = 0
    diffs = []

    while pending:
        # Find request with shortest seek time from current position
        closest = min(pending, key=lambda track: abs(track - current))
        diff = abs(closest - current)
        diffs.append(diff)
        head_movement += diff
        current = closest
        sequence.append(current)
        pending.remove(closest)

    return {
        "algorithm": "SSTF",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def disk_scan(requests, initial_head, disk_size=200, direction="high"):
    reqs = sorted(list(requests))
    sequence = [initial_head]
    head_movement = 0
    diffs = []

    left = [r for r in reqs if r < initial_head]
    right = [r for r in reqs if r >= initial_head]

    if direction == "high":
        # Move up towards disk_size - 1, then reverse
        sub_seq = right + [disk_size - 1] + list(reversed(left))
    else:
        # Move down towards 0, then reverse
        sub_seq = list(reversed(left)) + [0] + right

    current = initial_head
    for track in sub_seq:
        diff = abs(track - current)
        diffs.append(diff)
        head_movement += diff
        current = track
        sequence.append(current)

    return {
        "algorithm": "SCAN (Elevator)",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def disk_cscan(requests, initial_head, disk_size=200):
    reqs = sorted(list(requests))
    sequence = [initial_head]
    head_movement = 0
    diffs = []

    left = [r for r in reqs if r < initial_head]
    right = [r for r in reqs if r >= initial_head]

    # Move right to end, jump to 0, then serve left
    sub_seq = right + [disk_size - 1, 0] + left

    current = initial_head
    for track in sub_seq:
        diff = abs(track - current)
        diffs.append(diff)
        head_movement += diff
        current = track
        sequence.append(current)

    return {
        "algorithm": "C-SCAN",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def disk_look(requests, initial_head, direction="high"):
    reqs = sorted(list(requests))
    sequence = [initial_head]
    head_movement = 0
    diffs = []

    left = [r for r in reqs if r < initial_head]
    right = [r for r in reqs if r >= initial_head]

    if direction == "high":
        sub_seq = right + list(reversed(left))
    else:
        sub_seq = list(reversed(left)) + right

    current = initial_head
    for track in sub_seq:
        diff = abs(track - current)
        diffs.append(diff)
        head_movement += diff
        current = track
        sequence.append(current)

    return {
        "algorithm": "LOOK",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def disk_clook(requests, initial_head):
    reqs = sorted(list(requests))
    sequence = [initial_head]
    head_movement = 0
    diffs = []

    left = [r for r in reqs if r < initial_head]
    right = [r for r in reqs if r >= initial_head]

    # Move right to highest request, then jump directly to lowest request (no 0 or disk_size-1 boundary hit)
    sub_seq = right + left

    current = initial_head
    for track in sub_seq:
        diff = abs(track - current)
        diffs.append(diff)
        head_movement += diff
        current = track
        sequence.append(current)

    return {
        "algorithm": "C-LOOK",
        "initial_head": initial_head,
        "sequence": sequence,
        "seek_diffs": diffs,
        "total_head_movement": head_movement,
        "average_seek_length": round(head_movement / len(requests), 2) if requests else 0
    }


def compare_disk_algorithms(requests, initial_head, disk_size=200):
    return {
        "fcfs": disk_fcfs(requests, initial_head),
        "sstf": disk_sstf(requests, initial_head),
        "scan": disk_scan(requests, initial_head, disk_size),
        "cscan": disk_cscan(requests, initial_head, disk_size),
        "look": disk_look(requests, initial_head),
        "clook": disk_clook(requests, initial_head)
    }


if __name__ == "__main__":
    req = [98, 183, 37, 122, 14, 124, 65, 67]
    head = 53
    print("FCFS:", disk_fcfs(req, head)["total_head_movement"])
    print("SSTF:", disk_sstf(req, head)["total_head_movement"])
    print("SCAN:", disk_scan(req, head)["total_head_movement"])
    print("LOOK:", disk_look(req, head)["total_head_movement"])
    print("C-LOOK:", disk_clook(req, head)["total_head_movement"])
