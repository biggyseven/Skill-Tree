---
node_id: telecom-5g-debutant
title: Réseaux Mobiles (4G/5G)
---

# Réseaux mobiles 4G/5G — Niveau débutant

## Objectifs et prérequis
À la fin de ce cours, vous saurez expliquer la chaîne radio jusqu'au cœur de réseau, distinguer LTE/4G et 5G NR, lire les principaux rôles du RAN et du Core, et diagnostiquer les premières causes d'une perte de service. Prérequis : adressage IP, Ethernet, notions de radio et de routage.

## 1. Vue d'ensemble

Un réseau mobile relie un terminal (UE) à des services IP en passant par une interface radio, des stations de base et un cœur de réseau opérateur.

```text
Téléphone / UE
    |
    | radio : LTE ou 5G NR
    v
Station de base
  4G : eNodeB       5G : gNodeB
    |
    v
Transport / réseau d'agrégation
    |
    v
Cœur mobile
  4G : EPC          5G : 5GC
    |
    +---- Internet
    +---- IMS / voix
    +---- services privés
```

Le RAN (Radio Access Network) gère l'accès radio et les ressources de la cellule. Le transport achemine le trafic entre les sites radio et le cœur. Le Core assure l'enregistrement, la mobilité, les sessions, les politiques et la sortie vers les réseaux de données.

## 2. LTE/4G et 5G

| Élément | 4G LTE | 5G |
|---|---|---|
| Radio | LTE | 5G NR |
| Station de base | eNodeB | gNodeB |
| Cœur typique | EPC | 5GC |
| Architecture | largement centrée EPC | fonctions davantage séparées et orientées services |
| Cas d'usage | haut débit mobile, VoLTE | eMBB, faible latence selon déploiement, IoT massif |

La 5G ne garantit pas automatiquement une latence extrêmement faible : le résultat dépend du spectre, de la charge radio, du transport, du cœur, de l'emplacement des applications et de la configuration du service.

## 3. Notions radio essentielles

- **Cellule** : zone desservie par une configuration radio.
- **Bande et spectre** : fréquences autorisées pour le service.
- **Bande passante radio** : largeur de spectre affectée ; elle influence la capacité.
- **RSRP** : puissance reçue des signaux de référence, indicateur de couverture.
- **RSRQ** : qualité du signal en tenant compte notamment de la charge/interférences.
- **SINR** : rapport signal utile / interférences et bruit ; un bon SINR aide à utiliser des modulations plus efficaces.
- **Handover** : transfert de la connexion radio d'une cellule à une autre.

Une couverture forte n'implique pas nécessairement une bonne qualité : des interférences ou une cellule congestionnée peuvent dégrader le débit.

## 4. Mobilité et établissement de service

```text
UE allumé
  -> recherche de cellule et synchronisation
  -> accès radio
  -> authentification et sécurité
  -> enregistrement auprès du réseau
  -> établissement d'une session de données
  -> attribution/configuration IP
  -> trafic vers Internet ou réseau privé
```

L'authentification protège l'accès ; les mécanismes de mobilité permettent de maintenir le service lors des déplacements. La voix peut utiliser VoLTE en 4G ou VoNR dans certaines architectures 5G, mais elle peut aussi dépendre de mécanismes de repli selon le réseau.

## 5. Déploiements 5G

- **NSA (Non-Standalone)** : la 5G NR s'appuie sur une infrastructure/cœur 4G dans les architectures courantes.
- **SA (Standalone)** : la 5G NR utilise le cœur 5G, permettant les fonctions natives du 5GC.
- **FDD/TDD** : duplexage fréquentiel ou temporel.
- **Small cells** : cellules de petite portée utiles pour augmenter la capacité localement.
- **Network slicing** : séparation logique de services sur une infrastructure partagée ; elle nécessite une orchestration et des politiques de bout en bout, pas seulement un identifiant de slice.

## 6. Diagnostic initial

1. Vérifier l'état SIM/eSIM, le forfait et l'autorisation d'accès.
2. Vérifier si le problème est limité à une zone, une cellule, un terminal ou un service.
3. Comparer RSRP, RSRQ et SINR ; ne pas se limiter aux barres affichées.
4. Vérifier congestion, incidents radio, transport et cœur.
5. Tester séparément l'enregistrement, la session de données, DNS et accès IP.
6. Corréler heure, cellule, mobilité et compteurs avant toute modification.

Les opérations sur réseau opérateur doivent être réalisées par du personnel autorisé ; ne jamais tenter d'interférer avec des fréquences radio.

## 7. Travaux pratiques

**TP : classer des symptômes**
- Cas A : RSRP faible partout dans un bâtiment. Hypothèse : couverture/pénétration indoor.
- Cas B : RSRP correct, SINR mauvais et débit variable. Hypothèse : interférences ou charge.
- Cas C : le terminal s'enregistre mais aucune application n'accède à Internet. Vérifier session de données, APN/DNN, attribution IP, DNS et routage.
- Cas D : coupure pendant un déplacement. Examiner les mesures de voisinage et les échecs de handover.

## Exercices corrigés

1. **Quel composant gère l'accès radio ?** Le RAN.
2. **La 5G garantit-elle toujours une latence plus faible ?** Non ; le résultat dépend du réseau complet et de l'application.
3. **RSRP bon, SINR faible :** la puissance est suffisante mais la qualité radio peut être affectée par les interférences ou le bruit.
4. **UE enregistré mais pas de données :** diagnostiquer la session, le profil APN/DNN, l'IP, le DNS et le chemin réseau.

## Défi final corrigé

Un utilisateur voit « 5G », mais le débit est faible et les appels sont instables. Procédure attendue : confirmer la cellule et le mode NSA/SA, mesurer RSRP/RSRQ/SINR, comparer plusieurs terminaux et emplacements, vérifier charge radio et transport, puis examiner séparément données et voix (VoLTE/VoNR ou repli). Ne conclure à un défaut du terminal qu'après comparaison contrôlée.

## Glossaire
**UE** : terminal utilisateur. **RAN** : réseau d'accès radio. **EPC** : cœur 4G. **5GC** : cœur 5G. **gNodeB** : station de base 5G. **Handover** : transfert intercellulaire. **APN/DNN** : paramètres de réseau de données.

## Références
- 3GPP, spécifications LTE et 5G NR : https://www.3gpp.org/
- GSMA, ressources sur les réseaux mobiles : https://www.gsma.com/
