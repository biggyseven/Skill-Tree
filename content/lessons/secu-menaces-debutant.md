# Panorama des menaces

> **Mise en contexte**
>
> Une entreprise possède une plateforme de formation, des comptes de messagerie, un serveur de fichiers et une application qui conserve des informations sur les apprenants. Une employée reçoit un courriel pressant qui lui demande de confirmer son mot de passe. Plus tard, un compte est utilisé pour télécharger des documents, des fichiers deviennent inaccessibles et le service ralentit. Il faut découvrir ce qui s'est passé sans confondre les faits avec les suppositions.
>
> Ce cours présente les familles de menaces, les signes qui peuvent signaler un incident et les premières mesures de prévention, détection et réponse. Il prolonge la Triade CIA : une menace doit être analysée selon les données et les services qu'elle peut affecter.

## 1. Menace, vulnérabilité, attaque et risque

Une **menace** est une situation, une action ou un événement susceptible de nuire à un système ou à une organisation. Elle peut provenir d'un acteur malveillant, d'une erreur humaine, d'une panne ou d'un événement physique.

Une **vulnérabilité** est une faiblesse qui peut être exploitée ou déclencher un incident : logiciel non corrigé, permission excessive, configuration incorrecte, procédure de récupération insuffisante ou mauvaise pratique récurrente.

Une **attaque** est une action entreprise pour compromettre un système ou un objectif. Un **incident** est un événement qui a compromis ou menace réellement les systèmes et nécessite une évaluation ou une réponse. Le **risque** correspond à la possibilité de conséquences négatives ; son appréciation prend en compte la vraisemblance, l'impact, l'exposition et les contrôles existants.

Exemple : la menace est qu'une personne tente de voler des identifiants. La vulnérabilité est que le compte utilise un mot de passe réutilisé et ne possède pas de protection adaptée. L'attaque réussit si une personne non autorisée accède effectivement au compte. La conséquence peut être une fuite de données ou une fraude.

Il faut distinguer ce qui est observé de ce qui est possible. Une alerte peut correspondre à une tentative bloquée, et une connexion inhabituelle peut être légitime. La bonne réaction consiste à vérifier les faits sans minimiser les signaux inquiétants ni déclarer une attaque sans preuve suffisante.

## 2. Les acteurs et leurs motivations

Les **cybercriminels** recherchent souvent un avantage financier : vol de données, fraude, extorsion, revente d'identifiants ou utilisation de ressources compromises. Certains se spécialisent dans un seul maillon d'une opération, par exemple la collecte de comptes ou l'hébergement d'infrastructures.

Les **acteurs motivés par le renseignement** peuvent chercher des informations stratégiques, économiques, politiques ou techniques. Leurs opérations peuvent être longues et discrètes. Toutefois, il serait imprudent d'attribuer une intrusion à une organisation précise sans éléments techniques et contextuels suffisants.

Les **acteurs idéologiques** peuvent chercher à diffuser un message ou perturber une activité. Les **personnes internes** peuvent agir volontairement ou commettre une erreur ; leur accès légitime peut rendre certains incidents plus difficiles à détecter.

Les **événements accidentels** occupent aussi une place importante : panne électrique, erreur de manipulation, défaut logiciel, mauvaise configuration ou incident environnemental. La sécurité doit couvrir ces scénarios même lorsqu'il n'existe aucune intention malveillante.

La motivation ne suffit pas à déduire la capacité d'un acteur. Pour planifier les protections, il faut examiner les actifs exposés, les voies d'accès, les faiblesses et les conséquences possibles.

## 3. Ingénierie sociale et hameçonnage

L'**ingénierie sociale** exploite la confiance, l'urgence, la peur, la curiosité ou le désir d'aider afin d'obtenir une information, un accès ou une action. Une personne peut être amenée à transmettre un secret, ouvrir un fichier dangereux, réaliser un paiement ou approuver une connexion.

L'**hameçonnage**, ou phishing, est une forme de manipulation qui pousse la victime à révéler une information ou à effectuer une action risquée. Un message peut imiter une banque, un service de livraison, une plateforme de formation ou un responsable interne.

Les signaux suspects peuvent comprendre une demande inattendue de mot de passe, une menace de désactivation immédiate, un lien qui ne correspond pas au domaine officiel, une pièce jointe surprenante ou une demande de paiement qui contourne les procédures. Un signal isolé ne prouve pas toujours une fraude : c'est le contexte complet qui doit être examiné.

