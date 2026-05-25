import numpy as np

def get_H(coors:list[list]):

    A, B, C = np.array(coors[0]), np.array(coors[1]), np.array(coors[2])

    x = (C - B) / np.linalg.norm(C - B)
    tmp = (A - B) / np.linalg.norm(A - B)

    z = np.cross(x, tmp) 
    z /= np.linalg.norm(z)

    y = np.cross(z, x) 
    y /= np.linalg.norm(y)

    t = B

    R = np.zeros((3,3))
    R[:, 0] = x
    R[:, 1] = y
    R[:, 2] = z

    H = np.zeros((4,4))
    H[:3, :3] = R
    H[:3, 3] = t
    H[-1, -1] = 1

    return H
    
if __name__ == '__main__':
    
    """Script that calculates the matrix (H) for transformation from pixels to mm, to which the robot can then move"""
    
    kamera = [
        [710.8, 177.2, 0],
        [245.2, 595.4, 0],
        [1020.7, 763.3, 0]
    ]

    robot = [
        [506.9, -46.1, 60.7], 
        [624.8, -170.5, 67.85], 
        [662.0, 40.7, 55.3] 
    ]

    dist1 = np.linalg.norm(np.array(kamera[0])[:-1] - np.array(kamera[1])[:-1])
    dist2 = np.linalg.norm(np.array(robot[0])[:-1] - np.array(robot[1])[:-1])

    print(f"{dist1=}")
    print(f"{dist2=}")

    conversion = dist2 / dist1 # mm / px

    print(f"{conversion=}")

    for l in kamera:
        for i in range(len(l)):
            l[i] *= conversion

    H_kamera = get_H(kamera)
    print(f"{H_kamera=}")
    H_robot = get_H(robot)
    print(f"{H_robot=}")

    H = H_robot @ np.linalg.inv(H_kamera)

    np.savetxt('H1.csv', H, delimiter=',')

    print(f'{H=}')


