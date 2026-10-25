# AWS VPC — Cours complet de niveau expert
## Concevoir, sécuriser, exploiter et dépanner des architectures réseau AWS à grande échelle

**Nom du fichier :** `aws-vpc-expert.md`  
**Domaine :** Architecture réseau cloud, connectivité hybride, cybersécurité et opérations AWS  
**Niveau :** Expert  
**Public cible :** Ingénieurs réseau/cloud, architectes cloud, administrateurs systèmes et réseaux expérimentés, responsables de plateformes et apprenants ayant terminé les niveaux débutant et intermédiaire  
**Durée indicative :** 24 à 40 heures, ateliers et révisions compris  
**Prérequis :** Maîtriser le contenu des cours AWS VPC débutant et intermédiaire, CIDR IPv4/IPv6, tables de routage, Security Groups, Network ACL, NAT Gateway, VPC endpoints, VPC Peering, VPC Flow Logs et diagnostic réseau  
**Méthode pédagogique :** Théorie approfondie, modèles d'architecture, schémas textuels, matrices de routage et de flux, commandes AWS CLI, ateliers guidés, exercices corrigés, scénarios d'incident et challenge final corrigé

> **Règle de lecture :** ce document est autonome. Le cours théorique, les schémas, les ateliers, les exercices, le challenge final et sa correction sont intégrés dans **ce seul fichier Markdown**. Aucun fichier annexe n'est nécessaire.
>
> **Précaution de coûts :** plusieurs ateliers font intervenir des services facturés, notamment Transit Gateway, NAT Gateway, Network Firewall, certains endpoints, Route 53 Resolver endpoints, Site-to-Site VPN et Direct Connect. Le cours peut être étudié sans déployer toutes les ressources. Utiliser un compte de laboratoire, définir un budget et supprimer les ressources après les essais.


# Sommaire

1. Positionnement du niveau expert et méthode d'architecture
2. Architecture de référence et conventions utilisées
3. Plan d'adressage à l'échelle : CIDR, IPAM, IPv6 et prévention des chevauchements
4. Routage AWS avancé : sélection des routes, limites et chemins asymétriques
5. Transit Gateway : architecture hub-and-spoke et segmentation par domaines
6. Inspection centralisée : AWS Network Firewall, appliances et symétrie des flux
7. Connectivité hybride : Site-to-Site VPN, BGP, Direct Connect et bascule
8. AWS Cloud WAN et choix entre modèles de connectivité
9. PrivateLink, endpoints, DNS privé et contrôle de l'accès aux services
10. DNS hybride avec Route 53 VPC Resolver et DNS Firewall
11. Architecture IPv6 dual-stack et IPv6-only
12. Sécurité réseau multicouche, gouvernance multi-comptes et moindre privilège
13. Observabilité, diagnostic et validation des chemins
14. Automatisation, Infrastructure as Code et validation continue
15. Disponibilité, performances, MTU, coûts et capacité opérationnelle
16. Procédures de dépannage expert par symptôme
17. Atelier guidé A — concevoir un hub réseau de production
18. Atelier guidé B — inspection centralisée sans rupture de flux
19. Atelier guidé C — connecter un réseau on-premises de façon résiliente
20. Atelier guidé D — accès privé aux services AWS et DNS hybride
21. Exercices de consolidation avec corrections
22. Challenge final autonome — plateforme multi-comptes et connectivité hybride
23. Correction détaillée du challenge final
24. Checklist d'architecture, grille d'évaluation et glossaire
25. Documentation officielle


# 1. Positionnement du niveau expert et méthode d'architecture

## 1.1. Le changement de posture

Au niveau débutant, l'apprenant apprend à créer un VPC, des sous-réseaux, des routes, une Internet Gateway et des règles de sécurité. Au niveau intermédiaire, il assemble ces composants, construit une segmentation et diagnostique des problèmes classiques.

Au niveau expert, l'objectif est différent : **concevoir un système réseau global qui reste compréhensible, sécurisé, résilient, auditable et exploitable malgré l'augmentation du nombre de VPC, de comptes, de régions, d'équipes et de connexions**.

Un expert ne se contente pas de demander : « Est-ce que la connexion fonctionne ? » Il demande aussi :

- Est-elle autorisée par une politique documentée ?
- Le chemin est-il déterministe dans les deux sens ?
- Que se passe-t-il si une zone de disponibilité tombe ?
- Que se passe-t-il si une route est propagée par erreur ?
- Une nouvelle connexion pourrait-elle ouvrir un chemin non prévu ?
- Comment prouver qu'un flux est bloqué ou autorisé ?
- Peut-on reproduire l'architecture depuis le code ?
- Comment détecter une dérive de configuration ?
- Quels sont les coûts fixes et variables de cette architecture ?
- Qui est autorisé à modifier les routes, les règles de pare-feu et les associations de transit ?

## 1.2. Les six dimensions d'une architecture réseau experte

| Dimension | Question fondamentale | Preuve attendue |
|---|---|---|
| Adressage | Les plages sont-elles évolutives et non chevauchantes ? | Registre CIDR, IPAM, conventions de nommage |
| Connectivité | Chaque chemin est-il explicite et bidirectionnel ? | Schéma, tables de routage, tests de reachability |
| Sécurité | Les flux autorisés sont-ils minimaux ? | Matrice de flux, règles SG/NACL/Firewall |
| Résilience | Une panne de zone ou de tunnel est-elle tolérée ? | Tests de bascule, redondance multi-AZ |
| Observabilité | Peut-on expliquer un flux ou un rejet ? | Flow Logs, journaux Firewall, métriques, runbooks |
| Exploitabilité | Peut-on déployer, vérifier et revenir en arrière ? | IaC, pipeline, tests, procédures de rollback |

## 1.3. Séparer les plans de décision

Un réseau cloud doit être raisonné en plusieurs plans complémentaires.

```text
PLAN D'ADRESSAGE
  CIDR du VPC, CIDR des sous-réseaux, IPv6, IPAM
              |
              v
PLAN DE ROUTAGE
  Route tables VPC, associations TGW, propagations, BGP
              |
              v
PLAN DE CONTRÔLE DE SÉCURITÉ
  Security Groups, NACL, Network Firewall, endpoint policies
              |
              v
PLAN DE RÉSOLUTION DE NOMS
  Route 53 Resolver, private hosted zones, règles DNS
              |
              v
PLAN D'OBSERVABILITÉ ET DE GOUVERNANCE
  Flow Logs, CloudTrail, Network Access Analyzer, IaC, SCP
```

Une panne peut venir de n'importe lequel de ces plans. Un nom DNS peut pointer vers une adresse correcte mais le routage ne pas permettre d'y accéder. Un chemin peut être routable mais refusé par un Security Group. Un flux peut être accepté par le pare-feu mais échouer à cause d'un service qui n'écoute pas sur le port attendu.

## 1.4. La méthode de conception « intention, chemin, preuve »

Pour chaque besoin, documenter trois éléments.

1. **Intention :** qui doit parler à qui, sur quel protocole et pourquoi ?
2. **Chemin :** quelles routes, passerelles, attachements, interfaces et contrôles traversent le flux ?
3. **Preuve :** quel test, journal ou analyse démontre que la configuration correspond à l'intention ?

Exemple :

```text
INTENTION
VPC-APP (10.20.0.0/16) doit joindre le service comptable
VPC-FINANCE (10.40.0.0/16) sur TCP/8443.
VPC-APP ne doit pas initier de connexion vers les autres VPC.

CHEMIN ATTENDU
Instance APP -> route table du subnet -> Transit Gateway
-> route table TGW du domaine applicatif -> attachment FINANCE
-> route table cible -> SG du service comptable.
Le retour doit utiliser un chemin cohérent, sans inspection asymétrique.

PREUVE
Reachability Analyzer si le chemin est pris en charge, test TCP depuis
une instance de test, VPC Flow Logs sur les interfaces concernées,
logs de pare-feu et validation de la règle SG.
```

## 1.5. Principes qui guident tout le cours

- **Deny by default au niveau de la conception :** ne créer que les chemins nécessaires.
- **Moindre privilège :** préférer un flux précis à une autorisation générale.
- **Segmentation explicite :** séparation des environnements, des fonctions et des niveaux de confiance.
- **Symétrie maîtrisée :** les équipements stateful doivent voir les deux sens d'une session.
- **Pas de chevauchement de CIDR :** prévoir les réseaux futurs, pas seulement les besoins immédiats.
- **Infrastructure as Code :** une architecture reproductible vaut mieux qu'une configuration manuelle non documentée.
- **Tester la négation :** vérifier non seulement que les flux voulus fonctionnent, mais aussi que les flux interdits échouent.
- **Coût et sécurité sont liés :** les chemins centralisés, les endpoints, les NAT et la journalisation doivent être conçus et budgétés ensemble.


# 2. Architecture de référence et conventions utilisées

## 2.1. Organisation logique d'une entreprise fictive

Le cours utilisera une entreprise fictive, **Orion**, avec plusieurs environnements et une connectivité vers un réseau local.

```text
ORGANISATION AWS
|
+-- Compte Network
|   +-- VPC-INSPECTION
|   +-- Transit Gateway régional
|   +-- Pare-feu de sortie centralisé
|   +-- VPC-DNS-SHARED (services DNS communs)
|
+-- Compte Production
|   +-- VPC-PROD-APP
|   +-- VPC-PROD-DATA
|
+-- Compte NonProduction
|   +-- VPC-DEV
|   +-- VPC-TEST
|
+-- Réseau on-premises Orion
    +-- 172.20.0.0/16
    +-- DNS interne
    +-- Applications historiques
```

Cette séparation est un modèle pédagogique. Le nombre de comptes et de VPC doit suivre les frontières de responsabilité, les exigences de sécurité, l'organisation et les contraintes opérationnelles réelles.

## 2.2. Plan d'adressage de référence

| Domaine | CIDR d'exemple | Rôle |
|---|---|---|
| PROD-APP | `10.20.0.0/16` | Services applicatifs de production |
| PROD-DATA | `10.30.0.0/16` | Données et services sensibles |
| DEV | `10.40.0.0/16` | Développement |
| TEST | `10.50.0.0/16` | Tests et validation |
| INSPECTION | `10.60.0.0/16` | Contrôles réseau centralisés |
| DNS-SHARED | `10.70.0.0/16` | Services DNS partagés |
| Réseau local | `172.20.0.0/16` | Applications historiques |

**Important :** ces blocs sont fictifs et ne constituent pas un plan d'adressage universel. Avant de les réutiliser, vérifier qu'ils ne chevauchent aucun réseau local, VPC, réseau partenaire ou plage réservée à une autre région.

Chaque VPC peut ensuite contenir plusieurs sous-réseaux par AZ et par rôle. Exemple pour PROD-APP :

```text
VPC-PROD-APP : 10.20.0.0/16
|
+-- AZ A
|   +-- subnet-app-a       10.20.10.0/24
|   +-- subnet-endpoint-a  10.20.20.0/24
|   +-- subnet-tgw-a       10.20.30.0/28
|
+-- AZ B
    +-- subnet-app-b       10.20.11.0/24
    +-- subnet-endpoint-b  10.20.21.0/24
    +-- subnet-tgw-b       10.20.31.0/28
```

Les sous-réseaux dédiés aux attachements TGW et aux endpoints sont des choix de conception fréquents, mais les exigences exactes dépendent de la ressource AWS déployée et de l'architecture retenue. Les tailles et sous-réseaux doivent être choisis en fonction des quotas, de la capacité disponible et de la documentation propre à chaque service.

## 2.3. Conventions de nommage

Privilégier des noms structurés, par exemple :

```text
<organisation>-<environnement>-<fonction>-<region>-<az>

orion-prod-app-eu-west-1a
orion-net-inspection-eu-west-1
orion-prod-rt-private-app-eu-west-1a
orion-prod-sg-app
orion-net-tgw-prod
```

Ne pas coder en dur des informations susceptibles d'être fausses après un changement. Les IDs AWS restent des identifiants techniques ; les tags et la documentation doivent apporter le contexte.

Tags conseillés selon la gouvernance de l'entreprise :

```text
Environment = prod | test | dev | shared
Owner       = equipe-proprietaire
CostCenter  = centre-de-cout
Application = nom-application
ManagedBy   = terraform | cloudformation | pipeline
DataClass   = public | internal | confidential | restricted
```

## 2.4. Matrice initiale des flux

Avant de créer des routes, définir les besoins.

| Source | Destination | Port/protocole | Autorisation | Justification |
|---|---|---|---|---|
| Internet | Load balancer public | TCP/443 | Oui, point d'entrée publié | HTTPS utilisateur |
| Load balancer | Application PROD | TCP/8443 | Oui | Requêtes applicatives |
| Application PROD | Données PROD | TCP/5432 | Oui, source strictement limitée | Accès base de données |
| DEV | Base PROD | Tous | Non | Séparation des environnements |
| Application PROD | S3 via endpoint | HTTPS/443 | Oui, bucket autorisé | Journaux et artefacts |
| Application PROD | Internet arbitraire | Tous | Non par défaut ; exceptions validées | Contrôle des sorties |
| On-premises | Services privés publiés | Flux nominativement autorisés | Selon besoin | Intégration hybride |

La matrice devient une référence pour les Security Groups, Network Firewall, routes, tests et audits.


# 3. Plan d'adressage à l'échelle : CIDR, IPAM, IPv6 et prévention des chevauchements

## 3.1. Pourquoi un plan d'adressage devient critique à grande échelle

Un seul VPC peut fonctionner avec un CIDR choisi rapidement. Une organisation comprenant des dizaines de VPC, plusieurs régions et plusieurs environnements peut rencontrer des conflits difficiles à corriger si chaque équipe choisit ses propres plages.

Les chevauchements impactent notamment :

- Le VPC Peering, qui ne prend pas en charge des CIDR IPv4 qui se chevauchent entre les VPC concernés.
- Le routage via Transit Gateway entre réseaux aux préfixes identiques ou ambigus.
- Les connexions VPN ou Direct Connect avec un réseau local.
- La migration d'applications et la fusion d'entreprises.
- Les règles de pare-feu et les journaux, dont les adresses peuvent devenir ambiguës.
- Les architectures multi-régions et l'usage de services partagés.

## 3.2. Réserver les blocs par domaine

Une méthode de départ consiste à attribuer des plages suffisamment larges par domaine, puis à allouer des VPC dans ces réserves.

```text
PLAN GLOBAL D'EXEMPLE
10.0.0.0/8
|
+-- 10.0.0.0/12     Réserve Région A
|   +-- 10.16.0.0/16  réservé à un domaine différent (hors bloc précédent)
|
+-- 10.32.0.0/12    Réserve Région B
|
+-- 10.64.0.0/12    Réserve environnement non-production
|
+-- 10.96.0.0/12    Réserve services partagés
|
+-- autres plages   Réserves futures documentées
```

Ce diagramme est illustratif : les réserves réelles doivent être calculées pour qu'elles ne se chevauchent pas. Ne pas recopier les lignes comme un plan mathématiquement validé sans vérifier les bornes CIDR.

La méthode correcte consiste à :

1. Recenser le LAN, les VPN, les plages partenaires et les VPC existants.
2. Définir les besoins régionaux et les réserves de croissance.
3. Vérifier les frontières CIDR et les chevauchements par outil.
4. Documenter la plage attribuée et son propriétaire.
5. Contrôler les nouvelles allocations dans un processus automatisé.

## 3.3. Amazon VPC IP Address Manager (IPAM)

VPC IPAM aide à planifier, suivre et superviser l'utilisation des adresses IP dans AWS. Il permet notamment de structurer des pools d'adresses, de surveiller l'utilisation, de suivre l'historique des allocations et d'allouer automatiquement des CIDR selon des règles définies.

Modèle conceptuel :

```text
IPAM
|
+-- Scope privé
    |
    +-- Pool organisation
        |
        +-- Pool Région A
        |   +-- Pool Production
        |   +-- Pool NonProduction
        |
        +-- Pool Région B
            +-- Pool Production
            +-- Pool NonProduction
```

Le schéma illustre une hiérarchie logique, pas une obligation de créer exactement ces pools.

### Processus conseillé

- Définir qui administre IPAM et qui peut allouer des plages.
- Définir les scopes privés/publics nécessaires selon le périmètre.
- Créer des pools et règles d'allocation correspondant au plan d'adressage de l'entreprise.
- Déléguer les droits de manière contrôlée aux comptes concernés.
- Suivre les ressources utilisant les CIDR et leurs allocations.
- Détecter les VPC non conformes ou les allocations manuelles non enregistrées.
- Réserver de l'espace pour de futurs VPC, extensions de CIDR et migrations.

IPAM ne remplace pas la gouvernance : il faut encore décider des plages autorisées, gérer les exceptions et empêcher les équipes de contourner le processus.

## 3.4. Calculer une subdivision sans chevauchement

Supposons une réserve `10.80.0.0/16`. On veut quatre VPC `/18`.

Un `/18` contient :

\[
2^{32-18}=16\,384\text{ adresses}
\]

Les quatre sous-réseaux sont :

```text
10.80.0.0/18       10.80.0.0  - 10.80.63.255
10.80.64.0/18      10.80.64.0 - 10.80.127.255
10.80.128.0/18     10.80.128.0 - 10.80.191.255
10.80.192.0/18     10.80.192.0 - 10.80.255.255
```

Les quatre blocs couvrent exactement le `/16`. Un plan peut réserver certains de ces blocs à des VPC particuliers plutôt que de tous les allouer immédiatement.

## 3.5. IPv6 : planifier plutôt que l'ajouter en urgence

IPv6 réduit fortement la pression sur les plages privées IPv4, mais introduit ses propres exigences de conception et de sécurité.

