# Laboratoire de dépannage DNS — `lab_tshoot_dns.md`

> **Parcours :** débutant → intermédiaire → expert  
> **Objectif :** diagnostiquer méthodiquement les pannes de résolution de noms, depuis le poste client jusqu'au serveur DNS, aux données de zone et aux captures réseau.  
> **Environnement principal :** Linux avec `dig`, `tcpdump` et BIND 9 ; procédures équivalentes pour Windows.  
> **Fil conducteur :** réseau de laboratoire NovaTech avec une zone privée `lab.test`.


## 1. Objectifs pédagogiques

À la fin de ce laboratoire, tu dois pouvoir :

1. distinguer une panne de résolution DNS d'une panne IP, d'une panne applicative ou d'un problème de routage ;
2. interroger directement un serveur DNS donné sans dépendre du résolveur configuré sur le poste ;
3. interpréter les réponses `NOERROR`, `NXDOMAIN`, `SERVFAIL`, `REFUSED` et un délai d'attente ;
4. vérifier les paramètres DNS reçus par DHCP, les suffixes de recherche, les caches locaux et les fichiers `hosts` ;
5. inspecter les enregistrements A, AAAA, CNAME, MX, NS, SOA et PTR ;
6. contrôler la configuration et les journaux d'un serveur BIND ;
7. capturer une requête DNS sur UDP/53 et la comparer à une requête TCP/53 ;
8. reconnaître les erreurs de zone, les caches périmés, les problèmes de délégation et les incidents liés à la récursion ;
9. produire un rapport de diagnostic qui relie le symptôme aux preuves, à la cause et à la correction.

Le but n'est pas de mémoriser des commandes au hasard. Chaque commande doit répondre à une question précise.

## 2. Précautions et environnement

Ce cahier utilise une zone de test privée et des adresses RFC 1918. Réalise les changements de service et les essais de pare-feu dans une VM ou un réseau isolé. Ne modifie pas un résolveur d'entreprise ni un pare-feu de production pour reproduire ces exercices.

### 2.1 Topologie de référence

Deux machines virtuelles reliées au même réseau virtuel isolé :

```text
Client Linux / Windows                    Serveur DNS Linux
10.10.10.10/24  ------------------------- 10.10.10.53/24
                 réseau de laboratoire

Zone DNS : lab.test
Nom attendu : www.lab.test.       A       10.10.10.80
Nom attendu : portal.lab.test.    CNAME   www.lab.test.
Nom attendu : mail.lab.test.      A       10.10.10.25
```

Aucune passerelle n'est nécessaire pour les tests entre ces deux VM. Si ton hyperviseur impose un autre plan d'adressage, remplace les adresses partout dans le document de manière cohérente.

### 2.2 Outils

Sur Debian ou Ubuntu, installe les outils uniquement dans les VM de laboratoire :

```bash
sudo apt update
sudo apt install dnsutils bind9 bind9-utils tcpdump
```

Sur certaines distributions, le paquet fournissant `dig` ou le service BIND porte un nom différent. Vérifie le gestionnaire de paquets de ton système.

Les outils principaux sont :

| Outil | Utilité |
|---|---|
| `dig` | Interroger un serveur DNS précis, choisir le type d'enregistrement et afficher les indicateurs DNS |
| `nslookup` | Tester simplement une résolution depuis Windows ou Linux |
| `Resolve-DnsName` | Interroger le DNS depuis PowerShell Windows |
| `resolvectl` | Inspecter et vider le cache de `systemd-resolved` sur les systèmes qui l'utilisent |
| `ipconfig /all` | Vérifier adresse, passerelle, serveurs DNS et suffixe sous Windows |
| `tcpdump` / Wireshark | Vérifier si la requête quitte le client et si une réponse revient |
| `named-checkconf` | Vérifier la syntaxe de la configuration BIND |
| `named-checkzone` | Vérifier la syntaxe et la cohérence d'un fichier de zone |
| `journalctl` | Lire les journaux du service DNS sous systemd |


## 3. Méthode de diagnostic : toujours suivre les couches

Lorsqu'un utilisateur indique « Internet ne fonctionne pas », ne commence pas par vider tous les caches ni par redémarrer le serveur DNS. Décompose le problème.

### Étape 1 — Définir précisément le symptôme

- Un seul nom est-il en panne, ou tous les noms ?
- Le problème touche-t-il un seul poste, un VLAN entier, une agence ou plusieurs sites ?
- L'accès par adresse IP fonctionne-t-il lorsque ce test est pertinent ?
- Le nom complet fonctionne-t-il alors que le nom court échoue ?
- Le problème est-il intermittent, lent, ou systématique ?
- Le problème a-t-il commencé après une modification DHCP, DNS, pare-feu, VPN ou routage ?

### Étape 2 — Vérifier la configuration du client

Linux :

```bash
ip address show
ip route show
cat /etc/resolv.conf
resolvectl status 2>/dev/null || true
```

Windows, dans une invite de commandes :

```text
ipconfig /all
route print
```

Vérifie l'adresse IP, le masque, la passerelle, le ou les serveurs DNS et le suffixe de recherche. Le DNS configuré doit être joignable depuis le réseau et doit pouvoir répondre pour les noms demandés.

### Étape 3 — Tester la connectivité vers le serveur DNS

Depuis Linux :

```bash
ping -c 3 10.10.10.53
```

Depuis Windows :

