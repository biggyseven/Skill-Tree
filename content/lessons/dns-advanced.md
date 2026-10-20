# DNS avancé — zones, autorité, DNSSEC et sécurité

> **Objectif** : passer du « serveur DNS qui répond » à l'ingénierie DNS. Comprendre la hiérarchie, les zones, les types d'enregistrements, les transferts, la validation DNSSEC, les attaques et les commandes de diagnostic Cisco/Linux.

---

## 1. Le DNS n'est pas un simple annuaire

Le DNS est une base de données distribuée, hiérarchique et fortement mise en cache. Une requête peut traverser plusieurs serveurs avant d'obtenir une réponse. Un ingénieur réseau doit distinguer quatre questions différentes :

1. Qui est autoritaire pour ce nom ?
2. Qui répond réellement au client ?
3. La réponse est-elle authentique et complète ?
4. Combien de temps peut-elle rester en cache ?

```text
Client
  |
  | requête récursive
  v
Résolveur récursif (cache)
  |
  |-- demande aux serveurs racine
  |-- demande au TLD (.com, .fr, .lab)
  |-- demande au serveur autoritaire de la zone
  v
Réponse + TTL
  |
  v
Client
```

### 1.1 Serveur récursif, autoritaire, forwarder

| Rôle | Fonction | Exemple |
|---|---|---|
| Résolveur récursif | Fait le travail pour le client et met en cache | Unbound, BIND récursif, serveur d'entreprise |
| Serveur autoritaire | Détient la zone et répond pour elle | BIND primaire/secondaire, DNS cloud |
| Forwarder | Transmet les requêtes à un autre résolveur | dnsmasq, systemd-resolved |
| Stub resolver | Petit client qui interroge un récursif | Bibliothèque du poste, `dig` |
| Cache-only | Ne fait pas d'autorité, seulement du cache | Résolveur local |

Un serveur autoritaire ne doit pas être ouvert à la récursion pour Internet. Un résolveur récursif ne doit pas être autoritaire pour les zones publiques sans séparation claire. Mélanger les rôles est une source de cache poisoning et d'amplification.

### 1.2 Récursion, itération et cache

Une requête récursive demande au serveur de fournir la réponse finale. Une requête itérative demande seulement la meilleure référence disponible. Le résolveur récursif combine les deux : il interroge la racine, puis le TLD, puis l'autoritaire, et conserve les réponses selon le TTL.

```text
Résolveur                          Autoritaire
   |--- question A? ---------------->|
   |<-- réponse + TTL ---------------|
   |                                  |
   | conserve en cache jusqu'à TTL   |
```

Le TTL est un compromis : un TTL long réduit la charge mais ralentit les changements ; un TTL court accélère les bascules mais augmente le trafic. Pour une migration, on baisse le TTL **avant** le changement, puis on le remonte après stabilisation.

---

## 2. Zones et fichiers de zone

Une zone est une portion de l'espace de noms déléguée à un serveur. Elle commence à un nom (apex) et contient les enregistrements de ce nom et de ses sous-domaines non délégués.

### 2.1 Enregistrement SOA

Le SOA (Start of Authority) décrit la zone : serveur primaire, contact, numéro de série et temporisations.

```bind
$TTL 3600
@   IN  SOA ns1.lab. admin.lab. (
        2026101901 ; serial : à incrémenter à chaque changement
        3600       ; refresh
        900        ; retry
        1209600    ; expire
        300        ; negative TTL
)
```

| Champ | Rôle |
|---|---|
| Serial | Version de la zone ; les secondaires comparent cette valeur |
| Refresh | Intervalle de vérification du secondaire |
| Retry | Délai avant nouvel essai après échec |
| Expire | Durée maximale sans contact avant de considérer la zone expirée |
| Negative TTL | Durée de cache des réponses NXDOMAIN/NODATA |

Le numéro de série doit augmenter à chaque modification. Une mauvaise pratique consiste à le laisser inchangé : le secondaire ne voit alors jamais la mise à jour.

### 2.2 Enregistrements essentiels

