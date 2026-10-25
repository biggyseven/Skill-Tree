# Administration réseau Linux — Filtrage, pare-feu et traduction d'adresses

## Module principal : Filtrage et NAT (nftables/iptables)

> **Niveau :** Intermédiaire  
> **Domaine :** Administration réseau Linux et sécurité des infrastructures  
> **Outils étudiés :** nftables, iptables, Netfilter, conntrack et sysctl  
> **Prérequis :** maîtriser les adresses IPv4/IPv6, les sous-réseaux, les interfaces, les routes, les passerelles et les commandes réseau Linux  
> **Environnement conseillé :** deux ou trois machines virtuelles Linux reliées à des réseaux virtuels isolés  
> **Objectif :** construire, tester et dépanner des règles de filtrage, comprendre le suivi des connexions et mettre en place des configurations NAT contrôlées.


# 1. Objectifs pédagogiques

Un administrateur Linux intermédiaire doit être capable de contrôler les flux réseau d'une machine, de comprendre le cheminement des paquets et d'identifier pourquoi une communication est acceptée, rejetée ou traduite.

À l'issue de ce cours, vous devez être capable de :

- expliquer le rôle de Netfilter dans le noyau Linux ;
- distinguer filtrage, routage, suivi des connexions et NAT ;
- comprendre les chaînes `INPUT`, `OUTPUT` et `FORWARD` d'iptables ;
- comprendre les tables, chaînes, hooks et priorités de nftables ;
- écrire un ensemble de règles nftables pour un serveur Linux ;
- appliquer une politique restrictive tout en autorisant les communications nécessaires ;
- utiliser le suivi des connexions avec `conntrack` ;
- autoriser les connexions établies et associées sans ouvrir inutilement de ports ;
- configurer un routeur Linux avec NAT ;
- distinguer SNAT, DNAT, MASQUERADE et REDIRECT ;
- activer le routage IPv4 et comprendre les enjeux IPv6 ;
- utiliser iptables pour examiner et maintenir un pare-feu existant ;
- comprendre la différence entre `iptables-nft` et `iptables-legacy` ;
- rendre une configuration de pare-feu persistante ;
- analyser les compteurs, les journaux et les traces de paquets ;
- dépanner des règles qui bloquent un service ou ne produisent pas l'effet attendu ;
- concevoir une stratégie de retour arrière pour les modifications sensibles.

Le cours privilégie les outils natifs de filtrage. Il ne remplace pas un cours spécialisé sur `firewalld`, UFW, les VPN, les IDS/IPS, les VLAN ou le routage de politiques avancé.

# 2. Architecture générale du filtrage sous Linux

## 2.1. Qu'est-ce que Netfilter ?

Netfilter est l'infrastructure du noyau Linux qui permet notamment d'inspecter, de filtrer, de suivre et de modifier le traitement des paquets réseau.

Les outils en espace utilisateur, comme `nft` et `iptables`, permettent de configurer les règles utilisées par cette infrastructure.

Il faut donc distinguer :

- **Netfilter** : infrastructure de traitement des paquets dans le noyau ;
- **nftables** : framework moderne de filtrage et de NAT ;
- **`nft`** : commande permettant de configurer nftables ;
- **iptables** : interface historique de configuration de règles Netfilter ;
- **conntrack** : mécanisme de suivi de l'état des connexions ;
- **sysctl** : mécanisme de configuration de paramètres du noyau, notamment l'autorisation de transfert IP.

## 2.2. Vue d'ensemble

```text
                    ADMINISTRATEUR
                           |
              +------------+------------+
              |                         |
              v                         v
             nft                    iptables
              |                         |
              v                         v
          nftables                API xtables
              |                         |
              +------------+------------+
                           |
                           v
                    Infrastructure
                      Netfilter
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
        Filtrage        Conntrack        NAT
            |              |              |
            +--------------+--------------+
                           |
                           v
                   Décision du noyau
                           |
              +------------+------------+
              |                         |
              v                         v
          Accepter                  Rejeter
          le paquet                 le paquet
```

Les chemins exacts et les interactions dépendent du type de paquet, des hooks traversés, des tables et chaînes configurées, ainsi que des autres composants qui installent des règles.

## 2.3. Filtrage, routage et NAT : trois fonctions différentes

| Fonction | Question principale | Exemple |
|---|---|---|
| Routage | Où envoyer le paquet ? | Envoyer un paquet vers `wan0` |
| Filtrage | Le paquet est-il autorisé ? | Autoriser TCP vers le port 22 |
| Suivi des connexions | À quelle connexion ce paquet appartient-il ? | Reconnaître une réponse à une connexion existante |
| NAT | Faut-il modifier les adresses ou ports IP ? | Traduire l'adresse source d'un réseau privé |

Ces fonctions collaborent mais ne se remplacent pas.

Un paquet peut être correctement routé puis rejeté par le pare-feu. Un paquet peut être autorisé par le filtrage mais ne pas atteindre sa destination en raison d'une erreur de routage. Un paquet peut être traduit par NAT, mais rester bloqué par une règle de filtrage.

## 2.4. Pare-feu local et routeur Linux

Un serveur Linux qui héberge une application et un routeur Linux ne traitent pas le même type de trafic.

Un serveur reçoit généralement des paquets destinés à lui-même, produit ses propres paquets et peut éventuellement transférer du trafic.

Un routeur reçoit également des paquets provenant d'une interface et destinés à une autre interface.

```text
SERVEUR LINUX

        Réseau
          |
          v
     Interface réseau
          |
          v
       INPUT
          |
          v
     Application locale
```

```text
ROUTEUR LINUX

Réseau LAN                     Réseau WAN
    |                               ^
    v                               |
Interface LAN                  Interface WAN
    |                               ^
    +----------> FORWARD ------------+
                   |
             Filtrage et routage
```

Pour un serveur, les chaînes les plus importantes sont généralement `INPUT` et `OUTPUT`.

Pour un routeur, la chaîne `FORWARD` joue un rôle essentiel, en complément du routage et du NAT si celui-ci est nécessaire.


# 3. Comprendre le cheminement des paquets

## 3.1. Les principales étapes Netfilter

Pour IPv4 et IPv6, les hooks classiques les plus importants sont :

| Hook | Fonction générale |
|---|---|
| `PREROUTING` | traite les paquets reçus avant la décision de routage |
| `INPUT` | traite les paquets qui seront livrés au système local |
| `FORWARD` | traite les paquets routés vers une autre destination |
| `OUTPUT` | traite les paquets générés localement |
| `POSTROUTING` | traite les paquets après la décision de routage, avant leur sortie |

Ces termes sont utilisés directement dans la conception des chaînes nftables et correspondent aux points d'accrochage du traitement réseau du noyau.

## 3.2. Trafic entrant destiné à une application locale

Un client tente de se connecter au serveur Linux sur le port TCP 22.

```text
Client distant
      |
      | TCP destination port 22
      v
Interface du serveur
      |
      v
PREROUTING
      |
      v
Décision de routage
      |
      v
INPUT
      |
      +---- Règle autorisante
      |          |
      |          v
      |      Application SSH
      |
      +---- Règle bloquante
                 |
                 v
              Paquet rejeté
```

Si le paquet est autorisé, il peut être livré à la socket d'écoute SSH, sous réserve que le service soit réellement disponible et que les autres mécanismes du système permettent la connexion.

## 3.3. Trafic généré par la machine

Un serveur souhaite établir une connexion HTTPS vers un serveur distant.

```text
Application locale
        |
        v
Construction du paquet
        |
        v
OUTPUT
        |
        v
Décision de routage
        |
        v
POSTROUTING
        |
        v
Interface de sortie
        |
        v
Réseau distant
```

Le trafic produit par une application locale ne suit pas le chemin `INPUT` ou `FORWARD` pour son premier paquet sortant. La chaîne `OUTPUT` est le point de filtrage pertinent.

## 3.4. Trafic traversant le routeur

Un client du LAN contacte une destination sur Internet.

```text
Client LAN
    |
    v
Interface LAN
    |
    v
PREROUTING
    |
    v
Décision de routage
    |
    v
FORWARD
    |
    v
POSTROUTING
    |
    v
Interface WAN
    |
    v
Internet
```

Le trafic ne sera pas nécessairement transmis à travers le routeur : il faut que le routage soit possible et que les règles le permettent.

Lorsque NAT est appliqué, l'adresse du paquet peut être modifiée au cours de ce processus.

## 3.5. La décision de routage intervient entre certains hooks

Une règle de filtrage ne décide pas de la route à elle seule.

Le noyau détermine le chemin en fonction de la destination et de la table de routage, ainsi que d'autres paramètres éventuels.

Cette distinction aide à éviter une erreur fréquente : tenter de corriger avec le pare-feu une situation où le système ne possède simplement pas de route valide.


# 4. Comprendre le modèle de filtrage : règles, chaînes et politiques

## 4.1. Une règle de pare-feu

Une règle comprend généralement :

1. des critères de correspondance ;
2. une action ou un verdict.

Exemple conceptuel :

```text
Si :
    protocole TCP
    port de destination 22
    interface d'entrée autorisée

Alors :
    accepter le paquet
```

Dans nftables, une règle peut être écrite :

```nft
iifname "lan0" tcp dport 22 accept
```

Cela signifie que les paquets qui correspondent à tous les critères de la règle sont acceptés.

Les critères d'une règle sont généralement combinés avec un ET logique : ils doivent tous correspondre pour que l'action soit exécutée.

## 4.2. Les principaux verdicts

| Verdict | Rôle |
|---|---|
| `accept` | autoriser le paquet à poursuivre son traitement |
| `drop` | supprimer silencieusement le paquet |
| `reject` | rejeter le paquet et, lorsque c'est possible, envoyer une réponse de rejet |
| `return` | revenir à la chaîne appelante dans le traitement d'une chaîne ordinaire |
| `jump` | appeler une autre chaîne et prévoir un retour |
| `goto` | poursuivre dans une autre chaîne selon les règles de contrôle de nftables |

La signification exacte dépend de la construction employée.

Il faut aussi comprendre qu'un `accept` dans une chaîne n'est pas toujours une garantie que le paquet traversera toutes les autres chaînes ou tous les mécanismes de filtrage du système. D'autres points de traitement peuvent encore intervenir.

## 4.3. Différence entre DROP et REJECT

`drop` abandonne le paquet sans envoyer de réponse de rejet au client.

`reject` peut renvoyer une réponse adaptée au protocole, comme une erreur ICMP ou un rejet TCP.

Exemple nftables :

```nft
tcp dport 23 reject with tcp reset
```

Cette règle rejette les connexions TCP visant le port 23 avec une réponse de réinitialisation TCP, lorsque ce comportement est applicable.

Un rejet explicite peut accélérer le diagnostic côté client, tandis qu'un rejet silencieux peut produire des délais d'attente. Le choix dépend de la politique de sécurité et des besoins opérationnels.

