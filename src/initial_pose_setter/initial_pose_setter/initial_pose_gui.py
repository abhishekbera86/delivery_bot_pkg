"""
GUI tool for setting initial pose for AMCL localization
Modern, professional interface matching location tagging GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import Bool
import sys
import os
import subprocess
import threading
import math


class InitialPoseGUI(Node):
    """ROS2 Node with GUI for setting initial pose"""
    
    # Color scheme - modern and professional (matching location tagging GUI)
    COLORS = {
        'primary': '#2E86AB',      # Blue
        'secondary': '#A23B72',     # Purple
        'success': '#06A77D',       # Green
        'warning': '#F18F01',       # Orange
        'danger': '#C73E1D',        # Red
        'bg_main': '#F5F5F5',       # Light gray background
        'bg_card': '#FFFFFF',       # White card background
        'text_dark': '#2C3E50',     # Dark text
        'text_light': '#7F8C8D',    # Light text
        'accent': '#7209B7',        # Purple accent
    }
    
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
        
        # Publisher to signal that initial pose has been set (for triggering location tagging GUI)
        self.initial_pose_set_pub = self.create_publisher(
            Bool,
            '/initial_pose_set',
            10
        )
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("🤖 Set Robot Initial Pose")
        self.root.geometry("700x650")
        self.root.configure(bg=self.COLORS['bg_main'])
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        self.get_logger().info('Initial Pose GUI Node started')
    
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.COLORS['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10,
                       font=('Arial', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', '#1E6A8B'), ('pressed', '#0D4A63')])
        
        style.configure('Success.TButton',
                       background=self.COLORS['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10,
                       font=('Arial', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#058A65'), ('pressed', '#03664A')])
        
        style.configure('Warning.TButton',
                       background=self.COLORS['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=8,
                       font=('Arial', 9))
    
    def load_locations(self):
        """Load locations from JSON file if it exists"""
        import json
        locations_file = os.environ.get('HOME') + '/delivery_bot_pkg/data/locations.json'
        if os.path.exists(locations_file):
            try:
                with open(locations_file, 'r') as f:
                    self.locations = json.load(f)
                self.get_logger().info(f"Loaded {len(self.locations)} locations")
            except Exception as e:
                self.get_logger().warn(f"Could not load locations: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.COLORS['bg_main'], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.COLORS['primary'], pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🤖 Set Robot Initial Pose",
            font=('Arial', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Set robot's initial position for localization",
            font=('Arial', 10),
            bg=self.COLORS['primary'],
            fg='#E8F4F8'
        )
        subtitle_label.pack()
        
        # Location selection card
        location_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        location_card.pack(fill=tk.X, pady=(0, 15))
        
        location_header = tk.Label(
            location_card,
            text="📍 Use Tagged Location",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        location_header.pack(fill=tk.X)
        
        location_content = tk.Frame(location_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        location_content.pack(fill=tk.X)
        
        if self.locations:
            name_frame = tk.Frame(location_content, bg=self.COLORS['bg_card'])
            name_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                name_frame,
                text="Select Location:",
                font=('Arial', 10, 'bold'),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_dark'],
                anchor='w'
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            self.location_var = tk.StringVar()
            location_combo = ttk.Combobox(
                name_frame,
                textvariable=self.location_var,
                values=list(self.locations.keys()),
                state="readonly",
                width=30,
                font=('Arial', 10)
            )
            location_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            use_location_btn = ttk.Button(
                location_content,
                text="✅ Use This Location",
                style='Success.TButton',
                command=self.use_location_pose
            )
            use_location_btn.pack(fill=tk.X)
        else:
            no_loc_label = tk.Label(
                location_content,
                text="No tagged locations available.\nUse manual entry or RViz2 below.",
                font=('Arial', 10),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_light'],
                justify=tk.CENTER
            )
            no_loc_label.pack(pady=10)
        
        # Manual entry card
        manual_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        manual_card.pack(fill=tk.X, pady=(0, 15))
        
        manual_header = tk.Label(
            manual_card,
            text="⌨️ Manual Entry",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        manual_header.pack(fill=tk.X)
        
        manual_content = tk.Frame(manual_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        manual_content.pack(fill=tk.X)
        
        # Position inputs
        input_frame = tk.Frame(manual_content, bg=self.COLORS['bg_card'])
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="X (meters):",
            font=('Arial', 10),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.x_var = tk.StringVar(value="0.0")
        x_entry = tk.Entry(
            input_frame,
            textvariable=self.x_var,
            width=20,
            font=('Arial', 10),
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#CCCCCC'
        )
        x_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        tk.Label(
            input_frame,
            text="Y (meters):",
            font=('Arial', 10),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.y_var = tk.StringVar(value="0.0")
        y_entry = tk.Entry(
            input_frame,
            textvariable=self.y_var,
            width=20,
            font=('Arial', 10),
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#CCCCCC'
        )
        y_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        tk.Label(
            input_frame,
            text="Yaw (degrees, 0=north):",
            font=('Arial', 10),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.yaw_var = tk.StringVar(value="0.0")
        yaw_entry = tk.Entry(
            input_frame,
            textvariable=self.yaw_var,
            width=20,
            font=('Arial', 10),
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#CCCCCC'
        )
        yaw_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        use_manual_btn = ttk.Button(
            manual_content,
            text="✅ Set Initial Pose (Manual)",
            style='Success.TButton',
            command=self.use_manual_pose
        )
        use_manual_btn.pack(fill=tk.X)
        
        # RViz2 card
        rviz_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        rviz_card.pack(fill=tk.X, pady=(0, 15))
        
        rviz_header = tk.Label(
            rviz_card,
            text="👁️ Visual Method",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        rviz_header.pack(fill=tk.X)
        
        rviz_content = tk.Frame(rviz_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        rviz_content.pack(fill=tk.X)
        
        rviz_btn = ttk.Button(
            rviz_content,
            text="🗺️ Open RViz2 to Set Pose Visually",
            style='Primary.TButton',
            command=self.open_rviz2
        )
        rviz_btn.pack(fill=tk.X, pady=(0, 10))
        
        rviz_info = tk.Label(
            rviz_content,
            text="Opens RViz2 with map. Use '2D Pose Estimate' tool to set pose.\nAfter setting pose in RViz2, click 'OK' below.",
            font=('Arial', 9),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            justify=tk.CENTER
        )
        rviz_info.pack(pady=(0, 10))
        
        rviz_ok_btn = ttk.Button(
            rviz_content,
            text="✅ OK - Pose Set in RViz2",
            style='Success.TButton',
            command=self.rviz_pose_set
        )
        rviz_ok_btn.pack(fill=tk.X)
        
        # Status bar
        status_frame = tk.Frame(main_container, bg=self.COLORS['text_dark'], height=30)
        status_frame.pack(fill=tk.X, pady=(0, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to set initial pose",
            font=('Arial', 9),
            bg=self.COLORS['text_dark'],
            fg='white',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
    
    def use_location_pose(self):
        """Use pose from selected location"""
        location_name = self.location_var.get()
        if not location_name:
            messagebox.showwarning("Warning", "Please select a location")
            self.status_label.config(text="⚠️ Please select a location", fg=self.COLORS['warning'])
            return
        
        if location_name not in self.locations:
            messagebox.showerror("Error", f"Location '{location_name}' not found")
            self.status_label.config(text="❌ Location not found", fg=self.COLORS['danger'])
            return
        
        loc = self.locations[location_name]
        x = loc['position']['x']
        y = loc['position']['y']
        ox = loc['orientation']['x']
        oy = loc['orientation']['y']
        oz = loc['orientation']['z']
        ow = loc['orientation']['w']
        
        self.set_initial_pose(x, y, ox, oy, oz, ow, f"Location: {location_name}")
    
    def use_manual_pose(self):
        """Use manually entered pose"""
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            yaw_deg = float(self.yaw_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            self.status_label.config(text="❌ Invalid input", fg=self.COLORS['danger'])
            return
        
        # Convert yaw (degrees) to quaternion
        yaw_rad = math.radians(yaw_deg)
        ow = math.cos(yaw_rad / 2)
        oz = math.sin(yaw_rad / 2)
        ox = 0.0
        oy = 0.0
        
        self.set_initial_pose(x, y, ox, oy, oz, ow, "Manual entry")
    
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
        
        # Signal that initial pose has been set (for triggering location tagging GUI)
        signal_msg = Bool()
        signal_msg.data = True
        self.initial_pose_set_pub.publish(signal_msg)
        
        self.status_label.config(
            text=f"✅ Initial pose set at ({x:.2f}, {y:.2f}) - {source}",
            fg=self.COLORS['success']
        )
        self.get_logger().info(f"Initial pose published: ({x}, {y})")
        self.get_logger().info("Signal sent: Initial pose set - Location tagging GUI can now start")
        
        # Show success message and close after delay
        messagebox.showinfo("Success", f"Initial pose set at ({x:.2f}, {y:.2f})\n\nLocation Tagging GUI will open automatically.")
        
        # Close the GUI after a short delay
        self.root.after(500, self.close_gui)
    
    def close_gui(self):
        """Close the GUI window"""
        self.root.destroy()
        self.get_logger().info("Initial Pose GUI closed")
    
    def open_rviz2(self):
        """Open RViz2 in a subprocess with better configuration"""
        def check_map_topic():
            """Check if map topic is available"""
            try:
                result = subprocess.run(
                    ['ros2', 'topic', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if '/map' in result.stdout:
                    return True
                return False
            except:
                return False
        
        def run_rviz():
            try:
                # Wait a moment for map_server to be ready
                import time
                time.sleep(1)
                
                # Try to open RViz2
                subprocess.run(['rviz2'], check=True)
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"❌ Error opening RViz2: {e}", 
                    fg=self.COLORS['danger']
                ))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Could not open RViz2: {e}"))
        
        # Check if map topic is available
        if not check_map_topic():
            warning_msg = (
                "⚠️ Map topic not detected yet!\n\n"
                "The /map topic may not be available yet.\n"
                "Please ensure:\n"
                "1. Localization launch is running\n"
                "2. Map server has started\n"
                "3. Wait a few seconds and try again\n\n"
                "RViz2 will still open, but you may need to:\n"
                "- Wait for map to appear\n"
                "- Manually add Map display (topic: /map)\n"
                "- Set Fixed Frame to 'map'"
            )
            messagebox.showwarning("Map Topic Check", warning_msg)
        
        rviz_thread = threading.Thread(target=run_rviz, daemon=True)
        rviz_thread.start()
        
        # Detailed instructions
        info_msg = (
            "RViz2 Setup Instructions:\n\n"
            "1. WAIT for map to load (may take 5-10 seconds)\n\n"
            "2. If map doesn't appear automatically:\n"
            "   - Click 'Add' button (bottom left)\n"
            "   - Select 'Map' from list\n"
            "   - In Map properties, set Topic to: /map\n"
            "   - Click 'OK'\n\n"
            "3. Set Fixed Frame:\n"
            "   - At top of RViz2, find 'Fixed Frame'\n"
            "   - Change from 'base_link' to 'map'\n\n"
            "4. Set Initial Pose:\n"
            "   - Click '2D Pose Estimate' tool (toolbar, or press P)\n"
            "   - Click on map where robot is located\n"
            "   - Drag to set orientation (which way robot faces)\n\n"
            "5. After setting pose, return to GUI and click:\n"
            "   '✅ OK - Pose Set in RViz2'\n\n"
            "Troubleshooting:\n"
            "- If map is blank: Check /map topic exists: ros2 topic echo /map\n"
            "- If map_server error: Check map file path in launch command"
        )
        messagebox.showinfo("RViz2 Setup Guide", info_msg)
        self.status_label.config(
            text="🗺️ RViz2 opened - Follow setup instructions, then use 2D Pose Estimate tool", 
            fg=self.COLORS['primary']
        )
    
    def rviz_pose_set(self):
        """Handle when user sets pose via RViz2"""
        # Signal that initial pose has been set (for triggering location tagging GUI)
        signal_msg = Bool()
        signal_msg.data = True
        self.initial_pose_set_pub.publish(signal_msg)
        
        self.status_label.config(
            text="✅ Initial pose set via RViz2 - Location Tagging GUI will open",
            fg=self.COLORS['success']
        )
        self.get_logger().info("Signal sent: Initial pose set via RViz2 - Location tagging GUI can now start")
        
        # Show success message and close after delay
        messagebox.showinfo("Success", "Initial pose set via RViz2.\n\nLocation Tagging GUI will open automatically.")
        
        # Close the GUI after a short delay
        self.root.after(500, self.close_gui)
    
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
