# Architecture Zero Trust — Niveau expert
## Ingénierie des politiques, identités de charges de travail, multi-cloud et validation continue

> **Suite pédagogique :** `zero-trust-debutant.md` → `zero-trust-intermediaire.md` → `zero-trust-expert.md`
>
> **Public :** architectes sécurité, ingénieurs plateforme, spécialistes IAM, réseau, cloud, DevSecOps et réponse aux incidents.
>
> **Objectif :** concevoir, tester, déployer et exploiter une architecture Zero Trust à grande échelle, avec des politiques explicables, des identités vérifiables, une application cohérente des décisions et une résilience mesurée.
>
> **Pré-requis :** maîtrise des notions abordées aux niveaux débutant et intermédiaire : identité, MFA, segmentation, ZTNA, flux de service, journalisation, cycle de vie des sessions et gestion des exceptions.
>
> **Convention de lecture :** les schémas de ce document sont exclusivement textuels. Les blocs de configuration sont explicitement identifiés comme exemples, pseudo-code ou configurations propres à une technologie. Les valeurs de démonstration ne doivent pas être copiées en production sans adaptation.


## 1. Ce qui distingue le niveau expert

Le niveau expert ne consiste pas à installer davantage d'outils. Il consiste à faire fonctionner les contrôles comme un système cohérent, à rendre les décisions testables, à maîtriser les identités non humaines et à prouver que les mécanismes résistent aux erreurs de configuration et aux pannes.

L'architecture doit répondre aux questions suivantes :

- Une requête peut-elle atteindre la ressource sans passer par le point d'application prévu ?
- Quelle identité cryptographique représente l'utilisateur ou la charge de travail ?
- Quelle politique a autorisé l'opération, sur la base de quelles données ?
- Comment prouver qu'une politique refuse les scénarios interdits ?
- Que se passe-t-il lorsqu'un fournisseur d'identité, un moteur de politique, un proxy ou un collecteur est indisponible ?
- Comment révoquer un accès sans attendre la fin d'une longue session ?
- Comment éviter qu'un changement de politique réduise accidentellement le niveau de sécurité ?
- Comment déployer une modification sans interrompre une application critique ?
- Comment mesurer la couverture réelle plutôt que le nombre de produits achetés ?

### Compétences cibles

À l'issue du cours, l'apprenant devrait pouvoir :

1. produire une architecture logique Zero Trust pour un environnement hybride et multi-cloud ;
2. définir des identités de charges de travail avec un cycle de vie maîtrisé ;
3. séparer authentification, autorisation, attestation et chiffrement ;
4. concevoir des politiques indépendantes du fournisseur quand c'est possible ;
5. tester les politiques dans une chaîne CI/CD et traiter les changements comme du code ;
6. analyser les risques de contournement, de privilèges excessifs et de panne ;
7. définir des objectifs de détection, de révocation et de reprise ;
8. conduire un exercice de validation offensive défensive autorisé, puis documenter les résultats ;
9. présenter les compromis, les risques résiduels et les preuves de contrôle.

### Trajectoire de maîtrise

```text
DÉBUTANT
  Comprendre les principes et protéger une application
       |
       v
INTERMÉDIAIRE
  Cartographier les flux, définir les politiques et piloter les contrôles
       |
       v
EXPERT
  Industrialiser les identités et politiques, automatiser les tests,
  vérifier les chemins de contournement et prouver la résilience
       |
       v
AMÉLIORATION CONTINUE
  Mesurer la couverture, corriger la dérive et réévaluer les risques
```


## 2. Référentiel d'architecture

Les références Zero Trust donnent des principes et modèles, mais ne remplacent pas le modèle de menace de l'organisation. Le NIST SP 800-207 décrit notamment une architecture logique basée sur la politique et l'application des décisions. Le NIST SP 800-207A traite plus spécifiquement le contrôle d'accès des applications cloud-native dans des environnements multi-cloud. Le modèle de maturité CISA permet de structurer la progression organisationnelle.

### 2.1 Architecture logique

```text
                         SOURCES DE CONTEXTE
      +-------------------+-------------------+-------------------+
      | Identité humaine  | Identité machine | Posture / risque  |
      | groupes, rôle     | workload, certif.| EDR, conformité   |
      +---------+---------+---------+---------+---------+---------+
                |                   |                   |
                +-------------------+-------------------+
                                    |
                                    v
                        +------------------------+
                        | MOTEUR DE POLITIQUE    |
                        | évaluation / décision  |
                        +-----------+------------+
                                    |
                         décision + contexte
                                    |
                                    v
                        +------------------------+
                        | POINT D'APPLICATION    |
                        | proxy, gateway, agent, |
                        | service, pare-feu      |
                        +-----------+------------+
                                    |
                                    v
                        +------------------------+
                        | RESSOURCE PROTÉGÉE     |
                        | API, application, DB,  |
                        | cluster, plan admin    |
                        +-----------+------------+
                                    |
                                    v
                        +------------------------+
                        | TÉLÉMÉTRIE / AUDIT     |
                        | décision, flux, traces |
                        +------------------------+
```

Les fonctions logiques peuvent être distribuées. Un fournisseur d'identité ne remplace pas nécessairement le moteur d'autorisation de chaque application ; un proxy ne remplace pas les contrôles de l'origine ; un certificat de service n'accorde pas automatiquement le droit d'exécuter toutes les opérations.

### 2.2 Invariants de conception

Un **invariant** est une propriété de sécurité qui doit rester vraie même lorsque l'architecture évolue.

Exemples :

- aucune ressource critique n'est accessible depuis un chemin non documenté ;
- toute opération administrative exige une identité et un rôle administrateur dédiés ;
- une identité de service ne peut accéder qu'aux API, opérations et données nécessaires ;
- chaque décision critique peut être corrélée à un événement d'audit ;
- une panne du moteur de politique ne donne pas silencieusement des privilèges plus larges ;
- aucune modification de politique sensible n'est déployée sans tests et procédure de retour arrière ;
- les secrets de longue durée sont évités ou placés sous une gestion explicite ;
- les exceptions ont un propriétaire, une raison, un périmètre et une date de révision.

### 2.3 Construire un modèle de menace

Pour chaque ressource importante, identifier au minimum :

| Menace | Exemple | Contrôle à tester |
|---|---|---|
| Usurpation d'identité | Jeton volé ou compte détourné | Validation du jeton, MFA, révocation |
| Compromission d'appareil | Poste géré mais contrôlé par un attaquant | Signal de posture, segmentation, accès limité |
| Mouvement latéral | Service web appelle une base non nécessaire | Politique service-à-service |
| Élévation de privilège | Compte d'application devient administrateur | Séparation des rôles, tests négatifs |
| Contournement du PEP | Connexion directe à l'origine de l'application | Test d'exposition directe |
| Dérive de configuration | Une règle permissive est ajoutée | Revue de code et tests de politique |
| Panne de dépendance | IdP, DNS, proxy ou moteur indisponible | Test de résilience et comportement documenté |
| Abus d'identité machine | Clé API copiée dans un dépôt | Rotation, identité courte durée, détection |
| Fuite de données d'audit | Jetons complets écrits dans les logs | Filtrage des secrets et contrôles d'accès |
| Usage abusif d'une exception | Règle temporaire jamais retirée | Expiration, propriétaire, alerte de revue |

Ne pas se contenter d'une liste générique. Pour chaque menace, documenter un scénario, le prérequis de l'attaque, l'impact, le contrôle préventif, le contrôle détectif, la preuve attendue et le risque résiduel.


## 3. Architecture multi-cloud et environnements hybrides

Les ressources peuvent être réparties entre un datacenter, plusieurs fournisseurs cloud, des services SaaS, des clusters Kubernetes et des équipements sur site. L'architecture doit harmoniser les principes sans supposer que les mécanismes techniques sont identiques partout.

### 3.1 Vue logique

