---
node_id: aaa-expert
title: Authentification réseau (AAA) - Expert
---

# Authentification réseau (AAA) - Expert

**Niveau :** EXPERT

Ce cours prolonge les niveaux Débutant et Intermédiaire. Il suppose que le lecteur sait distinguer authentification, autorisation et accounting, configurer une base AAA centralisée, appliquer des listes de méthodes sur Cisco IOS/IOS XE, utiliser TACACS+ pour l’administration, utiliser RADIUS pour l’accès réseau et 802.1X, interpréter les journaux courants et maintenir une voie de secours. Les bases ne sont donc pas reprises pas à pas : l’objectif est de concevoir, gouverner, sécuriser et exploiter AAA comme un service critique à l’échelle d’un réseau d’entreprise.

À ce niveau, le problème n’est plus simplement de faire réussir une connexion. Il faut garantir qu’une identité est correctement liée à une personne ou à un équipement, que le contexte de la demande est pris en compte, que les décisions restent cohérentes entre des centaines ou des milliers de points d’application, que les traces permettent de reconstituer les actions et que le service continue à fonctionner sans ouverture excessive des droits pendant une panne. Une politique AAA mal gouvernée peut transformer un service centralisé en point de défaillance commun à tout le réseau.

Le cours aborde l’architecture de confiance, les modèles de privilèges, la sécurité des transports, la gestion du cycle de vie des identités, les politiques dynamiques, les systèmes distribués, la résilience, la détection des abus, l’accounting comme preuve, les migrations et les scénarios de réponse à incident. Les exemples Cisco sont des modèles de laboratoire : leur syntaxe, leurs capacités exactes et leur comportement de repli dépendent de la version, de la plate-forme et du serveur AAA. Toute commande doit être validée dans la documentation de la version ciblée avant un changement en production.

> **Analogie** : un système AAA d’entreprise ressemble à une chaîne de contrôle d’accès composée d’un service d’identité, d’un bureau qui attribue des habilitations, de lecteurs de badges installés sur les portes et d’un système de journalisation inviolable. Le lecteur n’invente pas les droits ; il applique la décision qu’il sait comprendre. Le service central ne peut pas non plus compenser une porte mal configurée. La sécurité réelle dépend de l’ensemble : identité, politique, point d’application, canal de communication, preuve et procédure de secours.

---

## 1. La théorie et les algorithmes

### 1.1. Élever AAA au rang de service critique

L’architecture AAA doit être conçue comme un service de sécurité avec des objectifs de disponibilité, de cohérence et d’audit, pas comme une simple option de connexion. Une modification AAA peut bloquer simultanément l’accès SSH aux routeurs, l’administration des commutateurs, les VPN, le Wi-Fi, le réseau filaire 802.1X et certains accès d’urgence. Cette portée transversale impose une gouvernance plus stricte que celle d’une application ordinaire.

Il faut spécifier au minimum :

- **Périmètre d’identité** : administrateurs, opérateurs, sous-traitants, utilisateurs, comptes techniques, terminaux et équipements de réseau.
- **Points d’application** : routeurs, commutateurs, contrôleurs WLAN, pare-feu, concentrateurs VPN, solutions NAC, consoles et systèmes d’orchestration.
- **Décisions** : authentification simple ou multifacteur, rôles, autorisation par commande, profil réseau, VLAN, ACL, durée de session et politiques de réauthentification.
- **Qualité de service** : latence de décision, capacité de pointe, disponibilité, objectifs de reprise, comportement sur panne et limites de concurrence.
- **Preuves** : événements de connexion, commandes, changements de profil, refus, changements administratifs, événements du serveur et horodatage fiable.
- **Gouvernance** : propriétaires de rôles, approbation des droits, révision périodique, rotation de clés, procédure de changement et réponse aux incidents.

Une politique n’est complète que lorsqu’elle décrit non seulement le chemin normal, mais aussi les états dégradés : serveur indisponible, certificat expiré, annuaire lent, réplication en retard, compte désactivé, attribut absent, temps incorrect, perte de journaux ou compromission de la plateforme centrale. Une architecture qui autorise tout en cas de panne peut être disponible, mais elle est vulnérable. Une architecture qui refuse tout en cas de panne peut être sûre au sens strict, mais peut immobiliser une infrastructure critique. L’arbitrage doit être explicite, documenté et différencié selon le service.

### 1.2. Modéliser les domaines de confiance et les points d’application

Le serveur AAA ne protège pas à lui seul l’accès réseau. La décision dépend du client AAA, du réseau de transport, du serveur, de l’annuaire, des autorités de certification, des sources de groupes et parfois d’un moteur de politique ou d’un SIEM/SOAR. Chacun de ces composants possède ses propres comptes d’administration, ses propres journaux et sa propre surface d’attaque.

```text
                 PLAN D'IDENTITE ET DE POLITIQUE
        +----------------------------------------------+
        | Annuaire / IdP | Groupes | PKI | Moteur NAC   |
        +----------------------+-----------------------+
                               |
                      politique / attributs
                               v
 ADMIN -- SSH --> [Routeur / Switch / Firewall] <---> [AAA]
                         |              ^              |
                         |              |              v
                         |         Accounting      SIEM / SOC
                         |                             |
                         +------ accès local ---------+
                                  contrôlé
```

Il faut séparer au moins trois plans :

1. **Plan de contrôle d’identité** : création, validation, suspension, récupération et suppression des identités et authentificateurs.
2. **Plan de décision et d’application** : calcul des droits par le moteur de politique, transport vers les clients, interprétation par les équipements et application locale.
3. **Plan de preuve et de détection** : collecte, normalisation, corrélation, protection et exploitation des événements.

Ces plans peuvent partager des produits, mais ne doivent pas être confondus dans la conception. Par exemple, si la même console permet de modifier le groupe d’un administrateur, de changer les règles d’autorisation et d’effacer les journaux, une compromission de cette console peut servir à la fois à accorder un privilège, à l’utiliser et à masquer l’opération. Des contrôles de séparation des tâches doivent casser cette chaîne.

### 1.3. Distinguer identité, authentificateur, session et autorisation

Une identité n’est pas une preuve. Un nom d’utilisateur désigne une identité logique ; un mot de passe, une clé FIDO, un certificat ou un secret technique est un authentificateur ; une session représente une interaction autorisée à un instant donné ; un rôle décrit les opérations possibles. Mélanger ces concepts crée des erreurs telles que le partage d’un compte de groupe ou la conservation de privilèges après le départ d’un collaborateur.

Pour chaque accès sensible, le modèle devrait préciser :

- **Sujet** : utilisateur humain, processus, terminal ou équipement.
- **Preuve présentée** : mot de passe, certificat, clé matérielle, réponse EAP, jeton ou mécanisme propriétaire.
- **Contexte** : point de connexion, heure, posture du terminal, réseau d’origine, niveau de risque et état du service.
- **Décision** : refus, profil minimal, rôle, privilège ou autorisation d’une opération particulière.
- **Durée** : durée maximale de session, délai d’inactivité, expiration d’un privilège élevé et conditions de réauthentification.
- **Traçabilité** : identifiant de session stable, identité nominative, équipement cible, commandes et résultat.

Un certificat client authentifie en premier lieu la possession d’une clé privée associée à une identité de certificat. Il ne prouve pas automatiquement qu’un employé est encore autorisé à accéder au réseau. De la même façon, une authentification MFA réussie ne donne pas un rôle administrateur à un utilisateur qui ne le possède pas. La preuve d’identité et l’autorisation métier sont deux décisions distinctes.

### 1.4. Construire une matrice d’autorisation plutôt qu’une collection d’exceptions

L’autorisation fine devient vite ingérable si chaque utilisateur reçoit une liste spécifique de commandes. Il faut construire des rôles stables basés sur les fonctions et les responsabilités. Les rôles doivent être compréhensibles, limités, attribuables par un propriétaire métier et testables. L’héritage de rôles est possible, mais chaque héritage augmente la difficulté à expliquer pourquoi un utilisateur possède un droit.

| Rôle | Portée | Actions permises | Actions refusées explicitement | Preuve attendue |
|---|---|---|---|---|
| Observabilité | Équipements autorisés | Lire état, interfaces et journaux approuvés | Modifier la configuration, créer des comptes | Session et commandes consultatives |
| Exploitation N1 | Périmètre défini | Diagnostic de base, vérification et commandes de récupération sûres | Modifier routage, ACL ou identités | Ticket lié à la session |
| Ingénierie réseau | Équipements de son domaine | Changements de configuration approuvés | Administrer l’annuaire central ou effacer les traces | Changement approuvé, commandes et résultat |
| Sécurité AAA | Plateforme d’identité et politiques | Gérer les profils AAA et les clients enregistrés | Modifier les journaux historiques sans procédure dédiée | Approbation croisée et audit indépendant |
| Compte d’urgence | Portée minimale définie | Rétablir l’accès ou corriger une panne | Usage courant et tâches non urgentes | Alerte immédiate, motif et revue post-incident |

Un rôle peut être adapté par une règle contextuelle, mais les conditions doivent rester lisibles. Les exceptions doivent avoir un propriétaire, un motif, une date d’expiration et une preuve de validation. Les rôles temporaires sont préférables aux modifications permanentes de groupes pour résoudre un incident ponctuel.

> **Piège :** un profil « opérateur » qui permet `configure terminal` mais bloque quelques commandes dangereuses n’est pas nécessairement en lecture seule. Les commandes CLI sont souvent imbriquées, certaines permettent d’atteindre une commande privilégiée autrement et les alias varient selon la plateforme. L’autorisation des commandes doit être testée sur le chemin réel d’exécution, pas seulement évaluée à partir d’une liste textuelle.

### 1.5. Autorisation par commande : granularité, risques et limites

