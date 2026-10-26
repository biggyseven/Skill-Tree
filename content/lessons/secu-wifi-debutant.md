# Sécurité Wi-Fi

> **Encadré de mise en contexte**
>
> Tu es technicien réseau dans une entreprise qui utilise une plateforme de formation en ligne. Les apprenants se connectent depuis une salle équipée de points d'accès Wi-Fi, les formateurs utilisent des ordinateurs portables et les administrateurs gèrent les serveurs depuis un réseau réservé.
>
> Un matin, plusieurs employés se connectent à un réseau sans fil dont le nom ressemble à celui de l'entreprise. La connexion fonctionne, mais certains utilisateurs sont redirigés vers une page qui leur demande de saisir de nouveau leurs identifiants. En parallèle, un appareil inconnu apparaît dans la liste des équipements connectés. Les techniciens découvrent également que le mot de passe d'administration du routeur n'a jamais été modifié depuis son installation.
>
> Dans une autre situation, des visiteurs utilisent le même réseau que les formateurs. Un appareil invité peut communiquer directement avec une imprimante interne et essayer d'atteindre d'autres équipements. Le Wi-Fi fonctionne normalement, mais la séparation entre les utilisateurs n'est pas suffisante.
>
> Ces situations rappellent qu'un réseau sans fil ne se sécurise pas uniquement avec un mot de passe. Il faut choisir un mécanisme de protection adapté, sécuriser les équipements réseau, distinguer les profils d'utilisateurs, surveiller les accès et vérifier que les appareils connectés ne disposent que des communications nécessaires.
>
> Dans ce cours, tu vas apprendre à sécuriser un réseau Wi-Fi domestique ou professionnel, à comprendre les différences entre WPA2 et WPA3, à reconnaître les principaux risques sans fil, à configurer une architecture simple et à réaliser des vérifications dans un environnement que tu es autorisé à administrer.

## 1. Objectifs du cours

À la fin de ce cours, tu devras être capable de :

- expliquer le fonctionnement général d'un réseau Wi-Fi ;
- distinguer un point d'accès, un routeur, un SSID et un client sans fil ;
- comprendre les risques spécifiques aux communications radio ;
- différencier WEP, WPA, WPA2 et WPA3 ;
- choisir un mode de sécurité adapté aux appareils et à l'organisation ;
- distinguer WPA-Personal de WPA-Enterprise ;
- comprendre le rôle d'un serveur RADIUS et d'IEEE 802.1X dans une architecture d'entreprise ;
- sécuriser l'administration du point d'accès et du routeur ;
- configurer une séparation entre réseau principal, réseau invité et équipements connectés ;
- reconnaître les faux points d'accès, les réseaux usurpés et les risques liés aux réseaux publics ;
- comprendre pourquoi masquer le SSID et filtrer les adresses MAC ne remplacent pas un mécanisme cryptographique robuste ;
- appliquer une méthode de diagnostic Wi-Fi sous Windows et Linux ;
- établir une procédure simple de maintenance et de réponse à un incident sans fil ;
- concevoir un plan de sécurisation adapté à une petite entreprise.

Ce cours reste au niveau débutant : il présente les mécanismes, les choix d'architecture et les vérifications pratiques sans demander de perturber un réseau réel ni de tenter d'accéder à un réseau sans autorisation.

## 2. Comprendre le Wi-Fi

### 2.1. Qu'est-ce que le Wi-Fi ?

Le Wi-Fi permet à des appareils de communiquer par radio au sein d'un réseau local sans utiliser un câble Ethernet pour chaque liaison. Un ordinateur portable peut ainsi accéder à une application interne, à une imprimante ou à Internet depuis une salle de formation.

Les équipements échangent des trames radio selon les mécanismes de la famille de standards IEEE 802.11. La portée dépend notamment de la puissance, des antennes, de l'environnement, de la bande de fréquences et des obstacles.

La communication sans fil apporte de la mobilité, mais elle impose un défi particulier : le signal radio peut dépasser les limites physiques d'une pièce ou d'un bâtiment. Une personne située à proximité peut détecter la présence d'un réseau même si elle n'est pas autorisée à l'utiliser.

C'est pourquoi il faut contrôler l'accès au réseau et protéger les échanges, plutôt que compter sur le fait que le signal ne serait pas visible depuis l'extérieur.

### 2.2. Les composants d'un réseau Wi-Fi

Les principaux composants sont :

**Le client sans fil.** C'est l'appareil qui se connecte : ordinateur, téléphone, tablette ou équipement connecté.

**Le point d'accès, ou AP.** Il fournit l'accès radio au réseau local. Il associe les clients sans fil au réseau selon le mode de sécurité configuré.

**Le routeur.** Il achemine des paquets entre différents réseaux. Dans un petit réseau, le routeur peut intégrer le point d'accès, le serveur DHCP, le pare-feu et d'autres fonctions.

**Le commutateur.** Il relie généralement les équipements filaires et peut transporter le trafic des points d'accès, parfois avec des VLAN pour séparer les réseaux.

**Le serveur DHCP.** Il attribue notamment des adresses IP et d'autres paramètres réseau aux clients.

**Le serveur DNS.** Il permet de résoudre des noms tels que `formation.example` en adresses IP, selon l'architecture utilisée.

**Le serveur d'authentification.** Dans certaines architectures professionnelles, il participe à la vérification de l'identité des utilisateurs ou des appareils, par exemple au moyen de RADIUS et d'IEEE 802.1X.

Un appareil appelé « routeur Wi-Fi » peut intégrer plusieurs de ces fonctions dans un même boîtier. Il reste important de distinguer leurs rôles pour diagnostiquer les problèmes et configurer les protections au bon endroit.

### 2.3. Point d'accès et routeur : ne pas les confondre

Un point d'accès fournit la connectivité Wi-Fi vers un réseau local. Un routeur assure l'acheminement entre réseaux. Les deux peuvent être intégrés à un même appareil domestique.

Une configuration sans fil peut donc être correcte sur le point d'accès, tandis que le routeur autorise trop de communications entre le réseau invité et le réseau interne. À l'inverse, un bon filtrage IP ne compense pas un mécanisme d'authentification Wi-Fi faible.

La sécurité doit couvrir les équipements et les fonctions qui composent le chemin complet de la communication.

### 2.4. Qu'est-ce qu'un SSID ?

Le SSID est le nom logique utilisé pour identifier un réseau Wi-Fi. Par exemple, une entreprise peut utiliser le nom `NovaLearn-Staff` pour le réseau du personnel et `NovaLearn-Guest` pour les visiteurs.

Un SSID n'est pas une preuve d'identité. Un attaquant peut créer un réseau portant un nom identique ou très similaire à celui d'un réseau légitime. Le client doit donc utiliser les mécanismes de sécurité et les paramètres de confiance appropriés, pas seulement reconnaître le nom affiché.

### 2.5. Un réseau visible n'est pas forcément ouvert

Voir un nom de réseau ne signifie pas que l'on peut s'y connecter librement. Le SSID peut être annoncé alors que le réseau exige une authentification et un chiffrement.

À l'inverse, un nom de réseau qui n'est pas annoncé visiblement ne garantit pas que le réseau est sécurisé. L'identité du réseau, l'authentification et la protection des données sont des questions différentes.

### 2.6. Les bandes de fréquences

Les réseaux Wi-Fi peuvent utiliser plusieurs bandes, notamment 2,4 GHz, 5 GHz et, avec les équipements compatibles, 6 GHz.

La bande 2,4 GHz peut offrir une portée utile, mais elle est souvent davantage encombrée et possède moins de canaux non chevauchants selon le domaine réglementaire. Les bandes 5 GHz et 6 GHz peuvent offrir davantage de capacité ou de canaux disponibles, mais leur portée et leur propagation dépendent des conditions radio et des règles applicables.

Le choix de la bande influence surtout la couverture, les performances et l'interférence. **La bande ou la génération Wi-Fi ne remplace pas le choix d'un mécanisme de sécurité approprié.** Un équipement récent peut rester mal sécurisé si son mot de passe d'administration, son mode d'authentification ou ses règles d'accès sont faibles.

## 3. Pourquoi le Wi-Fi présente-t-il des risques particuliers ?

### 3.1. Le signal dépasse parfois les locaux

Un réseau filaire exige généralement un accès physique au câblage ou à un port de réseau. Le Wi-Fi transmet par radio : le signal peut être détecté depuis le couloir, un parking ou un bâtiment voisin.

Cela ne signifie pas que chaque personne qui capte le signal peut lire les échanges. Le chiffrement protège les communications selon le protocole utilisé. Mais l'organisation doit supposer qu'un attaquant peut être à portée radio et concevoir ses contrôles en conséquence.

### 3.2. Interception et écoute

Sur un réseau correctement protégé, les échanges sans fil sont chiffrés selon le mécanisme et les clés utilisés. Sur un réseau ouvert ou mal configuré, les protections au niveau du Wi-Fi peuvent être insuffisantes.