| Type | Rôle | Exemple |
|---|---|---|
| `A` | Nom vers IPv4 | `www.lab. 300 IN A 10.10.0.20` |
| `AAAA` | Nom vers IPv6 | `www.lab. 300 IN AAAA 2001:db8::20` |
| `CNAME` | Alias vers un nom canonique | `web.lab. CNAME www.lab.` |
| `MX` | Serveur de messagerie avec priorité | `lab. MX 10 mail.lab.` |
| `TXT` | Texte, SPF, DKIM, vérification | `lab. TXT "v=spf1 mx -all"` |
| `PTR` | Résolution inverse | `20.0.10.10.in-addr.arpa. PTR www.lab.` |
| `NS` | Serveur de noms de la zone | `lab. NS ns1.lab.` |
| `SRV` | Service, protocole, port, cible | `_sip._tcp.lab. SRV 10 5 5060 sip.lab.` |
| `CAA` | Autorité de certification autorisée | `lab. CAA 0 issue "letsencrypt.org"` |
| `TLSA` | Certificat associé à un service TLS | `_443._tcp.lab. TLSA 3 1 1 ...` |

### 2.3 CNAME : règles à connaître

Un CNAME ne peut pas cohabiter avec un autre enregistrement au même nom. Il ne faut donc pas mettre un CNAME à l'apex d'une zone qui porte déjà SOA, NS, MX ou TXT. Les alias d'apex sont souvent gérés par des enregistrements propriétaires (`ALIAS`, `ANAME`) ou par le fournisseur DNS.

```text
www.lab.      CNAME   app.lab.
app.lab.      A       10.10.0.20
```

Une chaîne de CNAME trop longue augmente la latence et peut compliquer le diagnostic. Un CNAME vers un nom externe doit être surveillé : si la cible change, le cache peut retarder la propagation.

### 2.4 MX et messagerie

```bind
lab.            IN MX 10 mail1.lab.
lab.            IN MX 20 mail2.lab.
mail1.lab.      IN A 10.10.0.25
mail2.lab.      IN A 10.10.0.26
```

La priorité la plus faible est essayée d'abord. Un MX doit pointer vers un nom qui possède un A ou AAAA, jamais directement vers une adresse IP. Les enregistrements SPF, DKIM et DMARC sont publiés en TXT (ou en TXT via des noms dédiés) et participent à la réputation de messagerie.

### 2.5 PTR et résolution inverse

La résolution inverse utilise le domaine `in-addr.arpa` pour IPv4 et `ip6.arpa` pour IPv6. Elle est souvent déléguée au fournisseur d'accès ou au propriétaire de la plage.

```text
10.10.0.20  ->  20.0.10.10.in-addr.arpa.
```

Un PTR n'est pas obligatoire pour le fonctionnement d'un site web, mais il est important pour la messagerie, les journaux et certains contrôles d'accès. Un PTR doit idéalement correspondre au nom direct (forward-confirmed reverse DNS).

### 2.6 TTL et propagation

| TTL | Usage |
|---:|---|
| 60 s | Bascule rapide, environnement très dynamique |
| 300 s | Équilibrage ou changement fréquent |
| 3600 s | Valeur courante d'entreprise |
| 86400 s | Enregistrements très stables |

Le cache négatif utilise le negative TTL du SOA. Après une suppression, les clients peuvent continuer à recevoir un NXDOMAIN ou une ancienne réponse jusqu'à expiration.

---

## 3. Délégation et transferts de zone

### 3.1 Délégation

La zone parente publie des enregistrements NS pour déléguer un sous-domaine :

```bind
; dans la zone lab.
sub.lab.    IN NS ns1.sub.lab.
sub.lab.    IN NS ns2.sub.lab.
ns1.sub.lab. IN A 10.10.1.53
ns2.sub.lab. IN A 10.10.1.54
```

Le serveur autoritaire de `sub.lab` répond ensuite pour les noms sous cette zone. Une délégation mal configurée crée des « lame delegations » : les NS existent mais ne répondent pas autoritairement.

