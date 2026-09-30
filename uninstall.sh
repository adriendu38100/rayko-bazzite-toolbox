#!/usr/bin/env bash
set -euo pipefail

rm -f -- "$HOME/.local/bin/rayko-toolbox"
rm -f -- "$HOME/.local/share/applications/rayko-bazzite-toolbox.desktop"
rm -f -- "$HOME/.local/share/icons/hicolor/scalable/apps/rayko-toolbox.svg"
rm -rf -- "$HOME/.local/share/rayko-bazzite-toolbox"
command -v update-desktop-database >/dev/null && update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
echo "Rayko Bazzite Toolbox V2 a été désinstallée. La V1 et vos rapports/sauvegardes sont conservés."