Il faut déterminer :

- Les VPC qui seront dual-stack et ceux qui seront IPv6-only.
- La manière d'attribuer les préfixes IPv6 aux VPC et aux sous-réseaux.
- Les chemins vers les destinations IPv6.
- Les contrôles de sécurité et règles SG/NACL applicables à IPv6.
- Les dépendances DNS avec les enregistrements A et AAAA.
- Les systèmes d'observabilité capables de représenter les adresses IPv6.
- Les besoins d'accès aux systèmes IPv4-only, éventuellement via DNS64/NAT64.

Ne pas considérer IPv6 comme sécurisé parce que ses adresses sont plus longues ou parce qu'il n'utilise pas NAT de la même manière. Les règles de sécurité et les routes doivent être explicitement conçues.

## 3.6. Atelier court : valider un plan CIDR

**Énoncé :** trois équipes demandent les blocs suivants : `10.100.0.0/16`, `10.100.128.0/17`, `10.101.0.0/16`.

**Analyse attendue :**

- `10.100.128.0/17` est inclus dans `10.100.0.0/16` : chevauchement.
- `10.101.0.0/16` est adjacent mais distinct du premier `/16` : pas de chevauchement avec `10.100.0.0/16`.
- Il faut réattribuer le deuxième bloc ou le choisir dans une réserve libre.

**Réflexion expert :** le rejet doit idéalement être effectué automatiquement dans le processus d'allocation, pas découvert après la mise en production d'un VPN ou d'un Transit Gateway.


# 4. Routage AWS avancé : sélection des routes, limites et chemins asymétriques

## 4.1. Une table de routage est une politique de sortie

Une route indique où envoyer les paquets dont la destination correspond à un préfixe. Elle ne décide pas à elle seule si un paquet est autorisé par les contrôles de sécurité.

Exemple de table de routage d'un sous-réseau d'application :

| Destination | Cible | Rôle |
|---|---|---|
| `10.20.0.0/16` | `local` | Communication dans le VPC |
| `10.30.0.0/16` | `tgw-...` | Réseau de données via Transit Gateway |
| `172.20.0.0/16` | `tgw-...` | Réseau local via Transit Gateway/VPN |
| `0.0.0.0/0` | `tgw-...` | Sortie centralisée si conçue ainsi |

Attention : la route par défaut vers TGW n'est correcte que si le chemin transit est configuré pour atteindre les destinations voulues et si le contrôle centralisé autorise ces flux. Une route `0.0.0.0/0 -> TGW` ne crée pas par elle-même de connectivité Internet.

## 4.2. Le principe du préfixe le plus spécifique

AWS utilise en général la correspondance du préfixe le plus long (longest prefix match) : parmi plusieurs routes correspondant à une destination, la route la plus spécifique est privilégiée. Lorsque des routes ont des destinations identiques, d'autres règles de priorité s'appliquent selon le type de route et le type de table.

Exemple pédagogique :

| Destination | Cible |
|---|---|
| `10.0.0.0/8` | TGW-A |
| `10.20.0.0/16` | TGW-B |
| `10.20.10.0/24` | Peering-C |
| `10.20.10.5/32` | Interface-D (si route valide et prise en charge) |

Une destination `10.20.10.5` correspond à plusieurs préfixes. La route `/32`, si elle est prise en charge et active dans la table concernée, est la plus spécifique. Pour une destination `10.20.10.7`, la route `/24` devient la plus spécifique des routes indiquées.

Ne pas simplifier la logique à « le plus long préfixe gagne toujours » sans regarder les contraintes du type de cible, les routes locales, les routes de service et les règles de priorité pour les destinations identiques.

## 4.3. VPC route tables et Transit Gateway route tables : deux systèmes distincts

Une erreur fréquente est de confondre les tables de routage d'un VPC avec les tables de routage du Transit Gateway.

```text
INSTANCE
   |
   v
TABLE DE ROUTAGE DU SOUS-RÉSEAU VPC
   |
   v
ATTACHEMENT TRANSIT GATEWAY
   |
   v
TABLE DE ROUTAGE DU TRANSIT GATEWAY
   |
   v
ATTACHEMENT DE DESTINATION
   |
   v
TABLE DE ROUTAGE DU SOUS-RÉSEAU VPC DESTINATAIRE
   |
   v
SECURITY GROUP / NETWORK ACL / SERVICE
```

Chaque table a des routes, des cibles et des règles d'association distinctes. Une route vers TGW dans le VPC ne suffit pas si la table du TGW ne possède pas de chemin approprié. De même, le TGW peut choisir le bon attachement alors que le VPC destinataire n'a pas de route de retour.

## 4.4. Le trafic retour doit être traité comme un besoin séparé

Considérons :

```text
VPC-A : 10.20.0.0/16
VPC-B : 10.30.0.0/16
```

Si A initie une connexion TCP vers B :

1. A doit avoir une route vers B.
2. La table TGW utilisée par l'attachement A doit contenir une route vers B.
3. L'attachement B doit être choisi comme destination.
4. B doit permettre le flux avec ses contrôles de sécurité.
5. La réponse de B doit pouvoir rejoindre A par le chemin attendu.
6. Les pare-feu stateful doivent recevoir les deux sens de la session lorsque leur état l'exige.

Un test qui réussit dans un sens n'est pas la preuve que toutes les communications requises fonctionnent. TCP dépend d'un échange bidirectionnel.

## 4.5. Routes statiques et routes propagées

Dans un Transit Gateway, les routes peuvent notamment provenir de routes statiques définies dans la table ou de propagations depuis des attachements. Le choix doit être conscient : les propagations facilitent l'échange de routes, tandis que des routes statiques permettent des décisions explicitement contrôlées, des routes de synthèse et parfois des chemins de secours.

Bonnes pratiques :

- Documenter quelles pièces jointes ont le droit de propager des préfixes dans chaque table TGW.
- Ne pas activer la propagation partout par commodité.
- Examiner les routes actives et les routes en conflit après chaque changement.
- Éviter les annonces de préfixes trop larges qui captureraient du trafic inattendu.
- Utiliser des routes de rejet/blackhole si une destination doit être explicitement injoignable et si le modèle retenu le permet.
- Tester l'effet des changements de route sur les flux existants et nouveaux.

## 4.6. Route par défaut centralisée : puissante mais risquée

Une table VPC contenant :

```text
0.0.0.0/0 -> Transit Gateway
```

peut envoyer le trafic IPv4 non couvert par une route plus spécifique vers une architecture centrale d'inspection ou d'egress.

Avantage : contrôle centralisé.

Risques :

- Dépendance envers les routes et les équipements du hub.
- Possibilité de détourner vers le hub un trafic destiné à une autre connexion.
- Frais de transfert, inspection et traitement.
- Défaillance potentielle si la route retour n'est pas conçue.
- Effet de panne étendu à plusieurs VPC.

Une route par défaut centralisée doit donc être couplée à des tables TGW segmentées, des routes explicites, des tests d'intention et un plan de récupération.

## 4.7. Une table main n'est pas une stratégie de gouvernance

Chaque VPC possède une table de routage principale. Les nouveaux sous-réseaux peuvent utiliser cette table si aucune association explicite différente ne leur est attribuée. En architecture contrôlée, il faut éviter de dépendre de valeurs implicites : associer explicitement les tables voulues, nommer les ressources et valider les associations dans le code.

Avant un changement : identifier les sous-réseaux réellement associés, pas seulement le nom de la table que l'on pense avoir configurée.

## 4.8. Diagnostiquer une route qui ne fait pas ce que l'on attend

Utiliser cette séquence :

```text
1. Quelle est l'IP de destination réelle ?
2. Une résolution DNS incorrecte a-t-elle fourni une autre IP ?
3. Quelle table de routage est associée au sous-réseau source ?
4. Quelle route correspond à la destination et laquelle est la plus spécifique ?
5. Quelle est la cible de cette route ?
6. Si la cible est TGW : quelle table est associée à l'attachement source ?
7. Quelle route TGW est sélectionnée et quel attachement en résulte ?
8. La table du sous-réseau de destination autorise-t-elle le retour ?
9. Un SG, NACL, firewall ou endpoint policy bloque-t-il le flux ?
10. Quel journal ou test confirme le premier composant bloquant ?
```


# 5. Transit Gateway : architecture hub-and-spoke et segmentation par domaines

## 5.1. Pourquoi le VPC Peering seul devient difficile à gérer

Avec quelques VPC, le VPC Peering peut convenir. À grande échelle, une topologie maillée augmente le nombre de connexions à gérer et ne fournit pas de routage transitif entre pairs.

Pour un maillage complet de `n` VPC, le nombre de connexions bidirectionnelles nécessaires est :

\[
C = \frac{n(n-1)}{2}
\]

Par exemple, avec 10 VPC :

\[
C = \frac{10 \times 9}{2} = 45
\]

Ce nombre ne représente pas les coûts totaux ni une limite de service ; il illustre l'augmentation du nombre de relations à gérer.

## 5.2. Modèle hub-and-spoke avec Transit Gateway

Transit Gateway sert de point de transit régional pour connecter de nombreux VPC et certaines connexions hybrides à l'aide d'attachements et de tables de routage de transit.

```text
                         RÉSEAU ON-PREMISES
                                  |
                           VPN / Direct Connect
                                  |
                                  v
+-------------+            +--------------+            +-------------+
| VPC-PROD    |--attache-->|              |<--attache--| VPC-DEV     |
| 10.20/16    |            | TRANSIT      |            | 10.40/16    |
+-------------+            | GATEWAY      |            +-------------+
                           |              |
+-------------+            |              |            +-------------+
| VPC-DATA    |--attache-->|              |<--attache--| VPC-TOOLS   |
| 10.30/16    |            +--------------+            | 10.70/16    |
+-------------+                                        +-------------+
```

Le Transit Gateway ne constitue pas un pare-feu applicatif automatique. Sa capacité à acheminer un paquet est distincte de la décision de l'autoriser.

## 5.3. Les objets à distinguer

- **Transit Gateway :** routeur de transit régional.
- **Attachment :** connexion d'un VPC, VPN, Direct Connect Gateway, autre TGW ou autre type de connexion pris en charge.
- **Transit Gateway route table :** table qui décide vers quel attachement le trafic est envoyé.
- **Association :** lie un attachement à une table TGW pour l'acheminement des paquets entrants depuis cet attachement.
- **Propagation :** publie les routes associées à un attachement dans une table TGW.
- **Route statique :** route ajoutée manuellement à une table TGW.
- **Blackhole route :** route destinée à supprimer le trafic d'une destination, plutôt que de l'envoyer vers un attachement.
- **Appliance mode :** mécanisme qui aide à maintenir la cohérence de sélection de l'interface d'appliance pour une session traversant un VPC d'inspection, lorsque le modèle et les paramètres le requièrent.

L'association et la propagation sont différentes. Une association décide quelle table traite le trafic reçu d'un attachement. Une propagation indique dans quelles tables ses routes sont publiées.

## 5.4. Segmenter avec plusieurs tables TGW

Une table unique à laquelle tous les VPC sont associés et vers laquelle tous les préfixes sont propagés est simple à expliquer mais peut donner une connectivité trop permissive.

Exemple de segmentation :

```text
TRANSIT GATEWAY
|
+-- RT-PROD
|   +-- Routes vers VPC-PROD-APP
|   +-- Routes vers VPC-PROD-DATA
|   +-- Routes vers services partagés explicitement autorisés
|
+-- RT-NONPROD
|   +-- Routes vers VPC-DEV
|   +-- Routes vers VPC-TEST
|   +-- Routes vers services partagés explicitement autorisés
|
+-- RT-ONPREM
|   +-- Routes vers réseaux on-premises autorisés
|   +-- Routes vers domaines qui doivent être accessibles au LAN
|
+-- RT-INSPECTION
    +-- Routes vers VPC de charge
    +-- Routes vers les destinations d'egress
```

Le nom des tables n'impose aucune sémantique AWS. C'est le contenu réel de la table, les associations et les propagations qui déterminent la connectivité.

## 5.5. Exemple d'associations et de propagations contrôlées

| Attachement | Table associée | Routes propagées vers | But |
|---|---|---|---|
| VPC-PROD-APP | RT-PROD | RT-PROD, RT-ONPREM si requis | Production |
| VPC-PROD-DATA | RT-PROD-DATA | RT-PROD si besoin d'accès | Isoler la donnée |
| VPC-DEV | RT-NONPROD | RT-NONPROD uniquement | Isoler les tests |
| VPN-ONPREM | RT-ONPREM | Tables explicitement autorisées | LAN hybride |
| VPC-INSPECTION | RT-INSPECTION | RT-INSPECTION et tables concernées selon le design | Inspection centrale |

Cette matrice est illustrative. Il faut vérifier les chemins retour et les restrictions de connectivité nécessaires pour chaque flux.

## 5.6. Contrôler les chemins entre environnements

Exigence : DEV peut joindre un service de dépôt d'artefacts partagé, mais ne peut pas joindre les bases de production.

Conception possible :

1. Ne pas propager ou ajouter de route DEV vers le VPC de données de production dans sa table TGW.
2. Ne pas créer de routes qui rendraient le même préfixe accessible par un chemin alternatif.
3. Restreindre également les Security Groups et politiques applicatives.
4. Appliquer un filtrage central si nécessaire, sans considérer ce filtrage comme substitut à la segmentation du routage.
5. Valider que le réseau on-premises ne permet pas à DEV de contourner la politique et d'atteindre les bases par un chemin indirect.
6. Prouver le blocage à l'aide de tests et d'outils d'analyse.

La sécurité est plus solide lorsque plusieurs contrôles cohérents se complètent sans que l'un soit le seul rempart.

## 5.7. Limites du Transit Gateway et chevauchements

Les réseaux connectés doivent être conçus en tenant compte des plages CIDR qui se chevauchent. Les réseaux aux plages identiques peuvent rendre le routage ambigu. Le simple fait d'attacher un VPC au TGW ne garantit pas qu'une connectivité exploitable sera possible avec un autre réseau qui partage ses adresses.

Options à envisager en cas de chevauchement :

- Renumérotation, généralement plus propre mais parfois difficile.
- Segmentation des domaines et routes très spécifiques lorsque cela suffit réellement.
- Traduction d'adresses par une architecture conçue et testée, si la renumérotation est impossible.
- Publication de services via AWS PrivateLink au lieu d'accorder une connectivité IP réseau complète.

Ne pas utiliser une exception de routage pour masquer un problème de plan d'adressage qui s'étend à toute l'entreprise.

## 5.8. Commandes AWS CLI de contrôle

Les exemples suivants utilisent des identifiants fictifs. Les commandes `describe` servent à l'inspection et ne modifient pas la configuration.

```bash
# Lister les Transit Gateways de la région configurée
aws ec2 describe-transit-gateways

# Lister les attachements d'un Transit Gateway
aws ec2 describe-transit-gateway-attachments \
  --filters Name=transit-gateway-id,Values=tgw-EXAMPLE

# Examiner les tables de routage TGW
aws ec2 describe-transit-gateway-route-tables \
  --filters Name=transit-gateway-id,Values=tgw-EXAMPLE

# Examiner les routes actives et candidates d'une table TGW
aws ec2 search-transit-gateway-routes \
  --transit-gateway-route-table-id tgw-rtb-EXAMPLE \
  --filters Name=state,Values=active

# Examiner les associations d'une table
aws ec2 get-transit-gateway-route-table-associations \
  --transit-gateway-route-table-id tgw-rtb-EXAMPLE

# Examiner les propagations d'une table
aws ec2 get-transit-gateway-route-table-propagations \
  --transit-gateway-route-table-id tgw-rtb-EXAMPLE
```

Dans les scripts d'exploitation, vérifier le compte, la région, le profil AWS CLI et les permissions avant d'exécuter les commandes. Les opérations de modification doivent passer par un processus de changement contrôlé.

## 5.9. Quand préférer VPC Peering, Transit Gateway ou PrivateLink ?

| Besoin | Option à examiner | Limite ou avantage principal |
|---|---|---|
| Quelques VPC qui se parlent directement | VPC Peering | Simple, mais non transitif |
| Nombreux VPC et connexions hybrides | Transit Gateway | Hub de routage central, coûts et gouvernance nécessaires |
| Exposer un service précis à des consommateurs | PrivateLink | Publie un service, pas un accès IP complet au VPC fournisseur |
| Connectivité globale entre régions/sites | Transit Gateway inter-régional, Cloud WAN ou autre architecture adaptée | Dépend du périmètre, de la complexité et du modèle d'exploitation |
| Besoin de politique globale de connectivité de nombreux sites | Cloud WAN à évaluer | Politique de réseau global et opérations associées |

Ces options ne sont pas toujours exclusives. Une architecture réelle peut combiner TGW pour le routage, PrivateLink pour publier des services et VPN/DX pour le réseau hybride.


# 6. Inspection centralisée : AWS Network Firewall, appliances et symétrie des flux

## 6.1. Pourquoi centraliser l'inspection ?

Une organisation peut exiger que les flux entre réseaux, vers Internet et vers le réseau local passent par un point de contrôle central pour appliquer une politique uniforme et produire des journaux cohérents.

```text
                    VPC-PROD
                       |
                       | route vers TGW
                       v
                  TRANSIT GATEWAY
                       |
                       v
                VPC-INSPECTION
                +-------------------+
                | AWS Network       |
                | Firewall /        |
                | appliances        |
                +-------------------+
                       |
             +---------+----------+
             |                    |
           INTERNET           ON-PREMISES
```

Une telle architecture ne fonctionne correctement que si les routes aller et retour, les associations TGW, les règles du pare-feu et les chemins d'egress sont conçus ensemble.

