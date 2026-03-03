import casadi as ca

class RRAzelModel:
    def __init__(self):
        x = ca.SX.sym('x', 6)
        r_cw = x[0:3]
        v_cw = x[3:6]

        P = ca.SX([[0,  1,  0],
                   [0,  0, -1],
                   [-1, 0,  0]])

        r = P @ r_cw
        v = P @ v_cw

        rx, ry, rz = r[0], r[1], r[2]

        rho = ca.sqrt(rx**2 + ry**2 + rz**2)
        rho_safe = ca.if_else(rho > 1e-12, rho, 1e-12)

        rho_dot = (r.T @ v) / rho_safe

        az = ca.atan2(ry, rx)

        s = ca.sqrt(rx**2 + ry**2)
        s_safe = ca.if_else(s > 1e-12, s, 1e-12)
        el = ca.atan2(rz, s_safe)

        h = ca.vertcat(rho, rho_dot, az, el)
        H = ca.jacobian(h, x)

        self.h = ca.Function('h', [x], [h])
        self.update_H = ca.Function('H', [x], [H])