## 4.4. Pourquoi une politique par défaut restrictive est-elle importante ?

Une chaîne de filtrage peut posséder une politique par défaut, par exemple `accept` ou `drop`.

Une politique `drop` signifie que les paquets qui atteignent la fin de la chaîne de base sans recevoir de verdict terminal seront abandonnés.

Cette approche est souvent utile pour les chaînes d'entrée et de transfert d'un pare-feu restrictif.

Cependant, définir une politique `drop` sans avoir d'abord créé les règles qui autorisent les connexions nécessaires peut interrompre les services ou verrouiller une administration à distance.


# 5. nftables : structure et syntaxe

## 5.1. Les objets nftables

nftables utilise une structure hiérarchique.

```text
Ruleset complet
    |
    v
Tables
    |
    v
Chaînes
    |
    v
Règles
    |
    +-- Expressions de correspondance
    |
    +-- Verdicts ou actions
    |
    +-- Compteurs éventuels
```

Le *ruleset* est l'ensemble des objets de filtrage chargés dans le contexte réseau considéré.

Contrairement à l'ancien modèle iptables, nftables ne crée pas automatiquement toutes les tables et chaînes traditionnelles. On définit les objets qui répondent aux besoins du pare-feu.

## 5.2. Les familles de tables

Les familles définissent les types de paquets que les objets peuvent traiter.

| Famille | Usage général |
|---|---|
| `ip` | IPv4 |
| `ip6` | IPv6 |
| `inet` | IPv4 et IPv6 dans les chaînes compatibles |
| `arp` | traitement associé à ARP |
| `bridge` | filtrage dans des scénarios de pont Ethernet |
| `netdev` | traitement de trafic à des points spécifiques au niveau d'une interface |

Pour un pare-feu de serveur qui traite principalement le trafic IP, la famille `inet` simplifie souvent la gestion commune d'IPv4 et d'IPv6.

Toutes les expressions ne sont pas applicables à toutes les familles. Une règle destinée à IPv4 doit être adaptée lorsqu'elle vise IPv6.

## 5.3. Créer et inspecter une table

Dans un environnement de laboratoire :

```bash
sudo nft add table inet lab_firewall
```

Afficher le ruleset :

```bash
sudo nft list ruleset
```

Afficher uniquement la table :

```bash
sudo nft list table inet lab_firewall
```

Si la table existe déjà, la commande de création peut échouer. Vérifiez l'état courant avant de recréer ou de supprimer des objets.

## 5.4. Créer une chaîne de base

```bash
sudo nft 'add chain inet lab_firewall input { type filter hook input priority 0; policy drop; }'
```

Cette commande crée une chaîne de base pour le trafic entrant vers le système local, avec une politique restrictive.

Attention : la chaîne ne contient encore aucune règle autorisante. Le fait de créer cette chaîne ne revient pas à construire un pare-feu complet et utilisable.

De plus, si d'autres chaînes ou services de filtrage sont actifs, leurs interactions peuvent affecter le traitement final.

## 5.5. Syntaxe dans un fichier

Dans un fichier de configuration nftables, les éléments peuvent être écrits sans les échappements nécessaires à certaines formes de commande dans le shell.

Exemple de fichier :

```nft
table inet lab_firewall {
    chain input {
        type filter hook input priority 0;
        policy drop;
    }
}
```

Le fichier contient une déclaration structurée. Le programme `nft` lit la configuration et communique avec l'infrastructure Netfilter.

Pour les configurations persistantes, la syntaxe dans un fichier est plus facile à contrôler, versionner et tester que des séries de commandes interactives.


# 6. Priorités et hooks nftables

## 6.1. Comprendre les priorités

Les chaînes de base associées à un même hook sont ordonnées selon leur priorité numérique. Les opérations internes du noyau, dont le suivi des connexions et certains traitements NAT, possèdent également des points d'intervention.

Les priorités usuelles des familles IP incluent notamment :

| Opération | Priorité conventionnelle |
|---|---:|
| Certains traitements avant le suivi des connexions | `-300` |
| Conntrack | `-200` |
| Mangle | `-150` |
| Destination NAT | `-100` |
| Filtrage | `0` |
| Source NAT | `100` |

Ces nombres sont des valeurs de référence courantes pour les hooks IP. Les possibilités et interactions varient selon la famille, le hook, la version et les fonctions utilisées.

Pour les scénarios ordinaires, préférez les mots-clés de priorité lorsque la version de nftables les prend en charge :

```nft
priority filter
priority dstnat
priority srcnat
```

Ne modifiez pas les priorités sans comprendre les mécanismes du noyau qui interviennent avant et après la chaîne.

## 6.2. Pourquoi les priorités comptent-elles ?

Un paquet peut être soumis à plusieurs opérations avant d'atteindre sa destination.

Par exemple, pour une connexion entrante qui fait l'objet d'une traduction de destination :

1. le paquet arrive sur une interface ;
2. certaines opérations préliminaires sont effectuées ;
3. la décision de traduction de destination peut être appliquée ;
4. le noyau décide ensuite où le paquet doit être envoyé ;
5. le paquet est soumis aux règles de filtrage appropriées.

Les priorités influencent l'ordre dans lequel certaines chaînes s'exécutent. Une priorité incorrecte peut changer le résultat du traitement.

## 6.3. Règle pratique

Pour un pare-feu standard :

- utilisez les hooks habituels ;
- utilisez des priorités conventionnelles ;
- gardez une organisation simple ;
- évitez les chaînes multiples concurrentes sans nécessité ;
- examinez les règles déjà installées avant d'ajouter les vôtres.


# 7. Conntrack : suivre l'état des connexions

## 7.1. Pourquoi suivre les connexions ?

Sans suivi de connexion, le pare-feu devrait examiner chaque paquet sans disposer de l'historique associé à la communication.

Conntrack permet de conserver des informations sur les flux observés et d'aider le pare-feu à distinguer différentes situations.

Cela facilite notamment les politiques qui autorisent une nouvelle connexion vers un service donné et laissent passer les paquets de réponse associés.

## 7.2. Les états courants

Les états généralement utilisés par nftables comprennent :

| État | Signification générale |
|---|---|
| `new` | paquet associé à une nouvelle connexion ou à une tentative de connexion nouvelle selon le protocole et les états observés |
| `established` | paquet associé à une connexion suivie qui a atteint un état établi selon conntrack |
| `related` | paquet associé à une connexion suivie existante, selon les mécanismes de suivi et les relations reconnues |
| `invalid` | paquet que conntrack ne peut pas associer correctement à un état valide |
| `untracked` | paquet qui n'est pas suivi par conntrack |

Les états ne doivent pas être interprétés comme une preuve d'identité du client. Ils décrivent la façon dont le mécanisme de suivi classe le trafic.

## 7.3. Autoriser les communications établies

Règle nftables :

```nft
ct state established,related accept
```

Cette règle autorise les paquets associés aux connexions établies et aux connexions reconnues comme liées.

Elle est fréquemment utilisée dans les règles d'entrée et de transfert.

Cependant, elle doit être intégrée à une politique qui contrôle aussi les nouvelles connexions. Le simple fait qu'un paquet ait un état donné ne remplace pas une politique complète.

## 7.4. Bloquer les paquets invalides

```nft
ct state invalid drop
```

Cette règle abandonne les paquets classés comme invalides.

Elle constitue une mesure courante, mais son effet dépend du contexte. Ne concluez pas que chaque paquet classé invalide correspond nécessairement à une attaque.

## 7.5. Visualiser les connexions

Si les outils conntrack sont installés :

```bash
sudo conntrack -L
```

Pour afficher les événements en temps réel :

```bash
sudo conntrack -E
```

Les sorties peuvent être nombreuses. Utilisez les options de filtre appropriées lorsque vous cherchez une connexion spécifique.

La disponibilité de cet outil dépend de l'installation et des fonctionnalités du noyau.

## 7.6. Pourquoi ne pas autoriser tous les nouveaux paquets ?

Une politique de pare-feu doit définir les nouvelles connexions autorisées.

Exemple de principe :

```nft
ct state established,related accept
tcp dport 22 accept
tcp dport { 80, 443 } accept
```

La première règle prend en charge les communications suivies. Les suivantes autorisent des nouvelles connexions visant les services spécifiés.

Les règles sont à adapter aux interfaces, aux réseaux sources et aux services réellement nécessaires.


# 8. Construire un pare-feu de serveur avec nftables

Cette section construit un pare-feu destiné à une machine Linux qui héberge des services.

## 8.1. Cahier des charges

Imaginons un serveur possédant :

```text
Interface : enp0s3
Rôle : serveur web et administration SSH
Services :
- SSH TCP 22
- HTTP TCP 80
- HTTPS TCP 443
```

Ce modèle suppose que ces ports correspondent aux services voulus. Dans un véritable environnement, il convient de limiter les sources d'accès lorsque cela est possible.

Avant l'application d'une politique restrictive, vérifiez la configuration existante et prévoyez un moyen de récupération.

## 8.2. Construire le fichier de configuration

Créez un fichier dans votre laboratoire, par exemple :

```text
lab-server.nft
```

Contenu :

```nft
#!/usr/sbin/nft -f

table inet server_firewall {
    chain input {
        type filter hook input priority filter;
        policy drop;

        # Autoriser le trafic local.
        iifname "lo" accept

        # Refuser les paquets associés à un état invalide.
        ct state invalid drop

        # Autoriser les connexions existantes et associées.
        ct state established,related accept

        # Autoriser les messages de diagnostic IPv4.
        ip protocol icmp accept

        # Autoriser ICMPv6, nécessaire à plusieurs fonctions IPv6.
        meta l4proto ipv6-icmp accept

        # Autoriser l'administration SSH.
        tcp dport 22 ct state new accept

        # Autoriser les services web.
        tcp dport { 80, 443 } ct state new accept
    }

    chain forward {
        type filter hook forward priority filter;
        policy drop;
    }

    chain output {
        type filter hook output priority filter;
        policy accept;
    }
}
```

## 8.3. Comprendre chaque chaîne

### `input`

Cette chaîne traite les paquets destinés au système local.

La politique `drop` interdit les paquets qui ne correspondent à aucune règle d'autorisation.

La règle `iifname "lo" accept` autorise le trafic de boucle locale.

La règle `ct state invalid drop` rejette le trafic classé comme invalide.

La règle `ct state established,related accept` permet les réponses des connexions suivies.

Les règles suivantes autorisent des services précis.

### `forward`

Cette chaîne traite les paquets qui traversent la machine en étant routés vers une autre destination.

La politique `drop` signifie qu'aucun trafic transféré ne sera autorisé sans règle supplémentaire.

C'est un choix prudent pour un serveur qui ne doit pas servir de routeur.

### `output`

