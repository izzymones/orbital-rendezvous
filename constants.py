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

        self.chiefSC_position = np.array([-1500.90777805625, 6858.56290468965, 1080.92254153641])
        self.chiefSC_velocity = np.array([0.835109399282293, 1.32674441436118, -7.33600093128616])
        self.deputySC_position = np.array([-1400.90777805625, 6858.56290468965, 1080.92254153641])
        self.deputySC_velocity = np.array([0.835109399282293, 1.32674441436118, -7.33600093128616])

        self.chiefSC_keplerian = np.array([self.a, 0, 0, 0, 0, 0])
        self.deputySC_keplerian = np.array([self.a + 67.5, 0.05, 1, 1, 1, 1])

        self.max_days = 1 / 24
        self.mission_plan_path = r"C:\Mac\Home\Documents\FreeFlyer\FreeFlyer 7.10.0.43083514 (64-Bit)\Phase0.MissionPlan"

        self.ff_install_dir = r"C:\Program Files\a.i. solutions, Inc\FreeFlyer 7.10.0.43083514 (64-Bit)"
        
        self.chiefSC_Name = "chiefSC"
        self.deputySC_Name = "deputySC"

        self.xr = ca.vertcat(0.0,0.0,0.0,0.0,0.0,0.0)
        self.ur = ca.vertcat(0.0,0.0,0.0)

        self.Q = ca.diag([1,1,1,100000,100000,100000])
        self.R = ca.diag([100, 100, 100])

        self.terminal_cost_factor = 0




