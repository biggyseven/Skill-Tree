# VTP et gestion des VLAN — Niveau Débutant

**Niveau :** Débutant

La segmentation logique des réseaux Ethernet est l'une des méthodes fondamentales de conception des réseaux d'entreprise. Un réseau local peut contenir des dizaines, des centaines, voire des milliers d'équipements : postes utilisateurs, imprimantes, téléphones IP, points d'accès Wi-Fi, serveurs, caméras et équipements de gestion. Les regrouper dans un unique domaine de diffusion simplifie parfois les premières configurations, mais devient rapidement difficile à administrer et à sécuriser. Les VLAN (*Virtual Local Area Networks*) permettent de séparer logiquement ces équipements en domaines de couche 2 distincts, même lorsque leurs ports physiques se trouvent sur les mêmes commutateurs.

Dès qu'une architecture possède plusieurs commutateurs, la gestion des VLAN doit être cohérente. Si le VLAN 20 représente le service comptabilité, il doit exister sur les commutateurs qui transportent ce trafic. Un VLAN absent d'un commutateur intermédiaire peut empêcher certains équipements de communiquer, même si les câbles, les ports et les adresses IP semblent correctement configurés. Créer et modifier manuellement chaque VLAN sur chaque commutateur est possible, mais la méthode devient source d'erreurs à grande échelle. Le VLAN Trunking Protocol (VTP), historiquement développé par Cisco, a été conçu pour diffuser de façon centralisée les informations de configuration des VLAN dans un domaine VTP.

VTP n'est toutefois ni un protocole de routage IP ni un mécanisme de transport des données utilisateurs. Il diffuse des informations de gestion des VLAN entre commutateurs compatibles, principalement à travers les liens trunk. Le trafic des postes est toujours transporté par les mécanismes Ethernet, VLAN et trunking. L'utilisation de VTP doit donc être comprise en parallèle de la création des VLAN, du protocole 802.1Q, de la configuration des ports d'accès et de la sécurité des trunks. Une mauvaise configuration VTP peut avoir un impact étendu : selon la version et le mode, une base VLAN inadéquate peut être propagée à plusieurs commutateurs.

Ce cours présente les notions nécessaires pour comprendre et configurer VTP sur un environnement Cisco débutant : rôle des VLAN, domaine VTP, modes serveur/client/transparent/off, versions 1, 2 et 3, annonces, numéro de révision, pruning, configuration pratique et dépannage. Les commandes et comportements exacts dépendent du modèle de commutateur et de sa version logicielle ; il faut donc comparer les exemples avec la documentation de la plateforme utilisée.

> **Analogie** : Imagine une entreprise qui possède plusieurs bâtiments et des équipes différentes : comptabilité, informatique, accueil et production. Chaque équipe doit disposer de ses propres salles et d'une signalétique cohérente. Les VLAN représentent les groupes logiques d'équipes ; les ports des commutateurs représentent les prises réseau attribuées à ces équipes ; les trunks représentent les couloirs qui transportent plusieurs catégories de circulation entre les bâtiments.
>
> Sans système centralisé, chaque responsable de bâtiment doit recopier manuellement les mêmes catégories et leurs noms. Une personne peut créer « COMPTA » dans le bâtiment A, « COMPTABILITE » dans le bâtiment B, puis oublier de créer la catégorie correspondante dans le bâtiment C. Les câbles sont opérationnels, mais la coordination des groupes est incorrecte.
>
> VTP ressemble à un registre commun de catégories, diffusé aux commutateurs d'un domaine compatible. En mode serveur, un commutateur autorisé peut modifier ce registre et faire connaître les changements aux autres commutateurs concernés. Un commutateur client reçoit les mises à jour et adapte sa base VLAN, sans permettre normalement à l'administrateur de créer librement les VLAN dans ce mode. Un commutateur transparent maintient sa configuration VLAN locale ; selon la version, il peut transmettre les annonces VTP reçues sans appliquer lui-même leur contenu. Le mode off, lorsqu'il est pris en charge, ne participe pas aux annonces et ne les relaie pas.
>
> Cette analogie met également en évidence le risque principal : si le registre centralisé est remplacé par un registre erroné mais considéré comme plus récent, les changements peuvent affecter plusieurs bâtiments. C'est pourquoi l'administrateur doit connaître l'origine des annonces, le domaine, la version et le numéro de révision avant de raccorder un commutateur inconnu à un réseau VTP. La centralisation réduit les oublis, mais elle ne dispense jamais de contrôle du changement ni de sauvegarde.

---

## 1. Fondamentaux et fonctionnement

### 1.1. Rappel : qu'est-ce qu'un VLAN ?

Un VLAN est un domaine logique de couche 2. Sur un commutateur Ethernet, il permet d'associer des ports à des groupes séparés. Deux postes placés dans des VLAN différents ne communiquent normalement pas directement au niveau Ethernet, même s'ils sont raccordés au même commutateur. Pour communiquer entre VLAN, ils ont généralement besoin d'un équipement de couche 3, comme un routeur ou un commutateur multicouche, et d'un plan d'adressage IP approprié.

Un VLAN ne doit pas être confondu avec un sous-réseau IP, même si les deux sont souvent associés dans une architecture d'entreprise. Le VLAN assure une séparation de couche 2 ; le sous-réseau définit un préfixe d'adresses de couche 3. Une bonne pratique courante consiste à associer un sous-réseau IP distinct à chaque VLAN utilisateur, mais cette association est une décision de conception et pas une identité absolue entre les deux concepts.

Exemple :

| VLAN | Nom | Usage | Exemple de sous-réseau |
|---:|---|---|---|
| 10 | ADMIN | Administration réseau | 192.168.10.0/24 |
| 20 | COMPTA | Comptabilité | 192.168.20.0/24 |
| 30 | SUPPORT | Assistance informatique | 192.168.30.0/24 |
| 40 | INVITES | Accès visiteurs | 192.168.40.0/24 |

Les identifiants et les noms sont des exemples. Ils doivent être définis dans le plan d'adressage et appliqués de manière cohérente. Deux VLAN de même ID dans des domaines L2 distincts ne sont pas automatiquement le même domaine de diffusion de bout en bout : il faut aussi que le VLAN soit autorisé et transporté sur les liaisons concernées.

### 1.2. Pourquoi faut-il gérer les VLAN de manière cohérente ?

Dans une topologie constituée d'un seul commutateur, il suffit parfois de créer les VLAN localement et d'affecter les ports correspondants. Dans une topologie multi-commutateurs, les VLAN doivent exister sur les commutateurs qui les transportent. Le trunking permet de faire circuler plusieurs VLAN sur une liaison physique ; chaque commutateur doit toutefois savoir à quels VLAN les trames appartiennent et quels VLAN sont autorisés sur le trunk.

Une incohérence peut apparaître dans plusieurs situations :

- le VLAN existe sur le commutateur d'accès, mais pas sur le commutateur voisin ;
- les deux commutateurs ont des trunks actifs, mais le VLAN est absent de la liste autorisée ;
- une équipe crée un VLAN sur un équipement et oublie les autres commutateurs ;
- le VLAN est renommé ou supprimé sur un seul équipement alors que la conception suppose qu'il reste disponible sur plusieurs liens ;
- une annonce VTP remplace une base VLAN locale par une configuration différente de celle attendue.

VTP peut limiter les différences de base VLAN entre les commutateurs qui participent au même domaine. Il ne corrige pas automatiquement tous les problèmes de configuration de couche 2. Par exemple, VTP ne transforme pas un port d'accès en trunk, ne configure pas automatiquement les adresses IP des passerelles, ne rend pas opérationnel un lien physique défaillant et ne remplace pas le contrôle des VLAN autorisés sur chaque trunk.

### 1.3. Qu'est-ce que VTP ?

Le VLAN Trunking Protocol est un protocole de gestion des VLAN associé à l'écosystème Cisco. Il permet de diffuser des informations VLAN entre commutateurs d'un même domaine VTP. Les informations propagées peuvent notamment concerner la création, la modification, le renommage et la suppression de VLAN, selon la version, le mode et la plateforme.

VTP s'appuie sur les liaisons trunk pour faire circuler ses annonces entre commutateurs. Un trunk transporte plusieurs VLAN sur une même liaison logique. Dans un environnement Ethernet moderne, ce transport est généralement réalisé au moyen du marquage 802.1Q. Les annonces VTP sont des messages de contrôle, distincts des trames de données ordinaires des utilisateurs.

VTP ne remplace donc pas les VLAN : il aide à gérer leur base de configuration. Il ne remplace pas non plus STP, qui protège la topologie Ethernet contre les boucles de couche 2, ni le routage inter-VLAN, qui permet aux sous-réseaux IP de communiquer. Ces fonctions sont complémentaires et répondent à des problèmes différents.

### 1.4. Domaine VTP

Un domaine VTP est un groupe logique de commutateurs qui échangent et interprètent des informations VTP selon des paramètres compatibles. Le nom de domaine joue un rôle important : les commutateurs doivent être placés dans le domaine attendu pour participer correctement à la synchronisation prévue.

Les autres paramètres importants comprennent la version de VTP et, lorsque l'authentification est configurée, le mot de passe ou le mécanisme d'authentification. Les conditions exactes dépendent de la version et du mode. Un mauvais nom de domaine, une version incompatible ou un mot de passe différent peut empêcher les annonces d'être acceptées ou la synchronisation de se comporter comme prévu.

