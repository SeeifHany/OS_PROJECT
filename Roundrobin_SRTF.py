import tkinter as tk
from tkinter import ttk, messagebox

# =========================
# PROCESS CLASS
# =========================
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = -1
        self.completion = 0

# =========================
# ALGORITHMS (RR & SJF)
# =========================

def round_robin(processes, quantum):
    time = 0
    queue = []
    completed = []
    gantt = []
    
    procs = sorted(processes, key=lambda x: x.arrival)
    i = 0
    
    while len(completed) < len(procs):
        while i < len(procs) and procs[i].arrival <= time:
            queue.append(procs[i])
            i += 1
            
        if not queue:
            if i < len(procs):
                time = procs[i].arrival
                continue
            else:
                break
                
        current = queue.pop(0)
        
        if current.start_time == -1:
            current.start_time = time
            
        exec_time = min(quantum, current.remaining)
        gantt.append(f"{current.pid}({time}-{time+exec_time})")
        
        time += exec_time
        current.remaining -= exec_time
        
        
        while i < len(procs) and procs[i].arrival <= time:
            queue.append(procs[i])
            i += 1
            
        if current.remaining > 0:
            queue.append(current)
        else:
            current.completion = time
            completed.append(current)
            
    return completed, gantt

def sjf_algorithm(processes):
    time = 0
    completed = []
    gantt = []
    n = len(processes)
    
    while len(completed) < n:
       
        available = [p for p in processes if p.arrival <= time and p.completion == 0]
        
        if not available:
            
            next_arrival = min([p.arrival for p in processes if p.completion == 0])
            time = next_arrival
            continue
            
       
        current = min(available, key=lambda x: x.burst)
        
        current.start_time = time
        start = time
        time += current.burst
        
        current.completion = time
        current.remaining = 0
        
        gantt.append(f"{current.pid}({start}-{time})")
        completed.append(current)
        
    return completed, gantt

# =========================
# METRICS CALCULATION
# =========================
def calculate_metrics(processes):
    results = []
    if not processes: return results, 0, 0, 0
    for p in processes:
        tat = p.completion - p.arrival # Turnaround Time [cite: 11]
        wt = tat - p.burst             # Waiting Time [cite: 11]
        rt = p.start_time - p.arrival  # Response Time [cite: 11]
        results.append((p.pid, wt, tat, rt))
    
    avg_wt = sum(r[1] for r in results) / len(results)
    avg_tat = sum(r[2] for r in results) / len(results)
    avg_rt = sum(r[3] for r in results) / len(results)
    return results, avg_wt, avg_tat, avg_rt

# =========================
# GUI LOGIC
# =========================
process_list = []

def add_process():
    try:
        pid = pid_entry.get().strip()
        arrival = int(arrival_entry.get())
        burst = int(burst_entry.get())
        
      
        if pid == "": raise ValueError
        if any(p.pid == pid for p in process_list):
            messagebox.showerror("Error", "Duplicate PID!")
            return
        if arrival < 0 or burst <= 0:
            messagebox.showerror("Error", "Invalid Arrival/Burst time!")
            return
            
        process_list.append(Process(pid, arrival, burst))
        tree.insert("", "end", values=(pid, arrival, burst))
        
        pid_entry.delete(0, tk.END)
        arrival_entry.delete(0, tk.END)
        burst_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Please enter valid numeric data.")

def run_simulation():
    if not process_list:
        messagebox.showerror("Error", "No processes added!")
        return
    try:
        q_val = quantum_entry.get()
        quantum = int(q_val) if q_val else 2
        if quantum <= 0: raise ValueError
    except:
        messagebox.showerror("Error", "Invalid Quantum Value!")
        return

    
    rr_proc = [Process(p.pid, p.arrival, p.burst) for p in process_list]
    sjf_proc = [Process(p.pid, p.arrival, p.burst) for p in process_list]

    
    rr_done, rr_gantt = round_robin(rr_proc, quantum)
    sjf_done, sjf_gantt = sjf_algorithm(sjf_proc)

   
    rr_res, rr_awt, rr_atat, rr_art = calculate_metrics(rr_done)
    sjf_res, sjf_awt, sjf_atat, sjf_art = calculate_metrics(sjf_done)

    
    rr_table.delete(*rr_table.get_children())
    sjf_table.delete(*sjf_table.get_children())

    for r in sorted(rr_res, key=lambda x: x[0]): rr_table.insert("", "end", values=r)
    for r in sorted(sjf_res, key=lambda x: x[0]): sjf_table.insert("", "end", values=r)

    rr_gantt_label.config(text="RR Gantt Chart: " + " -> ".join(rr_gantt))
    sjf_gantt_label.config(text="SJF Gantt Chart: " + " -> ".join(sjf_gantt))

    avg_label.config(
        text=f"COMPARISON SUMMARY\n"
             f"--------------------------------------------------\n"
             f"Round Robin:  Avg WT = {rr_awt:.2f} | Avg TAT = {rr_atat:.2f} | Avg RT = {rr_art:.2f}\n"
             f"SJF        :  Avg WT = {sjf_awt:.2f} | Avg TAT = {sjf_atat:.2f} | Avg RT = {sjf_art:.2f}"
    )