Le hameçonnage ciblé personnalise le message avec le nom d'un collègue, un projet réel ou le vocabulaire de l'entreprise. La fraude au dirigeant ou au fournisseur peut demander un virement urgent ou un changement de coordonnées bancaires.

La règle de base est de vérifier les opérations sensibles par un canal indépendant déjà connu. Il ne faut pas communiquer un mot de passe en réponse à un message. Les organisations doivent aussi fournir un moyen simple de signaler un courriel suspect et encourager les employés à rapporter rapidement une erreur.

## 4. Les logiciels malveillants

Un **logiciel malveillant**, ou malware, est un programme destiné à réaliser une action nuisible ou non autorisée. Les familles se distinguent par leur comportement et leur mode de propagation.

Un **virus** peut s'attacher à un fichier ou à un composant exécutable. Un **ver** peut se propager entre plusieurs systèmes. Un **cheval de Troie** semble légitime mais dissimule une fonction malveillante. Un **logiciel espion** cherche à collecter des informations. Un **enregistreur de frappe** peut recueillir des frappes au clavier et exposer des secrets.

Un **rançongiciel** rend des fichiers ou des systèmes inaccessibles, souvent pour demander une rançon. Certaines opérations associent le chiffrement des fichiers au vol préalable de données et à la menace de divulgation. Le paiement ne garantit ni la récupération ni la suppression des copies détenues par l'attaquant.

Les protections comprennent l'installation de logiciels depuis des sources de confiance, les mises à jour, la limitation des privilèges, la protection des postes, la segmentation, la supervision et les sauvegardes testées. Ces mesures sont complémentaires : aucun antivirus ne peut garantir qu'aucun logiciel malveillant ne réussira jamais à agir.

Un ralentissement ou un processus inconnu ne prouve pas à lui seul une infection. Il faut examiner les alertes, les journaux et le contexte. Dans un environnement professionnel, évite de supprimer des fichiers ou de terminer des processus au hasard ; suis les procédures prévues.

## 5. Vol d'identifiants et compromission de comptes

Les identifiants peuvent être volés par hameçonnage, logiciel malveillant, fuite de données ou manipulation. Un compte compromis peut permettre de lire des messages, récupérer des fichiers, modifier des données, envoyer de nouveaux messages frauduleux ou réinitialiser d'autres comptes.

La réutilisation du même mot de passe augmente le risque : la compromission d'un service peut faciliter l'accès à d'autres services. Des attaques automatisées peuvent tester des identifiants déjà divulgués. La force brute essaie de nombreuses valeurs, tandis que les attaques par dictionnaire se concentrent sur des mots de passe probables.

Les défenses comprennent des mots de passe uniques, un gestionnaire de mots de passe, la MFA pour les comptes importants, la limitation des tentatives, les alertes sur les connexions inhabituelles et une gestion rigoureuse des privilèges. Les mécanismes de récupération du compte doivent eux-mêmes être protégés.

Après une compromission, changer le mot de passe peut ne pas suffire si des sessions restent actives ou si une règle de transfert malveillante a été ajoutée à la messagerie. Il faut examiner les actions, révoquer les sessions si nécessaire, vérifier les options de récupération et déterminer si d'autres comptes sont concernés.

## 6. Vulnérabilités et erreurs de configuration

Une vulnérabilité est une faiblesse d'un système ou d'une procédure. Elle peut se trouver dans un système d'exploitation, une bibliothèque, une application, un protocole, une configuration ou une organisation.

Les logiciels non corrigés peuvent rester exposés à des failles connues. La gestion des correctifs demande un inventaire, une évaluation de la gravité et de l'exposition, une planification des mises à jour et une vérification après correction.

Les erreurs de configuration comprennent des services inutiles exposés, des permissions excessives, un stockage rendu public, des comptes par défaut mal protégés ou des secrets inclus dans le code. Une application Web qui ne vérifie pas les autorisations côté serveur peut divulguer des données même si son interface cache certains liens.

La gestion des vulnérabilités ne consiste pas à exécuter un scanner et à fermer les alertes. Il faut hiérarchiser les résultats selon la criticité des actifs, l'exposition, l'exploitabilité et les conséquences métier. Une correction doit aussi être testée afin d'éviter une interruption imprévue.

## 7. Menaces réseau

Les réseaux sont ciblés parce qu'ils donnent accès aux services, transportent des données et connectent les systèmes internes. Des services mal configurés ou inutilement exposés augmentent la surface d'attaque.

