
# Microsoft Azure — Cours expert
## Architecture cloud d'entreprise, réseau avancé, Zero Trust, gouvernance et automatisation industrialisée

**Niveau :** Expert  
**Prérequis :** maîtrise du cours Azure intermédiaire, des réseaux TCP/IP, du routage, des identités, de RBAC, de Bicep et de la supervision.  
**Public cible :** architectes cloud, ingénieurs plateforme, ingénieurs réseau, spécialistes sécurité et responsables d'infrastructures Azure.  
**Objectif général :** concevoir, déployer et exploiter une plateforme Azure d'entreprise gouvernée, sécurisée, automatisée et résiliente.

---

# Sommaire

1. Objectifs et laboratoire expert
2. Architecture Azure à grande échelle
3. Landing zones et gouvernance
4. Réseau hub-and-spoke et routage avancé
5. Sécurité Zero Trust et défense en profondeur
6. Identités managées, RBAC et privilèges
7. Infrastructure as Code industrialisée
8. Automatisation avec Azure CLI, Bicep et pipelines
9. Observabilité avancée et réponse aux incidents
10. Haute disponibilité, continuité et reprise après sinistre
11. Stockage, données et sécurité des accès privés
12. FinOps et optimisation des plateformes
13. Travaux pratiques guidés
14. Exercices corrigés
15. Défi final expert sur 100 points
16. Correction complète du défi
17. Références et checklist de production

---

# 1. Objectifs et laboratoire expert

## 1.1 Compétences visées

À la fin du cours, l'apprenant doit être capable de :

- concevoir une architecture Azure multi-abonnements ;
- structurer une landing zone selon les responsabilités et les contraintes de sécurité ;
- distinguer gouvernance, gestion des identités et plan de données ;
- concevoir un réseau hub-and-spoke et analyser ses limites de transit ;
- choisir entre peering, Azure Firewall, VPN Gateway, ExpressRoute et Virtual WAN ;
- établir une stratégie Zero Trust adaptée aux ressources cloud ;
- limiter les privilèges des identités humaines et applicatives ;
- concevoir des modules Bicep réutilisables ;
- mettre en place des déploiements contrôlés et vérifiables ;
- organiser les journaux, métriques, alertes et enquêtes ;
- concevoir des objectifs RPO/RTO et des tests de reprise ;
- arbitrer entre sécurité, disponibilité, complexité et coût ;
- documenter les décisions d'architecture et les procédures opérationnelles.

## 1.2 Préparer un environnement de laboratoire

Le laboratoire doit être isolé de la production.

Préparer :

- un abonnement Azure de test ;
- Azure CLI ;
- Bicep ;
- Git ;
- un éditeur de code ;
- un compte disposant uniquement des permissions nécessaires ;
- une région approuvée ;
- un budget de laboratoire ;
- un plan de suppression des ressources.

Vérifier l'environnement :

```bash
az version
az bicep version
az account show --output json
az account list --output table
```

Si Bicep ou Azure CLI n'est pas disponible, consulter l'aide officielle de l'outil et installer une version prise en charge.

Définir explicitement le contexte :

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
az account show \
  --query "{subscription:name,id:id,tenant:tenantId}" \
  --output json
```

Ne jamais exécuter les laboratoires sur un abonnement de production sans validation formelle.

## 1.3 Principes de conception expert

Toute décision doit prendre en compte au minimum :

1. les exigences métier ;
2. les menaces ;
3. les dépendances ;
4. la disponibilité ;
5. les performances ;
6. le coût ;
7. l'exploitabilité ;
8. les obligations réglementaires ;
9. le cycle de vie ;
10. les mécanismes de retour arrière.

Une architecture n'est pas optimale simplement parce qu'elle utilise le plus grand nombre de services Azure. La complexité supplémentaire doit être justifiée par un besoin mesurable.

---

# 2. Architecture Azure à grande échelle

## 2.1 Séparer les responsabilités

Une architecture d'entreprise peut séparer les responsabilités en plusieurs abonnements.

```text
Microsoft Entra ID
|
+-- Management Group : Platform
|   |
|   +-- Subscription : Connectivity
|   |   +-- Hub VNet
|   |   +-- Firewall
|   |   +-- VPN / ExpressRoute
|   |
|   +-- Subscription : Management
|       +-- Supervision
|       +-- Automatisation
|       +-- Services de gestion
|
+-- Management Group : LandingZones
|   |
|   +-- Subscription : Application-Production
|   +-- Subscription : Application-NonProduction
|   +-- Subscription : Data-Platform
|
+-- Management Group : Sandbox
    +-- Subscription : Lab
```

Cette séparation peut améliorer l'isolation, la gouvernance, la délégation et la visibilité financière.

Elle doit rester proportionnée aux besoins. Un abonnement par application n'est pas une règle universelle : le choix dépend des frontières de sécurité, de facturation, d'exploitation et des quotas.

## 2.2 Modèle de responsabilité

Une landing zone doit définir clairement qui est responsable :

| Domaine | Responsabilité à formaliser |
|---|---|
| Identité | Utilisateurs, groupes, accès privilégiés |
| Réseau | Adressage, connectivité, filtrage |
| Sécurité | Politiques, détection, réponse |
| Plateforme | Services partagés et automatisation |
| Applications | Configuration et dépendances métier |
| Données | Classification, accès et rétention |
| Coûts | Budgets, attribution et optimisation |
| Continuité | Sauvegarde, restauration et bascule |

Une responsabilité non attribuée devient souvent une faille opérationnelle.

## 2.3 Plan de contrôle et plan de données

Le plan de contrôle gère les ressources : création, modification, configuration et suppression.

Le plan de données correspond à l'utilisation réelle du service : lire un blob, interroger une base ou échanger du trafic applicatif.

```text
Administrateur
     |
     v
Plan de contrôle
ARM / RBAC / Azure Policy
     |
     v
Configuration du service
     |
     v
Plan de données
Application / Blob / Base de données
```

Conséquence importante : une personne peut être autorisée à gérer la ressource sans disposer des droits nécessaires pour lire les données. Inversement, un rôle de données ne confère pas automatiquement des droits d'administration du service.

## 2.4 Architecture multi-région

Une architecture multi-région doit définir :

- la région principale ;
- la région secondaire ;
- la stratégie de réplication ;
- le mécanisme de bascule ;
- le routage et la résolution DNS ;
- la cohérence des données ;
- les dépendances régionales ;
- les procédures de retour à la normale.

```text
                    Utilisateurs
                         |
                  Point de routage
                         |
               +---------+---------+
               |                   |
               v                   v
          Région A             Région B
          Principale           Secours
               |                   |
          Application         Application
               |                   |
          Données A <------> Données B
                Réplication adaptée
