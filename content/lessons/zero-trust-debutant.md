# Architecture Zero Trust — Niveau débutant
## Cours pratique progressif pour les réseaux et les systèmes

> **Objectif :** comprendre les principes Zero Trust et savoir réaliser un premier déploiement limité, mesurable et réversible.
>
> **Public :** techniciens réseau/système, étudiants en cybersécurité et administrateurs débutants.
>
> **Pré-requis :** notions de base sur IP, Ethernet, comptes utilisateurs, pare-feu et authentification.
>
> **Important :** Zero Trust n'est ni un produit unique ni une commande magique. C'est une architecture et un ensemble de pratiques qui réduisent la confiance implicite, vérifient les accès et limitent les conséquences d'une compromission.


## 1. Objectifs pédagogiques

À la fin du cours, vous saurez :

- expliquer pourquoi « être dans le réseau interne » ne suffit pas pour être digne de confiance ;
- distinguer identité, appareil, ressource, politique et décision d'accès ;
- dessiner un flux Zero Trust simple ;
- appliquer le principe du moindre privilège ;
- protéger un petit service interne avec MFA, règles d'accès et journalisation ;
- préparer un pilote sans bloquer toute l'entreprise ;
- lire des journaux d'accès et traiter quelques incidents courants.

### Parcours de progression

```text
COMPRENDRE
    |
    v
Identifier les ressources et les utilisateurs
    |
    v
Définir qui peut accéder à quoi, depuis quel appareil
    |
    v
Mettre en place une vérification forte (MFA + état de l'appareil)
    |
    v
Limiter l'accès à une application précise
    |
    v
Journaliser, tester, corriger et étendre progressivement
```


## 2. Pourquoi le modèle traditionnel ne suffit pas

Un modèle traditionnel peut considérer qu'un utilisateur est fiable parce qu'il est connecté au LAN ou au VPN. Or un compte peut être volé, un poste compromis ou un appareil non géré branché au réseau.

### Schéma textuel — confiance implicite

```text
                  RÉSEAU D'ENTREPRISE
+----------+      +--------------------+      +----------------+
| PC        |----->| LAN considéré      |----->| Serveur métier |
| utilisateur|     | comme fiable       |      |                |
+----------+      +--------------------+      +----------------+
                         |
                         +----> autres serveurs accessibles
```

**Risque :** une fois à l'intérieur, un compte ou un poste compromis peut parfois atteindre trop de ressources.

Zero Trust ne signifie pas « ne jamais faire confiance à personne » au sens humain. Cela signifie **ne pas accorder de confiance permanente sur la seule base de l'emplacement réseau**. Chaque demande d'accès est évaluée selon une politique.


## 3. Les principes fondamentaux

### 3.1 Vérifier explicitement

La décision peut tenir compte de plusieurs signaux :

- identité de l'utilisateur et rôle ;
- force de l'authentification, notamment MFA ;
- identité et état de conformité de l'appareil ;
- ressource demandée ;
- sensibilité de la donnée ;
- emplacement ou risque de la connexion, comme signal supplémentaire ;
- heure, comportement et alertes de sécurité, si ces signaux sont disponibles.

Aucun signal isolé ne garantit qu'une session est sûre. Les règles doivent être adaptées au risque et éviter de collecter des données inutiles.

### 3.2 Appliquer le moindre privilège

Un utilisateur reçoit uniquement les droits nécessaires, pendant la durée nécessaire.

```text
TROP LARGE                         MOINDRE PRIVILÈGE
---------                          -----------------
Employé ---> Tous les serveurs     Employé ---> Portail RH
Admin   ---> Tous les postes       Admin   ---> Outils admin autorisés
Invité  ---> LAN complet           Invité  ---> Internet uniquement
```

### 3.3 Supposer qu'une compromission est possible

Concevoir les contrôles pour limiter l'impact d'un compte ou d'un poste compromis :

- segmenter les ressources ;
- limiter les flux entre segments ;
- protéger les comptes privilégiés ;
- journaliser les accès ;
- détecter les comportements anormaux ;
- révoquer rapidement une session ou un identifiant compromis.

### 3.4 Réévaluer l'accès

L'authentification initiale n'autorise pas nécessairement un accès illimité et permanent. Selon le système, l'accès peut être réévalué à la connexion, lors d'un changement de risque, à l'expiration d'un jeton ou lors d'une modification de conformité.


## 4. Les composants d'une architecture Zero Trust

