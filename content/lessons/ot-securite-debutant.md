# Cybersécurité OT — Débutant

**Module :** Réseaux Industriels (OT) · **Catégorie :** OT/ICS  
**Identifiant de cours :** `ot-securite-debutant`

## Objectifs pédagogiques
- Comprendre pourquoi la cybersécurité OT doit tenir compte des conséquences physiques et de la sûreté.
- Identifier PLC, HMI, SCADA, Historian, station d’ingénierie et réseaux de terrain.
- Lire les niveaux Purdue et comprendre la fonction d’une DMZ industrielle.
- Appliquer les bases : inventaire, moindre privilège, accès distant encadré et sauvegardes vérifiées.

## 1. IT et OT : objectifs différents
Les systèmes IT privilégient souvent confidentialité, intégrité et disponibilité des services informatiques. En OT, la disponibilité du procédé, l’intégrité des commandes et la sécurité des personnes peuvent être prioritaires. Une action technique pourtant habituelle — scan agressif, redémarrage, patch immédiat ou coupure réseau — peut perturber un équipement industriel.

## 2. Actifs industriels
- **PLC/API :** exécute la logique de contrôle et échange avec les entrées/sorties.
- **HMI/IHM :** interface opérateur pour surveiller et commander le procédé.
- **SCADA :** supervision et collecte de données à l’échelle d’un site ou de plusieurs sites.
- **Historian :** conserve mesures, tendances et événements.
- **Station d’ingénierie :** outil de configuration et de maintenance des automates.
- **Équipements de terrain :** capteurs, variateurs, actionneurs et instruments.

## 3. Modèle Purdue simplifié
```text
Niveau 4/5 : services et systèmes d’entreprise IT
                    |
Niveau 3.5 : DMZ industrielle (bastion, relais contrôlés)
                    |
Niveau 3   : opérations de site / SCADA / Historian
                    |
Niveau 2   : supervision locale / HMI
                    |
Niveau 1   : PLC / DCS
                    |
Niveau 0   : capteurs, actionneurs et procédé physique
```
Purdue est un modèle de référence, pas une topologie obligatoire. Le point important est de documenter les actifs, les frontières de confiance et les flux réellement nécessaires.

## 4. Règles de base
1. Tenir un inventaire avec propriétaire, rôle, version, emplacement et criticité.
2. Ne pas exposer directement les PLC, HMI ou interfaces d’ingénierie à Internet.
3. Utiliser des comptes nominatifs, des privilèges minimaux et des accès temporaires.
4. Protéger les sauvegardes de projets PLC, configurations réseau et images de stations.
5. Tester la restauration ; une sauvegarde non restaurable n’est pas une preuve de reprise.
6. Planifier les changements avec l’équipe opérationnelle et un retour arrière documenté.

## 5. Accès distant et segmentation
```text
Technicien autorisé
      |
VPN avec MFA
      |
Bastion contrôlé dans la DMZ OT
      |
Pare-feu avec flux explicitement autorisés
      |
Station d’ingénierie / service nécessaire
      |
PLC (jamais accès Internet direct)
```
Un fournisseur ne doit pas conserver un accès permanent par défaut. L’accès doit avoir un motif, une approbation, une durée limitée et une journalisation adaptée. Ne pas utiliser de compte partagé si un compte nominatif est possible.

## 6. Réponse à un incident
En cas de comportement inhabituel, protéger les personnes et stabiliser le procédé en priorité. Alerter l’équipe OT et le responsable opérationnel, conserver les journaux et configurations, puis évaluer les conséquences avant d’isoler un équipement. Toute mesure de confinement doit tenir compte du rôle de l’actif dans le procédé.

## TP — Cartographier une cellule industrielle
Dessiner une cellule avec une HMI, deux PLC, une station d’ingénierie, un Historian et une connexion IT. Placer la DMZ, tracer uniquement les flux nécessaires, identifier les accès distants et noter les sauvegardes critiques.

**Livrables :** schéma annoté, inventaire minimal, liste des flux autorisés et procédure d’accès fournisseur temporaire.

## Exercices corrigés
1. **Pourquoi un PLC ne doit-il pas être directement accessible depuis Internet ?** Parce que cela expose une fonction de contrôle physique à des accès non maîtrisés.
2. **La DMZ industrielle remplace-t-elle les pare-feu ?** Non. Elle héberge des services intermédiaires et doit être protégée par des règles entre zones.
3. **Faut-il débrancher immédiatement tout équipement suspect ?** Pas sans évaluer l’impact sur le procédé et la sûreté ; coordonner la décision avec l’équipe OT.
4. **Pourquoi tester une restauration ?** Pour confirmer que les sauvegardes permettent réellement de récupérer une configuration connue.

## Défi final corrigé
Un fournisseur demande un accès permanent à une station d’ingénierie. Refuser l’accès permanent par défaut, créer un accès temporaire approuvé via bastion et MFA, limiter les destinations, journaliser la session, vérifier la sauvegarde avant intervention et retirer les droits à la fin. Confirmer le fonctionnement du procédé et conserver un compte rendu sans secrets.

## Références
- NIST SP 800-82 Rev. 3 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
- CISA Industrial Control Systems : https://www.cisa.gov/topics/industrial-control-systems