Cette chaîne traite les paquets produits localement.

La politique `accept` autorise le trafic sortant qui atteint cette chaîne, sous réserve d'autres mécanismes de filtrage.

Un environnement très restrictif peut nécessiter une politique de sortie plus précise. Il faut alors documenter les dépendances réseau des services.

## 8.4. Pourquoi autoriser ICMP et ICMPv6 ?

ICMP transporte des messages de contrôle et d'erreur utilisés par plusieurs mécanismes réseau.

ICMPv6 est également essentiel à des fonctions IPv6, notamment Neighbor Discovery et la découverte de certains problèmes de chemin.

Un blocage aveugle d'ICMP et d'ICMPv6 peut provoquer des problèmes de connectivité difficiles à diagnostiquer.

L'exemple utilise une règle IPv4 ICMP et autorise ICMPv6. Dans une politique de sécurité particulièrement restrictive, vous pouvez affiner les types ICMPv6 autorisés selon le besoin, tout en préservant les mécanismes requis par le réseau.

## 8.5. Vérifier le fichier sans l'appliquer

```bash
sudo nft -c -f lab-server.nft
```

L'option `-c` demande à nftables de vérifier la validité de la configuration sans effectuer normalement les changements demandés.

Corrigez toute erreur signalée avant de poursuivre.

## 8.6. Charger les règles dans un laboratoire

```bash
sudo nft -f lab-server.nft
```

Cette commande charge les objets décrits dans le fichier.

Attention : le fichier ci-dessus crée une table nommée `server_firewall`. Si cette table existe déjà, un nouveau chargement peut échouer à la création de la table.

Pour rendre le déploiement répétable, vous pouvez concevoir un fichier déclaratif qui traite explicitement la table qu'il possède. Ne videz pas globalement le ruleset sans avoir vérifié que vous ne supprimeriez pas des règles gérées par d'autres composants.

## 8.7. Examiner le résultat

```bash
sudo nft list ruleset
sudo nft list table inet server_firewall
```

Vérifiez que la table et les chaînes correspondent à ce qui a été défini.

Puis contrôlez les services :

```bash
ss -tuln
```

Le pare-feu peut autoriser un port même si aucun service n'écoute dessus. Inversement, un service peut écouter alors que le pare-feu empêche son accès.

## 8.8. Limiter SSH à un réseau d'administration

Au lieu d'autoriser le port 22 depuis n'importe quelle source, il peut être préférable de restreindre l'accès à un réseau de gestion.

Supposons que le réseau autorisé soit `192.168.10.0/24`.

Remplacez la règle SSH globale par :

```nft
ip saddr 192.168.10.0/24 tcp dport 22 ct state new accept
```

La règle autorise les nouvelles connexions TCP vers le port 22 provenant du réseau indiqué.

Cette adresse est un exemple. Utilisez le réseau réel de votre administration.

### Attention à IPv6

Cette règle est spécifique à IPv4. Si le serveur est accessible par IPv6, une règle IPv6 adaptée peut être nécessaire.

Dans une table de famille `inet`, une restriction IPv4 ne doit pas être considérée comme couvrant automatiquement IPv6.

## 8.9. Compter les paquets

Les compteurs peuvent aider à mesurer l'utilisation d'une règle.

Exemple :

```nft
tcp dport 22 counter accept
```

Le mot-clé `counter` compte les paquets et les octets qui correspondent à cette règle.

Pour un diagnostic utile, ajoutez des compteurs aux points où vous souhaitez mesurer le trafic, puis examinez-les avec `nft list ruleset`.


# 9. Chaînes personnalisées et organisation des règles

## 9.1. Pourquoi créer une chaîne personnalisée ?

Une chaîne personnalisée permet de séparer les règles par responsabilité.

Exemple :

```text
table inet server_firewall
    |
    +-- input
          |
          +-- règles de base
          |
          +-- administration
          |
          +-- services web
          |
          +-- diagnostic
```

Le but n'est pas simplement d'ajouter des chaînes, mais de rendre les règles plus lisibles et faciles à maintenir.

## 9.2. Exemple de chaîne dédiée

Dans un fichier nftables :

```nft
table inet server_firewall {
    chain administration {
        tcp dport 22 ct state new accept
    }

    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept
        ct state invalid drop
        ct state established,related accept

        jump administration
    }
}
```

Les règles de la chaîne appelée sont évaluées lorsque `jump` est exécuté.

Lorsque la chaîne appelée atteint sa fin sans verdict terminal, le traitement revient à la chaîne appelante.

Cet exemple est destiné à un laboratoire. Il ne constitue pas un pare-feu complet pour toutes les configurations d'un serveur, notamment si IPv6 doit être utilisé ou si des services additionnels sont requis.

## 9.3. `jump` et `goto`

`jump` appelle une chaîne et prévoit le retour au point suivant de la chaîne appelante lorsque la chaîne appelée retourne normalement.

`goto` transfère le contrôle vers une autre chaîne selon les règles de nftables, sans créer le même point de retour que `jump`.

Pour les configurations débutantes et intermédiaires, utilisez généralement `jump` lorsque vous souhaitez organiser les règles par sous-ensembles et revenir à la chaîne d'origine.

N'utilisez `goto` que lorsque le comportement de contrôle est réellement souhaité et compris.


# 10. iptables : tables, chaînes et cibles

iptables est l'interface historique de gestion des règles Netfilter.

Elle est encore présente sur de nombreux systèmes, notamment pour maintenir des scripts et des configurations hérités.

Pour les nouvelles configurations, nftables est généralement préférable lorsque la distribution et l'environnement le permettent.

## 10.1. Les tables iptables classiques

| Table | Fonction traditionnelle |
|---|---|
| `filter` | filtrage des paquets |
| `nat` | traduction d'adresses et de ports |
| `mangle` | modifications ou marquages de paquets dans les contextes pris en charge |
| `raw` | actions effectuées notamment en interaction avec le suivi des connexions |
| `security` | règles associées à certains mécanismes de sécurité |

La disponibilité et les fonctionnalités précises dépendent du backend et du système.

## 10.2. Les chaînes iptables

Dans la table `filter`, les chaînes intégrées courantes sont :

| Chaîne | Fonction |
|---|---|
| `INPUT` | paquets destinés à la machine locale |
| `OUTPUT` | paquets générés localement |
| `FORWARD` | paquets transférés par le système |

Dans la table `nat`, les chaînes habituelles incluent :

| Chaîne | Fonction |
|---|---|
| `PREROUTING` | traduction de destination avant la décision de routage |
| `OUTPUT` | traitement NAT associé aux paquets générés localement |
| `POSTROUTING` | traduction de source après la décision de routage |

La façon dont ces chaînes interviennent est liée aux hooks Netfilter et au traitement du routage.

## 10.3. Les cibles courantes

| Cible | Signification |
|---|---|
| `ACCEPT` | accepter le paquet |
| `DROP` | abandonner silencieusement le paquet |
| `REJECT` | rejeter le paquet |
| `LOG` | enregistrer un message selon la configuration et le backend |
| `DNAT` | modifier la destination |
| `SNAT` | modifier la source |
| `MASQUERADE` | traduire la source en utilisant généralement l'adresse de l'interface de sortie |

Les noms et les usages des cibles sont propres à la syntaxe iptables. Ne transposez pas directement toutes les constructions en syntaxe nftables sans vérifier la correspondance fonctionnelle.

## 10.4. Afficher les règles

```bash
sudo iptables -L -n -v
```

Cette commande affiche les règles des chaînes de la table `filter` avec les compteurs et sans résolution de noms.

Pour afficher la représentation sous forme de commandes :

```bash
sudo iptables -S
```

Pour la table NAT :

```bash
sudo iptables -t nat -L -n -v
```

Pour IPv6 :

```bash
sudo ip6tables -L -n -v
```

Un pare-feu IPv4 correct ne garantit pas que le trafic IPv6 est filtré selon la même politique.

## 10.5. Examiner le backend actif

```bash
iptables -V
```

Selon la distribution, vous pouvez voir une indication de backend telle que `nf_tables` ou `legacy`.

Sur les systèmes utilisant le mécanisme alternatives, examinez également la configuration :

```bash
update-alternatives --display iptables
```

Cette commande est disponible sur les systèmes qui utilisent `update-alternatives`, notamment Debian et Ubuntu.

L'objectif est de savoir si les outils iptables utilisent le backend nftables ou une implémentation historique distincte.


# 11. Configurer un pare-feu simple avec iptables

Cette section sert principalement à comprendre ou maintenir des systèmes existants.

**Ne remplacez pas une politique de production en copiant directement ces commandes.** Elles sont destinées à un laboratoire dont l'accès peut être récupéré depuis la console.

## 11.1. Exemple : autoriser le trafic de boucle locale

```bash
sudo iptables -A INPUT -i lo -j ACCEPT
```

Cette commande ajoute une règle autorisant le trafic entrant sur l'interface de boucle locale.

## 11.2. Autoriser les connexions établies

```bash
sudo iptables -A INPUT \
  -m conntrack \
  --ctstate ESTABLISHED,RELATED \
  -j ACCEPT
```

Cette règle autorise les paquets entrant associés aux connexions établies ou liées, selon conntrack.

## 11.3. Autoriser SSH

```bash
sudo iptables -A INPUT \
  -p tcp --dport 22 \
  -m conntrack --ctstate NEW \
  -j ACCEPT
```

Cette règle autorise les nouvelles connexions TCP vers le port 22.

Elle n'est pas restreinte par adresse source. En production, il est généralement préférable d'appliquer une politique d'accès limitée au réseau d'administration lorsque c'est possible.

## 11.4. Comprendre les politiques des chaînes

```bash
sudo iptables -P INPUT DROP
```

Cette commande définit la politique par défaut de la chaîne `INPUT` sur `DROP`.

Si elle est exécutée avant l'installation des règles autorisant SSH, l'administrateur peut perdre son accès distant.

Pour apprendre, installez et inspectez les règles dans une machine virtuelle avec une console de secours. En exploitation, préparez une procédure de retour arrière avant de modifier une politique restrictive.

## 11.5. Éviter les duplications

Une règle ajoutée avec `-A` peut être répétée si la procédure est relancée.

Vérifiez les règles existantes :

```bash
sudo iptables -S INPUT
```

Dans un script, vous pouvez contrôler la présence d'une règle avant de l'ajouter :

```bash
sudo iptables -C INPUT -i lo -j ACCEPT 2>/dev/null || \
  sudo iptables -A INPUT -i lo -j ACCEPT
```

Cette forme permet d'éviter une duplication dans ce scénario simple. Elle ne suffit pas à garantir qu'une configuration complète sera cohérente si les règles changent ou si d'autres processus modifient simultanément le pare-feu.

## 11.6. Enregistrer et restaurer des règles

Pour sauvegarder les règles iptables IPv4 :

