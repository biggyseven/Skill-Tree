# La Triade CIA

> **Mise en contexte**
>
> Une plateforme de formation conserve les comptes des apprenants, leurs résultats et les documents de cours. Un étudiant parvient à consulter le dossier d'un autre, une note change sans explication et le portail devient inaccessible pendant une heure. Ces événements illustrent trois objectifs différents : empêcher la divulgation, préserver l'exactitude des données et maintenir l'accès aux services. La triade CIA aide à analyser le problème avant de sélectionner les protections.

## 1. Pourquoi la cybersécurité a besoin d'objectifs

La cybersécurité rassemble les pratiques techniques, organisationnelles et humaines qui protègent les systèmes, les réseaux, les applications et les informations contre les accès, modifications, destructions ou interruptions non autorisés. Elle ne consiste pas seulement à installer un antivirus ni à choisir un mot de passe complexe. Elle vise à maintenir un niveau de confiance acceptable dans les données et les services malgré les erreurs, les pannes et les actions malveillantes.

Une banque doit protéger les transactions, une école doit préserver les résultats, un hôpital doit rendre les dossiers disponibles aux professionnels autorisés et une entreprise doit protéger ses contrats. Ces besoins se recoupent sans être identiques. Pour structurer l'analyse, les professionnels utilisent souvent la triade CIA : confidentialité, intégrité et disponibilité. CIA reprend les termes anglais Confidentiality, Integrity et Availability.

La triade est un modèle de raisonnement, pas une solution technique prête à installer. Elle aide à définir les objectifs auxquels les contrôles doivent répondre. Elle ne promet jamais une sécurité absolue et ne remplace pas une analyse des risques adaptée au métier.

## 2. Confidentialité

La **confidentialité** consiste à empêcher l'accès ou la divulgation d'informations à des personnes, des systèmes ou des processus qui ne sont pas autorisés à les recevoir. Elle ne signifie pas que personne ne doit consulter les données : les utilisateurs légitimes ont besoin d'y accéder. L'enjeu consiste à faire correspondre les permissions aux responsabilités et au besoin réel.

Les données pouvant exiger une protection renforcée comprennent les informations personnelles, les dossiers de santé, les résultats, les contrats, les données financières, les secrets commerciaux, les mots de passe, les clés privées et les jetons de session. Leur niveau de sensibilité dépend du contexte et des conséquences possibles d'une divulgation.

### Exemple

Un enseignant doit consulter les résultats des élèves de ses classes, mais pas automatiquement ceux de tous les établissements ni les informations salariales du personnel. Un visiteur ne doit pas accéder à un dossier privé simplement en changeant un numéro dans une URL. Le serveur doit vérifier l'autorisation pour chaque ressource ; masquer un bouton dans l'interface n'est pas suffisant.

### Menaces contre la confidentialité

Un mot de passe volé peut permettre d'ouvrir une messagerie. Un courriel envoyé au mauvais destinataire peut divulguer un fichier sans intervention d'un pirate. Un stockage en ligne mal configuré peut rendre des documents publics. Un ordinateur perdu peut exposer des fichiers s'ils ne sont pas protégés.

Les permissions trop larges augmentent aussi le risque. Un compte qui peut lire des données inutiles pour sa mission expose davantage d'informations si ce compte est compromis. Le principe du moindre privilège consiste à accorder uniquement les droits nécessaires, pendant la durée nécessaire.

### Mesures de protection

Le contrôle d'accès définit qui peut lire, modifier ou administrer une ressource. Les comptes individuels aident à attribuer les actions. L'authentification multifacteur réduit le risque associé au seul vol d'un mot de passe. Le chiffrement protège les données au repos ou en transit lorsqu'il est correctement configuré. La classification des informations permet d'ajuster les protections à la sensibilité des données.

Aucune de ces mesures ne résout tous les problèmes. Le chiffrement d'un disque ne garantit pas que l'application refusera à un utilisateur connecté l'accès à des dossiers qui ne le concernent pas. La MFA renforce l'authentification mais ne détermine pas les permissions applicatives. Les contrôles doivent être combinés.

## 3. Intégrité