L'interception consiste à observer des échanges sans autorisation. Le chiffrement des communications réduit certains risques, mais certaines métadonnées peuvent rester visibles. Les attaques de l'intermédiaire cherchent à observer ou modifier une communication ; la validation des certificats et l'usage correct de TLS sont importants.

L'usurpation consiste à présenter une identité ou une information qui ne correspond pas à son origine réelle. Les journaux doivent être interprétés en corrélant plusieurs éléments, car une adresse ou un nom affiché ne prouve pas toujours l'origine d'une action.

Une attaque par déni de service cherche à empêcher les utilisateurs légitimes d'accéder à un service en saturant ou en perturbant ses ressources. Les protections peuvent inclure la limitation de débit, le filtrage et la répartition de charge. Il faut distinguer un trafic malveillant d'un pic d'activité légitime à partir des métriques et du comportement observé.

Un Wi-Fi mal sécurisé peut faciliter un accès non autorisé. La segmentation permet de séparer les appareils et services selon leurs besoins, par exemple les postes administratifs, les visiteurs et les serveurs. Elle limite les communications inutiles sans remplacer la sécurité des postes.

## 8. Menaces Web, Cloud et chaîne d'approvisionnement

Les applications Web traitent des entrées, gèrent des sessions et appliquent des règles métier. Une validation incorrecte ou un contrôle d'accès insuffisant peut permettre une action non autorisée. Les vérifications d'autorisation doivent être appliquées côté serveur.

Les secrets applicatifs, comme les clés d'API et les mots de passe de base de données, ne doivent pas être publiés dans un dépôt de code ou un journal accessible. Un secret divulgué doit être considéré comme compromis jusqu'à vérification ; il faut le révoquer ou le remplacer selon sa fonction.

Dans le Cloud, une permission incorrecte peut rendre des données publiques et un compte compromis peut permettre de créer ou supprimer des ressources. Les responsabilités sont partagées selon le modèle de service ; il faut connaître les contrôles qui incombent au fournisseur et au client.

Les logiciels dépendent de bibliothèques, paquets et prestataires. Un composant vulnérable ou compromis peut affecter plusieurs applications. L'organisation doit connaître ses dépendances, suivre les avis de sécurité, limiter les accès des prestataires et révoquer les permissions qui ne sont plus nécessaires.

## 9. Menaces physiques et internes

Le vol d'un ordinateur, la perte d'une clé USB, un incendie, une inondation ou une coupure électrique peuvent affecter les systèmes. Le chiffrement des supports, le contrôle physique, l'alimentation de secours et les copies conservées dans un lieu approprié limitent certaines conséquences.

Les risques internes comprennent l'envoi d'un mauvais fichier, la suppression accidentelle, une configuration incorrecte ou l'utilisation d'un compte partagé. Ils ne signifient pas que tous les employés sont malveillants : ils rappellent qu'un système sûr doit mieux tolérer les erreurs.

Les comptes oubliés peuvent rester actifs après un départ ou un changement de fonction. Il faut gérer leur cycle de vie : création, attribution des droits, revue périodique et révocation lorsque le besoin prend fin.

Une culture de signalement est essentielle. Si une personne clique sur un lien suspect ou envoie un document au mauvais destinataire, elle doit savoir à qui le déclarer. Une réaction rapide peut limiter l'étendue de l'incident.

## 10. Détection et réponse

Les signes possibles d'incident comprennent des échecs de connexion répétés, une connexion inhabituelle, la création d'un compte inattendu, un téléchargement massif, une protection désactivée ou des modifications inexpliquées. Aucun signal isolé ne prouve automatiquement une compromission.

Les journaux enregistrent les connexions, actions et erreurs. Ils doivent être protégés contre les modifications, conservés selon une politique définie et utiliser des horodatages suffisamment cohérents. La corrélation de plusieurs sources permet de mieux reconstruire une séquence.

Lorsqu'un événement est suspect, note les faits, l'heure, le système, le compte et les messages d'erreur. Ne mets jamais des mots de passe ou des jetons dans un rapport ordinaire. Suis la procédure de l'organisation et évite les manipulations improvisées.

Selon le cas, l'équipe peut devoir révoquer des sessions, remplacer des secrets, limiter l'accès à un appareil, préserver les journaux ou restaurer des fichiers. Après le confinement, il faut comprendre la cause, corriger les faiblesses et vérifier les systèmes avant le retour à un fonctionnement normal.

## 11. Construire une défense en couches

