             .',;::::;,'.                 adrien@Adrien
         .';:cccccccccccc:;,.             -------------
      .;cccccccccccccccccccccc;.          OS: Bazzite x86_64
    .:cccccccccccccccccccccccccc:.        Kernel: Linux 7.2.7-ogc1.1.fc44.x86_64
  .;ccccccccccccc;.:dddl:.;ccccccc;.      Uptime: 45 mins
 .:ccccccccccccc;OWMKOOXMWd;ccccccc:.     Packages: 1 (appimage), 74 (flatpak-system), 11 (flatpak-user), 2832 (rpm)
.:ccccccccccccc;KMMc;cc;xMMc;ccccccc:.    Shell: bash 5.3.9
,cccccccccccccc;MMM.;cc;;WW:;cccccccc,    Display (SKG2522): 1920x1080 in 27", 180 Hz [External] *
:cccccccccccccc;MMM.;cccccccccccccccc:    Display (VG240Y): 1920x1080 in 24", 75 Hz [External]
:ccccccc;oxOOOo;MMM000k.;cccccccccccc:    Desktop Environment: KDE Plasma 6.7.5
cccccc;0MMKxdd:;MMMkddc.;cccccccccccc;    Window Manager: KWin (Wayland)
ccccc;XMO';cccc;MMM.;cccccccccccccccc'    WM Theme: Breeze
ccccc;MMo;ccccc;MMW.;ccccccccccccccc;     Theme: Oxygen (Dark) [Qt], Vapor [GTK2/3]
ccccc;0MNc.ccc.xMMd;ccccccccccccccc;      Icons: oxygen [Qt], oxygen [GTK2/3/4]
cccccc;dNMWXXXWM0:;cccccccccccccc:,       Font: Noto Sans (10pt) [Qt], Noto Sans (10pt) [GTK2/3/4]
cccccccc;.:odl:.;cccccccccccccc:,.        Cursor: Oxygen_Zion (24px)
ccccccccccccccccccccccccccccc:'.          Terminal: codex
:ccccccccccccccccccccccc:;,..             CPU: Intel(R) Core(TM) i5-14600K (12+8) @ 5.30 GHz
 ':cccccccccccccccc::;,.                  GPU: NVIDIA GeForce RTX 2070 [Discrete]
                                          Memory: 5.85 GiB / 31.01 GiB (19%)
                                          Swap: 0 B / 15.51 GiB (0%)
                                          Disk (/): 46.63 MiB / 46.63 MiB (100%) - overlay [Read-only]
                                          Disk (/etc): 423.38 GiB / 444.54 GiB (95%) - btrfs
                                          Disk (/var/mnt/jeux): 740.23 GiB / 953.87 GiB (78%) - ntfs3
                                          Local IP (eno1): 192.168.1.35/24
                                          Locale: C.UTF-8
                                          
                                          [40m   [41m   [42m   [43m   [44m   [45m   [46m   [47m   [m
                                          [5m[100m   [101m   [102m   [103m   [104m   [105m   [106m   [107m   [m
#!/usr/bin/env python3
"""Rayko Bazzite Toolbox V2 — interface KDE/Qt, sans dépendance à la V1."""

from __future__ import annotations

import html
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
    QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget,
)

APP_NAME = "Rayko Bazzite Toolbox"
APP_VERSION = "2.1.0"
UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/adriendu38100/rayko-bazzite-toolbox/main/update.json"
GAME_DISK = Path("/var/mnt/jeux")
REPORT_DIR = Path.home() / "Rayko-Reports"
BACKUP_DIR = Path.home() / "Rayko-Backups"
AUTOSTART_FILE = Path.home() / ".config/autostart/rayko-bazzite-toolbox.desktop"
SETTINGS_FILE = Path.home() / ".config/rayko-bazzite-toolbox/settings.json"
HEALTH_INTERVAL_MS = 5 * 60 * 1000
UPDATE_INTERVAL_MS = 60 * 60 * 1000
OK_NOTIFICATION_INTERVAL = 60 * 60


def run_text(command: list[str], timeout: float = 2.0) -> str:
    """Run a short read-only command for a dashboard value."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return (result.stdout or result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def cpu_temperature() -> str:
    values: list[float] = []
    for path in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
        try:
            value = float(path.read_text().strip()) / 1000
            if 10 <= value <= 120:
                values.append(value)
        except (OSError, ValueError):
            pass
    return f"{max(values):.0f} °C" if values else "Non disponible"


def memory_summary() -> str:
    try:
        entries = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            entries[key] = int(value.split()[0]) * 1024
        total, available = entries["MemTotal"], entries["MemAvailable"]
        used = total - available
        return f"{used / 2**30:.1f} / {total / 2**30:.1f} Gio"
    except (OSError, KeyError, ValueError):
        return "Non disponible"


def disk_summary(path: Path) -> str:
    try:
        usage = shutil.disk_usage(path)
        percent = (usage.used / usage.total * 100) if usage.total else 0
        return f"{usage.used / 2**30:.0f} / {usage.total / 2**30:.0f} Gio · {percent:.0f}%"
    except OSError:
        return "Non monté"


def gpu_summary() -> tuple[str, str]:
    result = run_text([
        "nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ])
    if not result:
        return "NVIDIA non détecté", "Température indisponible"
    parts = [part.strip() for part in result.splitlines()[0].split(",")]
    if len(parts) >= 5:
        name, temp, load, used, total = parts[:5]
        return f"{name} · {load}% · {used}/{total} Mio", f"{temp} °C"
    return result.splitlines()[0], "Température indisponible"


@dataclass(frozen=True)
class Action:
    title: str
    description: str
    command: str
    confirmation: str | None = None
    button: str = "Lancer"


class MetricCard(QFrame):
    def __init__(self, title: str, accent: str):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        label = QLabel(title.upper())
        label.setObjectName("metricTitle")
        self.value = QLabel("Chargement…")
        self.value.setObjectName("metricValue")
        self.value.setWordWrap(True)
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"background:{accent}; border-radius:1px;")
        layout.addWidget(label)
        layout.addWidget(self.value, 1)
        layout.addWidget(bar)


class ActionCard(QFrame):
    def __init__(self, action: Action, callback):
        super().__init__()
        self.setObjectName("actionCard")
        layout = QVBoxLayout(self)
        title = QLabel(action.title)
        title.setObjectName("actionTitle")
        desc = QLabel(action.description)
        desc.setWordWrap(True)
        desc.setObjectName("muted")
        button = QPushButton(action.button)
        button.clicked.connect(lambda: callback(action))
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(button)


class ToolboxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process: QProcess | None = None
        self._current_action = ""
        self._really_quit = False
        self._tray_hint_shown = False
        self._notification_target = ""
        self._last_health_signature: tuple[str, ...] | None = None
        self._last_ok_notification = 0.0
        self.update_process: QProcess | None = None
        self.toolbox_update_process: QProcess | None = None
        self.install_update_process: QProcess | None = None
        self.available_manifest: dict | None = None
        self.settings = self.load_settings()
        self.setWindowTitle(f"{APP_NAME} · {APP_VERSION}")
        self.setMinimumSize(1040, 700)
        icon = Path(__file__).with_name("rayko-toolbox.svg")
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self._build_ui()
        self._apply_style()
        self._setup_tray()
        self.refresh_dashboard()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(2000)
        self.health_timer = QTimer(self)
        self.health_timer.timeout.connect(self.check_health)
        self.health_timer.start(HEALTH_INTERVAL_MS)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_updates)
        self.update_timer.start(UPDATE_INTERVAL_MS)
        QTimer.singleShot(8000, self.check_health)
        QTimer.singleShot(20000, self.check_updates)
        QTimer.singleShot(30000, lambda: self.check_toolbox_update(silent=True))

    def load_settings(self) -> dict:
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {"automatic_toolbox_updates": False}

    def save_settings(self):
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self, APP_NAME, f"Impossible d’enregistrer les réglages :\n{error}")

    def _setup_tray(self):
        """Install the KDE system-tray icon and its menu."""
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray.setToolTip(f"{APP_NAME} · surveillance active")
        menu = QMenu(self)

        show_action = QAction("Afficher la Toolbox", self)
        show_action.triggered.connect(self.show_from_tray)
        menu.addAction(show_action)

        refresh_action = QAction("Actualiser maintenant", self)
        refresh_action.triggered.connect(self.refresh_dashboard)
        menu.addAction(refresh_action)

        updates_action = QAction("Vérifier les mises à jour", self)
        updates_action.triggered.connect(self.check_updates)
        menu.addAction(updates_action)
        menu.addSeparator()

        self.autostart_action = QAction("Lancer au démarrage de KDE", self)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(AUTOSTART_FILE.exists())
        self.autostart_action.toggled.connect(self.set_autostart)
        menu.addAction(self.autostart_action)
        menu.addSeparator()

        quit_action = QAction("Quitter complètement", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.messageClicked.connect(self.notification_clicked)
        self.tray.show()

    def notify(self, title: str, message: str, *, warning: bool = False, target: str = ""):
        self._notification_target = target
        icon = (QSystemTrayIcon.MessageIcon.Warning if warning
                else QSystemTrayIcon.MessageIcon.Information)
        self.tray.showMessage(title, message, icon, 7000)
        self.log.appendPlainText(f"[{datetime.now():%H:%M:%S}] 🔔 {title} — {message}")

    def notification_clicked(self):
        self.show_from_tray()
        if self._notification_target == "maintenance":
            self.show_page(1)
        elif self._notification_target == "dashboard":
            self.show_page(0)
        elif self._notification_target == "toolbox":
            self.show_page(4)

    def check_health(self):
        """Check local hardware health without changing the system."""
        problems: list[str] = []
        cpu_text = cpu_temperature()
        try:
            cpu_value = float(cpu_text.split()[0])
            if cpu_value >= 90:
                problems.append(f"température CPU élevée ({cpu_value:.0f} °C)")
        except (ValueError, IndexError):
            pass

        gpu_text = run_text([
            "nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"
        ])
        try:
            gpu_value = float(gpu_text.splitlines()[0])
            if gpu_value >= 85:
                problems.append(f"température GPU élevée ({gpu_value:.0f} °C)")
        except (ValueError, IndexError):
            if shutil.which("nvidia-smi"):
                problems.append("le GPU NVIDIA ne répond pas")

        for label, path in (("système", Path("/var")), ("SSD Jeux", GAME_DISK)):
            try:
                usage = shutil.disk_usage(path)
                percent = usage.used / usage.total * 100 if usage.total else 0
                if percent >= 95:
                    problems.append(f"stockage {label} presque plein ({percent:.0f} %)")
            except OSError:
                if label == "SSD Jeux":
                    problems.append("SSD Jeux non monté")

        signature = tuple(problems)
        now = time.monotonic()
        if problems and signature != self._last_health_signature:
            self.notify("Attention requise", " • ".join(problems), warning=True, target="dashboard")
        elif not problems and (self._last_health_signature is None or
                               self._last_health_signature or
                               now - self._last_ok_notification >= OK_NOTIFICATION_INTERVAL):
            self.notify("Tout va bien", "Températures et espaces de stockage sont normaux.", target="dashboard")
            self._last_ok_notification = now
        self._last_health_signature = signature

    def check_updates(self):
        """Asynchronously check Bazzite and Flatpak updates; never install them."""
        if self.update_process and self.update_process.state() != QProcess.ProcessState.NotRunning:
            return
        command = r"""
system=unknown
if command -v rpm-ostree >/dev/null; then
  rpm-ostree upgrade --check --unchanged-exit-77 >/dev/null 2>&1
  case $? in 0) system=yes ;; 77) system=no ;; *) system=unknown ;; esac
fi
flatpak_count=0
if command -v flatpak >/dev/null; then
  flatpak_count=$(flatpak remote-ls --updates --columns=application 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
fi
printf 'SYSTEM=%s\nFLATPAK=%s\n' "$system" "$flatpak_count"
"""
        self.update_process = QProcess(self)
        self.update_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.update_process.finished.connect(self.update_check_finished)
        self.update_process.start("bash", ["-c", command])

    def update_check_finished(self, _exit_code: int, _status):
        if not self.update_process:
            return
        output = bytes(self.update_process.readAllStandardOutput()).decode(errors="replace")
        values = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value
        system_update = values.get("SYSTEM") == "yes"
        try:
            flatpak_count = int(values.get("FLATPAK", "0"))
        except ValueError:
            flatpak_count = 0
        available = int(system_update) + flatpak_count
        if available:
            details = []
            if system_update:
                details.append("une mise à jour Bazzite")
            if flatpak_count:
                details.append(f"{flatpak_count} mise(s) à jour Flatpak")
            self.notify(
                "Mises à jour disponibles",
                " et ".join(details) + ". Cliquez ici pour ouvrir Maintenance.",
                target="maintenance",
            )
        else:
            self.log.appendPlainText(f"[{datetime.now():%H:%M:%S}] Vérification : aucune mise à jour détectée.")

    def tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_from_tray()

    def show_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def set_autostart(self, enabled: bool):
        try:
            if enabled:
                AUTOSTART_FILE.parent.mkdir(parents=True, exist_ok=True)
                launcher = Path.home() / ".local/bin/rayko-toolbox"
                icon = Path.home() / ".local/share/icons/hicolor/scalable/apps/rayko-toolbox.svg"
                AUTOSTART_FILE.write_text(
                    "[Desktop Entry]\n"
                    "Type=Application\n"
                    f"Name={APP_NAME}\n"
                    f"Exec={launcher} --background\n"
                    f"Icon={icon}\n"
                    "Terminal=false\n"
                    "X-KDE-autostart-after=panel\n"
                    "X-GNOME-Autostart-enabled=true\n",
                    encoding="utf-8",
                )
                self.tray.showMessage(APP_NAME, "Démarrage automatique activé.",
                                      QSystemTrayIcon.MessageIcon.Information, 2500)
            elif AUTOSTART_FILE.exists():
                AUTOSTART_FILE.unlink()
        except OSError as error:
            self.autostart_action.blockSignals(True)
            self.autostart_action.setChecked(not enabled)
            self.autostart_action.blockSignals(False)
            QMessageBox.warning(self, APP_NAME, f"Impossible de modifier le démarrage automatique :\n{error}")

    def quit_application(self):
        self._really_quit = True
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            answer = QMessageBox.question(
                self, APP_NAME, "Une opération est en cours. L’arrêter et quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self._really_quit = False
                return
            self.process.kill()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        if self._really_quit:
            event.accept()
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            event.accept()
            QApplication.quit()
            return
        event.ignore()
        self.hide()
        if not self._tray_hint_shown:
            self.tray.showMessage(
                APP_NAME,
                "La Toolbox continue de fonctionner en arrière-plan. "
                "Cliquez sur son icône pour la rouvrir.",
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )
            self._tray_hint_shown = True

    def _build_ui(self):
        root = QWidget()
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(20, 28, 20, 24)
        logo = QLabel("RAYKO\nTOOLBOX")
        logo.setObjectName("logo")
        subtitle = QLabel(f"BAZZITE · KDE · V{APP_VERSION}")
        subtitle.setObjectName("eyebrow")
        nav.addWidget(logo)
        nav.addWidget(subtitle)
        nav.addSpacing(34)
        self.nav_buttons = []
        for index, text in enumerate(("Tableau de bord", "Maintenance", "Diagnostics", "Jeux & données", "Toolbox & mises à jour")):
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.show_page(i))
            nav.addWidget(button)
            self.nav_buttons.append(button)
        nav.addStretch()
        power_row = QHBoxLayout()
        for text, mode in (("Redémarrer", "reboot"), ("Éteindre", "poweroff")):
            button = QPushButton(text)
            button.setObjectName("powerButton")
            button.clicked.connect(lambda checked=False, m=mode: self.power_action(m))
            power_row.addWidget(button)
        nav.addLayout(power_row)
        version = QLabel(f"Version {APP_VERSION}\nV1 Bash conservée")
        version.setObjectName("muted")
        nav.addWidget(version)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(28, 24, 28, 20)
        header = QHBoxLayout()
        self.page_title = QLabel("Tableau de bord")
        self.page_title.setObjectName("pageTitle")
        live_status = QLabel("● Auto · 2 s")
        live_status.setObjectName("liveStatus")
        refresh = QPushButton("Actualiser")
        refresh.clicked.connect(self.refresh_dashboard)
        header.addWidget(self.page_title)
        header.addStretch()
        header.addWidget(live_status)
        header.addWidget(refresh)
        right_layout.addLayout(header)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_page())
        self.stack.addWidget(self.actions_page(self.maintenance_actions()))
        self.stack.addWidget(self.actions_page(self.diagnostic_actions()))
        self.stack.addWidget(self.actions_page(self.data_actions()))
        self.stack.addWidget(self.toolbox_update_page())
        right_layout.addWidget(self.stack, 1)

        log_header = QHBoxLayout()
        log_label = QLabel("Journal des opérations")
        log_label.setObjectName("sectionTitle")
        self.status_label = QLabel("Prêt")
        self.status_label.setObjectName("status")
        clear = QPushButton("Effacer")
        clear.clicked.connect(lambda: self.log.clear())
        self.stop_button = QPushButton("Arrêter")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_process)
        log_header.addWidget(log_label)
        log_header.addWidget(self.status_label)
        log_header.addStretch()
        log_header.addWidget(clear)
        log_header.addWidget(self.stop_button)
        right_layout.addLayout(log_header)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(5000)
        self.log.setMinimumHeight(150)
        self.log.setPlaceholderText("Les sorties des commandes apparaîtront ici.")
        right_layout.addWidget(self.log)

        shell.addWidget(sidebar)
        shell.addWidget(right, 1)
        self.setCentralWidget(root)
        self.show_page(0)

    def dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Vue instantanée de la machine")
        intro.setObjectName("sectionTitle")
        layout.addWidget(intro)
        grid = QGridLayout()
        grid.setSpacing(14)
        specs = (
            ("cpu", "CPU", "#7c5cff"), ("cpu_temp", "Température CPU", "#ffb454"),
            ("memory", "Mémoire", "#4dd4ac"), ("gpu", "GPU NVIDIA", "#76b900"),
            ("gpu_temp", "Température GPU", "#76b900"), ("root_disk", "Stockage système", "#53a7ff"),
            ("game_disk", "SSD Jeux", "#ff6b9a"), ("system", "Système", "#9aa4b2"),
        )
        self.metrics = {}
        for i, (key, title, accent) in enumerate(specs):
            card = MetricCard(title, accent)
            self.metrics[key] = card.value
            grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def toolbox_update_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("actionCard")
        card_layout = QVBoxLayout(card)
        title = QLabel("Rayko Bazzite Toolbox")
        title.setObjectName("actionTitle")
        self.toolbox_version_label = QLabel(f"Version installée : {APP_VERSION}")
        self.toolbox_update_status = QLabel("Aucune vérification effectuée.")
        self.toolbox_update_status.setObjectName("muted")
        self.toolbox_update_status.setWordWrap(True)
        self.toolbox_notes = QLabel(
            "Version 2.1.0\n• Gestion des versions et mises à jour en ligne\n"
            "• Surveillance système et notifications\n• Interface en arrière-plan"
        )
        self.toolbox_notes.setWordWrap(True)
        self.auto_toolbox_updates = QCheckBox("Télécharger et installer automatiquement les nouvelles versions")
        self.auto_toolbox_updates.setChecked(bool(self.settings.get("automatic_toolbox_updates", False)))
        self.auto_toolbox_updates.toggled.connect(self.set_automatic_toolbox_updates)
        buttons = QHBoxLayout()
        check_button = QPushButton("Vérifier maintenant")
        check_button.clicked.connect(lambda: self.check_toolbox_update(silent=False))
        self.install_toolbox_button = QPushButton("Installer la mise à jour")
        self.install_toolbox_button.setEnabled(False)
        self.install_toolbox_button.clicked.connect(self.install_toolbox_update)
        buttons.addWidget(check_button)
        buttons.addWidget(self.install_toolbox_button)
        buttons.addStretch()
        card_layout.addWidget(title)
        card_layout.addWidget(self.toolbox_version_label)
        card_layout.addWidget(self.toolbox_update_status)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.toolbox_notes)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.auto_toolbox_updates)
        card_layout.addLayout(buttons)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def set_automatic_toolbox_updates(self, enabled: bool):
        self.settings["automatic_toolbox_updates"] = enabled
        self.save_settings()

    @staticmethod
    def version_tuple(value: str) -> tuple[int, ...]:
        try:
            return tuple(int(part) for part in value.split("."))
        except ValueError:
            return (0,)

    def check_toolbox_update(self, silent: bool = False):
        if self.toolbox_update_process and self.toolbox_update_process.state() != QProcess.ProcessState.NotRunning:
            return
        self.toolbox_update_status.setText("Recherche d’une nouvelle version…")
        self.toolbox_update_process = QProcess(self)
        self.toolbox_update_process.setProperty("silent", silent)
        self.toolbox_update_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.toolbox_update_process.finished.connect(self.toolbox_update_check_finished)
        self.toolbox_update_process.start("curl", ["-fsSL", "--max-time", "15", UPDATE_MANIFEST_URL])

    def toolbox_update_check_finished(self, exit_code: int, _status):
        process = self.toolbox_update_process
        if not process:
            return
        silent = bool(process.property("silent"))
        raw = bytes(process.readAllStandardOutput()).decode(errors="replace")
        if exit_code != 0:
            self.toolbox_update_status.setText("Impossible de joindre le service de mise à jour.")
            if not silent:
                QMessageBox.warning(self, "Mise à jour", "La vérification en ligne a échoué. Réessayez plus tard.")
            return
        try:
            manifest = json.loads(raw)
            remote_version = str(manifest["version"])
            files = manifest["files"]
            if not isinstance(files, list) or not files:
                raise ValueError
        except (ValueError, KeyError, TypeError):
            self.toolbox_update_status.setText("Le fichier de mise à jour en ligne est invalide.")
            return
        if self.version_tuple(remote_version) > self.version_tuple(APP_VERSION):
            self.available_manifest = manifest
            notes = str(manifest.get("notes", "Nouvelle version disponible."))
            self.toolbox_update_status.setText(f"Version {remote_version} disponible.")
            self.toolbox_notes.setText(notes)
            self.install_toolbox_button.setEnabled(True)
            self.notify("Mise à jour de la Toolbox", f"Version {remote_version} disponible. Cliquez pour l’ouvrir.", target="toolbox")
            if self.settings.get("automatic_toolbox_updates", False):
                self.install_toolbox_update(automatic=True)
        else:
            self.available_manifest = None
            self.install_toolbox_button.setEnabled(False)
            self.toolbox_update_status.setText(f"La version {APP_VERSION} est à jour.")
            if not silent:
                QMessageBox.information(self, "Mise à jour", "La Toolbox est déjà à jour.")

    def install_toolbox_update(self, checked=False, automatic: bool = False):
        manifest = self.available_manifest
        if not manifest:
            return
        if not automatic:
            answer = QMessageBox.question(
                self, "Installer la mise à jour",
                f"Installer la version {manifest['version']} ? Une copie de secours sera conservée.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        install_dir = Path(__file__).resolve().parent
        commands = ["set -euo pipefail", "stage=$(mktemp -d)", "trap 'rm -rf -- \"$stage\"' EXIT"]
        for item in manifest["files"]:
            name = str(item.get("name", ""))
            url = str(item.get("url", ""))
            checksum = str(item.get("sha256", ""))
            if name not in {"rayko_toolbox.py", "rayko-toolbox", "rayko-toolbox.svg"} or len(checksum) != 64:
                self.toolbox_update_status.setText("Manifest refusé : fichier ou empreinte invalide.")
                return
            commands.append(f"curl -fsSL --max-time 30 {shlex.quote(url)} -o \"$stage/{name}\"")
            commands.append(f"echo {shlex.quote(checksum + '  ')}\"$stage/{name}\" | sha256sum -c -")
        backup_dir = install_dir / "previous-version"
        commands.append(f"mkdir -p {shlex.quote(str(backup_dir))}")
        for item in manifest["files"]:
            name = str(item["name"])
            target = install_dir / name
            commands.append(f"[ ! -e {shlex.quote(str(target))} ] || cp -a {shlex.quote(str(target))} {shlex.quote(str(backup_dir / name))}")
            mode = "755" if name in {"rayko_toolbox.py", "rayko-toolbox"} else "644"
            commands.append(f"install -m {mode} \"$stage/{name}\" {shlex.quote(str(target))}")
        self.toolbox_update_status.setText("Installation de la nouvelle version…")
        self.install_toolbox_button.setEnabled(False)
        self.install_update_process = QProcess(self)
        self.install_update_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.install_update_process.finished.connect(self.toolbox_update_install_finished)
        self.install_update_process.start("bash", ["-c", "\n".join(commands)])

    def toolbox_update_install_finished(self, exit_code: int, _status):
        if exit_code != 0:
            output = bytes(self.install_update_process.readAllStandardOutput()).decode(errors="replace") if self.install_update_process else ""
            self.toolbox_update_status.setText("Échec de l’installation. La version actuelle est conservée.")
            self.log.appendPlainText(output)
            return
        self.toolbox_update_status.setText("Mise à jour installée. Redémarrage nécessaire.")
        answer = QMessageBox.question(
            self, "Mise à jour installée", "La nouvelle version est installée. Redémarrer la Toolbox maintenant ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            QProcess.startDetached(str(Path.home() / ".local/bin/rayko-toolbox"), [])
            self.quit_application()

    def actions_page(self, actions: list[Action]) -> QWidget:
        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(14)
        for i, action in enumerate(actions):
            grid.addWidget(ActionCard(action, self.launch_action), i // 2, i % 2)
        grid.setRowStretch((len(actions) + 1) // 2, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        return scroll

    def maintenance_actions(self) -> list[Action]:
        update = """set -o pipefail
echo '=== Mise à jour de Bazzite ==='
if command -v ujust >/dev/null; then ujust update; else rpm-ostree upgrade; fi
echo; echo '=== Mise à jour des Flatpak ==='; flatpak update -y
if command -v brew >/dev/null; then echo; echo '=== Mise à jour Homebrew ==='; brew update && brew upgrade; fi"""
        clean = """set -o pipefail
echo '=== Nettoyage prudent ==='
flatpak uninstall --unused -y
echo; echo 'Suppression des miniatures utilisateur…'
find "$HOME/.cache/thumbnails" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + 2>/dev/null || true
echo; du -sh "$HOME/.cache" 2>/dev/null || true
echo 'Le cache général, Steam et Lutris n’ont pas été supprimés.'"""
        flatpak = """set -o pipefail
echo '=== Réparation Flatpak utilisateur ==='; flatpak repair --user
echo; echo '=== Applications installées ==='; flatpak list --app
echo; echo '=== Runtimes installés ==='; flatpak list --runtime"""
        return [
            Action("Mettre à jour Bazzite", "Système atomique, Flatpak et Homebrew si présent.", update,
                   "Cette opération peut télécharger et installer des mises à jour. Continuer ?", "Mettre à jour"),
            Action("Nettoyage prudent", "Retire les Flatpak inutilisés et les miniatures. Les caches de jeux restent intacts.", clean,
                   "Supprimer les Flatpak inutilisés et les miniatures ?", "Nettoyer"),
            Action("Vérifier Flatpak", "Répare l’installation utilisateur et affiche les applications et runtimes inutilisés.", flatpak,
                   "Lancer la réparation Flatpak de votre compte ?", "Vérifier"),
        ]

    def diagnostic_actions(self) -> list[Action]:
        network = """echo '=== Interfaces ==='; ip -br addr
echo; echo '=== Route par défaut ==='; ip route | grep default || true
echo; echo '=== DNS ==='; resolvectl status 2>/dev/null | grep -E 'DNS Servers|Current DNS' || true
echo; ping -c 2 -W 2 1.1.1.1 >/dev/null && echo '✓ Internet accessible' || echo '✗ Internet inaccessible'
getent hosts github.com >/dev/null && echo '✓ Résolution DNS fonctionnelle' || echo '✗ Résolution DNS en échec'
curl -Is --max-time 5 https://github.com >/dev/null && echo '✓ GitHub accessible' || echo '✗ GitHub inaccessible'
curl -Is --max-time 5 https://ghcr.io >/dev/null && echo '✓ GHCR accessible' || echo '✗ GHCR inaccessible'"""
        nvidia = """echo '=== NVIDIA ==='
if ! command -v nvidia-smi >/dev/null; then echo 'nvidia-smi indisponible'; exit 1; fi
nvidia-smi; echo; echo '=== Modules ==='; lsmod | grep -E '^nvidia' || true
echo; echo '=== Pilote ==='; modinfo nvidia 2>/dev/null | grep '^version:' | head -1 || true
echo; echo '=== Cartes graphiques PCI ==='; lspci | grep -Ei 'VGA|3D' || true"""
        return [
            Action("Diagnostic réseau", "Interfaces, route, DNS et accès à Internet, GitHub et GHCR.", network, button="Analyser"),
            Action("Diagnostic NVIDIA", "État GPU, pilote, modules du noyau et périphérique PCI.", nvidia, button="Analyser"),
            Action("Rapport complet", "Crée un rapport texte horodaté dans ~/Rayko-Reports.", "__REPORT__", button="Générer"),
        ]

    def data_actions(self) -> list[Action]:
        game_disk = f"""echo '=== SSD Jeux : {GAME_DISK} ==='
if [ ! -d {shlex.quote(str(GAME_DISK))} ]; then echo 'Le SSD Jeux n’est pas monté.'; exit 1; fi
df -h {shlex.quote(str(GAME_DISK))}; echo; echo '=== Plus gros dossiers accessibles ==='
du -h --max-depth=1 {shlex.quote(str(GAME_DISK))} 2>/dev/null | sort -hr | head -20"""
        steam = """echo '=== Steam ==='
for path in "$HOME/.local/share/Steam" "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"; do
  [ -d "$path" ] && echo "✓ Installation détectée : $path"
done
echo; echo '=== Proton / outils de compatibilité ==='
find "$HOME/.local/share/Steam/compatibilitytools.d" "$HOME/.steam/root/compatibilitytools.d" "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort -u
echo; pgrep -x steam >/dev/null && echo '✓ Steam est lancé' || echo 'ℹ Steam n’est pas lancé'"""
        return [
            Action("Analyser le SSD Jeux", f"Espace et dossiers les plus volumineux de {GAME_DISK}.", game_disk, button="Analyser"),
            Action("Steam & Proton", "Détecte Steam natif ou Flatpak, Proton et l’état du client.", steam, button="Vérifier"),
            Action("Sauvegarder les configurations", "Archive les réglages utilisateur, Lutris et la configuration Steam dans ~/Rayko-Backups.", "__BACKUP__",
                   "Créer une archive de vos configurations ? Selon votre dossier .config, cela peut prendre du temps.", "Sauvegarder"),
        ]

    def show_page(self, index: int):
        titles = ("Tableau de bord", "Maintenance", "Diagnostics", "Jeux & données", "Toolbox & mises à jour")
        self.stack.setCurrentIndex(index)
        self.page_title.setText(titles[index])
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def refresh_dashboard(self):
        cpu = run_text(["sh", "-c", "lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -1"])
        gpu, gpu_temp = gpu_summary()
        os_name = "Bazzite"
        try:
            for line in Path("/etc/os-release").read_text().splitlines():
                if line.startswith("PRETTY_NAME="):
                    os_name = line.split("=", 1)[1].strip('"')
        except OSError:
            pass
        values = {
            "cpu": cpu or "Non disponible", "cpu_temp": cpu_temperature(), "memory": memory_summary(),
            "gpu": gpu, "gpu_temp": gpu_temp, "root_disk": disk_summary(Path("/var")),
            "game_disk": disk_summary(GAME_DISK), "system": os_name,
        }
        for key, value in values.items():
            self.metrics[key].setText(value)

    def launch_action(self, action: Action):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.information(self, APP_NAME, "Une opération est déjà en cours.")
            return
        if action.confirmation:
            answer = QMessageBox.question(self, action.title, action.confirmation,
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                          QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Yes:
                return
        command = action.command
        if command == "__REPORT__":
            command = self.report_command()
        elif command == "__BACKUP__":
            command = self.backup_command()
        self.run_command(action.title, command)

    def run_command(self, title: str, command: str):
        self.log.appendPlainText(f"\n[{datetime.now():%H:%M:%S}] ▶ {title}\n")
        self._current_action = title
        self.status_label.setText("En cours…")
        self.stop_button.setEnabled(True)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_process_output)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.process.start("bash", ["-c", command])

    def read_process_output(self):
        if not self.process:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        if data:
            self.log.moveCursor(self.log.textCursor().MoveOperation.End)
            self.log.insertPlainText(data)
            self.log.ensureCursorVisible()

    def process_finished(self, exit_code: int, _status):
        self.read_process_output()
        word = "terminée" if exit_code == 0 else f"terminée avec le code {exit_code}"
        self.log.appendPlainText(f"\n[{datetime.now():%H:%M:%S}] ■ Opération {word}.\n")
        self.status_label.setText("Prêt" if exit_code == 0 else "Erreur")
        self.stop_button.setEnabled(False)
        self.refresh_dashboard()

    def process_error(self, error):
        self.log.appendPlainText(f"Impossible de lancer la commande : {error}")
        self.status_label.setText("Erreur")
        self.stop_button.setEnabled(False)

    def stop_process(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            QTimer.singleShot(2500, lambda: self.process and self.process.kill()
                              if self.process.state() != QProcess.ProcessState.NotRunning else None)

    def report_command(self) -> str:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORT_DIR / f"bazzite-report-{datetime.now():%Y-%m-%d_%H-%M-%S}.txt"
        q = shlex.quote(str(path))
        return f"""REPORT={q}
{{
echo '========================================'; echo 'RAYKO BAZZITE TOOLBOX V2 - RAPPORT'; echo '========================================'
echo; echo 'DATE'; date
echo; echo 'SYSTÈME'; cat /etc/os-release
echo; echo 'KERNEL'; uname -a
echo; echo 'CPU'; lscpu
echo; echo 'RAM'; free -h
echo; echo 'TEMPÉRATURES'; command -v sensors >/dev/null && sensors || true
echo; echo 'STOCKAGE'; df -h
echo; echo 'GPU'; lspci | grep -Ei 'VGA|3D' || true
echo; echo 'NVIDIA'; command -v nvidia-smi >/dev/null && nvidia-smi || true
echo; echo 'RÉSEAU'; ip -br addr; echo; ip route
echo; echo 'RPM-OSTREE'; rpm-ostree status 2>/dev/null || true
echo; echo 'FLATPAK'; flatpak list 2>/dev/null || true
}} > "$REPORT" 2>&1
echo "✓ Rapport créé : $REPORT"""

    def backup_command(self) -> str:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        path = BACKUP_DIR / f"bazzite-config-{datetime.now():%Y-%m-%d_%H-%M-%S}.tar.gz"
        q = shlex.quote(str(path))
        return f"""set -o pipefail
cd "$HOME" || exit 1
items=()
[ -d .config ] && items+=(.config)
[ -d .local/share/lutris ] && items+=(.local/share/lutris)
[ -d .local/share/Steam/config ] && items+=(.local/share/Steam/config)
[ -d .var/app/com.valvesoftware.Steam/.local/share/Steam/config ] && items+=(.var/app/com.valvesoftware.Steam/.local/share/Steam/config)
if [ ${{#items[@]}} -eq 0 ]; then echo 'Aucune configuration trouvée.'; exit 1; fi
tar --exclude='*/Cache/*' --exclude='*/cache/*' --exclude='*/GPUCache/*' -czf {q} "${{items[@]}}"
echo '✓ Sauvegarde créée : {path}'; du -h {q}"""

    def power_action(self, mode: str):
        verb = "redémarrer" if mode == "reboot" else "éteindre"
        answer = QMessageBox.warning(
            self, f"Confirmer : {verb}",
            f"Voulez-vous vraiment {verb} l’ordinateur maintenant ?\n\nEnregistrez d’abord vos documents ouverts.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            QProcess.startDetached("systemctl", [mode])

    def _apply_style(self):
        self.setStyleSheet("""
            * { font-family: Inter, "Noto Sans", sans-serif; font-size: 13px; }
            QMainWindow, QWidget { background: #11141b; color: #eef1f7; }
            #sidebar { background: #171b24; border-right: 1px solid #292f3d; }
            #logo { font-size: 25px; font-weight: 800; letter-spacing: 2px; color: #ffffff; }
            #eyebrow, #metricTitle { color: #858fa2; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
            #pageTitle { font-size: 26px; font-weight: 750; }
            #sectionTitle { font-size: 15px; font-weight: 700; margin: 4px 0; }
            #metricValue { font-size: 17px; font-weight: 650; }
            #actionTitle { font-size: 16px; font-weight: 700; }
            #muted { color: #929bad; }
            #status { color: #4dd4ac; padding-left: 10px; }
            #liveStatus { color: #4dd4ac; font-size: 12px; padding-right: 6px; }
            #card, #actionCard { background: #1a1f2a; border: 1px solid #2b3241; border-radius: 10px; }
            #card { min-height: 86px; }
            #actionCard { min-height: 135px; }
            QPushButton { background: #282f3e; color: #f4f6fa; border: 1px solid #394256; border-radius: 7px; padding: 8px 12px; }
            QPushButton:hover { background: #343d50; border-color: #7c5cff; }
            QPushButton:disabled { color: #616a7b; background: #20242e; }
            #navButton { text-align: left; border: none; background: transparent; padding: 11px 12px; }
            #navButton:hover { background: #202634; }
            #navButton:checked { background: #2c2750; color: #b9acff; border-left: 3px solid #8b70ff; }
            #powerButton { font-size: 11px; padding: 7px 5px; }
            QPlainTextEdit { background: #0c0f14; color: #cdd5e3; border: 1px solid #2b3241; border-radius: 8px; padding: 8px; font-family: "JetBrains Mono", monospace; }
            QScrollArea { background: transparent; }
            QScrollBar:vertical { background: #151922; width: 10px; }
            QScrollBar::handle:vertical { background: #394256; border-radius: 5px; min-height: 24px; }
        """)


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Rayko")
    app.setDesktopFileName("rayko-bazzite-toolbox")
    icon_path = Path(__file__).with_name("rayko-toolbox.svg")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#11141b"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#eef1f7"))
    app.setPalette(palette)
    window = ToolboxWindow()
    if "--background" not in sys.argv:
        window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