Les termes varient selon les produits. Le modèle conceptuel ci-dessous sépare la décision de l'application de cette décision.

```text
                 PLAN DE CONTRÔLE
+-----------------------+      +-------------------------+
| Moteur de politique   |<-----| Signaux et sources      |
| décide : autoriser ?  |      | identité, MFA, appareil,|
+-----------+-----------+      | risque, inventaire      |
            |                  +-------------------------+
            | décision
            v
+-----------------------+
| Point d'application   |
| autorise / refuse /   |
| limite la session     |
+-----------+-----------+
            |
            | accès autorisé selon la politique
            v
+-----------------------+       +----------------------+
| Ressource protégée    |------>| Journaux / alertes   |
| application ou donnée |       | supervision          |
+-----------------------+       +----------------------+
```

- **Moteur de politique :** évalue les informations et prend une décision.
- **Point d'application :** applique la décision, par exemple un proxy d'accès, une passerelle ou un composant de l'application.
- **Sources de signaux :** fournisseur d'identité, MFA, gestion des appareils, inventaire et détection.
- **Ressource protégée :** application, serveur, API, base de données ou donnée.
- **Journalisation :** conserve les événements utiles à l'audit et au diagnostic.

Un produit réel peut regrouper plusieurs rôles dans un même service. Le schéma décrit des fonctions, pas forcément des machines distinctes.


## 5. Identité : l'utilisateur et l'appareil

### 5.1 Identité de l'utilisateur

Utiliser des comptes nominatifs et supprimer les comptes partagés quand cela est possible. Les comptes privilégiés doivent être séparés des comptes bureautiques ordinaires.

Bonnes pratiques :

1. comptes uniques par personne ;
2. MFA pour les accès sensibles et distants ;
3. rôles et groupes documentés ;
4. suppression ou suspension rapide des comptes qui ne sont plus nécessaires ;
5. comptes administrateurs dédiés et protégés ;
6. processus de récupération de compte sécurisé.

Le MFA réduit le risque lié au vol de mot de passe, mais n'empêche pas toutes les attaques, notamment le vol de session ou certaines attaques de phishing. Privilégier les méthodes résistantes au phishing lorsque c'est possible.

### 5.2 Identité et état de l'appareil

Un utilisateur authentifié depuis un appareil compromis reste un risque. Selon les capacités de l'organisation, vérifier :

- appareil inventorié et attribué ;
- système et correctifs pris en charge ;
- chiffrement du disque si pertinent ;
- protection antimalware/EDR active ;
- verrouillage de session ;
- configuration de sécurité conforme ;
- certificat d'appareil ou identité machine, si le système le prend en charge.

Ne pas supposer qu'une adresse IP, un nom d'hôte ou une adresse MAC prouve à elle seule l'identité d'un appareil : ces valeurs peuvent être modifiées ou usurpées.


## 6. Ressources et classification

Avant de créer des règles, il faut savoir ce que l'on protège.

### Exemple de registre minimal

| Ressource | Sensibilité | Utilisateurs autorisés | Contrôles essentiels |
|---|---|---|---|
| Portail public | Faible | Public | Correctifs, filtrage, journaux |
| Portail RH | Élevée | RH et personnes autorisées | SSO, MFA, moindre privilège |
| Dépôt de code | Élevée | Équipe technique | MFA, droits par projet, audit |
| Console d'administration | Critique | Administrateurs désignés | Poste géré, MFA fort, accès limité |
| Sauvegardes | Critique | Opérateurs de sauvegarde autorisés | Comptes séparés, immutabilité, audit |

Classer les ressources aide à choisir des contrôles proportionnés. Éviter de donner à tout le monde le même accès « par commodité ».


## 7. Schéma d'accès à une application interne

Exemple : une employée doit ouvrir le portail RH.

```text
[Employée]
     |
     | 1. Demande /rh
     v
[Passerelle ou proxy d'accès]
     |
     +----> [Fournisseur d'identité]
     |          |
     |          +--> Identité valide ?
     |          +--> MFA réussi ?
     |
     +----> [Gestion de l'appareil]
     |          |
     |          +--> Appareil conforme ?
     |
     v
[Évaluation de la politique]
     |
     +---- NON conforme / refus --> [Refus + journal]
     |
     +---- Autorisé -------------> [Portail RH]
                                      |
                                      v
                              [Journal d'accès]
```