Une démarche de défense commence par l'inventaire des actifs et services. Il faut connaître les données sensibles, les systèmes exposés et les comptes privilégiés.

La prévention comprend les mises à jour, les permissions adaptées, la MFA, la segmentation et la protection des secrets. La détection comprend les journaux, les alertes et la supervision. La réponse et la récupération s'appuient sur une procédure d'incident et des sauvegardes dont la restauration a été testée.

Les contrôles doivent être vérifiés. Les autorisations peuvent être testées avec des comptes différents. La restauration doit être réalisée dans un environnement adapté. Les procédures d'incident peuvent être exercées sans utiliser de vrais secrets ni compromettre les données de production.

## 12. TP : examiner un message suspect

Considère ce message fictif. Le domaine .invalid est utilisé à titre d'exemple :

~~~text
Objet : URGENT — Votre compte sera supprimé dans 15 minutes

Votre compte présente un problème. Confirmez vos identifiants via
https://compte-verification.invalid/exemple pour éviter la suspension.
Service informatique
~~~

Repère l'urgence, la demande d'identifiants, l'absence de contexte et le domaine inattendu. Ne clique pas sur le lien. Vérifie la demande via un canal officiel déjà connu et signale le message selon la procédure.

Si tu as déjà saisi ton mot de passe, signale rapidement l'événement. L'équipe responsable pourra révoquer les sessions, remplacer le secret et examiner les connexions. Ne suppose pas qu'un simple changement de mot de passe suffit si des sessions ou paramètres malveillants peuvent persister.

## 13. TP : observer son propre poste

Sous Windows PowerShell, tu peux observer les processus :

~~~powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 ProcessName, Id, CPU
~~~

Tu peux afficher des connexions TCP visibles :

~~~powershell
Get-NetTCPConnection -ErrorAction SilentlyContinue |
    Select-Object -First 20 LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess
~~~

Sous Linux :

~~~bash
ps aux --sort=-%cpu | head -n 11
ss -tupn
~~~

Ces commandes affichent des informations sur la machine que tu contrôles ; elles ne prouvent pas qu'un processus est malveillant. Un processus inconnu peut être légitime. Consulte la documentation, les alertes et le contexte. Ne lance pas de scan d'un réseau tiers sans autorisation.

## 14. Étude de cas : Horizon Services

Une employée saisit son mot de passe sur une page frauduleuse. Le lendemain, des messages inhabituels sont envoyés depuis son compte et certains fichiers ont disparu.

Les faits connus sont la saisie des identifiants, l'envoi de messages et l'absence de certains fichiers. Les hypothèses comprennent le vol d'identifiants, un accès non autorisé, le téléchargement de documents ou une suppression. Les journaux doivent aider à déterminer l'étendue de l'événement.

La confidentialité peut être compromise si le compte a permis de lire des messages. L'intégrité est touchée si des fichiers ont été supprimés ou modifiés. La disponibilité peut être affectée si les employés ne peuvent plus travailler avec les documents.

La réponse initiale comprend le signalement, la révocation contrôlée des sessions, la vérification des règles de messagerie, l'analyse des journaux et la restauration depuis une source fiable si nécessaire. Les actions à long terme comprennent le renforcement de l'authentification, la limitation des permissions, une meilleure supervision et la sensibilisation des utilisateurs.

## 15. Exercices corrigés

**Exercice 1.** Un compte possède des droits inutiles : menace, vulnérabilité ou conséquence ?

**Correction :** faiblesse ou vulnérabilité de configuration. Elle peut augmenter les conséquences d'une erreur ou d'une compromission.

**Exercice 2.** Un message réclame un mot de passe sous pression. Quelle action est adaptée ?

**Correction :** ne pas transmettre le secret, vérifier par un canal officiel et signaler le message.

**Exercice 3.** Des fichiers sont chiffrés et une rançon est demandée. Quelles propriétés sont concernées ?

**Correction :** la disponibilité est directement touchée ; intégrité et confidentialité doivent être évaluées selon les autres actions réalisées.

**Exercice 4.** Un logiciel est obsolète mais fonctionne. Peut-on ignorer le risque ?

**Correction :** non. Il faut inventorier la version, évaluer les vulnérabilités et planifier une correction vérifiée.

**Exercice 5.** Une panne survient après une modification réseau. Faut-il conclure à une attaque ?

**Correction :** non. Examiner la configuration, les journaux, le routage et les dépendances avant de conclure.

**Exercice 6.** Une connexion vient d'un lieu inhabituel. Est-ce une preuve de compromission ?