```text
ping 10.10.10.53
```

Un ping réussi prouve seulement qu'un échange ICMP fonctionne. Il ne prouve pas que le service DNS écoute, que UDP/53 ou TCP/53 est autorisé, ni que la zone contient le bon enregistrement. Un ping échoué ne prouve pas forcément que DNS est inaccessible : ICMP peut être filtré alors que DNS fonctionne.

### Étape 4 — Interroger explicitement le serveur

```bash
dig @10.10.10.53 www.lab.test. A
```

Le `@10.10.10.53` désigne le serveur interrogé et le point final de `www.lab.test.` évite qu'un suffixe de recherche soit ajouté. Cette commande permet de séparer un problème du résolveur local d'un problème du serveur interrogé.

Sous Windows :

```powershell
Resolve-DnsName -Name www.lab.test. -Server 10.10.10.53 -DnsOnly
```

Ou :

```text
nslookup www.lab.test. 10.10.10.53
```

### Étape 5 — Interpréter la réponse

| Résultat | Signification typique | Première piste |
|---|---|---|
| `NOERROR` avec une réponse | La requête a abouti pour le type demandé | Vérifier que l'adresse et le type renvoyés sont ceux attendus |
| `NOERROR` sans réponse dans ANSWER (*NODATA*) | Le nom peut exister, mais aucun enregistrement du type demandé n'est fourni | Tester le type pertinent : A, AAAA, MX, etc. |
| `NXDOMAIN` | Le serveur indique que le nom demandé n'existe pas dans le contexte DNS interrogé | Vérifier le nom, la zone, la délégation et le cache négatif |
| `SERVFAIL` | Le serveur n'a pas pu traiter la requête correctement | Vérifier les journaux, la zone, la récursion, les forwarders et éventuellement DNSSEC |
| `REFUSED` | Le serveur refuse cette requête selon sa politique | Vérifier `allow-query`, la récursion et les ACL DNS |
| Délai d'attente (*timeout*) | Aucune réponse n'a été reçue avant la fin du délai | Vérifier IP, écoute, filtrage UDP/TCP 53, route retour et capture |
| `FORMERR` | Le serveur considère la requête mal formée ou non prise en charge | Examiner le client, EDNS et la compatibilité du serveur/intermédiaire |

Ne confonds pas `NXDOMAIN` et `SERVFAIL`. Le premier est une réponse sur l'existence du nom ; le second indique une incapacité à produire une réponse correcte.


## 4. TP 1 — Établir une référence de fonctionnement

**Objectif :** créer une situation saine avant d'injecter les pannes.

### 4.1 Vérifier le réseau

Sur le serveur DNS, confirme que l'interface de laboratoire possède `10.10.10.53/24`. Sur le client, confirme `10.10.10.10/24`. Les deux machines doivent se trouver sur le même segment virtuel.

Sur les deux machines :

```bash
ip -br address
ip route show
```

Teste ensuite l'accessibilité IP du serveur depuis le client :

```bash
ping -c 3 10.10.10.53
```

### 4.2 Installer et configurer une zone BIND de laboratoire

Sur le serveur DNS, sauvegarde les fichiers que tu modifies. Les chemins suivants correspondent à une installation Debian/Ubuntu classique ; ils peuvent être différents sur d'autres distributions.

Dans `/etc/bind/named.conf.local`, ajoute :

```conf
zone "lab.test" {
    type primary;
    file "/etc/bind/db.lab.test";
};
```

Crée `/etc/bind/db.lab.test` :

```dns
$TTL 300
@   IN  SOA ns1.lab.test. hostmaster.lab.test. (
        2026102401 ; serial : augmenter à chaque modification
        3600       ; refresh
        900        ; retry
        604800     ; expire
        300        ; negative cache TTL
)

@       IN  NS      ns1.lab.test.
ns1     IN  A       10.10.10.53
www     IN  A       10.10.10.80
portal  IN  CNAME   www.lab.test.
mail    IN  A       10.10.10.25
@       IN  MX 10   mail.lab.test.
```

Le nom `lab.test` est réservé aux essais/documentation. Les adresses de `www` et `mail` représentent des services fictifs : l'enregistrement DNS peut être correct même si aucun serveur web ou mail n'écoute à ces adresses.

Dans `/etc/bind/named.conf.options`, fusionne les paramètres ci-dessous avec le bloc `options` existant. **Ne crée pas un deuxième bloc `options` si le fichier en contient déjà un.**

```conf
options {
    directory "/var/cache/bind";
    listen-on { 127.0.0.1; 10.10.10.53; };
    allow-query { localhost; 10.10.10.0/24; };
    recursion no;
};
```

Ce profil est un serveur autoritaire de laboratoire, sans récursion. Il n'est pas prévu pour résoudre les noms publics des clients. Il restreint les requêtes à la boucle locale et au sous-réseau de test. Le but est d'éviter de transformer accidentellement le serveur en résolveur récursif ouvert.

Si ta configuration existante possède des paramètres supplémentaires nécessaires, comme `listen-on-v6` ou des clés de contrôle, conserve-les si approprié. Vérifie les options prises en charge par ta version de BIND.

### 4.3 Valider puis recharger

```bash
sudo named-checkconf
sudo named-checkzone lab.test /etc/bind/db.lab.test
sudo systemctl restart bind9
sudo systemctl --no-pager --full status bind9
sudo ss -luntp | grep ':53'
```