La passerelle ne doit exposer que la ressource prévue. L'application doit elle-même conserver une authentification et une autorisation appropriées lorsque c'est nécessaire ; la passerelle ne remplace pas automatiquement toutes les protections internes.


## 8. VPN et Zero Trust : comprendre la différence

Zero Trust ne signifie pas que le VPN est interdit. Un VPN peut rester utile pour certains usages, mais l'accès au réseau ne doit pas donner automatiquement accès à toutes les ressources.

```text
VPN traditionnel trop permissif
[Utilisateur] --> [VPN] --> [Réseau interne étendu]
                              |-- Serveur A
                              |-- Serveur B
                              |-- Administration

Accès par ressource
[Utilisateur] --> [Identité + MFA + contrôle appareil]
                           |
                           v
                    [Passerelle d'accès]
                           |
                           +--> Application autorisée
                           |
                           +--> Autres ressources : refus
```

Objectif : remplacer progressivement les accès réseau trop larges par des accès explicites aux applications ou services nécessaires. Certaines applications nécessitent encore un VPN ou une connectivité réseau spécifique ; il faut alors réduire les routes et les droits au strict nécessaire.


## 9. Microsegmentation et contrôle des flux

La segmentation limite les communications entre catégories de systèmes. Elle peut s'appuyer sur VLAN, pare-feu, ACL, politiques d'identité ou contrôles de l'hyperviseur. Un VLAN seul n'est pas une politique Zero Trust complète.

### Exemple de politique

```text
ZONE UTILISATEURS
    |
    +---- HTTPS ----> PORTAIL RH        AUTORISÉ
    |
    +---- SSH ------> SERVEURS          REFUSÉ
    |
    +---- RDP ------> POSTES ADMIN      REFUSÉ

ZONE ADMINISTRATION (poste dédié)
    |
    +---- SSH ------> SERVEURS GÉRÉS    AUTORISÉ si MFA + rôle valide

ZONE INVITÉS
    |
    +---- Internet -------------------- AUTORISÉ selon filtrage
    +---- Réseau interne -------------- REFUSÉ
```

Les flux autorisés doivent être définis à partir des besoins réels. Documenter les exceptions, leur propriétaire et leur date de révision.


## 10. Premier laboratoire : créer un accès protégé

### Objectif

Mettre en place une politique pilote pour une seule application de test, sans modifier immédiatement l'ensemble du réseau de production.

### Matériel et environnement

- deux comptes de test : un autorisé, un non autorisé ;
- une application web de test non sensible ;
- un fournisseur d'identité ou une plateforme de laboratoire ;
- MFA disponible ;
- si possible, un appareil géré et un appareil non conforme ;
- accès aux journaux d'authentification et de décision.

Ne pas utiliser un portail RH réel ou des données de production pour un premier exercice.

### Étape A — définir les règles

```text
RESSOURCE : application-demo
POLITIQUE :
  - utilisateur membre du groupe "ZT-Pilote" : condition requise
  - MFA réussi : obligatoire
  - appareil géré et conforme : obligatoire si le contrôle est disponible
  - autre utilisateur : refus
  - décision et motif : journalisés
```

### Étape B — construire une matrice de tests

| Test | Identité | MFA | Appareil | Résultat attendu |
|---|---|---|---|---|
| 1 | Autorisée | Réussi | Conforme | Autoriser |
| 2 | Non autorisée | Réussi | Conforme | Refuser |
| 3 | Autorisée | Échec | Conforme | Refuser |
| 4 | Autorisée | Réussi | Non conforme | Refuser ou accès limité selon politique |
| 5 | Compte désactivé | Réussi si session ancienne | Conforme | Refuser après révocation/réévaluation appropriée |

Le comportement d'une session déjà ouverte dépend du produit et de la durée de vie des jetons. Tester explicitement la révocation et ne pas supposer qu'une désactivation coupe instantanément toutes les sessions.

### Étape C — valider

Pour chaque test, enregistrer :

- heure et identifiant du test ;
- ressource demandée ;
- résultat attendu et obtenu ;
- règle qui a décidé ;
- événement correspondant dans les journaux ;
- action corrective si le résultat diffère.

### Étape D — retour arrière

Avant de déployer, documenter comment désactiver la règle pilote et restaurer l'accès administratif légitime. Garder un compte de secours fortement protégé, surveillé et réservé à la récupération, si l'architecture en a besoin. Tester cette procédure à l'avance.