## 6.2. AWS Network Firewall

AWS Network Firewall fournit des contrôles de trafic réseau gérés, avec des règles stateless et stateful, selon les capacités documentées du service. Il peut être utilisé dans un VPC dédié à l'inspection et intégré à une architecture de transit.

Les règles doivent être conçues selon le besoin réel :

- Protocoles et ports autorisés.
- Sources et destinations.
- Filtrage stateful ou stateless.
- Filtrage par domaine ou autres attributs pris en charge par les règles adaptées.
- Journalisation et destination des logs.
- Priorité et comportement par défaut des règles.
- Test des connexions autorisées et des connexions interdites.

Ne pas confondre Network Firewall, Security Groups, NACL, WAF et IAM. Ils répondent à des couches et des objectifs différents.

## 6.3. Le problème de l'asymétrie

Considérons un équipement stateful qui observe le chemin aller mais pas le chemin retour.

```text
FLUX ALLER
VPC-A -> TGW -> Firewall -> VPC-B

FLUX RETOUR MAL CONÇU
VPC-B -> TGW ----------------> VPC-A
                 (Firewall contourné)
```

Le pare-feu peut ne pas reconnaître le retour comme faisant partie d'une session suivie. La session peut échouer même si certaines routes semblent correctes.

Chemin désiré :

```text
ALLER : VPC-A -> TGW -> Firewall -> VPC-B
RETOUR: VPC-B -> TGW -> Firewall -> VPC-A
```

Il faut ensuite vérifier que le chemin retour traverse l'état de firewall attendu et que les routes de chaque sous-réseau et de chaque attachement sont cohérentes.

## 6.4. Appliance mode et sélection du chemin

Lorsqu'une architecture s'appuie sur des appliances stateful au sein d'un VPC attaché à un Transit Gateway, l'appliance mode peut être nécessaire. Il aide le Transit Gateway à maintenir une sélection cohérente de l'interface d'appliance pour un flux entre zones, sous réserve des exigences du service et de l'architecture choisie.

L'appliance mode n'est pas une réparation universelle. Il ne remplace pas :

- Les routes vers l'interface de firewall.
- La route retour.
- Les tables de routage TGW appropriées.
- Le routage local dans le VPC d'inspection.
- La configuration du service de pare-feu.
- La vérification des chemins depuis les VPC consommateurs.

## 6.5. Concevoir le VPC d'inspection

Exemple conceptuel sur deux AZ :

```text
VPC-INSPECTION : 10.60.0.0/16
|
+-- AZ A
|   +-- subnet-tgw-a          10.60.10.0/24
|   +-- subnet-firewall-a     10.60.20.0/24
|   +-- subnet-egress-a       10.60.30.0/24
|
+-- AZ B
    +-- subnet-tgw-b          10.60.11.0/24
    +-- subnet-firewall-b     10.60.21.0/24
    +-- subnet-egress-b       10.60.31.0/24
```

Ce plan est illustratif. Les exigences réelles de sous-réseau et de déploiement varient selon les endpoints de firewall, les attachements, les zones retenues et le service utilisé.

À concevoir explicitement :

- Les sous-réseaux d'attachement au transit.
- Les routes qui envoient les flux vers le firewall.
- Les routes de sortie du firewall vers la destination.
- Les routes de retour vers les VPC et les réseaux on-premises.
- Les besoins de NAT et les endroits où il s'applique.
- Les règles d'inspection internes et sortantes.
- Les politiques de journalisation et la rétention.
- La tolérance aux pannes d'une AZ ou d'une ressource.

## 6.6. Inspection centrale des sorties Internet

Flux logique attendu :

```text
Instance privée du VPC-APP
          |
          v
Route table du subnet-app
0.0.0.0/0 -> Transit Gateway
          |
          v
Table TGW du domaine d'origine
          |
          v
Attachment du VPC-INSPECTION
          |
          v
Network Firewall / appliance
          |
          v
NAT / route de sortie appropriée
          |
          v
Internet Gateway du VPC d'egress
          |
          v
       INTERNET
```

Le NAT Gateway, quand il est utilisé, est une fonction de traduction et de sortie IPv4. Il n'inspecte pas le contenu du trafic comme un firewall stateful. La politique de filtrage doit rester distincte.

### Contrôles à tester

- Le trafic autorisé atteint son service.
- Le trafic non autorisé est bloqué par la règle attendue.
- Les flux de retour traversent les composants stateful requis.
- Les flux directs qui contournent l'inspection ne sont pas routables depuis les sources concernées.
- Les logs contiennent les champs suffisants pour expliquer la décision.
- L'indisponibilité d'un composant ou d'une AZ a un comportement documenté.

## 6.7. Risques d'une centralisation excessive

Une architecture centrale réduit la duplication de politiques, mais crée un composant critique. Les erreurs peuvent affecter de nombreux VPC. Le coût du transit, des données transférées, de l'inspection et des NAT peut aussi devenir important.

Il faut envisager :

- La haute disponibilité par AZ.
- Les quotas et capacités réelles.
- Le nombre de flux et la bande passante.
- La latence ajoutée.
- La procédure de changement et de rollback.
- Le plan de secours si le hub est indisponible.
- Les exceptions de trafic nécessaires aux services AWS.
- La détection d'un chemin de contournement.


# 7. Connectivité hybride : Site-to-Site VPN, BGP, Direct Connect et bascule

## 7.1. Objectif de la connectivité hybride

La connectivité hybride relie les ressources AWS à un réseau qui n'est pas dans le VPC, par exemple un centre de données, un siège ou un environnement partenaire.

Les options comprennent notamment AWS Site-to-Site VPN, AWS Direct Connect et des architectures les combinant.

```text
                 AWS REGION
       +--------------------------------+
       |        TRANSIT GATEWAY         |
       +----------------+---------------+
                        |
                +-------+-------+
                |               |
              VPN             Direct Connect
                |               |
                +-------+-------+
                        |
                  EDGE ON-PREMISES
                        |
                 ROUTEUR / FIREWALL
                        |
                    LAN INTERNE
```

Ce schéma représente deux options de connexion et non une configuration automatique de bascule. Les routes, les annonces BGP, les priorités et les capacités de chaque connexion doivent être configurées.

## 7.2. AWS Site-to-Site VPN

Site-to-Site VPN établit une connectivité IPsec entre un réseau distant et AWS à travers des tunnels. Selon l'architecture, la connexion peut être terminée sur un virtual private gateway ou intégrée à une architecture Transit Gateway.

Points de conception :

- Deux tunnels sont généralement fournis pour une connexion VPN Site-to-Site ; les deux doivent être configurés conformément aux consignes AWS et de l'équipement client.
- Les paramètres de chiffrement, d'authentification et les secrets doivent être gérés de manière sûre.
- Le routage peut être statique ou dynamique, selon le type de passerelle et la configuration.
- Avec BGP, surveiller l'état des sessions et les préfixes annoncés/reçus.
- Les règles de pare-feu et les ACL côté on-premises doivent autoriser les flux nécessaires.
- La MTU, la fragmentation et le MSS TCP peuvent affecter les applications même lorsque le tunnel est établi.

Le statut « tunnel UP » n'est pas la preuve que tous les préfixes sont annoncés ni que toutes les applications sont accessibles.

## 7.3. BGP : ce qu'un architecte réseau doit vérifier

BGP est un protocole de routage dynamique qui permet d'échanger des préfixes et des attributs de chemin entre systèmes autonomes ou domaines de routage définis.

Dans un contexte hybride AWS, vérifier notamment :

- L'établissement des sessions BGP.
- Le voisinage configuré, l'ASN et les paramètres attendus.
- Les préfixes annoncés depuis chaque côté.
- Les préfixes effectivement reçus et acceptés.
- Les filtres de routes et les agrégations.
- Les chemins de secours et leur préférence.
- Les annonces trop larges ou inattendues.
- La convergence après perte d'un tunnel ou d'une connexion.

Exemple de checklist de préfixes :

| Préfixe | Qui doit l'annoncer ? | Destinataires attendus | Contrôle |
|---|---|---|---|
| `172.20.0.0/16` | On-premises | TGW et VPC autorisés | Présence dans la table attendue |
| `10.20.0.0/16` | AWS/VPC via l'architecture | On-premises si besoin | Filtrage avant annonce |
| `0.0.0.0/0` | Un edge désigné seulement si nécessaire | Périmètre contrôlé | Ne pas annoncer par erreur à tous les domaines |

Ne pas annoncer un résumé `10.0.0.0/8` simplement parce qu'il englobe les VPC : cela peut attirer des flux vers un chemin qui n'a aucune route plus spécifique, puis les perdre.

## 7.4. Direct Connect

Direct Connect fournit une liaison réseau dédiée entre un site et AWS via un emplacement Direct Connect. Il ne doit pas être décrit comme un tunnel chiffré IPsec par défaut : si le chiffrement est requis, il faut choisir une solution de chiffrement appropriée à l'architecture et à la compatibilité de service.

Les décisions importantes incluent :

- Débit et type de port nécessaires.
- Emplacement et opérateur partenaire éventuel.
- Virtual interfaces et gateway appropriés.
- Modèle de routage BGP.
- Redondance du site, du routeur, du circuit et du fournisseur.
- Objectif de disponibilité et processus de bascule.
- Besoin de VPN de secours.
- Mesures de sécurité pour les flux transportés.

Une seule connexion physique, même dédiée, peut rester un point de défaillance. Les besoins de résilience doivent inclure la connectivité physique et le routage, pas seulement le service logique AWS.

## 7.5. Direct Connect principal et VPN de secours

Une architecture fréquente utilise Direct Connect comme chemin principal et un VPN comme chemin de secours. Le comportement réel de sélection des routes dépend du type d'attachement, du routage dynamique, des préfixes reçus et des mécanismes de préférence disponibles.

Ne jamais déclarer une bascule automatique fiable sans la tester. Vérifier :

1. État normal : les routes et le trafic empruntent le chemin principal prévu.
2. Perte d'une interface ou du circuit principal : les routes de secours deviennent utilisables.
3. Retour du circuit principal : le trafic revient selon la politique attendue, sans oscillation incontrôlée.
4. Les sessions applicatives survivent ou se rétablissent selon les garanties réalistes.
5. Les alertes détectent la bascule et l'équipe possède un runbook.

## 7.6. MTU, MSS et gros paquets

Une connectivité peut réussir pour les petits paquets et échouer pour des transferts plus volumineux. Les tunnels, l'encapsulation et certains chemins intermédiaires réduisent la taille utile des paquets ou modifient le comportement de la découverte de MTU.

Symptômes possibles :

- SSH fonctionne, mais un transfert de fichier bloque.
- La négociation TCP se termine, mais le transfert ne progresse pas.
- Certaines réponses HTTPS échouent lorsqu'elles sont volumineuses.
- Un ping avec charge utile faible passe, mais un test avec paquet large échoue.

Approche :

- Déterminer le MTU de bout en bout et les couches d'encapsulation.
- Contrôler les messages ICMP nécessaires à la découverte de MTU selon la famille IP et le contexte.
- Vérifier les paramètres TCP MSS sur les équipements qui les modifient.
- Tester des tailles de paquets progressives dans un environnement autorisé.
- Éviter de changer le MSS au hasard sans mesurer l'effet.

## 7.7. Runbook de perte de connectivité hybride

```text
ÉTAPE 1 — État physique/logique
  Le circuit, l'interface, le tunnel et les équipements sont-ils actifs ?

ÉTAPE 2 — Voisinage de routage
  BGP est-il établi ? Les routes sont-elles reçues et annoncées ?

ÉTAPE 3 — Sélection de route
  Quel préfixe AWS utilise-t-il ? Quel préfixe le routeur local utilise-t-il ?

ÉTAPE 4 — Tables TGW/VPC
  Les routes existent-elles dans la table TGW associée ?
  Les VPC ont-ils leurs routes retour ?

ÉTAPE 5 — Sécurité
  SG, NACL, firewall AWS et pare-feu on-premises autorisent-ils le flux ?

ÉTAPE 6 — DNS
  Le nom pointe-t-il vers l'adresse attendue depuis chaque côté ?

ÉTAPE 7 — MTU / application
  Les petits tests passent-ils mais pas les gros transferts ?

ÉTAPE 8 — Preuves et rétablissement
  Capturer l'état des routes, les timestamps, les Flow Logs et les événements.
```


# 8. AWS Cloud WAN et choix entre modèles de connectivité

## 8.1. Où se situe Cloud WAN ?

AWS Cloud WAN est un service de mise en réseau globale qui permet de construire et de gérer un réseau mondial avec une politique de réseau centralisée. Il vise des scénarios où la gestion de la connectivité entre régions, VPC et sites peut devenir plus complexe qu'une administration manuelle de connexions et de routeurs.

Transit Gateway demeure une option importante pour le transit régional et les architectures hub-and-spoke. Cloud WAN et Transit Gateway peuvent être comparés selon les besoins de gestion globale, les politiques de segmentation, les connexions nécessaires et les opérations existantes.

## 8.2. Modèle conceptuel Cloud WAN

```text
                    POLITIQUE DE RÉSEAU GLOBALE
                               |
                               v
                         AWS CLOUD WAN
                               |
             +-----------------+-----------------+
             |                 |                 |
          Région A          Région B        Site distant
             |                 |                 |
          VPC PROD          VPC DATA          VPN / DX
             |
          VPC DEV
```

Le schéma exprime une vue logique et ne détaille pas les segments, attachements ou règles d'une politique réelle.

## 8.3. Les questions qui guident le choix

| Critère | Transit Gateway | Cloud WAN |
|---|---|---|
| Besoin principal | Transit régional et connectivité hub-and-spoke | Gouvernance et connectivité réseau globale par politique |
| Modèle d'administration | Gestion des TGW, tables et attachements | Gestion d'un cœur global et d'une politique de réseau |
| Échelle | Efficace pour de nombreux réseaux régionaux | À considérer pour des réseaux multisites/multirégions nécessitant une vue globale |
| Compétences existantes | Équipes qui maîtrisent TGW | Équipes prêtes à gouverner une politique réseau plus globale |
| Coût | Dépend des attachements, du traitement et du transfert | Dépend des éléments Cloud WAN utilisés, des attachements et du transfert |

Ce tableau est une orientation initiale, pas une recommandation universelle. Comparer les services réellement disponibles dans les régions ciblées, leurs limites, leur facturation actuelle et la migration opérationnelle à prévoir.

## 8.4. Gouvernance de la politique réseau

Quel que soit le service choisi, une politique réseau devrait spécifier :

- Les segments/environnements attendus.
- Les VPC et sites autorisés à les rejoindre.
- Les communications inter-segments permises.
- Les chemins vers l'inspection centrale.
- Les routes annoncées vers les sites et services partagés.
- La manière d'introduire une nouvelle région ou un nouvel environnement.
- Le propriétaire de l'approbation d'une exception.
- Les preuves de validation et le rollback.

La centralisation de la politique ne dispense pas de tester les flux ni de surveiller la dérive.


# 9. PrivateLink, endpoints, DNS privé et contrôle de l'accès aux services

## 9.1. Pourquoi PrivateLink est différent du transit IP

Le routage entre VPC fournit une connectivité réseau selon les routes et contrôles. AWS PrivateLink permet à un consommateur d'accéder à un service pris en charge via des interfaces privées sans nécessiter l'exposition d'un accès général au réseau du fournisseur.

```text
VPC-CONSUMER
  Instance / client
        |
        v
  Interface endpoint (ENI privée)
        |
   réseau PrivateLink géré
        |
        v
VPC-PROVIDER
  Service publié / endpoint service
```

Le client ne reçoit pas une route générale vers tous les sous-réseaux du fournisseur. Cela peut réduire la portée de la relation réseau.

## 9.2. Quand choisir PrivateLink ?

PrivateLink mérite d'être étudié lorsque :

- Un fournisseur doit exposer un service précis à plusieurs consommateurs.
- Les consommateurs et producteurs ont des plages CIDR qui se chevauchent.
- On ne souhaite pas permettre un routage complet entre les deux VPC.
- Le service doit être consommé en privé par plusieurs comptes.
- L'accès doit être limité à un point de service plutôt qu'à un réseau complet.

Il ne remplace pas toutes les architectures de VPC à VPC. Il faut vérifier que le type de service à publier et le modèle d'accès sont pris en charge par PrivateLink.

## 9.3. Interface endpoints et gateway endpoints

| Type | Caractéristique générale | À retenir |
|---|---|---|
| Interface endpoint | Utilise des interfaces réseau privées dans les sous-réseaux choisis | Le SG de l'endpoint est une partie importante du contrôle du trafic |
| Gateway endpoint | Route vers un service pris en charge, notamment S3 ou DynamoDB, via une entrée de table de routage | Le modèle de contrôle est différent de celui d'un interface endpoint |

Ne pas traiter tous les endpoints comme identiques. Les exigences DNS, les politiques, la disponibilité régionale, les routes et la facturation peuvent varier selon le service et le type de point de terminaison.

## 9.4. Private DNS : un nom correct ne prouve pas que le chemin fonctionne

Pour un interface endpoint, les noms DNS privés permettent souvent au client d'utiliser le nom habituel du service tout en résolvant une adresse privée d'endpoint, lorsque les paramètres et la configuration du service le permettent.

Vérifications :

1. Le DNS du VPC est configuré de manière appropriée.
2. Le private DNS de l'endpoint est activé lorsque nécessaire.
3. Les requêtes proviennent du bon VPC et utilisent le résolveur prévu.
4. Le SG de l'endpoint autorise le trafic du client sur le port requis.
5. Les routes et NACL permettent le chemin.
6. L'endpoint policy, les politiques IAM et les politiques de la ressource ne refusent pas l'opération.
7. Le service cible et la région sont corrects.

