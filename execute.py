import numpy as np
import shutil
import socket
import cv2
import time

from dataclasses import dataclass
from pathlib import Path
from parsing import Recording, Parse
from obj_recognition import prepoznajObjekte
from kamera import request_capture

TIMEOUTCAMERA = 0

def clear_folder() -> None:

    folder = Path(IMG_PATH)

    if folder.iterdir():
        for item in folder.iterdir():
            shutil.rmtree(item)

def find_image(which:str = "image.png", timeout:int = 3) -> Path | None:

    search = Path(IMG_PATH)
    t0 = time.time()

    while time.time() - t0 < timeout:
        files_found = list(search.rglob(which))
        if files_found:
            return files_found[0]
        time.sleep(0.1)

    return None

def image_capture() -> None:
    clear_folder()
    print("Image capture requested")
    request_capture()
    time.sleep(5)

def listenANDparse(pickdrop:bool = True, options:str = " ") -> tuple[str, str] | int:

    waittime = 10 if pickdrop is True else 5

    stt = Recording(duration=waittime).speech_to_text()
    parsed = Parse(stt)

    if pickdrop:
        whattodo = parsed.extract()
        what = whattodo["pick"]
        where = whattodo["drop"]
        return what, where
    else:

        for word in parsed.words:

            if word == "zero" or word == "0" or word == "first":
                return 0
            elif word == "one" or word == "1" or word == "second":
                return 1
            elif word == "two" or word == "2" or word == "third":
                return 2
            elif word == "three" or word == "3" or word == "fourth":
                return 3
            elif word == "again":
                return 1
            elif word== "stop":
                return 0

            # More than 4 are most likely not fitting in the picture :)

        print("Valid option has not been recognized. Please input one of the correct options when prompted.")
        print("Options are: " + options)

        return listenANDparse(pickdrop=False, options=options)

@dataclass
class ObjectPicker:
    annotated_img:np.ndarray
    selections:dict

    @classmethod
    def from_recognition(cls):

        path = find_image()

        while path is None:
            path = find_image()

        selections, annotated_img = prepoznajObjekte(path.as_posix())

        return cls(annotated_img, selections)

    def dropping_coors(self, which:str) -> tuple:
        try:
            return self.selections[which][0]["center"]
        except KeyError:
            print(f"Dropping point: \"{which}\" was not recognized in the image")
            print("Recognized objects are shown on the image, to close it click on it and press enter.")
            
            cv2.imshow("anotated", self.annotated_img)
            cv2.waitKey(10000)
            cv2.destroyAllWindows()

            print("Now that you have seen the image, move the desired object appropriately in the frame of the picture.")
    
            input("When you are done press enter and the image will be captured again")

            image_capture()
            
            new_picker = ObjectPicker.from_recognition()
            
            return new_picker.dropping_coors(which)

    def picking_coors(self, which: str) -> tuple:

        global TIMEOUTCAMERA
        
        if TIMEOUTCAMERA == 2:
            print("Object was not found in 2 tries, I will just restart...")
            print()
            TIMEOUTCAMERA = 0
            return main(first=False)

        cnt_found = len(self.selections.get(which, []))

        if cnt_found == 0:
            print(f"Object '{which}' not found. Recapturing image...")
            print()
            image_capture()
            new_picker = ObjectPicker.from_recognition()
            TIMEOUTCAMERA += 1
            return new_picker.picking_coors(which) 

        if cnt_found == 1:
            TIMEOUTCAMERA = 0
            return self.selections[which][0]['center']

        else:
            print()
            print(f"I found {cnt_found} of the same fruit you picked on floor. Which one do you want me to pick up?")
            print("Options: first/second/... (from the top left edge of the image)")
            print()
            print("Now please check the picture (it will close after 5 s)")

            time.sleep(3)

            cv2.imshow("anotated", self.annotated_img)
            cv2.waitKey(5000)
            cv2.destroyAllWindows()
            
            print("Now please choose your selection via voice (when prompted).")
  
            opts = list(range(cnt_found))
            vnos = listenANDparse(pickdrop=False, options=''.join(" "+str(x) for x in opts))

            origin = np.array([0.0, 0.0])
            coms = [np.array(self.selections[which][i]["center"]) for i in range(cnt_found)]
            dists = np.argsort([np.linalg.norm(com - origin) for com in coms])

            chosen = dists[0] if vnos == 0 else dists[vnos]
            TIMEOUTCAMERA = 0

            return self.selections[which][chosen]['center']

