"""
ROS2 Node for navigating to delivery goal locations
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../location_manager'))
from location_manager.location_handler import LocationHandler


class GoalNavigatorNode(Node):
    """ROS2 Node for navigating to goal locations"""
    
    def __init__(self):
        super().__init__('goal_navigator_node')
        
        # Initialize location handler
        self.location_handler = LocationHandler()
        
        # Action client for Nav2 navigation
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Wait for action server
        self.get_logger().info('Waiting for navigate_to_pose action server...')
        if not self.nav_action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().warn('navigate_to_pose action server not available')
        else:
            self.get_logger().info('Connected to navigate_to_pose action server')
        
        # Subscribers
        self.create_subscription(
            String,
            'delivery_goal',
            self.goal_callback,
            10
        )
        
        # Publishers
        self.status_pub = self.create_publisher(String, 'navigation_status', 10)
        
        # Current goal tracking
        self.current_goal_handle = None
        
        self.get_logger().info('Goal Navigator Node started')
        self.get_logger().info('Send location name to /delivery_goal topic to navigate')
    
    def goal_callback(self, msg: String):
        """
        Callback for receiving goal location name
        
        Args:
            msg: String message containing location name
        """
        location_name = msg.data.strip()
        
        if not location_name:
            self.get_logger().warn('Empty goal location name received')
            status_msg = String(data='ERROR: Empty location name')
            self.status_pub.publish(status_msg)
            return
        
        self.get_logger().info(f'Navigating to location: {location_name}')
        
        # Get location from handler
        location = self.location_handler.get_location(location_name)
        
        if location is None:
            self.get_logger().error(f'Location "{location_name}" not found')
            status_msg = String(data=f'ERROR: Location "{location_name}" not found')
            self.status_pub.publish(status_msg)
            return
        
        # Convert to PoseStamped (pass self to get current timestamp)
        pose = self.location_handler.location_to_pose_stamped(location_name, node=self)
        
        if pose is None:
            self.get_logger().error(f'Failed to convert location "{location_name}" to pose')
            status_msg = String(data=f'ERROR: Failed to convert location "{location_name}"')
            self.status_pub.publish(status_msg)
            return
        
        # Send navigation goal
        self.send_goal(pose, location_name)
    
    def send_goal(self, pose: PoseStamped, location_name: str):
        """
        Send navigation goal to Nav2
        
        Args:
            pose: Target pose
            location_name: Name of the location
        """
        # Cancel any existing goal first
        if self.current_goal_handle is not None:
            self.get_logger().info('Canceling previous goal before sending new one')
            try:
                cancel_future = self.current_goal_handle.cancel_goal_async()
                # Don't wait for cancel to complete, just send the new goal
            except Exception as e:
                self.get_logger().warn(f'Error canceling previous goal: {e}')
            self.current_goal_handle = None
        
        # Create goal message
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        
        # Send goal
        self.get_logger().info(f'Sending navigation goal to {location_name}')
        self.get_logger().info(
            f'  Position: x={pose.pose.position.x:.2f}, '
            f'y={pose.pose.position.y:.2f}, z={pose.pose.position.z:.2f}'
        )
        
        send_goal_future = self.nav_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        
        send_goal_future.add_done_callback(
            lambda future: self.goal_response_callback(future, location_name)
        )
    
    def goal_response_callback(self, future, location_name: str):
        """
        Callback when goal is accepted/rejected
        
        Args:
            future: Future from send_goal_async
            location_name: Name of the location
        """
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error(f'Goal rejected for location: {location_name}')
            status_msg = String(data=f'ERROR: Goal rejected for "{location_name}"')
            self.status_pub.publish(status_msg)
            return
        
        self.get_logger().info(f'Goal accepted for location: {location_name}')
        self.current_goal_handle = goal_handle
        
        # Get result
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda future: self.result_callback(future, location_name)
        )
    
    def feedback_callback(self, feedback_msg):
        """
        Callback for navigation feedback
        
        Args:
            feedback_msg: Navigation feedback message
        """
        feedback = feedback_msg.feedback
        # Can be used to update GUI with navigation progress
        # distance_remaining = feedback.distance_remaining
        # estimated_time_remaining = feedback.estimated_time_remaining
    
    def result_callback(self, future, location_name: str):
        """
        Callback when navigation completes
        
        Args:
            future: Future from get_result_async
            location_name: Name of the location
        """
        try:
            goal_response = future.result()
            goal_status = goal_response.status
            result = goal_response.result
            
            # Nav2 action status codes (from action_msgs.msg.GoalStatus):
            # 0 = UNKNOWN, 1 = ACCEPTED, 2 = EXECUTING, 3 = CANCELED, 
            # 4 = SUCCEEDED, 5 = ABORTED, 6 = CANCELING, 7 = ABORTING
            self.get_logger().info(f'Navigation result for {location_name}: status={goal_status}')
            
            if goal_status == 4:  # SUCCEEDED
                self.get_logger().info(f'Navigation completed successfully for location: {location_name}')
                status_msg = String(data=f'SUCCESS: Arrived at "{location_name}"')
                self.status_pub.publish(status_msg)
            elif goal_status == 3:  # CANCELED
                self.get_logger().warn(f'Navigation was canceled for location: {location_name}')
                status_msg = String(data=f'CANCELED: Navigation canceled for "{location_name}"')
                self.status_pub.publish(status_msg)
            elif goal_status == 5:  # ABORTED
                self.get_logger().error(f'Navigation aborted for location: {location_name}')
                status_msg = String(data=f'ERROR: Navigation aborted for "{location_name}"')
                self.status_pub.publish(status_msg)
            elif goal_status == 6:  # CANCELING
                self.get_logger().warn(f'Navigation is being canceled for location: {location_name}')
                status_msg = String(data=f'CANCELED: Navigation canceled for "{location_name}"')
                self.status_pub.publish(status_msg)
            elif goal_status == 7:  # ABORTING
                self.get_logger().error(f'Navigation is being aborted for location: {location_name}')
                status_msg = String(data=f'ERROR: Navigation aborted for "{location_name}"')
                self.status_pub.publish(status_msg)
            else:
                self.get_logger().warn(f'Navigation ended with status {goal_status} for location: {location_name}')
                status_msg = String(data=f'ERROR: Navigation failed (status {goal_status}) for "{location_name}"')
                self.status_pub.publish(status_msg)
        except Exception as e:
            self.get_logger().error(f'Error processing navigation result for {location_name}: {e}')
            status_msg = String(data=f'ERROR: Navigation failed for "{location_name}"')
            self.status_pub.publish(status_msg)
        
        self.current_goal_handle = None


def main(args=None):
    rclpy.init(args=args)
    node = GoalNavigatorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

