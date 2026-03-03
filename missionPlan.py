import traceback
import numpy as np
import warnings
warnings.filterwarnings("ignore", module="do_mpc")

from constants import Constants
from spacecraft import Spacecraft
from observation import Observation
from lqrController import LQRController
from CW_Model import CWModel
from ekf import CWEKF
from est_model import RRAzelModel
from ff_engine import FreeFlyerEngine, RuntimeApiException

params = Constants()

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


                print("Run to the 'Set state' label.")
                engine.executeUntilApiLabel("Set state")

                print("Set in the initial state.")
                chiefSC.set_keplerian(params.chiefSC_keplerian.tolist())
                deputySC.set_keplerian(params.deputySC_keplerian.tolist())

                true_state = deputySC.eci_relative_to_lvlh(chiefSC)
                print("og_true_staet: ", true_state)
                ekf.init_state(true_state)


                deputySC.set_epoch(chiefSC.get_epoch())
                
                burn = np.zeros(3, dtype=float)

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
                    print("true: ", true_state)
                    print("ekf: ", state)
                    # print(state, burn / params.dt)
                    deputySC.set_burn(deputySC.CW_to_FF(burn * params.dt))


                chiefSC.print_cartesian()
                deputySC.print_cartesian()
                deputySC.print_relative(chiefSC)


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