```bash
sudo iptables-save > iptables-backup.rules
```

Pour afficher le contenu sauvegardé :

```bash
cat iptables-backup.rules
```

Pour le restaurer dans un environnement où le contenu est approuvé :

```bash
sudo iptables-restore < iptables-backup.rules
```

Une restauration peut remplacer les règles existantes selon le contenu du fichier et les opérations qu'il contient. Vérifiez ce que vous chargez avant de l'exécuter.

Les règles IPv6 doivent être traitées séparément lorsque le pare-feu utilise les outils ip6tables.


# 12. NAT : comprendre la traduction d'adresses

## 12.1. Qu'est-ce que le NAT ?

NAT signifie *Network Address Translation*.

Le NAT modifie une ou plusieurs informations d'adresse IP, et éventuellement de port, au cours du traitement des paquets.

Deux besoins très courants sont :

- permettre à plusieurs machines d'un réseau privé de partager une adresse IP de sortie ;
- rendre un service interne accessible depuis une autre zone réseau.

## 12.2. Topologie de référence

Pour les exemples suivants, utilisons un routeur Linux avec deux interfaces.

```text
                         INTERNET
                            |
                            |
                  +---------------------+
                  | Routeur Linux       |
                  |                     |
                  | WAN : wan0          |
                  | LAN : lan0          |
                  +---------------------+
                            |
                            |
                  Réseau LAN privé
                  192.168.50.0/24
                            |
                  +---------+---------+
                  |                   |
                  v                   v
             Client 01           Serveur interne
             192.168.50.20       192.168.50.10
```

Les adresses, noms d'interfaces et réseaux utilisés sont des exemples. Adaptez-les au laboratoire.

## 12.3. Sans NAT : problème fréquent

Un client du LAN peut envoyer un paquet vers Internet, mais le réseau amont doit aussi disposer d'une route de retour vers l'adresse privée du client.

Si le réseau amont ne possède pas cette route, la réponse peut ne pas parvenir au client.

## 12.4. Avec NAT source

Le routeur remplace l'adresse source privée par une adresse de sortie appropriée.

```text
AVANT NAT

Source      : 192.168.50.20
Destination : 203.0.113.10

       |
       v

APRÈS NAT

Source      : adresse de sortie du routeur
Destination : 203.0.113.10
```

La réponse peut revenir à l'adresse de sortie du routeur. Conntrack permet ensuite d'appliquer la traduction inverse au trafic appartenant à cette connexion.

Le réseau amont doit néanmoins autoriser le trafic et le chemin réseau doit être valide.

## 12.5. Les principales formes de NAT

| Mécanisme | Rôle |
|---|---|
| SNAT | modifie l'adresse source vers une adresse explicitement choisie |
| MASQUERADE | variante de SNAT qui utilise généralement l'adresse de l'interface de sortie |
| DNAT | modifie la destination d'un paquet |
| REDIRECT | variante de redirection de destination vers la machine locale |

Ces mécanismes sont distincts du routage. Un routeur qui réalise du NAT doit toujours posséder les routes nécessaires et autoriser le trafic dans les chaînes de filtrage pertinentes.


# 13. SNAT et MASQUERADE

## 13.1. SNAT

SNAT signifie *Source Network Address Translation*.

Il est généralement utilisé en sortie, au hook `POSTROUTING`, pour remplacer une adresse source par une autre adresse.

Exemple conceptuel :

```text
Paquet avant traduction :
192.168.50.20 -> destination distante

Paquet après SNAT :
198.51.100.20 -> destination distante
```

L'adresse `198.51.100.20` appartient à une plage réservée aux exemples. Elle ne constitue pas une véritable adresse publique à utiliser sur un réseau.

## 13.2. MASQUERADE

MASQUERADE est souvent utilisé lorsque l'adresse IP de sortie est dynamique ou susceptible de changer.

Il permet de traduire les sources du réseau privé en utilisant l'adresse de l'interface de sortie.

Exemple nftables :

```nft
ip saddr 192.168.50.0/24 oifname "wan0" masquerade
```

Cette règle doit se trouver dans une chaîne NAT de type `postrouting`.

Le mécanisme convient couramment à une passerelle dont l'adresse de sortie est attribuée par DHCP. Pour une adresse source fixe et des besoins précis, SNAT peut être préférable.

## 13.3. Pourquoi le NAT ne suffit-il pas ?

Pour qu'un client traverse le routeur, il faut au minimum :

1. une adresse IP valide sur le client ;
2. une passerelle adaptée ;
3. le routage activé sur le routeur ;
4. une route de sortie ;
5. une règle de transfert autorisant le trafic ;
6. une règle NAT cohérente si la traduction est nécessaire ;
7. un réseau amont qui transmet les paquets.

Une règle `masquerade` ne remplace aucune de ces étapes.


# 14. DNAT et transfert de ports

## 14.1. Comprendre le DNAT

DNAT modifie l'adresse de destination du paquet.

Ce mécanisme peut être utilisé pour exposer un service interne à travers un routeur.

Exemple :

```text
Client externe
198.51.100.50
      |
      | TCP destination wan0:8080
      v
Routeur Linux
      |
      | DNAT : port 8080 -> serveur interne port 80
      v
Serveur interne
192.168.50.10:80
```

Les adresses de documentation sont fictives.

Le routeur reçoit le paquet et réécrit sa destination. Le noyau peut ensuite décider de le transférer vers le serveur interne.

## 14.2. Pourquoi le DNAT ne suffit-il pas ?

La traduction de destination ne garantit pas que la communication aboutira.

Il faut également que :

- la destination après traduction soit correcte ;
- le routeur possède le routage nécessaire ;
- le transfert IP soit activé ;
- la chaîne `FORWARD` autorise le trafic ;
- le serveur interne écoute sur le port attendu ;
- le serveur interne possède une route de retour appropriée ;
- les pare-feu sur le serveur et sur les réseaux traversés autorisent la communication.

Une erreur dans l'un de ces éléments peut empêcher la connexion.

## 14.3. REDIRECT

REDIRECT est un mécanisme qui dirige le trafic vers un service local.

Il est notamment employé dans certains scénarios de proxy transparent ou de redirection locale.

Il ne doit pas être confondu avec le transfert de port DNAT vers un autre hôte.


# 15. Configurer le NAT avec nftables

Cette section met en place un scénario de routeur IPv4 dans un laboratoire isolé.

## 15.1. Prérequis de topologie

Le routeur possède deux interfaces :

```text
lan0 : interface LAN
wan0 : interface WAN
```

Le réseau LAN est :

```text
192.168.50.0/24
```

La passerelle LAN du routeur est supposée avoir une adresse dans ce réseau.

Avant de configurer les règles, vérifiez :

```bash
ip -br address
ip route
```

Les interfaces doivent déjà disposer d'une configuration d'adressage valide et d'une route de sortie adaptée.

## 15.2. Activer le routage IPv4

Le transfert IPv4 est contrôlé par le paramètre du noyau :

```text
net.ipv4.ip_forward
```

Vérifiez sa valeur :

```bash
sysctl net.ipv4.ip_forward
```

Pour activer temporairement le routage dans un laboratoire :

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Cette modification est temporaire et peut être perdue au redémarrage.

## 15.3. Rendre le routage persistant

Pour un routeur de laboratoire dont la conception a été vérifiée, créez un fichier tel que :

```text
/etc/sysctl.d/99-ip-forward.conf
```

Contenu :

```ini
net.ipv4.ip_forward = 1
```

Puis appliquez les paramètres :

```bash
sudo sysctl --system
```

Le réglage du transfert IPv4 change le comportement de routage de la machine. Ne l'activez pas par défaut sur un poste ou un serveur qui ne doit pas transférer le trafic d'autres machines.

## 15.4. Exemple nftables pour le transfert et le NAT

Dans le fichier de configuration dédié au routeur :

```nft
table inet router_filter {
    chain forward {
        type filter hook forward priority filter;
        policy drop;

        ct state invalid drop

        ct state established,related accept

        iifname "lan0" oifname "wan0" \
            ip saddr 192.168.50.0/24 \
            accept
    }
}

table ip router_nat {
    chain postrouting {
        type nat hook postrouting priority srcnat;
        policy accept;

        oifname "wan0" \
            ip saddr 192.168.50.0/24 \
            masquerade
    }
}
```

L'objectif est de montrer la séparation entre filtrage du trafic transféré et traduction d'adresse.

La règle de transfert autorise le trafic IPv4 issu du réseau LAN vers l'interface WAN, puis permet le trafic retour associé à des connexions suivies.

La règle MASQUERADE traduit la source des paquets IPv4 quittant `wan0` lorsqu'ils proviennent du réseau privé indiqué.

Ce fichier n'est pas un pare-feu complet pour tous les usages d'un routeur. Il ne définit pas toutes les règles destinées au trafic local, à l'administration, à IPv6 ou aux autres interfaces.

## 15.5. Vérifier avant de charger

Enregistrez la configuration dans un fichier local, puis contrôlez-la :

```bash
sudo nft -c -f router.nft
```

Si la validation réussit, examinez les objets qui existent déjà :

```bash
sudo nft list ruleset
```

Sur un système utilisé par d'autres services réseau, ne chargez pas aveuglément une configuration qui modifie des tables déjà administrées.

Le contenu de l'exemple doit être adapté à la configuration actuelle et aux autres outils qui gèrent le pare-feu.

## 15.6. Charger et inspecter

Dans le laboratoire :

```bash
sudo nft -f router.nft
```

Puis :

```bash
sudo nft list table inet router_filter
sudo nft list table ip router_nat
```

Vérifiez les adresses et routes du routeur ainsi que le paramètre `net.ipv4.ip_forward`.

## 15.7. Tester depuis un client

Sur un client du réseau privé :

```bash
ip route
ping -c 3 ADRESSE_LAN_DU_ROUTEUR
```

Puis testez une destination externe autorisée.

Le succès dépend des routes du réseau virtuel, de l'interface WAN, du réseau amont et des règles présentes sur le routeur.

Ne diagnostiquez pas uniquement à partir du compteur NAT : vérifiez également le chemin réseau et les règles de transfert.

## 15.8. Vérifier les compteurs

```bash
sudo nft list ruleset
```

Si les règles comportent des compteurs, examinez le nombre de paquets et d'octets associés.

Un compteur qui ne progresse pas peut indiquer que le trafic ne traverse pas la règle attendue. Il peut aussi s'expliquer par un trafic différent de celui que vous cherchez ou par un autre chemin de traitement.


# 16. Configurer le transfert de port avec nftables

Le transfert de port requiert à la fois DNAT et le filtrage du trafic transféré.

## 16.1. Exemple de scénario

```text
Réseau externe
      |
      | TCP destination port 8080
      v
Routeur
wan0
      |
      | DNAT vers 192.168.50.10:80
      v
Serveur Web interne
192.168.50.10:80
      |
      v
Réseau LAN
```

