# VeerSeva – Defence Welfare Management System

## Phase-III Integrated OS & DBMS Project Progress

**Course:** OS (PCS-502) & DBMS (PCS-503)  
**Institution:** Graphic Era Deemed to be University, Dehradun  
**Team Code:** OSDBMS/T210 (Team 210)  

### Team Members
- **Pooja Bisht** (Team Lead) – Student ID: `240221631` | `Kanchanb706@gmail.com`
- **Richa Maurya** – Student ID: `240221320` | `Richamaurya011@gmail.com`
- **Sakshi Kalkar** – Student ID: `240221444` | `Sakshi.kalkar8@gmail.com`

---

## Project Overview

VeerSeva is a centralized academic Defence Welfare Management System integrating core principles of **Operating Systems (OS)** and **Database Management Systems (DBMS)**. The system models welfare administration activities (application intake, document verification, rules checking, DBT grant disbursal) into OS processes and relational transactions.

---

## Operating Systems (OS) Simulation Suite

The OS component (`os_module/`) implements 7 interactive modules:

1. **CPU Scheduling (`cpu_scheduling.py`):**
   - First-Come First-Served (FCFS)
   - Shortest Job First (SJF Non-preemptive)
   - Shortest Remaining Time First (SRTF Preemptive)
   - Priority Scheduling (Non-preemptive)
   - Round Robin (Time-shared with configurable Quantum)
   - Performance metrics: Waiting Time, Turnaround Time, Response Time, and Gantt chart visualization.

2. **Deadlock Management & Banker's Algorithm (`bankers_algorithm.py`):**
   - Allocation Matrix, Maximum Claim Matrix, and Need Matrix calculation ($Need = Max - Allocation$)
   - Safety Algorithm verifying Safe Execution Sequences ($P1 \to P3 \to P4 \to P0 \to P2$)
   - Interactive Resource Request Evaluation for administrative resources (Verification Officers, Biometric Scanning Kits, Disbursal Slots).

3. **Virtual Memory & Page Replacement (`page_replacement.py`):**
   - Document caching in physical memory frames (Discharge Book, ECHS Card, PPO Certificate, Bonafide Marksheet)
   - Algorithms: FIFO, LRU, Optimal (Belady's OPT), LFU (Least Frequently Used)
   - Cache Hit Ratio, Page Fault Ratio, and Belady's Anomaly Demonstration.

4. **Disk I/O Track Scheduling (`disk_scheduling.py`):**
   - Hard disk seek optimization for storage archives across tracks (0 to 199)
   - Algorithms: FCFS, SSTF, SCAN (Elevator), C-SCAN, LOOK, C-LOOK
   - Total Head Movement (THM) calculation and interactive SVG trajectory path.

5. **Process Synchronization & Semaphores (`process_sync.py`):**
   - **Producer-Consumer Bounded Buffer:** Fixed capacity ($N=5$) with counting semaphores (`mutex`, `empty`, `full`)
   - **Readers-Writers Concurrency:** Shared reading for beneficiaries vs exclusive database write lock for admin updates.

6. **Contiguous Memory Allocation (`memory_management.py`):**
   - Dynamic partitioning algorithms: First-Fit, Best-Fit, Worst-Fit
   - Internal and External fragmentation tracking across RAM partitions.

7. **Process Lifecycle & PCB Inspector (`process_management.py`):**
   - Academic 5-State Machine: `NEW` $\to$ `READY` $\rightleftharpoons$ `RUNNING` $\to$ `TERMINATED` (with `WAITING`/`BLOCKED` for I/O & DB locks)
   - Live Process Control Block (PCB) inspector tracking PID, Program Counter (PC), CPU Registers (EAX, EBX, ECX, ESP), Memory Bounds, and Open File Descriptors.

---

## Database Management Systems (DBMS) Core

- **Relational Tables:** `users`, `schemes`, `eligibility_rules`, `applications`, `documents`, `application_status`, `notifications`, `audit_logs`.
- **Stored Procedures:** `CheckEligibility`, `AddNotification`, `LogAuditAction`, `AdvanceApplicationStatus`.
- **Triggers:** `trg_after_application_status_update` for automatic audit logging and status history tracking.
- **Indexes:** B-tree indexes on `user_id`, `scheme_id`, `current_status`, and `uploaded_at`.

---

## Project Architecture

```
User Request ──► DBMS Query/Transaction ──► OS Process Creation ──► Scheduling & Allocation ──► Execution & Response
```

---

## Running the Application

### 1. Launch Backend Server:
```bash
python backend/app.py
```
Server runs at `http://127.0.0.1:5000` (serves both API and frontend UI).

### 2. Launch Standalone Frontend:
Open `frontend/index.html` directly in any web browser. All OS simulations include client-side execution fallbacks.

---

## Academic Disclaimer
This project is an academic prototype developed for educational demonstration under courses PCS-502 & PCS-503.
