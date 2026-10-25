# PKI — Niveau expert

**Niveau : Expert** · **Prérequis :** maîtrise du cycle de vie X.509, des chaînes de certification, des extensions, de TLS/mTLS, de CRL/OCSP, d’ACME et des outils de diagnostic OpenSSL.

Ce cours s’adresse aux personnes qui doivent **concevoir, gouverner, sécuriser et exploiter une PKI à l’échelle d’une organisation**. Le fil conducteur n’est plus seulement « comment fonctionne un certificat ? », mais « comment empêcher une erreur d’émission, une compromission de clé ou une panne de validation de devenir un incident majeur ? ». Les exemples reposent sur des environnements de laboratoire. Les procédures réelles doivent être adaptées à la politique de sécurité, aux exigences réglementaires, aux versions logicielles et à la politique de certification applicable.

> **Analogie :** une PKI experte ressemble à un réseau bancaire de confiance. La cryptographie fournit les serrures et les signatures ; la gouvernance définit qui peut ouvrir quel coffre ; les procédures de cérémonie contrôlent les opérations sensibles ; la supervision surveille les transactions ; et la réponse à incident détermine comment rétablir la confiance sans détruire inutilement toute l’infrastructure.


## 1. Objectifs du niveau expert

À la fin de ce module, vous devriez pouvoir :

- concevoir une hiérarchie de CA en fonction des frontières d’administration, des risques et des types d’identité ;
- justifier l’emploi de racines hors ligne, de CA intermédiaires spécialisées, de HSM et de contrôles de quorum ;
- définir une politique d’émission comme un ensemble de contrôles techniques et organisationnels vérifiables ;
- distinguer les responsabilités de l’architecture, des opérateurs, de l’enregistrement, des développeurs et des auditeurs ;
- planifier les renouvellements, les rotations, les migrations cryptographiques et la réponse à une compromission ;
- concevoir le contrôle de statut, les alertes d’expiration et la surveillance CT comme des services opérationnels ;
- interpréter les conséquences d’une révocation, d’une indisponibilité OCSP ou d’une CA compromise ;
- mesurer la qualité d’une PKI par des objectifs de service, des preuves d’audit et des tests de reprise.

### Livrables attendus d’un ingénieur PKI expert

| Livrable | Ce qu’il doit démontrer |
|---|---|
| Architecture cible | Rôles de CA, frontières de confiance, flux d’émission, plan de reprise, dépendances. |
| Politique de certification et procédures | Identités acceptées, preuves nécessaires, profils, autorisations, durées et règles de suspension/révocation. |
| Modèle de menace | Actifs, adversaires, chemins d’attaque, contrôles préventifs/détectifs/correctifs, risque résiduel. |
| Plan de clés | Génération, stockage, activation, usage, sauvegarde, rotation, destruction et preuve de destruction. |
| Plan d’exploitation | SLO, alertes, propriétaires, runbooks, seuils de renouvellement, tests de restauration. |
| Plan de migration | Inventaire, compatibilité, phase pilote, métriques, retour arrière, retrait des anciens algorithmes. |

### Règle de sécurité du laboratoire

Ne créez pas de CA de laboratoire dans le magasin de confiance de votre système principal. Ne copiez pas les clés privées vers un dépôt Git, un outil de ticketing, une image de conteneur ou une sauvegarde non chiffrée. N’utilisez pas une clé de démonstration pour signer des certificats destinés à des services réels. La création d’une CA interne de production exige une procédure formelle et une séparation des responsabilités ; une commande OpenSSL n’est pas à elle seule une procédure de production.


## 2. Concevoir l’architecture à partir des frontières de confiance

### 2.1 Partir des actifs et des conséquences

Une architecture PKI commence par les actifs qu’elle protège : clés de signature des CA, clés TLS des services, identités des utilisateurs et des appareils, canaux de renouvellement, annuaires, bases d’émission, journaux, configurations des validateurs et magasins de confiance. Il faut ensuite définir ce qui se passe si chaque actif est compromis, indisponible ou mal configuré.

Une clé de serveur compromise affecte normalement un service ou un ensemble de services qui partagent cette clé. Une clé d’AC émettrice compromise peut permettre l’émission de nombreux certificats dans les limites de cette CA. Une clé racine compromise peut remettre en question la confiance dans toute la branche rattachée et contraindre les organisations à déployer une nouvelle ancre. **Le rayon d’impact** dépend donc du niveau hiérarchique, des contraintes techniques, de la portée des identités autorisées et des contrôles qui entourent la clé.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Architecture PKI expert avec CA racine hors ligne, CA de politique, CA émettrice, workloads et séparation des plans" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Architecture de référence et réduction du rayon d’impact</text><rect x="25" y="60" width="180" height="76" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="115.0" y="85" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Root offline</text><text x="115.0" y="105" text-anchor="middle" fill="#a7f3d0" font-size="11.5">Trust anchor</text><text x="115.0" y="121" text-anchor="middle" fill="#a7f3d0" font-size="11.5">HSM · ceremony</text><rect x="246" y="60" width="180" height="76" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="336.0" y="85" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Policy CA</text><text x="336.0" y="105" text-anchor="middle" fill="#ddd6fe" font-size="11.5">Name constraints</text><text x="336.0" y="121" text-anchor="middle" fill="#ddd6fe" font-size="11.5">Policy OIDs</text><rect x="467" y="60" width="180" height="76" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="557.0" y="85" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Issuing CA</text><text x="557.0" y="105" text-anchor="middle" fill="#bae6fd" font-size="11.5">Online / restricted</text><text x="557.0" y="121" text-anchor="middle" fill="#bae6fd" font-size="11.5">Short-lived credentials</text><rect x="688" y="60" width="145" height="76" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="760.5" y="85" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Workloads</text><text x="760.5" y="105" text-anchor="middle" fill="#aabbd0" font-size="11.5">TLS · mTLS</text><text x="760.5" y="121" text-anchor="middle" fill="#aabbd0" font-size="11.5">User / device</text><path d="M205 98 L238 98" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M426 98 L459 98" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M647 98 L680 98" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="4" fill="#34d399" opacity="0.96"><animateMotion path="M205 98 L238 98" dur="2.0s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#a78bfa" opacity="0.96"><animateMotion path="M426 98 L459 98" dur="2.0s" begin=".45s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#38bdf8" opacity="0.96"><animateMotion path="M647 98 L680 98" dur="2.0s" begin=".9s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="52" y="177" width="230" height="84" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="167.0" y="202" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Plane de contrôle</text><text x="167.0" y="222" text-anchor="middle" fill="#fde68a" font-size="11.5">identités · approbations</text><text x="167.0" y="238" text-anchor="middle" fill="#fde68a" font-size="11.5">politiques · journaux</text><rect x="315" y="177" width="230" height="84" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="430.0" y="202" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Plan cryptographique</text><text x="430.0" y="222" text-anchor="middle" fill="#fecdd3" font-size="11.5">clés · signatures</text><text x="430.0" y="238" text-anchor="middle" fill="#fecdd3" font-size="11.5">HSM · sauvegardes</text><rect x="578" y="177" width="230" height="84" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="693.0" y="202" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Plan de données</text><text x="693.0" y="222" text-anchor="middle" fill="#aabbd0" font-size="11.5">certificats · OCSP/CRL</text><text x="693.0" y="238" text-anchor="middle" fill="#aabbd0" font-size="11.5">clients · services</text><path d="M115 136 L115 160" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round"/><path d="M115 160 L430 160" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round"/><path d="M430 160 L430 177" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round"/><path d="M430 160 L693 160" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round"/><path d="M693 160 L693 177" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round"/><text x="430" y="292" text-anchor="middle" fill="#aabbd0" font-size="12">Séparation des domaines : compromettre un plan ne doit pas permettre de contourner tous les autres.</text></svg></div>

**Principe de conception :** la hiérarchie n’est pas seulement un arbre de certificats. C’est une séparation de pouvoirs. La hiérarchie doit limiter ce qu’une CA peut émettre, qui peut lui demander un certificat, sur quels noms ou identités elle peut agir et qui peut modifier ses règles.

### 2.2 Racine hors ligne : contrôle du risque, pas fétiche

Une racine hors ligne réduit son exposition aux attaques réseau. Cela ne suffit pas si les médias contenant la clé sont mal protégés, si plusieurs opérateurs disposent de tous les secrets, si les sauvegardes sont exportées sans contrôle ou si la procédure de réactivation n’est pas testée. Une racine dite « hors ligne » mais connectée régulièrement à un poste d’administration généraliste peut conserver une surface d’attaque importante.

Bonnes pratiques de conception :

1. **Minimiser les occasions d’usage.** La racine signe les certificats de CA subordonnées lors d’opérations planifiées, plutôt que les certificats des serveurs au quotidien.
2. **Définir un environnement de cérémonie.** Matériel identifié, supports contrôlés, binôme/quorum, authentification forte, journaux signés ou protégés et procédure d’arrêt en cas d’écart.
3. **Séparer les rôles.** La personne qui approuve la demande ne doit pas pouvoir seule effectuer la signature et effacer les preuves.
4. **Planifier l’indisponibilité.** L’organisation sait combien de temps il faut pour effectuer une cérémonie et dispose d’un plan pour une urgence hors horaires ouvrés.
5. **Tester la restauration.** Une clé non restaurable peut devenir un risque de disponibilité ; une clé trop facilement restaurable devient un risque de compromission.
6. **Mesurer l’inventaire.** Certificats subordonnés, dates de fin, algorithmes, contraintes, points de publication et dépendances doivent être documentés.

La racine hors ligne ne signifie pas que l’ensemble de l’écosystème est hors ligne. Les CA émettrices peuvent être en ligne et répondre aux opérations autorisées, tandis que leurs pouvoirs sont réduits par des profils, des contraintes de noms, des politiques et des limites d’exploitation.

### 2.3 Séparer les rôles de CA par domaine d’identité

Une séparation utile peut être construite selon plusieurs axes :

- **Public contre interne.** Une racine interne ne doit pas automatiquement être une racine publique, et une CA publique n’est pas nécessairement appropriée pour des identités internes non exposées.
- **Serveur contre client.** Des CA ou profils distincts limitent le risque qu’un certificat prévu pour une authentification client soit accepté comme identité d’un serveur.
- **Utilisateur contre machine.** Les preuves d’identité, les droits de renouvellement et les mécanismes d’enrôlement diffèrent.
- **Production contre développement.** Une CA de développement ne doit pas pouvoir délivrer des certificats qui seraient acceptés par des applications de production.
- **Environnements sensibles contre environnement général.** Une CA spécialisée peut appliquer des contrôles de validation et une durée de validité plus stricts.
- **Régions ou unités légales.** Une délégation géographique ou organisationnelle peut réduire le besoin d’accès croisé et clarifier les responsabilités de révocation.

Une multiplication des CA n’est pas automatiquement plus sûre. Elle ajoute des clés, des journaux, des procédures et des points de défaillance à maintenir. On recherche le **minimum de privilèges avec une séparation claire**, pas un arbre le plus grand possible.

### 2.4 Contraindre techniquement la délégation

La séparation organisationnelle doit être appuyée par des contraintes cryptographiques lorsque le format et les validateurs les prennent en charge. Une CA subordonnée peut être limitée par `basicConstraints`, `pathLenConstraint`, `nameConstraints`, `keyUsage`, `extendedKeyUsage` et des politiques de certification selon le profil d’émission et la compatibilité requise.

