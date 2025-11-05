"""
ROS2 Node for saving SLAM maps
Supports both SLAM Toolbox (during mapping) and Nav2 (during navigation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav2_msgs.srv import SaveMap as Nav2SaveMap
try:
    from slam_toolbox.srv import SaveMap as SlamToolboxSaveMap
except ImportError:
    SlamToolboxSaveMap = None
import os
import time


class MapSaverNode(Node):
    """ROS2 Node for saving maps from SLAM"""
    
    def __init__(self):
        super().__init__('map_saver_node')
        
        # Default map directory
        self.map_dir = os.environ.get('HOME') + '/delivery_bot_pkg/data/maps'
        os.makedirs(self.map_dir, exist_ok=True)
        
        # Clients for map_saver services (try both SLAM Toolbox and Nav2)
        self.nav2_map_saver_client = None
        self.slam_toolbox_map_saver_client = None
        self.active_service_type = None
        
        # Try to connect to Nav2 map saver (for navigation)
        self.nav2_map_saver_client = self.create_client(Nav2SaveMap, '/map_saver/save_map')
        
        # Try to connect to SLAM Toolbox map saver (for mapping)
        if SlamToolboxSaveMap is not None:
            self.slam_toolbox_map_saver_client = self.create_client(
                SlamToolboxSaveMap, '/slam_toolbox/save_map')
        
        # Wait for at least one service to be available
        self.get_logger().info('Waiting for map saver service...')
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            # Check Nav2 service
            if self.nav2_map_saver_client.wait_for_service(timeout_sec=1.0):
                self.active_service_type = 'nav2'
                self.get_logger().info('Connected to Nav2 map_saver service')
                break
            
            # Check SLAM Toolbox service
            if (self.slam_toolbox_map_saver_client is not None and 
                self.slam_toolbox_map_saver_client.wait_for_service(timeout_sec=1.0)):
                self.active_service_type = 'slam_toolbox'
                self.get_logger().info('Connected to SLAM Toolbox map_saver service')
                break
            
            attempts += 1
            self.get_logger().warn(
                f'map_saver service not available (attempt {attempts}/{max_attempts}), waiting...')
        
        if self.active_service_type is None:
            self.get_logger().error(
                'No map saver service available. Make sure SLAM or Nav2 is running.')
            self.get_logger().error(
                'Expected services: /map_saver/save_map (Nav2) or /slam_toolbox/save_map (SLAM Toolbox)')
        
        # Subscribers
        self.create_subscription(
            String,
            'save_map',
            self.save_map_callback,
            10
        )
        
        # Publishers
        self.status_pub = self.create_publisher(String, 'map_save_status', 10)
        
        self.get_logger().info('Map Saver Node started')
        self.get_logger().info(f'Default map directory: {self.map_dir}')
        self.get_logger().info('Send map name to /save_map topic to save current map')
    
    def save_map_callback(self, msg: String):
        """
        Callback for saving map
        
        Args:
            msg: String message containing map name
        """
        map_name = msg.data.strip()
        
        if not map_name:
            self.get_logger().warn('Empty map name received')
            status_msg = String(data='ERROR: Empty map name')
            self.status_pub.publish(status_msg)
            return
        
        # Re-check which service is available (in case it wasn't available at startup)
        if self.active_service_type is None:
            if self.nav2_map_saver_client.wait_for_service(timeout_sec=0.5):
                self.active_service_type = 'nav2'
                self.get_logger().info('Nav2 map_saver service now available')
            elif (self.slam_toolbox_map_saver_client is not None and 
                  self.slam_toolbox_map_saver_client.wait_for_service(timeout_sec=0.5)):
                self.active_service_type = 'slam_toolbox'
                self.get_logger().info('SLAM Toolbox map_saver service now available')
        
        if self.active_service_type is None:
            self.get_logger().error('No map saver service available')
            status_msg = String(data='ERROR: No map saver service available')
            self.status_pub.publish(status_msg)
            return
        
        self.get_logger().info(f'Saving map: {map_name} using {self.active_service_type}')
        
        if self.active_service_type == 'nav2':
            # Use Nav2 map saver
            request = Nav2SaveMap.Request()
            request.map_url = os.path.join(self.map_dir, map_name)
            future = self.nav2_map_saver_client.call_async(request)
            rclpy.spin_until_future_complete(self, future)
            
            if future.result() is not None:
                response = future.result()
                if response:
                    self.get_logger().info(f'Map saved successfully: {request.map_url}')
                    status_msg = String(data=f'SUCCESS: Map saved to {request.map_url}')
                else:
                    self.get_logger().error(f'Failed to save map: {map_name}')
                    status_msg = String(data=f'ERROR: Failed to save map {map_name}')
            else:
                self.get_logger().error('Nav2 service call failed')
                status_msg = String(data=f'ERROR: Service call failed for {map_name}')
        
        elif self.active_service_type == 'slam_toolbox':
            # Use SLAM Toolbox map saver
            # SLAM Toolbox saves to the current working directory
            # So we need to change directory before calling the service
            map_name_clean = map_name.replace('.yaml', '').replace('.pgm', '')
            
            # Save current directory
            original_cwd = os.getcwd()
            
            try:
                # Change to map directory (SLAM Toolbox saves to current directory)
                os.chdir(self.map_dir)
                
                request = SlamToolboxSaveMap.Request()
                request.name.data = map_name_clean
                
                # SLAM Toolbox save_map service is known to sometimes hang
                # So we'll call it and check for files, rather than waiting for response
                self.get_logger().info(f'Calling SLAM Toolbox to save map: {map_name_clean}')
                future = self.slam_toolbox_map_saver_client.call_async(request)
                
                # Wait a bit for service call to be sent
                rclpy.spin_once(self, timeout_sec=0.5)
                
                # Wait for files to appear (more reliable than waiting for service response)
                # SLAM Toolbox often ignores current directory and saves to workspace root
                self.get_logger().info('Waiting for map files to be created...')
                map_yaml_path = os.path.join(self.map_dir, map_name_clean + '.yaml')
                map_pgm_path = os.path.join(self.map_dir, map_name_clean + '.pgm')
                
                # Check multiple possible locations where SLAM Toolbox might save files
                # 1. Target map directory
                # 2. Original current directory (where node was started)
                # 3. Workspace root (~/delivery_bot_pkg/)
                workspace_root = os.environ.get('HOME') + '/delivery_bot_pkg'
                possible_locations = [
                    (self.map_dir, "target map directory"),
                    (original_cwd, "node startup directory"),
                    (workspace_root, "workspace root"),
                    (os.environ.get('HOME'), "home directory"),
                ]
                
                max_wait_time = 15.0  # Wait up to 15 seconds for files
                check_interval = 0.5
                start_time = time.time()
                files_created = False
                found_yaml_path = None
                found_pgm_path = None
                
                while (time.time() - start_time) < max_wait_time:
                    # Check all possible locations
                    for check_dir, location_desc in possible_locations:
                        check_yaml = os.path.join(check_dir, map_name_clean + '.yaml')
                        check_pgm = os.path.join(check_dir, map_name_clean + '.pgm')
                        
                        if os.path.exists(check_yaml) and os.path.exists(check_pgm):
                            found_yaml_path = check_yaml
                            found_pgm_path = check_pgm
                            self.get_logger().info(f'Found map files in {location_desc}: {check_dir}')
                            
                            # If not in target directory, move them
                            if check_dir != self.map_dir:
                                import shutil
                                try:
                                    self.get_logger().info(f'Moving map files to target directory...')
                                    shutil.move(check_yaml, map_yaml_path)
                                    shutil.move(check_pgm, map_pgm_path)
                                    self.get_logger().info(f'Moved map files to {self.map_dir}')
                                except Exception as e:
                                    self.get_logger().error(f'Error moving map files: {e}')
                                    # Files found but couldn't move - still consider success
                            
                            files_created = True
                            break
                    
                    if files_created:
                        break
                    
                    # Process ROS callbacks while waiting
                    rclpy.spin_once(self, timeout_sec=check_interval)
                
                if files_created:
                    self.get_logger().info(f'Map saved successfully: {map_yaml_path}')
                    status_msg = String(data=f'SUCCESS: Map saved to {map_yaml_path}')
                else:
                    # Check if service call completed
                    if future.done():
                        try:
                            response = future.result()
                            if response.result == 0:
                                self.get_logger().info(f'Service returned success but files not found yet. Map may still be saving.')
                                status_msg = String(data=f'WARNING: Service success but files not visible yet. Check {self.map_dir}')
                            else:
                                self.get_logger().error(f'Service returned error code: {response.result}')
                                status_msg = String(data=f'ERROR: Failed to save map (code: {response.result})')
                        except Exception as e:
                            self.get_logger().error(f'Error getting service result: {e}')
                            status_msg = String(data=f'ERROR: Service call issue - check if map files were created')
                    else:
                        self.get_logger().error('Map files not created within timeout period')
                        status_msg = String(data=f'ERROR: Map files not created. Service may still be processing.')
            finally:
                # Always restore original directory
                os.chdir(original_cwd)
        
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = MapSaverNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

