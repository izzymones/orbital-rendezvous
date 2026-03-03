import numpy as np
import casadi as ca
import scipy.linalg as la

class LQRController:
    def __init__(self, params, cw):
        self.p = params
        self.cw = cw
        self.K = None

    def get_AB(self):
        A_sx = ca.jacobian(self.cw.dynamics, self.cw.state)
        B_sx = ca.jacobian(self.cw.dynamics, self.cw.control)

        A_fun = ca.Function('A_fun', [self.cw.state, self.cw.control], [A_sx])
        B_fun = ca.Function('B_fun', [self.cw.state, self.cw.control], [B_sx])
        A = np.array(A_fun(self.p.xr, self.p.ur), dtype=float)
        B = np.array(B_fun(self.p.xr, self.p.ur), dtype=float)
        return A, B
    
    def get_AB_discrete(self, dt=None):
        if dt is None:
            dt = self.p.dt

        A, B = self.get_AB()
        nx = A.shape[0]
        nu = B.shape[1]

        M = np.zeros((nx + nu, nx + nu))
        M[:nx, :nx] = A
        M[:nx, nx:] = B

        Md = la.expm(M * dt)

        Ad = Md[:nx, :nx]
        Bd = Md[:nx, nx:]

        return Ad, Bd


    def compute_K(self):
        [A, B] = self.get_AB()
        P = la.solve_continuous_are(A, B, self.p.Q, self.p.R)
        self.K = np.linalg.inv(self.p.R) @ (B.T @ P)


    def compute_K_discrete(self, dt):
        Ad, Bd = self.get_AB_discrete(dt)

        P = la.solve_discrete_are(Ad, Bd, self.p.Q, self.p.R)

        S = Bd.T @ P @ Bd + self.p.R
        self.K = np.linalg.solve(S, Bd.T @ P @ Ad)

        return self.K
    

    def control_law(self, state):
        x_res = state - self.p.xr
        if self.K is None:
            self.compute_K()
        u = -self.K @ x_res
        return u
    