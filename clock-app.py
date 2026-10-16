import sys
import os
from zoneinfo import ZoneInfo
from datetime import datetime
from PyQt5.QtCore import (QTimer, QTime, Qt, QElapsedTimer, QUrl)
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QStackedWidget, QListWidget, QLineEdit,
                             QTimeEdit, QCheckBox, QMessageBox, QComboBox, QSpinBox)


class CronometerWidget(QWidget):
    def __init__(self, main_windows):
        super().__init__()

        self.main_windows = main_windows

        self.inside_layout = QHBoxLayout()
        self.label = QLabel("00:00:00")
        self.label.setAlignment(Qt.AlignCenter)

        self.inside_layout.addWidget(self.label)
        self.setLayout(self.inside_layout)

        # Kronometre değişkenleri
        self.timer = QTimer(self)
        self.elapsed = QElapsedTimer()
        self.elapsed_before = 0
        self.is_running = False

        # Sinyal bağlantıları
        self.timer.timeout.connect(self.crono_func)
        self.main_windows.stCronoButton.clicked.connect(self.crono_start_func)
        self.main_windows.stopCronoButton.clicked.connect(self.crono_stop_func)
        self.main_windows.restartCronoButton.clicked.connect(self.crono_restart_func)
        self.change_theme()

    def change_theme(self):
        if self.main_windows.theme_is == "white":
            self.label.setStyleSheet(
                "font-size: 50px; color: black;"
            )
        else:
            self.label.setStyleSheet(
                "font-size: 50px; color: white;"
            )

    def crono_start_func(self):
        if self.is_running:
            return

        self.elapsed.start()
        self.timer.start(1000)
        self.is_running = True

        self.main_windows.stopCronoButton.setText("STOP")
        self.main_windows.stopCronoButton.show()
        self.main_windows.restartCronoButton.show()
        self.main_windows.stCronoButton.hide()

        self.crono_func()

    def crono_stop_func(self):
        if self.is_running:
            self.elapsed_before += self.elapsed.elapsed()
            self.timer.stop()
            self.is_running = False
            self.main_windows.stopCronoButton.setText("CONTINUE")
        else:
            self.elapsed.start()
            self.timer.start(1000)
            self.is_running = True
            self.main_windows.stopCronoButton.setText("STOP")

        self.crono_func()

    def crono_restart_func(self):
        self.timer.stop()
        self.elapsed_before = 0
        self.is_running = False

        self.label.setText("00:00:00")

        self.main_windows.stopCronoButton.setText("STOP")
        self.main_windows.stopCronoButton.hide()
        self.main_windows.restartCronoButton.hide()
        self.main_windows.stCronoButton.show()

    def crono_func(self):
        total_ms = self.elapsed_before

        if self.is_running:
            total_ms += self.elapsed.elapsed()

        total_seconds = total_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        self.label.setText(
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )


class AlarmWidget(QWidget):
    def __init__(self, main_windows):
        super().__init__()

        self.main_windows = main_windows
        self.alarms = []

        # Alarm sesi
        self.sound = QSoundEffect(self)
        sound_path = os.path.abspath("alarm_sound.wav")
        self.sound.setSource(QUrl.fromLocalFile(sound_path))
        self.sound.setLoopCount(QSoundEffect.Infinite)
        self.sound.setVolume(0.8)

        # Başlık
        self.label = QLabel("ALARM")
        self.label.setStyleSheet("font-size: 50px;")
        self.label.setAlignment(Qt.AlignCenter)

        # Alarm adı
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Alarm name...")
        self.name_input.setStyleSheet("font-size: 50px;border: 5px solid black;")

        # Alarm saati
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setStyleSheet("font-size: 50px;border: 5px solid black;")
        self.time_input.setTime(QTime.currentTime())

        # "All" checkbox
        self.all_checkbox = QCheckBox("All (Everyday)")
        self.all_checkbox.setStyleSheet("font-size: 20px;")
        self.all_checkbox.stateChanged.connect(self.toggle_select_all)

        # Günler (İngilizce kısaltmalar)
        self.days = {
            "Monday": QCheckBox("Mon"),
            "Tuesday": QCheckBox("Tue"),
            "Wednesday": QCheckBox("Wed"),
            "Thursday": QCheckBox("Thu"),
            "Friday": QCheckBox("Fri"),
            "Saturday": QCheckBox("Sat"),
            "Sunday": QCheckBox("Sun")
        }
        for self.checks in self.days.values():
            self.checks.setStyleSheet("""QCheckBox {font-size: 20px;}
            QCheckBox::indicator {
                width: 20px;  
                height: 20px; 
            }""")
        self.mainDays_layout = QVBoxLayout()

        self.days_layout1 = QHBoxLayout()
        for name in ["Monday", "Tuesday", "Wednesday"]:
            self.days_layout1.addWidget(self.days[name])

        self.days_layout2 = QHBoxLayout()
        for name in ["Thursday", "Friday", "Saturday"]:
            self.days_layout2.addWidget(self.days[name])

        self.days_layout3 = QHBoxLayout()
        self.days_layout3.addWidget(self.days["Sunday"])
        self.days_layout3.addWidget(self.all_checkbox)

        self.mainDays_layout.addLayout(self.days_layout1)
        self.mainDays_layout.addLayout(self.days_layout2)
        self.mainDays_layout.addLayout(self.days_layout3)

        self.main_windows.makeAlarmButton.clicked.connect(self.make_alarm)

        # Alarm listesi
        self.alarm_list = QListWidget()
        self.alarm_list.setStyleSheet("font-size: 20px;border: 5px solid black;")

        # Çalan alarmı susturma butonu
        self.stop_sound_button = QPushButton("STOP ALARM SOUND")
        self.stop_sound_button.setStyleSheet("font-size: 20px;border: 5px solid black; background-color: white;")
        self.stop_sound_button.hide()
        self.stop_sound_button.clicked.connect(self.stop_alarm_sound)

        # Yerleşim
        self.main_layout = QVBoxLayout()
        self.inside1_layout = QHBoxLayout()
        self.inside2_layout = QHBoxLayout()
        self.main_layout.addWidget(self.label)
        self.inside1_layout.addWidget(self.name_input, 2)
        self.inside1_layout.addWidget(self.time_input, 1)
        self.inside2_layout.addLayout(self.mainDays_layout, 1)
        self.inside2_layout.addWidget(self.alarm_list, 2)
        self.main_layout.addLayout(self.inside1_layout)
        self.main_layout.addLayout(self.inside2_layout)
        self.main_layout.addWidget(self.stop_sound_button)
        self.setLayout(self.main_layout)

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_alarms)
        self.check_timer.start(1000)

        self.change_theme()

    def toggle_select_all(self, state):
        durum = self.all_checkbox.isChecked()
        for checkbox in self.days.values():
            checkbox.setChecked(durum)

    def change_theme(self):
        if self.main_windows.theme_is == "white":
            self.label.setStyleSheet("color: black;")
        else:
            self.label.setStyleSheet("color: white;")

    def make_alarm(self):
        name = self.name_input.text().strip()
        if not name:
            name = "Unnamed Alarm"

        alarm_time = self.time_input.time().toString("HH:mm")

        if self.all_checkbox.isChecked():
            selected_days = list(self.days.keys())
        else:
            selected_days = [
                day for day, checkbox in self.days.items()
                if checkbox.isChecked()
            ]

        alarm = {
            "name": name,
            "time": alarm_time,
            "days": selected_days,
            "enabled": True,
            "last_trigger_date": None
        }

        self.alarms.append(alarm)

        days_text = (
            ", ".join(selected_days)
            if selected_days
            else "One-time"
        )

        self.alarm_list.addItem(f"{name} | {alarm_time} | {days_text}")
        self.name_input.clear()
        self.all_checkbox.setChecked(False)
        for checkbox in self.days.values():
            checkbox.setChecked(False)

    def check_alarms(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.date()
        today_name = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ][now.weekday()]

        for alarm in self.alarms:
            if not alarm["enabled"]:
                continue
            if alarm["time"] != current_time:
                continue
            if alarm["last_trigger_date"] == today:
                continue

            if alarm["days"] and today_name not in alarm["days"]:
                continue

            alarm["last_trigger_date"] = today

            if not alarm["days"]:
                alarm["enabled"] = False

            self.stop_sound_button.show()
            self.sound.play()

            QMessageBox.information(
                self,
                "Alarm",
                f"{alarm['name']} time is up!"
            )

    def stop_alarm_sound(self):
        self.sound.stop()
        self.stop_sound_button.hide()


