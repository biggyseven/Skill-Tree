---
node_id: troubleshooting-debutant
title: Méthodologie de dépannage - Débutant
---

# Méthodologie de dépannage - Débutant

**Niveau :** DÉBUTANT

Le dépannage réseau consiste à identifier une anomalie, à comprendre dans quelles conditions elle apparaît, à isoler sa cause probable, puis à appliquer une correction vérifiable. Il ne s'agit pas d'essayer des commandes au hasard jusqu'à ce que « ça remarche ». Une méthode rigoureuse réduit le temps d'indisponibilité, protège la configuration et permet d'expliquer ce qui s'est réellement passé.

Ce cours présente une démarche progressive utilisable sur un poste Windows, un réseau local Ethernet ou Wi-Fi, et un équipement Cisco IOS. Il suppose seulement des notions élémentaires d'adresse IP, de masque, de passerelle par défaut et de DNS. Les termes nécessaires sont définis au moment où ils apparaissent.

L'objectif du niveau Débutant est d'apprendre à observer avant d'agir. Vous allez décrire un symptôme sans tirer de conclusion trop tôt, collecter des informations utiles, tester la connectivité étape par étape, distinguer une panne locale d'un problème plus éloigné et rédiger un compte rendu compréhensible par un collègue.

Les exemples utilisent des adresses privées et des noms fictifs. Les sorties de commandes sont illustratives : elles peuvent varier selon la version de Windows, l'équipement Cisco, le système d'exploitation et la topologie. Une commande de diagnostic ne prouve pas toujours, à elle seule, qu'un service fonctionne ou qu'il est en panne.

> **Analogie** : Le dépannage réseau ressemble au diagnostic d'une fuite d'eau dans une maison. On commence par demander où l'eau manque ou fuit, on vérifie les robinets et les conduites les plus proches, puis on remonte progressivement vers la source. On ne démonte pas toute la plomberie dès le premier symptôme. Chaque test doit permettre d'écarter une hypothèse ou d'en renforcer une, sans provoquer de dommages supplémentaires.

---

## 1. La théorie et les algorithmes

### 1.1 Qu'est-ce qu'un incident réseau ?

Un incident réseau est un écart observable entre le fonctionnement attendu et le fonctionnement réel. Un utilisateur ne peut plus ouvrir un site, une imprimante disparaît, la connexion Wi-Fi se coupe, une application répond lentement ou plusieurs postes perdent l'accès à un serveur. Le symptôme est ce que l'on observe ; la cause est le mécanisme qui produit ce symptôme. Cette distinction est essentielle.

Dire « le DNS est en panne » est déjà une hypothèse. Dire « le poste peut joindre la passerelle en adresse IP, mais la résolution de `intranet.exemple.test` échoue » décrit des observations. La seconde formulation est plus utile parce qu'un autre technicien peut la vérifier.

Un même symptôme peut avoir plusieurs causes. Une page Web qui ne s'ouvre pas peut être liée à l'adresse IP du poste, au masque, à la passerelle, au DNS, au routage, à un pare-feu, à un certificat TLS, au serveur Web ou au navigateur. À l'inverse, une seule cause — par exemple une panne de commutateur — peut produire de nombreux symptômes.

Il faut donc commencer sans certitude prématurée. Le but des premiers tests n'est pas de prouver son intuition ; c'est de réduire la liste des explications possibles à l'aide d'éléments vérifiables.

### 1.2 Décrire le problème avec précision

Avant d'exécuter une commande, définissez le symptôme à l'aide de questions simples :

- **Qui est concerné ?** Un seul utilisateur, un étage, un VLAN, un site ou tout le monde ?
- **Qu'est-ce qui ne fonctionne pas ?** Un site, une application, toutes les connexions Internet, l'accès au serveur de fichiers ou la connexion physique ?
- **Depuis quand ?** Heure approximative, durée, apparition soudaine ou dégradation progressive ?
- **Dans quelles conditions ?** En filaire, en Wi-Fi, avec un VPN, depuis un réseau précis, à certaines heures ou après une modification ?
- **Qu'est-ce qui fonctionne encore ?** D'autres sites, des adresses IP, la passerelle locale, d'autres postes ou d'autres applications ?
- **Qu'est-ce qui a changé ?** Déplacement de poste, remplacement de câble, mise à jour, changement d'adresse IP, règle de sécurité ou intervention réseau ?

La question « est-ce que ça marche chez un collègue ? » est particulièrement utile. Si un seul poste est touché, on examinera d'abord ce poste et son port de connexion. Si tous les postes d'un même VLAN sont touchés, on regardera plus volontiers le commutateur, la passerelle, le DHCP, le DNS partagé ou une règle de sécurité commune.

Il faut cependant éviter de traiter ce raisonnement comme une certitude. Deux postes peuvent être dans des VLAN différents malgré leur proximité physique. Un service peut être dégradé pour une seule plage d'adresses. Une application distribuée peut dépendre d'un serveur différent selon le site. Le périmètre guide les tests ; il ne remplace pas les preuves.

### 1.3 Évaluer l'impact et l'urgence

Le dépannage commence également par la gestion de l'impact. Une panne totale de réseau dans un service critique n'a pas la même priorité qu'une imprimante non essentielle inaccessible pour une seule personne. L'évaluation doit tenir compte du nombre d'utilisateurs, de la criticité du service, de la durée et de l'existence d'un contournement sûr.

| Critère | Question à poser | Exemple |
|---|---|---|
| Étendue | Combien de personnes ou de services ? | Un poste ou tout un bâtiment |
| Criticité | Quelle activité est bloquée ? | Téléphonie d'urgence, facturation, navigation non essentielle |
| Durée | La panne est-elle continue ou intermittente ? | Depuis 10 minutes, ou quelques secondes toutes les heures |
| Contournement | Existe-t-il une solution temporaire autorisée ? | Utiliser un poste de secours ou un lien secondaire |
| Sécurité | Y a-t-il un indice de compromission ? | Des équipements inconnus ou des changements non autorisés |

Un symptôme potentiellement lié à une intrusion, à une propagation de logiciel malveillant ou à une modification non autorisée doit être transmis selon la procédure de sécurité de l'organisation. On ne réinitialise pas précipitamment des équipements si cela risque de détruire des journaux ou des éléments utiles à l'enquête.

### 1.4 Le modèle par couches : du plus proche au plus éloigné

Une communication traverse plusieurs fonctions. Le modèle OSI comporte sept couches, mais il n'est pas nécessaire de les mémoriser toutes pour commencer le dépannage. Retenez surtout la succession suivante :

1. **Physique :** alimentation, câble, connecteur, fibre, signal radio et état du lien.
2. **Liaison :** carte réseau, adresse MAC, commutateur, VLAN, association Wi-Fi et apprentissage des adresses.
3. **Réseau :** adresse IP, masque, passerelle, routage et ICMP.
4. **Transport :** TCP ou UDP, ports, établissement de session et pertes.
5. **Application :** DNS, HTTP/HTTPS, messagerie, partage de fichiers ou logiciel métier.

Cette liste est un guide, pas une loi absolue. On peut commencer par une application si le problème est clairement limité à celle-ci, ou par les journaux du système si un changement vient d'être effectué. Mais pour un débutant, vérifier méthodiquement du lien local jusqu'à l'application aide à ne pas sauter une dépendance fondamentale.

Une application peut être indisponible même quand le réseau IP fonctionne. De même, un câble peut être connecté alors que le VLAN est incorrect. Une adresse IP peut être valide et pourtant le trafic peut être bloqué par une ACL ou un pare-feu. Chaque couche ajoute des possibilités, et un test réussi à une couche ne valide pas automatiquement les couches supérieures.

### 1.5 Chemin d'une communication

Prenons un poste `192.168.10.25/24` qui veut joindre un serveur `192.168.20.50`. Comme les adresses appartiennent à deux sous-réseaux différents, le poste transmet le paquet à sa passerelle par défaut, par exemple `192.168.10.1`. Le routeur doit ensuite disposer d'une route vers `192.168.20.0/24`, et les règles de sécurité doivent autoriser le flux. Le serveur doit être allumé, écouter sur le port attendu et pouvoir retourner la réponse.

