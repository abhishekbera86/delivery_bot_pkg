"""
GUI for selecting delivery goal locations
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../location_manager'))
from location_manager.location_handler import LocationHandler
import threading


class DeliveryGUI(Node):
    """ROS2 Node with GUI for selecting delivery locations"""
    
    def __init__(self):
        # Initialize ROS2 node
        super().__init__('delivery_gui_node')
        
        # Initialize location handler
        self.location_handler = LocationHandler()
        
        # Publisher for sending goals
        self.goal_pub = self.create_publisher(String, 'delivery_goal', 10)
        
        # Subscriber for navigation status
        self.create_subscription(
            String,
            'navigation_status',
            self.navigation_status_callback,
            10
        )
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Delivery Bot - Location Selector")
        self.root.geometry("600x500")
        
        # Status variables
        self.current_status = tk.StringVar(value="Ready")
        
        # Create GUI elements
        self.create_widgets()
        
        # Load locations
        self.refresh_locations()
        
        self.get_logger().info('Delivery GUI Node started')
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Delivery Bot Control", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Location selection frame
        location_frame = ttk.LabelFrame(main_frame, text="Select Delivery Location", padding="10")
        location_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Location dropdown
        ttk.Label(location_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(location_frame, textvariable=self.location_var, 
                                           width=30, state="readonly")
        self.location_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Go button
        self.go_button = ttk.Button(location_frame, text="Go to Location", 
                                    command=self.send_goal, state=tk.NORMAL)
        self.go_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Location management frame
        manage_frame = ttk.LabelFrame(main_frame, text="Location Management", padding="10")
        manage_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Refresh button
        refresh_button = ttk.Button(manage_frame, text="Refresh Locations", 
                                   command=self.refresh_locations)
        refresh_button.grid(row=0, column=0, pady=5, padx=5)
        
        # Location list
        list_label = ttk.Label(manage_frame, text="Available Locations:")
        list_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(manage_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.location_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.location_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.location_listbox.yview)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        status_label = ttk.Label(status_frame, text="Status:")
        status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.current_status, 
                                     foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Status log
        log_label = ttk.Label(status_frame, text="Status Log:")
        log_label.grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        
        self.status_log = scrolledtext.ScrolledText(status_frame, height=8, width=60)
        self.status_log.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        location_frame.columnconfigure(1, weight=1)
        manage_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
    
    def refresh_locations(self):
        """Refresh location list from JSON file"""
        self.location_handler.load_locations()
        locations = self.location_handler.get_location_names()
        
        # Update combobox
        self.location_combo['values'] = locations
        if locations:
            self.location_var.set(locations[0])
            self.go_button.config(state=tk.NORMAL)
        else:
            self.location_var.set("")
            self.go_button.config(state=tk.DISABLED)
            self.log_status("No locations available. Please tag locations first.")
        
        # Update listbox
        self.location_listbox.delete(0, tk.END)
        for loc in locations:
            location_data = self.location_handler.get_location(loc)
            desc = location_data.get('description', '')
            display_text = f"{loc}"
            if desc:
                display_text += f" - {desc}"
            self.location_listbox.insert(tk.END, display_text)
        
        self.log_status(f"Loaded {len(locations)} locations")
    
    def send_goal(self):
        """Send goal location to navigator"""
        location_name = self.location_var.get()
        
        if not location_name:
            messagebox.showwarning("Warning", "Please select a location")
            return
        
        # Confirm with user
        confirm = messagebox.askyesno("Confirm", f"Navigate to {location_name}?")
        if not confirm:
            return
        
        # Publish goal
        goal_msg = String(data=location_name)
        self.goal_pub.publish(goal_msg)
        
        self.current_status.set(f"Navigating to {location_name}...")
        self.status_label.config(foreground="blue")
        self.log_status(f"Sent navigation goal: {location_name}")
    
    def navigation_status_callback(self, msg: String):
        """Callback for navigation status updates"""
        status = msg.data
        self.log_status(f"Navigation: {status}")
        
        if "SUCCESS" in status:
            self.current_status.set("Navigation Successful")
            self.status_label.config(foreground="green")
        elif "ERROR" in status:
            self.current_status.set("Navigation Failed")
            self.status_label.config(foreground="red")
        
        # Update GUI in main thread
        self.root.after(0, lambda: None)
    
    def log_status(self, message: str):
        """Log status message"""
        self.status_log.insert(tk.END, f"{message}\n")
        self.status_log.see(tk.END)
        self.get_logger().info(message)
    
    def run(self):
        """Run the GUI"""
        # Spin ROS2 node in a separate thread
        def spin_node():
            rclpy.spin(self)
        
        spin_thread = threading.Thread(target=spin_node, daemon=True)
        spin_thread.start()
        
        # Run GUI main loop
        self.root.mainloop()
        
        # Cleanup
        self.destroy_node()
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    app = DeliveryGUI()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()

