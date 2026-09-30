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