```text
[Poste client]
  IP : 192.168.10.25/24
  Passerelle : 192.168.10.1
       |
       | Ethernet / Wi-Fi
       v
[Commutateur VLAN 10]
       |
       v
[Routeur ou commutateur L3]
  Interface VLAN 10 : 192.168.10.1
  Interface VLAN 20 : 192.168.20.1
       |
       v
[Commutateur VLAN 20]
       |
       v
[Serveur : 192.168.20.50]
```

Le paquet aller n'est qu'une partie de l'échange. Le serveur doit pouvoir répondre à l'adresse source. Si sa passerelle est erronée, la requête peut arriver mais la réponse se perd. Une panne réseau n'est donc pas toujours sur le trajet aller ; elle peut apparaître au retour.

Si le serveur est dans le même sous-réseau IP que le client, le poste tente normalement de résoudre l'adresse MAC de la destination à l'aide d'ARP en IPv4, puis envoie la trame directement. Si la destination est dans un autre sous-réseau, il résout plutôt l'adresse MAC de la passerelle. Cette différence explique pourquoi une erreur de masque peut provoquer des comportements étranges : l'hôte peut croire qu'une destination distante est locale, ou l'inverse.

### 1.6 Méthode générale en sept étapes

La méthode de base proposée dans ce cours est la suivante :

1. **Décrire :** formuler le problème en une ou deux phrases observables.
2. **Délimiter :** déterminer les utilisateurs, postes, destinations et périodes affectés.
3. **Collecter :** relever la configuration, les messages d'erreur, l'heure et les tests déjà réalisés.
4. **Formuler :** établir quelques hypothèses plausibles et classées par priorité.
5. **Tester :** exécuter un test à la fois, en prédisant le résultat attendu.
6. **Corriger :** effectuer la modification minimale autorisée et documentée.
7. **Valider et clôturer :** reproduire le test initial, confirmer le service avec l'utilisateur et noter la cause ainsi que la correction.

Un test doit répondre à une question précise. Si l'on veut vérifier la connectivité IP locale, on peut tester la passerelle. Si l'on veut vérifier le DNS, on interroge un résolveur ou on compare le résultat d'une résolution de nom à une connexion par adresse IP. Si l'on veut savoir si un port TCP est accessible, un test ICMP seul ne répond pas à cette question.

> **Piège :** Un seul échec de `ping` ne prouve pas qu'une destination est inaccessible. Le pare-feu de la destination ou un équipement intermédiaire peut bloquer ICMP, alors que le service Web ou SSH reste accessible. À l'inverse, un `ping` réussi prouve seulement qu'une réponse ICMP a été reçue ; il ne garantit pas que le service applicatif fonctionne.

### 1.7 Construire et tester des hypothèses

Une hypothèse doit être assez précise pour être testée. « Le réseau est cassé » est trop vague. « Le poste n'a pas reçu de passerelle via DHCP » peut être vérifié avec `ipconfig /all`. « Le nom ne se résout pas mais l'adresse IP répond » peut être testé avec `nslookup`, puis avec une connexion vers l'adresse IP si l'application le permet.

Classez généralement les hypothèses selon trois critères : la probabilité, l'impact et le coût du test. Vérifier l'état du câble et l'adresse IP est peu coûteux. Redémarrer un commutateur de distribution est risqué et affecte potentiellement beaucoup d'utilisateurs ; ce n'est pas un premier test raisonnable. Un dépannage professionnel préfère les vérifications peu invasives qui apportent rapidement de l'information.

Gardez une trace des résultats. Une petite table évite de répéter inutilement le même test :

| Hypothèse | Test | Résultat observé | Conclusion provisoire |
|---|---|---|---|
| Le poste n'a pas de lien | Vérifier l'icône réseau et les voyants | Lien actif | Hypothèse moins probable |
| La passerelle est inaccessible | `ping 192.168.10.1` | Réponses reçues | La connectivité IP locale semble disponible |
| Le DNS échoue | `nslookup portail.exemple.test` | Délai dépassé | DNS à examiner davantage |
| Le serveur Web ne répond pas | Tester TCP/443 | Connexion réussie | Le port TCP est accessible ; reste à vérifier HTTPS et l'application |

Ces résultats sont illustratifs. Un test peut être influencé par un cache, un proxy, une règle spécifique à la source ou une réponse partielle. Écrivez « semble disponible » plutôt que « fonctionne à 100 % » tant que la portée du test est limitée.

### 1.8 Observation, modification et risque

Les commandes de dépannage n'ont pas toutes le même niveau de risque. Les commandes d'observation affichent un état sans changer volontairement la configuration : `show ip interface brief`, `ipconfig /all`, `ping`, `tracert` ou `show logging`. Certaines commandes génèrent toutefois du trafic et peuvent être mal utilisées sur un réseau fragile si elles sont lancées à grande échelle.

Les commandes de modification changent un état : désactivation d'une interface, suppression d'une route, modification d'une ACL, renouvellement forcé d'un bail, redémarrage d'un service ou effacement de compteurs. Elles peuvent couper la communication ou supprimer des éléments de preuve. Avant de les utiliser, il faut comprendre leur effet, disposer de l'autorisation nécessaire et prévoir une procédure de retour arrière.

> **Danger :** Ne lancez pas de commandes comme `reload`, `erase startup-config`, `clear ip route *`, la suppression d'une ACL ou la désactivation d'une interface sur un équipement de production simplement pour voir si le problème disparaît. Elles peuvent interrompre le réseau ou effacer une configuration. Commencez par des commandes de lecture, demandez une validation et consignez toute modification.

### 1.9 Mesures de référence et intermittence

La performance attendue sert de référence. Si une application est d'ordinaire accessible en moins d'une seconde et met soudainement 20 secondes, le service n'est peut-être pas complètement indisponible, mais il est dégradé. Relevez la latence, les pertes, le moment où le problème survient, le nombre de postes touchés et le type de trafic concerné.

Une panne intermittente demande plus de patience qu'une panne permanente. Notez les heures, la fréquence, la durée et les événements associés : réunion vidéo, sauvegarde nocturne, changement de point d'accès, expiration d'un bail DHCP, surcharge du lien ou mise à jour. Un test unique réussi à 10 h ne contredit pas forcément une plainte qui survient à 10 h 05 tous les jours.

Pour observer un problème intermittent, privilégiez des contrôles répétés et limités dans le temps. Évitez les boucles de tests agressives. Si vous enregistrez des mesures, indiquez la destination testée, l'intervalle, la durée et la source. Une statistique de latence sans ces informations est difficile à interpréter.

### 1.10 Les limites des outils les plus courants

- `ping` teste une réponse ICMP, pas une application complète.
- `tracert` et `traceroute` estiment le chemin au moyen de réponses aux paquets à durée de vie limitée ; certains routeurs ne répondent pas et apparaissent sous forme d'astérisques.
- `nslookup` vérifie la résolution DNS à l'aide d'un serveur interrogé, mais peut ne pas reproduire exactement le comportement du résolveur système, du navigateur ou d'un proxy.
- `ipconfig /all` montre la configuration de l'interface locale, mais ne garantit pas que le réseau en amont utilise les bonnes routes ou règles.
- `show interfaces` sur Cisco aide à observer l'état et les compteurs d'une interface, mais un compteur isolé ne suffit pas toujours à conclure à une panne.
- Un voyant vert indique souvent un lien actif, pas que le VLAN, l'adressage ou le service applicatif est correct.

Le rôle du technicien est de combiner les indices. Aucune commande ne donne un verdict universel. La conclusion doit correspondre exactement à ce que le test mesure.

### 1.11 Algorithme de diagnostic élémentaire

```text
DÉBUT
  Décrire le symptôme et son impact
  Déterminer si un seul poste ou plusieurs sont concernés
  Vérifier alimentation, câble ou association Wi-Fi
  Relever adresse IP, masque, passerelle et DNS
  SI configuration absente ou incohérente
      Vérifier DHCP, VLAN et configuration du poste
  SINON
      Tester la passerelle locale
      SI passerelle inaccessible
          Examiner lien, VLAN, adresse, masque et passerelle
      SINON
          Tester une destination IP autorisée
          SI IP distante inaccessible
              Examiner route, pare-feu, chemin et destination
          SINON
              Tester la résolution du nom
              SI résolution en échec
                  Examiner serveur DNS, suffixe et enregistrement
              SINON
                  Tester le port et l'application
                  Examiner service, authentification, proxy et TLS
  Appliquer une correction approuvée
  Refaire le test initial et vérifier les effets secondaires
  Documenter les résultats et clôturer
FIN
```

