# Sécurité Wi-Fi

> **Mise en contexte**
>
> Le Wi-Fi transporte les communications par ondes radio, qui peuvent dépasser les murs et les limites physiques d'un bureau. Il faut donc protéger l'accès radio, les équipements clients, les données et les communications vers les ressources internes. La sécurité ne repose pas uniquement sur un mot de passe : elle dépend aussi du mode de chiffrement, de l'administration du point d'accès, des mises à jour, de la segmentation, de l'authentification et des habitudes des utilisateurs.
>
> Ce cours présente les mécanismes modernes, la configuration d'un routeur, l'isolation des invités, le diagnostic et la réponse aux anomalies. Les manipulations supposent un équipement personnel ou un laboratoire autorisé. Ne teste pas un réseau tiers sans permission.

## 1. Objectifs et notions de départ

À la fin du cours, tu sauras reconnaître les risques du Wi-Fi, comparer les mécanismes de protection, distinguer les modes personnels et entreprise, protéger l'administration, séparer les invités et appareils connectés, interpréter les paramètres d'un terminal et diagnostiquer une panne. Tu dois connaître les notions d'adresse IP, de passerelle, de DNS et de port, ou être prêt à les revoir dans les exemples.

Un point d'accès (AP) fournit le réseau radio. Le SSID est le nom logique du réseau. Le BSSID identifie une interface radio d'un point d'accès. Les bandes courantes incluent 2,4 GHz et 5 GHz ; 6 GHz est disponible dans certains pays et matériels. Le canal désigne une portion de spectre. Le roaming correspond au passage d'un AP à l'autre. Le routeur dirige le trafic entre réseaux tandis qu'un pare-feu applique une politique de filtrage, même si ces fonctions sont souvent réunies dans une même box.

## 2. Pourquoi le Wi-Fi doit-il être sécurisé ?

La portée radio ne s'arrête pas à la porte de la pièce. Une personne à proximité peut parfois détecter le réseau ou observer des caractéristiques des transmissions. Les menaces incluent la découverte de réseaux mal configurés, la devinette d'un secret faible, l'installation d'un point d'accès non autorisé, l'imitation d'un SSID connu, la collecte de métadonnées et les tentatives d'interposition.

Il faut distinguer les attaques des problèmes de disponibilité. Un canal encombré, un pilote défectueux, des obstacles ou un AP surchargé peuvent causer des coupures. Un diagnostic doit s'appuyer sur les journaux, les mesures radio et des tests reproductibles, plutôt que de conclure immédiatement à une attaque.

La sécurité radio est seulement une couche. L'authentification contrôle l'accès au réseau ; la segmentation limite ce qu'un appareil peut atteindre après connexion ; les applications doivent valider les certificats, protéger les sessions et appliquer leurs propres autorisations. Un Wi-Fi chiffré ne corrige pas une application vulnérable ou un ordinateur compromis.

## 3. WEP, WPA2 et WPA3

WEP est un mécanisme historique vulnérable et ne doit plus être utilisé comme protection normale. Les premières générations de WPA sont elles aussi dépassées pour les nouveaux déploiements. WPA2 avec AES-CCMP a été largement déployé et reste présent dans de nombreux environnements. WPA3 apporte des protections supplémentaires et doit être privilégié lorsque les équipements nécessaires le prennent en charge.

WPA3-Personal emploie SAE pour l'établissement de clé, renforçant la protection contre certaines attaques hors ligne sur le mot de passe par rapport au mécanisme personnel traditionnel. WPA3-Enterprise s'adresse notamment aux entreprises et peut accompagner des exigences cryptographiques renforcées, selon la configuration. Vérifie les modes réellement proposés par le matériel et les clients.

Un mode de transition peut accepter WPA2 et WPA3 pendant une migration. Il ne faut pas supposer que tous les appareils profitent automatiquement du mode le plus récent. Un appareil qui ne supporte que WEP ou un mode ancien doit être remplacé, mis à jour ou isolé temporairement après analyse du risque. Pour un nouveau réseau domestique, choisis WPA3-Personal si les appareils indispensables sont compatibles ; sinon un mode moderne WPA2 avec AES est préférable aux mécanismes obsolètes. Évite WEP, WPA ancien et TKIP.

## 4. Mode personnel et mode entreprise

