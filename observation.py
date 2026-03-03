import numpy as np

class Observation:
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine
        self.z = None

    def update_meas(self):
        z = [
            self.engine.getExpressionVariable(self.name + ".Range.ObservedValue"),
            self.engine.getExpressionVariable(self.name + ".RangeRate.ObservedValue"),
            self.engine.getExpressionVariable(self.name + ".Azimuth.ObservedValue"),
            self.engine.getExpressionVariable(self.name + ".Elevation.ObservedValue")
        ]
        self.z = np.array(z, dtype=float)

    def get_meas(self, refresh=True):
        if refresh or self.z is None:
            self.update_meas()
        return self.z