Même lorsque le Wi-Fi est chiffré, les utilisateurs doivent continuer à utiliser HTTPS et les protocoles sécurisés. Le chiffrement Wi-Fi protège une partie du trajet, entre le client et le point d'accès ; HTTPS protège la communication entre le navigateur et le serveur Web selon le protocole TLS.

Ces mécanismes sont complémentaires. Il ne faut pas penser que le chiffrement du Wi-Fi permet de se passer des protections des applications.

### 3.3. Usurpation de réseau

Un attaquant peut créer un point d'accès qui imite le nom d'un réseau légitime. Cette technique est souvent appelée *faux point d'accès* ou *evil twin*.

Un utilisateur qui choisit le mauvais réseau peut être exposé à des tentatives de phishing, à des pages de connexion frauduleuses ou à des communications observables lorsque les applications ne sont pas correctement protégées.

Le risque est particulièrement important lorsqu'un appareil se connecte automatiquement à des réseaux mémorisés. Il est donc utile de désactiver l'auto-connexion aux réseaux publics qui ne sont pas nécessaires et de retirer les profils Wi-Fi devenus inutiles.

### 3.4. Faux portails captifs

Certains réseaux publics utilisent un portail captif qui demande d'accepter des conditions ou de s'authentifier avant de fournir l'accès à Internet.

Un attaquant peut imiter ce portail pour demander des informations qu'il ne devrait pas collecter. Il faut vérifier le contexte du réseau et éviter de saisir le mot de passe de son compte professionnel dans une page inattendue.

Un portail captif ne constitue pas, à lui seul, une méthode de chiffrement du Wi-Fi. Il contrôle généralement une étape d'accès au service ; il ne doit pas être confondu avec WPA2 ou WPA3.

### 3.5. Points d'accès non autorisés

Un employé peut installer un point d'accès personnel pour améliorer la couverture ou connecter des équipements. Ce point d'accès peut être mal configuré et permettre à des appareils non approuvés d'accéder au réseau interne.

Un point d'accès non autorisé crée également une architecture sans documentation : personne ne sait nécessairement qui l'administre, quels correctifs il reçoit, quels clients y sont connectés ni comment ses règles sont contrôlées.

Il faut encadrer l'installation de matériel Wi-Fi et maintenir un inventaire des points d'accès approuvés.

### 3.6. Perturbations et disponibilité

Le Wi-Fi partage un support radio. Des interférences, des équipements défectueux, une mauvaise planification des canaux ou des perturbations intentionnelles peuvent rendre la connexion instable.

Une attaque par brouillage vise à perturber la communication radio et peut affecter la disponibilité. Les mesures cryptographiques n'empêchent pas nécessairement une perturbation physique du signal.

Pour une activité critique, il est donc important de conserver une solution alternative lorsque c'est possible, par exemple des connexions filaires pour certains équipements et services essentiels.

### 3.7. Le déplacement latéral

Un appareil invité connecté au même réseau logique que les postes du personnel peut tenter de communiquer avec eux. Si les appareils internes possèdent des services vulnérables ou des permissions excessives, le risque peut dépasser le simple accès à Internet.

La séparation des réseaux, le filtrage entre segments et les pare-feu des terminaux réduisent ce risque. Un réseau invité correctement conçu devrait normalement être incapable d'accéder directement aux serveurs internes, sauf exception documentée.

## 4. Les générations de sécurité Wi-Fi

### 4.1. WEP : une technologie obsolète

WEP est un ancien mécanisme de sécurité sans fil. Ses faiblesses cryptographiques sont connues et permettent de retrouver les clés dans des conditions qui ne sont plus acceptables pour protéger un réseau moderne.

Il ne faut pas utiliser WEP pour un nouveau réseau ni considérer qu'un mot de passe complexe rend WEP sûr. Une faiblesse du protocole ne se répare pas en ajoutant des caractères au mot de passe.

Si un équipement ne prend en charge que WEP ou d'anciens modes de sécurité, il faut envisager son remplacement plutôt que continuer à l'utiliser pour transporter des données sensibles.

### 4.2. WPA : une transition historique

WPA a été introduit comme amélioration par rapport à WEP, mais les anciennes variantes et certains mécanismes associés ne constituent plus un bon choix pour une nouvelle installation.

En pratique, il faut éviter les modes de sécurité anciens qui ne fournissent pas les protections modernes attendues.

### 4.3. WPA2

WPA2 a apporté une sécurité nettement plus robuste que WEP et les anciennes variantes WPA, en s'appuyant notamment sur des mécanismes de chiffrement modernes tels qu'AES-CCMP.

WPA2 peut encore être nécessaire pour la compatibilité avec certains appareils. Toutefois, il faut le configurer avec un mode adapté, protéger les secrets, mettre à jour les équipements et vérifier les autres paramètres de sécurité.

Il ne faut pas confondre WPA2-AES avec les anciennes configurations qui utilisent TKIP. Les options héritées doivent être évitées lorsque l'objectif est une configuration moderne et sûre.

### 4.4. WPA3

WPA3 est la génération plus récente de protection Wi-Fi. Le choix précis du mode dépend du type de réseau, des appareils et des exigences de l'organisation.

Pour un réseau personnel, WPA3-Personal utilise notamment SAE (*Simultaneous Authentication of Equals*) à la place du modèle de clé partagée préalablement utilisé par WPA2-Personal. WPA3 ajoute des améliorations de sécurité et vise à renforcer la protection de l'authentification, mais ne rend pas toute configuration automatiquement sûre.

Pour un réseau d'entreprise, WPA3-Enterprise s'intègre à un modèle d'authentification d'entreprise. Il ne remplace pas les exigences de gestion des identités, de validation des certificats ou de segmentation.

### 4.5. Quel mode faut-il préférer ?

Dans une nouvelle installation, privilégie le mode le plus robuste pris en charge par les points d'accès et tous les clients nécessaires, généralement WPA3 dans les environnements compatibles.

Si certains appareils ne prennent pas en charge WPA3, évalue les conséquences et les possibilités de remplacement. Un mode de transition peut aider à gérer la compatibilité, mais il maintient des comportements hérités et doit être considéré comme un choix temporaire ou justifié, plutôt que comme une option à activer sans analyse.

Si WPA3 n'est pas disponible, WPA2-Personal correctement configuré avec un chiffrement moderne et une phrase secrète robuste reste préférable aux protocoles obsolètes. La politique exacte doit tenir compte des contraintes du matériel.

### 4.6. Tableau de synthèse

| Technologie | Évaluation générale | Décision pratique |
|---|---|---|
| WEP | Obsolète et vulnérable | Ne pas utiliser |
| WPA avec anciens mécanismes | Hérité | Éviter pour de nouvelles installations |
| WPA2 avec AES-CCMP | Encore utilisé selon le contexte et les exigences | Option de compatibilité correctement configurée |
| WPA3-Personal | Protection personnelle plus récente | À privilégier avec les appareils compatibles |
| WPA2/WPA3-Enterprise avec 802.1X | Authentification professionnelle par utilisateur ou appareil selon la configuration | Choisir selon les capacités et la politique |
| Réseau ouvert | Pas de protection Wi-Fi par clé de réseau | Éviter pour les données sensibles ; segmenter et protéger les applications |

Ces catégories ne constituent pas à elles seules une évaluation complète. Il faut aussi considérer le micrologiciel, la configuration d'administration, les règles de réseau et la gestion des clients.

## 5. WPA-Personal et WPA-Enterprise

### 5.1. WPA-Personal

Un réseau personnel utilise généralement une phrase secrète partagée par les appareils autorisés. Le modèle est pratique pour une maison, un petit atelier ou un réseau simple.

Le secret doit être unique et robuste. Si tous les utilisateurs partagent la même phrase secrète, il peut être difficile de retirer l'accès à une seule personne sans modifier le mot de passe sur tous les appareils.

Le réseau personnel convient surtout aux environnements où l'on peut gérer directement les utilisateurs et leurs appareils.

### 5.2. WPA-Enterprise

Les réseaux d'entreprise utilisent souvent IEEE 802.1X avec un service d'authentification tel que RADIUS. Les utilisateurs ou les appareils sont authentifiés selon une méthode EAP, et l'accès est établi en fonction des politiques.

Cela permet notamment d'attribuer des identifiants individuels plutôt qu'une phrase secrète partagée par toute l'organisation. Lorsqu'un employé quitte l'entreprise, son compte peut être désactivé sans nécessairement changer la configuration Wi-Fi de chaque utilisateur.

La sécurité réelle dépend toutefois du choix EAP, des certificats, de la configuration du serveur, des politiques d'accès et des contrôles appliqués sur le réseau.

### 5.3. Le rôle de 802.1X

IEEE 802.1X fournit un cadre de contrôle d'accès basé sur l'authentification. Il est utilisé avec des méthodes EAP appropriées pour vérifier un utilisateur ou un appareil avant d'autoriser l'accès au réseau.

Dans une architecture typique, on retrouve :
- le **supplicant**, composant client qui demande l'accès ;
- l'**authenticator**, souvent le point d'accès ou le commutateur qui contrôle le passage du trafic ;
- le **serveur d'authentification**, par exemple RADIUS, qui applique les règles et vérifie les informations nécessaires.

