# RoboFructus
GoFa robot project for the HRI course in the 2025/26 academic year - Monday group.

## Requirements

1. Create a new Python virtual environment
2. Activate the environment
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

These steps are only required if you are not running the program on a computer in the Laboratory for Robotics (RoboLab). On the laboratory computer, all required dependencies are already installed in the project's virtual environment (`D:\VAJE\HRI\2526\Monday\fruityBrat\`).

## Network Configuration

Before running the program, make sure that the PC, ABB GoFa controller and SICK camera are connected to the same network.

The current setup uses the following IP addresses:

* SICK camera: `192.168.65.207`
* FTP server on the PC: `192.168.65.42:2121`
* ABB controller: `192.168.125.1`
* Robot socket port: `5000`

If the system is moved to a different network, these IP addresses must be updated in the corresponding Python and RAPID files.

## Running the Program

### 1. Set Up the Robot Side

1. Start RobotStudio.
2. Connect to the ABB GoFa controller.
3. Import the RAPID modules from the `modulesRobotStudio/` directory:

   * `Socket_Communication.modx` → RAPID → `Communication`
   * `MainModule.modx` → RAPID → `T_ROB1`

---

### 2. Set Up the Camera

1. Open a web browser and navigate to the camera server at `192.168.65.207`.

   * If running locally in RoboLab, Job **312** already contains all required presets.
2. Run `ftp_server.py` to enable image acquisition.
3. Verify that the connection to the SICK camera is working correctly.

---

### 3. Set Up the Python Side and Run the System

1. Activate the Python virtual environment.
2. Start `MainModule.modx` on the ABB controller.
3. Open a separate terminal window and run:

```bash
python execute.py
```

4. Follow the voice prompts and enjoy :)