```

Ce schéma ne signifie pas que les données sont automatiquement synchronisées. La réplication et la cohérence dépendent du service choisi.

Les modes actif-actif et actif-passif ont des coûts et des contraintes différents. Le mode actif-actif peut améliorer la disponibilité et la latence, mais il complique la cohérence, les conflits d'écriture et l'exploitation.

## 2.5 ADR — Architecture Decision Record

Chaque décision majeure doit être documentée.

Exemple :

```text
ADR-001 : Architecture réseau hub-and-spoke

Contexte :
Plusieurs équipes doivent partager une connectivité
hybride et un point central de contrôle.

Décision :
Utiliser un hub réseau partagé et des spokes isolés.

Options évaluées :
- Réseau plat
- Peering direct généralisé
- Hub-and-spoke
- Azure Virtual WAN

Conséquences :
- Contrôle centralisé possible
- Nécessité de concevoir le transit
- Dépendance accrue aux services du hub
- Coût et exploitation du pare-feu à mesurer

Conditions de réévaluation :
Croissance importante du nombre de régions,
de tunnels ou de réseaux interconnectés.
```

Un ADR ne remplace pas un diagramme réseau, une matrice de flux ou un plan de reprise.

---

# 3. Landing zones et gouvernance

## 3.1 Azure Policy

Azure Policy permet d'évaluer et de contrôler la conformité des ressources.

Effets courants, selon la définition et le scénario :

- `Audit` : signaler les écarts ;
- `Deny` : refuser les opérations non conformes ;
- `Modify` : modifier certaines propriétés prises en charge ;
- `DeployIfNotExists` : déclencher un déploiement complémentaire selon les conditions ;
- `Disabled` : désactiver l'effet d'une définition selon la configuration.

Les effets ne sont pas interchangeables. Les droits d'identité managée, les remédiations et les prérequis doivent être examinés pour les politiques qui déploient ou modifient des ressources.

## 3.2 Gouvernance en couches

```text
Management Group racine
|
+-- Politiques et rôles communs
|
+-- Platform
|   +-- Réseau partagé
|   +-- Gestion et supervision
|
+-- Landing Zones
|   +-- Production
|   +-- Non-production
|
+-- Sandbox
    +-- Expérimentation contrôlée
```

Une politique héritée peut affecter les ressources d'un abonnement ou d'un groupe de ressources. Les exclusions doivent être justifiées, documentées et surveillées.

## 3.3 Exemple de stratégie de gouvernance

Une entreprise peut définir les exigences suivantes :

- seules certaines régions sont autorisées ;
- chaque ressource doit posséder des balises de propriétaire et de centre de coûts ;
- les journaux de diagnostic requis doivent être configurés ;
- les accès publics aux données doivent être limités ;
- les ressources non conformes doivent être détectées ;
- les exceptions doivent posséder un responsable et une date de révision.

Toutes les ressources Azure ne prennent pas en charge exactement les mêmes propriétés ou effets. Une politique doit être testée sur les types de ressources réellement utilisés.

## 3.4 Déployer une affectation de stratégie

Exemple conceptuel :

```bash
az policy assignment list \
  --scope "/subscriptions/<SUBSCRIPTION_ID>" \
  --output table
```

Lister les définitions :

```bash
az policy definition list --output table
```

Pour une politique intégrée, vérifier son identifiant, ses paramètres et son effet avant de créer une affectation.

Ne pas attribuer une politique restrictive à toute la production sans analyse d'impact. Utiliser d'abord un périmètre de test ou un effet d'audit lorsque cela convient.

## 3.5 RBAC et gouvernance

RBAC et Azure Policy ont des rôles différents :

- RBAC décide qui peut effectuer une action ;
- Azure Policy évalue ou contrôle la conformité d'une ressource ;
- les règles réseau contrôlent les communications ;
- les contrôles de données déterminent l'accès aux contenus ;
- les mécanismes de détection identifient des comportements anormaux.

Aucun de ces mécanismes ne remplace tous les autres.

---

# 4. Réseau hub-and-spoke et routage avancé

## 4.1 Architecture de référence

```text
                     Réseau d'entreprise
                             |
                       VPN / ExpressRoute
                             |
                             v
+------------------------------------------------+
| HUB : 10.100.0.0/16                            |
|                                                |
|  Gateway ---- Azure Firewall ---- Services DNS |
|                    |                           |
+--------------------+---------------------------+
                     |
              Routage et peerings
             /                   \
            v                     v
+-----------------------+  +-----------------------+
| SPOKE-APP              |  | SPOKE-DATA             |
| 10.110.0.0/16          |  | 10.120.0.0/16          |
|                        |  |                        |
| App subnet             |  | Private Endpoints      |
| Compute                |  | Services de données    |
+------------------------+  +-----------------------+
```

Les plages sont illustratives. Elles doivent être adaptées au plan d'adressage réel.

Le hub héberge les services de connectivité et de contrôle partagés. Les spokes isolent les applications, les environnements ou les domaines de données.

## 4.2 Peering non transitif

Le peering de VNets est non transitif.

```text
Spoke-A <---- peering ----> Hub
Spoke-B <---- peering ----> Hub

Spoke-A  -X->  Spoke-B
```

La présence de deux peerings avec un même hub ne suffit pas à établir une communication entre les spokes.

Pour permettre un transit, concevoir un chemin explicite avec les fonctionnalités et routes adaptées : pare-feu ou appliance réseau, passerelle et propagation de routes, ou autre mécanisme pris en charge.

Le peering direct entre deux spokes peut être adapté à certains flux sensibles à la latence, mais il peut aussi contourner l'inspection centralisée. Cette décision doit être explicite.

## 4.3 Routage forcé via Azure Firewall

Une route personnalisée peut diriger le trafic vers une appliance virtuelle.

```text
Spoke
  |
  | UDR : 0.0.0.0/0
  v
Azure Firewall
  |
  +----> Destination autorisée
  |
  +----> Destination refusée
