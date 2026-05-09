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
# ALGORITHMS (RR & SRTF)
# =========================
def round_robin(processes, quantum):
    time = 0
    queue = []
    completed = []
    gantt = []
    processes.sort(key=lambda x: x.arrival)
    i = 0
    while len(completed) < len(processes):
        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1
        if not queue:
            time += 1
            continue
        current = queue.pop(0)
        if current.start_time == -1:
            current.start_time = time
        exec_time = min(quantum, current.remaining)
        gantt.append(f"{current.pid}({time}-{time+exec_time})")
        time += exec_time
        current.remaining -= exec_time
        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1
        if current.remaining > 0:
            queue.append(current)
        else:
            current.completion = time
            completed.append(current)
    return completed, gantt

def srtf(processes):
    time = 0
    completed = []
    gantt = []
    processes.sort(key=lambda x: x.arrival)
    n = len(processes)
    while len(completed) < n:
        available = [p for p in processes if p.arrival <= time and p.remaining > 0]
        if not available:
            time += 1
            continue
        current = min(available, key=lambda x: x.remaining)
        if current.start_time == -1:
            current.start_time = time
        gantt.append(f"{current.pid}({time}-{time+1})")
        current.remaining -= 1
        time += 1
        if current.remaining == 0:
            current.completion = time
            completed.append(current)
    return completed, gantt

# =========================
# METRICS
# =========================
def calculate_metrics(processes):
    results = []
    if not processes: return results, 0, 0, 0
    for p in processes:
        tat = p.completion - p.arrival
        wt = tat - p.burst
        rt = p.start_time - p.arrival
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
        if pid == "":
            messagebox.showerror("Error", "Enter PID")
            return
        for p in process_list:
            if p.pid == pid:
                messagebox.showerror("Error", f"PID '{pid}' already exists!")
                return
        if arrival < 0 or burst <= 0:
            messagebox.showerror("Error", "Invalid values")
            return
        process_list.append(Process(pid, arrival, burst))
        tree.insert("", "end", values=(pid, arrival, burst))
        pid_entry.delete(0, tk.END)
        arrival_entry.delete(0, tk.END)
        burst_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Enter valid input")

def run():
    if not process_list:
        messagebox.showerror("Error", "No processes")
        return
    try:
        q_val = quantum_entry.get()
        quantum = int(q_val) if q_val else 2
        if quantum <= 0: raise ValueError
    except:
        messagebox.showerror("Error", "Invalid Quantum")
        return

    rr_proc = [Process(p.pid, p.arrival, p.burst) for p in process_list]
    srtf_proc = [Process(p.pid, p.arrival, p.burst) for p in process_list]

    rr_done, rr_gantt = round_robin(rr_proc, quantum)
    srtf_done, srtf_gantt = srtf(srtf_proc)

    rr_results, rr_wt, rr_tat, rr_rt = calculate_metrics(rr_done)
    srtf_results, srtf_wt, srtf_tat, srtf_rt = calculate_metrics(srtf_done)

    rr_table.delete(*rr_table.get_children())
    srtf_table.delete(*srtf_table.get_children())

    for r in rr_results: rr_table.insert("", "end", values=r)
    for r in srtf_results: srtf_table.insert("", "end", values=r)

    rr_gantt_label.config(text="RR Gantt: " + " -> ".join(rr_gantt))
    srtf_gantt_label.config(text="SRTF Gantt: " + " -> ".join(srtf_gantt))

    avg_label.config(
        text=f"AVERAGES SUMMARY\n"
             f"--------------------------------------------------\n"
             f"Round Robin:  WT = {rr_wt:.2f} | TAT = {rr_tat:.2f} | RT = {rr_rt:.2f}\n"
             f"SRTF       :  WT = {srtf_wt:.2f} | TAT = {srtf_tat:.2f} | RT = {srtf_rt:.2f}"
    )

def clear_all():
    global process_list
    process_list.clear()
    pid_entry.delete(0, tk.END)
    arrival_entry.delete(0, tk.END)
    burst_entry.delete(0, tk.END)
    quantum_entry.delete(0, tk.END)
    tree.delete(*tree.get_children())
    rr_table.delete(*rr_table.get_children())
    srtf_table.delete(*srtf_table.get_children())
    rr_gantt_label.config(text="")
    srtf_gantt_label.config(text="")
    avg_label.config(text="")

# =========================
# THEME COLORS
# =========================
BG_MAIN = "#121212"
BG_PANEL = "#1e1e1e"
FG_TEXT = "#e0e0e0"
ACCENT_BLUE = "#3d5afe"
ACCENT_GREEN = "#00e676"
ACCENT_RED = "#ff5252"
ACCENT_PURPLE = "#b388ff"

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("CPU Scheduling Simulator - Dark Mode")
root.geometry("1100x950")
root.configure(bg=BG_MAIN)

