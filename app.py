
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


# Function to scan Wi-Fi networks
def scan_wifi():

    for item in wifi_table.get_children():
        wifi_table.delete(item)

    status_label.config(text="Scanning Wi-Fi networks...")
    window.update_idletasks()

    command = [
        "netsh", "wlan", "show",
        "networks", "mode=bssid"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            messagebox.showerror("Scan Error", result.stderr)
            status_label.config(text="Scan failed")
            return

        networks = []
        current_network = None
        current_ap = None

        def save_ap():
            nonlocal current_ap

            if current_ap is not None:
                networks.append(current_ap)
                current_ap = None

        for line in result.stdout.splitlines():

            line = line.strip()

            # Detect Wi-Fi network name
            if line.startswith("SSID ") and ":" in line:
                save_ap()

                name = line.split(":", 1)[1].strip()

                current_network = {
                    "ssid": name,
                    "security": "-",
                    "band": "-",
                    "signal": "-",
                    "channel": "-"
                }

            elif line.startswith("Authentication") and current_network:
                current_network["security"] = line.split(":", 1)[1].strip()

            elif line.startswith("BSSID ") and ":" in line and current_network:
                save_ap()
                current_ap = current_network.copy()

            elif line.startswith("Signal") and current_ap:
                current_ap["signal"] = line.split(":", 1)[1].strip()

            elif line.startswith("Band") and current_ap:
                current_ap["band"] = line.split(":", 1)[1].strip()

            elif line.startswith("Channel") and current_ap:
                current_ap["channel"] = line.split(":", 1)[1].strip()

        save_ap()

        # Display results in table
        for network in networks:
            wifi_table.insert(
                "",
                tk.END,
                values=(
                    network["ssid"],
                    network["signal"],
                    network["security"],
                    network["band"],
                    network["channel"]
                )
            )

        # Update total access point count
        total_label.config(
            text=f"Total Access Points Found: {len(networks)}"
        )

        status_label.config(
            text=f"Scan completed! {len(networks)} access point(s) found."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Scan failed")


# Create main window
window = tk.Tk()
window.title("Wi-Fi Network Scanner")
window.geometry("850x700")
window.configure(bg="#1e1e2e")


# Heading
heading = tk.Label(
    window,
    text="Wi-Fi Network Scanner",
    font=("Arial", 22, "bold"),
    bg="#1e1e2e",
    fg="white"
)
heading.pack(pady=20)


# Description
description = tk.Label(
    window,
    text="Discover and Monitor Nearby Wi-Fi Networks",
    font=("Arial", 11),
    bg="#1e1e2e",
    fg="lightgray"
)
description.pack()


# Buttons frame
button_frame = tk.Frame(window, bg="#1e1e2e")
button_frame.pack(pady=20)


# Scan button
scan_button = tk.Button(
    button_frame,
    text="SCAN WI-FI",
    font=("Arial", 12, "bold"),
    bg="#5865f2",
    fg="white",
    command=scan_wifi,
    padx=20,
    pady=10
)
scan_button.pack(side=tk.LEFT, padx=10)


# Refresh button
refresh_button = tk.Button(
    button_frame,
    text="REFRESH",
    font=("Arial", 12, "bold"),
    bg="#16865b",
    fg="white",
    command=scan_wifi,
    padx=20,
    pady=10
)
refresh_button.pack(side=tk.LEFT, padx=10)


# Table heading
table_heading = tk.Label(
    window,
    text="NETWORK INFORMATION",
    font=("Arial", 14, "bold"),
    bg="#1e1e2e",
    fg="white"
)
table_heading.pack(pady=10)


# Table style
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#28283d",
    foreground="white",
    fieldbackground="#28283d",
    rowheight=35,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background="#5865f2",
    foreground="white",
    font=("Arial", 10, "bold")
)


# Create Wi-Fi information table
columns = ("SSID", "Signal", "Security", "Band", "Channel")

wifi_table = ttk.Treeview(
    window,
    columns=columns,
    show="headings",
    height=8
)

for column in columns:
    wifi_table.heading(column, text=column)
    wifi_table.column(column, width=145, anchor="center")

wifi_table.pack(padx=20, pady=10, fill="x")


# Total access points label
total_label = tk.Label(
    window,
    text="Total Access Points Found: 0",
    font=("Arial", 12, "bold"),
    bg="#1e1e2e",
    fg="#00d68f"
)
total_label.pack(pady=5)


# Status label
status_label = tk.Label(
    window,
    text="Click SCAN WI-FI to discover networks",
    font=("Arial", 10),
    bg="#1e1e2e",
    fg="lightgreen"
)
status_label.pack(pady=15)


# Start application - MUST BE THE LAST LINE
window.mainloop()