Le routeur présente le port 8080 sur son interface WAN et dirige les connexions vers le port 80 du serveur interne.

Utilisez uniquement des adresses et services que vous administrez.

## 16.2. Règle de destination NAT

Dans une table NAT de famille IPv4 :

```nft
table ip router_nat {
    chain prerouting {
        type nat hook prerouting priority dstnat;
        policy accept;

        iifname "wan0" tcp dport 8080 \
            dnat to 192.168.50.10:80
    }
}
```

Cette règle réécrit la destination des connexions TCP entrantes visant le port 8080 de `wan0`.

Il ne faut pas considérer cette règle comme une garantie de sécurité ou comme une configuration de pare-feu complète. Elle n'autorise pas à elle seule la circulation dans toutes les chaînes de filtrage.

## 16.3. Autoriser le trafic transféré

La chaîne de transfert peut inclure une règle dédiée :

```nft
iifname "wan0" oifname "lan0" \
    ip daddr 192.168.50.10 \
    tcp dport 80 \
    ct status dnat \
    accept
```

Cette règle accepte les paquets transférés dont la destination a été traduite vers le serveur et le port spécifiés, en fonction des informations de suivi de connexion.

Elle doit être intégrée à une chaîne de base `forward` dont la politique et les règles existantes ont été examinées.

Les règles `established,related` restent généralement nécessaires pour permettre les paquets de retour.

## 16.4. Autoriser le serveur à répondre

Le serveur interne doit posséder une route de retour cohérente.

Dans un réseau classique où le routeur Linux constitue sa passerelle, les réponses peuvent repasser par le même routeur, qui utilisera l'état de connexion pour effectuer la traduction inverse.

Si le serveur utilise une autre passerelle, le trafic retour peut prendre un chemin différent et ne pas traverser le routeur qui a appliqué la traduction. Cela peut casser la session ou empêcher la traduction attendue.

## 16.5. Sécurité du transfert de port

Un transfert de port rend un service interne accessible depuis une autre zone réseau.

Avant de publier le service :

- vérifiez l'identité et l'usage du serveur cible ;
- limitez les sources autorisées lorsque c'est possible ;
- vérifiez les règles du routeur et du serveur ;
- confirmez les protocoles et ports réels ;
- surveillez les journaux ;
- assurez-vous que le service ne donne pas accès à des données qui ne devraient pas être exposées.

Un service interne n'est pas automatiquement sûr simplement parce qu'il était auparavant inaccessible depuis l'extérieur.


# 17. Comprendre le NAT avec iptables

## 17.1. MASQUERADE en IPv4

Dans un routeur Linux qui utilise iptables :

```bash
sudo iptables -t nat -A POSTROUTING \
  -s 192.168.50.0/24 \
  -o wan0 \
  -j MASQUERADE
```

Cette règle utilise la table `nat` et la chaîne `POSTROUTING`.

Elle traduit l'adresse source des paquets IPv4 issus du réseau indiqué et quittant l'interface `wan0`.

Cette règle ne remplace pas les règles de transfert et n'active pas automatiquement le routage.

## 17.2. Autoriser le transfert

Exemple pour permettre le trafic établi et le transfert du LAN vers le WAN :

```bash
sudo iptables -A FORWARD \
  -m conntrack \
  --ctstate ESTABLISHED,RELATED \
  -j ACCEPT
```

Puis :

```bash
sudo iptables -A FORWARD \
  -i lan0 \
  -o wan0 \
  -s 192.168.50.0/24 \
  -j ACCEPT
```

Ces commandes servent de démonstration. L'ordre et les règles existantes sont importants.

Dans un routeur réel, vérifiez ce qui est déjà configuré, notamment la politique par défaut de `FORWARD`.

## 17.3. Activer le routage IPv4

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Cette modification temporaire doit être réalisée sur une machine destinée à jouer le rôle de routeur.

Pour la rendre persistante, utilisez une configuration sysctl adaptée et vérifiez les règles de sécurité de la machine.

## 17.4. DNAT avec iptables

Exemple :

```bash
sudo iptables -t nat -A PREROUTING \
  -i wan0 \
  -p tcp --dport 8080 \
  -j DNAT --to-destination 192.168.50.10:80
```

La règle traduit les connexions entrantes vers le port 8080 de `wan0` pour les diriger vers le serveur interne sur le port 80.

Il faut ensuite que la chaîne `FORWARD` autorise ce trafic, que la route soit valide et que le serveur puisse répondre.

## 17.5. Examiner le résultat

```bash
sudo iptables -t nat -L -n -v
sudo iptables -L FORWARD -n -v
sudo iptables -S
```

Pour IPv6, les règles et outils correspondants doivent être examinés séparément si le trafic IPv6 est routé ou filtré.


# 18. nftables et iptables : comparaison pratique

## 18.1. Différences conceptuelles

| Aspect | nftables | iptables |
|---|---|---|
| Interface | `nft` | `iptables`, `ip6tables` |
| Organisation | tables, chaînes de base, chaînes ordinaires, sets et maps | tables et chaînes traditionnelles, cibles et extensions |
| IPv4/IPv6 | famille `inet` disponible pour les règles IP compatibles | gestion historiquement séparée par outil |
| Ensembles et maps | intégrés au framework | fonctions historiques souvent réparties entre outils et extensions |
| Configuration | syntaxe déclarative adaptée aux fichiers | commandes avec options et règles ajoutées successivement |
| Compatibilité | framework moderne Netfilter | outil historique, éventuellement sur backend nftables |
| Usages courants | nouvelles règles et maintenance moderne | compatibilité et maintenance de configurations existantes |

## 18.2. Ce que signifie `iptables-nft`

Sur de nombreux systèmes modernes, la commande `iptables` utilise un backend reposant sur l'API nftables.

Ainsi, `iptables` et `nft` peuvent interagir avec l'infrastructure nftables tout en utilisant des interfaces et abstractions différentes.

Le terme `iptables-legacy` désigne un backend historique distinct.

Il ne suffit donc pas de voir la commande `iptables` pour déterminer si les règles sont gérées avec le backend moderne ou l'implémentation historique.

## 18.3. Vérifier le backend

```bash
iptables -V
```

Puis, lorsque le système utilise le mécanisme alternatives :

```bash
update-alternatives --display iptables
```

Pour consulter la configuration native nftables :

```bash
sudo nft list ruleset
```

Si un gestionnaire utilise des règles iptables-nft, une partie de son état peut apparaître dans le ruleset nftables.

Les représentations et les possibilités de conversion ne sont toutefois pas identiques dans tous les cas.

## 18.4. Ne pas gérer la même politique à travers plusieurs systèmes indépendants

Imaginez les situations suivantes :

- un administrateur modifie manuellement nftables ;
- un service UFW réécrit des règles iptables ;
- un moteur de conteneurs ajoute des règles de transfert ;
- un VPN modifie la configuration du pare-feu.

Ces changements peuvent interagir et produire des résultats difficiles à expliquer.

La bonne approche consiste à identifier le gestionnaire propriétaire des règles et à définir les règles selon une méthode cohérente.

Plusieurs mécanismes peuvent coexister dans certaines architectures, mais il faut alors connaître les chaînes, priorités et interactions de chaque composant.

## 18.5. Politique de migration

Pour migrer un système existant :

1. inventorier les règles et leur origine ;
2. vérifier le backend actif ;
3. identifier les services qui créent des règles automatiquement ;
4. documenter la politique de filtrage actuelle ;
5. construire les règles nftables équivalentes ;
6. tester les différences ;
7. préparer le retour arrière ;
8. déployer de manière progressive ;
9. vérifier les compteurs et les communications réelles.

Une traduction syntaxique des commandes n'est pas toujours une équivalence fonctionnelle parfaite.


# 19. Persistance des règles nftables

## 19.1. Pourquoi les règles temporaires posent-elles problème ?

Les règles ajoutées depuis le terminal sont généralement associées au ruleset actif du namespace réseau et peuvent disparaître après un redémarrage ou lorsqu'une configuration est réinitialisée.

Il faut donc définir une méthode de chargement persistant.

## 19.2. Emplacement courant

Sur de nombreuses distributions, le fichier principal est :

```text
/etc/nftables.conf
```

La configuration peut également être organisée en plusieurs fichiers, si le mécanisme de chargement retenu le prévoit.

Avant de remplacer le fichier, consultez sa configuration existante et vérifiez si d'autres outils en dépendent.

## 19.3. Configurer le service système

Sur les distributions qui fournissent l'unité correspondante :

```bash
sudo systemctl enable nftables.service
sudo systemctl start nftables.service
```

Cette opération active la méthode de chargement du service nftables.

Il faut vérifier le comportement exact du service et de sa configuration sur la distribution concernée.

## 19.4. Exemple de fichier persistant

Un fichier central peut contenir les règles du serveur :

```nft
#!/usr/sbin/nft -f

table inet server_firewall {
    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept
        ct state invalid drop
        ct state established,related accept

        ip protocol icmp accept
        meta l4proto ipv6-icmp accept

        tcp dport 22 ct state new accept
        tcp dport { 80, 443 } ct state new accept
    }

    chain forward {
        type filter hook forward priority filter;
        policy drop;
    }

    chain output {
        type filter hook output priority filter;
        policy accept;
    }
}
```

Cette configuration est un exemple de laboratoire.

Avant de la placer dans `/etc/nftables.conf`, adaptez les services nécessaires et examinez les règles déjà présentes.

## 19.5. Vérifier avant de recharger

```bash
sudo nft -c -f /etc/nftables.conf
```

Examinez ensuite le contenu du fichier pour comprendre les changements qui seront effectués.

Lorsque l'on veut remplacer une table gérée exclusivement par ce fichier, on peut organiser la configuration de manière à détruire ou recréer uniquement cette table.

Évitez une commande globale qui efface toutes les tables si d'autres applications gèrent des règles distinctes.

## 19.6. `flush ruleset` : danger important

La commande :

```bash
sudo nft flush ruleset
```

vide l'ensemble du ruleset nftables dans le contexte concerné.

Elle peut supprimer des tables, des chaînes, des règles, des maps, des sets et des objets associés, y compris ceux gérés par d'autres applications.

Elle ne doit pas être utilisée aveuglément sur une machine réelle.

Dans un laboratoire isolé, elle peut servir à repartir d'un état connu lorsque vous contrôlez l'ensemble du ruleset. Sur un système partagé ou en production, privilégiez une gestion ciblée des objets dont vous êtes responsable.


# 20. Rendre iptables persistant

Les mécanismes exacts dépendent de la distribution.

Sur Debian et Ubuntu, on rencontre notamment le paquet `iptables-persistent`, qui peut charger des règles sauvegardées au démarrage.

Installation, si cette méthode est souhaitée :