```

Une route `0.0.0.0/0` vers un pare-feu peut servir à contrôler les sorties Internet, mais sa présence ne garantit pas à elle seule que tout le trafic sera inspecté.

Il faut vérifier :

- les routes effectives ;
- les règles du pare-feu ;
- les routes de retour ;
- la propagation des routes de passerelle ;
- les exceptions nécessaires ;
- les flux vers les services de plateforme ;
- les éventuels chemins alternatifs.

Une mauvaise UDR peut créer une panne globale ou une asymétrie de routage.

## 4.4 Azure Firewall, NSG et appliance réseau

| Mécanisme | Rôle typique |
|---|---|
| NSG | Filtrage réseau au niveau du sous-réseau ou de l'interface |
| Azure Firewall | Contrôle centralisé des flux réseau et règles prises en charge |
| Application Gateway | Entrée applicative HTTP(S), fonctions WAF selon configuration |
| Azure Bastion | Administration de VM via un accès contrôlé |
| NVA | Appliance réseau virtuelle tierce ou personnalisée |
| Route table | Contrôle du prochain saut pour les destinations concernées |

Ces composants sont complémentaires. Un NSG ne remplace pas un WAF, et un pare-feu réseau n'effectue pas automatiquement toutes les fonctions de protection applicative.

## 4.5 VPN Gateway et ExpressRoute

VPN Gateway fournit une connectivité chiffrée via VPN, souvent sur Internet.

ExpressRoute fournit une connectivité privée via un fournisseur ou un partenaire. Il n'implique pas à lui seul que tous les flux sont chiffrés de bout en bout.

Le choix dépend notamment :

- du besoin de connectivité privée ;
- des performances ;
- du SLA et de la résilience ;
- du nombre de sites ;
- du routage BGP ;
- du coût ;
- des exigences de chiffrement ;
- des régions et services à connecter.

Pour un environnement comportant de nombreux sites et régions, évaluer également Azure Virtual WAN.

## 4.6 Diagnostic du routage

Démarche :

1. identifier la source et la destination ;
2. vérifier les préfixes ;
3. examiner les peerings ;
4. examiner les routes effectives ;
5. vérifier les UDR ;
6. vérifier les routes propagées ;
7. examiner les règles NSG ;
8. contrôler le pare-feu et le routage de retour ;
9. tester avec Network Watcher ;
10. confirmer le résultat avec les journaux disponibles.

Ne pas conclure à un problème NSG uniquement parce qu'une connexion échoue.

## 4.7 Journalisation du trafic

Pour les nouveaux déploiements, privilégier les VNet flow logs et les intégrer à la stratégie d'observabilité.

Les NSG flow logs ne prennent plus en charge la création de nouveaux flux depuis le 30 juin 2025 et sont prévus pour retrait le 30 septembre 2027. Les architectures qui les utilisent encore doivent prévoir leur migration.

Les journaux de flux décrivent les flux réseau, mais ne constituent pas une capture complète du contenu des paquets. Ils doivent être combinés aux journaux du pare-feu, aux métriques et aux diagnostics adaptés.

---

# 5. Sécurité Zero Trust et défense en profondeur

## 5.1 Principes Zero Trust

Zero Trust repose notamment sur trois principes :

1. vérifier explicitement ;
2. appliquer le moindre privilège ;
3. considérer qu'une compromission peut survenir.

Il ne s'agit pas d'installer un produit unique. Il s'agit d'une stratégie de contrôle des identités, des appareils, des applications, des données, du réseau et des opérations.

## 5.2 Défense en profondeur

```text
Identité
   |
   v
Authentification forte
   |
   v
Autorisation minimale
   |
   v
Accès réseau contrôlé
   |
   v
Protection de la ressource
   |
   v
Journalisation et détection
   |
   v
Réponse et récupération
```

Une application privée peut toujours être vulnérable si son identité dispose de trop de privilèges. Un réseau segmenté n'empêche pas une fuite si les données sont exposées par une autorisation trop large.

## 5.3 Identité et accès conditionnel

Les contrôles d'identité doivent être adaptés aux risques et aux licences disponibles.

Selon les besoins, examiner :

- authentification multifacteur ;
- accès conditionnel ;
- authentification résistante au phishing pour les comptes privilégiés ;
- accès privilégié juste-à-temps ;
- comptes d'urgence protégés et surveillés ;
- restriction des applications et appareils ;
- gestion du cycle de vie des identités.

Les paramètres exacts dépendent du tenant et des fonctionnalités de licence disponibles.

## 5.4 Protection des secrets

Ordre de préférence fréquent :

1. identité managée pour les services Azure compatibles ;
2. fédération d'identité pour les pipelines compatibles ;
3. secret ou certificat géré et renouvelé lorsque nécessaire ;
4. clés permanentes uniquement lorsque le service l'exige et que les autres mécanismes ne sont pas disponibles.

Un secret ne doit pas être stocké en clair dans un dépôt Git, une image de conteneur ou un fichier de configuration versionné.

## 5.5 Segmentation des charges de travail

Exemple :

```text
Zone d'entrée
   |
   v
Application
   |
   v
Service métier
   |
   v
Base de données privée
```

Chaque segment doit limiter les communications autorisées. Les règles doivent décrire les flux métier, pas simplement ouvrir des ports « pour que cela fonctionne ».

La segmentation doit aussi prendre en compte les chemins d'administration, les sauvegardes, les services partagés et la supervision.

## 5.6 Sécurité du cycle de vie

Un cycle sécurisé comprend :

- conception des menaces ;
- revue des autorisations ;
- validation de l'IaC ;
- déploiement contrôlé ;
- collecte de journaux ;
- détection ;
- gestion des vulnérabilités ;
- réponse aux incidents ;
- restauration et retour d'expérience.

---

# 6. Identités managées, RBAC et privilèges

## 6.1 Conception des identités applicatives

Une application ne doit pas utiliser un compte administrateur général pour accéder à tous ses services.

```text
Application A
    |
    +--> Identité A
             |
             +--> Lecture sur le conteneur A
             |
             +--> Aucun accès au conteneur B

Application B
    |
    +--> Identité B
             |
             +--> Écriture sur le conteneur B