## 11. Exemple de politique d'accès lisible

Voici une représentation indépendante d'un produit. Ce n'est pas un langage de configuration exécutable.

```text
POLITIQUE : accès-au-portail-admin

RESSOURCE :
  console d'administration

SUJET :
  membre du groupe "Administrateurs-Réseau"

CONDITIONS :
  identité vérifiée
  MFA résistant au phishing si disponible
  appareil administrateur géré
  état de conformité valide
  session limitée dans le temps

DÉCISION :
  toutes les conditions obligatoires sont satisfaites -> AUTORISER
  sinon -> REFUSER et journaliser

LIMITES :
  accès uniquement à la console désignée
  pas d'accès implicite aux autres serveurs
  réévaluation selon les capacités de la plateforme
```

La politique doit être testée avec des cas positifs et négatifs. Une règle « autoriser si l'utilisateur est interne » ne répond pas à l'objectif.


## 12. Journalisation et diagnostic

### Événements à surveiller

- authentifications réussies et échouées ;
- demandes MFA refusées ou inhabituelles ;
- accès refusés et raison de la décision ;
- changements de groupes et de rôles ;
- enrôlement ou perte d'un appareil ;
- désactivation de compte ;
- modifications des règles d'accès ;
- connexions administratives ;
- anomalies de localisation ou de comportement, lorsque leur collecte est justifiée.

### Schéma de diagnostic

```text
ACCÈS REFUSÉ
     |
     v
1. Identifier l'utilisateur et la ressource
     |
     v
2. Lire le motif exact dans les journaux
     |
     +--> Identité / groupe incorrect ? --> Corriger le rôle
     |
     +--> MFA absent ou échoué ? --------> Vérifier méthode et session
     |
     +--> Appareil non conforme ? -------> Vérifier état et enrôlement
     |
     +--> Ressource ou règle incorrecte ? -> Examiner la politique
     |
     v
3. Refaire le test contrôlé
     |
     v
4. Documenter la cause et la correction
```

Ne pas contourner une politique en ajoutant une exception permanente simplement pour faire disparaître un refus. Comprendre d'abord la cause.


## 13. Erreurs fréquentes

1. **Déployer partout d'un seul coup.** Commencer par un pilote limité.
2. **Croire que MFA suffit.** Ajouter l'état de l'appareil et le moindre privilège selon le risque.
3. **Conserver des comptes partagés.** Utiliser des identités nominatives autant que possible.
4. **Laisser des règles trop larges.** Écrire explicitement les ressources et les rôles autorisés.
5. **Oublier les comptes de secours.** Prévoir une récupération contrôlée et testée.
6. **Ne pas lire les journaux.** Un refus sans diagnostic encourage les contournements.
7. **Ignorer les sessions déjà ouvertes.** Vérifier l'expiration, la révocation et la réévaluation.
8. **Confondre VLAN et Zero Trust.** La segmentation est une couche, pas l'architecture entière.
9. **Collecter trop de données.** Définir une finalité, limiter la conservation et protéger les journaux.
10. **Ne pas prévoir le retour arrière.** Toute modification d'accès doit avoir une procédure de récupération.


## 14. Projet de synthèse : protéger trois ressources

### Contexte

Une petite organisation dispose d'un portail RH, d'un dépôt de code et d'une console d'administration.

### Travail demandé

1. dresser le registre des trois ressources ;
2. définir les rôles autorisés ;
3. choisir les conditions d'identité et d'appareil ;
4. dessiner le chemin d'accès de chaque ressource ;
5. définir les décisions d'autorisation et de refus ;
6. écrire au moins cinq tests positifs et négatifs ;
7. préciser les événements à journaliser ;
8. définir une procédure de révocation ;
9. documenter le retour arrière ;
10. présenter les risques résiduels.

### Critères de réussite

- aucune ressource sensible n'est accessible uniquement parce que l'utilisateur est sur le LAN ;
- les rôles sont nominatifs et limités ;
- les refus sont expliqués et journalisés ;
- les comptes privilégiés disposent de protections renforcées ;
- le pilote peut être désactivé sans perdre l'accès de récupération ;
- les tests sont reproductibles et leurs résultats sont documentés.


## 15. Exercices avec corrigés

### Exercice 1 — utilisateur interne

Un utilisateur est connecté au Wi-Fi d'entreprise. Peut-on lui donner automatiquement accès à tous les serveurs ?