```bash
sudo apt install iptables-persistent
```

Cette opération doit être effectuée conformément à la politique de gestion du système. Elle ne doit pas être utilisée pour remplacer aveuglément un gestionnaire de pare-feu déjà actif.

## 20.1. Sauvegarder l'état

```bash
sudo iptables-save
```

Pour écrire dans un fichier de sauvegarde protégé :

```bash
sudo sh -c 'iptables-save > /root/iptables-v4.rules'
```

Ce fichier appartient à l'administration système. Protégez-le et veillez à ce que son contenu ne soit pas exposé inutilement.

## 20.2. Restaurer un jeu de règles

```bash
sudo iptables-restore < /root/iptables-v4.rules
```

La restauration peut modifier le ruleset actif. Il est important de comprendre le fichier de sauvegarde et les conséquences sur l'accès réseau.

## 20.3. Et IPv6 ?

Si le système utilise IPv6, sauvegardez et restaurez également les règles IPv6 selon le mécanisme approprié.

Un pare-feu dont seule la configuration IPv4 est maîtrisée peut laisser un chemin IPv6 insuffisamment filtré.

Il faut vérifier les deux familles et leurs interactions.


# 21. Journalisation et diagnostic des règles

## 21.1. Pourquoi compter les paquets ?

Les compteurs donnent des indications sur le trafic qui correspond aux règles.

Si une règle d'acceptation ne reçoit aucun paquet, cela peut signifier :

- qu'aucun trafic correspondant n'a été envoyé ;
- que les conditions de la règle sont incorrectes ;
- qu'un autre chemin est utilisé ;
- que le paquet est bloqué avant d'atteindre la règle ;
- que les compteurs ont été réinitialisés.

Ils ne donnent pas automatiquement la cause d'un échec, mais permettent de vérifier le chemin suivi par le trafic.

## 21.2. Ajouter un compteur dans nftables

```nft
tcp dport 22 counter accept
```

Pour observer les compteurs :

```bash
sudo nft list ruleset
```

Pour examiner plus précisément une chaîne :

```bash
sudo nft list chain inet server_firewall input
```

## 21.3. Journaliser des paquets

Exemple :

```nft
tcp dport 22 log prefix "SSH_ATTEMPT: " counter accept
```

Cette règle journalise les paquets qui correspondent, puis les accepte.

Elle peut être utile dans un laboratoire, mais il faut faire attention au volume de journaux. Une règle qui journalise un grand nombre de paquets peut saturer la journalisation et compliquer l'analyse.

## 21.4. Limiter les journaux

Dans nftables, un mécanisme de limitation peut être ajouté à une règle de journalisation.

Exemple :

```nft
limit rate 5/second log prefix "FW: " counter
```

Cette règle limite le débit des messages de journalisation selon la syntaxe prise en charge par la version utilisée.

Elle doit être intégrée à une règle appropriée. Un test syntaxique est nécessaire avant son déploiement.

La limitation de débit n'exonère pas de définir un plan de journalisation adapté.

## 21.5. Journaux noyau

Selon la configuration du système :

```bash
journalctl -k
```

Les messages envoyés par certaines règles de filtrage peuvent apparaître dans les journaux du noyau.

Il faut distinguer les messages de journalisation du pare-feu des logs produits par l'application qui reçoit le trafic.

## 21.6. Éviter la journalisation excessive

Un pare-feu exposé à un flux important peut générer un volume considérable de messages.

Préférez :

- la journalisation des événements utiles ;
- une limite de débit ;
- des préfixes identifiables ;
- une politique de conservation ;
- un contrôle de l'espace disque ;
- des compteurs pour observer le trafic non nécessitant de log détaillé.


# 22. Tracer le chemin d'un paquet dans nftables

nftables permet d'utiliser des mécanismes de traçage pour comprendre quelles règles sont traversées par un paquet.

Le principe consiste à activer le suivi pour une sélection contrôlée de paquets, puis à consulter les événements de trace.

La procédure exacte dépend de la version, de la table, du hook et du contexte réseau.

Exemple conceptuel dans un laboratoire :

```nft
ip saddr 192.0.2.10 meta nftrace set 1
```

Cette règle active le traçage pour les paquets IPv4 correspondant à l'adresse source spécifiée, si elle est placée dans un contexte compatible.

L'adresse `192.0.2.10` est réservée à la documentation. Utilisez l'adresse source de votre laboratoire.

Ensuite, dans une autre session :

```bash
sudo nft monitor trace
```

Le traçage est un outil de diagnostic, pas une règle d'autorisation. Il peut générer beaucoup d'événements et doit être retiré ou désactivé après l'analyse.

N'activez pas le traçage indiscriminément sur tout le trafic d'une interface très chargée.


# 23. Conntrack et NAT : comprendre la traduction inverse

## 23.1. Pourquoi la réponse retrouve-t-elle le bon client ?

Lorsqu'une connexion traverse un routeur avec NAT stateful, le noyau peut conserver une association entre les informations de la connexion avant et après traduction.

Cela permet d'effectuer la traduction inverse sur les paquets de retour correspondant à cette connexion.

```text
CLIENT LAN
192.168.50.20:50000
        |
        | Source NAT
        v
ROUTEUR
203.0.113.20:61000
        |
        v
SERVEUR DISTANT
203.0.113.50:443
```

Le port `50000`, les adresses et les ports illustrent un scénario. Le port traduit peut être différent selon la disponibilité des tuples et l'implémentation.

Lorsque le serveur distant répond, le routeur retrouve l'association de suivi de connexion et réalise la traduction inverse afin que la réponse corresponde au client original.

## 23.2. Pourquoi la perte d'état peut-elle casser une connexion ?

Si le suivi de connexion ne reconnaît plus la session, le traitement des paquets peut ne plus produire le résultat attendu.

Cela peut arriver dans certains cas de redémarrage, de modification de topologie, de perte d'état ou lorsque les paquets prennent un chemin différent.

Dans les architectures à plusieurs routeurs ou plusieurs liens, il faut tenir compte de la symétrie des chemins et, selon le scénario, des mécanismes de synchronisation d'état.

## 23.3. Examiner les connexions NAT

```bash
sudo conntrack -L
```

L'examen doit se concentrer sur le protocole, les adresses et les ports liés au trafic que vous cherchez à diagnostiquer.

Une entrée de conntrack indique qu'une association est suivie. Elle ne prouve pas que le service applicatif est sain.


# 24. IPv6 : ne pas oublier le filtrage

## 24.1. IPv4 et IPv6 sont deux familles distinctes

Une règle IPv4 ne filtre pas nécessairement les paquets IPv6.

Exemple de réseau :

```text
Serveur Linux
   |
   +-- IPv4 : 192.168.10.20/24
   |
   +-- IPv6 : 2001:db8:10::20/64
```

Même si l'administrateur configure correctement IPv4, des services peuvent rester accessibles via IPv6 selon les adresses et les règles.

## 24.2. Pourquoi la famille `inet` est-elle utile ?

Dans nftables :

```nft
table inet server_firewall {
    chain input {
        type filter hook input priority filter;
        policy drop;
    }
}
```

La famille `inet` permet de gérer IPv4 et IPv6 dans une même structure pour les règles compatibles.

Il faut néanmoins utiliser les critères adaptés au protocole.

Une condition telle que :

```nft
ip saddr 192.168.10.0/24
```

est spécifique à IPv4.

Une condition IPv6 doit utiliser les champs `ip6`, par exemple :

```nft
ip6 saddr 2001:db8:10::/64
```

Ces adresses appartiennent à une plage réservée aux exemples.

## 24.3. ICMPv6

ICMPv6 fournit des fonctions indispensables au bon fonctionnement de plusieurs mécanismes IPv6.

Un blocage trop large peut notamment affecter la découverte des voisins, la découverte des routeurs et certains messages d'erreur.

Il ne faut donc pas reproduire mécaniquement les règles IPv4 en oubliant les besoins du protocole IPv6.

## 24.4. Router aussi IPv6 ?

Le transfert IPv6 dépend de ses propres paramètres et de la configuration de routage.

Il ne faut pas considérer le paramètre `net.ipv4.ip_forward` comme une activation générale de tout routage IP.

Si le routeur doit transférer IPv6, analysez et configurez séparément les paramètres et politiques correspondants. Les règles de filtrage IPv6 doivent être testées indépendamment du chemin IPv4.


# 25. Erreurs fréquentes et dépannage

## 25.1. Le pare-feu bloque SSH

Symptômes :

- l'adresse de la machine répond ;
- la route semble correcte ;
- la connexion TCP vers le port SSH échoue.

Diagnostic :

```bash
sudo nft list ruleset
sudo iptables -S
ss -tuln
```

Vérifiez également le gestionnaire responsable du filtrage.

Causes possibles :

- port non autorisé ;
- règle source trop restrictive ;
- politique `DROP` sans exception nécessaire ;
- service SSH qui n'écoute pas ;
- route de retour manquante ;
- filtrage supplémentaire sur le réseau ou le serveur.

## 25.2. Le NAT fonctionne partiellement

Symptômes :

- le client envoie du trafic ;
- la règle NAT possède un compteur ;
- aucune réponse n'arrive.

Vérifiez successivement :

1. la route du client ;
2. l'adresse LAN du routeur ;
3. le transfert IP ;
4. les règles `FORWARD` ;
5. la règle NAT ;
6. la route de sortie ;
7. la route de retour ;
8. les pare-feu du réseau amont.

Un compteur NAT qui progresse ne garantit pas que les réponses arrivent.

## 25.3. La règle semble correcte mais ne correspond pas

Vérifiez :

- le hook utilisé ;
- l'interface réelle ;
- la famille IP ;
- le protocole ;
- le port source ou de destination ;
- l'état conntrack ;
- la priorité ;
- l'ordre des chaînes ;
- le contenu réellement chargé.

Ne vous fiez pas uniquement au fichier local. Inspectez également le ruleset actif.

## 25.4. Les règles disparaissent au redémarrage

Causes possibles :

- règles ajoutées manuellement sans persistance ;
- service nftables non activé ;
- mauvais fichier chargé au démarrage ;
- outil de gestion différent ;
- règles recréées par un autre service.

Vérifiez :

```bash
systemctl status nftables
sudo nft list ruleset
```

Sur le système concerné, examinez la configuration de démarrage et les services qui gèrent les règles.

## 25.5. UFW ou firewalld modifie les règles

UFW, firewalld, Docker, certains outils VPN et d'autres applications peuvent configurer Netfilter.

Évitez de superposer des commandes manuelles sans avoir compris la propriété des règles.

Pour identifier les services présents :

```bash
systemctl is-active ufw
systemctl is-active firewalld
systemctl is-active nftables
```

Un résultat `inactive` ou `unknown` dépend de l'état et de l'existence des unités. Ces commandes ne prouvent pas à elles seules qu'aucune autre application n'a installé de règles.