class WorldWidget(QWidget):
    def __init__(self, main_windows):
        super().__init__()

        self.main_windows = main_windows

        self.locations = {
            "Istanbul": "Europe/Istanbul",
            "London": "Europe/London",
            "Paris": "Europe/Paris",
            "New York": "America/New_York",
            "Tokyo": "Asia/Tokyo",
            "Dubai": "Asia/Dubai",
            "Seoul": "Asia/Seoul"
        }

        self.selected_location = "Istanbul"

        self.title_label = QLabel("WORLD TIME")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.location_label = QLabel("Istanbul")
        self.location_label.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)

        self.location_input = QComboBox()
        self.location_input.setStyleSheet("font-size: 20px;border: 5px solid black;")

        self.location_input.addItems(self.locations.keys())
        self.location_input.currentTextChanged.connect(
            self.select_location
        )

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.location_label)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.location_input)

        self.setLayout(self.layout)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.change_time)
        self.clock_timer.start(1000)

        self.change_time()
        self.change_theme()

    def select_location(self, location):
        self.selected_location = location
        self.location_label.setText(location)
        self.change_time()

    def change_time(self):
        timezone = ZoneInfo(
            self.locations[self.selected_location]
        )
        current_time = datetime.now(timezone)
        self.time_label.setText(
            current_time.strftime("%H:%M:%S")
        )

    def change_theme(self):
        color = (
            "black"
            if self.main_windows.theme_is == "white"
            else "white"
        )

        self.title_label.setStyleSheet(
            f"font-size: 35px; color: {color};"
        )
        self.location_label.setStyleSheet(
            f"font-size: 25px; color: {color};"
        )
        self.time_label.setStyleSheet(
            f"font-size: 65px; color: {color};"
        )