### Schéma : la propagation dans un domaine VTP

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-label="Domaine VTP : un switch serveur transmet les annonces VLAN aux clients par les trunks" width="960" height="390" style="width:100%;height:auto;display:block"><defs><marker id="vtpDomArrow" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#67d9ff"/></marker></defs><style>.vdflow{fill:none;stroke:#67d9ff;stroke-width:4;stroke-dasharray:10 8;marker-end:url(#vtpDomArrow);animation:vtpDomDash 2.8s linear infinite}@keyframes vtpDomDash{to{stroke-dashoffset:-36}}@media(prefers-reduced-motion:reduce){.vdflow{animation:none}}</style><rect x="18" y="18" width="924" height="354" rx="22" fill="#0b1220" stroke="#263b54" stroke-width="2"/><rect x="40" y="32" width="880" height="38" rx="10" fill="#14263a" stroke="#375471"/><text x="480" y="56" font-family="system-ui,sans-serif" font-size="17" font-weight="700" fill="#eaf3ff" text-anchor="middle">DOMAINE VTP : CAMPUS-LAB</text><rect x="55" y="112" width="230" height="100" rx="14" fill="#173451" stroke="#67d9ff" stroke-width="2.5"/><text x="170" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#eef7ff">SW1 · SERVER</text><text x="170" y="171" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#b9d5ea">Gère la base VLAN</text><text x="170" y="191" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#b9d5ea">Révision contrôlée</text><rect x="680" y="90" width="225" height="84" rx="13" fill="#183a2e" stroke="#73e0a0" stroke-width="2.5"/><text x="792" y="121" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#effff5">SW2 · CLIENT</text><text x="792" y="147" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#c2f4d5">Reçoit et synchronise</text><rect x="680" y="235" width="225" height="84" rx="13" fill="#183a2e" stroke="#73e0a0" stroke-width="2.5"/><text x="792" y="266" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#effff5">SW3 · CLIENT</text><text x="792" y="292" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#c2f4d5">Reçoit et synchronise</text><path class="vdflow" marker-end="url(#vtpDomArrow)" d="M285 144 C420 144 520 125 670 125"/><path class="vdflow" marker-end="url(#vtpDomArrow)" d="M285 180 C430 224 510 277 670 277"/><text x="465" y="115" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="700" fill="#67d9ff">Annonces VTP</text><text x="460" y="255" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#9fb4ca">Via les trunks compatibles</text><rect x="55" y="248" width="230" height="72" rx="12" fill="#202b3b" stroke="#647890" stroke-width="1.5"/><text x="170" y="277" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="700" fill="#e7eff9">Prérequis</text><text x="170" y="299" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#b7c5d8">Domaine/version cohérents</text><text x="480" y="350" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#9fb4ca">VTP gère la base VLAN ; il ne transporte pas à lui seul les données utilisateur.</text></svg></div>

Un domaine VTP ne signifie pas que tous les commutateurs doivent être interconnectés physiquement directement. Les annonces peuvent traverser une suite de trunks compatibles et d'équipements capables de les relayer. La topologie et le mode de chaque équipement déterminent la façon dont les messages se propagent.

Il faut aussi distinguer le domaine VTP d'un domaine de diffusion VLAN. Le domaine VTP sert à la gestion de la base VLAN ; le domaine de diffusion est lié à un VLAN précis et à sa continuité de couche 2. Un domaine VTP peut gérer plusieurs VLAN distincts.

### 1.5. Les modes VTP

Les modes VTP déterminent comment un commutateur gère sa base VLAN et traite les annonces reçues. Les modes disponibles et leur comportement précis dépendent de l'IOS, de l'IOS XE, du modèle de commutateur et de la version VTP.

| Mode | Créer/modifier les VLAN localement ? | Synchroniser sa base avec les annonces ? | Transmettre les annonces VTP ? |
|---|---|---|---|
| Server | Oui, selon les permissions et la version | Participe à la gestion du domaine | Oui |
| Client | Normalement non | Oui | Oui |
| Transparent | Oui, base locale indépendante | Non, il ne synchronise pas sa base à partir des annonces reçues | Souvent oui en VTP v2/v3 ; détails dépendants de la version |
| Off | Oui, selon la plateforme, base locale indépendante | Non | Non, lorsqu'un mode off est disponible |

**Mode serveur (server).** Le commutateur permet la gestion de la base VLAN et peut annoncer les changements aux autres équipements du domaine. Dans les versions historiques, plusieurs commutateurs peuvent être configurés en mode serveur. Avec VTP version 3, la fonction de serveur primaire (primary server) apporte un contrôle supplémentaire de l'autorité qui peut modifier et publier la base correspondante.

**Mode client (client).** Le commutateur reçoit les annonces et adapte sa base VLAN selon les règles VTP. Il ne permet normalement pas de créer, supprimer ou renommer localement les VLAN comme le ferait un serveur. Il est conçu pour recevoir la configuration gérée ailleurs. Le comportement de sauvegarde des informations peut varier selon la version : dans les implémentations historiques v1/v2, les VLAN ne sont généralement pas enregistrés en NVRAM comme sur un serveur ; VTPv3 modifie certains aspects de cette gestion.

**Mode transparent (transparent).** Le commutateur conserve une base VLAN locale indépendante. Il ne synchronise pas automatiquement sa propre base avec les annonces VTP qu'il reçoit. En versions 2 et 3, il peut transmettre des annonces VTP sur ses trunks sans appliquer leur contenu à sa base locale. Le comportement de relais en v1 est plus limité et doit être vérifié dans la documentation de la plateforme.

**Mode off.** Sur les plateformes qui le proposent, le mode off se comporte comme le mode transparent du point de vue de la base VLAN locale, mais ne relaie pas les annonces VTP. Il permet de désactiver explicitement la participation et le transit des messages VTP.

Le mode transparent n'est pas synonyme de port trunk transparent, et le mode client ne signifie pas qu'un commutateur ne transmet pas le trafic utilisateur. Ces modes concernent la gestion et la diffusion des informations VTP ; le transfert Ethernet continue à dépendre des VLAN, des trunks, de STP et des tables MAC.