- `CA:TRUE` marque un certificat qui peut représenter une autorité de certification ; il ne doit pas être attribué à un certificat final.
- `pathLenConstraint` limite la profondeur des CA non auto-émises qui peuvent se trouver sous une CA dans un chemin, selon les règles de validation applicables. Il ne remplace pas les procédures d’approbation.
- `nameConstraints` peut limiter les espaces de noms DNS, les adresses IP ou d’autres formes d’identité prises en charge. Le comportement réel doit être testé sur les validateurs cibles.
- `keyCertSign` et `cRLSign` sont des usages de clé associés aux opérations de CA et de CRL.
- `extendedKeyUsage` peut limiter le certificat à des usages tels que l’authentification serveur ou client. Les applications interprètent toutefois les profils selon leurs normes et politiques.

Ces extensions réduisent les erreurs et les abus, mais elles ne corrigent pas une politique d’émission défaillante. Si une CA peut délivrer un certificat hors des limites qu’elle est censée respecter, l’organisation doit considérer l’écart comme une faiblesse d’architecture ou de configuration à corriger.

### 2.5 Deux plans distincts : administration et données cryptographiques

La **couche de contrôle** gère les comptes opérateurs, les demandes, les validations d’identité, les profils, les approbations et les journaux. Le **plan cryptographique** détient ou utilise les clés et produit les signatures. Le **plan de distribution** sert les certificats, les CRL, les réponses OCSP, les journaux CT et les données d’inventaire.

Il ne faut pas supposer qu’un composant portant le nom « CA » réalise nécessairement toutes ces fonctions dans un seul processus. Une architecture plus robuste sépare autant que raisonnable les systèmes de gestion de demandes, les bases d’audit, les systèmes de stockage de clés, les services de signature et les services de publication. Les interfaces entre ces composants deviennent des frontières de sécurité à documenter et à surveiller.


## 3. Modéliser la menace PKI

### 3.1 Adversaires, capacités et objectifs

Un modèle de menace utile distingue les adversaires au lieu de traiter « l’attaquant » comme une entité générique :

- **Opérateur malveillant ou contraint.** Détient un accès légitime mais tente d’émettre un certificat non autorisé ou de cacher ses traces.
- **Compte d’administration compromis.** L’attaquant prend la main sur un compte, un jeton API, un bastion ou un système de ticketing.
- **Compromission d’une application d’enrôlement.** Une API vulnérable ou un contrôleur de domaine détourné déclenche des demandes d’identité au nom de tiers.
- **Vol d’une clé privée finale.** La clé sort d’un poste, d’une image de conteneur, d’une sauvegarde ou d’un répertoire trop permissif.
- **Compromission d’une CA émettrice.** L’attaquant obtient la capacité de signature ou manipule les contrôles avant signature.
- **Compromission d’une racine ou d’une chaîne de confiance.** La confiance elle-même doit être reconstruite et redéployée.
- **Défaillance interne non malveillante.** Une configuration, une mise à jour, une horloge, une URL de publication ou un renouvellement défectueux provoque une panne.

Pour chaque scénario, décrivez l’actif ciblé, la précondition, l’événement observable, les contrôles de prévention, les contrôles de détection, la stratégie de confinement et les preuves à conserver. Une mesure de sécurité utile doit être associée à un risque explicite et à un responsable.

### 3.2 Scénarios d’attaque courants

**Abus d’auto-enrôlement.** Un utilisateur ou un service peut demander un certificat pour une identité plus privilégiée que la sienne. Les contrôles doivent relier l’identité authentifiée du demandeur, l’objet demandé, le profil autorisé et le droit sur le nom. Le simple fait qu’une CSR soit signée par la clé correspondante ne prouve aucun droit sur le nom demandé.

**Confusion de profil.** Un même endpoint accepte plusieurs profils et choisit le mauvais à cause d’un paramètre modifiable par le demandeur. Le profil doit être déterminé par une règle côté serveur et par le rôle authentifié, non par un champ libre fourni par l’appelant.

**Élévation de privilège par EKU ou sujet.** Une application suppose que le nom du sujet ou un champ organisationnel suffit à autoriser un accès. Les applications doivent vérifier l’identité attendue et l’usage spécifique, et ne pas interpréter un certificat valide comme une autorisation universelle.

**Abus d’une CA intermédiaire permissive.** Une CA d’environnement de test ou de filiale peut émettre des identités qui ne devraient pas être acceptées ailleurs. Il faut maîtriser sa distribution comme ancre potentielle, ses contraintes, ses chemins valides et les magasins dans lesquels elle est installée.

**Dérive du plan de contrôle.** Les règles changent sans validation indépendante, l’audit est incomplet, ou un administrateur peut modifier les autorisations et approuver sa propre demande. Utilisez des contrôles de changement, des examens à quatre yeux et une surveillance des différences de configuration.

### 3.3 Prévention, détection, correction

| Moment | Exemples de contrôles | Preuves attendues |
|---|---|---|
| Prévention | MFA, RBAC/ABAC, approbation indépendante, profils codés et testés, HSM, contraintes de nom. | Politique approuvée, configuration versionnée, test automatisé. |
| Détection | Journaux d’émission, alerte sur EKU/nom inattendu, CT, surveillance de changements, alertes sur renouvellement atypique. | Événement horodaté, identité de l’acteur, demande et certificat associés. |
| Correction | Révocation, rotation, désactivation de compte, remplacement de CA, reconfiguration des clients, notification ciblée. | Plan d’incident, inventaire touché, tests de retour à un état sûr. |
| Résilience | Restauration testée, CA redondante lorsque justifiée, publication de secours, runbooks, exercices. | Résultats de tests, objectifs mesurés, écarts suivis. |

La sécurité d’une PKI ne peut pas être évaluée seulement par l’algorithme ou la taille de clé. Le scénario le plus probable est souvent un abus d’autorisation ou une erreur opérationnelle autour d’une primitive cryptographique solide.


## 4. Gouvernance : politique de certification et procédure d’exploitation

### 4.1 Distinguer les documents

Une **Certificate Policy (CP)** décrit les garanties et règles auxquelles une classe de certificats doit satisfaire : identification, responsabilités, usages acceptés, exigences de clé, révocation, audit et obligations des participants. Une **Certification Practice Statement (CPS)** explique comment une CA applique ses règles en pratique. Une politique interne d’émission peut définir les règles opérationnelles d’un environnement. Les termes exacts et les exigences dépendent de l’écosystème et du cadre réglementaire ; ne supposez pas que les documents ont le même sens dans chaque organisation.

Une CP/CPS n’est pas une décoration documentaire. Les contrôles annoncés doivent correspondre aux mécanismes réellement présents. Si la procédure indique que chaque certificat privilégié reçoit une approbation indépendante, les journaux et la configuration doivent démontrer cette séparation. Si le document promet une publication de CRL à fréquence donnée, l’équipe doit surveiller effectivement cette fraîcheur et alerter avant l’expiration.

### 4.2 Matrice d’émission

Chaque type de certificat devrait avoir un profil explicite. Une matrice pratique comprend au minimum :

| Élément de profil | Questions de conception |
|---|---|
| Identité | Quels SAN, identifiants d’utilisateur, d’appareil ou de service sont autorisés ? Qui prouve le droit sur cette identité ? |
| Usage | Serveur TLS, client TLS, signature de code, signature de document, chiffrement ou autre usage spécialisé ? |
| Algorithme | Quelle famille de clé, quel niveau de sécurité, quels mécanismes de signature et quelles contraintes de compatibilité ? |
| Durée | Quelle durée maximale est autorisée par la politique, le type d’identité et les exigences externes applicables ? |
| Renouvellement | Quelle preuve faut-il répéter ? Une preuve récente de possession et de droit sur l’identité est-elle exigée ? |
| Révocation | Quels événements déclenchent la révocation, qui peut la demander, dans quel délai et par quel mécanisme ? |
| Publication | Certificat final, intermédiaire, CRL, OCSP, CT ou journal d’audit : quoi, où et comment ? |
| Approbation | Automatique, approbation par le propriétaire, validation à deux personnes ou contrôle spécialisé ? |
| Exploitation | Responsable métier, équipe d’astreinte, SLO, procédure de dépannage, environnement de test. |

L’émission doit échouer de façon sûre lorsque les données obligatoires manquent ou que la source d’identité est indisponible. Un mode dégradé temporaire peut être nécessaire pour la continuité, mais il doit être explicite, limité, audité et autorisé par le niveau de risque approprié. Évitez les solutions qui abaissent silencieusement les contrôles en cas d’erreur.

### 4.3 Profils versionnés et tests de conformité

Traitez les profils de certificats comme du code : fichiers source versionnés, revue, tests, déploiement contrôlé, journal de changement et possibilité de revenir à une version précédente. Les tests doivent inspecter les certificats réellement émis, pas seulement valider le fichier de configuration. Ils vérifient les champs attendus, les extensions critiques, les noms, les usages, les dates, les algorithmes et la chaîne.

Un test négatif est particulièrement important : envoyer une demande qui tente de demander un SAN interdit, une EKU hors profil, une durée excessive, une contrainte de nom absente ou une clé trop faible. Le test doit prouver que le système refuse la demande, et que le refus apparaît dans les journaux avec un motif utile. Une suite qui ne teste que les cas heureux ne prouve pas que la politique résiste à un appelant malveillant.


## 5. Maîtriser les clés : HSM, quorum et cérémonie

### 5.1 La clé est l’actif critique

Un certificat est public. La clé privée correspondante est l’actif sensible. Les équipes ne doivent donc pas construire leurs contrôles autour du seul fichier `.crt` ou `.pem`, mais autour de la génération, l’usage, la sauvegarde, la restauration, l’accès et la destruction de la clé. La clé finale d’un service peut être générée localement ou dans un HSM/KMS selon les exigences ; dans de nombreux cas, la meilleure option est de garder la clé là où elle est utilisée, sans l’exporter.

Un HSM peut isoler les opérations cryptographiques et limiter l’export de clés. Il ne supprime pas tous les risques : les rôles d’administration, les interfaces API, les mécanismes de quorum, le firmware, la configuration, les sauvegardes, la disponibilité et les applications autorisées à demander des signatures restent critiques. Une application compromise qui possède le droit de faire signer des données arbitraires peut exploiter le service de signature même sans extraire la clé.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Schéma de cérémonie de clé HSM avec quorum, séparation des tâches et journalisation inviolable" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Cérémonie de clé et frontières de confiance du HSM</text><rect x="35" y="66" width="170" height="82" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="120.0" y="91" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Opérateur A</text><text x="120.0" y="111" text-anchor="middle" fill="#bae6fd" font-size="11.5">authentification forte</text><text x="120.0" y="127" text-anchor="middle" fill="#bae6fd" font-size="11.5">quorum partiel</text><rect x="246" y="66" width="170" height="82" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="331.0" y="91" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Opérateur B</text><text x="331.0" y="111" text-anchor="middle" fill="#ddd6fe" font-size="11.5">séparation des rôles</text><text x="331.0" y="127" text-anchor="middle" fill="#ddd6fe" font-size="11.5">quorum partiel</text><rect x="457" y="66" width="170" height="82" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="542.0" y="91" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Témoin / audit</text><text x="542.0" y="111" text-anchor="middle" fill="#fde68a" font-size="11.5">procès-verbal</text><text x="542.0" y="127" text-anchor="middle" fill="#fde68a" font-size="11.5">vérification indépendante</text><rect x="668" y="66" width="160" height="82" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="748.0" y="91" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">HSM / domaine</text><text x="748.0" y="111" text-anchor="middle" fill="#a7f3d0" font-size="11.5">clé non exportable</text><text x="748.0" y="127" text-anchor="middle" fill="#a7f3d0" font-size="11.5">règles M-of-N</text><path d="M205 105 L238 105" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M416 105 L449 105" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M627 105 L660 105" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="4" fill="#38bdf8" opacity="0.96"><animateMotion path="M205 105 L238 105" dur="1.9s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#a78bfa" opacity="0.96"><animateMotion path="M416 105 L449 105" dur="1.9s" begin=".3s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#fbbf24" opacity="0.96"><animateMotion path="M627 105 L660 105" dur="1.9s" begin=".6s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="138" y="190" width="584" height="75" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="430.0" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Journal inviolable et artefacts de cérémonie</text><text x="430.0" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">approbation · empreintes · horodatage · inventaire · test de restauration</text><text x="430.0" y="251" text-anchor="middle" fill="#aabbd0" font-size="11.5">Aucune personne ne doit pouvoir créer, utiliser et effacer seule les preuves.</text><path d="M120 148 L120 173" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M331 148 L331 173" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M542 148 L542 173" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M748 148 L748 173" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><text x="430" y="294" text-anchor="middle" fill="#aabbd0" font-size="12">La sécurité dépend autant des procédures, des rôles et des sauvegardes que du matériel cryptographique.</text></svg></div>

