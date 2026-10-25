# SD-WAN — Niveau intermédiaire

## Configuration multisite, tunnels sécurisés, routage, politiques applicatives et dépannage


# PRÉSENTATION DU COURS

Ce cours constitue la suite directe de `sd-wan-debutant.md`.

Au niveau débutant, nous avons étudié le fonctionnement général d'un réseau WAN, les limites d'une architecture traditionnelle et le rôle du SD-WAN dans la gestion des connexions entre plusieurs sites.

Nous avons également découvert les notions d'underlay et d'overlay, les équipements WAN Edge, les plans de gestion et de contrôle, les tunnels sécurisés, les politiques applicatives, les mesures de performance et les principes du basculement.

Le niveau intermédiaire transforme ces connaissances en une démarche opérationnelle.

Nous allons reprendre l'entreprise fictive NovaTech, ses deux agences, son siège et ses services hébergés dans le cloud. L'objectif sera de comprendre comment préparer les équipements, établir les connexions nécessaires, vérifier la distribution des routes, observer les tunnels et définir des politiques qui adaptent les chemins aux exigences des applications.

Pour rendre les explications concrètes, nous utiliserons **Cisco Catalyst SD-WAN comme plateforme de référence**.

Ce choix est pédagogique : les noms des composants, les politiques et les commandes de vérification seront associés à une implémentation documentée. Les concepts fondamentaux pourront ensuite être comparés avec ceux d'autres solutions SD-WAN.

Ce cours ne suppose pas que l'apprenant dispose déjà d'une infrastructure Cisco opérationnelle. Les étapes sont décrites dans un ordre logique, afin de pouvoir être utilisées dans un laboratoire autorisé.

Le comportement exact des commandes, des fonctionnalités et des écrans d'administration doit être vérifié en fonction des versions logicielles utilisées.

## Place dans le parcours

```text
NIVEAU DÉBUTANT
sd-wan-debutant.md
        |
        v
Comprendre les WAN et le SD-WAN
Distinguer underlay et overlay
Découvrir les tunnels sécurisés
Comprendre les plans et les politiques
        |
        v
NIVEAU INTERMÉDIAIRE
sd-wan-intermediaire.md
        |
        v
Préparer NovaTech
Planifier les adresses et les sites
Intégrer les équipements
Établir les connexions de contrôle
Vérifier les routes et les tunnels
Configurer les politiques applicatives
Tester les chemins de secours
        |
        v
NIVEAU EXPERT
sd-wan-expert.md
        |
        v
Concevoir une architecture évolutive
Maîtriser la sécurité et la segmentation
Optimiser le routage et les politiques
Étudier la haute disponibilité
Automatiser les contrôles
Organiser l'exploitation avancée
```

**Règle de continuité :** le niveau intermédiaire réutilise le modèle de l'entreprise NovaTech du cours débutant. Le niveau expert devra reprendre cette même architecture pour approfondir les politiques avancées, la résilience, l'automatisation et la gouvernance.


# OBJECTIFS PÉDAGOGIQUES

À la fin du cours, l'apprenant doit être capable de :

1. Construire un plan d'adressage pour un réseau SD-WAN multisite.
2. Distinguer les informations de transport des paramètres de l'overlay.
3. Expliquer le rôle de Cisco SD-WAN Manager, SD-WAN Controller et SD-WAN Validator.
4. Comprendre l'enregistrement et l'authentification des équipements.
5. Préparer les interfaces de transport des équipements WAN Edge.
6. Vérifier les connexions de contrôle et la distribution des routes.
7. Comprendre le rôle d'OMP dans la diffusion des informations de routage.
8. Vérifier l'établissement des tunnels de données.
9. Comprendre le rôle de BFD dans la détection de la disponibilité des chemins.
10. Concevoir une politique Application-Aware Routing adaptée à une application.
11. Distinguer les politiques centralisées des politiques locales.
12. Organiser la segmentation des services de NovaTech.
13. Comprendre les principes de l'Internet breakout.
14. Définir un protocole de test et de validation après configuration.
15. Diagnostiquer les pannes de transport, de contrôle, de tunnel et de politique.
16. Préparer le projet pour les mécanismes avancés du niveau expert.

## Prérequis

L'apprenant doit maîtriser les notions du niveau débutant :

- WAN traditionnel et SD-WAN.
- Underlay et overlay.
- Adresses IP et routage.
- Tunnels sécurisés.
- Latence, gigue et pertes de paquets.
- Politiques applicatives.
- Principes du basculement.
- Segmentation et sécurité de base.

Il est également recommandé de connaître les notions de VPN, de routes statiques, de routage dynamique, de pare-feu et de NAT.


# PARTIE 1 — REPRENDRE LE SCÉNARIO NOVATECH

## 1. Présentation de l'entreprise

NovaTech possède un siège social, deux agences et des services hébergés dans le cloud.

Les employés des agences doivent accéder aux applications centrales, aux services partagés et aux ressources Internet.

L'entreprise dispose de plusieurs types de connectivité WAN. Chaque accès possède ses caractéristiques de coût, de capacité, de latence et de disponibilité.

La mission consiste à construire un réseau capable de relier ces sites, de sécuriser les échanges et de sélectionner les chemins adaptés aux applications.

Dans un premier temps, nous allons privilégier la stabilité et la visibilité. Les équipements devront être intégrés correctement, les routes vérifiées et les tunnels établis avant d'ajouter des politiques applicatives.

Cette approche réduit la difficulté du dépannage : si un problème apparaît après la mise en place d'une politique, il sera possible de déterminer si le transport et l'overlay fonctionnaient correctement avant le changement.

## 2. Topologie de référence

Le réseau de NovaTech utilise les éléments suivants :

| Site | Rôle | Accès WAN |
|---|---|---|
| HQ | Siège et services centraux | MPLS et Internet |
| BR-A | Première agence | MPLS et Internet |
| BR-B | Deuxième agence | Internet et accès mobile |
| CLOUD | Services hébergés | Connectivité adaptée à la plateforme cloud |

Ces accès représentent un scénario pédagogique. Ils ne sont pas des recommandations universelles sur les technologies de transport à choisir.

L'entreprise doit vérifier que les chemins sont réellement distincts, que les capacités sont suffisantes et que les défaillances communes ont été prises en compte.

### Architecture logique

```text
                         CLOUD
                           |
                           |
                      +----+----+
                      |   HQ    |
                      |  SIÈGE  |
                      +----+----+
                           |
                +----------+----------+
                |                     |
                v                     v
             BR-A                    BR-B
             AGENCE A                AGENCE B
```

Chaque site possède un équipement WAN Edge. Cet équipement relie le LAN local à l'underlay et participe à l'overlay SD-WAN.

Les tunnels logiques entre les équipements permettent de transporter les données entre les sites lorsque les routes et les politiques autorisent la communication.

La topologie réelle peut être de type hub-and-spoke, full-mesh ou mixte. Les communications directes entre agences ne doivent pas être supposées présentes avant d'avoir vérifié la topologie et les routes distribuées.

## 3. Réutiliser les concepts du niveau débutant

Le niveau débutant a introduit trois notions essentielles.

L'underlay transporte les paquets entre les adresses de transport. Il peut utiliser MPLS, Internet ou d'autres services IP.

L'overlay représente la connectivité logique entre les équipements SD-WAN. Il peut utiliser des tunnels sécurisés et des mécanismes de distribution des routes.

Les politiques définissent le comportement attendu pour le trafic : chemin préféré, critères de performance, segmentation et règles de sécurité.

Le niveau intermédiaire doit vérifier chacune de ces fonctions séparément.

Un lien Internet opérationnel ne prouve pas que le tunnel SD-WAN est établi. Un tunnel établi ne prouve pas que la route de l'application est présente. Une route présente ne garantit pas que la politique sélectionne le chemin voulu.

Cette distinction est fondamentale pour la suite du cours.


# PARTIE 2 — CHOISIR LA PLATEFORME DE RÉFÉRENCE

## 4. Pourquoi utiliser Cisco Catalyst SD-WAN ?

Il existe plusieurs solutions SD-WAN, et chacune possède ses composants, ses mécanismes de contrôle et ses outils d'administration.

Nous utiliserons Cisco Catalyst SD-WAN pour les exemples pratiques afin d'avoir une terminologie cohérente et des procédures de vérification identifiables.

Dans la documentation actuelle de Cisco, les composants principaux sont présentés avec les noms suivants :

- **Cisco SD-WAN Manager** : gestion, configuration centralisée et supervision.
- **Cisco SD-WAN Controller** : plan de contrôle de l'overlay et distribution des informations de routage et de politique.
- **Cisco SD-WAN Validator** : orchestration et assistance à l'intégration des équipements.
- **WAN Edge** : équipement de bordure qui transporte le trafic des utilisateurs et forme les connexions de données.