TACACS+ est souvent choisi pour les équipements réseau parce que les implémentations compatibles peuvent soumettre des demandes d’autorisation pour des commandes CLI. Le serveur reçoit typiquement des informations de service, de commande et d’arguments, puis autorise ou refuse. Le niveau exact de détail dépend de l’équipement, du logiciel, du mode CLI et de la façon dont le serveur exprime sa politique.

Une règle doit considérer le contexte complet : commande principale, sous-commandes, arguments, mode de configuration et effets de bord. Autoriser `show` en bloc est pratique, mais peut exposer des secrets, des clés ou des données sensibles dans certaines sorties. Autoriser toutes les commandes `clear` ou `debug` peut provoquer une interruption ou une charge importante. Autoriser `copy` peut permettre d’exporter des configurations ou d’écraser une image ; autoriser des commandes de sauvegarde sans contrôler la destination peut exfiltrer une configuration.

L’approche recommandée est de classer les commandes par impact :

- **Observation à faible risque** : état des interfaces, compteurs, version, routes selon la sensibilité des informations.
- **Diagnostic à risque modéré** : captures, débogage ciblé, tests de connectivité, commandes qui peuvent consommer des ressources.
- **Modification contrôlée** : changements d’interface, de VLAN, de routage ou de filtrage, exécutés dans le cadre d’un changement approuvé.
- **Actions critiques** : création d’utilisateurs, modification AAA, sauvegarde/restauration, mise à jour logicielle, effacement, changement de clés et réinitialisation.

L’autorisation par commande n’est pas une garantie d’approbation du changement. Elle confirme une permission technique, pas que le changement est légitime, nécessaire ou validé par le processus de gestion. Le système doit donc associer les sessions privilégiées à un ticket ou à un workflow d’approbation lorsqu’il s’agit d’une production sensible.

### 1.6. Séparation des privilèges et élévation temporaire

Le moindre privilège consiste à attribuer uniquement les droits nécessaires à une tâche déterminée. Il ne signifie pas qu’un administrateur doit passer toute sa journée dans un compte qui ne permet pas de travailler : il faut concevoir une élévation temporaire, contrôlée et traçable pour les opérations qui l’exigent.

Un modèle mature distingue les sessions ordinaires et les sessions privilégiées. L’identité de base sert à ouvrir une session et à lire les informations nécessaires. L’élévation vers le privilège supérieur exige une preuve appropriée, une justification et parfois une seconde approbation. Les autorisations sont limitées dans le temps ou à un périmètre précis. À la fin de l’intervention, les droits reviennent au niveau normal sans dépendre d’un nettoyage manuel.

La séparation peut s’exprimer par plusieurs identités nominatives liées à un même individu, mais ces identités doivent rester corrélables dans les journaux. Les comptes génériques partagés sont à éviter, sauf exception technique gouvernée. S’ils existent, leur usage doit être nominativement attribuable par un coffre-fort, un proxy de session ou un mécanisme de réservation audité ; un simple mot de passe partagé ne permet pas de reconstruire qui a agi.

> **Astuce :** pour chaque rôle privilégié, écris une phrase testable du type « peut effectuer A sur les équipements B, depuis la zone C, pendant D minutes, avec les traces E et l’approbation F ». Si la règle est impossible à exprimer clairement, elle est probablement trop large ou incomplète.

### 1.7. RADIUS, TACACS+ historique et transports modernes

Le choix du protocole doit partir du cas d’usage et des garanties attendues. RADIUS est courant pour l’accès au réseau, le Wi-Fi, les VPN et les décisions 802.1X. TACACS+ est fréquemment employé pour l’administration des équipements avec autorisation détaillée. Les deux ne sont pas interchangeables dans toutes les plateformes, et la prise en charge d’une extension ne doit jamais être déduite de la seule disponibilité d’une RFC.

TACACS+ historique utilise habituellement TCP/49. Son mécanisme historique de masquage du corps ne constitue pas un chiffrement moderne. RFC 8907 décrit le protocole TACACS+ ; RFC 9887, publiée en décembre 2025, spécifie un profil TACACS+ sur TLS 1.3, avec authentification mutuelle et le port TCP/300 par défaut. Pour ce profil TLS, le client ne doit pas envoyer de données TACACS+ avant la fin de la négociation TLS et ne doit pas revenir silencieusement à la variante non TLS si l’établissement TLS échoue. Il faut vérifier explicitement que les équipements, les serveurs et leurs versions prennent en charge ce profil : un extrait de configuration TACACS+ classique n’active pas automatiquement TLS.

RADIUS classique est défini notamment par RFC 2865 et RFC 2866, historiquement sur UDP. RADIUS sur TLS a été spécifié par RFC 6614 comme expérimental. RFC 9765 décrit également RADIUS/1.1 négocié via ALPN dans le cadre RADIUS/TLS ou DTLS ; cette spécification est expérimentale et ne change pas RADIUS/UDP. L’existence de ces documents ne prouve pas que la fonctionnalité est disponible partout ni qu’elle convient sans analyse. Le projet doit vérifier la compatibilité, les certificats, la validation du pair, la supervision, le comportement sur perte du canal et la configuration de bout en bout.

| Scénario | Piste de conception | Contrôles à vérifier |
|---|---|---|
| Administration CLI de routeurs | TACACS+ si autorisation par commande prise en charge | TLS disponible, authentification des pairs, autorisation réelle des arguments |
| Wi-Fi ou filaire 802.1X | RADIUS avec méthode EAP adaptée | Certificats, validation de l’identité du serveur, profils de terminaux |
| VPN utilisateur | RADIUS ou intégration native à un fournisseur d’identité | MFA, attributs de groupe, posture, expiration et révocation |
| Réseau industriel ancien | Transition progressive avec segmentation stricte | Compatibilité, exposition du protocole, plan de remplacement et suivi du risque |
| Interconnexion intersites | Transport protégé et zones de gestion dédiées | Routage, filtrage, validation des certificats, synchronisation et journalisation |

### 1.8. PKI, certificats et gestion du cycle de vie

Les certificats introduisent des dépendances que le mot de passe ne révèle pas toujours : chaîne de certification, usages autorisés, nom du service, dates de validité, révocation, renouvellement et distribution de la confiance. Un certificat correctement signé peut néanmoins être inacceptable s’il est délivré à la mauvaise identité, s’il est expiré, s’il ne possède pas le bon usage ou si le client ne vérifie pas la correspondance avec le serveur attendu.

Une politique PKI AAA doit définir :

1. les autorités auxquelles les clients font confiance ;
2. les identités attendues dans le champ Subject Alternative Name ;
3. les usages de clé et les usages étendus nécessaires ;
4. le processus de délivrance et de renouvellement ;
5. la distribution des certificats et des chaînes de confiance ;
6. le traitement de la révocation et des autorités compromises ;
7. les alertes d’expiration ;
8. les procédures de remplacement en cas de panne ou de perte de clé privée.

Les certificats de client AAA et les certificats d’utilisateur final ne doivent pas être confondus. Le certificat qui authentifie un commutateur auprès du serveur RADIUS n’est pas forcément celui qui authentifie le terminal 802.1X. Des autorités, des profils et des règles distincts limitent la possibilité qu’un certificat destiné à un usage serve à un autre.

Il faut également tenir compte des dépendances d’infrastructure. Si la validation du certificat nécessite une consultation OCSP ou CRL et que le service de révocation est injoignable depuis une zone isolée, l’authentification peut échouer ou adopter un comportement de secours particulier. Le comportement doit être documenté pour chaque produit : certains valident en cache, certains échouent de manière fermée, d’autres peuvent différer le contrôle. Aucune hypothèse implicite ne doit être acceptée pour un service critique.

### 1.9. Identité humaine, identité machine et fédération

L’AAA réseau gère des identités humaines mais aussi des terminaux, des équipements, des services et des processus automatisés. Ces catégories ne doivent pas utiliser le même modèle de preuve. Une personne peut utiliser une clé matérielle ou un autre authentificateur interactif ; un commutateur doit normalement présenter des informations de confiance provisionnées de manière contrôlée ; un pipeline d’automatisation devrait utiliser une identité de service non interactive, avec portée et durée limitées.

La fédération d’identité permet à un fournisseur d’identité de produire une assertion consommée par un service. Cette assertion peut porter une identité, des groupes ou des attributs. Un équipement réseau ne sait pas nécessairement consommer directement SAML ou OpenID Connect ; une couche d’intégration peut traduire la décision vers RADIUS, TACACS+ ou une API propriétaire. Cette traduction devient un point critique : elle doit préserver l’identité, la signification des groupes, l’expiration, les refus et la provenance des attributs.

Une intégration mal conçue peut provoquer une confusion de rôle : un groupe portant le même nom dans deux domaines distincts peut être interprété comme équivalent ; une identité invitée peut être liée à un compte interne ; un attribut manquant peut déclencher un rôle par défaut trop puissant. Il faut privilégier des identifiants stables, des correspondances explicites et des tests de collision de noms.

### 1.10. MFA et résistance au phishing

Le MFA associe plusieurs catégories de preuves, par exemple possession et connaissance. Pourtant, tous les facteurs n’offrent pas la même résistance au phishing. Un code à usage unique peut être relayé en temps réel par un attaquant ; une notification push peut être approuvée par fatigue ou ingénierie sociale ; une méthode cryptographique liée au site ou au contexte est généralement mieux adaptée aux accès les plus sensibles.

La sélection doit être fondée sur le risque : administration distante, comptes de domaine, accès au serveur AAA, modification des politiques, compte d’urgence et opérations de sécurité nécessitent une attention renforcée. Les recommandations NIST SP 800-63B-4, publiée en juillet 2025, donnent un cadre actualisé pour les authentificateurs et leur gestion. Elles ne remplacent pas l’analyse locale : le secteur, la réglementation, les équipements hérités et les exigences de continuité peuvent imposer des contraintes supplémentaires.