WPA-Personal s'appuie généralement sur un secret partagé par les appareils. Il est simple à gérer pour un foyer, mais la révocation individuelle est difficile : quand un ancien invité conserve le secret, il faut parfois le changer pour tout le monde. Le secret doit être long, unique, difficile à deviner et différent du mot de passe d'administration du routeur.

WPA-Enterprise utilise typiquement 802.1X avec un serveur d'authentification, souvent RADIUS. Il permet des identités individuelles, des autorisations distinctes et une meilleure gestion des départs. EAP-TLS, par exemple, s'appuie sur TLS et des certificats. Le déploiement exige la gestion du cycle de vie des certificats, la révocation, la synchronisation de l'heure, des journaux et un plan de continuité si le serveur d'authentification tombe.

Le client doit vérifier le certificat du serveur d'authentification selon le profil prévu. Un profil qui accepte n'importe quel certificat peut être trompé par un serveur imposteur. Ne valide pas une invite inattendue simplement pour connecter l'appareil ; vérifie le changement par un canal fiable.

## 5. Mot de passe et administration

Utilise un mot de passe Wi-Fi long et unique. Une phrase secrète composée de plusieurs mots aléatoires peut être plus mémorisable qu'un secret court et prévisible. Évite les noms, dates, numéros de téléphone et mots courants. Un gestionnaire de mots de passe aide à conserver des secrets robustes. Le mot de passe Wi-Fi ne doit pas être réutilisé pour l'administration, l'e-mail ou un autre compte.

Remplace les identifiants par défaut du routeur. Protège l'interface d'administration avec un secret unique et désactive l'administration depuis Internet si elle n'est pas nécessaire. Si elle est indispensable, utilise un chemin maîtrisé, une restriction de sources et une authentification forte. Installe les mises à jour officielles, vérifie la fin de support du produit et sauvegarde la configuration après validation.

Désactive WPS s'il n'est pas requis. Évalue UPnP et les fonctions de redirection automatique de ports en fonction des usages. Un SSID caché ne chiffre pas les communications et ne rend pas le réseau invisible à un observateur radio. Le filtrage d'adresses MAC ne remplace pas l'authentification robuste, car ces adresses peuvent être observées et usurpées. Un code QR Wi-Fi doit être traité comme un secret : une personne qui peut le photographier peut potentiellement rejoindre le réseau.

## 6. Réseau invité, IoT et administration

Les visiteurs ne devraient pas obtenir les mêmes droits que les employés. Le réseau invité doit généralement permettre l'accès Internet et bloquer l'accès aux ressources internes. L'isolation des clients peut aussi empêcher des invités de communiquer directement entre eux, selon les capacités du matériel.

Les caméras, téléviseurs, imprimantes et autres appareils IoT peuvent être peu maintenus ou utiliser des identifiants faibles. Place-les dans un segment restreint et n'autorise que les flux nécessaires. Une caméra peut devoir joindre un serveur de gestion ; une imprimante peut être accessible depuis certains postes. Il faut décrire ces besoins sans ouvrir l'ensemble du réseau.

Le réseau d'administration doit être réservé aux postes ou bastions gérés. Un SSID distinct ne garantit pas une segmentation : vérifie le lien SSID-VLAN, les routes et les règles de filtrage. Teste depuis un vrai client invité que les ressources internes qui doivent être inaccessibles le sont réellement.

## 7. Faux points d'accès et clients

Un point d'accès non autorisé peut être installé dans une entreprise ; un faux SSID peut imiter celui d'un hôtel ou d'un réseau professionnel pour attirer les clients. Le nom du réseau n'est pas une preuve d'authenticité. Les organisations peuvent inventorier les AP, BSSID, canaux et emplacements, puis investiguer les observations inconnues.

Les utilisateurs devraient désactiver la connexion automatique aux réseaux inconnus, vérifier le nom officiel du réseau par un canal fiable et ne pas ignorer les avertissements de certificat. HTTPS correctement authentifié et un VPN professionnel peuvent compléter la protection, mais ne rendent pas le terminal invulnérable et ne prouvent pas qu'un site est honnête.

Les mises à jour du système et du pilote Wi-Fi sont importantes. Supprime les profils publics qui ne servent plus, désactive les partages inutiles sur les réseaux non fiables et vérifie la politique du pare-feu local. Ne considère pas un Wi-Fi comme digne de confiance simplement parce qu'il demande un mot de passe.

