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
# Rayko Bazzite Toolbox V2

Version actuelle : **2.1.0**

Interface graphique KDE/Qt pour Bazzite. Elle est indépendante de la V1 Bash et ne modifie pas
`~/Documents/Scripts/rayko-bazzite-toolbox.sh`.

## Installation

Ouvrez ce dossier dans Dolphin, puis lancez `install.sh` dans un terminal :

```bash
./install.sh
```

L’application apparaît ensuite dans le menu Applications de KDE sous le nom **Rayko Bazzite Toolbox**.
Si le menu était déjà ouvert, fermez-le et rouvrez-le. On peut aussi lancer l’application avec :

```bash
rayko-toolbox
```

## Essai sans installation

```bash
./rayko-toolbox
```

## Fonctions

- tableau de bord CPU, RAM, GPU NVIDIA, températures et stockage ;
- état du SSD Jeux `/var/mnt/jeux` ;
- mise à jour Bazzite, Flatpak et Homebrew si présent ;
- nettoyage prudent sans vider les caches Steam/Lutris ;
- diagnostics réseau et NVIDIA ;
- vérification Flatpak, Steam et Proton ;
- rapport dans `~/Rayko-Reports` ;
- sauvegarde des configurations dans `~/Rayko-Backups` ;
- journal intégré, arrêt d’une commande et confirmations d’alimentation.
- gestion des versions et mises à jour manuelles ou automatiques depuis GitHub.

Une seule opération longue est exécutée à la fois. Les commandes d’administration peuvent afficher
la demande d’authentification habituelle de Bazzite dans le journal ou dans une fenêtre système.

## Désinstallation

```bash
./uninstall.sh
```

Les rapports, sauvegardes et la V1 sont conservés.
