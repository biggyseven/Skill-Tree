# Sécurité des services réseau

## Introduction

DNS, DHCP, NTP, SNMP, SSH et syslog sont des services d’infrastructure essentiels. Une compromission peut détourner les utilisateurs, perturber l’adressage, désynchroniser les journaux ou révéler des informations sur le réseau.

Chaque service doit être limité à son rôle : protéger l’administration DNS, contrôler les serveurs DHCP, utiliser des sources NTP fiables et préférer SNMPv3 avec authentification et confidentialité. SSH et syslog doivent être restreints et configurés sans identifiants par défaut.

Une exploitation sûre combine segmentation, ACL dédiées, correctifs, journaux et sauvegardes de configuration. La synchronisation de l’heure aide à corréler les événements, tandis que la restauration testée accélère le rétablissement des services après incident.

## Concepts clés

- **DNS** : limiter les transferts de zone et l’accès d’administration.
- **DHCP** : contrôler les serveurs autorisés ; DHCP Snooping si disponible.
- **NTP** : sources de temps fiables et surveillance des écarts.
- **SNMPv3** : authentification et confidentialité.
- **SSH / syslog** : limiter l’administration et centraliser les événements.

## Méthode pratique

1. Inventorie les services et leurs clients légitimes.
2. Limite les sources et ports autorisés.
3. Retire les protocoles non chiffrés et secrets par défaut.
4. Vérifie synchronisation horaire, collecte et restauration de configuration.

## À retenir

Les services d’infrastructure forment une base de confiance qui doit être durcie et surveillée.