## 9.5. Endpoint policies et identité IAM

Les endpoint policies peuvent restreindre les actions et ressources autorisées à travers un endpoint lorsqu'elles sont prises en charge. Elles ne remplacent pas les politiques IAM ni les politiques de la ressource cible.

Exemple de défense en profondeur pour l'accès à un bucket S3 :

```text
Instance privée
   |
   +-- IAM role : autorise seulement les actions nécessaires
   |
   +-- SG/NACL : permettent le trafic réseau nécessaire
   |
   +-- Route table : dirige le trafic vers l'endpoint adapté
   |
   +-- Endpoint policy : limite les accès via cet endpoint
   |
   +-- Bucket policy : impose les conditions d'accès au bucket
```

Les règles doivent être compatibles entre elles. Une permission réseau n'accorde pas l'autorisation S3, et une permission IAM n'invente pas un chemin réseau absent.

## 9.6. Réduire la dépendance au NAT grâce aux endpoints

Si des workloads privés utilisent fréquemment des services AWS, il peut être pertinent d'évaluer les endpoints disponibles afin d'éviter que les appels concernés passent par un NAT Gateway et l'Internet public.

Il faut toutefois comparer :

- Les frais d'endpoint, le nombre d'AZ et le volume de données.
- Le coût du NAT, du transfert et des données traitées.
- Les besoins DNS et les politiques de sécurité.
- Les services qui ne prennent pas en charge le type d'endpoint souhaité.
- La résilience et l'impact de la suppression d'une route de sortie.

La meilleure architecture est celle dont le chemin est nécessaire, autorisé, observable et économiquement raisonnable.


# 10. DNS hybride avec Route 53 VPC Resolver et DNS Firewall

## 10.1. Le DNS est une dépendance du réseau

Un diagnostic réseau doit toujours distinguer la résolution de noms de la connectivité IP.

Une application peut échouer alors que le routage IP fonctionne parce que :

- Le nom résout vers une adresse obsolète.
- Un enregistrement A et un enregistrement AAAA ne représentent pas des chemins équivalents.
- Une private hosted zone n'est associée qu'à certains VPC.
- Une règle de forwarding DNS n'est pas associée au VPC attendu.
- Le réseau local ne peut pas atteindre les adresses d'un endpoint Resolver.
- Le port UDP/53 fonctionne, mais le chemin TCP/53 nécessaire dans certains cas est bloqué.
- Un nom interne est masqué par une zone privée plus spécifique ou une règle DNS concurrente.

## 10.2. Route 53 VPC Resolver

Le résolveur DNS fourni par AWS pour un VPC traite les demandes DNS des ressources de ce VPC. Il permet notamment de résoudre les noms publics, certains noms internes propres à VPC et les enregistrements des private hosted zones associées.

Pour un VPC IPv4, l'adresse du résolveur du VPC est généralement l'adresse IPv4 du bloc VPC plus deux. Cela ne signifie pas que les machines on-premises ou les autres VPC doivent interroger directement cette adresse. Pour intégrer un DNS distant, utiliser le mécanisme d'endpoints Resolver et les règles de forwarding adaptés.

## 10.3. Modèle DNS hybride

```text
                  VPC CLOUD
              +------------------+
              | Instances privées|
              +--------+---------+
                       |
                       v
              Route 53 VPC Resolver
                       |
              Règle de forwarding
                       |
                       v
              Outbound Resolver endpoint
                       |
            VPN / Direct Connect / transit
                       |
                       v
              DNS ON-PREMISES
              internal.orion.example
```

Pour résoudre des noms AWS depuis le réseau local :

```text
Client on-premises
       |
       v
DNS interne on-premises
       |
Règle de forwarding conditionnelle
       |
       v
Inbound Resolver endpoint dans AWS
       |
       v
Route 53 VPC Resolver / private hosted zone
       |
       v
Réponse vers le client
```

Les endpoints doivent être déployés dans un ou plusieurs sous-réseaux/AZ selon les recommandations du service et la disponibilité recherchée. Les routes, SG, NACL et ACL du réseau local doivent permettre le trafic DNS nécessaire, en UDP et selon le besoin en TCP.

## 10.4. Règles de forwarding conditionnelles

Exemple d'intention :

```text
Domaine public : orion.example
  -> Résolution publique, selon la configuration DNS habituelle

Domaine privé AWS : aws.orion.example
  -> Private hosted zone associée aux VPC concernés

Domaine hérité : legacy.orion.example
  -> DNS on-premises via Resolver outbound endpoint

Domaine de test : dev.orion.example
  -> Zone privée ou résolveur de test accessible seulement aux environnements DEV
```

La priorité effective des règles et des zones doit être testée. Éviter les domaines trop génériques qui risquent d'envoyer des requêtes au mauvais résolveur.

## 10.5. DNS Firewall

Route 53 Resolver DNS Firewall permet d'appliquer des règles au trafic de résolution DNS sortant qui passe par le VPC Resolver. Il peut être utilisé pour bloquer des domaines malveillants, réduire certaines tentatives d'exfiltration DNS ou appliquer une liste d'autorisation de domaines pour des workloads spécifiques.

Exemple d'approche progressive :

1. Activer une journalisation pertinente.
2. Observer les domaines réellement utilisés.
3. Construire des règles et des groupes réutilisables.
4. Commencer en mode de surveillance lorsqu'il est pris en charge et adapté.
5. Examiner les faux positifs et les domaines dépendants.
6. Déployer progressivement les règles bloquantes.
7. Définir une procédure d'exception approuvée.

Le filtrage DNS n'inspecte pas automatiquement toutes les connexions réseau. Une application peut utiliser une IP codée en dur ou un résolveur DNS différent. La stratégie doit aussi prendre en compte l'egress, les services de résolution autorisés et les comportements de contournement.

## 10.6. Tests DNS à exécuter

Depuis une machine de test autorisée :

```bash
# Résolution A
nslookup service.aws.orion.example

# Requête explicite avec dig, si disponible
dig service.aws.orion.example A

# Vérifier IPv6
dig service.aws.orion.example AAAA

# Tester un résolveur précis
dig @10.70.10.10 service.legacy.orion.example

# Vérifier TCP/443 après résolution, avec un client approprié
curl -v --connect-timeout 5 https://service.aws.orion.example/
```

`10.70.10.10` est une adresse d'exemple et ne doit pas être copiée sans remplacer par l'adresse réelle du résolveur cible.

Comparer la réponse DNS, l'IP cible et le chemin réseau. Une résolution réussie ne garantit pas que le service écoute ni que le flux est autorisé.


# 11. Architecture IPv6 dual-stack et IPv6-only

## 11.1. Dual-stack

Une architecture dual-stack utilise IPv4 et IPv6 en parallèle. Elle peut faciliter la migration progressive, mais exige que les applications, les politiques de sécurité, les logs et les chemins réseau soient cohérents pour les deux familles d'adresses.

```text
VPC DUAL-STACK
IPv4 : 10.80.0.0/16
IPv6 : préfixe IPv6 attribué au VPC
|
+-- Sous-réseau App A
|   +-- IPv4 privée
|   +-- IPv6 globale ou interne selon l'attribution
|
+-- Sous-réseau App B
    +-- IPv4 privée
    +-- IPv6 globale ou interne selon l'attribution
```

Un utilisateur peut constater que l'accès IPv4 fonctionne alors que l'accès IPv6 échoue, ou l'inverse. Il faut donc tester les deux familles explicitement.

## 11.2. IPv6 et Internet

Les adresses IPv6 ne sont pas traitées comme les adresses privées RFC1918 IPv4 avec NAT. Une adresse IPv6 routable peut être globalement unique ; la possibilité réelle d'initier une connexion entrante reste dépendante des routes et des contrôles de sécurité.

Pour autoriser la sortie IPv6 tout en empêchant Internet d'initier des connexions vers les instances, AWS propose un **egress-only internet gateway**. C'est une passerelle IPv6, et non un remplacement du NAT Gateway IPv4.

Exemple de route :

```text
Destination IPv6 : ::/0
Cible            : egress-only internet gateway
```

Il ne faut pas supposer qu'une route IPv6 se déduit d'une route IPv4. Les tables doivent être vérifiées séparément.

## 11.3. Différence entre NAT IPv4 et Egress-Only Internet Gateway IPv6

| Besoin | Mécanisme typique | Fonction |
|---|---|---|
| Sortie IPv4 privée vers Internet | NAT Gateway IPv4 | Traduction d'adresses IPv4 |
| Sortie IPv6 avec blocage des nouvelles connexions entrantes initiées depuis Internet | Egress-only Internet Gateway | Sortie IPv6 seulement, sans NAT IPv6 traditionnel |
| Charge IPv6-only qui doit contacter un service IPv4-only | DNS64/NAT64, selon le chemin | Synthèse d'adresse DNS et traduction IPv6 vers IPv4 |

Le NAT64 n'est pas nécessaire pour toutes les architectures IPv6-only. Il est utile lorsque les workloads IPv6-only doivent atteindre des destinations IPv4-only qui ne sont pas autrement accessibles en IPv6.

## 11.4. DNS64/NAT64

DNS64 peut synthétiser un enregistrement AAAA à partir d'un enregistrement IPv4 lorsque le nom ne possède pas d'adresse IPv6. Le trafic IPv6 vers cette adresse synthétisée peut être envoyé vers un NAT Gateway configuré pour le chemin NAT64 approprié.

```text
Instance IPv6-only
       |
       | demande DNS pour service IPv4-only
       v
Route 53 Resolver avec DNS64
       |
       | renvoie une adresse IPv6 synthétisée
       v
Table de routage IPv6-only
64:ff9b::/96 -> NAT Gateway
       |
       v
NAT64 -> destination IPv4-only
```

La configuration doit aussi comprendre les routes IPv4 pertinentes côté NAT Gateway et la route IPv6 vers le préfixe NAT64 documenté. Se référer à la documentation AWS actuelle avant de déployer ; ne pas créer ces routes uniquement sur la base du diagramme.

## 11.5. Checklist de sécurité IPv6

- Les SG ont-ils des règles IPv6 cohérentes avec les règles IPv4 ?
- Les NACL filtrent-ils correctement les deux familles ?
- Les routes `::/0` sont-elles dirigées vers la cible attendue ?
- Un chemin IPv6 ne contourne-t-il pas une inspection prévue seulement pour IPv4 ?
- Les règles DNS et les enregistrements AAAA sont-ils cohérents ?
- Les outils de sécurité et les journaux prennent-ils en charge IPv6 ?
- Les tests d'acceptation couvrent-ils IPv4 et IPv6 ?
- Les applications et les dépendances tierces acceptent-elles réellement IPv6 ?


# 12. Sécurité réseau multicouche, gouvernance multi-comptes et moindre privilège

## 12.1. Les couches de contrôle ne sont pas interchangeables

| Contrôle | Fonction principale | Ne remplace pas |
|---|---|---|
| Security Group | Filtrage stateful appliqué aux interfaces réseau des ressources concernées | Routage, IAM ou filtrage central de toutes les sorties |
| Network ACL | Filtrage stateless au niveau du sous-réseau | SG, route table ou contrôle d'identité |
| AWS Network Firewall | Inspection/filtrage réseau central ou local selon l'architecture | IAM, contrôle de l'application ou gouvernance des comptes |
| Route table | Détermine une cible de routage | Autorisation applicative |
| Endpoint policy | Restreint l'accès via certains endpoints selon le service | Bucket policy ou IAM |
| IAM | Contrôle d'accès aux actions et ressources AWS | Connectivité IP |
| AWS WAF | Filtrage de requêtes Web sur des ressources intégrées prises en charge | Pare-feu réseau généraliste |
| SCP / Control Tower / gouvernance d'organisation | Cadre de permissions et de gestion des comptes | Règles de flux applicatives |

La conception doit permettre de répondre à deux questions distinctes : « Le paquet peut-il atteindre la destination ? » et « L'identité a-t-elle le droit d'effectuer l'action sur le service ? ».

## 12.2. Security Groups : référence par groupe quand c'est possible

Lorsque la cible et le scénario le permettent, les règles de SG peuvent référencer un autre SG plutôt que d'inscrire une plage CIDR large.

Exemple conceptuel :

```text
SG-LOAD-BALANCER
  Entrant TCP/443 depuis les sources clientes approuvées

SG-APP
  Entrant TCP/8443 depuis SG-LOAD-BALANCER

SG-DATABASE
  Entrant TCP/5432 depuis SG-APP
```

Cette méthode exprime une relation fonctionnelle et évite de faire dépendre la règle uniquement des IP actuelles. Il faut vérifier les restrictions spécifiques des références SG, particulièrement avec le transit, les connexions hybrides et les communications inter-VPC : le fait que deux réseaux soient routés via TGW ne signifie pas que toutes les références de SG fonctionnent comme on l'imagine.

## 12.3. Egress : ne pas confondre « privé » et « sans sortie »

Une instance dans un sous-réseau privé peut disposer de chemins sortants via NAT Gateway, Transit Gateway, endpoints ou d'autres routes. « Privé » décrit surtout l'organisation et l'exposition de la ressource ; le chemin réel dépend des routes et des contrôles.

Une stratégie d'egress devrait décrire :

- Les destinations requises par les mises à jour et dépendances applicatives.
- Les services AWS à joindre via endpoints privés.
- Les destinations Internet explicitement autorisées.
- Les mécanismes de résolution DNS autorisés.
- La politique de journalisation et de conservation.
- Les contrôles qui empêchent un chemin de contournement.
- Le plan de changement pour ajouter une destination autorisée.

## 12.4. Gouvernance multi-comptes

Une séparation en comptes AWS distincts peut réduire les risques de modifications accidentelles et faciliter la facturation, l'audit et la délégation. Le réseau central peut être administré dans un compte dédié, tandis que les équipes de production et de développement possèdent leurs workloads dans d'autres comptes.

```text
AWS ORGANIZATION
|
+-- Compte Network
|   +-- TGW / Cloud WAN selon l'architecture
|   +-- VPC Inspection
|   +-- DNS shared
|   +-- Logs réseau centralisés
|
+-- Compte Security
|   +-- Agrégation des alertes et findings
|   +-- Outils de supervision selon les services retenus
|
+-- Compte Production
|   +-- VPC de production
|
+-- Compte NonProduction
    +-- VPC dev/test
```

Les comptes partagés doivent être gouvernés et leurs droits d'administration strictement limités. Une équipe applicative ne devrait pas pouvoir supprimer le firewall central ou changer les routes globales sans contrôle approuvé.

## 12.5. Autorisations IAM et rôles opérationnels

Définir des rôles distincts, par exemple :

- Lecteur réseau : description des routes et ressources, pas de modification.
- Opérateur réseau : changements limités à un périmètre précis.
- Responsable de la politique centrale : contrôle des TGW, firewall, DNS et routes globales.
- Auditeur : lecture des configurations et journaux.
- Pipeline IaC : rôle automatisé avec permissions au périmètre requis.

Éviter l'utilisation quotidienne de comptes root et de clés d'accès de longue durée. Protéger le pipeline qui modifie le réseau : un changement de route peut exposer un système ou interrompre des dizaines d'applications.

## 12.6. Audit des flux autorisés

Une règle réseau doit répondre à :

- Quel service en a besoin ?
- Qui en est propriétaire ?
- Quel est le protocole et le port ?
- Quelle source et quelle destination sont nécessaires ?
- Quel risque représente la règle ?
- Comment la tester ?
- Quand la réexaminer ou la supprimer ?

Une règle ouverte temporairement doit avoir une date d'expiration et un propriétaire. « Temporaire » sans expiration devient souvent permanent.

## 12.7. Network Access Analyzer et intention de sécurité

Network Access Analyzer permet d'identifier des chemins réseau conformes ou non conformes à des intentions spécifiées selon les capacités du service. Il complète Reachability Analyzer, qui analyse la connectivité entre une source et une destination.

Exemples d'objectifs d'analyse :

- Rechercher des chemins susceptibles de rendre un workload accessible depuis des réseaux non autorisés.
- Vérifier des conditions de séparation entre environnements.
- Détecter des chemins inattendus vers des ressources sensibles.
- Contrôler une architecture après un changement de route ou une nouvelle connexion.

Ne pas supposer qu'un outil d'analyse couvre toutes les dimensions du contrôle de sécurité. Il faut examiner sa portée et ses limitations actuelles, puis compléter par des tests applicatifs et une revue de politique.


# 13. Observabilité, diagnostic et validation des chemins

## 13.1. Pourquoi plusieurs outils sont nécessaires

Aucun outil isolé ne prouve à lui seul qu'une architecture fonctionne comme prévu. La visibilité doit combiner plusieurs sources.

| Outil ou journal | Réponse apportée | Limite à connaître |
|---|---|---|
| VPC Flow Logs | Enregistre des métadonnées de flux IP observés sur les ressources prises en charge | Ne capture pas tous les types de trafic ; ne fournit pas une capture complète du payload |
| Reachability Analyzer | Analyse statique d'un chemin réseau entre ressources prises en charge | Ne garantit pas que l'application répond ; ne constitue pas une capture live |
| Network Access Analyzer | Recherche des chemins selon des exigences de réseau et de sécurité | Doit être configuré avec des intentions pertinentes et relu selon sa portée |
| CloudTrail | Journalise les actions API de contrôle AWS | Ne remplace pas les logs de trafic applicatif |
| Logs Network Firewall | Aide à expliquer les décisions et événements d'inspection | Dépendent des règles, de la configuration et des champs journalisés |
| Métriques CloudWatch | Montre des volumes, erreurs ou événements de service disponibles | Une métrique ne dit pas toujours quelle règle ou quel paquet est en cause |
| Traffic Mirroring | Copie du trafic réseau sélectionné vers une cible d'analyse prise en charge | Coûts, limites de protocole, capacité et configuration à considérer |
| Logs DNS Resolver/DNS Firewall | Aide à comprendre la résolution et les blocages DNS | Ne remplace pas les logs applicatifs ni les tables de routage |