```text
                        PLAN DE GOUVERNANCE
                 +-------------------------------+
                 | Catalogue des politiques      |
                 | Référentiel des identités     |
                 | Gestion des exceptions        |
                 | CI/CD, preuves, audit         |
                 +---------------+---------------+
                                 |
                  décisions, standards, contrôle
                                 |
      +--------------------------+---------------------------+
      |                          |                           |
      v                          v                           v
+-------------+           +-------------+             +-------------+
| Datacenter  |           | Cloud A     |             | Cloud B     |
| legacy, VM  |           | VPC, K8s    |             | PaaS, SaaS  |
+------+------+           +------+------+             +------+------+
       |                         |                           |
       +-------------------------+---------------------------+
                                 |
                   identités et flux vérifiés
                                 |
                                 v
                     [Journalisation centralisée]
```

Un « plan de gouvernance » n'est pas nécessairement un serveur unique. Il peut être composé d'un dépôt de politiques, de pipelines, de catalogues et de contrôles de conformité. Il faut éviter qu'une panne de gouvernance bloque toutes les opérations normales ou qu'une compromission de ce plan puisse publier silencieusement une politique permissive.

### 3.2 Principes de cohérence

1. Définir un vocabulaire commun : sujet, ressource, action, environnement, sensibilité, propriétaire.
2. Définir des standards minimaux, puis adapter les implémentations à chaque plateforme.
3. Utiliser des identités fédérées et des identités de service à courte durée de vie lorsqu'elles sont prises en charge.
4. Prévoir un contrôle explicite des flux entre environnements.
5. Ne pas considérer qu'un peering réseau ou un lien privé donne une autorisation applicative.
6. Standardiser les événements à collecter et les identifiants de corrélation.
7. Tester les chemins alternatifs, notamment interfaces publiques, endpoints de secours et accès d'administration.
8. Séparer les environnements de production, de test et de laboratoire, y compris dans les domaines de confiance lorsque le risque le justifie.

### 3.3 Exemples de zones de confiance

```text
TRUST DOMAIN / ENVIRONNEMENT PRODUCTION
  - charges de travail de production
  - identités de production
  - certificats et politiques de production

TRUST DOMAIN / ENVIRONNEMENT NON-PRODUCTION
  - tests, préproduction et intégration
  - jeux de données non sensibles ou masqués
  - autorisations distinctes de la production

ENVIRONNEMENT D'ADMINISTRATION
  - postes d'administration dédiés
  - comptes privilégiés distincts
  - bastions et journaux renforcés

FOURNISSEURS EXTERNES
  - accès limités à un service ou une opération
  - identités et durées explicitement définies
  - expiration, surveillance et retrait des accès
```

Les domaines de confiance peuvent être séparés logiquement ou techniquement selon les besoins. La séparation n'est efficace que si les politiques et les clés de confiance ne recréent pas un accès global entre eux.


## 4. Identité de charge de travail : SPIFFE et SPIRE

Les comptes de service, certificats et clés API ont souvent une durée de vie plus longue que nécessaire. Dans une infrastructure dynamique, une identité liée uniquement à une adresse IP ou à un nom de serveur vieillit mal. SPIFFE fournit une manière standardisée de représenter des identités de charges de travail ; SPIRE est une implémentation qui effectue l'attestation et l'émission d'identités selon des conditions définies.

### 4.1 Concepts essentiels

- **SPIFFE ID :** identifiant URI d'une charge de travail, par exemple `spiffe://prod.exemple.internal/ns/paiement/sa/api`.
- **Trust domain :** domaine qui délimite une racine de confiance.
- **SVID :** document d'identité vérifiable d'une charge de travail, sous forme X.509 ou JWT selon le cas.
- **Attestation du nœud :** vérification de l'environnement ou de la machine qui héberge l'agent.
- **Attestation de workload :** vérification des propriétés de la charge de travail qui demande une identité.
- **Workload API :** interface par laquelle la charge de travail récupère les éléments d'identité autorisés.
- **Rotation :** renouvellement régulier des documents d'identité et des clés associées.

Un SVID prouve une identité dans un domaine de confiance selon la chaîne et les règles de validation ; il ne suffit pas à donner une autorisation. La politique doit encore décider si cette identité peut appeler la ressource et l'opération demandées.

### 4.2 Parcours conceptuel d'émission

```text
+--------------------+            +--------------------+
| SPIRE Server       |            | SPIRE Agent        |
| autorité / registre|            | sur le nœud        |
+---------+----------+            +----------+---------+
          ^                                  ^
          | attestation du nœud              | demande d'identité
          |                                  |
          +----------------------------------+
                                             |
                                             v
                                   +--------------------+
                                   | Charge de travail  |
                                   | demande un SVID    |
                                   +---------+----------+
                                             |
                                             v
                                   +--------------------+
                                   | Identité remise    |
                                   | selon sélecteurs   |
                                   +---------+----------+
                                             |
                                             v
                                   Authentification du
                                   service destinataire
```

SPIRE associe des identités à des sélecteurs et à des conditions d'attestation. Une entrée de registre trop large peut accorder la même identité à des workloads non prévus. Les sélecteurs et les privilèges de gestion du registre doivent donc être traités comme des objets de sécurité critiques.

### 4.3 Cycle de vie cible

```text
DÉPLOIEMENT
    |
    v
Attestation du nœud
    |
    v
Attestation du workload
    |
    v
Émission d'une identité courte durée
    |
    v
Authentification mutuelle / usage autorisé
    |
    v
Rotation automatique avant expiration
    |
    +---- workload supprimé / identité révoquée ----> retrait
```

### 4.4 Identité X.509 ou JWT-SVID

| Caractéristique | X.509-SVID | JWT-SVID |
|---|---|---|
| Usage typique | Authentification TLS mutuelle | Cas où un jeton est plus approprié, notamment à travers certains intermédiaires |
| Preuve | Certificat et clé privée associée | Jeton signé |
| Risque spécifique | Mauvaise validation des certificats ou du trust bundle | Rejeu du jeton s'il est intercepté et encore valide |
| Contrôles | chaîne, SAN, période, identité attendue, rotation | signature, émetteur, audience, expiration, `iat` si exigé, protection contre le rejeu adaptée |
| Choix | À privilégier pour les connexions service-à-service lorsque possible | À employer lorsque le modèle d'intégration le justifie |

Ne pas traiter JWT-SVID comme un simple jeton d'utilisateur OpenID Connect. Respecter la sémantique et les règles de validation propres à l'identité de workload.

### 4.5 Laboratoire conceptuel SPIFFE/SPIRE

Le laboratoire doit être effectué dans un cluster ou une VM de test, jamais directement sur un environnement critique.

**Objectifs :**
1. créer un domaine de confiance de laboratoire distinct ;
2. inscrire une identité pour un service `catalogue-api` ;
3. attribuer à `catalogue-api` uniquement le droit d'appeler `catalogue-db-proxy` ;
4. faire échouer l'attestation d'un workload dont les sélecteurs ne correspondent pas ;
5. observer l'émission, le renouvellement et la disparition de l'identité ;
6. vérifier que l'identité de développement ne peut pas s'authentifier comme service de production.

**Contrôles de réussite :**
- l'identité émise correspond au workload attendu ;
- un autre workload ne peut pas récupérer cette identité ;
- les certificats sont renouvelés avant expiration ;
- le service destinataire vérifie l'identité du pair et applique une autorisation ;
- l'arrêt du workload supprime ou rend inutilisable l'accès selon les mécanismes prévus.


## 5. Authentification, autorisation, attestation et chiffrement

Ces fonctions sont liées, mais elles ne sont pas interchangeables.

