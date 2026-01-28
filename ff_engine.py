import sys
from pathlib import Path

file_path = Path(__file__).resolve()
python_rtapi_src_path = file_path.parent / "ff_rtapi_src"
sys.path.insert(0, str(python_rtapi_src_path))

try:
    from aisolutions.freeflyer.runtimeapi.RuntimeApiEngine import RuntimeApiEngine
    from aisolutions.freeflyer.runtimeapi.RuntimeApiEngine import FFTimeSpan
    from aisolutions.freeflyer.runtimeapi.ConsoleOutputProcessingMethod import ConsoleOutputProcessingMethod
    from aisolutions.freeflyer.runtimeapi.WindowedOutputMode import WindowedOutputMode
    from aisolutions.freeflyer.runtimeapi.RuntimeApiException import RuntimeApiException
except ImportError:
    print("Import error!")

class FreeFlyerEngine:
    def __init__(self, install_dir):
        self.ff_install_dir = install_dir

    def __enter__(self):
        self.engine = RuntimeApiEngine(
            self.ff_install_dir,
            consoleOutputProcessingMethod=ConsoleOutputProcessingMethod.RedirectToRuntimeApi,
            windowedOutputMode=WindowedOutputMode.GenerateOutputWindows
        )
        return self.engine

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.engine is not None:
                self.engine.cleanupMissionPlan()
        except Exception:
            pass
        self.engine = None
        return False