## 13.2. VPC Flow Logs : champs et interprétation

Un enregistrement de Flow Logs représente des métadonnées d'un flux IP sur une période d'agrégation. Les champs peuvent comprendre, selon le format choisi, source, destination, ports, protocole, action, état de journalisation, interfaces, adresses paquet, chemin de trafic et autres attributs.

Exemple schématique, non garanti comme format complet exact :

```text
version account-id interface-id srcaddr dstaddr srcport dstport protocol
packets bytes start end action log-status
```

- `ACCEPT` indique que le trafic a été autorisé par les contrôles de sécurité capturés dans le contexte du log.
- `REJECT` indique que le trafic a été rejeté par un contrôle de sécurité capturé.
- `NODATA` ou d'autres valeurs de statut peuvent signaler l'absence de données selon les conditions décrites par AWS.

Les noms de champs et comportements exacts dépendent de la version et du format du log configuré. Choisir explicitement un format personnalisé si des champs supplémentaires sont nécessaires.

### Limites critiques

Flow Logs ne capture pas tous les types de trafic. La documentation AWS signale notamment des exclusions telles que certains flux DNS vers le serveur DNS Amazon, le trafic DHCP, le trafic vers les adresses de métadonnées d'instance, ARP et d'autres catégories définies par le service. Certains records peuvent également manquer lors d'une période d'agrégation.

Conséquence pratique : **l'absence d'un record Flow Logs n'est pas une preuve absolue qu'aucun paquet n'a existé**. Comprendre la couverture de l'outil avant d'en tirer une conclusion.

## 13.3. Reachability Analyzer

Reachability Analyzer analyse la connectivité virtuelle entre une source et une destination prises en charge, en examinant les composants réseau pertinents. Il peut fournir des détails de chemin ou identifier le composant bloquant lorsqu'il y a une configuration incompatible.

Utilisations typiques :

- Tester qu'une instance peut atteindre une destination prévue.
- Vérifier l'effet de modifications de SG, NACL ou routes.
- Déterminer si une configuration correspond à l'intention attendue.
- Automatiser des contrôles dans un processus de changement lorsque le cas est pris en charge.

Ne pas le confondre avec un test `curl` depuis une instance. L'analyse porte sur la configuration réseau supportée et n'affirme pas que le processus applicatif écoute ou répond correctement.

## 13.4. Démonstration : flux rejeté par un Security Group

Scénario : une instance cliente doit atteindre `10.30.10.25:5432`, mais la base ne répond pas.

Méthode :

1. Résoudre le nom pour connaître la véritable IP cible.
2. Examiner les routes VPC et TGW des deux côtés.
3. Vérifier qu'un test Reachability Analyzer est possible entre les ressources choisies.
4. Examiner les SG de la ressource base et la source réelle du flux.
5. Examiner les NACL dans les deux sens si elles sont personnalisées.
6. Chercher le flux dans les Flow Logs des interfaces source et destination.
7. Vérifier le listener base de données et les logs applicatifs.

Il faut éviter d'ajouter immédiatement une règle `0.0.0.0/0` vers TCP/5432. Le changement doit autoriser uniquement la source réelle et requise.

## 13.5. Exemple de requête Athena sur les logs stockés dans S3

Le SQL doit correspondre au schéma déclaré pour la table Athena. L'exemple ci-dessous n'est pas directement exécutable sans créer une table avec les champs correspondants.

```sql
SELECT
  srcaddr,
  dstaddr,
  dstport,
  protocol,
  action,
  COUNT(*) AS records
FROM vpc_flow_logs
WHERE action = 'REJECT'
  AND dstport IN (443, 5432, 8443)
GROUP BY srcaddr, dstaddr, dstport, protocol, action
ORDER BY records DESC;
```

Cette requête permet de regrouper des rejets vers quelques ports. Elle ne prouve pas, à elle seule, quel contrôle a rejeté un flux ni si tous les records existent. Croiser les résultats avec les logs et la configuration des composants.

## 13.6. Journaux et rétention

Définir des exigences de rétention en fonction du contexte réglementaire, de l'analyse d'incident, des coûts et du besoin métier.

- Séparer les logs de diagnostic courts termes et les archives de sécurité longue durée si nécessaire.
- Limiter l'accès aux journaux réseau.
- Centraliser l'horodatage et la région/compte d'origine.
- Prévoir des tableaux de bord pour les anomalies de trafic, les routes et les tunnels.
- Déclencher des alertes sur les changements critiques, pas uniquement sur les erreurs visibles par l'application.
- Vérifier que les logs sont effectivement livrés et non seulement que la ressource de journalisation a été créée.


# 14. Automatisation, Infrastructure as Code et validation continue

## 14.1. Pourquoi le réseau doit être reproductible

Une table de routage ou une règle de firewall peut avoir un effet sur plusieurs applications. Les modifications manuelles sont parfois nécessaires lors d'un incident, mais doivent être enregistrées puis rapprochées du code déclaratif.

L'Infrastructure as Code (IaC) permet de décrire les ressources, de revoir les changements, de produire des déploiements reproductibles et de limiter les différences entre environnements.

Les options comprennent notamment AWS CloudFormation, AWS CDK et Terraform. Le choix dépend des standards de l'équipe, de l'écosystème, de la gouvernance et du niveau d'abstraction souhaité.

## 14.2. Pipeline réseau recommandé

```text
Modification IaC
      |
      v
Formatage + lint + validation syntaxique
      |
      v
Tests de politique CIDR et de cohérence
      |
      v
Plan/diff relu par une personne habilitée
      |
      v
Déploiement dans un environnement de test
      |
      v
Tests positifs et négatifs de connectivité
      |
      v
Analyse de chemins / revue de sécurité
      |
      v
Approbation de production
      |
      v
Déploiement progressif + surveillance
      |
      +--> échec : arrêt / rollback documenté
```

## 14.3. Tests automatiques à prévoir

Tests statiques possibles :

- Aucun CIDR de VPC ne chevauche les allocations incompatibles connues.
- Aucun sous-réseau ne sort du CIDR du VPC.
- Les rôles et tags obligatoires sont présents.
- Les SG n'incluent pas de ports administratifs ouverts à Internet sans exception approuvée.
- Les tables de routage des environnements sensibles n'ont pas de chemins par défaut inattendus.
- Les attachements TGW sont associés à la table correcte.
- Les propagations sont limitées aux domaines prévus.
- Les règles de firewall n'acceptent pas d'accès excessif.
- Les endpoints utilisent les politiques et paramètres DNS requis.

Tests dynamiques possibles :

- Une connexion autorisée atteint sa destination.
- Une connexion interdite échoue.
- La résolution DNS renvoie l'adresse prévue depuis le VPC source.
- La route de secours devient active lors d'un scénario de panne contrôlé.
- Les événements de supervision apparaissent dans la destination attendue.

## 14.4. Exemple de vérification AWS CLI avant un changement

Les commandes sont des exemples de lecture. Remplacer les identifiants d'exemple, le profil et la région.

```bash
# Contexte AWS courant
aws sts get-caller-identity
aws configure get region

# Examiner les VPC et leurs plages
aws ec2 describe-vpcs \
  --query 'Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,State:State}'

# Examiner les tables de routage
aws ec2 describe-route-tables \
  --filters Name=vpc-id,Values=vpc-EXAMPLE

# Examiner les associations de sous-réseaux et leurs routes
aws ec2 describe-subnets \
  --filters Name=vpc-id,Values=vpc-EXAMPLE

# Examiner les règles de SG d'un périmètre ciblé
aws ec2 describe-security-groups \
  --filters Name=vpc-id,Values=vpc-EXAMPLE
```

La sortie doit être analysée par le script ou l'opérateur. Une commande `describe` n'effectue pas une évaluation complète de la sécurité ; elle fournit des données nécessaires à cette évaluation.

## 14.5. Contrôle de dérive

La configuration réelle peut diverger du code par une intervention manuelle, une migration partielle ou une automatisation externe.

Procédure :

1. Comparer l'état déployé à l'état déclaratif.
2. Identifier quelles ressources ont divergé et depuis quand.
3. Déterminer si le changement manuel était une réponse à incident ou une modification non approuvée.
4. Décider si l'état réel ou le code représente l'intention autorisée.
5. Réconcilier le code et l'infrastructure avec une procédure relue.
6. Vérifier les flux positifs et négatifs après correction.

Ne pas exécuter automatiquement un « apply » correctif sans examiner si la dérive contient un changement critique lié à une restauration ou à un incident.

## 14.6. Déployer sans coupure évitable

Pour des modifications de routage, d'inspection ou de DNS :

- Lire les dépendances et les flux affectés.
- Préparer une sauvegarde logique ou une version connue du code.
- Prévoir une fenêtre de changement si le risque l'exige.
- Déployer d'abord dans un périmètre de test.
- Mesurer les routes actives et les sessions de connectivité.
- Surveiller les logs et métriques après le changement.
- Garder une procédure de rollback validée.
- Documenter le résultat, même si le changement est annulé.


# 15. Disponibilité, performances, MTU, coûts et capacité opérationnelle

## 15.1. La haute disponibilité se conçoit à chaque couche

Une architecture réseau peut être redondante au niveau d'un service mais fragile au niveau de ses routes ou de ses dépendances.

Exemples de fausse résilience :

- Deux instances dans deux AZ, mais un seul mécanisme d'accès qui n'est pas résilient.
- Deux tunnels VPN disponibles, mais les routes de retour ne convergent pas.
- Plusieurs AZ applicatives, mais un NAT Gateway unique dans une AZ, sans stratégie documentée pour l'autre AZ.
- Plusieurs attachements, mais tous associés à la même table TGW mal configurée.
- Un pare-feu en plusieurs AZ, mais une route de retour contournant l'inspection.
- Une connectivité primaire et une connectivité de secours, mais une annonce BGP trop spécifique qui empêche la bascule attendue.

La résilience doit être vérifiée pour chaque dépendance : compute, réseau, routage, DNS, sécurité, observabilité et processus humain.

## 15.2. NAT Gateway et disponibilité par AZ

Une NAT Gateway est créée dans un sous-réseau associé à une zone de disponibilité. Pour réduire le risque qu'une panne de zone ou d'un chemin inter-AZ affecte tous les workloads, une architecture de production peut déployer un NAT Gateway par AZ et diriger le trafic de chaque sous-réseau applicatif vers le NAT local à cette AZ.

```text
AZ A                                  AZ B
+----------------------+              +----------------------+
| Subnet APP A         |              | Subnet APP B         |
| route -> NAT A       |              | route -> NAT B       |
+----------+-----------+              +----------+-----------+
           |                                     |
           v                                     v
       [ NAT A ]                             [ NAT B ]
           |                                     |
           +----------------+--------------------+
                            |
                      Internet Gateway
                            |
                         INTERNET
```

Cette architecture peut améliorer l'isolation par AZ et éviter certains coûts de transfert inter-AZ, mais augmente le coût fixe lié au nombre de NAT Gateway. La décision doit comparer le coût, les objectifs de résilience et le volume de trafic.

Ne pas supposer que la présence de NAT Gateway rend automatiquement le sous-réseau accessible depuis Internet : une NAT Gateway sert typiquement au trafic initié de l'intérieur, et les ressources privées ne deviennent pas directement des destinations entrantes publiques du seul fait de cette route.

## 15.3. Mesurer avant d'optimiser

Les performances perçues dépendent de plusieurs variables :

- Distance géographique et nombre de sauts logiques.
- Débit et limitations des ressources impliquées.
- Latence d'inspection ou de proxy.
- Charge et nombre de connexions concurrentes.
- MTU et fragmentation.
- Résolution DNS et caches.
- Établissement de sessions TLS et timeouts applicatifs.
- Transfert inter-AZ, inter-région ou vers Internet.
- Quotas du service et capacité du chemin complet.

Il faut distinguer latence, débit, perte de paquets et taux d'échec de connexion. Des tests doivent être reproductibles et corrélés avec les métriques du service.

## 15.4. Budget et coûts : les postes à examiner

Le modèle de coût dépend des services et des régions, mais les catégories suivantes doivent figurer dans une estimation :

- Heures et traitement des NAT Gateways.
- Données traitées par les NAT, endpoints et pare-feu lorsque le service les facture ainsi.
- Nombre et type d'attachements Transit Gateway.
- Données traitées et transfert via TGW.
- Cross-AZ et transferts inter-région.
- Endpoint interface PrivateLink et données transférées.
- Route 53 Resolver endpoints et volume de requêtes.
- VPC Flow Logs, livraison, stockage, requêtes Athena et rétention.
- AWS Network Firewall et stockage/ingestion des logs associés.
- Direct Connect, opérateur et frais de transfert selon le modèle.
- VPN, services de supervision, Traffic Mirroring et outils d'analyse selon l'utilisation.

Ne pas utiliser une estimation figée : consulter les tarifs actuels et simuler plusieurs scénarios de trafic. Le coût d'une architecture de faible trafic peut être dominé par les coûts fixes, alors qu'un réseau intensif peut être dominé par le volume de données et les transferts.

## 15.5. Quotas et capacité

Un architecte doit vérifier les quotas qui s'appliquent aux ressources et à l'architecture choisies, notamment les CIDR, sous-réseaux, route tables, règles, attachements, routes et endpoints. Les valeurs par défaut peuvent varier, être modifiables ou dépendre du service et de la région.

Avant le déploiement :

1. Recenser les quotas nécessaires dans les régions cibles.
2. Vérifier les valeurs actuelles dans la documentation et Service Quotas.
3. Demander une augmentation à l'avance lorsque c'est nécessaire.
4. Ajouter une marge pour les migrations, blue/green et tests de reprise.
5. Surveiller l'utilisation avant qu'elle atteigne la limite.

## 15.6. Test de résilience contrôlé

Un test de bascule doit définir à l'avance :

- L'hypothèse testée.
- Les ressources touchées.
- Le périmètre d'impact autorisé.
- La méthode de déclenchement de panne.
- Les métriques et logs observés.
- Les critères de succès/échec.
- La personne qui peut interrompre le test.
- Le mécanisme de restauration.

Ne pas provoquer une panne de service partagé dans un environnement de production sans autorisation, coordination, plan de repli et évaluation des risques.


# 16. Procédures de dépannage expert par symptôme

## 16.1. Méthode générale : observer, formuler, tester, isoler

```text
SYMPTÔME
   |
   v
DÉFINIR LE PÉRIMÈTRE
Source réelle ? Destination réelle ? Port ? Heure ? Un seul AZ ou plusieurs ?
   |
   v
FORMULER UNE HYPOTHÈSE TESTABLE
DNS, route VPC, route TGW, SG, NACL, firewall, MTU, application ?
   |
   v
COLLECTER UNE PREUVE
Tables, Reachability Analyzer, Flow Logs, logs firewall, test TCP, métriques
   |
   v
MODIFIER UNE SEULE VARIABLE À LA FOIS
   |
   v
RETTESTER LE FLUX POSITIF ET LES FLUX NÉGATIFS
   |
   v
DOCUMENTATION + PRÉVENTION DE LA RÉCIDIVE
```

## 16.2. Symptôme A : un VPC ne joint pas un autre VPC via TGW

Contrôles ordonnés :

1. Vérifier les CIDR des deux VPC et rechercher un chevauchement.
2. Vérifier que les deux attachments sont disponibles et attachés au TGW attendu.
3. Vérifier la table VPC source : route vers le CIDR distant avec cible TGW.
4. Vérifier l'association de l'attachment source à la table TGW voulue.
5. Vérifier dans cette table la route vers le CIDR destination et sa cible.
6. Vérifier l'association/propagation côté destination si l'architecture en dépend.
7. Vérifier la route de retour côté destination et dans la table TGW de retour.
8. Vérifier SG/NACL et firewall éventuel.
9. Vérifier que le service écoute et que la bonne IP est utilisée.
10. Capturer les éléments avant et après la correction.

## 16.3. Symptôme B : VPC A accède à VPC B, mais B ne peut pas accéder à A

Il faut déterminer si le besoin est une connexion initiée par B ou si l'on observe uniquement l'absence de réponse à une session initiée par A.

Ces cas sont différents :

- Les SG sont stateful et autorisent généralement les retours d'une session permise, mais n'autorisent pas automatiquement de nouvelles connexions initiées dans le sens inverse.
- Les routes peuvent être asymétriques ou absentes dans une direction.
- Les NACL sont stateless et doivent permettre les ports éphémères et les retours nécessaires selon le flux.
- Un pare-feu central stateful peut rejeter les flux s'il ne voit qu'un côté.
- Une politique TGW peut autoriser une table à voir B sans offrir un chemin de retour approprié.

Écrire le sens de l'initiation dans la matrice de flux et tester séparément `A -> B` et `B -> A`.

## 16.4. Symptôme C : l'accès Internet sortant échoue

```text
1. L'IP cible est-elle correcte ?
2. Le DNS fonctionne-t-il depuis ce subnet ?
3. La table du subnet contient-elle la route attendue ?
4. La cible IGW, NAT, TGW ou firewall est-elle disponible ?
5. Si NAT : est-il public, placé dans le bon subnet et associé au bon chemin IGW ?
6. Les SG/NACL autorisent-ils le flux et les retours ?
7. L'egress central accepte-t-il la destination ?
8. Le retour suit-il le même chemin stateful lorsque cela est requis ?
9. La destination Internet répond-elle et le protocole est-il correct ?
10. Les limites de service, DNS ou MTU expliquent-elles l'échec ?
```