| Fonction | Question | Exemple de mécanisme |
|---|---|---|
| Authentification | Qui présente la demande ? | SSO, certificat client, identité machine |
| Attestation | Sur quelles preuves l'identité ou l'environnement est-il établi ? | Propriétés du nœud, workload ou appareil |
| Autorisation | Cette identité peut-elle faire cette action sur cette ressource ? | RBAC, ABAC, politique de l'application |
| Confidentialité / intégrité | Les données du canal sont-elles protégées ? | TLS, mTLS, chiffrement de stockage |
| Audit | Peut-on expliquer qui a fait quoi et avec quelle décision ? | Journaux corrélés, traces et événements |
| Détection | Peut-on identifier un comportement anormal ? | Règles, analyses, corrélation et réponse |

Un canal mTLS peut être chiffré et authentifié tout en autorisant à tort une opération. Une politique d'accès peut être correcte mais inefficace si les identités sont usurpables. Une décision peut être correcte mais impossible à auditer si les événements ne contiennent pas de contexte suffisant.

### Schéma de décision service-à-service

```text
[Service A]
    |
    | 1. Présente identité cryptographique
    v
[Service B / proxy d'entrée]
    |
    +--> Valide la chaîne et l'identité attendue
    |
    +--> Vérifie le canal TLS/mTLS selon politique
    |
    +--> Évalue identité + action + ressource + contexte
    |
    +---- NON --> Refus + événement d'audit
    |
    +---- OUI --> Exécuter l'opération autorisée
                         |
                         v
                  Résultat + trace corrélée
```


## 6. Autorisation distribuée et points d'application

Une architecture moderne peut appliquer des politiques à plusieurs couches : passerelle, service mesh, API, application et base de données. Cette défense en profondeur ne doit pas produire des décisions contradictoires ou des zones silencieuses.

### 6.1 Modèle PEP/PDP

- **PDP (Policy Decision Point) :** évalue la politique.
- **PEP (Policy Enforcement Point) :** applique la décision.
- **PIP (Policy Information Point) :** fournit des attributs nécessaires à l'évaluation.
- **PA (Policy Administrator) :** coordonne le déploiement ou la gestion de l'accès, dans les modèles qui utilisent ce terme.

Ces termes sont des fonctions logiques. La répartition exacte dépend du modèle et de la plateforme.

### 6.2 Autorisation locale ou distante

| Modèle | Avantages | Risques et limites |
|---|---|---|
| Décision locale embarquée | Latence faible, peut continuer avec des données mises en cache | Synchronisation, drift, version de politique locale |
| PDP central distant | Gouvernance et décision centralisées | Latence, dépendance réseau, disponibilité |
| Modèle hybride | Combine rapidité et gouvernance | Complexité de versions, cache, révocation et observabilité |

Pour chaque modèle, définir la durée de validité des attributs mis en cache, le comportement en cas de panne, la version des politiques appliquées et le mécanisme de propagation des changements.

### 6.3 Règle de cohérence

Une autorisation en amont ne devrait pas élargir les droits accordés par l'application. Une architecture typique peut faire passer le trafic par un proxy puis dans l'application ; l'application doit garder ses contrôles métier, surtout pour les opérations sensibles et la séparation entre objets.

```text
Utilisateur
   |
   v
PEP 1 : proxy / gateway
  - identité de session
  - route et exposition
   |
   v
PEP 2 : service applicatif
  - rôle métier
  - objet demandé
  - action autorisée
   |
   v
PEP 3 : accès aux données
  - identité de service
  - opération / périmètre DB
   |
   v
Donnée
```

Le proxy peut autoriser la route `/api/clients`, mais l'application doit encore vérifier si la personne a le droit de lire le client identifié dans la requête. Une autorisation de route ne suffit pas à garantir l'autorisation au niveau de l'objet.


## 7. Policy-as-code : traiter les politiques comme du logiciel

Le policy-as-code consiste à représenter des règles de décision dans un format versionné et testable, avec revue, validation, déploiement et surveillance. Il aide à réduire les modifications manuelles non traçables, mais ne rend pas automatiquement une politique correcte.

### 7.1 Chaîne de production des politiques

```text
Besoin / modèle de menace
          |
          v
Règle proposée dans un dépôt versionné
          |
          v
Revue par les propriétaires concernés
          |
          v
Lint + tests unitaires + tests négatifs
          |
          v
Tests d'intégration / simulation
          |
          v
Analyse de dérive et approbation
          |
          v
Artefact signé ou version identifié
          |
          v
Déploiement progressif
          |
          v
Surveillance, comparaison et retour arrière
```

Un changement de politique est un changement de sécurité. Le processus doit préserver la traçabilité, identifier l'auteur, les approbateurs et la version appliquée, puis fournir une méthode de retour à une version précédente connue.

### 7.2 Exemple de pseudo-politique indépendante d'un produit

Le bloc ci-dessous exprime une logique, pas une syntaxe directement exécutable.

```text
POLITIQUE: admin-reseau

AUTORISER si et seulement si :
  sujet.identite_active == vrai
  ET sujet.role contient "network-admin"
  ET authentification.mfa_fort == vrai
  ET appareil.gere == vrai
  ET appareil.conforme == vrai
  ET ressource.type == "equipement-reseau"
  ET ressource.id figure dans sujet.cibles_autorisees
  ET action figure dans sujet.actions_autorisees
  ET session.expiration non dépassée

SINON :
  REFUSER
  JOURNALISER motif + version de politique
```

La politique doit définir explicitement les valeurs manquantes. Si l'état de l'appareil est inconnu, il ne faut pas traiter automatiquement cette absence comme `conforme = vrai`.

### 7.3 Structure d'un dépôt

```text
zero-trust-policy/
├── README.md
├── policies/
│   ├── human_access/
│   ├── workload_access/
│   └── privileged_access/
├── tests/
│   ├── positive/
│   ├── negative/
│   └── regression/
├── schemas/
│   └── decision-input.schema.json
├── fixtures/
│   ├── approved-request.json
│   └── denied-request.json
├── docs/
│   ├── threat-model.md
│   ├── exceptions.md
│   └── rollback.md
└── pipeline/
    └── validate-policy.yml
```

L'organisation exacte dépend du moteur de politiques. Séparer les politiques, les données de test, les schémas, les preuves et la documentation permet de garder une chaîne d'audit compréhensible.

### 7.4 Contrôles requis dans la chaîne CI/CD

- format et syntaxe valides ;
- tests positifs et négatifs ;
- tests de régression sur des décisions connues ;
- tests des attributs manquants, nuls et mal formés ;
- recherche des règles toujours vraies ou trop permissives ;
- couverture des branches de décision ;
- revue par un propriétaire technique et un propriétaire métier ;
- attribution de version ;
- signature ou vérification de provenance si le système le permet ;
- déploiement progressif et retour arrière ;
- preuve de la version qui a pris chaque décision.

Ne pas considérer qu'un taux de couverture élevé garantit une politique sûre. Il faut couvrir les cas dangereux, les refus attendus et les scénarios adverses.


## 8. Exemple avancé avec Open Policy Agent (OPA)

OPA est un moteur de politique généraliste. La syntaxe évolue ; épingler la version utilisée dans le laboratoire et consulter la documentation officielle correspondant à cette version. L'exemple ci-dessous illustre une décision d'accès à une API, sans constituer une politique de production prête à l'emploi.

### 8.1 Exemple Rego

```rego
package zerotrust.api

default allow := false

allow if {
    input.subject.active == true
    input.subject.role == "finance-reader"
    input.auth.mfa == true
    input.device.managed == true
    input.device.compliant == true
    input.resource == "invoice-api"
    input.action == "read"
}
```

**Hypothèses de l'exemple :**
- `input` est produit par un composant de confiance, et non fourni sans validation par le client ;
- les champs et types sont contrôlés avant évaluation ;
- l'application valide elle-même l'identité, l'émetteur, l'audience et la durée du jeton ;
- les droits au niveau de l'objet métier restent contrôlés dans l'application ;
- toute absence de champ mène au refus grâce à la politique par défaut, sous réserve de la manière dont l'entrée est construite.

### 8.2 Tests Rego représentatifs

