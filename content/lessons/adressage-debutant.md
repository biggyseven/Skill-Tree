# L'adressage IP pour les débutants

Pour envoyer une information au bon appareil, le réseau a besoin d'adresses.
L'adresse IP est l'adresse logique d'un appareil sur un réseau.

> Analogie : une adresse IP ressemble à l'adresse d'une maison. Le facteur a
> besoin de cette adresse pour savoir où livrer le courrier. Le réseau a besoin
> de l'adresse IP pour savoir à quel appareil remettre les paquets.

## Une adresse IPv4

Une adresse IPv4 est composée de quatre nombres séparés par des points :

```text
192.168.1.20
```

Chaque nombre peut aller de 0 à 255. Il existe aussi des adresses IPv6, plus
longues, mais nous allons commencer avec IPv4, la plus simple à reconnaître.

Une adresse IP ne sert pas seulement à identifier un appareil : elle indique
aussi dans quel réseau il se trouve. C'est pour cela qu'un appareil a besoin
d'un **masque de réseau**. Pour débuter, retiens simplement que le masque aide
la machine à savoir si une destination est dans son quartier ou ailleurs.

## Adresse privée et adresse publique

Toutes les adresses IP ne sont pas visibles directement sur Internet.

| Type | Où la trouve-t-on ? | Exemple |
|---|---|---|
| Adresse privée | Dans une maison, une entreprise, un réseau local | `192.168.1.20` |
| Adresse publique | Sur Internet, attribuée par le fournisseur d'accès | `203.0.113.10` |

Les trois plages privées les plus connues sont :

- `10.0.0.0` à `10.255.255.255` ;
- `172.16.0.0` à `172.31.255.255` ;
- `192.168.0.0` à `192.168.255.255`.

Ces adresses ne sont pas routées telles quelles sur Internet. La box utilise le
**NAT** pour traduire les adresses privées de la maison en une adresse publique.
Tu n'as pas besoin de faire ce calcul pour commencer : retiens simplement que
le privé reste à la maison et que la box fait le passage.

> Analogie : les adresses privées sont les numéros de chambre d'un hôtel. Le
> facteur n'a pas besoin de connaître chaque chambre ; il livre à l'accueil, et
> l'accueil transmet au bon client.

## DHCP : l'attribution automatique

Quand tu connectes un téléphone à un réseau Wi-Fi, il reçoit souvent une adresse
automatiquement. Le service qui s'en occupe s'appelle **DHCP**.

Le DHCP fournit généralement :

- une adresse IP ;
- un masque de réseau ;
- l'adresse de la passerelle ;
- l'adresse d'un ou plusieurs serveurs DNS.

> Analogie : à l'hôtel, la réception te donne une chambre libre sans que tu
> choisisses le numéro. DHCP fait pareil avec les adresses IP.

Sans DHCP, il faudrait configurer chaque appareil à la main. C'est possible,
mais plus long et plus facile à erreur.

## DNS : le répertoire des noms

Les humains retiennent mieux les noms que les suites de chiffres. Le **DNS**
traduit un nom comme `www.exemple.fr` en adresse IP.

> Analogie : le DNS est l'annuaire téléphonique d'Internet. Tu connais le nom de
> la personne, l'annuaire te donne son numéro.

Quand tu tapes une adresse dans ton navigateur :

1. Ton appareil demande au DNS l'adresse IP du site.
2. Le DNS répond avec une adresse.
3. Ton appareil peut ensuite envoyer sa demande au bon serveur.

Si le DNS ne répond pas, un site peut être inaccessible même si la connexion
Internet fonctionne. C'est pour cela qu'on teste parfois le DNS avant de dire
que « tout Internet est en panne ».

## La passerelle par défaut

La **passerelle par défaut** est l'adresse de l'appareil qui permet de sortir
du réseau local. Dans une maison, c'est très souvent la box.

> Analogie : la passerelle est la porte de sortie du quartier. Pour aller chez
> le voisin, tu peux rester dans le quartier. Pour aller en ville, tu passes par
> la porte de sortie.

Exemple de configuration simple :

```text
PC              192.168.1.20
Masque          255.255.255.0
Passerelle      192.168.1.1
DNS             192.168.1.1
```

Ici, le PC, la box et les autres appareils sont dans le même réseau local. La
box est à la fois la passerelle et souvent le serveur DNS relais de la maison.

## Que se passe-t-il quand j'ouvre un site ?

1. Le PC utilise le DNS pour trouver l'adresse IP du site.
2. Le PC regarde si le site est dans son réseau local.
3. S'il est ailleurs, il envoie les paquets à la passerelle.
4. La box traduit l'adresse privée avec le NAT et envoie vers Internet.
5. La réponse revient par la box, puis jusqu'au PC.

C'est une succession de petites étapes. Si une étape manque, le site peut ne
pas s'afficher.

## Commandes simples pour observer

Sous Windows :

```powershell
ipconfig
```

Sous Linux :

```bash
ip a
ip route
```

Ces commandes affichent l'adresse IP, la passerelle et parfois le DNS. Elles
sont utiles pour vérifier ce que l'appareil a réellement reçu.

## À retenir

- Une adresse IP identifie un appareil sur un réseau.
- Une adresse privée reste dans un réseau local ; une adresse publique est
  visible sur Internet.
- DHCP attribue automatiquement les paramètres réseau.
- DNS traduit les noms de sites en adresses IP.
- La passerelle est la porte de sortie vers les autres réseaux.
- La box fait souvent routeur, passerelle, DHCP, DNS relais et NAT.

Tu n'as pas besoin de maîtriser les sous-réseaux pour commencer. Le plus
important est de comprendre le rôle de chaque élément et l'ordre des étapes.
