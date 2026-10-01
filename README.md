# Rayko Bazzite Toolbox V2

Version actuelle : **2.1.1**

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
- export du journal intégré au format texte dans `~/Rayko-Reports`.

Une seule opération longue est exécutée à la fois. Les commandes d’administration peuvent afficher
la demande d’authentification habituelle de Bazzite dans le journal ou dans une fenêtre système.

## Désinstallation

```bash
./uninstall.sh
```

Les rapports, sauvegardes et la V1 sont conservés.