Le code suivant montre la structure des tests OPA. Il est nécessaire d'adapter les fixtures, la version de Rego et la politique au laboratoire employé.

```rego
package zerotrust.api_test

import data.zerotrust.api

test_valid_finance_reader_allowed if {
    api.allow with input as {
        "subject": {"active": true, "role": "finance-reader"},
        "auth": {"mfa": true},
        "device": {"managed": true, "compliant": true},
        "resource": "invoice-api",
        "action": "read"
    }
}

test_unmanaged_device_denied if {
    not api.allow with input as {
        "subject": {"active": true, "role": "finance-reader"},
        "auth": {"mfa": true},
        "device": {"managed": false, "compliant": false},
        "resource": "invoice-api",
        "action": "read"
    }
}

test_write_denied if {
    not api.allow with input as {
        "subject": {"active": true, "role": "finance-reader"},
        "auth": {"mfa": true},
        "device": {"managed": true, "compliant": true},
        "resource": "invoice-api",
        "action": "write"
    }
}
```

Exécuter les tests selon la version OPA installée, par exemple :

```bash
opa test ./policies ./tests --fail-on-empty
```

Ne pas ignorer un test absent ou non exécuté. Une chaîne CI devrait échouer si aucun test n'est trouvé.

### 8.3 Cas à ajouter aux tests

- champ `subject` absent ;
- rôle inconnu ;
- `mfa` absent ou de type inattendu ;
- appareil inconnu ;
- ressource falsifiée ;
- action non prévue ;
- session expirée ;
- demande vers une autre audience ;
- attributs contradictoires ;
- changement de politique qui autorise une requête auparavant refusée.

### 8.4 Décision et journaux

Les journaux de décision OPA peuvent inclure le résultat, la politique interrogée et des informations utiles au diagnostic. Ils doivent être configurés pour éviter de capturer des secrets complets, des jetons, des données personnelles inutiles ou des corps de requête sensibles. Utiliser un identifiant de décision et un identifiant de trace pour relier l'événement au service appelant.


## 9. Bundles, signature et chaîne de confiance des politiques

Le déploiement d'une politique est lui-même un chemin sensible. Un attaquant capable de modifier le dépôt, le pipeline, l'artefact ou la configuration de vérification pourrait transformer une règle restrictive en une autorisation générale.

### 9.1 Chaîne de publication

```text
Auteur
  |
  v
Dépôt sous contrôle de version
  |
  v
Revue indépendante + tests
  |
  v
Pipeline CI de confiance
  |
  v
Artefact de politique versionné
  |
  v
Signature / provenance, selon outillage
  |
  v
Vérification côté consommateur
  |
  v
Activation + contrôle de version
```

### 9.2 Contrôles de sécurité

- protéger les branches principales ;
- exiger une revue indépendante pour les politiques critiques ;
- limiter les permissions du pipeline ;
- séparer les secrets de signature des runners non fiables ;
- identifier la version et le digest de l'artefact ;
- vérifier la signature au point où l'artefact est activé ;
- surveiller les erreurs de vérification ;
- tester le rejet d'un artefact modifié ;
- empêcher le mode de test ou de développement de signer pour la production ;
- documenter comment revenir à une version connue et vérifiée.

La présence d'une clé de vérification ne suffit pas si le composant ne l'applique pas réellement à l'artefact. Tester la configuration de signature et le comportement en cas d'absence ou d'échec de signature selon le moteur utilisé.


## 10. Kubernetes et service mesh

Un cluster Kubernetes comporte plusieurs couches d'identité et de réseau : identité de l'utilisateur API, ServiceAccount, identité de workload, labels, NetworkPolicy, politique de mesh et autorisation applicative. Aucune couche seule ne constitue un contrôle complet.

### 10.1 Modèle de flux

```text
Utilisateur / pipeline
       |
       v
API Kubernetes
  - authentification
  - RBAC
  - admission et audit
       |
       v
Déploiement d'un workload
       |
       v
Pod / service account
       |
       +--> identité de workload
       |
       +--> politique réseau
       |
       +--> politique mTLS / identité de pair
       |
       +--> politique d'autorisation
       |
       v
Service cible / API / stockage
```

### 10.2 Les contrôles ne sont pas équivalents

- **RBAC Kubernetes :** définit les actions d'un sujet sur les objets de l'API Kubernetes.
- **NetworkPolicy :** filtre certains flux réseau selon le plugin et l'implémentation utilisés.
- **mTLS du mesh :** protège le canal et authentifie les pairs selon la configuration.
- **AuthorizationPolicy :** autorise ou refuse des requêtes selon l'identité et les attributs disponibles.
- **Admission control :** bloque ou modifie des objets au moment de leur admission.
- **Contrôle applicatif :** vérifie les droits métier et l'accès aux objets.

Les politiques réseau exigent un CNI compatible ; une ressource `NetworkPolicy` créée ne garantit pas, à elle seule, qu'elle soit effectivement appliquée dans tous les environnements.

### 10.3 Exemple Istio : exiger mTLS

L'extrait suivant est un exemple propre à Istio. Vérifier la version, le namespace et l'effet des politiques héritées avant usage. Il ne crée pas à lui seul une autorisation métier.

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: finance
spec:
  mtls:
    mode: STRICT
```

Ce réglage exige mTLS pour les workloads concernés par cette politique, selon les règles d'héritage de la configuration Istio. Il faut tester les clients qui ne prennent pas en charge mTLS, les probes de santé, les gateways et les flux d'observabilité avant le déploiement.

### 10.4 Exemple Istio : autorisation minimale

Exemple à adapter au modèle d'identité et aux identités réellement émises par le mesh :

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: allow-catalogue-reader
  namespace: catalogue
spec:
  selector:
    matchLabels:
      app: catalogue-api
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - "cluster.local/ns/front/sa/web"
    to:
    - operation:
        methods: ["GET"]
        paths: ["/v1/catalogue/*"]
```

**Points de contrôle :**
- vérifier l'identité exacte du principal telle qu'elle apparaît en production ;
- confirmer les comportements des politiques `ALLOW` et `DENY` déjà présentes ;
- tester les méthodes HTTP et chemins non autorisés ;
- ne pas utiliser un namespace ou un ServiceAccount partagé pour des workloads aux rôles différents ;
- protéger les objets de politique contre des modifications non autorisées ;
- vérifier les chemins d'accès qui contournent le mesh.

### 10.5 Politique de cluster

Les permissions qui permettent de créer des Pods, modifier des ServiceAccounts, monter des secrets ou changer les politiques réseau peuvent avoir des effets puissants. Appliquer le moindre privilège sur le plan de contrôle et surveiller ces modifications comme des événements de sécurité majeurs.


## 11. CI/CD et sécurité du plan de contrôle

Le pipeline de déploiement peut créer, modifier ou supprimer des politiques. Il doit être traité comme une ressource privilégiée.

### 11.1 Séparation des responsabilités

```text
DÉVELOPPEUR
  - propose une modification
  - ne peut pas publier directement en production
          |
          v
REVUE TECHNIQUE + REVUE SÉCURITÉ
  - analyse des effets
  - tests positifs et négatifs
          |
          v
PIPELINE DE CONFIANCE
  - exécution isolée
  - permissions minimales
  - artefact versionné
          |
          v
APPROBATION / CONTRÔLE DE DÉPLOIEMENT
  - scope et environnement vérifiés
          |
          v
PRODUCTION
  - déploiement progressif
  - surveillance et retour arrière
```

### 11.2 Identité du pipeline

Privilégier des identités de workload fédérées ou éphémères lorsque l'environnement le permet, plutôt que des clés d'accès cloud persistantes placées dans des variables ou fichiers. Restreindre chaque job aux ressources et actions dont il a réellement besoin.

### 11.3 Contrôles de pipeline

