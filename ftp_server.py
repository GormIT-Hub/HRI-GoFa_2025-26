from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

# server ip = 192.168.65.42:2121

def run_ftp():

    authorizer = DummyAuthorizer()
    if not os.path.exists('./camera_images'): os.makedirs('./camera_images')

    # set user: "sick", password: "password" and full permissions
    authorizer.add_user("ftp_server", "ftp_server", "./camera_images", perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", 2121), handler)
    print("FTP Server is running on port 2121")
    server.serve_forever()

if __name__ == "__main__":
    """Script that launches the FTP server which has to be running in the background so that image acquisition can be possible"""
    run_ftp()
