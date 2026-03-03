import numpy as np
class CWEKF:

    def __init__(self, Phi, Gamma, params, RRAzelModel):
        self.x_hat = None
        self.RRAzelModel = RRAzelModel
        self.Phi = Phi
        self.Gamma = Gamma
        self.P = params.P0
        self.Q = params.Q_ekf
        self.R = params.R_ekf


    def step(self, z, u, meas_valid = True):
        x_minus, P_minus = self.predict(u)

        if not meas_valid:
            self.x_hat, self.P = x_minus, P_minus
            return

        H = np.array(self.RRAzelModel.update_H(x_minus)).astype(float)
        K = self.compute_gain(P_minus, H)
        self.update_estimate(x_minus, K, z)
        self.compute_covariance(P_minus, K, H)

        return self.x_hat


    def predict(self,u):
        if self.x_hat is None:
            raise ValueError("EKF state not initialized. Call init_state(state).")

        x = np.array(self.x_hat, dtype=float).reshape(6,)
        if u is None:
            u = np.zeros(3, dtype=float)
        else:
            u = np.array(u, dtype=float).reshape(3,)
        x_minus = self.Phi @ x + self.Gamma @ u
        P_minus = self.Phi @ self.P @ self.Phi.T + self.Q
        return x_minus, P_minus

    def compute_gain(self, P_minus, H):
        S = H @ P_minus @ H.T + self.R
        K = np.linalg.solve(S.T, (P_minus @ H.T).T).T
        return K
    

    def update_estimate(self, x_minus, K, z):

        y = z - np.array(self.RRAzelModel.h(x_minus)).reshape(4,)
        y[2] = self.wrap(y[2])
        y[3] = self.wrap(y[3])
        self.x_hat = x_minus + K @ y


    def compute_covariance(self, P_minus, K, H):
        I = np.eye(6)
        self.P = (I - K @ H) @ P_minus @ (I - K @ H).T + K @ self.R @ K.T

    def wrap(self, angle):
        return (angle + np.pi) % (2.0 * np.pi) - np.pi

    def init_state(self, state):
        self.x_hat = state