```

Chaque identité doit correspondre à une responsabilité compréhensible.

Les identités managées affectées par l'utilisateur sont utiles lorsque le cycle de vie de l'identité doit être indépendant de celui des ressources consommatrices. Elles exigent cependant une gouvernance de leur partage et de leurs attributions.

## 6.2 RBAC : évaluer une attribution

Pour chaque rôle, examiner :

- le principal ;
- le rôle ;
- l'étendue ;
- les éventuelles conditions ;
- l'héritage ;
- les autorisations réellement nécessaires ;
- la possibilité de suppression ou d'élévation ;
- le temps de propagation.

L'étendue la plus petite n'est pas toujours le seul critère : la maintenabilité et le cycle de vie doivent également être considérés. Il faut néanmoins éviter les droits larges sans justification.

## 6.3 Exemple de rôle personnalisé

Un rôle personnalisé peut limiter les opérations autorisées, mais il doit être conçu avec prudence.

Avant de le créer :

1. identifier les opérations ARM nécessaires ;
2. distinguer les opérations de lecture, d'écriture et de suppression ;
3. examiner les actions de données ;
4. tester les refus attendus ;
5. vérifier les dépendances ;
6. documenter le propriétaire du rôle.

Ne pas copier une liste d'autorisations sans comprendre les opérations réellement requises par le service.

## 6.4 Gestion des accès privilégiés

Une stratégie mature prévoit :

- séparation des comptes d'administration et d'utilisation courante ;
- MFA ;
- approbation ou justification pour les accès sensibles ;
- durée limitée des privilèges lorsque possible ;
- revue régulière des attributions ;
- surveillance des actions administratives ;
- procédure d'urgence ;
- suppression rapide des accès devenus inutiles.

---

# 7. Infrastructure as Code industrialisée

## 7.1 Architecture de dépôt

```text
azure-platform/
|
+-- infra/
|   +-- main.bicep
|   +-- modules/
|   |   +-- network.bicep
|   |   +-- security.bicep
|   |   +-- monitoring.bicep
|   |   +-- storage.bicep
|   +-- parameters/
|       +-- dev.bicepparam
|       +-- test.bicepparam
|       +-- prod.bicepparam
|
+-- tests/
+-- scripts/
+-- docs/
+-- .gitignore
+-- README.md
```

Les paramètres de production ne doivent pas contenir de secrets en clair. Les données sensibles doivent être injectées par un mécanisme sécurisé adapté au pipeline.

## 7.2 Principes de conception Bicep

Un bon module :

- a une responsabilité claire ;
- possède des paramètres documentés ;
- expose des sorties utiles ;
- limite les valeurs codées en dur ;
- applique des conventions cohérentes ;
- rend explicites les dépendances ;
- évite les secrets ;
- se teste indépendamment ;
- utilise une version d'API prise en charge.

Les modules ne doivent pas devenir de simples couches d'abstraction inutiles. Ils doivent améliorer la réutilisation et la lisibilité.

## 7.3 Exemple de module réseau

Fichier `modules/network.bicep` :

```bicep
targetScope = 'resourceGroup'

@description('Nom du réseau virtuel')
param vnetName string

@description('Région de déploiement')
param location string = resourceGroup().location

@description('Préfixe principal du réseau')
param addressPrefix string

@description('Préfixe du sous-réseau applicatif')
param appSubnetPrefix string

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: appSubnetPrefix
        }
      }
    ]
  }
}

output id string = vnet.id
output name string = vnet.name
```

Le module doit être appelé depuis un modèle parent avec des paramètres validés.

## 7.4 Exemple de modèle parent

Fichier `main.bicep` :

```bicep
targetScope = 'resourceGroup'

param location string = resourceGroup().location
param vnetName string = 'vnet-platform-dev'
param addressPrefix string = '10.60.0.0/16'
param appSubnetPrefix string = '10.60.1.0/24'

module network './modules/network.bicep' = {
  name: 'network-deployment'
  params: {
    vnetName: vnetName
    location: location
    addressPrefix: addressPrefix
    appSubnetPrefix: appSubnetPrefix
  }
}

output deployedVnetId string = network.outputs.id
```

Ce modèle ne constitue qu'un composant réseau de base. Une plateforme de production doit intégrer les contrôles, routes, diagnostics, dépendances et paramètres adaptés.

## 7.5 Pipeline de déploiement

```text
Commit
  |
  v
Revue de code
  |
  v
Compilation Bicep
  |
  v
Validation statique et tests
  |
  v
Authentification fédérée
  |
  v
Validation Azure
  |
  v
What-if
  |
  v
Approbation selon environnement
  |
  v
Déploiement
  |
  v
Tests post-déploiement
  |
  v
Rapport et audit
```

L'authentification fédérée évite de maintenir un secret client permanent lorsque le fournisseur de pipeline et la configuration Azure prennent en charge ce mécanisme.

## 7.6 Séparer validation et déploiement

Exemple de commandes :

```bash
az bicep build --file infra/main.bicep

az deployment group validate \
  --resource-group rg-platform-dev \
  --template-file infra/main.bicep

az deployment group what-if \
  --resource-group rg-platform-dev \
  --template-file infra/main.bicep

az deployment group create \
  --resource-group rg-platform-dev \
  --template-file infra/main.bicep
```

Le compte de déploiement doit disposer des droits nécessaires sur le périmètre cible, sans être automatiquement administrateur global.

## 7.7 Tests et retour arrière

Un pipeline expert doit prévoir :

- validation des paramètres ;
- détection des erreurs de compilation ;
- contrôles de sécurité ;
- comparaison des changements ;
- approbation pour les environnements sensibles ;
- tests de santé après déploiement ;
- journalisation de l'exécution ;
- procédure de retour arrière ;
- contrôle de dérive.

Le retour arrière n'est pas toujours un simple redéploiement de l'ancienne version. Une migration de données ou une suppression de ressource peut être irréversible sans sauvegarde ou stratégie dédiée.

---

# 8. Automatisation avec Azure CLI, Bicep et pipelines

## 8.1 Idempotence

Une opération idempotente peut être répétée sans produire un changement supplémentaire indésirable une fois l'état cible atteint.

Les déploiements déclaratifs facilitent cette approche, mais ne garantissent pas à eux seuls l'idempotence de toutes les opérations externes.

Les scripts doivent :

- vérifier les préconditions ;
- gérer les erreurs ;
- éviter les suppressions implicites ;
- être réexécutables ;
- produire des journaux ;
- signaler clairement leur état.

## 8.2 Script de prévalidation

Exemple Bash :

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${SUBSCRIPTION_ID:?Définir SUBSCRIPTION_ID}"
: "${RESOURCE_GROUP:?Définir RESOURCE_GROUP}"
: "${TEMPLATE_FILE:?Définir TEMPLATE_FILE}"

az account set --subscription "$SUBSCRIPTION_ID"

ACTIVE_SUBSCRIPTION_ID="$(
  az account show --query id --output tsv
)"

if [[ "$ACTIVE_SUBSCRIPTION_ID" != "$SUBSCRIPTION_ID" ]]; then
  echo "Erreur : abonnement actif inattendu." >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Erreur : modèle introuvable." >&2
  exit 1
fi

az bicep build --file "$TEMPLATE_FILE"

az deployment group validate \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE"

az deployment group what-if \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE"

echo "Prévalidation terminée. Déploiement non exécuté."
```

