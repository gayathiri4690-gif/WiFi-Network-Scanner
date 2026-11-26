
import csv
import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# Store scanned Wi-Fi networks
scanned_networks = []


# Function to scan Wi-Fi networks
def scan_wifi():
    global scanned_networks

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

        # Save the final access point
        save_ap()

        # Store scanned networks for searching
        scanned_networks = networks.copy()

        # Display networks in table
        for network in scanned_networks:
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

        # Calculate network statistics
        signal_values = []

        for network in scanned_networks:
            match = re.search(r"\d+", network["signal"])

            if match:
                signal_values.append(int(match.group()))

        total = len(scanned_networks)

        strongest = max(signal_values) if signal_values else None

        average = (
            round(sum(signal_values) / len(signal_values), 1)
            if signal_values else None
        )

        secure = sum(
            1 for network in scanned_networks
            if network["security"].strip().lower()
            not in ("-", "open", "none", "")
            and "open" not in network["security"].strip().lower()
        )

        # Update statistics dashboard
        total_value.config(text=str(total))

        strongest_value.config(
            text=f"{strongest}%" if strongest is not None else "N/A"
        )

        average_value.config(
            text=f"{average}%" if average is not None else "N/A"
        )

        secure_value.config(text=str(secure))

        status_label.config(
            text=f"Scan completed! {total} access point(s) found."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Scan failed")


# Function to search Wi-Fi networks
def search_wifi():

    search_text = search_entry.get().strip().lower()

    for item in wifi_table.get_children():
        wifi_table.delete(item)

    matches = 0

    for network in scanned_networks:

        if search_text in network["ssid"].lower():

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

            matches += 1

    status_label.config(
        text=f"{matches} matching network(s) found."
    )


# Function to show all scanned networks
def show_all_networks():

    search_entry.delete(0, tk.END)

    for item in wifi_table.get_children():
        wifi_table.delete(item)

    for network in scanned_networks:
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

    status_label.config(
        text=f"Showing all {len(scanned_networks)} scanned access point(s)."
    )


# Function to export scan results
def export_report():

    networks = []

    for item in wifi_table.get_children():
        networks.append(wifi_table.item(item)["values"])

    if not networks:
        messagebox.showwarning(
            "No Data",
            "Please scan Wi-Fi networks before exporting."
        )
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Wi-Fi Report"
    )

    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow(
                ["SSID", "Signal", "Security", "Band", "Channel"]
            )

            writer.writerows(networks)

        messagebox.showinfo(
            "Success",
            "Wi-Fi report exported successfully!"
        )

    except Exception as e:
        messagebox.showerror("Export Error", str(e))


# Create main window
window = tk.Tk()
window.title("Wi-Fi Network Scanner")
window.geometry("1100x900")
window.minsize(990, 500)
window.state("zoomed")
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


# Export button
export_button = tk.Button(
    button_frame,
    text="EXPORT REPORT",
    font=("Arial", 12, "bold"),
    bg="#d97706",
    fg="white",
    command=export_report,
    padx=20,
    pady=10
)
export_button.pack(side=tk.LEFT, padx=10)


# Search section
search_frame = tk.Frame(window, bg="#1e1e2e")
search_frame.pack(pady=10)


search_label = tk.Label(
    search_frame,
    text="Search Wi-Fi:",
    font=("Arial", 11, "bold"),
    bg="#1e1e2e",
    fg="white"
)
search_label.pack(side=tk.LEFT, padx=5)


search_entry = tk.Entry(
    search_frame,
    font=("Arial", 11),
    width=25
)
search_entry.pack(side=tk.LEFT, padx=5)


search_button = tk.Button(
    search_frame,
    text="SEARCH",
    command=search_wifi,
    bg="#5865f2",
    fg="white",
    font=("Arial", 10, "bold")
)
search_button.pack(side=tk.LEFT, padx=5)


show_all_button = tk.Button(
    search_frame,
    text="SHOW ALL",
    command=show_all_networks,
    bg="#16865b",
    fg="white",
    font=("Arial", 10, "bold")
)
show_all_button.pack(side=tk.LEFT, padx=5)


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
    height=7
)

for column in columns:
    wifi_table.heading(column, text=column)
    wifi_table.column(column, width=175, anchor="center")

wifi_table.pack(padx=20, pady=10, fill="x")


# Network Statistics Heading
stats_heading = tk.Label(
    window,
    text="NETWORK STATISTICS",
    font=("Arial", 15, "bold"),
    bg="#1e1e2e",
    fg="white"
)
stats_heading.pack(pady=15)


# Statistics dashboard frame
stats_frame = tk.Frame(window, bg="#1e1e2e")
stats_frame.pack(pady=5)


# Function to create statistics cards
def create_stat_card(parent, title, initial_value, column):

    card = tk.Frame(
        parent,
        bg="#28283d",
        width=200,
        height=100
    )

    card.grid(row=0, column=column, padx=8)
    card.pack_propagate(False)

    title_label = tk.Label(
        card,
        text=title,
        font=("Arial", 10, "bold"),
        bg="#28283d",
        fg="lightgray"
    )
    title_label.pack(pady=(12, 5))

    value_label = tk.Label(
        card,
        text=initial_value,
        font=("Arial", 22, "bold"),
        bg="#28283d",
        fg="#00d68f"
    )
    value_label.pack()

    return value_label


# Four statistics cards
total_value = create_stat_card(
    stats_frame, "Total Access Points", "0", 0
)

strongest_value = create_stat_card(
    stats_frame, "Strongest Signal", "N/A", 1
)

average_value = create_stat_card(
    stats_frame, "Average Signal", "N/A", 2
)

secure_value = create_stat_card(
    stats_frame, "Secured Networks", "0", 3
)


# Status label
status_label = tk.Label(
    window,
    text="Click SCAN WI-FI to discover networks",
    font=("Arial", 10),
    bg="#1e1e2e",
    fg="lightgreen"
)
status_label.pack(pady=20)


# Start application
window.mainloop()