L'**intégrité** vise à préserver l'exactitude, la cohérence et la complétude des informations, ainsi qu'à protéger les systèmes contre les modifications ou destructions non autorisées. Une donnée peut rester confidentielle tout en étant fausse. Une facture réservée à un seul employé peut néanmoins avoir été modifiée incorrectement.

L'intégrité est importante chaque fois qu'une décision repose sur une information. Une banque doit calculer un solde exact ; une école doit conserver les notes réellement obtenues ; un administrateur réseau doit disposer d'une configuration fiable. Une erreur de manipulation, une application défectueuse ou un compte compromis peuvent tous affecter l'intégrité.

### Formes d'altération

Une altération peut être une modification frauduleuse, une suppression accidentelle, l'ajout d'un enregistrement fictif, la corruption d'un support, une erreur de programme ou un changement de configuration non approuvé. Certaines altérations se corrigent facilement ; d'autres demandent une enquête ou une restauration.

Dans une application de notes, limiter les valeurs aux nombres compris entre zéro et vingt empêche certaines entrées mal formées, mais ne prouve pas qu'une note de 19 est légitime. Il faut aussi limiter qui peut la modifier, conserver l'historique utile et documenter les corrections.

### Mesures de protection

Les permissions limitent les personnes capables de modifier les données. Les validations contrôlent la forme et la cohérence des entrées. Les journaux d'audit enregistrent les opérations importantes. La gestion des changements précise qui propose, approuve et réalise une modification. Les sauvegardes permettent de retrouver des versions antérieures si elles sont saines et restaurables.

Une fonction de hachage cryptographique peut aider à détecter une différence entre deux contenus. Pour vérifier un fichier téléchargé, on peut calculer une empreinte SHA-256 et la comparer à une référence obtenue par un canal fiable. Une empreinte seule n'empêche pas l'altération et n'identifie pas automatiquement l'auteur. Si un attaquant peut remplacer le fichier et la référence ensemble, la vérification est insuffisante.

Une signature numérique peut contribuer à vérifier que le contenu correspond à celui qui a été signé avec une clé privée associée. La clé publique et son lien avec l'identité attendue doivent être validés.

## 4. Disponibilité

La **disponibilité** signifie que les utilisateurs et processus autorisés peuvent accéder aux informations et services dans les délais nécessaires. Un système peut conserver des données confidentielles et exactes, mais devenir inutilisable si le serveur est arrêté ou si le réseau est coupé.

Les causes d'indisponibilité comprennent les pannes matérielles, les erreurs logicielles, la saturation des ressources, les coupures électriques, les mauvaises configurations, les pannes DNS, les problèmes de routage et les attaques par déni de service. Un rançongiciel peut également rendre des fichiers inaccessibles.

### Mesures de protection

La redondance permet à un composant de prendre le relais lorsqu'un autre tombe en panne. Elle peut concerner les alimentations, les liens réseau, les serveurs ou les zones d'hébergement. Elle ne garantit pas une continuité parfaite : deux serveurs installés dans le même local peuvent subir le même incident physique.

La supervision mesure l'état des composants, la charge, la mémoire, l'espace disque, les erreurs et le temps de réponse. Les sauvegardes facilitent la récupération, mais ne garantissent pas à elles seules un retour immédiat au service. Il faut tester la restauration et documenter les étapes.

Le RTO, ou objectif de durée de reprise, exprime le délai cible dans lequel un service doit être rétabli. Le RPO, ou objectif de point de reprise, décrit la perte de données temporelle maximale considérée acceptable dans un scénario donné. Ce sont des objectifs à soutenir par des architectures et procédures testées, pas des garanties automatiques.

## 5. Comparaison des trois propriétés

| Propriété | Question | Exemple | Contrôles possibles |
|---|---|---|---|
| Confidentialité | Qui peut voir l'information ? | Un étudiant consulte un dossier privé. | Permissions, MFA, chiffrement, contrôle côté serveur |
| Intégrité | L'information est-elle exacte et protégée ? | Une facture change sans approbation. | Droits d'écriture, validations, journaux, signatures |
| Disponibilité | Le service est-il utilisable quand il le faut ? | Une panne bloque les commandes. | Supervision, redondance, sauvegardes testées, reprise |

Une même attaque peut toucher plusieurs propriétés. Un rançongiciel peut rendre les fichiers inaccessibles et s'accompagner d'un vol préalable de données. Un compte administrateur compromis peut permettre de lire des documents, de modifier des données et d'arrêter un service. Il faut classifier les effets observés plutôt que forcer chaque incident dans une seule catégorie.