La vérification de zone doit signaler une zone chargée avec succès. Si elle échoue, corrige les erreurs de syntaxe avant de redémarrer le service.

### 4.4 Valider les réponses DNS

Depuis le client :

```bash
dig @10.10.10.53 www.lab.test. A
dig @10.10.10.53 portal.lab.test. CNAME
dig @10.10.10.53 lab.test. NS
dig @10.10.10.53 lab.test. SOA
dig @10.10.10.53 lab.test. MX
```

Pour une réponse autoritaire, l'en-tête `dig` doit normalement contenir le drapeau `aa` (*authoritative answer*). La réponse A attendue pour `www.lab.test.` est `10.10.10.80`.

La requête suivante est attendue comme refusée dans ce TP, car la récursion est désactivée :

```bash
dig @10.10.10.53 example.com. A
```

Un `REFUSED` pour cette requête ne prouve pas que le serveur est défaillant. Il correspond à la politique définie pour ce serveur autoritaire de laboratoire.


## 5. TP 2 — Mauvais serveur DNS configuré sur le client

**Symptôme :** la résolution via le résolveur habituel échoue, mais le serveur DNS de laboratoire répond lorsqu'il est interrogé explicitement.

### Procédure

1. Confirme que la commande directe fonctionne :

   ```bash
   dig @10.10.10.53 www.lab.test. A
   ```

2. Affiche le serveur utilisé par le résolveur système :

   ```bash
   cat /etc/resolv.conf
   resolvectl status 2>/dev/null || true
   ```

3. Compare les résultats d'une requête directe et d'une requête système :

   ```bash
   dig @10.10.10.53 www.lab.test. A
   getent hosts www.lab.test
   ```

4. Si tu utilises `systemd-resolved` dans une VM dédiée, configure temporairement le serveur DNS de l'interface de laboratoire. Remplace `enp0s3` par le nom réel de l'interface :

   ```bash
   sudo resolvectl dns enp0s3 10.10.10.53
   sudo resolvectl domain enp0s3 '~lab.test'
   resolvectl status
   resolvectl query www.lab.test
   ```

   Le domaine `~lab.test` définit un domaine de routage DNS pour cette interface sur `systemd-resolved`. Ce réglage est spécifique à `systemd-resolved`; les systèmes utilisant NetworkManager, un autre gestionnaire ou une configuration statique doivent être traités selon leur méthode. N'écrase pas aveuglément `/etc/resolv.conf`, qui peut être généré automatiquement.

### Variante Windows

```text
ipconfig /all
nslookup www.lab.test. 10.10.10.53
nslookup www.lab.test.
ipconfig /displaydns
```

Si la requête avec serveur explicitement indiqué fonctionne mais celle qui utilise la configuration par défaut échoue, vérifie les DNS distribués par DHCP, les paramètres de l'interface et la stratégie DNS du système.

**Panne à injecter :** configure temporairement sur le client un serveur DNS inexistant dans le réseau de laboratoire. Observe si la requête directe au bon serveur fonctionne toujours. Restaure ensuite le DNS correct.

**Conclusion attendue :** une erreur de configuration du client ne se corrige pas en modifiant les enregistrements de zone sur un serveur qui répond correctement.


## 6. TP 3 — Le service DNS ne répond plus

**Symptôme :** le client n'obtient aucune réponse du serveur.

### Procédure contrôlée

Sur le serveur de laboratoire uniquement :

```bash
sudo systemctl stop bind9
```

Depuis le client :

```bash
dig @10.10.10.53 www.lab.test. A +time=2 +tries=1
```

Le résultat devrait être un délai d'attente si aucun autre service n'écoute sur cette adresse et ce port. Vérifie ensuite le service :

```bash
sudo systemctl --no-pager status bind9
sudo journalctl -u bind9 --since '-10 minutes' --no-pager
sudo ss -luntp | grep ':53' || true
```

Redémarre le service :

```bash
sudo systemctl start bind9
sudo systemctl --no-pager status bind9
```

Répète la requête DNS et compare les résultats.

### Questions

- L'interface du serveur était-elle toujours active lorsque BIND était arrêté ?
- Pourquoi un ping peut-il réussir alors que DNS ne répond plus ?
- Quelle preuve permet de différencier un service arrêté d'un filtrage réseau ?

**Critère de réussite :** identifier l'arrêt du service à partir de l'état de systemd, du port d'écoute et de la requête, puis démontrer que le rétablissement de BIND restaure la réponse.


## 7. TP 4 — UDP/53 bloqué, TCP/53 encore disponible

DNS utilise généralement UDP pour les requêtes courantes et peut utiliser TCP, notamment lorsqu'une réponse est tronquée ou lorsque d'autres conditions l'exigent. Il est donc incorrect de conclure que « DNS utilise uniquement UDP ».

> **Sécurité :** le test ci-dessous ajoute une règle temporaire au pare-feu de la VM serveur. Fais-le uniquement dans la VM isolée. Si la VM héberge d'autres services, ne poursuis pas.

### Ajouter une règle de laboratoire

Sur le serveur, crée une table distincte pour ce test :

```bash
sudo nft add table inet labdns_test
sudo nft 'add chain inet labdns_test input { type filter hook input priority 0; policy accept; }'
sudo nft add rule inet labdns_test input ip saddr 10.10.10.0/24 udp dport 53 drop
sudo nft list table inet labdns_test
```

