import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from my_robot_interfaces.msg import TurtleArray
from my_robot_interfaces.msg import Turtle
from my_robot_interfaces.srv import CatchTurtle
import math
from functools import partial
 
class TurtleControllerNode(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("turtle_contoller") # MODIFY NAME
        self.turtle_to_catch_: Turtle = None
        self.pose_: Pose = None
        self.catch_turtle_client_ = self.create_client(CatchTurtle, "catch_turtle")
        self.pose_subscriber_ = self.create_subscription(Pose,"turtle1/pose",self.callback_turtle_pose,10)
        self.cmd_vel_publisher_ = self.create_publisher(Twist,"turtle1/cmd_vel",10)
        self.control_loop_timer_ = self.create_timer(0.01, self.control_loop)
        self.alive_turtles_subscriber_ = self.create_subscription(TurtleArray,"alive_turtles",self.callback_alive_turtles,10)

    def callback_alive_turtles(self, msg:TurtleArray):
        if len(msg.turtles) > 0:
            self.turtle_to_catch_ = msg.turtles[0]
            self.get_logger().info(f"Catching turtle: {self.turtle_to_catch_.name}")

    def callback_turtle_pose(self, pose:Pose):
        self.pose_ = pose
        
    def control_loop(self):
        if self.pose_ == None or self.turtle_to_catch_ == None:
            return
        
        dist_x = self.turtle_to_catch_.x - self.pose_.x
        dist_y = self.turtle_to_catch_.y - self.pose_.y
        distance = math.sqrt(dist_x**2 + dist_y**2)
        
        cmd = Twist()

        

        if distance > 0.5:
            cmd.linear.x = 2*distance
            goal_theta = math.atan2(dist_y, dist_x)
            diff = goal_theta - self.pose_.theta
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi
            cmd.angular.z = 6*diff
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.call_catch_turtle_service(self.turtle_to_catch_.name)
            self.turtle_to_catch_ = None

        self.cmd_vel_publisher_.publish(cmd)

    def call_catch_turtle_service(self,turtle_name):
        while not self.catch_turtle_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for catch turtle service to be available")
        request = CatchTurtle.Request()
        request.name = turtle_name
        future = self.catch_turtle_client_.call_async(request)
        future.add_done_callback(partial(self.callback_catch_turtle_service, turtle_name=turtle_name))
    def callback_catch_turtle_service(self,future,turtle_name):
        response:CatchTurtle.Response = future.result()
        if response.success:
            self.get_logger().info(f"Caught turtle with name {turtle_name}")
        else:
            self.get_logger().error("Failed to catch turtle")

def main(args=None): 
    rclpy.init(args=args)
    node = TurtleControllerNode() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()