Le MFA appliqué en amont d’un portail de gestion ne se transmet pas automatiquement à une connexion CLI directe. Il faut vérifier où le facteur est demandé, comment la décision est associée à la session, si une session déjà ouverte demeure valide après révocation, et comment les comptes de service non interactifs sont authentifiés. Une promesse de « MFA partout » doit être prouvée par une matrice des chemins d’accès, pas par la seule présence d’un fournisseur d’identité.

### 1.11. 802.1X, EAP, posture et politiques dynamiques

Dans un réseau filaire ou Wi-Fi, 802.1X et EAP mettent en relation le supplicant, l’authenticator et le serveur d’authentification. La décision RADIUS peut produire un profil réseau, un VLAN, des filtres ou des attributs constructeur si les équipements compatibles les interprètent. Une réponse `Access-Accept` ne signifie pas nécessairement « accès intégral » : les attributs de politique et la configuration locale déterminent le résultat.

Pour un déploiement avancé, il faut établir une taxonomie d’identités : terminal d’entreprise géré, terminal personnel, invité, imprimante, équipement industriel, téléphone IP, appareil inconnu et poste en quarantaine. Chaque classe doit avoir un profil réseau minimal, des exceptions contrôlées et une procédure d’enrôlement. L’adresse MAC ou le profilage passif peut aider à catégoriser certains équipements, mais une adresse MAC peut être usurpée et ne constitue pas une authentification forte.

La posture peut inclure l’état du système, les mises à jour, un agent, la présence d’un certificat, le niveau de chiffrement ou l’adhésion à un domaine. Le résultat peut influencer l’autorisation, mais la source de posture doit être évaluée : une information ancienne, falsifiée ou indisponible ne doit pas être traitée comme une preuve certaine. Il faut définir les délais de validité, le comportement en cas de doute et les possibilités de mise en quarantaine.

Le changement dynamique de VLAN ou de politique pendant une session exige un contrôle de bout en bout. Il faut vérifier la prise en charge de CoA/Disconnect par les équipements, la protection et la source autorisée des messages, l’effet sur les sessions actives, les limites de l’authenticator et la cohérence entre les journaux RADIUS et ceux du commutateur. Une politique annoncée par le serveur mais non appliquée par le commutateur crée un faux sentiment de sécurité.

### 1.12. Le problème du fallback : panne, rejet et résultat indéterminé

Le comportement de secours est l’une des parties les plus délicates d’AAA. Il faut séparer au moins quatre états :

- **Acceptation explicite** : le serveur a validé l’identité et renvoyé une décision positive.
- **Rejet explicite** : le serveur a refusé la demande ; cela ne devrait généralement pas déclencher un compte local alternatif pour contourner la politique.
- **Absence de réponse** : expiration du délai, perte réseau, serveur arrêté ou saturation ; un mécanisme de secours peut être prévu selon le service.
- **Erreur de confiance ou de protocole** : secret incohérent, certificat non valide, désaccord de chiffrement ou message mal formé ; ce cas ne doit pas être assimilé automatiquement à une simple indisponibilité.

La logique recherchée ressemble à une machine à états, et non à une longue liste de commandes mémorisées :

```text
                +----------------------+
                | Demande d'accès      |
                +-----------+----------+
                            |
                            v
                   +--------+--------+
                   | Réponse AAA ?   |
                   +--+----------+---+
                      |          |
                 explicite      aucune réponse
                  /     \            |
                 v       v           v
             ACCEPT    REJECT     appliquer la
                 |       |        politique panne
                 v       v           |
             rôle prévu  refus      +-------------------+
                                   | secours limité ou |
                                   | refus fermé selon  |
                                   | le service         |
                                   +-------------------+
```

Dans plusieurs implémentations, le comportement exact de listes de méthodes et des mots-clés de repli varie selon le service AAA. Il faut le confirmer dans la documentation, puis le valider par des tests qui isolent panne réseau, serveur arrêté, rejet d’identité, secret incorrect et mauvais certificat. La disponibilité du serveur ne doit pas servir d’excuse à une élévation silencieuse de privilège.

> **Danger :** ne traite jamais un refus explicite comme si le serveur était indisponible. Un tel comportement peut donner à un compte local la possibilité de contourner une désactivation centrale ou une politique de refus. Le secours doit répondre à un état précis, et non à l’objectif vague de « laisser l’accès fonctionner ».

### 1.13. Haute disponibilité et cohérence distribuée

Deux serveurs AAA ne forment pas automatiquement un service résilient. Il faut comprendre comment les politiques, les secrets, les clés privées, les bases d’identité, les certificats, les journaux et les informations de session sont répliqués. Une réplication asynchrone peut produire un état où un compte est désactivé sur le serveur principal mais encore accepté sur un nœud secondaire. La redondance améliore la disponibilité, mais peut élargir la fenêtre d’incohérence.

Les points d’architecture à formaliser sont :

- **Topologie** : actifs-actifs, actif-passif, sites distincts, zones de confiance et liens de secours.
- **Sélection du serveur** : ordre de préférence, répartition de charge, affinité de session et critères de bascule.
- **Réplication** : délai, conflits, horodatage, traitement des suppressions et mode de récupération.
- **Cohérence** : version de politique, identités désactivées, groupes, certificats révoqués, secrets et listes de clients autorisés.
- **Observabilité** : latence par serveur, timeouts, erreurs de transport, files d’attente, CPU, mémoire, connexions actives et erreurs de base de données.
- **Reprise** : restauration de sauvegarde, restauration de certificats et clés, retour sur le site primaire, reconstruction et exercice périodique.

Les sondes de disponibilité ne doivent pas s’appuyer seulement sur un ping. Un serveur peut répondre à ICMP alors que l’authentification est impossible, ou refuser des demandes tout en étant joignable. Les contrôles doivent tester un parcours représentatif, sans créer de fausses sessions privilégiées ni générer des comptes de test permanents. Un compte technique de surveillance doit avoir des droits minimaux et une identité facilement reconnaissable dans les journaux.

### 1.14. Latence, capacité et stratégie de timeouts

Le délai AAA s’ajoute au temps perçu par l’utilisateur. Pour l’accès filaire, un timeout excessif peut retenir un port dans un état transitoire ; pour la gestion SSH, il peut donner l’impression que l’équipement est indisponible ; pour un VPN, il peut provoquer une succession de tentatives ; pour un réseau à grande échelle, les nouvelles tentatives peuvent amplifier une panne.

La capacité doit être évaluée à partir des pointes : reprise après panne, redémarrage de commutateurs, ouverture de classe, début de service, réauthentification périodique ou renouvellement de sessions. Un scénario d’échec peut être plus exigeant que le fonctionnement nominal si les clients réessaient en boucle. Les files d’attente, connexions et limites de débit des serveurs doivent être mesurées sous charge représentative.

Une stratégie utile associe : délais raisonnables, nombre contrôlé de tentatives, délais exponentiels ou jitter quand ils sont disponibles, limitation des demandes anormales et supervision de la saturation. Ces recommandations doivent être adaptées au comportement réellement supporté par le client AAA. Ne modifie pas simultanément les timeouts de tous les équipements sans test : une valeur qui résout un réseau lent peut rendre une panne centrale beaucoup plus coûteuse.

### 1.15. Accounting, horodatage et qualité des preuves

L’accounting n’est pas seulement un journal de confort. Il peut être nécessaire pour reconstruire une action, prouver l’usage d’un privilège, expliquer une interruption, analyser une compromission et démontrer que les contrôles sont opérationnels. Pour être fiable, une trace doit être complète, attribuable, horodatée, protégée contre l’altération et conservée selon une politique définie.

Un événement de session utile comporte idéalement l’identité, l’équipement, le type d’accès, l’adresse source, le résultat, la méthode d’authentification, les attributs de rôle, un identifiant de session, les heures de début et de fin, le motif de fermeture et la référence du changement si disponible. Toutes les plateformes ne fournissent pas tous ces champs. Il faut donc mesurer les lacunes et ne pas supposer que le serveur AAA peut connaître l’intégralité d’une session CLI.

Les commandes enregistrées dans TACACS+ peuvent offrir une meilleure visibilité sur certaines opérations, mais elles ne remplacent ni la sauvegarde de configuration, ni la journalisation de la plateforme, ni un système de contrôle de changement. Une commande approuvée peut échouer ; une commande refusée peut être suivie d’une autre voie d’accès ; une commande complexe peut modifier plusieurs objets. Les traces doivent être corrélées avec le système de gestion des changements, les journaux système, les alertes du SIEM et les événements du serveur d’identité.

La synchronisation horaire est un prérequis. Des écarts entre contrôleurs de domaine, serveurs AAA, équipements de réseau, PKI et SIEM rendent difficile la corrélation. Chaque source doit avoir une configuration NTP cohérente, une alerte en cas de dérive et des métadonnées qui permettent de connaître sa qualité temporelle. Une horloge correcte aujourd’hui ne prouve pas que l’horloge était correcte au moment d’un incident : les corrections et dérives doivent aussi être traçables.

### 1.16. Détection des abus et signaux d’attaque

Les événements AAA forment une source d’indicateurs de sécurité. Les signaux utiles incluent des échecs répétés sur de nombreux équipements, une réussite à la suite d’une série d’échecs, une connexion depuis une zone inhabituelle, un usage d’un compte dormant, une élévation en dehors d’une fenêtre approuvée, un changement d’attribut massif, des tentatives vers des clients AAA inconnus ou un nombre inhabituel de refus de commande.

Une seule règle d’alerte ne suffit pas. Il faut définir la logique de corrélation et son contexte. Dix échecs venant d’une adresse partagée peuvent correspondre à une faute de saisie ou à un mot de passe diffusé ; une réussite juste après peut être légitime ou indiquer une compromission. Les seuils doivent tenir compte du profil des utilisateurs, de l’architecture NAT/proxy et des activités planifiées. Les alertes doivent avoir une action attendue, un propriétaire et des critères de clôture.

