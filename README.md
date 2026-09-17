# Desktop Analog Clock

A small PyQt6 analog clock for Linux desktops. It stays on top, can be moved by dragging, and shows the current date and digital time.

This project was developed with AI assistance under human direction and review.

## Requirements

- Linux with a graphical desktop session
- Python 3.10 or newer
- `python3-venv`
- X11 or Wayland with XWayland available

## Setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/kegch66/desktop-clock.git
cd desktop-clock
```

Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
```

Start the clock:

```bash
./start.sh
```

The window is 300 x 400 pixels. Drag the clock to move it, and use the button in the upper-right corner to close it.

## Start Automatically

The included `desktop-clock.desktop` file is a template. Before using it, replace `/path/to/desktop-clock` in the `Exec` line with the absolute path of your cloned directory.

For example, if the repository is cloned to `/home/alice/apps/desktop-clock`:

```ini
Exec=/home/alice/apps/desktop-clock/start.sh
```

Then install the desktop entry for the current user:

```bash
mkdir -p ~/.config/autostart
cp desktop-clock.desktop ~/.config/autostart/
```

Log out and back in, or start `./start.sh` manually to use the clock immediately.

## Platform Note

`start.sh` uses the `xcb` Qt platform plugin by default because it works with common X11 and XWayland desktop setups. To let Qt choose the platform automatically, run:

```bash
QT_QPA_PLATFORM= ./start.sh
```

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for the full text.

PyQt6 and its bundled Qt components are separate dependencies with their own licenses.