## 8. Fréquences et performance

La bande 2,4 GHz peut mieux traverser certains obstacles, mais elle est fréquemment encombrée. La bande 5 GHz offre souvent davantage d'options de canaux et un bon débit. La bande 6 GHz peut offrir plus de spectre là où elle est autorisée et prise en charge, mais tous les appareils ne la supportent pas.

Le canal et sa largeur influencent l'interférence. Une largeur plus grande peut améliorer le débit théorique dans un environnement libre mais occuper davantage de spectre dans une zone dense. Ne choisis pas automatiquement la largeur maximale. Mesure la couverture, la charge, les retransmissions et les canaux utilisés.

Le roaming dépend du placement des AP, de la puissance, des paramètres et des capacités client. Ajouter un AP sans étude peut dégrader les performances : les cellules se chevauchent mal ou les clients restent attachés au mauvais AP. Teste dans les zones réelles d'usage.

## 9. Supervision et réponse à un incident

Tiens un inventaire des points d'accès, des versions de firmware, des SSID, des VLAN et des responsables. Surveille les échecs d'authentification, les changements de configuration et les clients inconnus. Une hausse d'échecs peut venir d'un secret modifié, d'un certificat expiré, d'un mauvais profil ou d'une activité non autorisée ; le volume ne prouve pas à lui seul une attaque.

Lors d'une suspicion, note l'heure, le terminal, le SSID, le BSSID, la zone, les symptômes et les changements récents. Protège les journaux et limite leur diffusion. Évalue l'impact avant d'isoler un équipement, car une action précipitée peut interrompre un service légitime. Suis la procédure d'escalade et d'isolation approuvée.

Après l'incident, cherche la cause racine : secret trop partagé, firmware obsolète, AP non inventorié, certificat mal vérifié ou segmentation insuffisante. Corrige la cause, reteste les contrôles et documente les mesures préventives. La fermeture doit être fondée sur les résultats observés.

## 10. Diagnostic sous Windows

Pour afficher la configuration IP :

~~~powershell
ipconfig /all
~~~

Pour voir les réseaux Wi-Fi détectés :

~~~powershell
netsh wlan show networks
~~~

Pour afficher l'état des interfaces sans fil :

~~~powershell
netsh wlan show interfaces
~~~

Pour lister les profils enregistrés :

~~~powershell
netsh wlan show profiles
~~~

Ces commandes sont principalement des commandes de lecture. Les sorties peuvent contenir des noms internes et des adresses ; ne les publie pas sans nécessité. En cas d'échec, vérifie le SSID, la bande, le signal, le mode de sécurité, l'adresse IP, la passerelle et DNS. Si le client s'authentifie mais ne reçoit pas d'adresse, examine DHCP et le VLAN avant d'accuser le chiffrement.

## 11. Diagnostic sous Linux

Avec NetworkManager, affiche les périphériques :

~~~bash
nmcli device status
~~~

Pour afficher les réseaux détectés :

~~~bash
nmcli dev wifi list
~~~

Pour examiner les profils configurés :

~~~bash
nmcli connection show
~~~

Pour consulter les adresses et routes :

~~~bash
ip address
ip route
~~~

La visibilité des SSID dépend du matériel, du pilote et des conditions radio. Si l'authentification échoue, examine le mode de sécurité, le secret ou le certificat. Si aucune adresse IP n'est attribuée, vérifie DHCP, VLAN et relais. Si les noms ne se résolvent pas, vérifie le DNS. Si seule une application échoue, examine sa destination, son port et son certificat au lieu de conclure à une panne Wi-Fi globale.

## 12. Laboratoire : durcir un routeur

Utilise un équipement personnel ou autorisé et note la configuration initiale. Identifie le modèle, le firmware, les SSID, les comptes et les appareils dépendants. Prépare un accès local de secours.

Remplace les identifiants d'administration par défaut, désactive la gestion distante inutile et vérifie les mises à jour du fabricant. Choisis WPA3-Personal si les appareils essentiels le prennent en charge ; sinon sélectionne un mode moderne WPA2 avec AES et planifie la modernisation des clients anciens. N'interromps jamais l'alimentation pendant une mise à jour.