Le SIEM doit normaliser les noms d’utilisateurs, les noms d’équipement, les adresses, les résultats et les identifiants de session sans perdre les valeurs originales nécessaires à l’investigation. Le filtrage d’événements côté collecteur doit éviter de supprimer les refus, les changements de rôle ou les événements de sécurité « bruyants ». Les informations sensibles présentes dans les commandes doivent être masquées ou protégées, mais le masquage ne doit pas rendre impossible la compréhension du changement.

### 1.17. Zero Trust et décision contextuelle

Le modèle Zero Trust ne signifie pas « demander un mot de passe à chaque paquet ». Il repose sur une vérification explicite de l’identité et du contexte, l’application du moindre privilège, la segmentation des ressources et une réévaluation adaptée au risque. NIST SP 800-207 constitue une référence de conception pour l’architecture Zero Trust ; elle ne prescrit pas un produit AAA particulier.

Dans une architecture de ce type, AAA peut être l’un des mécanismes qui contribuent à la décision d’accès. La politique peut tenir compte de la force de l’authentification, du rôle, de l’état du terminal, du réseau de provenance, de la sensibilité de la cible, du risque détecté et de la fraîcheur des signaux. Cependant, un contexte absent ne doit pas être interprété implicitement comme un contexte sûr. Si la source de posture est indisponible, la politique devrait prévoir une décision de réduction de droits ou une voie de remédiation plutôt qu’une autorisation complète automatique.

La décision ne devrait pas être plus permissive que nécessaire pour des raisons de commodité. Par exemple, le fait qu’un administrateur ait une session VPN ne signifie pas qu’il doit administrer tous les équipements. Une session peut être autorisée pour un seul bastion, depuis lequel un autre contrôle AAA applique des rôles plus fins. Les décisions successives doivent être cohérentes et leurs identifiants de corrélation transmis lorsque la plateforme le permet.

### 1.18. Menaces contre les clients et serveurs AAA

AAA est une cible à haute valeur. Une compromission du serveur peut permettre de modifier des autorisations à grande échelle ; une compromission d’un client AAA peut permettre de voler les secrets partagés ou d’usurper un équipement ; une compromission de l’annuaire peut accorder des rôles ; une altération du SIEM peut masquer les preuves.

Les contrôles défensifs comprennent :

- isoler les interfaces d’administration et n’autoriser que les sources nécessaires ;
- réduire les flux réseau entre clients AAA et serveurs aux protocoles, adresses et ports attendus ;
- utiliser un secret unique par client lorsque le protocole classique l’exige et qu’il est supporté ;
- privilégier un transport moderne avec authentification du pair lorsque la plateforme le prend en charge ;
- protéger les clés privées dans un coffre ou un HSM si adapté ;
- appliquer une gestion des correctifs et limiter les services installés sur les serveurs AAA ;
- protéger les sauvegardes, les exports de politique et les journaux ;
- séparer les rôles d’administration du service AAA, de l’annuaire et du SIEM ;
- surveiller les modifications de clients, de secrets, de politiques et d’autorités de certification.

Les protections réseau ne remplacent pas le transport sécurisé. Un réseau de gestion isolé réduit l’exposition, mais un initié, un équipement compromis ou une mauvaise route peut toujours accéder à ce réseau. La défense doit donc cumuler segmentation, authentification mutuelle, limitation des privilèges et détection.

### 1.19. Gestion de configuration, dérive et contrôle de conformité

Une flotte d’équipements peut dériver même si chaque serveur AAA est correctement configuré. Certains équipements peuvent pointer vers un ancien serveur, appliquer une liste de méthodes différente, conserver un compte local oublié, manquer l’accounting des commandes ou ne pas prendre en charge une fonction de transport récente. La conformité AAA doit donc être mesurée du point de vue du parc.

Il est utile de maintenir un inventaire contenant : modèle, version logicielle, type de client AAA, serveurs utilisés, adresses source, suites de méthodes, profils d’autorisation, modes de secours, paramètres de journalisation et statut de compatibilité avec les transports modernes. Des contrôles automatisés peuvent comparer l’état observé à une référence approuvée et ouvrir un ticket en cas de divergence. Les secrets ne doivent évidemment pas être inclus en clair dans les rapports de conformité.

La normalisation ne signifie pas rendre tous les équipements strictement identiques. Un commutateur d’accès 802.1X, un routeur de cœur et un pare-feu peuvent avoir des besoins distincts. Il faut définir des profils par fonction et accepter les exceptions uniquement lorsqu’elles sont justifiées, testées et suivies dans le temps.

> **Astuce :** mesure la conformité à partir de la configuration réellement appliquée sur les équipements, puis confronte-la aux politiques du serveur AAA. Une politique centrale parfaite ne prouve pas que tous les clients l’utilisent.

### 1.20. Algorithme de décision AAA de référence

Le pseudocode suivant sert à raisonner sur une politique, pas à reproduire le code interne d’un produit.

```text
fonction decision_AAA(demande):
    vérifier que le client est enregistré et attendu
    vérifier le canal et l'identité du pair
    si canal non fiable ou client inconnu:
        journaliser et refuser

    identité = résoudre_identité(demande)
    preuve = vérifier_authentificateur(demande)
    si preuve invalide:
        journaliser un échec et refuser

    contexte = collecter_contexte(demande)
    si contexte obligatoire absent ou trop ancien:
        choisir refus ou profil de remédiation

    rôles = charger_rôles_et_attributs(identité)
    droits = calculer_droits_minimaux(rôles, contexte)
    si demande non couverte par droits:
        journaliser le refus et refuser

    créer identifiant de session corrélable
    appliquer la décision au point d'accès
    enregistrer identité, contexte, décision et version de politique
    retourner autorisation limitée
```

Ce modèle doit intégrer le traitement explicite des erreurs, des timeouts et du cache. Il ne faut pas conserver une décision en cache au-delà de la durée prévue, en particulier pour les désactivations de comptes et les retraits de privilèges. Le cache peut améliorer la disponibilité, mais il étend la période pendant laquelle une information ancienne reste applicable. Cette fenêtre doit être choisie en fonction de la sensibilité de l’accès.

---

## 2. Configuration et pratique

### 2.1. Objectifs du laboratoire expert

Ce laboratoire construit une stratégie d’administration de routeurs et de commutateurs avec TACACS+ classique sur Cisco IOS/IOS XE, des rôles différenciés, l’accounting des commandes et une procédure de validation qui ne dépend pas d’un seul test de connexion. Il ne prétend pas activer TACACS+ sur TLS : l’utilisation de RFC 9887 exige une prise en charge explicite par les versions et les produits utilisés, et les commandes de configuration varient selon les constructeurs.

Scénario :

- `R1` est un routeur de laboratoire à l’adresse de gestion `192.0.2.11` ;
- `SW1` est un commutateur à l’adresse de gestion `192.0.2.12` ;
- le serveur AAA est à `192.0.2.50` ;
- le poste d’administration se trouve dans le réseau `192.0.2.0/24` ;
- le réseau de gestion est isolé du réseau utilisateur ;
- un accès console ou hors bande est testé et disponible pendant le changement.

Les adresses du bloc TEST-NET sont réservées à la documentation. Remplace-les dans un laboratoire réel et ne copie pas ces exemples tels quels dans une production.

```text
 Poste admin
 192.0.2.100
      |
      | SSH depuis zone de gestion uniquement
      v
 +-------------------+        flux AAA filtré        +----------------+
 | R1 192.0.2.11     | ----------------------------> | AAA 192.0.2.50 |
 | SW1 192.0.2.12    | ----------------------------> | TACACS+        |
 +-------------------+                               +----------------+
      |
      +---- accès console / hors bande pour secours
```

### 2.2. Préparer le changement et les preuves initiales

Avant de configurer AAA, sauvegarde la configuration, note la version exacte, la méthode actuelle d’administration et les comptes locaux, puis vérifie l’accès console ou hors bande. Garde une session existante ouverte pendant la modification et utilise une deuxième session pour tester. Sur un équipement distant, la procédure doit comprendre un moyen de revenir à l’état précédent si la nouvelle politique coupe SSH.

Établis une matrice initiale : connexion nominative autorisée, mauvais mot de passe refusé, compte désactivé refusé, serveur injoignable, serveur secondaire utilisé, autorisation de commande accordée, autorisation refusée, accounting reçu et rétablissement après retour du serveur. Enregistre la configuration initiale et les versions de fichiers de politique ; sans état de référence, il devient difficile de distinguer l’effet de ton changement d’une dérive antérieure.

### 2.3. Exemple IOS/IOS XE pour un groupe TACACS+ classique

Le modèle suivant illustre une configuration traditionnelle. Les commandes `tacacs server`, `aaa group server tacacs+`, `aaa authentication`, `aaa authorization` et `aaa accounting` sont présentes sur de nombreuses versions IOS/IOS XE, mais la syntaxe exacte doit être vérifiée dans le guide de configuration de la version. Le serveur doit être déclaré comme client connu et utiliser le même secret que l’équipement. Ne place pas de secret de production dans un dépôt de code ou un document non protégé.

```text
! Exemple de laboratoire uniquement
hostname R1
ip domain name lab.example
!
username secours privilege 15 secret <SECRET_LOCAL_FORT_ET_UNIQUE>
!
! Vérifier les capacités et la syntaxe de la version avant application
 tacacs server AAA-1
  address ipv4 192.0.2.50
  key <SECRET_TACACS_LONG_UNIQUE>
!
 aaa group server tacacs+ AAA-GROUP
  server name AAA-1
!
 aaa new-model
 aaa authentication login ADMIN-LOGIN group AAA-GROUP local
 aaa authorization exec ADMIN-EXEC group AAA-GROUP local
 aaa authorization commands 15 ADMIN-CMD group AAA-GROUP local
 aaa accounting exec ADMIN-ACCT start-stop group AAA-GROUP
 aaa accounting commands 15 ADMIN-CMD-ACCT start-stop group AAA-GROUP
!
 line vty 0 15
  transport input ssh
  login authentication ADMIN-LOGIN
  authorization exec ADMIN-EXEC
  accounting exec ADMIN-ACCT
```