Cet algorithme ne couvre pas toutes les situations. Il montre une manière d'avancer sans sauter directement à la modification. Si le problème touche un service critique ou semble lié à la sécurité, appliquez en priorité la procédure d'incident correspondante et faites intervenir le niveau de support adapté.

### 1.12 Savoir quand arrêter et escalader

Un débutant n'est pas obligé de résoudre seul tous les incidents. Il doit surtout savoir reconnaître les limites de son périmètre. Escaladez lorsque l'incident dépasse vos droits, touche plusieurs équipements de cœur, nécessite une modification à fort impact, semble lié à la sécurité, persiste malgré des tests documentés ou concerne une plateforme que vous ne maîtrisez pas.

Une bonne escalade comprend le symptôme exact, le périmètre, l'heure de début, les adresses IP utiles, les commandes exécutées et leurs résultats, les modifications éventuellement faites et les éléments qui restent inconnus. Dire « Internet ne marche pas » oblige le niveau suivant à recommencer le diagnostic. Dire « depuis 10 h 14, trois postes du VLAN 30 atteignent leur passerelle mais pas le serveur DNS 10.30.0.53 ; les autres VLANs ne semblent pas touchés » fournit un vrai point de départ.

L'escalade n'est pas un échec. Elle est un mécanisme de contrôle du risque. Il vaut mieux transmettre tôt un incident important que tenter une correction non maîtrisée qui transforme une panne limitée en coupure générale.

---

## 2. Configuration et pratique

### 2.1 Préparer une fiche de diagnostic

Avant toute action, remplissez une fiche simple. Elle peut être un ticket dans l'outil de support, un formulaire ou un document partagé autorisé. Ne stockez pas les mots de passe, les secrets partagés, les clés privées, les jetons de session ou des données personnelles inutiles dans le compte rendu.

```text
Numéro du ticket : INC-2026-0101 (exemple)
Date et heure du signalement :
Utilisateur / service concerné :
Équipement / nom du poste :
Emplacement / VLAN si connu :
Symptôme exact :
Début et fréquence :
Impact métier :
Ce qui fonctionne encore :
Dernier changement connu :
Tests et résultats :
Hypothèse actuelle :
Action autorisée / responsable :
Résultat après correction :
Cause confirmée ou encore inconnue :
```

Le nom de l'utilisateur peut être nécessaire au support, mais ne doit pas être recopié dans des canaux publics sans raison. Suivez la politique de conservation des tickets. Pour un laboratoire, remplacez les identifiants personnels par des noms fictifs.

### 2.2 Les premières vérifications sur Windows

Commencez par vérifier les éléments évidents : le poste est-il allumé, le mode avion est-il activé, le câble est-il bien branché, la connexion Wi-Fi est-elle associée au bon réseau, et une fenêtre de portail captif est-elle attendue ? Si une station d'accueil USB ou un adaptateur externe est utilisé, notez-le également. Ne supposez pas qu'un lien actif prouve que le réseau logique est correct.

Ouvrez l'invite de commandes ou PowerShell. Dans un contexte de support, suivez les règles de votre organisation concernant les droits administrateur. Beaucoup de commandes de lecture ne nécessitent pas d'élévation.

#### a) Afficher la configuration IP

```powershell
ipconfig /all
```

Repérez l'adaptateur réellement utilisé. Un poste peut avoir Ethernet, Wi-Fi, VPN, Bluetooth et des interfaces virtuelles. Regardez :

- **IPv4 Address / Adresse IPv4 :** adresse attribuée à l'interface.
- **Subnet Mask / Masque :** détermine la partie réseau et la partie hôte.
- **Default Gateway / Passerelle par défaut :** route utilisée pour les destinations hors du sous-réseau local.
- **DNS Servers / Serveurs DNS :** serveurs interrogés pour résoudre les noms.
- **DHCP Enabled / DHCP activé :** indique si l'adresse est normalement obtenue par DHCP.
- **Lease Obtained / Lease Expires :** informations sur le bail DHCP lorsque disponibles.

Une adresse IPv4 automatique de la plage `169.254.0.0/16` peut indiquer que le poste n'a pas obtenu de bail DHCP. Ce n'est pas une preuve absolue d'une panne du serveur DHCP : le poste peut être sur un réseau isolé, configuré spécialement, ou présenter une autre anomalie. Vérifiez aussi le lien, le VLAN, le serveur, le relais DHCP et la présence d'adresses disponibles.

> **Astuce :** Comparez la configuration avec celle d'un poste fonctionnel situé dans le même VLAN et utilisant le même type d'accès. Ne copiez pas aveuglément l'adresse IP d'un collègue : cela peut créer un conflit. Comparez le sous-réseau, la passerelle, les serveurs DNS et le mode DHCP plutôt que de dupliquer toutes les valeurs.

#### b) Vérifier la carte réseau

```powershell
Get-NetAdapter
Get-NetIPConfiguration
```

`Get-NetAdapter` affiche les interfaces et leur état. `Get-NetIPConfiguration` présente les informations IP principales. Si l'interface utilisée est `Disconnected`, cherchez d'abord le câble, le port, le signal Wi-Fi, l'adaptateur ou son pilote. Si elle est active mais que l'adresse est absente, poursuivez vers DHCP et la configuration IP.

Sur certaines versions ou éditions de Windows, les champs peuvent être différents. Une interface virtuelle de VPN peut aussi modifier les routes ou le DNS. Si le problème n'apparaît qu'après la connexion au VPN, comparez prudemment l'état avant/après et consultez l'équipe responsable du VPN.

#### c) Tester la passerelle locale

```powershell
ping 192.168.10.1
```

Remplacez l'adresse par la passerelle réelle. Quatre réponses indiquent que la destination a répondu aux requêtes ICMP pendant ce test. Un délai dépassé peut correspondre à un problème de liaison, de VLAN, d'adressage ou de passerelle, mais aussi à une politique qui filtre ICMP.

Vérifiez également que l'adresse de passerelle appartient au sous-réseau attendu. Un masque trop large ou trop étroit peut amener le poste à prendre une mauvaise décision de routage. Si vous ne connaissez pas les valeurs attendues, cherchez le plan d'adressage ou demandez au responsable réseau plutôt que de deviner.

#### d) Tester une IP distante et un nom DNS

```powershell
ping 1.1.1.1
nslookup example.com
```

Ces destinations ne sont que des exemples publics et peuvent être interdites par la politique réseau. Dans un environnement d'entreprise, utilisez d'abord une destination interne prévue pour les tests. Le ping d'une adresse publique peut échouer alors que l'accès Web fonctionne, notamment si ICMP est filtré.

`nslookup` interroge le système de noms de domaine. Notez le serveur utilisé, le nom interrogé, la réponse et l'erreur éventuelle. Une réponse `Non-existent domain` indique généralement que le serveur affirme que le nom n'existe pas dans la zone interrogée ; un timeout signifie que la requête n'a pas obtenu de réponse à temps. Les deux erreurs ne sont pas équivalentes.

#### e) Examiner le chemin et les routes

```powershell
tracert 10.20.0.50
route print
```

`tracert` montre les routeurs qui répondent aux sondes du chemin vers la destination. Des astérisques ne signifient pas forcément que le chemin s'arrête à cet endroit : un routeur peut ne pas répondre aux sondes, tout en transférant les paquets ordinaires. `route print` permet de repérer la table de routage locale et la route par défaut.

N'affichez pas de données sensibles dans une capture destinée à un forum public. Les routes, les noms de domaine, les adresses internes et les noms d'hôtes peuvent révéler l'architecture de l'organisation.

#### f) Tester un port TCP

```powershell
Test-NetConnection 10.20.0.50 -Port 443
```

