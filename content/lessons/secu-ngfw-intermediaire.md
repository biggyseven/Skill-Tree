# Architecture de pare-feu (NGFW)

> **Mise en contexte**
>
> Une entreprise utilise plusieurs réseaux : postes employés, serveurs applicatifs, Wi-Fi invité, environnement de test, accès distant et zone de services publiés. Un pare-feu classique basé sur les adresses et les ports contrôle une partie des communications. Mais une application peut utiliser des ports non habituels, un logiciel indésirable peut communiquer en HTTPS et plusieurs utilisateurs différents peuvent partager la même adresse IP après NAT ou via un proxy. L'équipe a donc besoin de comprendre non seulement le port, mais aussi l'application, l'identité, le contexte et le comportement du trafic.
>
> Un NGFW (*Next-Generation Firewall*, pare-feu de nouvelle génération) combine généralement les fonctions classiques de filtrage avec des capacités telles que l'identification applicative, les politiques liées aux utilisateurs, la prévention d'intrusion, le filtrage d'URL, la réputation de menace et l'inspection de fichiers. Les fonctions exactes varient selon le fournisseur, la licence, le mode de déploiement, le chiffrement et la version. Ce cours explique comment concevoir et exploiter ces contrôles sans croire qu'un seul appareil rend automatiquement le réseau sûr.

## 1. Objectifs pédagogiques et prérequis

À la fin du cours, tu dois pouvoir différencier un pare-feu à états d'un NGFW, comprendre les zones de sécurité et les chemins de trafic, écrire une règle fondée sur le besoin métier, expliquer l'identification d'application et d'utilisateur, distinguer contrôle d'accès et prévention d'intrusion, raisonner sur l'inspection TLS, comprendre les politiques de fichiers et d'URL, décrire les profils de menace, planifier la haute disponibilité, mesurer les effets sur les performances, lire les journaux et dépanner une politique sans ouvrir le réseau trop largement.

Les prérequis sont les bases TCP/IP, les ports et protocoles, le routage, les VLAN, les ACL, NAT, VPN et l'administration réseau. Le précédent cours sur les pare-feu présente les règles simples ; celui-ci approfondit l'architecture et les contrôles de couche applicative. Les exemples utilisent des termes génériques et des noms de fonctions rencontrés chez plusieurs fournisseurs. Il ne faut pas supposer qu'une fonction portant un nom proche se comporte exactement de la même façon sur deux produits.

## 2. Du filtrage classique au NGFW

Un filtre de paquets peut utiliser les adresses source et destination, le protocole et les ports. Un pare-feu stateful suit l'état des connexions et autorise le trafic retour associé à une session permise, selon sa machine d'état. Ces mécanismes restent indispensables ; un NGFW n'est pas un remplacement du filtrage de base, mais une extension de l'inspection et de la politique.

Un NGFW cherche à classifier le trafic par application, à tenir compte de l'utilisateur ou du groupe quand l'identité est disponible, et à appliquer des profils de sécurité au flux autorisé. Selon la plateforme, il peut intégrer ou associer IPS, filtrage Web, analyse de fichiers, réputation, contrôle DNS, détection de commandes et contrôle de transfert de données. Les moteurs peuvent se trouver dans un même appareil ou être distribués à travers des services de sécurité connectés.

**Schéma pédagogique — couches de contrôles**

~~~text
Flux entrant ou sortant
        |
        v
[Interface / zone / routage / NAT]
        |
        v