## 6. De l'actif au risque

Un **actif** est une donnée, un service ou un système qui a de la valeur. Une **menace** est un événement ou un acteur susceptible de provoquer un incident. Une **vulnérabilité** est une faiblesse exploitable ou capable de déclencher un problème. Le **risque** correspond à la possibilité de conséquences négatives et s'évalue en tenant compte de la vraisemblance, de l'impact, de l'exposition et des contrôles existants.

Exemple : les factures constituent l'actif ; une personne peut tenter de les modifier ; les comptes partagés constituent une faiblesse ; la fraude est une conséquence possible. Les comptes individuels, l'approbation des modifications, les journaux et les sauvegardes réduisent différentes parties du risque.

Il ne faut pas prétendre que le risque est nul après l'installation d'un outil. Les contrôles doivent être entretenus et vérifiés, particulièrement après les changements d'architecture ou de personnel.

## 7. Construire une matrice CIA

Pour chaque actif, demande-toi ce qui se passerait si l'information était divulguée, modifiée ou indisponible. Une base de données clients peut exiger une confidentialité élevée, une intégrité élevée et une disponibilité importante. Pour un document public, la confidentialité peut être faible tandis que l'intégrité reste critique si le document est la référence officielle d'une procédure.

La classification doit être adaptée au métier. Elle peut utiliser des niveaux tels que faible, moyen, élevé et critique, mais leur signification doit être documentée. Une étiquette n'a d'utilité que si elle entraîne des décisions concrètes : accès restreint, chiffrement, durée de conservation, procédure de partage ou objectif de reprise.

Il faut distinguer les besoins métiers des moyens techniques. Dire « le site doit être disponible » reste vague. Préciser les heures critiques, le délai de reprise, la perte de données acceptable et les dépendances essentielles permet de choisir une architecture appropriée.

## 8. Mesures préventives, détectives et correctives

Les mesures **préventives** cherchent à empêcher un incident ou à réduire sa probabilité. Le contrôle d'accès, la MFA, les correctifs et la segmentation en sont des exemples.

Les mesures **détectives** aident à repérer un événement. Les journaux, la supervision, les alertes et certains contrôles d'intégrité contribuent à la détection.

Les mesures **correctives** limitent les conséquences ou permettent de revenir à un état acceptable. La révocation des accès, la correction d'une configuration, la restauration de fichiers et la reprise après sinistre en font partie.

Une stratégie efficace combine ces familles. Même une organisation préparée ne peut pas garantir l'absence de tout incident. Elle peut en revanche réduire les occasions d'attaque, repérer les anomalies et se rétablir plus efficacement.

## 9. TP : vérifier l'intégrité d'un fichier

Dans un répertoire de travail personnel, crée un fichier de test. Sous Windows PowerShell :

~~~powershell
"Bonjour, cybersécurité !" | Set-Content -Path .\cia-demo.txt -Encoding utf8
Get-FileHash .\cia-demo.txt -Algorithm SHA256
~~~

Note l'empreinte, modifie ensuite le texte et recalcule-la :

~~~powershell
"Bonjour, sécurité informatique !" | Set-Content -Path .\cia-demo.txt -Encoding utf8
Get-FileHash .\cia-demo.txt -Algorithm SHA256
~~~

Sous Linux, les commandes équivalentes sont :

~~~bash
printf '%s\n' 'Bonjour, cybersécurité !' > cia-demo.txt
sha256sum cia-demo.txt
printf '%s\n' 'Bonjour, sécurité informatique !' > cia-demo.txt
sha256sum cia-demo.txt
~~~

Les empreintes devraient différer. Cette observation illustre la détection d'un changement de contenu. Elle ne garantit ni la confidentialité, ni l'identité de l'auteur, ni la fiabilité d'une référence. Pour une vérification utile, la valeur de référence doit provenir d'un canal fiable.

Supprime le fichier uniquement après avoir vérifié qu'il s'agit du fichier créé pour l'exercice. Ne lance pas une commande de suppression sur un document important.

## 10. TP : analyser un incident fictif

