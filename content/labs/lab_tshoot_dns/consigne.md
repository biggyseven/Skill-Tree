# Lab dépannage DNS : l'enregistrement pointe vers la mauvaise IP

## Objectif

Le client utilise le bon serveur DNS (`10.70.1.53`), et ce serveur répond. Le
problème est dans **l'enregistrement DNS** : `intranet.lab` pointe vers
`10.70.1.99`, une adresse qui n'est pas celle du service. Tu dois trouver la
mauvaise configuration sur le serveur, la corriger, redémarrer `dnsmasq` et
vérifier que le nom résout vers `10.70.1.53`.

```text
+--------------------------+          +--------------------------+
| dns                      |          | client                   |
| veth-dns : 10.70.1.53/24 |<========>| veth-client : .10/24     |
| dnsmasq                  |          | resolv.conf -> .53 (OK)  |
| intranet.lab -> .99 (X)  |          |                          |
+--------------------------+          +--------------------------+
```

## Ce qui est déjà prêt

Le script `setup.sh` :

- crée les namespaces `dns` et `client` ;
- configure la connectivité entre `10.70.1.10` et `10.70.1.53` ;
- démarre `dnsmasq` sur `10.70.1.53` ;
- configure le client pour utiliser `10.70.1.53` ;
- laisse volontairement un mauvais enregistrement dans
  `/tmp/dnsmasq-tshoot.conf`.

La ligne fautive est :

```text
address=/intranet.lab/10.70.1.99
```

## Travail demandé

1. Reproduis le symptôme :

```bash
ip netns exec client nslookup -type=A intranet.lab
```

La réponse contient `10.70.1.99` au lieu de `10.70.1.53`.

2. Vérifie que le serveur répond et lis sa configuration :

```bash
ip netns exec client ping -c 1 10.70.1.53
cat /tmp/dnsmasq-tshoot.conf
```

3. Corrige l'enregistrement DNS :

```bash
sed -i 's#address=/intranet.lab/10.70.1.99#address=/intranet.lab/10.70.1.53#' \
    /tmp/dnsmasq-tshoot.conf
```

4. Redémarre `dnsmasq` pour recharger la configuration :

```bash
kill "$(cat /tmp/dnsmasq-tshoot.pid)"
ip netns exec dns dnsmasq --conf-file=/tmp/dnsmasq-tshoot.conf
```

5. Vérifie la résolution sans préciser de serveur :

```bash
ip netns exec client nslookup -type=A intranet.lab
```

La dernière ligne `Address:` doit afficher `10.70.1.53`.

## Comprendre le problème

Un enregistrement DNS associe un nom à une adresse. Ici :

| Nom | Ancienne cible | Cible attendue |
|-----|----------------|----------------|
| `intranet.lab` | `10.70.1.99` (fausse) | `10.70.1.53` |

Le client et le réseau fonctionnent : seule la donnée publiée par le serveur est
fausse. C'est un cas classique où `ping` sur l'adresse IP fonctionne mais où
l'application échoue parce qu'elle utilise un nom.

`dnsmasq` garde sa configuration en mémoire au démarrage. Modifier le fichier ne
suffit pas : il faut envoyer un signal au processus ou le redémarrer. Le fichier
`/tmp/dnsmasq-tshoot.pid` contient le PID à arrêter.

## Méthode de diagnostic

| Test | Ce qu'il prouve |
|------|------------------|
| `ping 10.70.1.53` | La connectivité IP est bonne. |
| `nslookup ... 10.70.1.53` | Le serveur DNS répond. |
| `cat /tmp/dnsmasq-tshoot.conf` | La donnée DNS est-elle correcte ? |
| `nslookup ...` sans serveur | Le client utilise-t-il le bon résolveur ? |

Quand le serveur répond mais renvoie une mauvaise adresse, le problème est dans
la zone ou l'enregistrement, pas dans la connectivité.

## Critères de validation

Le script `check.sh` vérifie :

- le client utilise `10.70.1.53` comme résolveur ;
- le client joint le serveur ;
- `intranet.lab` se résout vers `10.70.1.53` et non vers `10.70.1.99`.

## Pistes en cas d'échec

- Vérifie que la ligne `address=/intranet.lab/10.70.1.53` est bien présente dans
  `/tmp/dnsmasq-tshoot.conf`.
- Vérifie que l'ancien processus est arrêté :
  `ps | grep dnsmasq` ou `cat /tmp/dnsmasq-tshoot.pid`.
- Si le redémarrage échoue, regarde le port 53 :
  `ip netns exec dns ss -lunp | grep :53`.
- Teste directement le serveur :
  `ip netns exec client nslookup -type=A intranet.lab 10.70.1.53`.
- Ne modifie pas l'adresse IP du client : le contrôle attend le réseau fourni.

> En production, on vérifie toujours la donnée DNS et le processus qui la sert.
> Un enregistrement corrigé mais un serveur non rechargé continue de répondre
> avec l'ancienne valeur, ce qui donne l'impression que la correction n'a pas
> fonctionné.