Si le routeur permet un réseau invité réellement isolé, active-le et teste depuis un appareil de test l'accès Internet ainsi que le refus vers une destination interne. Un nom de réseau distinct ne suffit pas. Après les tests, consigne le résultat et restaure l'état précédent si un service essentiel est cassé.

## 13. Concevoir le Wi-Fi d'une entreprise

Distingue les postes gérés, les appareils personnels, les visiteurs, les imprimantes, les caméras et l'administration. Les visiteurs doivent accéder à Internet sans atteindre les ressources internes. Les objets connectés doivent joindre les services nécessaires, pas toute l'entreprise. Les interfaces d'administration doivent être accessibles seulement depuis un petit nombre de systèmes gérés.

Le mode personnel peut convenir à une très petite structure si le secret est distribué et renouvelé correctement. Pour de nombreuses identités et des besoins de révocation individuelle, un mode Enterprise avec 802.1X peut être plus adapté. Il faut toutefois prévoir la gestion de RADIUS, des certificats et des pannes d'authentification.

Évite la multiplication des SSID sans justification. Elle accroît la charge de gestion et peut affecter la capacité radio. La segmentation doit suivre les besoins métier, être appliquée par les VLAN, routes et règles appropriés, et être testée depuis un client de chaque zone.

## 14. Procédure de dépannage

Classe le symptôme : SSID absent, authentification refusée, adresse IP manquante, accès local sans Internet, lenteur, déconnexions ou panne d'une application. Un SSID absent appelle l'examen de la radio, de la bande, de la couverture et du pilote. Une erreur d'authentification appelle l'examen du mode WPA, du secret, du profil et du certificat. L'absence d'adresse IP oriente vers DHCP ou VLAN. Des échecs de résolution orientent vers DNS.

Note l'heure, le terminal, la zone, le SSID, la bande, l'adresse IP, le message d'erreur et les changements récents. Utilise des commandes de lecture et les journaux. Ne désactive pas l'ensemble du pare-feu pour tester. Une hypothèse doit être confirmée par une observation, puis le flux permis et le flux interdit doivent être testés après correction.

## 15. Bonnes pratiques de cycle de vie

Documente chaque changement : responsable, date, raison, paramètres modifiés, appareils concernés, résultat et méthode de restauration. Revois les comptes, secrets et règles temporaires ; les accès accordés à un prestataire doivent être retirés à la fin du besoin. Planifie les mises à jour et vérifie la fin de support du matériel.

Dans une petite entreprise, le réseau doit rester compréhensible par la personne chargée de le maintenir. Une configuration jamais documentée devient fragile lorsque la personne qui l'a créée n'est plus disponible. Conserve l'inventaire et les procédures dans un emplacement protégé, pas dans un document public contenant des secrets.

## 16. Exercices de compréhension

Un SSID caché n'est pas une protection suffisante : il ne remplace ni le chiffrement ni l'authentification. WEP ne doit pas être conservé comme méthode normale, même si un appareil ancien l'exige. Une invite de certificat inconnue doit être vérifiée auprès de l'administrateur par un canal fiable. Un client connecté sans IP indique qu'il faut vérifier DHCP et VLAN. Un réseau invité qui voit les imprimantes nécessite une vérification de la segmentation, pas seulement un renommage du SSID.

Un faux SSID doit être confirmé auprès de l'exploitant. Une caméra qui tente des connexions inhabituelles doit être isolée selon la procédure, avec conservation des journaux. Une interface d'administration exposée sur Internet doit être désactivée si elle est inutile. Un VPN protège le trajet jusqu'à son point de terminaison selon sa configuration, mais il ne supprime pas les risques du terminal ou des applications.

## 17. Références

- Centre canadien pour la cybersécurité, protection lors de l'utilisation du Wi-Fi : https://www.cyber.gc.ca/en/guidance/protecting-your-organization-while-using-wi-fi-itsap80009
- FTC, sécuriser un réseau Wi-Fi domestique : https://consumer.ftc.gov/articles/how-secure-your-home-wi-fi-network
- Centre canadien pour la cybersécurité, bonnes pratiques de sécurité des routeurs : https://www.cyber.gc.ca/en/guidance/routers-cyber-security-best-practices-itsap80019
- NIST SP 800-153, sécurisation des réseaux locaux sans fil : https://csrc.nist.gov/pubs/sp/800/153/final