Cette chaîne de base filtre uniquement les paquets correspondant à la règle ajoutée dans ce test isolé. Les règles de pare-feu déjà présentes peuvent également intervenir ; vérifie le jeu de règles complet avant d'interpréter le résultat.

Depuis le client, compare les requêtes :

```bash
dig @10.10.10.53 www.lab.test. A +time=2 +tries=1
dig +tcp @10.10.10.53 www.lab.test. A +time=2 +tries=1
```

La requête UDP doit expirer si la règle s'applique. La requête TCP peut réussir si TCP/53 est autorisé et que BIND écoute sur TCP.

### Nettoyage obligatoire

Sur le serveur :

```bash
sudo nft delete table inet labdns_test
sudo nft list ruleset
```

La seconde commande sert à confirmer que la table temporaire a été supprimée. N'applique pas ce scénario à un serveur DNS réel sans procédure de changement approuvée.

### Interprétation

- UDP échoue, TCP réussit : examine un filtrage UDP, un chemin réseau asymétrique ou un intermédiaire qui traite différemment les transports.
- UDP et TCP échouent : examine l'écoute du service, l'adressage, le routage, le filtrage commun et la capture réseau.
- Les deux réussissent : la règle ne correspond peut-être pas au trafic, le pare-feu actif n'est peut-être pas nftables, ou un autre facteur doit être examiné.


## 8. TP 5 — Lire les captures DNS avec tcpdump et Wireshark

**Objectif :** vérifier si la requête quitte le client, si elle atteint le serveur et si une réponse revient.

### Sur le client

Remplace `enp0s3` par la véritable interface du réseau de laboratoire :

```bash
sudo tcpdump -ni enp0s3 'port 53'
```

Dans un second terminal :

```bash
dig @10.10.10.53 www.lab.test. A
```

### Sur le serveur

Lance aussi une capture côté serveur :

```bash
sudo tcpdump -ni enp0s3 'host 10.10.10.10 and port 53'
```

Remplace l'interface si nécessaire. La capture peut montrer les requêtes UDP ainsi que les échanges TCP sur le port 53.

### Cas typiques

| Capture client | Capture serveur | Interprétation à examiner |
|---|---|---|
| Aucune requête observée | Aucune requête observée | Mauvaise interface de capture, résolution satisfaite par le cache ou `hosts`, application ne lançant pas de requête DNS, ou problème côté client |
| Requête sortante visible | Rien côté serveur | Routage, VLAN, ACL, pare-feu ou point de capture incorrect |
| Requête et réponse visibles côté serveur | Requête visible mais pas de réponse côté client | Chemin retour, filtrage retour, réseau virtuel ou capture côté client |
| Requête et réponse visibles aux deux extrémités | Réponse reçue mais application en échec | Cache, mauvais type d'enregistrement, suffixe, IPv6, politique applicative ou problème qui n'est pas DNS |

### Filtres Wireshark utiles

Filtres d'affichage :

```text
dns
dns.flags.rcode != 0
dns.qry.name == "www.lab.test"
udp.port == 53
tcp.port == 53
```

Ces filtres sont à entrer dans la barre de filtre d'affichage Wireshark, pas dans le champ des filtres de capture. Pour `tcpdump`, le filtre `port 53` est un filtre de capture BPF.

**Exercice :** capture une requête fonctionnelle, puis reproduis le TP 4 et compare l'échange UDP avec l'échange TCP.


## 9. TP 6 — Enregistrement absent, mauvais type et zone non rechargée

### A. Distinguer NXDOMAIN et NODATA

Compare :

```bash
dig @10.10.10.53 www.lab.test. A
dig @10.10.10.53 www.lab.test. AAAA
dig @10.10.10.53 absent.lab.test. A
```

Dans la zone du TP, `www.lab.test.` possède un enregistrement A, mais pas forcément de AAAA. La requête AAAA peut répondre `NOERROR` sans réponse AAAA (NODATA), tandis que `absent.lab.test.` doit typiquement donner `NXDOMAIN`.

### B. Modifier un enregistrement

Sur le serveur, sauvegarde le fichier de zone, puis modifie le record A de `www` vers une autre adresse de documentation de test. Incrémente le numéro de série SOA (par exemple, de `2026102401` à `2026102402`) à chaque modification de la zone.

Valide puis recharge :

```bash
sudo named-checkconf
sudo named-checkzone lab.test /etc/bind/db.lab.test
sudo systemctl reload bind9
```

Depuis le client, interroge directement le serveur autoritaire :

```bash
dig @10.10.10.53 www.lab.test. A
```

La réponse directe devrait refléter l'enregistrement modifié une fois la zone chargée. Si elle ne change pas, examine les erreurs de validation, le rechargement, le fichier réellement associé à la zone et les journaux du service.

### C. Mauvais nom ou mauvais suffixe

Compare les requêtes :

```bash
dig @10.10.10.53 www.lab.test. A
dig @10.10.10.53 www A
dig @10.10.10.53 www.lab.test.example. A
```

Une requête DNS n'est pas une recherche approximative. Les noms sont précis et le suffixe peut modifier le nom final demandé par le système. Le point final d'un FQDN évite l'ajout d'un suffixe de recherche dans les outils qui appliquent cette logique.

### D. CNAME et cible manquante

```bash
dig @10.10.10.53 portal.lab.test. CNAME
dig @10.10.10.53 portal.lab.test. A
```

