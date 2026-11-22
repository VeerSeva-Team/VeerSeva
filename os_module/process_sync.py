"""
VeerSeva OS Module - Process Synchronization & Concurrency Control
Implements:
1. Producer-Consumer Problem (Bounded Buffer using Semaphores: mutex, empty, full)
   Scenario: Defence welfare application intake queue.
   - Producers: Web portal users submitting applications.
   - Consumers: Background verification worker threads.
2. Readers-Writers Problem (Database Concurrency)
   Scenario: Beneficiary queries (Readers) vs Administrative scheme updates (Writers).
"""

import threading
import time
from collections import deque

class BoundedBufferSync:
    """
    Simulates the classical Producer-Consumer bounded buffer with counting semaphores:
    - mutex: binary semaphore for mutual exclusion on buffer access
    - empty: counting semaphore for tracking empty slots (initially capacity)
    - full:  counting semaphore for tracking filled slots (initially 0)
    """
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.buffer = []
        self.mutex = 1
        self.empty = capacity
        self.full = 0
        self.log_history = []
        self.produced_count = 0
        self.consumed_count = 0

    def get_state(self):
        return {
            "capacity": self.capacity,
            "buffer": list(self.buffer),
            "current_size": len(self.buffer),
            "semaphores": {
                "mutex": self.mutex,
                "empty": self.empty,
                "full": self.full
            },
            "produced_count": self.produced_count,
            "consumed_count": self.consumed_count,
            "recent_logs": self.log_history[-10:]
        }

    def produce(self, item_name=None):
        if self.empty <= 0:
            msg = f"Buffer FULL ({self.capacity}/{self.capacity}): Producer BLOCKED on semWait(empty). Cannot insert."
            self.log_history.append({"type": "BLOCKED", "action": "PRODUCE", "message": msg, "time": time.strftime("%H:%M:%S")})
            return {"success": False, "message": msg, "state": self.get_state()}

        # semWait(empty)
        self.empty -= 1
        # semWait(mutex)
        self.mutex = 0

        self.produced_count += 1
        item_id = f"APP-{1000 + self.produced_count}"
        name = item_name or f"Welfare Application #{self.produced_count}"
        item = {"id": item_id, "name": name, "timestamp": time.strftime("%H:%M:%S")}
        self.buffer.append(item)

        # semSignal(mutex)
        self.mutex = 1
        # semSignal(full)
        self.full += 1

        msg = f"Produced {item_id} ('{name}'). Buffer: {len(self.buffer)}/{self.capacity}. Semaphores: [mutex={self.mutex}, empty={self.empty}, full={self.full}]."
        self.log_history.append({"type": "PRODUCED", "action": "PRODUCE", "message": msg, "item": item, "time": time.strftime("%H:%M:%S")})

        return {"success": True, "message": msg, "item": item, "state": self.get_state()}

    def consume(self):
        if self.full <= 0:
            msg = "Buffer EMPTY (0/5): Consumer BLOCKED on semWait(full). Waiting for new applications."
            self.log_history.append({"type": "BLOCKED", "action": "CONSUME", "message": msg, "time": time.strftime("%H:%M:%S")})
            return {"success": False, "message": msg, "state": self.get_state()}

        # semWait(full)
        self.full -= 1
        # semWait(mutex)
        self.mutex = 0

        item = self.buffer.pop(0)
        self.consumed_count += 1

        # semSignal(mutex)
        self.mutex = 1
        # semSignal(empty)
        self.empty += 1

        msg = f"Consumed {item['id']} for verification. Remaining in buffer: {len(self.buffer)}/{self.capacity}. Semaphores: [mutex={self.mutex}, empty={self.empty}, full={self.full}]."
        self.log_history.append({"type": "CONSUMED", "action": "CONSUME", "message": msg, "item": item, "time": time.strftime("%H:%M:%S")})

        return {"success": True, "message": msg, "item": item, "state": self.get_state()}

    def reset(self):
        self.buffer.clear()
        self.mutex = 1
        self.empty = self.capacity
        self.full = 0
        self.produced_count = 0
        self.consumed_count = 0
        self.log_history.clear()
        return self.get_state()