Schéma conceptuel :

    Ordinateur client
       Supplicant
           |
           v
    Point d'accès Wi-Fi
       Authenticator
           |
           v
    Serveur RADIUS
    Authentification et politique
           |
           v
    Accès accordé ou refusé

Les noms décrivent des rôles logiques. Selon le matériel et l'architecture, plusieurs fonctions peuvent être intégrées ou administrées par un service centralisé.

### 5.4. Le rôle de RADIUS

RADIUS est un protocole couramment utilisé pour centraliser l'authentification, l'autorisation et, selon l'architecture, la comptabilisation des accès réseau.

Dans une entreprise, le point d'accès peut transmettre les échanges d'authentification au serveur RADIUS. Ce serveur applique la politique définie : quel compte est valide, quelle méthode est autorisée et quel accès doit être accordé.

L'organisation doit protéger le serveur, ses secrets partagés avec les équipements, ses certificats et ses journaux. Un serveur RADIUS mal configuré peut devenir un point faible important.

### 5.5. Certificats et validation du serveur

Certaines méthodes EAP s'appuient sur des certificats pour authentifier le serveur et parfois le client. La validation du certificat serveur est essentielle : si le client accepte aveuglément un serveur inconnu, un faux réseau peut tenter de lui présenter un serveur d'authentification frauduleux et collecter certaines informations.

Les appareils doivent être configurés avec le nom attendu du serveur ou les autorités de certification de confiance selon les capacités de la solution. Il ne faut pas désactiver la validation des certificats simplement parce que la connexion ne fonctionne pas.

Pour les réseaux d'entreprise, EAP-TLS est souvent un choix robuste lorsqu'une infrastructure de certificats est disponible et correctement gérée. Le choix doit tenir compte des capacités client, du cycle de vie des certificats et de l'organisation des identités.

### 5.6. Quand utiliser chaque approche ?

Une maison ou une petite structure avec peu d'appareils peut utiliser WPA3-Personal avec une phrase secrète robuste, un mot de passe administrateur distinct et un réseau invité séparé.

Une entreprise disposant de nombreux employés, de départs fréquents ou de ressources sensibles peut bénéficier d'un réseau Enterprise avec 802.1X/RADIUS, des identités individuelles et une procédure de retrait d'accès.

La complexité doit rester justifiée : une architecture Enterprise mal maintenue peut créer de nouveaux problèmes. Il faut prévoir la gestion du serveur d'authentification, des certificats, des comptes, des journaux et du support aux utilisateurs.

## 6. Sécuriser le point d'accès et le routeur

### 6.1. Le mot de passe Wi-Fi n'est pas le mot de passe d'administration

Il faut distinguer deux secrets :

**Le secret du réseau Wi-Fi** permet à un client de rejoindre le réseau lorsque le mode utilise une phrase secrète partagée.

**Le secret d'administration du routeur ou du point d'accès** permet de modifier la configuration, les réseaux, les règles et parfois les mises à jour.

Si quelqu'un obtient les droits d'administration de l'équipement, il peut modifier les paramètres et affaiblir les autres protections. Le mot de passe d'administration doit être unique, robuste et distinct du secret Wi-Fi.

### 6.2. Modifier les identifiants par défaut

Les équipements peuvent être livrés avec des identifiants ou des paramètres par défaut. Ils ne doivent pas rester en place si l'organisation peut les modifier.

Utilise un secret d'administration unique et un mécanisme de stockage adapté. Si l'appareil prend en charge plusieurs comptes d'administration, limite les comptes et les permissions selon le besoin.

Il faut également désactiver ou retirer les comptes inutilisés quand la plateforme le permet.

### 6.3. Mettre à jour le micrologiciel

Le micrologiciel, ou firmware, est le logiciel bas niveau qui fait fonctionner l'équipement. Des mises à jour peuvent corriger des vulnérabilités et des défauts de fonctionnement.

Une procédure de maintenance doit identifier le modèle et la version, vérifier les mises à jour du fabricant ou du fournisseur, appliquer les correctifs selon le processus prévu puis vérifier le fonctionnement.

Un routeur dont le fabricant ne fournit plus de correctifs doit faire l'objet d'une migration planifiée, surtout s'il protège un réseau professionnel ou des données sensibles.

### 6.4. Réduire l'administration distante

L'administration du routeur ne devrait pas être exposée directement à Internet par défaut. Désactive la gestion distante si elle n'est pas nécessaire. Si elle est nécessaire, restreins son accès à des sources ou à un chemin d'administration approuvé, utilise un mécanisme sécurisé et surveille les connexions.

Un accès d'administration depuis le réseau invité est également à éviter. Les administrateurs devraient accéder aux interfaces de gestion depuis une zone adaptée, avec des comptes distincts et des protections fortes.

### 6.5. Désactiver les fonctions inutiles

Des fonctions telles que WPS, UPnP ou l'administration distante peuvent être utiles dans certains contextes, mais elles élargissent la surface d'exposition et doivent être évaluées.

WPS vise à simplifier l'association des appareils. S'il n'est pas nécessaire, désactive-le selon la documentation du fabricant.

UPnP permet à des appareils et applications de demander certaines ouvertures ou configurations automatiques. Son activation peut être inappropriée dans un réseau professionnel ; il faut l'évaluer et le désactiver lorsque les besoins ne le justifient pas.

Ne désactive pas une fonction sans vérifier les dépendances. La décision doit se fonder sur une analyse et une politique documentée.

### 6.6. Sauvegarder la configuration

Un routeur ou un contrôleur Wi-Fi peut contenir des informations critiques : SSID, paramètres d'authentification, VLAN, politiques, paramètres radio et comptes.

Conserve une sauvegarde de configuration dans un emplacement protégé. La configuration peut contenir des secrets ou des informations sensibles ; elle doit donc être restreinte et protégée lorsqu'elle est stockée ou transférée.

La sauvegarde doit être associée à une procédure de restauration testée. Une copie jamais vérifiée peut s'avérer inutilisable lors d'une panne.

### 6.7. Documenter les changements

La documentation doit inclure le rôle de l'équipement, son modèle et sa version, les SSID, les modes de sécurité, les réseaux associés, les règles de segmentation et les comptes administratifs autorisés.

Toute modification importante devrait indiquer qui l'a réalisée, pourquoi, quand elle a été effectuée et comment le résultat a été vérifié. Une configuration approuvée facilite le diagnostic et permet de détecter les changements inattendus.

## 7. Séparer le réseau principal du réseau invité

### 7.1. Pourquoi un réseau invité ?

Les visiteurs ont souvent besoin d'accéder à Internet, mais pas aux postes internes, aux serveurs, aux imprimantes ou aux interfaces d'administration.

Un réseau invité permet de séparer ces besoins. Un visiteur peut accéder à Internet sans recevoir automatiquement les mêmes privilèges qu'un employé.

La séparation doit être réelle : une différence de SSID n'est pas suffisante si les deux noms conduisent au même réseau sans filtrage.

### 7.2. Exemple d'architecture

    Internet
       |
       v
    Routeur / pare-feu
       |
       +------------------+
       |                  |
       v                  v
    VLAN personnel     VLAN invités
       |                  |
       v                  v
    Serveurs internes   Internet uniquement
    et postes gérés     selon la politique

Dans un réseau correctement segmenté, le trafic des invités est filtré pour empêcher les accès directs au réseau interne. Les détails dépendent de la topologie, des VLAN, des règles du pare-feu et des fonctions du matériel.

### 7.3. Le rôle des VLAN

Un VLAN permet de séparer logiquement des domaines de diffusion sur une infrastructure compatible. Il peut contribuer à la segmentation entre personnel, invités, appareils IoT et administration.

Un VLAN ne constitue pas à lui seul une politique de sécurité complète. Il faut vérifier les règles d'acheminement, les ACL, le pare-feu et les chemins qui peuvent permettre à un segment de joindre un autre.

Un réseau invité configuré dans un VLAN distinct mais dont les règles autorisent l'accès à tout le réseau interne n'est pas réellement isolé sur le plan des autorisations.

### 7.4. Isoler les clients Wi-Fi

Certains points d'accès offrent une fonction d'isolation des clients : les appareils connectés au même SSID ne peuvent pas communiquer directement entre eux selon la mise en œuvre.

Cette fonction peut être utile dans les hôtels, les salles de formation ou les réseaux visiteurs. Elle ne remplace cependant pas la segmentation en amont, car l'isolation des clients ne garantit pas à elle seule l'impossibilité d'atteindre tous les autres réseaux.

Il faut tester les communications prévues et vérifier que la configuration correspond à la politique.

### 7.5. Réseau IoT

Des téléviseurs, imprimantes, caméras, assistants vocaux ou capteurs peuvent utiliser le Wi-Fi. Certains disposent de capacités de mise à jour limitées ou d'un support de sécurité inférieur à celui d'un ordinateur récent.

Lorsque c'est compatible avec les usages, place ces appareils dans un réseau séparé et limite les communications nécessaires. Ne leur accorde pas automatiquement un accès aux postes des utilisateurs ou aux serveurs d'administration.

