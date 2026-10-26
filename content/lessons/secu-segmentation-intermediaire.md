# Segmentation réseau

## Introduction

La segmentation divise un réseau en zones selon les rôles, les actifs ou les niveaux de confiance. Elle vise à réduire les communications inutiles et à limiter la progression d’un intrus après la compromission d’un appareil.

Les VLAN et sous-réseaux séparent des domaines, mais ne suffisent pas si les flux entre eux restent librement autorisés. Des ACL, pare-feu, VRF ou politiques hôtes peuvent appliquer une politique explicite ; la microsegmentation permet des contrôles plus granulaires entre charges de travail.

Une démarche fiable commence par l’identification des flux légitimes et des dépendances applicatives. Les règles trop larges, les réseaux d’administration mélangés aux réseaux utilisateurs et les exceptions oubliées affaiblissent les bénéfices ; documentation et revues périodiques restent nécessaires.

## Concepts clés

- **Macrosegmentation** : séparation par zone ou fonction.
- **Microsegmentation** : contrôles fins entre workloads, services ou identités.
- **Contrôles inter-zones** : ACL, pare-feu ou politiques hôtes.
- **Mouvement latéral** : progression vers d’autres actifs après un compromis.

## Méthode pratique

1. Classe les actifs et documente leurs flux nécessaires.
2. Sépare utilisateurs, serveurs, invités, administration et services exposés.
3. Refuse les flux inter-zones non documentés lorsque possible.
4. Teste les applications et révise les exceptions.

## À retenir

Des VLAN distincts ne garantissent pas la sécurité si les communications entre eux restent ouvertes.