Le premier test interroge le CNAME lui-même. Le second demande l'adresse et peut également montrer la résolution de la cible. Vérifie que la cible du CNAME est un nom correctement orthographié et que les enregistrements nécessaires existent.

**À rendre :** captures ou sorties illustrant une réponse A correcte, NODATA, NXDOMAIN et un CNAME.


## 10. TP 7 — Cache DNS local et cache négatif

Les caches existent à plusieurs niveaux : application, système d'exploitation, résolveur local, résolveur récursif et parfois équipement ou proxy intermédiaire. Vider le cache d'un poste ne supprime pas automatiquement les entrées en cache d'un résolveur récursif.

### Linux avec systemd-resolved

```bash
resolvectl statistics
sudo resolvectl flush-caches
resolvectl statistics
```

Ces commandes ne s'appliquent que si le système utilise `systemd-resolved`.

### Windows

```text
ipconfig /displaydns
ipconfig /flushdns
ipconfig /displaydns
```

### Exercice

1. Effectue une résolution système d'un nom qui fonctionne.
2. Consulte le cache local si le système expose cette information.
3. Vide le cache local puis relance la résolution.
4. Compare avec une requête `dig @10.10.10.53 ...`, qui interroge directement le serveur indiqué.
5. Pour un laboratoire avec un résolveur récursif, observe également la baisse du TTL en répétant une requête à ce même résolveur.

### Cache négatif

Une réponse négative peut également être mise en cache. Après avoir créé un enregistrement qui n'existait pas, un client ou résolveur qui avait précédemment reçu NXDOMAIN peut continuer à présenter le résultat négatif jusqu'à l'expiration de l'entrée concernée. Le TTL négatif dépend de la zone et du comportement du résolveur.

Ne vide pas systématiquement tous les caches avant de recueillir les preuves : le cache peut être justement l'indice principal qui explique pourquoi certains postes voient l'ancien résultat et d'autres le nouveau.


## 11. TP 8 — Résolution directe et inverse (PTR)

La résolution directe retrouve des informations à partir d'un nom. La résolution inverse utilise un enregistrement PTR dans une zone spéciale `in-addr.arpa` pour IPv4 ou `ip6.arpa` pour IPv6. Une entrée A n'entraîne pas automatiquement la création d'un PTR.

### Ajouter une zone inverse de laboratoire

Dans `/etc/bind/named.conf.local`, ajoute :

```conf
zone "10.10.10.in-addr.arpa" {
    type primary;
    file "/etc/bind/db.10.10.10";
};
```

Crée `/etc/bind/db.10.10.10` :

```dns
$TTL 300
@   IN  SOA ns1.lab.test. hostmaster.lab.test. (
        2026102401
        3600
        900
        604800
        300
)
@   IN  NS  ns1.lab.test.
53  IN  PTR ns1.lab.test.
80  IN  PTR www.lab.test.
25  IN  PTR mail.lab.test.
```

Valide puis recharge les zones :

```bash
sudo named-checkconf
sudo named-checkzone 10.10.10.in-addr.arpa /etc/bind/db.10.10.10
sudo systemctl reload bind9
```

Teste la requête inverse depuis le client :

```bash
dig @10.10.10.53 -x 10.10.10.53
dig @10.10.10.53 -x 10.10.10.80
```

**Panne à injecter :** retire une entrée PTR, mais garde son enregistrement A. Montre que la résolution directe peut encore fonctionner tandis que la résolution inverse échoue.


## 12. TP 9 — Dépannage DNS sous Windows

Ce TP peut être réalisé dans une VM Windows du même réseau isolé.

### 12.1 Inspecter le client

Dans une invite de commandes :

```text
ipconfig /all
ipconfig /displaydns
route print
```

Vérifie les DNS utilisés, le suffixe DNS propre à la connexion et la présence éventuelle de plusieurs serveurs DNS.

### 12.2 Tester le résolveur et le serveur ciblé

Dans PowerShell :

```powershell
Resolve-DnsName -Name www.lab.test. -Server 10.10.10.53 -Type A -DnsOnly
Resolve-DnsName -Name portal.lab.test. -Server 10.10.10.53 -Type CNAME -DnsOnly
```

`nslookup` constitue également un test utile :

```text
nslookup www.lab.test. 10.10.10.53
```

### 12.3 Vérifier le fichier hosts

Sous Windows, examine le fichier :

```text
C:\Windows\System32\drivers\etc\hosts
```

Une entrée locale peut influencer la résolution sans qu'une requête DNS soit envoyée. Ne modifie ce fichier que dans la VM de laboratoire et restaure-le après l'essai.

Sous Linux, le fichier habituel est `/etc/hosts` :

```bash
cat /etc/hosts
getent hosts www.lab.test
```

### 12.4 Vider le cache lorsque les preuves le justifient

```text
ipconfig /flushdns
```

Après le vidage, reteste le même nom et conserve le résultat. Si la requête directe vers le serveur est toujours mauvaise, le cache client n'est pas la cause principale.


## 13. TP 10 — Résultats DNS lents ou intermittents

Un délai DNS peut être causé par un serveur non joignable, un serveur DNS secondaire lent, un suffixe de recherche trop long, un résolveur récursif qui attend une réponse en amont, des retransmissions ou un problème de transport. Plusieurs serveurs DNS configurés ne garantissent pas que le client bascule immédiatement vers un serveur sain dans chaque situation.