Une école observe trois événements : un étudiant consulte le dossier d'un autre, une note change sans approbation, puis le portail devient indisponible. Le but est de formuler des hypothèses sans les confondre avec des faits établis.

Note les faits confirmés, les heures, les comptes et les systèmes concernés. Rattache chaque conséquence à une ou plusieurs propriétés CIA. Examine les journaux et les autorisations disponibles. Préserve les éléments utiles et signale l'incident selon la procédure prévue.

Pour la confidentialité, vérifie les contrôles côté serveur et les ressources consultées. Pour l'intégrité, examine l'historique des modifications et les sauvegardes. Pour la disponibilité, étudie les journaux applicatifs, la connectivité, la charge et les dépendances du portail. Les événements peuvent être liés, mais l'enquête doit le démontrer.

## 11. Compromis et erreurs fréquentes

La sécurité n'est pas uniquement une question de restriction. Un système auquel aucun utilisateur légitime ne peut accéder ne remplit pas son objectif. À l'inverse, un système où tout le monde peut tout lire et tout modifier est trop permissif. Il faut définir les accès nécessaires et vérifier que les contrôles ne bloquent pas inutilement l'activité.

Une sauvegarde ne garantit pas une disponibilité immédiate : il faut restaurer, vérifier et redémarrer les dépendances. Le chiffrement ne remplace pas l'autorisation applicative. Un antivirus ne garantit pas l'intégrité de toutes les données. Une empreinte ne prouve pas l'identité de l'auteur. Un certificat valide pour un domaine ne prouve pas que tous les contenus du site sont honnêtes.

La méthode professionnelle consiste à identifier l'actif, décrire la menace, évaluer les conséquences, choisir une mesure, tester son fonctionnement et documenter les limites restantes.

## 12. Exercices corrigés

**Exercice 1.** Un employé envoie un dossier médical à une personne non autorisée. Quelle propriété est principalement compromise ?

**Correction :** la confidentialité, car les informations ont été divulguées. Les autres propriétés ne sont concernées que si une conséquence supplémentaire est observée.

**Exercice 2.** Une facture est modifiée sans approbation. Quelle propriété est visée ?

**Correction :** l'intégrité. Il faut examiner les permissions, l'historique des modifications et les procédures d'approbation.

**Exercice 3.** Un serveur Web ne répond plus après une panne électrique.

**Correction :** la disponibilité est directement touchée. Il faut identifier les dépendances, rétablir le service et évaluer l'alimentation de secours si la criticité le justifie.

**Exercice 4.** Un fichier a la même empreinte SHA-256 que la valeur de référence reçue d'une source fiable. Que peut-on conclure ?

**Correction :** les contenus correspondent avec une très forte confiance dans l'usage attendu. Cette comparaison ne garantit pas à elle seule l'identité de l'auteur, sauf si la référence et son origine sont fiables.

**Exercice 5.** Une application impose la MFA mais autorise chaque utilisateur à lire tous les dossiers.

**Correction :** l'authentification est renforcée, mais l'autorisation est trop permissive. La MFA ne remplace pas le contrôle d'accès aux ressources.

**Exercice 6.** L'entreprise sauvegarde sa base chaque nuit mais ne teste jamais la restauration.

**Correction :** sa capacité réelle de récupération reste inconnue. Il faut effectuer un test documenté et mesurer le délai de restauration.

## 13. Défi final : sécuriser KivuTech Services

KivuTech exploite une boutique en ligne, conserve les données des clients, facture ses commandes et doit rester accessible pendant les heures d'activité. Les employés partagent parfois un compte de fichiers, les factures peuvent être modifiées sans historique fiable, les sauvegardes restent connectées au serveur et le site connaît des interruptions.

Le rapport doit identifier les actifs, associer chaque problème aux propriétés CIA, prioriser les actions, proposer des contrôles et définir comment les vérifier.

**Correction attendue.** Les données clients demandent des protections de confidentialité et d'intégrité. Des comptes individuels et des permissions adaptées réduisent les accès excessifs. Les factures exigent des contrôles de modification et une journalisation protégée. Les sauvegardes doivent être protégées contre la suppression et leur restauration doit être testée. Les interruptions du site doivent être analysées au moyen des métriques, des journaux applicatifs et de l'état des dépendances. Des objectifs RTO et RPO doivent être définis avec le métier.