Un équipement qui doit communiquer avec une application interne doit recevoir uniquement les flux nécessaires, avec une documentation de ces exceptions.

### 7.6. Réseau d'administration

Les interfaces de gestion des points d'accès, contrôleurs, commutateurs et routeurs doivent être séparées des réseaux invités et, lorsque c'est possible, des réseaux utilisateurs ordinaires.

L'accès à l'administration devrait être limité aux postes et comptes autorisés. Le plan de gestion doit disposer d'une protection renforcée, car une compromission de cette zone peut modifier plusieurs réseaux à la fois.

## 8. SSID caché et filtrage MAC : leurs limites

### 8.1. Masquer le SSID ne sécurise pas le réseau

Certaines interfaces permettent de désactiver la diffusion habituelle du nom du réseau. Cela peut réduire sa visibilité dans certaines listes ordinaires, mais ne fournit pas une protection cryptographique et ne remplace ni l'authentification ni le chiffrement.

Le SSID peut être révélé par des échanges de gestion ou par le comportement des clients. Les dispositifs qui recherchent automatiquement un réseau caché peuvent également créer des problèmes de confidentialité en annonçant leurs réseaux mémorisés dans certains contextes.

Il vaut donc mieux se concentrer sur le bon mécanisme de sécurité, une phrase secrète robuste ou une authentification Enterprise, le firmware et la segmentation.

### 8.2. Le filtrage par adresse MAC

Une adresse MAC identifie une interface réseau au niveau de la couche liaison. Certaines interfaces Wi-Fi permettent de créer une liste d'adresses autorisées.

Mais l'adresse MAC ne constitue pas une preuve d'identité cryptographique. Elle peut être observée sur le réseau et, selon l'appareil, modifiée ou usurpée. De nombreux appareils modernes utilisent également des adresses MAC privées ou aléatoires pour protéger la vie privée.

Un filtrage MAC peut être un contrôle complémentaire dans un contexte restreint, mais il ne doit pas remplacer une méthode d'authentification robuste.

### 8.3. Le vrai ordre des priorités

Pour améliorer la sécurité, commence par :
1. choisir un mode de sécurité moderne ;
2. utiliser une authentification appropriée au contexte ;
3. modifier le mot de passe d'administration ;
4. maintenir le firmware ;
5. segmenter les réseaux et limiter les permissions ;
6. protéger la gestion distante ;
7. surveiller les accès et les changements ;
8. documenter la configuration et les exceptions.

Le masquage du SSID et le filtrage MAC ne devraient pas détourner l'attention de ces contrôles essentiels.

## 9. Sécuriser les clients Wi-Fi

### 9.1. Le poste doit être protégé lui aussi

La sécurité ne dépend pas uniquement du point d'accès. Un ordinateur connecté au réseau doit disposer de mises à jour, de protections adaptées, d'un pare-feu local et d'une gestion correcte des sessions.

Sur un réseau partagé, il faut éviter d'exposer inutilement les services de partage de fichiers et de découverte aux autres clients.

### 9.2. Profils Wi-Fi mémorisés

Les systèmes peuvent conserver des profils Wi-Fi et s'y reconnecter automatiquement. Les profils anciens ou créés pour un réseau dont la confiance n'est plus établie peuvent présenter des risques.

Supprime les profils inutiles et désactive la connexion automatique aux réseaux publics qui ne sont pas nécessaires. Pour un réseau d'entreprise, utilise le profil fourni ou approuvé par l'organisation, notamment lorsqu'il configure la validation des certificats.

### 9.3. Faux réseaux de même nom

Un nom identique ne garantit pas qu'il s'agit du réseau légitime. Avant de saisir des identifiants dans une page inattendue, vérifie le réseau et le contexte.

Dans une organisation utilisant WPA-Enterprise, les profils clients doivent être configurés pour vérifier le serveur d'authentification selon la politique. L'utilisateur ne devrait pas accepter un certificat inconnu simplement pour faire fonctionner la connexion.

### 9.4. Pare-feu local

Même lorsqu'un ordinateur est connecté à un Wi-Fi fiable, le pare-feu local contribue à limiter les communications entrantes. Le profil réseau du système doit être approprié et les services de partage ne devraient être disponibles que lorsque nécessaire.

La configuration doit tenir compte des besoins : une salle de formation peut nécessiter certains flux autorisés, mais ceux-ci doivent être définis plutôt que tout laisser accessible.

### 9.5. Mises à jour et sécurité applicative

Le navigateur, le système d'exploitation et les applications doivent rester maintenus. HTTPS est important lorsqu'on accède à des sites Web, y compris depuis un réseau Wi-Fi protégé. Les avertissements de certificat ne doivent pas être ignorés comme s'ils étaient un problème purement esthétique.

Une connexion Wi-Fi sûre réduit certains risques sur le segment radio, mais ne corrige pas un faux site Web ou un logiciel vulnérable.

## 10. Utiliser les réseaux Wi-Fi publics

### 10.1. Pourquoi faut-il être prudent ?

Les réseaux Wi-Fi publics sont souvent partagés par de nombreux utilisateurs et parfois ne disposent pas d'une authentification forte au niveau du réseau. Certains peuvent être usurpés, mal configurés ou mal entretenus.

Un réseau public peut être utile, mais il ne faut pas lui accorder la même confiance qu'à un réseau professionnel géré et documenté.

### 10.2. Bonnes pratiques

Lorsque c'est possible, évite d'utiliser un réseau public non fiable pour des activités professionnelles sensibles. Utilise des sites en HTTPS, garde le système à jour, active le pare-feu local, évite les partages de fichiers ouverts et désactive l'auto-connexion aux réseaux inconnus.

Un VPN approuvé par l'organisation peut protéger une partie du trafic jusqu'à son point de terminaison, mais il ne rend pas tous les sites sûrs et ne protège pas un appareil déjà compromis.

### 10.3. Ne pas se fier uniquement au portail captif

Le fait qu'un café ou un hôtel demande d'accepter ses conditions ne prouve pas que le réseau est authentique ni que ses communications sont protégées.

Vérifie que le nom du réseau correspond aux informations fournies par l'établissement. Évite de saisir les identifiants d'un compte professionnel dans un portail inattendu.

### 10.4. Après une connexion suspecte

Si tu crois t'être connecté à un faux réseau et avoir saisi des identifiants, utilise un canal fiable pour sécuriser le compte : change le secret lorsque nécessaire, vérifie les sessions et signale l'incident à l'équipe responsable. Ne suppose pas que se déconnecter du Wi-Fi annule tous les accès qu'un attaquant aurait déjà obtenus.

## 11. Planification radio : disponibilité et sécurité

### 11.1. Choisir l'emplacement du point d'accès

L'emplacement influence la couverture et la stabilité. Des murs, structures métalliques, équipements électriques et réseaux voisins peuvent dégrader le signal. Un point d'accès placé dans un endroit peu accessible peut être plus difficile à maintenir ou à surveiller.

Le matériel doit être installé dans un lieu approprié, protégé contre les manipulations non autorisées et accessible au personnel responsable de la maintenance.

### 11.2. Canaux et interférences

Un canal encombré peut créer des pertes de performance et des déconnexions. Le diagnostic doit examiner la couverture, les interférences et les capacités des clients. Une mauvaise performance n'indique pas automatiquement une attaque.

Les choix de canaux doivent respecter le domaine réglementaire, les contraintes des équipements et la planification de l'environnement. Il faut éviter de modifier les paramètres radio au hasard, surtout sur un réseau utilisé par plusieurs équipes.

### 11.3. Couverture et puissance

Une puissance trop faible peut créer des zones sans couverture. Une puissance excessive ne garantit pas de meilleures performances et peut accroître les interférences ou étendre la zone dans laquelle le réseau est détectable.

La couverture doit être adaptée aux locaux et aux besoins. Il est utile de mesurer les zones de connexion et d'identifier les endroits où les utilisateurs basculent entre plusieurs points d'accès.

### 11.4. Roaming

Dans une installation comportant plusieurs points d'accès, un client peut changer de point d'accès lorsque l'utilisateur se déplace. Le roaming doit être configuré pour offrir une transition fiable sans créer de zones de confiance incohérentes.

Les fonctions d'optimisation du roaming et la gestion des clés varient selon les équipements. Une organisation doit tester le comportement réel des clients au lieu de supposer qu'une option activée améliore nécessairement toutes les situations.

### 11.5. Continuité d'activité

Le Wi-Fi peut être affecté par une panne matérielle, une interférence ou une perturbation. Pour les activités essentielles, conserver certains équipements critiques en filaire peut offrir une solution de repli.

La planification doit identifier les usages qui ne peuvent pas rester indisponibles et prévoir des moyens alternatifs réalistes.

## 12. Surveillance et détection d'anomalies Wi-Fi

### 12.1. Qu'observer ?

