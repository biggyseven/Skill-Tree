# Architecture de pare-feu (NGFW)

## Introduction

Un pare-feu de nouvelle génération (NGFW) combine le filtrage à états avec l’identification applicative, le contrôle selon l’utilisateur, le filtrage d’URL ou la prévention d’intrusion. Il analyse ainsi plus de contexte que le seul port TCP ou UDP.

Une architecture sûre sépare les zones selon leur rôle : utilisateurs, serveurs, administration, invités et services exposés. Les règles précisent source, destination, service, action et profil d’inspection ; les exceptions doivent être justifiées, nommées et révisées.

Les fonctions avancées peuvent consommer des ressources et l’inspection TLS nécessite une conception prudente des certificats et exclusions. La haute disponibilité, la journalisation, les performances et les procédures de retour arrière doivent être testées avant le déploiement.

## Concepts clés

- **Inspection avec état** : suit les sessions et leur trafic associé.
- **Contrôle applicatif** : identifie les applications au-delà du numéro de port.
- **Inspection TLS** : a des implications de performance, de confiance et de confidentialité.
- **Zones** : groupent les réseaux selon leur fonction et leur confiance.

## Méthode pratique

1. Définis les zones et les flux indispensables.
2. Applique le moindre privilège dans les règles.
3. Ajoute des profils IPS ou URL selon le risque.
4. Centralise les journaux et teste bascule et retour arrière.

## À retenir

Un NGFW avancé nécessite des règles compréhensibles et régulièrement revues.