## 16.5. Symptôme D : le tunnel VPN est UP mais le LAN reste inaccessible

Un tunnel UP valide une partie du chemin IPsec, pas l'ensemble du routage.

- Examiner les préfixes BGP reçus et envoyés, ou les routes statiques.
- Vérifier les routes de la table TGW appropriée.
- Vérifier les routes dans les sous-réseaux VPC et la connectivité retour.
- Vérifier les réseaux annoncés côté routeur client.
- Contrôler les ACL et les Security Groups.
- Tester une IP avant le DNS, puis comparer la résolution.
- Vérifier que le trafic ne passe pas par une appliance qui n'accepte pas le flux.
- Tester MTU/MSS si les gros transferts échouent.

## 16.6. Symptôme E : résolution DNS erronée entre AWS et on-premises

- Tester la résolution depuis chaque côté avec le même FQDN.
- Contrôler la zone privée et ses associations VPC.
- Vérifier les règles de forwarding et leurs associations.
- Vérifier l'accessibilité des endpoints Resolver via UDP/TCP 53.
- Ne pas substituer un appel direct au VPC+2 à une architecture Resolver hybride prise en charge.
- Vérifier les caches locaux et TTL.
- Identifier les zones qui se chevauchent et les règles les plus spécifiques.
- Contrôler les logs DNS Firewall si le filtrage est actif.

## 16.7. Symptôme F : seul IPv6 échoue

- Vérifier l'attribution du CIDR IPv6 au VPC et au sous-réseau.
- Vérifier l'adresse IPv6 effective de l'instance.
- Inspecter les routes IPv6 de la table.
- Vérifier les règles SG/NACL IPv6 séparément.
- Contrôler l'enregistrement AAAA, le chemin de sortie et l'inspection.
- Déterminer si la destination est réellement accessible en IPv6.
- En cas de destination IPv4-only, vérifier si DNS64/NAT64 est conçu pour ce besoin.

## 16.8. Symptôme G : seuls les gros paquets ou transferts échouent

- Confirmer si les petits échanges passent.
- Tester progressivement la taille de la charge utile.
- Examiner l'encapsulation VPN, transit, inspection et MTU du chemin.
- Vérifier la découverte MTU et les messages ICMP nécessaires.
- Vérifier les paramètres MSS éventuellement ajustés.
- Vérifier que les firewalls n'éliminent pas des messages de contrôle essentiels.
- Ne pas masquer le problème en abaissant arbitrairement le MTU partout sans mesurer.

## 16.9. Symptôme H : l'endpoint privé AWS ne fonctionne pas

- Vérifier que le type d'endpoint correspond au service utilisé.
- Vérifier le DNS privé, les enregistrements et l'adresse qui est résolue.
- Pour un interface endpoint, contrôler le SG de ses ENI.
- Vérifier la route table pour un gateway endpoint.
- Examiner les endpoint policies, les permissions IAM et la policy de ressource.
- Confirmer la région et le nom de service.
- Vérifier que le trafic ne contourne pas le chemin prévu par le DNS ou un proxy.

## 16.10. Exemple de fiche d'incident réseau

```text
ID INCIDENT : NET-YYYY-NNNN
Date/heure UTC ou fuseau documenté :
Application / propriétaire :
Source (IP, subnet, VPC, compte) :
Destination (nom, IP, port) :
Première observation :
Étendue de l'impact :
Dernier changement connu :
Hypothèse initiale :
Preuves collectées :
Premier composant bloquant :
Correction appliquée :
Test positif après correction :
Test négatif de sécurité :
Rollback réalisé ?
Cause racine :
Mesure préventive :
Lien vers changement et journaux :
```

Cette fiche aide à éviter les changements « à l'aveugle » et permet de transformer un incident en amélioration durable.


# 17. Atelier guidé A — concevoir un hub réseau de production

## 17.1. Objectif

Créer un plan d'architecture pour relier PROD-APP, PROD-DATA, DEV et le réseau local via un Transit Gateway tout en conservant une segmentation contrôlée.

## 17.2. Besoin fonctionnel

- PROD-APP peut joindre PROD-DATA uniquement sur TCP/5432.
- DEV peut accéder à un service d'artefacts partagé mais pas à PROD-DATA.
- Le réseau on-premises `172.20.0.0/16` peut joindre un service de production publié et des services partagés approuvés.
- Les sorties Internet des workloads privés doivent emprunter un chemin central contrôlé.

## 17.3. Topologie cible

```text
                         ON-PREMISES
                         172.20.0.0/16
                               |
                           VPN / DX
                               |
                               v
+-------------+       +------------------+       +-------------+
| VPC-PROD-APP|------>|                  |<------| VPC-DEV     |
| 10.20/16    |       | TRANSIT GATEWAY  |       | 10.40/16    |
+------+------+       |                  |       +-------------+
       |               +--------+---------+
       |                        |
       v                        v
+-------------+       +------------------+
| VPC-PROD-DATA|      | VPC-INSPECTION   |
| 10.30/16    |       | 10.60/16         |
+-------------+       +------------------+
```

Le dessin montre la logique. Il ne montre pas toutes les tables, et ne garantit pas que chaque paire est connectée. Les associations et routes seront déterminées dans l'atelier.

## 17.4. Étapes de conception

### Étape 1 — valider l'adressage

Confirmer les CIDR sans chevauchement avec les VPC connus et les réseaux du LAN. Enregistrer les allocations dans IPAM ou le référentiel de l'organisation.

### Étape 2 — définir les domaines de routage

Créer des tables TGW différentes pour les segments lorsque la politique de sécurité exige des vues de routes distinctes, par exemple `RT-PROD`, `RT-NONPROD`, `RT-ONPREM` et `RT-INSPECTION`.

Ne pas propager tous les préfixes dans toutes les tables. Décider explicitement qui peut atteindre qui.

### Étape 3 — ajouter les routes des VPC

Dans chaque subnet concerné, configurer les routes vers TGW pour les CIDR distants nécessaires. Ne pas ajouter une route par défaut vers TGW tant que le chemin central d'egress et les restrictions ne sont pas prêts.

### Étape 4 — configurer les tables TGW

Pour chaque attachement :

- Vérifier la table associée.
- Vérifier les routes statiques et propagées.
- Vérifier les routes de retour.
- Vérifier les routes de l'inspection si l'inspection centrale est requise.

### Étape 5 — mettre en place les contrôles de sécurité

Appliquer des règles SG limitées aux ports et sources nécessaires. Ajouter des règles réseau centralisées quand elles sont requises par la politique. Éviter d'ouvrir tout un CIDR de production uniquement pour simplifier le test.

### Étape 6 — produire les preuves

- Tester `PROD-APP -> PROD-DATA:5432`.
- Tester un port interdit entre ces mêmes environnements.
- Tester `DEV -> PROD-DATA` et vérifier l'échec.
- Tester l'accès DEV au service partagé.
- Tester les sorties d'egress autorisées et non autorisées.
- Contrôler les logs attendus.

## 17.5. Résultat attendu

Un dossier court contenant le schéma, les CIDR, les associations/propagations TGW, la matrice de flux, les tests positifs/négatifs et le plan de rollback.


# 18. Atelier guidé B — inspection centralisée sans rupture de flux

## 18.1. Objectif

Comprendre comment le routage aller/retour, les tables VPC et TGW, ainsi que l'appliance mode, influencent un chemin traversant un firewall stateful.

## 18.2. Scénario de départ

```text
VPC-APP  ---> TGW ---> VPC-INSPECTION ---> sortie contrôlée
                \
                 \
                  ---> VPC-DATA (chemin direct accidentel)
```

Une route mal définie dans la table TGW pourrait permettre un chemin direct vers VPC-DATA qui contourne le contrôle attendu. Une autre erreur pourrait acheminer l'aller via le firewall mais le retour directement vers l'application.

## 18.3. Questions avant toute modification

1. Quelle est l'association de la table TGW pour l'attachment de VPC-APP ?
2. La destination est-elle dirigée vers VPC-INSPECTION ou vers le VPC cible ?
3. Quelles routes existent dans la table du VPC-INSPECTION ?
4. Le firewall dispose-t-il d'un chemin de sortie et d'un chemin retour ?
5. L'appliance mode est-il requis et activé sur l'attachement concerné ?
6. Existe-t-il une route plus spécifique qui contourne l'inspection ?
7. Les logs montrent-ils un rejet, une acceptation ou aucune donnée ?

## 18.4. Déroulement

1. Documenter le flux de test, par exemple APP vers un serveur web de test.
2. Vérifier les routes source, TGW, inspection et destination.
3. Vérifier les chemins retour.
4. Vérifier les règles du firewall et la journalisation.
5. Tester le chemin autorisé.
6. Tester un domaine/port interdit selon une règle de laboratoire.
7. Examiner si un chemin direct contourne le firewall.
8. Modifier une seule association ou route à la fois, avec validation préalable.
9. Relancer les tests et capturer les résultats.

## 18.5. Critères de réussite

- Le flux prévu traverse le contrôle central.
- Les flux interdits n'ont pas de chemin alternatif.
- Les sessions stateful fonctionnent dans les deux sens.
- Les journaux du firewall et du VPC suffisent à expliquer les décisions.
- Le plan de secours et les impacts d'une panne sont documentés.


# 19. Atelier guidé C — connecter un réseau on-premises de façon résiliente

## 19.1. Objectif

Concevoir une liaison principale Direct Connect et une liaison VPN de secours, en gardant à l'esprit qu'une haute disponibilité dépend de la configuration de bout en bout.

## 19.2. Schéma

```text
                         AWS
                    +------------+
                    | Transit GW |
                    +-----+------+
                          |
              +-----------+-----------+
              |                       |
        Direct Connect              Site-to-Site VPN
          principal                   secours
              |                       |
              +-----------+-----------+
                          |
                    Routeur LAN
                          |
                    172.20.0.0/16
```

## 19.3. Préparation

- Vérifier les allocations CIDR et le périmètre de routes annoncé.
- Définir les ASNs et la politique BGP selon les besoins et contraintes du service.
- Définir les préfixes autorisés en entrée et en sortie.
- Examiner les limites et quotas actuels.
- Planifier une fenêtre de test de bascule.
- Déterminer la mesure de succès : convergence de route, maintien de connectivité, durée acceptable et alerte.

## 19.4. Test planifié

1. Capturer l'état normal : BGP, routes actives, latence, taux d'erreur.
2. Confirmer la route effective vers chaque réseau critique.
3. Simuler une perte de connectivité dans un cadre autorisé.
4. Observer les changements de session et de route.
5. Tester l'accès à une IP et à un service applicatif réels.
6. Vérifier le retour à l'état normal.
7. Contrôler si les sessions existantes sont rétablies ou interrompues selon les attentes.
8. Documenter les temps réels et toute route inattendue.

## 19.5. Critères de réussite

- Le trafic utilise le chemin attendu en régime normal.
- Le chemin de secours devient utilisable après perte du principal.
- Aucune route trop large n'est annoncée involontairement.
- Les applications critiques sont testées, pas seulement les tunnels.
- Les équipes peuvent détecter et interpréter la bascule.


# 20. Atelier guidé D — accès privé aux services AWS et DNS hybride

## 20.1. Objectif

Concevoir un accès privé à un service AWS et résoudre les noms internes du réseau local depuis une application privée.

## 20.2. Schéma cible

```text
                       VPC APP
                  +----------------+
                  | Instance privée|
                  +--------+-------+
                           |
             +-------------+--------------+
             |                            |
             v                            v
       Endpoint AWS              Route 53 Resolver
       (service ciblé)            outbound endpoint
                                          |
                                          v
                               VPN / Direct Connect
                                          |
                                          v
                                  DNS on-premises
```

## 20.3. Étapes

1. Identifier si le service AWS prend en charge un gateway endpoint ou un interface endpoint dans le scénario prévu.
2. Vérifier les contraintes de région, de DNS et d'adressage.
3. Configurer les routes ou ENI et les groupes de sécurité selon le type d'endpoint.
4. Définir l'endpoint policy et les politiques IAM nécessaires.
5. Créer une règle Resolver pour le domaine hérité et l'associer aux VPC consommateurs concernés.
6. Vérifier le chemin vers les adresses du DNS on-premises.
7. Tester la résolution du nom et le trafic applicatif.
8. Vérifier la journalisation et la méthode de diagnostic.

## 20.4. Critères de réussite

- L'application joint le service AWS sans utiliser inutilement la sortie Internet attendue pour ce service.
- L'accès ne dépasse pas les permissions prévues.
- Les noms hérités se résolvent par le Resolver attendu.
- Le changement ne crée pas de dépendance DNS non documentée.


# 21. Exercices de consolidation avec corrections

## Exercice 1 — Préfixe le plus spécifique

Une table TGW contient les routes suivantes :

| Destination | Cible |
|---|---|
| `10.0.0.0/8` | Attachment A |
| `10.30.0.0/16` | Attachment B |
| `10.30.4.0/22` | Attachment C |
| `0.0.0.0/0` | Attachment D |

Quelle cible est sélectionnée pour `10.30.5.10` ? Et pour `10.30.8.10` ?

### Correction

- `10.30.5.10` appartient à `10.30.4.0/22` et aux préfixes moins spécifiques. La route `/22` est la plus spécifique, donc Attachment C si la route est active et applicable.
- `10.30.8.10` appartient à `10.30.0.0/16`, mais pas à `10.30.4.0/22`. La route `/16` mène à Attachment B.

Il faut toujours vérifier que la cible et la route sont valides dans le contexte réel. Le simple tableau ne décrit pas les politiques de sécurité.

## Exercice 2 — VPC Peering ou Transit Gateway ?

Une organisation a 24 VPC dans trois régions, un réseau on-premises, une inspection centrale et des domaines prod/nonprod. Les équipes demandent un nouveau VPC chaque mois.

### Correction

Une topologie uniquement basée sur le VPC Peering risque de devenir complexe : le peering n'est pas transitif et les relations doivent être administrées individuellement. Un modèle Transit Gateway par région, avec une architecture inter-région ou Cloud WAN selon le besoin global, doit être évalué. Les tables doivent être segmentées afin de ne pas donner automatiquement à chaque VPC une route vers tous les autres.

La recommandation finale doit être confirmée par une étude de routes, de disponibilité régionale, de quotas, de coûts et de responsabilités d'exploitation.

## Exercice 3 — Un tunnel VPN est UP, mais aucun trafic ne passe

Citer au moins six causes possibles sans supposer que le tunnel est défectueux.

### Correction

Causes possibles : préfixe absent ou filtré dans BGP ; route manquante dans la table TGW ; VPC sans route retour ; association TGW incorrecte ; CIDR qui se chevauche ; SG ou NACL trop restrictive ; pare-feu on-premises bloquant le flux ; table de routage du routeur client incorrecte ; DNS incorrect ; MTU/MSS inadapté pour les gros flux ; destination qui n'écoute pas sur le port testé.

## Exercice 4 — Détecter une inspection contournée

Une route TGW contient :

```text
10.30.0.0/16 -> attachment VPC-DATA
0.0.0.0/0    -> attachment VPC-INSPECTION
```

La politique impose l'inspection de tous les flux entre VPC applicatifs et VPC de données. Que se passe-t-il pour une destination `10.30.12.7` ?

### Correction

Le `/16` de destination est plus spécifique que la route par défaut. Le trafic est donc envoyé directement vers VPC-DATA, si la route est active et valide, et contourne la route par défaut vers l'inspection. La correction possible consiste à retirer la route directe ou à la remplacer par une architecture explicitement inspectée, selon le modèle de tables TGW choisi. Il faut aussi vérifier les chemins alternatifs et le retour.

## Exercice 5 — endpoint S3 et permissions

Une instance privée résout le nom S3 vers le chemin attendu et atteint l'endpoint, mais reçoit `AccessDenied`.

### Correction

Le problème n'est plus nécessairement un problème de routage. Examiner le rôle IAM, la bucket policy, l'endpoint policy, les conditions de chiffrement, l'ARN de bucket/objet, le compte, la région et l'action précise. Un chemin réseau fonctionnel n'accorde pas une autorisation de service.

## Exercice 6 — Pourquoi l'absence de Flow Logs n'est pas une preuve absolue ?

### Correction

Flow Logs ne capture pas tous les types de trafic et peut omettre certains records selon les contraintes du service et l'intervalle d'agrégation. Il faut connaître les exclusions, vérifier l'activation et la livraison des logs, puis croiser avec d'autres observations : Reachability Analyzer, logs firewall, métriques, capture prise en charge ou test applicatif.

## Exercice 7 — IPv6 seulement

Une instance IPv6-only peut résoudre un nom vers une adresse IPv4 et ne peut pas se connecter. Quelle piste examiner ?

### Correction

Une ressource IPv6-only ne peut pas utiliser directement une destination IPv4-only en envoyant un paquet IPv6 ordinaire vers l'adresse A. Vérifier si DNS64/NAT64 est un besoin adapté et si le sous-réseau, les routes, le NAT Gateway et le résolveur sont configurés selon la documentation. Vérifier aussi si le service possède en réalité un endpoint IPv6 accessible.

## Exercice 8 — Bascule DX/VPN

Quelle est la différence entre observer un tunnel VPN UP et démontrer que le VPN peut reprendre le trafic après une panne Direct Connect ?

### Correction

Un tunnel UP montre un état du tunnel. Il ne prouve pas que le routage de secours est accepté, que les bons préfixes sont annoncés, que les routes de retour existent, que les priorités sont correctes ou que l'application récupère. Il faut effectuer une bascule planifiée, capturer les routes avant/après, tester la vraie application, mesurer la durée et valider le retour au chemin principal.