Cet extrait est un schéma de configuration, pas une configuration universelle à coller telle quelle. Selon la version, la ligne qui associe l’autorisation de commandes, le niveau de privilège, la méthode `local` et les noms des listes peut différer. Certaines fonctions d’accounting peuvent nécessiter une association différente. Vérifie `?`, la documentation du train logiciel et le comportement effectif des sessions avant de déployer.

La liste `group AAA-GROUP local` illustre un mécanisme de méthodes de secours, mais ne prouve pas que le comportement du produit correspond exactement à l’intention métier. Il faut notamment tester comment un `REJECT` explicite se distingue d’un timeout, et si la méthode locale est consultée en cas d’erreur de protocole. Si la réponse à ces questions n’est pas connue, ne déploie pas cette liste sur des équipements critiques.

### 2.4. Sécuriser la méthode d’accès et la source des demandes

L’administration distante doit être limitée au protocole nécessaire, généralement SSH, et aux réseaux de gestion autorisés. La source utilisée par l’équipement pour envoyer les demandes AAA doit être stable et enregistrée côté serveur. Une source inattendue peut être rejetée comme client inconnu, mais elle peut également révéler une route ou une configuration erronée.

Exemple à adapter à la topologie :

```text
interface Loopback0
 description Source stable pour les services de gestion
 ip address 192.0.2.11 255.255.255.255
!
! La commande ip tacacs source-interface ou son équivalent,
! si disponible, doit correspondre à l'adresse déclarée côté serveur.
! Vérifier le routage retour et le support de l'adresse choisie.
```

Une interface loopback est utile si le routage permet d’atteindre le serveur et de recevoir ses réponses. Elle ne doit pas être utilisée de façon automatique : la source choisie doit être annoncée et filtrée correctement, et l’acheminement de retour doit être vérifié. Si une zone de management utilise une interface physique spécifique, une adresse de cette zone peut être plus appropriée.

Le filtrage réseau doit limiter les échanges aux clients AAA connus et aux ports réellement requis. Les règles sont différentes pour TACACS+ classique, TACACS+ sur TLS, RADIUS classique ou RADIUS sur TLS. N’ouvre pas simultanément tous les ports « au cas où ». Documente le port source, la destination, le sens initiateur, le mécanisme de réponse et les besoins d’accounting ou de CoA.

### 2.5. Rôles de commandes : approche et tests

Côté serveur, crée des profils séparés pour l’observation, l’exploitation et l’ingénierie. Pour chacun, liste les commandes autorisées, les arguments acceptés et les opérations explicitement interdites. Les profils doivent être testés sur les équipements réels ou un environnement de même version, car une politique qui fonctionne sur un routeur ne garantit pas qu’elle fonctionnera sur un commutateur ou un pare-feu.

| Test | Observabilité | Exploitation | Ingénierie |
|---|---|---|---|
| Connexion SSH nominative | Autorisée | Autorisée | Autorisée |
| Afficher version/interfaces | Autorisé | Autorisé | Autorisé |
| Afficher certaines données sensibles | Refusé ou masqué selon besoin | Limité | Selon rôle |
| Passer en mode configuration | Refusé | Refusé sauf procédure dédiée | Autorisé si changement approuvé |
| Modifier une interface de production | Refusé | Refusé | Contrôlé et journalisé |
| Créer un compte local ou modifier AAA | Refusé | Refusé | Réservé à un rôle AAA spécialisé |
| Effacer ou purger les traces | Refusé | Refusé | Refusé en usage ordinaire ; procédure séparée |

Les noms et groupes sont indicatifs. La politique effective dépend des commandes d’autorisation réellement envoyées par le client et interprétées par le serveur. Utilise les journaux de requête pour déterminer la commande, les arguments et le service reçus ; ne construis pas les règles sur une supposition.

### 2.6. Protéger le compte de secours

Le compte local d’urgence est une exception de continuité, non un compte d’usage courant. Il doit être nominativement contrôlé ou livré par un coffre-fort selon une procédure approuvée, avec un secret unique, une restriction de source si la plateforme le permet, une alerte dès son utilisation et un changement du secret après une intervention si le modèle de coffre l’exige.

Le compte de secours doit être testé périodiquement sans le laisser constamment ouvert. L’organisation doit connaître les équipements qui n’ont pas de voie hors bande et décider explicitement si le risque de verrouillage à distance est acceptable. Si la politique locale est plus permissive que la politique centrale, la différence doit être minimale et documentée. Un compte local de privilège 15 qui contourne toute autorisation par commande n’est pas un secours limité ; c’est une porte d’administration complète.

> **Piège :** ajouter `local` comme méthode de repli peut préserver l’accès, mais peut également permettre à un compte local ancien ou trop privilégié de contourner les contrôles centraux lors d’un problème de transport. La sécurité dépend de la distinction entre panne, rejet explicite et erreur de confiance, ainsi que de l’inventaire des comptes locaux.

### 2.7. Validation du parcours AAA

N’utilise pas un seul test « je peux me connecter » comme preuve de succès. Le compte de test doit être essayé avec plusieurs états. Le tableau suivant constitue le minimum ; ajoute des cas propres au produit et au contexte.

| Scénario | Résultat attendu | Contrôle du côté client | Preuve côté serveur |
|---|---|---|---|
| Utilisateur autorisé, rôle attendu | Connexion et droits conformes | Session SSH, commandes représentatives | Acceptation, identité et attributs |
| Secret incorrect | Refus | Aucune session privilégiée | Échec d’authentification |
| Compte désactivé | Refus central | Aucune élévation locale implicite | Refus lié à l’identité |
| Commande non autorisée | Commande refusée | Message cohérent, autres droits inchangés | Décision d’autorisation négative |
| Serveur secondaire seul disponible | Service maintenu selon design | Serveur choisi, délai acceptable | Journal sur le nœud secondaire |
| Tous les serveurs injoignables | Comportement de panne documenté | Secours restreint ou refus fermé | Alarme de disponibilité |
| Certificat ou canal invalide | Refus sécurisé | Pas de rétrogradation non contrôlée | Erreur TLS/certificat enregistrée |
| Horloge décalée | Détection et correction contrôlée | Diagnostic temporel | Événement de dérive et rétablissement |
| Accounting interrompu | Alerte et procédure de continuité | Droit d’accès maintenu ou restreint selon politique | Lacune de journalisation détectée |

La validation doit inclure des tests négatifs. Pour les rôles, essaie les commandes normalement autorisées et celles qui devraient échouer. Pour les transports TLS, contrôle la validation réelle des certificats, le rejet d’un certificat non approuvé et l’absence de repli en clair. Pour la haute disponibilité, coupe réellement l’accès au nœud primaire dans un environnement contrôlé, plutôt que de simplement arrêter une sonde de surveillance.

### 2.8. RADIUS et 802.1X : politique par classe de terminal

Dans un labo de contrôle d’accès réseau, distingue les postes gérés, appareils d’infrastructure, terminaux invités et appareils inconnus. Utilise EAP-TLS si le cycle de certificats et la compatibilité le permettent ; toute autre méthode doit être choisie en connaissance de ses propriétés et limites. Le point déterminant est la validation par le supplicant de l’identité du serveur d’authentification, afin d’éviter d’envoyer des preuves à un faux serveur.

Les attributs RADIUS qui attribuent un VLAN, un filtre ou un profil doivent être cohérents avec la configuration du commutateur ou du contrôleur. Vérifie l’effet de la politique dans l’équipement d’accès, puis teste la connectivité réellement permise. Un journal `Access-Accept` n’est qu’une partie de la preuve : le port peut appliquer un VLAN par défaut, un filtre local ou un état d’authenticator inattendu.

Pour les équipements sans supplicant 802.1X, une exception peut être nécessaire. L’exception doit être limitée par le port, le profil d’appareil, la segmentation, les flux autorisés et une date de révision. La seule correspondance d’une adresse MAC ne doit pas être présentée comme équivalente à une authentification forte. Il faut documenter le risque résiduel et le plan de modernisation lorsque cela est possible.

### 2.9. Accounting et corrélation SIEM

Le serveur AAA envoie ou conserve ses propres événements, mais le SIEM doit aussi recevoir les logs utiles des équipements, de l’annuaire, de la PKI et de la gestion de configuration. Un schéma de normalisation devrait comporter : horodatage d’origine, horodatage de réception, source, identité, client AAA, cible, protocole, type d’événement, résultat, rôle, identifiant de session et référence de changement si disponible.

```text
Équipement -- session/commandes --> AAA -- événements --> SIEM
     |                              |                    |
     | syslog / configuration       | événements service | corrélation
     +------------------------------+--------------------+
                                      annuaire / PKI
```

Conserve la provenance de chaque champ. Si le SIEM enrichit un nom d’utilisateur depuis l’annuaire, garde la valeur originale qui a été observée au moment de l’événement. Si le nom a été renommé depuis, la résolution actuelle ne doit pas écraser l’identité historique. Les journaux doivent être protégés contre l’altération par les mêmes administrateurs qui peuvent modifier la politique AAA, ou exportés vers une zone à contrôle séparé.

### 2.10. Stratégie de migration vers un transport sécurisé

Une migration du TACACS+ classique vers TACACS+ sur TLS ou de RADIUS/UDP vers une variante protégée n’est pas une simple modification de port. Il faut inventorier les versions, confirmer la prise en charge, construire une PKI de service, distribuer la confiance, configurer les identités de certificats, vérifier le routage et le filtrage, surveiller l’expiration et définir les comportements de refus. Certains clients n’auront pas la fonction souhaitée ; les exceptions doivent être isolées.