- runners isolés et régulièrement mis à jour ;
- permissions de lecture/écriture minimales ;
- identités séparées entre test et production ;
- approbations indépendantes pour les politiques critiques ;
- journalisation des actions de pipeline ;
- protection contre la réutilisation de secrets par des branches non fiables ;
- provenance des artefacts et vérification du digest ;
- tests d'abus sur la politique et le déploiement ;
- arrêt du déploiement si la source ou l'artefact ne correspond pas à la version attendue.

Un « pipeline vert » prouve seulement que les étapes configurées ont réussi. Il faut vérifier que les tests pertinents existent et que la chaîne ne peut pas être contournée.


## 12. Authentification forte et gestion de la confiance utilisateur

Le niveau expert doit tenir compte des recommandations actuelles d'identité numérique, de la résistance au phishing, de la récupération de compte et de la fédération. NIST SP 800-63-4 et ses parties, dont SP 800-63B-4, ont été finalisés en juillet 2025 et remplacent les éditions précédentes correspondantes.

### 12.1 Risques souvent négligés

- récupération de compte plus faible que l'authentification normale ;
- ajout frauduleux d'un facteur ;
- session active survivant à la désactivation d'un compte ;
- jeton émis pour une audience différente ;
- application qui accepte une assertion avec vérifications insuffisantes ;
- comptes d'urgence sans alerte ;
- accès de prestataire non supprimé à la fin de la mission.

### 12.2 Contrôles avancés

- authentification résistante au phishing pour les accès sensibles lorsque possible ;
- politiques d'accès conditionnel adaptées à la criticité ;
- élévation temporaire des privilèges ;
- revalidation pour les opérations à fort impact ;
- révocation de session et de jeton testée, pas seulement documentée ;
- séparation des identités d'administration et des identités bureautiques ;
- preuve et revue pour l'enrôlement et la récupération des facteurs ;
- limitation des sessions et jetons selon risque et capacités techniques.

N'utiliser des exigences précises de conformité qu'après avoir consulté la publication officielle applicable à la juridiction, au secteur et au système concernés.


## 13. Révocation et propagation des changements

Dans une architecture distribuée, une révocation peut être retardée par des caches, des jetons encore valides, des connexions persistantes ou des politiques propagées de manière asynchrone. La révocation doit être conçue et mesurée de bout en bout.

### 13.1 Chaîne de propagation

```text
ÉVÉNEMENT
  compte compromis / départ / appareil perdu / rôle supprimé
       |
       v
Système source désactive l'identité ou signale le risque
       |
       +--> révocation des sessions et jetons, si disponible
       |
       +--> retrait des groupes / rôles / privilèges
       |
       +--> invalidation ou rotation des certificats / secrets concernés
       |
       +--> mise à jour des décisions et caches
       |
       v
Points d'application
       |
       v
Tests d'accès répétés + événements de vérification
       |
       v
Confirmation et clôture de l'incident
```

### 13.2 Mesurer un délai réel

Définir un test périodique :
1. créer un compte ou une identité de laboratoire avec accès connu ;
2. ouvrir une session et confirmer l'accès ;
3. déclencher la désactivation ou la révocation ;
4. réessayer l'accès par chaque chemin prévu ;
5. mesurer le temps jusqu'au refus effectif ;
6. rechercher les jetons ou sessions qui restent valides ;
7. corriger la cause et consigner le délai observé.

Ne pas inventer un SLA universel. Définir la cible selon la criticité, la capacité des produits et l'impact d'un accès résiduel.

### 13.3 Préserver la disponibilité

Une révocation massive ou une erreur dans l'autorité de certificats peut interrompre des services. Prévoir des procédures de rotation, de retrait et de restauration, ainsi qu'une séparation entre les rôles qui demandent une révocation et ceux qui l'approuvent pour les actions à fort impact.


## 14. Disponibilité, dégradation et modes de panne

Un système Zero Trust dépend souvent de plusieurs services : identité, posture, DNS, certificat, policy engine, gateway, service mesh, logs et API. Il faut définir le comportement de chaque ressource en cas d'indisponibilité.

### 14.1 Décision selon la criticité

| Ressource | Panne de l'IdP | Panne de posture | Panne du journal central |
|---|---|---|---|
| Console admin | Accès refusé sauf procédure d'urgence strictement contrôlée | Refus ou accès d'urgence spécifié | Continuité seulement si la collecte locale et les seuils sont acceptables |
| Application métier sensible | Refus ou mode de continuité limité | Refus ou accès très restreint selon politique | Mode dégradé documenté et alerte |
| Documentation publique | Contrôles applicatifs indépendants, selon architecture | Peut ne pas être pertinent | Continuité possible si la sécurité n'est pas affaiblie |
| API service-à-service | Identités valides déjà émises selon durée et mode de vérification | Dépend de l'attestation disponible | Buffer local ou arrêt selon la sensibilité et les obligations d'audit |

Ce tableau n'est pas une règle universelle. Les modes doivent être validés avec les responsables métier et sécurité.

### 14.2 Fail-closed, fail-open et mode dégradé

- **Fail-closed :** refuser lorsque la décision de sécurité ne peut pas être obtenue ou vérifiée.
- **Fail-open :** continuer malgré l'absence d'un contrôle ; cela augmente le risque.
- **Mode dégradé :** conserver uniquement des fonctions préalablement sélectionnées avec des restrictions explicites.

Le mode fail-open ne doit jamais être la conséquence accidentelle d'un time-out. Si une exception de continuité est indispensable, la limiter à une ressource, une durée, des opérations et une surveillance définies.

### 14.3 Tests de chaos contrôlé

Dans un environnement isolé et avec autorisation :
- couper l'accès au PDP ;
- rendre indisponible un fournisseur d'identité de test ;
- faire expirer un certificat de laboratoire ;
- interrompre le collecteur central ;
- retarder la propagation d'une politique ;
- tenter d'accéder directement à une origine censée être derrière un proxy.

Pour chaque scénario, consigner : résultat attendu, résultat réel, impact utilisateur, événement généré, temps de détection, procédure de reprise et risque résiduel.


## 15. Observabilité, corrélation et détection de comportements

Les journaux ne doivent pas seulement contenir « accès accordé ». Pour un diagnostic, il faut comprendre quel sujet, quel service, quelle ressource, quelle action, quelle politique et quelle version ont conduit à la décision, tout en évitant les secrets et les données inutiles.

### 15.1 Modèle d'événement recommandé

```json
{
  "timestamp": "2026-10-24T10:30:00Z",
  "event_type": "authorization.decision",
  "decision_id": "example-decision-id",
  "trace_id": "example-trace-id",
  "policy_id": "api-invoice-read",
  "policy_version": "git-sha-or-release",
  "subject_type": "workload",
  "subject_id": "spiffe://prod.example/ns/billing/sa/api",
  "resource": "invoice-api",
  "action": "read",
  "decision": "deny",
  "reason_code": "device_or_workload_context_missing",
  "environment": "prod"
}
```

Ce JSON est un schéma illustratif, pas un format universel. Les identifiants, conventions et champs doivent être adaptés au système de journalisation.

### 15.2 Règles de protection des journaux

- ne jamais stocker mots de passe, clés privées ou jetons complets ;
- supprimer ou masquer les champs sensibles avant envoi central ;
- limiter l'accès aux traces détaillées ;
- protéger les horodatages et synchroniser les horloges ;
- corréler les événements sans exposer des identifiants personnels non nécessaires ;
- définir la durée de conservation selon le risque et les exigences applicables ;
- détecter les interruptions de collecte ;
- tester la résistance aux suppressions et modifications non autorisées.

### 15.3 Signaux de détection

- hausse brutale d'autorisations pour un rôle ou une identité ;
- même identité de workload utilisée depuis des contextes inattendus ;
- échecs de validation de certificats ;
- changement d'une politique critique en dehors de la fenêtre prévue ;
- ajout d'une exception large ;
- compte de service qui accède à une ressource nouvelle ;
- réutilisation de jeton détectée par le système, lorsqu'il a ce signal ;
- accès direct à une origine normalement protégée par un proxy ;
- panne du journal ou absence de heartbeat d'un point d'application.