### 5.2 Modèle de séparation des tâches

Une cérémonie de clé importante doit répondre aux questions suivantes :

- Qui autorise la cérémonie et quelle justification est conservée ?
- Qui prépare l’environnement, les supports et les logiciels, et qui valide leur intégrité ?
- Combien de personnes doivent être présentes pour autoriser une action critique ?
- La clé est-elle créée, importée, restaurée ou simplement activée ? Chaque cas a un niveau de risque différent.
- Quels contrôles prouvent que la clé est restée dans le HSM et que les objets créés sont bien ceux attendus ?
- Qui contrôle l’empreinte du certificat après signature et la correspondance entre la clé publique certifiée et la clé privée attendue ?
- Comment les journaux sont-ils protégés contre les modifications après la cérémonie ?
- Comment s’assurer que les opérations inutilisées ou les supports temporaires sont nettoyés ?

Le quorum **M sur N** signifie qu’un ensemble d’au moins M parmi N facteurs ou détenteurs est nécessaire pour autoriser une opération. Le modèle précis varie selon le HSM. Il faut éviter de confondre seuil d’activation, quorum d’administration, contrôle d’accès logique et séparation des approbations métier. Ces contrôles peuvent être complémentaires, mais aucun ne remplace les autres.

### 5.3 Rotation, sauvegarde, restauration, destruction

Définissez les événements qui entraînent une rotation : échéance planifiée, suspicion de divulgation, changement d’algorithme, migration vers un nouveau HSM, changement de propriétaire, modification de la frontière de sécurité ou exigence réglementaire. Le plan doit préciser la génération, la validation, la distribution de la nouvelle clé publique, le chevauchement des certificats, la mise à jour des services, la révocation éventuelle de l’ancien certificat et la destruction de l’ancienne clé quand les contraintes de retour arrière sont terminées.

Les sauvegardes de clés de CA méritent une politique distincte de celle des données ordinaires. Elles doivent conserver le même niveau de contrôle d’accès et de traçabilité que la clé active. Il faut tester une restauration complète dans un environnement contrôlé : une sauvegarde jamais testée ne constitue pas une preuve de reprise. Inversement, une copie de récupération qui peut être reconstituée par une seule personne depuis un poste standard peut neutraliser les bénéfices de la séparation des tâches.

Une destruction sûre n’est pas seulement l’effacement d’un fichier. Il faut tenir compte des copies exportées, supports de sauvegarde, snapshots, images, caches, journaux, répliques et systèmes de reprise. Les preuves de destruction doivent être adaptées au support et à l’environnement ; évitez de conserver dans les tickets des fragments de secrets ou des commandes qui exposent les clés.

### 5.4 Contrôles et limites de HSM/KMS

Un appel au service de signature doit lui-même être autorisé. Utilisez des identités de service distinctes, une portée d’accès minimale, des limites sur les opérations, des journaux corrélables aux demandes d’émission et des mécanismes de révocation des accès. Les comptes d’administration du HSM ne doivent pas servir à l’émission quotidienne de certificats. Les tests d’indisponibilité du HSM, de quorum insuffisant et de rotation du matériel doivent être planifiés.

L’expression « clé non exportable » ne veut pas dire que l’usage de cette clé est impossible à détourner. Il faut réduire les capacités des logiciels autorisés à appeler le HSM et distinguer l’autorité qui peut créer une clé de l’autorité qui peut demander une signature. Lorsque le produit le permet, liez les opérations à des objets ou à des politiques précis plutôt qu’à un accès générique « signer tout contenu ».


## 6. Chaîne d’émission avancée et sécurité du plan de contrôle

### 6.1 Une demande de signature n’est pas une autorisation

Une CSR contient généralement une clé publique et des attributs ou extensions demandés. Elle peut être signée par la clé privée correspondante afin de démontrer la possession de cette clé. **Elle ne prouve pas le droit de contrôler le nom DNS, d’être un administrateur, d’agir comme client mTLS ou de se voir attribuer un attribut métier.** Ces droits proviennent de sources d’identité et d’autorisations indépendantes.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 305" width="100%" height="auto" role="img" aria-label="Pipeline expert de délivrance de certificat avec contrôles d’identité, moteur de politique et signature sous HSM" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Pipeline d’émission : preuves, politique, signature et publication</text><rect x="24" y="65" width="145" height="72" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="96.5" y="90" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Demandeur</text><text x="96.5" y="110" text-anchor="middle" fill="#bae6fd" font-size="11.5">CSR · clé locale</text><rect x="205" y="65" width="145" height="72" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="277.5" y="90" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">RA / identité</text><text x="277.5" y="110" text-anchor="middle" fill="#fde68a" font-size="11.5">preuve de contrôle</text><rect x="386" y="65" width="145" height="72" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="458.5" y="90" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Moteur de règles</text><text x="458.5" y="110" text-anchor="middle" fill="#ddd6fe" font-size="11.5">profil · limites</text><rect x="567" y="65" width="126" height="72" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="630.0" y="90" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">CA émettrice</text><text x="630.0" y="110" text-anchor="middle" fill="#a7f3d0" font-size="11.5">signature HSM</text><rect x="729" y="65" width="105" height="72" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="781.5" y="90" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Publication</text><text x="781.5" y="110" text-anchor="middle" fill="#aabbd0" font-size="11.5">certificat</text><path d="M169 101 L197 101" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.2" fill="#38bdf8" opacity="0.96"><animateMotion path="M169 101 L197 101" dur="1.5s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M350 101 L378 101" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.2" fill="#fbbf24" opacity="0.96"><animateMotion path="M350 101 L378 101" dur="1.5s" begin=".3s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M531 101 L559 101" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.2" fill="#a78bfa" opacity="0.96"><animateMotion path="M531 101 L559 101" dur="1.5s" begin=".6s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M693 101 L721 101" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.2" fill="#34d399" opacity="0.96"><animateMotion path="M693 101 L721 101" dur="1.5s" begin=".9s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="210" y="185" width="460" height="66" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="440.0" y="210" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Émission refusée si une preuve est manquante</text><text x="440.0" y="230" text-anchor="middle" fill="#fecdd3" font-size="11.5">identité · droit sur le nom · profil · révocation de privilège</text><path d="M458 137 L458 169" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><g transform="translate(458 153)"><circle cx="0" cy="0" r="4" fill="#fb7185" opacity="0.9"/><animateTransform attributeName="transform" type="scale" values="0.85;1.35;0.85" dur="1.4s" begin="0s" repeatCount="indefinite" additive="sum"/></g><text x="430" y="284" text-anchor="middle" fill="#aabbd0" font-size="12">Le CSR prouve la possession de la clé correspondante, pas le droit d’obtenir n’importe quel nom ou EKU.</text></svg></div>

### 6.2 Déterminer l’identité à partir d’une source de vérité

La validation de l’identité dépend du contexte : challenge DNS pour un certificat public, enregistrement géré par un annuaire pour un certificat d’appareil, inventaire d’actifs pour un service interne, approbation métier pour une identité à privilèges, ou flux d’enrôlement propre à une plateforme. Le contrôleur doit vérifier une source de vérité appropriée et confirmer que le demandeur est autorisé à agir sur l’identité demandée.

Ne permettez pas à un demandeur de remplir librement des champs tels que `subject`, `subjectAltName`, `extendedKeyUsage`, une durée ou un identifiant de politique sans contrôle côté serveur. Un paramètre libre devient une surface d’élévation de privilège si l’application l’honore sans vérifier l’autorisation. Préférez des profils auxquels sont associés des champs dérivés de la source d’identité, et rejetez les extensions inattendues.

### 6.3 Sécuriser une API d’émission

Une API de demande de certificat doit fournir au minimum : authentification forte des appels sensibles, autorisation sur l’identité demandée, protection contre les rejeux lorsque le flux le nécessite, quotas raisonnables, limitation du débit, validation stricte des entrées, journaux complets et contrôles de changement. Les secrets de compte et les jetons API doivent être rotatables et limités à un service ou un rôle précis.

Les journaux doivent relier un identifiant de requête au demandeur, à la preuve d’identité, à la version de politique, à l’approbateur, au numéro de série du certificat, à l’empreinte, à l’émetteur et au résultat de publication. Évitez d’enregistrer les clés privées, les mots de passe ou des données personnelles qui ne sont pas nécessaires à l’audit. Le format doit faciliter l’export vers un SIEM et la corrélation avec les systèmes sources.

### 6.4 Prévenir la confusion entre CA, RA et service de publication

Une RA peut authentifier des identités, approuver des demandes et appliquer certaines règles sans détenir une clé de signature. La CA produit la signature au titre de sa délégation. Le service de publication distribue les certificats ou informations de statut. Si ces fonctions sont combinées dans un service unique, il faut documenter les risques que cette concentration introduit.

Un endpoint de publication ne doit pas devenir un endpoint de signature déguisé. Une base de certificats ne doit pas être considérée comme source de vérité pour les droits. Un certificat présent dans un annuaire n’est pas nécessairement actuel, valide, non révoqué ou associé au bon appareil. La lecture du certificat et l’autorisation d’accès doivent rester des décisions distinctes.


## 7. Construire des chaînes robustes et gérer la compatibilité

### 7.1 Construire et vérifier le chemin

La validation du chemin vérifie les signatures, les périodes de validité, les contraintes et les autres règles du profil. Elle s’appuie sur une ancre de confiance explicitement reconnue par le validateur. Un certificat auto-signé n’est pas automatiquement fiable simplement parce qu’il est correctement auto-signé.

Dans les déploiements réels, les clients ne possèdent pas tous les mêmes magasins de confiance ou les mêmes versions de bibliothèque. Une chaîne cross-signée peut offrir différents chemins de validation, mais peut aussi créer des chemins inattendus et prolonger la dépendance à une hiérarchie ancienne. Ne déployez pas une cross-signature comme solution universelle sans étudier les validateurs visés, les contraintes, les ancres installées et la durée de coexistence.

### 7.2 Exemple d’inspection avec OpenSSL

Commandes utiles dans un répertoire de laboratoire :

```bash
# Informations générales du certificat
openssl x509 -in serveur.pem -noout -subject -issuer -serial -dates

# Extensions, algorithmes et empreinte
openssl x509 -in serveur.pem -noout -text
openssl x509 -in serveur.pem -noout -fingerprint -sha256

# Examiner la CSR
openssl req -in demande.csr -noout -verify -text

# Vérifier un chemin à partir d'une ancre et d'un bundle d'intermédiaires
openssl verify -verbose -show_chain \
  -CAfile racines-de-test.pem \
  -untrusted intermediaires.pem serveur.pem

# Vérifier le nom DNS en plus du chemin
openssl verify -verbose -verify_hostname api.example.test \
  -CAfile racines-de-test.pem \
  -untrusted intermediaires.pem serveur.pem
```

