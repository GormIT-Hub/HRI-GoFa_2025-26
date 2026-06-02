# RoboFructus
GoFa robot project for the HRI course in the 2025/26 academic year - Monday group.

## Requirements

1. Create a new Python virual environment
2. Activate the environment
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

These steps are only required if you are not running the program on a computer in the Laboratory for Robotics. On the laboratory computer, all required dependencies are already installed in the project's virtual environment (D:\VAJE\HRI\2526\Monday\fruityBrat\).

## Running the program

### 1. Set up the robot side
1. Activate the camera server by opening a web browser and navigating to the camera server at `192.168.65.207`.
2. Start RobotStudio.
3. Import the modules from the modulesRobotStudio/ directory.

### 2. Set up the Python side
1. Activate the Python virtual environment.
2. Run `ftp_server.py` script to enable image acquisiton
3. Open a separate terminal window and run `execute.py` to start the program.


