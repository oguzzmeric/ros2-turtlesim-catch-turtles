import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
from functools import partial
import random
import math
from my_robot_interfaces.msg import TurtleArray
from my_robot_interfaces.msg import Turtle
from my_robot_interfaces.srv import CatchTurtle
from turtlesim.srv import Kill
 
class TurtleSpawnerNode(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("turtle_spawner") # MODIFY NAME
        self.spawn_client_ = self.create_client(Spawn, "/spawn")
        self.spawn_turtles_timer_ = self.create_timer(2.0,self.spawn_new_turtle)
        self.catch_turtle_service_ = self.create_service(CatchTurtle, "catch_turtle", self.callback_catch_turtle)
        self.alive_turtles_publisher_ = self.create_publisher(TurtleArray, "alive_turtles", 10)
        self.kill_client_ = self.create_client(Kill, "/kill")
        self.alive_turtles_ = []
        self.turtle_name_prefix = "turtle"
        self.turtle_counter_ = 1

    def publish_alive_turtles(self):
        msg = TurtleArray()
        msg.turtles = self.alive_turtles_
        self.alive_turtles_publisher_.publish(msg)

    def callback_catch_turtle(self,request:CatchTurtle.Request,response:CatchTurtle.Response):
        self.call_kill_service(request.name)
        response.success = True
        return response


    def spawn_new_turtle(self):
        self.turtle_counter_ += 1
        name = self.turtle_name_prefix + str(self.turtle_counter_)
        x = random.uniform(0.0, 11.0)
        y = random.uniform(0.0, 11.0)
        theta = random.uniform(0.0, 2 * math.pi)
        self.call_spawn_service(name, x, y, theta)
        


    def call_spawn_service(self,turtle_name, x, y, theta):
        while not self.spawn_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for spawn service to be available")

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        future = self.spawn_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_spawn_service, request=request))

    def callback_call_spawn_service(self,future,request):
        response:Spawn.Response = future.result()
        if response.name !="":
            self.get_logger().info(f"Spawned a turtle with name {response.name}")
            new_turtle = Turtle()
            new_turtle.name = response.name
            new_turtle.x = request.x
            new_turtle.y = request.y
            new_turtle.theta = request.theta
            self.alive_turtles_.append(new_turtle)
            self.publish_alive_turtles()
            
        else:
            self.get_logger().error("Failed to spawn turtle")


    def call_kill_service(self,turtle_name):
        while not self.kill_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for kill service to be available")

        request = Kill.Request()
        request.name = turtle_name

        future = self.kill_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_kill_service, turtle_name=turtle_name))

    def callback_call_kill_service(self,future,turtle_name):
        for(i,turtle) in enumerate(self.alive_turtles_):
            if turtle.name == turtle_name:
                del self.alive_turtles_[i]
                self.publish_alive_turtles()
                break

def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawnerNode() # MODIFY NAME
    #node.call_spawn_service(turtle_name="turtle2", x=1.0, y=1.0, theta=0.0)
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()