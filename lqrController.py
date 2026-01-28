import numpy as np
import casadi as ca
import scipy.linalg as la

from CW_Model import CWModel

from constants import Constants
mc = Constants()

class LQRController:
    def __init__(self):
        self.cw = CWModel(mc)
        self.K = None

    def get_AB(self):
        A_sx = ca.jacobian(self.cw.dynamics, self.cw.state)
        B_sx = ca.jacobian(self.cw.dynamics, self.cw.control)

        A_fun = ca.Function('A_fun', [self.cw.state, self.cw.control], [A_sx])
        B_fun = ca.Function('B_fun', [self.cw.state, self.cw.control], [B_sx])
        A = np.array(A_fun(mc.xr, mc.ur), dtype=float)
        B = np.array(B_fun(mc.xr, mc.ur), dtype=float)
        return A, B

    def compute_K(self):
        [A, B] = self.get_AB()
        P = la.solve_continuous_are(A, B, mc.Q, mc.R)
        self.K = np.linalg.inv(mc.R) @ (B.T @ P)
    
    def control_law(self, state):
        x_res = state - mc.xr
        if self.K is None:
            self.compute_K()
        return -self.K @ x_res
    