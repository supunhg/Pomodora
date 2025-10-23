import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QDialog, QRadioButton, 
                            QCheckBox, QButtonGroup, QFrame, QScrollArea,
                            QSpinBox, QGridLayout, QGroupBox, QComboBox)
from PyQt5.QtCore import QTimer, Qt, QTime, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtMultimedia import QSoundEffect
import platform

class SettingsDialog(QDialog):
    themeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None, current_theme='dark', mute_enabled=False, 
                 work_time=25, short_break=5, long_break=15,
                 auto_start_break=False, auto_start_work=False, auto_break_type="short"):
        super().__init__(parent)
        self.setWindowTitle("Settings - Pomodora")
        self.setMinimumSize(350, 400)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_group = QButtonGroup()
        self.dark_radio = QRadioButton("Dark Mode")
        self.light_radio = QRadioButton("Light Mode")
        
        if current_theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
            
        self.theme_group.addButton(self.dark_radio)
        self.theme_group.addButton(self.light_radio)
        
        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.light_radio)
        theme_group.setLayout(theme_layout)
        content_layout.addWidget(theme_group)
        
        timer_group = QGroupBox("Timer Settings (minutes)")
        timer_layout = QGridLayout()
        
        timer_layout.addWidget(QLabel("Work:"), 0, 0)
        self.work_time_spin = QSpinBox()
        self.work_time_spin.setRange(1, 120)
        self.work_time_spin.setValue(work_time)
        timer_layout.addWidget(self.work_time_spin, 0, 1)
        
        timer_layout.addWidget(QLabel("Short Break:"), 1, 0)
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(short_break)
        timer_layout.addWidget(self.short_break_spin, 1, 1)
        
        timer_layout.addWidget(QLabel("Long Break:"), 2, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 60)
        self.long_break_spin.setValue(long_break)
        timer_layout.addWidget(self.long_break_spin, 2, 1)
        
        timer_group.setLayout(timer_layout)
        content_layout.addWidget(timer_group)
        
        auto_group = QGroupBox("Auto-start Options")
        auto_layout = QVBoxLayout()
        
        self.auto_start_break = QCheckBox("Auto-start break after work timer")
        self.auto_start_break.setChecked(auto_start_break)
        auto_layout.addWidget(self.auto_start_break)
        
        break_type_layout = QHBoxLayout()
        break_type_layout.addWidget(QLabel("Break type:"))
        self.break_type_combo = QComboBox()
        self.break_type_combo.addItems(["Short Break", "Long Break"])
        if auto_break_type == "long":
            self.break_type_combo.setCurrentIndex(1)
        break_type_layout.addWidget(self.break_type_combo)
        auto_layout.addLayout(break_type_layout)
        
        self.auto_start_work = QCheckBox("Auto-start work timer after break")
        self.auto_start_work.setChecked(auto_start_work)
        auto_layout.addWidget(self.auto_start_work)
        
        auto_group.setLayout(auto_layout)
        content_layout.addWidget(auto_group)
        
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QVBoxLayout()
        
        self.mute_checkbox = QCheckBox("Mute Sound Notifications")
        self.mute_checkbox.setChecked(mute_enabled)
        sound_layout.addWidget(self.mute_checkbox)
        
        sound_group.setLayout(sound_layout)
        content_layout.addWidget(sound_group)
        
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_label = QLabel("Pomodora v1.0\nCreator: Supun Hewagamage\ngithub.com/supunhg")
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet("color: gray;")
        about_layout.addWidget(about_label)
        
        about_group.setLayout(about_layout)
        content_layout.addWidget(about_group)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.dark_radio.toggled.connect(self.on_theme_change)
        self.light_radio.toggled.connect(self.on_theme_change)
        
    def on_theme_change(self):
        theme = 'dark' if self.dark_radio.isChecked() else 'light'
        self.themeChanged.emit(theme)
        
    def is_muted(self):
        return self.mute_checkbox.isChecked()
    
    def get_work_time(self):
        return self.work_time_spin.value()
    
    def get_short_break_time(self):
        return self.short_break_spin.value()
    
    def get_long_break_time(self):
        return self.long_break_spin.value()
    
    def get_auto_start_break(self):
        return self.auto_start_break.isChecked()
    
    def get_auto_start_work(self):
        return self.auto_start_work.isChecked()
    
    def get_auto_break_type(self):
        return "short" if self.break_type_combo.currentIndex() == 0 else "long"