### 3.2 Transfert AXFR et IXFR

Un serveur secondaire synchronise une zone par transfert :

```bash
dig AXFR lab @10.10.1.53
dig IXFR=2026101901 lab @10.10.1.53
```

| Transfert | Description |
|---|---|
| AXFR | Copie complète de la zone |
| IXFR | Transfert incrémental basé sur le serial |
| TSIG | Authentification des transferts par clé partagée |
| NOTIFY | Le primaire prévient les secondaires d'un changement |

Les transferts doivent être restreints aux adresses des secondaires. Un AXFR ouvert expose toute la zone, y compris des noms internes.

```bind
allow-transfer { 10.10.1.54; };
also-notify { 10.10.1.54; };
notify yes;
```

### 3.3 Primaire, secondaire et hidden primary

Un primaire détient la version de référence ; les secondaires servent des copies. Le primaire peut être caché derrière un load balancer ou un bastion. Les secondaires doivent être plusieurs, dans des zones de disponibilité différentes, pour survivre à la perte d'un site.

```text
           +----------------+
           | Primaire caché |
           +--------+-------+
                    |
          +---------+---------+
          |                   |
   +------v------+     +------v------+
   | Secondaire A|     | Secondaire B|
   +-------------+     +-------------+
```

---

## 4. DNSSEC : authenticité et intégrité

DNSSEC ajoute des signatures cryptographiques aux données DNS. Il ne chiffre pas les requêtes : il permet à un résolveur validateur de vérifier que la réponse vient bien de la zone et n'a pas été modifiée.

### 4.1 Chaîne de confiance

```text
Racine (. )
  | DS de la zone .lab
  v
Zone lab.
  | DS de la zone sub.lab
  v
Zone sub.lab.
  | DNSKEY + RRSIG
  v
Réponses signées
```

| Élément | Rôle |
|---|---|
| `DNSKEY` | Clé publique de la zone (ZSK/KSK) |
| `RRSIG` | Signature d'un ensemble d'enregistrements |
| `DS` | Empreinte d'une clé de sous-zone, publiée par le parent |
| `NSEC`/`NSEC3` | Preuve d'inexistence |
| `CD`/`AD` | Bits de requête/réponse liés à la validation |

Le résolveur valide la chaîne depuis une ancre de confiance (souvent la racine). Si une signature manque ou est invalide, la réponse est considérée comme non sécurisée ou boguée selon la politique.

### 4.2 Validation avec dig et delv

```bash
dig +dnssec www.lab
dig +dnssec +multi lab DNSKEY
dig +dnssec lab DS
delv @10.10.1.53 www.lab
```

Sur un résolveur local, on peut vérifier :

```bash
resolvectl query --legend=no www.lab
resolvectl status
```

Un `AD` (Authenticated Data) dans la réponse indique que le résolveur a validé la signature. Attention : `dig` peut afficher une signature sans que le résolveur du poste ait validé la chaîne.

### 4.3 NSEC et NSEC3

NSEC prouve l'absence d'un nom en listant le nom suivant dans l'ordre canonique. NSEC3 ajoute un hachage pour limiter l'énumération de zone, au prix d'un coût CPU et d'une complexité de diagnostic.

### 4.4 Rollover de clés

| Étape | Action |
|---|---|
| 1 | Publier la nouvelle DNSKEY |
| 2 | Attendre la propagation |
| 3 | Signer avec la nouvelle clé |
| 4 | Publier le nouveau DS chez le parent |
| 5 | Retirer l'ancienne clé après expiration des caches |

Un rollover mal séquencé casse la validation. Les signatures ont une fenêtre de validité ; une horloge dérivée peut invalider DNSSEC même si les clés sont bonnes.

---

## 5. Attaques DNS et contre-mesures

### 5.1 Spoofing et cache poisoning

Un attaquant tente d'injecter une réponse avant la vraie réponse. Les défenses incluent :

- identifiants de transaction aléatoires ;
- ports sources aléatoires ;
- 0x20 encoding (casse aléatoire du nom) ;
- DNSSEC ;
- résolveurs récursifs restreints.