### Procédure

1. Mesure la durée de résolution du nom complet.
2. Interroge directement chaque DNS configuré, un par un.
3. Compare le même nom, le même type et la même période.
4. Observe si des requêtes sont retransmises ou si plusieurs serveurs sont essayés.
5. Vérifie la liste de suffixes de recherche lorsque le problème concerne un nom court.
6. Répète les mesures à plusieurs moments et conserve la dispersion des temps, pas seulement une moyenne.

Linux :

```bash
time dig @10.10.10.53 www.lab.test. A +tries=1 +time=2
```

Windows PowerShell :

```powershell
Measure-Command { Resolve-DnsName -Name www.lab.test. -Server 10.10.10.53 -DnsOnly }
```

Pour un laboratoire fermé, les durées dépendent des ressources de la VM, de l'hyperviseur et de la capture. Ne considère pas un seuil arbitraire comme une garantie universelle de qualité.

### Test de suffixe de recherche

Compare un nom court et un FQDN terminé par un point. Si le FQDN répond rapidement mais que le nom court est lent, regarde les suffixes de recherche et les requêtes additionnelles qu'ils déclenchent.


## 14. TP 11 — Comprendre SERVFAIL, REFUSED et la récursion

Ces réponses ont des significations différentes et ne doivent pas être traitées de la même manière.

### REFUSED

Dans la configuration de référence de ce cahier, BIND est configuré sans récursion. Une requête pour un nom public non présent dans `lab.test` peut être refusée. Ce comportement est intentionnel pour le serveur autoritaire de laboratoire.

```bash
dig @10.10.10.53 example.com. A
```

Vérifie la politique configurée avant de conclure à une panne du service.

### SERVFAIL

`SERVFAIL` peut indiquer que le résolveur n'a pas pu obtenir ou valider la réponse. Les causes possibles incluent une défaillance de résolution récursive, un forwarder injoignable, une erreur de délégation, une zone mal chargée ou un échec de validation DNSSEC. Il faut d'abord établir si le serveur interrogé est autoritaire ou récursif pour le nom concerné, puis lire ses journaux et interroger les serveurs pertinents.

### Délai d'attente

Un timeout signifie qu'aucune réponse n'a été reçue à temps. Il peut être causé par un service arrêté ou une perte de paquets ; il ne précise pas à lui seul où le paquet a été perdu. Une capture aux deux extrémités est souvent le meilleur moyen de réduire l'espace de recherche.

### DNSSEC (approfondissement)

DNSSEC permet de vérifier cryptographiquement l'authenticité des données DNS au moyen d'enregistrements et de signatures. Il ne chiffre pas le contenu des requêtes DNS. Un échec de validation peut entraîner `SERVFAIL` sur un résolveur validant, même si une requête vers un serveur non validant semble fonctionner. N'essaie pas de désactiver globalement la validation DNSSEC en production pour faire disparaître une erreur : identifie d'abord la cause et le périmètre.


## 15. TP 12 — Zone mal configurée et analyse des journaux BIND

**Objectif :** trouver une erreur de configuration sans redémarrer à l'aveugle.

### Procédure sûre

1. Fais une copie du fichier de zone avant toute modification.
2. Modifie une valeur dans la VM de laboratoire, par exemple une faute de syntaxe dans un fichier de test, mais ne détruis pas la seule copie valide.
3. Lance `named-checkzone` et constate l'erreur.
4. Corrige le fichier et relance le contrôle.
5. Augmente le numéro de série SOA si tu changes le contenu de la zone.
6. Recharge le service, puis vérifie l'enregistrement par une requête DNS.

Commandes :

```bash
sudo named-checkconf
sudo named-checkzone lab.test /etc/bind/db.lab.test
sudo journalctl -u bind9 --since '-15 minutes' --no-pager
sudo systemctl reload bind9
```

Le contrôle de syntaxe de `named.conf` ne valide pas à lui seul toutes les propriétés de la zone. C'est pourquoi `named-checkzone` est nécessaire pour vérifier le fichier correspondant.

### Indices à rechercher dans les journaux

- fichier de zone absent ou illisible par le service ;
- erreur de syntaxe ;
- zone non chargée ;
- port d'écoute déjà utilisé ;
- interface ou adresse IP d'écoute inexistante ;
- refus d'accès selon la configuration ;
- erreurs liées à la récursion ou à la résolution amont lorsque celle-ci est activée.

**Critère de réussite :** le problème est reproduit dans la VM, identifié par une validation ou un journal, corrigé et confirmé par une requête directe.


## 16. TP 13 — Adresses A et AAAA : le nom résout, mais l'application ne fonctionne pas

Un nom DNS peut avoir des enregistrements A (IPv4), AAAA (IPv6), ou les deux. Le fait qu'un nom se résolve correctement ne garantit pas que l'adresse renvoyée est joignable depuis le client ni que le service écoute sur le port demandé.

### Tests

```bash
dig @10.10.10.53 www.lab.test. A
dig @10.10.10.53 www.lab.test. AAAA
```

Si une adresse AAAA est publiée mais qu'aucun chemin IPv6 fonctionnel n'existe, certaines applications peuvent tenter IPv6 puis subir un délai avant d'utiliser IPv4. Diagnostique l'adresse renvoyée, la route correspondante, la joignabilité du service et le comportement applicatif avant de supprimer des enregistrements.

