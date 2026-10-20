# Lab : dépannage VLAN

## Topologie

```text
        ns1                                             ns2
  192.168.50.10/24                                 192.168.50.20/24
        |                                               |
     veth1-a                                          veth2-a
        |                                               |
     veth1-b                                         veth2-b
        |                                               |
        +-------------- br-trouble ---------------------+
                    bridge VLAN filtering
```

Deux namespaces sont connectés au même bridge Linux. Les adresses IP sont
correctes et les liens sont up. Pourtant :

```text
ip netns exec ns1 ping -c 2 192.168.50.20
```

**Le ping échoue. Trouve le problème et corrige-le.**

## Ce qui est déjà en place

| Élément | Valeur |
| --- | --- |
| ns1 | `192.168.50.10/24` sur `veth1-a` |
| ns2 | `192.168.50.20/24` sur `veth2-a` |
| Bridge | `br-trouble`, `vlan_filtering 1` |
| Port ns1 | `veth1-b` attaché au bridge |
| Port ns2 | `veth2-b` attaché au bridge |

Les adresses sont dans le même sous-réseau. Il n'y a pas de routeur : le trafic
doit être commuté au niveau 2. Le forwarding IP et les routes ne sont donc pas
la cause du problème.

## Méthode de diagnostic

1. Vérifier que les interfaces sont up et que les adresses sont présentes :

   ```sh
   ip netns exec ns1 ip -br addr
   ip netns exec ns2 ip -br addr
   bridge link show
   ```

2. Vérifier l'appartenance VLAN des ports du bridge :

   ```sh
   bridge vlan show
   ```

3. Comparer les VLAN des deux ports. Un port d'accès doit avoir le même PVID
   que l'autre port s'ils doivent partager le même domaine L2.

4. Tester à nouveau :

   ```sh
   ip netns exec ns1 ping -c 2 192.168.50.20
   ip netns exec ns2 ping -c 2 192.168.50.10
   ```

## Correction attendue

Le port `veth2-b` est dans le VLAN 60, alors que `veth1-b` est dans le VLAN 50.
Les trames non taguées de `ns2` sont donc classées dans le VLAN 60 et ne
peuvent pas atteindre le VLAN 50. Pour corriger, place d'abord le port dans le
VLAN 50, puis retire l'ancien VLAN :

```sh
bridge vlan add vid 50 dev veth2-b pvid untagged
bridge vlan del vid 60 dev veth2-b
bridge vlan show
```

Vérifie ensuite :

```sh
ip netns exec ns1 ping -c 2 192.168.50.20
ip netns exec ns2 ping -c 2 192.168.50.10
```

Le `check.sh` valide le ping dans les deux sens.

## Pourquoi cela échoue

Le bridge avec `vlan_filtering 1` classe chaque trame entrante selon le PVID du
port. Une trame non taguée reçue sur `veth2-b` est placée dans le VLAN 60 ;
une trame non taguée reçue sur `veth1-b` est placée dans le VLAN 50. Un bridge
ne commute pas entre deux VLAN différents : l'ARP de `ns1` ne trouve jamais
`ns2`, et le ping échoue.

Le fait que les deux adresses soient dans `192.168.50.0/24` ne suffit pas :
le sous-réseau IP est une notion de niveau 3, tandis que le PVID est une
notion de niveau 2. Ici, le problème est bien le classement VLAN.

## Pièges à éviter

- Ne change pas les adresses IP : elles sont correctes.
- Ne cherche pas une route par défaut : les deux hôtes sont dans le même
  sous-réseau et le problème est L2.
- Vérifie que `bridge vlan show` affiche bien le VLAN 50 sur `veth2-b` après
  la correction.
- Si tu supprimes le VLAN 60 avant d'ajouter le VLAN 50, le PVID peut revenir
  à sa valeur par défaut ; ajoute d'abord le VLAN 50 avec `pvid untagged`.
- Une fois corrigé, les deux pings doivent réussir, pas seulement l'aller.
