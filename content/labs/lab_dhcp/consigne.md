# Lab DHCP & DNS : obtenir un bail et résoudre un nom

## Objectif

Un serveur `dnsmasq` est déjà démarré dans le namespace `srv`. Il doit fournir
une adresse au client `cli` par DHCP, puis répondre à une requête DNS pour le
nom `intranet.lab`.

```text
+-----------------------------+          +-----------------------------+
| srv                         |          | cli                         |
| veth-srv : 10.20.0.1/24     |<========>| veth-cli : aucune adresse    |
| dnsmasq : DHCP + DNS        |          | à configurer par DHCP       |
+-----------------------------+          +-----------------------------+

Plage DHCP : 10.20.0.100 -> 10.20.0.150
Passerelle : 10.20.0.1
DNS        : 10.20.0.1
Nom        : intranet.lab -> 10.20.0.1
```

## Ce qui est déjà prêt

Le script `setup.sh` crée :

- les namespaces `srv` et `cli` ;
- la paire de liens `veth-srv` / `veth-cli` ;
- l'adresse `10.20.0.1/24` sur le serveur ;
- le serveur `dnsmasq` avec la plage DHCP et l'enregistrement DNS.

Le client `cli` n'a **aucune adresse IP**. C'est le travail du bail DHCP.

## Travail demandé

1. Demande un bail DHCP dans le namespace client :

```bash
ip netns exec cli udhcpc -i veth-cli -q -n
```

L'option `-q` quitte dès que le bail est obtenu. `-n` évite de rester bloqué si
aucun serveur ne répond.

2. Vérifie l'adresse, la route et le serveur DNS reçus :

```bash
ip netns exec cli ip -4 addr show dev veth-cli
ip netns exec cli ip route
cat /etc/netns/cli/resolv.conf 2>/dev/null || ip netns exec cli cat /etc/resolv.conf
```

3. Teste la résolution du nom :

```bash
ip netns exec cli nslookup -type=A intranet.lab 10.20.0.1
ip netns exec cli ping -c 2 10.20.0.1
```

La commande `nslookup -type=A` avec `10.20.0.1` est volontairement explicite :
elle prouve que le serveur DNS répond à une requête IPv4. Le bail doit aussi
avoir installé ce serveur dans la configuration du client.

## À comprendre

DHCP utilise quatre messages principaux :

| Message | Rôle |
|---------|------|
| `DHCPDISCOVER` | Le client cherche un serveur DHCP. |
| `DHCPOFFER` | Le serveur propose une adresse et des options. |
| `DHCPREQUEST` | Le client demande officiellement l'offre. |
| `DHCPACK` | Le serveur confirme le bail. |

Le serveur peut transmettre plusieurs options : adresse IP, masque, passerelle
(`option 3`), serveur DNS (`option 6`) et durée du bail. Sans l'option 3, le
client aurait une adresse mais ne saurait pas comment sortir de son réseau.
Sans l'option 6, il ne saurait pas à quel serveur envoyer ses requêtes DNS.

## Critères de validation

Le script `check.sh` vérifie :

- une adresse IPv4 sur `veth-cli`, dans `10.20.0.0/24` ;
- une adresse comprise entre `10.20.0.100` et `10.20.0.150` ;
- la route par défaut via `10.20.0.1` ;
- la présence de `nameserver 10.20.0.1` dans `/etc/resolv.conf` ;
- la résolution de `intranet.lab` en `10.20.0.1` ;
- la connectivité vers le serveur.

## Pistes en cas d'échec

- Vérifie que `veth-cli` est bien `UP` : `ip netns exec cli ip link show veth-cli`.
- Lance `udhcpc` avec `-f` pour le garder au premier plan et voir les échanges.
- Vérifie que `dnsmasq` tourne : `ip netns exec srv ps | grep dnsmasq`.
- Regarde les baux : `ip netns exec srv cat /var/lib/misc/dnsmasq.leases`.
- Si `nslookup` échoue, teste directement le serveur :
  `ip netns exec cli nslookup -type=A intranet.lab 10.20.0.1`.
- Ne configure pas l'adresse à la main : le contrôle vérifie que le client a
  réellement obtenu un bail dans la plage.

> Un bail DHCP n'est pas seulement une adresse : c'est un ensemble de paramètres
> réseau. En production, on vérifie toujours l'adresse, la passerelle, le DNS et
> la durée du bail avant de conclure que le service fonctionne.