Certains documents ou certaines versions peuvent encore employer les anciens noms commerciaux vManage, vSmart et vBond. Il faut tenir compte des noms et des fonctionnalités de la version réellement utilisée. [Documentation d'architecture Cisco Catalyst SD-WAN](https://www.cisco.com/c/en/us/td/docs/solutions/CVD/SDWAN/cisco-sdwan-design-guide.html)

## 5. Le rôle du SD-WAN Manager

Le Manager constitue l'interface principale d'administration.

Il permet généralement de préparer les configurations, gérer les équipements, définir les politiques et consulter des informations de supervision.

Il n'est pas nécessaire que le trafic de tous les utilisateurs traverse le Manager.

Les équipements WAN Edge assurent le forwarding du trafic. Le Manager intervient surtout dans la gestion, la configuration et la visibilité sur le fonctionnement du réseau.

Cette séparation est importante pour comprendre le comportement du système en cas de panne de la plateforme de gestion.

Une indisponibilité de l'interface de gestion peut limiter la capacité de modifier ou de superviser le réseau sans nécessairement interrompre immédiatement toutes les communications déjà établies.

Le comportement exact doit toutefois être confirmé pour la version et l'architecture considérées.

## 6. Le rôle du SD-WAN Controller

Le Controller participe au plan de contrôle. Il maintient les informations nécessaires à la connaissance de l'overlay et distribue les routes et les politiques selon les mécanismes de la solution.

Dans Cisco Catalyst SD-WAN, le protocole OMP (*Overlay Management Protocol*) joue un rôle important dans la distribution des informations de routage entre les composants de contrôle et les équipements WAN Edge.

Les routes, les informations de transport et certaines informations de service sont utilisées pour construire l'état de l'overlay.

La connectivité de contrôle et la connectivité de données doivent être examinées séparément.

La réception d'une route par OMP ne suffit pas à garantir que le paquet atteindra son destinataire : le next-hop doit être résolu et un chemin de données opérationnel doit exister.

## 7. Le rôle du SD-WAN Validator

Le Validator participe à l'intégration et à l'orchestration des équipements.

Selon le mode d'enregistrement utilisé, il intervient dans les procédures d'initialisation, d'authentification et de découverte des composants nécessaires à l'intégration.

Les équipements doivent pouvoir communiquer avec les composants attendus et posséder les informations d'identité requises.

Une mauvaise configuration de l'enregistrement ou des certificats peut empêcher un équipement de rejoindre correctement le réseau SD-WAN.

Le Validator ne doit pas être confondu avec un routeur qui transporterait le trafic applicatif entre toutes les agences.

## 8. Le rôle des WAN Edge

Les WAN Edge se trouvent à la bordure des sites.

Ils disposent d'interfaces de transport et d'interfaces côté services. Ils établissent les connexions de données prévues par l'architecture et appliquent les politiques qui déterminent le traitement du trafic.

Ils peuvent également mesurer les performances des chemins et sélectionner les tunnels selon les critères définis.

Ce sont les équipements qui transmettent le trafic utilisateur entre les sites et les réseaux concernés.

### Séparation fonctionnelle

```text
GESTION
SD-WAN Manager
       |
       v
CONTRÔLE
SD-WAN Controller
       |
       v
TRANSPORT DES DONNÉES
WAN Edge <---- tunnels ----> WAN Edge
       |
       v
Réseaux des utilisateurs
```

Ce schéma simplifie les relations entre les composants. Dans une architecture réelle, les chemins de communication et les dépendances de chaque composant doivent être vérifiés dans la documentation de la version déployée.


# PARTIE 3 — PLANIFIER LE RÉSEAU AVANT LA CONFIGURATION

## 9. Pourquoi préparer un plan d'adressage ?

Un réseau SD-WAN mal planifié peut fonctionner dans une configuration initiale puis devenir difficile à maintenir lorsque des sites sont ajoutés.

Le plan d'adressage doit distinguer les interfaces de transport, les identifiants logiques des équipements et les sous-réseaux des utilisateurs.

Il faut éviter les ambiguïtés entre les adresses du réseau de transport et celles des réseaux de services.

Pour chaque site, l'administrateur doit savoir quelles adresses sont utilisées pour le transport, quelle adresse identifie l'équipement dans l'overlay et quels préfixes doivent être annoncés aux autres sites.

Le plan doit aussi préciser les accès de secours et les routes attendues.

## 10. Exemple de plan d'adressage

Les plages ci-dessous sont fictives et servent uniquement à illustrer la méthode. Elles ne doivent pas être considérées comme des adresses réellement configurées.

| Site | Réseau LAN d'entreprise | Réseau voix | Transport principal | Transport secondaire |
|---|---|---|---|---|
| HQ | `10.10.0.0/16` | `10.110.0.0/16` | MPLS | Internet |
| BR-A | `10.20.0.0/16` | `10.120.0.0/16` | MPLS | Internet |
| BR-B | `10.30.0.0/16` | `10.130.0.0/16` | Internet | Mobile |

Le plan complet doit également contenir les adresses des interfaces de transport, les adresses de loopback éventuelles, les identifiants de site et les paramètres nécessaires à la plateforme.

Les identifiants logiques d'un équipement doivent être uniques dans le domaine SD-WAN lorsqu'une solution l'exige.

Il faut aussi vérifier que les sous-réseaux des sites ne se chevauchent pas involontairement. Un chevauchement peut provoquer des ambiguïtés de routage et compliquer la distribution des préfixes.

## 11. Distinguer les interfaces de transport des interfaces de service

Dans Cisco Catalyst SD-WAN, les interfaces sont organisées selon les VPN logiques utilisés par la plateforme.

Une convention courante consiste à utiliser :

- **VPN 0** pour les interfaces de transport WAN et certaines fonctions nécessaires à la connectivité de l'overlay.
- **VPN 512** pour les fonctions de gestion hors bande lorsque cette organisation est utilisée.
- D'autres VPN pour les réseaux de services, les LAN des utilisateurs et les segments spécialisés.

Il s'agit de conventions propres à Cisco Catalyst SD-WAN, et non de règles universelles applicables à toutes les solutions.

Le plan d'adressage doit documenter chaque interface, son rôle, son réseau et les routes attendues.

## 12. Vérifier les routes avant l'overlay

Avant d'établir les tunnels SD-WAN, il faut confirmer que les adresses de transport peuvent être jointes.

Si le réseau utilise des routes statiques, elles doivent être présentes et correctes. Si un protocole de routage dynamique est utilisé, les adjacences et les routes doivent être examinées.

La connectivité entre les équipements de transport ne doit pas dépendre d'un chemin qui nécessite lui-même l'overlay que l'on cherche à établir.

Une vérification simple peut utiliser les outils de diagnostic disponibles sur les équipements pour contrôler l'adresse source, la destination et le chemin emprunté.

Cette étape facilite fortement le dépannage ultérieur.


# PARTIE 4 — PRÉPARER LE LABORATOIRE

## 13. Les environnements possibles

Un véritable laboratoire Cisco Catalyst SD-WAN nécessite les images logicielles, les ressources de calcul, les licences et les droits d'utilisation appropriés pour les composants retenus.

Il peut s'appuyer sur une plateforme de laboratoire prise en charge, un environnement de virtualisation autorisé ou une infrastructure d'essai fournie par l'organisation.

Il ne faut pas supposer qu'un simple routeur Linux ou qu'un ensemble de machines virtuelles génériques reproduira toutes les fonctions d'un contrôleur SD-WAN commercial.

Des outils génériques peuvent permettre de tester l'adressage, le routage, les tunnels IPsec ou certaines politiques de trafic. Ils ne démontrent pas à eux seuls le fonctionnement du plan de contrôle propriétaire de Cisco Catalyst SD-WAN.

Pour apprendre cette implémentation, il faut donc utiliser un environnement qui prend réellement en charge les composants et fonctions concernés.

## 14. Les prérequis du laboratoire

Avant de commencer, préparez une fiche contenant :

- La version logicielle du Manager.
- La version logicielle du Controller et du Validator.
- La version des images WAN Edge.
- Les licences nécessaires.
- La topologie.
- Le plan d'adressage.
- Les identifiants des équipements.
- Les certificats et méthodes d'authentification.
- Les paramètres de transport.
- Les préfixes LAN à annoncer.
- Les politiques attendues.
- Les étapes de vérification.
- La procédure de nettoyage ou de retour arrière.

Les fonctionnalités et les procédures d'enregistrement peuvent varier entre les versions. Il faut vérifier leur compatibilité avant de créer les configurations.

## 15. Préparer les étapes du déploiement

Le laboratoire doit suivre un ordre logique.

D'abord, il faut intégrer les équipements et valider leur identité.

Ensuite, il faut mettre en place la connectivité de transport.

Puis, il faut établir les connexions de contrôle et vérifier les routes de l'overlay.

Après cela, il faut confirmer les tunnels de données.

Enfin, les politiques applicatives et les mécanismes de basculement peuvent être introduits progressivement.

Cette organisation évite de configurer toutes les fonctions en même temps et de rendre les causes d'une panne difficiles à identifier.


# PARTIE 5 — INTÉGRER LES ÉQUIPEMENTS AU RÉSEAU SD-WAN

## 16. Comprendre l'onboarding

L'onboarding correspond au processus d'intégration d'un nouvel équipement dans l'architecture SD-WAN.

Selon la plateforme, le processus peut inclure une initialisation, une authentification, une vérification de l'identité, l'association de l'équipement à une organisation et l'application d'une configuration initiale.

L'intégration ne se résume pas à attribuer une adresse IP à un routeur.

L'équipement doit être reconnu et autorisé par les composants de contrôle. Il doit également disposer des informations nécessaires pour trouver les composants de gestion et de contrôle.

Dans Cisco Catalyst SD-WAN, les procédures d'onboarding décrivent les échanges nécessaires entre les équipements WAN Edge et les composants SD-WAN. Il faut suivre les procédures officielles correspondant à la plateforme et à la version utilisées. [Cisco Catalyst SD-WAN Onboarding Guide](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/onboarding/sdwan-onboarding-guide.html)

## 17. Pourquoi l'identité des équipements est-elle importante ?

Dans un réseau qui utilise des tunnels sécurisés, un équipement ne doit pas pouvoir rejoindre librement l'overlay simplement parce qu'il dispose d'une adresse IP.

Son identité doit être vérifiée selon le mécanisme d'authentification utilisé.

Les certificats et les mécanismes de confiance sont donc des éléments importants de l'intégration.

Une erreur d'identité, un certificat incorrect ou une autorisation manquante peut empêcher l'établissement des connexions de contrôle.

Il faut distinguer ce problème d'un simple défaut de routage IP : les deux situations peuvent produire une absence de connectivité entre les composants, mais les actions correctives sont différentes.

## 18. Les contrôles après onboarding

Une fois qu'un équipement a été intégré, plusieurs vérifications doivent être effectuées :

- L'identité de l'équipement est-elle reconnue ?
- Les connexions de contrôle attendues sont-elles établies ?
- Les paramètres de site sont-ils corrects ?
- L'équipement utilise-t-il les bons transports ?
- Le système a-t-il reçu la configuration attendue ?
- Les interfaces sont-elles opérationnelles ?
- L'équipement annonce-t-il ses informations de transport ?

Le fait que le routeur apparaisse dans l'interface de gestion ne démontre pas que toutes les fonctions de l'overlay sont opérationnelles.

L'état de l'équipement, celui des connexions de contrôle et celui des tunnels de données doivent être examinés séparément.


# PARTIE 6 — CONFIGURER LES MODÈLES DE BASE

## 19. Pourquoi utiliser des modèles ?

Lorsque plusieurs sites possèdent une structure similaire, les modèles de configuration permettent de réutiliser des paramètres communs et de limiter les erreurs de saisie.

Un modèle peut contenir les paramètres de transport, les interfaces de service, les routes locales et certains paramètres de sécurité.

Les valeurs qui changent d'un site à l'autre doivent être fournies par des variables ou des paramètres propres au site.

La réutilisation de modèles ne doit pas conduire à appliquer aveuglément une configuration identique à des sites qui possèdent des besoins différents.

Le modèle doit distinguer les propriétés communes des propriétés locales.

## 20. Concevoir un modèle pour NovaTech

Nous allons utiliser quatre groupes de paramètres conceptuels.

Le premier groupe décrit l'identité et le rôle du site. Il contient les informations qui permettent d'identifier l'équipement dans l'overlay.

Le deuxième groupe décrit l'underlay. Il précise les interfaces de transport, leurs adresses, les paramètres de routage et les caractéristiques des liens.

Le troisième groupe décrit les services locaux. Il comprend les réseaux des utilisateurs, les interfaces LAN, les routes locales et les éventuels segments spécialisés.

Le quatrième groupe décrit les politiques. Il peut contenir les paramètres de sécurité, les règles applicatives et les politiques de routage.

Une configuration réelle doit également prendre en compte les certificats, les versions logicielles et les paramètres spécifiques à chaque équipement.

## 21. Exemple de fiche logique

La fiche suivante illustre la structure des données utilisées pour préparer un modèle.

```text
SITE : BR-A
RÔLE : AGENCE

TRANSPORT PRINCIPAL
- Type : MPLS
- Interface : WAN-1
- Adresse : à définir dans le laboratoire
- Couleur logique : mpls

TRANSPORT SECONDAIRE
- Type : INTERNET
- Interface : WAN-2
- Adresse : à définir dans le laboratoire
- Couleur logique : biz-internet ou équivalent

SERVICES
- LAN utilisateurs
- Réseau voix
- Réseau de gestion local

POLITIQUES
- Voix : chemin répondant aux critères de qualité
- Applications métier : chemins autorisés vers HQ
- Internet : sortie selon la politique du site
```

Les noms de couleurs de transport sont des exemples de conventions utilisées dans Cisco Catalyst SD-WAN. Ils ne décrivent pas une couleur physique de câble et ne constituent pas des valeurs universelles pour toutes les plateformes.

Les valeurs exactes doivent être définies selon la version et la configuration de l'environnement.

## 22. Pourquoi les valeurs doivent-elles rester cohérentes ?

Une erreur de variable peut provoquer un comportement incorrect sur un seul site ou sur tout un groupe de sites.

Par exemple, si deux interfaces de transport sont associées à des identifiants logiques incompatibles avec les politiques, le chemin attendu peut ne pas être sélectionné.

Si une interface de service est associée à un mauvais VPN, les routes locales peuvent être annoncées dans un contexte incorrect.

Le modèle doit donc être validé avant son application, et les résultats doivent être contrôlés immédiatement après son déploiement.


# PARTIE 7 — ÉTABLIR LE PLAN DE CONTRÔLE

## 23. Vérifier les connexions de contrôle

Les connexions de contrôle permettent aux équipements de bordure de communiquer avec les composants SD-WAN nécessaires au fonctionnement de l'overlay.

Pour qu'elles soient établies, les conditions suivantes doivent être réunies :

- Le réseau de transport doit joindre les destinations nécessaires.
- Les paramètres d'identité doivent être corrects.
- Les certificats ou mécanismes d'authentification doivent être acceptés.
- Les ports et protocoles requis doivent être autorisés.
- Les paramètres de site doivent être cohérents.
- Les composants de contrôle doivent être opérationnels.

Une session de contrôle absente peut empêcher l'équipement d'apprendre les routes ou les politiques attendues.

Cependant, l'absence de connectivité de contrôle n'implique pas nécessairement que tout trafic déjà établi est immédiatement interrompu. Le comportement dépend de l'état existant et des mécanismes de reprise de la plateforme.

## 24. OMP : distribution des routes de l'overlay

Dans Cisco Catalyst SD-WAN, OMP distribue des informations associées au réseau overlay.

Les informations peuvent inclure des routes de préfixes, des informations de transport appelées TLOC et des routes de services selon les fonctions utilisées.

Les TLOC décrivent des propriétés des emplacements de transport, notamment les informations utiles pour identifier les chemins WAN.

Les routes de préfixes permettent aux équipements d'apprendre les réseaux distants. Les TLOC contribuent à déterminer comment les atteindre.

L'équipement utilise ensuite les informations retenues pour construire l'état de forwarding approprié.

Il faut retenir qu'OMP fournit des informations de contrôle. Il ne transporte pas lui-même les paquets applicatifs qui traversent les tunnels de données.

## 25. Pourquoi une route peut-elle être absente ?

Une route peut ne pas être produite localement si le préfixe n'existe pas ou si les conditions d'annonce ne sont pas satisfaites.

Elle peut aussi être produite mais ne pas être distribuée à tous les équipements en raison d'une politique, d'une topologie ou d'un état de contrôle.

Enfin, une route peut être reçue mais ne pas être sélectionnée ou installée dans le contexte local attendu.

Le diagnostic doit donc identifier l'étape à laquelle l'information disparaît.

Cette distinction évite les modifications de configuration inutiles. Si le problème est une politique de distribution, modifier l'adressage d'une interface peut ne rien résoudre.

## 26. Vérifier les routes OMP

Dans un environnement Cisco Catalyst SD-WAN, les commandes opérationnelles suivantes peuvent aider à examiner l'état de l'overlay :

```text
show sdwan omp peers
show sdwan omp routes
show sdwan omp tlocs
show sdwan control connections
```

La syntaxe et les informations disponibles dépendent du type de périphérique et de sa version. Il faut utiliser le guide de commandes correspondant à la plateforme réellement installée.

Les résultats doivent être interprétés en répondant à quatre questions :

1. La session de contrôle attendue est-elle établie ?
2. Le préfixe existe-t-il dans les routes connues ?
3. Les informations de transport nécessaires sont-elles disponibles ?
4. La route est-elle résolue et utilisable par le plan de données ?

Une route présente dans une table de contrôle ne constitue pas une preuve suffisante d'une communication de bout en bout.


# PARTIE 8 — ÉTABLIR LES TUNNELS DE DONNÉES

## 27. Pourquoi faut-il vérifier les tunnels séparément ?

Les connexions de contrôle distribuent les informations de l'overlay.

Les tunnels de données assurent le transport des paquets des utilisateurs entre les équipements de bordure.

Dans Cisco Catalyst SD-WAN, les chemins de données sécurisés sont généralement établis entre des WAN Edge selon les paramètres de transport et les informations distribuées par le plan de contrôle.

La disponibilité d'une session de contrôle ne garantit pas que tous les tunnels nécessaires sont opérationnels.

Un tunnel peut être absent à cause d'un problème de transport, de filtrage, de configuration ou de compatibilité. Il faut vérifier l'état réel des connexions de données.

## 28. Le rôle de BFD

BFD (*Bidirectional Forwarding Detection*) est utilisé pour détecter la disponibilité de chemins dans plusieurs architectures réseau.

Dans Cisco Catalyst SD-WAN, BFD participe au suivi des connexions de données entre équipements. Les sessions permettent de détecter certains cas de perte de connectivité et d'actualiser l'état des chemins.

Le délai de détection dépend des paramètres et de l'implémentation.

Un intervalle de détection plus court peut permettre une réaction rapide, mais il faut aussi éviter les réglages qui produisent des détections erronées en présence de congestion ou de conditions de transport instables.

La détection d'une panne par BFD ne signifie pas qu'une application est automatiquement fonctionnelle sur le chemin alternatif. Il faut aussi vérifier les routes, les politiques et les capacités du lien de secours.

## 29. Vérifier les sessions BFD

Les commandes suivantes permettent d'examiner l'état des sessions et certains événements associés :

```text
show sdwan bfd sessions
show sdwan bfd summary
show sdwan bfd history
```

Les commandes disponibles et leur sortie varient selon la plateforme et la version.

Il faut vérifier le nombre de sessions attendues, le nombre de sessions actives et les éventuelles variations répétées d'état.

Si plusieurs sessions passent régulièrement de l'état opérationnel à l'état indisponible, cela peut indiquer un problème de transport, une instabilité du chemin, une surcharge ou des paramètres de détection inadaptés.

L'historique permet d'examiner ces événements. Il doit être rapproché des mesures de performance et des événements d'interface.

## 30. Le comportement à vérifier

Dans un laboratoire, il faut confirmer :

- Que les connexions de données attendues existent.
- Que les chemins nécessaires sont opérationnels.
- Que les routes de l'overlay utilisent des TLOC appropriés.
- Que les mesures des chemins sont disponibles.
- Que les applications atteignent leurs destinations.
- Que la perte d'un lien produit le comportement prévu.

L'objectif n'est pas de simplement obtenir un statut `up`. Il faut démontrer que le chemin réalise la fonction attendue.


# PARTIE 9 — MESURER LES PERFORMANCES DES CHEMINS

## 31. Pourquoi mesurer le chemin ?

Dans un réseau comprenant plusieurs transports, le statut d'une interface ne suffit pas à déterminer la qualité d'un chemin.

Un lien peut être opérationnel mais présenter une forte latence, de la gigue ou des pertes.

La mesure des performances permet de déterminer si le chemin répond aux exigences d'une application.

Dans Cisco Catalyst SD-WAN, les mécanismes d'Application-Aware Routing utilisent les mesures des tunnels, notamment la latence, la gigue et les pertes, pour guider la sélection des chemins selon les politiques configurées. [Documentation Application-Aware Routing](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR/app-aware-routing.html)

## 32. Comprendre la latence

La latence représente le délai de transport des paquets selon la méthode de mesure utilisée.

Elle peut dépendre de la distance, de la charge du réseau, du nombre d'équipements traversés, des files d'attente et de la capacité de traitement.

Une application interactive peut devenir difficile à utiliser lorsque le délai global dépasse ses exigences.

La latence mesurée entre deux équipements n'est cependant pas nécessairement égale au temps de réponse d'une application. Le serveur distant, le LAN et les traitements applicatifs peuvent aussi contribuer au délai global.

## 33. Comprendre la gigue

La gigue correspond aux variations du délai des paquets.

Pour la voix et la visioconférence, une variation importante peut affecter la régularité de la restitution audio et vidéo.

La gigue doit être considérée avec la latence et les pertes. Un chemin qui satisfait un objectif de latence moyenne peut tout de même produire une communication dégradée si ses délais varient fortement.

## 34. Comprendre la perte de paquets

La perte de paquets peut être causée par la congestion, des erreurs de transmission, des pannes de chemin ou des mécanismes de filtrage.

Elle affecte particulièrement les flux temps réel et peut ralentir les transferts utilisant TCP.

Les mesures doivent être interprétées avec prudence, car leur granularité et leur méthode de collecte influencent les résultats.

Une seule mesure ponctuelle ne suffit pas toujours à caractériser le comportement d'un lien sur la durée.

## 35. Comparer plusieurs chemins

Supposons que BR-A possède un transport MPLS et un transport Internet.

Le transport MPLS présente une latence de 35 ms et une perte de 0,1 % au moment de l'observation. Le transport Internet présente une latence de 65 ms et une perte de 0,2 %.

Dans cet exemple fictif, les deux chemins peuvent satisfaire une politique de qualité donnée.

Le chemin préféré dépend alors des objectifs, du coût, de la capacité et des autres règles de l'organisation.

Si les performances de l'un des liens se dégradent, la sélection peut évoluer selon la politique et les mécanismes disponibles.

Les valeurs de cet exemple ne représentent pas des caractéristiques garanties du MPLS ou d'Internet.


# PARTIE 10 — CONFIGURER UNE POLITIQUE APPLICATION-AWARE ROUTING

## 36. Qu'est-ce que l'Application-Aware Routing ?

Application-Aware Routing, ou AAR, permet d'associer une application ou une catégorie de trafic à des exigences de performance pour la sélection des chemins.

Dans Cisco Catalyst SD-WAN, les politiques AAR peuvent utiliser des classes SLA qui définissent des limites acceptables pour la latence, la gigue et les pertes.

La plateforme mesure les caractéristiques des tunnels et utilise les critères de la politique pour déterminer les chemins qui satisfont les exigences de l'application.

Le mécanisme ne consiste pas à choisir une connexion sur la seule base de son nom. Il s'appuie sur des mesures et sur les règles de sélection configurées. [Cisco Catalyst SD-WAN — SLA et AAR](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR/sla-aar.html)

## 37. Définir une classe SLA

Une classe SLA représente un ensemble de critères de performance.

NovaTech peut définir une classe destinée à la voix, avec des limites de perte, de latence et de gigue.

Les seuils sont propres au besoin de l'organisation. Les exemples pédagogiques ne doivent pas être réutilisés automatiquement dans une infrastructure de production.

Avant d'élaborer la politique, il faut déterminer les niveaux de performance nécessaires aux applications et vérifier que les chemins WAN sont capables de les atteindre.

### Exemple de critères pédagogiques

| Catégorie | Latence maximale illustrative | Gigue maximale illustrative | Pertes maximales illustratives |
|---|---:|---:|---:|
| Voix | 100 ms | 30 ms | 1 % |
| Application métier | 150 ms | 50 ms | 1 % |
| Transfert de fichiers | 250 ms | 100 ms | 3 % |

Ces valeurs servent uniquement aux exercices. Les seuils appropriés dépendent des applications, du réseau, des contrats de service et des méthodes de mesure.

Certaines applications métier peuvent exiger une latence plus faible que la voix, tandis que d'autres tolèrent davantage de délai. Les catégories ne doivent donc pas être considérées comme des règles universelles.

## 38. Construire la politique

La conception d'une politique AAR doit préciser :

- Le trafic concerné.
- Les sites auxquels la règle s'applique.
- Les chemins ou transports autorisés.
- La classe SLA.
- La priorité des règles.
- Le comportement lorsque le chemin préféré est indisponible.
- Le comportement si aucun chemin ne respecte les critères.
- Les conditions du retour au chemin préféré lorsque celui-ci redevient acceptable.

La politique doit être suffisamment claire pour que le comportement attendu puisse être testé.

Un réseau peut posséder plusieurs chemins actifs sans que tous soient adaptés à toutes les applications.

## 39. Pourquoi définir un comportement de secours ?

Supposons que le transport principal soit dégradé et que le transport alternatif soit disponible.

La politique peut sélectionner le chemin alternatif s'il satisfait les critères définis.

Mais si aucun chemin ne satisfait la classe SLA, il faut décider quoi faire.

Selon la politique, il peut être nécessaire de laisser le trafic utiliser un chemin de secours, de préférer un chemin particulier ou de limiter certaines communications.

L'action exacte dépend de la solution et de la politique définie.

Dans Cisco Catalyst SD-WAN, les actions associées à AAR et le comportement par défaut doivent être compris avec précision. Une politique dont aucune règle ne satisfait les critères ne doit pas être supposée bloquer automatiquement tous les paquets. [Guide Cisco des politiques AAR](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR.html)

## 40. Séparer la classification applicative et le choix du tunnel

Identifier une application et sélectionner un chemin sont deux opérations distinctes.

La classification détermine quel trafic correspond à la règle. La politique de routage détermine ensuite quelles conditions doivent être satisfaites pour le transmettre.

Si la classification est incorrecte, une règle de performance parfaitement configurée peut ne pas s'appliquer au trafic prévu.

Il faut donc tester le comportement avec des flux représentatifs et vérifier les résultats dans les outils de supervision de la plateforme.


# PARTIE 11 — POLITIQUES CENTRALISÉES ET POLITIQUES LOCALES

## 41. Pourquoi distinguer les types de politiques ?

Dans Cisco Catalyst SD-WAN, les politiques peuvent être définies de manière centralisée ou locale.

Les politiques centralisées sont configurées au niveau du plan de contrôle pour influencer le comportement du réseau overlay, selon leur type.

Les politiques locales sont appliquées sur les équipements de bordure et contrôlent certains comportements de routage et de traitement sur les équipements concernés.

Cette distinction ne signifie pas que toute politique centralisée agit de la même manière. Il faut identifier si elle modifie le contrôle des routes, le traitement du trafic ou les paramètres d'un équipement.

## 42. Politiques de contrôle

Une politique de contrôle influence la distribution ou la sélection des informations de routage du réseau overlay.

Elle peut notamment influencer les préfixes ou les chemins annoncés aux équipements.

Une erreur de politique de contrôle peut empêcher un site d'apprendre un préfixe nécessaire ou modifier la topologie logique.

Le dépannage doit examiner les routes produites, les routes distribuées et les résultats de leur sélection.

## 43. Politiques de données

Une politique de données contrôle le traitement des paquets.

Elle peut, selon les capacités de la plateforme, agir sur le forwarding, la sélection des chemins, certaines propriétés de trafic et certaines fonctions de NAT.

L'effet exact dépend des conditions de correspondance et des actions associées à la politique.

Il est essentiel de comprendre l'ordre d'évaluation des règles et le comportement par défaut, notamment lorsqu'aucune condition ne correspond au paquet.

## 44. Politiques locales

Une politique locale configure le comportement d'un équipement de bordure, par exemple pour certains paramètres de routage, de QoS ou d'autres fonctions prises en charge par la plateforme.

Ces politiques doivent rester cohérentes avec la politique globale.

Une erreur locale sur une agence peut produire un comportement différent de celui des autres sites, même lorsque la politique centralisée semble correcte.

La supervision doit donc permettre d'identifier les divergences entre sites.

## 45. Préparer et activer une politique

Dans une démarche d'exploitation contrôlée, il faut :

1. Définir les objectifs de la politique.
2. Déterminer les sites et les VPN concernés.
3. Définir les critères et actions.
4. Vérifier les règles et leur ordre.
5. Vérifier le comportement par défaut.
6. Évaluer l'effet sur les routes et le trafic.
7. Préparer une validation avant activation.
8. Activer la politique selon la procédure de la plateforme.
9. Vérifier sa distribution et son application.
10. Tester les flux concernés et conserver les résultats.

La réussite de la compilation ou de l'activation d'une politique ne prouve pas que son comportement correspond au besoin. Il faut aussi vérifier les résultats opérationnels.


# PARTIE 12 — ROUTAGE ET DISTRIBUTION DES PRÉFIXES

## 46. Pourquoi les routes sont-elles essentielles ?

Le SD-WAN ne remplace pas les informations de routage nécessaires à la communication entre réseaux.

Pour qu'une agence rejoigne une application hébergée au siège, l'équipement doit connaître la route vers le préfixe concerné et disposer d'un chemin de données utilisable.

Les routes peuvent provenir des réseaux locaux, de routes statiques ou de protocoles de routage, selon l'architecture.

Dans Cisco Catalyst SD-WAN, OMP distribue des informations de routage overlay. Les routes et les informations de transport permettent aux équipements de construire l'état de forwarding.

Une politique de routage peut également modifier les routes distribuées et leurs attributs.

## 47. Vérifier les préfixes

Supposons que BR-A doive joindre le réseau du siège `10.10.0.0/16`.

Il faut vérifier que ce préfixe existe localement au siège, qu'il est annoncé selon les règles prévues et qu'il apparaît dans les informations de routage de BR-A.

Si le préfixe est absent, il faut rechercher à quel stade la route n'est pas produite ou distribuée.

Si le préfixe est présent mais que la communication échoue, il faut examiner la résolution du chemin, les tunnels, les politiques de données et les mécanismes de sécurité.

## 48. Distinguer route connue et chemin utilisable

Une route peut apparaître dans une table sans que le chemin de données correspondant soit opérationnel.

Par exemple, l'équipement peut connaître le préfixe distant alors que le tunnel associé est indisponible.

Il faut alors vérifier si un chemin alternatif existe et si les politiques permettent de l'utiliser.

Cette distinction est essentielle au dépannage : la résolution d'un problème de routage n'est pas toujours suffisante pour rétablir la communication.

## 49. Contrôler les routes OMP

Les commandes suivantes peuvent être utilisées, selon le modèle d'équipement et la version :

```text
show sdwan omp routes
show sdwan omp tlocs
show sdwan omp peers
```

Pour rechercher un préfixe particulier, certaines versions prennent également en charge une forme de commande permettant de préciser ce préfixe.

Il faut consulter la référence de commandes appropriée avant d'utiliser des options précises.

L'objectif est de déterminer si la route existe, quel est son état, quelles informations de transport lui sont associées et si elle peut être utilisée pour le forwarding.


# PARTIE 13 — SEGMENTATION DES SERVICES

## 50. Pourquoi segmenter les réseaux ?

NovaTech doit séparer les utilisateurs, la voix et certains systèmes de gestion.

La segmentation limite les communications et permet d'appliquer des politiques distinctes.

Dans Cisco Catalyst SD-WAN, des VPN logiques sont couramment utilisés pour séparer les réseaux de services. Ces instances possèdent leurs propres contextes de routage et leurs règles d'accès.

La segmentation doit être préparée avant la distribution des routes afin d'éviter de connecter des réseaux qui ne doivent pas communiquer.

## 51. Exemple de segmentation

| Segment logique | Rôle | Exemple de préfixe |
|---|---|---|
| VPN 10 | Utilisateurs et applications métier | `10.20.0.0/16` à BR-A |
| VPN 20 | Voix et communications temps réel | `10.120.0.0/16` à BR-A |
| VPN 30 | Réseau invité | `172.20.0.0/16` à BR-A |
| VPN 512 | Gestion hors bande selon la convention retenue | Selon le plan de gestion |

Les identifiants et les préfixes sont fictifs. Les numéros de VPN doivent être cohérents avec la plateforme, le modèle de configuration et la convention d'administration de l'organisation.

Le fait de créer un VPN distinct ne suffit pas à garantir l'isolation complète. Les routes, les politiques de fuite de routes, les interfaces et les règles de filtrage doivent être vérifiées.

## 52. Éviter les fuites de routes

Une fuite de routes se produit lorsqu'une route est rendue accessible dans un contexte où elle n'était pas prévue.

Dans un réseau segmenté, elle peut permettre à un réseau utilisateur de connaître des préfixes réservés à l'administration ou à un service sensible.

Il faut donc vérifier les routes importées et exportées entre les instances logiques, et contrôler les politiques de communication.

Une isolation correcte doit être démontrée par les tables de routage et par des tests de connectivité négatifs et positifs.

Un test positif confirme que le flux autorisé fonctionne. Un test négatif confirme que le flux interdit n'est pas accepté dans le scénario testé.


# PARTIE 14 — INTERNET BREAKOUT

## 53. Pourquoi utiliser une sortie Internet directe ?

Le cours débutant a présenté le principe du *Direct Internet Access*.

Le niveau intermédiaire doit maintenant intégrer cette fonction dans la conception des chemins et des politiques.

NovaTech peut souhaiter que certains flux Internet sortent directement depuis une agence, tandis que les flux destinés aux applications internes continuent d'utiliser l'overlay.

Cela peut éviter certains détours vers le siège et réduire la charge du réseau central.

Cependant, les avantages ne sont pas automatiques. La décision dépend du chemin vers les services, de la capacité locale, des exigences de sécurité et du traitement du trafic retour.

## 54. Contrôler les règles de sortie

Une politique de sortie directe doit préciser les flux autorisés, les flux qui restent dans l'overlay et les règles de sécurité appliquées localement.

Le filtrage, le NAT, les contrôles DNS et la journalisation doivent être cohérents avec la politique de sécurité de NovaTech.

Une règle qui autorise la sortie directe de tous les flux sans analyse du besoin peut contourner des contrôles qui étaient auparavant appliqués au siège.

Il faut donc documenter les exceptions et vérifier qu'elles ne permettent pas d'accéder à des services internes par un chemin non prévu.

## 55. Le secours vers Internet

Certaines architectures peuvent utiliser un mécanisme de secours pour permettre au trafic Internet de sortir directement lorsque le chemin par tunnel devient indisponible.

Dans Cisco Catalyst SD-WAN, des politiques de NAT et de *fallback* existent pour certains scénarios et certaines plateformes. Leur configuration dépend de la version et du modèle de déploiement. [Documentation Cisco des politiques centralisées](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/sd-wan-centralized-policy/config-centralized-policies.html)

Avant d'utiliser un mécanisme de secours, il faut vérifier :

- Les conditions de déclenchement.
- Les flux concernés.
- La disponibilité du chemin alternatif.
- Le fonctionnement du NAT.
- Les règles de sécurité appliquées au chemin direct.
- Le trafic retour.
- Le comportement lorsque le tunnel revient.

La réussite d'un test de sortie Internet ne démontre pas que les routes applicatives internes restent correctes.


# PARTIE 15 — TESTER LE COMPORTEMENT DES POLITIQUES

## 56. Pourquoi faut-il tester plusieurs états du réseau ?

Une politique SD-WAN doit être vérifiée lorsque les liens sont disponibles, lorsque leurs performances se dégradent et lorsqu'une connexion devient indisponible.

Le comportement peut être correct dans le scénario nominal tout en échouant pendant une transition.

Il est donc nécessaire de tester plusieurs conditions et de mesurer les résultats.

## 57. Scénario normal

Au départ, les deux transports de BR-A sont disponibles.

Le chemin principal satisfait les critères de qualité de la politique. L'application vocale doit donc utiliser un chemin autorisé qui répond aux exigences définies.

L'administrateur vérifie la sélection du tunnel et observe les mesures disponibles.

Cette étape établit un état de référence auquel comparer les scénarios de dégradation.

## 58. Scénario de dégradation

Le transport principal subit une perte de paquets qui dépasse le seuil prévu pour l'application.

Si la solution mesure correctement cette dégradation et que la politique prévoit un autre chemin satisfaisant les critères, elle peut sélectionner le chemin alternatif.

Il faut mesurer :

- Le moment de la détection.
- Le chemin sélectionné après la décision.
- La durée de l'interruption éventuelle.
- Les mesures de performance après le changement.
- Le comportement du trafic retour.

L'objectif est d'évaluer la fonction réelle et pas uniquement l'état des interfaces.

## 59. Scénario de perte complète

Le transport principal devient indisponible.

Le mécanisme de détection doit identifier la défaillance et les politiques doivent permettre d'utiliser le chemin de secours prévu.

La durée du basculement dépend de plusieurs facteurs : détection, mise à jour des routes, disponibilité des tunnels, convergence et comportement de l'application.

Il ne faut pas promettre un temps de basculement universel. Celui-ci doit être mesuré sur la plateforme et dans les conditions utilisées.

## 60. Scénario où tous les chemins sont dégradés

Si aucun chemin n'offre les performances attendues, la politique doit appliquer le comportement défini pour cette situation.

Il faut éviter de déclarer l'application conforme simplement parce qu'un tunnel reste établi.

La décision peut inclure une priorité de chemin, une dégradation contrôlée ou une action différente selon les règles de l'organisation.

Le comportement exact doit être explicite dans la conception et testé en laboratoire.


# PARTIE 16 — SUPERVISION OPÉRATIONNELLE

## 61. Pourquoi combiner plusieurs niveaux de supervision ?

La supervision doit permettre d'établir la relation entre l'état des équipements, les connexions de contrôle, les tunnels de données et les résultats applicatifs.

Une seule vue n'est pas suffisante.

Par exemple, un tunnel actif ne garantit pas que la route du service est correcte. Un préfixe présent dans OMP ne garantit pas que l'application répond. Un test applicatif échoué ne signifie pas toujours que le WAN est responsable.

La supervision doit fournir plusieurs sources d'information et permettre de les corréler.

## 62. Les informations à surveiller

Pour chaque site, NovaTech doit pouvoir examiner :

- L'état du WAN Edge.
- L'état des connexions de contrôle.
- L'état des routes OMP.
- Les TLOC disponibles.
- L'état des sessions BFD.
- Les performances des chemins.
- Les changements de chemin.
- L'état des interfaces WAN.
- Les résultats des tests applicatifs.
- Les erreurs d'authentification et d'établissement de tunnel.

Les données nécessaires varient selon la politique et les services déployés.

La fréquence de collecte doit aussi être adaptée : une mesure trop espacée peut ne pas révéler certains événements transitoires, alors qu'une collecte trop fréquente peut augmenter la charge ou le volume des données.

## 63. Vérifier les connexions de contrôle

Sur un équipement qui prend en charge ces commandes, les contrôles peuvent commencer par :

```text
show sdwan control connections
show sdwan omp peers
```

Le premier permet d'examiner les connexions de contrôle. Le second aide à examiner les relations OMP.

Il faut ensuite comparer ces résultats à ce que le site devrait posséder.

Une connexion absente doit être analysée en fonction du composant concerné, de la connectivité de transport, des paramètres d'identité et de l'état des composants de contrôle.

## 64. Vérifier le transport et les tunnels

Les commandes suivantes peuvent aider à examiner les sessions de données :

```text
show sdwan bfd sessions
show sdwan bfd summary
show sdwan bfd history
```

Les résultats doivent être interprétés par site et par chemin.

Il faut vérifier si toutes les sessions attendues sont présentes, si certaines sont indisponibles et si elles changent fréquemment d'état.

Une session indisponible sur un chemin qui n'est pas utilisé peut avoir un impact différent de la panne d'un chemin indispensable à l'application.

Il faut donc associer les données de BFD aux politiques, aux routes et aux flux concernés.


# PARTIE 17 — MÉTHODE DE DÉPANNAGE

## 65. Une méthode fondée sur les dépendances

Le dépannage est plus efficace lorsqu'il suit les dépendances du réseau.

L'administrateur doit commencer par vérifier les composants indispensables à l'établissement des connexions, puis poursuivre vers les fonctions de routage, de politique et d'application.

Cette approche évite de corriger plusieurs paramètres à la fois sans savoir lequel était à l'origine de la panne.

## 66. Cas A — L'équipement ne rejoint pas le réseau SD-WAN

Il faut vérifier l'adressage local, les routes vers les composants nécessaires, les paramètres de découverte, l'identité de l'équipement et les mécanismes d'authentification.

Il faut aussi vérifier que les ports et protocoles nécessaires ne sont pas bloqués par un pare-feu.

Un équipement qui n'a pas établi ses connexions de contrôle ne possède pas nécessairement les routes et politiques attendues.

Le diagnostic doit donc distinguer les erreurs de transport et les erreurs de confiance.

## 67. Cas B — La connexion de contrôle est établie, mais les tunnels sont absents

La connectivité de contrôle permet de distribuer les informations nécessaires, mais les connexions de données doivent aussi être établies.

Il faut examiner les TLOC, les paramètres des liens, l'accessibilité des adresses de transport et l'état des sessions de données.

Un problème de MTU, de filtrage ou de compatibilité peut empêcher le bon fonctionnement des tunnels même si les connexions de contrôle restent actives.

Les informations de contrôle doivent être rapprochées de l'état opérationnel des liens.

## 68. Cas C — Le tunnel est établi, mais le préfixe distant est absent

Il faut déterminer si le réseau local annonce bien le préfixe prévu et si la distribution des routes fonctionne.

Les causes possibles incluent une route locale absente, une règle d'annonce incorrecte ou une politique de contrôle qui ne distribue pas le préfixe.

Il faut aussi vérifier le VPN logique concerné.

Modifier le tunnel n'est pas nécessairement la bonne solution si le problème concerne uniquement la distribution d'une route.

## 69. Cas D — Le préfixe existe, mais le trafic ne passe pas

Dans ce cas, il faut examiner le next-hop, le chemin de transport, les tunnels et les politiques qui affectent le flux.

Il faut vérifier que le paquet utilise l'interface et le tunnel attendus, que le trafic n'est pas rejeté par un pare-feu et que le chemin retour existe.

Un routage aller correct ne garantit pas automatiquement un routage retour correct.

Il faut aussi vérifier les éventuelles traductions NAT et les restrictions entre les réseaux logiques.

## 70. Cas E — L'application utilise le mauvais chemin

Lorsque l'application fonctionne mais n'utilise pas le chemin attendu, il faut examiner la classification du trafic et la politique qui correspond au flux.

Il faut vérifier que la règle s'applique au site, au VPN et au type de trafic concernés.

Il faut aussi confirmer que la classe SLA est bien définie et que le tunnel satisfait ou ne satisfait pas ses critères selon les mesures collectées.

Le comportement par défaut de la politique doit être examiné. Il ne faut pas supposer que l'absence de correspondance entraîne automatiquement un blocage.

## 71. Cas F — Le basculement provoque une dégradation

Un basculement peut être techniquement réussi tout en entraînant une dégradation de l'application.

Le lien de secours peut être moins performant, saturé ou dépendre d'un autre chemin défaillant.

Il faut vérifier :

- Le temps nécessaire à la détection.
- La durée de transition.
- Le débit disponible.
- Les mesures de qualité après basculement.
- Les éventuelles pertes pendant la convergence.
- Le comportement des sessions applicatives.
- Le chemin retour.

Les résultats doivent être documentés afin de distinguer une panne de la politique d'un problème de capacité.


# PARTIE 18 — PROTOCOLE DE TEST DU LABORATOIRE

## 72. État initial

Avant d'activer les politiques avancées, enregistrez l'état initial du réseau.

Il faut conserver les informations sur les interfaces, les routes, les connexions de contrôle, les tunnels et les tests de connectivité.

Cette référence permet de comparer le comportement avant et après chaque changement.

La fiche initiale doit aussi décrire les chemins qui sont censés être utilisés par les principales applications.

## 73. Test 1 — Connectivité locale

Vérifiez d'abord que les machines d'une agence peuvent accéder aux services locaux attendus.

Cette étape permet d'écarter certaines causes liées au LAN, aux VLAN, aux passerelles et aux pare-feu locaux.

Si les applications ne fonctionnent pas dans le LAN, le SD-WAN n'est pas nécessairement responsable.

## 74. Test 2 — Connectivité WAN

Vérifiez la connectivité des interfaces de transport et des destinations nécessaires au fonctionnement du réseau.

Confirmez ensuite que les connexions de contrôle et les tunnels de données sont établis.

Conservez les informations de routage pour permettre de comparer les résultats lors des étapes suivantes.

## 75. Test 3 — Connectivité applicative

Effectuez des tests représentatifs vers les services centraux et les services cloud.

Le test doit vérifier le chemin de bout en bout, et pas uniquement la disponibilité d'une interface de transport.

Pour une application métier, il peut être nécessaire de tester la connexion au service ou au port attendu. Pour la voix, des mesures de qualité et des tests de communication réels peuvent être nécessaires.

Le choix des tests dépend du service et de ses objectifs.

## 76. Test 4 — Sélection de chemin

Activez la politique d'application prévue et vérifiez le chemin utilisé.

Comparez les mesures de latence, de gigue et de pertes avec les critères de la politique.

Si le chemin choisi n'est pas celui attendu, examinez la classification applicative, les conditions de correspondance, les mesures et l'état des tunnels.

## 77. Test 5 — Dégradation du lien

Dans le laboratoire, simulez une dégradation contrôlée selon les moyens de la plateforme.

Il peut s'agir d'une perte artificielle de paquets ou d'une modification des conditions du lien dans un environnement d'émulation adapté.

La méthode doit être documentée et réversible.

Vérifiez que la politique détecte la condition, choisit le comportement attendu et produit les résultats opérationnels prévus.

## 78. Test 6 — Perte complète du lien

Simulez une panne du transport principal dans le laboratoire autorisé.

Il faut mesurer la détection, observer la sélection du chemin alternatif et confirmer la communication de bout en bout.

Après le test, rétablissez le lien et observez le comportement de retour selon la politique définie.

Le retour sur le chemin principal peut être soumis à des règles de stabilité. Il faut donc vérifier que la transition est prévisible et qu'elle ne provoque pas de changements de chemin répétés.


# PARTIE 19 — DOCUMENTATION ET GESTION DES CHANGEMENTS

## 79. Pourquoi documenter les changements ?

Une configuration qui fonctionne aujourd'hui peut être difficile à dépanner si personne ne sait pourquoi les paramètres ont été choisis.

La documentation doit décrire les intentions, les dépendances et les critères de validation.

Elle doit notamment préciser :

- Les sites concernés.
- Les préfixes et VPN associés.
- Les transports disponibles.
- Les politiques applicatives.
- Les seuils SLA.
- Les chemins préférés.
- Les comportements de secours.
- Les contrôles de sécurité.
- Les tests réalisés.
- Les résultats obtenus.

Le document doit être suffisamment précis pour permettre à un autre administrateur de comprendre et de reproduire la démarche.

## 80. Préparer un changement

Avant de modifier une politique, il faut connaître son périmètre et ses effets potentiels.

Il est préférable de préparer un plan avant l'activation.

Le plan doit indiquer ce qui sera modifié, les équipements concernés, les conditions préalables, les tests à exécuter et les critères permettant de conclure à un succès.

Il doit aussi définir ce qui se passe si le résultat ne correspond pas aux attentes.

## 81. Prévoir le retour arrière

Une procédure de retour arrière doit être préparée avant un changement important.

Elle peut consister à restaurer une version précédente de la politique ou à réappliquer une configuration validée.

Cependant, la restauration d'une configuration ne garantit pas à elle seule que les services retrouveront immédiatement leur état antérieur.

Il faut vérifier les routes, les tunnels, les mesures et le comportement des applications après le retour arrière.

La procédure doit être testée dans un environnement approprié lorsque cela est possible.


# PARTIE 20 — EXERCICES CORRIGÉS

## 82. Exercice 1 — Onboarding

**Question :** un WAN Edge possède une adresse IP correcte, mais n'établit pas ses connexions de contrôle. Quels éléments faut-il examiner ?

### Correction

Il faut vérifier la connectivité vers les composants de contrôle, les paramètres d'identité, les certificats, les autorisations et les règles de filtrage.

Il faut aussi confirmer que l'équipement utilise la procédure d'intégration correspondant à la version et au mode de déploiement retenus.

Une adresse IP correcte n'est qu'une condition parmi celles nécessaires à l'intégration.

## 83. Exercice 2 — OMP

**Question :** pourquoi une route peut-elle être présente dans les informations de contrôle sans que l'application puisse communiquer avec sa destination ?

### Correction

La route peut exister dans le plan de contrôle alors que le next-hop n'est pas résolu ou que le tunnel correspondant est indisponible.

Il faut vérifier la sélection et l'installation de la route, l'état du tunnel et les politiques qui affectent le trafic.

## 84. Exercice 3 — BFD

**Question :** pourquoi un tunnel doit-il être vérifié indépendamment des connexions de contrôle ?

### Correction

Les connexions de contrôle distribuent les informations nécessaires à l'overlay, tandis que les tunnels de données transportent le trafic applicatif.

Le plan de contrôle peut fonctionner alors qu'un chemin de données est indisponible.

L'état des sessions BFD et les données opérationnelles doivent donc être examinés séparément.

## 85. Exercice 4 — Politique SLA

**Question :** le transport principal reste opérationnel, mais la perte de paquets dépasse le seuil de la politique de voix. Que faut-il vérifier ?

### Correction

Il faut vérifier les mesures collectées, la classe SLA, la règle qui correspond au trafic et les chemins de remplacement disponibles.

Il faut ensuite confirmer que la politique permet bien de sélectionner un chemin alternatif dans les conditions observées.

Le basculement ne doit pas être supposé automatique sans vérifier la configuration et le comportement de la plateforme.

## 86. Exercice 5 — Segmentation

**Question :** le réseau invité doit accéder à Internet mais ne doit pas accéder aux applications internes. Comment vérifier la conception ?

### Correction

Il faut examiner son VPN logique, ses routes, les politiques de distribution, le routage vers Internet et les règles de sécurité.

Il faut réaliser des tests positifs vers les services autorisés et des tests négatifs vers les ressources interdites.

Le seul fait que le réseau invité possède un VPN distinct ne démontre pas l'isolation de bout en bout.

## 87. Exercice 6 — Internet breakout

**Question :** l'accès Internet direct fonctionne, mais certains contrôles de sécurité du siège ne sont plus appliqués. Quel est le problème ?

### Correction

La sortie directe a modifié le chemin du trafic et l'endroit où certains contrôles étaient appliqués.

Il faut vérifier les règles de sécurité locales, le filtrage, la journalisation et les exigences de protection des applications.

La sortie directe doit être considérée comme un changement d'architecture de sécurité autant que comme une optimisation du chemin.

## 88. Exercice 7 — Tunnel actif

**Question :** le tunnel de données est actif, mais l'application métier ne répond pas. Que faut-il vérifier ?

### Correction

Il faut examiner les routes, la segmentation, la politique qui s'applique au trafic, les pare-feu, le NAT éventuel, le chemin retour et le service distant.

Le tunnel actif ne prouve pas que le chemin applicatif est correct.

## 89. Exercice 8 — Retour au chemin principal

**Question :** après le rétablissement du lien principal, le trafic continue d'utiliser le chemin alternatif. Est-ce nécessairement une panne ?

### Correction

Pas nécessairement.

Le comportement dépend des règles de sélection, des critères de stabilité et des mécanismes de retour au chemin préféré.

Il faut vérifier la politique et les mesures disponibles, puis déterminer si la décision correspond au comportement prévu.

## 90. Exercice 9 — Capacité de secours

**Question :** le basculement fonctionne, mais l'application devient lente après le transfert de nombreux flux vers le lien de secours. Pourquoi ?

### Correction

Le lien alternatif peut ne pas posséder une capacité suffisante pour le volume de trafic qui lui est transféré.

La disponibilité et la qualité doivent être évaluées avec la charge réelle ou une charge de test représentative.

Il faut également examiner les mécanismes de QoS et la priorité des applications.

## 91. Exercice 10 — Préparation du niveau expert

**Question :** quels éléments faudra-t-il approfondir au niveau expert pour concevoir un réseau SD-WAN de grande taille ?

### Correction indicative

Il faudra approfondir la conception de l'underlay et de l'overlay, la distribution avancée des routes, les politiques de contrôle et de données, la segmentation, les mécanismes de sécurité, la haute disponibilité, la convergence et l'automatisation des contrôles.

L'objectif sera de concevoir un réseau évolutif, dont le comportement peut être testé et vérifié.


# PARTIE 21 — ERREURS FRÉQUENTES

## 92. Confondre onboarding et fonctionnement complet

Un équipement intégré dans le système de gestion ne possède pas nécessairement toutes les routes et tous les tunnels opérationnels.

**Bonne pratique :** vérifier séparément l'identité, les connexions de contrôle, les routes et les tunnels.

## 93. Activer une politique sans vérifier son comportement par défaut

Une règle peut traiter certains flux et laisser les autres suivre le comportement normal de routage.

**Bonne pratique :** définir le comportement attendu pour les flux qui ne correspondent à aucune règle et vérifier les actions réellement appliquées.

## 94. Supposer qu'une SLA classe suffit

La présence d'une classe SLA ne signifie pas que le trafic utilise un chemin qui la respecte.

**Bonne pratique :** vérifier la correspondance applicative, la politique AAR, les mesures des tunnels et le chemin effectivement sélectionné.

## 95. Confondre transport disponible et transport de bonne qualité

Un lien peut rester actif tout en présentant des pertes ou une forte latence.

**Bonne pratique :** examiner les mesures de performance et leur évolution, pas seulement l'état de l'interface.

## 96. Tester uniquement la connectivité IP

Un ping réussi peut confirmer une partie du transport mais ne prouve pas que le service applicatif fonctionne.

**Bonne pratique :** ajouter des tests représentatifs du service, des politiques et du chemin retour.

## 97. Modifier plusieurs politiques à la fois

Lorsque plusieurs modifications sont activées en même temps, il devient difficile d'identifier la cause d'un changement de comportement.

**Bonne pratique :** introduire les modifications progressivement, conserver un état de référence et mesurer les résultats.


# PARTIE 22 — GLOSSAIRE INTERMÉDIAIRE

**WAN Edge :** équipement de bordure qui relie un site à l'underlay et participe à l'overlay SD-WAN.

**SD-WAN Manager :** composant de gestion et de supervision centralisées dans Cisco Catalyst SD-WAN.

**SD-WAN Controller :** composant du plan de contrôle qui participe à la distribution des routes et politiques de l'overlay.

**SD-WAN Validator :** composant qui participe à l'orchestration et à l'intégration des équipements.

**OMP — Overlay Management Protocol :** protocole utilisé dans Cisco Catalyst SD-WAN pour distribuer des informations de contrôle de l'overlay.

**TLOC — Transport Locator :** ensemble d'informations permettant d'identifier un emplacement de transport et ses caractéristiques.

**BFD — Bidirectional Forwarding Detection :** mécanisme de détection de la disponibilité des chemins.

**Application-Aware Routing (AAR) :** mécanisme de sélection de chemins en fonction des politiques applicatives et de critères de performance.

**SLA class :** ensemble de critères de qualité utilisés pour déterminer si un chemin satisfait les exigences définies.

**VPN logique :** instance de réseau ou de routage séparée utilisée pour organiser les services et leur connectivité.

**NAT — Network Address Translation :** mécanisme de traduction d'adresses réseau.

**Internet breakout :** sortie directe de certains flux vers Internet depuis un site.

**Control policy :** politique qui influence les informations de routage ou le comportement du contrôle de l'overlay.

**Data policy :** politique qui agit sur le traitement et le forwarding des paquets selon les capacités de la plateforme.

**Onboarding :** processus d'intégration d'un équipement au système SD-WAN.

**Convergence :** processus de mise à jour des routes et des chemins après un changement ou une panne.


# PARTIE 23 — ÉVALUATION DE FIN DE NIVEAU

## 98. Questions théoriques

L'apprenant doit pouvoir répondre sans consulter le cours.

1. Quel est le rôle du SD-WAN Manager ?
2. Quelle différence existe entre le Controller et le Validator ?
3. Pourquoi l'identité des équipements doit-elle être vérifiée ?
4. Pourquoi faut-il valider l'underlay avant de diagnostiquer l'overlay ?
5. À quoi sert OMP ?
6. Quelle différence existe entre une route OMP et un tunnel de données ?
7. Quel est le rôle de BFD ?
8. Pourquoi un tunnel actif ne garantit-il pas que toutes les applications fonctionnent ?
9. Quels critères peuvent être utilisés par AAR ?
10. Comment les seuils SLA influencent-ils la sélection des chemins ?
11. Quelle différence existe entre une politique de contrôle et une politique de données ?
12. Pourquoi faut-il vérifier les VPN et les routes dans une architecture segmentée ?
13. Quels contrôles sont nécessaires avant une sortie Internet directe ?
14. Pourquoi la capacité du lien de secours doit-elle être évaluée ?
15. Comment vérifier qu'un basculement a réellement amélioré la connectivité ?
16. Quelles informations conserver avant une modification importante ?
17. Pourquoi faut-il tester le comportement lorsque tous les chemins sont dégradés ?
18. Comment distinguer une panne du WAN d'une panne applicative ?
19. Pourquoi une politique doit-elle définir le comportement des flux non correspondants ?
20. Quels éléments du projet devront être approfondis au niveau expert ?

## 99. Projet pratique de fin de niveau

Le projet consiste à documenter et à valider une architecture SD-WAN de laboratoire pour NovaTech.

Il doit inclure :

- Un plan d'adressage cohérent.
- Une topologie comprenant le siège et les deux agences.
- Une description des équipements de contrôle et des WAN Edge.
- Les paramètres nécessaires à l'intégration.
- Un inventaire des transports disponibles.
- Les routes et préfixes attendus.
- Les règles de segmentation.
- Une politique AAR pour la voix.
- Une politique pour les applications métier.
- Les règles de sortie Internet.
- Les commandes de vérification utilisées.
- Un protocole de test du transport et des tunnels.
- Un test de sélection de chemin.
- Un test de panne du transport principal.
- Un rapport des résultats.
- Une procédure de retour arrière documentée.

Les étapes de configuration réelle doivent être réalisées uniquement dans un environnement autorisé et avec les versions compatibles des composants.

Le rapport final doit distinguer clairement les contrôles exécutés, ceux qui ont réussi, ceux qui ont échoué et ceux qui n'ont pas été réalisés.

## 100. Critères de maîtrise

Le niveau intermédiaire est considéré comme acquis lorsque l'apprenant peut :

- Expliquer l'architecture de la plateforme utilisée.
- Préparer et vérifier l'underlay.
- Comprendre l'intégration des équipements.
- Vérifier les connexions de contrôle.
- Examiner les routes distribuées.
- Vérifier les tunnels et les mesures de performance.
- Construire une politique AAR correspondant à un besoin explicite.
- Organiser la segmentation des services.
- Comprendre les règles d'Internet breakout.
- Tester les changements de chemin.
- Diagnostiquer les principales pannes.
- Documenter les résultats et les limites des tests.

La maîtrise ne consiste pas simplement à obtenir un statut vert dans l'interface de gestion. Elle consiste à démontrer que les routes, les tunnels, les politiques et les applications fonctionnent conformément aux objectifs définis.


# PARTIE 24 — TRANSITION VERS LE NIVEAU EXPERT

## 101. Ce qui est maintenant acquis

Le niveau débutant a permis de comprendre les principes généraux du SD-WAN.

Le niveau intermédiaire a présenté l'architecture opérationnelle de Cisco Catalyst SD-WAN, le rôle des composants de contrôle, la préparation des transports, la vérification des routes, les tunnels de données et les politiques applicatives.

L'apprenant a également étudié la segmentation, l'Internet breakout et les principales étapes de dépannage.

Il dispose désormais d'une méthode pour séparer les problèmes de connectivité, de contrôle, de routage, de tunnel et de politique.

## 102. Le parcours complet

```text
DÉBUTANT
Comprendre le SD-WAN
        |
        v
INTERMÉDIAIRE
Configurer, vérifier et dépanner
        |
        v
EXPERT
Concevoir, sécuriser et optimiser
        |
        v
EXPLOITATION AVANCÉE
Automatisation, observabilité,
haute disponibilité et gouvernance
```

## 103. Contenu attendu du cours expert

Le cours expert reprendra la même architecture NovaTech et les paramètres construits dans les deux premiers cours.

Il approfondira notamment :

- La conception du plan de routage et de contrôle.
- Les politiques de distribution et les scénarios de topologie.
- La segmentation avancée et les politiques entre domaines.
- La haute disponibilité des équipements et des chemins.
- Le comportement en cas de panne des composants de contrôle.
- Les mécanismes avancés de sélection applicative.
- La sécurité de l'overlay et l'intégration avec les services de sécurité.
- L'automatisation des validations.
- La gestion des changements et des configurations.
- La supervision et l'analyse des performances à grande échelle.

Le niveau expert devra expliquer les décisions de conception et leurs conséquences opérationnelles. Il ne devra pas simplement reprendre les commandes de configuration du niveau intermédiaire.


# CONCLUSION GÉNÉRALE

Le niveau intermédiaire représente le passage entre la compréhension des principes SD-WAN et leur utilisation dans une architecture de laboratoire.

L'apprenant a étudié le rôle des composants de Cisco Catalyst SD-WAN, la préparation du plan d'adressage, l'intégration des équipements, les connexions de contrôle, la distribution des routes et l'établissement des tunnels de données.

Il a également approfondi les politiques Application-Aware Routing, la segmentation, la sortie Internet directe et les mécanismes de dépannage.

Ces fonctions doivent être vérifiées séparément. Un équipement intégré n'est pas nécessairement opérationnel, une route distribuée ne garantit pas l'existence d'un tunnel utilisable et un tunnel actif ne prouve pas que l'application fonctionne.

Les politiques applicatives doivent être définies en fonction des exigences métier et des mesures disponibles. Les changements doivent être testés progressivement, documentés et associés à une procédure de reprise adaptée.

Le niveau expert prolongera ce travail avec la conception avancée, la sécurité, la résilience, l'automatisation et l'exploitation d'une infrastructure multisite.

**Principe final : préparer le transport, vérifier l'identité, établir le contrôle, confirmer les routes, vérifier les tunnels, appliquer les politiques et mesurer le comportement réel des applications.**


# RÉFÉRENCES TECHNIQUES

## Architecture et intégration

- Cisco Catalyst SD-WAN — Design Guide  
  https://www.cisco.com/c/en/us/td/docs/solutions/CVD/SDWAN/cisco-sdwan-design-guide.html

- Cisco Catalyst SD-WAN — Onboarding Guide  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/onboarding/sdwan-onboarding-guide.html

- Cisco Catalyst SD-WAN — Solution Overview  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/solution/cisco-catalyst-sd-wan-solution-overview/solution.html

## Routage et supervision

- Cisco Catalyst SD-WAN — Network Monitoring Guide  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/network-monitoring/network-monitoring-guide/m-network.html

- Cisco Catalyst SD-WAN — BFD Protocol  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/network-monitoring/network-monitoring-guide/monitoring-the-network/bfd-protocol-info.html

- Cisco Catalyst SD-WAN — OMP Routing  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/routing/routing-configuration-guide/OMP-routing-protocol-ref/omp-routing-protocol-feature-history.html

## Politiques et sélection des chemins

- Cisco Catalyst SD-WAN — Application-Aware Routing  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR/app-aware-routing.html

- Cisco Catalyst SD-WAN — SLA Configuration  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR/sla-aar.html

- Cisco Catalyst SD-WAN — Centralized Policies  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/sd-wan-centralized-policy/config-centralized-policies.html

Les commandes, les noms des composants et les fonctions disponibles dépendent des versions logicielles et des modèles d'équipements. Toute configuration doit être vérifiée dans la documentation correspondant à l'environnement effectivement utilisé.