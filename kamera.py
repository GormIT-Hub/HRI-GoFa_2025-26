import socket

def request_capture(camera_ip="192.168.65.207"):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    try:
        s.connect((camera_ip, 14158))
        print()
        print("Connection with the camera established!")
    except:
        print()
        print("Couldnt find connection, ending after 5s...")
        return

    cmd = b'\x02Run.Locate,312\x03'

    s.sendall(cmd)
    #response = s.recv(4096)

    print("Camera triggered!")

if __name__ == "__main__":
    request_capture()
