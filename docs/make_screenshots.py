import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from PIL import ImageGrab

import main as app_module


def grab(widget, name):
    for _ in range(40):
        widget.update()
        time.sleep(0.02)
    x, y = widget.winfo_rootx(), widget.winfo_rooty()
    box = (x, y, x + widget.winfo_width(), y + widget.winfo_height())
    shot = ImageGrab.grab(bbox=box)
    path = os.path.join(ROOT, "docs", name)
    shot.save(path)
    print(f"{name}: {shot.width}x{shot.height}")


def main():
    app = app_module.App()
    app.update()
    app.attributes("-topmost", True)
    grab(app, "screenshot-main.png")

    app.open_settings()
    for _ in range(60):
        app.update()
        time.sleep(0.02)
    settings = [w for w in app.winfo_children() if w.winfo_class() == "Toplevel"][-1]
    settings.attributes("-topmost", True)
    settings.lift()
    grab(settings, "screenshot-settings.png")

    app.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