Cette commande aide à vérifier si une connexion TCP vers le port 443 peut être établie. Elle ne valide pas à elle seule la page Web, le certificat, l'authentification ou le contenu retourné par HTTPS. Si le port est accessible mais que le site échoue, poursuivez vers TLS, le proxy, le serveur Web et l'application.

### 2.3 Ordre conseillé des tests côté poste

Pour un problème générique de connectivité, appliquez les tests dans cet ordre, en adaptant la liste à la plainte réelle :

| Étape | Test | Question traitée |
|---|---|---|
| 1 | Contrôler câble, Wi-Fi et état de l'interface | Le poste a-t-il un lien physique ou radio ? |
| 2 | `ipconfig /all` | Dispose-t-il d'une configuration cohérente ? |
| 3 | Ping de la passerelle | Peut-il communiquer avec le premier saut IP ? |
| 4 | Tester une destination IP interne autorisée | Le routage au-delà du réseau local fonctionne-t-il ? |
| 5 | `nslookup` du nom concerné | La résolution de nom fonctionne-t-elle ? |
| 6 | Tester le port du service | Le transport vers le service est-il accessible ? |
| 7 | Ouvrir l'application et lire ses erreurs | Le service applicatif répond-il correctement ? |
| 8 | Comparer avec un poste ou un réseau de référence | Le problème est-il local ou partagé ? |

Ne lancez pas mécaniquement toute la séquence quand le symptôme est spécifique. Si seule une imprimante est concernée, l'adresse et le port de l'imprimante sont prioritaires. Si un message de certificat apparaît dans le navigateur, il faut étudier le nom du certificat, sa date et la chaîne de confiance au lieu d'accuser immédiatement le DNS.

### 2.4 Dépannage élémentaire sur un commutateur Cisco

Sur un commutateur Cisco IOS ou IOS XE, connectez-vous avec un compte autorisé. Les commandes ci-dessous sont principalement des commandes de lecture. Les noms et détails de sortie varient selon le modèle et la version. Si l'équipement est géré par une plateforme centrale, les pratiques locales de gestion peuvent prévaloir.

```text
show clock
show version
show interfaces status
show interfaces gigabitEthernet 1/0/10
show vlan brief
show mac address-table dynamic
show ip interface brief
show logging
```

- `show clock` aide à associer les observations à une heure, sous réserve que l'horloge soit correcte.
- `show version` indique notamment la plateforme et la version logicielle.
- `show interfaces status` donne un aperçu de l'état des ports.
- `show interfaces ...` affiche les statistiques du port ciblé : état, débit, duplex et compteurs d'erreurs selon la plateforme.
- `show vlan brief` permet de vérifier l'existence des VLAN et l'affectation des ports d'accès.
- `show mac address-table dynamic` aide à voir où le commutateur apprend les adresses MAC.
- `show ip interface brief` est utile sur un équipement de couche 3 pour l'état des interfaces IP.
- `show logging` affiche une partie des messages de journalisation disponibles en mémoire.

Si un port apparaît `notconnect`, vérifiez l'équipement connecté, le câble et la négociation du lien. Si le port est actif mais affecté au mauvais VLAN, un poste peut avoir une connectivité partielle ou aucune connectivité. Avant de modifier le VLAN d'un port, vérifiez le plan réseau et confirmez qu'il ne s'agit pas d'un port trunk ou d'un équipement particulier.

Pour un poste qui ne communique pas avec un autre poste du même VLAN, vérifiez que la table MAC apprend les deux adresses sur les ports attendus. L'absence d'une adresse ne prouve pas toujours que l'équipement est éteint : aucune trame récente n'a peut-être été envoyée, l'adresse a pu expirer de la table, ou le trafic passe par un autre chemin.

### 2.5 Diagnostic élémentaire d'une interface de routeur Cisco

```text
show ip interface brief
show interfaces gigabitEthernet 0/0
show ip route
show arp
show access-lists
```

`show ip interface brief` donne un aperçu compact des interfaces IP et de leur état. `up/up` signifie que l'interface et le protocole de ligne sont déclarés actifs, mais cela ne garantit pas que le routage ou la sécurité est correct. `administratively down` indique souvent que l'interface a été désactivée par configuration. `show ip route` présente les routes connues par l'équipement. `show arp` affiche les associations IPv4/MAC apprises. `show access-lists` permet de vérifier des listes de contrôle d'accès présentes sur l'équipement.

Une route vers un réseau de destination doit exister sur le routeur qui transfère le paquet. La route retour doit également être correcte. Si le client envoie vers le serveur mais que celui-ci renvoie par un autre routeur qui ne connaît pas le réseau source ou applique une règle différente, la session peut échouer de manière asymétrique.

Les commandes de dépannage ne doivent jamais remplacer la vérification du contexte. Si un routeur possède plusieurs tables de routage, VRF, tunnels VPN ou politiques de routage, une commande générale peut ne pas montrer exactement le chemin utilisé par le trafic concerné. Au niveau débutant, notez ce que vous savez et escaladez pour l'analyse de ces fonctionnalités avancées.

### 2.6 Exemple de laboratoire : un poste n'accède pas à Internet

**Topologie fictive :** un PC `192.168.10.25/24`, une passerelle `192.168.10.1`, un serveur DNS interne `192.168.10.10` et une connexion Internet via le routeur de site.

**Étape 1 — Décrire.** L'utilisateur indique que les sites Web ne s'ouvrent plus depuis environ 10 h. Demandez si le problème touche tous les sites, si une application interne fonctionne encore et si ses collègues rencontrent la même anomalie.

**Étape 2 — Observer le poste.** Avec `ipconfig /all`, relevez l'adresse, le masque, la passerelle et le DNS de l'interface active. Si l'adresse est absente ou dans un réseau inattendu, cherchez en premier lieu un problème d'adressage ou de DHCP.

**Étape 3 — Tester le réseau local.** Lancez un ping de la passerelle réelle. Si elle répond, notez le résultat et poursuivez. Si elle ne répond pas, vérifiez le lien, le VLAN, le masque et la configuration de la passerelle avant de conclure à une panne Internet.

**Étape 4 — Tester une destination IP autorisée.** Utilisez une cible de référence choisie par l'organisation. Une réponse indique qu'un chemin IP existe pour ce flux ICMP. L'absence de réponse demande d'examiner les routes et les règles ; elle ne permet pas, seule, de désigner le fournisseur d'accès comme responsable.

**Étape 5 — Tester le DNS.** Interrogez le serveur DNS configuré avec `nslookup`. Si la résolution interne échoue, comparez le résultat avec un poste fonctionnel et examinez l'accessibilité du résolveur. Évitez de modifier le DNS du poste vers un serveur public sans autorisation : cela pourrait contourner les règles de sécurité ou rendre inaccessibles les noms internes.

**Étape 6 — Tester le port et le navigateur.** Si une adresse IP répond mais que le site ne s'ouvre pas, testez le port TCP prévu, puis examinez le navigateur, le proxy, les certificats et le serveur. Les sites qui utilisent un nom virtuel ou HTTPS peuvent ne pas fonctionner correctement quand on saisit simplement une adresse IP dans le navigateur.

**Étape 7 — Corriger et valider.** Une fois la cause confirmée, appliquez la correction minimale autorisée. Refaites les tests qui avaient échoué, vérifiez les services internes et demandez à l'utilisateur de reproduire son action initiale. Consignez le résultat et toute limitation restante.

```text
PC 192.168.10.25
       |
       | VLAN 10
       v
Passerelle 192.168.10.1
       |
       +----> DNS interne 192.168.10.10
       |
       v
Routeur du site / pare-feu
       |
       v
Réseau externe / Internet
```

### 2.7 Exemple de laboratoire : un seul poste n'obtient pas d'adresse IP

Supposons que cinq postes soient connectés au même commutateur, mais qu'un seul affiche une adresse `169.254.x.x`. Les autres ont des adresses valides.