[Politique d'acces L3/L4 et etat de session]
        |
        v
[Identification application et utilisateur]
        |
        v
[Profils de securite applicables]
 IPS | URL | fichiers/malwares | reputation | protocoles
        |
        v
[Decision : autoriser / bloquer / inspecter / journaliser]
        |
        v
[Compteurs, journaux, alertes et supervision]
~~~

Le fonctionnement réel peut avoir un ordre interne différent. Certains produits évaluent la réputation avant les règles complètes, d'autres classifient le trafic progressivement ou appliquent des modules conditionnellement. Le dessin illustre les familles de contrôle, pas une séquence universelle. Consulte la documentation du système et vérifie les journaux qui indiquent quelles règles et quels profils ont réellement été appliqués.

## 3. Pourquoi le port TCP/443 ne suffit pas

Les ports sont des indices de classification, pas une preuve suffisante de l'application. Des navigateurs utilisent HTTPS, mais aussi des outils d'administration, des clients de synchronisation, des logiciels malveillants et des applications propriétaires. Inversement, une application professionnelle peut utiliser un port différent du port attendu. Une règle « autoriser TCP/443 » autorise donc une famille de connexions, mais pas forcément uniquement l'application métier souhaitée.

L'identification applicative utilise des indices disponibles : négociation de protocoles, structure des échanges, signatures, séquences de transactions, métadonnées et parfois analyse approfondie du contenu. L'efficacité dépend de la visibilité du pare-feu, de la disponibilité des décodeurs, de l'état de chiffrement et de la capacité du trafic à être correctement classifié. Un tunnel chiffré, une application inconnue ou un protocole propriétaire peuvent limiter la confiance de classification.

Une politique qui autorise une application métier par son identité réduit parfois les autorisations excessives par port, mais il faut examiner les dépendances. Certaines applications utilisent plusieurs services ou protocoles et doivent contacter des services d'identité, DNS, mise à jour ou relais. Autoriser le nom de l'application sans comprendre ces dépendances peut conduire à des erreurs ; autoriser une large plage de ports pour compenser risque d'élargir l'accès inutilement.

**Schéma pédagogique — port versus application**

~~~text
TCP/443
   |
   +--> [Navigateur vers portail approuve] ------> usage permis selon politique
   |
   +--> [Application de stockage personnel] ----> peut etre interdite
   |
   +--> [Logiciel inconnu / tunnel masque] ------> classifier / limiter / bloquer
   |
   +--> [Client malveillant en HTTPS] -----------> besoin d'inspection et contexte

Même port != même application != même risque.
~~~

L'identification applicative n'est pas infaillible. Une politique sérieuse définit le traitement des applications inconnues, journalise les classifications nouvelles et évite d'autoriser automatiquement tout ce qui utilise un port standard.

## 4. Comprendre les zones de sécurité

Une zone représente une interface, un ensemble d'interfaces ou un segment logique qui partage une politique de sécurité. Les noms varient, mais une architecture courante distingue Internet/WAN, utilisateurs internes, serveurs, DMZ, invités, administration, partenaires et tunnels VPN. L'objectif est de rendre les frontières et les règles compréhensibles plutôt que d'avoir des exceptions opaques sur des interfaces individuelles.

**Schéma pédagogique — zones et flux d'une entreprise**

~~~text
                       [Internet]
                           |
                           v
                    [NGFW perimetrique]
                    /        |        \
                   v         v         v
               [DMZ Web] [LAN interne] [VPN distant]
                   |       /      \          |
                   v      v        v         v
             [Services] [Employes] [Admin] [Pool VPN]
                         |
                    politique L3-L7
                         |
                [Serveurs sensibles]

Les fleches representent des chemins possibles, pas des autorisations automatiques.
~~~

Une zone n'est pas une étiquette de confiance absolue. Les serveurs d'une même zone peuvent avoir des niveaux de sensibilité différents ; il peut être nécessaire de compléter la segmentation par des politiques inter-hôtes ou des zones plus fines. En sens inverse, trop de zones peuvent rendre la gestion de règles difficile sans améliorer significativement le modèle de menace. La segmentation doit suivre les besoins, les responsabilités, les flux observés et les risques.

Les règles doivent considérer les flux qui traversent le pare-feu ainsi que les flux destinés à l'appareil lui-même. L'accès à l'interface de gestion du NGFW n'est pas identique au trafic qui traverse l'appareil. Les services de gestion doivent avoir des sources et protocoles précis ; le fait qu'une interface appartienne à une zone interne ne justifie pas nécessairement tous les accès administratifs.

## 5. Créer une politique fondée sur le besoin

Une règle opérationnelle devrait préciser au minimum la source, la destination, l'application ou le service, la direction ou les zones, l'action, la période si nécessaire, la journalisation et la justification. Selon le produit, elle peut inclure un utilisateur, un groupe, une catégorie d'URL, une condition de posture, un profil IPS ou un comportement de fichier.

**Schéma pédagogique — méthode de construction d'une règle**

~~~text
Besoin metier documente
        |
        v
[Qui ?] [Vers quoi ?] [Quelle application ?] [Quel motif ?]
        |
        v
[Controle de dependances et de moindre privilege]
        |
        v
[Regle precise + profils de securite]
        |
        v
[Test autorise] + [Test negatif] + [Journal]
        |
        v
[Approbation / mise en production / revue]
~~~

Une politique de refus par défaut réduit les autorisations implicites, mais elle doit être introduite avec un inventaire et un pilote pour éviter de couper des dépendances nécessaires. Si un flux critique est bloqué, la bonne réaction est d'identifier la règle et la preuve, puis d'ajouter une autorisation précise et justifiée. Une règle temporaire doit avoir un propriétaire et une date de fin, sinon elle risque de devenir permanente.

L'ordre des règles dépend du produit. Les politiques à première correspondance peuvent cacher des règles situées plus bas ; des produits combinent parfois plusieurs tables ou phases de traitement. Ne transpose pas la logique d'une marque à l'autre sans lire la documentation. Les compteurs et journaux doivent montrer quelle règle a correspondu et quels profils ont été exécutés.

## 6. Stateful inspection et tables de session

Le contrôle stateful maintient un état de connexion : adresses, ports, protocole, interface, état TCP ou informations de session pertinentes. Les paquets qui correspondent à une session existante peuvent être traités différemment des nouveaux flux. Cela aide à gérer le trafic retour, mais n'implique pas que tout paquet d'un hôte interne soit toujours sûr.

**Schéma pédagogique — session suivie**

~~~text
Client 192.0.2.10:51514
       |
       | SYN vers 198.51.100.20:443
       v
   [Regle initiale autorise ?]
       |
       v
[Creation et suivi de session]
       |
       +------ flux client --> serveur
       |
       +<----- reponse serveur <- client
       |
       v
[Expiration / fermeture / suppression de session]
~~~

La table de session est importante lors du dépannage. Une règle modifiée peut ne s'appliquer qu'aux nouvelles sessions, selon le produit. Une session longue peut continuer de fonctionner avec un état créé antérieurement. Certains produits disposent de mécanismes de revalidation, mais le comportement n'est pas identique partout. Avant d'effacer des sessions, évalue l'impact : une suppression globale peut couper des applications essentielles et compliquer le diagnostic.

Le suivi d'état ne remplace pas l'identification de l'application, les contrôles de contenu ni le moindre privilège. Une connexion initialement autorisée peut être utilisée par un processus malveillant. Les contrôles de menace examinent donc les échanges avec les capacités et limites de la plateforme.

## 7. Identification de l'application et identité utilisateur

Les mécanismes d'identification d'application classent le trafic en tenant compte de ses caractéristiques, au lieu de considérer uniquement le port. Certains produits associent une identité utilisateur à une session via un fournisseur d'identité, un agent, des journaux d'authentification ou une intégration d'annuaire. La méthode doit être fiable et adaptée à l'environnement.

L'adresse IP ne représente pas toujours une personne : une même machine peut servir à plusieurs utilisateurs, le NAT partage des adresses, les postes peuvent changer de connexion et des services intermédiaires peuvent masquer la source. Une corrélation utilisateur-IP doit donc avoir une durée de validité et une source de preuve. Les règles qui ciblent un groupe doivent définir le traitement des utilisateurs inconnus et des comptes techniques.

**Schéma pédagogique — enrichissement du contexte**

~~~text
Paquet / session
      |
      +--> adresse et port
      |
      +--> classification d'application
      |
      +--> identité utilisateur (si preuve disponible)
      |
      +--> zone, appareil, horaire et réputation
                     |
                     v
             Decision de politique
                     |
          +----------+----------+
          v                     v
       Autoriser              Refuser
       avec profils            et loguer
~~~

Une erreur d'identité peut aussi être dangereuse : si un agent fournit une correspondance IP-utilisateur périmée, une politique privilégiée peut s'appliquer au mauvais utilisateur. Surveille la fraîcheur des associations, les événements d'authentification et les changements d'adresse. Les politiques sensibles devraient prévoir un comportement sûr si l'identité n'est pas disponible.

## 8. IPS, signatures et anomalies de protocole

Un système de prévention d'intrusion (*Intrusion Prevention System*, IPS) compare le trafic à des signatures, règles, anomalies de protocole ou analyses adaptées à la plateforme. En ligne, une politique peut bloquer une session identifiée comme malveillante. Le rôle est différent de celui d'un IDS purement détectif, qui observe et alerte sans nécessairement interrompre le flux.

Une signature peut identifier une séquence connue associée à un exploit, mais elle ne garantit pas la détection de toutes les variantes. Des mises à jour sont nécessaires pour suivre les nouvelles menaces, et des faux positifs peuvent bloquer un trafic légitime. Les profils doivent être adaptés, mesurés et testés ; le mode de blocage peut être introduit progressivement selon le risque.

**Schéma pédagogique — cycle de décision IPS**

~~~text
Paquet / flux entrant
        |
        v
[Normalisation et decodage de protocole]
        |
        v
[Signatures / anomalies / contexte]
        |
     +--+----------------+
     |                   |
     v                   v
Correspondance       Aucune correspondance
     |                   |
     v                   v
[Politique IPS]       Continuer inspection
     |
     +--> alerte / log
     |
     +--> bloquer si politique preventive
~~~

L'IPS n'est pas nécessairement placé après le contrôle applicatif dans tous les produits. L'ordre dépend de la chaîne de traitement, de la performance et des fonctions activées. Le schéma représente le principe de classification et de décision ; pour dépanner un blocage, utilise les événements réels du moteur et la documentation de la plateforme.

Les signatures doivent être maintenues. Une règle IPS désactivée pour faire disparaître un faux positif peut supprimer une protection contre une attaque réelle. La bonne pratique est de recueillir l'événement, vérifier le trafic, appliquer une exception précise si elle est justifiée, documenter la durée et créer un test de non-régression.

## 9. Filtrage d'URL, réputation et DNS

Le filtrage d'URL peut appliquer des politiques par catégories, domaine, réputation, chemin ou utilisateur selon les possibilités du produit. Il peut aider à bloquer les domaines connus pour héberger du phishing ou des logiciels malveillants et à limiter certaines catégories d'usage. Les listes de réputation ne sont pas infaillibles et peuvent retarder ou mal classifier un domaine nouveau ou compromis.

L'analyse d'un URL en HTTPS dépend de la visibilité du contenu et des métadonnées. Certains contrôles peuvent classifier des domaines sans voir le contenu complet ; d'autres nécessitent une inspection TLS. Il faut distinguer les fonctions disponibles sans déchiffrement de celles qui ont besoin de voir la requête complète.

Le contrôle DNS peut analyser les requêtes vers les résolveurs prévus, appliquer des listes de domaines ou détecter des motifs suspects. Le trafic DNS chiffré vers un service externe peut réduire la visibilité si l'architecture ne le prend pas en compte. Bloquer aveuglément le DNS non autorisé peut aussi casser des clients légitimes si le chemin de résolution n'est pas documenté.

**Schéma pédagogique — requête Web avec politiques**

~~~text
[Utilisateur / poste]
         |
         v
      DNS / URL
         |
         v
[NGFW: politique d'acces]
         |
         +--> reputation / categorie
         |
         +--> application / utilisateur
         |
         +--> inspection TLS si autorisee et necessaire
         |
         v
[IPS / controle contenu selon profil]
         |
         v
[Site autorise ou blocage explique]
~~~

La réputation ne doit pas être le seul critère de décision. Un site professionnel légitime peut être compromis et une infrastructure cloud partagée peut héberger des contenus différents. Combine la réputation avec la politique d'application, la classification, l'identité, le contexte et la réponse à incident. Les exceptions d'URL doivent être précises et revues.

## 10. Inspection TLS et limites du déchiffrement

Le trafic HTTPS est chiffré entre le client et le serveur. Un NGFW peut observer certaines métadonnées sans déchiffrer le contenu, mais l'inspection complète des URL, pièces jointes ou requêtes HTTP peut nécessiter une terminaison TLS intermédiaire. Le comportement dépend du produit, des protocoles supportés et de la politique définie.

**Schéma pédagogique — inspection TLS intermédiaire**

~~~text
[Client] -- session TLS 1 --> [NGFW inspection TLS] -- session TLS 2 --> [Serveur]
                                  |
                                  +--> verifie politique
                                  +--> inspecte contenu autorise
                                  +--> journaux / decision
~~~

Dans ce modèle, l'appareil agit comme un intermédiaire de confiance et crée deux sessions TLS. Les terminaux doivent accepter l'autorité de certification utilisée par l'organisation, et le NGFW doit protéger la clé privée correspondante. Si le certificat n'est pas correctement déployé, les utilisateurs peuvent recevoir des erreurs ou être tentés d'ignorer des avertissements.

Le déchiffrement ne doit pas être activé sur tous les flux sans analyse préalable. Certains secteurs, applications, certificats mutuels, pinning de certificat ou données personnelles peuvent rendre l'inspection inadaptée ou incompatible. Les exceptions doivent être documentées ; elles ne doivent pas devenir une liste invisible qui rend la politique impossible à comprendre. Respecte le droit applicable, les règles de confidentialité et les politiques internes.

Le trafic chiffré peut aussi être surveillé par métadonnées, classification de client ou analyse de comportement, mais cela ne fournit pas le même niveau de visibilité que l'inspection du contenu. Il faut énoncer clairement ce qui est détectable et les angles morts restants. Ne promets jamais qu'un NGFW « voit tout » dans le trafic chiffré.

## 11. Inspection de fichiers et lutte contre les malwares

Un NGFW peut inspecter des fichiers transférés via des protocoles pris en charge, utiliser des signatures antimalware ou transmettre un échantillon à un service d'analyse selon la licence et l'architecture. Les résultats peuvent être immédiats ou différés ; la politique doit définir quoi faire en attendant, selon la criticité du flux.

Les fichiers peuvent être reçus par HTTPS, courrier, stockage cloud, application métier ou canaux qui ne sont pas inspectables dans la configuration actuelle. Un transfert chiffré de bout en bout, un protocole non reconnu ou un fichier volumineux peut limiter la couverture. Documente les protocoles inclus, les limites de taille, les mécanismes d'analyse et les actions en cas d'erreur.

Une réputation favorable ne garantit pas l'absence de malware nouveau. Le NGFW complète l'EDR, les contrôles applicatifs, la gestion des correctifs et les protections de messagerie. Si une menace est détectée, conserve les événements et identifiants de fichier, isole les systèmes concernés selon le plan d'incident et vérifie la présence du même indicateur dans d'autres points du réseau.

## 12. Gestion des applications inconnues et des usages à risque

Un NGFW peut classer un trafic comme inconnu quand les informations disponibles ne suffisent pas ou que le protocole n'est pas reconnu. Une bonne politique définit une action cohérente pour l'inconnu : bloquer, surveiller, limiter, ou autoriser temporairement après analyse. Le laisser implicitement passer affaiblit l'approche de moindre privilège.

Le trafic inconnu peut être légitime : nouveaux logiciels, protocoles propriétaires, mises à jour de clients, applications internes ou version récente d'un service. Il faut donc investiguer plutôt que présumer qu'il est malveillant. Observe la source, la destination, le port, le volume, la fréquence, le certificat, les journaux et la fenêtre où le trafic apparaît.

**Schéma pédagogique — traiter une application inconnue**

~~~text
Trafic non classe
       |
       v
[Identifier poste, utilisateur, destination et volume]
       |
       v
[Comparer inventaire et besoin metier]
       |
       +-----------------------+
       |                       |
       v                       v
Besoin confirme          Aucune justification
       |                       |
       v                       v
Regle limitee + test     Bloquer ou isoler selon risque
       |                       |
       +-----------+-----------+
                   v
             Surveiller et revoir
~~~

Une règle temporaire pour une application inconnue doit préciser le propriétaire, le motif, le périmètre et une échéance. Si elle devient nécessaire durablement, transforme-la en règle soutenue par un besoin documenté et une politique de sécurité appropriée. Évite les exceptions « any application » qui deviennent impossibles à auditer.

## 13. NAT, routage et politique NGFW

Un NGFW doit acheminer le trafic, éventuellement le traduire, puis appliquer les politiques conformément à son modèle de traitement. NAT ne constitue pas en soi une décision complète d'autorisation. Une traduction peut rendre un service joignable, mais une règle de sécurité doit aussi déterminer si le flux entrant est permis.

Les fonctionnalités peuvent être évaluées dans un ordre propre au produit : route, traduction, politique, identification, profils de sécurité ou autres étapes. Les règles de NAT, les politiques de sécurité et les objets d'adresse peuvent être gérés dans des écrans différents. En diagnostic, consigne les adresses avant et après traduction et regarde quelle règle correspond à chacune des étapes.

~~~text
Paquet original
      |
      v
[Route / interface d'entree]
      |
      v
[NAT si applicable] ---> adresse traduite
      |
      v
[Politique de securite]
      |
      v
[Identification et profils d'inspection]
      |
      v
[Route de sortie] ---> serveur / WAN
      |
      v
[Route retour + etat de session]
~~~

Ce diagramme illustre le raisonnement à suivre et non un ordre universel d'exécution. Les produits diffèrent, notamment pour le moment où les objets avant ou après NAT sont évalués. Consulte le guide exact pour comprendre comment les règles se réfèrent à l'adresse originale ou traduite.

En cas de problème, vérifie les deux sens. Un paquet peut parvenir au serveur après traduction mais la réponse peut suivre un autre routeur, manquer d'état de session ou être refusée par une ACL interne. Le fait que la règle NAT affiche un hit ne prouve pas que le service applicatif fonctionne.

## 14. Politiques inter-zones et moindre privilège

Le moindre privilège signifie autoriser uniquement les communications nécessaires, pas seulement bloquer quelques ports célèbres. Une règle ne doit pas autoriser « tout » entre la zone utilisateurs et la zone serveurs sous prétexte que certains systèmes doivent communiquer. Définis les applications, les destinations, les sources et les dépendances.

Une matrice de flux aide à construire la politique. Pour chaque besoin, précise l'initiateur, la destination, le service ou l'application, la justification, les propriétaires, les heures utiles, la journalisation et le comportement attendu en cas d'échec. Les flux temporairement autorisés doivent être distingués des flux permanents et revus périodiquement.

Les règles d'administration sont particulièrement sensibles. Restreins l'accès aux interfaces de gestion du NGFW à une zone et à des sources dédiées. Utilise des comptes individuels, des rôles de moindre privilège, une MFA lorsqu'elle est disponible, une journalisation des modifications et un accès de secours protégé. Ne publie pas l'interface d'administration sur Internet pour simplifier la maintenance.

## 15. Profils de sécurité : IPS, URL, malware, fichiers

Les profils de sécurité peuvent être appliqués à des règles autorisées selon le produit. Une règle qui autorise une application sans attacher le profil de sécurité prévu n'apporte pas nécessairement la détection ou la prévention attendue. Il faut donc vérifier simultanément la règle, les profils associés, le mode de blocage, la mise à jour des signatures et la journalisation.

Une politique de déploiement peut commencer en observation pour comprendre les faux positifs, puis passer en prévention après validation. Le mode d'observation seul ne bloque généralement pas le trafic détecté ; son usage doit être une étape de déploiement, pas une preuve que la menace est empêchée. Les exceptions doivent être minimales et être revues après mise à jour des signatures.

L'activation de trop de fonctions peut affecter le débit et la latence. Le dimensionnement doit prendre en compte les débits réels avec les profils activés, le nombre de sessions, les tailles de paquets, le volume TLS, les journaux et les pointes. La fiche technique qui annonce un débit de pare-feu sans inspection ne représente pas nécessairement les performances avec tous les contrôles de sécurité activés.

## 16. Performances et dimensionnement

Le dimensionnement d'un NGFW tient compte du débit avec les fonctions prévues, du nombre de nouvelles connexions par seconde, des sessions simultanées, des VPN, de l'inspection TLS, de la taille des paquets, des interfaces et de la redondance. Un équipement peut être suffisant au début et saturer après activation d'inspection ou croissance du trafic.

Ne confonds pas le débit d'un test synthétique avec le comportement applicatif réel. Mesure les performances avec les profils nécessaires, plusieurs tailles de paquets et les types de flux significatifs. Surveille CPU, mémoire, files d'attente, sessions, interfaces, pertes, latence, taux d'inspection et événements de ressources. Le problème peut venir d'un lien saturé, d'une inspection coûteuse, d'un serveur lent ou d'une mauvaise route.

Lorsque le trafic est ralenti, évite de désactiver globalement IPS ou l'inspection TLS avant d'avoir isolé la cause. Compare une règle de test, examine les métriques, vérifie les mises à jour, et ne retire qu'un profil à la fois dans un cadre autorisé. Toute réduction temporaire de protection doit être limitée, documentée et revue.

## 17. Haute disponibilité et continuité

Un déploiement critique peut utiliser une paire de NGFW en haute disponibilité, des liens redondants ou plusieurs chemins réseau. Le type d'état synchronisé, les délais de bascule et le comportement de reprise dépendent du produit. La configuration de la paire, les politiques, certificats, licences, routes et versions doivent être compatibles.

Une bascule ne doit pas être validée parce qu'un équipement secondaire devient actif. Il faut vérifier que les sessions utiles sont conservées ou rétablies selon la conception, que les routes convergent, que la politique est identique et que les journaux indiquent clairement l'événement. Les applications peuvent devoir se reconnecter si leur état n'est pas synchronisé.

Planifie des essais en fenêtre de maintenance. Vérifie la connectivité métier, les VPN, le NAT, les profils IPS, les logs et la répartition des interfaces. Une redondance mal configurée peut provoquer un split-brain, une asymétrie de trafic ou une panne plus longue que celle qu'elle devait éviter.

## 18. Journaux, événements et supervision

Les journaux NGFW peuvent contenir les sessions acceptées/refusées, l'application identifiée, les utilisateurs, la zone, la règle, la traduction, les profils IPS, les URL, les verdicts de fichier, les actions automatiques et les changements administratifs. La qualité du diagnostic dépend de la granularité et de la cohérence des horodatages.

Un journal d'acceptation massif peut générer beaucoup de volume sans aider à la réponse. Journalise les événements nécessaires aux investigations, les refus pertinents, les accès administratifs, les changements de règle et les menaces détectées. Ajuste le niveau de détail selon la capacité, les exigences de conservation et la protection des données. Évite de journaliser les secrets ou des contenus personnels non nécessaires.

**Schéma pédagogique — corrélation d'événements NGFW**

~~~text
[Journal de session] ----\
[Journal de menace] ------+--> [Collecteur / SIEM]
[Identite / MFA] ---------+          |
[DNS / proxy / endpoint] -/          v
                            correlation par temps,
                            utilisateur, IP, regle,
                            application et evenement
                                      |
                                      v
                              [Investigation / alerte]
                                      |
                                      v
                             [Reponse documentee]
~~~

Un refus ne signifie pas à lui seul une attaque. Il peut correspondre à une politique correcte, une application mal configurée ou une dépendance oubliée. À l'inverse, l'absence de refus ne prouve pas que le trafic est sûr. Il faut corréler les événements, vérifier la règle appliquée et regarder l'activité autour de l'alerte.

## 19. Changement de politique et gestion des règles

Avant un changement, identifie l'objectif, la source, la destination, les applications, les profils de sécurité, les impacts possibles, le propriétaire et la méthode de test. Exporte ou sauvegarde la configuration selon les possibilités du produit. Utilise une fenêtre appropriée pour les règles qui touchent des services sensibles ou la gestion.

Après changement, vérifie la règle qui a réellement correspondu, les compteurs, les journaux, les flux autorisés et les flux qui doivent être refusés. Un test unique depuis un seul poste n'est pas suffisant si la règle touche plusieurs VLAN et groupes. Les modifications doivent être relues par une autre personne lorsque le processus l'exige.

Une revue périodique doit rechercher les règles sans propriétaire, les règles inutilisées, les exceptions temporaires expirées, les objets doublons, les autorisations trop larges, les profils désactivés, les zones obsolètes et les flux qui ne sont plus nécessaires. Supprimer une règle inactive sans vérifier les pointes saisonnières ou les usages rares peut casser un service ; chaque retrait mérite un test adapté.

## 20. Méthode de dépannage d'un blocage

1. Décris précisément le symptôme : source, destination, application, horaire et résultat attendu.
2. Confirme la connectivité de base, les routes et les interfaces.
3. Identifie le NGFW réellement traversé et les zones d'entrée/sortie.
4. Vérifie la règle et son ordre, l'action et les objets correspondant au flux.
5. Vérifie l'adresse avant et après NAT selon le traitement du produit.
6. Observe l'application identifiée et la correspondance de l'utilisateur.
7. Consulte les événements IPS, URL, fichiers, DNS et TLS.
8. Vérifie les routes retour et l'état de session.
9. Teste avec un flux contrôlé, puis compare avec une source de référence.
10. Change un élément à la fois, documente le résultat et teste la non-régression.

Le diagnostic doit s'appuyer sur les preuves du système, pas seulement sur le fait que le navigateur affiche une erreur. Une application peut échouer à cause du DNS, d'un certificat, d'un service distant, d'une dépendance API ou d'une règle du pare-feu local, même si le NGFW ne bloque pas le flux principal.

## 21. Procédure de dépannage de faux positif IPS

Un faux positif est un trafic légitime détecté à tort comme malveillant. Il est possible mais ne doit pas être conclu à partir du seul témoignage d'un utilisateur. Collecte l'identifiant de signature, la règle, les adresses, l'heure, le protocole et les détails du moteur. Compare le paquet ou la session au comportement normal de l'application et vérifie la mise à jour de la signature.

Si la fausse détection est confirmée, utilise une exception aussi étroite que possible : source, destination, signature, application ou fenêtre, selon ce que la plateforme permet. Ajoute un motif, un propriétaire et une date de revue. Si le même trafic est observé partout, corrige la politique ou la classification de façon contrôlée plutôt que d'exclure tout le profil IPS.

Après l'exception, vérifie qu'une autre source ou un autre exploit reste détecté. Revois l'exception après la prochaine mise à jour des signatures. Les faux positifs et faux négatifs sont des compromis opérationnels qui exigent des tests et une boucle de retour avec l'équipe applicative.

## 22. Inspection TLS : décision et test

Avant d'activer la décryption TLS, identifie les catégories de trafic, les besoins métier, les exigences légales, les applications avec certificat mutuel ou certificate pinning, les données sensibles et la manière de gérer les certificats clients. Prépare une politique avec des exceptions explicites, une chaîne de confiance interne et une procédure de révocation de la CA d'inspection.

Teste depuis un groupe pilote. Vérifie les applications métier, la validation des certificats, les erreurs navigateur, les téléphones, les agents et les clients qui utilisent des protocoles spécifiques. Compare les journaux du NGFW, ceux du poste et ceux de l'application. Le test doit aussi vérifier les exclusions : un flux exclu doit être traité par les protections alternatives documentées.

L'inspection TLS ajoute des contraintes de performance et de confiance. La clé privée de l'autorité d'inspection doit être protégée comme un secret majeur. Les utilisateurs doivent comprendre la politique de l'organisation. Les exceptions ne doivent pas être accordées simplement parce qu'une application génère un avertissement sans étude du besoin.

## 23. Trois travaux pratiques guidés

### TP 1 — Politique par application et par zone

Crée une matrice de flux pour un poste utilisateur qui doit accéder à un portail HTTPS approuvé, à DNS interne et à un serveur de fichiers uniquement pour certains partages. Le poste ne doit pas accéder aux interfaces d'administration du NGFW ou des serveurs. Définis les zones, les objets, les règles et les profils appropriés dans un environnement de test.

**Correction attendue :** une règle distincte permet le portail approuvé, les flux DNS nécessaires sont limités au résolveur choisi, et l'accès fichiers est restreint aux serveurs et services nécessaires. L'administration est autorisée uniquement depuis une zone ou un groupe dédié. Les profils de sécurité applicables sont attachés aux règles concernées et les événements utiles sont journalisés. Teste chaque flux autorisé et au moins deux refus prévus.

### TP 2 — Interpréter un blocage IPS

Un utilisateur ne peut plus téléverser un document vers un portail interne après mise à jour des signatures. Le journal montre une signature IPS qui bloque la session. Collecte les faits, confirme l'identité de l'application, les adresses et le contexte. Compare avec un environnement de test et, si le faux positif est confirmé, propose une exception minimale et temporaire.

**Correction attendue :** le technicien ne désactive pas le profil IPS entier. Il prouve le faux positif, documente la signature et le flux exacts, limite l'exception, conserve les logs et vérifie que les autres protections restent actives. Une revue est planifiée après la mise à jour de signature suivante.

### TP 3 — Inspection TLS pilote

L'entreprise souhaite inspecter certains téléchargements HTTPS sur les postes administrés. Identifie les catégories et utilisateurs inclus, les cas exclus, la chaîne de certificats, le stockage de la clé, les impacts sur les applications, les règles de journalisation et la méthode de retour arrière.

**Correction attendue :** commence par un groupe pilote géré, déploie l'autorité de confiance par la méthode officielle, documente les exclusions justifiées et valide les applications sensibles. Le retour arrière restaure les sessions prévues sans désactiver les autres contrôles. La politique est publiée seulement après les tests et la validation des parties responsables.

## 24. Exercices corrigés

### Exercice 1 — Port TCP/443 autorisé

Pourquoi cette règle ne suffit-elle pas à garantir que seul le portail professionnel est accessible ?

**Correction :** de nombreuses applications peuvent utiliser HTTPS. Une règle par port ne distingue pas nécessairement les applications ni le contexte utilisateur. Il faut identifier le besoin, utiliser les fonctions applicatives disponibles et vérifier les dépendances.

### Exercice 2 — Application inconnue

Une application interne apparaît comme inconnue dans les journaux. Quelle est la démarche correcte ?

**Correction :** identifier le propriétaire, la source, la destination, le port, le protocole, les dépendances et le comportement observé. Tester dans un environnement maîtrisé, puis créer une règle précise si le besoin est justifié. Ne l'autorise pas largement par défaut.

### Exercice 3 — Une règle de sécurité correspond mais la session échoue

Cite quatre autres éléments à vérifier.

**Correction :** route de retour, NAT, état de session, résolution DNS, profil IPS/URL, inspection TLS, pare-feu hôte et état du serveur. La règle d'accès seule ne confirme pas le succès applicatif.

### Exercice 4 — Faux positif IPS

Pourquoi ne faut-il pas désactiver l'IPS entier ?

**Correction :** la désactivation élargit la surface d'exposition et supprime d'autres détections utiles. Confirme le faux positif et applique une exception limitée à la signature et au flux nécessaires, avec une date de révision.

### Exercice 5 — Inspection TLS

Quelle est une contrainte importante de la décryption TLS intermédiaire ?

**Correction :** le NGFW termine une session TLS et en ouvre une autre. Les certificats, la clé privée, la confiance des clients, les exceptions, la confidentialité et la compatibilité des applications doivent être traités explicitement.

### Exercice 6 — Une URL malveillante passe encore

Quelles causes sont plausibles ?

**Correction :** la catégorie ou réputation n'est pas utilisée par la règle qui correspond, la source utilise un autre DNS ou chemin, le trafic est chiffré et non inspecté, le domaine est nouveau, ou une exception autorise le flux. Vérifie les événements et la couverture avant de modifier la politique.

### Exercice 7 — L'accès Internet ralentit après activation de profils

Que mesurer ?

**Correction :** débit réel avec les profils actifs, latence, CPU, sessions, nouvelles connexions par seconde, interfaces, pertes, inspection TLS et éventuels événements de ressources. Désactive un profil à la fois seulement dans un cadre contrôlé si une comparaison est nécessaire.

### Exercice 8 — Une application change de port

Quelle est la différence entre règle L4 et identification applicative ?

**Correction :** une règle basée sur le port peut cesser de correspondre si le comportement change ; l'identification applicative peut reconnaître l'application à partir de ses caractéristiques, mais dépend de la visibilité et des capacités du moteur. Il faut tester la classification et conserver des règles de moindre privilège.

### Exercice 9 — L'administration du NGFW est accessible depuis tous les VLAN

Pourquoi est-ce risqué ?

**Correction :** la compromission d'un poste utilisateur peut offrir un chemin vers le plan de gestion. Isole l'administration, limite les sources, utilise une identité forte et journalise les changements. Préserve un accès de secours testé.

### Exercice 10 — HA annoncée mais panne complète lors d'une bascule

Que vérifier ?

**Correction :** état de synchronisation, versions, routes, liens, licences, politique, VPN, état de session et événements de bascule. Teste la reprise des applications et pas seulement le rôle actif/secondaire.

### Exercice 11 — Les journaux montrent un refus

Est-ce nécessairement un incident malveillant ?

**Correction :** non. Le refus peut correspondre au moindre privilège attendu, à une application mal configurée ou à une dépendance oubliée. Corrèle le contexte avec l'identité, la destination, la règle, la fréquence et les autres sources.

### Exercice 12 — L'équipe demande permit any any temporairement

Quelle alternative proposer ?

**Correction :** identifier les flux précis nécessaires et créer une règle limitée par source, destination, application et durée. Si une règle d'urgence est indispensable selon la gouvernance, elle doit avoir une approbation, un propriétaire, une surveillance renforcée et une échéance courte ; la solution ne doit pas rester permanente.

## 25. Défi final — concevoir la politique NGFW d'une agence

### Contexte

Une agence possède des postes utilisateurs, des serveurs internes, des imprimantes, un réseau invité, une zone DMZ pour un portail Web publié et un accès VPN pour les employés nomades. Les employés doivent accéder au portail métier et à certains services internes. Les invités doivent accéder à Internet, mais pas au réseau interne. Les administrateurs doivent gérer les serveurs et le NGFW depuis un poste dédié. L'organisation veut activer IPS, filtrage d'URL et inspection de fichiers sur les flux pertinents, puis envisager l'inspection TLS sur un groupe pilote.

### Correction détaillée

**Étape 1 — Recenser les zones.** Définis WAN, DMZ, utilisateurs, serveurs, invités, gestion et VPN. Cartographie les interfaces, VLAN, passerelles, sous-réseaux et routes. Les noms et interfaces doivent correspondre à la configuration réelle.

**Étape 2 — Créer la matrice des flux.** Liste les applications métier, sources, destinations, ports/dépendances, propriétaires, horaires, actions attendues et journaux nécessaires. Refuse les flux par défaut lorsqu'ils ne sont pas justifiés, mais réalise un inventaire pour éviter de couper les services essentiels.

**Étape 3 — Définir les règles d'accès.** Autorise le portail métier aux groupes concernés, limite les invités à Internet et aux services nécessaires, et réserve l'administration aux sources approuvées. Ne confonds pas identité utilisateur, IP source et application ; vérifie la méthode d'association utilisée.

**Étape 4 — Attacher les profils.** Applique les profils IPS, URL et fichiers aux flux qui doivent être inspectés. Définis le traitement des applications inconnues et les événements à centraliser. Introduis les profils de blocage suivant la validation et la tolérance aux faux positifs.

**Étape 5 — Traiter TLS avec prudence.** Définis les catégories inclues et exclues, déploie les certificats via une méthode gérée, sécurise la clé privée, teste les applications sensibles et organise le retour arrière. N'active pas l'inspection complète du trafic de tous les utilisateurs sans pilote.

**Étape 6 — Tester les scénarios positifs et négatifs.** Vérifie l'accès au portail depuis les utilisateurs autorisés, le refus depuis les invités, le refus de l'administration depuis un poste ordinaire et la détection en laboratoire d'un scénario inoffensif connu. Vérifie les journaux et profils réellement appliqués.

**Étape 7 — Mesurer et surveiller.** Mesure débit, latence, sessions, ressources, nouveaux flux, erreurs de classification, faux positifs et événements de menace. Corrèle le NGFW avec les logs d'identité, DNS et endpoints.

**Étape 8 — Préparer le changement et le rollback.** Sauvegarde la politique, note l'état avant/après, teste l'accès administratif hors bande, définis le responsable, les critères de succès et le retour arrière. Planifie la revue des exceptions et des règles temporaires.

Le défi est réussi quand les flux métier nécessaires passent, les accès invités et administratifs sont séparés, les profils de sécurité sont effectivement actifs là où ils sont requis, les exceptions sont documentées et les journaux permettent de comprendre les décisions.

## 26. Checklist de validation

- Les zones correspondent aux domaines de confiance et aux flux réels.
- Les règles sont précises, documentées et ordonnées correctement.
- Le comportement des applications inconnues est défini.
- L'identification applicative et utilisateur est vérifiée, pas supposée.
- Les profils IPS, URL et de fichiers sont appliqués aux règles prévues.
- Les mises à jour des signatures et classifications sont supervisées.
- Les limites et exclusions de l'inspection TLS sont documentées.
- Le plan de gestion est isolé et protégé.
- Le comportement NAT, routes retour et état de session est vérifié.
- Les journaux et horloges sont exploitables.
- Le dimensionnement inclut les services de sécurité activés.
- La haute disponibilité est testée par un scénario réel.
- Un test autorisé et un test de refus sont réalisés pour chaque catégorie.
- Le plan de rollback et la sauvegarde sont disponibles.
- Chaque exception temporaire possède un propriétaire et une échéance.

## 27. Glossaire

**NGFW :** pare-feu de nouvelle génération intégrant généralement des contrôles applicatifs et des profils de sécurité supplémentaires.

**Stateful inspection :** suivi de l'état des connexions pour traiter les paquets dans le contexte d'une session.

**App-ID / identification applicative :** classification du trafic par application à partir d'indices et de mécanismes propres au produit.

**IPS :** système de prévention d'intrusion capable de détecter et, selon la politique, de bloquer certains trafics malveillants.

**IDS :** système de détection qui signale une activité suspecte sans nécessairement l'interrompre.

**Inspection TLS :** traitement intermédiaire du trafic TLS par un dispositif de confiance, avec des contraintes de certificats, compatibilité et confidentialité.

**DMZ :** zone séparée pour héberger des services exposés, filtrée vis-à-vis des réseaux internes.

**NAT :** traduction d'adresses ou de ports, distincte de la décision de sécurité.

**Zone de sécurité :** groupe d'interfaces ou segment logique utilisant une politique de sécurité commune.

**Faux positif :** trafic légitime détecté comme malveillant.

**Faux négatif :** activité malveillante qui n'est pas détectée.

**SIEM :** plateforme qui centralise et corrèle des événements de sécurité.

**HA :** haute disponibilité, conception visant à maintenir ou rétablir le service lors d'une panne.

**Règle temporaire :** autorisation limitée dans le temps avec un propriétaire et une date de revue.

## 28. Références officielles

- NIST SP 800-41 Rev. 1, Guidelines on Firewalls and Firewall Policy : https://csrc.nist.gov/pubs/sp/800/41/r1/final
- Cisco Secure Firewall, Application Control : https://secure.cisco.com/secure-firewall/docs/application-control
- Cisco Secure Firewall, Threat Protection Best Practices : https://secure.cisco.com/secure-firewall/docs/threat-protection-best-practices
- Palo Alto Networks, App-ID : https://docs.paloaltonetworks.com/ngfw/administration/app-id
- Palo Alto Networks, Monitor Applications and Threats : https://origin-docs.paloaltonetworks.com/ngfw/administration/monitoring/monitor-applications-and-threats

Les possibilités d'identification applicative, d'inspection du trafic chiffré, de prévention d'intrusion, de contrôle de fichiers et de haute disponibilité varient selon le fabricant, le modèle, la version et les licences. Vérifie toujours le guide de la plateforme ciblée avant de déployer une politique en production.

## 29. Cas de dépannage NGFW — situations pratiques

### Cas de dépannage 1 — Une application utilise HTTPS mais n'est pas reconnue

**Analyse.** Le port ne suffit pas à établir l'identité de l'application ; le trafic peut être nouveau, encapsulé ou trop peu visible. Vérifie la règle ayant correspondu, les détails de classification, la source, la destination, le protocole et les dépendances. Teste avec une source de référence et documente les besoins applicatifs avant de créer une autorisation. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne crée pas une règle large sur TCP/443 pour tous les hôtes sans connaître le besoin. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 2 — Le portail métier est bloqué après une mise à jour IPS

**Analyse.** Une signature peut être devenue trop sensible ou le comportement de l'application peut correspondre à tort à un motif de menace. Collecte l'identifiant de signature, le flux, les horodatages, les paquets disponibles et la version de contenu. Confirme le faux positif en environnement maîtrisé puis crée une exception précise avec échéance. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne désactive pas l'ensemble du profil IPS comme première réponse. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 3 — Le nom de domaine est autorisé mais l'URL est refusée

**Analyse.** Une catégorie, une réputation, un chemin URL ou une politique utilisateur peut être différente de celle attendue. Consulte l'événement de filtrage URL et la règle correspondante, vérifie le profil appliqué et les éventuelles exceptions. Teste avec un domaine de référence autorisé. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne supprime pas globalement le filtrage URL pour corriger un seul cas. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 4 — L'inspection TLS provoque des erreurs de certificat

**Analyse.** Les clients peuvent ne pas faire confiance à la CA d'inspection, ou une application utilise un mécanisme incompatible. Vérifie la chaîne déployée, le nom du serveur, la date, les journaux du client et les exceptions documentées. Teste une exclusion limitée lorsque le besoin le justifie. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne demande pas aux utilisateurs d'ignorer aveuglément les avertissements de certificat. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 5 — L'inspection TLS augmente la latence

**Analyse.** La terminaison et la réinspection peuvent augmenter la charge CPU et créer un goulot d'étranglement. Mesure la latence, le débit, l'utilisation des ressources et les catégories de flux inspectées. Compare à un pilote et optimise la couverture plutôt que de désactiver globalement les protections. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne déduis pas de la seule fiche de débit sans inspection la performance attendue en mode complet. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 6 — La règle autorise le flux mais le serveur ne répond pas

**Analyse.** Le routage retour, NAT, le service serveur, l'état de session ou un pare-feu interne peut expliquer l'échec. Vérifie le chemin, la traduction avant/après NAT, les compteurs, les états de session et les logs du serveur. Teste un port applicatif autorisé avec une source connue. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne modifie pas la règle de sécurité sans preuve que le paquet est bloqué à cet endroit. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 7 — Une règle générale masque une règle plus restrictive

**Analyse.** L'ordre ou la logique de la politique peut faire correspondre le flux à une règle plus large que prévu. Examine la règle réellement appliquée, ses compteurs et l'ordre des objets/règles. Réorganise ou spécialise la politique selon la sémantique du produit et reteste les flux négatifs. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne suppose pas que toutes les plateformes évaluent les règles exactement de la même manière. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 8 — Une application inconnue génère beaucoup de trafic

**Analyse.** Un nouveau logiciel légitime ou un programme indésirable peut générer des sessions non classifiées. Corrèle les sources, destinations, volumes, identité, horaires et changements récents. Identifie le propriétaire et reproduis le comportement dans un environnement contrôlé. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne laisse pas l'application inconnue passer durablement avec une autorisation globale. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 9 — Les identités liées aux adresses IP sont incorrectes

**Analyse.** Le mappage peut être périmé ou affecté par NAT, une adresse réattribuée, un proxy ou plusieurs utilisateurs sur un hôte partagé. Vérifie la source du mappage, son âge, l'événement d'authentification et les changements d'adresse. Corrige l'intégration et contrôle les règles ciblant les groupes. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne fonde pas une règle privilégiée sur une association utilisateur-IP dont la fraîcheur n'est pas connue. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 10 — Le journal montre un refus qui est en réalité attendu

**Analyse.** Un refus peut appliquer correctement le moindre privilège, ou correspondre à une dépendance oubliée. Compare le flux avec la matrice approuvée, le propriétaire métier et les règles de destination. Justifie la nécessité avant d'ajouter une autorisation. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne traite pas chaque refus comme un défaut de sécurité à supprimer. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 11 — Le profil antimalware ne voit pas un fichier transféré

**Analyse.** Le protocole, le chiffrement, la taille ou le chemin peut être hors de la couverture inspectée. Vérifie les protocoles couverts, les limites de taille, le niveau de déchiffrement et les journaux de fichier. Complète avec EDR, messagerie sécurisée ou contrôles de dépôt si nécessaire. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne prétends pas que tout fichier sur tout protocole est automatiquement analysé. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 12 — Un flux est permis mais aucun profil de menace n'est appliqué

**Analyse.** La règle peut autoriser le trafic sans les profils prévus, ou les conditions d'application des profils diffèrent de l'attente. Vérifie les profils associés à la règle, les licences/versions, les compteurs et un flux de test. Corrige la règle dans un pilote avant le déploiement général. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne confonds pas l'action ALLOW avec une preuve que le trafic a été inspecté. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 13 — Les invités peuvent accéder à un serveur interne

**Analyse.** La politique de zone ou le routage autorise un flux trop large, ou un chemin contourne le NGFW attendu. Vérifie les interfaces, VLAN, routes inter-zones et la règle qui correspond. Teste le refus des destinations internes et vérifie le chemin IPv4 et IPv6. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne suppose pas que le nom de zone « invité » bloque automatiquement les communications. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 14 — L'accès administrateur au NGFW est accessible depuis les postes

**Analyse.** Les interfaces de gestion ou les services d'administration ne sont pas limités aux sources approuvées. Restreins le plan de gestion aux réseaux d'administration, utilise les comptes individuels et MFA si disponible, et vérifie le chemin de secours. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne modifie pas la règle de gestion avant d'avoir conservé un accès console ou hors bande. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 15 — Une bascule HA laisse les VPN en panne

**Analyse.** Les routes, certificats, versions, paramètres, sessions ou états ne sont pas synchronisés ou rétablis comme prévu. Examine les journaux de bascule, l'état de synchronisation, les routes, les associations VPN et les politiques. Teste de nouveaux tunnels et les applications derrière la passerelle. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne considère pas le rôle actif/secondaire comme la seule métrique de disponibilité. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 16 — La table de session est pleine

**Analyse.** Le nombre de connexions, le trafic en rafale ou un comportement anormal peut consommer la capacité de session. Mesure les sessions existantes et nouvelles, les ressources et les sources dominantes. Compare aux limites du modèle et aux métriques historiques ; réduit la cause identifiée selon le processus. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne supprime pas toutes les sessions sans analyser l'impact sur les services métier. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 17 — La réputation bloque un site professionnel

**Analyse.** Le domaine peut être mal classifié, nouveau ou hébergé sur une infrastructure partagée. Vérifie la catégorie, la réputation, le certificat et le besoin métier par une source fiable. Utilise si nécessaire une exception précise pour le domaine et l'usage validés. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne crée pas une exception de réputation à un domaine parent trop large sans évaluer les sous-domaines. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 18 — Le trafic DNS contourne la politique prévue

**Analyse.** Les clients peuvent utiliser un résolveur externe ou un DNS chiffré non inclus dans l'architecture de contrôle. Examine les destinations DNS, les politiques de sortie, le proxy ou DNS chiffré autorisé et les journaux. Applique la politique de résolveur avec un plan pour les clients légitimes. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne bloque pas arbitrairement tous les flux DNS avant de garantir une résolution autorisée. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 19 — Une exception temporaire n'a pas expiré

**Analyse.** Le propriétaire et la date de fin ne sont pas suivis dans le processus de règles. Identifie les flux réellement utilisés, fais confirmer le besoin et retire l'exception après test si elle n'est plus nécessaire. Programme une revue des exceptions restantes. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne garde pas une ouverture indéfinie simplement parce qu'elle a été créée pour un incident. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 20 — La règle NAT fonctionne mais l'application n'arrive pas au serveur

**Analyse.** La translation est présente mais un autre contrôle, le routage, l'état ou le service cible peut encore échouer. Compare l'adresse publique, l'adresse traduite, la règle de sécurité, la route de sortie, le serveur et le chemin retour. Corrèle les journaux avec les horodatages. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne traite pas un hit NAT comme la preuve que le flux a été autorisé et traité jusqu'au serveur. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 21 — Le NGFW protège le trafic entrant mais pas les flux internes

**Analyse.** La topologie peut faire passer les flux latéraux par un chemin qui ne traverse pas le NGFW. Cartographie les chemins inter-VLAN et inter-serveurs, place les contrôles aux frontières nécessaires ou complète par segmentation distribuée et pare-feu hôte. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne suppose pas que tout trafic interne traverse le pare-feu périmétrique. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 22 — Un utilisateur est identifié comme inconnu après connexion

**Analyse.** L'intégration identité peut être indisponible, l'adresse a changé ou la méthode d'association n'est pas fiable. Vérifie l'authentification, l'état du connecteur, les journaux d'annuaire, le mappage IP-utilisateur et le délai de rafraîchissement. Applique le comportement de repli défini par politique. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne permets pas automatiquement les mêmes droits aux utilisateurs inconnus et aux identités vérifiées. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 23 — Le téléchargement est bloqué mais aucune information n'apparaît

**Analyse.** La journalisation de fichier ou de menace peut être désactivée, la fonction peut manquer ou le flux ne fait pas partie de sa couverture. Vérifie le profil, le type de journal, les licences, le protocole et le chemin TLS. Réalise un test contrôlé avec un fichier inoffensif de validation prévu par l'organisation. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne considère pas l'absence de journal comme une preuve d'absence de menace. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 24 — Le débit chute seulement avec l'IPS actif

**Analyse.** L'inspection, le taux de nouvelles connexions ou le débit peut dépasser les ressources effectives de l'équipement. Compare des mesures de base, ressources, sessions et débit avec un jeu de tests représentatif. Vérifie les options de performance recommandées et le dimensionnement avec les profils actifs. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne laisse pas IPS désactivé en permanence sans analyse du risque et décision formelle. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 25 — Le trafic autorisé ne génère aucun journal

**Analyse.** La règle peut avoir une journalisation désactivée, une destination de collecte incorrecte ou un filtre de consultation qui masque les événements. Vérifie la configuration de logs, l'horodatage, le collecteur, les filtres et un flux de test connu. Confirme la réception des événements sur la destination finale. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne valide pas une politique sur l'hypothèse que tout événement est enregistré par défaut. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 26 — Le certificat d'inspection TLS approche de l'expiration

**Analyse.** L'expiration peut interrompre la validation du trafic inspecté ou pousser les utilisateurs à ignorer des erreurs. Planifie le renouvellement, la distribution de confiance, la validation d'un groupe pilote et une procédure de rollback. Surveille la date et l'état de la clé privée. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne renouvelle pas sans tester la chaîne et les clients concernés. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 27 — Un exploit est détecté sans preuve d'impact

**Analyse.** Une détection IPS peut signaler une tentative bloquée, une anomalie ou un faux positif. Vérifie l'action appliquée, le contexte réseau, les événements serveur et endpoint, et conserve les preuves pertinentes. Distingue tentative, blocage et compromission confirmée. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne déclare pas un système compromis sur la seule présence d'une signature, ni ne conclue qu'il est sain sans investiguer. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 28 — Une règle d'URL est bypassée par une autre application

**Analyse.** Le contrôle peut être appliqué seulement à certains types de trafic ou les flux peuvent prendre une route non inspectée. Vérifie la classification de l'application, la règle réellement correspondante, les chemins alternatifs et la visibilité TLS/DNS. Teste toutes les applications et protocoles couverts par la politique. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne suppose pas qu'une règle ciblant le navigateur s'applique à chaque client utilisant HTTP ou HTTPS. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 29 — La configuration de sécurité n'est pas cohérente entre les pairs HA

**Analyse.** Un déploiement incomplet ou une synchronisation en échec peut laisser des politiques différentes. Compare les versions et empreintes de politique, l'état de synchronisation, les objets, certificats et profils. Corrige la divergence via la procédure officielle et reteste une bascule. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne modifie pas chaque pair séparément sans connaître la méthode de synchronisation du fournisseur. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 30 — Une règle devenue inutile est toujours active

**Analyse.** L'absence de revue du cycle de vie augmente la surface d'exposition et complique l'audit. Consulte les compteurs et journaux sur une période représentative, contacte le propriétaire puis retire en fenêtre contrôlée avec test de non-régression. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne supprime pas une règle uniquement parce qu'elle n'a pas été utilisée durant une courte fenêtre. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 31 — Le contrôle applicatif et le contrôle URL donnent des résultats différents

**Analyse.** Ils évaluent des attributs différents et peuvent s'appliquer à des étapes différentes. Examine la règle, le moteur applicatif, le contexte URL, la décryption et les journaux correspondant au même flux. Documente les exceptions et les priorités entre fonctions. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne suppose pas qu'une catégorie de domaine et une identité d'application représentent le même critère. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

### Cas de dépannage 32 — Une nouvelle version de signatures modifie le classement des applications

**Analyse.** Les définitions de signatures et détecteurs évoluent, ce qui peut changer les règles qui correspondent. Consulte les notes de version, surveille les applications affectées et valide les règles sensibles en pilote. Utilise les mécanismes de prévisualisation ou de surveillance fournis par le produit. Consigne l'heure, les adresses, les zones, l'identité, la règle et les profils qui ont correspondu. Compare la configuration attendue aux événements réellement enregistrés avant d'agir.

**Erreur à éviter.** Ne désactive pas les mises à jour de sécurité indéfiniment pour conserver une classification ancienne. Après correction, teste à nouveau le flux métier, un flux qui doit être refusé et la journalisation correspondante.

## 30. Synthèse et critères de réussite

Le NGFW est utile lorsqu'il rend explicites les décisions de sécurité : qui communique, avec quelle application, vers quelle destination et sous quelles conditions. Le filtrage L3/L4 et le suivi d'état restent la base. L'identification applicative, les informations d'identité, les profils IPS, l'URL, les fichiers et les capacités d'inspection ajoutent du contexte, mais chacun dépend de la visibilité et des fonctions réellement activées.

Une politique mature se construit à partir des besoins métier, d'une segmentation claire, de règles précises, de profils maintenus et de journaux exploitables. Le déploiement doit mesurer les faux positifs, les angles morts et les effets sur les performances. Les exceptions doivent être minimales, révisées et assorties d'un propriétaire. Le NGFW complète les contrôles des endpoints, de l'identité, du DNS, du Cloud et des applications ; il ne les remplace pas.

**Le cours est maîtrisé lorsque tu peux** représenter le chemin d'un paquet, retrouver la règle qui a décidé, expliquer pourquoi un profil a été appliqué ou non, distinguer une détection d'une compromission confirmée, tester un flux autorisé et un flux refusé, puis effectuer un changement avec sauvegarde, vérification et retour arrière.

Fin du cours.