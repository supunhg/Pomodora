import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QDialog, QRadioButton, 
                            git branch -M mainQCheckBox, QButtonGroup, QFrame)
from PyQt5.QtCore import QTimer, Qt, QTime, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtMultimedia import QSoundEffect
import platform

class SettingsDialog(QDialog):
    themeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None, current_theme='dark', mute_enabled=False):
        super().__init__(parent)
        self.setWindowTitle("Settings - Pomodora")
        self.setFixedSize(300, 200)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Theme selection
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(theme_label)
        
        self.theme_group = QButtonGroup()
        self.dark_radio = QRadioButton("Dark Mode")
        self.light_radio = QRadioButton("Light Mode")
        
        if current_theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
            
        self.theme_group.addButton(self.dark_radio)
        self.theme_group.addButton(self.light_radio)
        
        layout.addWidget(self.dark_radio)
        layout.addWidget(self.light_radio)
        
        layout.addSpacing(20)
        
        # Mute option
        self.mute_checkbox = QCheckBox("Mute Sound Notifications")
        self.mute_checkbox.setChecked(mute_enabled)
        layout.addWidget(self.mute_checkbox)
        
        layout.addSpacing(20)
        
        # About section
        about_label = QLabel("Pomodora v1.0\nCreator: Supun Hewagamage\ngithub.com/supunhg")
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(about_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.dark_radio.toggled.connect(self.on_theme_change)
        self.light_radio.toggled.connect(self.on_theme_change)
        
    def on_theme_change(self):
        theme = 'dark' if self.dark_radio.isChecked() else 'light'
        self.themeChanged.emit(theme)
        
    def is_muted(self):
        return self.mute_checkbox.isChecked()


class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.time_left = 25 * 60  # 25 minutes in seconds
        self.is_running = False
        self.current_mode = "work"  # work, short_break, long_break
        self.theme = "dark"
        self.zen_mode = False
        self.mute = False
        
        # Time configurations (in seconds)
        self.work_time = 25 * 60
        self.short_break_time = 5 * 60
        self.long_break_time = 15 * 60
        
        self.init_ui()
        self.apply_theme()
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # System tray for notifications
        self.setup_tray()
        
    def init_ui(self):
        self.setWindowTitle("Pomodora")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(320, 400)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title bar with close button
        title_layout = QHBoxLayout()
        self.title_label = QLabel("POMODORA")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setFont(QFont("Arial", 16))
        self.close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        main_layout.addLayout(title_layout)
        
        # Mode label
        self.mode_label = QLabel("WORK TIME")
        self.mode_label.setFont(QFont("Arial", 10))
        self.mode_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mode_label)
        
        # Timer display
        self.time_display = QLabel("25:00")
        self.time_display.setFont(QFont("Arial", 48, QFont.Bold))
        self.time_display.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.time_display)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("START")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.start_btn.clicked.connect(self.toggle_timer)
        
        self.reset_btn = QPushButton("RESET")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setFont(QFont("Arial", 10))
        self.reset_btn.clicked.connect(self.reset_timer)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.reset_btn)
        main_layout.addLayout(control_layout)
        
        # Mode buttons
        mode_layout = QHBoxLayout()
        self.work_btn = QPushButton("Work")
        self.short_break_btn = QPushButton("Short Break")
        self.long_break_btn = QPushButton("Long Break")
        
        for btn in [self.work_btn, self.short_break_btn, self.long_break_btn]:
            btn.setFixedHeight(35)
            
        self.work_btn.clicked.connect(lambda: self.change_mode("work"))
        self.short_break_btn.clicked.connect(lambda: self.change_mode("short_break"))
        self.long_break_btn.clicked.connect(lambda: self.change_mode("long_break"))
        
        mode_layout.addWidget(self.work_btn)
        mode_layout.addWidget(self.short_break_btn)
        mode_layout.addWidget(self.long_break_btn)
        main_layout.addLayout(mode_layout)
        
        # Feature buttons
        feature_layout = QHBoxLayout()
        self.zen_btn = QPushButton("Zen Mode")
        self.zen_btn.setFixedHeight(35)
        self.zen_btn.setCheckable(True)
        self.zen_btn.clicked.connect(self.toggle_zen_mode)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setFixedHeight(35)
        self.settings_btn.clicked.connect(self.show_settings)
        
        feature_layout.addWidget(self.zen_btn)
        feature_layout.addWidget(self.settings_btn)
        main_layout.addLayout(feature_layout)
        
        # Footer
        self.footer_label = QLabel("by Supun Hewagamage • github.com/supunhg")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("font-size: 8pt; color: gray;")
        main_layout.addWidget(self.footer_label)
        
        self.setLayout(main_layout)
        
        # Make window draggable
        self.oldPos = self.pos()
        
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Pomodora Timer")
        
    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #4d4d4d;
                }
                QPushButton#start_btn {
                    background-color: #4CAF50;
                }
                QPushButton#start_btn:hover {
                    background-color: #45a049;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d8d8d8;
                }
                QPushButton#start_btn {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                }
                QPushButton#start_btn:hover {
                    background-color: #45a049;
                }
            """)
        
        self.start_btn.setObjectName("start_btn")
        
    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("START")
        else:
            self.timer.start(1000)
            self.start_btn.setText("PAUSE")
        self.is_running = not self.is_running
        
    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
        else:
            self.timer_finished()
            
    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
        
    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.start_btn.setText("START")
        
        if self.current_mode == "work":
            self.time_left = self.work_time
        elif self.current_mode == "short_break":
            self.time_left = self.short_break_time
        else:
            self.time_left = self.long_break_time
            
        self.update_display()
        
    def change_mode(self, mode):
        self.current_mode = mode
        self.timer.stop()
        self.is_running = False
        self.start_btn.setText("START")
        
        if mode == "work":
            self.time_left = self.work_time
            self.mode_label.setText("WORK TIME")
        elif mode == "short_break":
            self.time_left = self.short_break_time
            self.mode_label.setText("SHORT BREAK")
        else:
            self.time_left = self.long_break_time
            self.mode_label.setText("LONG BREAK")
            
        self.update_display()
        
    def timer_finished(self):
        self.timer.stop()
        self.is_running = False
        self.start_btn.setText("START")
        
        # Show notification
        mode_text = self.mode_label.text()
        self.tray_icon.showMessage(
            "Pomodora Timer",
            f"{mode_text} finished!",
            QSystemTrayIcon.Information,
            3000
        )
        
        # Play sound if not muted
        if not self.mute:
            self.play_notification_sound()
            
    def play_notification_sound(self):
        # Simple beep using system bell
        QApplication.beep()
        # Alternative: use shell command for Linux
        if platform.system() == "Linux":
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null &')
            
    def toggle_zen_mode(self):
        self.zen_mode = self.zen_btn.isChecked()
        
        if self.zen_mode:
            # Hide all controls except timer
            self.mode_label.hide()
            self.reset_btn.hide()
            self.work_btn.hide()
            self.short_break_btn.hide()
            self.long_break_btn.hide()
            self.settings_btn.hide()
            self.footer_label.hide()
            self.setFixedSize(320, 200)
        else:
            self.mode_label.show()
            self.reset_btn.show()
            self.work_btn.show()
            self.short_break_btn.show()
            self.long_break_btn.show()
            self.settings_btn.show()
            self.footer_label.show()
            self.setFixedSize(320, 400)
            
    def show_settings(self):
        dialog = SettingsDialog(self, self.theme, self.mute)
        dialog.themeChanged.connect(self.change_theme)
        dialog.exec_()
        self.mute = dialog.is_muted()
        
    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodora")
    
    window = PomodoroTimer()
    window.show()
    
    sys.exit(app.exec_())