1. Vérifiez que le poste est branché sur le bon port et que le lien est actif.
2. Vérifiez si le poste est configuré pour obtenir une adresse automatiquement ou s'il doit utiliser une adresse statique documentée.
3. Comparez le VLAN du port à celui des autres postes comparables.
4. Vérifiez la présence du service DHCP, du relais DHCP éventuel et de ressources d'adresses disponibles si plusieurs postes sont concernés.
5. Si les règles locales l'autorisent, `ipconfig /release` puis `ipconfig /renew` peuvent aider à renouveler le bail. Ces commandes modifient temporairement la configuration IP du poste et coupent potentiellement ses connexions ; ne les exécutez pas pendant une tâche critique sans accord.
6. Si l'échec ne concerne que ce poste, vérifiez aussi le pilote, les paramètres de sécurité réseau et un éventuel conflit ou blocage d'accès.

Si tous les postes d'un VLAN échouent en même temps, l'hypothèse d'un incident partagé devient plus forte. Le serveur DHCP peut être indisponible, le relais mal configuré, le VLAN incorrect ou le pool épuisé. Le périmètre permet de choisir le prochain point de contrôle.

### 2.8 Exemple de laboratoire : le nom ne se résout pas

Un utilisateur peut ouvrir `https://192.168.20.50` dans un outil adapté, mais `https://portail.exemple.test` échoue. Cet indice suggère un problème de résolution de nom, sans le prouver complètement : le serveur Web peut héberger plusieurs sites et dépendre du nom demandé, et TLS peut vérifier le nom d'hôte.

Exécutez :

```powershell
ipconfig /all
nslookup portail.exemple.test
```

Notez quel serveur DNS est interrogé. Vérifiez ensuite si le problème concerne tous les noms ou seulement un enregistrement. Un nom interne peut ne pas exister sur un résolveur public ; utiliser un DNS externe peut donc aggraver le symptôme. L'enregistrement DNS peut être manquant, obsolète ou associé à une adresse erronée, ou encore la requête peut être bloquée en transit.

Ne corrigez pas le problème en ajoutant durablement une entrée au fichier `hosts` de chaque poste, sauf procédure approuvée et temporaire. Cette approche masque souvent la cause centrale et crée des divergences entre les appareils.

### 2.9 Comparer deux postes de manière utile

La comparaison est un outil puissant, à condition de choisir deux postes équivalents. Comparez la même application, la même destination, le même moment et si possible le même VLAN. Les différences utiles peuvent inclure l'adresse IP, le masque, la passerelle, les DNS, le nom de l'interface, l'état du VPN, le proxy et l'heure des dernières modifications.

Évitez de comparer un poste filaire à un poste Wi-Fi si vous essayez de diagnostiquer un problème propre à un VLAN filaire, ou un poste sans VPN à un poste qui utilise un tunnel. L'environnement doit être suffisamment proche pour que la différence observée ait une valeur diagnostique.

Un poste fonctionnel est une référence, pas une garantie que sa propre configuration est idéale. Il peut fonctionner grâce à un cache, un ancien bail, une route spécifique ou une application déjà ouverte. Une comparaison doit faire apparaître des hypothèses ; elle ne remplace pas la validation sur le poste affecté.

### 2.10 Mesurer la connectivité et comprendre les messages

Lors d'un ping, les principaux résultats courants sont : réponse reçue, délai dépassé, hôte inaccessible et nom introuvable. Ces messages orientent l'analyse mais ne donnent pas tous une cause précise.

- **Réponse reçue :** une réponse ICMP est revenue de la destination ou d'un équipement qui répond pour elle.
- **Délai dépassé :** aucune réponse n'est arrivée dans le délai prévu. Cela peut venir d'une perte, d'un filtrage, d'une congestion ou d'une destination qui ne répond pas à ICMP.
- **Destination inaccessible :** un hôte ou routeur indique qu'il ne peut pas acheminer le paquet, ce qui constitue un indice sur le chemin ou le réseau de destination.
- **Nom introuvable :** le programme n'a pas pu résoudre le nom ; il faut distinguer le cache, le résolveur configuré, le nom demandé et le type d'erreur reçu.

Enregistrez le message exact plutôt que d'écrire seulement « ping KO ». Si l'erreur disparaît en répétant le test, notez le nombre d'essais et l'heure : une anomalie intermittente ne doit pas être transformée en conclusion absolue.

### 2.11 Laboratoire de lecture sur Cisco

Considérez un port utilisateur `GigabitEthernet1/0/10`. Le poste signale qu'il n'accède pas au serveur de fichiers. Commencez par des commandes de lecture :

```text
show interfaces status
show interfaces gigabitEthernet 1/0/10
show vlan brief
show mac address-table dynamic
show logging
```

Posez-vous les questions suivantes :

- Le port est-il actif ?
- Le port est-il configuré comme port d'accès ou trunk, conformément à la conception ?
- Le VLAN attendu existe-t-il et le port en fait-il partie ?
- L'adresse MAC du poste est-elle apprise sur ce port ?
- Les compteurs d'erreurs évoluent-ils ?
- Les journaux contiennent-ils un message correspondant à l'heure du problème ?

Un compteur d'erreurs non nul peut provenir d'un incident antérieur ; observez son évolution si c'est autorisé et possible. Ne remettez pas les compteurs à zéro simplement pour faire disparaître une valeur gênante, car elle peut être utile au diagnostic. Si vous devez comparer des compteurs dans le temps, notez les valeurs et l'intervalle d'observation.

> **Astuce :** Avant de quitter une session d'équipement, copiez les informations nécessaires dans le ticket selon les règles de l'organisation. Les sorties des commandes `show` peuvent contenir des détails internes ; conservez-les dans un emplacement autorisé et évitez de publier une configuration complète sur un forum public.

### 2.12 Créer un plan de test avant la correction

Un plan de test liste ce qui doit fonctionner avant et après le changement. Pour une panne d'accès à une application Web interne, il peut contenir :

| Test | Avant correction | Résultat attendu après correction |
|---|---|---|
| Le poste conserve une configuration IP valide | À relever | Configuration conforme au plan d'adressage |
| Le poste joint la passerelle | Échec ou résultat à relever | Résultat conforme à la politique ICMP du réseau |
| Le nom de l'application se résout | Échec ou adresse incorrecte | Adresse attendue retournée par le DNS approprié |
| Le port TCP attendu est accessible | Échec ou état inconnu | Connexion TCP réussie si le service est prévu disponible |
| L'application s'ouvre avec l'identité autorisée | Échec | Application opérationnelle, sans contournement de sécurité |
| Les autres applications restent fonctionnelles | À vérifier | Pas de régression détectée |

La correction n'est pas terminée parce qu'une commande affiche une réponse positive. Il faut refaire le test d'origine, confirmer que les dépendances principales fonctionnent et s'assurer que la réparation n'a pas créé une nouvelle panne ailleurs.

---

## 3. Dépannage et sécurité

### 3.1 Symptômes fréquents et premières hypothèses

Le tableau suivant aide à choisir un point de départ. Il ne faut pas l'utiliser comme une table de vérité : une panne inhabituelle peut avoir une cause différente.

| Symptôme | Première vérification | Hypothèses courantes |
|---|---|---|
| Aucun réseau sur un seul poste | Câble/Wi-Fi, état de l'interface, `ipconfig /all` | Carte, câble, VLAN, DHCP, configuration locale |
| Adresse en `169.254.x.x` | DHCP activé, lien et VLAN | Serveur ou relais DHCP inaccessible, pool épuisé, poste mal connecté |
| La passerelle ne répond pas | IP/masque, lien, VLAN | Mauvais réseau IP, port incorrect, ICMP bloqué, passerelle indisponible |
| Les sites par nom échouent | `nslookup` | DNS, suffixe, enregistrement, cache, résolution liée au VPN |
| L'adresse IP fonctionne mais pas l'application | Port TCP, proxy et journal de l'application | Port bloqué, service arrêté, TLS, authentification, mauvais nom d'hôte |
| Le réseau est lent à certaines heures | Mesures à plusieurs moments, portée de l'impact | Congestion, Wi-Fi, sauvegardes, serveurs sollicités, pertes ou latence |
| Une imprimante est inaccessible | Adresse, état du port et du service d'impression | Changement IP, conflit, VLAN, ACL, pilote ou file bloquée |
| Le VPN se connecte, mais une ressource manque | Routes, DNS, autorisations VPN | Route absente, split tunneling, chevauchement de sous-réseaux, politique d'accès |