Les options disponibles peuvent varier selon la version d’OpenSSL. Consultez `openssl verify -help` et `openssl x509 -help` sur la machine cible. Un résultat positif de `openssl verify` démontre le comportement de cet outil avec les options et certificats fournis ; il ne prouve pas que toutes les applications, tous les navigateurs ou toutes les bibliothèques valideront exactement de la même façon.

### 7.3 SAN et identité de service

L’identité du service doit être comparée à l’identifiant de référence que l’application veut joindre, par exemple un nom DNS ou une adresse IP. Pour un service TLS, le nom utilisé dans le SAN est important ; le champ `Common Name` historique ne doit pas servir de substitut général aux règles modernes de vérification du service. La norme de référence pour les identités de service TLS est la RFC 9525, à appliquer avec la spécification du protocole et de l’application concernée.

Les noms génériques (`*.example.test`) ont une portée et des limites précises. Le certificat `*.example.test` ne doit pas être supposé couvrir toute profondeur sous `example.test`, comme `a.b.example.test`, ni le domaine nu `example.test`, à moins que celui-ci ne figure aussi parmi les identités valides. Les règles de correspondance sont définies par le profil et le validateur. Un SAN erroné ne se corrige pas par une chaîne plus complète : il faut réémettre un certificat avec l’identité appropriée.

### 7.4 Magasins de confiance et déploiement interne

Une PKI privée n’est utile que si les validateurs nécessaires font confiance à l’ancre pertinente et appliquent le bon profil. Pour déployer une racine interne, utilisez le mécanisme de gestion de configuration ou d’appareils autorisé par l’organisation, contrôlez l’empreinte indépendamment et planifiez la suppression de l’ancienne racine. Installer une racine dans un magasin de confiance augmente son pouvoir : toute CA rattachée peut potentiellement se voir accorder une capacité d’authentification importante selon ses contraintes et les applications.

Ne conseillez pas de contourner l’erreur TLS ou de désactiver la validation du certificat pour rétablir un service. Le diagnostic consiste à identifier l’élément incorrect — nom, chaîne, date, usage, ancre, statut — puis à le corriger. Un contournement temporaire peut transformer une panne visible en vulnérabilité silencieuse.


## 8. Révocation à grande échelle : sémantique et disponibilité

### 8.1 CRL, OCSP et agrafage ne résolvent pas le même problème

Une CRL est un objet signé publié par un émetteur qui liste des certificats révoqués dans un périmètre donné. OCSP permet à un client d’interroger un répondeur sur le statut d’un certificat. L’agrafage OCSP permet à un serveur TLS de fournir une réponse OCSP signée au client, réduisant le besoin d’une requête séparée depuis le client. Le support exact et les règles de traitement varient selon le protocole, la bibliothèque, la plateforme et la politique du service.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Architecture de statut de révocation CRL OCSP avec publication, caches et politique de panne" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Révocation à l’échelle : état, distribution, cache et décision</text><rect x="28" y="68" width="165" height="75" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="110.5" y="93" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Émetteur CA</text><text x="110.5" y="113" text-anchor="middle" fill="#ddd6fe" font-size="11.5">base de révocation</text><rect x="254" y="68" width="165" height="75" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="336.5" y="93" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Publication CRL</text><text x="336.5" y="113" text-anchor="middle" fill="#bae6fd" font-size="11.5">signature · cadence</text><rect x="480" y="68" width="165" height="75" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="562.5" y="93" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Répondeur OCSP</text><text x="562.5" y="113" text-anchor="middle" fill="#a7f3d0" font-size="11.5">statut signé</text><rect x="706" y="68" width="126" height="75" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="769.0" y="93" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Validateur</text><text x="769.0" y="113" text-anchor="middle" fill="#fde68a" font-size="11.5">cache · politique</text><path d="M193 105 L246 105" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M419 105 L472 105" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M645 105 L698 105" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="4" fill="#a78bfa" opacity="0.96"><animateMotion path="M193 105 L246 105" dur="2s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#38bdf8" opacity="0.96"><animateMotion path="M419 105 L472 105" dur="2s" begin=".5s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#34d399" opacity="0.96"><animateMotion path="M645 105 L698 105" dur="2s" begin="1s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="75" y="190" width="195" height="68" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="172.5" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Disponibilité CRL</text><text x="172.5" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">URL accessible · fraîcheur</text><rect x="333" y="190" width="195" height="68" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="430.5" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Disponibilité OCSP</text><text x="430.5" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">latence · statut signé</text><rect x="591" y="190" width="195" height="68" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="688.5" y="215" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Politique de panne</text><text x="688.5" y="235" text-anchor="middle" fill="#fecdd3" font-size="11.5">hard-fail / soft-fail</text><path d="M336 143 L172 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M562 143 L430 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M769 143 L688 190" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><text x="430" y="290" text-anchor="middle" fill="#aabbd0" font-size="12">Définir les comportements de panne par application et niveau de risque ; ne pas supposer qu’ils sont universels.</text></svg></div>

Les mécanismes de statut ont des compromis :

- **Fraîcheur.** Le client doit évaluer `thisUpdate`, `nextUpdate` et les paramètres temporels applicables. Une réponse ancienne ne doit pas être assimilée sans réflexion à un statut actuel.
- **Disponibilité.** Un endpoint CRL ou OCSP indisponible ne signifie pas que le certificat est nécessairement révoqué, mais peut empêcher le client de confirmer le statut.
- **Confidentialité et observabilité.** Une requête OCSP peut révéler à un répondeur quel certificat un client utilise. L’agrafage et les caches modifient cette surface, sans l’éliminer dans tous les cas.
- **Échelle.** Une CRL volumineuse peut peser sur la distribution et le cache. Plusieurs périmètres, listes delta ou mécanismes de publication peuvent être nécessaires selon la plateforme et les exigences.
- **Sémantique.** `good`, `revoked` et `unknown` ne sont pas interchangeables. Un statut `good` dans OCSP ne remplace pas tous les autres contrôles du chemin et de l’identité.

### 8.2 Hard-fail et soft-fail : une décision de risque

En **hard-fail**, l’application refuse la connexion si elle ne peut pas effectuer la vérification de statut requise. Cela peut renforcer le contrôle contre l’usage d’un certificat révoqué, mais introduit une dépendance de disponibilité à la source de statut. En **soft-fail**, l’application peut poursuivre si elle ne parvient pas à confirmer le statut, selon les règles du produit ou du protocole. Cela réduit le risque d’interruption, mais peut laisser passer une connexion dont le statut de révocation reste inconnu.

Il n’existe pas une politique universelle adaptée à toutes les applications. L’authentification d’un administrateur sur un plan de contrôle critique et la navigation vers un site public n’ont pas nécessairement le même modèle de risque. La décision doit préciser : quelles erreurs autorisent une continuation, pendant combien de temps, quelle fraîcheur minimale est acceptée, comment le client met en cache, quel événement déclenche une alerte, et comment les équipes opèrent lorsque le service de statut est indisponible.

Évitez un `soft-fail` silencieux et permanent. Si une application ne peut pas vérifier les statuts alors que sa politique l’exige, elle doit produire un signal exploitable : métrique, journal et alerte. De même, un `hard-fail` sans redondance, sans test de bascule et sans runbook peut provoquer une panne de grande ampleur à partir d’une défaillance du service OCSP.

### 8.3 Délai de révocation de bout en bout

Le délai opérationnel entre la détection d’un incident et la prise en compte par tous les clients dépend de plusieurs étapes : décision de révocation, publication de la CRL ou mise à jour OCSP, rafraîchissement de cache, comportement des validateurs et connexions déjà établies. Révoquer un certificat dans la base de la CA ne garantit donc pas que chaque client cessera de l’accepter à la milliseconde suivante.

Pour réduire le délai, définissez les objectifs de publication, surveillez `nextUpdate`, testez les caches et documentez les limites des clients. Dans certains scénarios, il faut aussi invalider des sessions, remplacer une clé, retirer un secret de déploiement et redémarrer ou reconfigurer les services. Le statut X.509 ne résout pas à lui seul toutes les questions de session ou d’autorisation applicative.

### 8.4 Autorité de révocation et continuité du service

Les procédures doivent définir qui peut révoquer, comment les demandes d’urgence sont authentifiées, comment éviter qu’un appelant non autorisé provoque une révocation malveillante, et comment escalader lorsqu’une personne ne peut pas être jointe. Le flux de révocation ne doit pas dépendre uniquement du même compte ou du même système qu’un attaquant pourrait déjà avoir compromis.

Documentez les cas où il faut révoquer un certificat final, suspendre une émission, révoquer un certificat de CA subordonnée ou retirer une ancre de confiance. Ces actions ont des portées différentes. Une révocation de certificat final ne corrige pas une clé de CA compromise ; une révocation de CA intermédiaire ne garantit pas que chaque système a supprimé cette CA de son magasin ; le retrait d’une racine nécessite un mécanisme de distribution aux validateurs concernés.


## 9. Certificate Transparency et surveillance externe

### 9.1 Ce que CT apporte — et n’apporte pas

Certificate Transparency (CT) rend l’émission des certificats publics plus observable en permettant de vérifier l’inclusion de certificats ou de pré-certificats dans des journaux transparents et de recevoir des preuves d’inclusion. Les moniteurs peuvent détecter des certificats publics émis pour des noms connus ou inattendus et déclencher une investigation. CT est donc une source de détection et de surveillance pour certaines classes de certificats publiquement approuvés.

CT n’est pas une autorisation d’émission et ne prévient pas, à lui seul, une demande frauduleuse. La présence d’un certificat dans un journal ne veut pas automatiquement dire que celui-ci est malveillant ; un nouveau certificat peut résulter d’un renouvellement légitime, d’un changement d’hébergeur, d’un certificat de pré-production ou d’une modification de fournisseur. Le contexte est essentiel.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Flux de surveillance Certificate Transparency entre CA, logs, moniteur et SIEM" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Certificate Transparency : observer les certificats publics</text><rect x="28" y="68" width="160" height="77" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="108.0" y="93" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">CA publique</text><text x="108.0" y="113" text-anchor="middle" fill="#bae6fd" font-size="11.5">pré-certificat / cert</text><rect x="244" y="68" width="160" height="77" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="324.0" y="93" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Logs CT</text><text x="324.0" y="113" text-anchor="middle" fill="#ddd6fe" font-size="11.5">promesses SCT</text><rect x="460" y="68" width="160" height="77" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="540.0" y="93" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Moniteur</text><text x="540.0" y="113" text-anchor="middle" fill="#a7f3d0" font-size="11.5">collecte continue</text><rect x="676" y="68" width="156" height="77" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="754.0" y="93" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">SIEM / équipe</text><text x="754.0" y="113" text-anchor="middle" fill="#fde68a" font-size="11.5">alerte contextualisée</text><path d="M188 106 L236 106" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M404 106 L452 106" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M620 106 L668 106" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="4" fill="#38bdf8" opacity="0.96"><animateMotion path="M188 106 L236 106" dur="1.9s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#a78bfa" opacity="0.96"><animateMotion path="M404 106 L452 106" dur="1.9s" begin=".35s" repeatCount="indefinite" calcMode="linear"/></circle><circle r="4" fill="#34d399" opacity="0.96"><animateMotion path="M620 106 L668 106" dur="1.9s" begin=".7s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="100" y="190" width="660" height="74" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="430.0" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Détection de dérive</text><text x="430.0" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">nouveau sous-domaine · émetteur inattendu · doublon · nom ressemblant</text><text x="430.0" y="251" text-anchor="middle" fill="#aabbd0" font-size="11.5">Un certificat observé dans CT est un signal à analyser, pas automatiquement une preuve de compromission.</text><path d="M538 145 L538 190" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><g transform="translate(538 168)"><circle cx="0" cy="0" r="4" fill="#34d399" opacity="0.9"/><animateTransform attributeName="transform" type="scale" values="0.85;1.35;0.85" dur="1.7s" begin="0s" repeatCount="indefinite" additive="sum"/></g><text x="430" y="292" text-anchor="middle" fill="#aabbd0" font-size="12">La valeur vient de la couverture des noms et de la rapidité d’escalade, pas du simple stockage des logs.</text></svg></div>

