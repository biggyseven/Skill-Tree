---
node_id: ot-scada-debutant
title: Introduction aux Réseaux OT / ICS
---

# Introduction aux Réseaux OT / ICS

## Objectifs et prérequis
Décrire un environnement industriel, identifier les composants OT/ICS/SCADA, lire une architecture simple et appliquer des règles de sécurité adaptées à la disponibilité et à la sûreté. Prérequis : notions Ethernet, IP et segmentation réseau.

## 1. OT, ICS et SCADA
**OT (Operational Technology)** regroupe les technologies qui surveillent ou pilotent des procédés physiques. **ICS** désigne les systèmes de contrôle industriels. **SCADA** supervise des équipements distribués, collecte des télémesures et permet des commandes opérateur. Un DCS est souvent utilisé pour le contrôle intégré d'un procédé d'usine.

```text
Niveau entreprise / IT
        |
   DMZ industrielle
        |
Supervision / serveurs SCADA / Historian
        |
Réseau de contrôle industriel
        |
PLC / RTU / contrôleurs
        |
Capteurs ---- procédé ---- actionneurs
```

- **Capteur** : mesure une grandeur (température, pression, débit).
- **Actionneur** : agit sur le procédé (vanne, moteur).
- **PLC/API industriel** : exécute une logique de contrôle.
- **RTU** : unité de télémesure/commande, fréquente sur des sites distants.
- **HMI/IHM** : interface opérateur.
- **Historian** : conserve les séries temporelles de mesures et événements.
- **SCADA** : supervision et commande de systèmes distribués.

## 2. IT et OT : priorités différentes
En IT, confidentialité, intégrité et disponibilité sont souvent les objectifs principaux. En OT, la sécurité des personnes et du procédé, la disponibilité, l'intégrité du contrôle et le comportement déterministe sont essentiels. Un redémarrage, une mise à jour ou un scan agressif peut interrompre une production ou créer un risque physique.

Toute action doit suivre les procédures du site, être autorisée, testée et planifiée. Ne jamais envoyer de commandes à un automate réel sans validation de l'équipe industrielle.

## 3. Protocoles et communication
Les réseaux OT utilisent Ethernet/IP, TCP/UDP et des protocoles spécialisés tels que Modbus TCP, PROFINET, EtherNet/IP, OPC UA ou DNP3. Certains protocoles historiques offrent peu ou pas d'authentification ou de chiffrement ; leur protection dépend alors fortement de la segmentation, du contrôle d'accès et de la supervision.

## 4. Segmentation de base

```text
Réseau IT
   |
[Firewall / règles explicites]
   |
[DMZ industrielle : relais, bastion, transfert contrôlé]
   |
[Firewall industriel]
   |
[SCADA / supervision]
   |
[VLAN ou zone PLC]
   |
[Automates et équipements de procédé]
```

Éviter les connexions directes entre postes bureautiques et automates. Autoriser uniquement les flux nécessaires, documentés par source, destination, protocole et port. Les accès distants doivent passer par un VPN/bastion avec MFA, comptes nominatifs et journalisation.

## 5. Inventaire et exploitation
Pour chaque actif, documenter : propriétaire, fabricant, modèle, version, adresse, fonction, criticité, dépendances, protocole, fenêtre de maintenance et méthode de restauration. Maintenir des sauvegardes vérifiées des configurations PLC/HMI/SCADA et tester le processus de restauration.

## 6. Détection et réponse
Les indicateurs peuvent inclure une nouvelle station d'ingénierie, des changements de logique, une communication inattendue, un scan réseau, des connexions hors horaires ou une variation anormale des commandes. Préserver les journaux et les captures ; coordonner toute réponse avec les responsables de procédé et de sûreté avant d'isoler un système critique.

## TP guidé
Sur une maquette ou un simulateur :
1. Dessiner la chaîne capteur → PLC → HMI/SCADA.
2. Placer une DMZ entre IT et OT.
3. Établir une matrice de flux minimale pour HMI vers PLC et Historian vers serveur de collecte.
4. Définir qui autorise les changements et comment restaurer une configuration.
5. Repérer trois risques d'une connexion directe entre poste bureautique et PLC.

## Exercices corrigés
1. **À quoi sert un PLC ?** À exécuter une logique de contrôle du procédé.
2. **Pourquoi éviter un scan agressif ?** Certains équipements peuvent être sensibles à la charge ou aux requêtes imprévues.
3. **Rôle d'une DMZ OT :** contrôler et journaliser les échanges entre IT et OT.
4. **Que faire avant un changement ?** Autorisation, analyse de risque, test, fenêtre planifiée et plan de retour arrière.

## Défi final corrigé
Une station bureautique doit consulter des rapports SCADA. Ne lui donnez pas un accès direct aux PLC. Déployer un service relais ou Historian dans la DMZ, n'autoriser que les flux requis, limiter les comptes, journaliser l'accès et valider le fonctionnement avec l'équipe OT.

## Glossaire et références
OT, ICS, SCADA, PLC/API, RTU, HMI/IHM, Historian, DMZ.
- NIST SP 800-82 Rev. 3, Guide to Operational Technology Security : https://csrc.nist.gov/pubs/sp/800/82/r3/final
- CISA, ressources ICS : https://www.cisa.gov/topics/industrial-control-systems
