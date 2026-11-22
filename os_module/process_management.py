"""
VeerSeva OS Module - Process Lifecycle & Process Control Block (PCB) Management
Simulates the academic 5-state process lifecycle:
- NEW: Process is being created by welfare application submission
- READY: Process is in the ready queue waiting for CPU allocation
- RUNNING: Process instructions are being executed by CPU
- WAITING (BLOCKED): Process is waiting for an I/O event or DBMS transaction lock
- TERMINATED: Process has finished execution and resources are deallocated

Also tracks the Process Control Block (PCB) fields:
- Process ID (PID)
- Process State
- Program Counter (PC)
- CPU Registers (Accumulator, Index, Stack Pointer)
- CPU Scheduling Information (Priority, Burst, Queue)
- Memory Management Information (Base, Limit, Page Table Pointer)
- Accounting Information (CPU time used, Time limits)
- I/O Status Information (List of open files/documents, I/O devices assigned)
"""

import time
import random

class ProcessControlBlock:
    def __init__(self, pid, name, burst_time, priority=1, memory_size=64):
        self.pid = pid
        self.name = name
        self.state = "NEW"  # NEW, READY, RUNNING, WAITING, TERMINATED
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.memory_base = 0x1000 + (pid * 0x0800)
        self.memory_limit = memory_size * 1024  # in bytes
        self.program_counter = self.memory_base
        self.cpu_registers = {
            "EAX": 0,
            "EBX": 0,
            "ECX": 0,
            "ESP": self.memory_base + self.memory_limit - 4
        }
        self.open_files = [f"/var/veerseva/docs/doc_app_{pid}.pdf", "/var/log/veerseva_audit.log"]
        self.io_devices = []
        self.cpu_time_used = 0
        self.creation_time = time.strftime("%H:%M:%S")
        self.history = [{"state": "NEW", "time": self.creation_time, "event": "Process instantiated in PCB table"}]

    def transition(self, new_state, event_desc=""):
        old_state = self.state
        self.state = new_state
        entry = {
            "from": old_state,
            "to": new_state,
            "event": event_desc or f"Transitioned from {old_state} to {new_state}",
            "time": time.strftime("%H:%M:%S")
        }
        self.history.append(entry)
        if new_state == "RUNNING":
            self.program_counter += 4
            self.cpu_registers["EAX"] += random.randint(1, 10)
        return entry

    def execute_slice(self, time_slice=1):
        if self.state != "RUNNING":
            return {"error": "Process must be in RUNNING state to execute"}
        run_dur = min(time_slice, self.remaining_time)
        self.remaining_time -= run_dur
        self.cpu_time_used += run_dur
        self.program_counter += (run_dur * 8)
        self.cpu_registers["EAX"] += run_dur * 10
        self.cpu_registers["EBX"] += 1

        if self.remaining_time <= 0:
            self.transition("TERMINATED", "Process completed execution and returned status code 0")
        return {
            "executed_ms": run_dur,
            "remaining_ms": self.remaining_time,
            "state": self.state
        }

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "priority": self.priority,
            "program_counter": hex(self.program_counter),
            "memory_range": f"{hex(self.memory_base)} - {hex(self.memory_base + self.memory_limit)}",
            "memory_size_kb": self.memory_limit // 1024,
            "registers": {k: hex(v) if isinstance(v, int) else v for k, v in self.cpu_registers.items()},
            "open_files": self.open_files,
            "cpu_time_used": self.cpu_time_used,
            "history": self.history
        }


