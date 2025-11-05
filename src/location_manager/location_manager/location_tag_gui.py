"""
GUI-based location tagging tool for delivery bot
Colorful, professional interface for tagging robot positions
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String, Bool
from tf2_ros import Buffer, TransformListener, TransformException
from location_manager.location_handler import LocationHandler
import threading
import time
import math


class LocationTagGUI(Node):
    """ROS2 Node with GUI for tagging delivery locations"""
    
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
        'text_light': '#7F8C8D',    # Light text
        'accent': '#7209B7',        # Purple accent
    }
    
    def __init__(self):
        super().__init__('location_tag_gui_node')
        
        # Initialize location handler
        self.location_handler = LocationHandler()
        
        # TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Current pose tracking
        self.current_pose = None
        self.pose_update_rate = 0.5  # Update every 0.5 seconds
        
        # Flag to wait for initial pose to be set (for AMCL mode)
        self.initial_pose_set = False
        self.wait_for_initial_pose = True  # Can be set to False to skip waiting
        # Flag to track if map frame exists (works during SLAM or after AMCL initialization)
        self.map_frame_available = False
        
        # Flag to track if we're shutting down
        self.shutting_down = False
        
        # Subscribe to initial pose set signal
        self.initial_pose_set_sub = self.create_subscription(
            Bool,
            '/initial_pose_set',
            self.initial_pose_set_callback,
            10
        )
        
        # Initialize GUI but don't show it yet if waiting for initial pose
        self.root = tk.Tk()
        self.root.title("📍 Location Tagging Tool")
        self.root.geometry("800x700")
        self.root.configure(bg=self.COLORS['bg_main'])
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start pose update thread
        self.pose_update_active = True
        self.pose_thread = threading.Thread(target=self.update_pose_loop, daemon=True)
        self.pose_thread.start()
        
        # Check if we should wait for initial pose
        if self.wait_for_initial_pose:
            self.get_logger().info('Location Tagging GUI Node started - waiting for map frame (SLAM) or initial pose (AMCL)...')
            self.root.withdraw()  # Hide GUI until map frame is available
        else:
            self.get_logger().info('Location Tagging GUI Node started (will work if map frame exists)')
    
    def initial_pose_set_callback(self, msg):
        """Callback when initial pose is set"""
        if msg.data and not self.initial_pose_set:
            self.initial_pose_set = True
            self.get_logger().info('Initial pose set signal received - showing Location Tagging GUI')
            # Show the GUI window
            self.root.after(0, self.show_gui)
    
    def show_gui(self):
        """Show the GUI window"""
        self.root.deiconify()  # Show the window
        self.root.lift()  # Bring to front
        self.root.focus_force()  # Focus the window
    
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
            text="📍 Location Tagging Tool",
            font=('Arial', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Tag current robot position as a delivery location",
            font=('Arial', 10),
            bg=self.COLORS['primary'],
            fg='#E8F4F8'
        )
        subtitle_label.pack()
        
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
        
        # Position display
        self.position_frame = tk.Frame(position_content, bg=self.COLORS['bg_card'])
        self.position_frame.pack(fill=tk.X)
        
        self.position_label = tk.Label(
            self.position_frame,
            text="Position: Loading...",
            font=('Arial', 11),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
            anchor='w'
        )
        self.position_label.pack(fill=tk.X)
        
        self.orientation_label = tk.Label(
            self.position_frame,
            text="Orientation: Loading...",
            font=('Arial', 11),
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_light'],
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
        
        # Save button
        button_frame = tk.Frame(tag_content, bg=self.COLORS['bg_card'])
        button_frame.pack(fill=tk.X)
        
        self.save_button = ttk.Button(
            button_frame,
            text="💾 Save Location",
            style='Success.TButton',
            command=self.tag_location
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = ttk.Button(
            button_frame,
            text="🔄 Refresh Position",
            style='Primary.TButton',
            command=self.refresh_position
        )
        refresh_button.pack(side=tk.LEFT)
        
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
        
        # Locations list with scrollbar
        list_frame = tk.Frame(locations_card, bg=self.COLORS['bg_card'], padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for locations
        tree_frame = tk.Frame(list_frame, bg=self.COLORS['bg_card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.locations_tree = ttk.Treeview(
            tree_frame,
            columns=('Name', 'X', 'Y', 'Yaw'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=8
        )
        scrollbar.config(command=self.locations_tree.yview)
        
        # Configure columns
        self.locations_tree.heading('Name', text='Location Name')
        self.locations_tree.heading('X', text='X (m)')
        self.locations_tree.heading('Y', text='Y (m)')
        self.locations_tree.heading('Yaw', text='Yaw (deg)')
        
        self.locations_tree.column('Name', width=200)
        self.locations_tree.column('X', width=100)
        self.locations_tree.column('Y', width=100)
        self.locations_tree.column('Yaw', width=100)
        
        self.locations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Delete button for selected location
        delete_frame = tk.Frame(list_frame, bg=self.COLORS['bg_card'])
        delete_frame.pack(fill=tk.X, pady=(10, 0))
        
        delete_button = ttk.Button(
            delete_frame,
            text="🗑️ Delete Selected",
            style='Danger.TButton',
            command=self.delete_selected_location
        )
        delete_button.pack(side=tk.LEFT)
        
        refresh_locations_button = ttk.Button(
            delete_frame,
            text="🔄 Refresh List",
            style='Primary.TButton',
            command=self.refresh_locations_list
        )
        refresh_locations_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Exit button frame
        exit_frame = tk.Frame(main_container, bg=self.COLORS['bg_main'], pady=10)
        exit_frame.pack(fill=tk.X, pady=(10, 0))
        
        exit_button = ttk.Button(
            exit_frame,
            text="🚪 Exit Location Tagging",
            style='Danger.TButton',
            command=self.exit_program
        )
        exit_button.pack(side=tk.RIGHT)
        
        # Status bar
        status_frame = tk.Frame(main_container, bg=self.COLORS['text_dark'], height=30)
        status_frame.pack(fill=tk.X, pady=(0, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to tag locations",
            font=('Arial', 9),
            bg=self.COLORS['text_dark'],
            fg='white',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
        
        # Initial load
        self.refresh_locations_list()
        self.refresh_position()
    
    def update_pose_loop(self):
        """Continuously update current pose in background thread"""
        while self.pose_update_active and rclpy.ok():
            try:
                # Check if map frame exists (works during SLAM or after AMCL initialization)
                map_frame_exists = self.check_map_frame_exists()
                self.map_frame_available = map_frame_exists
                
                # If waiting for initial pose (AMCL mode), only proceed if initial pose is set
                # Otherwise (SLAM mode), proceed if map frame exists
                if self.wait_for_initial_pose and not self.initial_pose_set:
                    # Still waiting for initial pose in AMCL mode
                    self.root.after(0, lambda: self.update_position_display(waiting=True))
                elif map_frame_exists:
                    # Map frame exists (either SLAM or AMCL), try to get pose
                    pose = self.get_current_pose()
                    if pose is not None:
                        self.current_pose = pose
                        # Update GUI in main thread
                        self.root.after(0, self.update_position_display)
                        # If we were waiting for initial pose and now have a pose, show GUI
                        if self.wait_for_initial_pose and not self.initial_pose_set and map_frame_exists:
                            # Map frame exists during SLAM - allow tagging even without initial_pose_set
                            self.root.after(0, self.show_gui)
                    else:
                        self.root.after(0, lambda: self.update_position_display(error=True))
                else:
                    # Map frame doesn't exist yet
                    self.root.after(0, lambda: self.update_position_display(waiting=True))
            except Exception as e:
                # Only log errors if map frame should exist (to avoid spam)
                if self.map_frame_available:
                    self.get_logger().error(f'Error updating pose: {e}')
            
            time.sleep(self.pose_update_rate)
    
    def check_map_frame_exists(self) -> bool:
        """Check if map frame exists (works during SLAM or after AMCL initialization)"""
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
            # Check if frame exists first
            try:
                # Try to check if transform is available (with timeout)
                can_transform = self.tf_buffer.can_transform(
                    frame_id,
                    'base_link',
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=0.1)
                )
                if not can_transform:
                    # Transform not available yet
                    return None
            except (TransformException, LookupError, ValueError):
                # Frame doesn't exist yet or transform not available
                return None
            
            # Get the transform
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
            # Don't log errors if map frame doesn't exist yet (this is expected)
            error_str = str(e)
            if "does not exist" in error_str or "LookupError" in error_str:
                return None  # Frame doesn't exist yet, return None silently
            # Only log other errors
            self.get_logger().error(f'Failed to get current pose: {error_str}')
            return None
    
    def update_position_display(self, error=False, waiting=False):
        """Update position display in GUI"""
        if waiting:
            self.position_label.config(
                text="Position: ⏳ Waiting for initial pose to be set...",
                fg=self.COLORS['warning']
            )
            self.orientation_label.config(
                text="Orientation: ⏳ Waiting for map frame...",
                fg=self.COLORS['warning']
            )
            return
        
        if error or self.current_pose is None:
            self.position_label.config(
                text="Position: ❌ Not available (Robot not localized)",
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
        
        # Convert quaternion to yaw
        qx = pose.pose.orientation.x
        qy = pose.pose.orientation.y
        qz = pose.pose.orientation.z
        qw = pose.pose.orientation.w
        
        # Calculate yaw angle
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
            self.status_label.config(text="❌ Failed to get position. Check robot localization.", fg=self.COLORS['danger'])
    
    def tag_location(self):
        """Tag the current location"""
        location_name = self.location_name_var.get().strip()
        
        if not location_name:
            messagebox.showwarning("Warning", "Please enter a location name")
            self.status_label.config(text="⚠️ Please enter a location name", fg=self.COLORS['warning'])
            return
        
        if self.current_pose is None:
            messagebox.showerror("Error", "Cannot get current robot position.\nMake sure robot is localized.")
            self.status_label.config(text="❌ Cannot get position", fg=self.COLORS['danger'])
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
        
        count = len(locations)
        self.status_label.config(
            text=f"📋 {count} location(s) loaded",
            fg='white'
        )
    
    def delete_selected_location(self):
        """Delete the selected location"""
        selection = self.locations_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a location to delete")
            return
        
        item = self.locations_tree.item(selection[0])
        location_name = item['values'][0]
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete location '{location_name}'?"
        )
        
        if result:
            success = self.location_handler.delete_location(location_name)
            if success:
                self.refresh_locations_list()
                self.status_label.config(
                    text=f"✅ Location '{location_name}' deleted",
                    fg=self.COLORS['success']
                )
                self.root.after(3000, lambda: self.status_label.config(text="Ready", fg='white'))
            else:
                messagebox.showerror("Error", f"Failed to delete location '{location_name}'")
                self.status_label.config(text="❌ Failed to delete location", fg=self.COLORS['danger'])
    
    def exit_program(self):
        """Exit the program cleanly"""
        result = messagebox.askyesno(
            "Exit Location Tagging",
            "Are you sure you want to exit?\n\nThis will stop the location tagging node."
        )
        
        if result:
            self.status_label.config(text="🔄 Exiting...", fg='white')
            self.root.update()
            
            self.get_logger().info("Location Tagging GUI exited by user - shutting down...")
            
            # Perform shutdown immediately
            self._perform_shutdown()
    
    def _perform_shutdown(self):
        """Perform the actual shutdown"""
        self.shutting_down = True
        
        # Stop pose update thread
        self.pose_update_active = False
        
        # Shutdown ROS2 first (this will stop the spin thread)
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
        
        # Close GUI - this will exit mainloop()
        self.root.quit()
        
        # Give a moment for cleanup
        import time
        time.sleep(0.1)
        
        # Force exit the program
        import os
        os._exit(0)  # Force exit (terminates process immediately)
    
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
        
        # Clean shutdown (only if not already shutting down)
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
    app = LocationTagGUI()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

