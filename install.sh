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
                                          Memory: 5.88 GiB / 31.01 GiB (19%)
                                          Swap: 0 B / 15.51 GiB (0%)
                                          Disk (/): 46.63 MiB / 46.63 MiB (100%) - overlay [Read-only]
                                          Disk (/etc): 423.38 GiB / 444.54 GiB (95%) - btrfs
                                          Disk (/var/mnt/jeux): 740.23 GiB / 953.87 GiB (78%) - ntfs3
                                          Local IP (eno1): 192.168.1.35/24
                                          Locale: C.UTF-8
                                          
                                          [40m   [41m   [42m   [43m   [44m   [45m   [46m   [47m   [m
                                          [5m[100m   [101m   [102m   [103m   [104m   [105m   [106m   [107m   [m
#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/rayko-bazzite-toolbox"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

if ! python3 -c 'import PySide6' >/dev/null 2>&1; then
    echo "Erreur : PySide6 n’est pas disponible pour Python 3."
    echo "Sur Bazzite, vérifiez d’abord : python3 -c 'import PySide6'"
    exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$APP_DIR" "$ICON_DIR"
install -m 755 "$SOURCE_DIR/rayko_toolbox.py" "$INSTALL_DIR/rayko_toolbox.py"
install -m 755 "$SOURCE_DIR/rayko-toolbox" "$INSTALL_DIR/rayko-toolbox"
install -m 644 "$SOURCE_DIR/rayko-toolbox.svg" "$INSTALL_DIR/rayko-toolbox.svg"
ln -sfn "$INSTALL_DIR/rayko-toolbox" "$BIN_DIR/rayko-toolbox"
install -m 644 "$SOURCE_DIR/rayko-toolbox.svg" "$ICON_DIR/rayko-toolbox.svg"

sed \
    -e "s|^Exec=.*|Exec=$BIN_DIR/rayko-toolbox|" \
    -e "s|^Icon=.*|Icon=$ICON_DIR/rayko-toolbox.svg|" \
    "$SOURCE_DIR/rayko-bazzite-toolbox.desktop" > "$APP_DIR/rayko-bazzite-toolbox.desktop"
chmod 644 "$APP_DIR/rayko-bazzite-toolbox.desktop"

command -v update-desktop-database >/dev/null && update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
command -v kbuildsycoca6 >/dev/null && kbuildsycoca6 >/dev/null 2>&1 || true

echo "Rayko Bazzite Toolbox V2 est installée."
echo "Ouvrez le menu Applications de KDE et cherchez : Rayko Bazzite Toolbox"
echo "La V1 n’a pas été modifiée."
