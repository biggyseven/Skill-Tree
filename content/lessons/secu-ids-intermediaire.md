# IDS/IPS et détection d'intrusion

## Introduction

Un système de détection d’intrusion (IDS) observe des événements ou des flux pour signaler des comportements suspects. Un système de prévention d’intrusion (IPS) peut également agir sur le trafic, par exemple en bloquant une correspondance considérée malveillante.

Les signatures repèrent des motifs connus, tandis que les méthodes comportementales recherchent des écarts à une référence. Les signatures peuvent manquer une attaque inconnue ; les détections d’anomalie peuvent produire davantage de faux positifs si elles ne sont pas adaptées à l’environnement.

L’efficacité dépend du contexte, des mises à jour et du traitement des alertes, pas du volume d’alertes. Un blocage automatique doit être testé avec prudence lorsqu’un faux positif peut affecter un service critique, et chaque alerte importante doit conduire à une investigation ou une escalade.

## Concepts clés

- **IDS** : observe et alerte sans nécessairement bloquer.
- **IPS** : peut bloquer le trafic lorsqu’une règle correspond.
- **Signature / anomalie** : motif connu / écart au comportement attendu.
- **Faux positif / négatif** : alerte erronée / menace non détectée.

## Méthode pratique

1. Place les capteurs où ils voient les flux pertinents.
2. Priorise les alertes selon l’actif, la sévérité et le contexte.
3. Examine des exemples de vrais et faux positifs.
4. Ajuste finement les règles sans désactiver largement les protections.

## À retenir

Une alerte n’a de valeur que si elle est contextualisée et suivie d’une action proportionnée.
