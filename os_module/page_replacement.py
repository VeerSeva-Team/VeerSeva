"""
VeerSeva OS Module - Memory Management & Page Replacement
Simulates virtual memory page replacement for caching digital welfare documents
(Discharge Book, ECHS Card, PPO Certificate, Bonafide Marksheet).
Supported Algorithms:
1. FIFO (First In First Out)
2. LRU (Least Recently Used)
3. Optimal (Belady's Min / OPT)
4. LFU (Least Frequently Used)
Includes Belady's Anomaly evaluation!
"""

def fifo(pages, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []

    for page in pages:
        if page in frames:
            hits += 1
            status = "HIT"
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)

        # Pad frames representation for display
        padded_frames = list(frames) + [None] * (frame_count - len(frames))
        history.append({
            "page": page,
            "status": status,
            "frames": padded_frames
        })

    return {
        "algorithm": "FIFO",
        "frame_count": frame_count,
        "page_faults": faults,
        "page_hits": hits,
        "total_requests": len(pages),
        "hit_ratio": round((hits / len(pages)) * 100, 2) if pages else 0,
        "fault_ratio": round((faults / len(pages)) * 100, 2) if pages else 0,
        "history": history
    }


def lru(pages, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []
    last_used = {}

    for time, page in enumerate(pages):
        if page in frames:
            hits += 1
            status = "HIT"
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                # Find page with oldest last_used time
                lru_page = min(frames, key=lambda p: last_used.get(p, -1))
                idx = frames.index(lru_page)
                frames[idx] = page

        last_used[page] = time
        padded_frames = list(frames) + [None] * (frame_count - len(frames))
        history.append({
            "page": page,
            "status": status,
            "frames": padded_frames
        })

    return {
        "algorithm": "LRU",
        "frame_count": frame_count,
        "page_faults": faults,
        "page_hits": hits,
        "total_requests": len(pages),
        "hit_ratio": round((hits / len(pages)) * 100, 2) if pages else 0,
        "fault_ratio": round((faults / len(pages)) * 100, 2) if pages else 0,
        "history": history
    }


def optimal(pages, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []

    for idx, page in enumerate(pages):
        if page in frames:
            hits += 1
            status = "HIT"
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                # Find page not used for longest time in future
                future_pages = pages[idx + 1:]
                farthest_idx = -1
                victim_page = frames[0]

                for f in frames:
                    if f not in future_pages:
                        victim_page = f
                        break
                    else:
                        next_use = future_pages.index(f)
                        if next_use > farthest_idx:
                            farthest_idx = next_use
                            victim_page = f

                frame_idx = frames.index(victim_page)
                frames[frame_idx] = page

        padded_frames = list(frames) + [None] * (frame_count - len(frames))
        history.append({
            "page": page,
            "status": status,
            "frames": padded_frames
        })

    return {
        "algorithm": "OPTIMAL",
        "frame_count": frame_count,
        "page_faults": faults,
        "page_hits": hits,
        "total_requests": len(pages),
        "hit_ratio": round((hits / len(pages)) * 100, 2) if pages else 0,
        "fault_ratio": round((faults / len(pages)) * 100, 2) if pages else 0,
        "history": history
    }


def lfu(pages, frame_count):
    """
    Least Frequently Used (LFU):
    Replaces the page with smallest reference frequency count.
    In case of a tie, FIFO order is used.
    """
    frames = []
    frequencies = {}
    faults = 0
    hits = 0
    history = []

    for page in pages:
        frequencies[page] = frequencies.get(page, 0) + 1

        if page in frames:
            hits += 1
            status = "HIT"
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                # Find page with minimal frequency
                min_freq = min(frequencies[f] for f in frames)
                candidates = [f for f in frames if frequencies[f] == min_freq]
                victim = candidates[0]  # FIFO tie break
                idx = frames.index(victim)
                frames[idx] = page

        padded_frames = list(frames) + [None] * (frame_count - len(frames))
        history.append({
            "page": page,
            "status": status,
            "frames": padded_frames
        })

    return {
        "algorithm": "LFU",
        "frame_count": frame_count,
        "page_faults": faults,
        "page_hits": hits,
        "total_requests": len(pages),
        "hit_ratio": round((hits / len(pages)) * 100, 2) if pages else 0,
        "fault_ratio": round((faults / len(pages)) * 100, 2) if pages else 0,
        "history": history
    }


def evaluate_beladys_anomaly():
    """
    Classic Belady's Anomaly Reference String:
    [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    Demonstrates that increasing frames from 3 to 4 increases page faults from 9 to 10 in FIFO!
    """
    belady_pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    res_3 = fifo(belady_pages, 3)
    res_4 = fifo(belady_pages, 4)
    return {
        "reference_string": belady_pages,
        "frames_3_faults": res_3["page_faults"],
        "frames_4_faults": res_4["page_faults"],
        "anomaly_observed": res_4["page_faults"] > res_3["page_faults"],
        "explanation": "Belady's Anomaly is the phenomenon where increasing the number of page frames results in an increase in the number of page faults for certain memory access patterns under FIFO replacement."
    }


def compare_page_algorithms(pages, frame_count):
    return {
        "fifo": fifo(pages, frame_count),
        "lru": lru(pages, frame_count),
        "optimal": optimal(pages, frame_count),
        "lfu": lfu(pages, frame_count)
    }


if __name__ == "__main__":
    test_pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    print("FIFO Result:", fifo(test_pages, 3)["page_faults"], "faults")
    print("LRU Result:", lru(test_pages, 3)["page_faults"], "faults")
    print("Optimal Result:", optimal(test_pages, 3)["page_faults"], "faults")
    print("LFU Result:", lfu(test_pages, 3)["page_faults"], "faults")
    print("Belady's Check:", evaluate_beladys_anomaly())