Kaminsky a montré qu'une découverte systématique de ports et d'identifiants pouvait empoisonner un cache. Les résolveurs modernes randomisent davantage et limitent la récursion.

### 5.2 Amplification et réflexion

Une requête DNS peut être petite et la réponse volumineuse. Avec une adresse source usurpée, un attaquant dirige des réponses vers une victime. Les protections : limiter la récursion, rate limiting, réponse minimale, anycast, filtrage BCP38.

### 5.3 Tunneling DNS

Des données sont encodées dans des noms ou des requêtes TXT. Les signaux : requêtes longues, nombreux NXDOMAIN, domaines aléatoires, volume anormal. Les défenses : inspection, RPZ, blocage de résolveurs non autorisés, journaux et analyse comportementale.

### 5.4 Détournement de registrar et de zone

Une compromission du compte registrar ou du fournisseur DNS permet de changer les NS. Les défenses : MFA, verrouillage de domaine, DNSSEC, surveillance des changements, alertes sur les enregistrements.

### 5.5 Attaques par déni de service

Les attaques DNS peuvent saturer les résolveurs ou les autoritaires. On combine anycast, répartition de charge, cache, limites de requêtes et protection DDoS. Une zone critique doit avoir plusieurs fournisseurs DNS et des TTL adaptés.

---

## 6. Configuration BIND

### 6.1 named.conf minimal

```bind
options {
    directory "/var/cache/bind";
    recursion no;
    listen-on port 53 { 10.10.1.53; };
    allow-query { 10.10.0.0/16; };
    dnssec-validation auto;
};

zone "lab" IN {
    type primary;
    file "/etc/bind/db.lab";
    allow-transfer { 10.10.1.54; };
    notify yes;
};
```

### 6.2 Fichier de zone

```bind
$TTL 300
@   IN  SOA ns1.lab. admin.lab. (
        2026101901 3600 900 1209600 300 )
    IN  NS  ns1.lab.
    IN  NS  ns2.lab.
    IN  MX  10 mail.lab.
ns1     IN  A   10.10.1.53
ns2     IN  A   10.10.1.54
mail    IN  A   10.10.0.25
www     IN  A   10.10.0.20
app     IN  A   10.10.0.20
web     IN  CNAME www.lab.
```

### 6.3 Vérifications

```bash
named-checkconf /etc/bind/named.conf
named-checkzone lab /etc/bind/db.lab
rndc reload
rndc status
journalctl -u named -f
```

Sur un serveur autoritaire, `recursion no` évite d'être un résolveur ouvert. Sur un résolveur, on limite `allow-recursion` aux réseaux internes.

### 6.4 Cisco IOS comme client et serveur

```cisco
ip name-server 10.10.1.53
ip domain-name lab
ip domain lookup
ip dns server
ip host app.lab 10.10.0.20
ip host www.lab 10.10.0.20
```

Vérification :

```cisco
show hosts
show ip dns view
show running-config | include name-server|domain
```

Un routeur Cisco peut servir de petit relais DNS, mais un vrai service d'entreprise doit être rendu par des serveurs dédiés, avec supervision et redondance.

---

## 7. Diagnostic Linux

### 7.1 dig

```bash
dig www.lab A
dig www.lab AAAA
dig www.lab MX
dig www.lab TXT
dig -x 10.10.0.20
dig +trace www.lab
dig +short www.lab
dig +dnssec +multi lab DNSKEY
dig AXFR lab @10.10.1.53
```

| Option | Usage |
|---|---|
| `+short` | Sortie minimale |
| `+trace` | Suit la délégation depuis la racine |
| `+dnssec` | Demande les signatures |
| `+tcp` | Force TCP |
| `+noall +answer` | Affiche uniquement la section réponse |

### 7.2 Résolveur local

```bash
resolvectl status
resolvectl query www.lab
resolvectl flush-caches
cat /etc/resolv.conf
```

Sur systemd-resolved, `resolvectl` interroge le résolveur local. Un `resolv.conf` pointant vers `127.0.0.53` est normal si systemd-resolved est actif.