## Exercice 9 — Choix de service

Une équipe doit exposer seulement une API à des consommateurs de plusieurs VPC dont les CIDR se chevauchent. Quelle solution faut-il étudier en premier ?

### Correction

AWS PrivateLink est un candidat naturel si le type de service et le scénario sont pris en charge. Il publie un service sans exiger un routage IP général entre les VPC. Il faut concevoir l'endpoint service, le contrôle des consommateurs, le DNS, la disponibilité et les politiques d'accès.

## Exercice 10 — Vrai ou faux

1. Une route vers TGW garantit que la destination est accessible.
2. Une route de retour est toujours facultative si le SG autorise le flux.
3. Deux routes avec des préfixes différents sont résolues sans examiner la longueur du préfixe.
4. Un firewall stateful peut échouer si le trafic retour contourne le firewall.
5. Une route `0.0.0.0/0 -> TGW` crée automatiquement un accès Internet.
6. Les règles IPv4 prouvent que le chemin IPv6 est sécurisé.

### Correction

1. Faux. Il faut aussi des routes TGW/VPC, les cibles, les contrôles de sécurité et une destination en écoute.
2. Faux. Le retour doit avoir un chemin de routage valide ; les états de sécurité ne créent pas de route.
3. Faux. La longueur du préfixe et les règles de priorité sont essentielles.
4. Vrai. L'état de session peut ne pas être cohérent si le chemin est asymétrique.
5. Faux. Le TGW doit avoir les routes suivantes et le chemin vers une sortie viable, avec les contrôles et éventuelle traduction nécessaires.
6. Faux. Il faut auditer les routes et règles IPv6 séparément.


# 22. Challenge final autonome — plateforme multi-comptes et connectivité hybride

## 22.1. Règle du challenge

Ce challenge est la dernière partie du cours. Il utilise les connaissances des chapitres précédents. L'objectif est de concevoir une architecture sûre, d'identifier les erreurs de configuration et d'expliquer comment les prouver.

**Le scénario, les tâches, les critères, le barème et la correction sont tous inclus ici.** Il n'est pas nécessaire de créer ou de télécharger un autre document.

## 22.2. Contexte d'entreprise

Orion exploite une plateforme dans AWS. La plateforme comprend :

- Un VPC applicatif de production.
- Un VPC de données de production.
- Un VPC de développement.
- Un VPC central d'inspection et de sortie réseau.
- Un réseau on-premises connecté à AWS.
- Un service d'artefacts accessible depuis DEV.
- Un service DNS interne historique.

L'organisation utilise Transit Gateway dans une région AWS. Direct Connect est le chemin hybride préféré ; Site-to-Site VPN est prévu comme secours. L'architecture doit pouvoir être étendue à d'autres comptes et à d'autres régions.

## 22.3. CIDR du scénario

| Réseau | CIDR | Attachement/usage |
|---|---|---|
| VPC-PROD-APP | `10.20.0.0/16` | Instances et services applicatifs |
| VPC-PROD-DATA | `10.30.0.0/16` | Base de données et services sensibles |
| VPC-DEV | `10.40.0.0/16` | Environnement non-production |
| VPC-INSPECTION | `10.60.0.0/16` | Firewall et egress contrôlé |
| VPC-DNS-SHARED | `10.70.0.0/16` | Resolver et services partagés selon le modèle retenu |
| On-premises | `172.20.0.0/16` | Réseau historique et serveurs DNS |

Hypothèse : ces plages ont été validées sans chevauchement pour ce scénario. Dans un vrai projet, les vérifier dans IPAM et dans le registre des réseaux de l'entreprise.

## 22.4. Exigences métier et sécurité

1. Les utilisateurs Internet peuvent atteindre le point d'entrée Web public approuvé sur TCP/443 ; ils ne doivent pas atteindre directement les instances applicatives privées ou les bases de données.
2. PROD-APP doit accéder à PROD-DATA uniquement sur TCP/5432, depuis les ressources applicatives autorisées.
3. DEV doit accéder à un dépôt d'artefacts partagé publié en privé ; DEV ne doit pas accéder à PROD-DATA.
4. Les sorties Internet des workloads privés doivent traverser l'inspection centrale.
5. Le réseau on-premises `172.20.0.0/16` peut accéder à l'API interne publiée de PROD-APP sur TCP/8443 et résoudre les noms DNS privés concernés.
6. On-premises ne doit pas disposer d'un accès direct à PROD-DATA ni à DEV, sauf exception explicitement approuvée.
7. Direct Connect est préféré en régime normal ; VPN doit constituer un chemin de secours testé.
8. Les flux réseau doivent être observables et les changements de routes critiques doivent être gouvernés.
9. La solution doit éviter les chevauchements CIDR et faciliter l'ajout futur de VPC.
10. L'architecture doit documenter ses coûts significatifs et ses limites.

## 22.5. État de configuration volontairement défectueux

L'équipe d'exploitation fournit les informations suivantes. Certaines sont correctes, d'autres créent des écarts avec les exigences.

### Table VPC du sous-réseau applicatif

```text
Destination       Cible
10.20.0.0/16      local
10.30.0.0/16      tgw-ORION
172.20.0.0/16     tgw-ORION
0.0.0.0/0         tgw-ORION
```

### Table TGW associée aux attachements applicatifs — `RT-SPOKE`

```text
Destination       Cible
10.30.0.0/16      attachment VPC-PROD-DATA
0.0.0.0/0         attachment VPC-INSPECTION
```

La politique de l'entreprise impose que les flux inter-VPC passent par le firewall central. La route `/16` vers PROD-DATA est donc suspecte.

### Table TGW associée à l'attachement on-premises — `RT-HYBRID`

```text
Destination       Cible
10.20.0.0/16      attachment VPC-INSPECTION
10.30.0.0/16      attachment VPC-PROD-DATA
10.40.0.0/16      attachment VPC-DEV
```

La politique ne prévoit pas d'accès on-premises vers PROD-DATA ni DEV. Les deux dernières destinations nécessitent une revue et l'une d'elles viole clairement l'exigence.

### Security Group de la base de données

```text
Entrant TCP/5432 depuis 0.0.0.0/0
```

Cette règle est trop permissive. Le besoin se limite aux ressources applicatives de production autorisées.

### DNS hybride

- Les instances PROD-APP résolvent certains noms hérités via un forwarding DNS.
- Les administrateurs on-premises ne parviennent pas à résoudre le nom `api.prod.aws.orion.example`.
- L'équipe n'a pas documenté les associations de private hosted zones, les Resolver endpoints, les règles de forwarding ni les règles réseau UDP/TCP 53.

### Observabilité

- Les tables et les groupes de sécurité sont gérés en partie manuellement.
- Les VPC Flow Logs ne sont pas activés de manière standard sur tous les VPC de production.
- Aucun test de bascule DX/VPN récent n'est disponible.

## 22.6. Travaux demandés

Le candidat doit livrer une proposition d'architecture et de correction qui comprend :

### Travail A — adresser et segmenter (10 points)

1. Confirmer les CIDR du scénario et expliquer comment prévenir les chevauchements à l'avenir.
2. Proposer un découpage de sous-réseaux adapté à deux AZ pour PROD-APP et VPC-INSPECTION.
3. Identifier les plages à suivre dans IPAM ou un référentiel équivalent.

### Travail B — Transit Gateway et routage (20 points)

1. Expliquer pourquoi la route `10.30.0.0/16 -> VPC-PROD-DATA` de `RT-SPOKE` contourne potentiellement l'inspection.
2. Proposer des tables TGW et des associations adaptées à la segmentation.
3. Décrire le chemin aller/retour de PROD-APP vers PROD-DATA après correction.
4. Expliquer comment éviter l'accès depuis on-premises vers DEV et PROD-DATA.

### Travail C — filtrage et inspection (15 points)

1. Corriger la règle de Security Group de la base de données.
2. Décrire le parcours des sorties Internet et les contrôles à placer dans le VPC d'inspection.
3. Expliquer pourquoi un firewall stateful exige une attention particulière à la symétrie.
4. Lister les tests positifs et négatifs.

### Travail D — connectivité hybride (10 points)

1. Décrire la stratégie DX principal / VPN secours.
2. Décrire les routes et annonces qui doivent être vérifiées.
3. Proposer un test de bascule mesurable.

### Travail E — PrivateLink et DNS (10 points)

1. Expliquer comment publier le dépôt d'artefacts afin que DEV consomme le service sans obtenir un accès IP complet au réseau de son fournisseur.
2. Concevoir le DNS hybride pour le nom `api.prod.aws.orion.example` et les noms on-premises.
3. Distinguer résolution DNS, routage et autorisation d'accès.

### Travail F — supervision et automatisation (15 points)

1. Proposer les sources de logs et les tests réseau à activer.
2. Décrire comment valider les chemins et détecter les dérives.
3. Proposer un processus IaC et une procédure de rollback.

### Travail G — risque, coût et documentation (10 points)

1. Identifier au moins quatre risques opérationnels.
2. Lister les principaux postes de coûts à estimer.
3. Décrire les éléments du dossier d'architecture à remettre.

### Travail H — qualité de la démarche (10 points)

Le candidat doit expliquer ses choix, faire la différence entre faits observés et hypothèses et proposer une validation des flux interdits autant que des flux autorisés.

**Total : 100 points.**

## 22.7. Livrables attendus

Le résultat doit inclure :

- Un schéma textuel lisible de bout en bout.
- Un tableau des associations et propagations TGW.
- Une matrice de flux autorisés/interdits.
- Un tableau indiquant les corrections des erreurs détectées.
- Un plan de tests avant/après.
- Une stratégie DNS, supervision et gestion des changements.
- Une synthèse des coûts, risques et limites.


# 23. Correction détaillée du challenge final

## 23.1. Correction A — adresser et segmenter (10 points)

Les CIDR fournis sont distincts dans le scénario. Dans une vraie organisation, le candidat doit comparer ces plages à tous les réseaux existants, y compris les sites distants, les VPC partenaires, les VPC d'autres régions et les réserves prévues.

Une proposition d'exemple pour PROD-APP :

```text
VPC-PROD-APP : 10.20.0.0/16
|
+-- AZ A
|   +-- subnet-app-a        10.20.10.0/24
|   +-- subnet-endpoint-a   10.20.20.0/24
|   +-- subnet-tgw-a        10.20.30.0/24 (taille à valider selon l'usage)
|
+-- AZ B
    +-- subnet-app-b        10.20.11.0/24
    +-- subnet-endpoint-b   10.20.21.0/24
    +-- subnet-tgw-b        10.20.31.0/24 (taille à valider selon l'usage)
```

Exemple pour VPC-INSPECTION :

```text
VPC-INSPECTION : 10.60.0.0/16
|
+-- AZ A
|   +-- subnet-tgw-a        10.60.10.0/24
|   +-- subnet-firewall-a   10.60.20.0/24
|   +-- subnet-egress-a     10.60.30.0/24
|
+-- AZ B
    +-- subnet-tgw-b        10.60.11.0/24
    +-- subnet-firewall-b   10.60.21.0/24
    +-- subnet-egress-b     10.60.31.0/24
```

Les tailles ne sont pas prescrites pour toutes les ressources. La proposition doit être ajustée aux exigences du service, à la quantité d'adresses consommées et aux quotas. Il faut utiliser une réserve par AZ et éviter de remplir les plages dès le premier déploiement.

IPAM ou le registre réseau devrait contenir au minimum : propriétaire, compte, région, environnement, CIDR, date d'allocation, justification, capacité estimée et plage future réservée.

## 23.2. Correction B — Transit Gateway et routage (20 points)

### Erreur 1 : route directe vers PROD-DATA

Dans `RT-SPOKE`, la route `10.30.0.0/16 -> attachment VPC-PROD-DATA` est plus spécifique que `0.0.0.0/0 -> attachment VPC-INSPECTION`. Le trafic vers PROD-DATA prendra donc le chemin direct plutôt que le chemin par défaut vers l'inspection.

**Correction :** retirer cette route directe de la table utilisée par les flux qui doivent obligatoirement être inspectés. Envoyer les destinations concernées vers l'attachement d'inspection selon le modèle choisi. Le VPC d'inspection doit ensuite renvoyer le trafic vers TGW, et la table TGW associée à l'attachement d'inspection doit connaître les CIDR de destination.

### Table TGW proposée pour les spokes

```text
RT-SPOKE
Associations : attachements VPC-PROD-APP, VPC-PROD-DATA, VPC-DEV
(à adapter selon la politique et le sens du flux)

Destination       Cible
0.0.0.0/0         attachment VPC-INSPECTION
```

Cette table est un exemple pour des flux de spokes qui doivent tous passer par l'inspection. Si certaines communications ne doivent pas passer par ce chemin, il faut les modéliser expressément et vérifier les implications de sécurité et de symétrie. Ne pas ajouter de route spécifique vers PROD-DATA si cela contourne la politique.

### Table TGW proposée pour le trafic qui sort de l'inspection

```text
RT-INSPECTION
Association : attachment VPC-INSPECTION

Destination       Cible
10.20.0.0/16      attachment VPC-PROD-APP
10.30.0.0/16      attachment VPC-PROD-DATA
10.40.0.0/16      attachment VPC-DEV        (seulement si nécessaire)
10.70.0.0/16      attachment VPC-DNS-SHARED  (selon l'architecture)
172.20.0.0/16     attachment hybride DX/VPN selon les routes actives
```

Les routes de destination correspondent aux destinations que le trafic inspecté peut rejoindre. Il faut éviter de publier automatiquement `10.40.0.0/16` à tous les domaines si DEV ne doit pas être accessible par certains chemins.

### Table TGW pour on-premises

```text
RT-HYBRID
Association : attachment hybride

Destination       Cible
10.20.0.0/16      attachment VPC-INSPECTION
10.70.0.0/16      attachment VPC-INSPECTION (si DNS est inspecté/acheminé ainsi)
```

Les routes directes vers `10.30.0.0/16` et `10.40.0.0/16` doivent être retirées, sauf exception formellement approuvée. En renvoyant les destinations autorisées vers l'inspection, le chemin réseau peut contrôler l'accès à l'API de production sans donner un chemin direct vers le réseau de données.

### Table VPC de l'inspection

Les routes des sous-réseaux traversés doivent acheminer les flux reçus vers le firewall selon l'intégration du service, puis les flux post-inspection vers TGW pour les destinations privées ou vers le NAT/IGW pour la sortie Internet. Il faut vérifier le détail de la topologie de Network Firewall, notamment les routes des subnets de transit, des endpoints et de sortie.

### Chemin PROD-APP vers PROD-DATA

```text
Instance APP
   |
   v
Route table subnet APP : 10.30.0.0/16 -> TGW
   |
   v
RT-SPOKE : destination non locale -> attachment INSPECTION
   |
   v
VPC-INSPECTION : firewall stateful
   |
   v
Route post-inspection -> TGW
   |
   v
RT-INSPECTION : 10.30.0.0/16 -> attachment PROD-DATA
   |
   v
VPC-PROD-DATA : SG autorise seulement TCP/5432 depuis l'identité/réseau applicatif requis
```

Retour :

```text
VPC-PROD-DATA
   |
   v
Route table DATA : 10.20.0.0/16 -> TGW
   |
   v
RT-SPOKE pour l'attachment DATA : route par défaut vers INSPECTION
   |
   v
VPC-INSPECTION : firewall voit le retour du flux
   |
   v
RT-INSPECTION : 10.20.0.0/16 -> attachment PROD-APP
   |
   v
Instance APP
```

La description est un modèle logique. Dans le déploiement réel, les tables TGW d'entrée et de sortie, les routes du sous-réseau d'inspection et l'appliance mode doivent être adaptées et validées par les tests de chemin. Il faut notamment confirmer que le retour traverse la bonne ressource stateful.

### Prévenir l'accès on-premises vers DEV/DATA

- Retirer les routes vers `10.30.0.0/16` et `10.40.0.0/16` de `RT-HYBRID` si elles ne sont pas prévues.
- Ne pas annoncer ces préfixes au réseau local, sauf exception approuvée.
- Contrôler les routes des routeurs on-premises ainsi que les tables TGW.
- Ajouter le contrôle central d'inspection pour les seuls préfixes publiés, comme l'API et les services DNS.
- Tester explicitement des tentatives vers PROD-DATA et DEV depuis le LAN et constater leur échec.

## 23.3. Correction C — filtrage et inspection (15 points)

### Security Group de la base

Règle initiale :

```text
Entrant TCP/5432 depuis 0.0.0.0/0
```

Cette règle permet une portée beaucoup trop large si une route vers la base existe depuis des sources non désirées. La correction doit être limitée aux ressources applicatives autorisées. Lorsque le modèle de connectivité et les restrictions AWS le permettent, préférer une référence au SG applicatif approprié. Sinon, limiter la règle aux CIDR source exacts ou au chemin documenté.

Exemple conceptuel :

```text
SG-DATABASE
  Entrant : TCP/5432 depuis SG-PROD-APP
  Sortant : règles nécessaires au fonctionnement documentées
```

Le nom `SG-PROD-APP` représente un SG défini dans la configuration réelle ; ce n'est pas un ID littéral. La compatibilité des références de SG doit être confirmée pour la topologie transitive choisie. En cas de restriction, utiliser une méthode de filtrage adaptée plutôt que considérer une référence SG comme universellement applicable.

### Egress centralisé

Le chemin doit être :

```text
Subnet privé
  -> TGW
  -> table TGW du domaine spoke
  -> attachment VPC-INSPECTION
  -> Network Firewall / appliance
  -> NAT Gateway si sortie IPv4 requise
  -> Internet Gateway
  -> destination Internet
```