Les anomalies sont des signaux à enquêter, pas des preuves suffisantes à elles seules. Définir une sévérité, des critères de triage et des actions autorisées.


## 16. Défense contre le contournement et les erreurs de confiance

Un contrôle peut exister sur le chemin prévu tout en étant contourné par un accès direct, une interface de secours, un port non surveillé ou un rôle trop large.

### 16.1 Revue des chemins

```text
CHEMIN ATTENDU
Client --> Gateway/PEP --> Application --> Données

CHEMINS ALTERNATIFS À RECHERCHER
Client -------> IP / DNS direct de l'origine
Admin --------> interface de gestion secondaire
Service A ----> port de secours de Service B
Pipeline -----> API cloud avec une identité plus large
Compte service -> stockage / base non lié au besoin
```

### 16.2 Revue technique autorisée

Dans un périmètre approuvé :
1. lister les interfaces exposées et les endpoints d'origine ;
2. vérifier les règles réseau et les interfaces d'administration ;
3. tester les chemins directs depuis les zones de test non autorisées ;
4. vérifier les en-têtes d'identité transmis par proxy et leur provenance ;
5. confirmer la validation cryptographique des jetons et certificats ;
6. vérifier les droits effectifs d'une identité de test ;
7. consigner les résultats et corriger selon le processus de changement.

Le but est la validation défensive des contrôles de sa propre infrastructure. Ne pas conduire ces tests sur des systèmes tiers ou hors du périmètre autorisé.

### 16.3 Problèmes fréquents

- reverse proxy qui ajoute un en-tête d'identité mais laisse l'origine accessible ;
- service qui fait confiance à `X-User` sans s'assurer que l'en-tête vient d'un proxy de confiance ;
- wildcard dans une politique ;
- compte de service partagé par plusieurs applications ;
- certificat valable accepté sans vérifier l'identité attendue ;
- clé de signature exposée dans le pipeline ;
- règle de secours permissive oubliée après une panne ;
- cache d'autorisation qui ne se met pas à jour après révocation.


## 17. Laboratoire expert 1 — politique comme code et régression

### Objectif

Créer une politique pour une API sensible, la versionner et vérifier qu'aucune modification n'autorise un cas interdit.

### Entrées de test

```text
CAS A — rôle correct, MFA correct, appareil conforme, lecture
  Résultat attendu : AUTORISER

CAS B — rôle inconnu, tous les autres attributs corrects
  Résultat attendu : REFUSER

CAS C — rôle correct, MFA manquant
  Résultat attendu : REFUSER

CAS D — appareil non conforme
  Résultat attendu : REFUSER ou remédiation limitée, selon politique écrite

CAS E — action write alors que seule read est prévue
  Résultat attendu : REFUSER

CAS F — ressource différente
  Résultat attendu : REFUSER

CAS G — attribut d'identité absent ou mal formé
  Résultat attendu : REFUSER

CAS H — ancienne version du test n'est plus exécutée
  Résultat attendu : pipeline en échec si aucun test ne s'exécute
```

### Étapes

1. écrire la règle et un schéma d'entrée ;
2. définir les cas positifs et négatifs avant le code ;
3. exécuter les tests localement ;
4. créer une modification volontairement permissive dans une branche de laboratoire ;
5. vérifier qu'au moins un test échoue ;
6. vérifier que le pipeline échoue en cas de zéro test ;
7. exiger une revue indépendante ;
8. simuler un retour à une version approuvée ;
9. enregistrer la version utilisée pour chaque décision.

### Critères de réussite

- le refus par défaut est effectif ;
- les attributs manquants ne créent pas d'autorisation ;
- le test d'une action interdite échoue si la politique est rendue trop permissive ;
- l'artefact livré est identifiable par version ;
- la procédure de rollback est démontrée.


## 18. Laboratoire expert 2 — identité workload de bout en bout

### Scénario

Un service `billing-api` doit appeler `ledger-service` dans un cluster. Un workload non lié ne doit ni obtenir l'identité du service ni appeler l'API protégée.

### Architecture

```text
[billing-api]
     |
     | demande d'identité
     v
[Agent / système d'identité workload]
     |
     | attestation + sélecteurs validés
     v
[Identité courte durée]
     |
     | connexion mTLS
     v
[PEP / ledger-service]
     |
     +--> validation du pair
     +--> autorisation de l'opération
     +--> événement d'audit
```

### Tests

- workload attendu reçoit l'identité prévue ;
- workload dans un autre namespace ne reçoit pas cette identité ;
- certificat expiré ou non fiable est rejeté ;
- identité valide mais action interdite est rejetée ;
- après rotation, l'ancienne identité cesse d'être utilisable selon la fenêtre définie ;
- les erreurs sont journalisées sans exposer la clé ou le jeton complet.

### Résultat attendu

L'identité établit qui est le service ; mTLS protège le canal et authentifie le pair ; la politique autorise une opération précise. Ces trois fonctions doivent être testées séparément.


## 19. Laboratoire expert 3 — déployer une politique sans interruption

### Contexte

Une application critique possède une règle de flux trop large. L'objectif est de réduire ses droits tout en conservant les opérations métier.

### Méthode

```text
1. INVENTAIRE
   - ressources et flux
   - propriétaire de chaque dépendance
        |
        v
2. OBSERVATION
   - collecte sur une période représentative
   - validation avec les propriétaires
        |
        v
3. MODE ALERTE
   - nouvelles règles évaluées sans bloquer, si possible
   - comparaison attendue / réelle
        |
        v
4. GROUPE PILOTE
   - périmètre réduit
   - tests métiers + tests négatifs
        |
        v
5. DÉPLOIEMENT PROGRESSIF
   - surveillance renforcée
   - seuil d'arrêt défini
        |
        v
6. VALIDATION
   - flux utiles maintenus
   - flux interdits refusés
   - événements et métriques vérifiés
        |
        v
7. CLÔTURE
   - suppression des exceptions temporaires
   - dossier de preuve et révision planifiée
```

### Conditions d'arrêt

Arrêter ou revenir à une version approuvée si :
- un flux critique nécessaire est bloqué ;
- une ressource devient accessible par un chemin non prévu ;
- les journaux ou signaux critiques cessent de fonctionner ;
- une identité de production reçoit des droits inattendus ;
- la procédure de secours ne peut pas être utilisée ;
- les résultats ne correspondent pas à ceux attendus.

Le retour arrière ne doit pas réintroduire une règle générale sans date de fin. Documenter la situation temporaire et le plan de correction.


## 20. Laboratoire expert 4 — exercice de révocation

### Objectif

Mesurer le temps nécessaire pour retirer l'accès d'une identité compromise, y compris les sessions actives et identités machine.

### Scénario

Un secret de service ou une identité utilisateur est considéré compromis. Le service de sécurité déclenche une procédure de containment.

### Procédure

1. enregistrer l'heure de départ ;
2. désactiver ou révoquer l'identité source selon le cas ;
3. retirer les permissions et groupes concernés ;
4. invalider les sessions et jetons lorsque pris en charge ;
5. renouveler les secrets ou certificats exposés ;
6. vérifier les accès par les chemins principaux et alternatifs ;
7. rechercher les traces d'utilisation postérieures ;
8. confirmer que le service reste opérationnel avec les identités légitimes ;
9. consigner le temps de propagation et les écarts ;
10. ajuster la politique et refaire le test.

### Tableau de mesure

| Mesure | Valeur à enregistrer |
|---|---|
| Heure de déclenchement | Horodatage synchronisé |
| Heure de désactivation source | Horodatage |
| Heure de refus effectif sur API | Horodatage |
| Heure de refus effectif sur chemin alternatif | Horodatage |
| Session longue encore valable ? | Oui/non et preuve |
| Identité machine/secret secondaire trouvé ? | Oui/non |
| Impact métier | Description |
| Cause de retard | Cache, jeton, réplication, erreur de procédure |
| Action corrective | Responsable et échéance |