class ReadersWritersSync:
    """
    Simulates the First Readers-Writers Problem (Readers Preference):
    - readcount: number of active readers currently reading welfare scheme database
    - mutex: binary semaphore ensuring mutual exclusion when updating readcount
    - wrt: binary semaphore ensuring mutual exclusion for writers
    """
    def __init__(self):
        self.read_count = 0
        self.mutex = 1
        self.wrt = 1
        self.active_readers = []
        self.active_writer = None
        self.log_history = []

    def get_state(self):
        return {
            "read_count": self.read_count,
            "semaphores": {
                "mutex": self.mutex,
                "wrt": self.wrt
            },
            "active_readers": list(self.active_readers),
            "active_writer": self.active_writer,
            "recent_logs": self.log_history[-10:]
        }

    def start_read(self, reader_id):
        if self.active_writer is not None:
            msg = f"Reader {reader_id} BLOCKED: Writer '{self.active_writer}' holds exclusive database lock (wrt=0)."
            self.log_history.append({"type": "BLOCKED", "message": msg, "time": time.strftime("%H:%M:%S")})
            return {"success": False, "message": msg, "state": self.get_state()}

        # semWait(mutex)
        self.mutex = 0
        self.read_count += 1
        if self.read_count == 1:
            # First reader acquires wrt lock to prevent writers
            self.wrt = 0
        # semSignal(mutex)
        self.mutex = 1

        self.active_readers.append(reader_id)
        msg = f"Reader {reader_id} started querying database. Active readers: {self.read_count}. Lock [wrt={self.wrt}]."
        self.log_history.append({"type": "READ_START", "message": msg, "time": time.strftime("%H:%M:%S")})
        return {"success": True, "message": msg, "state": self.get_state()}

    def end_read(self, reader_id):
        if reader_id not in self.active_readers:
            return {"success": False, "message": f"Reader {reader_id} not currently reading.", "state": self.get_state()}

        self.active_readers.remove(reader_id)
        # semWait(mutex)
        self.mutex = 0
        self.read_count -= 1
        if self.read_count == 0:
            # Last reader releases wrt lock so writers may proceed
            self.wrt = 1
        # semSignal(mutex)
        self.mutex = 1

        msg = f"Reader {reader_id} finished reading. Remaining readers: {self.read_count}. Lock [wrt={self.wrt}]."
        self.log_history.append({"type": "READ_END", "message": msg, "time": time.strftime("%H:%M:%S")})
        return {"success": True, "message": msg, "state": self.get_state()}

    def start_write(self, writer_id):
        if self.wrt == 0 or self.read_count > 0 or self.active_writer is not None:
            reason = f"Active readers ({self.read_count})" if self.read_count > 0 else f"Active writer ({self.active_writer})"
            msg = f"Writer {writer_id} BLOCKED: Database is in use by {reason}. Must wait for wrt lock."
            self.log_history.append({"type": "BLOCKED", "message": msg, "time": time.strftime("%H:%M:%S")})
            return {"success": False, "message": msg, "state": self.get_state()}

        # semWait(wrt)
        self.wrt = 0
        self.active_writer = writer_id
        msg = f"Writer {writer_id} acquired exclusive database lock. Updating welfare schemes table."
        self.log_history.append({"type": "WRITE_START", "message": msg, "time": time.strftime("%H:%M:%S")})
        return {"success": True, "message": msg, "state": self.get_state()}

    def end_write(self):
        if self.active_writer is None:
            return {"success": False, "message": "No active writer to finish.", "state": self.get_state()}

        w_id = self.active_writer
        self.active_writer = None
        # semSignal(wrt)
        self.wrt = 1

        msg = f"Writer {w_id} finished writing and released exclusive database lock (wrt=1)."
        self.log_history.append({"type": "WRITE_END", "message": msg, "time": time.strftime("%H:%M:%S")})
        return {"success": True, "message": msg, "state": self.get_state()}


# Global singletons for demonstration
bounded_buffer = BoundedBufferSync(capacity=5)
readers_writers = ReadersWritersSync()