**Correction :** non. C'est un signal qui doit être corrélé à d'autres événements et au contexte.

## 16. Défi final : protéger NovaLearn

NovaLearn possède une plateforme, une base d'apprenants, un serveur de fichiers et une messagerie. Les employés réutilisent certains mots de passe, le site utilise un logiciel ancien, des documents sont partagés par des liens non revus et la restauration des sauvegardes n'a pas été testée.

Le plan doit inventorier les actifs, définir les menaces et les vulnérabilités, associer les propriétés CIA, prioriser les mesures, prévoir la détection et définir les premières actions d'incident.

**Correction indicative.** Protéger les comptes avec des secrets uniques et une MFA adaptée ; évaluer et corriger les logiciels vulnérables ; revoir les permissions des documents ; tester les restaurations ; simplifier le signalement des messages suspects ; définir une procédure de réponse aux comptes compromis. Les résultats doivent être vérifiés avec des tests de rôles, des contrôles de versions, des restaurations réelles et des exercices de réponse.

Le plan doit distinguer les faits des hypothèses, attribuer un responsable à chaque action et documenter les risques qui subsistent.

## 17. Glossaire et ressources

**Attaque :** action visant à compromettre un système ou un objectif de sécurité.  
**Hameçonnage :** manipulation visant à faire révéler une information ou à provoquer une action risquée.  
**Ingénierie sociale :** techniques exploitant le comportement humain pour obtenir une information, un accès ou une action.  
**Logiciel malveillant :** programme réalisant des actions nuisibles ou non autorisées.  
**Rançongiciel :** opération qui cherche à bloquer l'accès à des données ou systèmes.  
**Menace :** circonstance susceptible de provoquer un incident.  
**Vulnérabilité :** faiblesse exploitable ou susceptible de déclencher un incident.  
**Risque :** possibilité de conséquences négatives.  
**Surface d'attaque :** ensemble des points par lesquels un système peut être atteint.  
**Journalisation :** enregistrement d'événements utiles à la détection et à l'analyse.  
**Segmentation :** division d'un réseau en zones dont les communications sont contrôlées.

Ressources : NIST Cybersecurity Framework, https://www.nist.gov/cyberframework ; NIST Glossary, https://csrc.nist.gov/glossary ; OWASP Cheat Sheet Series, https://cheatsheetseries.owasp.org/ ; ANSSI, https://cyber.gouv.fr/

## 18. Dossiers pratiques d'analyse

### Cas 1 — Campagne de faux messages RH

**Situation.** Des employés reçoivent un message affirmant que leur paie sera suspendue sans confirmation immédiate des identifiants.

**Analyse.** L'urgence et la demande de secret signalent un risque d'ingénierie sociale, mais la compromission n'est pas confirmée tant qu'aucun accès non autorisé n'est établi. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Ne pas ouvrir le lien, vérifier la demande auprès des ressources humaines via un canal connu et signaler le message au point de contact sécurité. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Corréler les messages reçus, les clics signalés et les événements d'authentification sans jamais partager les mots de passe dans le rapport. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** Une procédure de signalement rapide peut limiter la propagation. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 2 — Réutilisation d'un mot de passe après une fuite externe

**Situation.** Un utilisateur emploie le même mot de passe sur un forum et sa messagerie professionnelle. Le forum annonce une fuite.

**Analyse.** La réutilisation peut permettre des tentatives automatisées sur d'autres services, surtout si la messagerie permet de réinitialiser d'autres comptes. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Changer le secret depuis un appareil de confiance, activer la MFA si disponible et examiner les sessions et moyens de récupération. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier les connexions récentes et confirmer la révocation des anciennes sessions lorsque nécessaire. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** La singularité des mots de passe limite l'effet domino d'une fuite. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 3 — Rançongiciel sur un poste partagé

**Situation.** Des fichiers deviennent inaccessibles après l'ouverture d'une pièce jointe inattendue sur un poste utilisé par plusieurs employés.

**Analyse.** La disponibilité des fichiers est directement affectée ; l'intégrité et la confidentialité doivent être examinées selon le périmètre de l'incident. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Suivre la procédure, limiter la connectivité du poste selon les consignes, prévenir l'équipe responsable et préserver les éléments utiles. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier les journaux, les appareils potentiellement affectés et la possibilité d'une restauration depuis une copie saine après confinement. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** Il faut contenir l'incident avant d'engager une restauration précipitée. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 4 — Serveur public non corrigé

