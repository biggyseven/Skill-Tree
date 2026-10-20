# Gestion réseau — NTP, horloges et centralisation Syslog

> **Objectif** : comprendre pourquoi le temps est une donnée réseau critique, configurer NTP/chrony et Cisco IOS, centraliser les journaux avec Syslog, et diagnostiquer les problèmes de synchronisation ou de perte de logs.

---

## 1. Pourquoi le temps est critique

Une horloge dérivée casse plus de choses qu'on ne le croit :

- les certificats TLS semblent invalides ;
- Kerberos refuse l'authentification ;
- DNSSEC échoue à valider les signatures ;
- les logs de plusieurs équipements ne peuvent plus être corrélés ;
- les baux DHCP et les sessions AAA deviennent incohérents ;
- les sauvegardes et les jobs planifiés se déclenchent au mauvais moment.

Le temps réseau doit être **uniforme**, **traçable** et **surveillé**. On ne règle pas les équipements à la main : on les synchronise sur des sources fiables et on alerte quand l'écart dépasse un seuil.

```text
Sources de temps (GPS, horloges atomiques, serveurs publics)
                 |
                 v
        Serveurs NTP internes (stratum 2)
          /                     \
         v                       v
  Routeurs / switches       Serveurs / postes
         \                       /
          +---- journaux corrélés ----+
```

---

## 2. NTP : principes et stratum

NTP (Network Time Protocol) permet à un client d'estimer son décalage par rapport à un serveur et d'ajuster progressivement son horloge. NTPv4 fonctionne sur UDP 123. Il utilise plusieurs échantillons, filtre les sources et sélectionne les meilleures.

### 2.1 Stratum

| Stratum | Signification |
|---:|---|
| 0 | Référence physique : GPS, horloge atomique, radio |
| 1 | Serveur directement relié à une référence |
| 2 | Serveur synchronisé sur un stratum 1 |
| 3 | Serveur synchronisé sur un stratum 2 |
| 15 | Limite pratique |
| 16 | Non synchronisé |

Le stratum ne mesure pas la qualité absolue : un stratum 2 proche et stable peut être meilleur qu'un stratum 1 lointain et chargé. Il faut surveiller le décalage, le jitter, le root delay et la stabilité.

### 2.2 Modes NTP

- **client/serveur** : le client interroge un serveur ;
- **symmetric active/passive** : pairs de même niveau ;
- **broadcast/multicast** : diffusion sur un réseau local ;
- **manycast** : découverte de serveurs.

En entreprise, on utilise généralement des serveurs internes redondants et des clients configurés avec plusieurs sources. On évite d'ouvrir UDP 123 vers Internet depuis tous les postes.

### 2.3 NTP et sécurité

NTP n'authentifie pas les paquets par défaut. Un attaquant qui usurpe un serveur peut décaler l'heure. Les mesures :

- authentification symétrique NTP (clés) ;
- ACL restrictives ;
- serveurs internes contrôlés ;
- surveillance des changements d'heure ;
- filtrage des paquets d'amplification ;
- désactivation des modes inutiles.

---

## 3. Configuration Linux avec chrony

`chrony` est le client NTP recommandé sur les distributions modernes. Il démarre rapidement, gère les changements de réseau et fonctionne bien sur les VM.

### 3.1 chrony.conf

```conf
pool 2.pool.ntp.org iburst
server ntp1.lab iburst
server ntp2.lab iburst
driftfile /var/lib/chrony/chrony.drift
makestep 1.0 3
rtcsync
logdir /var/log/chrony
```

`makestep 1.0 3` autorise un saut d'horloge au démarrage si l'écart est important, puis ajuste progressivement. Un saut brutal en production peut perturber les applications ; il faut le planifier.

### 3.2 Commandes de vérification

```bash
chronyc tracking
chronyc sources -v
chronyc sourcestats -v
chronyc makestep
timedatectl
date -u
```

| Commande | Usage |
|---|---|
| `chronyc tracking` | Décalage, stratum, dernière synchronisation |
| `chronyc sources -v` | État des sources (`^*` = source sélectionnée) |
| `chronyc sourcestats` | Statistiques de stabilité |
| `timedatectl` | État du service et fuseau horaire |
| `journalctl -u chronyd` | Logs de synchronisation |

### 3.3 systemd-timesyncd