La bonne pratique est d'examiner d'abord les causes communes au périmètre touché. Si tous les utilisateurs d'un même étage échouent, il est peu probable que chaque carte réseau soit tombée en panne simultanément. Une cause commune — commutateur, liaison montante, VLAN ou service partagé — mérite alors une attention prioritaire.

### 3.2 DHCP : distinguer le poste du service

Le protocole DHCP permet à un client de recevoir des paramètres réseau comme une adresse IP, un masque, une passerelle et des serveurs DNS. Le client envoie des messages pour découvrir un serveur, proposer ou demander une adresse, puis obtenir une confirmation. En pratique, les messages initiaux sont généralement diffusés sur le réseau local ; un relais DHCP peut être nécessaire pour atteindre un serveur dans un autre sous-réseau.

Si une machine ne reçoit pas d'adresse, procédez par échelle :

1. Vérifiez le lien et l'interface utilisés.
2. Vérifiez si les autres appareils du même VLAN obtiennent un bail.
3. Confirmez le VLAN et le plan d'adressage.
4. Faites vérifier par la personne autorisée le service DHCP, le pool d'adresses, les exclusions et les journaux.
5. Si le serveur est distant, vérifiez le relais DHCP et le routage associé.
6. Vérifiez les restrictions d'accès au réseau, les contrôles de sécurité de port et les éventuelles règles de filtrage.

Ne configurez pas au hasard une adresse IP statique pour contourner un DHCP en panne. Cela peut créer un conflit, contourner les règles d'attribution, utiliser une mauvaise passerelle ou donner l'illusion que le problème est résolu alors que d'autres postes restent en panne. Toute adresse statique doit être autorisée et issue du plan d'adressage.

### 3.3 DNS : vérifier la chaîne de résolution

Le DNS traduit des noms en informations, souvent des adresses IP. Plusieurs composants peuvent intervenir : le résolveur du poste, un cache, le serveur DNS interne, les redirecteurs, les zones DNS et les serveurs faisant autorité. Le nom peut exister dans une zone interne mais pas sur les résolveurs publics.

Commencez par connaître le nom exact, le type de résultat attendu et le serveur configuré. Comparez le résultat sur le poste affecté et sur un poste comparable. Si l'adresse retournée est erronée, notez-la au lieu de seulement dire que « le DNS ne marche pas ». Si le nom se résout, mais que le service est inaccessible, passez ensuite à la connectivité, au port et à l'application.

Les causes possibles comprennent un enregistrement manquant ou obsolète, un DNS inaccessible, un suffixe mal défini, un cache local ancien, un problème d'accès au VPN ou une différence entre DNS interne et public. La commande `ipconfig /flushdns` vide le cache DNS local ; elle peut être utile dans un cas précis, mais il faut d'abord conserver le résultat des tests et vérifier que la politique interne autorise cette action. Vider le cache sans diagnostic ne corrige pas un enregistrement central incorrect.

### 3.4 Adresse IP, masque et passerelle

Une adresse IP identifie une interface dans un réseau logique. Le masque ou le préfixe détermine la partie réseau. La passerelle par défaut est le prochain saut utilisé pour les destinations qui ne sont pas considérées comme locales. Une erreur sur l'un de ces champs peut empêcher certaines destinations d'être joignables tout en laissant fonctionner d'autres communications.

Pour diagnostiquer ce cas, comparez les valeurs à un plan d'adressage fiable. Vérifiez que l'adresse appartient au bon sous-réseau, que la passerelle est cohérente et qu'aucune autre machine n'utilise la même adresse. Un conflit IP peut produire des interruptions intermittentes : différentes réponses ARP peuvent pointer vers des adresses MAC différentes.

Ne modifiez pas un masque parce qu'une formule trouvée sur Internet semble « plus logique ». Le masque doit correspondre à la conception du VLAN et au routage existant. Une modification locale peut créer un conflit ou changer la façon dont le poste choisit son prochain saut.

### 3.5 Couches 1 et 2 : lien, câble, VLAN et Wi-Fi

Les problèmes de couche physique comprennent un câble endommagé, un connecteur mal inséré, une fibre inversée ou sale, une alimentation manquante, une carte défaillante ou un signal radio faible. Les symptômes incluent un lien absent, des déconnexions fréquentes, des erreurs physiques, un débit anormal ou une connexion qui varie quand le câble bouge.

Les problèmes de couche liaison comprennent un VLAN inadapté, une négociation incorrecte, une table MAC incohérente, une association Wi-Fi au mauvais SSID ou une politique de sécurité du port. Une interface peut être `up` alors que le poste est dans un VLAN qui ne lui permet pas d'atteindre sa passerelle attendue.

Inspectez visuellement ce que vous êtes autorisé à manipuler. Ne retirez pas une fibre ou un câble critique sans autorisation. Sur un réseau Wi-Fi, vérifiez le bon SSID, l'état de l'authentification, le niveau du signal et si d'autres clients sont touchés. La puissance du signal n'est pas la seule cause possible : interférences, saturation de canal, itinérance ou politiques d'accès peuvent aussi intervenir.

### 3.6 Routage et chemin de retour

Le routage détermine par où un paquet doit être envoyé pour atteindre son réseau de destination. Un routeur utilise sa table de routage pour choisir le prochain saut. Si aucune route appropriée n'existe, le paquet peut être abandonné ou une erreur peut être retournée. La destination doit également posséder une route de retour, soit directement connectée, soit via une passerelle correcte.

Un test de chemin aide à repérer l'endroit où les réponses cessent d'être visibles, mais il ne localise pas toujours la panne. Certains routeurs ne répondent pas aux sondes traceroute alors qu'ils transfèrent le trafic. Comparez les résultats à partir de plusieurs sources si vous en avez l'autorisation, et recherchez les différences de réseau source, de VPN ou de VLAN.

Une panne de routage peut être causée par une route absente, une route par défaut incorrecte, une interface de sortie inactive, une route plus spécifique, un chevauchement de sous-réseaux ou une politique de routage. Si les équipements utilisent BGP, OSPF, VRF ou des tunnels, l'analyse dépasse souvent le niveau Débutant : collectez les faits et escaladez sans changer les routes au hasard.

### 3.7 Pare-feu et listes de contrôle d'accès

Un pare-feu ou une ACL peut autoriser certains flux et en refuser d'autres. Une connexion peut échouer alors que l'adressage et le routage sont corrects. Le test doit préciser le flux : adresse source, destination, protocole et port. « Le port 443 est bloqué » est trop vague si l'on ne sait pas de quelle source, vers quelle destination et à quelle heure.

Si la connectivité IP générale fonctionne mais qu'une application spécifique échoue, vérifiez avec l'équipe responsable si le port attendu est autorisé. Ne désactivez jamais un pare-feu globalement pour « tester ». Une exception temporaire doit avoir une portée minimale, être approuvée, journalisée et retirée après validation si elle n'est pas nécessaire.

Les règles de sécurité peuvent aussi être appliquées à différents endroits : poste, commutateur, routeur, pare-feu central, système hôte ou application. Un échec ne prouve pas quelle règle bloque. Les journaux de décision peuvent aider si leur accès est autorisé et si l'horloge est synchronisée.

### 3.8 Performance : lenteur, pertes et latence

La lenteur est un symptôme difficile parce qu'elle peut venir du réseau, du poste, du serveur ou de l'application. Il faut préciser ce qui est lent : ouverture initiale, transfert d'un gros fichier, visioconférence, résolution DNS, chargement d'une page ou seulement un logiciel particulier.

Mesurez à plusieurs moments et comparez, si possible, avec une destination locale et une destination distante. Une latence élevée jusqu'à la passerelle locale peut orienter vers l'accès local, le Wi-Fi ou le poste. Une passerelle qui répond vite n'exclut pas une congestion plus loin. Une perte de paquets occasionnelle vers une destination ne permet pas de conclure à un lien défectueux sans tenir compte du filtrage ICMP et du comportement du chemin.

Évitez les tests très fréquents ou très volumineux sur un réseau de production sans autorisation. Des tests de débit mal dimensionnés peuvent charger une liaison déjà dégradée. Pour un diagnostic de niveau Débutant, notez d'abord la latence approximative, la période, l'étendue et les applications affectées, puis transmettez ces informations au responsable réseau.