class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.time_left = 25 * 60
        self.is_running = False
        self.current_mode = "work"
        self.theme = "dark"
        self.zen_mode = False
        self.mute = False
        
        self.work_time_min = 25
        self.short_break_min = 5
        self.long_break_min = 15
        
        self.work_time = self.work_time_min * 60
        self.short_break_time = self.short_break_min * 60
        self.long_break_time = self.long_break_min * 60
        
        self.auto_start_break = False
        self.auto_start_work = False
        self.auto_break_type = "short"
        
        self.init_ui()
        self.apply_theme()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.setup_tray()
        
    def init_ui(self):
        self.setWindowTitle("Pomodora")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(320, 400)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_area = QWidget()
        title_area_layout = QHBoxLayout(title_area)
        title_area_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("POMODORA")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft)
        title_area_layout.addWidget(self.title_label)
        title_area_layout.addStretch()
        
        title_area.setCursor(Qt.SizeAllCursor)
        title_area.setMinimumHeight(30)
        
        title_layout.addWidget(title_area)
        title_layout.addStretch()
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setFont(QFont("Arial", 16))
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(title_layout)
        
        self.mode_label = QLabel("WORK TIME")
        self.mode_label.setFont(QFont("Arial", 10))
        self.mode_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mode_label)
        
        self.time_display = QLabel("25:00")
        self.time_display.setFont(QFont("Arial", 48, QFont.Bold))
        self.time_display.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.time_display)
        
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
        
        self.footer_label = QLabel("by Supun Hewagamage • github.com/supunhg")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("font-size: 8pt; color: gray;")
        main_layout.addWidget(self.footer_label)
        
        self.setLayout(main_layout)
        
        self.oldPos = self.pos()
        
    def mousePressEvent(self, event):
        if event.pos().y() <= 50:
            self.oldPos = event.globalPos()
        else:
            self.oldPos = None
        
    def mouseMoveEvent(self, event):
        if self.oldPos:
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
                QPushButton:checked {
                    background-color: #3d3d3d;
                    border: 1px solid #5d5d5d;
                }
                QPushButton#start_btn {
                    background-color: #4CAF50;
                }
                QPushButton#start_btn:hover {
                    background-color: #45a049;
                }
                QPushButton#pause_btn {
                    background-color: #f44336;
                }
                QPushButton#pause_btn:hover {
                    background-color: #e53935;
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
                QPushButton:checked {
                    background-color: #e0e0e0;
                    border: 1px solid #ccc;
                }
                QPushButton#start_btn {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                }
                QPushButton#start_btn:hover {
                    background-color: #45a049;
                }
                QPushButton#pause_btn {
                    background-color: #f44336;
                    color: white;
                    border: none;
                }
                QPushButton#pause_btn:hover {
                    background-color: #e53935;
                }
            """)
        
        if self.is_running:
            self.start_btn.setObjectName("pause_btn")
        else:
            self.start_btn.setObjectName("start_btn")
        
    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("START")
            self.start_btn.setObjectName("start_btn")
        else:
            self.timer.start(1000)
            self.start_btn.setText("PAUSE")
            self.start_btn.setObjectName("pause_btn")
        self.is_running = not self.is_running
        self.style().unpolish(self.start_btn)
        self.style().polish(self.start_btn)
        
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
        self.start_btn.setObjectName("start_btn")
        self.style().unpolish(self.start_btn)
        self.style().polish(self.start_btn)
        
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
        self.start_btn.setObjectName("start_btn")
        self.style().unpolish(self.start_btn)
        self.style().polish(self.start_btn)
        
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
        self.start_btn.setObjectName("start_btn")
        self.style().unpolish(self.start_btn)
        self.style().polish(self.start_btn)
        
        if not self.mute:
            self.play_notification_sound()
        
        mode_text = self.mode_label.text()
        self.tray_icon.showMessage(
            "Pomodora Timer",
            f"{mode_text} finished!",
            QSystemTrayIcon.Information,
            3000
        )
        
        if self.current_mode == "work" and self.auto_start_break:
            break_type = "long_break" if self.auto_break_type == "long" else "short_break"
            self.change_mode(break_type)
            self.toggle_timer()
        elif (self.current_mode == "short_break" or self.current_mode == "long_break") and self.auto_start_work:
            self.change_mode("work")
            self.toggle_timer()
            
    def play_notification_sound(self):
        QApplication.beep()
        if platform.system() == "Linux":
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null &')
            
    def toggle_zen_mode(self):
        self.zen_mode = self.zen_btn.isChecked()
        
        pos = self.pos()
        
        if self.zen_mode:
            self.mode_label.hide()
            self.reset_btn.hide()
            self.work_btn.hide()
            self.short_break_btn.hide()
            self.long_break_btn.hide()
            self.settings_btn.hide()
            self.footer_label.hide()
            
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setFixedSize(320, 240)
        else:
            self.mode_label.show()
            self.reset_btn.show()
            self.work_btn.show()
            self.short_break_btn.show()
            self.long_break_btn.show()
            self.settings_btn.show()
            self.footer_label.show()
            
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setFixedSize(320, 400)
        
        self.show()
        self.move(pos)
            
    def show_settings(self):
        dialog = SettingsDialog(
            self, 
            self.theme, 
            self.mute,
            self.work_time_min,
            self.short_break_min,
            self.long_break_min,
            self.auto_start_break,
            self.auto_start_work,
            self.auto_break_type
        )
        dialog.themeChanged.connect(self.change_theme)
        
        if dialog.exec_():
            self.mute = dialog.is_muted()
            
            self.work_time_min = dialog.get_work_time()
            self.short_break_min = dialog.get_short_break_time()
            self.long_break_min = dialog.get_long_break_time()
            
            self.work_time = self.work_time_min * 60
            self.short_break_time = self.short_break_min * 60
            self.long_break_time = self.long_break_min * 60
            
            self.auto_start_break = dialog.get_auto_start_break()
            self.auto_start_work = dialog.get_auto_start_work()
            self.auto_break_type = dialog.get_auto_break_type()
            
            if not self.is_running:
                self.reset_timer()
        
    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodora")
    
    window = PomodoroTimer()
    window.show()
    
    sys.exit(app.exec_())