Les réglages exacts dépendent du matériel, des versions logicielles, de la réglementation et de l'architecture. Vérifie les documents officiels du produit réel et valide les changements en laboratoire.

Fin du cours.

## 18. Études de cas de diagnostic

Ces cas servent à répéter une démarche prudente et reproductible. La sécurité doit être vérifiée par des observations, et non déduite du seul nom du SSID ou d'une case cochée dans l'interface.

### Cas pratique 1 — Équipement ancien exige WEP

**Situation et analyse.** WEP ne peut pas être rendu moderne en cachant le SSID. Vérifie si le fabricant fournit une mise à jour, si l'équipement peut être remplacé et quel service métier en dépend. Si une exception temporaire est incontournable, isole-la et interdis l'accès aux ressources sensibles. L'objectif est de réduire la dépendance puis de supprimer l'exception à une date déterminée. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne présente pas le filtrage MAC comme une compensation cryptographique. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 2 — Invités voient les imprimantes

**Situation et analyse.** Le SSID distinct ne garantit pas la séparation. Vérifie l'adresse du client, son VLAN, les routes et les règles entre zones. Si les visiteurs doivent imprimer, publie un mécanisme contrôlé plutôt que l'ensemble du réseau d'impression. Depuis un client invité, teste les imprimantes, serveurs et interfaces qui doivent être inaccessibles, puis vérifie que l'accès Internet fonctionne. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne crée pas une règle invitée-vers-tout le LAN pour satisfaire un besoin limité. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 3 — Certificat changé sans annonce

**Situation et analyse.** Une nouvelle invite de certificat peut être un changement prévu ou une tentative d'interposition. Confirme le renouvellement auprès de l'administrateur en utilisant un canal connu, puis vérifie le nom de serveur et la chaîne attendue. Déploie un profil correct via l'outil de gestion prévu et documente le changement de certificat. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne demande pas aux utilisateurs d'accepter tous les certificats. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 4 — Connexion Wi-Fi sans adresse IP

**Situation et analyse.** La couche d'authentification peut fonctionner alors que DHCP échoue. Examine la portée d'adresses, les journaux du serveur DHCP, le relais éventuel et le VLAN auquel le client est affecté. Compare avec un client qui fonctionne dans le même segment et vérifie l'attribution après chaque correction. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne change pas le mode WPA si les preuves pointent vers DHCP. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 5 — Réseau lent à midi

**Situation et analyse.** La charge, l'encombrement des canaux, les retransmissions et le nombre de clients peuvent expliquer la lenteur. Mesure aux heures de pointe et en période calme avant de modifier la puissance ou les canaux. Répète les mesures dans les mêmes lieux après l'ajustement afin de comparer des conditions similaires. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** N'augmente pas la puissance radio à l'aveugle. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 6 — SSID suspect dans un hôtel

**Situation et analyse.** Un faux AP peut utiliser un nom familier. Demande le nom officiel au personnel par un canal fiable et désactive l'association automatique à ce réseau inconnu. Retire le profil suspect et vérifie les certificats et les services utilisés avant de transmettre des données sensibles. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne suppose pas que le mot « Free » ou un logo familier prouve la légitimité. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 7 — Caméra IoT tente d'atteindre les postes

**Situation et analyse.** Le comportement peut provenir d'une mauvaise configuration ou d'une compromission. Identifie les destinations et services nécessaires, puis isole l'équipement selon la procédure approuvée et conserve les journaux. Autorise ensuite uniquement les flux vers les services de gestion nécessaires, puis vérifie que les autres segments sont inaccessibles. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Changer le secret radio sans examiner le firmware peut laisser la cause intacte. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 8 — Administration accessible depuis Internet

**Situation et analyse.** Une interface d'administration non nécessaire augmente la surface d'attaque. Désactive l'accès distant ou impose une voie maîtrisée, des sources restreintes, une authentification robuste et des mises à jour. Teste que le réseau d'administration autorisé fonctionne et que l'accès public échoue. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Un compte avec un nom inhabituel ne remplace pas ces contrôles. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 9 — Profils Wi-Fi publics oubliés

**Situation et analyse.** Un profil enregistré peut reconnecter l'appareil à un réseau qui n'est plus digne de confiance. Révise les profils, retire ceux qui ne servent plus et désactive la connexion automatique aux réseaux inconnus. Vérifie que les réseaux approuvés continuent de fonctionner après le retrait. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne conserve pas des profils inconnus pour gagner quelques secondes lors d'une connexion. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 10 — Une seule application échoue