### 3.9 MTU et problèmes qui n'affectent que certains flux

La MTU définit la taille maximale d'un paquet ou d'une trame au niveau concerné. Si un chemin contient un tunnel VPN ou une encapsulation, la taille utilisable peut être réduite. Une mauvaise gestion de la fragmentation ou de la découverte de MTU peut créer des symptômes trompeurs : de petites requêtes passent, mais certains transferts ou pages restent bloqués.

Un débutant doit surtout reconnaître le motif : seuls certains sites, téléchargements ou applications échouent ; la connexion générale semble active ; le problème peut apparaître après l'activation d'un VPN. Notez précisément l'application, la destination, le type de réseau et la comparaison avant/après VPN. N'abaissez pas au hasard la MTU de toutes les interfaces : demandez au responsable VPN ou réseau de vérifier le chemin et les paramètres adaptés.

### 3.10 Sécurité pendant le dépannage

Un technicien doit garder la sécurité active pendant l'investigation. Un système qui « remarche » grâce à une règle trop large ou à un compte privilégié partagé est un mauvais résultat. Respectez le moindre privilège, utilisez des comptes autorisés et évitez de transmettre des secrets dans les tickets ou les captures d'écran.

Principes utiles :

- **Autorisation :** n'exécutez que les actions relevant de votre rôle ou explicitement approuvées.
- **Minimisation :** collectez les informations nécessaires, pas l'intégralité du contenu privé de l'utilisateur.
- **Confidentialité :** masquez les noms, adresses, identifiants et détails sensibles avant un partage externe.
- **Intégrité :** conservez les journaux et sorties utiles sans les modifier pour « nettoyer » le résultat.
- **Traçabilité :** notez qui a fait quoi, à quelle heure et avec quelle justification.
- **Retour arrière :** avant un changement, connaissez la configuration précédente et la procédure de restauration.

> **Danger :** Ne demandez jamais à un utilisateur de communiquer son mot de passe et ne copiez pas de secrets dans un ticket. Si un compte semble compromis, suivez le processus de sécurité de l'organisation au lieu d'effectuer une réinitialisation improvisée qui pourrait détruire des preuves ou laisser persister l'attaque.

### 3.11 Changement contrôlé et retour arrière

Même une modification simple peut provoquer une panne plus large. Avant d'appliquer un changement, écrivez : la cause supposée, la commande ou le paramètre à changer, le résultat attendu, les tests de validation, la personne qui approuve et la manière de revenir à l'état précédent.

Sur un équipement réseau, conservez une sauvegarde de la configuration si vous êtes autorisé, confirmez que la sauvegarde est exploitable et vérifiez les conséquences sur la production. Ne copiez pas aveuglément une configuration trouvée en ligne. Les noms d'interfaces, VLAN, adresses, syntaxe et fonctionnalités disponibles dépendent de l'équipement et de la version.

Effectuez la modification à la période prévue, surveillez les effets, validez les services et consignez le résultat. Si les effets sont inattendus, arrêtez la séquence et utilisez le plan de retour arrière approuvé. N'effectuez pas une succession de changements non documentés : il deviendrait impossible de savoir lequel a produit le résultat.

### 3.12 Résolution, cause racine et contournement

Trois résultats doivent être distingués :

- **Contournement :** une solution temporaire permet de poursuivre l'activité, mais la cause n'est pas nécessairement éliminée.
- **Résolution :** le service retrouve le comportement attendu dans les conditions testées.
- **Cause racine :** la raison fondamentale qui explique pourquoi l'incident s'est produit et pourquoi les contrôles préventifs ne l'ont pas empêché.

Par exemple, redémarrer une application peut rétablir temporairement le service, mais la cause racine pourrait être une fuite de mémoire, un pool de connexions épuisé ou un problème de dépendance réseau. Pour un débutant, il est acceptable de déclarer « service rétabli, cause non confirmée » plutôt que d'inventer une explication.

Une analyse post-incident doit se concentrer sur les faits et l'amélioration du système plutôt que sur la recherche d'un coupable. Les questions utiles sont : qu'est-ce qui a rendu l'incident possible, quel signal aurait pu être détecté plus tôt, quelle procédure manque et comment éviter la répétition ?

### 3.13 Communication avec l'utilisateur

Pendant le dépannage, informez l'utilisateur des étapes utiles sans lui promettre un résultat que vous ne pouvez pas garantir. Demandez-lui de décrire le message exact, l'heure et l'action réalisée. Ne lui demandez pas de relancer continuellement une opération qui peut dupliquer une transaction ou mettre en danger ses données.

Un message de suivi peut indiquer :

> « Nous avons confirmé que le poste conserve une adresse IP et atteint sa passerelle. Le test de résolution du nom échoue vers le serveur DNS configuré. Nous vérifions le service DNS ; aucune modification locale n'a encore été effectuée. Prochain point de situation : selon la procédure du support. »

Cette formulation présente les faits, les actions et l'incertitude restante. Elle évite le jargon inutile et empêche qu'une hypothèse soit comprise comme une cause déjà confirmée.

### 3.14 Clôturer proprement un ticket

Avant de fermer le ticket, vérifiez :

1. Le test qui échouait au début fonctionne maintenant, ou l'état restant est clairement indiqué.
2. L'utilisateur ou le propriétaire du service a confirmé le rétablissement quand cela est possible.
3. Les tests n'ont pas révélé de régression importante.
4. La cause est confirmée ou explicitement notée comme inconnue.
5. Les modifications et le retour arrière éventuel sont documentés.
6. Les preuves utiles et les journaux sont conservés dans un emplacement autorisé.
7. Une action préventive est créée si nécessaire : mise à jour de documentation, supervision, capacité, sauvegarde ou correction durable.

Un ticket bien clôturé aide les prochaines interventions et fournit des données utiles pour détecter les incidents répétitifs. Des tickets « résolu » sans symptômes, tests ou cause obligent l'équipe à recommencer à zéro la prochaine fois.

### 3.15 Étude de cas guidée : seule une salle est affectée

**Situation :** plusieurs utilisateurs d'une salle ne peuvent plus accéder à une application interne. Les utilisateurs d'un autre étage y accèdent normalement. Le problème a commencé après le déplacement de plusieurs postes.

**Observation initiale :** les postes affectés ont une adresse IP, mais certains ne joignent pas la passerelle. Le périmètre commun est la salle, ce qui rend une cause liée à l'accès local plausible.

**Hypothèses :** mauvais VLAN sur le commutateur d'accès, câblage vers le mauvais panneau, port désactivé, configuration IP incorrecte ou incident sur un commutateur local. Un problème du serveur applicatif paraît moins probable, puisque l'autre étage accède au service, mais il n'est pas encore totalement exclu.

**Tests :** relever l'IP et la passerelle de plusieurs postes ; vérifier les liens ; comparer la configuration avec un poste fonctionnel du même VLAN ; demander au technicien autorisé d'examiner les ports et le VLAN ; vérifier si les adresses MAC sont apprises sur les ports attendus.

**Correction possible :** le port d'un poste a été affecté au mauvais VLAN pendant un déplacement. Le responsable réseau rétablit le VLAN prévu, après confirmation du plan d'adressage et du rôle du port.

**Validation :** le poste reçoit une configuration cohérente, joint la passerelle, atteint la destination interne, ouvre l'application et conserve les autres accès attendus. Les autres postes de la salle sont également testés.

**Compte rendu :** mentionner le symptôme, le nombre de postes touchés, la période, le VLAN attendu, la modification appliquée par la personne autorisée, les résultats avant/après et une action préventive, par exemple vérifier la procédure de brassage et documenter les ports.

Ce cas enseigne une règle importante : lorsque plusieurs utilisateurs proches sont touchés, recherchez un composant commun avant de dépanner chaque poste individuellement.

### 3.16 Étude de cas guidée : un nom interne est inaccessible depuis le VPN

**Situation :** l'utilisateur établit son VPN et atteint certains serveurs internes par adresse IP, mais ne peut pas ouvrir `fichiers.exemple.test` par son nom. Les collègues présents au bureau n'ont pas le problème.

**Observations :** le tunnel semble établi ; au moins une destination interne est accessible ; la panne concerne un nom ou un ensemble de noms depuis le VPN.