Sur un poste simple, `systemd-timesyncd` peut suffire. Il est plus limité qu'un vrai NTP et ne doit pas être utilisé pour un serveur de temps d'entreprise.

```bash
timedatectl set-ntp true
timedatectl status
```

---

## 4. NTP sur Cisco IOS

```cisco
ntp server 10.10.1.10 prefer
ntp server 10.10.1.11
ntp source Loopback0
ntp authentication-key 1 md5 MonSecret
ntp trusted-key 1
ntp authenticate
clock timezone CET 1
clock summer-time CEST recurring last Sun Mar 2:00 last Sun Oct 3:00
```

Vérification :

```cisco
show ntp status
show ntp associations
show ntp config
show clock detail
show running-config | include ntp|clock
```

`show ntp status` doit indiquer `Clock is synchronized` et un stratum cohérent. `show ntp associations` affiche les sources, le décalage et la sélection (`*`).

### 4.1 Bonnes pratiques Cisco

- utiliser une interface loopback stable comme source ;
- configurer au moins deux serveurs ;
- restreindre les requêtes NTP avec une ACL ;
- authentifier les pairs si le matériel le permet ;
- surveiller les changements d'heure et les logs `%SYS-6-CLOCKUPDATE` ;
- ne pas dépendre d'un seul serveur interne.

---

## 5. Syslog : centraliser les événements

Syslog transporte des messages d'événements vers un collecteur. Le format historique (RFC 3164) est simple ; le format structuré (RFC 5424) ajoute des métadonnées. Les équipements réseau utilisent souvent UDP 514, mais TCP 514 et TLS 6514 sont préférés pour la fiabilité et la confidentialité.

### 5.1 Niveaux de sévérité

| Niveau | Nom | Gravité |
|---:|---|---|
| 0 | Emergency | Système inutilisable |
| 1 | Alert | Action immédiate requise |
| 2 | Critical | Défaillance critique |
| 3 | Error | Erreur |
| 4 | Warning | Avertissement |
| 5 | Notice | Événement normal notable |
| 6 | Informational | Information |
| 7 | Debug | Débogage détaillé |

Plus le niveau est bas, plus il est grave. Une configuration `logging trap warnings` envoie les niveaux 0 à 4.

### 5.2 Facilities et PRI

Le PRI combine la facility et la severity : `PRI = facility × 8 + severity`. Les facilities usuelles : `kern` (0), `user` (1), `mail` (2), `daemon` (3), `auth` (4), `syslog` (5), `local0` à `local7` (16 à 23).

```text
<134>Oct 19 22:00:00 r1 %%SYS-5-CONFIG_I: Configured from console
```

`134 = 16 × 8 + 6` : facility `local0`, severity informational.

### 5.3 Format RFC 5424

```text
<165>1 2026-10-19T22:00:00.000Z r1.example.net evntslog - ID47 [exampleSDID@32473 iut="3"] Message
```

Le format structuré permet d'ajouter des champs exploitables par un SIEM. Les vieux équipements restent souvent en RFC 3164 ; le collecteur doit savoir parser les deux.

---

## 6. Configuration Syslog

### 6.1 Cisco IOS

```cisco
logging buffered 16384 informational
logging console warnings
logging monitor informational
logging host 10.10.1.20 transport udp port 514
logging trap informational
logging source-interface Loopback0
service timestamps log datetime msec localtime show-timezone
service sequence-numbers
```

Vérification :

```cisco
show logging
show logging history
show running-config | include logging
```

`logging buffered` conserve les logs localement ; `logging host` les envoie au collecteur. `logging trap` filtre ce qui part vers le collecteur. Un `debug` sans `logging trap debugging` ne sera pas envoyé.

### 6.2 Linux rsyslog

```conf
# /etc/rsyslog.d/50-remote.conf
*.* action(type="omfwd" target="10.10.1.20" port="514" protocol="udp"
          queue.type="linkedList" queue.failseover="on")
```

Pour TLS :

```conf
module(load="imtcp" StreamDriver.Name="gtls" StreamDriver.Mode="1")
input(type="imtcp" port="6514" ruleset="tls")
```

Les files d'attente et la reprise après panne évitent de perdre des logs quand le collecteur est indisponible. On protège aussi les fichiers par rotation et permissions.

### 6.3 journald

```bash
journalctl -b
journalctl -u ssh --since "1 hour ago"
journalctl -p err -n 100
journalctl --disk-usage
```