Ne pas fixer une cible de révocation arbitraire. Définir un objectif selon le risque, puis mesurer si l'architecture l'atteint réellement.


## 21. Laboratoire expert 5 — revue d'une chaîne CI/CD

### Objectif

Vérifier que seule une chaîne de confiance peut publier une politique de production et que les identités du pipeline n'ont pas de droits globaux.

### Scénario de revue

Un pipeline d'intégration peut tester les politiques, mais il ne doit pas automatiquement pouvoir modifier tous les groupes IAM, supprimer des logs ou publier un artefact de production depuis une branche non fiable.

### Contrôles

- identité distincte entre développement et production ;
- permissions minimales au niveau de chaque job ;
- protection des branches de politique ;
- approbation indépendante pour les changements critiques ;
- artefact versionné et provenance vérifiable ;
- secrets absents des logs ;
- runners isolés des jobs non fiables ;
- validation côté consommateur de l'artefact ;
- test d'un artefact modifié ou non signé ;
- audit de l'appelant et de la version déployée.

### Schéma

```text
Branche non fiable
  |
  +--> tests dans environnement isolé
  +--> aucun secret de production
  +--> aucun droit de publication prod
           |
           v
Branche protégée + revue
           |
           v
Pipeline de publication de confiance
           |
           +--> tests complets
           +--> artefact versionné/signé
           +--> approbation requise
           |
           v
Consommateur de politique
           |
           +--> vérifie version / signature
           +--> active la version attendue
           +--> journalise la décision
```


## 22. Indicateurs de maturité et preuves de contrôle

Le niveau expert doit relier les pratiques aux preuves. Les indicateurs ne sont utiles que s'ils orientent une action, possèdent un responsable et sont interprétés avec leurs limites.

| Domaine | Indicateur possible | Preuve à conserver |
|---|---|---|
| Inventaire | Couverture des ressources critiques | Catalogue propriétaire/sensibilité |
| Accès | Ressources sensibles avec PEP vérifié | Tests de chemin direct |
| Identité humaine | Comptes privilégiés protégés selon politique | Rapports de configuration et tests |
| Workload | Identités à durée de vie maîtrisée | Registre, rotation et test de révocation |
| Politique | Politiques exécutées par CI/CD | Résultats de tests, version, approbation |
| Résilience | Comportement connu en cas de panne | Rapport d'exercice |
| Révocation | Délai réel de refus après incident | Mesures horodatées |
| Audit | Couverture des événements essentiels | Échantillons de traces et tests de collecte |
| Exceptions | Exceptions échues encore actives | Registre et alertes |
| Détection | Scénarios de détection testés | Résultat, délai, responsable et correction |

Éviter de réduire l'état de sécurité à un score agrégé. Afficher les écarts critiques même si la moyenne paraît bonne.


## 23. Gouvernance des exceptions et gestion des changements

À grande échelle, les exceptions sont inévitables. Le risque vient des exceptions mal délimitées, non révisées ou impossibles à supprimer.

### 23.1 Enregistrement obligatoire

```text
ID : ZT-EXC-0007
Ressource : nom et identifiant stables
Sujet : utilisateur, rôle ou workload précis
Action : opération permise
Périmètre réseau : uniquement si nécessaire
Justification : besoin métier documenté
Propriétaire : personne / équipe responsable
Approbateur : rôle autorisé
Date de début : valeur approuvée
Date de fin / révision : obligatoire
Contrôle compensatoire : mesure explicite
Journaux : événements attendus
Plan de retrait : procédure et test
```

### 23.2 Processus de changement

- préciser l'objectif et le risque traité ;
- évaluer les systèmes et politiques affectés ;
- exécuter les tests de régression ;
- faire valider les cas d'usage par le propriétaire ;
- préparer et tester le retour arrière ;
- déployer à petite échelle ;
- vérifier les décisions après déploiement ;
- fermer les exceptions temporaires ;
- archiver les preuves et fixer une date de révision.


## 24. Gouvernance des données de contexte et confidentialité

Les signaux de contexte peuvent inclure des données personnelles, des informations d'appareil et des comportements. Plus de données n'implique pas automatiquement une meilleure décision.

Principes :
- définir la finalité de chaque signal ;
- collecter le minimum utile ;
- limiter l'accès aux données brutes ;
- retenir les journaux pendant une durée justifiée ;
- séparer les attributs de sécurité des informations métier non nécessaires ;
- documenter les traitements et les responsabilités ;
- réduire les identifiants dans les tableaux de bord lorsque l'identité nominative n'est pas nécessaire ;
- s'assurer que les équipes support ne peuvent pas lire les secrets d'authentification ;
- prévoir la réponse aux demandes d'accès, de rectification ou de suppression lorsque les règles applicables l'exigent.

La politique de sécurité doit respecter les contraintes juridiques locales et sectorielles. Ce cours est technique et ne constitue pas un avis juridique.


## 25. Scénarios d'architecture avancés

### Scénario A — application héritée

Une application ancienne ne sait pas utiliser SSO ou mTLS.

Approche possible :
- placer l'application derrière un point d'application compatible ;
- rendre l'origine inaccessible par les chemins non prévus ;
- limiter le compte de service et les flux réseau ;
- conserver ou renforcer l'autorisation dans l'application ;
- définir une feuille de route de modernisation ;
- documenter les risques résiduels et les limites du proxy.

Un proxy n'élimine pas une vulnérabilité applicative. Il réduit certains chemins d'accès, mais le risque lié au code et aux permissions internes reste.

### Scénario B — service cloud-native multi-cloud

Une API dans un cloud appelle un service dans un autre.

Contrôles possibles :
- identité de workload plutôt que confiance basée uniquement sur l'adresse IP ;
- fédération ou autorité de confiance explicitement configurée ;
- mTLS lorsque pertinent ;
- autorisation au niveau service et de l'opération ;
- politique réseau en défense complémentaire ;
- rotation de certificats et procédure de panne ;
- traces corrélées entre les environnements.

Le lien privé entre clouds n'est pas une autorisation applicative. Chaque service doit valider le pair, l'action et la ressource.

### Scénario C — accès d'un fournisseur externe

Approche possible :
- identité nominative et sponsor interne ;
- MFA adapté au risque ;
- accès limité à la ressource et à la période ;
- appareil géré ou conditions compensatoires approuvées ;
- aucune appartenance implicite au réseau interne ;
- journalisation et revue ;
- expiration et retrait testés à la fin de contrat.

### Scénario D — environnements de production et de développement

Approche possible :
- domaines de confiance ou autorités séparés quand le risque le justifie ;
- comptes et secrets distincts ;
- aucun accès de développement aux données sensibles en clair sans justification ;
- pipelines séparés ;
- contrôle explicite de la promotion des artefacts ;
- tests de non-interférence entre politiques.


## 26. Évaluation finale

### Partie 1 — conception

Dessiner une architecture textuelle qui comprend :
- deux clouds ;
- un datacenter ;
- un IdP ;
- une gateway d'accès utilisateur ;
- une plateforme d'identité workload ;
- deux applications ;
- une API sensible ;
- un environnement d'administration ;
- un pipeline de politiques ;
- une collecte de journaux.

**Attendu :** indiquer les points d'application, les flux autorisés, les identités et les chemins qui doivent être refusés.

### Partie 2 — policy-as-code

Écrire une politique et des tests pour que seul un `billing-reader` authentifié, disposant d'un MFA adapté et d'un appareil conforme puisse lire une ressource de facturation.

**Attendu :** tester l'accès légitime, le rôle incorrect, la posture absente, une action d'écriture, une autre ressource et une identité désactivée.

### Partie 3 — réponse à incident