### 9.2 Construire une surveillance utile

Un programme de surveillance devrait :

1. inventorier les domaines racines, sous-domaines, noms historiques, domaines de filiales et domaines à risque de typosquatting ;
2. collecter des événements depuis des sources publiques ou des moniteurs CT conformes aux règles applicables ;
3. rapprocher les SAN observés de l’inventaire interne et des changements approuvés ;
4. classer les alertes par criticité, nouveauté, émetteur, portée du nom et contexte de déploiement ;
5. relier chaque alerte à une personne responsable de l’identité ou du domaine ;
6. conserver les preuves utiles et documenter la conclusion (légitime, non expliqué, suspect ou confirmé) ;
7. mesurer le délai de détection, le taux d’alertes utiles et le temps jusqu’à décision.

Ne vous appuyez pas seulement sur des expressions régulières ou sur une liste partielle de sous-domaines. La surveillance doit prendre en compte les noms internationaux sous leur représentation normalisée, les certificats avec plusieurs SAN, les changements de propriété et les services externalisés. Les alertes nécessitent un mécanisme de validation, faute de quoi le bruit finit par faire ignorer les signaux importants.

### 9.3 Traitement d’un certificat inconnu

Lorsqu’un certificat inattendu apparaît, comparez d’abord les noms, l’émetteur, les dates, les références de changement et le propriétaire du domaine. Confirmez si le certificat a été émis par une CA publique légitime et s’il est utilisable, si l’émission respecte les politiques de l’écosystème, et si le domaine est réellement sous contrôle de l’organisation. Si l’événement reste inexpliqué, escaladez à l’équipe DNS/domaine et à l’équipe PKI ; selon la situation, ouvrez une investigation auprès de l’émetteur. Ne révoquez pas à l’aveugle un certificat légitime exploité par un fournisseur critique sans connaître l’impact, mais ne laissez pas non plus une anomalie ouverte sans propriétaire ni échéance.


## 10. Automatisation de l’émission et des renouvellements

### 10.1 Automatiser le cycle complet, pas seulement la commande

L’automatisation doit comprendre l’obtention de l’identité, la génération ou l’accès à la clé, la demande, l’approbation éventuelle, l’installation du certificat, le rechargement du service, la surveillance de l’expiration, le renouvellement, le retrait de l’ancien certificat et la preuve que la nouvelle version sert réellement les clients. Une tâche planifiée qui écrit un nouveau fichier mais laisse le serveur présenter l’ancien certificat n’est pas un renouvellement réussi.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Cycle de vie avancé des certificats et des clés : création, émission, déploiement, renouvellement, révocation, retrait" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Cycle de vie opérationnel : l’état du certificat et celui de la clé</text><rect x="25" y="75" width="145" height="72" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="97.5" y="100" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Créer</text><text x="97.5" y="120" text-anchor="middle" fill="#bae6fd" font-size="11.5">contrôle documenté</text><rect x="190" y="75" width="145" height="72" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="262.5" y="100" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Enregistrer</text><text x="262.5" y="120" text-anchor="middle" fill="#aabbd0" font-size="11.5">contrôle documenté</text><rect x="355" y="75" width="145" height="72" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="427.5" y="100" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Émettre</text><text x="427.5" y="120" text-anchor="middle" fill="#aabbd0" font-size="11.5">contrôle documenté</text><rect x="520" y="75" width="145" height="72" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="592.5" y="100" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Déployer</text><text x="592.5" y="120" text-anchor="middle" fill="#bae6fd" font-size="11.5">contrôle documenté</text><rect x="685" y="75" width="145" height="72" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="757.5" y="100" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Renouveler</text><text x="757.5" y="120" text-anchor="middle" fill="#aabbd0" font-size="11.5">contrôle documenté</text><path d="M170 111 L182 111" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#38bdf8" opacity="0.96"><animateMotion path="M170 111 L182 111" dur="1.8s" begin="0.0s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M335 111 L347 111" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#38bdf8" opacity="0.96"><animateMotion path="M335 111 L347 111" dur="1.8s" begin="0.2s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M500 111 L512 111" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#38bdf8" opacity="0.96"><animateMotion path="M500 111 L512 111" dur="1.8s" begin="0.4s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M665 111 L677 111" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#38bdf8" opacity="0.96"><animateMotion path="M665 111 L677 111" dur="1.8s" begin="0.6000000000000001s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="145" y="190" width="220" height="70" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="255.0" y="215" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Révoquer / bloquer</text><text x="255.0" y="235" text-anchor="middle" fill="#fecdd3" font-size="11.5">compromission · erreur · départ</text><rect x="495" y="190" width="220" height="70" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="605.0" y="215" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Retirer et prouver</text><text x="605.0" y="235" text-anchor="middle" fill="#fde68a" font-size="11.5">désinstaller · purger · auditer</text><path d="M592 147 L592 170" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M592 170 L255 170" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M255 170 L255 190" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M365 225 L487 225" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#fbbf24" opacity="0.96"><animateMotion path="M365 225 L487 225" dur="2s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><text x="430" y="292" text-anchor="middle" fill="#aabbd0" font-size="12">Expiration, révocation et retrait du service sont trois événements distincts à orchestrer.</text></svg></div>

### 10.2 ACME et validation du contrôle de domaine

ACME, normalisé initialement par la RFC 8555, décrit un protocole d’automatisation de la gestion des certificats. Les clients et serveurs ACME échangent des objets de compte, commandes, challenges, demandes d’émission et opérations de renouvellement ou de révocation selon ce que le serveur et son profil prennent en charge. Les détails et extensions d’un fournisseur peuvent évoluer ; inspectez les exigences de l’autorité choisie et la version du protocole prise en charge.

Les challenges classiques incluent notamment HTTP-01, DNS-01 et TLS-ALPN-01 dans les écosystèmes qui les prennent en charge. Ils prouvent le contrôle d’un nom selon la méthode retenue ; ils ne prouvent pas automatiquement qu’un demandeur peut être administrateur d’une application, d’un compte métier ou d’une autre identité. DNS-01 peut permettre de valider des noms sans exposer directement le service web, mais requiert une protection stricte des identifiants d’API DNS. Les jetons de modification DNS doivent être limités aux zones et opérations indispensables.

### 10.3 Renouvellement sans coupure

Le renouvellement fiable inclut une période de chevauchement où l’ancien certificat fonctionne encore pendant que le nouveau est distribué. Il faut contrôler l’intégrité du fichier, la clé associée, les permissions, la chaîne, le SAN, le profil, la date d’expiration et la réussite du rechargement. En cas d’échec, le service devrait conserver la configuration précédente sûre plutôt que remplacer un certificat valide par un fichier incomplet.

Mesurez le taux de renouvellement réussi, le nombre de certificats proches de l’expiration, les tentatives échouées, le temps entre émission et déploiement, et la confirmation de certificat réellement servi. La sonde de confirmation doit examiner le point de terminaison réel, y compris les équilibreurs, proxies, CDN et instances géographiques lorsque ces composants terminent TLS. Le fichier local ne prouve pas que la chaîne publique a été mise à jour.

### 10.4 Idempotence, reprise et secrets d’automatisation

Une opération est idempotente si la relancer sans changement pertinent ne produit pas d’effets secondaires inattendus. Les workflows de renouvellement doivent pouvoir être relancés après une coupure sans créer de clés orphelines, multiplier des commandes concurrentes ou supprimer le certificat actuellement en service. Utilisez des états explicites, des verrous adaptés, des journaux corrélables et une reprise testée.

Les secrets permettant de solliciter une CA, de modifier le DNS ou d’administrer le compte ACME sont souvent plus risqués qu’ils n’en ont l’air. Ils doivent être stockés dans un gestionnaire de secrets ou un mécanisme équivalent, limités dans leur portée, rotatifs, absents des journaux et non embarqués dans une image ou un dépôt. La rotation du secret ne doit pas casser silencieusement un renouvellement critique : validez la nouvelle identité, puis révoquez ou supprimez l’ancienne selon la procédure.

### 10.5 Scénario d’automatisation à tester

Concevez un test qui :

- émet un certificat de test avec une identité autorisée ;
- vérifie automatiquement la chaîne et les extensions ;
- déploie le certificat dans un environnement isolé ;
- exécute une sonde TLS depuis un client représentatif ;
- simule un échec d’émission et garantit que l’ancienne configuration reste active ;
- simule une erreur de rechargement et déclenche l’alerte appropriée ;
- confirme que la clé privée et les secrets ne sont pas dans les journaux ;
- démontre que le renouvellement est relançable sans effet indésirable.


## 11. Gestion de parc, inventaire et observabilité

### 11.1 Un inventaire doit relier les certificats à des propriétaires

Un inventaire de certificats est exploitable s’il associe chaque certificat à un service, un responsable, une application, un environnement, un emplacement de déploiement, une clé ou référence de clé, une CA émettrice, une date de fin, un SAN, des usages, un mécanisme de renouvellement et un statut de conformité. Une liste de certificats sans propriétaire peut permettre de repérer une expiration, mais pas d’organiser la correction.

Les sources d’inventaire peuvent inclure les CA, les orchestrateurs, les gestionnaires de secrets, les clouds, les équilibreurs de charge, les reverse proxies, les serveurs web, les scanners autorisés et les journaux de renouvellement. Aucune source n’est complète à elle seule. Prévoyez une réconciliation qui identifie les certificats observés mais inconnus, les certificats délivrés jamais déployés et les certificats encore servis après leur retrait annoncé.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Observabilité PKI avec émission, renouvellement, validation, confiance et tableau de bord de service" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Observabilité PKI : indicateurs à relier aux responsabilités</text><rect x="30" y="65" width="175" height="80" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="117.5" y="90" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Émission</text><text x="117.5" y="110" text-anchor="middle" fill="#bae6fd" font-size="11.5">SLO délivrance</text><text x="117.5" y="126" text-anchor="middle" fill="#bae6fd" font-size="11.5">file / taux de refus</text><rect x="245" y="65" width="175" height="80" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="332.5" y="90" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Renouvellement</text><text x="332.5" y="110" text-anchor="middle" fill="#a7f3d0" font-size="11.5">certificats à échéance</text><text x="332.5" y="126" text-anchor="middle" fill="#a7f3d0" font-size="11.5">succès avant date</text><rect x="460" y="65" width="175" height="80" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="547.5" y="90" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Validation</text><text x="547.5" y="110" text-anchor="middle" fill="#ddd6fe" font-size="11.5">latence OCSP</text><text x="547.5" y="126" text-anchor="middle" fill="#ddd6fe" font-size="11.5">erreurs de chaîne</text><rect x="675" y="65" width="150" height="80" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="750.0" y="90" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Confiance</text><text x="750.0" y="110" text-anchor="middle" fill="#fde68a" font-size="11.5">CT · racines</text><text x="750.0" y="126" text-anchor="middle" fill="#fde68a" font-size="11.5">écarts de politique</text><rect x="104" y="190" width="652" height="74" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="430.0" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Tableau de bord orienté service</text><text x="430.0" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">certificats orphelins · expiration proche · empreintes inconnues · rotation non terminée</text><text x="430.0" y="251" text-anchor="middle" fill="#aabbd0" font-size="11.5">Chaque alerte doit avoir un propriétaire, une gravité, un runbook et un délai de traitement.</text><path d="M117 145 L117 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M332 145 L332 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M547 145 L547 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M750 145 L750 190" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><text x="430" y="292" text-anchor="middle" fill="#aabbd0" font-size="12">Mesurer le résultat (continuité, confiance, délais de remédiation), pas seulement le nombre de certificats.</text></svg></div>

