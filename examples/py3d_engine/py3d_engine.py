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


def get_orbit_projection(elev, azim, radius, center=[0, 0, 0], aspect=1., near=0.5, far=5.):
    relev, razim = np.pi * elev/180, np.pi * azim/180

    xp = center[0] + cos(razim) * cos(relev) * radius
    yp = center[1] + sin(razim) * cos(relev) * radius
    zp = center[2] + sin(relev) * radius
    eye = np.array((xp, yp, zp))

    if abs(relev) > pi / 2.:
        up = np.array((0, 0, -1))
    else:
        up = np.array((0, 0, 1))

    view_matrix = get_look_at_matrix(eye, center, up)
    projection_matrix = get_perspective_matrix(50, aspect, 0.5, 2 * radius)
    return np.dot(projection_matrix, view_matrix)