**Hypothèses :** le client VPN n'utilise pas les DNS internes, le suffixe DNS manque, le routage vers le résolveur n'est pas installé, le DNS n'autorise pas les requêtes de la plage VPN ou l'enregistrement est incorrect.

**Tests autorisés :** consulter les DNS indiqués dans la configuration du poste pendant le VPN, lancer `nslookup` du nom cible et noter le serveur interrogé, tester le port du service si l'adresse du serveur est connue et approuvée, puis comparer avec un poste du bureau.

**Interprétation :** si le DNS interrogé n'est pas celui prévu pour les noms internes, le client VPN ou sa politique peut être en cause. Si le bon DNS est utilisé mais ne répond pas, vérifiez son accessibilité et ses journaux. Si le nom retourne la bonne adresse mais que le service échoue, continuez vers le routage, les règles d'accès et le serveur.

**Précaution :** ne remplacez pas durablement le DNS du poste par un DNS public et ne créez pas d'entrée `hosts` comme solution permanente. Transmettez les observations à l'équipe VPN avec les routes et le DNS observés, sans joindre de secrets.

### 3.17 Mesures d'amélioration après l'incident

Après la résolution, recherchez une amélioration proportionnée à l'incident. Si des ports changent régulièrement de VLAN par erreur, mettez à jour le plan des ports et la procédure de brassage. Si les utilisateurs signalent une lenteur qui précède les pannes, ajoutez une mesure de capacité ou une supervision adaptée. Si le service DHCP arrive à saturation, planifiez une extension ou une correction durable avec l'équipe responsable.

Une action préventive doit avoir un propriétaire et une échéance. « Améliorer le réseau » n'est pas une action vérifiable. « Documenter les ports de la salle 2, vérifier leur VLAN attendu et faire valider le plan par le responsable réseau » est plus concret.

Les incidents récurrents méritent une analyse spécifique. Un simple retour à la normale ne suffit pas s'ils réapparaissent chaque semaine. Comparez les heures, les événements, les changements et les composants communs pour identifier un motif. Conservez des mesures fiables et évitez de conclure sur la base d'un seul exemple.

---

## Points à retenir

- Le symptôme est une observation ; la cause est une explication qui doit être vérifiée.
- Commencez par préciser qui est touché, ce qui échoue, depuis quand et ce qui fonctionne encore.
- Le périmètre de l'incident aide à privilégier une panne locale ou un composant commun.
- Vérifiez les couches dans un ordre cohérent : lien, configuration IP, passerelle, chemin, DNS, port et application.
- Un ping réussi ne prouve pas que l'application fonctionne ; un ping échoué ne prouve pas toujours que la destination est inaccessible.
- `ipconfig /all`, `nslookup`, `tracert`, `Test-NetConnection` et les commandes Cisco `show` fournissent des indices complémentaires.
- Chaque test doit répondre à une question précise et son résultat doit être noté.
- Comparez le poste touché à une référence réellement équivalente, sans copier aveuglément son adresse IP.
- Préférez les commandes d'observation avant les modifications ; toute action risquée doit être autorisée et réversible.
- Ne désactivez pas un pare-feu globalement, ne modifiez pas de routes au hasard et ne redémarrez pas un équipement de production sans procédure.
- Distinguez le contournement temporaire, le rétablissement du service et la cause racine.
- En cas de doute ou d'impact important, escaladez avec des faits précis plutôt que d'improviser.
- Vérifiez après la correction que le problème initial est résolu et qu'aucune régression n'a été créée.
- Un bon compte rendu permet au prochain technicien de reprendre l'enquête sans recommencer tous les tests.

### Checklist rapide de dépannage

```text
[ ] J'ai formulé le symptôme sans supposer la cause.
[ ] J'ai identifié les utilisateurs, appareils et services touchés.
[ ] J'ai noté l'heure, la fréquence et les changements récents.
[ ] J'ai vérifié les éléments physiques et l'interface active.
[ ] J'ai relevé IP, masque, passerelle et DNS.
[ ] J'ai testé la passerelle et une destination autorisée.
[ ] J'ai testé DNS, port ou application selon le symptôme.
[ ] J'ai comparé avec une référence équivalente si nécessaire.
[ ] J'ai enregistré les résultats exacts et gardé les données utiles.
[ ] Toute modification est autorisée, minimale et réversible.
[ ] J'ai refait les tests initiaux après la correction.
[ ] J'ai informé l'utilisateur et documenté la conclusion.
```

### Exercices d'auto-évaluation

**Exercice 1 — Adresse automatique.** Un poste affiche `169.254.44.12` et les autres postes de la salle ont des adresses `192.168.10.x`. Quelle est la première interprétation prudente et quelles sont les trois premières vérifications ?

**Corrigé :** le poste n'a probablement pas obtenu de bail DHCP sur l'interface utilisée. Il faut vérifier l'interface et le lien, confirmer qu'elle utilise DHCP si cela est prévu, puis comparer le VLAN et le résultat DHCP avec un poste équivalent. Il ne faut pas simplement choisir une adresse statique au hasard.

**Exercice 2 — Ping réussi, application en panne.** La passerelle répond et le serveur répond au ping, mais la connexion Web échoue. Pourquoi ne peut-on pas conclure que « tout le réseau marche » ?

**Corrigé :** ICMP et HTTPS sont deux flux différents. Le port TCP, le pare-feu, le service Web, TLS, le proxy, l'authentification ou l'application peuvent échouer alors que le ping réussit. Il faut tester le port et examiner l'erreur applicative.

**Exercice 3 — Lenteur collective.** Plusieurs personnes d'un même étage signalent une lenteur qui commence à la même heure. Pourquoi la vérification d'un composant partagé est-elle prioritaire ?

**Corrigé :** l'étendue et la synchronisation du symptôme suggèrent une dépendance commune, telle qu'une liaison montante, un point d'accès, un commutateur, un service DNS ou une charge partagée. Cette piste est plus efficace que de supposer immédiatement plusieurs pannes indépendantes de postes.

**Exercice 4 — Traceroute avec astérisques.** Le deuxième saut affiche `* * *`, mais l'application fonctionne. Est-ce une preuve de panne ?

**Corrigé :** non. Certains équipements ne répondent pas aux sondes de traceroute ou limitent ces réponses, tout en transférant le trafic. Le résultat doit être interprété avec les autres tests.

**Exercice 5 — Pare-feu.** Un collègue propose de désactiver le pare-feu pour voir si le site fonctionne. Quelle est la meilleure réponse ?

**Corrigé :** ne pas désactiver globalement le pare-feu. Définir le flux concerné, examiner les journaux et demander à l'équipe autorisée une vérification ciblée. Si un test de règle est nécessaire, utiliser une exception minimale, temporaire, approuvée et documentée.

### Références techniques

1. Cisco, **Troubleshooting Overview — Problem-Solving Model** : https://www.cisco.com/en/US/docs/internetworking/troubleshooting/guide/tr1901.html
2. Cisco, **What Is Network Troubleshooting?** : https://www.cisco.com/site/us/en/learn/topics/networking/what-is-network-troubleshooting.html
3. NIST, **SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management**, publication finale du 3 avril 2025 : https://csrc.nist.gov/pubs/sp/800/61/r3/final
4. IETF, **RFC 792 — Internet Control Message Protocol (ICMP)** : https://www.rfc-editor.org/info/rfc792/
5. IETF, **RFC 2131 — Dynamic Host Configuration Protocol (DHCP)** : https://www.rfc-editor.org/info/rfc2131/
6. IETF, **RFC 1034 — Domain Names: Concepts and Facilities** : https://www.rfc-editor.org/rfc/rfc1034
7. IETF, **RFC 1035 — Domain Names: Implementation and Specification** : https://www.rfc-editor.org/rfc/rfc1035
8. IETF, **RFC 1918 — Address Allocation for Private Internets** : https://www.rfc-editor.org/rfc/rfc1918

Les RFC décrivent des protocoles et leurs comportements. Elles ne remplacent pas la documentation spécifique de la version Windows, de l'équipement Cisco ou des outils de supervision installés dans votre environnement. Les procédures internes de changement, de sécurité et d'escalade restent prioritaires.
