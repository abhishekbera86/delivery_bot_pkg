"""
ROS2 Node for tagging current robot position as a delivery location
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener
from location_manager.location_handler import LocationHandler


class LocationTagNode(Node):
    """ROS2 Node for tagging the current robot position as a delivery location"""
    
    def __init__(self):
        super().__init__('location_tag_node')
        
        # Initialize location handler
        self.location_handler = LocationHandler()
        
        # TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Subscribers
        self.create_subscription(
            String,
            'tag_location',
            self.tag_location_callback,
            10
        )
        
        # Publishers
        self.status_pub = self.create_publisher(String, 'location_tag_status', 10)
        
        self.get_logger().info('Location Tag Node started. Send location name to /tag_location topic.')
        self.get_logger().info('Example: ros2 topic pub /tag_location std_msgs/String "data: \'Loc1\'"')
    
    def get_current_pose(self, frame_id: str = "map") -> PoseStamped:
        """
        Get current robot pose in the specified frame
        
        Args:
            frame_id: Target frame (default: "map")
            
        Returns:
            PoseStamped message or None if transform fails
        """
        try:
            # Get transform from base_link to map
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
            self.get_logger().error(f'Failed to get current pose: {str(e)}')
            return None
    
    def tag_location_callback(self, msg: String):
        """
        Callback for tagging a location
        
        Args:
            msg: String message containing location name
        """
        location_name = msg.data.strip()
        
        if not location_name:
            self.get_logger().warn('Empty location name received')
            status_msg = String(data=f'ERROR: Empty location name')
            self.status_pub.publish(status_msg)
            return
        
        self.get_logger().info(f'Tagging location: {location_name}')
        
        # Get current pose
        pose = self.get_current_pose()
        
        if pose is None:
            self.get_logger().error('Failed to get current robot pose')
            status_msg = String(data=f'ERROR: Failed to get current pose')
            self.status_pub.publish(status_msg)
            return
        
        # Add location
        success = self.location_handler.add_location(
            name=location_name,
            pose=pose,
            description=f"Tagged location: {location_name}"
        )
        
        if success:
            self.get_logger().info(f'Successfully tagged location: {location_name}')
            self.get_logger().info(
                f'  Position: x={pose.pose.position.x:.2f}, '
                f'y={pose.pose.position.y:.2f}, z={pose.pose.position.z:.2f}'
            )
            status_msg = String(data=f'SUCCESS: Tagged {location_name}')
        else:
            self.get_logger().error(f'Failed to tag location: {location_name}')
            status_msg = String(data=f'ERROR: Failed to tag {location_name}')
        
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = LocationTagNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