`journald` peut être configuré pour transmettre à rsyslog (`ForwardToSyslog=yes`) ou pour conserver ses journaux dans `/var/log/journal`.

---

## 7. Corréler les journaux

Une attaque ou une panne se comprend en corrélant plusieurs sources :

```text
22:00:01  switch  %LINK-3-UPDOWN: Interface Gi0/1 changed state to down
22:00:02  routeur %OSPF-5-ADJCHG: Neighbor down
22:00:02  firewall %ASA-6-302014: Teardown TCP connection
22:00:03  serveur sshd: Failed password for admin
```

Sans horodatage fiable, ces lignes ne peuvent pas être ordonnées. D'où la règle : **NTP d'abord, Syslog ensuite**.

### 7.1 Fuseaux horaires

On stocke souvent en UTC, on affiche en heure locale. Cisco peut utiliser `clock timezone` et `service timestamps ... localtime` ; Linux utilise `/etc/localtime`. Dans un SIEM, tout doit être normalisé en UTC.

### 7.2 Rétention et volumétrie

| Source | Volumetypique | Rétention |
|---|---|---|
| Routeur | Faible à moyen | 30 à 90 jours |
| Firewall | Élevé | 90 jours à 1 an |
| Serveur | Moyen | Selon conformité |
| Debug temporaire | Très élevé | Quelques heures |

Un debug permanent peut saturer le CPU, le disque et le réseau. On l'active pour une durée limitée, avec un filtre précis.

---

## 8. Dépannage NTP et Syslog

### 8.1 Le temps est faux

```bash
chronyc tracking
chronyc sources -v
ntpq -p
ss -lunp | grep 123
tcpdump -ni any port 123
```

Vérifier : serveur joignable, UDP 123 autorisé, source sélectionnée, stratum valide, horloge matérielle, fuseau horaire. Un décalage de plusieurs heures est souvent un problème de fuseau ou de RTC, pas de NTP.

### 8.2 Les logs n'arrivent pas

1. `show logging` : le buffered local contient-il le message ?
2. `logging host` et `logging trap` sont-ils corrects ?
3. Le collecteur écoute-t-il sur le bon port ?
4. Le firewall autorise-t-il UDP/TCP 514 ou 6514 ?
5. Le DNS du collecteur résout-il ?
6. Les files d'attente rsyslog sont-elles saturées ?

```bash
ss -lunp | grep 514
tcpdump -ni any port 514
tail -f /var/log/syslog
logger -n 10.10.1.20 -P 514 "test syslog"
```

### 8.3 Les logs sont dans le désordre

Corriger NTP avant d'analyser. Vérifier que tous les équipements utilisent la même source et que les timestamps incluent les millisecondes et le fuseau.

---

## 9. Bonnes pratiques d'exploitation

- au moins deux sources NTP internes, avec des upstream distincts ;
- NTP authentifié ou restreint aux réseaux de management ;
- Syslog TCP/TLS pour les environnements sensibles ;
- collecteur redondant et stockage dimensionné ;
- alertes sur les niveaux 0 à 3 et sur l'absence de logs ;
- rotation, compression et rétention conformes ;
- documentation des sources de temps et des collecteurs ;
- tests réguliers de restauration et de corrélation.

Le couple NTP/Syslog est la fondation de l'observabilité réseau. Un équipement sans heure fiable produit des logs inutilisables ; un collecteur sans NTP peut lui-même fausser la chronologie. On supervise donc les deux ensemble.

---

## 10. Exercices

1. Configurer chrony avec deux serveurs internes et vérifier la source sélectionnée.
2. Configurer un routeur Cisco pour envoyer ses logs vers un collecteur rsyslog.
3. Provoquer un décalage d'horloge et observer l'effet sur les timestamps.
4. Calculer le PRI pour facility `local4` et severity `error`.
5. Capturer du NTP avec tcpdump et identifier le mode et le stratum.
6. Configurer rsyslog avec une file d'attente et couper le collecteur.
7. Comparer RFC 3164 et RFC 5424 sur un même message.
8. Mettre en place une alerte sur les logs `%LINK-3-UPDOWN`.
9. Vérifier la rétention et la rotation des journaux Linux.
10. Rédiger une procédure de diagnostic « logs manquants » en cinq étapes.