Ne crée pas d'enregistrement AAAA fictif uniquement pour faire correspondre une table. Un enregistrement DNS doit correspondre à une adresse réellement prévue et joignable dans la conception.


## 17. TP 14 — Split DNS et vues différentes selon le réseau

Le split DNS consiste à fournir des réponses différentes pour un même nom selon le résolveur ou le contexte de requête. C'est courant lorsque des noms internes et externes partagent un suffixe. Cela peut aussi expliquer pourquoi un poste connecté au VPN obtient une réponse différente de celle obtenue hors VPN.

### Scénario

`app.example.test` peut être résolu vers une adresse privée depuis le réseau interne et vers une adresse publique ou un autre service depuis un contexte externe. Dans ce TP, utilise uniquement des noms et des adresses de documentation ; ne modifie pas la résolution réelle d'un domaine d'entreprise.

### Procédure de diagnostic

1. Requête le même FQDN depuis deux contextes différents.
2. Note le serveur DNS réellement interrogé dans chaque contexte.
3. Compare les réponses et les TTL.
4. Vérifie les suffixes de recherche, les règles VPN, le DNS par interface et la politique de routage DNS.
5. Détermine si la différence est volontaire ou due à un mauvais serveur configuré.

Une différence de réponse n'est pas automatiquement un défaut. Elle doit être comparée à la conception attendue et au contexte de l'utilisateur.


## 18. Matrice de dépannage rapide

| Symptôme | Vérification immédiate | Cause possible | Correction à envisager après preuve |
|---|---|---|---|
| Tous les noms échouent | DNS configuré, route, capture UDP/TCP 53 | DNS injoignable, service arrêté, filtrage | Corriger l'adresse DNS, le service ou le chemin réseau |
| Un seul FQDN renvoie NXDOMAIN | Requête directe au DNS attendu ; vérifier l'orthographe et la zone | Enregistrement absent ou mauvais suffixe | Corriger le nom ou la zone, vérifier les caches négatifs |
| FQDN fonctionne, nom court échoue | Suffixe de recherche et requêtes émises | Suffixe absent ou liste incorrecte | Corriger la stratégie de suffixe si cela correspond au besoin |
| La requête directe fonctionne, l'application échoue | Cache, `hosts`, type A/AAAA, port du service | Résolution locale, préférence IPv6, application ou service | Comparer la réponse réellement utilisée par l'application |
| DNS répond REFUSED | Politique du serveur, récursion, ACL | Requête hors périmètre autorisé | Ajuster la politique uniquement si le besoin le justifie |
| DNS répond SERVFAIL | Journaux serveur, forwarders, délégation, DNSSEC | Échec de traitement ou validation | Corriger la cause précise, ne pas contourner aveuglément la validation |
| UDP échoue, TCP réussit | Capture et filtrage par protocole | UDP/53 filtré ou traité différemment | Corriger la règle ou l'intermédiaire concerné |
| Certains postes sont lents | DNS secondaires configurés, suffixes, caches | Serveur indisponible dans la liste ou résolution séquentielle | Nettoyer la configuration distribuée et valider les DNS autorisés |
| Réponse différente selon le site | DNS utilisé, VPN, split DNS, cache | Vues ou résolveurs différents | Confirmer le design et corriger la distribution si elle est erronée |
| A fonctionne, mais le service ne répond pas | Adresse renvoyée, route, TCP/UDP du service | DNS correct, problème applicatif ou de chemin | Poursuivre le diagnostic après la résolution DNS |


## 19. Arbre de décision de diagnostic

```text
Un nom ne se résout pas
          |
          v
Le client a-t-il la bonne configuration IP/DNS ?
       | oui                         | non
       v                             v
Interroger le DNS explicitement      Corriger config client/DHCP
       |
       v
Une réponse arrive-t-elle ?
  | oui                         | non
  v                             v
Interpréter RCODE et answer       Vérifier service, écoute, transport,
  |                              capture, firewall et route retour
  v
A / AAAA / CNAME / NXDOMAIN /
SERVFAIL / REFUSED / NODATA
  |
  v
Comparer zone, politique, cache et besoin applicatif
  |
  v
Corriger une seule cause puis répéter les tests
```


## 20. Exercice final — Incident NovaTech

### Situation

Plusieurs utilisateurs de NovaTech indiquent que `portal.lab.test` ne fonctionne plus. Certains postes signalent un nom introuvable ; d'autres parviennent encore à accéder à une adresse IP connue. Le service DNS semble actif à première vue.

### Mission

Sans réinitialiser tous les équipements ni vider immédiatement tous les caches :

1. identifie les postes, le sous-réseau et le serveur DNS concernés ;
2. compare `dig @10.10.10.53 portal.lab.test. CNAME` et `dig @10.10.10.53 portal.lab.test. A` ;
3. vérifie les enregistrements CNAME et A de la cible ;
4. inspecte la zone et le numéro de série ;
5. vérifie si le résolveur système du client utilise le DNS attendu ;
6. capture une requête si le résultat reste ambigu ;
7. distingue une zone incorrecte d'un cache périmé ou d'un serveur DNS différent ;
8. applique une seule correction, puis répète les tests directs et systèmes ;
9. prouve que les autres enregistrements de la zone continuent à fonctionner.

### Livrable obligatoire

Complète ce rapport :