Le rapport doit distinguer les faits des hypothèses, attribuer un responsable à chaque action et inclure une validation après chaque changement. Il ne suffit pas d'installer un outil : il faut montrer que le contrôle protège réellement l'actif et ne rend pas le service inutilisable.

## 14. Glossaire et ressources

**Actif :** donnée, système ou service ayant de la valeur.  
**Confidentialité :** prévention des accès et divulgations non autorisés.  
**Intégrité :** protection de l'exactitude et de l'état autorisé des données.  
**Disponibilité :** capacité à accéder à une ressource au moment requis.  
**Menace :** circonstance susceptible de provoquer un incident.  
**Vulnérabilité :** faiblesse exploitable ou susceptible de déclencher un incident.  
**Risque :** possibilité de conséquences négatives.  
**MFA :** authentification multifacteur.  
**RTO :** objectif de durée de reprise.  
**RPO :** objectif de point de reprise.  
**Journal d'audit :** trace structurée des actions et événements importants.

Ressources : NIST Computer Security Resource Center, https://csrc.nist.gov/ ; NIST Cybersecurity Framework, https://www.nist.gov/cyberframework ; OWASP Cheat Sheet Series, https://cheatsheetseries.owasp.org/ ; ANSSI, https://cyber.gouv.fr/

## 15. Études de cas approfondies

### Cas 1 — Dossier médical envoyé au mauvais destinataire

**Situation.** Une secrétaire joint un dossier de patient au courriel envoyé à un autre patient.

**Analyse CIA.** La confidentialité est touchée. Il faut établir le contenu partagé, le destinataire, la période d'exposition et les accès ultérieurs possibles. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Contacter le responsable compétent, documenter les faits, réduire la diffusion et appliquer la procédure de signalement de l'organisation. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Vérifier les journaux d'envoi et tester une étape de validation du destinataire sans utiliser de vraies données sensibles. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Les erreurs humaines peuvent compromettre la sécurité sans qu'un pirate intervienne. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 2 — Facture modifiée après validation

**Situation.** Une facture approuvée porte un montant différent lors du paiement et personne ne sait qui l'a changé.

**Analyse CIA.** L'intégrité est directement en jeu et l'absence de traces complique l'analyse. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Limiter les droits de modification, conserver l'historique, exiger une justification pour les changements sensibles et séparer les rôles. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Effectuer une modification contrôlée dans un environnement de test et vérifier l'enregistrement de l'auteur, de la date et de la valeur. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Une entrée valide au format n'est pas nécessairement légitime. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 3 — Panne de base pendant les inscriptions

**Situation.** Le portail ne peut plus enregistrer de nouvelles inscriptions alors que le serveur Web semble fonctionner.

**Analyse CIA.** La disponibilité du service métier est compromise, même si un composant répond encore. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Examiner la base, les journaux, la connectivité et les ressources avant d'engager une reprise coordonnée. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Tester une transaction témoin et suivre le taux d'erreur après rétablissement. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** La disponibilité doit être évaluée du point de vue de l'utilisateur. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 4 — Ordinateur portable perdu

**Situation.** Un appareil contient des documents d'entreprise et des sessions qui peuvent être encore actives.

**Analyse CIA.** La confidentialité dépend du chiffrement et de la protection de session ; des données locales uniques peuvent aussi être indisponibles. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Déclarer la perte, révoquer les sessions pertinentes, vérifier la gestion de l'appareil et déterminer quelles données étaient présentes. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Confirmer la révocation des sessions et vérifier les connexions postérieures à la perte. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** La préparation avant l'incident vaut mieux que l'improvisation après. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 5 — Sauvegarde restaurée mais incohérente

**Situation.** Une restauration réussit techniquement mais les commandes ne correspondent plus aux factures.

**Analyse CIA.** L'intégrité et la disponibilité sont concernées, car les données restaurées ne permettent pas de reprendre correctement l'activité. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Restaurer un point cohérent, valider les dépendances entre tables et documenter l'ordre de reprise. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Comparer des transactions de référence et effectuer des contrôles métier avant le retour en production. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Une copie restaurée doit être vérifiée, pas seulement ouverte. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 6 — Permissions trop larges dans un espace partagé

**Situation.** Tous les employés peuvent voir des contrats et des documents de ressources humaines.