class ProcessLifecycleManager:
    def __init__(self):
        self.processes = {}
        self.ready_queue = []
        self.waiting_queue = []
        self.running_process = None
        self.terminated_list = []
        self._init_defaults()

    def _init_defaults(self):
        default_procs = [
            (101, "P1: Document OCR Validation", 5, 2, 64),
            (102, "P2: Aadhaar Biometric Match", 3, 1, 128),
            (103, "P3: DBMS Eligibility Evaluation", 4, 3, 32),
            (104, "P4: Sanction Officer Review", 2, 2, 48),
            (105, "P5: Direct Bank Transfer (DBT)", 6, 1, 96),
        ]
        for pid, name, burst, prio, mem in default_procs:
            pcb = ProcessControlBlock(pid, name, burst, prio, mem)
            # Admit to ready
            pcb.transition("READY", "Admitted by Long-Term Job Scheduler to Ready Queue")
            self.processes[pid] = pcb
            self.ready_queue.append(pid)

    def admit_process(self, name, burst_time, priority=2, memory_kb=64):
        new_pid = max(self.processes.keys(), default=100) + 1
        pcb = ProcessControlBlock(new_pid, name, burst_time, priority, memory_kb)
        self.processes[new_pid] = pcb
        pcb.transition("READY", "Admitted to Ready Queue")
        self.ready_queue.append(new_pid)
        return pcb.to_dict()

    def dispatch(self, pid=None):
        """Short-term scheduler dispatches process to RUNNING"""
        if not self.ready_queue:
            return {"error": "Ready queue is empty"}

        if pid is not None and pid in self.ready_queue:
            target_pid = pid
            self.ready_queue.remove(target_pid)
        else:
            target_pid = self.ready_queue.pop(0)

        # Preempt current running if any
        if self.running_process is not None:
            old_proc = self.processes.get(self.running_process)
            if old_proc and old_proc.state == "RUNNING":
                old_proc.transition("READY", "Preempted by scheduler (Context Switch)")
                self.ready_queue.append(self.running_process)

        self.running_process = target_pid
        pcb = self.processes[target_pid]
        pcb.transition("RUNNING", "Dispatched to CPU by Short-Term Scheduler")
        return {"dispatched_pid": target_pid, "pcb": pcb.to_dict()}

    def trigger_io(self, pid=None):
        """Process requests I/O or waits for database lock -> WAITING"""
        target = pid or self.running_process
        if not target or target not in self.processes:
            return {"error": "No running process to block for I/O"}

        pcb = self.processes[target]
        if pcb.state != "RUNNING":
            return {"error": f"Process {target} is not RUNNING (current: {pcb.state})"}

        pcb.transition("WAITING", "Blocked waiting for Disk I/O / DBMS Transaction lock")
        if self.running_process == target:
            self.running_process = None
        self.waiting_queue.append(target)
        return {"blocked_pid": target, "pcb": pcb.to_dict()}

    def complete_io(self, pid=None):
        """I/O event completes -> process returns to READY queue"""
        if not self.waiting_queue:
            return {"error": "Waiting queue is empty"}

        target = pid if pid in self.waiting_queue else self.waiting_queue.pop(0)
        if pid in self.waiting_queue:
            self.waiting_queue.remove(target)

        pcb = self.processes[target]
        pcb.transition("READY", "I/O operation completed, returned to Ready Queue")
        self.ready_queue.append(target)
        return {"ready_pid": target, "pcb": pcb.to_dict()}

    def terminate_process(self, pid=None):
        target = pid or self.running_process
        if not target or target not in self.processes:
            return {"error": "No process to terminate"}

        pcb = self.processes[target]
        pcb.transition("TERMINATED", "Terminated and resources released back to OS")
        if self.running_process == target:
            self.running_process = None
        if target in self.ready_queue:
            self.ready_queue.remove(target)
        if target in self.waiting_queue:
            self.waiting_queue.remove(target)
        if target not in self.terminated_list:
            self.terminated_list.append(target)
        return {"terminated_pid": target, "pcb": pcb.to_dict()}

    def get_system_state(self):
        return {
            "running": self.processes[self.running_process].to_dict() if self.running_process else None,
            "ready_queue": [self.processes[pid].to_dict() for pid in self.ready_queue if pid in self.processes],
            "waiting_queue": [self.processes[pid].to_dict() for pid in self.waiting_queue if pid in self.processes],
            "terminated_list": [self.processes[pid].to_dict() for pid in self.terminated_list if pid in self.processes],
            "all_processes": [p.to_dict() for p in self.processes.values()]
        }


process_lifecycle_manager = ProcessLifecycleManager()