Une équipe réseau peut surveiller :
- l'inventaire des points d'accès ;
- les versions de firmware ;
- les appareils associés ;
- les échecs d'authentification ;
- les changements de configuration ;
- les apparitions de points d'accès non approuvés ;
- les plaintes de connexion inhabituelles ;
- les connexions répétées à des SSID ressemblant au réseau officiel ;
- les événements d'authentification Enterprise ;
- les changements des comptes administrateurs.

Ces informations doivent être interprétées avec le contexte. Un nouvel appareil peut être légitime, par exemple un téléphone de remplacement. Un nombre élevé d'échecs peut résulter d'un mot de passe changé, d'un profil client obsolète ou d'une tentative malveillante.

### 12.2. Détecter un point d'accès non autorisé

La détection peut s'appuyer sur l'inventaire, la gestion des contrôleurs, l'observation radio et les processus de signalement. Un réseau au même nom qu'un réseau approuvé mais diffusé par un appareil inconnu mérite une vérification.

Ne tente pas de désactiver, perturber ou attaquer le point d'accès suspect sans autorisation. Les étapes utiles consistent à consigner l'heure, le lieu approximatif, le SSID observé, les identifiants techniques disponibles et à faire examiner le cas par l'équipe responsable.

### 12.3. Journaux d'authentification

Dans un réseau Enterprise, les journaux RADIUS et ceux du contrôleur peuvent aider à comprendre les échecs ou succès d'authentification. Il faut conserver suffisamment d'informations pour enquêter tout en protégeant les données personnelles et en évitant d'enregistrer inutilement des secrets.

Les journaux doivent être protégés contre les modifications non autorisées et leur durée de conservation doit correspondre à la politique de l'organisation.

### 12.4. Changements de configuration

Une modification de mode de sécurité, de certificat, de SSID ou de règle de segmentation peut avoir un impact important. Les équipements et contrôleurs devraient enregistrer les changements d'administration lorsque possible.

Une revue périodique permet de comparer la configuration courante à la configuration approuvée et de repérer les exceptions oubliées.

## 13. Diagnostic Wi-Fi sous Windows

Ces commandes servent à observer la configuration et l'état du poste. Exécute-les sur un appareil que tu es autorisé à examiner. Elles ne doivent pas être utilisées pour tenter d'accéder à un réseau sans permission.

### 13.1. Voir les interfaces et leur état

Ouvre PowerShell ou l'invite de commandes et exécute :

    netsh wlan show interfaces

La sortie peut afficher le nom de l'interface sans fil, son état, le SSID connecté, le type de radio, le canal, le débit et certains paramètres de signal, selon la version du système et le matériel.

Utilise ces informations pour répondre à des questions simples :
- Le Wi-Fi est-il connecté ?
- Le bon SSID est-il sélectionné ?
- Le signal est-il faible ?
- Le type de radio et le canal sont-ils cohérents avec l'environnement ?

Un signal faible n'indique pas nécessairement une attaque. Il peut être provoqué par la distance, les obstacles ou les interférences.

### 13.2. Examiner le pilote et les capacités

    netsh wlan show drivers

Cette commande affiche des informations sur le pilote Wi-Fi et les capacités prises en charge. Les détails disponibles dépendent du matériel et du pilote.

Si un mode attendu n'apparaît pas, vérifie la version du pilote, la capacité de l'adaptateur et la compatibilité du système. Le point d'accès et le client doivent prendre en charge le mode souhaité.

### 13.3. Lister les réseaux visibles

    netsh wlan show networks mode=bssid

Cette commande affiche les réseaux détectés et, selon le système, des détails sur les points d'accès et les signaux observés.

Une liste de réseaux voisins est normale dans de nombreux environnements urbains ou professionnels. Ne conclus pas à une attaque simplement parce qu'un SSID inconnu apparaît. Si un réseau ressemble au réseau de l'organisation, signale-le selon la procédure plutôt que de tenter de le tester en dehors du périmètre autorisé.

### 13.4. Examiner les profils enregistrés

    netsh wlan show profiles

Cette commande affiche les profils Wi-Fi enregistrés. Elle aide à repérer les anciens profils qui ne sont plus nécessaires. Ne cherche pas à afficher ou copier les secrets Wi-Fi des profils sur un appareil qui ne t'appartient pas ou que tu n'es pas autorisé à administrer.

Supprime les profils inutiles via les paramètres Windows ou les outils approuvés de gestion de l'appareil. Avant de retirer un profil professionnel, assure-toi de pouvoir le réinscrire selon la procédure de l'organisation.

### 13.5. Utiliser les observations avec méthode

Pour diagnostiquer une connexion, documente la date, l'emplacement, le SSID attendu, l'état de l'interface, le niveau de signal et le message d'erreur. Compare ensuite les résultats à ceux d'un appareil qui fonctionne, si cela est autorisé.

Les commandes d'observation ne constituent pas un audit complet de sécurité. Elles servent à comprendre l'état du client et à orienter la suite du diagnostic.

## 14. Diagnostic Wi-Fi sous Linux

Les commandes ci-dessous s'appliquent à de nombreuses distributions Linux, mais les outils disponibles et les permissions varient.

### 14.1. Identifier les interfaces

    ip link

Cette commande affiche les interfaces réseau et leur état administratif. Le nom de l'interface Wi-Fi dépend du système ; il peut ressembler à `wlan0` ou suivre une convention de nommage moderne.

La présence de l'interface ne signifie pas nécessairement que le pilote, l'authentification ou l'accès réseau fonctionnent correctement.

### 14.2. Afficher les interfaces Wi-Fi

    iw dev

Si l'outil `iw` est installé, la commande affiche les interfaces sans fil et des informations sur leur fonctionnement. Elle ne réalise pas une attaque et ne contourne pas l'authentification ; elle sert à observer la configuration locale.

### 14.3. Voir les réseaux autour du poste

Avec NetworkManager, on peut utiliser :

    nmcli device wifi list

La commande affiche les réseaux visibles selon l'état de l'interface et les droits disponibles. La visibilité d'un SSID n'indique pas si le réseau est fiable ou malveillant.

Pour un réseau suspect, n'essaie pas de te connecter simplement pour vérifier s'il est réel. Utilise les informations d'inventaire et signale la différence à l'équipe responsable.

### 14.4. Examiner la connexion active

    nmcli connection show --active

Cette commande affiche les connexions actives gérées par NetworkManager. Elle peut aider à vérifier quel profil est utilisé.

### 14.5. Distinguer panne radio et panne réseau

Un appareil peut être associé au point d'accès sans avoir une adresse IP correcte ou un accès DNS fonctionnel. Il faut distinguer :
- l'activation de l'interface ;
- l'association au point d'accès ;
- l'authentification Wi-Fi ;
- l'attribution d'une adresse IP ;
- la résolution DNS ;
- l'accès à la passerelle ;
- l'accès aux services attendus.

Cette démarche évite de modifier les paramètres de sécurité alors que la cause réelle est une panne DHCP, un problème DNS ou une erreur de routage.

## 15. TP guidé : sécuriser un routeur de laboratoire

### 15.1. Objectif et périmètre

Ce TP s'effectue uniquement sur un routeur ou un point d'accès que tu possèdes ou que tu es autorisé à administrer. N'applique pas de changements sur le routeur d'une entreprise, d'un établissement ou d'un fournisseur sans permission explicite.

L'objectif est de créer une configuration de base : accès administrateur protégé, protocole de sécurité adapté, firmware maintenu et réseau invité séparé.

### 15.2. Étape 1 — Identifier l'équipement

Note le fabricant, le modèle, la version du firmware, la fonction de l'appareil et l'adresse ou le mode d'accès à l'interface d'administration. Vérifie que l'équipement est encore maintenu par son fabricant ou fournisseur.

Ne publie pas sur un forum ouvert l'adresse d'administration, les détails sensibles de configuration ou les informations qui pourraient faciliter une attaque.

### 15.3. Étape 2 — Protéger l'administration

Change les identifiants par défaut. Utilise un mot de passe d'administration unique, différent du secret du réseau Wi-Fi. Si l'appareil permet de créer des comptes d'administration individuels, limite les permissions et retire les comptes inutiles.

Désactive l'administration distante si elle n'est pas nécessaire. Si elle est nécessaire, restreins-la au chemin d'administration approuvé.

### 15.4. Étape 3 — Choisir la sécurité Wi-Fi

Vérifie les options disponibles. Privilégie WPA3 si les clients le prennent en charge et si le mode correspond à ton besoin. Si la compatibilité impose WPA2, sélectionne une configuration moderne avec AES-CCMP et une phrase secrète robuste pour un réseau personnel.

N'utilise pas WEP ou les modes anciens. N'active pas un mode de compatibilité sans comprendre quels clients l'exigent et quelle conséquence cela a sur la posture globale.

### 15.5. Étape 4 — Définir un SSID adapté

Utilise un nom qui n'expose pas inutilement des informations personnelles ou internes. Un nom de réseau unique est utile pour les utilisateurs, mais n'est pas un mécanisme de sécurité en lui-même.

Il n'est pas nécessaire de masquer le SSID pour obtenir une protection robuste. L'important est que l'accès au réseau et l'administration soient protégés.

