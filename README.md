# ROS 2 Turtlesim - Catch Them All

A 2D autonomous target pursuit simulation built with ROS 2. This project demonstrates core robotic middleware concepts including custom message/service interfaces, publisher/subscriber nodes, and basic kinematics for autonomous navigation.

## Features
* **Custom ROS 2 Interfaces:** Utilizes custom `.msg` (TurtleArray) and `.srv` (CatchTurtle) definitions for structured inter-node communication.
* **Autonomous Navigation:** The hunter turtle implements a Proportional (P) Controller to calculate Euclidean distances, dynamically adjust its heading ($\theta$), and pursue the closest active target.
* **Dynamic Spawning System:** A dedicated spawner node acts as a Game Master, generating targets at random coordinates, maintaining an active target array, and handling kill requests.
* **Asynchronous Service Calls:** Employs async clients to spawn new entities and remove caught targets without blocking the control loop.

## Node Architecture
1.  **`turtlesim_node`**: The core 2D physics and rendering environment.
2.  **`turtle_spawner`**:
    * Calls `/spawn` to generate new turtles randomly.
    * Publishes the active list to `/alive_turtles`.
    * Provides the `/catch_turtle` service to remove turtles using the `/kill` service.
3.  **`turtle_controller`**:
    * Subscribes to `/alive_turtles` to find the closest target.
    * Calculates necessary angular and linear velocities.
    * Publishes to `turtle1/cmd_vel` to drive the hunter.

## 🏗️ Project Structure
* **`turtlesim_catch_them_all`**: Core Python package containing logic nodes.
* **`my_robot_interfaces`**: Custom CMake package for MSG and SRV definitions.
* **`turtlesim_bringup`**: Launch package to start the entire simulation with a single command.

## 🛠️ Prerequisites
* Ubuntu (22.04 or 24.04)
* ROS 2 (Humble or Jazzy)
* Python 3.10+

## ⚙️ Installation & Build
```bash
# Navigate to your ROS 2 workspace
cd ~/ros2_ws/src

# Clone the repository
git clone [https://github.com/oguzzmeric/ros2-turtlesim-catch-turtles.git](https://github.com/oguzzmeric/ros2-turtlesim-catch-turtles.git)

# Build the packages
cd ~/ros2_ws
colcon build --packages-select my_robot_interfaces turtlesim_catch_them_all turtlesim_bringup

# Source the workspace
source install/setup.bash