Ce script s'arrête après `what-if`. Il ne réalise pas de déploiement automatique. La décision de déployer doit être prise par une étape explicite du pipeline.

## 8.3 Authentification du pipeline

Ordre de préférence courant :

1. fédération d'identité prise en charge ;
2. identité managée pour les agents compatibles ;
3. autre mécanisme sécurisé approuvé et avec rotation contrôlée.

Éviter les identifiants permanents stockés directement dans les scripts.

L'identité du pipeline doit disposer uniquement des droits nécessaires au déploiement visé.

## 8.4 Dérive de configuration

La dérive correspond à un écart entre l'état attendu et l'état réel.

Causes possibles :

- modification manuelle ;
- script non versionné ;
- changement externe ;
- déploiement partiel ;
- ressource modifiée par un autre système.

Stratégie :

1. versionner les modèles ;
2. identifier les propriétaires ;
3. détecter les changements ;
4. analyser les écarts ;
5. déterminer s'ils sont légitimes ;
6. corriger via un processus contrôlé ;
7. vérifier l'état final.

Un déploiement déclaratif ne doit pas écraser automatiquement des changements manuels sans analyse d'impact.

---

# 9. Observabilité avancée et réponse aux incidents

## 9.1 Les trois piliers

```text
Observabilité
|
+-- Métriques
|   +-- CPU
|   +-- Latence
|   +-- Débit
|
+-- Journaux
|   +-- Événements
|   +-- Erreurs
|   +-- Décisions de sécurité
|
+-- Traces
    +-- Parcours des requêtes
    +-- Dépendances
    +-- Durées des opérations
```

Ces sources sont complémentaires.

Les métriques détectent souvent rapidement une anomalie. Les journaux donnent le contexte des événements. Les traces permettent de suivre une requête entre plusieurs composants instrumentés.

## 9.2 Concevoir des alertes exploitables

Une alerte doit préciser :

- la condition ;
- la durée d'évaluation ;
- la gravité ;
- le destinataire ;
- l'action attendue ;
- la procédure associée ;
- le risque de faux positifs ;
- le coût éventuel de collecte.

Une alerte qui se déclenche constamment sans action possible perd rapidement sa valeur.

## 9.3 Exemple de requête KQL

Pour analyser les événements disponibles dans une table de journaux applicatifs compatible :

```kusto
AppRequests
| where TimeGenerated > ago(1h)
| summarize
    Total = count(),
    Echecs = countif(Success == false)
  by bin(TimeGenerated, 5m)
| order by TimeGenerated desc
```

Cette requête est un exemple de structure analytique. Le nom de la table et les colonnes doivent être adaptés au schéma réel de l'espace de travail.

Autre exemple conceptuel :

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where ActivityStatusValue == "Failure"
| project TimeGenerated,
          Caller,
          OperationNameValue,
          ResourceGroup,
          ActivityStatusValue
| order by TimeGenerated desc
```

Les colonnes réellement disponibles peuvent varier selon la table et la configuration de collecte. Vérifier le schéma avant d'utiliser une requête dans un incident.

## 9.4 Réponse aux incidents

```text
Détection
   |
   v
Qualification
   |
   v
Évaluation de l'impact
   |
   v
Confinement
   |
   v
Éradication
   |
   v
Récupération
   |
   v
Retour d'expérience
```

Un processus de réponse doit préciser :

- qui décide du confinement ;
- quelles preuves conserver ;
- comment limiter l'impact métier ;
- quelles identités révoquer ;
- comment rétablir le service ;
- comment communiquer ;
- comment éviter une récidive.

Les actions de confinement doivent être adaptées à l'incident. Une désactivation générale du réseau peut aggraver l'indisponibilité.

## 9.5 Conservation des journaux

La durée de rétention dépend des besoins d'investigation, des obligations réglementaires, des coûts et des exigences de confidentialité.

Les journaux doivent être protégés contre les accès non autorisés et les suppressions injustifiées. Les données sensibles doivent être limitées au strict nécessaire.

---

# 10. Haute disponibilité, continuité et reprise après sinistre

## 10.1 Définir les objectifs

Le RPO définit la perte de données maximale acceptable.

Le RTO définit le délai cible de rétablissement.

Exemple :

```text
Incident à 14:00
|
+-- RPO de 15 minutes
|   +-- Perte de données cible limitée
|       aux 15 dernières minutes
|
+-- RTO de 2 heures
    +-- Service restauré au plus tard
        à 16:00 selon l'objectif retenu
```

Cet exemple exprime des objectifs métier, pas une garantie fournie automatiquement par Azure.

## 10.2 Dépendances de reprise

Une application peut nécessiter :

- réseau ;
- DNS ;
- identités ;
- secrets ;
- certificats ;
- base de données ;
- stockage ;
- images et artefacts ;
- clés de chiffrement ;
- services tiers ;
- pipelines de déploiement.

La restauration du calcul sans les dépendances ne suffit pas à rétablir le service.

## 10.3 Stratégies de reprise

| Stratégie | Principe | Compromis |
|---|---|---|
| Sauvegarde et restauration | Reconstruire après incident | Coût réduit, RTO potentiellement long |
| Pilot light | Services critiques minimaux dans la région secondaire | Préparation nécessaire |
| Warm standby | Environnement secondaire prêt à prendre le relais | Coût permanent plus élevé |
| Actif-actif | Plusieurs régions servent le trafic | Complexité et coûts importants |

Le choix doit découler des objectifs métier et des capacités réelles des services.

## 10.4 Exercices de bascule

Un exercice sérieux doit :

1. établir les préconditions ;
2. définir les critères de succès ;
3. prévenir les équipes ;
4. isoler ou simuler la panne ;
5. exécuter la bascule ;
6. vérifier l'intégrité des données ;
7. tester les parcours utilisateur ;
8. mesurer le RTO ;
9. analyser la perte de données ;
10. documenter les écarts ;
11. préparer le retour à la normale.

La bascule ne doit pas être considérée comme réussie simplement parce que les VM de secours sont démarrées.

---

# 11. Stockage, données et sécurité des accès privés

## 11.1 Private Endpoint et DNS

Un Private Endpoint associe une interface privée à un service Azure compatible.

La résolution DNS doit conduire les clients concernés vers l'adresse privée attendue.

```text
Client dans le VNet
        |
        v
Résolution DNS privée
        |
        v
Nom du service
        |
        v
Adresse privée du Private Endpoint
        |
        v
