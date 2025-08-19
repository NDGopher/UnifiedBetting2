import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path


SPORTS_MARKETS = {
    "MLB": ["moneyline", "spread", "total"],
    "MLS": ["moneyline", "spread", "total"],
    "NFL": ["moneyline", "spread", "total"],
    "WNBA": ["moneyline", "spread", "total"],
    "NCAAF": ["moneyline", "total"],
    "EPL": ["moneyline", "spread", "total"],
    "LA_LIGA": ["total"],
    "NBA": ["moneyline", "spread", "total"],
    "NHL": ["moneyline", "spread", "total"],
}


def main():
    root = tk.Tk()
    root.title("Select Sports and Markets")
    root.geometry("1100x680")
    root.minsize(980, 600)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    # Light modern look
    style.configure("TFrame", background="#f6f7fb")
    style.configure("TLabelframe", background="#f6f7fb")
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", background="#f6f7fb", font=("Segoe UI", 10))
    style.configure("TCheckbutton", background="#f6f7fb", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))

    root.configure(bg="#f6f7fb")
    wrapper = ttk.Frame(root, padding=12)
    wrapper.pack(fill=tk.BOTH, expand=True)

    header = ttk.Label(wrapper, text="Choose what to monitor (PTO tabs)", font=("Segoe UI", 12, "bold"))
    header.pack(anchor=tk.W, pady=(0, 10))

    body = ttk.Frame(wrapper)
    body.pack(fill=tk.BOTH, expand=True)

    # Two option columns + summary
    opt_col1 = ttk.Frame(body)
    opt_col1.grid(row=0, column=0, sticky="nsew")
    opt_col2 = ttk.Frame(body)
    opt_col2.grid(row=0, column=1, sticky="nsew", padx=(12, 12))
    right = ttk.Frame(body, width=320)
    right.grid(row=0, column=2, sticky="nsew")
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.columnconfigure(2, weight=0)
    body.rowconfigure(0, weight=1)
    sum_title = ttk.Label(right, text="Selections", font=("Segoe UI", 10, "bold"))
    sum_title.pack(anchor=tk.W)
    summary_box = tk.Listbox(right, height=16, font=("Consolas", 10))
    summary_box.pack(fill=tk.BOTH, expand=False, pady=(6, 8))

    prefs_frame = ttk.LabelFrame(right, text="Preferences")
    prefs_frame.pack(fill=tk.X, pady=(6, 8))
    browser_var = tk.StringVar(value="embedded")
    row1 = ttk.Frame(prefs_frame); row1.pack(fill=tk.X, padx=8, pady=(6,2))
    ttk.Label(row1, text="Dashboard window:").pack(side=tk.LEFT)
    ttk.Radiobutton(row1, text="Embedded (recommended)", value="embedded", variable=browser_var).pack(side=tk.LEFT, padx=6)
    row1b = ttk.Frame(prefs_frame); row1b.pack(fill=tk.X, padx=8, pady=(2,2))
    ttk.Label(row1b, text="or External:").pack(side=tk.LEFT)
    ttk.Radiobutton(row1b, text="Chrome", value="chrome", variable=browser_var).pack(side=tk.LEFT, padx=6)
    ttk.Radiobutton(row1b, text="Firefox", value="firefox", variable=browser_var).pack(side=tk.LEFT, padx=6)
    ttk.Radiobutton(row1b, text="Comet", value="comet", variable=browser_var).pack(side=tk.LEFT, padx=6)

    row2 = ttk.Frame(prefs_frame); row2.pack(fill=tk.X, padx=8, pady=(2,8))
    pto_headless_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(row2, text="Run PTO hidden (headless)", variable=pto_headless_var).pack(side=tk.LEFT)

    row3 = ttk.Frame(prefs_frame); row3.pack(fill=tk.X, padx=8, pady=(0,8))
    ttk.Label(row3, text="Attach Chrome debug port:").pack(side=tk.LEFT)
    dbg_var = tk.StringVar(value="")
    dbg_entry = ttk.Entry(row3, textvariable=dbg_var, width=8)
    dbg_entry.pack(side=tk.LEFT, padx=6)

    vars_map: dict[str, dict[str, tk.BooleanVar]] = {}

    def refresh_summary():
        summary_box.delete(0, tk.END)
        lines = []
        for sport, mvars in vars_map.items():
            chosen = [m for m, v in mvars.items() if v.get()]
            if chosen:
                lines.append(f"{sport}: {', '.join(x.capitalize() for x in chosen)}")
        if not lines:
            summary_box.insert(tk.END, "(none selected)")
        else:
            for ln in lines:
                summary_box.insert(tk.END, ln)

    # Build options in two columns
    items = list(SPORTS_MARKETS.items())
    for idx, (sport, markets) in enumerate(items):
        parent = opt_col1 if (idx % 2 == 0) else opt_col2
        grp = ttk.LabelFrame(parent, text=sport)
        grp.pack(fill=tk.X, pady=6)
        vars_map[sport] = {}
        row = ttk.Frame(grp)
        row.pack(fill=tk.X, padx=8, pady=6)
        for m in markets:
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(row, text=m.capitalize(), variable=var, command=refresh_summary)
            chk.pack(side=tk.LEFT, padx=10)
            vars_map[sport][m] = var

    foot = ttk.Frame(wrapper)
    foot.pack(fill=tk.X, pady=(10, 0))
    status = ttk.Label(foot, text="Selections will be saved to sports_selection.json", foreground="#6b7280")
    status.pack(side=tk.LEFT)

    def submit():
        selected: list[str] = []
        for s, mvars in vars_map.items():
            for m, v in mvars.items():
                if v.get():
                    selected.append(f"{s}:{m}".lower())
        payload = {
            "selections": selected,
            "opts": {
                "open_browser": browser_var.get(),
                "pto_headless": bool(pto_headless_var.get()),
                "chrome_debug_port": int(dbg_var.get()) if dbg_var.get().strip().isdigit() else None,
            }
        }
        Path("sports_selection.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        # Also store UI prefs for dashboard quick-open default
        Path("ui_prefs.json").write_text(json.dumps({"open_browser": browser_var.get()}), encoding="utf-8")
        root.destroy()

    start_btn = ttk.Button(foot, text="Start", command=submit)
    start_btn.pack(side=tk.RIGHT)

    refresh_summary()
    root.mainloop()


if __name__ == "__main__":
    main()