Une séquence de migration maîtrisée :

1. inventaire des clients, serveurs, versions et dépendances ;
2. validation en laboratoire de la négociation, des certificats et des rôles ;
3. déploiement du service sécurisé sur un endpoint distinct ;
4. migration pilote d’un petit groupe d’équipements ;
5. tests positifs, négatifs, de panne et de reprise ;
6. migration par lots avec métriques et retour arrière préparé ;
7. retrait contrôlé de l’ancien transport ;
8. vérification des flux réseau et audit de la flotte.

Pour TACACS+ sur TLS selon RFC 9887, le port par défaut défini par la spécification est TCP/300, distinct du port TCP/49 de la variante historique. Le serveur TLS ne doit pas accepter silencieusement la variante non TLS sur le même service, et le client ne doit pas retomber sur le canal non sécurisé si TLS échoue. Ces principes doivent être vérifiés sur les implémentations concrètes. Pour RADIUS/TLS ou RADIUS/1.1, la documentation et les statuts des spécifications doivent être consultés de la même manière ; RFC 6614 et RFC 9765 sont des documents expérimentaux, pas une preuve d’adoption universelle.

### 2.11. Gestion de la dérive et automatisation

L’automatisation peut vérifier la conformité des listes de méthodes, des serveurs déclarés, des adresses source, du filtrage SSH, de l’accounting et des comptes locaux. L’outil ne doit pas exposer les secrets pendant la collecte et devrait stocker les résultats sous forme de valeurs d’état, de différences contrôlées ou de références de coffre-fort.

Les déploiements doivent être idempotents autant que possible, limités en taille de lot et assortis d’un mécanisme de validation. Une automatisation qui supprime puis recrée toutes les lignes AAA peut interrompre les sessions ou effacer des paramètres manuels essentiels. Une action automatisée de correction ne doit pas être lancée sur un réseau distant sans une voie de récupération et des limites de portée.

La surveillance de dérive peut vérifier le comportement plutôt que la seule syntaxe : un compte de test doit obtenir le profil de rôle prévu ; une commande interdite doit échouer ; l’événement doit être reçu par le collecteur ; la politique doit être identique sur les serveurs secondaires. Ces tests doivent utiliser des identités techniques à droits limités et ne pas provoquer des changements destructifs.

### 2.12. Exercices pratiques expert

**Exercice A — Révocation immédiate :** un administrateur quitte l’organisation. Définis les systèmes à mettre à jour, les sessions à invalider, les caches à purger ou attendre, les comptes d’urgence à contrôler et les preuves qui démontrent le retrait effectif. Une désactivation d’annuaire ne prouve pas à elle seule que toutes les sessions déjà ouvertes ont été terminées.

**Corrigé indicatif :** désactiver l’identité et les authentificateurs selon la procédure ; retirer les groupes et rôles ; révoquer ou invalider les certificats selon la politique PKI ; mettre fin aux sessions VPN, bastion et équipements quand le produit le permet ; vérifier les comptes locaux ou identités secondaires ; confirmer les changements sur les nœuds répliqués ; rechercher les connexions récentes ; documenter les exceptions et les délais de propagation.

**Exercice B — Secours trop permissif :** le serveur principal est indisponible, et un compte local dont le privilège est maximal reste accepté sur tous les routeurs. Propose une réduction du risque sans supprimer immédiatement toute possibilité de récupération.

**Corrigé indicatif :** inventorier les comptes locaux, limiter les sources d’administration, séparer le secours par rôle ou coffre-fort, placer un compte d’urgence à usage contrôlé, tester une solution hors bande, déclencher une alerte à l’usage, interdire l’usage ordinaire et tester le comportement de panne avant de réduire le privilège. Ne pas retirer le seul accès local sans alternative éprouvée.

**Exercice C — Échec TLS :** les clients TACACS+ compatibles TLS refusent le certificat après le renouvellement. Les clients ne doivent pas basculer automatiquement vers TCP/49. Établis le diagnostic.

**Corrigé indicatif :** vérifier l’horloge, la chaîne de certification, la date de validité, l’usage de clé, le nom attendu du serveur, le magasin de confiance, le certificat client si l’authentification mutuelle est utilisée, la distribution de la CA et les logs TLS. Tester depuis un client représentatif et restaurer un certificat valable ou une configuration précédemment validée sans autoriser de rétrogradation en clair.

**Exercice D — Access-Accept mais mauvais VLAN :** le serveur RADIUS accepte l’identité, mais le poste obtient le VLAN de quarantaine. Identifie les hypothèses.

**Corrigé indicatif :** contrôler les attributs exacts et leur format ; vérifier le groupe et la politique qui ont correspondu ; contrôler le profil du port et l’ordre des règles ; confirmer que le commutateur comprend l’attribut et que le VLAN existe ; vérifier l’état 802.1X/MAB, les politiques de session, les attributs constructeur et les journaux locaux ; confirmer ensuite le VLAN réellement appliqué et les flux accessibles.

**Exercice E — Accounting incomplet :** les connexions apparaissent dans le SIEM mais certaines commandes n’y figurent pas. Distingue le défaut de collecte du défaut de génération.

**Corrigé indicatif :** valider si l’équipement génère l’accounting des commandes ; vérifier la liste appliquée au bon niveau de privilège et au bon type de session ; consulter les journaux bruts du serveur AAA ; identifier les différences de version ou de syntaxe ; tester une commande connue autorisée et une commande refusée ; contrôler les filtres et parseurs SIEM, les pertes de transport et le délai de recherche. Ne déduis pas l’absence d’une commande du seul fait qu’elle n’apparaît pas dans une vue normalisée.

### 2.13. Checklist de mise en production

Avant le changement :

- [ ] Les versions d’équipement et capacités AAA ont été inventoriées.
- [ ] Les politiques centrales et les listes réellement appliquées ont été comparées.
- [ ] Les comptes locaux, leurs privilèges et leurs propriétaires sont connus.
- [ ] L’accès console/hors bande, la sauvegarde et le retour arrière ont été testés.
- [ ] Les certificats, secrets, règles de pare-feu et sources AAA sont préparés.
- [ ] Les tests positifs, négatifs, de panne, de secours et d’accounting sont définis.

Après le changement :

- [ ] Les rôles donnent exactement les droits prévus sur chaque catégorie d’équipement.
- [ ] Un rejet explicite ne contourne pas la politique centrale.
- [ ] Une panne suit le comportement approuvé et déclenche une alerte.
- [ ] Les événements sont corrélables dans le SIEM et l’horloge est fiable.
- [ ] La haute disponibilité et la révocation sont testées.
- [ ] Les flux anciens ont été retirés lorsque la migration est validée.
- [ ] La documentation et le plan de retour arrière sont mis à jour.

---

## 3. Dépannage et sécurité

### 3.1. Diagnostiquer à partir d’une hypothèse mesurable

Le dépannage expert commence par une question précise : quelle fonction échoue, à quel point du parcours et pour quelles identités ? « AAA ne fonctionne pas » est trop vague. La connexion peut échouer avant d’atteindre le serveur, l’authentification peut réussir puis l’autorisation EXEC échouer, la commande peut être refusée, ou l’accès peut réussir alors que l’accounting ne parvient pas au collecteur.

Découpe la chaîne en étapes : transport, validation du client, authentification, résolution d’identité, autorisation, application locale, accounting, normalisation et détection. Pour chacune, définis une preuve observable. Une capture réseau peut démontrer que des paquets sont envoyés, mais ne dit pas pourquoi un serveur a refusé une identité. Un journal serveur peut montrer un refus, mais ne prouve pas à lui seul que la commande a été appliquée ou que l’équipement a reçu l’attribut.

La collecte doit être non destructive : export de configuration, logs horodatés, état des processus, statistiques, captures limitées, version et identifiants de session. Les commandes `debug` très bavardes peuvent charger un équipement et exposer des informations sensibles. Toute activation de débogage en production doit être courte, filtrée et assortie d’un plan d’arrêt.

### 3.2. Matrice symptôme → hypothèses → preuve

| Symptôme | Hypothèses possibles | Preuve suivante |
|---|---|---|
| SSH ne demande pas l’identité prévue | Mauvaise liste de méthodes, ACL VTY, source bloquée, session existante | Configuration de ligne, logs d’accès et test depuis la zone de gestion |
| Identité acceptée, shell refusé | Autorisation EXEC, rôle manquant, serveur indisponible après auth | Journal d’authentification puis demande d’autorisation EXEC |
| Shell accepté, commande refusée | Politique d’autorisation de commande, arguments inattendus, privilège différent | Requête TACACS+ exacte et règle qui a correspondu |
| Tous les clients échouent après renouvellement de certificat | Horloge, chaîne, SAN, EKU, confiance ou certificat client | Logs TLS, chaîne et identité du certificat |
| Un site distant échoue, l’autre fonctionne | Routage retour, ACL intersite, source AAA différente, décalage local | Capture des deux côtés, chemin réseau, adresse source réellement utilisée |
| Après bascule, les droits sont anciens | Réplication en retard, cache, groupe non synchronisé | Version de politique, état de réplication et logs des deux nœuds |
| Accounting présent côté serveur mais absent SIEM | Collecteur, transport, parsing, filtre ou retard | Journaux bruts, métriques de collecte et événement témoin |
| Connexions très lentes pendant une panne | Réessais synchronisés, timeouts élevés, file saturée | Latence par étape, taux de demandes, nombre de tentatives et saturation |

### 3.3. Pourquoi le compte est accepté mais la commande ne l’est pas

