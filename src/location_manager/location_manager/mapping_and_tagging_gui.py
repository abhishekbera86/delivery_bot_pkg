"""
Unified GUI for mapping and location tagging
Combines SLAM mapping, location tagging, and map saving in one interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener, TransformException
from location_manager.location_handler import LocationHandler, find_workspace_root
import threading
import time
import math
import os


class MappingAndTaggingGUI(Node):
    """ROS2 Node with unified GUI for mapping and location tagging"""
    
    # Color scheme - modern and professional
    COLORS = {
        'primary': '#2E86AB',      # Blue
        'secondary': '#A23B72',     # Purple
        'success': '#06A77D',       # Green
        'warning': '#F18F01',       # Orange
        'danger': '#C73E1D',        # Red
        'bg_main': '#F5F5F5',       # Light gray background
        'bg_card': '#FFFFFF',       # White card background
        'text_dark': '#2C3E50',     # Dark text
        'text_light': '#7F8C8D',     # Light text
        'accent': '#7209B7',        # Purple accent
    }
    
    def __init__(self):
        super().__init__('mapping_and_tagging_gui_node')
        
        # Initialize location handler (will be updated when JSON filename is set)
        self.locations_file = None
        self.location_handler = None
        
        # TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Current pose tracking
        self.current_pose = None
        self.pose_update_rate = 0.5  # Update every 0.5 seconds
        self.map_frame_available = False
        
        # Flag to track if we're shutting down
        self.shutting_down = False
        
        # Publisher for map saving
        self.map_save_pub = self.create_publisher(String, '/save_map', 10)
        
        # Subscriber for map save status
        self.map_save_status_sub = self.create_subscription(
            String,
            '/map_save_status',
            self.map_save_status_callback,
            10
        )
        
        # Map save status
        self.map_save_status = None
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("🗺️ Mapping and Location Tagging")
        self.root.geometry("900x850")
        self.root.configure(bg=self.COLORS['bg_main'])
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start pose update thread
        self.pose_update_active = True
        self.pose_thread = threading.Thread(target=self.update_pose_loop, daemon=True)
        self.pose_thread.start()
        
        self.get_logger().info('Mapping and Tagging GUI Node started - waiting for map frame...')
    
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
            text="🗺️ Mapping and Location Tagging",
            font=('Arial', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Create map, tag locations, and save everything",
            font=('Arial', 10),
            bg=self.COLORS['primary'],
            fg='#E8F4F8'
        )
        subtitle_label.pack()
        
        # Configuration Card
        config_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        config_card.pack(fill=tk.X, pady=(0, 15))
        
        config_header = tk.Label(
            config_card,
            text="⚙️ Configuration",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        config_header.pack(fill=tk.X)
        
        config_content = tk.Frame(config_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        config_content.pack(fill=tk.X)
        
        # JSON filename input
        json_frame = tk.Frame(config_content, bg=self.COLORS['bg_card'])
        json_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            json_frame,
            text="Locations JSON File:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.json_filename_var = tk.StringVar(value="locations")
        json_entry = tk.Entry(
            json_frame,
            textvariable=self.json_filename_var,
            font=('Arial', 11),
            width=40,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#CCCCCC'
        )
        json_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        set_json_btn = ttk.Button(
            json_frame,
            text="Set",
            style='Primary.TButton',
            command=self.set_json_filename
        )
        set_json_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Current Position Card
        position_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        position_card.pack(fill=tk.X, pady=(0, 15))
        
        position_header = tk.Label(
            position_card,
            text="🤖 Current Robot Position",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        position_header.pack(fill=tk.X)
        
        position_content = tk.Frame(position_card, bg=self.COLORS['bg_card'], padx=15, pady=10)
        position_content.pack(fill=tk.X)
        
        self.position_frame = tk.Frame(position_content, bg=self.COLORS['bg_card'])
        self.position_frame.pack(fill=tk.X)
        
        self.position_label = tk.Label(
            self.position_frame,
            text="Position: Waiting for map frame...",
            font=('Arial', 11),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['warning'],
            anchor='w'
        )
        self.position_label.pack(fill=tk.X)
        
        self.orientation_label = tk.Label(
            self.position_frame,
            text="Orientation: Waiting for map frame...",
            font=('Arial', 11),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['warning'],
            anchor='w'
        )
        self.orientation_label.pack(fill=tk.X, pady=(5, 0))
        
        # Tag Location Card
        tag_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        tag_card.pack(fill=tk.X, pady=(0, 15))
        
        tag_header = tk.Label(
            tag_card,
            text="🏷️ Tag New Location",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        tag_header.pack(fill=tk.X)
        
        tag_content = tk.Frame(tag_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        tag_content.pack(fill=tk.X)
        
        # Location name input
        name_frame = tk.Frame(tag_content, bg=self.COLORS['bg_card'])
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            name_frame,
            text="Location Name:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.location_name_var = tk.StringVar()
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.location_name_var,
            font=('Arial', 11),
            width=30,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#CCCCCC'
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name_entry.bind('<Return>', lambda e: self.tag_location())
        
        # Save location button
        button_frame = tk.Frame(tag_content, bg=self.COLORS['bg_card'])
        button_frame.pack(fill=tk.X)
        
        self.save_location_btn = ttk.Button(
            button_frame,
            text="💾 Save Location",
            style='Success.TButton',
            command=self.tag_location
        )
        self.save_location_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh Position",
            style='Primary.TButton',
            command=self.refresh_position
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Existing Locations Card
        locations_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        locations_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        locations_header = tk.Label(
            locations_card,
            text="📋 Tagged Locations",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        locations_header.pack(fill=tk.X)
        
        list_frame = tk.Frame(locations_card, bg=self.COLORS['bg_card'], padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(list_frame, bg=self.COLORS['bg_card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.locations_tree = ttk.Treeview(
            tree_frame,
            columns=('Name', 'X', 'Y', 'Yaw'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=6
        )
        scrollbar.config(command=self.locations_tree.yview)
        
        self.locations_tree.heading('Name', text='Location Name')
        self.locations_tree.heading('X', text='X (m)')
        self.locations_tree.heading('Y', text='Y (m)')
        self.locations_tree.heading('Yaw', text='Yaw (deg)')
        
        self.locations_tree.column('Name', width=200)
        self.locations_tree.column('X', width=100)
        self.locations_tree.column('Y', width=100)
        self.locations_tree.column('Yaw', width=100)
        
        self.locations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Save Map Card
        save_map_card = tk.Frame(main_container, bg=self.COLORS['bg_card'], relief=tk.RAISED, bd=2)
        save_map_card.pack(fill=tk.X, pady=(0, 15))
        
        save_map_header = tk.Label(
            save_map_card,
            text="💾 Save Map",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            padx=15,
            pady=10
        )
        save_map_header.pack(fill=tk.X)
        
        save_map_content = tk.Frame(save_map_card, bg=self.COLORS['bg_card'], padx=15, pady=15)
        save_map_content.pack(fill=tk.X)
        
        map_name_frame = tk.Frame(save_map_content, bg=self.COLORS['bg_card'])
        map_name_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            map_name_frame,
            text="Map Name:",
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_dark'],
            anchor='w',
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.map_name_var = tk.StringVar()
        map_name_entry = tk.Entry(
            map_name_frame,
            textvariable=self.map_name_var,
            font=('Arial', 11),
            width=30,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['warning'],
            highlightbackground='#CCCCCC',
            state='readonly'
        )
        map_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        map_name_entry.bind('<Return>', lambda e: self.save_map())
        
        save_map_btn = ttk.Button(
            map_name_frame,
            text="💾 Save Map",
            style='Warning.TButton',
            command=self.save_map
        )
        save_map_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.map_save_status_label = tk.Label(
            save_map_content,
            text="",
            font=('Arial', 9),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            anchor='w'
        )
        self.map_save_status_label.pack(fill=tk.X)
        
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
            text="Ready - Waiting for map frame...",
            font=('Arial', 9),
            bg=self.COLORS['text_dark'],
            fg='white',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
        
        # Initialize location handler with default filename
        self.set_json_filename()
    
    def set_json_filename(self):
        """Set the JSON filename for locations"""
        json_name = self.json_filename_var.get().strip()
        if not json_name:
            json_name = "locations"
            self.json_filename_var.set(json_name)
        
        # Remove .json extension if user typed it (we'll add it internally)
        if json_name.endswith('.json'):
            json_name = json_name[:-5]
            self.json_filename_var.set(json_name)
        
        # Add .json extension internally for file operations
        json_filename = json_name + '.json'
        
        # Update map name field with the same name
        self.map_name_var.set(json_name)
        
        # Create full path in data/locations directory
        workspace_dir = find_workspace_root()
        data_dir = os.path.join(workspace_dir, "data")
        locations_dir = os.path.join(data_dir, "locations")
        os.makedirs(locations_dir, exist_ok=True)
        locations_file = os.path.join(locations_dir, json_filename)
        
        self.locations_file = locations_file
        
        # Reinitialize location handler with new file
        self.location_handler = LocationHandler(locations_file=locations_file)
        
        self.get_logger().info(f'Locations file set to: {locations_file}')
        self.status_label.config(text=f"Locations will be saved to: {json_filename}")
        self.root.after(2000, lambda: self.status_label.config(text="Ready", fg='white'))
        
        # Refresh locations list
        self.refresh_locations_list()
    
    def map_save_status_callback(self, msg: String):
        """Callback for map save status"""
        self.map_save_status = msg.data
        self.root.after(0, self.update_map_save_status)
    
    def update_map_save_status(self):
        """Update map save status display"""
        if self.map_save_status:
            if "SUCCESS" in self.map_save_status or "successfully" in self.map_save_status.lower():
                self.map_save_status_label.config(
                    text=f"✅ {self.map_save_status}",
                    fg=self.COLORS['success']
                )
                self.status_label.config(
                    text=f"✅ Map saved successfully!",
                    fg=self.COLORS['success']
                )
            elif "ERROR" in self.map_save_status or "error" in self.map_save_status.lower():
                self.map_save_status_label.config(
                    text=f"❌ {self.map_save_status}",
                    fg=self.COLORS['danger']
                )
                self.status_label.config(
                    text=f"❌ {self.map_save_status}",
                    fg=self.COLORS['danger']
                )
            else:
                self.map_save_status_label.config(
                    text=self.map_save_status,
                    fg=self.COLORS['text_light']
                )
    
    def update_pose_loop(self):
        """Continuously update current pose in background thread"""
        while self.pose_update_active and rclpy.ok():
            try:
                map_frame_exists = self.check_map_frame_exists()
                self.map_frame_available = map_frame_exists
                
                if map_frame_exists:
                    pose = self.get_current_pose()
                    if pose is not None:
                        self.current_pose = pose
                        self.root.after(0, self.update_position_display)
                    else:
                        self.root.after(0, lambda: self.update_position_display(error=True))
                else:
                    self.root.after(0, lambda: self.update_position_display(waiting=True))
            except Exception as e:
                if self.map_frame_available:
                    self.get_logger().error(f'Error updating pose: {e}')
            
            time.sleep(self.pose_update_rate)
    
    def check_map_frame_exists(self) -> bool:
        """Check if map frame exists"""
        try:
            can_transform = self.tf_buffer.can_transform(
                'map',
                'base_link',
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.1)
            )
            return can_transform
        except (TransformException, LookupError, ValueError):
            return False
    
    def get_current_pose(self, frame_id: str = "map") -> PoseStamped:
        """Get current robot pose in the specified frame"""
        try:
            transform = self.tf_buffer.lookup_transform(
                frame_id,
                'base_link',
                rclpy.time.Time()
            )
            
            pose = PoseStamped()
            pose.header.frame_id = frame_id
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = transform.transform.translation.x
            pose.pose.position.y = transform.transform.translation.y
            pose.pose.position.z = transform.transform.translation.z
            pose.pose.orientation = transform.transform.rotation
            
            return pose
        except Exception as e:
            return None
    
    def update_position_display(self, error=False, waiting=False):
        """Update position display in GUI"""
        if waiting:
            self.position_label.config(
                text="Position: ⏳ Waiting for map frame...",
                fg=self.COLORS['warning']
            )
            self.orientation_label.config(
                text="Orientation: ⏳ Waiting for map frame...",
                fg=self.COLORS['warning']
            )
            return
        
        if error or self.current_pose is None:
            self.position_label.config(
                text="Position: ❌ Not available",
                fg=self.COLORS['danger']
            )
            self.orientation_label.config(
                text="Orientation: ❌ Not available",
                fg=self.COLORS['danger']
            )
            return
        
        pose = self.current_pose
        x = pose.pose.position.x
        y = pose.pose.position.y
        z = pose.pose.position.z
        
        qx = pose.pose.orientation.x
        qy = pose.pose.orientation.y
        qz = pose.pose.orientation.z
        qw = pose.pose.orientation.w
        
        yaw_rad = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
        yaw_deg = math.degrees(yaw_rad)
        
        self.position_label.config(
            text=f"Position: X = {x:.3f} m, Y = {y:.3f} m, Z = {z:.3f} m",
            fg=self.COLORS['success']
        )
        self.orientation_label.config(
            text=f"Orientation: Yaw = {yaw_deg:.1f}°",
            fg=self.COLORS['success']
        )
    
    def refresh_position(self):
        """Manually refresh current position"""
        self.status_label.config(text="🔄 Refreshing position...", fg='white')
        self.root.update()
        
        pose = self.get_current_pose()
        if pose is not None:
            self.current_pose = pose
            self.update_position_display()
            self.status_label.config(text="✅ Position updated", fg=self.COLORS['success'])
            self.root.after(2000, lambda: self.status_label.config(text="Ready", fg='white'))
        else:
            self.update_position_display(error=True)
            self.status_label.config(text="❌ Failed to get position", fg=self.COLORS['danger'])
    
    def tag_location(self):
        """Tag the current location"""
        location_name = self.location_name_var.get().strip()
        
        if not location_name:
            messagebox.showwarning("Warning", "Please enter a location name")
            self.status_label.config(text="⚠️ Please enter a location name", fg=self.COLORS['warning'])
            return
        
        if self.current_pose is None:
            messagebox.showerror("Error", "Cannot get current robot position.\nMake sure SLAM is running and map frame exists.")
            self.status_label.config(text="❌ Cannot get position", fg=self.COLORS['danger'])
            return
        
        if self.location_handler is None:
            messagebox.showerror("Error", "Location handler not initialized.\nPlease set the JSON filename first.")
            self.status_label.config(text="❌ Set JSON filename first", fg=self.COLORS['danger'])
            return
        
        # Check if location already exists
        existing_locations = self.location_handler.get_all_locations()
        if location_name in existing_locations:
            result = messagebox.askyesno(
                "Location Exists",
                f"Location '{location_name}' already exists.\nDo you want to overwrite it?"
            )
            if not result:
                return
        
        # Tag the location
        self.status_label.config(text=f"💾 Saving location '{location_name}'...", fg='white')
        self.root.update()
        
        success = self.location_handler.add_location(
            name=location_name,
            pose=self.current_pose,
            description=f"Tagged location: {location_name}"
        )
        
        if success:
            self.get_logger().info(f'Successfully tagged location: {location_name}')
            messagebox.showinfo(
                "Success",
                f"Location '{location_name}' tagged successfully!\n\n"
                f"Position: ({self.current_pose.pose.position.x:.2f}, {self.current_pose.pose.position.y:.2f})"
            )
            self.location_name_var.set("")
            self.refresh_locations_list()
            self.status_label.config(
                text=f"✅ Location '{location_name}' saved successfully",
                fg=self.COLORS['success']
            )
            self.root.after(3000, lambda: self.status_label.config(text="Ready", fg='white'))
        else:
            self.get_logger().error(f'Failed to tag location: {location_name}')
            messagebox.showerror("Error", f"Failed to save location '{location_name}'")
            self.status_label.config(text="❌ Failed to save location", fg=self.COLORS['danger'])
    
    def refresh_locations_list(self):
        """Refresh the list of tagged locations"""
        # Clear existing items
        for item in self.locations_tree.get_children():
            self.locations_tree.delete(item)
        
        if self.location_handler is None:
            return
        
        # Load locations
        locations = self.location_handler.get_all_locations()
        
        # Populate tree
        for name, location in locations.items():
            x = location['position']['x']
            y = location['position']['y']
            
            # Calculate yaw from quaternion
            qx = location['orientation']['x']
            qy = location['orientation']['y']
            qz = location['orientation']['z']
            qw = location['orientation']['w']
            yaw_rad = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
            yaw_deg = math.degrees(yaw_rad)
            
            self.locations_tree.insert(
                '',
                tk.END,
                values=(name, f"{x:.3f}", f"{y:.3f}", f"{yaw_deg:.1f}")
            )
    
    def save_map(self):
        """Save the current map"""
        map_name = self.map_name_var.get().strip()
        
        if not map_name:
            messagebox.showwarning("Warning", "Please enter a map name")
            self.status_label.config(text="⚠️ Please enter a map name", fg=self.COLORS['warning'])
            return
        
        # Confirm save
        result = messagebox.askyesno(
            "Save Map",
            f"Save map as '{map_name}'?\n\n"
            f"This will save the map to:\n"
            f"{os.path.join(find_workspace_root(), 'data', 'maps', map_name)}.yaml"
        )
        
        if not result:
            return
        
        # Publish map save request
        self.status_label.config(text=f"💾 Saving map '{map_name}'...", fg='white')
        self.map_save_status_label.config(text="Saving map...", fg=self.COLORS['text_light'])
        self.root.update()
        
        msg = String()
        msg.data = map_name
        self.map_save_pub.publish(msg)
        
        self.get_logger().info(f'Map save request sent: {map_name}')
    
    def exit_program(self):
        """Exit the program cleanly"""
        result = messagebox.askyesno(
            "Exit",
            "Are you sure you want to exit?\n\n"
            "Make sure you have:\n"
            "1. Saved all locations\n"
            "2. Saved the map (if done mapping)\n\n"
            "This will stop the mapping and tagging node."
        )
        
        if result:
            self.status_label.config(text="🔄 Exiting...", fg='white')
            self.root.update()
            
            self.get_logger().info("Exiting Mapping and Tagging GUI...")
            self._perform_shutdown()
    
    def _perform_shutdown(self):
        """Perform the actual shutdown"""
        self.shutting_down = True
        
        # Stop pose update thread
        self.pose_update_active = False
        
        # Shutdown ROS2
        if rclpy.ok():
            try:
                self.get_logger().info("Shutting down ROS2 node...")
                rclpy.shutdown()
            except Exception as e:
                self.get_logger().error(f"Error during ROS2 shutdown: {e}")
        
        # Destroy node
        try:
            self.destroy_node()
        except Exception as e:
            self.get_logger().error(f"Error destroying node: {e}")
        
        # Close GUI
        self.root.quit()
        
        # Force exit
        import os
        os._exit(0)
    
    def run(self):
        """Run the GUI"""
        def spin_node():
            try:
                rclpy.spin(self)
            except Exception as e:
                if not self.shutting_down:
                    self.get_logger().error(f"Error in spin thread: {e}")
        
        spin_thread = threading.Thread(target=spin_node, daemon=True)
        spin_thread.start()
        
        self.root.mainloop()
        
        # Clean shutdown
        if not self.shutting_down:
            self.pose_update_active = False
            if rclpy.ok():
                try:
                    self.destroy_node()
                    rclpy.shutdown()
                except Exception as e:
                    self.get_logger().error(f"Error during cleanup: {e}")


def main(args=None):
    rclpy.init(args=args)
    app = MappingAndTaggingGUI()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