Service Azure
```

La zone DNS privée, les liens de VNet, la résolution hybride et les paramètres du service cible doivent être cohérents.

Un Private Endpoint ne désactive pas automatiquement toutes les voies d'accès public. La configuration du service doit être examinée séparément.

## 11.2 Défense des données

Contrôles à évaluer :

- identité et RBAC ;
- restriction réseau ;
- chiffrement au repos ;
- chiffrement en transit ;
- protection contre la suppression ;
- rétention ;
- sauvegarde ;
- journalisation ;
- classification ;
- gestion des clés.

Le choix des contrôles doit tenir compte de la sensibilité des données et des scénarios de menace.

## 11.3 Cycle de vie des données

```text
Création
   |
   v
Classification
   |
   v
Stockage et accès
   |
   v
Surveillance
   |
   v
Rétention
   |
   v
Archivage ou suppression
```

Une stratégie de conservation doit définir le propriétaire des données, la durée, les conditions de suppression et les exceptions légales.

---

# 12. FinOps et optimisation des plateformes

## 12.1 Les coûts architecturaux

Le coût d'une plateforme comprend plus que les machines virtuelles :

- calcul ;
- stockage ;
- transactions ;
- transfert de données ;
- pare-feu ;
- passerelles ;
- supervision ;
- sauvegarde ;
- réplication ;
- services managés ;
- support et licences.

Les architectures multi-régions, les environnements redondants et les journaux détaillés augmentent souvent les coûts, mais peuvent être justifiés par les exigences de disponibilité et de sécurité.

## 12.2 Optimisation mesurable

Pour chaque action, mesurer :

- coût avant ;
- coût après ;
- impact sur les performances ;
- impact sur la disponibilité ;
- impact sur la sécurité ;
- effort d'exploitation ;
- risque introduit.

Une réduction de coût qui supprime la seule sauvegarde restaurable n'est pas une optimisation acceptable.

## 12.3 Gouvernance financière

Mettre en place :

- balises de coût ;
- budgets ;
- alertes de consommation ;
- revues périodiques ;
- propriétaires par ressource ;
- détection des ressources inutilisées ;
- choix de SKU adaptés ;
- contrôle des données et journaux ;
- processus d'exception.

Les budgets et alertes aident à détecter les dérives, mais ne garantissent pas à eux seuls un plafond strict de dépense.

---

# 13. Travaux pratiques guidés

## TP 1 — Concevoir un réseau hub-and-spoke

### Objectif

Concevoir une architecture à trois VNets avec des plages sans chevauchement, un hub et deux spokes.

### Adressage

- Hub : `10.100.0.0/16`
- Spoke-App : `10.110.0.0/16`
- Spoke-Data : `10.120.0.0/16`

### Étapes

1. Vérifier les plages et les routes existantes.
2. Créer les trois VNets dans un groupe de ressources de laboratoire.
3. Créer les peerings dans les deux directions.
4. Vérifier l'état des peerings.
5. Documenter les communications autorisées.
6. Vérifier que le peering seul ne fournit pas de transit entre les spokes.
7. Concevoir une solution de transit via une appliance ou un service adapté.
8. Évaluer les routes de retour et les risques de contournement.

### Critères de réussite

- plages non chevauchantes ;
- peerings établis ;
- flux décrits ;
- non-transitivité correctement expliquée ;
- stratégie de transit documentée.

## TP 2 — Sécuriser une identité applicative

### Objectif

Permettre à une charge de travail d'accéder uniquement à un conteneur de données nécessaire.

### Étapes

1. Créer un compte de stockage de laboratoire.
2. Créer un conteneur privé.
3. Activer une identité managée sur une ressource compatible.
4. Identifier le principal de cette identité.
5. Attribuer le rôle de données minimal nécessaire.
6. Tester l'accès depuis la charge de travail.
7. Tester un accès interdit à une autre ressource.
8. Examiner les journaux et les autorisations.
9. Documenter les limites du rôle et le périmètre.

### Critères de réussite

L'identité accède aux données nécessaires, sans disposer d'un rôle global inutile. Les refus attendus sont également testés.

## TP 3 — Construire un pipeline IaC

### Objectif

Industrialiser le déploiement d'un réseau à l'aide de Git, Bicep et Azure CLI.

### Étapes

1. Créer un dépôt Git.
2. Ajouter le modèle Bicep et ses paramètres.
3. Compiler le modèle.
4. Exécuter les validations.
5. Exécuter `what-if`.
6. Examiner les changements.
7. Déployer dans un environnement de développement.
8. Exécuter des tests de santé.
9. Enregistrer le résultat.
10. Préparer une promotion contrôlée vers un environnement supérieur.

### Critères de réussite

Le pipeline distingue la validation du déploiement et ne contient aucun secret permanent en clair.

## TP 4 — Construire un plan de reprise

### Objectif

Définir une stratégie de continuité pour une application composée de calcul, données, DNS et secrets.

### Étapes

1. Recenser les dépendances.
2. Définir RPO et RTO.
3. Choisir une stratégie de sauvegarde et de réplication.
4. Identifier les dépendances régionales.
5. Décrire la bascule.
6. Décrire la restauration des données.
7. Définir les tests applicatifs.
8. Mesurer les résultats d'un exercice.
9. Documenter les écarts.
10. Définir une action corrective.

### Critères de réussite

La stratégie couvre l'application et ses dépendances. Elle distingue les objectifs théoriques des résultats mesurés.

---

# 14. Exercices corrigés

## Exercice 1 — Transit réseau

Deux spokes sont peerés avec le hub. Les machines des deux spokes ne communiquent pas entre elles.

### Correction

C'est le comportement attendu : le peering n'est pas transitif. Il faut établir un chemin de transit pris en charge, configurer le routage et vérifier le retour du trafic ainsi que les règles de filtrage.

## Exercice 2 — Défense en profondeur

Une VM n'a pas d'adresse IP publique, mais son identité peut lire tous les conteneurs d'un compte de stockage.

Le système est-il correctement sécurisé ?

### Correction

Pas nécessairement. L'absence d'IP publique réduit une surface d'exposition réseau, mais l'identité possède un privilège excessif. Il faut réduire le rôle et son étendue, puis tester les accès autorisés et refusés.

## Exercice 3 — Déploiement Bicep

Un pipeline peut créer des ressources mais échoue lorsqu'il attribue un rôle RBAC.

### Correction

Les droits de déploiement des ressources ne comprennent pas nécessairement les autorisations d'attribution des rôles. Il faut examiner l'identité du pipeline, le périmètre et les opérations de rôle requises. Ne pas attribuer un rôle administrateur global sans justification.

## Exercice 4 — DNS privé

Une application ne parvient plus à joindre un service après l'ajout d'un Private Endpoint.

### Correction

Examiner la résolution DNS depuis la charge de travail, les zones privées, les liens des VNets, les règles de transfert DNS et la configuration du service. Comparer l'adresse résolue à l'adresse privée attendue. Vérifier ensuite le routage et les règles réseau.

## Exercice 5 — RPO et RTO

Une sauvegarde quotidienne est effectuée, mais l'entreprise exige un RPO de 15 minutes.

### Correction

Une sauvegarde quotidienne ne garantit pas un RPO de 15 minutes. Il faut une solution de protection des données dont les caractéristiques, la fréquence et la restauration permettent de respecter l'objectif, puis valider le résultat par des tests.

## Exercice 6 — Coûts

Une équipe veut réduire les coûts en supprimant les journaux de sécurité.

### Correction

Il faut d'abord déterminer les exigences d'audit, de détection et de rétention. L'optimisation doit porter sur la collecte utile, les niveaux de détail, les destinations et les durées autorisées, sans supprimer les preuves nécessaires.

## Exercice 7 — Dérive

Un administrateur modifie manuellement une règle NSG en production, mais le dépôt IaC ne change pas.

### Correction

La configuration réelle diverge de l'état versionné. Il faut examiner le changement, décider s'il est légitime, mettre à jour le modèle ou rétablir l'état attendu, puis contrôler le résultat via un processus auditable.

## Exercice 8 — Multi-région

Deux régions hébergent l'application, mais le coffre de secrets et le DNS dépendent d'une seule région.

### Correction

La résilience du calcul ne garantit pas la reprise complète. Les secrets, les identités, le DNS, les données et les services de gestion doivent être inclus dans l'analyse des dépendances et dans les tests de bascule.

---

# 15. Défi final expert — Architecture d'entreprise (100 points)

## Scénario

Une entreprise exploite plusieurs applications Azure. Elle doit concevoir une plateforme comportant :

- un réseau central partagé ;
- des réseaux isolés pour les applications et les données ;
- une connectivité hybride ;
- une gouvernance centralisée ;
- des identités applicatives à privilèges limités ;
- des déploiements reproductibles ;
- une supervision exploitable ;
- une stratégie de continuité et de reprise ;
- une maîtrise des coûts.

Le dossier doit expliquer les décisions et les compromis, pas simplement lister des services.

## Partie A — Architecture et réseau (25 points)

1. Proposer une organisation multi-abonnements et justifier les frontières. (5 points)
2. Décrire le hub et deux spokes, avec des plages non chevauchantes. (5 points)
3. Expliquer la non-transitivité du peering et le transit contrôlé. (5 points)
4. Comparer VPN Gateway, ExpressRoute et Azure Virtual WAN pour le scénario. (5 points)
5. Décrire les routes, les règles de filtrage et le diagnostic. (5 points)

## Partie B — Sécurité et gouvernance (20 points)

1. Définir une stratégie Zero Trust. (5 points)
2. Décrire la gouvernance via Management Groups, Azure Policy et RBAC. (5 points)
3. Concevoir une stratégie d'identités managées et de secrets. (5 points)
4. Définir les mesures de surveillance des accès privilégiés. (5 points)

## Partie C — Infrastructure as Code (20 points)

1. Proposer une structure de dépôt Bicep modulaire. (5 points)
2. Fournir un module réseau paramétrable. (5 points)
3. Décrire les étapes de validation, `what-if`, approbation et déploiement. (5 points)
4. Décrire l'authentification du pipeline, les tests et la gestion de la dérive. (5 points)

## Partie D — Observabilité et continuité (20 points)

1. Définir une stratégie de métriques, journaux, traces et alertes. (5 points)
2. Décrire une démarche de réponse aux incidents. (5 points)
3. Définir RPO, RTO, sauvegarde et reprise multi-région. (5 points)
4. Expliquer comment les tests de reprise prouvent les objectifs. (5 points)

## Partie E — Arbitrage de production (15 points)

Une équipe demande de supprimer le filtrage central pour réduire la latence et le coût. Elle demande aussi des privilèges administratifs permanents afin d'accélérer les déploiements.

1. Analyser les risques réseau et les risques d'identité. (5 points)
2. Proposer des solutions alternatives et des compromis mesurables. (5 points)
3. Définir les validations et indicateurs avant toute décision. (5 points)

---

# 16. Correction complète du défi final

## 16.1 Partie A — Architecture et réseau (25 points)

### Organisation

Une proposition est de séparer les abonnements de connectivité, de gestion et des applications. Les applications peuvent ensuite être regroupées selon leur cycle de vie, leur criticité et leurs exigences de sécurité.

Cette séparation limite certains périmètres d'administration et facilite la répartition des coûts. Elle augmente néanmoins le nombre de ressources et les besoins d'automatisation.

### Plan d'adressage

```text
Hub       : 10.100.0.0/16
Spoke-App : 10.110.0.0/16
Spoke-Data: 10.120.0.0/16
```

Ces plages ne se chevauchent pas.

### Transit

Les peerings du hub avec les spokes ne fournissent pas de transit automatique entre ces derniers. Un transit doit être explicitement conçu, avec un mécanisme de routage et de contrôle pris en charge.

Le trafic entre spokes peut être dirigé vers Azure Firewall ou une appliance réseau selon les exigences. Les routes effectives et les chemins retour doivent être validés.

### Connectivité hybride

- **VPN Gateway :** adapté à de nombreux scénarios de connectivité chiffrée via Internet.
- **ExpressRoute :** adapté lorsque la connectivité privée via un partenaire et les caractéristiques de service répondent aux exigences.
- **Azure Virtual WAN :** à évaluer pour une architecture de connectivité étendue comportant de nombreux sites, réseaux ou régions.

Le choix final nécessite des informations sur la bande passante, la latence, les exigences de chiffrement, les régions, le SLA et le budget.

### Diagnostic

La procédure doit examiner les préfixes, les peerings, les routes, les NSG, le pare-feu, les chemins de retour, DNS et les journaux. Elle doit éviter les changements globaux non justifiés.

## 16.2 Partie B — Sécurité et gouvernance (20 points)

### Zero Trust

Vérifier explicitement les identités et les conditions d'accès, appliquer le moindre privilège et supposer qu'une compromission reste possible.

### Gouvernance

Les Management Groups organisent les abonnements. Azure Policy évalue ou impose les configurations prises en charge. RBAC attribue les droits d'administration sur les périmètres.

Les politiques doivent être testées avant généralisation, et les exceptions doivent être justifiées.

### Identités

Les charges de travail doivent utiliser des identités managées ou une fédération lorsqu'elles sont compatibles. Les rôles doivent être limités aux ressources et actions nécessaires.

Les secrets restants doivent être conservés et renouvelés par un mécanisme sécurisé. Les journaux d'accès privilégiés doivent permettre une enquête.

## 16.3 Partie C — Infrastructure as Code (20 points)

### Organisation

```text
infra/
├── main.bicep
├── modules/
│   ├── network.bicep
│   ├── security.bicep
│   └── monitoring.bicep
└── parameters/
    ├── dev.bicepparam
    └── prod.bicepparam