def reset():
    global process_list
    process_list.clear()
    tree.delete(*tree.get_children())
    rr_table.delete(*rr_table.get_children())
    sjf_table.delete(*sjf_table.get_children())
    rr_gantt_label.config(text="RR Gantt Chart will appear here...")
    sjf_gantt_label.config(text="SJF Gantt Chart will appear here...")
    avg_label.config(text="")

# =========================
# UI SETUP (Dark Theme)
# =========================
root = tk.Tk()
root.title("CPU Scheduling: RR vs SJF (Project C5)")
root.geometry("1000x900")
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0)
style.configure("Treeview.Heading", background="#333", foreground="white")

# Input Panel 
input_frame = tk.LabelFrame(root, text=" Input Panel ", bg="#121212", fg="#b388ff", font=("Arial", 10, "bold"))
input_frame.pack(fill="x", padx=20, pady=10)

fields = [("PID", 0), ("Arrival Time", 1), ("Burst Time", 2), ("Quantum (RR)", 3)]
entries = []

tk.Label(input_frame, text="PID", bg="#121212", fg="white").grid(row=0, column=0)
pid_entry = tk.Entry(input_frame, width=10, bg="#333", fg="white")
pid_entry.grid(row=1, column=0, padx=5, pady=5)

tk.Label(input_frame, text="Arrival", bg="#121212", fg="white").grid(row=0, column=1)
arrival_entry = tk.Entry(input_frame, width=10, bg="#333", fg="white")
arrival_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Burst", bg="#121212", fg="white").grid(row=0, column=2)
burst_entry = tk.Entry(input_frame, width=10, bg="#333", fg="white")
burst_entry.grid(row=1, column=2, padx=5, pady=5)

tk.Label(input_frame, text="Quantum", bg="#121212", fg="white").grid(row=0, column=3)
quantum_entry = tk.Entry(input_frame, width=10, bg="#333", fg="white")
quantum_entry.grid(row=1, column=3, padx=5, pady=5)

tk.Button(input_frame, text="Add Process", command=add_process, bg="#3d5afe", fg="white", bd=0, padx=10).grid(row=1, column=4, padx=5)
tk.Button(input_frame, text="Run Simulation", command=run_simulation, bg="#00e676", fg="black", bd=0, padx=10).grid(row=1, column=5, padx=5)
tk.Button(input_frame, text="Reset", command=reset, bg="#ff5252", fg="white", bd=0, padx=10).grid(row=1, column=6, padx=5)

# Process Table
tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst"), show="headings", height=5)
for c in ("PID", "Arrival", "Burst"): tree.heading(c, text=c); tree.column(c, anchor="center")
tree.pack(fill="x", padx=20, pady=5)

# Results Tables 
tk.Label(root, text="ROUND ROBIN RESULTS", bg="#121212", fg="#b388ff", font=("Arial", 10, "bold")).pack()
rr_table = ttk.Treeview(root, columns=("PID", "WT", "TAT", "RT"), show="headings", height=5)
for c in ("PID", "WT", "TAT", "RT"): rr_table.heading(c, text=c); rr_table.column(c, anchor="center")
rr_table.pack(fill="x", padx=20, pady=5)

tk.Label(root, text="SJF RESULTS (Non-Preemptive)", bg="#121212", fg="#00e676", font=("Arial", 10, "bold")).pack()
sjf_table = ttk.Treeview(root, columns=("PID", "WT", "TAT", "RT"), show="headings", height=5)
for c in ("PID", "WT", "TAT", "RT"): sjf_table.heading(c, text=c); sjf_table.column(c, anchor="center")
sjf_table.pack(fill="x", padx=20, pady=5)

# Gantt Charts [cite: 232, 237]
rr_gantt_label = tk.Label(root, text="RR Gantt Chart will appear here...", bg="#1e1e1e", fg="#b388ff", font=("Consolas", 9), wraplength=900, pady=10)
rr_gantt_label.pack(fill="x", padx=20, pady=5)

sjf_gantt_label = tk.Label(root, text="SJF Gantt Chart will appear here...", bg="#1e1e1e", fg="#00e676", font=("Consolas", 9), wraplength=900, pady=10)
sjf_gantt_label.pack(fill="x", padx=20, pady=5)

# Summary 
avg_label = tk.Label(root, text="", bg="#121212", fg="white", font=("Courier", 11, "bold"))
avg_label.pack(pady=10)

root.mainloop()