Les routes de retour et la symétrie doivent être vérifiées. Les endpoints privés des services AWS peuvent être un chemin spécifique, documenté et contrôlé plutôt qu'une sortie Internet. Il faut veiller à ce qu'aucune route plus spécifique n'autorise une sortie non inspectée qui viole les exigences.

### Tests positifs et négatifs

| Test | Résultat attendu |
|---|---|
| APP vers DATA en TCP/5432 | Autorisé uniquement depuis la source approuvée |
| APP vers DATA en TCP/22 | Bloqué, sauf besoin et exception approuvés |
| DEV vers DATA en TCP/5432 | Bloqué |
| On-premises vers API PROD en TCP/8443 | Autorisé si le chemin et l'identité de source sont approuvés |
| On-premises vers DATA | Bloqué |
| Workload privé vers destination Internet approuvée | Autorisé via le chemin d'inspection prévu |
| Workload privé vers domaine ou port non autorisé | Bloqué par le contrôle prévu |
| Client Internet vers instance DATA directement | Aucun chemin d'entrée direct publié ; bloqué par architecture et règles |

Un seul contrôle ne doit pas être la preuve de toutes les propriétés. Les tests doivent vérifier le routage, le firewall, les SG, le DNS et l'application.

## 23.4. Correction D — connectivité hybride (10 points)

- Configurer Direct Connect comme chemin préféré selon la politique de routage retenue.
- Configurer Site-to-Site VPN comme secours et vérifier les deux tunnels fournis, quand ils s'appliquent à la connexion retenue.
- Définir les préfixes annoncés depuis le LAN et ceux autorisés vers le LAN.
- Limiter les routes vers les services réellement publiés : API PROD et services partagés nécessaires.
- Vérifier BGP, les routes reçues, les routes actives, les propagations et les routes de retour.
- Contrôler que la route vers le LAN passe par le bon attachement DX/VPN lorsque l'inspection a été traversée.

### Test de bascule proposé

1. Capturer les routes et métriques normales.
2. Tester une requête applicative depuis on-premises vers l'API `:8443`.
3. Simuler la perte du chemin Direct Connect dans une fenêtre approuvée.
4. Vérifier que le VPN est établi et que les routes de secours sont actives.
5. Retester l'API, la résolution DNS et les flux autorisés.
6. Mesurer le temps de bascule et les erreurs.
7. Restaurer DX et confirmer le chemin préféré.
8. Rechercher toute route inattendue, fuite de préfixe ou oscillation.

Critères : bascule observée et expliquée, durée compatible avec l'objectif de service, aucune ouverture de route interdite, journalisation et procédure de retour fonctionnelles.

## 23.5. Correction E — PrivateLink et DNS (10 points)

### Dépôt d'artefacts

Si le service d'artefacts peut être publié à travers une solution compatible PrivateLink, l'équipe fournisseur peut exposer ce service via un endpoint service et autoriser seulement les consommateurs attendus. DEV consomme le service par son interface endpoint et les noms DNS appropriés.

Le design doit inclure :

- Politique d'acceptation des consommateurs.
- DNS privé et noms de service.
- SG de l'interface endpoint.
- Contrôle d'identité au niveau du service.
- Disponibilité et placement sur plusieurs AZ si nécessaire.
- Journaux et critères de retrait d'un consommateur.

PrivateLink donne accès au service exposé, et non un accès IP général à tout le VPC du fournisseur.

### DNS pour l'API interne

Créer ou vérifier une private hosted zone qui porte le nom `api.prod.aws.orion.example`, selon le modèle DNS de l'entreprise, et l'associer aux VPC qui doivent résoudre ce nom. Pour les clients on-premises, mettre en place un Resolver inbound endpoint dans le VPC de DNS partagé ou dans le VPC d'un service DNS convenablement gouverné. Le DNS local configure une règle de forwarding conditionnelle vers les adresses privées de cet endpoint pour le domaine AWS privé concerné.

Pour les noms on-premises résolus depuis AWS, utiliser un outbound Resolver endpoint et une règle de forwarding conditionnelle pointant vers les résolveurs DNS on-premises. Vérifier routes, SG/NACL, UDP/TCP 53, redondance multi-AZ, règles de domaine, associations de VPC et journaux DNS.

### Distinguer les trois étapes

1. **DNS :** le nom renvoie-t-il la bonne adresse ?
2. **Routage et filtrage :** le client peut-il joindre l'adresse/port via le chemin voulu ?
3. **Autorisation applicative :** l'identité et la requête sont-elles autorisées par le service ?

Un échec DNS n'est pas un échec de routage ; un échec `AccessDenied` n'est pas nécessairement un problème réseau.

## 23.6. Correction F — supervision et automatisation (15 points)

### Sources à activer

- VPC Flow Logs sur les VPC de production et les interfaces critiques selon la politique d'observabilité.
- Logs de AWS Network Firewall ou de l'appliance retenue.
- CloudTrail pour les changements API de routes, SG, attachements et règles.
- Métriques et alarmes CloudWatch pertinentes pour les services de transit, VPN, NAT, endpoints et firewall.
- Logs et métriques Route 53 Resolver/DNS Firewall si requis.
- Reachability Analyzer pour des tests de chemins pris en charge.
- Network Access Analyzer pour vérifier des exigences de chemins et d'accès.
- Journaux et métriques du routeur on-premises, BGP et Direct Connect selon l'environnement.

Les destinations de logs et leurs accès doivent être protégés. Il faut vérifier la livraison réelle et la rétention, pas seulement l'existence d'une configuration.

### IaC et validation continue

Décrire dans CloudFormation/CDK/Terraform ou l'outil standard de l'entreprise : VPC, sous-réseaux, tables et associations de routage, attachements TGW, tables TGW et routes, SG, endpoints, logs et ressources réseau compatibles avec l'outil choisi.

Pipeline recommandé :

1. Analyse de code et validation des CIDR.
2. Contrôles de sécurité et de policy.
3. Revue du plan de changement.
4. Déploiement sur un environnement de test.
5. Tests positifs et négatifs.
6. Analyse de reachability appropriée.
7. Approbation et déploiement progressif.
8. Surveillance et rollback si nécessaire.

### Détecter la dérive

Comparer périodiquement la configuration réelle au code déclaré. Les modifications manuelles critiques doivent être documentées et réintégrées dans le code ou réverties de façon contrôlée. Le pipeline ne doit pas effacer aveuglément une correction d'incident sans examen.

## 23.7. Correction G — risques, coûts et documentation (10 points)

### Risques identifiés

Au minimum :

1. Route spécifique qui contourne l'inspection.
2. Security Group de base ouvert à `0.0.0.0/0`.
3. Accès on-premises à DEV et DATA par routes TGW incorrectes.
4. DNS hybride incomplet ou dépendant d'une règle non documentée.
5. Absence de test récent de bascule DX/VPN.
6. Observabilité incomplète.
7. Changements manuels non reproductibles.
8. Risque d'asymétrie au niveau du firewall stateful.
9. Coût de transit/inspection/NAT plus élevé que prévu.
10. Chevauchement CIDR à venir si le plan d'adressage n'est pas gouverné.

### Postes de coûts à estimer

NAT Gateway et données traitées, Transit Gateway et transferts, Network Firewall, interface endpoints et PrivateLink, Route 53 Resolver endpoints et requêtes, Flow Logs et requêtes d'analyse, trafic inter-AZ/inter-région, Direct Connect et services opérateur, VPN et services d'observabilité. Les prix varient selon région et utilisation ; utiliser les tarifs actuels et des prévisions de trafic réalistes.

### Dossier final d'architecture

Le dossier doit contenir :

- Diagramme de l'architecture et flux critiques.
- Registre CIDR et conventions.
- Tables de routage VPC et TGW, associations et propagations.
- Matrice des flux avec source, destination, port, propriétaire, justification et résultat de test.
- Règles SG, NACL et firewall pertinentes.
- Architecture DNS et dépendances de résolution.
- Stratégie DX/VPN, routage BGP et tests de bascule.
- Architecture de logs, alarmes et rétention.
- Processus IaC, tests, approbations et rollback.
- Risques résiduels, limites, coûts et propriétaires opérationnels.

## 23.8. Correction H — qualité de démarche (10 points)

Une réponse experte doit distinguer :

- Les faits observés (par exemple, une route active ou un rejet dans un log).
- Les hypothèses (par exemple, « la route plus spécifique peut contourner l'inspection »).
- Les tests qui permettent de départager les hypothèses.
- Les corrections, leur périmètre et les risques de changement.
- Les tests qui démontrent que l'accès voulu fonctionne.
- Les tests qui démontrent que les accès interdits échouent.

Une bonne démarche évite les changements massifs, garde des preuves avant/après et crée des mesures empêchant la répétition du défaut.


# 24. Checklist d'architecture, grille d'évaluation et glossaire

## 24.1. Checklist avant mise en production

### Adressage

- [ ] Les CIDR VPC, subnets, LAN et réseaux partenaires sont inventoriés.
- [ ] Aucun chevauchement incompatible n'existe.
- [ ] Les nouvelles allocations suivent IPAM ou un processus documenté.
- [ ] Des réserves existent pour l'évolution, les migrations et la reprise.
- [ ] IPv4 et IPv6 ont été considérés séparément.

### Routage

- [ ] Chaque subnet est associé explicitement à la route table attendue.
- [ ] Les routes VPC nécessaires existent et les routes superflues ont été évitées.
- [ ] Les associations et propagations TGW correspondent aux domaines de sécurité.
- [ ] Le comportement des routes les plus spécifiques a été examiné.
- [ ] Les routes retour sont documentées.
- [ ] Les routes de contournement de l'inspection ont été recherchées.
- [ ] Les annonces BGP sont filtrées et testées.

### Sécurité

- [ ] Les Security Groups appliquent le moindre privilège.
- [ ] Les règles NACL tiennent compte de leur nature stateless et des ports de retour requis.
- [ ] Le firewall est sur le chemin voulu dans les deux sens.
- [ ] L'appliance mode est activé si le modèle le nécessite.
- [ ] Les accès privés aux services AWS utilisent les endpoints adaptés.
- [ ] Les endpoint policies, IAM et policies de ressources sont cohérentes.
- [ ] Les flux interdits sont testés, pas seulement les flux autorisés.

### DNS et IPv6

- [ ] Les zones privées sont associées aux VPC concernés.
- [ ] Les Resolver endpoints et règles de forwarding sont documentés.
- [ ] Les règles réseau pour UDP/TCP 53 sont justifiées.
- [ ] Les enregistrements A/AAAA sont cohérents avec les chemins.
- [ ] Les routes IPv6 et règles IPv6 sont auditées.
- [ ] DNS64/NAT64 est déployé seulement si un besoin réel le justifie.

### Disponibilité et coûts

- [ ] Les dépendances critiques sont réparties et testées par AZ lorsque nécessaire.
- [ ] Les chemins DX/VPN et les priorités de route ont été testés.
- [ ] Les objectifs de récupération et leur mesure sont définis.
- [ ] Le coût fixe et variable des principaux services est estimé.
- [ ] Les quotas sont suffisants pour le déploiement et la croissance.

### Observabilité et exploitation

- [ ] Flow Logs sont activés selon le périmètre attendu.
- [ ] Les logs de firewall, DNS, CloudTrail et services critiques sont disponibles.
- [ ] Reachability Analyzer/Network Access Analyzer sont utilisés lorsque pertinents.
- [ ] La dérive IaC est détectée et traitée.
- [ ] Une procédure de changement et un rollback sont documentés.
- [ ] Les propriétaires d'exploitation et d'escalade sont connus.

## 24.2. Grille d'évaluation du challenge

| Score | Interprétation |
|---:|---|
| 90–100 | Niveau expert solide : architecture cohérente, contrôle des flux, preuves et limites bien expliqués |
| 80–89 | Très bon niveau : choix robustes avec quelques détails d'exploitation ou de validation à préciser |
| 70–79 | Niveau opérationnel : conception globalement correcte, mais certains risques ou chemins restent insuffisamment couverts |
| 60–69 | Connaissances présentes mais lacunes notables en segmentation, symétrie ou validation |
| 40–59 | Conception fragile ; confusion entre routes, permissions et contrôles réseau |
| 0–39 | Les fondamentaux de conception et de dépannage doivent être repris avant le déploiement |

## 24.3. Glossaire

- **AZ (Availability Zone)** : zone de disponibilité dans une région AWS.
- **BGP** : protocole de routage dynamique pour échanger des préfixes et des attributs de route.
- **CIDR** : notation définissant une plage d'adresses IP par préfixe.
- **Cloud WAN** : service AWS de gestion d'un réseau global via une politique de connectivité.
- **Direct Connect (DX)** : connexion réseau dédiée entre un site et AWS via un emplacement Direct Connect.
- **DNS64** : mécanisme qui synthétise des réponses AAAA à partir d'enregistrements IPv4 selon sa configuration.
- **Egress** : trafic sortant d'un réseau ou d'une ressource.
- **Egress-only Internet Gateway** : passerelle de sortie IPv6 empêchant les connexions entrantes initiées depuis Internet.
- **IPAM** : gestionnaire d'adresses IP pour organiser, suivre et contrôler les allocations.
- **Longest prefix match** : règle de sélection fondée sur le préfixe de destination le plus spécifique, selon les priorités du service.
- **MTU** : taille maximale d'un paquet sur un lien ou un chemin donné.
- **NACL** : Network Access Control List, filtrage stateless associé à un sous-réseau.
- **NAT64** : traduction permettant à des systèmes IPv6 d'atteindre certains systèmes IPv4 selon la configuration.
- **PrivateLink** : moyen d'accès privé à des services via des endpoints pris en charge, sans imposer un peering IP général.
- **Private hosted zone** : zone DNS privée Route 53 associée à un ou plusieurs VPC.
- **Reachability Analyzer** : outil d'analyse de connectivité réseau virtuelle entre ressources prises en charge.
- **Resolver endpoint** : point de terminaison Route 53 VPC Resolver pour les échanges DNS entrants ou sortants.
- **Route propagation** : publication de routes d'un attachement vers une table de routage selon la configuration.
- **Security Group (SG)** : pare-feu stateful associé aux interfaces/ressources compatibles.
- **Site-to-Site VPN** : connectivité VPN IPsec entre un réseau distant et AWS.
- **TGW (Transit Gateway)** : hub de transit pour relier plusieurs VPC et connexions hybrides.
- **TGW attachment** : attachement reliant un réseau ou une connexion à un Transit Gateway.
- **TGW route table** : table du Transit Gateway qui détermine l'attachement de destination.
- **VPC** : réseau virtuel isolé logiquement dans AWS.
- **VPC Flow Logs** : enregistrement de métadonnées sur une partie du trafic IP associé à un VPC, sous-réseau ou interface pris en charge.
- **VPC Peering** : connexion privée entre deux VPC, non transitive.


# 25. Documentation officielle

Les liens ci-dessous pointent vers la documentation AWS à utiliser pour vérifier les détails techniques, les limitations, les quotas, les tarifs et les procédures. Les services cloud évoluent : vérifier la page officielle au moment du déploiement.

## VPC et routage

- Amazon VPC User Guide : https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- Priorité des routes et longest prefix match : https://docs.aws.amazon.com/vpc/latest/userguide/route-tables-priority.html
- VPC Flow Logs : https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- Limitations de Flow Logs : https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
- Reachability Analyzer : https://docs.aws.amazon.com/vpc/latest/reachability/what-is-reachability-analyzer.html
- VPC IP Address Manager : https://docs.aws.amazon.com/vpc/latest/ipam/

## Transit Gateway et routage centralisé

- Fonctionnement de Transit Gateway : https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
- Tables de routage Transit Gateway : https://docs.aws.amazon.com/vpc/latest/tgw/tgw-route-tables.html
- Propagation des routes TGW : https://docs.aws.amazon.com/vpc/latest/tgw/enable-tgw-route-propagation.html
- AWS Network Firewall : https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html
- Dépannage Network Firewall avec TGW : https://docs.aws.amazon.com/network-firewall/latest/developerguide/troubleshooting-general-issues.html
- AWS Cloud WAN : https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html

## Endpoints, PrivateLink et DNS

- Gateway endpoints : https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html
- AWS PrivateLink : https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html
- Route 53 VPC Resolver : https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html
- DNS Firewall : https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html
- DNS64 et NAT64 : https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-nat64-dns64.html
- Egress-only Internet Gateway : https://docs.aws.amazon.com/vpc/latest/userguide/egress-only-internet-gateway.html

## Connectivité hybride

- AWS Site-to-Site VPN : https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
- AWS Direct Connect : https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html

## Gouvernance et sécurité

- AWS Well-Architected Framework — Security Pillar : https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html
- AWS Well-Architected Framework — Reliability Pillar : https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html
- AWS CloudTrail : https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- AWS Service Quotas : https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html
- AWS Pricing Calculator : https://calculator.aws/


# Conclusion générale

Un réseau AWS expert ne se résume pas à connecter des VPC. Il faut organiser l'espace d'adressage, contrôler les tables et les annonces de routes, segmenter les domaines de transit, garantir la symétrie des chemins stateful, intégrer le DNS, contrôler les sorties, observer les décisions et automatiser les changements.

Le meilleur indicateur de maturité n'est pas le nombre de services AWS utilisés. C'est la capacité de l'équipe à expliquer chaque flux important, à prouver pourquoi il est autorisé ou bloqué, à mesurer la réaction à une panne et à restaurer une configuration connue sans dépendre de connaissances tacites.

**Règle finale : concevoir le flux, vérifier les routes, appliquer le moindre privilège, instrumenter le chemin, tester le retour et documenter la preuve.**