```text
Incident :
Date et heure :
Utilisateurs / sites affectés :
Nom et type DNS demandés :
Serveur DNS réellement interrogé :
Symptôme observé :
Résultat de la requête directe :
Résultat de la résolution système :
État du service DNS :
État de la zone et du SOA :
Éléments de capture :
Cause racine prouvée :
Correction appliquée :
Tests de non-régression :
Action préventive :
```

### Barème sur 100

| Domaine évalué | Points |
|---|---:|
| Définition exacte du symptôme et du périmètre | 10 |
| Vérification de la configuration client | 10 |
| Requêtes ciblées vers un serveur précis | 15 |
| Interprétation correcte des codes DNS | 15 |
| Inspection de la zone et validation BIND | 15 |
| Utilisation pertinente de capture ou journaux | 15 |
| Correction minimale et tests de non-régression | 10 |
| Rapport clair et action préventive | 10 |
| **Total** | **100** |


## 21. Erreurs de dépannage à éviter

1. **Conclure que DNS est en panne parce qu'un site web ne répond pas.** Le service web, le routage, le pare-feu et le TLS peuvent être en cause.
2. **Tester seulement avec `ping`.** Un ping ne vérifie ni le port DNS ni la validité de la réponse.
3. **Utiliser uniquement la résolution système.** Interroge aussi le serveur voulu directement avec `dig @serveur`.
4. **Confondre NXDOMAIN et SERVFAIL.** Ces réponses n'orientent pas vers les mêmes causes.
5. **Vider tous les caches en premier.** Tu peux faire disparaître un indice précieux.
6. **Modifier une zone sans incrémenter le SOA.** Cela peut perturber la propagation vers les secondaires dans les scénarios concernés.
7. **Oublier TCP/53.** DNS ne se limite pas à UDP.
8. **Autoriser la récursion pour tout le monde.** Un résolveur récursif doit être accessible uniquement aux clients prévus.
9. **Publier un AAAA non fonctionnel.** Le nom peut se résoudre tout en menant les clients vers une connectivité IPv6 indisponible.
10. **Réparer sans retester les autres noms.** Toute modification DNS doit inclure une vérification de non-régression.
11. **Redémarrer avant de collecter les journaux.** Un redémarrage peut éliminer des indices et n'explique pas la cause.
12. **Prendre une réponse différente comme une erreur sans contexte.** Le split DNS peut être intentionnel.


## 22. Fiche de commandes à retenir

### Linux

```bash
# Configuration client
ip -br address
ip route show
cat /etc/resolv.conf
resolvectl status
resolvectl query www.lab.test

# Requêtes DNS ciblées
dig @10.10.10.53 www.lab.test. A
dig @10.10.10.53 www.lab.test. AAAA
dig @10.10.10.53 portal.lab.test. CNAME
dig @10.10.10.53 lab.test. SOA
dig @10.10.10.53 -x 10.10.10.53
dig +tcp @10.10.10.53 www.lab.test. A

# Capture
sudo tcpdump -ni enp0s3 'port 53'

# BIND
sudo named-checkconf
sudo named-checkzone lab.test /etc/bind/db.lab.test
sudo systemctl status bind9
sudo journalctl -u bind9 --since '-15 minutes' --no-pager
sudo ss -luntp | grep ':53'
```

### Windows

```text
ipconfig /all
ipconfig /displaydns
ipconfig /flushdns
nslookup www.lab.test. 10.10.10.53
```

PowerShell :

```powershell
Resolve-DnsName -Name www.lab.test. -Server 10.10.10.53 -Type A -DnsOnly
Measure-Command { Resolve-DnsName -Name www.lab.test. -Server 10.10.10.53 -DnsOnly }
```

Vérifie la disponibilité et la syntaxe des commandes selon la version du système d'exploitation.


## 23. Références officielles

1. [Microsoft Learn — Troubleshooting DNS clients](https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-client) — configuration IP, serveurs DNS, suffixe de recherche, `nslookup` et cache client.
2. [Microsoft Learn — Troubleshooting DNS servers](https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-server) — vérification du service DNS, des données autoritaires et de la récursion.
3. [Microsoft Learn — Resolve-DnsName](https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname?view=windowsserver2025-ps) — syntaxe et options du client DNS PowerShell.
4. [Documentation BIND 9](https://bind9.readthedocs.io/en/stable/) — configuration, zones, exploitation et dépannage du serveur DNS.
5. [Manuel BIND 9 — named-checkconf et named-checkzone](https://bind9.readthedocs.io/en/stable/manpages.html) — validation de la configuration et des fichiers de zone.
6. [Documentation systemd-resolved / resolvectl](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) — inspection et test du résolveur sur les systèmes utilisant systemd-resolved.

Consulte la documentation correspondant à ta version et au mode de déploiement. Les exemples de ce cahier visent un laboratoire fermé et doivent être adaptés avant tout usage en production.


## Conclusion

Un dépannage DNS efficace suit une logique simple : vérifier le client, interroger explicitement le serveur, lire le code de réponse, inspecter la zone et la politique du serveur, puis utiliser capture et journaux pour localiser la perte ou l'erreur. La correction doit être minimale et validée avec des tests positifs comme négatifs.

Le résultat attendu n'est pas seulement « le nom fonctionne de nouveau ». Il faut aussi pouvoir expliquer pourquoi il échouait, démontrer la cause à partir de preuves et montrer que la correction ne crée pas de nouvelle panne.
