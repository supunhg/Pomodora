# Pomodora

Pomodora is a clean and minimalistic Pomodoro timer application built with Python and PyQt5. It helps you boost your productivity by breaking work into focused intervals with short breaks.

## Features

- **Customizable Timers**: Set your preferred duration for work sessions, short breaks, and long breaks
- **Theme Options**: Choose between dark and light themes to match your preference
- **Zen Mode**: Simplified interface with only the essential timer display
- **Alerts**: Sound alerts when timers complete
- **Auto-start Options**: Automatically start breaks after work sessions or start work sessions after breaks
- **Custom Break Types**: Configure which break type (short or long) should follow a work session
- **Mute Option**: Easily mute sound notifications if needed

## Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5

### Setup
1. Clone this repository:

```bash
git clone https://github.com/supunhg/Pomodora.git
```

2. Navigate to the project directory:

```bash
cd
```

3. Install the required dependencies:

```bash
python -m pip install -r requirements.txt

# or

pip install PyQt5
```

4. Run the application:

```bash
python pomodora.py
```

## Screenshots

### Dark and Light Themes

<img width="317" height="395" alt="Screenshot_20251023_113905-2" src="https://github.com/user-attachments/assets/ace52075-b816-40af-a60a-e26bbb6cd946" />
<img width="318" height="399" alt="Screenshot_20251023_114231" src="https://github.com/user-attachments/assets/8adb3f24-55d7-4de7-a021-6a6485d8c4d7" />

### Settings Page

<img width="348" height="498" alt="Screenshot_20251023_114145" src="https://github.com/user-attachments/assets/c00f6a8a-6f86-476e-b628-7d9db193527e" />

### Zen Mode

<img width="315" height="237" alt="Screenshot_20251023_114341" src="https://github.com/user-attachments/assets/27e9a601-63df-4d3b-9503-6318970e8dfc" />

## Usage

1. **Start a Work Session**: Click the "START" button to begin a work session
2. **Take Breaks**: Use the "Short Break" or "Long Break" buttons when you need a pause
3. **Reset Timer**: Reset the current timer at any time with the "RESET" button
4. **Zen Mode**: Toggle Zen Mode to hide interface elements and focus on just the timer
5. **Settings**: Customize timers, themes, and auto-start options through the Settings panel

## Future Implementations

- Always-on-top feature for keeping the timer visible over other windows
- Additional sound effects and notification options
- Statistics tracking to monitor productivity over time
- Task/project labeling for work sessions
- Timer presets for different types of activities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
