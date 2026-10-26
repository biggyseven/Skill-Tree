# Sécurité des systèmes Linux

## Introduction

La sécurité Linux repose sur une configuration minimale, des privilèges limités, des correctifs réguliers et la détection des anomalies. Les comptes, groupes et permissions Unix contrôlent l’accès aux fichiers et aux opérations sensibles.

Le durcissement inclut la désactivation des services inutiles, la protection de SSH, le contrôle de sudo, la mise à jour des paquets et des règles de pare-feu hôte. Les changements d’accès à distance doivent être préparés avec un moyen de secours afin d’éviter de se verrouiller hors du serveur.

La supervision s’appuie sur les journaux d’authentification, les événements système, l’audit des comptes et des tâches planifiées, ainsi que sur des sauvegardes testées. Les outils de détection apportent de la valeur lorsqu’ils s’intègrent à une procédure de triage et de réponse définie.

## Concepts clés

- **Moindre privilège** : comptes nominatifs, sudo limité et permissions minimales.
- **SSH** : clés protégées et accès d’administration restreints.
- **Services** : retirer ceux qui ne sont pas nécessaires.
- **Pare-feu** : `nftables` ou outil équivalent avec règles documentées.
- **Journaux** : `journalctl` et événements d’authentification.

## Méthode pratique

1. Contrôle les ports en écoute avec `ss -lntup`.
2. Mets le système à jour et examine comptes et services.
3. Vérifie SSH et les droits des clés.
4. Applique les règles réseau avec une session de secours.
5. Contrôle les journaux et teste une restauration.

## À retenir

Le durcissement doit être progressif, documenté et vérifié après chaque changement.
