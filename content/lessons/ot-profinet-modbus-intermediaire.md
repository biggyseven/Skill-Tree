---
node_id: ot-profinet-modbus-intermediaire
title: Protocoles Industriels (Modbus, Profinet)
---

# Protocoles industriels : Modbus et PROFINET — Niveau intermédiaire

## Objectifs
Comparer Modbus RTU, Modbus TCP et PROFINET, comprendre les rôles client/serveur ou contrôleur/périphérique, analyser les échanges et concevoir une segmentation adaptée. Prérequis : bases OT/ICS et Ethernet/IP.

## 1. Modbus
Modbus est un protocole industriel simple. Dans Modbus RTU sur liaison série, les équipements partagent un bus selon les règles du support ; Modbus TCP encapsule les messages dans TCP, généralement sur le port 502. Le modèle traditionnel utilise un client qui demande une opération à un serveur.

Concepts :
- **Coil** : valeur binaire lisible/écrivable.
- **Discrete input** : entrée binaire en lecture.
- **Input register** : registre 16 bits en lecture.
- **Holding register** : registre 16 bits lisible/écrivable.
- **Function code** : opération demandée, par exemple lecture de coils ou de registres.
- **Unit Identifier** : identifiant utile notamment avec des passerelles.

Les adresses documentaires 0xxxx/1xxxx/3xxxx/4xxxx ne sont pas toujours présentées de façon identique dans les outils. Toujours confirmer l'offset réel, la convention d'adressage, l'ordre des mots pour les valeurs multi-registres et l'échelle d'ingénierie. Modbus TCP traditionnel ne fournit pas, à lui seul, une authentification forte ni un chiffrement.

## 2. PROFINET
PROFINET est une technologie Ethernet industrielle. L'architecture classique comprend un **IO-Controller** (souvent un PLC), des **IO-Devices** (modules et équipements de terrain) et parfois un **IO-Supervisor** pour l'ingénierie/diagnostic. Le trafic cyclique temps réel et les services acycliques de paramétrage/diagnostic ont des exigences différentes.

```text
Outil d'ingénierie / IO-Supervisor
              |
              v
PLC / IO-Controller ===== Ethernet industriel ===== IO-Device
                                                   capteur / variateur
              |
              +---- logique de contrôle
```

La performance dépend du cycle, de la charge, de la topologie, des équipements et du profil temps réel utilisé. Ne pas traiter tous les flux PROFINET comme du trafic bureautique ordinaire sans tenir compte des contraintes de déterminisme.

## 3. Comparaison

| Critère | Modbus TCP | PROFINET |
|---|---|---|
| Usage courant | lecture/écriture de registres | E/S cycliques, contrôle et diagnostic |
| Transport | TCP/IP, port 502 usuel | Ethernet industriel et services PROFINET |
| Modèle | requête/réponse client-serveur | contrôleur/périphérique, échanges cycliques et acycliques |
| Temps réel | dépend du transport et de la charge | profils temps réel dédiés |
| Sécurité | à renforcer par segmentation et contrôle d'accès | sécurisation de l'architecture, accès ingénierie et actifs |

## 4. Segmentation et flux
Créer des zones selon la fonction : supervision, cellules/îlots, ingénierie, accès distant et DMZ. Pour chaque flux, documenter source, destination, direction, protocole, criticité, propriétaire et justification. Les règles doivent être testées en mode observation ou sur maquette avant activation. Éviter une règle générique autorisant tout le sous-réseau OT.

## 5. Diagnostic
- Modbus TCP : vérifier IP, TCP/502, serveur actif, Unit Identifier, fonction, offset, timeout et cohérence des valeurs.
- PROFINET : vérifier nom d'équipement, IP, topologie, relation contrôleur/périphérique, version de configuration, diagnostics et charge réseau.
- Dans les deux cas : comparer le comportement attendu aux compteurs et captures passives ; préserver la sécurité du procédé.

Les captures passives sont préférables sur un réseau en production. Les scans actifs ou écritures de registres doivent être réalisés uniquement sur banc de test et avec autorisation explicite.

## TP guidé
Sur un simulateur :
1. Lire un registre Modbus connu et vérifier l'échelle physique.
2. Provoquer un mauvais offset dans le simulateur et reconnaître une valeur incohérente.
3. Représenter un PLC contrôleur PROFINET et deux périphériques.
4. Créer une matrice de flux et proposer les règles de segmentation minimales.
5. Écrire une procédure de changement et de retour arrière.

## Exercices corrigés
1. **Port usuel Modbus TCP :** TCP/502.
2. **Pourquoi une valeur Modbus peut-elle sembler fausse ?** Offset, format, ordre des mots, échelle ou registre incorrect.
3. **Rôle du IO-Controller :** piloter les échanges cycliques avec les IO-Devices.
4. **Pourquoi préférer une capture passive en production ?** Elle réduit le risque d'introduire des charges ou requêtes perturbatrices.

## Défi final corrigé
Un HMI ne lit plus un registre et un périphérique PROFINET affiche un défaut. Séparer les investigations : pour Modbus, confirmer la connectivité TCP, le code fonction, l'offset et le timeout ; pour PROFINET, vérifier le nom, la configuration, le lien et le diagnostic du contrôleur. Corréler les événements sans effectuer d'écriture sur le procédé réel.

## Références
- Modbus Organization, specifications : https://www.modbus.org/
- PI (PROFIBUS & PROFINET International) : https://www.profibus.com/
- NIST SP 800-82 Rev. 3 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
