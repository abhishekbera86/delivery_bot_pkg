"""
Unified Delivery Bot GUI
Manages map selection, localization, and location selection in one interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseWithCovarianceStamped
import sys
import os
import subprocess
import threading
import time
import glob
sys.path.append(os.path.join(os.path.dirname(__file__), '../../location_manager'))
from location_manager.location_handler import LocationHandler


class DeliveryBotMainGUI(Node):
    """ROS2 Node with unified GUI for delivery bot setup"""
    
    # Color scheme - modern and professional (matching mapping GUI)
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
        super().__init__('delivery_bot_main_gui_node')
        
        # State tracking
        self.selected_map = None
        self.map_path = None
        self.locations_file = None
        self.location_handler = None
        self.initial_pose_set = False
        self.localization_running = False
        self.nav2_running = False
        self.navigator_running = False
        
        # Process tracking
        self.localization_process = None
        self.nav2_process = None
        self.navigator_process = None
        self.initial_pose_gui_process = None
        
        # Publisher for initial pose
        self.initial_pose_pub = self.create_publisher(
            PoseWithCovarianceStamped, 
            '/initialpose', 
            10
        )
        
        # Publisher to signal initial pose set
        self.initial_pose_set_pub = self.create_publisher(
            Bool,
            '/initial_pose_set',
            10
        )
        
        # Publisher for delivery goals
        self.goal_pub = self.create_publisher(String, '/delivery_goal', 10)
        
        # Subscriber for navigation status
        self.nav_status_sub = self.create_subscription(
            String,
            '/navigation_status',
            self.nav_status_callback,
            10
        )
        
        # Subscriber for initial pose set signal
        self.initial_pose_set_sub = self.create_subscription(
            Bool,
            '/initial_pose_set',
            self.initial_pose_set_callback,
            10
        )
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("🤖 Delivery Bot - Main Control")
        self.root.geometry("900x750")
        self.root.configure(bg=self.COLORS['bg_main'])
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Status variables
        self.current_status = "Ready"
        self.navigation_status = ""
        
        # Load available maps
        self.refresh_maps()
        
        self.get_logger().info('Delivery Bot Main GUI Node started')
    
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
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
                       padding=8,
                       font=('Arial', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#058A65'), ('pressed', '#03664A')])
        
        style.configure('Danger.TButton',
                       background=self.COLORS['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=8,
                       font=('Arial', 9))
        style.map('Danger.TButton',
                 background=[('active', '#A63217'), ('pressed', '#8B2A14')])
        
        style.configure('Warning.TButton',
                       background=self.COLORS['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=8,
                       font=('Arial', 9))
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.COLORS['bg_main'], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.COLORS['primary'], pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🤖 Delivery Bot - Main Control",
            font=('Arial', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Select map, set initial pose, and navigate to locations",
            font=('Arial', 10),
            bg=self.COLORS['primary'],
            fg='#E8F4F8'
        )
        subtitle_label.pack()
        
        # Map Selection Card
        map_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        map_card.pack(fill=tk.X, pady=(0, 15))
        
        map_header = tk.Label(
            map_card,
            text="🗺️ Map Selection",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        map_header.pack(fill=tk.X)
        
        map_content = tk.Frame(map_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        map_content.pack(fill=tk.X)
        
        map_frame = tk.Frame(map_content, bg=self.COLORS['bg_card'])
        map_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            map_frame,
            text="Select Map:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.map_var = tk.StringVar()
        self.map_combo = ttk.Combobox(
            map_frame,
            textvariable=self.map_var,
            state="readonly",
            width=40,
            font=('Arial', 11)
        )
        self.map_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.map_combo.bind('<<ComboboxSelected>>', self.on_map_selected)
        
        refresh_maps_btn = ttk.Button(
            map_frame,
            text="🔄 Refresh",
            style='Primary.TButton',
            command=self.refresh_maps
        )
        refresh_maps_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.load_map_btn = ttk.Button(
            map_content,
            text="📂 Load Map and Start Localization",
            style='Success.TButton',
            command=self.load_map,
            state=tk.DISABLED
        )
        self.load_map_btn.pack(fill=tk.X)
        
        self.map_status_label = tk.Label(
            map_content,
            text="",
            font=('Arial', 9),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            anchor='w'
        )
        self.map_status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Initial Pose Card (shown when map is loaded)
        self.initial_pose_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        
        initial_pose_header = tk.Label(
            self.initial_pose_card,
            text="📍 Set Initial Pose",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        initial_pose_header.pack(fill=tk.X)
        
        initial_pose_content = tk.Frame(self.initial_pose_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        initial_pose_content.pack(fill=tk.X)
        
        # Location selection for initial pose
        location_frame = tk.Frame(initial_pose_content, bg=self.COLORS['bg_card'])
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            location_frame,
            text="Use Tagged Location:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.initial_pose_location_var = tk.StringVar()
        self.initial_pose_location_combo = ttk.Combobox(
            location_frame,
            textvariable=self.initial_pose_location_var,
            state="readonly",
            width=30,
            font=('Arial', 11)
        )
        self.initial_pose_location_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        use_location_btn = ttk.Button(
            location_frame,
            text="✅ Use This Location",
            style='Success.TButton',
            command=self.use_location_for_initial_pose
        )
        use_location_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Manual entry
        manual_frame = tk.Frame(initial_pose_content, bg=self.COLORS['bg_card'])
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        manual_label = tk.Label(
            manual_frame,
            text="Manual Entry:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=20
        )
        manual_label.pack(side=tk.LEFT, padx=(0, 10))
        
        entry_frame = tk.Frame(manual_frame, bg=self.COLORS['bg_card'])
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(entry_frame, text="X:", bg=self.COLORS['bg_card'], font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.x_var = tk.StringVar(value="0.0")
        tk.Entry(entry_frame, textvariable=self.x_var, width=8, font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(entry_frame, text="Y:", bg=self.COLORS['bg_card'], font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.y_var = tk.StringVar(value="0.0")
        tk.Entry(entry_frame, textvariable=self.y_var, width=8, font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(entry_frame, text="Yaw:", bg=self.COLORS['bg_card'], font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.yaw_var = tk.StringVar(value="0.0")
        tk.Entry(entry_frame, textvariable=self.yaw_var, width=8, font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        set_manual_btn = ttk.Button(
            manual_frame,
            text="✅ Set Manual",
            style='Primary.TButton',
            command=self.set_initial_pose_manual
        )
        set_manual_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.initial_pose_status_label = tk.Label(
            initial_pose_content,
            text="",
            font=('Arial', 9),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            anchor='w'
        )
        self.initial_pose_status_label.pack(fill=tk.X)
        
        # Location Selection Card (shown after initial pose is set)
        self.location_selection_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        
        location_header = tk.Label(
            self.location_selection_card,
            text="🎯 Select Delivery Location",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        location_header.pack(fill=tk.X)
        
        location_content = tk.Frame(self.location_selection_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        location_content.pack(fill=tk.X)
        
        location_frame = tk.Frame(location_content, bg=self.COLORS['bg_card'])
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            location_frame,
            text="Location:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(
            location_frame,
            textvariable=self.location_var,
            state="readonly",
            width=30,
            font=('Arial', 11)
        )
        self.location_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        refresh_locations_btn = ttk.Button(
            location_frame,
            text="🔄 Refresh",
            style='Primary.TButton',
            command=self.refresh_locations
        )
        refresh_locations_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        go_location_btn = ttk.Button(
            location_content,
            text="🚀 Go to Location",
            style='Success.TButton',
            command=self.send_goal,
            state=tk.DISABLED
        )
        go_location_btn.pack(fill=tk.X)
        self.go_location_btn = go_location_btn
        
        self.location_status_label = tk.Label(
            location_content,
            text="",
            font=('Arial', 9),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            anchor='w'
        )
        self.location_status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Navigation Status Card
        nav_status_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        nav_status_card.pack(fill=tk.X, pady=(0, 15))
        
        nav_status_header = tk.Label(
            nav_status_card,
            text="📊 Navigation Status",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        nav_status_header.pack(fill=tk.X)
        
        nav_status_content = tk.Frame(nav_status_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        nav_status_content.pack(fill=tk.X)
        
        self.nav_status_label = tk.Label(
            nav_status_content,
            text="Ready",
            font=('Arial', 11),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['success'],
            anchor='w'
        )
        self.nav_status_label.pack(fill=tk.X)
        
        # Exit button
        exit_frame = tk.Frame(main_container, bg=self.COLORS['bg_main'], pady=10)
        exit_frame.pack(fill=tk.X, pady=(10, 0))
        
        exit_btn = ttk.Button(
            exit_frame,
            text="🚪 Exit",
            style='Danger.TButton',
            command=self.exit_program
        )
        exit_btn.pack(side=tk.RIGHT)
        
        # Status bar
        status_frame = tk.Frame(main_container, bg=self.COLORS['text_dark'], height=30)
        status_frame.pack(fill=tk.X, pady=(0, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Select a map to begin",
            font=('Arial', 9),
            bg=self.COLORS['text_dark'],
            fg='white',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
    
    def refresh_maps(self):
        """Refresh list of available maps"""
        home_dir = os.environ.get('HOME') or os.path.expanduser('~')
        maps_dir = os.path.join(home_dir, 'delivery_bot_pkg', 'data', 'maps')
        os.makedirs(maps_dir, exist_ok=True)
        
        # Find all .yaml map files
        map_files = glob.glob(os.path.join(maps_dir, '*.yaml'))
        map_names = []
        
        for map_file in sorted(map_files):
            map_name = os.path.basename(map_file)
            # Remove .yaml extension
            if map_name.endswith('.yaml'):
                map_name = map_name[:-5]
            map_names.append(map_name)
        
        self.map_combo['values'] = map_names
        
        if map_names:
            self.map_status_label.config(
                text=f"Found {len(map_names)} map(s)",
                fg=self.COLORS['success']
            )
            self.load_map_btn.config(state=tk.NORMAL)
        else:
            self.map_status_label.config(
                text="No maps found in ~/delivery_bot_pkg/data/maps/",
                fg=self.COLORS['warning']
            )
            self.load_map_btn.config(state=tk.DISABLED)
    
    def on_map_selected(self, event=None):
        """Handle map selection"""
        map_name = self.map_var.get()
        if map_name:
            self.map_status_label.config(
                text=f"Selected: {map_name}.yaml",
                fg=self.COLORS['text_dark']
            )
    
    def load_map(self):
        """Load selected map and start localization"""
        map_name = self.map_var.get()
        if not map_name:
            messagebox.showwarning("Warning", "Please select a map")
            return
        
        # Set map path
        home_dir = os.environ.get('HOME') or os.path.expanduser('~')
        maps_dir = os.path.join(home_dir, 'delivery_bot_pkg', 'data', 'maps')
        self.map_path = os.path.join(maps_dir, f"{map_name}.yaml")
        
        if not os.path.exists(self.map_path):
            messagebox.showerror("Error", f"Map file not found: {self.map_path}")
            return
        
        # Set locations file path (same name as map)
        locations_dir = os.path.join(home_dir, 'delivery_bot_pkg', 'data', 'locations')
        os.makedirs(locations_dir, exist_ok=True)
        self.locations_file = os.path.join(locations_dir, f"{map_name}.json")
        self.selected_map = map_name
        
        # Initialize location handler
        self.location_handler = LocationHandler(locations_file=self.locations_file)
        
        self.get_logger().info(f'Loading map: {self.map_path}')
        self.get_logger().info(f'Using locations file: {self.locations_file}')
        
        # Update status
        self.status_label.config(text=f"📂 Loading map '{map_name}'...", fg='white')
        self.map_status_label.config(
            text=f"Loading: {map_name}.yaml",
            fg=self.COLORS['warning']
        )
        self.root.update()
        
        # Start localization in background
        self.start_localization()
        
        # Show initial pose card (pack it normally, not before location_selection_card)
        self.initial_pose_card.pack(fill=tk.X, pady=(0, 15))
        
        # Load locations for initial pose selection
        self.refresh_locations()
        
        self.status_label.config(
            text=f"✅ Map loaded. Set initial pose to continue.",
            fg=self.COLORS['success']
        )
    
    def start_localization(self):
        """Start localization with selected map"""
        if self.localization_running:
            return
        
        # Launch localization
        cmd = [
            'ros2', 'launch', 'turtlebot4_navigation', 'localization.launch.py',
            f'map:={self.map_path}'
        ]
        
        try:
            self.localization_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.localization_running = True
            self.get_logger().info(f'Localization started with map: {self.map_path}')
            
            # Wait a bit, then open initial pose GUI
            self.root.after(3000, self.open_initial_pose_gui)
            
        except Exception as e:
            self.get_logger().error(f'Failed to start localization: {e}')
            messagebox.showerror("Error", f"Failed to start localization: {e}")
    
    def open_initial_pose_gui(self):
        """Open initial pose GUI"""
        # Check if initial pose is already set
        # For now, always show the card - user can set pose
        
        # Load locations for initial pose dropdown
        self.refresh_locations()
        
        self.initial_pose_status_label.config(
            text="Select a location or enter pose manually to set initial pose",
            fg=self.COLORS['text_light']
        )
    
    def refresh_locations(self):
        """Refresh locations list from JSON file"""
        if not self.location_handler:
            self.get_logger().warn('Location handler not initialized')
            return
        
        # Verify locations_file is set
        if not hasattr(self, 'locations_file') or not self.locations_file:
            self.get_logger().error('Locations file path not set')
            return
        
        # Check if locations file exists (use absolute path)
        locations_file_path = os.path.abspath(self.locations_file)
        self.get_logger().info(f'Checking locations file: {locations_file_path}')
        self.get_logger().info(f'File exists: {os.path.exists(locations_file_path)}')
        
        if not os.path.exists(locations_file_path):
            self.get_logger().warn(f'Locations file does not exist: {locations_file_path}')
            self.initial_pose_location_combo['values'] = []
            self.initial_pose_location_var.set("")
            self.location_combo['values'] = []
            self.location_var.set("")
            self.initial_pose_status_label.config(
                text=f"No locations file found: {os.path.basename(self.locations_file)}\nTag locations first using the mapping GUI.",
                fg=self.COLORS['warning']
            )
            return
        
        try:
            # Reload locations from file (use absolute path)
            self.location_handler.locations_file = locations_file_path
            self.location_handler.load_locations()
            locations = self.location_handler.get_location_names()
            
            self.get_logger().info(f'Loaded {len(locations)} locations from {locations_file_path}')
            self.get_logger().info(f'Location names: {locations}')
            
            # Update initial pose location combo
            self.initial_pose_location_combo['values'] = locations
            if locations:
                self.initial_pose_location_var.set(locations[0])
                self.initial_pose_status_label.config(
                    text=f"✅ Found {len(locations)} location(s). Select one to set initial pose.",
                    fg=self.COLORS['success']
                )
            else:
                self.initial_pose_location_var.set("")
                self.initial_pose_status_label.config(
                    text="No locations in file. Tag locations first using the mapping GUI.",
                    fg=self.COLORS['warning']
                )
            
            # Update location selection combo
            self.location_combo['values'] = locations
            if locations:
                self.location_var.set(locations[0])
                self.go_location_btn.config(state=tk.NORMAL)
            else:
                self.location_var.set("")
                self.go_location_btn.config(state=tk.DISABLED)
                self.location_status_label.config(
                    text="No locations available for this map",
                    fg=self.COLORS['warning']
                )
        except Exception as e:
            import traceback
            self.get_logger().error(f'Error loading locations: {e}')
            self.get_logger().error(f'Traceback: {traceback.format_exc()}')
            self.initial_pose_status_label.config(
                text=f"Error loading locations: {str(e)}",
                fg=self.COLORS['danger']
            )
    
    def use_location_for_initial_pose(self):
        """Use selected location for initial pose"""
        location_name = self.initial_pose_location_var.get()
        if not location_name:
            messagebox.showwarning("Warning", "Please select a location")
            return
        
        location = self.location_handler.get_location(location_name)
        if not location:
            messagebox.showerror("Error", f"Location '{location_name}' not found")
            return
        
        # Get pose from location
        pose_msg = self.location_handler.location_to_pose_stamped(location_name, node=self)
        
        # Convert to PoseWithCovarianceStamped
        initial_pose_msg = PoseWithCovarianceStamped()
        initial_pose_msg.header = pose_msg.header
        initial_pose_msg.pose.pose = pose_msg.pose
        
        # Set covariance (default values)
        initial_pose_msg.pose.covariance = [
            0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942
        ]
        
        # Publish initial pose
        self.initial_pose_pub.publish(initial_pose_msg)
        
        # Signal that initial pose is set
        signal_msg = Bool(data=True)
        self.initial_pose_set_pub.publish(signal_msg)
        
        self.get_logger().info(f'Initial pose set from location: {location_name}')
        self.initial_pose_status_label.config(
            text=f"✅ Initial pose set from location: {location_name}",
            fg=self.COLORS['success']
        )
        
        # Wait a bit, then proceed to next step
        self.root.after(2000, self.on_initial_pose_set)
    
    def set_initial_pose_manual(self):
        """Set initial pose manually"""
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            yaw = float(self.yaw_var.get())
            
            # Convert yaw to quaternion
            import math
            yaw_rad = math.radians(yaw)
            qz = math.sin(yaw_rad / 2)
            qw = math.cos(yaw_rad / 2)
            
            # Create pose message
            initial_pose_msg = PoseWithCovarianceStamped()
            initial_pose_msg.header.frame_id = 'map'
            initial_pose_msg.header.stamp = self.get_clock().now().to_msg()
            initial_pose_msg.pose.pose.position.x = float(x)
            initial_pose_msg.pose.pose.position.y = float(y)
            initial_pose_msg.pose.pose.position.z = 0.0
            initial_pose_msg.pose.pose.orientation.z = float(qz)
            initial_pose_msg.pose.pose.orientation.w = float(qw)
            
            # Set covariance
            initial_pose_msg.pose.covariance = [
                0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942
            ]
            
            # Publish initial pose
            self.initial_pose_pub.publish(initial_pose_msg)
            
            # Signal that initial pose is set
            signal_msg = Bool(data=True)
            self.initial_pose_set_pub.publish(signal_msg)
            
            self.get_logger().info(f'Initial pose set manually: x={x}, y={y}, yaw={yaw}')
            self.initial_pose_status_label.config(
                text=f"✅ Initial pose set manually: ({x:.2f}, {y:.2f}, {yaw:.1f}°)",
                fg=self.COLORS['success']
            )
            
            # Wait a bit, then proceed to next step
            self.root.after(2000, self.on_initial_pose_set)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for X, Y, and Yaw")
    
    def initial_pose_set_callback(self, msg: Bool):
        """Callback when initial pose is set"""
        if msg.data and not self.initial_pose_set:
            self.initial_pose_set = True
            self.on_initial_pose_set()
    
    def on_initial_pose_set(self):
        """Called when initial pose is set"""
        if not self.initial_pose_set:
            self.initial_pose_set = True
        
        # Hide initial pose card
        self.initial_pose_card.pack_forget()
        
        # Show location selection card (pack it after navigation status card)
        self.location_selection_card.pack(fill=tk.X, pady=(0, 15))
        
        # Start Nav2 and navigator
        self.start_nav2()
        self.start_navigator()
        
        # Refresh locations
        self.refresh_locations()
        
        self.status_label.config(
            text="✅ Initial pose set. Navigation ready!",
            fg=self.COLORS['success']
        )
    
    def start_nav2(self):
        """Start Nav2 navigation stack"""
        if self.nav2_running:
            return
        
        cmd = ['ros2', 'launch', 'launch/nav2.launch.py']
        
        try:
            home_dir = os.environ.get('HOME') or os.path.expanduser('~')
            self.nav2_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.join(home_dir, 'delivery_bot_pkg')
            )
            self.nav2_running = True
            self.get_logger().info('Nav2 started')
        except Exception as e:
            self.get_logger().error(f'Failed to start Nav2: {e}')
    
    def start_navigator(self):
        """Start delivery navigator node"""
        if self.navigator_running:
            return
        
        if not self.selected_map:
            self.get_logger().error('Cannot start navigator: no map selected')
            return
        
        # Start navigator with map name parameter
        cmd = [
            'ros2', 'run', 'delivery_navigator', 'goal_navigator_node',
            '--ros-args', '-p', f'map_name:={self.selected_map}'
        ]
        
        try:
            home_dir = os.environ.get('HOME') or os.path.expanduser('~')
            self.navigator_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.join(home_dir, 'delivery_bot_pkg'),
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', '')}
            )
            self.navigator_running = True
            self.get_logger().info(f'Delivery navigator started with map: {self.selected_map}')
        except Exception as e:
            self.get_logger().error(f'Failed to start navigator: {e}')
    
    def send_goal(self):
        """Send navigation goal"""
        location_name = self.location_var.get()
        if not location_name:
            messagebox.showwarning("Warning", "Please select a location")
            return
        
        # Confirm
        result = messagebox.askyesno(
            "Confirm Navigation",
            f"Navigate to '{location_name}'?"
        )
        
        if not result:
            return
        
        # Publish goal
        goal_msg = String(data=location_name)
        self.goal_pub.publish(goal_msg)
        
        self.get_logger().info(f'Navigation goal sent: {location_name}')
        self.location_status_label.config(
            text=f"🚀 Navigating to: {location_name}...",
            fg=self.COLORS['warning']
        )
        self.nav_status_label.config(
            text=f"Navigating to: {location_name}...",
            fg=self.COLORS['warning']
        )
    
    def nav_status_callback(self, msg: String):
        """Callback for navigation status"""
        status = msg.data
        self.navigation_status = status
        
        self.root.after(0, lambda: self.update_nav_status(status))
    
    def update_nav_status(self, status: str):
        """Update navigation status display"""
        if "SUCCESS" in status or "successfully" in status.lower():
            self.nav_status_label.config(
                text=f"✅ {status}",
                fg=self.COLORS['success']
            )
            self.location_status_label.config(
                text=f"✅ {status}",
                fg=self.COLORS['success']
            )
        elif "ERROR" in status or "error" in status.lower() or "FAILED" in status:
            self.nav_status_label.config(
                text=f"❌ {status}",
                fg=self.COLORS['danger']
            )
            self.location_status_label.config(
                text=f"❌ {status}",
                fg=self.COLORS['danger']
            )
        else:
            self.nav_status_label.config(
                text=status,
                fg=self.COLORS['text_dark']
            )
    
    def exit_program(self):
        """Exit the program cleanly"""
        result = messagebox.askyesno(
            "Exit",
            "Are you sure you want to exit?\n\n"
            "This will stop all running nodes:\n"
            "- Localization\n"
            "- Nav2\n"
            "- Delivery Navigator\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        self.status_label.config(text="🔄 Exiting...", fg='white')
        self.root.update()
        
        # Stop all processes
        if self.localization_process:
            self.localization_process.terminate()
        if self.nav2_process:
            self.nav2_process.terminate()
        if self.navigator_process:
            self.navigator_process.terminate()
        if self.initial_pose_gui_process:
            self.initial_pose_gui_process.terminate()
        
        # Wait a bit for cleanup
        time.sleep(1)
        
        self.get_logger().info("Exiting Delivery Bot Main GUI...")
        
        # Shutdown ROS2
        if rclpy.ok():
            try:
                rclpy.shutdown()
            except:
                pass
        
        # Destroy node
        try:
            self.destroy_node()
        except:
            pass
        
        # Close GUI
        self.root.quit()
        
        # Force exit
        os._exit(0)
    
    def run(self):
        """Run the GUI"""
        def spin_node():
            try:
                rclpy.spin(self)
            except Exception as e:
                self.get_logger().error(f"Error in spin thread: {e}")
        
        spin_thread = threading.Thread(target=spin_node, daemon=True)
        spin_thread.start()
        
        self.root.mainloop()
        
        # Cleanup
        if rclpy.ok():
            try:
                self.destroy_node()
                rclpy.shutdown()
            except:
                pass


def main(args=None):
    rclpy.init(args=args)
    app = DeliveryBotMainGUI()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