### 7.3 Capture et logs

```bash
tcpdump -ni any port 53
tcpdump -ni eth0 'udp port 53' -vv
journalctl -u named -f
tail -f /var/log/syslog
```

Pour un incident, on note : nom demandé, type, serveur interrogé, code de réponse (`NOERROR`, `NXDOMAIN`, `SERVFAIL`, `REFUSED`), TTL et source. Un `SERVFAIL` peut venir d'une validation DNSSEC, d'une zone expirée ou d'un serveur secondaire indisponible.

---

## 8. Haute disponibilité et exploitation

| Bonne pratique | Pourquoi |
|---|---|
| Au moins deux autoritaires | Résilience réseau et site |
| Secondaires dans des AS/sites différents | Panne de datacenter |
| Supervision des réponses et du TTL | Détecter une zone expirée |
| Alertes sur serial et transferts | Éviter une divergence |
| DNSSEC avec rollover planifié | Intégrité sans rupture |
| Journalisation des requêtes | Enquête et capacité |
| Limitation de récursion | Sécurité et anti-amplification |

Un bon monitoring DNS ne se limite pas à un ping : il interroge des noms critiques, vérifie les codes de réponse, compare les vues et contrôle la validation DNSSEC. On surveille aussi le taux de NXDOMAIN, les latences et les transferts de zone.

---

## 9. Scénarios concrets

### 9.1 Un nom interne ne résout pas

1. `dig app.lab @10.10.1.53` : le serveur autoritaire répond-il ?
2. `dig app.lab` : le client utilise-t-il le bon résolveur ?
3. `dig +trace app.lab` : la délégation est-elle correcte ?
4. Vérifier le SOA, le serial et les NS.
5. Vérifier `allow-query`, les ACL et le firewall UDP/TCP 53.

### 9.2 Un site externe renvoie SERVFAIL

1. Vérifier l'heure du résolveur (DNSSEC dépend du temps).
2. Tester `dig +dnssec` et `delv`.
3. Vérifier les DNSKEY/DS et la zone parente.
4. Vérifier les logs du résolveur et la connectivité aux autoritaires.

### 9.3 Une zone secondaire est en retard

1. Comparer les serial avec `dig SOA`.
2. Vérifier `allow-transfer`, TSIG et le port 53 TCP.
3. Vérifier `notify` et les logs du secondaire.
4. Tester un AXFR manuel depuis le secondaire.

---

## 10. Résumé opérationnel

Le DNS avancé repose sur une séparation claire des rôles, des zones bien déléguées, des transferts maîtrisés et une validation DNSSEC correctement déployée. Les incidents les plus fréquents ne sont pas des bugs du protocole, mais des TTL mal préparés, des NS incohérents, des caches empoisonnés, des horloges dérivées ou des ACL trop ouvertes.

Un ingénieur réseau doit savoir lire une réponse DNS complète, expliquer la différence entre autoritaire et récursif, vérifier une chaîne DNSSEC et corréler un incident avec une capture et des journaux. C'est cette méthode, plus que la simple mémorisation des types d'enregistrements, qui fait la différence en production.

---

## 11. Exercices de consolidation

1. Créer une zone `lab` avec `www`, `mail`, `app`, un CNAME `web` et un MX.
2. Vérifier la délégation d'une sous-zone et le transfert AXFR entre deux serveurs.
3. Signer la zone avec DNSSEC et valider avec `delv`.
4. Provoquer un `SERVFAIL` par une horloge fausse et expliquer le diagnostic.
5. Comparer le comportement d'un résolveur récursif et d'un forwarder.
6. Restreindre une zone aux réseaux internes avec `allow-query` et tester depuis un client externe.
7. Capturer une requête DNS avec `tcpdump` et identifier la transaction et le TTL.
8. Mettre en place un CNAME et expliquer pourquoi il ne peut pas cohabiter avec un MX.
9. Configurer un secondaire et vérifier la reprise après modification du serial.
10. Rédiger une procédure de rollover DNSSEC sans interruption de service.
