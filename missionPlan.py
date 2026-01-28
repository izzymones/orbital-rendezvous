import traceback
import numpy as np
import warnings
warnings.filterwarnings("ignore", module="do_mpc")

from constants import Constants
from spacecraft import Spacecraft
from lqrController import LQRController


from ff_engine import FreeFlyerEngine, RuntimeApiException

mc = Constants()

class MissionPlan:
    def __init__(self):
        pass

    def create_and_run_engine(self):
        try:
            with FreeFlyerEngine(mc.ff_install_dir) as engine:
                self.initialize_mission(engine)

                chiefSC = Spacecraft(mc.chiefSC_Name, engine)
                deputySC = Spacecraft(mc.deputySC_Name, engine)

                lqr = LQRController()
                lqr.compute_K()

                start_day = chiefSC.get_epoch_days()


                print("Run to the 'Set state' label.")
                engine.executeUntilApiLabel("Set state")

                print("Set in the initial state.")
                chiefSC.set_keplerian(mc.chiefSC_keplerian.tolist())
                deputySC.set_keplerian(mc.deputySC_keplerian.tolist())

                # chiefSC.set_cartesian(mc.chiefSC_position.tolist(), mc.chiefSC_velocity.tolist())
                # deputySC.set_cartesian(mc.deputySC_position.tolist(), mc.deputySC_velocity.tolist())

                deputySC.set_epoch(chiefSC.get_epoch())
                
                while True:
                    engine.executeUntilApiLabel("break")
                    current_day = chiefSC.get_epoch_days()

                    if (current_day - start_day) >= mc.max_days:
                        print("Stopping loop.")
                        break
                    
                    state = deputySC.eci_relative_to_lvlh(chiefSC)

                    burn = lqr.control_law(state)
                    print(state, burn / 30)
                    deputySC.set_burn(deputySC.CW_to_FF(burn / 30))


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
        engine.loadMissionPlanFromFile(mc.mission_plan_path)

        print("Prepare to execute statements.")
        engine.prepareMissionPlan()

if __name__ == '__main__':
    mission = MissionPlan()
    mission.create_and_run_engine()