**Situation et analyse.** Le Wi-Fi peut être fonctionnel alors que DNS, le port, le certificat ou le service cible pose problème. Vérifie le nom, l'adresse, la route, le port et l'état de l'application avant de modifier les paramètres radio. Compare avec un client autorisé de référence et corrige le composant réellement en cause. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne conclus pas à une panne générale du Wi-Fi à partir d'une application. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 11 — Ancien employé connaît le secret

**Situation et analyse.** Un mot de passe partagé ne permet pas de révoquer un seul utilisateur. Prépare une rotation, mets à jour les appareils autorisés et communique le nouveau secret uniquement aux personnes qui en ont besoin. Confirme la reconnexion des appareils légitimes et réévalue le recours à une authentification individuelle. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne publie pas le nouveau secret sur un canal ouvert. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 12 — Point d'accès inconnu observé

**Situation et analyse.** Enregistre SSID, BSSID, canal, emplacement et heure. Compare avec l'inventaire, puis demande l'identification par l'équipe responsable. Un appareil inconnu doit être investigué, pas supposé automatiquement malveillant. Préserve les observations et applique une isolation approuvée si l'équipement est confirmé comme non autorisé. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne retire pas un équipement de production avant d'avoir vérifié sa fonction. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 13 — Transition WPA2/WPA3

**Situation et analyse.** Les appareils peuvent négocier des niveaux différents pendant une migration. Identifie les clients, leurs capacités et le mode réellement utilisé, puis fixe un plan de retrait des systèmes obsolètes. Réalise des tests avec des appareils représentatifs et documente les exceptions restant à traiter. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne prétends pas que chaque client utilise WPA3 uniquement parce que l'option est disponible. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 14 — Adresse IP présente, DNS échoue

**Situation et analyse.** Le réseau IP peut fonctionner sans que la résolution de noms soit correcte. Vérifie le résolveur reçu, la route vers lui, sa disponibilité et la règle d'accès correspondante. Teste une résolution connue et compare avec un client fonctionnel. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** N'ouvre pas tous les flux sortants pour résoudre un problème DNS. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 15 — Déconnexions lors du déplacement

**Situation et analyse.** Le roaming, le placement des AP et les cellules qui se chevauchent peuvent être en cause. Cartographie les lieux, examine le signal et les journaux d'association, puis mesure après ajustement. Teste plusieurs déplacements répétables avec le même terminal et consigne les interruptions. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne multiplie pas les AP sans étude radio. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 16 — Imprimante doit être accessible aux employés

**Situation et analyse.** Identifie les protocoles d'impression et les postes autorisés. Limite les flux depuis le segment bureautique et refuse l'accès invité sauf besoin explicitement conçu. Teste l'impression depuis un poste autorisé et l'échec depuis un poste qui ne doit pas y accéder. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne place pas l'imprimante dans un réseau ouvert à tous. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 17 — VPN sur Wi-Fi public

**Situation et analyse.** Le VPN protège le chemin vers son point de terminaison selon sa configuration, pas tous les services et le terminal lui-même. Vérifie le client officiel, le certificat, les routes et la politique de l'organisation. Confirme la connexion au VPN et continue de vérifier les domaines et avertissements du navigateur. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne désactive pas les contrôles de certificat en pensant améliorer la compatibilité. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 18 — Contrôleur inaccessible après changement

**Situation et analyse.** Une route, une règle ou un VLAN a pu être modifié. Compare l'heure de panne au changement et utilise le canal de secours pour lire l'état, puis applique le retour arrière prévu si nécessaire. Après restauration, teste l'accès depuis la source d'administration légitime et vérifie les journaux. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** N'empile pas d'autres changements sans conserver les preuves. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 19 — Échecs d'authentification répétés

**Situation et analyse.** Ils peuvent venir d'un mauvais mot de passe, d'un certificat, d'un profil obsolète ou d'une activité non autorisée. Groupe les événements par heure, source et type d'erreur avant de conclure. Vérifie les changements récents puis escalade les schémas anormaux selon la procédure. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne confonds pas le volume seul avec une preuve d'attaque. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 20 — Invité tente une ressource interne