### 15.6. Étape 5 — Évaluer les fonctions supplémentaires

Vérifie WPS, UPnP, l'administration distante, les comptes par défaut et les fonctions de découverte. Désactive les fonctions inutiles selon la documentation du fabricant et teste le fonctionnement après changement.

Ne désactive pas tout sans analyse : certaines fonctions peuvent être nécessaires à un usage légitime.

### 15.7. Étape 6 — Créer un réseau invité

Si l'équipement le permet, crée un SSID invité réellement séparé du réseau principal. Vérifie que les visiteurs peuvent accéder à Internet mais ne peuvent pas atteindre les interfaces d'administration, les partages internes ou les serveurs non destinés au public.

Un nom différent n'est pas suffisant. Il faut confirmer que la séparation et les règles de filtrage fonctionnent.

### 15.8. Étape 7 — Mettre à jour et sauvegarder

Vérifie la disponibilité d'une mise à jour officielle, planifie son installation selon la documentation, puis confirme que l'équipement redémarre et que le Wi-Fi fonctionne comme prévu.

Sauvegarde la configuration dans un emplacement protégé, puis documente les principaux paramètres et la procédure de restauration.

### 15.9. Étape 8 — Vérifier la configuration finale

Utilise une liste de vérification :
- les identifiants d'administration par défaut ont-ils été remplacés ?
- le mode Wi-Fi est-il moderne ?
- les clients autorisés peuvent-ils se connecter ?
- le réseau invité est-il séparé ?
- l'administration distante est-elle limitée ?
- le firmware est-il maintenu ?
- les fonctions inutiles ont-elles été examinées ?
- la configuration est-elle sauvegardée et documentée ?

Une vérification complète doit être réalisée après les changements, pas seulement pendant la configuration.

## 16. TP guidé : concevoir le Wi-Fi d'une petite entreprise

### 16.1. Scénario

Une entreprise compte quinze employés, cinq formateurs externes, plusieurs visiteurs et des équipements connectés tels que des imprimantes. Tous les utilisateurs utilisent actuellement un seul SSID et une seule phrase secrète. Le point d'accès est administré avec un mot de passe commun connu de plusieurs personnes.

L'objectif est de proposer une architecture plus adaptée.

### 16.2. Étape 1 — Identifier les profils

Commence par distinguer les besoins :
- le personnel doit accéder aux applications internes et à Internet ;
- les formateurs peuvent avoir besoin de la plateforme et de ressources pédagogiques ;
- les visiteurs ont surtout besoin d'Internet ;
- les imprimantes et appareils IoT ne doivent communiquer qu'avec les systèmes nécessaires ;
- les administrateurs doivent accéder aux interfaces de gestion.

Ces besoins ne justifient pas un accès réseau identique pour tous.

### 16.3. Étape 2 — Proposer les zones

Une proposition pourrait inclure :
- un réseau du personnel ;
- un réseau invité ;
- un réseau ou segment IoT ;
- un réseau d'administration séparé.

Le nombre de SSID et les VLAN nécessaires dépendent de l'équipement et de la conception. La séparation logique peut se faire au niveau du point d'accès, des commutateurs et du routeur ou pare-feu.

### 16.4. Étape 3 — Choisir l'authentification

Pour le personnel, une architecture Enterprise avec authentification individuelle peut faciliter le retrait des accès lorsque les employés changent de rôle ou quittent l'entreprise. Une petite structure peut avoir besoin d'une approche plus simple, mais doit alors définir comment elle gère la phrase secrète, les départs et les appareils autorisés.

Le réseau invité doit disposer de règles d'accès restreintes et ne doit pas utiliser les mêmes droits que le personnel.

### 16.5. Étape 4 — Définir les règles de flux

Exemple de politique de haut niveau :

| Source | Destination | Décision de principe |
|---|---|---|
| Personnel | Internet | Autoriser selon la politique |
| Personnel | Applications internes autorisées | Autoriser les flux nécessaires |
| Invités | Internet | Autoriser selon la politique |
| Invités | Administration et serveurs internes | Refuser |
| IoT | Services explicitement requis | Autoriser uniquement les flux documentés |
| IoT | Postes utilisateurs et gestion | Refuser par défaut, sauf besoin justifié |
| Administration | Interfaces de gestion approuvées | Autoriser depuis les postes et comptes désignés |

Cette matrice est un point de départ. Chaque flux autorisé doit être lié à un besoin réel, et l'application des règles doit être testée.

### 16.6. Étape 5 — Définir l'administration

L'accès à la gestion des points d'accès et du routeur doit être réservé aux administrateurs autorisés. Les identifiants doivent être individuels lorsque la technologie le permet, les privilèges limités et les changements enregistrés.

La configuration doit être sauvegardée et les changements inattendus examinés.

### 16.7. Étape 6 — Définir la maintenance

La maintenance couvre les mises à jour, l'examen des journaux, la vérification des clients et points d'accès, la revue des comptes, les sauvegardes et les tests de restauration.

Les appareils qui ne sont plus maintenus doivent être remplacés ou isolés selon une décision de risque documentée.

### 16.8. Étape 7 — Tester

Dans un environnement autorisé, vérifie :
- le personnel peut joindre ses applications prévues ;
- les invités n'accèdent pas directement aux ressources internes ;
- les appareils IoT ne communiquent qu'avec les services requis ;
- les interfaces de gestion ne sont pas disponibles depuis le réseau invité ;
- les méthodes d'authentification fonctionnent ;
- les journaux contiennent les événements pertinents ;
- la sauvegarde de configuration peut être restaurée.

Un test réussi doit vérifier la règle elle-même, et pas seulement l'absence d'erreur visible sur un écran.

## 17. Réagir à un incident Wi-Fi

### 17.1. Signaux à prendre au sérieux

Les signaux peuvent inclure un réseau inattendu portant un nom proche de celui de l'entreprise, de nombreux échecs d'authentification, un appareil inconnu, une modification non approuvée de la configuration, une redirection inattendue ou un changement soudain de comportement.

Une seule observation ne prouve pas nécessairement une attaque. Les techniciens doivent recueillir les éléments utiles et éviter d'intervenir au hasard.

### 17.2. Contenir le risque

Selon le scénario, l'équipe peut retirer un client inconnu, désactiver un SSID non autorisé, isoler un segment ou suspendre un accès. Toute action doit être réalisée par du personnel autorisé et prendre en compte l'impact sur les services.

Ne tente pas de brouiller un réseau, de déconnecter des utilisateurs par des méthodes offensives ou de prendre le contrôle d'un point d'accès suspect. Ces actions peuvent perturber des services et ne remplacent pas l'investigation.

### 17.3. Préserver les éléments

Documente l'heure, le lieu, le SSID, les points d'accès connus, les événements d'authentification et les changements de configuration. Conserve les journaux pertinents dans un emplacement protégé et signale l'incident à l'équipe responsable.

Évite de publier les informations de configuration ou les détails du réseau dans des espaces publics.

### 17.4. Révoquer les accès concernés

Si une phrase secrète a pu être compromise, planifie son remplacement et mets à jour les appareils autorisés. Dans un réseau Enterprise, désactive les comptes compromis ou révoque les certificats selon le mécanisme utilisé.

Si l'administration du routeur a été compromise, vérifie les comptes, le firmware, les règles, les DNS et les paramètres de gestion avant de considérer le réseau comme sain.

### 17.5. Restaurer et revoir la configuration

Après l'incident, restaure une configuration connue et approuvée si cela est approprié. Vérifie le mode de sécurité, la segmentation, les comptes et les appareils connectés. Corrige la cause, puis teste la connectivité et les règles avant de remettre le réseau en service.

## 18. Erreurs fréquentes à éviter

### Erreur 1 — Croire que masquer le SSID sécurise le réseau

Le masquage ne fournit pas de chiffrement robuste et ne garantit pas que le réseau soit invisible.

**Correction :** choisir un mode de sécurité moderne, protéger l'administration et contrôler les accès.

### Erreur 2 — Réutiliser le même mot de passe partout

Une phrase secrète utilisée sur le Wi-Fi, le routeur et d'autres services peut propager une compromission.

**Correction :** utiliser des secrets uniques pour l'administration et les autres services ; gérer les accès selon le risque.

### Erreur 3 — Laisser les identifiants d'administration par défaut

Une personne qui accède à l'administration peut modifier les paramètres et affaiblir les contrôles.

**Correction :** remplacer les valeurs par défaut, limiter les comptes et protéger l'accès à la gestion.

### Erreur 4 — Croire que WPA3 suffit à sécuriser toute l'architecture

WPA3 améliore la protection radio, mais n'empêche pas une mauvaise segmentation, une administration distante exposée ou un serveur interne mal sécurisé.

**Correction :** protéger l'équipement, les identités, les applications et les flux du réseau.

### Erreur 5 — Confondre SSID invité et réseau invité isolé

Un second nom de réseau peut toujours être relié au même segment et aux mêmes ressources internes.

**Correction :** vérifier les VLAN, les règles du routeur et les chemins de communication.