### Vue visuelle des modes

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 370" role="img" aria-label="Comparaison des modes VTP Server, Client, Transparent et Off" width="1000" height="370" style="width:100%;height:auto;display:block"><defs><marker id="vtpModeArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker></defs><style>.vmaccent{fill:none;stroke:#67d9ff;stroke-width:3;stroke-dasharray:8 7;animation:vtpModeDash 2.4s linear infinite}@keyframes vtpModeDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.vmaccent{animation:none}}</style><rect x="12" y="12" width="976" height="346" rx="20" fill="#0b1220" stroke="#263b54" stroke-width="2"/><text x="500" y="42" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#edf5ff" text-anchor="middle">QUATRE MODES, QUATRE COMPORTEMENTS</text><rect x="35" y="70" width="220" height="225" rx="14" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="145" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#eff8ff">SERVER</text><text x="55" y="140" font-family="system-ui,sans-serif" font-size="14" fill="#d8e8f8">• Modifie la base VLAN</text><text x="55" y="166" font-family="system-ui,sans-serif" font-size="14" fill="#d8e8f8">• Publie les annonces</text><text x="55" y="192" font-family="system-ui,sans-serif" font-size="14" fill="#d8e8f8">• Contrôle de changement</text><text x="145" y="265" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#88dfff">Source de changements</text><rect x="275" y="70" width="220" height="225" rx="14" fill="#183a2e" stroke="#73e0a0" stroke-width="2"/><text x="385" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#effff5">CLIENT</text><text x="295" y="140" font-family="system-ui,sans-serif" font-size="14" fill="#d8f7e4">• Reçoit les annonces</text><text x="295" y="166" font-family="system-ui,sans-serif" font-size="14" fill="#d8f7e4">• Synchronise la base</text><text x="295" y="192" font-family="system-ui,sans-serif" font-size="14" fill="#d8f7e4">• Pas de création locale</text><text x="385" y="265" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#9eebba">Suit le domaine</text><rect x="515" y="70" width="220" height="225" rx="14" fill="#3a2c19" stroke="#f3bd66" stroke-width="2"/><text x="625" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#fff4e3">TRANSPARENT</text><text x="535" y="140" font-family="system-ui,sans-serif" font-size="14" fill="#ffebc9">• Base VLAN locale</text><text x="535" y="166" font-family="system-ui,sans-serif" font-size="14" fill="#ffebc9">• Ignore la synchronisation</text><text x="535" y="192" font-family="system-ui,sans-serif" font-size="14" fill="#ffebc9">• Peut relayer certaines annonces</text><text x="625" y="265" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#f6cf91">Relais selon version</text><rect x="755" y="70" width="210" height="225" rx="14" fill="#2a2938" stroke="#b9a3ff" stroke-width="2"/><text x="860" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#f5f0ff">OFF</text><text x="775" y="140" font-family="system-ui,sans-serif" font-size="14" fill="#e7ddff">• Base VLAN locale</text><text x="775" y="166" font-family="system-ui,sans-serif" font-size="14" fill="#e7ddff">• Ne traite pas les annonces</text><text x="775" y="192" font-family="system-ui,sans-serif" font-size="14" fill="#e7ddff">• Ne les relaie pas</text><text x="860" y="265" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#d2c5ff">Si disponible</text><path class="vmaccent" d="M55 118 L235 118"/><path class="vmaccent" d="M295 118 L475 118"/><path class="vmaccent" d="M535 118 L715 118"/><path class="vmaccent" d="M775 118 L945 118"/><text x="500" y="329" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#9fb4ca">Le mode Transparent ou Off peut être privilégié quand une propagation automatique n'est pas souhaitée.</text></svg></div>

### 1.6. Les versions de VTP

Les versions VTP ne sont pas toutes interchangeables. Les commutateurs d'un même domaine doivent employer des versions compatibles pour que les annonces soient interprétées correctement. Il ne faut donc pas activer une version sur un seul équipement sans analyser la compatibilité de tous les commutateurs concernés.

| Fonction | VTP v1 | VTP v2 | VTP v3 |
|---|---|---|---|
| Gestion de la base VLAN de plage normale | Oui | Oui | Oui |
| Propagation des VLAN étendus 1006–4094 | Non | Non | Oui, si la plateforme le prend en charge |
| Améliorations des comportements de relais et de gestion | Fonctionnalités historiques | Certaines améliorations par rapport à v1 | Fonctionnalités et contrôles supplémentaires |
| Private VLAN dans la base propagée | Non dans les versions historiques | Non dans les versions historiques | Pris en charge par les plateformes compatibles |
| Base MST propagée | Non dans le modèle historique | Non dans le modèle historique | Pris en charge par les implémentations compatibles |
| Serveur primaire pour la base VLAN | Non | Non | Oui |

VTP version 1 est la version historique. La version 2 apporte des améliorations et des différences de comportement, notamment dans le traitement des annonces par les équipements transparents. La version 3 étend les capacités, notamment avec les VLAN de plage étendue, des contrôles d'autorité plus stricts et la prise en charge d'autres bases selon la plateforme.

Sur certaines plateformes Cisco, v1 est la valeur par défaut tandis que v2 et v3 doivent être activées explicitement. Ce n'est pas une hypothèse sûre pour toutes les gammes et toutes les versions. La commande `show vtp status` doit être utilisée pour vérifier la version réellement active.

Dans les architectures modernes, VTPv3 est généralement préférable lorsqu'on souhaite employer les fonctionnalités qu'il apporte et que tous les équipements sont compatibles. Dans d'autres réseaux, les équipes choisissent de ne pas exploiter VTP et de gérer les VLAN localement en mode transparent ou off. Le bon choix dépend de l'architecture, de la compatibilité et du niveau de risque acceptable.

### 1.7. Publicités et types d'annonces VTP

VTP utilise des annonces de contrôle pour communiquer l'état de la base VLAN. Les formes exactes d'annonces dépendent de la version. Dans le fonctionnement historique, on rencontre notamment les catégories suivantes :

- **Summary Advertisement** : annonce récapitulative contenant des informations permettant d'identifier l'état du domaine et la révision de configuration ;
- **Subset Advertisement** : annonce contenant des informations détaillées sur une partie de la base VLAN ;
- **Advertisement Request** : demande d'informations permettant à un commutateur d'obtenir une base plus complète lorsqu'il en a besoin.

Ces catégories sont utiles pour comprendre le comportement d'ensemble, mais il ne faut pas supposer que chaque version implémente les mêmes détails internes ou traite chaque échange de manière identique. Les messages VTP de contrôle sont distincts des trames utilisateur transportées à travers les VLAN.

Lorsqu'un commutateur reçoit une annonce, il ne doit pas simplement recopier chaque champ sans vérification. Les informations du domaine, la version, l'authentification et la logique de révision participent à la décision. Les règles exactes dépendent de la version et du mode de fonctionnement.

Le protocole permet ainsi de faire circuler les modifications de VLAN dans le domaine. Mais l'efficacité de la propagation crée aussi un risque : une configuration incorrecte ou une source inattendue peut influencer plusieurs équipements. Un domaine VTP doit donc être traité comme une zone de gestion ayant des frontières et des règles d'administration explicites.

### 1.8. Le numéro de révision VTP

Le numéro de révision de configuration VTP est un compteur utilisé pour distinguer des états de configuration VLAN au sein du domaine. Dans les mécanismes classiques v1/v2, les commutateurs comparent notamment les informations de domaine et de révision pour déterminer si une annonce doit être utilisée pour synchroniser la base.

Une modification prise en compte dans la base VTP peut augmenter le numéro de révision. Un commutateur ajouté au réseau avec une révision supérieure à celle des équipements existants peut, dans les scénarios historiques et si les autres paramètres sont compatibles, diffuser une base qui sera considérée comme plus récente. Si cette base contient une liste VLAN erronée ou incomplète, une partie du réseau peut subir des perturbations importantes.

Exemple illustratif :

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-label="Risque de révision VTP plus élevée lors de l'ajout d'un commutateur inconnu" width="960" height="400" style="width:100%;height:auto;display:block"><defs><marker id="vtpRevArrow" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#ff7b7b"/></marker></defs><style>.vrflow{fill:none;stroke:#ff7b7b;stroke-width:4;stroke-dasharray:10 8;marker-end:url(#vtpRevArrow);animation:vtpRevDash 2.5s linear infinite}@keyframes vtpRevDash{to{stroke-dashoffset:-36}}@media(prefers-reduced-motion:reduce){.vrflow{animation:none}}</style><rect x="15" y="15" width="930" height="370" rx="20" fill="#0b1220" stroke="#3b2d3b" stroke-width="2"/><text x="480" y="47" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#fff0f0">RISQUE HISTORIQUE — VTP v1/v2</text><rect x="45" y="85" width="255" height="115" rx="14" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="172" y="116" text-anchor="middle" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#eff8ff">Réseau existant</text><text x="172" y="146" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" fill="#cfe5f8">Révision 12</text><text x="172" y="172" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#b2c5d9">VLAN 10, 20, 30, 40</text><rect x="660" y="85" width="255" height="115" rx="14" fill="#3a2028" stroke="#ff7b7b" stroke-width="2"/><text x="787" y="116" text-anchor="middle" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#fff0f0">Switch inconnu</text><text x="787" y="146" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" fill="#ffd0d0">Révision 47</text><text x="787" y="172" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#ffd0d0">VLAN 10, 99 seulement</text><path class="vrflow" marker-end="url(#vtpRevArrow)" d="M660 165 C540 225 420 225 300 165"/><rect x="260" y="246" width="440" height="68" rx="12" fill="#3a2028" stroke="#ff7b7b" stroke-width="1.8"/><text x="480" y="273" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#fff1f1">Risque : une base inattendue peut se propager</text><text x="480" y="296" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#ffd0d0">si domaine, version et paramètres sont compatibles</text><rect x="45" y="333" width="870" height="32" rx="8" fill="#162638" stroke="#3b5873"/><text x="480" y="354" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#d6e4f2">Contrôle : domaine · mode · version · authentification · révision · VLAN présents</text></svg></div>

Ce schéma montre un risque classique de révision, pas une garantie que tout commutateur à révision supérieure écrasera n'importe quelle base dans toutes les versions. VTPv3 introduit le rôle de serveur primaire et des mécanismes plus stricts pour les changements de base. Les protections et comportements dépendent de la version, du mode et de l'état du domaine.

Avant de connecter un commutateur inconnu à un domaine VTP existant, vérifie au minimum son mode, son domaine, sa version, son état d'authentification et son numéro de révision. Il ne faut jamais supposer qu'un équipement neuf possède nécessairement une révision nulle ou une base vierge.

Le numéro de révision n'est pas un numéro de VLAN ni un numéro de version logicielle. Il décrit l'état de la base dans le mécanisme de synchronisation VTP. Le remettre à zéro n'est pas une opération à effectuer sans procédure contrôlée : selon la plateforme, on peut devoir modifier le domaine ou le mode, ou réaliser une autre démarche documentée afin de neutraliser le risque avant raccordement.

### 1.9. VTPv3 et le serveur primaire

VTP version 3 fournit un mécanisme de serveur primaire pour la base concernée. Un serveur en mode serveur n'est pas forcément le serveur primaire au sens de VTPv3. L'opération de promotion en serveur primaire confère l'autorité de publier certains changements de base, notamment la base VLAN lorsqu'on sélectionne l'instance correspondante.

Le mécanisme vise à réduire le risque que plusieurs serveurs modifient indépendamment une base dans le même domaine sans contrôle de l'autorité. Dans un réseau qui utilise VTPv3, l'administrateur doit donc comprendre la différence entre mode serveur, état de serveur primaire et base de données gérée.

La commande de promotion dépend de la plateforme et peut prendre une forme proche de :

```cisco
vtp primary vlan
```

Certaines versions prévoient des options supplémentaires, une confirmation interactive ou des paramètres de forçage. Il est essentiel de consulter la documentation de la version réelle et de ne jamais utiliser une option de forçage sans comprendre les effets sur les autres serveurs.

Le rôle primaire n'élimine pas la nécessité des sauvegardes ni des processus de changement. Il renforce les contrôles au niveau du protocole, mais ne protège pas d'une personne disposant d'un accès administrateur légitime qui réalise une modification incorrecte.

### 1.10. Mot de passe et authentification VTP

Un mot de passe de domaine VTP peut être configuré pour contribuer à la vérification des annonces. Pour que la configuration fonctionne comme prévu, les commutateurs concernés doivent utiliser des paramètres d'authentification compatibles. Un mot de passe incorrect ou une configuration incohérente peut empêcher la synchronisation.

Sur Cisco IOS, la configuration historique peut ressembler à :

```cisco
vtp password MotDePasseAChanger
```

Cette ligne est un exemple syntaxique, pas un secret à réutiliser en production. Le mot de passe doit être fort, conservé dans un coffre de secrets ou une procédure de gestion autorisée, et appliqué de manière cohérente sur les équipements qui participent au domaine.

VTPv3 fournit des mécanismes d'authentification améliorés sur les plateformes compatibles, notamment des options qui évitent d'exposer le secret de la même manière que dans une configuration simpliste en clair. Les commandes et la représentation de la clé varient selon l'environnement.

Le mot de passe VTP n'est pas le mot de passe de connexion à la console, le secret enable ou la clé Wi-Fi. Il concerne le mécanisme VTP. Il ne faut pas non plus interpréter l'authentification comme une solution générale contre toutes les erreurs de VLAN : un administrateur autorisé peut encore supprimer un VLAN utile, mal configurer un trunk ou créer une erreur de conception.

### 1.11. VTP pruning

Le VTP pruning est une fonction destinée à limiter la propagation de certains trafics de diffusion, multicast et unicast inconnu sur des trunks lorsque les commutateurs en aval n'ont pas besoin de transporter le VLAN correspondant. L'objectif est de réduire le trafic inutile sur les liens inter-commutateurs.

Sans pruning, une trame de diffusion d'un VLAN peut être propagée sur des trunks où elle ne mène à aucun équipement qui utilise ce VLAN, sous réserve des règles de transfert du commutateur. Le pruning peut réduire ces transmissions lorsque les conditions de topologie le permettent.

Le pruning ne supprime pas le VLAN de la base, ne désactive pas le trunk et ne remplace pas la liste des VLAN autorisés. Il contrôle une partie du comportement de propagation du trafic sur les liens admissibles. Les VLAN réservés ou déclarés non éligibles ne sont pas nécessairement prunés ; le comportement dépend des règles de l'implémentation.

Sur de nombreuses plateformes Cisco traditionnelles, la commande d'activation globale est :

```cisco
vtp pruning
```

Dans les versions VTPv1/v2 classiques, l'activation depuis un serveur peut se propager à l'ensemble du domaine. Avec VTPv3, la procédure peut demander une configuration explicite sur les équipements concernés. Il faut vérifier la documentation et le comportement de la version utilisée.

Points importants :

- le pruning agit sur les trunks et sur les VLAN qui peuvent effectivement être prunés ;
- il ne doit pas être confondu avec `switchport trunk allowed vlan`, qui définit les VLAN autorisés sur une interface ;
- un VLAN qui doit atteindre un commutateur aval doit rester transportable et être pris en compte par la conception ;
- il faut vérifier la compatibilité si le domaine contient des équipements transparents ou des équipements de versions différentes.

Le pruning est un outil d'optimisation. Dans un petit laboratoire, il n'est pas indispensable pour apprendre à créer des VLAN et à synchroniser la base. Dans un réseau de production, il doit être activé et validé dans le cadre d'un plan d'architecture, avec des tests de connectivité avant et après le changement.

### 1.12. Plage normale et plage étendue de VLAN

Les identifiants VLAN vont généralement de 1 à 4094 dans les environnements 802.1Q, mais la manière dont ces VLAN sont gérés dépend de l'équipement et de VTP.

Historiquement, VTP v1 et v2 propagent la base des VLAN de plage normale, soit les identifiants 1 à 1005, avec des VLAN réservés selon les plateformes (les identifiants 1002 à 1005 sont traditionnellement réservés à d'anciens environnements Token Ring/FDDI). VTPv3 prend en charge la propagation des VLAN étendus, de 1006 à 4094, sur les plateformes compatibles.

Cela ne signifie pas que tous les commutateurs peuvent utiliser toutes les fonctions pour tous les identifiants. Il faut vérifier la gamme, la version logicielle, les VLAN réservés et les limites de la base. La syntaxe `vlan 2000` peut être acceptée localement sur une plateforme moderne tout en nécessitant VTPv3 si le but est de propager cette définition via VTP.

Un VLAN est dit « étendu » en raison de sa plage d'identifiants, pas parce qu'il traverse davantage de routeurs. La plage étendue ne constitue pas une méthode d'extension géographique ou d'acheminement inter-VLAN.

### 1.13. Relation entre VTP, 802.1Q et STP

Trois fonctions sont souvent confondues dans les premiers labs : VTP, trunking 802.1Q et Spanning Tree Protocol.

| Fonction | Objectif | Exemple de question à laquelle elle répond |
|---|---|---|
| VTP | Diffuser/gérer la base VLAN | Quels VLAN existent dans le domaine VTP ? |
| 802.1Q trunking | Transporter plusieurs VLAN sur une liaison | Quels VLAN peuvent emprunter ce lien et comment sont identifiées les trames ? |
| STP/RSTP/MST | Éviter les boucles de couche 2 | Quels liens doivent être bloqués ou activés pour maintenir une topologie sans boucle ? |
| Routage inter-VLAN | Permettre aux VLAN de communiquer en couche 3 | Comment le VLAN 10 atteint-il le VLAN 20 ? |

Le bon fonctionnement global requiert que ces fonctions soient cohérentes. VTP peut diffuser l'existence d'un VLAN, mais le VLAN doit encore être transporté sur les trunks appropriés. STP doit protéger la topologie et le routage doit être configuré si les sous-réseaux doivent échanger du trafic.

Une erreur fréquente consiste à supposer que la présence d'un VLAN dans `show vlan brief` signifie que les postes de ce VLAN sont joignables à travers toute l'architecture. Cette sortie indique la présence locale du VLAN, pas sa présence sur tous les commutateurs du chemin ni sa permission sur tous les trunks.

### 1.14. Cycle conceptuel de propagation d'un changement

Le fonctionnement général de VTP peut être décrit par un cycle :

1. Un administrateur crée ou modifie un VLAN sur un commutateur qui autorise ce changement.
2. La base VLAN locale est mise à jour.
3. Le mécanisme VTP met à jour les informations de révision ou d'état selon les règles de la version.
4. Le commutateur transmet les annonces appropriées à travers les trunks compatibles.
5. Les autres commutateurs du domaine valident les paramètres reçus.
6. Les équipements autorisés à synchroniser leur base appliquent le changement ; un commutateur transparent maintient sa propre base.
7. L'administrateur vérifie l'état de la base et la connectivité des VLAN concernés.

Ce cycle est volontairement simplifié : le protocole comporte des détails de formats d'annonces, d'authentification, de demandes et de transitions qui varient selon la version. Il représente toutefois le principe opérationnel qu'un administrateur doit comprendre.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 440" role="img" aria-label="Cycle de propagation d'une modification VLAN dans VTP" width="1000" height="440" style="width:100%;height:auto;display:block"><defs><marker id="vtpCycArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker><marker id="vtpCycGreen" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#73e0a0"/></marker></defs><style>.vcflow{fill:none;stroke:#67d9ff;stroke-width:3.5;stroke-dasharray:8 7;marker-end:url(#vtpCycArrow);animation:vtpCycDash 2.5s linear infinite}.vcbranch{fill:none;stroke:#73e0a0;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#vtpCycGreen);animation:vtpCycDash 2.8s linear infinite}@keyframes vtpCycDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.vcflow,.vcbranch{animation:none}}</style><rect x="12" y="12" width="976" height="416" rx="20" fill="#0b1220" stroke="#263b54" stroke-width="2"/><text x="500" y="42" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#edf5ff">CYCLE D'UNE MODIFICATION VLAN</text><rect x="35" y="76" width="200" height="72" rx="12" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="135" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#edf8ff">1. Modification</text><text x="135" y="126" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#bfdcf1">VLAN sur serveur autorisé</text><rect x="275" y="76" width="200" height="72" rx="12" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="375" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#edf8ff">2. Base mise à jour</text><text x="375" y="126" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#bfdcf1">État/révision selon version</text><rect x="515" y="76" width="200" height="72" rx="12" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="615" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#edf8ff">3. Annonce VTP</text><text x="615" y="126" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#bfdcf1">Envoi par trunk compatible</text><rect x="755" y="76" width="210" height="72" rx="12" fill="#183a2e" stroke="#73e0a0" stroke-width="2"/><text x="860" y="104" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#effff5">4. Validation</text><text x="860" y="126" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#c7f5d7">Domaine/version/auth.</text><path class="vcflow" marker-end="url(#vtpCycArrow)" d="M235 112 L267 112"/><path class="vcflow" marker-end="url(#vtpCycArrow)" d="M475 112 L507 112"/><path class="vcflow" marker-end="url(#vtpCycArrow)" d="M715 112 L747 112"/><path class="vcflow" marker-end="url(#vtpCycArrow)" d="M860 148 L860 190"/><rect x="720" y="190" width="240" height="82" rx="12" fill="#183a2e" stroke="#73e0a0" stroke-width="2"/><text x="840" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#effff5">Client VTP</text><text x="840" y="243" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#c7f5d7">Synchronise sa base</text><path class="vcflow" marker-end="url(#vtpCycArrow)" d="M720 231 L680 231"/><rect x="405" y="190" width="275" height="82" rx="12" fill="#183a2e" stroke="#73e0a0" stroke-width="2"/><text x="542" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#effff5">5. Vérification</text><text x="542" y="243" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#c7f5d7">Base, trunks, services</text><rect x="45" y="190" width="320" height="82" rx="12" fill="#3a2c19" stroke="#f3bd66" stroke-width="2"/><text x="205" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#fff4e3">Transparent</text><text x="205" y="243" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#ffebc9">Garde sa base locale indépendante</text><path class="vcbranch" marker-end="url(#vtpCycGreen)" d="M615 148 C615 172 420 170 365 218"/><rect x="45" y="322" width="910" height="74" rx="12" fill="#142638" stroke="#375471" stroke-width="1.5"/><text x="500" y="350" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="700" fill="#e6f2ff">Le succès VTP ne garantit pas à lui seul la connectivité des postes</text><text x="500" y="374" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#b8c9dc">Vérifier aussi les VLAN autorisés, les ports d'accès, STP et le routage si nécessaire.</text></svg></div>

La bonne pratique consiste à exécuter toute modification de VLAN selon une procédure contrôlée : vérifier le domaine et le mode, faire la modification, contrôler la synchronisation, puis tester les trunks et les services qui dépendent du VLAN.

> **Piège :** Un VLAN qui existe dans la base VTP n'est pas automatiquement autorisé sur tous les trunks. VTP gère la base VLAN, tandis que la liste `switchport trunk allowed vlan` détermine les VLAN admis par une interface trunk. Vérifie toujours les deux informations, ainsi que l'état opérationnel du trunk, avant de conclure qu'un VLAN est transporté de bout en bout.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-label="Différence entre la base VTP, les trunks 802.1Q, STP et le routage inter-VLAN" width="960" height="390" style="width:100%;height:auto;display:block"><defs><marker id="vtpLayArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker></defs><style>.vlaccent{fill:none;stroke:#67d9ff;stroke-width:3;stroke-dasharray:8 7;animation:vtpLayDash 2.5s linear infinite}@keyframes vtpLayDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.vlaccent{animation:none}}</style><rect x="14" y="14" width="932" height="362" rx="20" fill="#0b1220" stroke="#263b54" stroke-width="2"/><text x="480" y="43" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#edf5ff">QUATRE FONCTIONS COMPLÉMENTAIRES</text><rect x="42" y="72" width="420" height="100" rx="13" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="66" y="102" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#eff8ff">VTP</text><text x="66" y="127" font-family="system-ui,sans-serif" font-size="14" fill="#cfe5f8">Gère les définitions VLAN dans le domaine</text><text x="66" y="149" font-family="system-ui,sans-serif" font-size="13" fill="#a9c5dc">« Quels VLAN existent ? »</text><rect x="498" y="72" width="420" height="100" rx="13" fill="#183a2e" stroke="#73e0a0" stroke-width="2"/><text x="522" y="102" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#effff5">Trunk 802.1Q</text><text x="522" y="127" font-family="system-ui,sans-serif" font-size="14" fill="#d3f4df">Transporte les VLAN autorisés sur un lien</text><text x="522" y="149" font-family="system-ui,sans-serif" font-size="13" fill="#a9ddbc">« Quels VLAN passent ici ? »</text><rect x="42" y="205" width="420" height="100" rx="13" fill="#3a2c19" stroke="#f3bd66" stroke-width="2"/><text x="66" y="235" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#fff4e3">STP / RSTP</text><text x="66" y="260" font-family="system-ui,sans-serif" font-size="14" fill="#ffebc9">Prévient les boucles de couche 2</text><text x="66" y="282" font-family="system-ui,sans-serif" font-size="13" fill="#f0c77f">« Quelle topologie évite la boucle ? »</text><rect x="498" y="205" width="420" height="100" rx="13" fill="#2a2938" stroke="#b9a3ff" stroke-width="2"/><text x="522" y="235" font-family="system-ui,sans-serif" font-size="18" font-weight="700" fill="#f5f0ff">Routage inter-VLAN</text><text x="522" y="260" font-family="system-ui,sans-serif" font-size="14" fill="#e7ddff">Fait communiquer des réseaux IP distincts</text><text x="522" y="282" font-family="system-ui,sans-serif" font-size="13" fill="#d2c5ff">« Comment joindre un autre sous-réseau ? »</text><path class="vlaccent" d="M66 158 L438 158"/><path class="vlaccent" d="M522 158 L894 158"/><path class="vlaccent" d="M66 293 L438 293"/><path class="vlaccent" d="M522 293 L894 293"/><text x="480" y="343" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#aabbd0">Un VLAN peut exister dans la base sans être autorisé sur tous les trunks.</text><text x="480" y="362" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#aabbd0">Aucune de ces fonctions ne remplace les trois autres.</text></svg></div>

---

## 2. Configuration et Pratique

### 2.1. Topologie de laboratoire

Le laboratoire suivant utilise trois commutateurs Cisco IOS : SW1 joue le rôle de serveur VTP classique, SW2 et SW3 sont configurés comme clients. Tous appartiennent au domaine `CAMPUS-LAB`. Les commutateurs sont reliés entre eux par des trunks 802.1Q.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 430" role="img" aria-label="Topologie de laboratoire avec SW1 serveur VTP, SW2 et SW3 clients et postes VLAN" width="960" height="430" style="width:100%;height:auto;display:block"><defs><marker id="vtpLabArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker></defs><style>.vllink{fill:none;stroke:#67d9ff;stroke-width:4;stroke-dasharray:9 7;marker-end:url(#vtpLabArrow);animation:vtpLabDash 2.6s linear infinite}.vlaccess{fill:none;stroke:#73e0a0;stroke-width:3}@keyframes vtpLabDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.vllink{animation:none}}</style><rect x="14" y="14" width="932" height="402" rx="20" fill="#0b1220" stroke="#263b54" stroke-width="2"/><text x="480" y="42" text-anchor="middle" font-family="system-ui,sans-serif" font-size="19" font-weight="700" fill="#edf5ff">LABORATOIRE · DOMAINE CAMPUS-LAB</text><rect x="350" y="64" width="260" height="86" rx="13" fill="#173451" stroke="#67d9ff" stroke-width="2.5"/><text x="480" y="95" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#eff8ff">SW1 · VTP SERVER</text><text x="480" y="121" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#cfe5f8">VLAN 10, 20, 30</text><rect x="90" y="215" width="270" height="76" rx="13" fill="#183a2e" stroke="#73e0a0" stroke-width="2.5"/><text x="225" y="245" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#effff5">SW2 · CLIENT</text><text x="225" y="269" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#c7f5d7">Reçoit la base VLAN</text><rect x="600" y="215" width="270" height="76" rx="13" fill="#183a2e" stroke="#73e0a0" stroke-width="2.5"/><text x="735" y="245" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="#effff5">SW3 · CLIENT</text><text x="735" y="269" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#c7f5d7">Reçoit la base VLAN</text><path class="vllink" marker-end="url(#vtpLabArrow)" d="M410 150 L270 207"/><path class="vllink" marker-end="url(#vtpLabArrow)" d="M550 150 L690 207"/><text x="310" y="173" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#67d9ff">Trunk 802.1Q</text><text x="650" y="173" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#67d9ff">Trunk 802.1Q</text><path class="vlaccess" d="M225 291 L225 329 M735 291 L735 329"/><rect x="84" y="329" width="282" height="54" rx="10" fill="#202b3b" stroke="#73e0a0" stroke-width="1.5"/><text x="225" y="351" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="700" fill="#effff5">PC COMPTA · VLAN 20</text><text x="225" y="370" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#bfead0">Port access</text><rect x="594" y="329" width="282" height="54" rx="10" fill="#202b3b" stroke="#73e0a0" stroke-width="1.5"/><text x="735" y="351" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="700" fill="#effff5">PC SUPPORT · VLAN 30</text><text x="735" y="370" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#bfead0">Port access</text></svg></div>

Cette topologie est conceptuelle. Les noms et numéros d'interfaces doivent être adaptés au modèle de commutateur. Il faut définir avant le lab une version VTP compatible, un domaine identique, un mot de passe si l'authentification est utilisée et une liste cohérente de VLAN autorisés sur les trunks.

Pour une première démonstration, le VLAN 10 sera utilisé pour l'administration, le VLAN 20 pour la comptabilité et le VLAN 30 pour le support. Les VLAN doivent être créés sur SW1 dans son rôle de serveur, puis propagés aux clients.

### 2.2. Vérifications avant configuration

Avant d'activer VTP, effectue les vérifications suivantes sur chaque commutateur :

```cisco
show version
show running-config
show vlan brief
show interfaces trunk
show vtp status
```

Ces commandes servent à identifier la version logicielle, la configuration actuelle, les VLAN présents, les trunks opérationnels et l'état VTP. La sortie de `show vtp status` indique généralement des informations importantes : version VTP, nom de domaine, mode, numéro de révision, nombre de VLAN et état de pruning selon la plateforme.

Ne raccorde pas un commutateur inconnu à un domaine de production avant d'avoir vérifié son état VTP. Si ce commutateur possède déjà une base VLAN et un numéro de révision différents, son raccordement peut provoquer des effets inattendus selon la version et le mode.

Dans un laboratoire, tu peux repartir d'une configuration propre ou choisir le mode transparent/off pendant la préparation, selon ce qui est supporté. En production, il faut suivre la procédure officielle de réinitialisation et de raccordement correspondant au modèle et à l'IOS ; il ne faut pas improviser une remise à zéro en effaçant des fichiers ou des paramètres sans sauvegarde.

### 2.3. Configurer les trunks

VTP utilise les trunks pour transporter ses annonces. Un exemple de configuration statique sur SW1 vers SW2 :

```cisco
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
```

Sur SW2, l'interface opposée doit être configurée de manière compatible :

```cisco
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
```

Ces exemples correspondent à de nombreuses plateformes Catalyst où la commande `switchport mode trunk` est prise en charge. Certains modèles plus anciens nécessitent des paramètres d'encapsulation supplémentaires ; d'autres plateformes ont une syntaxe différente ou ne prennent pas en charge la négociation de la même façon. La documentation de la plateforme prévaut.

La liste `10,20,30` limite le trunk à ces VLAN dans cet exemple. Si le VLAN d'administration ou un autre VLAN nécessaire a besoin d'être transporté, il faut l'inclure explicitement. Une restriction de la liste autorisée est une mesure de conception utile, mais elle doit être cohérente avec tous les services réellement nécessaires.

Vérifie ensuite :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/1 switchport
```

La première commande montre les interfaces en trunk et les VLAN autorisés/actifs selon la sortie disponible. La deuxième donne le mode administratif et opérationnel d'une interface. Un port configuré administrativement en trunk peut ne pas fonctionner comme attendu si son état de liaison ou sa configuration distante est incorrecte.

### 2.4. Configurer SW1 en serveur VTP

Sur une plateforme compatible avec les commandes classiques :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode server
vtp version 2
! Facultatif : définir un mot de passe cohérent sur les membres du domaine
! vtp password RemplacerParUnSecretFort
end
copy running-config startup-config
```

Cette configuration définit le domaine, le mode serveur et demande l'activation de VTP version 2. Avant de choisir v2, confirme que les autres commutateurs du domaine la prennent en charge et que le comportement est approprié à l'architecture. Sur certaines plateformes, VTPv2 doit être activé explicitement ; sur d'autres, les fonctionnalités et syntaxes diffèrent.

Le domaine doit être identique sur les commutateurs qui participent à sa synchronisation. Le mot de passe, lorsqu'il est configuré, doit être compatible sur tous les équipements concernés.

La commande `copy running-config startup-config` sauvegarde la configuration en cours lorsqu'elle est nécessaire et prise en charge. La base VLAN et les paramètres VTP peuvent être conservés par des mécanismes différents selon le mode et la version ; il faut donc vérifier l'état réel plutôt que de supposer que toutes les données sont écrites dans le même fichier.

Contrôle :

```cisco
show vtp status
show vtp password
show vlan brief
```

`show vtp password` n'est pas disponible ou ne fournit pas les mêmes informations sur toutes les versions. Utilise les commandes compatibles avec la plateforme et ne révèle pas les secrets dans des captures ou des journaux non sécurisés.

### 2.5. Créer les VLAN sur le serveur

Une fois SW1 configuré et vérifié, crée les VLAN sur le serveur :

```cisco
configure terminal
vlan 10
 name ADMIN
vlan 20
 name COMPTA
vlan 30
 name SUPPORT
end
```

La création d'un VLAN et la définition de son nom modifient la base VLAN locale. Dans le fonctionnement VTP traditionnel, le serveur diffuse ensuite les informations correspondantes aux membres du domaine compatibles.

Affiche la base locale :

```cisco
show vlan brief
```

La sortie doit comporter les VLAN 10, 20 et 30 avec les noms attendus. La création de VLAN n'assigne pas automatiquement un port utilisateur. Elle crée une entrée dans la base. Pour qu'un poste utilise un VLAN, son port d'accès doit aussi être associé au bon identifiant et les trunks nécessaires doivent transporter ce VLAN.

### 2.6. Configurer SW2 et SW3 en clients

Sur SW2 :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode client
! Si un mot de passe VTP est utilisé, configurer le secret approprié
! vtp password RemplacerParUnSecretFort
end
copy running-config startup-config
```

Sur SW3, applique la même logique :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode client
! Si un mot de passe VTP est utilisé, configurer le secret approprié
! vtp password RemplacerParUnSecretFort
end
copy running-config startup-config
```

Sur de nombreuses plateformes IOS, pour VTP v1/v2, la commande qui sélectionne la version se configure en mode serveur ou transparent ; elle n’est pas répétée dans les blocs clients ci-dessous. Configure les versions selon la procédure de la plateforme et vérifie la version active avec `show vtp status`.

Les deux clients doivent être reliés par des trunks opérationnels au domaine. Une configuration locale en mode client ne suffit pas si le trunk ne transporte pas les annonces ou si le domaine et la version sont incompatibles.

Contrôle sur chaque client :

```cisco
show vtp status
show vlan brief
show interfaces trunk
```

Vérifie que le domaine est `CAMPUS-LAB`, que le mode indique `Client` et que les VLAN 10, 20 et 30 apparaissent dans la base selon le comportement de la version. Les annonces et les changements ne sont pas toujours visibles instantanément ; laisse au protocole le temps de fonctionner et contrôle l'état des liens si aucune synchronisation n'apparaît.

Ne tente pas de créer un VLAN sur un client en attendant le même comportement qu'en mode serveur. Le modèle client est conçu pour recevoir la base, pas pour être la source normale de modification.

### 2.7. Affecter des ports d'accès aux VLAN

La base VTP et l'affectation des ports sont des aspects distincts. Sur SW2, une interface vers un poste de comptabilité peut être configurée ainsi :

```cisco
interface GigabitEthernet1/0/10
 description POSTE_COMPTA
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
```

Sur une interface vers un poste du support :

```cisco
interface GigabitEthernet1/0/11
 description POSTE_SUPPORT
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown
```

`switchport mode access` fixe le rôle de port d'accès sur les plateformes qui prennent en charge cette syntaxe. `switchport access vlan 20` associe le port au VLAN 20. `spanning-tree portfast` est fréquemment utilisé sur les ports destinés aux terminaux, mais ne doit pas être appliqué sans réflexion à des liaisons entre commutateurs ou à des équipements susceptibles de créer des boucles. Certaines plateformes disposent de commandes équivalentes sous une forme différente.

Le fait que VTP ait propagé le VLAN 20 n'affecte pas automatiquement ce port : il faut toujours l'affecter explicitement. Le poste doit ensuite utiliser une configuration IP adaptée au sous-réseau lié au VLAN et une passerelle de couche 3 si la communication vers d'autres réseaux est nécessaire.

### 2.8. Vérifier la synchronisation de la base VLAN

Une vérification fiable compare plusieurs états, et pas seulement une commande unique :

```cisco
show vtp status
show vlan brief
show interfaces trunk
```

La comparaison doit porter sur :

- le nom du domaine VTP ;
- la version VTP réellement active ;
- le mode du commutateur ;
- le numéro de révision et les informations de base selon la version ;
- les VLAN attendus dans la base locale ;
- l'état des trunks et leur liste de VLAN autorisés.

Sur un client qui reçoit correctement la base, les VLAN propagés doivent apparaître conformément au fonctionnement de la version. Si le domaine est absent ou incorrect, la synchronisation peut ne pas avoir lieu. Si le trunk est en panne, les annonces ne peuvent pas suivre la liaison. Si le trunk est actif mais limite les VLAN utilisateur, le VLAN peut être connu localement sans être transporté comme attendu.

Il ne faut pas considérer le numéro de révision comme l'unique preuve d'une bonne configuration : il donne un indice sur la base et les changements VTP, mais ne prouve pas la connectivité utilisateur, la bonne affectation des ports ou l'autorisation de tous les VLAN sur les trunks.

### 2.9. Configurer le mode transparent

Le mode transparent est utile lorsqu'un commutateur doit gérer ses VLAN localement et ne pas synchroniser sa base avec la base VTP d'un autre équipement.

Exemple :

```cisco
configure terminal
vtp mode transparent
end
copy running-config startup-config
```

En mode transparent, les VLAN créés localement sont gérés par le commutateur sans être publiés comme des changements de base VTP du domaine selon le fonctionnement normal. En versions v2/v3, le commutateur peut relayer les annonces reçues sur ses trunks même s'il ne les applique pas à sa propre base. Ce comportement doit être vérifié dans la version réelle ; la version 1 présente des particularités historiques de relais.

Sur un commutateur transparent, on peut normalement créer des VLAN de manière locale :

```cisco
vlan 40
 name INVITES
```

Cela ne garantit pas que le VLAN 40 existe sur les autres commutateurs. Si le trafic du VLAN doit traverser plusieurs trunks, il faut gérer le VLAN sur les commutateurs correspondants et autoriser le VLAN sur les trunks nécessaires.

Le mode transparent constitue souvent une option prudente lorsqu'une organisation préfère gérer les bases VLAN localement. Il ne supprime toutefois pas les erreurs humaines et n'empêche pas les problèmes liés à une mauvaise liste de VLAN autorisés.

### 2.10. Mode off et différences de plateforme

Sur les équipements compatibles, le mode off permet de conserver une gestion VLAN locale tout en empêchant l'appareil de participer aux annonces VTP et de les relayer. La commande exacte peut être proche de :

```cisco
vtp mode off
```

Il ne faut pas supposer que toutes les plateformes proposent ce mode. Si la commande n'est pas disponible, il faut utiliser le mode recommandé par la documentation de l'équipement, souvent transparent lorsque l'on souhaite une base locale indépendante.

Le choix entre transparent et off dépend notamment du besoin de relayer les annonces à travers le commutateur. Un équipement en mode transparent peut servir de transit à des annonces VTP dans certaines versions ; le mode off ne les transmet pas lorsqu'il est pris en charge. Le mode off ne doit pas être confondu avec un arrêt du commutateur ni avec la désactivation de ses fonctions VLAN.

### 2.11. Activer VTP pruning

VTP pruning vise à réduire la propagation des trames de diffusion, multicast et unicast inconnues sur des trunks où certains VLAN ne sont pas nécessaires en aval.

Sur les plateformes classiques compatibles, l'activation peut ressembler à :

```cisco
configure terminal
vtp pruning
end
```

Avant toute activation, vérifie la version VTP et les conditions propres à la plateforme. Dans les versions traditionnelles v1/v2, l'activation à partir d'un serveur peut s'appliquer au domaine. Avec VTPv3, la configuration peut être gérée différemment, et les VLAN éligibles doivent être compris dans la conception.

Pour examiner l'état :

```cisco
show vtp status
show interfaces trunk
```

Le pruning est une optimisation du trafic, pas un contrôle de sécurité complet. Il ne remplace pas la sélection explicite des VLAN autorisés sur chaque trunk. Les VLAN qui ne sont pas éligibles au pruning continueront à suivre les règles propres au protocole et à la plateforme.

Dans un réseau simple, n'active pas le pruning uniquement parce que la commande existe. Identifie d'abord les VLAN réellement utilisés derrière chaque lien et réalise des tests après la modification.

### 2.12. Sauvegarder et documenter la configuration

Après les changements, sauvegarde la configuration lorsque c'est approprié :

```cisco
copy running-config startup-config
```

La sauvegarde de la configuration et la gestion de la base VLAN ne sont pas forcément une seule opération. Sur certaines plateformes Cisco, les informations VLAN sont maintenues dans un fichier de base dédié. Les comportements de stockage et de restauration varient avec le mode VTP, la version et le logiciel.

Avant une intervention, exporte la configuration, note le domaine VTP, le mode, la version et l'état de la base. Conserve également le plan des VLAN et les listes de VLAN autorisés sur les trunks. La documentation doit indiquer quel commutateur est autorisé à modifier les VLAN, quels liens transportent les annonces, et quels équipements utilisent une base locale indépendante.

Une sauvegarde doit être validée : un fichier non vérifié ou ancien ne constitue pas à lui seul un plan de restauration. Une procédure d'exploitation devrait spécifier comment vérifier le contenu de la sauvegarde et comment rétablir une base cohérente en cas d'incident.

### 2.13. Exemple récapitulatif de configuration

La configuration ci-dessous est un exemple pédagogique pour un domaine de laboratoire. Adapte les noms d'interfaces, la version VTP et les exigences de sécurité à la plateforme. Le mot de passe illustratif doit être remplacé si l'authentification est utilisée.

**SW1 — serveur :**

```cisco
hostname SW1
vtp domain CAMPUS-LAB
vtp mode server
vtp version 2
!
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
!
interface GigabitEthernet1/0/2
 description TRUNK_VERS_SW3
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
!
vlan 10
 name ADMIN
vlan 20
 name COMPTA
vlan 30
 name SUPPORT
!
end
copy running-config startup-config
```

**SW2 — client :**

La version VTP est configurée sur un équipement autorisé conformément aux règles de la plateforme ; sur de nombreuses implémentations IOS v1/v2, la commande de version se configure en mode serveur ou transparent, pas dans le bloc client. Vérifie la version active sur chaque commutateur avec `show vtp status`.

```cisco
hostname SW2
vtp domain CAMPUS-LAB
vtp mode client
!
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
!
interface GigabitEthernet1/0/10
 description POSTE_COMPTA
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
!
end
copy running-config startup-config
```

**SW3 — client :**

```cisco
hostname SW3
vtp domain CAMPUS-LAB
vtp mode client
!
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
!
interface GigabitEthernet1/0/10
 description POSTE_SUPPORT
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown
!
end
copy running-config startup-config
```

Cette configuration suppose que les interfaces existent et que le modèle accepte ces commandes. Le domaine utilise VTPv2 : configure cette version sur le serveur selon la documentation de la plateforme et vérifie qu’elle est bien active sur les clients ; ne répète pas une commande de version sur un client si l’IOS ne l’autorise pas. Elle ne configure pas les passerelles IP ni le routage inter-VLAN. Si les postes de VLAN 20 doivent communiquer avec des postes du VLAN 30, il faudra configurer une fonction de couche 3 et des politiques adaptées.

> **Astuce :** La commande `show vtp status` est la première vérification à réaliser après une modification VTP ou avant le raccordement d'un commutateur. Compare le domaine, le mode, la version et la révision. Ensuite, utilise `show vlan brief` pour la base locale et `show interfaces trunk` pour les VLAN transportés. Ces trois vérifications évitent de confondre la synchronisation VTP avec l'acheminement réel du trafic utilisateur.

---

## 3. Dépannage et Sécurité

### 3.1. Aucun VLAN ne se propage vers les clients

Commence par exécuter sur le serveur et le client :

```cisco
show vtp status
show interfaces trunk
show vlan brief
```

Compare le nom du domaine. Un client placé dans un autre domaine ne sera pas un membre correctement synchronisé du domaine prévu. Compare ensuite les versions et la compatibilité des paramètres d'authentification. Enfin, assure-toi qu'au moins un trunk opérationnel transporte les annonces entre les commutateurs.

Si tous les paramètres semblent corrects mais que la base ne se met pas à jour, examine le mode du serveur et du client, les éventuelles restrictions propres à la plateforme et les journaux. N'effectue pas une remise à zéro de la base avant d'avoir sauvegardé et compris les effets du changement.

Les commandes à comparer doivent être exécutées sur les deux côtés de la liaison. Un trunk mal configuré sur un côté peut apparaître différemment sur l'autre. Une interface administrativement définie en trunk n'est pas forcément opérationnelle si le lien physique est down ou si l'encapsulation n'est pas compatible.

### 3.2. Domaine VTP incorrect

Si `show vtp status` indique un domaine différent de celui attendu, le commutateur peut ne pas participer à la synchronisation du domaine prévu. Il faut vérifier si l'écart est intentionnel : l'équipement peut appartenir à un domaine isolé ou être configuré en transparent/off.

Ne modifie pas le domaine sur un équipement de production sans vérifier sa base VLAN, son rôle, ses trunks et son historique de révision. Le changement de domaine peut affecter la manière dont les annonces sont traitées. Une procédure doit préciser quel domaine est autorisé sur quel segment et comment les équipements sont migrés.

Avant de corriger le domaine, compare le plan de VLAN voulu aux VLAN présents localement. Sauvegarde la configuration et documente l'état VTP existant. Puis applique le changement dans une fenêtre contrôlée et vérifie que les VLAN attendus demeurent disponibles.

### 3.3. Numéro de révision inattendu

Un numéro de révision élevé n'est pas, à lui seul, une preuve de compromission ou d'erreur. Il peut refléter des modifications successives normales de la base. Cependant, lorsqu'un commutateur inconnu arrive sur le réseau, une révision inattendue doit être traitée comme un signal d'alerte.

Les procédures de prévention sont les suivantes :

1. isoler ou ne pas raccorder directement l'équipement inconnu au domaine de production ;
2. lire son mode VTP, sa version, son domaine et sa révision ;
3. comparer les VLAN présents à la base attendue ;
4. vérifier les mécanismes d'authentification et l'état du serveur primaire si VTPv3 est utilisé ;
5. appliquer la procédure de préparation et de réinitialisation validée pour le modèle, si nécessaire ;
6. raccorder l'équipement seulement après validation ;
7. surveiller la base VLAN et les trunks après intégration.

Les précautions sont particulièrement importantes dans un domaine historique v1/v2, où la logique de révision peut permettre à une base inattendue d'être considérée comme plus récente. VTPv3 fournit des contrôles plus stricts grâce à son modèle de serveur primaire, mais ne remplace pas la gestion rigoureuse des changements.

### 3.4. VLAN présent, mais trafic impossible

Si le VLAN figure dans `show vlan brief`, il faut poursuivre le diagnostic. Vérifie l'état du port d'accès, l'affectation du VLAN, les trunks et la liste des VLAN autorisés. Contrôle également STP et l'état de la liaison.

Commandes utiles :

```cisco
show vlan brief
show interfaces status
show interfaces trunk
show spanning-tree vlan 20
show mac address-table dynamic vlan 20
```

La syntaxe de la table MAC peut varier avec la plateforme. L'objectif est de vérifier si le commutateur apprend les adresses MAC sur les ports et si le VLAN est présent sur le chemin.

Si les postes sont dans le même VLAN, ils doivent pouvoir communiquer au niveau 2 lorsque la configuration IP et les liaisons fonctionnent. S'ils sont dans des VLAN différents, le trafic doit passer par une fonction de routage inter-VLAN. VTP ne réalise pas ce routage.

Si le poste ne peut pas joindre sa passerelle, examine son adressage IP, son masque, le port d'accès, la présence du VLAN sur le chemin et la configuration de la passerelle. Si la passerelle répond mais que les réseaux distants sont inaccessibles, le problème peut se trouver dans le routage ou les politiques de sécurité plutôt que dans VTP.

### 3.5. Trunk opérationnel, mais VLAN manquant

Un trunk peut être établi tout en ne transportant pas le VLAN requis. Vérifie sa liste autorisée et la présence du VLAN dans la base locale sur les commutateurs concernés.

Exemple de liste explicite :

```cisco
interface GigabitEthernet1/0/1
 switchport trunk allowed vlan 10,20,30
```

Si le VLAN 40 doit également traverser le lien, il faut l'ajouter à la liste selon la syntaxe supportée. Sur une interface déjà configurée, les commandes d'ajout et de remplacement ne sont pas équivalentes sur toutes les plateformes : une commande qui remplace la liste peut supprimer accidentellement des VLAN déjà autorisés. Vérifie la syntaxe et l'état avant toute modification.

Le VLAN doit être présent aux extrémités et sur les commutateurs intermédiaires nécessaires. Une seule liaison qui ne le transporte pas peut interrompre la continuité de couche 2. Les états opérationnels du trunk et les VLAN autorisés doivent donc être vérifiés de proche en proche.

### 3.6. Incompatibilité de version VTP

Si un domaine contient des versions différentes, le comportement dépend de la compatibilité offerte par ces versions et par les plateformes. VTP v1 et v2 ne doivent pas être considérées comme librement interchangeables dans tous les scénarios. VTPv3 ajoute ses propres fonctionnalités et exigences de déploiement.

Avant une migration, vérifie les versions prises en charge par tous les commutateurs, le type de base qui doit être propagé, l'utilisation éventuelle des VLAN étendus, et la méthode de transition recommandée par le constructeur.

Une modification de version doit être réalisée de manière coordonnée. Ne change pas un équipement isolé dans l'espoir qu'il choisira automatiquement la meilleure compatibilité. Contrôle après migration la version active, l'état du domaine, les VLAN et les trunks.

### 3.7. Risques de configuration erronée

Les risques les plus importants sont les suivants :

- une base VLAN indésirable se propage à des commutateurs qui la synchronisent ;
- des VLAN nécessaires sont supprimés ou ne sont pas créés aux endroits attendus ;
- des trunks transportent des VLAN inutiles ou omettent des VLAN nécessaires ;
- une modification non planifiée affecte plusieurs bâtiments ou sites ;
- une authentification incohérente entraîne une perte de synchronisation ;
- des VLAN de gestion ou d'administration sont mal transportés, ce qui réduit l'accès aux équipements ;
- une modification VTP est confondue avec un changement de routage, alors que le problème se situe dans la continuité de couche 2.

Pour limiter ces risques, conserve une liste de VLAN de référence, un plan d'adressage, les configurations des trunks et un inventaire des modes VTP. Toute modification de VLAN doit être approuvée, exécutée de façon contrôlée et vérifiée après propagation.

### 3.8. Bonnes pratiques de sécurité

La première règle est de ne pas activer une synchronisation centralisée sans besoin clairement défini. VTP peut simplifier l'administration, mais la centralisation augmente aussi l'impact possible d'une erreur. Certaines organisations préfèrent gérer les VLAN localement en mode transparent/off afin de mieux contrôler chaque changement, à condition de disposer d'un processus fiable de cohérence de configuration.

La deuxième règle est de limiter le nombre d'équipements autorisés à modifier la base. Avec VTPv3, la fonction de serveur primaire doit être comprise et protégée. En versions historiques, les serveurs doivent être maîtrisés et les équipements inconnus préparés avec prudence avant d'être raccordés.

La troisième règle est de sécuriser les trunks. Configure explicitement le rôle trunk sur les ports nécessaires, n'autorise que les VLAN requis et évite les trunks dynamiques ouverts sans besoin. N'expose pas des ports inutilisés à des connexions non contrôlées. Désactive ou place dans un VLAN non utilisé les interfaces inutilisées selon la politique réseau.

La quatrième règle est de protéger les comptes d'administration et les secrets. Un mot de passe VTP ne remplace pas la protection du plan d'administration ni l'authentification des sessions de gestion. Les identifiants doivent être forts et conservés dans un système adapté.

Enfin, surveille les événements et sauvegarde les configurations. Une variation de base VLAN, une disparition simultanée de nombreux VLAN ou un changement inattendu du numéro de révision doit déclencher une vérification rapide.

### 3.9. Danger : une base erronée peut affecter plusieurs commutateurs

> **Danger :** Le principal risque opérationnel de VTP est la propagation d'une base VLAN incorrecte à plusieurs commutateurs du domaine. Dans les scénarios historiques v1/v2, un commutateur raccordé avec une base et une révision inattendues peut entraîner une synchronisation non souhaitée si les autres paramètres sont compatibles. Les VLAN utilisés par les postes peuvent alors disparaître ou être remplacés, provoquant des interruptions étendues. VTPv3 améliore le contrôle des modifications avec le mécanisme de serveur primaire, mais aucune version ne rend les changements non planifiés sans danger.
>
> Ne connecte jamais un commutateur inconnu à un domaine de production sans inspecter son état VTP. Vérifie le domaine, le mode, la version, la révision, les VLAN présents et l'authentification. Sauvegarde la configuration, respecte la procédure de préparation du constructeur et confirme après raccordement que les VLAN attendus sont toujours disponibles.

### 3.10. Liste de vérification pour une modification VLAN

Avant la modification :

- identifier le commutateur et le mode VTP ;
- vérifier la version, le domaine et l'état de révision ;
- sauvegarder la configuration et la base attendue ;
- confirmer les trunks et les VLAN qui doivent traverser les liens ;
- déterminer les ports d'accès et services impactés ;
- prévoir un test et une méthode de retour arrière.

Pendant la modification :

- utiliser le commutateur autorisé à changer la base ;
- créer ou modifier le VLAN avec un nom documenté ;
- vérifier les annonces et la synchronisation ;
- ne pas réaliser d'autres changements de couche 2 sans rapport dans la même étape.

Après la modification :

- vérifier la base locale sur les commutateurs concernés ;
- vérifier les trunks, la liste des VLAN autorisés et STP ;
- tester la connectivité des terminaux et des passerelles ;
- comparer les résultats avec le plan de VLAN ;
- documenter le changement et conserver la sortie des commandes utiles.

### Schéma de dépannage rapide

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" role="img" aria-label="Arbre de dépannage lorsqu'un VLAN ne se propage pas ou ne communique pas" width="960" height="440" style="width:100%;height:auto;display:block"><defs><marker id="vtpDiagArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker></defs><style>.vdgflow{fill:none;stroke:#67d9ff;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#vtpDiagArrow);animation:vtpDiagDash 2.4s linear infinite}@keyframes vtpDiagDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.vdgflow{animation:none}}</style><rect x="14" y="14" width="932" height="412" rx="20" fill="#0b1220" stroke="#263b54" stroke-width="2"/><rect x="245" y="38" width="470" height="58" rx="12" fill="#173451" stroke="#67d9ff" stroke-width="2"/><text x="480" y="62" text-anchor="middle" font-family="system-ui,sans-serif" font-size="17" font-weight="700" fill="#eff8ff">Problème : VLAN absent ou trafic bloqué</text><text x="480" y="82" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#cfe5f8">Commencer par localiser la couche en défaut</text><path class="vdgflow" marker-end="url(#vtpDiagArrow)" d="M480 96 L480 119"/><rect x="255" y="119" width="450" height="60" rx="12" fill="#162638" stroke="#54708c" stroke-width="1.8"/><text x="480" y="144" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#eaf3ff">1. VTP synchronise-t-il la base ?</text><text x="480" y="164" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#b8c9dc">Domaine · mode · version · authentification · révision</text><path class="vdgflow" marker-end="url(#vtpDiagArrow)" d="M360 179 L250 211"/><path class="vdgflow" marker-end="url(#vtpDiagArrow)" d="M600 179 L710 211"/><rect x="35" y="211" width="390" height="70" rx="12" fill="#3a2028" stroke="#ff7b7b" stroke-width="1.8"/><text x="230" y="238" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#fff0f0">Non : corriger le contrôle VTP</text><text x="230" y="260" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#ffd0d0">Ne pas modifier la base au hasard</text><rect x="535" y="211" width="390" height="70" rx="12" fill="#183a2e" stroke="#73e0a0" stroke-width="1.8"/><text x="730" y="238" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#effff5">Oui : vérifier le chemin L2</text><text x="730" y="260" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#c7f5d7">VLAN autorisé · trunk opérationnel · STP</text><path class="vdgflow" marker-end="url(#vtpDiagArrow)" d="M730 281 L730 307"/><rect x="535" y="307" width="390" height="70" rx="12" fill="#2a2938" stroke="#b9a3ff" stroke-width="1.8"/><text x="730" y="334" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="#f5f0ff">Puis vérifier les ports terminaux</text><text x="730" y="356" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#d2c5ff">Port access · VLAN affecté · adressage IP</text><text x="480" y="405" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#9fb4ca">Ne pas conclure à une panne VTP avant d'avoir vérifié les trunks et la configuration du port.</text></svg></div>

### 3.11. Commandes de référence

| Commande | Utilité principale |
|---|---|
| `show vtp status` | Domaine, mode, version, révision et état VTP selon la plateforme |
| `show vtp password` | Contrôle de la configuration du mot de passe lorsque la commande est disponible |
| `show vlan brief` | Vérifier la base VLAN locale et l'affectation des ports |
| `show interfaces trunk` | Vérifier les trunks et leurs VLAN autorisés/actifs |
| `show interfaces status` | Contrôler l'état des ports |
| `show spanning-tree vlan 20` | Examiner STP pour un VLAN précis |
| `show running-config` | Inspecter la configuration active |
| `show logging` | Rechercher des événements enregistrés |
| `copy running-config startup-config` | Sauvegarder la configuration active dans la configuration de démarrage |

Les schémas animés utilisent des traits en mouvement directement sur les chemins de flux (sans particules mobiles détachées) et respectent `prefers-reduced-motion`. Les commandes et sorties exactes dépendent de la plateforme. Si une commande n'est pas prise en charge, recherche la variante documentée pour le modèle concerné au lieu de conclure que la fonction n'existe pas.

### 3.12. Sources techniques de référence

Pour approfondir la configuration réelle, consulte la documentation officielle qui correspond à la gamme et à la version logicielle du commutateur :

- Cisco, *VLAN Configuration Guide — Configure VTP* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html
- Cisco, *Configuring VTP* pour les Catalyst 3650 : https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3650/software/release/3se/vlan/configuration_guide/b_vlan_3se_3650_cg/b_vlan_3se_3650_cg_chapter_010.html
- IEEE, *IEEE 802.1Q — Bridges and Bridged Networks*, pour les principes de VLAN et de pontage Ethernet : https://standards.ieee.org/standard/802_1Q-2022.html

Ces références permettent de vérifier les différences de syntaxe, les limites de la plateforme, les fonctionnalités prises en charge et les procédures de changement. Les exemples de ce cours sont pédagogiques ; la documentation de la version utilisée constitue la référence pour un déploiement réel.

## Points à retenir

- **VTP gère la propagation d'informations VLAN, pas le transport complet du trafic utilisateur.** Il faut aussi configurer les trunks, les listes de VLAN autorisés, les ports d'accès, STP et le routage inter-VLAN lorsque nécessaire.
- **Le domaine, la version, le mode et le numéro de révision sont des paramètres critiques.** Avant d'intégrer un commutateur ou de modifier VTP, inspecte son état, sauvegarde la configuration et vérifie la compatibilité des équipements.
- **La centralisation simplifie l'administration, mais augmente l'impact potentiel d'une erreur.** Utilise des modes adaptés, limite les équipements qui modifient la base, contrôle les annonces et vérifie systématiquement la connectivité après chaque changement de VLAN.
