"""
GUI tool for setting initial pose for AMCL localization
Shows available locations and allows easy selection or manual entry
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
import sys
import os
import subprocess
import threading


class InitialPoseGUI(Node):
    """ROS2 Node with GUI for setting initial pose"""
    
    def __init__(self):
        super().__init__('initial_pose_gui_node')
        
        # Load locations if available
        self.locations = {}
        self.load_locations()
        
        # Publisher for initial pose
        self.initial_pose_pub = self.create_publisher(
            PoseWithCovarianceStamped, 
            '/initialpose', 
            10
        )
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Set Robot Initial Pose")
        self.root.geometry("600x600")
        
        # Create GUI elements
        self.create_widgets()
        
        self.get_logger().info('Initial Pose GUI Node started')
    
    def load_locations(self):
        """Load locations from JSON file if it exists"""
        import json
        locations_file = os.path.expanduser("~/delivery_bot_pkg/data/locations.json")
        if os.path.exists(locations_file):
            try:
                with open(locations_file, 'r') as f:
                    self.locations = json.load(f)
                self.get_logger().info(f"Loaded {len(self.locations)} locations")
            except Exception as e:
                self.get_logger().warn(f"Could not load locations: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Set Robot Initial Pose", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Instructions
        info_text = (
            "Select a known location or enter position manually.\n"
            "The robot's initial pose will be sent to AMCL for localization."
        )
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.CENTER)
        info_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Location selection frame
        location_frame = ttk.LabelFrame(main_frame, text="Use Tagged Location", padding="10")
        location_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        if self.locations:
            ttk.Label(location_frame, text="Select Location:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.location_var = tk.StringVar()
            self.location_combo = ttk.Combobox(
                location_frame, 
                textvariable=self.location_var,
                values=list(self.locations.keys()),
                state="readonly",
                width=30
            )
            self.location_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            
            use_location_btn = ttk.Button(
                location_frame,
                text="Use This Location",
                command=self.use_location_pose
            )
            use_location_btn.grid(row=1, column=0, columnspan=2, pady=10)
        else:
            no_loc_label = ttk.Label(
                location_frame, 
                text="No tagged locations available.\nUse manual entry below."
            )
            no_loc_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Manual entry frame
        manual_frame = ttk.LabelFrame(main_frame, text="Manual Entry", padding="10")
        manual_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Position inputs
        ttk.Label(manual_frame, text="X (meters):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.x_var = tk.StringVar(value="0.0")
        x_entry = ttk.Entry(manual_frame, textvariable=self.x_var, width=15)
        x_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(manual_frame, text="Y (meters):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.y_var = tk.StringVar(value="0.0")
        y_entry = ttk.Entry(manual_frame, textvariable=self.y_var, width=15)
        y_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(manual_frame, text="Yaw (degrees, 0=north):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.yaw_var = tk.StringVar(value="0.0")
        yaw_entry = ttk.Entry(manual_frame, textvariable=self.yaw_var, width=15)
        yaw_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        use_manual_btn = ttk.Button(
            manual_frame,
            text="Set Initial Pose (Manual)",
            command=self.use_manual_pose
        )
        use_manual_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # RViz2 button
        rviz_frame = ttk.LabelFrame(main_frame, text="Visual Method", padding="10")
        rviz_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        rviz_btn = ttk.Button(
            rviz_frame,
            text="Open RViz2 to Set Pose Visually",
            command=self.open_rviz2
        )
        rviz_btn.grid(row=0, column=0, pady=5)
        
        rviz_info = ttk.Label(
            rviz_frame,
            text="Opens RViz2 with map. Use '2D Pose Estimate' tool to set pose.",
            font=("Arial", 9)
        )
        rviz_info.grid(row=1, column=0, pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=60)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        location_frame.columnconfigure(1, weight=1)
        manual_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
    
    def use_location_pose(self):
        """Use pose from selected location"""
        location_name = self.location_var.get()
        if not location_name:
            messagebox.showwarning("Warning", "Please select a location")
            return
        
        if location_name not in self.locations:
            messagebox.showerror("Error", f"Location '{location_name}' not found")
            return
        
        loc = self.locations[location_name]
        x = loc['position']['x']
        y = loc['position']['y']
        ox = loc['orientation']['x']
        oy = loc['orientation']['y']
        oz = loc['orientation']['z']
        ow = loc['orientation']['w']
        
        self.set_initial_pose(x, y, ox, oy, oz, ow, f"Location: {location_name}")
        messagebox.showinfo("Success", f"Initial pose set at ({x:.2f}, {y:.2f}) using location: {location_name}")
    
    def use_manual_pose(self):
        """Use manually entered pose"""
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            yaw_deg = float(self.yaw_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        
        # Convert yaw (degrees) to quaternion
        import math
        yaw_rad = math.radians(yaw_deg)
        ow = math.cos(yaw_rad / 2)
        oz = math.sin(yaw_rad / 2)
        ox = 0.0
        oy = 0.0
        
        self.set_initial_pose(x, y, ox, oy, oz, ow, "Manual entry")
        messagebox.showinfo("Success", f"Initial pose set at ({x:.2f}, {y:.2f})")
    
    def set_initial_pose(self, x, y, ox, oy, oz, ow, source=""):
        """Publish initial pose message"""
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x = float(x)
        msg.pose.pose.position.y = float(y)
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.x = float(ox)
        msg.pose.pose.orientation.y = float(oy)
        msg.pose.pose.orientation.z = float(oz)
        msg.pose.pose.orientation.w = float(ow)
        
        # Covariance matrix
        msg.pose.covariance = [
            0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942
        ]
        
        self.initial_pose_pub.publish(msg)
        
        status_msg = f"Initial pose set at ({x:.2f}, {y:.2f}) - {source}\n"
        self.log_status(status_msg)
        self.get_logger().info(f"Initial pose published: ({x}, {y})")
    
    def open_rviz2(self):
        """Open RViz2 in a subprocess"""
        def run_rviz():
            try:
                subprocess.run(['rviz2'], check=True)
            except Exception as e:
                self.log_status(f"Error opening RViz2: {e}\n")
                messagebox.showerror("Error", f"Could not open RViz2: {e}")
        
        rviz_thread = threading.Thread(target=run_rviz, daemon=True)
        rviz_thread.start()
        
        info_msg = (
            "RViz2 opened. To set initial pose:\n"
            "1. Add 'Map' display, topic: /map\n"
            "2. Set Fixed Frame to 'map'\n"
            "3. Click '2D Pose Estimate' tool (or press P)\n"
            "4. Click on map where robot is located\n"
            "5. Drag to set orientation\n"
        )
        messagebox.showinfo("RViz2 Instructions", info_msg)
        self.log_status("RViz2 opened - use 2D Pose Estimate tool\n")
    
    def log_status(self, message):
        """Log status message"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
    
    def run(self):
        """Run the GUI"""
        def spin_node():
            rclpy.spin(self)
        
        spin_thread = threading.Thread(target=spin_node, daemon=True)
        spin_thread.start()
        
        self.root.mainloop()
        
        # Clean shutdown
        if rclpy.ok():
            self.destroy_node()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    app = InitialPoseGUI()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

