---
node_id: ot-securite-expert
title: Cybersécurité OT (Purdue Model)
---

# Cybersécurité OT et Purdue Model — Niveau expert

## Objectifs
Concevoir une architecture de défense en profondeur pour un environnement OT, cartographier les niveaux Purdue, définir des zones et conduits, réduire les accès distants et organiser la réponse aux incidents sans compromettre la sûreté du procédé.

## 1. Modèle Purdue

Purdue est un modèle de référence logique, pas une topologie obligatoire. Les architectures modernes peuvent différer : l'essentiel est de documenter les actifs, les flux, les dépendances et les frontières de confiance.

```text
Niveau 5 : entreprise / services IT
             |
Niveau 4 : opérations métier et planification
             |
Niveau 3.5 : DMZ industrielle
             |
Niveau 3 : opérations de site / SCADA / Historian
             |
Niveau 2 : supervision locale / HMI
             |
Niveau 1 : contrôleurs PLC / DCS
             |
Niveau 0 : capteurs, actionneurs, procédé physique
```

La DMZ industrielle héberge des services relais tels que bastion, proxy, réplication Historian et transfert de fichiers contrôlé. Elle évite les connexions directes de l'IT vers les automates.

## 2. Zones et conduits
Créer des zones selon la fonction, la criticité, le fabricant et les besoins de communication. Un conduit est un chemin autorisé entre zones. Pour chaque flux, documenter source, destination, protocole/port, sens, fréquence, propriétaire et justification. Appliquer le refus par défaut, mais valider les dépendances avant d'activer les restrictions : des flux implicites peuvent être nécessaires au procédé.

## 3. Risque et disponibilité
L'analyse doit prendre en compte les conséquences physiques, la sécurité des personnes, l'environnement, la production, l'intégrité et la confidentialité. En OT, un redémarrage, un scan agressif, un patch immédiat ou une isolation brutale peut créer un risque opérationnel.

Priorités recommandées :
1. inventaire fiable et sauvegardes vérifiées ;
2. segmentation et suppression des chemins directs inutiles ;
3. identité forte et accès distant contrôlé ;
4. durcissement des postes d'ingénierie et serveurs ;
5. surveillance passive et détection des changements ;
6. gestion des vulnérabilités dans des fenêtres validées ;
7. exercices de restauration et réponse aux incidents.

## 4. Identité et accès distant
- Comptes nominatifs, MFA pour l'accès distant et privilèges minimaux.
- Bastion/jump host dans une zone contrôlée ; journaliser les sessions lorsque cela est approprié.
- Éviter les accès fournisseurs permanents : activer sur demande avec approbation et durée limitée.
- Séparer les comptes d'administration IT, d'ingénierie OT et les comptes de service.
- Retirer les comptes inactifs, protéger les secrets et réviser régulièrement les droits.
- Ne jamais publier directement sur Internet les interfaces PLC, HMI ou d'ingénierie.

## 5. Architecture de référence

```text
IT entreprise
    |
[Firewall IT/DMZ]
    |
DMZ industrielle
  +-- Bastion avec MFA
  +-- Relais de fichiers analysés
  +-- Réplication Historian
    |
[Firewall industriel : règles explicites]
    |
Zone supervision SCADA / HMI
    |
[Frontière cellule / îlot]
    |
PLC / DCS / équipements de terrain
```

Si un protocole ancien n'offre pas de sécurité native, limiter strictement les chemins réseau, contrôler les postes autorisés et surveiller les opérations sensibles. Ne pas autoriser un sous-réseau complet simplement pour résoudre une panne.

## 6. Détection et réponse OT
Établir une baseline des communications et détecter les nouvelles relations, scans, changements de logique, commandes inattendues et accès hors fenêtre. Corréler pare-feu, bastion, postes d'ingénierie, serveurs et événements du procédé.

En cas d'incident :
1. protéger les personnes et stabiliser le procédé ;
2. activer la chaîne de décision OT/IT/sûreté ;
3. préserver journaux, configurations et preuves ;
4. évaluer les conséquences avant d'isoler un équipement ;
5. restaurer depuis des sauvegardes connues et vérifier le fonctionnement ;
6. documenter la cause et renforcer les contrôles.

Préparer à l'avance les modes dégradés, les contacts, les critères d'arrêt sécurisé et les procédures manuelles. Une coupure réseau n'est jamais présumée sans conséquence.

## 7. Gouvernance
- **IEC 62443** : sécurité des systèmes d'automatisation et de contrôle industriels, zones, conduits et niveaux de sécurité.
- **NIST SP 800-82** : recommandations de sécurité OT.
- **Gestion des changements** : analyse de risque, test, approbation, fenêtre, sauvegarde et retour arrière.
- **Fournisseurs** : accès encadré, inventaire des dépendances et plan de correctifs.
- **Continuité** : sauvegardes hors ligne, procédures de secours et tests de restauration.

## TP d'architecture
Sur un diagramme fictif :
1. Identifier les actifs et leurs niveaux Purdue.
2. Placer la DMZ et supprimer l'accès direct IT → PLC.
3. Construire une matrice de flux minimale.
4. Définir les accès fournisseurs et l'usage de MFA.
5. Décrire la réponse à un poste d'ingénierie compromis sans interrompre brutalement le procédé.

## Exercices corrigés
1. **Purdue est-il une topologie obligatoire ?** Non : c'est un modèle de référence à adapter aux risques et aux flux réels.
2. **Pourquoi une DMZ industrielle ?** Pour contrôler les échanges IT/OT par des services intermédiaires.
3. **Faut-il isoler immédiatement un PLC suspect ?** Pas sans évaluer les conséquences opérationnelles ; coordonner avec l'équipe OT et la sûreté.
4. **Première priorité si l'inventaire est incomplet ?** Améliorer l'inventaire et la visibilité passive, puis traiter les frontières de confiance et actifs critiques.

## Défi final corrigé
Un compte fournisseur est compromis et une station d'ingénierie communique vers des PLC hors procédure. Alerter l'équipe OT/sûreté, suspendre l'accès distant via le mécanisme contrôlé, préserver journaux et configurations, déterminer l'étendue par observation passive et évaluer le risque procédé avant toute isolation. Restaurer la station depuis une image fiable, renouveler les secrets, vérifier la logique PLC selon une procédure approuvée, puis corriger la cause et tester le plan de réponse.

## Références
- IEC 62443 : https://www.iec.ch/
- NIST SP 800-82 Rev. 3 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
- CISA Industrial Control Systems : https://www.cisa.gov/topics/industrial-control-systems