Un SVID d'un workload aurait été copié ou une clé de signature de politique serait exposée.

**Attendu :**
1. définir la portée ;
2. révoquer ou remplacer les éléments de confiance concernés ;
3. identifier les accès postérieurs à la compromission ;
4. assurer le maintien des workloads légitimes ;
5. préserver les journaux ;
6. vérifier la révocation et la nouvelle chaîne de confiance ;
7. documenter la cause et les contrôles supplémentaires.

### Partie 4 — disponibilité

Le moteur de politique devient indisponible. La console d'administration, l'application RH et le site public ne doivent pas forcément adopter le même comportement.

**Attendu :** expliquer pour chaque ressource le mode de panne, le risque, le mécanisme de secours et le test à réaliser.

### Barème indicatif

| Domaine | Points |
|---|---:|
| Architecture et points d'application | 20 |
| Identités humaines et workload | 20 |
| Qualité des politiques et tests négatifs | 20 |
| Révocation, journalisation et détection | 15 |
| Résilience et retour arrière | 15 |
| Gouvernance, preuves et risques résiduels | 10 |
| **Total** | **100** |

Un bon résultat ne repose pas seulement sur la présence de composants. L'apprenant doit expliquer comment les règles sont appliquées, prouver les refus attendus et décrire les limites restantes.


## 27. Corrigés synthétiques

### Cas 1 — certificat accepté mais action interdite

**Bonne réponse :** l'authentification du pair ne suffit pas. Le PEP ou le service doit évaluer le droit sur la ressource et l'opération. Ajouter un test négatif pour démontrer le refus.

### Cas 2 — accès direct à l'origine

**Bonne réponse :** fermer le chemin alternatif au niveau réseau ou applicatif, vérifier les hôtes et ports publiés, puis tester depuis une source qui ne doit pas accéder. Ne pas supposer que le proxy protège une origine encore joignable directement.

### Cas 3 — pipeline capable de publier n'importe quelle politique

**Bonne réponse :** séparer les permissions entre test et production, protéger la branche et la chaîne de publication, contrôler l'artefact au moment de l'activation et ajouter une revue indépendante pour les règles critiques. Vérifier ensuite qu'un pipeline non fiable ne peut pas obtenir les secrets de production.

### Cas 4 — révocation lente

**Bonne réponse :** mesurer le délai par point d'application, inspecter les jetons, sessions et caches, documenter la limite technique, puis réduire la fenêtre de risque ou ajouter un mécanisme de containment. Ne pas annoncer une révocation « immédiate » sans mesure.

### Cas 5 — surcharge d'exceptions

**Bonne réponse :** regrouper les exceptions par cause, identifier les dépendances réelles, assigner des propriétaires, ajouter dates de fin et tests, puis supprimer les exceptions en pilote. Ne pas convertir les exceptions en règle globale.


## 28. Checklist de revue d'architecture

### Identité et confiance

- [ ] Identités humaines et machine séparées.
- [ ] Attestation et attribution d'identité comprises.
- [ ] Chaînes de certificats et audiences validées.
- [ ] Rotation et révocation testées.
- [ ] Domaines de confiance et fédérations documentés.

### Politique et application

- [ ] Décisions basées sur identité, ressource, action et contexte.
- [ ] Refus par défaut pour les chemins critiques.
- [ ] Chaque PEP est identifié.
- [ ] Les chemins alternatifs sont testés.
- [ ] Les contrôles métier de l'application restent actifs.
- [ ] Les politiques sont versionnées et testées.

### CI/CD et gouvernance

- [ ] Permissions de pipeline minimales.
- [ ] Revue indépendante des politiques sensibles.
- [ ] Artefacts de politique versionnés.
- [ ] Signature/provenance vérifiée selon capacité du système.
- [ ] Retour arrière démontré.
- [ ] Exceptions avec propriétaire et expiration.

### Exploitation

- [ ] Journaux protégés et sans secrets complets.
- [ ] Décisions corrélables à une version de politique.
- [ ] Alertes de changement et de panne testées.
- [ ] Révocation mesurée de bout en bout.
- [ ] Modes fail-open, fail-closed et dégradés documentés.
- [ ] Exercices de résilience réalisés.
- [ ] Risques résiduels connus et acceptés.


## 29. Références techniques officielles

Les liens ci-dessous servent de points de départ. Toujours vérifier la version exacte des produits, des API et des standards avant un déploiement.

1. **NIST SP 800-207 — Zero Trust Architecture**  
   https://csrc.nist.gov/pubs/sp/800/207/final  
   Modèle logique, principes et modèles de déploiement Zero Trust.

2. **NIST SP 800-207A — A Zero Trust Architecture Model for Access Control in Cloud-Native Applications in Multi-Cloud Environments**  
   https://csrc.nist.gov/pubs/sp/800/207/a/final  
   Contrôle d'accès cloud-native, identités d'application et environnements multi-cloud.

3. **CISA — Zero Trust Maturity Model**  
   https://www.cisa.gov/zero-trust-maturity-model  
   Modèle de progression de la maturité organisationnelle.

4. **NIST SP 800-63-4 — Digital Identity Guidelines**  
   https://csrc.nist.gov/pubs/sp/800/63/4/final  
   Identité numérique, authentification, fédération et gestion des authentificateurs. Édition finale de juillet 2025.

5. **NIST SP 800-63B-4 — Authentication and Authenticator Management**  
   https://csrc.nist.gov/pubs/sp/800/63/b/4/final  
   Recommandations sur les authentificateurs et les niveaux d'assurance. Édition finale du 31 juillet 2025.

6. **SPIFFE — Overview**  
   https://spiffe.io/docs/latest/spiffe-about/overview/  
   Principes de l'identité de workload et des SVID.

7. **SPIRE — Concepts**  
   https://spiffe.io/docs/latest/spire-about/spire-concepts/  
   Architecture serveur/agent, attestation des nœuds et workloads, registre et émission d'identités.

8. **Open Policy Agent — Policy Testing**  
   https://www.openpolicyagent.org/docs/policy-testing  
   Tests automatisés des politiques Rego.

9. **Open Policy Agent — Decision Logs**  
   https://www.openpolicyagent.org/docs/management-decision-logs  
   Journaux de décision, corrélation et audit.

10. **Open Policy Agent — Configuration**  
    https://www.openpolicyagent.org/docs/configuration  
    Bundles et vérification de signature selon la configuration.

11. **Istio — PeerAuthentication**  
    https://istio.io/latest/docs/reference/config/security/peer_authentication/  
    Configuration de l'authentification des pairs et de mTLS dans Istio.

Les standards et la documentation technique ne remplacent pas le modèle de menace, les tests opérationnels, les exigences réglementaires applicables ni la validation de l'implémentation choisie.


## Conclusion

Une architecture Zero Trust experte est une architecture **vérifiable**. Elle associe des identités solides, des décisions limitées, des points d'application qui ne peuvent pas être contournés, des politiques testées, des preuves d'audit et des procédures de révocation et de reprise mesurées.

La progression finale est la suivante :

```text
IDENTIFIER
  Ressources, sujets, services et flux
       |
       v
AUTHENTIFIER / ATTESTER
  Établir l'identité et vérifier les preuves
       |
       v
AUTORISER
  Décider selon l'identité, la ressource, l'action et le contexte
       |
       v
APPLIQUER
  Bloquer les chemins alternatifs et maintenir les contrôles métier
       |
       v
OBSERVER
  Corréler décisions, versions, événements et actions
       |
       v
TESTER / RÉVOQUER / AMÉLIORER
  Prouver les refus, mesurer les délais et corriger la dérive
```

Le critère final n'est pas le nombre de produits déployés, mais la capacité à démontrer, par des tests reproductibles et des preuves, qu'un sujet ne peut accéder qu'aux ressources et opérations qui lui sont explicitement accordées, y compris en cas de changement, de panne ou de tentative de contournement.