**Analyse CIA.** La confidentialité est menacée par des autorisations non proportionnées au rôle. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Classer les informations, limiter les groupes d'accès et supprimer les droits qui ne sont plus nécessaires. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Tester les accès avec plusieurs comptes de rôles distincts et documenter les résultats. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Le moindre privilège s'applique aux documents autant qu'aux comptes techniques. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 7 — Changement réseau non approuvé

**Situation.** Une règle de filtrage est ajoutée pendant une intervention et le service devient inaccessible.

**Analyse CIA.** La disponibilité est touchée et l'intégrité de la configuration peut être compromise. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Revenir à la configuration validée selon la procédure, examiner le changement et prévoir validation et retour arrière. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Comparer l'état avant/après et tester les flux métier autorisés. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** La gestion des changements est un contrôle de sécurité. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 8 — Compte administrateur partagé

**Situation.** Plusieurs techniciens utilisent le même identifiant et une suppression non prévue est constatée.

**Analyse CIA.** La confidentialité et l'intégrité peuvent être touchées, mais l'attribution de l'action devient difficile. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Créer des identités individuelles, réduire les privilèges et protéger les opérations administratives. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Vérifier qu'une action de test apparaît dans le journal avec une identité unique. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Des comptes individuels améliorent la traçabilité. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 9 — Site surchargé durant une campagne

**Situation.** Une campagne commerciale attire plusieurs fois le trafic habituel et les pages répondent lentement.

**Analyse CIA.** La disponibilité diminue, mais le trafic élevé ne prouve pas une attaque. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Analyser les métriques, distinguer demandes légitimes et trafic anormal, puis adapter capacité, cache ou répartition de charge. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Réaliser un test de charge autorisé dans un environnement adapté et comparer les temps de réponse. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Il faut diagnostiquer avant d'attribuer une cause malveillante. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 10 — Journaux d'audit modifiables

**Situation.** Un administrateur peut supprimer les traces de ses propres opérations.

**Analyse CIA.** L'intégrité des traces et la capacité de reconstituer un incident sont affaiblies. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Limiter les permissions sur les journaux et centraliser les événements essentiels dans un espace protégé. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Effectuer un test et vérifier que les traces demeurent consultables par le rôle d'audit. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Les journaux sont eux-mêmes des actifs à protéger. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 11 — Clé de chiffrement oubliée

**Situation.** Une équipe chiffre des archives mais la seule copie de la clé est conservée sur le poste d'un ancien collaborateur.

**Analyse CIA.** La disponibilité des données devient incertaine même si le chiffrement était correctement appliqué. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Inventorier les clés, définir une récupération contrôlée et attribuer des responsabilités de garde. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Tester une restauration à partir d'une copie de secours autorisée et vérifier les traces d'accès. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** La gestion des clés doit équilibrer confidentialité et récupération. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

### Cas 12 — Modification d'un résultat par API

**Situation.** Un utilisateur construit une requête qui tente de modifier la note d'un autre étudiant.

**Analyse CIA.** L'intégrité est compromise si le serveur ne vérifie pas l'autorisation sur la ressource. Il faut distinguer les faits des hypothèses, identifier les actifs concernés et noter les informations qui restent à confirmer. Les journaux et les témoignages doivent être examinés selon la procédure prévue, sans diffuser inutilement des informations sensibles.

**Mesures.** Corriger le contrôle côté serveur et ajouter des tests d'autorisation pour chaque rôle. Les mesures doivent être proportionnées aux conséquences possibles, attribuées à un responsable et réalisées avec une attention aux effets sur les utilisateurs légitimes. Pour un changement en production, il faut planifier la validation et prévoir une manière maîtrisée de revenir à un état stable.

**Vérification.** Vérifier que les requêtes d'un compte non autorisé sont refusées même si l'interface est contournée. Le résultat doit être consigné : contrôle effectué, résultat obtenu, écarts restants et prochaine action. Un contrôle n'est pas réputé efficace uniquement parce qu'une configuration a été modifiée ; il faut vérifier le comportement réel.

**À retenir.** Masquer un bouton ne remplace pas un contrôle côté serveur. Ce cas illustre le passage d'un événement à une action contrôlable, tout en reconnaissant les limites des preuves disponibles.

