"""Application controller and state bridge for GUI."""

from pathlib import Path
from typing import Callable

from yazilim_lab_project.gui.logger import log_command_execution, log_gui_action
from yazilim_lab_project.interface.engine import Engine
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import AnyCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models import AnyResult


class AppController:
    """Bridges GUI actions directly to Engine without violating GEMINI.md patterns."""

    def __init__(self, initial_data_path: Path | None = None) -> None:
        self.state: AppState | None = None
        self.engine: Engine | None = None
        self._listeners: list[Callable[[], None]] = []
        if initial_data_path is not None and initial_data_path.exists():
            self.load_initial_data(initial_data_path)

    def subscribe(self, callback: Callable[[], None]) -> None:
        """Register a callback to be notified on any state change."""
        self._listeners.append(callback)

    def notify(self) -> None:
        """Notify all listeners that the system state has updated."""
        for cb in self._listeners:
            try:
                cb()
            except Exception as e:
                print(f"Error in state listener: {e}")

    def load_initial_data(self, path: Path) -> None:
        """Initialize fresh AppState and Engine from a JSON file."""
        log_gui_action("load_initial_data", path=str(path))
        try:
            config = InitialData.model_validate_json(path.read_text(encoding="utf-8"))
            self.state = AppState(config=config)
            self.engine = Engine(self.state)
            self.notify()
            log_gui_action("initial_data_loaded_successfully", resources=len(self.state.config.resources), users=len(self.state.config.users))
        except Exception as e:
            log_gui_action("initial_data_load_failed", error=str(e))
            raise

    def execute(self, cmd: AnyCommand, *, record: bool = True) -> AnyResult:
        """Execute a command through the engine and notify listeners if state changed."""
        if self.engine is None or self.state is None:
            err = RuntimeError("Engine not initialized. Load initial data first.")
            log_command_execution(cmd, error=err)
            raise err
        try:
            result = self.engine.execute(cmd, record=record)
            log_command_execution(cmd, result=result)
            self.notify()
            return result
        except Exception as e:
            log_command_execution(cmd, error=e)
            raise
