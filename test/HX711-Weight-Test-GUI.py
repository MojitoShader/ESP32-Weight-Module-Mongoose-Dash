#!/usr/bin/env python3
"""
HX711 Weight Sensor Test GUI
Displays live weight readings from the ESP32 Weight Module via REST API
Updates every 100ms
"""

import tkinter as tk
from tkinter import ttk
import requests
import threading
from collections import deque
from datetime import datetime

class WeightTestGUI:
    def __init__(self, root, base_url="http://192.168.1.221", update_interval_ms=100):
        self.root = root
        self.base_url = base_url
        self.update_interval_ms = update_interval_ms
        self.running = True
        
        # Data storage
        self.readings = deque(maxlen=200)  # Keep last 200 readings
        self.last_error = None
        self.error_count = 0
        self.success_count = 0
        
        # Setup UI
        self.setup_ui()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Schedule first update
        self.scheduled_update()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Create the GUI layout"""
        self.root.title("HX711 Weight Sensor Test")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Top Frame: Connection Info ---
        top_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text="Target URL:").pack(side="left")
        self.url_label = ttk.Label(top_frame, text=self.base_url, foreground="blue")
        self.url_label.pack(side="left", padx=10)
        
        ttk.Label(top_frame, text="Update Interval:").pack(side="left", padx=(20, 0))
        self.interval_label = ttk.Label(top_frame, text=f"{self.update_interval_ms}ms", foreground="blue")
        self.interval_label.pack(side="left", padx=10)
        
        # --- Middle Frame: Live Display ---
        display_frame = ttk.LabelFrame(self.root, text="Live Weight Reading", padding=20)
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Large weight display
        self.weight_label = tk.Label(display_frame, text="-- g", font=("Arial", 96, "bold"), 
                                     foreground="#3498db")
        self.weight_label.pack(pady=20)
        
        # Weight unit
        self.unit_label = tk.Label(display_frame, text="grams (g)", font=("Arial", 14))
        self.unit_label.pack()
        
        # Time info
        self.time_label = tk.Label(display_frame, text="Last update: --", font=("Arial", 10))
        self.time_label.pack(pady=10)
        
        # --- Bottom Frame: Statistics ---
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Create grid for stats
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")
        
        # Min/Max/Avg readings
        ttk.Label(stats_grid, text="Min:").grid(row=0, column=0, sticky="w", padx=5)
        self.min_label = ttk.Label(stats_grid, text="--", foreground="blue")
        self.min_label.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Max:").grid(row=0, column=2, sticky="w", padx=5)
        self.max_label = ttk.Label(stats_grid, text="--", foreground="red")
        self.max_label.grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Avg:").grid(row=0, column=4, sticky="w", padx=5)
        self.avg_label = ttk.Label(stats_grid, text="--", foreground="green")
        self.avg_label.grid(row=0, column=5, sticky="w", padx=5)
        
        # Std Dev
        ttk.Label(stats_grid, text="StdDev:").grid(row=0, column=6, sticky="w", padx=5)
        self.stddev_label = ttk.Label(stats_grid, text="--", foreground="purple")
        self.stddev_label.grid(row=0, column=7, sticky="w", padx=5)
        
        # Success/Error counters
        ttk.Label(stats_grid, text="Success:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.success_label = ttk.Label(stats_grid, text="0", foreground="green")
        self.success_label.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Errors:").grid(row=1, column=2, sticky="w", padx=5)
        self.error_count_label = ttk.Label(stats_grid, text="0", foreground="red")
        self.error_count_label.grid(row=1, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Readings:").grid(row=1, column=4, sticky="w", padx=5)
        self.reading_count_label = ttk.Label(stats_grid, text="0", foreground="darkblue")
        self.reading_count_label.grid(row=1, column=5, sticky="w", padx=5)
        
        # Error message
        ttk.Label(stats_grid, text="Last Error:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.error_label = ttk.Label(stats_grid, text="None", foreground="darkgreen")
        self.error_label.grid(row=2, column=1, columnspan=7, sticky="w", padx=5)
        
        # --- Control Frame ---
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Clear Stats", command=self.clear_stats).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Tare", command=self.send_tare).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Exit", command=self.on_closing).pack(side="left", padx=5)
        
        self.paused = False
    
    def fetch_sensor_data(self):
        """Fetch sensor data from API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/sensor_read",
                timeout=2
            )
            response.raise_for_status()
            data = response.json()
            
            weight = data.get("weight", -1)
            if weight >= 0:
                self.readings.append(weight)
                self.success_count += 1
                self.last_error = None
                return weight
            else:
                self.error_count += 1
                self.last_error = "Invalid weight reading (weight < 0)"
                return None
                
        except requests.exceptions.Timeout:
            self.error_count += 1
            self.last_error = "Connection timeout"
            return None
        except requests.exceptions.ConnectionError:
            self.error_count += 1
            self.last_error = "Connection refused - check device IP"
            return None
        except requests.exceptions.HTTPError as e:
            self.error_count += 1
            self.last_error = f"HTTP Error: {e.response.status_code}"
            return None
        except Exception as e:
            self.error_count += 1
            self.last_error = f"Error: {str(e)}"
            return None
    
    def send_tare(self):
        """Send tare command to device"""
        try:
            response = requests.put(
                f"{self.base_url}/api/sensor_read",
                json={"tare": True},
                timeout=2
            )
            response.raise_for_status()
            self.last_error = "Tare completed!"
        except Exception as e:
            self.last_error = f"Tare failed: {str(e)}"
    
    def update_loop(self):
        """Background thread for fetching data"""
        import time
        while self.running:
            if not self.paused:
                self.fetch_sensor_data()
            time.sleep(self.update_interval_ms / 1000.0)
    
    def scheduled_update(self):
        """Update UI elements from main thread"""
        if self.running:
            self.update_display()
            self.root.after(100, self.scheduled_update)
    
    def update_display(self):
        """Update all UI elements with current data"""
        if self.readings:
            latest = self.readings[-1]
            self.weight_label.config(text=f"{latest} g")
            
            # Update colors based on weight
            if latest == 0:
                self.weight_label.config(foreground="#95a5a6")  # Gray - empty
            elif latest < 100:
                self.weight_label.config(foreground="#f39c12")  # Orange - light
            elif latest < 300:
                self.weight_label.config(foreground="#3498db")  # Blue - medium
            else:
                self.weight_label.config(foreground="#e74c3c")  # Red - heavy
        else:
            self.weight_label.config(text="-- g", foreground="#95a5a6")
        
        # Update time
        self.time_label.config(text=f"Last update: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
        # Update statistics
        if self.readings:
            readings_list = list(self.readings)
            self.min_label.config(text=f"{min(readings_list)} g")
            self.max_label.config(text=f"{max(readings_list)} g")
            avg = sum(readings_list) / len(readings_list)
            self.avg_label.config(text=f"{avg:.1f} g")
            
            # Calculate standard deviation
            if len(readings_list) > 1:
                variance = sum((x - avg) ** 2 for x in readings_list) / len(readings_list)
                stddev = variance ** 0.5
                self.stddev_label.config(text=f"{stddev:.1f} g")
            else:
                self.stddev_label.config(text="--")
        else:
            self.min_label.config(text="--")
            self.max_label.config(text="--")
            self.avg_label.config(text="--")
            self.stddev_label.config(text="--")
        
        # Update counters
        self.success_label.config(text=str(self.success_count))
        self.error_count_label.config(text=str(self.error_count))
        self.reading_count_label.config(text=str(len(self.readings)))
        
        # Update error message
        if self.last_error:
            if "Tare" in self.last_error:
                self.error_label.config(text=self.last_error, foreground="darkgreen")
            else:
                self.error_label.config(text=self.last_error, foreground="red")
        else:
            self.error_label.config(text="None", foreground="darkgreen")
    
    def toggle_pause(self):
        """Pause/Resume data fetching"""
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
    
    def clear_stats(self):
        """Clear all statistics"""
        self.readings.clear()
        self.success_count = 0
        self.error_count = 0
        self.last_error = None
        self.update_display()
    
    def on_closing(self):
        """Handle window close event"""
        self.running = False
        self.root.destroy()


def main():
    # Configuration
    DEVICE_IP = "192.168.1.233"  # Change this to your ESP32's IP
    UPDATE_INTERVAL_MS = 100      # Update every 100ms
    
    root = tk.Tk()
    app = WeightTestGUI(root, base_url=f"http://{DEVICE_IP}", update_interval_ms=UPDATE_INTERVAL_MS)
    root.mainloop()


if __name__ == "__main__":
    main()