Il faut distinguer le privilège local du rôle central. Une session peut être authentifiée avec succès, puis recevoir une autorisation EXEC insuffisante. Une commande peut ensuite être refusée parce que le client envoie des arguments différents de ceux attendus par la règle ou parce que la requête s’applique à un autre niveau de privilège.

Pour résoudre le problème :

1. relever l’identité, le serveur choisi et la méthode d’authentification ;
2. vérifier le rôle ou les attributs effectivement renvoyés ;
3. observer la demande d’autorisation exacte, avec le service, la commande et les arguments ;
4. repérer la règle qui a décidé, y compris l’ordre et les éventuels héritages ;
5. tester une commande simple autorisée, une commande interdite et une commande équivalente avec arguments ;
6. confirmer l’événement d’accounting correspondant et le résultat sur l’équipement.

Évite de résoudre le problème en donnant à l’utilisateur un privilège maximal permanent. Il faut corriger la règle minimale qui manque ou clarifier le rôle. Si la commande est réellement dangereuse, le refus peut être conforme à la politique, même si l’utilisateur pense en avoir besoin.

### 3.4. Pannes de transport et dégradation du service

Un timeout ne signifie pas nécessairement que le serveur est arrêté. Il peut être causé par une route asymétrique, un filtrage, une MTU inhabituelle, une saturation, une résolution DNS erronée, une source inattendue ou un pare-feu avec état incohérent. Il faut vérifier le chemin aller et retour et confirmer la source du client AAA.

Les captures doivent être prises à plusieurs points lorsqu’il est possible de le faire : client, pare-feu intermédiaire et serveur. Si la requête atteint le serveur mais que la réponse ne revient pas, le problème est différent d’une requête qui n’arrive jamais. Si TCP établit une connexion mais que TLS échoue, le diagnostic doit se déplacer vers les certificats et les paramètres cryptographiques. Pour RADIUS/UDP, les pertes et les retransmissions peuvent avoir un comportement très différent du transport TCP/TLS.

Pendant un incident global, ne change pas simultanément les délais de toutes les plateformes. Stabilise d’abord le service, limite les nouvelles tentatives si nécessaire, vérifie la capacité de chaque nœud et détermine si un serveur secondaire est réellement opérationnel. Une bascule répétée entre plusieurs nœuds mal configurés peut amplifier le problème au lieu de le résoudre.

### 3.5. Incidents de certificats et de PKI

Un échec TLS doit être diagnostiqué sans désactiver la validation du certificat comme premier réflexe. Contrôle l’horloge du client et du serveur, la chaîne complète, l’expiration, l’identité attendue dans SAN, les usages de clé, l’algorithme accepté et les journaux des deux extrémités. Avec une authentification mutuelle, il faut examiner les certificats client et serveur séparément.

Si un certificat vient d’être renouvelé, vérifie que la nouvelle CA intermédiaire a été distribuée aux clients qui en ont besoin. Vérifie aussi les stratégies de sélection de certificat et la présence de la clé privée. Le remplacement d’un certificat ne doit pas supprimer la seule voie valide de communication avant qu’un test de négociation complet soit réussi.

La désactivation de la validation du nom du serveur peut transformer un problème de configuration en vulnérabilité d’interception. Si une exception est indispensable pour une fenêtre de migration, elle doit avoir une portée très limitée, un propriétaire, une date de fin et une vérification formelle de retrait. La solution durable est de corriger la chaîne de confiance ou le nom de service attendu.

### 3.6. Défaillance de la réplication et révocation tardive

Un utilisateur désactivé sur le nœud primaire peut être encore accepté par un nœud secondaire si les changements ne sont pas répliqués immédiatement. Il faut mesurer la propagation réelle des désactivations, des suppressions de groupes, des changements de rôles et des révocations. Les caches locaux des équipements et les sessions déjà ouvertes ajoutent une deuxième fenêtre de retard.

Un plan de révocation doit préciser quelles actions sont instantanées et lesquelles sont différées. Par exemple, désactiver un compte peut empêcher les nouvelles connexions, mais ne termine pas nécessairement une session CLI déjà ouverte. Un VPN peut conserver une session jusqu’à expiration ; un commutateur peut conserver une authentification jusqu’à réauthentification ou réception d’une commande de terminaison. La révocation doit donc couvrir les sessions existantes et les nouveaux accès.

Exercice : un compte privilégié compromis est désactivé sur l’annuaire, mais une session SSH reste active sur un routeur et le nœud AAA secondaire n’a pas encore reçu le changement. La réponse doit inclure la terminaison de la session, la révocation des authentificateurs, la vérification des rôles sur les deux nœuds, la recherche d’autres accès, la préservation des journaux et la correction de la latence de réplication. Un simple ticket « compte désactivé » n’est pas une preuve de confinement.

### 3.7. Protection contre le contournement des politiques

Les stratégies de contournement courantes comprennent l’usage d’un compte local oublié, une méthode VTY qui ne consulte pas la liste attendue, un port console insuffisamment contrôlé, un service de gestion accessible depuis le réseau utilisateur, une identité d’automatisation trop puissante ou une route vers un ancien serveur AAA. Une politique centrale peut être exacte tandis que l’application locale permet un accès alternatif.

La revue doit porter sur les chemins d’accès, pas uniquement sur les comptes : SSH, console, API, SNMP d’administration, interface Web, VPN, bastion, terminal serveur, outils d’orchestration et mécanismes de récupération. Chaque chemin devrait être répertorié avec son authentificateur, son autorisation, sa journalisation et son mécanisme de secours. Les chemins que l’organisation n’utilise plus doivent être supprimés, pas simplement oubliés dans la documentation.

### 3.8. Attaques contre le serveur AAA et limitation de l’impact

Si un serveur AAA est compromis, la priorité est d’empêcher l’attaquant de modifier des politiques ou de distribuer des privilèges, tout en préservant les preuves. La réponse peut nécessiter l’isolement d’un nœud, la révocation de certificats, la rotation de secrets, la vérification des clients enregistrés et le rétablissement depuis une configuration approuvée. Les actions doivent être coordonnées pour ne pas déclencher un verrouillage généralisé.

Les secrets partagés classiques doivent être protégés dans un coffre ou une solution de gestion de secrets, limités par client autant que possible et tournés selon le risque. Si un secret est exposé, le remplacer uniquement côté serveur provoque une panne ; le remplacer uniquement sur l’équipement provoque aussi une panne. L’opération doit inclure les deux côtés, un lot pilote, le test de la nouvelle valeur et le contrôle de retrait de l’ancienne.

Les clés privées de certificats, les exports de configuration, les bases de politiques et les sauvegardes peuvent être aussi sensibles que les mots de passe. Leur chiffrement au repos ne suffit pas si les clés sont stockées à côté sans protection. Les sauvegardes doivent être isolées, testées en restauration et accessibles à des comptes distincts de ceux utilisés pour l’administration quotidienne.

### 3.9. Préserver l’intégrité des journaux

Un administrateur capable de changer AAA ne devrait pas être en mesure d’effacer seul toutes les preuves de ses actions. Les journaux sensibles doivent être exportés vers une zone indépendante, avec contrôle d’accès distinct, rétention définie et détection de rupture de flux. Les événements de changement de politique, de suppression de source, de modification de certificat et de gestion du compte d’urgence doivent recevoir une priorité particulière.

La rétention doit tenir compte de la législation, des exigences contractuelles, de la capacité de stockage et de la sensibilité des données. Il faut éviter de journaliser plus de données personnelles que nécessaire, mais aussi éviter de supprimer trop vite les preuves utiles. Les données de commande peuvent contenir des clés, des chaînes confidentielles ou des informations clients ; une politique de masquage doit protéger les secrets sans détruire la valeur d’audit.

Contrôle régulièrement que la chaîne complète fonctionne : un événement produit par l’équipement, reçu par le serveur AAA, exporté vers le collecteur, correctement normalisé, indexé, conservé et accessible au rôle SOC. Un tableau de bord vert ne suffit pas si un parseur élimine silencieusement le champ d’identité ou si les journaux de commandes n’ont jamais été générés par le client.

### 3.10. Continuité de service sans ouverture générale des droits

La continuité doit être différenciée selon la fonction. Pour un poste utilisateur non critique, il peut être préférable de refuser l’accès réseau lorsqu’un serveur d’authentification n’est pas joignable. Pour un réseau industriel, une politique contrôlée de continuité peut être requise. Pour l’administration d’un équipement distant, le besoin de récupération doit être satisfait par un chemin d’urgence protégé, pas nécessairement par l’acceptation de n’importe quel compte local.

La décision doit se fonder sur une analyse du risque : conséquence d’un refus, conséquence d’une acceptation indue, durée maximale d’indisponibilité, existence d’un accès hors bande, sensibilité du segment et capacité à détecter l’usage du secours. Les profils de continuité peuvent utiliser un accès restreint à un réseau de remédiation, des droits de lecture limités ou une liste de comptes d’urgence gérés. Ils doivent avoir une durée de validité et être testés.

> **Danger :** un « fail-open » global peut transformer une panne de quelques minutes en accès non autorisé à des segments entiers. Si une exception de continuité est nécessaire, limite-la à un rôle, une zone, une durée et un ensemble de flux précis, puis alerte dès son activation.

### 3.11. Réponse à incident : identité privilégiée compromise

Lorsqu’un compte administrateur semble compromis, les objectifs sont de contenir l’accès, conserver les preuves, identifier la portée et rétablir une confiance vérifiable. Les étapes dépendent de l’impact, mais doivent inclure :

1. confirmer l’identité, les sessions, les équipements et la période affectée ;
2. suspendre l’identité et ses authentificateurs selon la procédure ;
3. terminer les sessions actives et les accès indirects lorsque cela est possible ;
4. retirer les rôles et vérifier les nœuds secondaires, caches et comptes locaux ;
5. conserver les journaux bruts AAA, équipement, SIEM, bastion et système d’identité ;
6. examiner les commandes et modifications associées, puis comparer les configurations à une référence ;
7. tourner les secrets ou certificats susceptibles d’être exposés ;
8. rétablir le service depuis une configuration vérifiée ;
9. documenter les délais, les exceptions et les preuves de confinement ;
10. traiter la cause racine et tester le contrôle corrigé.