```

### Module réseau de référence

```bicep
targetScope = 'resourceGroup'

param vnetName string
param location string = resourceGroup().location
param addressPrefix string
param appSubnetPrefix string

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: appSubnetPrefix
        }
      }
    ]
  }
}

output id string = vnet.id
```

Le module doit être complété selon les besoins de production et validé avec les versions d'API prises en charge.

### Pipeline

Le pipeline compile et valide les modèles, exécute `what-if`, demande une approbation adaptée au risque, déploie, puis lance des tests post-déploiement.

L'identité de déploiement utilise une fédération prise en charge lorsque possible et ne reçoit que les droits nécessaires.

La dérive est détectée et analysée avant correction. Le retour arrière tient compte des changements de données et des opérations irréversibles.

## 16.4 Partie D — Observabilité et continuité (20 points)

### Observabilité

La stratégie combine les métriques pour les seuils et tendances, les journaux pour l'analyse des événements, les traces pour les dépendances applicatives et des alertes avec des procédures opérationnelles.

La collecte doit être suffisamment détaillée pour les enquêtes sans entraîner un coût ou une exposition excessive des données.

### Réponse aux incidents

Le processus comprend détection, qualification, confinement, éradication, récupération et retour d'expérience. Les décisions de confinement sont prises en fonction du risque et de l'impact métier.

### Continuité

RPO et RTO sont définis avec les responsables métier. La solution de sauvegarde ou de réplication doit correspondre à ces objectifs.

La stratégie couvre l'application, les données, DNS, identités, secrets, clés et dépendances de plateforme.

### Validation

Des exercices mesurent réellement le délai de bascule et la perte de données. Les résultats sont comparés aux objectifs et les écarts font l'objet d'actions correctives.

## 16.5 Partie E — Arbitrage de production (15 points)

### Analyse des risques

Supprimer le filtrage central peut réduire certains coûts ou délais, mais aussi diminuer la visibilité, l'inspection et la maîtrise des flux. Les privilèges administratifs permanents augmentent l'impact potentiel d'un compte compromis et rendent les actions excessives plus faciles.

### Solutions alternatives

- mesurer la latence et identifier les flux qui nécessitent réellement un chemin direct ;
- envisager un peering direct limité lorsque le contournement de l'inspection est acceptable ;
- conserver une segmentation locale et des contrôles d'identité ;
- automatiser les déploiements avec une identité dédiée ;
- limiter la durée et le périmètre des privilèges humains ;
- séparer les rôles de déploiement, d'exploitation et d'approbation ;
- optimiser les règles et les ressources réseau plutôt que supprimer globalement les contrôles.

### Validation

Avant toute modification :

1. mesurer la latence et les coûts actuels ;
2. établir les flux et les risques ;
3. tester dans un environnement non productif ;
4. vérifier la sécurité et les routes de retour ;
5. définir des critères de réussite ;
6. préparer un retour arrière ;
7. obtenir l'approbation appropriée ;
8. mesurer les résultats après changement.

La bonne décision est celle qui satisfait les objectifs métier avec un risque et un coût explicitement acceptés.

---

# 17. Références et checklist de production

## Références officielles

- Azure Architecture Center : https://learn.microsoft.com/azure/architecture/
- Cloud Adoption Framework : https://learn.microsoft.com/azure/cloud-adoption-framework/
- Azure Landing Zones : https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/
- Hub-and-spoke : https://learn.microsoft.com/azure/networking/design-guide/hub-spoke
- Azure Virtual WAN : https://learn.microsoft.com/azure/virtual-wan/
- Azure Policy : https://learn.microsoft.com/azure/governance/policy/overview
- Azure RBAC : https://learn.microsoft.com/azure/role-based-access-control/overview
- Identités managées : https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview
- Bicep : https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview
- Azure Monitor : https://learn.microsoft.com/azure/azure-monitor/
- VNet flow logs : https://learn.microsoft.com/azure/network-watcher/vnet-flow-logs-overview
- Azure Well-Architected Framework : https://learn.microsoft.com/azure/well-architected/

## Checklist avant mise en production

### Architecture
- [ ] Les frontières d'abonnements sont justifiées.
- [ ] Les dépendances partagées sont documentées.
- [ ] Les décisions d'architecture sont versionnées.
- [ ] Les objectifs de disponibilité sont définis.

### Réseau
- [ ] Les préfixes ne se chevauchent pas.
- [ ] Le transit est explicitement conçu.
- [ ] Les routes de retour sont vérifiées.
- [ ] Les accès publics sont justifiés.
- [ ] DNS privé et hybride sont testés.
- [ ] Les journaux de flux adaptés sont configurés.

### Sécurité
- [ ] Les identités disposent du moindre privilège.
- [ ] Les accès privilégiés sont contrôlés.
- [ ] Les secrets ne sont pas versionnés en clair.
- [ ] Les accès aux données sont testés.
- [ ] Les exceptions de gouvernance sont suivies.

### Automatisation
- [ ] Les modèles sont versionnés.
- [ ] Les déploiements sont validés.
- [ ] `what-if` est examiné.
- [ ] Les identités des pipelines sont limitées.
- [ ] La dérive est détectée.
- [ ] Les retours arrière sont documentés.

### Exploitation
- [ ] Les métriques et journaux sont disponibles.
- [ ] Les alertes possèdent un responsable.
- [ ] Les procédures d'incident sont testées.
- [ ] Les sauvegardes sont restaurables.
- [ ] Les exercices de reprise sont mesurés.
- [ ] Les coûts sont surveillés.

---

**Fin du cours Azure expert.**

La maîtrise experte se démontre par la capacité à justifier les décisions, anticiper les défaillances, limiter les privilèges, automatiser les changements et prouver par des tests que les objectifs de sécurité et de continuité sont atteints.