### Erreur 6 — Accepter un certificat inconnu pour faire fonctionner WPA-Enterprise

Cela peut permettre à un faux serveur d'authentification de tromper un client.

**Correction :** configurer correctement la validation du certificat et de l'identité du serveur selon la politique.

### Erreur 7 — Activer toutes les fonctions pratiques

WPS, UPnP ou l'administration distante peuvent élargir la surface d'attaque.

**Correction :** examiner chaque fonction, la désactiver si elle n'est pas nécessaire et tester les usages légitimes.

### Erreur 8 — Considérer un réseau public comme fiable parce qu'il est connu

Le nom d'un réseau peut être imité, et un portail captif ne garantit pas le chiffrement.

**Correction :** vérifier le réseau et protéger les échanges applicatifs, les comptes et les appareils.

### Erreur 9 — Confondre mauvaise performance et attaque

Les interférences, la couverture, les pilotes et les problèmes DHCP/DNS peuvent provoquer des symptômes similaires.

**Correction :** séparer association radio, authentification, adressage IP, DNS et accès aux services.

### Erreur 10 — Oublier les mises à jour de l'équipement

Un point d'accès ou routeur en fin de support peut rester exposé à des vulnérabilités.

**Correction :** maintenir le firmware et planifier le remplacement des équipements qui ne reçoivent plus de correctifs.

### Erreur 11 — Ne pas sauvegarder la configuration

Une panne peut imposer une reconstruction manuelle, et un incident peut nécessiter de restaurer un état connu.

**Correction :** conserver une sauvegarde protégée et vérifier la procédure de restauration.

### Erreur 12 — Réagir à un point d'accès suspect par une action non autorisée

Tenter de perturber ou d'attaquer le dispositif peut aggraver l'incident ou toucher un réseau voisin.

**Correction :** documenter le constat, limiter l'accès selon la procédure et faire intervenir l'équipe responsable.

## 19. Exercices d'application avec corrections

### Exercice 1 — Comprendre le SSID

Que représente principalement le SSID ?

A. Le secret cryptographique du réseau  
B. Le nom qui identifie un réseau Wi-Fi  
C. Une adresse IP du routeur  
D. Le mot de passe administrateur

**Correction : B.** Le SSID est un nom de réseau. Il ne constitue pas, à lui seul, une preuve d'identité ni une protection cryptographique.

### Exercice 2 — Choisir le mode de sécurité

Tu configures un nouveau réseau et tous les appareils indispensables prennent en charge un mode moderne. Quel principe dois-tu suivre ?

A. Utiliser WEP parce qu'il est compatible avec les anciens appareils  
B. Choisir le mode de sécurité robuste approprié pris en charge, généralement WPA3 lorsque possible  
C. Désactiver le chiffrement et masquer le SSID  
D. Utiliser le même mot de passe que l'administration du routeur

**Correction : B.** Il faut privilégier un mécanisme moderne adapté aux appareils. Les protocoles obsolètes ne deviennent pas sûrs parce qu'on ajoute un secret complexe.

### Exercice 3 — Réseau personnel ou entreprise

Pourquoi une entreprise disposant de nombreux employés peut-elle préférer une architecture WPA-Enterprise avec 802.1X ?

A. Parce qu'elle ne nécessite aucune gestion  
B. Parce qu'elle permet d'utiliser des identités et politiques individuelles plutôt que dépendre uniquement d'une phrase secrète partagée  
C. Parce qu'elle chiffre automatiquement tous les fichiers des ordinateurs  
D. Parce qu'elle remplace le pare-feu

**Correction : B.** L'authentification d'entreprise peut faciliter la gestion individuelle des accès. Elle demande cependant une infrastructure et une configuration correctement entretenues.

### Exercice 4 — Validation du certificat

Un ordinateur refuse de rejoindre le Wi-Fi d'entreprise parce qu'il ne reconnaît pas le certificat du serveur d'authentification. Quelle est la meilleure action ?

A. Désactiver immédiatement toute validation de certificat  
B. Accepter n'importe quel certificat  
C. Vérifier le profil client, le certificat et la configuration officielle auprès de l'équipe réseau  
D. Communiquer le mot de passe Wi-Fi à un collègue

**Correction : C.** Un certificat inconnu peut signaler une mauvaise configuration ou une tentative d'usurpation. Il faut comprendre le problème plutôt que désactiver le contrôle.

### Exercice 5 — Réseau invité

Quel est le but principal d'un réseau invité bien isolé ?

A. Donner aux visiteurs les mêmes accès que les administrateurs  
B. Fournir l'accès prévu, généralement Internet, sans ouvrir directement le réseau interne  
C. Supprimer le besoin de mises à jour sur les points d'accès  
D. Rendre le réseau invisible

**Correction : B.** La séparation doit être appliquée par l'architecture et les règles de filtrage. Un SSID différent ne suffit pas si le trafic peut toujours atteindre les systèmes internes.

### Exercice 6 — Masquage du SSID

Quel est le principal problème de sécurité lorsqu'on s'appuie uniquement sur un SSID masqué ?

A. Le réseau devient automatiquement chiffré  
B. Le nom ne constitue pas un secret fiable ni un mécanisme d'authentification  
C. Le routeur ne peut plus utiliser d'adresse IP  
D. Le point d'accès met fin à toutes les communications

**Correction : B.** Le masquage n'apporte pas une authentification robuste. Il faut protéger les accès par les mécanismes cryptographiques appropriés.

### Exercice 7 — Réseau public suspect

Tu vois deux réseaux du même café portant presque le même nom. Que fais-tu ?

A. Choisir celui dont le signal est le plus fort sans vérifier  
B. Saisir tes identifiants professionnels dans les deux pour comparer  
C. Vérifier le nom officiel auprès de l'établissement et éviter le réseau suspect  
D. Désactiver HTTPS dans le navigateur

**Correction : C.** Un réseau usurpé peut imiter un réseau légitime. Il faut vérifier la source, éviter les connexions inattendues et protéger les applications.

### Exercice 8 — Mauvaise performance

Un utilisateur se connecte au point d'accès mais n'arrive pas à ouvrir des sites. Quel diagnostic est le plus utile ?

A. Conclure immédiatement à une attaque par brouillage  
B. Vérifier l'association, l'adresse IP, la passerelle, le DNS et l'accès aux services  
C. Désactiver WPA3  
D. Remplacer le mot de passe administrateur avant tout diagnostic

**Correction : B.** La connexion radio peut fonctionner alors que DHCP, DNS ou le routage pose problème. Il faut isoler chaque étape.

### Exercice 9 — Mot de passe d'administration

Pourquoi faut-il le distinguer du mot de passe Wi-Fi ?

A. Ils doivent toujours être identiques  
B. Le secret d'administration permet de modifier les paramètres et peut donc compromettre l'ensemble de la configuration  
C. Le mot de passe Wi-Fi donne toujours accès à l'administration  
D. Le routeur n'a jamais besoin d'un accès administrateur protégé

**Correction : B.** Si l'administration est compromise, un attaquant peut modifier des réglages qui affaiblissent les autres protections. Les secrets doivent être distincts et robustes.

### Exercice 10 — Réaction à un point d'accès inconnu

Un point d'accès non approuvé semble être connecté au réseau professionnel. Quelle est la réaction la plus appropriée ?

A. Le perturber par une attaque radio  
B. Le reconfigurer sans autorisation  
C. Documenter le constat et le signaler à l'équipe autorisée, qui appliquera la procédure de containment et d'investigation  
D. Publier la configuration du réseau sur un forum

**Correction : C.** L'équipe doit collecter les informations pertinentes, limiter le risque selon ses procédures et préserver les éléments utiles.

## 20. Défi final — Sécuriser le Wi-Fi de NovaLearn

### 20.1. Scénario

NovaLearn possède un point d'accès qui dessert les formateurs, les apprenants, les visiteurs et plusieurs imprimantes. Tous se connectent actuellement au même SSID avec une seule phrase secrète. Le mot de passe administrateur du routeur n'a pas été modifié. Le firmware n'a pas été vérifié depuis longtemps, l'administration distante est activée et les appareils invités peuvent accéder à certains équipements internes.

L'entreprise veut améliorer la sécurité sans interrompre durablement les formations.

### 20.2. Travail demandé

Prépare une proposition qui comprend :
1. un inventaire des équipements Wi-Fi ;
2. le choix du mécanisme de sécurité ;
3. la protection de l'administration ;
4. la séparation des utilisateurs et appareils ;
5. les règles de communication ;
6. la maintenance et la sauvegarde ;
7. le suivi des connexions et des anomalies ;
8. une procédure de réponse à incident ;
9. des critères pour vérifier les résultats.

### 20.3. Correction détaillée

**Inventaire.** L'entreprise identifie les points d'accès, routeurs, commutateurs, modèles, versions de firmware, emplacements et responsables. Elle identifie les SSID, les méthodes d'authentification, les VLAN, les règles de filtrage et les comptes d'administration.