Ne réinitialise pas les serveurs ou ne purge pas les journaux avant d’avoir déterminé ce qui doit être préservé. Une action de remédiation rapide peut détruire des preuves nécessaires pour comprendre l’incident. Inversement, ne conserve pas un compte compromis actif au seul motif de maintenir les logs : la collecte doit se faire dans un cadre de confinement coordonné.

### 3.12. Indicateurs de performance et de sécurité

Les indicateurs doivent aider à détecter une dégradation avant qu’elle ne provoque une crise et à démontrer que la politique fonctionne. Des mesures possibles :

- taux de succès et de refus séparés par application, groupe et site ;
- latence p50, p95 et p99 des demandes AAA ;
- taux de timeout, retransmissions et bascules ;
- disponibilité par fonction, et pas seulement disponibilité du processus ;
- délai de réplication des comptes et politiques ;
- temps de propagation d’une révocation ;
- proportion d’équipements conformes au profil AAA ;
- nombre d’exceptions de politique échues mais encore actives ;
- état des certificats, expirations à venir et erreurs de validation ;
- complétude et délai d’ingestion des événements d’accounting ;
- fréquence d’usage du compte d’urgence ;
- nombre d’identités orphelines, comptes dormants et privilèges permanents.

Un indicateur sans seuil ni action est peu utile. Pour chaque mesure, définis une valeur de référence, un seuil d’alerte, une personne responsable et une procédure. Un taux de refus en hausse peut indiquer une attaque, une campagne de changement, un annuaire indisponible ou une configuration erronée ; la métrique doit être corrélée au contexte.

### 3.13. Gouvernance : revues, exceptions et expiration

La revue des droits doit être organisée par propriétaire métier et non uniquement par l’équipe qui exploite AAA. Les propriétaires confirment que les personnes ont encore besoin du rôle ; l’équipe technique confirme que le rôle se traduit par les droits attendus ; la sécurité analyse les exceptions et les risques. Les droits temporaires doivent expirer automatiquement lorsque cela est supporté, ou faire l’objet d’une tâche de retrait avec échéance contrôlée.

Chaque exception doit avoir une référence, un motif, un propriétaire, un périmètre, une date de création, une date d’expiration, les contrôles compensatoires et le risque accepté. Une exception sans échéance finit souvent par devenir une partie permanente de la politique. Un rapport périodique doit lister les exceptions expirées, les comptes sans propriétaire, les comptes de service non utilisés et les équipements restés sur une version incompatible.

### 3.14. Scénario de synthèse : déploiement multi-sites

Une entreprise possède plusieurs sites, des commutateurs de campus, des routeurs de cœur, des pare-feu, des accès Wi-Fi et des VPN. Elle veut uniformiser les identités, limiter les commandes administratives, protéger les échanges AAA et centraliser la preuve. Une mauvaise approche serait de déployer une configuration unique à tous les équipements et de supprimer immédiatement tous les comptes locaux.

Une approche experte commence par l’inventaire et la segmentation par fonction. Le réseau d’administration est isolé ; les serveurs AAA sont redondés sur plusieurs domaines de panne ; les rôles sont définis avec des propriétaires ; les équipements sont classés par capacité de transport ; les certificats sont provisionnés selon un profil clair ; l’accounting est intégré au SIEM ; les procédures de secours sont testées. Les équipements non compatibles sont isolés, documentés et intégrés à un plan de modernisation.

La migration se fait par petits lots : pilote de laboratoire, site de test, site pilote, sites de production selon le risque. Chaque lot comprend un test de réussite, un test négatif, un test de panne, un test de révocation et un contrôle des journaux. Le retour arrière ne consiste pas à réactiver librement des comptes locaux : il restaure une version connue de la configuration selon une procédure sécurisée.

Après migration, le service est exploité par des indicateurs : latence, taux d’échec, conformité, expiration des certificats, réplication et complétude de journaux. Une revue post-déploiement vérifie que les anciens ports et les anciens serveurs ne reçoivent plus de trafic, que les exceptions ont une échéance et que les équipes savent utiliser la procédure d’urgence. Le projet ne se termine qu’après cette vérification, pas au moment où les connexions fonctionnent.

### 3.15. Questions de synthèse

1. Pourquoi une authentification réussie n’est-elle pas une preuve d’autorisation correcte ?
2. En quoi l’autorisation par commande peut-elle être contournée ou devenir trop permissive si les arguments et modes CLI ne sont pas testés ?
3. Quels risques spécifiques apparaissent lorsqu’une désactivation d’identité n’est pas immédiatement répliquée ?
4. Pourquoi la redondance des serveurs AAA ne garantit-elle pas la cohérence des politiques ?
5. Quelles différences opérationnelles doivent être prises en compte entre TACACS+ historique et TACACS+ sur TLS selon RFC 9887 ?
6. Pourquoi faut-il tester les refus explicites séparément des timeouts ?
7. Quels éléments rendent un événement d’accounting exploitable comme preuve ?
8. Comment maintenir un accès d’urgence sans transformer le secours en contournement permanent ?
9. Pourquoi le MFA d’un portail d’identité ne garantit-il pas le MFA sur chaque accès CLI ?
10. Comment démontrer que la décision RADIUS s’est réellement traduite par le profil réseau attendu ?
11. Quelles preuves démontrent que les journaux ont été générés, transportés, normalisés et conservés correctement ?
12. Quels critères permettent de décider si une exception AAA doit être conservée, remplacée ou retirée ?

---

## Points à retenir

- AAA doit être traité comme un service de sécurité critique, avec des objectifs de disponibilité, de cohérence, d’audit et de reprise.
- Authentification, autorisation, accounting, application locale et collecte SIEM sont des étapes distinctes qui doivent être testées séparément.
- Une identité, un authentificateur, une session et un rôle ne sont pas équivalents ; les lier explicitement réduit les erreurs de privilège.
- L’autorisation par commande doit être testée avec les vrais arguments et modes CLI. Une session authentifiée n’implique pas que ses commandes sont autorisées.
- Le secours doit distinguer acceptation, rejet explicite, absence de réponse et erreur de confiance. Un refus ne doit pas déclencher un contournement local implicite.
- La haute disponibilité exige la cohérence des identités, politiques, secrets, certificats, caches et événements, pas uniquement deux serveurs joignables.
- TACACS+ historique sur TCP/49 ne fournit pas la sécurité moderne d’un transport TLS ; RFC 9887 spécifie TACACS+ sur TLS 1.3, par défaut TCP/300, si les produits le prennent explicitement en charge.
- RADIUS/TLS (RFC 6614) et RADIUS/1.1 (RFC 9765) ont un statut expérimental : vérifier l’implémentation et l’interopérabilité plutôt que supposer leur présence.
- Le MFA doit être évalué selon la résistance au phishing et selon le chemin d’accès réellement protégé.
- Les politiques 802.1X, VLAN dynamiques et attributs RADIUS doivent être vérifiés sur le point d’application et pas seulement dans le journal du serveur.
- Les traces ont une valeur probante si elles sont attribuables, horodatées, complètes, protégées, corrélables et conservées de façon contrôlée.
- La conformité de la flotte doit être mesurée sur les configurations effectives des équipements et comparée aux politiques centralisées.
- Les changements AAA doivent être progressifs, testés dans les deux sens, limités en taille de lot et accompagnés d’une voie de récupération indépendante.

### Références techniques

- IETF, **RFC 8907 — The TACACS+ Protocol** : https://www.rfc-editor.org/rfc/rfc8907.html
- IETF, **RFC 9887 — TACACS+ over TLS 1.3** (publiée en décembre 2025 ; profil TLS 1.3 et port TCP/300 par défaut) : https://www.rfc-editor.org/rfc/rfc9887.html
- IETF, **RFC 2865 — Remote Authentication Dial In User Service (RADIUS)** : https://www.rfc-editor.org/rfc/rfc2865.html
- IETF, **RFC 2866 — RADIUS Accounting** : https://www.rfc-editor.org/rfc/rfc2866.html
- IETF, **RFC 6614 — Transport Layer Security (TLS) Encryption for RADIUS** (Experimental) : https://www.rfc-editor.org/rfc/rfc6614.html
- IETF, **RFC 9765 — RADIUS/1.1: Leveraging ALPN to Remove MD5** (Experimental) : https://www.rfc-editor.org/rfc/rfc9765.html
- IETF, **RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3** : https://www.rfc-editor.org/rfc/rfc8446.html
- IETF, **RFC 9190 — EAP-TLS 1.3** : https://www.rfc-editor.org/rfc/rfc9190.html
- NIST, **SP 800-207 — Zero Trust Architecture** : https://csrc.nist.gov/pubs/sp/800/207/final
- NIST, **SP 800-63B-4 — Digital Identity Guidelines: Authentication and Authenticator Management** (finalisé en juillet 2025) : https://csrc.nist.gov/pubs/sp/800/63/b/4/final
- NIST, **SP 800-63C-4 — Digital Identity Guidelines: Federation and Assertions** : https://csrc.nist.gov/pubs/sp/800/63/C/4/final
- Cisco, **AAA and TACACS+ Configuration Guides for IOS/IOS XE** : https://www.cisco.com/ (consulter le guide du train logiciel et du modèle ciblés)

Les références normatives décrivent des mécanismes et des exigences, mais ne prouvent pas que chaque produit les implémente. Pour toute mise en production, vérifier le statut de la spécification, la documentation officielle de la version installée, les limites de l’équipement, les paramètres par défaut et les résultats d’un laboratoire représentatif.