### 11.2 Indicateurs qui aident à prendre une décision

Un tableau de bord expert inclut par exemple :

- pourcentage de certificats connus avec propriétaire désigné ;
- nombre de certificats expirant dans les fenêtres de 7, 14, 30 et 60 jours, selon les durées et politiques applicables ;
- taux de renouvellement sans intervention manuelle ;
- taux de renouvellement échoué et délai médian de récupération ;
- nombre de certificats non conformes au profil approuvé ;
- fraîcheur des CRL et disponibilité/latence des répondeurs OCSP ;
- durée entre demande, approbation, émission et déploiement ;
- nombre d’identités observées via CT sans changement approuvé connu ;
- nombre de certificats orphelins et de clés privées dont le propriétaire est inconnu ;
- succès des tests de restauration et exercices de rotation.

Il est utile d’avoir aussi des indicateurs de résultat : interruptions causées par un certificat, temps de détection d’une émission suspecte, temps entre décision de révocation et remédiation du service, part des systèmes confirmés comme migrés, et nombre de dérogations qui dépassent leur date de fin.

### 11.3 SLO et alertes graduées

Les SLO doivent être formulés en fonction de l’expérience des services et des clients. Par exemple, la disponibilité d’un endpoint OCSP peut être une métrique, mais la finalité est que les validateurs obtiennent un statut suffisamment frais dans les délais et selon la politique requise. Le taux d’émission réussie peut être un indicateur, mais la finalité est qu’un service légitime reçoive un certificat correct et le serve avant l’expiration. Évitez les SLO qui récompensent l’émission rapide au détriment de contrôles d’identité nécessaires.

Les alertes ont besoin d’un propriétaire, d’une sévérité, d’une condition de déclenchement, d’un runbook, d’un délai d’action et d’un mécanisme d’escalade. Une alerte d’expiration dans 60 jours est différente d’une alerte sur une CA dont la clé peut être compromise. Les alertes répétitives qui ne conduisent à aucune action finissent par être ignorées ; mesurez le bruit et supprimez les signaux redondants sans masquer les risques.


## 12. Incident PKI : clé de service, CA émettrice ou racine

### 12.1 Trier l’incident avant de choisir l’action

Un incident de certificat peut être causé par une clé finale copiée, une émission frauduleuse, un profil modifié, une erreur dans le magasin de confiance, une chaîne expirée, un endpoint de statut indisponible ou une compromission de CA. La première tâche consiste à préserver les preuves et à qualifier l’étendue : quels certificats, quelles clés, quels noms, quels émetteurs, quels systèmes et quels validateurs sont concernés ?

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 350" width="100%" height="auto" role="img" aria-label="Arbre de décision pour incident de compromission PKI et choix de portée de remédiation" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Réponse à incident : choisir la portée de la remédiation</text><rect x="300" y="55" width="260" height="58" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="430.0" y="80" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Signal incident</text><text x="430.0" y="100" text-anchor="middle" fill="#fecdd3" font-size="11.5">clé divulguée · émission suspecte</text><path d="M430 113 L430 142" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#fb7185" opacity="0.96"><animateMotion path="M430 113 L430 142" dur="1.3s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="284" y="142" width="292" height="60" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="430.0" y="167" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Qualifier le périmètre</text><text x="430.0" y="187" text-anchor="middle" fill="#fde68a" font-size="11.5">clé ? CA ? certificat final ? chaîne ?</text><path d="M360 202 L205 235" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M500 202 L655 235" fill="none" stroke="#7291b6" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><rect x="35" y="235" width="270" height="65" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="170.0" y="260" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">Clé finale compromise</text><text x="170.0" y="280" text-anchor="middle" fill="#fecdd3" font-size="11.5">isoler · révoquer · réémettre</text><rect x="555" y="235" width="270" height="65" rx="12" fill="#301c24" stroke="#fb7185" stroke-width="1.5"/><text x="690.0" y="260" text-anchor="middle" fill="#fff1f2" font-size="15" font-weight="750">CA compromise / doute fort</text><text x="690.0" y="280" text-anchor="middle" fill="#fecdd3" font-size="11.5">contenir · suspendre émission</text><text x="690.0" y="296" text-anchor="middle" fill="#fecdd3" font-size="11.5">rotation hiérarchie / confiance</text><text x="430" y="326" text-anchor="middle" fill="#aabbd0" font-size="12">Ne pas confondre révoquer un certificat et restaurer la confiance après compromission d’une CA.</text></svg></div>

### 12.2 Compromission d’une clé finale

Actions possibles, selon le contexte et le plan d’incident : isoler le système affecté, arrêter l’usage de la clé divulguée, révoquer le certificat, générer une clé nouvelle dans un environnement maîtrisé, réémettre le certificat et le déployer, invalider les secrets ou sessions qui dépendaient de l’ancienne identité lorsque nécessaire, puis vérifier que tous les points de terminaison servent la nouvelle chaîne. Conservez les éléments de preuve et recherchez le chemin de divulgation (image, sauvegarde, permissions, accès d’administration, pipeline CI/CD).

Ne réutilisez pas simplement la même clé privée pour un certificat de remplacement lorsque la suspicion porte sur sa compromission. Un nouveau certificat associé à la clé exposée ne restaure pas la confidentialité ni l’exclusivité de cette clé. Le remplacement doit inclure une clé distincte, puis le retrait des copies anciennes conformément au plan de réponse.

### 12.3 Compromission d’une CA émettrice

La compromission d’une CA émettrice nécessite une action plus large : suspendre ou limiter l’émission, conserver les journaux et les preuves, identifier la période et les certificats potentiellement émis sans autorisation, vérifier les chemins descendants et décider s’il faut révoquer la CA intermédiaire. Il faut également coordonner les services qui utilisent cette chaîne, préparer une chaîne de remplacement et s’assurer que les clients prennent en compte la nouvelle hiérarchie.

Une révocation de l’intermédiaire peut avoir un impact important sur tous les certificats qu’elle a délivrés. La décision ne doit donc pas attendre une perfection impossible des preuves si la clé semble réellement compromise, mais elle exige un processus d’incident adapté aux conséquences. L’organisation doit avoir préalablement défini qui peut prendre cette décision, comment informer les propriétaires d’applications et comment tester la nouvelle chaîne.

### 12.4 Compromission de la racine ou perte de confiance

Une racine compromise remet potentiellement en cause toutes les délégations qui en dépendent. La réponse peut nécessiter une nouvelle racine, de nouvelles CA intermédiaires, un plan de distribution du trust anchor aux clients, la migration des certificats finaux et le retrait de l’ancienne confiance. Une révocation classique d’un certificat final n’est pas suffisante. L’organisation doit vérifier les systèmes hors ligne, les appareils non gérés, les applications qui embarquent leur propre magasin, les environnements de récupération et les images déployées depuis longtemps.

La préparation est essentielle : inventaire des validateurs, canal de distribution des racines, mécanisme de déploiement d’urgence, procédure d’approbation, sauvegardes maîtrisées et exercice de migration. Si une organisation découvre qu’elle ne sait pas où sa racine est installée, la difficulté ne vient pas seulement de l’incident mais d’un déficit d’inventaire et de gouvernance.

### 12.5 Chronologie, preuve et communication

Un runbook de réponse doit préciser qui dirige l’incident, qui décide de la révocation, qui contrôle le plan cryptographique, qui déploie la chaîne de remplacement, qui communique avec les propriétaires de domaines/services, qui documente les preuves et qui confirme la remédiation. Les communications doivent être factuelles : portée connue, portée inconnue, décision prise, impact prévu, prochaine vérification et canal de contact.

Conservez les CSR, numéros de série, empreintes, journaux d’approbation, traces d’accès au HSM, événements d’administration et preuves de déploiement pertinents, avec des contrôles d’intégrité et un accès limité. N’ajoutez pas de secrets ou de clés privées au dossier d’incident. Une revue post-incident doit identifier les causes racines, les contrôles manquants, les mesures de détection ratées et les tests qui empêcheront la répétition.


## 13. Agilité cryptographique et préparation aux transitions

### 13.1 Inventorier avant de migrer

La migration cryptographique ne commence pas par le remplacement d’un algorithme au hasard. Il faut inventorier les usages de clés, certificats, signatures, protocoles, bibliothèques, HSM, appareils, clients hérités, infrastructures de révocation, systèmes d’archivage et dépendances éditeur. Une clé peut être utilisée pour plusieurs certificats ; un certificat peut apparaître dans plusieurs magasins ; un composant matériel peut ne pas supporter l’algorithme cible.

<div class="pki-diagram" style="box-sizing:border-box;width:100%;margin:1.25rem 0 1.6rem;padding:1rem;overflow:hidden;border:1px solid #253246;border-radius:16px;background:#0b111b;color:#e8f0fb"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 315" width="100%" height="auto" role="img" aria-label="Boucle d’agilité cryptographique avec inventaire, classification du risque, migration et mesure" style="display:block;max-width:100%;height:auto;font-family:Inter,Segoe UI,Arial,sans-serif"><text x="24" y="29" fill="#f1f5f9" font-size="17" font-weight="750">Agilité cryptographique : inventaire, migration, validation et retour arrière</text><rect x="40" y="70" width="170" height="72" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.5"/><text x="125.0" y="95" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Inventaire</text><text x="125.0" y="115" text-anchor="middle" fill="#bae6fd" font-size="11.5">algorithme · taille</text><text x="125.0" y="131" text-anchor="middle" fill="#bae6fd" font-size="11.5">certificat · dépendance</text><rect x="260" y="70" width="170" height="72" rx="12" fill="#302617" stroke="#fbbf24" stroke-width="1.5"/><text x="345.0" y="95" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="750">Classer le risque</text><text x="345.0" y="115" text-anchor="middle" fill="#fde68a" font-size="11.5">durée de vie des données</text><text x="345.0" y="131" text-anchor="middle" fill="#fde68a" font-size="11.5">contrainte / échéance</text><rect x="480" y="70" width="170" height="72" rx="12" fill="#241b38" stroke="#a78bfa" stroke-width="1.5"/><text x="565.0" y="95" text-anchor="middle" fill="#f5f3ff" font-size="15" font-weight="750">Piloter la migration</text><text x="565.0" y="115" text-anchor="middle" fill="#ddd6fe" font-size="11.5">test dual-stack</text><text x="565.0" y="131" text-anchor="middle" fill="#ddd6fe" font-size="11.5">interopérabilité</text><rect x="700" y="70" width="125" height="72" rx="12" fill="#102a25" stroke="#34d399" stroke-width="1.5"/><text x="762.5" y="95" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="750">Mesurer</text><text x="762.5" y="115" text-anchor="middle" fill="#a7f3d0" font-size="11.5">taux · erreurs</text><path d="M210 106 L252 106" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.1" fill="#38bdf8" opacity="0.96"><animateMotion path="M210 106 L252 106" dur="1.6s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M430 106 L472 106" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.1" fill="#fbbf24" opacity="0.96"><animateMotion path="M430 106 L472 106" dur="1.6s" begin=".3s" repeatCount="indefinite" calcMode="linear"/></circle><path d="M650 106 L692 106" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3.1" fill="#a78bfa" opacity="0.96"><animateMotion path="M650 106 L692 106" dur="1.6s" begin=".6s" repeatCount="indefinite" calcMode="linear"/></circle><rect x="115" y="190" width="630" height="70" rx="12" fill="#111c2a" stroke="#34465d" stroke-width="1.5"/><text x="430.0" y="215" text-anchor="middle" fill="#e5edf8" font-size="15" font-weight="750">Boucle de retour</text><text x="430.0" y="235" text-anchor="middle" fill="#aabbd0" font-size="11.5">compatibilité des clients · performance · alertes · retour arrière testé</text><path d="M760 142 L760 169" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M760 169 L430 169" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><path d="M430 169 L430 190" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-dasharray="7 7"/><circle r="3" fill="#34d399" opacity="0.96"><animateMotion path="M760 169 L430 169" dur="2.5s" begin="0s" repeatCount="indefinite" calcMode="linear"/></circle><text x="430" y="292" text-anchor="middle" fill="#aabbd0" font-size="12">L’agilité cryptographique est un processus d’ingénierie et de gouvernance, pas un remplacement improvisé d’algorithme.</text></svg></div>

