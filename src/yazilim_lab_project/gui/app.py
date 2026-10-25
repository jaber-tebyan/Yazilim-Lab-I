"""GUI Application entrypoint."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from yazilim_lab_project.gui.main_window import MainWindow


def main(initial_data_path: Path | None = None) -> None:
    app = QApplication(sys.argv)
    
    # Auto-load default initial data if none provided and asset exists
    if initial_data_path is None and len(sys.argv) > 1:
        initial_data_path = Path(sys.argv[1])
    elif initial_data_path is None:
        bundled = Path(__file__).parent.parent / "assets" / "baslangic_1.json"
        if bundled.exists():
            initial_data_path = bundled

    window = MainWindow(initial_data_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