# 26. Travaux pratiques guidés

Tous les TP doivent être réalisés sur une machine virtuelle ou un environnement réseau dont vous contrôlez l'accès.

Ne testez pas une politique restrictive sur un serveur distant important sans une console de secours.

## TP 1 — Créer un pare-feu de serveur avec nftables

### Objectif

Autoriser le trafic local, les connexions établies et les services nécessaires.

### Étape 1 : observer l'état actuel

```bash
sudo nft list ruleset
ip -br address
sudo ss -tuln
```

Identifiez les services réellement actifs et les règles déjà présentes.

### Étape 2 : préparer un fichier de laboratoire

Créez un fichier `server-lab.nft` :

```nft
table inet server_lab {
    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept
        ct state invalid drop
        ct state established,related accept

        ip protocol icmp accept
        meta l4proto ipv6-icmp accept

        tcp dport 22 accept
        tcp dport 8080 accept
    }

    chain forward {
        type filter hook forward priority filter;
        policy drop;
    }

    chain output {
        type filter hook output priority filter;
        policy accept;
    }
}
```

Le port 8080 est une valeur de laboratoire. Il ne doit être autorisé que si le service correspondant est réellement utilisé.

### Étape 3 : contrôler la syntaxe

```bash
sudo nft -c -f server-lab.nft
```

### Étape 4 : examiner les effets attendus

Avant l'application, indiquez :

- quels paquets seront autorisés ;
- quels paquets seront abandonnés ;
- si le serveur pourra initier des connexions sortantes ;
- si le serveur pourra transférer du trafic.

### Étape 5 : tester dans le laboratoire

Après chargement et vérification du ruleset, testez uniquement les services prévus.

Si le résultat n'est pas conforme, examinez les compteurs et les traces au lieu d'ajouter des règles au hasard.


## TP 2 — Créer un routeur avec masquerade

### Objectif

Permettre aux machines d'un réseau de laboratoire d'accéder à un réseau externe via un routeur Linux.

### Topologie

```text
Client : 192.168.50.20/24
    |
    v
LAN : 192.168.50.0/24
    |
    v
Routeur Linux
lan0 : adresse LAN du routeur
wan0 : liaison vers le réseau amont
    |
    v
Réseau amont
```

### Étape 1 : vérifier les interfaces

Sur le routeur :

```bash
ip -br address
ip route
```

### Étape 2 : activer temporairement le routage

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

### Étape 3 : préparer les règles

Exemple de fichier :

```nft
table inet lab_router_filter {
    chain forward {
        type filter hook forward priority filter;
        policy drop;

        ct state invalid drop

        ct state established,related accept

        iifname "lan0" oifname "wan0" \
            ip saddr 192.168.50.0/24 \
            accept
    }
}

table ip lab_router_nat {
    chain postrouting {
        type nat hook postrouting priority srcnat;
        policy accept;

        oifname "wan0" ip saddr 192.168.50.0/24 masquerade
    }
}
```

### Étape 4 : contrôler et appliquer

```bash
sudo nft -c -f router-lab.nft
```

Après validation, inspectez le ruleset existant, puis chargez les règles dans le laboratoire.

### Étape 5 : tester

Sur le client :

```bash
ip route
ping -c 3 ADRESSE_LAN_DU_ROUTEUR
```

Puis testez une destination autorisée et observez les compteurs sur le routeur.

### Étape 6 : analyser les échecs

Si le client ne peut pas joindre une destination extérieure, vérifiez :

- que la passerelle du client est correcte ;
- que le routeur peut joindre le réseau amont ;
- que le transfert IPv4 est activé ;
- que la chaîne `forward` reçoit les paquets ;
- que la règle de masquerade correspond au trafic.


## TP 3 — Mettre en place une publication de port

### Objectif

Publier un service web interne à travers un routeur de laboratoire.

### Données de travail

```text
Interface externe : wan0
Interface interne : lan0
Port externe : 8080
Serveur interne : 192.168.50.10
Port interne : 80
Protocole : TCP
```

Toutes les valeurs sont des exemples.

### Travail demandé

1. préparer une règle DNAT ;
2. intégrer une règle de filtrage dans `FORWARD` ;
3. vérifier la route de retour ;
4. vérifier que le service écoute sur le port 80 ;
5. tester depuis un client extérieur au LAN, sur un réseau contrôlé ;
6. confirmer les règles et les compteurs.

### Résultat attendu

Une connexion vers le port externe 8080 doit être dirigée vers le serveur interne sur le port 80, sous réserve que toutes les conditions de connectivité et de filtrage soient réunies.

### Point de sécurité

Ne publiez pas un service interne sans vérifier son exposition, son authentification, sa mise à jour et son niveau de sensibilité.


## TP 4 — Diagnostiquer une règle qui ne correspond pas

### Objectif

Apprendre à analyser le traitement d'un paquet avant de modifier les règles.

### Méthode

1. afficher le ruleset actif ;
2. identifier la table et la chaîne concernées ;
3. vérifier les critères de correspondance ;
4. examiner les compteurs ;
5. activer le traçage sur un trafic de test limité ;
6. générer une connexion contrôlée ;
7. examiner les traces ;
8. retirer les règles temporaires de diagnostic.

### Travail demandé

Rédigez un rapport contenant :

- le paquet testé ;
- la source et la destination ;
- le protocole et le port ;
- la règle qui devrait correspondre ;
- la règle ou le traitement réellement observé ;
- la correction proposée.

Le rapport ne doit pas contenir de secrets ni de données réseau sensibles qui n'auraient pas besoin d'être diffusées.


# 27. Exercices corrigés

## Exercice 1 — Choisir la bonne chaîne

Un paquet est adressé à un service local qui écoute sur TCP 443.

Quelle chaîne de filtrage est principalement concernée ?

**Correction :** `INPUT`, car le paquet est destiné au système local.

## Exercice 2 — Identifier le trafic transféré

Un client du LAN envoie un paquet à une destination sur Internet à travers un routeur Linux.

Quelle chaîne doit autoriser ce transfert ?

**Correction :** `FORWARD`, après que le noyau a déterminé que le paquet doit être routé vers une autre destination.

## Exercice 3 — Différencier SNAT et DNAT

Le routeur modifie l'adresse source d'un client privé en sortie.

Quel mécanisme est utilisé ?

**Correction :** SNAT ou MASQUERADE selon que l'adresse de sortie est spécifiée explicitement ou déterminée par l'interface de sortie.

## Exercice 4 — Comprendre MASQUERADE

Pourquoi MASQUERADE est-il couramment utilisé sur une interface WAN dont l'adresse est attribuée par DHCP ?

**Correction :** il utilise généralement l'adresse de l'interface de sortie, ce qui est pratique lorsque cette adresse peut changer. Cela ne supprime pas le besoin de routage et de règles de transfert.

## Exercice 5 — Le NAT ne fonctionne pas

Une règle MASQUERADE est présente, mais les clients du LAN ne peuvent pas accéder à Internet.

Donnez quatre contrôles prioritaires.

**Correction :**

- vérifier l'adresse et la route du client ;
- vérifier que le routage IPv4 est activé ;
- vérifier la chaîne `FORWARD` ;
- vérifier la route de sortie du routeur et le réseau amont.

Il faut aussi contrôler la correspondance effective des règles NAT.

## Exercice 6 — Comprendre conntrack

À quoi sert la règle suivante ?

```nft
ct state established,related accept
```

**Correction :** elle autorise les paquets associés à des connexions suivies et considérées comme établies ou liées. Elle ne suffit pas à elle seule à définir les nouvelles connexions autorisées.

## Exercice 7 — Identifier le danger

Que peut provoquer cette commande ?

```bash
sudo nft flush ruleset
```

**Correction :** elle vide l'ensemble des objets nftables dans le contexte réseau concerné, y compris ceux créés par d'autres composants. Elle peut retirer des règles de filtrage ou de NAT indispensables au fonctionnement du système.

## Exercice 8 — Distinguer les backends

La commande `iptables -V` affiche `nf_tables`.

Que peut-on en conclure ?

**Correction :** la commande iptables utilise le backend de compatibilité fondé sur nf_tables dans cet environnement. Cela ne signifie pas qu'il n'existe aucune autre règle ou aucun autre gestionnaire de filtrage sur la machine.

## Exercice 9 — Comprendre le transfert de port

Une règle DNAT dirige le trafic vers `192.168.50.10:80`, mais le client ne reçoit aucune réponse.

Donnez trois autres éléments à vérifier.

**Correction :**

- le transfert IP du routeur ;
- la règle `FORWARD` qui doit autoriser le paquet traduit ;
- le service web et la route de retour du serveur interne.

Il faut également examiner les pare-feu intermédiaires et les compteurs des règles.

## Exercice 10 — IPv4 et IPv6

Un pare-feu bloque bien les connexions entrantes IPv4 non autorisées. Peut-on en déduire que le serveur est correctement protégé en IPv6 ?

**Correction :** non. Il faut vérifier les adresses IPv6, les règles de filtrage IPv6, les services accessibles et le traitement des messages ICMPv6 nécessaires au fonctionnement du protocole.


# 28. Défi final — Construire un routeur Linux avec filtrage et NAT

## 28.1. Contexte

Vous devez mettre en place un routeur Linux pour un laboratoire.

Il possède deux interfaces :

```text
lan0 : côté utilisateurs
wan0 : côté réseau amont
```

Le réseau privé est :

```text
192.168.50.0/24
```

Le serveur interne de test est :

```text
192.168.50.10
```

L'objectif est de permettre aux clients du LAN d'atteindre un réseau externe autorisé et de publier, si cela est nécessaire dans le laboratoire, un service de test contrôlé.

## 28.2. Cahier des charges

Votre solution doit :

- activer le routage IPv4 de façon explicite ;
- autoriser le trafic local requis pour l'administration ;
- autoriser les connexions établies et associées ;
- autoriser uniquement les flux de transfert nécessaires ;
- réaliser du NAT source pour le trafic LAN vers WAN ;
- permettre un transfert de port de test vers le serveur interne, si ce besoin est activé ;
- conserver une configuration persistante ;
- fournir une méthode de diagnostic ;
- contrôler la syntaxe avant chargement ;
- documenter le retour arrière ;
- ne pas mélanger plusieurs gestionnaires de règles sans stratégie explicite.

## 28.3. Schéma de référence

```text
          RÉSEAU EXTERNE
                |
                v
         +--------------+
         |     wan0     |
         |              |
         | Routeur Linux|
         |              |
         |     lan0     |
         +--------------+
                |
                v
       192.168.50.0/24
                |
         +------+------+
         |             |
         v             v
      Client A     Serveur web
      .50.20       .50.10
```

## 28.4. Travail demandé

### Étape 1 : inventaire

Identifiez les interfaces, adresses, routes et règles présentes.