### 13.2 Classer selon la durée de protection attendue

Le risque ne dépend pas seulement du moment où l’algorithme pourrait être affaibli. Il dépend aussi de la durée pendant laquelle les données doivent rester confidentielles, de la durée de validité des certificats, de la durée de vie des signatures et archives, de la capacité à remplacer les logiciels et du temps nécessaire pour déployer de nouvelles clés. Les données sensibles qui doivent rester secrètes pendant longtemps peuvent exiger une planification différente des certificats éphémères d’un service de test.

Il faut distinguer les fonctions : échange de clés, signatures, hachage, authentification, stockage et signature de code n’ont pas nécessairement les mêmes chemins de migration. Un changement de certificat n’entraîne pas automatiquement le remplacement de tous les mécanismes cryptographiques du protocole, ni une mise à jour de tous les clients.

### 13.3 Tester l’interopérabilité et le retour arrière

Pour une migration, préparez un groupe pilote représentatif, des tests de validation négative et positive, des métriques d’erreur et de performance, une procédure de retour arrière, un plan d’extension graduelle et une date de retrait de l’ancien mécanisme. Si la solution nécessite une période où deux configurations coexistent, la politique doit préciser laquelle est prioritaire et dans quelles circonstances la solution ancienne reste autorisée.

Évitez une « agilité » qui signifie permettre toutes les versions ou tous les algorithmes sans contrôle. La flexibilité doit être bornée par une politique : inventaire des mécanismes autorisés, dérogations limitées dans le temps, télémétrie d’usage et tests réguliers de retrait. Le but est de pouvoir évoluer vite lorsque c’est nécessaire, pas de maintenir des choix faibles indéfiniment au nom de la compatibilité.

### 13.4 Post-quantique : préparer sans promettre l’interopérabilité universelle

Les standards NIST pour la cryptographie post-quantique, notamment FIPS 203 (ML-KEM), FIPS 204 (ML-DSA) et FIPS 205 (SLH-DSA), constituent des repères importants pour la planification cryptographique. Leur disponibilité ne signifie pas que chaque pile TLS, HSM, CA, navigateur ou format X.509 les prend déjà en charge de manière interopérable. Les équipes doivent suivre les profils, les recommandations et les implémentations effectivement approuvés pour leur écosystème, et ne pas inventer des extensions ou formats propriétaires pour obtenir une compatibilité apparente.

Le travail expert à mener immédiatement est l’inventaire, la classification des données selon leur durée de sensibilité, la cartographie des dépendances, les essais avec les fournisseurs et la capacité à renouveler les certificats et clés rapidement. Une migration cryptographique sérieuse est un programme de changement, pas une modification isolée d’une option de configuration.


## 14. Conformité des certificats TLS publics et internes

### 14.1 Les exigences ne sont pas toutes les mêmes

Une PKI interne contrôlée par une organisation et une PKI publique distribuée dans les magasins de confiance des navigateurs ou plateformes ne sont pas soumises exactement au même modèle de gouvernance. Les certificats TLS publiquement approuvés sont soumis à des exigences d’écosystème, des règles de validation et des audits spécifiques. Les Baseline Requirements du CA/Browser Forum forment une référence opérationnelle importante, mais ne doivent pas être confondues avec la politique interne de toutes les entreprises.

À la date de rédaction de ce cours, la page officielle du CA/Browser Forum indique la version 2.3.0 des Baseline Requirements pour les certificats de serveur TLS publiquement approuvés, datée du 7 septembre 2026. Les exigences peuvent évoluer et certaines dates d’entrée en vigueur diffèrent selon le type de certificat et les votes adoptés. Il faut consulter la version officielle en vigueur au moment de concevoir ou d’auditer le service, plutôt que figer dans le code un numéro de version sans processus de mise à jour.

Pour une CA publique, les sujets à maîtriser comprennent l’authentification du contrôle des identités concernées, les restrictions de profils, l’usage et la protection des clés, l’audit, les rapports d’incident, les délais, la journalisation et les exigences de publication. Dans un cadre interne, l’organisation définit ses propres exigences, mais elle doit être explicite sur les garanties fournies et sur les usages acceptés par les applications.

### 14.2 Audit et preuves

Un audit solide ne se limite pas à des captures d’écran de configuration. Il doit associer les exigences aux contrôles, aux propriétaires, aux preuves et à une méthode de vérification. Les preuves peuvent comprendre des configurations versionnées, des journaux exportés, des résultats de tests, des procès-verbaux de cérémonie, des inventaires d’accès, les résultats de restauration et les événements de déploiement.

L’échantillonnage doit couvrir les cas risqués, pas seulement les certificats ordinaires : certificat privilégié, certificat à SAN multiples, refus de demande, révocation urgente, renouvellement en échec, rotation de clé, changement de politique et incident de publication. L’auditeur doit pouvoir vérifier qu’une demande non autorisée est rejetée et que le système journalise la décision sans exposer de secret.

### 14.3 Dérogations

Les dérogations techniques doivent préciser le risque, le périmètre, le propriétaire, les compensations, la date d’expiration, la validation par l’autorité appropriée et la méthode de retrait. Une dérogation sans date de fin est une nouvelle politique non déclarée. Une dérogation qui n’est pas revue régulièrement peut maintenir une dépendance historique ou un algorithme fragile après la fin de sa justification.


## 15. TLS, identité et certificats spécialisés

### 15.1 Le certificat n’est qu’un composant de TLS

TLS fournit un canal sécurisé et peut authentifier le serveur, ainsi que le client si le protocole et la configuration le prévoient. La sécurité dépend de la négociation, du protocole, des suites cryptographiques, de la validation de certificat, de la vérification d’identité, de la gestion des clés et de la configuration des extrémités. La RFC 9846, publiée en juillet 2026, est la référence révisée de TLS 1.3 et remplace la RFC 8446. Elle conserve le numéro de version TLS 1.3 tout en clarifiant et en ajustant plusieurs exigences.

TLS 1.3 ne rend pas automatiquement une application sûre. Une application doit encore déterminer quel nom est attendu, quels certificats sont acceptables, si un certificat client est requis, comment l’identité authentifiée mappe vers un compte, et quelles actions sont autorisées. Un service qui accepte n’importe quel certificat client signé par une CA interne sans vérifier le SAN, l’EKU et la correspondance avec son annuaire peut authentifier un client non autorisé.

### 15.2 mTLS à l’échelle

Dans le TLS mutuel, le client et le serveur s’authentifient par certificat selon la configuration du protocole. Le certificat client doit être relié à une identité système claire : compte de service, workload, appareil ou utilisateur. Il faut définir le propriétaire de cette identité, son cycle de vie, le droit de renouvellement, la stratégie de révocation et la façon dont les applications traduisent le certificat en permissions.

Pour les microservices, la PKI doit tenir compte de la création et de la disparition rapides des workloads, des rotations fréquentes, de la découverte de services, des identités temporaires et du comportement en cas d’indisponibilité du plan de contrôle. Une clé partagée par toute une flotte facilite peut-être l’installation mais transforme chaque fuite en incident de grande portée. Des identités et clés par workload ou par unité de déploiement peuvent réduire le rayon d’impact, sous réserve que le renouvellement soit fiable.

### 15.3 Certificats spécialisés

Les certificats de signature de code, S/MIME, signature de document, authentification utilisateur, équipement réseau ou signature de CA peuvent avoir des exigences très différentes. Réutiliser un profil TLS serveur pour un autre usage ou accepter un certificat parce qu’il a une chaîne valable peut créer une confusion d’usage. Définissez le profil pour chaque but, les sources d’identité et les contraintes propres à l’usage, puis testez le comportement des applications consommatrices.

La portée d’un certificat résulte de plusieurs facteurs : identités, clés, usages, politiques, contraintes de chaîne et décision de l’application. Aucun champ seul ne doit être traité comme une preuve universelle de l’autorisation métier.


## 16. Laboratoire expert : inspection et vérifications négatives

Les exercices suivants sont destinés à un environnement isolé avec des certificats de test. Ils ne constituent pas une procédure de mise en place d’une CA de production. Vérifiez la version locale d’OpenSSL et utilisez des fichiers temporaires.

### Atelier A — Inspecter un certificat et son empreinte

```bash
openssl x509 -in serveur.pem -noout -subject -issuer -serial -dates
openssl x509 -in serveur.pem -noout -fingerprint -sha256
openssl x509 -in serveur.pem -noout -text
```

**À observer :** sujet et émetteur, dates, algorithme et paramètres de clé, `basicConstraints`, `keyUsage`, `extendedKeyUsage`, SAN, politiques éventuelles, identifiants d’autorité et de sujet. L’empreinte identifie l’encodage exact du certificat examiné ; elle ne prouve pas à elle seule que ce certificat est digne de confiance.

### Atelier B — Tester le nom DNS

```bash
openssl verify -verify_hostname api.example.test \
  -CAfile racines-de-test.pem \
  -untrusted intermediaires.pem serveur.pem
```

Changez `api.example.test` pour un autre nom non présent dans le SAN. Le test doit échouer si la chaîne est autrement valide mais que le certificat ne correspond pas à l’identité attendue. Expliquez pourquoi la réussite d’une signature ne répare pas un SAN erroné.

### Atelier C — Tester l’utilisation

Dans une configuration de test où les options nécessaires sont prises en charge :

```bash
openssl verify -purpose sslserver \
  -CAfile racines-de-test.pem \
  -untrusted intermediaires.pem serveur.pem
```

Comparez les informations de `keyUsage` et d’`extendedKeyUsage` avec l’usage attendu. Faites un test négatif avec un certificat qui ne correspond pas à l’usage prévu. Ne désactivez pas la vérification de but pour faire passer le test.

### Atelier D — Vérifier le déploiement effectif

Utilisez un client TLS représentatif pour consulter le certificat présenté par l’endpoint, pas seulement le fichier sur disque. Avec OpenSSL, la commande suivante peut aider dans un laboratoire :

```bash
openssl s_client -connect api.example.test:443 \
  -servername api.example.test -showcerts -verify_return_error
```

Adaptez `-CAfile` ou les paramètres d’ancre à l’environnement de test si nécessaire. Examinez le certificat leaf, les intermédiaires présentés et les erreurs détaillées. Le SNI doit correspondre au nom que le client utilise pour atteindre le service. La commande et la sortie varient selon la version et la configuration.

### Atelier E — Simuler un échec de renouvellement

