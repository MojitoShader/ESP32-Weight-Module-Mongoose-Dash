#!/usr/bin/env python3
"""
HC-SR04 Ultrasonic Sensor Test GUI
Displays live distance readings from the ESP32 Weight Module via REST API
"""

import tkinter as tk
from tkinter import ttk
import requests
import threading
from collections import deque
from datetime import datetime

class SensorTestGUI:
    def __init__(self, root, base_url="http://192.168.1.221", update_interval_ms=100):
        self.root = root
        self.base_url = base_url
        self.update_interval_ms = update_interval_ms
        self.running = True
        
        # Data storage
        self.readings = deque(maxlen=100)  # Keep last 100 readings
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
        self.root.title("HC-SR04 Ultrasonic Sensor Test")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Top Frame: Connection Info ---
        top_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text=f"Target URL:").pack(side="left")
        self.url_label = ttk.Label(top_frame, text=self.base_url, foreground="blue")
        self.url_label.pack(side="left", padx=10)
        
        # --- Middle Frame: Live Display ---
        display_frame = ttk.LabelFrame(self.root, text="Live Distance Reading", padding=20)
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Large distance display
        self.distance_label = tk.Label(display_frame, text="-- mm", font=("Arial", 72, "bold"), 
                                       foreground="#2ecc71")
        self.distance_label.pack(pady=20)
        
        # Distance unit
        self.unit_label = tk.Label(display_frame, text="millimeters (mm)", font=("Arial", 12))
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
        
        # Success/Error counters
        ttk.Label(stats_grid, text="Success:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.success_label = ttk.Label(stats_grid, text="0", foreground="green")
        self.success_label.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Errors:").grid(row=1, column=2, sticky="w", padx=5)
        self.error_count_label = ttk.Label(stats_grid, text="0", foreground="red")
        self.error_count_label.grid(row=1, column=3, sticky="w", padx=5)
        
        # Error message
        ttk.Label(stats_grid, text="Last Error:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.error_label = ttk.Label(stats_grid, text="None", foreground="darkgreen")
        self.error_label.grid(row=2, column=1, columnspan=5, sticky="w", padx=5)
        
        # --- Control Frame ---
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Clear Stats", command=self.clear_stats).pack(side="left", padx=5)
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
            
            distance = data.get("distance", -1)
            if distance >= 0:
                self.readings.append(distance)
                self.success_count += 1
                self.last_error = None
                return distance
            else:
                self.error_count += 1
                self.last_error = "Invalid sensor reading (distance < 0)"
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
            self.distance_label.config(text=f"{latest} mm")
            
            # Update colors based on distance
            if latest < 100:
                self.distance_label.config(foreground="#e74c3c")  # Red - close
            elif latest < 300:
                self.distance_label.config(foreground="#f39c12")  # Orange - medium
            else:
                self.distance_label.config(foreground="#2ecc71")  # Green - far
        else:
            self.distance_label.config(text="-- mm", foreground="#95a5a6")
        
        # Update time
        self.time_label.config(text=f"Last update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Update statistics
        if self.readings:
            readings_list = list(self.readings)
            self.min_label.config(text=f"{min(readings_list)} mm")
            self.max_label.config(text=f"{max(readings_list)} mm")
            self.avg_label.config(text=f"{sum(readings_list) / len(readings_list):.1f} mm")
        else:
            self.min_label.config(text="--")
            self.max_label.config(text="--")
            self.avg_label.config(text="--")
        
        # Update counters
        self.success_label.config(text=str(self.success_count))
        self.error_count_label.config(text=str(self.error_count))
        
        # Update error message
        if self.last_error:
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
    UPDATE_INTERVAL_MS = 1      # Update every 100ms
    
    root = tk.Tk()
    app = SensorTestGUI(root, base_url=f"http://{DEVICE_IP}", update_interval_ms=UPDATE_INTERVAL_MS)
    root.mainloop()


if __name__ == "__main__":
    main()
