import traceback
import numpy as np
import warnings
warnings.filterwarnings("ignore", module="do_mpc")

import matplotlib.pyplot as plt

from constants import Constants
from spacecraft import Spacecraft
from observation import Observation
from lqrController import LQRController
from CW_Model import CWModel
from ekf import CWEKF
from est_model import RRAzelModel
from ff_engine import FreeFlyerEngine, RuntimeApiException

params = Constants()

STATE_IDX = 0
STATE_LABEL = "x (m)"

class MissionPlan:
    def __init__(self):
        pass

    def create_and_run_engine(self):
        try:
            with FreeFlyerEngine(params.ff_install_dir) as engine:
                self.initialize_mission(engine)

                chiefSC = Spacecraft(params.chiefSC_Name, engine)
                deputySC = Spacecraft(params.deputySC_Name, engine)
                obsv = Observation(params.obsv_Name, engine)

                cw = CWModel(params)

                lqr = LQRController(params, cw)
                lqr.compute_K()
                Phi, Gamma = lqr.get_AB_discrete(params.dt)

                rrazel_model = RRAzelModel()
                ekf = CWEKF(Phi, Gamma, params, rrazel_model)

                start_day = chiefSC.get_epoch_days()

                t_log = []
                true_log = []
                ekf_log = []

                print("Run to the 'Set state' label.")
                engine.executeUntilApiLabel("Set state")

                print("Set in the initial state.")
                chiefSC.set_keplerian(params.chiefSC_keplerian.tolist())
                deputySC.set_keplerian(params.deputySC_keplerian.tolist())

                true_state = deputySC.eci_relative_to_lvlh(chiefSC)
                print("True State: ", true_state)
                ekf.init_state(true_state + np.array([10, 0, 0, 0, 0, 0]))

                deputySC.set_epoch(chiefSC.get_epoch())

                burn = np.zeros(3, dtype=float)
                step_k = 0

                while True:
                    engine.executeUntilApiLabel("break")

                    current_day = chiefSC.get_epoch_days()
                    if (current_day - start_day) >= params.max_days:
                        print("Stopping loop.")
                        break

                    true_state = deputySC.eci_relative_to_lvlh(chiefSC)
                    measurement = obsv.get_meas()
                    state = ekf.step(measurement, burn)

                    burn = lqr.control_law(state)

                    t_log.append(step_k * params.dt)
                    true_log.append(float(true_state[STATE_IDX]))
                    ekf_log.append(float(state[STATE_IDX]))
                    step_k += 1

                    deputySC.set_burn(deputySC.CW_to_FF(burn * params.dt))

                chiefSC.print_cartesian()
                deputySC.print_cartesian()
                deputySC.print_relative(chiefSC)

                if len(t_log) > 1:
                    plt.figure()
                    plt.plot(t_log, true_log, label="True")
                    plt.plot(t_log, ekf_log, label="EKF")
                    plt.xlabel("Time (s)")
                    plt.ylabel(STATE_LABEL)
                    plt.title(f"EKF vs True ({STATE_LABEL})")
                    plt.legend()
                    plt.tight_layout()
                    plt.show()

        except RuntimeApiException as exp:
            print("RuntimeApiException:", getattr(exp, "message", str(exp)))
            traceback.print_exc()
        except Exception:
            print("Unhandled exception:")
            traceback.print_exc()

    def initialize_mission(self, engine):
        print("Load the Mission Plan.")
        engine.loadMissionPlanFromFile(params.mission_plan_path)

        print("Prepare to execute statements.")
        engine.prepareMissionPlan()

if __name__ == '__main__':
    mission = MissionPlan()
    mission.create_and_run_engine()