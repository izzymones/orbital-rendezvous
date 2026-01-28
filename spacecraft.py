import numpy as np
import casadi as ca


class Spacecraft:
    def __init__(self, name, engine):
        self.name = name
        self.epoch_days = None
        self.r = None
        self.v = None
        self.a = None
        self.e = None
        self.i = None
        self.RAAN = None
        self.ArgOfPeri = None
        self.trueAnomaly = None
        self.engine = engine


    def update_cartesian(self):
        r = [
            self.engine.getExpressionVariable(self.name + ".Position[0]"),
            self.engine.getExpressionVariable(self.name + ".Position[1]"),
            self.engine.getExpressionVariable(self.name + ".Position[2]"),
        ]
        v = [
            self.engine.getExpressionVariable(self.name + ".Velocity[0]"),
            self.engine.getExpressionVariable(self.name + ".Velocity[1]"),
            self.engine.getExpressionVariable(self.name + ".Velocity[2]"),
        ]
        self.r = np.array(r, dtype=float)
        self.v = np.array(v, dtype=float)


    def set_cartesian(self, r, v):
        self.engine.setExpressionArray(self.name + ".Position", r)
        self.engine.setExpressionArray(self.name + ".Velocity", v)


    def get_cartesian(self, refresh=True):
        if refresh or self.r is None or self.v is None:
            self.update_cartesian()
        return self.r, self.v
    

    def set_epoch(self, epoch):
        self.engine.setExpressionTimeSpan(self.name + ".Epoch", epoch)


    def get_epoch(self):
        return self.engine.getExpressionTimeSpan(self.name + ".Epoch")
    

    def get_epoch_days(self):
        return self.engine.getExpressionTimeSpan(self.name + ".Epoch").getValueAsDays()
    

    def update_epoch(self):
        self.epoch_days = self.engine.getExpressionTimeSpan(self.name + ".Epoch").getValueAsDays()


    def print_cartesian(self, refresh=True):
        self.get_cartesian(refresh=refresh)
        print(self.name +" ICRF State:")
        print("Position: ")
        print(self.r)
        print("Velocity: ")
        print(self.v)
        print("\n")


    def rv_to_coe(self):
        pass


    def set_keplerian(self, kep):
        self.engine.setExpressionVariable(self.name + ".A", kep[0])
        self.engine.setExpressionVariable(self.name + ".E", kep[1])
        self.engine.setExpressionVariable(self.name + ".I", kep[2])
        self.engine.setExpressionVariable(self.name + ".RAAN", kep[3])
        self.engine.setExpressionVariable(self.name + ".W", kep[4])
        self.engine.setExpressionVariable(self.name + ".TA", kep[5])



    def get_keplerian(self):
        pass


    def print_keplerian(self):
        pass


    # rewrite
    def eci_relative_to_lvlh(self, chief, refresh=True):
        """
        Returns x_rel = [r_LVLH; v_LVLH] as a 6x1 CasADi DM.
        LVLH is built from the CHIEF (origin + frame).
        """
        r_d, v_d = self.get_cartesian(refresh=refresh)
        r_c, v_c = chief.get_cartesian(refresh=refresh)

        r_d = np.asarray(r_d, dtype=float).reshape(3,)
        v_d = np.asarray(v_d, dtype=float).reshape(3,)
        r_c = np.asarray(r_c, dtype=float).reshape(3,)
        v_c = np.asarray(v_c, dtype=float).reshape(3,)

        xhat = r_c / np.linalg.norm(r_c)
        h = np.cross(r_c, v_c)
        zhat = h / np.linalg.norm(h)
        yhat = np.cross(zhat, xhat)

        C_I2L = np.vstack((xhat, yhat, zhat))

        dr = r_d - r_c
        dv = v_d - v_c

        omega = np.cross(r_c, v_c) / (np.linalg.norm(r_c) ** 2)
        r_L = C_I2L @ dr
        v_L = C_I2L @ (dv - np.cross(omega, dr))

        x_rel = np.hstack((r_L, v_L)).reshape(6, 1)
        return ca.DM(x_rel)
    
    
    def print_relative(self, chief):
        print(self.eci_relative_to_lvlh(chief))

    

    def CW_to_FF(self, v_cw):
        v_ff = [v_cw[1],-v_cw[2],-v_cw[0]]
        return v_ff



    def lvlh_basis(self, chief):
        pass

    
    def set_burn(self, burn):
        if isinstance(burn, (ca.DM, ca.MX)):
            burn_list = np.array(ca.DM(burn)).astype(float).reshape(-1).tolist()
        else:
            burn_list = np.array(burn, dtype=float).reshape(-1).tolist()

        if len(burn_list) != 3:
            raise ValueError(f"BurnDirection must have length 3, got {len(burn_list)}: {burn_list}")
        self.engine.setExpressionArray("ImpulsiveBurn1.BurnDirection", burn_list)