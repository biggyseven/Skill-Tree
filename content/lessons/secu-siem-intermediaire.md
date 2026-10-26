# Introduction aux SIEM

## Introduction

Un SIEM collecte les événements des endpoints, serveurs, équipements réseau, applications et systèmes d’identité. Il permet de rapprocher des signaux dispersés pour repérer des scénarios de menace difficiles à voir dans un journal isolé.

Le traitement comprend ingestion, normalisation, enrichissement, stockage et évaluation de règles. Des horloges synchronisées, des champs cohérents et des sources pertinentes comptent davantage qu’une collecte massive sans objectif, qui augmente les coûts et le bruit.

Une règle de détection décrit un scénario, les données requises, la logique, la sévérité et les étapes d’investigation. Elle doit être testée, ajustée pour réduire les faux positifs et reliée à une procédure d’escalade : l’outil assiste l’analyste, il ne remplace pas son jugement.

## Concepts clés

- **Sources** : identité, endpoint, DNS, pare-feu, système et application.
- **Normalisation** : harmoniser les champs des différentes sources.
- **Corrélation** : relier des événements selon l’identité, le temps ou le contexte.
- **Cas d’usage** : scénario, critères de détection et procédure d’investigation.
- **Rétention** : arbitrer besoins d’enquête, confidentialité et coût.

## Méthode pratique

1. Définis l’objectif avant d’ajouter une source.
2. Vérifie horodatage et qualité des champs.
3. Teste les règles sur événements normaux et simulés.
4. Mesure les faux positifs et documente le triage.

## À retenir

Un SIEM efficace associe données fiables, détections explicables et procédures claires.