# STYLE CONFIG
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=BG_PANEL, foreground=FG_TEXT, fieldbackground=BG_PANEL, borderwidth=0)
style.map("Treeview", background=[('selected', ACCENT_BLUE)])
style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")

# INPUT FRAME
frame1 = tk.LabelFrame(root, text=" Input Panel ", padx=10, pady=10, bg=BG_MAIN, fg=ACCENT_BLUE, font=("Arial", 10, "bold"))
frame1.pack(fill="x", padx=20, pady=15)

labels = ["PID", "Arrival", "Burst", "Quantum (RR)"]
entries = []

for i, text in enumerate(labels):
    tk.Label(frame1, text=text, bg=BG_MAIN, fg=FG_TEXT).grid(row=0, column=i, padx=5, pady=2)
    
pid_entry = tk.Entry(frame1, width=12, bg="#333", fg="white", insertbackground="white", borderwidth=0)
arrival_entry = tk.Entry(frame1, width=12, bg="#333", fg="white", insertbackground="white", borderwidth=0)
burst_entry = tk.Entry(frame1, width=12, bg="#333", fg="white", insertbackground="white", borderwidth=0)
quantum_entry = tk.Entry(frame1, width=12, bg="#333", fg="white", insertbackground="white", borderwidth=0)

pid_entry.grid(row=1, column=0, padx=5, pady=5)
arrival_entry.grid(row=1, column=1, padx=5, pady=5)
burst_entry.grid(row=1, column=2, padx=5, pady=5)
quantum_entry.grid(row=1, column=3, padx=5, pady=5)

# BUTTONS
btn_style = {"font": ("Arial", 9, "bold"), "padx": 15, "pady": 5, "borderwidth": 0, "cursor": "hand2"}
tk.Button(frame1, text="Add Process", command=add_process, bg=ACCENT_BLUE, fg="white", **btn_style).grid(row=1, column=4, padx=5)
tk.Button(frame1, text="Run Simulation", command=run, bg=ACCENT_GREEN, fg="black", **btn_style).grid(row=1, column=5, padx=5)
tk.Button(frame1, text="Reset", command=clear_all, bg=ACCENT_RED, fg="white", **btn_style).grid(row=1, column=6, padx=5)

# MAIN TABLE
tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst"), show="headings", height=5)
for c in ("PID", "Arrival", "Burst"):
    tree.heading(c, text=c)
    tree.column(c, width=250, anchor="center")
tree.pack(fill="x", padx=20, pady=10)

# RESULTS TABLES
res_frame = tk.Frame(root, bg=BG_MAIN)
res_frame.pack(fill="both", expand=True, padx=20)

# RR Side
tk.Label(res_frame, text="ROUND ROBIN RESULTS", bg=BG_MAIN, fg=ACCENT_PURPLE, font=("Arial", 10, "bold")).pack(pady=(10,0))
rr_table = ttk.Treeview(res_frame, columns=("PID", "WT", "TAT", "RT"), show="headings", height=5)
for c in ("PID", "WT", "TAT", "RT"):
    rr_table.heading(c, text=c)
    rr_table.column(c, width=180, anchor="center")
rr_table.pack(fill="x", pady=5)

# SRTF Side
tk.Label(res_frame, text="SRTF RESULTS", bg=BG_MAIN, fg=ACCENT_GREEN, font=("Arial", 10, "bold")).pack(pady=(10,0))
srtf_table = ttk.Treeview(res_frame, columns=("PID", "WT", "TAT", "RT"), show="headings", height=5)
for c in ("PID", "WT", "TAT", "RT"):
    srtf_table.heading(c, text=c)
    srtf_table.column(c, width=180, anchor="center")
srtf_table.pack(fill="x", pady=5)

# GANTT LABELS
gantt_style = {"bg": BG_PANEL, "justify": "left", "anchor": "w", "wraplength": 1000, "font": ("Consolas", 9), "bd": 1, "relief": "solid", "padx": 10, "pady": 10}
rr_gantt_label = tk.Label(root, text="RR Gantt Chart will appear here...", fg=ACCENT_PURPLE, **gantt_style)
rr_gantt_label.pack(fill="x", padx=20, pady=5)

srtf_gantt_label = tk.Label(root, text="SRTF Gantt Chart will appear here...", fg=ACCENT_GREEN, **gantt_style)
srtf_gantt_label.pack(fill="x", padx=20, pady=5)

# AVERAGES
avg_label = tk.Label(root, text="", fg="white", bg=BG_MAIN, font=("Courier", 11, "bold"), justify="left")
avg_label.pack(pady=20)

root.mainloop()