Dans une application de test, forcez un renouvellement à échouer avant l’installation. Vérifiez que : le certificat valide actuel reste servi ; l’échec est journalisé ; le responsable reçoit une alerte ; la tâche est relançable ; l’équipe peut déterminer si l’échec est dû à la validation d’identité, à la CA, au DNS, au secret d’API ou au déploiement. Puis simulez un redémarrage raté et documentez le retour à la configuration sûre.

### Atelier F — Examiner le statut et la politique

Consultez les points de publication CRL/OCSP indiqués par le certificat, dans la mesure prise en charge par les outils et l’environnement de laboratoire. Distinguez l’absence de réponse, un statut inconnu, une réponse obsolète et une révocation confirmée. Documentez le comportement attendu de l’application dans chacun de ces cas. Un diagnostic expert formule la décision de sécurité attendue avant de changer une option.

### Questions d’évaluation

1. Pourquoi une CSR signée ne prouve-t-elle pas le contrôle du domaine demandé ?
2. Dans quels cas une CA intermédiaire spécialisée réduit-elle le rayon d’impact ? Dans quels cas augmente-t-elle la complexité sans bénéfice net ?
3. Quelle est la différence entre une clé privée non exportable et une interface de signature impossible à détourner ?
4. Pourquoi l’indisponibilité d’OCSP ne doit-elle pas être interprétée systématiquement comme une révocation ?
5. Quelles preuves démontrent qu’un certificat renouvelé est réellement déployé ?
6. Quelle action est nécessaire si la clé d’une CA émettrice est compromise, et pourquoi le remplacement du seul certificat final ne suffit-il pas ?
7. Quels éléments faut-il inventorier avant une transition d’algorithme ?
8. Comment une surveillance CT peut-elle détecter une émission inattendue tout en limitant les faux positifs ?
9. Pourquoi un certificat présent dans un magasin de confiance ne constitue-t-il pas une autorisation métier universelle ?
10. Comment définir un SLO de renouvellement qui ne récompense pas l’abaissement des contrôles d’identité ?


## 17. Étude de cas finale : PKI d’entreprise critique

### Contexte

Une organisation exploite un portail public, des API internes, des appareils administrés et plusieurs milliers de workloads. Les services publics utilisent une CA reconnue par les navigateurs ; les services internes utilisent une hiérarchie privée. Des certificats sont provisionnés automatiquement mais l’inventaire ne relie pas toujours chaque certificat à un propriétaire. L’équipe a observé des certificats expirés dans des environnements isolés, des échecs intermittents de vérification de statut et des clés présentes dans d’anciennes images de déploiement.

### Travail demandé

Concevez une architecture et un plan d’exploitation qui répondent aux exigences suivantes :

- séparer la confiance publique, la confiance interne, les environnements de test et les workloads de production ;
- expliquer quels rôles de CA sont hors ligne et quelles CA peuvent émettre automatiquement ;
- décrire les contrôles d’identité et de profil avant signature ;
- réduire les cas où une personne peut demander, approuver, faire signer et effacer la preuve d’une émission ;
- définir l’inventaire et les métriques de renouvellement ;
- proposer une stratégie de publication et de statut de révocation adaptée à la criticité des services ;
- concevoir une surveillance d’émission publique et une procédure d’investigation des noms inattendus ;
- définir la procédure de rotation d’une clé de workload et le processus de réponse si une CA émettrice est suspectée compromise ;
- planifier des tests de restauration, des exercices d’incident et une migration cryptographique future.

### Grille d’évaluation

| Domaine | Niveau attendu pour réussir |
|---|---|
| Architecture | Les frontières de confiance sont explicites ; les rôles et flux sont justifiés par les risques. |
| Émission | Chaque profil relie une identité prouvée à un usage autorisé ; les tests négatifs sont prévus. |
| Clés | Génération, accès, sauvegarde, rotation et destruction ont des responsables et des preuves. |
| Cycle de vie | Émission, déploiement réel, renouvellement, retrait et révocation sont distincts et suivis. |
| Résilience | SLO, cache de statut, bascule, sauvegardes et retour arrière sont testés. |
| Incident | Les réponses distinguent compromission d’une clé finale, d’une CA émettrice et de la racine. |
| Gouvernance | Les règles sont approuvées, versionnées, auditées et assorties de propriétaires. |
| Agilité | Inventaire et pilote existent avant le changement général ; ancien mécanisme retiré selon une politique. |

La meilleure réponse n’est pas forcément l’architecture avec le plus de composants. Elle est celle qui réduit le risque avec des responsabilités compréhensibles, une automatisation sûre et des preuves que les contrôles fonctionnent dans la réalité.


## 18. Anti-patterns d’une PKI mal gouvernée

- **Une racine dans chaque environnement.** Les racines prolifèrent sans propriétaire ni plan de retrait. Conséquence : magasin de confiance opaque et confiance plus large que prévu.
- **Une CA universelle pour tout.** Production, test, clients, serveurs et administrateurs partagent le même domaine de confiance sans justification. Conséquence : une erreur d’émission peut affecter plusieurs catégories de services.
- **Autorisation fondée seulement sur le CSR.** Les extensions demandées par l’appelant sont copiées sans politique. Conséquence : SAN ou usages non autorisés.
- **HSM sans contrôle du plan de contrôle.** La clé ne sort pas, mais une application compromise peut appeler l’opération de signature. Conséquence : abus cryptographique sans extraction de clé.
- **Renouvellement testé uniquement sur le fichier.** Le nouveau fichier existe, mais le service présente encore l’ancien certificat. Conséquence : expiration ou identité erronée en production.
- **Révocation sans vérification de propagation.** Le statut est changé dans la CA, mais les caches et validateurs ne sont pas testés. Conséquence : fausse impression d’éradication.
- **Alerte sans propriétaire.** Le système signale des expirations ou certificats inconnus sans responsable identifié. Conséquence : fatigue d’alerte.
- **Compatibilité sans date de retrait.** Un algorithme ou une racine ancienne reste autorisé indéfiniment. Conséquence : la dérogation devient la norme.
- **Sauvegarde jamais restaurée.** Le plan de reprise est un document non prouvé. Conséquence : impossibilité de reprendre ou contrôle moins strict à l’urgence.
- **Suppression d’une racine prise à la légère.** Une équipe retire la CA d’un seul serveur sans inventaire des applications et appareils. Conséquence : panne ou maintien de confiance non contrôlé ailleurs.


## 19. Checklist opérationnelle avant mise en production

### Architecture et confiance

- [ ] Les racines, intermédiaires et domaines d’identité ont un propriétaire et une justification documentée.
- [ ] Les magasins de confiance concernés sont inventoriés et leur mise à jour est testée.
- [ ] Les contraintes de CA, les usages, les noms et les profils sont testés avec les validateurs réels.
- [ ] Les environnements de test ne peuvent pas émettre une identité acceptée en production sans une décision explicite.

### Clés et droits

- [ ] Les clés critiques ont une politique de génération, de stockage, de sauvegarde, de restauration, de rotation et de destruction.
- [ ] Les rôles d’opération, d’approbation et d’administration sont suffisamment séparés.
- [ ] Les accès API, les comptes de service et les droits d’appel au HSM sont minimaux et audités.
- [ ] Les preuves de cérémonie et les journaux sont protégés et ne contiennent pas de secrets.

### Émission et cycle de vie

- [ ] Chaque profil est versionné, revu, testé et associé à une source d’identité.
- [ ] Les demandes hors profil sont refusées et journalisées.
- [ ] Les renouvellements sont idempotents, relançables et testés avant l’expiration.
- [ ] Le point de terminaison réel est sondé après déploiement ; le retrait de l’ancien certificat est confirmé.
- [ ] Les propriétaires reçoivent des alertes avant expiration avec une procédure d’escalade.

### Révocation et incident

- [ ] La fraîcheur et la disponibilité des CRL/OCSP sont surveillées.
- [ ] La politique hard-fail/soft-fail est explicite par usage et testée.
- [ ] Les scénarios de clé finale, CA émettrice et racine ont des runbooks distincts.
- [ ] Les plans de rotation et de retrait de racines ont été exercés sur des clients représentatifs.

### Surveillance, conformité et migration

- [ ] Les émissions inattendues sont rapprochées de l’inventaire et des changements approuvés.
- [ ] Les métriques possèdent un propriétaire, un SLO ou une limite, et une action associée.
- [ ] Les dérogations sont datées, approuvées et révisées.
- [ ] Les dépendances cryptographiques sont inventoriées ; les migrations comprennent un pilote, des tests et un retour arrière.


## 20. Références normatives et ressources

Les standards et politiques peuvent être révisés. Avant une implémentation ou un audit, consultez le texte normatif dans sa version en vigueur et vérifiez les errata ainsi que les profils spécifiques à votre écosystème.

- **RFC 5280 — Internet X.509 Public Key Infrastructure Certificate and CRL Profile** : profil X.509, extensions, chaînes et CRL. <https://www.rfc-editor.org/rfc/rfc5280.html>
- **RFC 9525 — Service Identity in TLS** : représentation et vérification des identités de service TLS. <https://www.rfc-editor.org/rfc/rfc9525.html>
- **RFC 9846 — The Transport Layer Security (TLS) Protocol Version 1.3** : mise à jour de TLS 1.3 publiée en juillet 2026, qui remplace RFC 8446. <https://www.rfc-editor.org/rfc/rfc9846.html>
- **RFC 6960 — Online Certificate Status Protocol (OCSP)** : statut en ligne des certificats. <https://www.rfc-editor.org/rfc/rfc6960.html>
- **RFC 8555 — Automatic Certificate Management Environment (ACME)** : automatisation de l’émission et de la gestion des certificats. <https://www.rfc-editor.org/rfc/rfc8555.html>
- **RFC 9162 — Certificate Transparency Version 2.0** : structures de transparence et preuves d’inclusion. <https://www.rfc-editor.org/rfc/rfc9162.html>
- **CA/Browser Forum — Baseline Requirements** : exigences applicables aux certificats TLS publiquement approuvés, version en vigueur à contrôler au moment de l’usage. <https://cabforum.org/working-groups/server/baseline-requirements/requirements/>
- **NIST SP 800-57 Part 1** : recommandations de gestion des clés cryptographiques. <https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final>
- **NIST FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)**. <https://csrc.nist.gov/pubs/fips/203/final>
- **NIST FIPS 204 — Module-Lattice-Based Digital Signature Standard (ML-DSA)**. <https://csrc.nist.gov/pubs/fips/204/final>
- **NIST FIPS 205 — Stateless Hash-Based Digital Signature Standard (SLH-DSA)**. <https://csrc.nist.gov/pubs/fips/205/final>
- **OpenSSL documentation** : syntaxe et options propres à la version installée. <https://docs.openssl.org/>


## Conclusion

Une PKI experte est un système de confiance gouverné, et non un simple serveur qui signe des certificats. Sa robustesse dépend de frontières claires entre les autorités, d’une politique d’émission appliquée par des contrôles testables, d’une gestion rigoureuse des clés, d’une automatisation réellement vérifiée, d’une stratégie explicite de statut et de révocation, d’une observabilité qui relie les alertes aux propriétaires, et d’un plan de réponse adapté à la portée d’une compromission.

Le niveau expert se reconnaît à la capacité de justifier les compromis, d’anticiper les pannes et de démontrer que les procédures fonctionnent : chaîne valide sur les clients cibles, clés protégées et récupérables selon la politique, renouvellement confirmé sur les endpoints, révocation traitée selon des délais connus, alertes actionnables et migrations testées. La confiance ne se déclare pas ; elle s’administre, se mesure et se rétablit par des preuves.