**Corrigé :** non. La connexion au Wi-Fi indique seulement une connectivité. Il faut évaluer l'identité, les droits, la ressource demandée et les conditions requises. La segmentation et les politiques doivent limiter les accès.

### Exercice 2 — MFA réussi, poste compromis

Un utilisateur a réussi le MFA, mais son poste ne respecte plus les règles de sécurité. Que faire ?

**Corrigé :** selon la politique, refuser ou limiter l'accès à la ressource sensible, journaliser la décision et orienter l'appareil vers une procédure de remédiation. Le MFA n'est pas une preuve que le poste est sain.

### Exercice 3 — VPN connecté

Un technicien se connecte au VPN. Doit-il accéder aux consoles de tous les équipements ?

**Corrigé :** non. Le VPN fournit un chemin réseau, pas une autorisation universelle. Les routes, ACL et contrôles d'identité doivent limiter l'accès aux équipements nécessaires.

### Exercice 4 — exception permanente

Une application bloque un utilisateur légitime. Un collègue propose d'autoriser tout le sous-réseau pour régler le problème. Est-ce acceptable ?

**Corrigé :** pas sans analyse. Il faut identifier le motif du refus, corriger le groupe ou la condition si nécessaire, puis retester. Une exception large crée un risque durable.

### Exercice 5 — compte désactivé

Un compte est désactivé, mais une session déjà ouverte continue de fonctionner. Pourquoi ?

**Corrigé :** certains jetons ou sessions restent valides jusqu'à leur expiration ou jusqu'à une révocation prise en charge. Il faut comprendre les mécanismes de session, tester la révocation et définir une réponse adaptée au risque.


## 16. Checklist de mise en œuvre

### Avant le pilote

- [ ] Ressource de test identifiée.
- [ ] Propriétaire métier et propriétaire technique désignés.
- [ ] Groupes et rôles vérifiés.
- [ ] MFA activé pour les comptes du pilote.
- [ ] Conditions liées à l'appareil définies si disponibles.
- [ ] Cas de refus et de réussite écrits.
- [ ] Journaux accessibles.
- [ ] Procédure de secours et retour arrière testée.

### Après le pilote

- [ ] Tous les tests exécutés et consignés.
- [ ] Refus inattendus analysés.
- [ ] Aucun contournement temporaire oublié.
- [ ] Accès des comptes privilégiés revu.
- [ ] Procédure de révocation testée.
- [ ] Utilisateurs informés des changements.
- [ ] Indicateurs de suivi définis avant extension.


## 17. Glossaire essentiel

- **Zero Trust :** approche qui supprime la confiance implicite et évalue les demandes d'accès selon une politique.
- **Identité :** représentation vérifiable d'un utilisateur, d'un service ou d'un appareil.
- **MFA :** authentification utilisant plusieurs facteurs distincts.
- **Moindre privilège :** droits minimaux nécessaires à une tâche.
- **PDP / moteur de décision :** fonction qui évalue la demande et décide.
- **PEP / point d'application :** fonction qui applique la décision d'accès.
- **ZTNA :** accès réseau orienté Zero Trust, souvent centré sur des applications précises.
- **Microsegmentation :** limitation fine des communications entre ressources ou groupes de ressources.
- **Posture de l'appareil :** état de conformité et de sécurité d'un appareil.
- **Révocation :** invalidation d'un droit, d'un identifiant, d'un certificat ou d'une session selon les mécanismes disponibles.
- **Journal d'audit :** trace des événements utiles à l'investigation et à la conformité.


## 18. Références pour continuer

- NIST SP 800-207, *Zero Trust Architecture* : https://csrc.nist.gov/pubs/sp/800/207/final
- CISA, *Zero Trust Maturity Model* : https://www.cisa.gov/zero-trust-maturity-model
- NIST SP 800-63B, recommandations sur l'authentification numérique : https://pages.nist.gov/800-63-4/sp800-63b.html

Consulter les versions officielles à jour avant de définir des exigences de conformité ou de sécurité.


## Conclusion

Zero Trust est une démarche progressive : **identifier les ressources, vérifier explicitement, appliquer le moindre privilège, limiter les communications et surveiller les résultats**. Pour débuter, protéger une seule application avec des tests positifs et négatifs est plus efficace que de déployer une politique générale impossible à vérifier. Une fois le pilote compris, documenté et réversible, l'organisation peut étendre les contrôles aux ressources plus sensibles.
