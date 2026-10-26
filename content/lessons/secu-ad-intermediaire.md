# Sécurité Active Directory

## Introduction

Active Directory centralise identités, groupes, politiques et authentification dans de nombreux environnements Windows. Le compromis d’un compte privilégié ou d’un contrôleur de domaine peut affecter une grande partie de l’organisation.

La protection repose sur la séparation des comptes d’administration, la limitation des privilèges, des GPO vérifiées et une gestion sûre des identifiants. Kerberos, LDAP et SMB doivent suivre des réglages adaptés ; délégations excessives et comptes de service mal gérés augmentent les risques.

La résilience nécessite une surveillance des authentifications et changements d’annuaire, ainsi que des sauvegardes de contrôleurs de domaine testées. Les politiques d’audit doivent être vérifiées dans un environnement contrôlé avant généralisation, et les identités privilégiées réservées aux tâches nécessaires.

## Concepts clés

- **Comptes séparés** : ne pas utiliser une identité privilégiée pour les usages quotidiens.
- **GPO** : centraliser paramètres et restrictions.
- **Kerberos** : protéger les comptes de service et surveiller les usages anormaux.
- **LAPS / gMSA** : mieux gérer secrets locaux et comptes de service.
- **Contrôleurs de domaine** : isoler l’administration et tester les sauvegardes.

## Méthode pratique

1. Examine groupes privilégiés, délégations et comptes inactifs.
2. Contrôle les GPO et les comptes de service.
3. Sépare postes utilisateurs et postes d’administration.
4. Centralise les événements et teste la récupération du domaine.

## À retenir

La sécurité AD commence par l’hygiène des identités et la protection des chemins d’administration.
