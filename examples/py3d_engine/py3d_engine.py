import numpy as np
from math import pi, cos, sin, tan


def pad_ones(x, y, z):
    return np.array([x, y, z, np.ones_like(x)])


def normalize(vec):
    return vec / np.linalg.norm(vec)


def project_vector(x, y, z, matrix):
    vec = np.dot(matrix, pad_ones(x, y, z))

    return vec[0]/vec[3], vec[1]/vec[3], vec[2]/vec[3]


def get_look_at_matrix(eye, center, up):
    n = normalize(eye - center)
    u = normalize(np.cross(up, n))
    v = np.cross(n, u)

    matrix_r = [[u[0], u[1], u[2], 0],
                [v[0], v[1], v[2], 0],
                [n[0], n[1], n[2], 0],
                [0,    0,    0,    1]]

    matrix_t = [[1, 0, 0, -eye[0]],
                [0, 1, 0, -eye[1]],
                [0, 0, 1, -eye[2]],
                [0, 0, 0, 1]]

    return np.dot(matrix_r, matrix_t)


def get_perspective_matrix(fovy, aspect, near, far):
    f = 1. / tan(fovy * pi / 360.)

    return np.array([
        [f/aspect, 0,                           0,                           0],
        [       0, f,                           0,                           0],
        [       0, 0,   (near + far)/(near - far), 2 * near * far/(near - far)],
        [       0, 0,                          -1,                           0]
    ])


class OrbitCamera():

    def __init__(self, radius, center, aspect, near=0, far=8):
        self.radius = radius
        self.center = np.array(center)
        self.aspect = aspect
        self.near = near
        self.far = far

        self.update_position(0, 0)

    def update_position(self, elev, azim):
        self.elev = elev
        self.azim = azim

        relev, razim = np.pi * self.elev/180, np.pi * self.azim/180

        xp = self.center[0] + cos(razim) * cos(relev) * self.radius
        yp = self.center[1] + sin(razim) * cos(relev) * self.radius
        zp = self.center[2] + sin(relev) * self.radius

        self.position = np.array((xp, yp, zp))
        self.front = self.center - self.position

        if abs(relev) > pi / 2.:
            self.up = np.array((0, 0, -1))
        else:
            self.up = np.array((0, 0, 1))

        self.update_matrix()

    def update_matrix(self):
        self.view_matrix = get_look_at_matrix(self.position, self.center, self.up)
        self.projection_matrix = get_perspective_matrix(50, self.aspect, self.near, self.far)
        self.matrix = np.dot(self.projection_matrix, self.view_matrix)