**Situation et analyse.** Vérifie si le refus est enregistré et si la règle correspond à la bonne zone. Si la connexion réussit, inspecte le VLAN, le routage et les exceptions existantes. Teste depuis un véritable client invité après correction et conserve les résultats. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne te contente pas d'une capture d'écran de configuration : confirme le comportement réel. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 21 — Mot de passe du routeur ancien

**Situation et analyse.** La solidité du secret doit être évaluée avec les comptes, l'administration distante et les mises à jour. Prépare un changement sans perdre l'accès. Modifie le secret par l'interface locale ou le canal approuvé, sauvegarde la configuration et vérifie l'accès administrateur. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** N'utilise pas le même mot de passe que pour l'e-mail. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 22 — Firmware plus maintenu

**Situation et analyse.** Un routeur hors support peut exposer des vulnérabilités sans correctif. Vérifie la date de fin de support et planifie une migration vers un modèle maintenu. Après remplacement, revalide les SSID, la segmentation, l'administration, les règles et les appareils clients. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne considère pas qu'un appareil fonctionne donc qu'il est sûr. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 23 — WPS activé sans besoin

**Situation et analyse.** WPS simplifie l'association mais peut augmenter le risque selon la méthode et l'implémentation. Vérifie si une fonction dépend réellement de lui et désactive-le s'il est inutile. Teste l'association normale avec le mot de passe après modification. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne désactive pas d'autres contrôles pour compenser un bouton de configuration. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 24 — AP diffuse trop de SSID

**Situation et analyse.** Chaque SSID supplémentaire ajoute de la gestion et peut affecter la capacité radio. Regroupe les besoins dans une architecture de segmentation explicite plutôt que de multiplier les noms. Documente les groupes d'appareils, les VLAN et les flux puis confirme le fonctionnement de chaque catégorie. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne confonds pas nombre de SSID et niveau de sécurité. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 25 — Incident après rotation du secret

**Situation et analyse.** Certains appareils conservent l'ancien secret ou des profils incompatibles. Compare les appareils concernés, leur heure de reconnexion et les messages d'erreur. Mets à jour les appareils autorisés, vérifie l'authentification et retire les anciens profils quand c'est utile. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne réactive pas un mode obsolète pour reconnecter un seul appareil sans évaluation. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 26 — Le routeur redémarre après mise à jour

**Situation et analyse.** Vérifie l'état du firmware, la disponibilité de l'AP et la configuration restaurée avant de supposer que la mise à jour a échoué. Confirme les SSID, la sécurité, le réseau invité, les routes et l'accès administrateur depuis les appareils de test. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne coupe jamais l'alimentation pendant une mise à jour active. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 27 — Un invité communique avec un autre invité

**Situation et analyse.** Vérifie si l'isolation des clients est prise en charge et activée, et si les deux clients sont réellement dans la zone invitée. Teste un échange direct entre deux appareils de laboratoire, puis confirme le résultat attendu après modification. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne suppose pas que la segmentation inter-VLAN isole aussi les clients dans le même VLAN. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 28 — Le Wi-Fi est visible au parking

**Situation et analyse.** La couverture hors de la zone peut augmenter l'exposition mais n'est pas, à elle seule, une preuve de compromission. Mesure le signal et examine la puissance et le placement. Ajuste la couverture si c'est compatible avec les besoins et conserve le chiffrement ainsi que la segmentation. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne compte pas uniquement sur la réduction de portée pour protéger le réseau. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

### Cas pratique 29 — Journal contient des appareils inconnus

**Situation et analyse.** Une adresse inconnue peut correspondre à un terminal invité, une adresse aléatoire ou un équipement non inventorié. Compare l'heure, le BSSID, le profil et les journaux d'authentification. Identifie le propriétaire avant une action disruptive et ajoute l'équipement légitime à l'inventaire. Pour établir la cause, collecte l'heure, le terminal concerné, le SSID, l'adresse IP et les journaux disponibles. Vérifie la configuration depuis le point de vue du client et non seulement dans l'interface d'administration.

**Validation.** Ne bloque pas immédiatement une adresse sans confirmer son rôle. Après toute correction, reteste la communication nécessaire et confirme qu'un flux qui doit être interdit l'est toujours. Note le changement, son responsable et toute date de revue.

Fin du cours.