@dataclass
class Coordinates:
    pick: tuple
    drop: tuple

    def format_coors(self, action:str, conversion:float = 0.3255, H_path:np.ndarray="H_new.csv") -> str:

        coors = self.pick if action == "pick" else self.drop

        coors_xyz = list(coors) + [0, 1]
        H = np.loadtxt(H_path, delimiter=",")

        # Convert coordinates in px to mm
        coors_xyz_mm = [x * conversion for x in coors_xyz]
        coors_xyz_mm[-1] = 1
        final_coors = H @ np.array(coors_xyz_mm)

        poslji = list(final_coors)[:-1]
        
        if which == "red apple":
            zoffs = 55
        elif which == "green apple":
            zoffs = 48
        else:
            zoffs = 47

        if whereto == "cup" and action == "drop":
            zoffs = 160

        poslji[-1] = zoffs 
        poslji1 = [float(el) for el in poslji]

        return str(poslji1)

def robot_response(raw_data) -> int:

    if "ERROR" in raw_data:
        print(f"!!! {raw_data}")
        return 0

    elif raw_data == "OK":
        return 1

    elif raw_data == "DROP":
        print()
        print("Robot requests drop position; drop coordinates from the command will be automatically forwarded.")
        cmd = COORS.format_coors(action="drop")
        SOCK.send(cmd.encode())
        return 0

    else:
        print(f"Unexpected response: {raw_data}")
        return 1

def init() -> bool:
    """Set up communication with the robot and clear the folder with the images"""

    global IMG_PATH, SOCK 

    IMG_PATH = r"camera_images"

    clear_folder()

    ROBOT_IP = "192.168.125.1"
    PORT = 5000
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SOCK.connect((ROBOT_IP, PORT))

    read = SOCK.recv(1024).decode()

    if read == "ACK":
        print()
        print("Connection acknowledged by robot")
        return True

    return False

def main(first:bool = True) -> None:

    global COORS, which, whereto

    if first:
        start = False
        while not start:
            start = init()

    image_capture()

    picker = ObjectPicker.from_recognition()

    print("Here is the captured image with the recognized objects: ")
    cv2.imshow("anotated", picker.annotated_img)
    cv2.waitKey(5000)
    cv2.destroyAllWindows() 

    if "cup" not in list(picker.selections.keys()) and "box" not in list(picker.selections.keys()):
        print("No drop object detected in the image...")
        print("You have 10s to rearrange the object in the FOV, then i will restart.")
        time.sleep(10)
        return main(first=False)

    which, whereto = listenANDparse()

    pick_coors = picker.picking_coors(which)
    release_coors = picker.dropping_coors(whereto)

    if pick_coors is not None and release_coors is not None:
        COORS = Coordinates(pick_coors, release_coors)
    else:
        return

    SOCK.send(
        COORS.format_coors(action="pick").encode()
    )

    try:
        while True:

            raw_data = SOCK.recv(1024).decode()
            response = robot_response(raw_data)

            if response == 0:
                break

    finally:
        print("Task performed.")

if __name__ == '__main__':

    first = True

    while True:

        main(first=first)
        print("Please wait for the robot to stop moving.")
        print()
        time.sleep(10) 

        print("You will shortly be asked if you want to stop or perform another task")
        print("Options are: STOP/AGAIN")
        
        vnos = listenANDparse(pickdrop=False, options="STOP/AGAIN")
        
        if vnos == 1:
            first = False
        else:
            SOCK.close()
            print()
            print("Closing connection now.")
            break