**Choix de sécurité.** Elle privilégie WPA3 lorsque tous les appareils indispensables sont compatibles et que le mode correspond au besoin. Si des équipements doivent encore utiliser WPA2, elle choisit une configuration moderne, documente cette contrainte et planifie l'évolution. Les modes obsolètes sont retirés.

**Administration.** Les identifiants par défaut sont remplacés par un secret unique. L'administration distante non nécessaire est désactivée. L'accès restant est limité au personnel et au chemin de gestion approuvés. Les changements sont journalisés et les secrets protégés.

**Segmentation.** L'entreprise crée un réseau du personnel, un réseau invité et une zone IoT si l'équipement le permet. Les interfaces d'administration sont accessibles seulement depuis une zone autorisée. Le réseau invité ne doit pas accéder directement aux serveurs ou aux postes internes.

**Règles de flux.** Le personnel peut accéder aux applications prévues, les invités disposent de l'accès Internet requis, et les appareils connectés communiquent uniquement avec les services nécessaires. Les exceptions sont documentées et les règles testées.

**Maintenance.** Le firmware est vérifié et mis à jour selon une procédure. La configuration est sauvegardée dans un emplacement protégé et la restauration est testée. Les équipements en fin de support sont planifiés pour remplacement.

**Surveillance.** L'équipe suit les points d'accès connus, les changements de configuration, les échecs d'authentification, les appareils inhabituels et les incidents signalés. Les journaux sont protégés et accessibles aux personnes autorisées.

**Réponse à incident.** L'équipe définit comment documenter un faux point d'accès, limiter les accès, révoquer les secrets compromis et restaurer une configuration connue. Les utilisateurs savent à qui signaler une connexion suspecte.

### 20.4. Priorisation

**Priorité 1 — Corriger les risques immédiats :** modifier l'administration par défaut, vérifier le mode de sécurité, restreindre l'administration distante et couper l'accès direct des invités aux ressources internes.

**Priorité 2 — Stabiliser :** inventorier les équipements, vérifier le firmware, sauvegarder la configuration et tester les règles.

**Priorité 3 — Renforcer :** mettre en place une authentification Enterprise si elle est justifiée, centraliser les journaux et réduire les permissions entre zones.

**Priorité 4 — Maintenir :** réviser les comptes, mettre à jour les équipements, tester la récupération et actualiser l'inventaire.

### 20.5. Critères d'autoévaluation

Tu as réussi si tu sais expliquer le choix du protocole, pourquoi un SSID n'est pas une preuve d'identité, comment le réseau invité est réellement séparé, comment les identités sont gérées, pourquoi l'administration doit être protégée, comment vérifier les flux et comment réagir lorsqu'un réseau semble usurpé.

## 21. Synthèse du cours

Le Wi-Fi permet aux appareils de communiquer par radio, mais le signal peut dépasser les limites physiques des locaux. Il faut donc considérer la possibilité qu'une personne non autorisée détecte le réseau, tente de s'y connecter ou crée un point d'accès qui imite le réseau légitime.

Le SSID identifie le nom du réseau ; il ne prouve pas à lui seul son authenticité. Masquer le SSID ou filtrer les adresses MAC ne remplace pas une méthode d'authentification et de chiffrement robuste.

Les anciennes technologies WEP et les modes de sécurité hérités ne sont pas adaptés à une nouvelle installation. WPA3 est à privilégier lorsque le matériel et les besoins le permettent. WPA2 correctement configuré peut rester nécessaire pour la compatibilité. Le choix doit tenir compte des clients, des méthodes d'authentification et de la politique de sécurité.

Pour les réseaux personnels, WPA3-Personal avec une phrase secrète robuste peut convenir. Pour les organisations qui doivent gérer de nombreux utilisateurs, WPA-Enterprise avec 802.1X, RADIUS et une méthode EAP correctement configurée peut faciliter la gestion individuelle des accès. Les certificats et les paramètres de confiance doivent être validés correctement.

La sécurité ne s'arrête pas au protocole radio. L'administration du routeur doit être protégée, les identifiants par défaut remplacés, le firmware maintenu, les fonctions inutiles examinées et les configurations sauvegardées.

La segmentation distingue le personnel, les invités, les appareils IoT et l'administration. Un réseau invité doit être réellement isolé ; un SSID différent ne suffit pas si les règles permettent toujours d'accéder aux ressources internes.

Les utilisateurs doivent être prudents sur les réseaux publics, désactiver l'auto-connexion aux réseaux inconnus et conserver HTTPS, les mises à jour et le pare-feu local. Le chiffrement Wi-Fi et les protections applicatives sont complémentaires.

Enfin, un réseau sans fil nécessite un inventaire, une surveillance, des tests de configuration et une procédure de réponse à incident. En cas de doute sur un point d'accès, il faut documenter et signaler la situation à l'équipe autorisée plutôt que tenter de perturber le réseau.

## 22. Glossaire des notions essentielles

**802.1X :** standard de contrôle d'accès réseau fondé sur l'authentification.

**AES-CCMP :** mécanisme de chiffrement et de protection utilisé dans des configurations Wi-Fi modernes compatibles.

**Authentificateur :** équipement ou composant qui participe au contrôle de l'accès, par exemple le point d'accès dans une architecture 802.1X.

**EAP :** cadre de méthodes d'authentification utilisé notamment avec 802.1X.

**EAP-TLS :** méthode EAP qui utilise des certificats TLS pour l'authentification mutuelle selon sa configuration.

**Evil twin :** faux point d'accès qui imite un réseau légitime.

**Firmware :** logiciel bas niveau qui fait fonctionner un équipement réseau ou matériel.

**IoT :** Internet des objets, ensemble d'appareils connectés tels que caméras, imprimantes, capteurs et équipements domestiques.

**Point d'accès (AP) :** appareil ou fonction qui fournit une connexion radio au réseau.

**RADIUS :** protocole utilisé pour centraliser l'authentification, l'autorisation et, selon l'architecture, la comptabilisation.

**Réseau invité :** réseau prévu pour les visiteurs, normalement séparé des ressources internes non nécessaires.

**Rogue AP :** point d'accès non approuvé ou non géré par l'organisation.

**SSID :** nom logique qui identifie un réseau Wi-Fi.

**VLAN :** séparation logique de réseaux sur une infrastructure compatible.

**WEP :** ancien mécanisme Wi-Fi aujourd'hui considéré comme vulnérable.

**Wi-Fi :** technologie de réseau local sans fil fondée sur la famille de standards IEEE 802.11.

**WPA2 :** génération de protection Wi-Fi antérieure à WPA3, encore utilisée dans certains environnements compatibles correctement configurés.

**WPA3 :** génération plus récente de protection Wi-Fi, disponible en modes personnel et entreprise selon les équipements.

**WPS :** mécanisme conçu pour faciliter l'association d'appareils au réseau ; il doit être évalué et désactivé lorsque non nécessaire.

## 23. Ressources pour approfondir

Les ressources suivantes permettent de vérifier les recommandations et d'aller plus loin. La configuration réelle doit toujours suivre la documentation du matériel, la politique de l'organisation et les exigences applicables.

- **Centre canadien pour la cybersécurité — Protecting your organization while using Wi-Fi (ITSAP.80.009)** : menaces telles que faux réseaux, écoute et points d'accès non autorisés, et mesures de segmentation.  
  https://www.cyber.gc.ca/en/guidance/protecting-your-organization-while-using-wi-fi-itsap80009

- **Centre canadien pour la cybersécurité — Router cybersecurity best practices (ITSAP.80.019)** : protection de l'administration, choix des paramètres et maintenance des routeurs.  
  https://www.cyber.gc.ca/en/guidance/routers-cyber-security-best-practices-itsap80019

- **Federal Trade Commission — How To Secure Your Home Wi-Fi Network** : conseils pratiques sur WPA3/WPA2, mots de passe d'administration, mises à jour et fonctions du routeur.  
  https://consumer.ftc.gov/articles/how-secure-your-home-wi-fi-network

- **NIST — SP 800-153, Guidelines for Securing Wireless Local Area Networks** : recommandations relatives à la sécurité des réseaux sans fil tout au long de leur cycle de vie.  
  https://csrc.nist.gov/pubs/sp/800/153/final

- **Australian Cyber Security Centre — Information Security Manual, Guidelines for networking (September 2026)** : cadre de référence actuel sur la conception, la documentation, la segmentation et la sécurité réseau.  
  https://www.cyber.gov.au/ism/2026-09/guidelines-for-networking

- **CISA — A Guide to Securing Networks for Wi-Fi (IEEE 802.11 Family)** : guide technique de sécurité Wi-Fi.  
  https://www.cisa.gov/sites/default/files/publications/A_Guide_to_Securing_Networks_for_Wi-Fi.pdf

Le but d'un audit Wi-Fi n'est pas simplement de confirmer qu'un réseau demande un mot de passe. Il faut vérifier le mécanisme de sécurité, les équipements, les identités, la segmentation, les règles de gestion et le résultat des tests. Un réseau peut sembler fonctionner parfaitement tout en donnant aux appareils invités un accès bien trop large.

**Fin du cours : Sécurité Wi-Fi.**