**Situation.** Un service accessible depuis Internet utilise une version contenant une vulnérabilité connue.

**Analyse.** La faiblesse offre une voie possible d'exploitation, mais il faut confirmer l'exposition réelle et la portée du système. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Inventorier la version, consulter les avis de sécurité, prioriser un correctif ou une mesure compensatoire et planifier une correction validée. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier la version après correction et rechercher des indices d'exploitation dans les journaux disponibles. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** La gestion des vulnérabilités continue après le déploiement du correctif. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 5 — Stockage Cloud rendu public

**Situation.** Un espace qui devait rester interne est accessible à toute personne possédant le lien.

**Analyse.** C'est un risque de confidentialité même si aucun téléchargement n'est encore confirmé. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Restreindre l'accès, révoquer le lien, examiner la durée d'exposition et revoir les règles de partage similaires. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Tester l'accès depuis un compte non autorisé et consulter les journaux de lecture disponibles. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** Les mauvaises configurations peuvent être aussi importantes que les failles logicielles. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 6 — Déni de service ou pic légitime

**Situation.** Une boutique devient lente durant une campagne et reçoit plusieurs fois son trafic habituel.

**Analyse.** La disponibilité souffre, mais le volume élevé ne prouve pas une attaque. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Comparer le profil des requêtes, les ressources et les sources ; appliquer les mécanismes adaptés sans bloquer les clients légitimes. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Mesurer les temps de réponse et le taux d'erreur avant et après l'ajustement. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** La distinction entre surcharge et attaque exige des mesures. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 7 — Compte de prestataire toujours actif

**Situation.** Un contrat de maintenance se termine, mais le compte distant du fournisseur reste valide.

**Analyse.** Un accès inutile augmente l'exposition et peut être utilisé même si le prestataire n'a plus de mission. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Confirmer la fin de mission, révoquer les accès non nécessaires et examiner les secrets ou clés partagés. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Comparer l'inventaire des prestataires aux comptes actifs et examiner les connexions depuis la fin du contrat. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** La révocation fait partie du cycle de vie des identités. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 8 — Programme téléchargé depuis une source inconnue

**Situation.** Un employé installe un utilitaire trouvé dans une publicité sans vérifier son origine.

**Analyse.** Le fichier peut être légitime, indésirable ou malveillant ; son nom et son icône ne suffisent pas à établir la confiance. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Éviter les installations non autorisées, utiliser les sources approuvées et signaler l'incident si l'installation a eu lieu. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier les alertes, l'origine du logiciel et les changements récents sans supprimer arbitrairement des preuves. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** La provenance compte autant que la présentation du programme. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 9 — Clé USB trouvée

**Situation.** Une clé USB découverte dans un couloir est branchée à un poste pour découvrir son propriétaire.

**Analyse.** Le support peut contenir des fichiers inconnus ou un mécanisme malveillant ; la curiosité a créé une exposition possible. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Ne pas brancher un support inconnu à un poste ordinaire ; suivre la procédure de remise et d'analyse isolée. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier que les consignes sur les supports amovibles sont connues de l'équipe. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** Un support inconnu ne doit pas être testé sur un poste de travail. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

### Cas 10 — Accès Web non autorisé

**Situation.** Un apprenant change un identifiant dans une URL et accède au dossier d'un autre utilisateur.

**Analyse.** La faiblesse probable est un contrôle d'accès insuffisant côté serveur. Commence par distinguer les faits des hypothèses et identifie les actifs, comptes et systèmes concernés. Note les éléments qui restent à confirmer. Les journaux et les témoignages doivent être étudiés selon la procédure de l'organisation, sans partager inutilement de données confidentielles.

**Réponse.** Corriger l'autorisation de chaque ressource et ajouter des tests avec des identités différentes. Les actions doivent être proportionnées à la gravité et aux conséquences possibles. Elles doivent être coordonnées avec les responsables, et les changements en production doivent tenir compte de la continuité du service et des besoins légitimes des utilisateurs.

**Vérification.** Vérifier qu'un utilisateur ne peut pas accéder aux dossiers d'autrui même par une requête construite manuellement. Consigne le contrôle effectué, le résultat, les écarts et les actions restantes. Ne déclare pas le risque résolu simplement parce qu'une configuration a changé : vérifie le comportement réel et l'état du service.

**À retenir.** Les contrôles d'interface ne remplacent pas ceux du serveur. Ce cas illustre le passage d'une observation à une action de sécurité vérifiable sans attribuer prématurément une intention.