class TimerWidget(QWidget):
    def __init__(self, main_windows):
        super().__init__()

        self.sound = QSoundEffect(self)
        sound_path = os.path.abspath("alarm_sound.wav")
        self.sound.setSource(QUrl.fromLocalFile(sound_path))
        self.sound.setLoopCount(QSoundEffect.Infinite)
        self.sound.setVolume(0.8)
        self.main_windows = main_windows

        self.remaining_seconds = 0
        self.is_running = False

        self.stop_sound_button = QPushButton("STOP ALARM SOUND")
        self.stop_sound_button.setStyleSheet("font-size: 20px;border: 5px solid black; background-color: white;")
        self.stop_sound_button.hide()
        self.stop_sound_button.clicked.connect(self.stop_alarm_sound)

        self.title_label = QLabel("TIMER")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)

        self.hour_input = QSpinBox()
        self.hour_input.setRange(0, 99)
        self.hour_input.setPrefix("Hour: ")
        self.hour_input.setStyleSheet("font-size: 20px;border: 5px solid black;")

        self.minute_input = QSpinBox()
        self.minute_input.setRange(0, 59)
        self.minute_input.setPrefix("Minute: ")
        self.minute_input.setStyleSheet("font-size: 20px;border: 5px solid black;")

        self.second_input = QSpinBox()
        self.second_input.setRange(0, 59)
        self.second_input.setPrefix("Second: ")
        self.second_input.setStyleSheet("font-size: 20px;border: 5px solid black;")

        self.start_button = QPushButton("START")
        self.start_button.setStyleSheet("font-size: 20px;border: 5px solid black;")
        self.start_button.show()
        self.pause_button = QPushButton("PAUSE")
        self.pause_button.setStyleSheet("font-size: 20px;border: 5px solid black;")
        self.pause_button.hide()
        self.reset_button = QPushButton("RESET")
        self.reset_button.setStyleSheet("font-size: 20px;border: 5px solid black;")
        self.reset_button.hide()

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.reset_button.clicked.connect(self.reset_timer)

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.hour_input)
        self.input_layout.addWidget(self.minute_input)
        self.input_layout.addWidget(self.second_input)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.reset_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.time_label)
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.stop_sound_button)

        self.setLayout(self.main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.countdown)

        self.change_theme()

    def start_timer(self):
        if self.is_running:
            return

        if self.remaining_seconds == 0:
            self.remaining_seconds = (
                self.hour_input.value() * 3600
                + self.minute_input.value() * 60
                + self.second_input.value()
            )

        if self.remaining_seconds <= 0:
            self.time_label.setText("Select time!")
            return

        self.start_button.hide()
        self.pause_button.show()
        self.reset_button.show()
        self.pause_button.setText("PAUSE")

        self.is_running = True
        self.timer.start(1000)
        self.update_display()

    def toggle_pause(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.pause_button.setText("CONTINUE")
        else:
            self.timer.start(1000)
            self.is_running = True
            self.pause_button.setText("PAUSE")

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.remaining_seconds = 0

        self.hour_input.setValue(0)
        self.minute_input.setValue(0)
        self.second_input.setValue(0)

        self.time_label.setText("00:00:00")

    def countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.is_running = False
            self.time_label.setText("00:00:00")
            self.sound.play()
            self.stop_sound_button.show()
            self.start_button.show()
            self.pause_button.hide()
            self.reset_button.hide()

            QMessageBox.information(
                self,
                "Timer",
                "Countdown completed!")

    def update_display(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        self.time_label.setText(
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )

    def change_theme(self):
        color = (
            "black"
            if self.main_windows.theme_is == "white"
            else "white"
        )

        self.title_label.setStyleSheet(
            f"font-size: 35px; color: {color};"
        )
        self.time_label.setStyleSheet(
            f"font-size: 65px; color: {color};"
        )

    def stop_alarm_sound(self):
        self.sound.stop()
        self.stop_sound_button.hide()


class MainWindows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clock App")
        self.setGeometry(450, 350, 1000, 400)

        self.cronometer_button = QPushButton("⏱️")
        self.makeAlarmButton = QPushButton("MAKE ALARM")
        self.stCronoButton = QPushButton("START")
        self.stopCronoButton = QPushButton("STOP")
        self.restartCronoButton = QPushButton("RESTART")
        self.alarm_button = QPushButton("⏲️")
        self.timer_button = QPushButton("⌛")
        self.theme_button = QPushButton("🖌️")
        self.world_time_button = QPushButton("🌍")
        self.main_menu = QPushButton("🏠")

        self.time_shower = QLabel("00:00:00")
        self.qtimer = QTimer()
        self.theme_is = "gray"

        self.stacked_widget = QStackedWidget()

        self.home_page = QWidget()
        self.init_home_content()

        self.cronometer_page = CronometerWidget(self)
        self.alarm_page = AlarmWidget(self)
        self.world_page = WorldWidget(self)
        self.timer_page = TimerWidget(self)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.cronometer_page)
        self.stacked_widget.addWidget(self.alarm_page)
        self.stacked_widget.addWidget(self.world_page)
        self.stacked_widget.addWidget(self.timer_page)

        self.central_widget = QWidget()

        self.inside1_layout = QHBoxLayout()
        self.inside1_layout.setSpacing(0)
        self.inside1_layout.setContentsMargins(0, 0, 0, 0)
        self.inside1_layout.addWidget(self.cronometer_button, 2)
        self.inside1_layout.addWidget(self.alarm_button, 2)
        self.inside1_layout.addWidget(self.timer_button, 2)
        self.inside1_layout.addWidget(self.theme_button, 2)
        self.inside1_layout.addWidget(self.world_time_button, 2)
        self.inside1_layout.addWidget(self.main_menu, 1)

        self.inside2_layout = QHBoxLayout()
        self.inside2_layout.setSpacing(0)
        self.inside2_layout.setContentsMargins(0, 0, 0, 0)
        self.inside2_layout.addWidget(self.stCronoButton)
        self.inside2_layout.addWidget(self.makeAlarmButton)
        self.inside2_layout.addWidget(self.restartCronoButton)
        self.inside2_layout.addWidget(self.stopCronoButton)

        self.outside_layout = QVBoxLayout()
        self.outside_layout.setSpacing(0)
        self.outside_layout.setContentsMargins(0, 0, 0, 0)
        self.outside_layout.addWidget(self.stacked_widget, 3)
        self.outside_layout.addLayout(self.inside2_layout, 1)
        self.outside_layout.addLayout(self.inside1_layout, 1)

        self.central_widget.setLayout(self.outside_layout)
        self.setCentralWidget(self.central_widget)

        self.initUI()

    def init_home_content(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.time_shower.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_shower)
        self.home_page.setLayout(layout)

    def initUI(self):
        self.qtimer.timeout.connect(self.update_time)
        self.qtimer.start(1000)
        self.apply_theme_styles()
        self.hide_all_extra_buttons()

        self.stacked_widget.currentChanged.connect(self.on_page_changed)

        self.main_menu.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.home_page))
        self.cronometer_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.cronometer_page))
        self.alarm_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.alarm_page))
        self.world_time_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.world_page))
        self.timer_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.timer_page))
        self.theme_button.clicked.connect(self.theme_func)

    def update_time(self):
        if self.stacked_widget.currentWidget() == self.home_page:
            self.time_shower.setText(QTime.currentTime().toString("hh:mm:ss"))

    def theme_func(self):
        if self.theme_is == "gray":
            self.theme_is = "white"
        elif self.theme_is == "white":
            self.theme_is = "red"
        elif self.theme_is == "red":
            self.theme_is = "purple"
        elif self.theme_is == "purple":
            self.theme_is = "green"
        elif self.theme_is == "green":
            self.theme_is = "brown"
        elif self.theme_is == "brown":
            self.theme_is = "gray"

        self.apply_theme_styles()
        self.cronometer_page.change_theme()
        self.alarm_page.change_theme()
        self.world_page.change_theme()
        self.timer_page.change_theme()

    def apply_theme_styles(self):
        themes = {
            "gray": {"bg": "#575555", "fg": "white", "btn_bg": "#3B3737", "hover": "#706767", "pressed": "#A19A9A",
                     "border": "white"},
            "white": {"bg": "#FFFBFA", "fg": "black", "btn_bg": "#DBD7D7", "hover": "#706767", "pressed": "#A19A9A",
                      "border": "black"},
            "red": {"bg": "#FF0000", "fg": "white", "btn_bg": "#D12828", "hover": "#8A2222", "pressed": "#611818",
                    "border": "black"},
            "purple": {"bg": "#8F09E0", "fg": "white", "btn_bg": "#7E1ABA", "hover": "#6A1C99", "pressed": "#441361",
                       "border": "black"},
            "green": {"bg": "#0AF22D", "fg": "white", "btn_bg": "#3FCC23", "hover": "#32FF00", "pressed": "#3EA629",
                      "border": "black"},
            "brown": {"bg": "#BA4C2B", "fg": "white", "btn_bg": "#8A3221", "hover": "#C2786B", "pressed": "#4F241A",
                      "border": "black"}
        }

        t = themes[self.theme_is]

        self.setStyleSheet(f"QMainWindow{{background-color:{t['bg']};}}")
        self.time_shower.setStyleSheet(f"""QLabel{{background-color:{t['bg']};
                                            color:{t['fg']};
                                            font-size: 150px;
                                            font-family: 'Courier New', monospace;
                                            font-weight: bold;
                                            border-radius: 10px;}}""")

        buttons1 = [self.theme_button, self.world_time_button, self.alarm_button,
                    self.timer_button, self.cronometer_button, self.main_menu]
        buttons2 = [self.stCronoButton,
                    self.makeAlarmButton, self.restartCronoButton, self.stopCronoButton]

        for btn in buttons1:
            btn.setStyleSheet(f"""QPushButton{{background-color:{t['btn_bg']};
                                                color: white;
                                                font-size: 30px;
                                                border: 5px solid {t['border']};}}
                                                QPushButton:hover{{background-color:{t['hover']};}}
                                                QPushButton:pressed{{background-color:{t['pressed']};}}""")
        for btn in buttons2:
            color = "black" if self.theme_is == "white" else "white"
            btn.setStyleSheet(f"""QPushButton{{background-color:{t['btn_bg']};
                                                color: {color};
                                                font-size: 30px;
                                                border: 5px solid {t['border']};}}
                                                QPushButton:hover{{background-color:{t['hover']};}}
                                                QPushButton:pressed{{background-color:{t['pressed']};}}""")

    def on_page_changed(self, index):
        self.hide_all_extra_buttons()
        if index == 1:
            self.stCronoButton.show()
        elif index == 2:
            self.makeAlarmButton.show()
        elif index == 3:
            pass
        elif index == 4:
            pass

    def hide_all_extra_buttons(self):
        self.makeAlarmButton.hide()
        self.stCronoButton.hide()
        self.stopCronoButton.hide()
        self.restartCronoButton.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindows()
    main.show()
    sys.exit(app.exec_())