### Étape 2 : conception

Dessinez le chemin des paquets LAN vers WAN et le chemin inverse.

Identifiez l'emplacement du filtrage et du NAT.

### Étape 3 : écriture

Créez un fichier nftables avec une table de filtrage et une table NAT adaptées.

### Étape 4 : test syntaxique

Vérifiez que le fichier est valide avant de le charger.

### Étape 5 : test du trafic

Exécutez les tests depuis un client du LAN et observez les compteurs du routeur.

### Étape 6 : persistance

Intégrez les règles au mécanisme de démarrage adapté à la distribution.

### Étape 7 : restauration

Documentez une procédure de restauration des règles et des paramètres de routage.

## 28.5. Critères de validation

Le défi est validé si :

- le routage fonctionne pour les flux prévus ;
- les nouvelles connexions non autorisées sont bloquées selon la politique choisie ;
- les réponses aux connexions autorisées peuvent revenir ;
- le NAT traduit les flux attendus ;
- le transfert de port éventuel fonctionne uniquement dans les conditions prévues ;
- les règles sont persistantes ;
- les journaux et compteurs permettent de comprendre un échec ;
- le retour arrière est documenté et testé.

La sécurité ne se mesure pas uniquement à la réussite de la connexion de test. Il faut également vérifier que les flux qui ne devraient pas être autorisés le sont effectivement refusés.


# 29. Grille de compétences

Cochez chaque compétence lorsque vous pouvez la démontrer dans un environnement de laboratoire.

## Netfilter et nftables

- [ ] Je sais expliquer le rôle de Netfilter.
- [ ] Je sais distinguer table, chaîne, hook et règle.
- [ ] Je sais expliquer `INPUT`, `OUTPUT` et `FORWARD`.
- [ ] Je sais créer une table et une chaîne nftables.
- [ ] Je sais définir une politique par défaut.
- [ ] Je sais filtrer par interface, protocole, adresse et port.
- [ ] Je sais utiliser les états conntrack.
- [ ] Je sais ajouter et inspecter des compteurs.
- [ ] Je sais vérifier une configuration avec `nft -c -f`.
- [ ] Je sais expliquer l'effet de `flush ruleset`.

## iptables

- [ ] Je sais afficher les règles avec `iptables -L` et `iptables -S`.
- [ ] Je sais distinguer les tables `filter` et `nat`.
- [ ] Je sais vérifier le backend avec `iptables -V`.
- [ ] Je sais autoriser les connexions établies.
- [ ] Je sais définir une politique par défaut sans couper involontairement l'administration.
- [ ] Je sais sauvegarder et restaurer les règles dans un laboratoire.

## NAT et routage

- [ ] Je sais expliquer SNAT et DNAT.
- [ ] Je sais distinguer MASQUERADE et SNAT.
- [ ] Je sais expliquer pourquoi le NAT ne remplace pas le routage.
- [ ] Je sais activer le transfert IPv4.
- [ ] Je sais rendre la configuration sysctl persistante.
- [ ] Je sais concevoir un transfert de port.
- [ ] Je sais vérifier le chemin de retour.

## Sécurité et diagnostic

- [ ] Je sais reconnaître l'interférence potentielle d'UFW, firewalld ou d'autres outils.
- [ ] Je sais utiliser conntrack pour examiner les connexions.
- [ ] Je sais utiliser les compteurs et le traçage.
- [ ] Je sais raisonner sur les différences entre IPv4 et IPv6.
- [ ] Je sais prévoir un retour arrière avant une modification sensible.
- [ ] Je sais documenter les règles et expliquer leur justification.


# 30. Fiche de révision

## Afficher le ruleset nftables

```bash
sudo nft list ruleset
```

## Contrôler un fichier nftables

```bash
sudo nft -c -f firewall.nft
```

## Charger une configuration de laboratoire

```bash
sudo nft -f firewall.nft
```

N'utilisez cette commande qu'après examen des effets du fichier et du ruleset existant.

## Observer les règles iptables

```bash
sudo iptables -L -n -v
sudo iptables -S
sudo iptables -t nat -L -n -v
```

## Identifier le backend iptables

```bash
iptables -V
```

## Vérifier conntrack

```bash
sudo conntrack -L
sudo conntrack -E
```

## Vérifier le transfert IPv4

```bash
sysctl net.ipv4.ip_forward
```

## Activer temporairement le transfert IPv4

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

À ne faire que sur une machine destinée à router le trafic.

## Voir les sockets

```bash
sudo ss -tuln
```

## Les règles à retenir

1. `INPUT` concerne les paquets destinés au système local.
2. `OUTPUT` concerne les paquets produits localement.
3. `FORWARD` concerne les paquets que le système route vers une autre destination.
4. Le NAT et le filtrage sont deux fonctions différentes.
5. MASQUERADE traduit généralement la source en utilisant l'adresse de sortie.
6. DNAT modifie la destination, mais ne suffit pas à autoriser une connexion.
7. Conntrack permet de traiter les paquets en fonction de l'état des connexions suivies.
8. `nftables` est le framework moderne privilégié pour les nouvelles règles lorsque l'environnement le permet.
9. `iptables` peut utiliser un backend nftables ou un backend historique.
10. Ne mélangez pas plusieurs gestionnaires de règles sans maîtriser leurs interactions.
11. Un pare-feu IPv4 ne garantit pas une politique IPv6 correcte.
12. Avant une politique `DROP`, vérifiez les règles nécessaires et prévoyez un accès de secours.
13. `nft flush ruleset` peut supprimer les règles de nombreux composants.
14. Les compteurs et le traçage aident à comprendre les décisions du pare-feu.
15. Une configuration n'est pas correctement déployée tant que sa persistance et son retour arrière ne sont pas compris.


# 31. Glossaire

**Conntrack** : mécanisme du noyau Linux qui conserve des informations sur les connexions réseau suivies.

**DNAT** : traduction qui modifie l'adresse ou le port de destination d'un paquet.

**DROP** : verdict qui abandonne un paquet sans réponse de rejet explicite.

**Hook** : point du traitement réseau auquel une chaîne de base peut être attachée.

**INPUT** : chaîne traditionnelle de filtrage destinée aux paquets livrés au système local.

**iptables** : outil historique de gestion des règles Netfilter.

**iptables-legacy** : backend historique d'iptables, distinct du backend nftables.

**iptables-nft** : interface iptables utilisant le backend nftables.

**MASQUERADE** : forme de traduction source adaptée notamment aux interfaces dont l'adresse peut changer.

**NAT** : traduction d'adresses réseau et parfois de ports.

**Netfilter** : infrastructure du noyau Linux qui traite notamment le filtrage et le NAT.

**nftables** : framework moderne de gestion des règles de filtrage et de NAT.

**`nft`** : commande permettant de manipuler le ruleset nftables.

**OUTPUT** : chaîne traditionnelle utilisée pour filtrer les paquets générés localement.

**POSTROUTING** : étape qui intervient après la décision de routage, avant que le paquet quitte le système.

**PREROUTING** : étape du traitement des paquets entrants située avant la décision de routage.

**REJECT** : verdict qui rejette un paquet et peut envoyer une réponse adaptée.

**SNAT** : traduction d'adresse source.

**DNAT** : traduction d'adresse de destination.

**Politique par défaut** : verdict appliqué aux paquets qui atteignent la fin d'une chaîne de base sans verdict terminal préalable.

**Table nftables** : conteneur d'objets de filtrage associés à une famille.

**Chaîne de base** : chaîne attachée à un hook Netfilter.

**Chaîne ordinaire** : chaîne appelée depuis une autre chaîne au lieu d'être directement attachée à un hook.

**Priorité** : valeur permettant d'ordonner certaines chaînes de base et opérations dans un hook.

**Routage IP** : décision sur le chemin à utiliser pour atteindre une destination IP.

**Transfert IP** : traitement qui permet à un système Linux de router des paquets entre interfaces.


# 32. Documentation et références officielles

Les documents suivants permettent d'approfondir les mécanismes étudiés.

## nftables et Netfilter

- Documentation de nftables sur Ubuntu :  
  https://documentation.ubuntu.com/security/security-features/network/firewall/nftables/

- Documentation générale sur le pare-feu Ubuntu :  
  https://documentation.ubuntu.com/security/security-features/network/firewall/

- Manuel officiel de nftables :  
  https://www.netfilter.org/projects/nftables/manpage.html

- Référence Netfilter sur les hooks :  
  https://wiki.nftables.org/wiki-nftables/index.php/Netfilter_hooks

- Référence nftables sur le NAT :  
  https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)

- Référence rapide nftables :  
  https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes

## iptables et compatibilité

- Documentation Debian sur nftables :  
  https://wiki.debian.org/nftables

- Documentation Debian sur iptables :  
  https://wiki.debian.org/iptables/

- Guide officiel Red Hat sur nftables :  
  https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/configuring_firewalls_and_packet_filters/getting-started-with-nftables

## Routage et paramètres du noyau

- Documentation du noyau Linux sur les paramètres IP :  
  https://docs.kernel.org/networking/ip-sysctl.html

- Pages de manuel Linux :  
  https://man7.org/linux/man-pages/

## Méthode de consultation

Pour chaque configuration, vérifiez :

1. la distribution et sa version ;
2. le backend utilisé ;
3. les outils déjà actifs ;
4. les règles installées par d'autres services ;
5. la syntaxe réellement prise en charge ;
6. les effets sur IPv4 et IPv6 ;
7. la persistance ;
8. les possibilités de retour arrière.

Ne recopiez pas directement une politique de filtrage trouvée en ligne dans un environnement de production. Une règle correcte dans un laboratoire peut être inadaptée à la topologie, aux services, aux utilisateurs ou au plan d'adressage d'une autre machine.


# Conclusion

Le filtrage et le NAT constituent deux compétences centrales de l'administration réseau Linux.

La maîtrise de Netfilter exige de comprendre le cheminement des paquets, les hooks, les chaînes, les politiques, les états conntrack et les mécanismes de traduction d'adresse. Elle exige aussi de distinguer le routage du filtrage : permettre au noyau de transférer un paquet ne signifie pas que le pare-feu l'autorisera, et appliquer du NAT ne garantit pas que le trafic retour fonctionnera.

nftables fournit une structure moderne pour définir les règles. iptables demeure important lorsqu'il faut analyser et maintenir des systèmes existants. Dans les deux cas, la qualité du résultat dépend d'une politique de filtrage claire, de règles adaptées au trafic attendu, d'un contrôle des états et d'une procédure de test et de restauration.

**Critère de validation du niveau intermédiaire :** vous devez être capable de créer et d'expliquer un jeu de règles cohérent, de distinguer le trafic local du trafic transféré, de mettre en œuvre un NAT contrôlé, de diagnostiquer un flux bloqué et de déployer les règles sans compromettre inutilement l'accès au système.