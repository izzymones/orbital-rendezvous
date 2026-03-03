import numpy as np
import casadi as ca

from ff_engine import FFTimeSpan

class Constants:
    def __init__(self):
        self.mu = 398600.4418
        self.r = 6378.0
        self.h = 400.0
        self.a = self.h + self.r
        self.n = (self.mu/(self.a**3))**0.5

        self.dt = 30.0

        # self.chiefSC_keplerian = np.array([self.a, 0, 0, 0, 0, 0])
        # self.deputySC_keplerian = np.array([self.a + 67.5, 0.05, 1, 1, 1, 1])

        self.chiefSC_keplerian = np.array([self.a, 0, 0, 0, 0, 0])
        self.deputySC_keplerian = np.array([self.a+100, 0, 0, 0, 0, 0])

        self.max_days = 1 / 24
        self.mission_plan_path = r"C:\Users\izzym\Documents\FreeFlyer\Phase0.MissionPlan"

        self.ff_install_dir = r"C:\Program Files\a.i. solutions, Inc\FreeFlyer 7.10.0.43083514 (64-Bit)"
        
        self.chiefSC_Name = "chiefSC"
        self.deputySC_Name = "deputySC"
        self.obsv_Name = "Obs1"

        self.xr = ca.vertcat(0.0,0.0,0.0,0.0,0.0,0.0)
        self.ur = ca.vertcat(0.0,0.0,0.0)

        self.P0 = np.array([
            [1.0e-2, 0.0,    0.0,    0.0,    0.0,    0.0],
            [0.0,    1.0e-2, 0.0,    0.0,    0.0,    0.0],
            [0.0,    0.0,    1.0e-2, 0.0,    0.0,    0.0],
            [0.0,    0.0,    0.0,    1.0e-8, 0.0,    0.0],
            [0.0,    0.0,    0.0,    0.0,    1.0e-8, 0.0],
            [0.0,    0.0,    0.0,    0.0,    0.0,    1.0e-8]
        ])

        self.Q_ekf = np.diag([
            1e-8, 1e-8, 1e-8,
            1e-12, 1e-12, 1e-12
        ])

        self.R_ekf = np.array([
            [2.5e-3, 0.0,     0.0,     0.0],
            [0.0,    2.5e-9,  0.0,     0.0],
            [0.0,    0.0,     4.0e-6,  0.0],
            [0.0,    0.0,     0.0,     4.0e-6]
        ])

        self.Q = ca.diag([1,1,1,100000,100000,100000])
        self.R = ca.diag([1e10, 1e10, 1e10])
        self.terminal_cost_factor = 0




