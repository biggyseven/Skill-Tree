# Laboratoire de dépannage VLAN — `lab_troubleshoot_vlan.md`

> **Parcours :** débutant → intermédiaire → avancé  
> **Environnement principal :** Cisco Packet Tracer, GNS3 ou commutateurs Cisco de laboratoire  
> **Thème :** diagnostic méthodique des problèmes de VLAN, ports access, trunks 802.1Q, routage inter-VLAN, SVI, DHCP et filtrage  
> **Méthode :** établir une référence fonctionnelle, provoquer une seule panne, collecter les preuves, formuler une hypothèse, corriger puis refaire les tests positifs et négatifs.


## 1. Objectifs du laboratoire

Un dépannage VLAN efficace ne consiste pas à changer plusieurs commandes jusqu'à ce que le ping fonctionne. Il faut localiser la couche où le problème apparaît et prouver la cause avant de corriger.

À la fin de ce laboratoire, tu dois pouvoir :

1. distinguer un problème de port, de VLAN, de trunk, d'adressage et de routage ;
2. utiliser les sorties de diagnostic Cisco pour confirmer l'appartenance des ports aux VLAN ;
3. vérifier les VLAN autorisés et le VLAN natif sur un trunk ;
4. diagnostiquer un défaut de routage inter-VLAN sur un routeur-on-a-stick ou un commutateur de couche 3 ;
5. différencier une panne DHCP d'une panne de connectivité ;
6. repérer l'effet d'une ACL, d'un état STP ou d'un port désactivé ;
7. simuler plusieurs incidents sans mélanger les causes ;
8. produire un compte rendu exploitable par une autre personne de l'équipe.

**Environnement recommandé :** Packet Tracer suffit pour une grande partie des exercices. Des commandes ou fonctions diffèrent selon le modèle et la version IOS. Les noms de ports de ce document sont des exemples : adapte `Fa0/2`, `Gi0/1`, etc. à la topologie réellement créée.

### Règles de sécurité du TP

- Réalise tous les changements dans une maquette isolée, jamais directement sur le réseau de production.
- Sauvegarde la configuration initiale ou conserve une copie de la configuration de référence.
- N'injecte qu'une panne à la fois.
- Avant de corriger, conserve les sorties des commandes qui montrent le problème.
- N'utilise pas un `permit ip any any`, la suppression d'une ACL ou la désactivation de STP comme solution permanente à un problème de connectivité.
- À la fin, restaure la topologie de référence et confirme que tous les tests passent.


## 2. La méthode de dépannage à appliquer à chaque incident

Utilise la même séquence pour chaque scénario. Elle évite de perdre du temps à modifier des éléments qui n'ont aucun rapport avec la panne.

### Étape 1 — Décrire précisément le symptôme

Remplace « le réseau ne marche pas » par une description vérifiable, par exemple :

- PC-A ne joint pas PC-B, alors qu'ils sont censés appartenir au VLAN 10 ;
- PC-A joint sa passerelle, mais pas le serveur du VLAN 20 ;
- les postes d'un même VLAN sur SW1 communiquent, mais ceux raccordés à SW2 échouent ;
- un poste n'obtient pas d'adresse DHCP alors qu'une configuration IP statique fonctionne ;
- un seul port est en panne, tandis que les autres ports du même VLAN fonctionnent.

Note l'heure, les équipements concernés, le VLAN, le port source, le port destination et le dernier changement connu.

### Étape 2 — Comparer avec un poste qui fonctionne

Choisis un poste sain du même VLAN, si possible sur un autre port ou un autre commutateur. Compare son adresse IP, son masque, sa passerelle, son VLAN access, l'état du port et les entrées MAC. Une différence claire entre un poste sain et un poste en panne est souvent plus utile qu'une inspection générale de tout le réseau.

### Étape 3 — Vérifier dans l'ordre

1. **Physique et état du port :** interface active, câble/liaison présents, pas d'état err-disabled.
2. **VLAN local :** VLAN créé, port access affecté au bon VLAN.
3. **Chemin de couche 2 :** trunk opérationnel, VLAN autorisé de bout en bout, STP en état de transfert.
4. **Adressage :** IP, masque, passerelle et absence de conflit.
5. **Routage :** si les communications traversent des sous-réseaux, vérifier la passerelle et les routes de retour.
6. **Services et sécurité :** DHCP, DNS, ACL, pare-feu, port-security et autres contrôles.
7. **Application :** tester le port et le service attendu après avoir validé les couches inférieures.

### Étape 4 — Formuler une hypothèse testable

Exemple : « Le VLAN 10 est absent de la liste des VLAN autorisés sur le trunk SW1–SW2 ; les hôtes du VLAN 10 ne peuvent donc plus échanger des trames au travers de ce lien. »

L'hypothèse doit prévoir une observation qui la confirme ou l'infirme. Une supposition comme « le switch doit être bloqué » ne donne pas de test précis.

### Étape 5 — Corriger une seule cause, puis vérifier

Après correction, exécute au minimum :

- le test qui échouait ;
- un test positif déjà fonctionnel, pour vérifier l'absence de régression ;
- un test négatif qui doit rester bloqué, si la politique impose une isolation.


## 3. Topologie de référence

La maquette comprend deux commutateurs de couche 2, quatre PC et un routeur qui réalise le routage inter-VLAN.

```text
                    R1
               G0/0 | trunk 802.1Q
                    |
                 Gi0/1
                  SW1
        PC-A       |       PC-D
      VLAN 10      |      VLAN 20
      Fa0/2        |      Fa0/3
                    \
                 Gi0/2 ===== Gi0/1
                     trunk
                      SW2
                 Fa0/2 | Fa0/3
                  PC-B | PC-C
                VLAN 10| VLAN 20
```

### Plan d'adressage

| Équipement | Port/VLAN | Adresse IPv4 | Passerelle |
|---|---|---|---|
| PC-A | SW1 Fa0/2, VLAN 10 | `192.168.10.10/24` | `192.168.10.1` |
| PC-B | SW2 Fa0/2, VLAN 10 | `192.168.10.11/24` | `192.168.10.1` |
| PC-C | SW2 Fa0/3, VLAN 20 | `192.168.20.10/24` | `192.168.20.1` |
| PC-D | SW1 Fa0/3, VLAN 20 | `192.168.20.11/24` | `192.168.20.1` |
| R1 G0/0.10 | VLAN 10 tagué | `192.168.10.1/24` | — |
| R1 G0/0.20 | VLAN 20 tagué | `192.168.20.1/24` | — |

Le VLAN natif des trunks sera le VLAN 999, dédié et inutilisé par des hôtes dans cette maquette. Le routeur possède une sous-interface native sans adresse IP. Si ton simulateur ou ton modèle ne prend pas en charge une commande donnée, utilise la méthode de configuration prise en charge et vérifie le résultat opérationnel.

### Tests qui doivent réussir lorsque tout fonctionne

| ID | Test | Résultat attendu |
|---|---|---|
| T1 | PC-A → PC-B | Réussite : même VLAN 10, à travers le trunk entre les switches |
| T2 | PC-C → PC-D | Réussite : même VLAN 20, à travers le trunk entre les switches |
| T3 | PC-A → `192.168.10.1` | Réussite : passerelle du VLAN 10 |
| T4 | PC-C → `192.168.20.1` | Réussite : passerelle du VLAN 20 |
| T5 | PC-A → PC-C | Réussite : routage entre VLAN 10 et VLAN 20 |
| T6 | PC-B → PC-D | Réussite : routage entre VLAN 10 et VLAN 20 |

Ces tests supposent qu'aucune ACL ni politique de sécurité ne bloque volontairement ces flux.


## 4. Créer la configuration de référence

### 4.1 Configuration de SW1

Adapte les interfaces à ta maquette. Sur certains switches, le port vers R1 est `Gi0/1`, le lien vers SW2 `Gi0/2` et les ports utilisateurs `Fa0/2` et `Fa0/3`.

```text
enable
configure terminal
hostname SW1
!
vlan 10
 name USERS
vlan 20
 name SERVERS
vlan 999
 name NATIVE_UNUSED
!
interface FastEthernet0/2
 description PC-A_VLAN10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
!
interface FastEthernet0/3
 description PC-D_VLAN20
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
!
interface GigabitEthernet0/1
 description TRUNK_TO_R1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,999
 no shutdown
!
interface GigabitEthernet0/2
 description TRUNK_TO_SW2
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,999
 no shutdown
!
end
```

Sur certains modèles plus anciens, il peut être nécessaire de préciser l'encapsulation 802.1Q avant `switchport mode trunk`. Sur beaucoup de Catalyst récents, la commande `switchport trunk encapsulation dot1q` n'est pas disponible parce que 802.1Q est la seule encapsulation prise en charge. Ne l'ajoute que si la plateforme l'exige.

`spanning-tree portfast` est placé uniquement sur les ports reliés à des postes d'extrémité, pas sur les trunks entre équipements réseau.

### 4.2 Configuration de SW2

```text
enable
configure terminal
hostname SW2
!
vlan 10
 name USERS
vlan 20
 name SERVERS
vlan 999
 name NATIVE_UNUSED
!
interface FastEthernet0/2
 description PC-B_VLAN10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
!
interface FastEthernet0/3
 description PC-C_VLAN20
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
!
interface GigabitEthernet0/1
 description TRUNK_TO_SW1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,999
 no shutdown
!
end
```

### 4.3 Configuration de R1 en router-on-a-stick

```text
enable
configure terminal
hostname R1
!
interface GigabitEthernet0/0
 description TRUNK_TO_SW1
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
!
interface GigabitEthernet0/0.999
 encapsulation dot1Q 999 native
 no ip address
end
```

La sous-interface `.999` est déclarée native pour correspondre au VLAN natif du trunk SW1–R1. Aucune adresse n'est attribuée à ce VLAN, et aucun poste n'y est connecté. L'interface physique doit être active. Une sous-interface peut apparaître dans un état différent de celui attendu si l'interface physique est inactive ou si la configuration de couche 2 ne correspond pas.

### 4.4 Configurer les PC

Dans Packet Tracer, configure les paramètres IP selon le tableau d'adressage. Pour chaque PC, contrôle attentivement :

- adresse IP ;
- masque ;
- passerelle par défaut ;
- absence de doublon d'adresse avec un autre PC.

Pour l'instant, configure les adresses statiquement. Nous ajouterons le dépannage DHCP plus loin, afin de ne pas mélanger les deux sujets.

### 4.5 Vérifier l'état initial

Sur SW1 et SW2 :

```text
show vlan brief
show interfaces trunk
show interfaces status
show spanning-tree vlan 10
show spanning-tree vlan 20
show mac address-table dynamic
```

Sur les versions IOS qui le permettent, inspecte aussi un port précis :

```text
show interfaces FastEthernet0/2 switchport
show running-config interface FastEthernet0/2
```

Sur R1 :

```text
show ip interface brief
show running-config interface GigabitEthernet0/0.10
show running-config interface GigabitEthernet0/0.20
show ip route
```

Sur chaque PC, réalise les tests T1 à T6. Ne commence les scénarios de panne qu'après avoir obtenu une référence fonctionnelle complète.


## 5. La séquence de tests depuis un poste

Pour tout incident, exécute les contrôles dans cet ordre et note le résultat.

### Test A — Adresse locale

Vérifie que le poste possède l'adresse, le masque et la passerelle attendus. Sur Windows :

```text
ipconfig /all
arp -a
```

Sur Linux :

```bash
ip address show
ip route show
ip neigh show
```

### Test B — Passerelle locale

Depuis PC-A, teste `192.168.10.1`. Depuis PC-C, teste `192.168.20.1`. Si ce test échoue, ne commence pas par modifier les routes distantes : vérifie l'interface access, le VLAN, le trunk vers R1, la sous-interface et l'adresse de passerelle.

### Test C — Autre hôte du même VLAN

PC-A vers PC-B, ou PC-C vers PC-D. Ce test vérifie notamment que le VLAN traverse correctement le lien SW1–SW2. Il ne dépend pas du routage inter-VLAN lorsque les deux postes ont des adresses et des masques cohérents.

### Test D — Hôte d'un autre VLAN

PC-A vers PC-C. Si le même VLAN fonctionne mais que ce test échoue, le problème est plus probablement associé au routage inter-VLAN, à la passerelle, à la sous-interface, à une route ou à un filtrage L3.

### Test E — Vérifier les tables

- La FDB du switch apprend-elle les MAC des postes attendus sur les bons ports ?
- Le VLAN est-il autorisé sur chaque trunk du chemin ?
- STP transfère-t-il le trafic sur les ports concernés ?
- Le routeur possède-t-il les deux réseaux directement connectés ?


## 6. TP A — Un poste est placé dans le mauvais VLAN

**Symptôme :** PC-A ne peut plus joindre PC-B, alors que les deux devraient être dans le VLAN 10. PC-D, sur le même SW1, continue de fonctionner.

### Injection de panne

Sur SW2, place volontairement le port de PC-B dans le VLAN 20 :

```text
configure terminal
interface FastEthernet0/2
 switchport access vlan 20
end
```

### Observations à collecter

1. Teste le ping PC-A → PC-B.
2. Teste le ping PC-C → PC-B.
3. Sur SW2, exécute `show vlan brief` et `show interfaces FastEthernet0/2 switchport`.
4. Observe les MAC apprises dans les VLAN 10 et 20 avec `show mac address-table dynamic`.

### Diagnostic attendu

Le port de PC-B appartient au VLAN 20 alors que PC-B possède toujours une adresse du sous-réseau `192.168.10.0/24`. L'hôte se trouve dans le mauvais domaine de couche 2. Le fait que son adresse IP semble correcte ne suffit pas : l'appartenance au VLAN est déterminée par la configuration du port et le chemin de couche 2.

### Correction

```text
configure terminal
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
end
```

Refais T1, T2, T3 et T5. Confirme que PC-C et PC-D continuent à fonctionner.

**Question :** pourquoi le ping de PC-B vers `192.168.10.1` ne prouvait-il pas nécessairement que le port était dans le VLAN 10 ? Explique le rôle de l'adresse IP, du masque et du domaine de broadcast dans ce scénario.


## 7. TP B — Un VLAN est absent de la liste autorisée du trunk

**Symptôme :** PC-A et PC-B ne communiquent plus à travers SW1–SW2, mais les hôtes locaux raccordés au même switch continuent à communiquer. Le VLAN 20 fonctionne toujours de bout en bout.

### Injection de panne

Sur SW1, retire le VLAN 10 de la liste autorisée sur le trunk vers SW2 :

```text
configure terminal
interface GigabitEthernet0/2
 switchport trunk allowed vlan 20,999
end
```

Attention : selon la plateforme, `switchport trunk allowed vlan ...` remplace la liste existante. Vérifie toujours la liste obtenue.

### Observations

Sur les deux switches :

```text
show interfaces trunk
show vlan brief
show mac address-table dynamic vlan 10
show spanning-tree vlan 10
```

Puis teste :

- PC-A → PC-B : doit échouer ;
- PC-C → PC-D : doit rester fonctionnel ;
- PC-A → PC-D : le routage inter-VLAN peut toujours fonctionner via R1 si ses autres liens et interfaces restent corrects, car ces deux postes sont raccordés au même switch et le routeur ne dépend pas du trunk SW1–SW2 pour cet échange.

Cette différence de résultat est une preuve importante : elle localise davantage l'incident sur le chemin inter-switch que sur la passerelle de PC-A.

### Correction

```text
configure terminal
interface GigabitEthernet0/2
 switchport trunk allowed vlan 10,20,999
end
```

Refais T1 et T2 puis vérifie que les VLAN autorisés sont identiques aux deux extrémités du trunk.

**Question :** pourquoi un trunk peut-il être opérationnel alors qu'un VLAN particulier ne traverse pas ce trunk ?


## 8. TP C — Trunk mal configuré ou transformé en port access

**Symptôme :** les hôtes du même VLAN communiquent sur un même switch, mais ceux situés derrière l'autre switch ne peuvent plus échanger. La configuration des ports access semble correcte.

### Injection de panne

Sur SW2, transforme le lien vers SW1 en port access dans le VLAN 10 :

```text
configure terminal
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
end
```

Cette modification est volontairement incohérente avec le trunk configuré sur SW1.

### Diagnostic

Sur SW1 et SW2 :

```text
show interfaces trunk
show interfaces GigabitEthernet0/2 switchport
show interfaces GigabitEthernet0/1 switchport
show logging
```

Compare le mode administratif et le mode opérationnel. Vérifie si des messages signalent un désaccord de configuration. Les trames VLAN 20 ne peuvent plus être transportées comme prévu sur un lien configuré en access.

### Correction

Sur SW2 :

```text
configure terminal
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,999
end
```

Vérifie ensuite les deux extrémités. Un trunk doit être configuré de manière compatible sur chaque équipement. La commande exacte nécessaire dépend du modèle et de ses fonctions de négociation.


## 9. TP D — Incohérence du VLAN natif

**Symptôme :** le trunk semble actif, mais les captures, les journaux ou certains tests indiquent un problème de traitement des trames non taguées. Une incohérence de VLAN natif peut également produire un avertissement de mismatch.

### Comprendre avant de changer

En 802.1Q, un VLAN natif est utilisé pour le traitement des trames non taguées sur un trunk, selon la configuration de l'équipement. Pour que les deux extrémités interprètent les trames non taguées de façon cohérente, le VLAN natif doit correspondre. Le désaccord ne signifie pas nécessairement que tous les VLAN tagués cessent immédiatement de fonctionner ; c'est pourquoi il faut tester le trafic touché et vérifier les logs.

### Injection de panne

Sur SW1 uniquement :

```text
configure terminal
interface GigabitEthernet0/2
 switchport trunk native vlan 10
end
```

SW2 conserve le VLAN natif 999. Cette situation est volontairement incorrecte pour le laboratoire. Puisque le VLAN 10 devient natif d'un côté mais reste tagué de l'autre, le trafic VLAN 10 peut être interprété de façon incohérente.

### Observations

```text
show interfaces trunk
show interfaces GigabitEthernet0/2 switchport
show logging
```

Teste PC-A → PC-B et PC-C → PC-D séparément. Ne te contente pas de relever si « le trunk est up » ; examine la cohérence du VLAN natif et la liste des VLAN autorisés.

### Correction

Restaure le VLAN natif 999 des deux côtés :

```text
configure terminal
interface GigabitEthernet0/2
 switchport trunk native vlan 999
end
```

Vérifie aussi SW2 :

```text
configure terminal
interface GigabitEthernet0/1
 switchport trunk native vlan 999
end
```

**Bonne pratique :** utilise un VLAN natif dédié et non utilisé pour les terminaux lorsque la politique et la plateforme le permettent. Cela ne remplace pas la sécurisation des trunks ni la limitation des VLAN autorisés.


## 10. TP E — VLAN absent sur le switch distant

**Symptôme :** le trunk est bien configuré et le VLAN est présent sur SW1, mais le VLAN 10 n'apparaît pas correctement sur SW2 ou ses ports ne transfèrent pas le trafic attendu.

### Injection de panne

Sur SW2, supprime temporairement le VLAN 10 :

```text
configure terminal
no vlan 10
end
```

La disponibilité exacte de cette commande et son effet dépendent du contexte de configuration ; ne fais l'essai que dans le laboratoire.

### Diagnostic

```text
show vlan brief
show interfaces trunk
show mac address-table dynamic vlan 10
show logging
```

Vérifie la présence du VLAN sur chaque switch et le fait que le trunk transporte ce VLAN. Sur un réseau utilisant VTP ou un autre mécanisme de distribution de configuration VLAN, examine aussi son état et sa politique. Ne modifie pas VTP à l'aveugle pour résoudre un problème de VLAN.

### Correction

```text
configure terminal
vlan 10
 name USERS
end
```

Puis réexécute T1. Assure-toi que les ports concernés sont encore associés au bon VLAN et que celui-ci est autorisé sur les trunks.


## 11. TP F — Le trunk est correct, mais un port est désactivé

**Symptôme :** seul PC-D est inaccessible. PC-C, placé dans le même VLAN 20 mais sur SW2, reste joignable. La configuration du VLAN 20 et des trunks est cohérente.

### Injection de panne

Sur SW1 :

```text
configure terminal
interface FastEthernet0/3
 shutdown
end
```

### Diagnostic

```text
show interfaces status
show ip interface brief
show running-config interface FastEthernet0/3
show logging
```

Le nom `show ip interface brief` peut montrer un état physique mais ne détaille pas à lui seul le VLAN du port. Utilise `show interfaces status` et `show interfaces ... switchport` pour compléter le diagnostic.

### Correction

```text
configure terminal
interface FastEthernet0/3
 no shutdown
end
```

Confirme que le port est opérationnel, que son VLAN est 20 et que PC-D a bien sa configuration IP.

### Variante : port err-disabled

Sur des équipements qui prennent en charge la fonction, une violation de port-security ou une autre protection peut placer un port dans l'état `err-disabled`. Observe la cause avec `show interfaces status`, les journaux et les commandes de vérification du mécanisme concerné. Corrige d'abord la cause — par exemple une adresse MAC non autorisée — puis restaure le port selon la procédure officielle de la plateforme. Ne configure pas un rétablissement automatique comme substitut à la compréhension de l'incident.


## 12. TP G — Panne de routage inter-VLAN sur router-on-a-stick

**Symptôme :** PC-A et PC-B communiquent entre eux, PC-C et PC-D communiquent entre eux, mais PC-A ne joint plus PC-C. Les pings vers la passerelle VLAN 10 ou VLAN 20 peuvent échouer suivant l'erreur injectée.

Le fonctionnement intra-VLAN et inter-VLAN doit être distingué : deux hôtes du même sous-réseau n'ont pas besoin d'un routeur pour communiquer, alors que deux sous-réseaux IP distincts requièrent un mécanisme L3 et un chemin retour.

### Panne 1 — Mauvaise encapsulation 802.1Q

Sur R1, modifie la sous-interface VLAN 10 pour utiliser temporairement le mauvais identifiant :

```text
configure terminal
interface GigabitEthernet0/0.10
 encapsulation dot1Q 11
end
```

Selon l'IOS, une modification de l'encapsulation peut être acceptée, ou rencontrer une contrainte avec les sous-interfaces existantes. Si la plateforme refuse la commande, observe le message d'erreur et utilise une variante autorisée dans la maquette pour reproduire l'erreur de tag.

**Tests :** PC-A → PC-B doit continuer à réussir ; PC-A → passerelle `192.168.10.1` ou PC-A → PC-C peut échouer. Cela aide à distinguer la connectivité L2 du routage L3.

**Correction :**

```text
configure terminal
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
end
```

### Panne 2 — Adresse de passerelle incorrecte

Change temporairement la passerelle de PC-A en `192.168.10.254`. PC-A peut encore joindre PC-B car ils sont dans le même sous-réseau, mais ne peut généralement plus atteindre les destinations distantes à travers la passerelle erronée.

Restaure `192.168.10.1` et répète T1, T3 et T5.

### Panne 3 — Sous-interface ou interface physique inactive

Sur R1, inspecte :

```text
show ip interface brief
show running-config interface GigabitEthernet0/0
show running-config interface GigabitEthernet0/0.10
show running-config interface GigabitEthernet0/0.20
show ip route
```

Vérifie l'état de l'interface physique, le numéro VLAN de chaque sous-interface et l'adresse IP correspondante. Si l'interface physique est désactivée, ses sous-interfaces ne peuvent pas assurer le routage attendu.

**À retenir :** ne corrige pas une panne de routage en changeant les VLAN access si les tests intra-VLAN prouvent que la couche 2 fonctionne déjà.


## 13. TP H — Dépannage d'une interface VLAN (SVI) sur un commutateur L3

Ce laboratoire est une **variante** de la topologie principale. Il ne faut pas activer simultanément le routage sur R1 et sur un switch L3 pour les mêmes passerelles sans plan d'architecture précis.

### Principe

Sur un commutateur multilayer, une interface VLAN (SVI) sert de passerelle L3 à un VLAN. Pour fonctionner, le VLAN doit exister et les conditions opérationnelles exigées par la plateforme doivent être satisfaites. Une SVI peut être administrativement active mais rester opérationnellement down si le VLAN ou les ports actifs requis ne sont pas présents.

### Configuration de référence d'un switch L3

Exemple indicatif, à appliquer dans une maquette adaptée :

```text
configure terminal
ip routing
vlan 10
 name USERS
vlan 20
 name SERVERS
!
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
end
```

Les ports des terminaux doivent être dans les VLAN correspondants. Dans cette variante, retire le routeur-on-a-stick ou désactive le routage concurrent selon le dessin de la maquette.

### Pannes à simuler

1. Supprimer le VLAN 10 ou l'absence de tout port actif dans le VLAN, puis observer `show ip interface brief` et `show vlan brief`.
2. Désactiver `interface Vlan10` et vérifier le résultat.
3. Oublier `ip routing` dans une configuration de switch L3 qui le requiert.
4. Affecter une adresse de passerelle erronée sur un poste.

Commandes utiles :

```text
show ip interface brief
show vlan brief
show interfaces vlan 10
show ip route
show running-config interface Vlan10
```

### Résultat attendu

Tu dois pouvoir distinguer une SVI absente, une SVI administrativement désactivée, une SVI non opérationnelle et une SVI opérationnelle mais affectée par un problème de routage ou de filtrage. La sortie exacte varie avec la famille de switch et sa version.


## 14. TP I — Le poste n'obtient pas d'adresse DHCP

**Symptôme :** un PC nouvellement raccordé ne reçoit pas les paramètres IP attendus. Un autre poste du même VLAN peut fonctionner avec une configuration statique.

Commence par distinguer deux scénarios :

- le serveur DHCP se trouve dans le même VLAN que le client ;
- le serveur DHCP se trouve dans un autre sous-réseau et le routeur ou switch L3 doit relayer la requête.

### Étape 1 — Contrôler le VLAN et le port

Vérifie `show vlan brief`, `show interfaces status`, `show interfaces ... switchport` et `show interfaces trunk`. Avant de toucher au serveur DHCP, prouve que le client est réellement connecté au VLAN attendu.

### Étape 2 — Comparer avec un client en IP statique

Attribue temporairement à un PC de laboratoire une adresse libre, un masque et une passerelle corrects du VLAN. Vérifie s'il peut joindre la passerelle. Si la connectivité statique fonctionne mais que DHCP échoue, oriente l'analyse vers la découverte DHCP, le serveur, le pool ou le relais.

### Étape 3 — Vérifier le serveur et le relais

Si le serveur est sur un autre sous-réseau, vérifie la présence du relais DHCP sur l'interface L3 qui reçoit les requêtes du client, ainsi que l'adresse de serveur ciblée. Sur Cisco IOS, `ip helper-address` est une commande courante de relais DHCP, mais elle doit être appliquée sur la bonne interface L3 et vers le bon serveur.

Exemple indicatif sur l'interface du VLAN client :

```text
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 ip helper-address 192.168.20.53
```

Ici `192.168.20.53` représente un serveur DHCP de laboratoire. Ne copie pas cet exemple si le serveur et le client sont sur le même VLAN ou si ton architecture de relais est différente.

### Étape 4 — Contrôler le pool

Sur le serveur ou routeur fournissant DHCP, vérifie : plage d'adresses disponible, exclusions, masque, passerelle par défaut, serveur DNS et absence de conflit. En environnement Cisco, utilise les commandes de consultation des bindings et des pools disponibles pour la version déployée.

### Pannes contrôlées

- Port du client déplacé temporairement vers le mauvais VLAN.
- VLAN client absent d'un trunk.
- Pool épuisé ou masque incorrect.
- Adresse de relais incorrecte ou configurée sur la mauvaise interface L3.

Pour chacune, relève les preuves avant la correction et confirme qu'un client du même VLAN reçoit les bons paramètres après réparation.


## 15. TP J — ACL ou politique de sécurité qui bloque le trafic

**Symptôme :** les VLAN et trunks paraissent corrects ; les routes sont présentes ; cependant, un type de trafic échoue alors que d'autres communications continuent.

### Diagnostic

Sur un routeur ou switch L3 Cisco, vérifie les ACL attachées aux interfaces et leurs compteurs :

```text
show access-lists
show ip interface
show running-config
```

Sur une plateforme donnée, des commandes plus ciblées permettent de voir l'ACL appliquée à une interface. Vérifie le sens (`in` ou `out`) et l'ordre des entrées. Un `deny` plus général placé avant une autorisation précise peut bloquer le trafic attendu. L'absence de règle autorisante peut également conduire au refus implicite dans une ACL classique.

### Méthode de test

1. Teste la passerelle du VLAN.
2. Teste un flux d'application connu comme autorisé.
3. Teste le flux qui échoue.
4. Relève les compteurs avant/après le test.
5. Compare l'adresse source/destination, le protocole et le port à la règle supposée correspondante.

Ne supprime pas toute l'ACL pour « prouver » qu'elle est responsable. Si une désactivation temporaire est indispensable en laboratoire, fais-le dans une maquette isolée et restaure la politique avant de terminer.


## 16. TP K — STP bloque un chemin ou le lien redondant change d'état

**Symptôme :** les VLAN existent, les ports sont configurés en trunk, mais un chemin redondant ne transfère pas les trames comme prévu.

STP peut placer un port en état de blocage afin d'éviter une boucle de couche 2. Ce comportement est normal dans une topologie redondante ; un port bloqué n'est pas automatiquement une panne. Il faut déterminer si ce port est censé transférer le trafic selon le dessin et le rôle STP attendu.

### Vérifications

```text
show spanning-tree
show spanning-tree vlan 10
show spanning-tree vlan 20
show interfaces status
show logging
```

### Travaux demandés

1. Identifier le root bridge et les ports root/designated/alternate (terminologie et affichage selon la version).
2. Expliquer le chemin utilisé entre PC-A et PC-B.
3. Débrancher un lien dans la maquette et observer la reconvergence.
4. Vérifier si le chemin restant transporte les VLAN nécessaires.
5. Restaurer le lien et comparer les états.

Ne désactive pas STP pour résoudre un simple problème de VLAN : tu pourrais transformer une erreur de configuration en boucle Ethernet.


## 17. TP L — Mauvaise adresse IP ou mauvais masque

**Symptôme :** le VLAN et le trunk fonctionnent, mais un seul PC ne peut pas atteindre certaines destinations.

### Scénario 1 : adresse du mauvais sous-réseau

Configure PC-A temporairement en `192.168.20.10/24`, alors que son port se trouve dans le VLAN 10. Observe les résultats vers PC-B et vers la passerelle. Vérifie le conflit éventuel avec PC-C et remets ensuite `192.168.10.10/24`.

### Scénario 2 : masque incorrect

Configure PC-A temporairement en `/25` au lieu de `/24`. La décision de considérer certaines adresses comme locales ou distantes peut changer. Teste un poste situé dans une autre partie du même `/24`, par exemple en ajoutant dans le labo une adresse de test `192.168.10.200/24` sur un hôte approprié.

### Scénario 3 : passerelle erronée

Garde l'adresse et le masque corrects, mais change la passerelle par défaut. Les communications dans le même sous-réseau peuvent continuer alors que les destinations distantes échouent.

**Leçon :** une panne qui ressemble à un problème VLAN peut être due au plan IP du seul poste concerné. Compare toujours le poste avec la configuration attendue.


## 18. Tableau de correspondance symptômes → premières vérifications

| Symptôme observé | Hypothèses à vérifier d'abord | Commandes/tests prioritaires |
|---|---|---|
| Un seul PC ne communique pas | Câble/port, VLAN access, adresse IP, port-security | `show interfaces status`, `show vlan brief`, `show interfaces ... switchport`, `ipconfig` |
| Deux hôtes du même VLAN ne communiquent pas entre switches | Trunk, liste VLAN autorisés, VLAN présent des deux côtés, STP | `show interfaces trunk`, `show vlan brief`, `show spanning-tree vlan X` |
| Les communications du VLAN 10 échouent mais le VLAN 20 marche | VLAN 10 absent d'un trunk ou mal affecté, règle spécifique | `show interfaces trunk`, `show mac address-table dynamic vlan 10` |
| Tous les hôtes d'un VLAN échouent vers d'autres VLAN | Passerelle, sous-interface/SVI, routage, ACL | `show ip interface brief`, `show ip route`, `show access-lists` |
| Un hôte joint sa passerelle mais pas un serveur distant | Route retour, ACL, service, DNS ou pare-feu | `show ip route`, traceroute, test du port applicatif |
| Un PC n'obtient aucune adresse DHCP | VLAN/port, trunk, pool, serveur ou relais | État du port, `show vlan brief`, pool/bindings DHCP, capture si possible |
| Le trunk est up mais un VLAN ne passe pas | VLAN non autorisé, VLAN absent, filtrage ou configuration de tag | `show interfaces trunk`, `show vlan brief`, `show interfaces ... switchport` |
| Avertissement de native VLAN mismatch | VLAN natif différent aux deux extrémités | `show interfaces trunk`, `show logging` |
| Le port est err-disabled | Port-security ou autre protection | `show interfaces status`, `show logging`, état des protections |
| Une SVI est down | VLAN inexistant, état opérationnel ou absence de ports actifs selon la plateforme | `show vlan brief`, `show ip interface brief`, `show interfaces vlan X` |
| Un ping échoue mais l'application fonctionne | ICMP filtré ou non pris en charge | Tester le protocole et le port applicatifs réels |
| La passerelle répond, mais les gros transferts échouent | MTU, PMTUD, filtrage ICMP utile, chemins asymétriques | Tests de taille de paquet et capture adaptée |

Ce tableau sert à hiérarchiser les hypothèses, pas à remplacer les preuves. Un symptôme peut avoir plusieurs causes possibles.


## 19. Commandes Cisco à connaître pour le dépannage VLAN

Les commandes ci-dessous sont courantes sur les commutateurs Catalyst IOS/IOS XE, mais les options disponibles et la sortie diffèrent selon la plateforme.

### VLAN et ports

```text
show vlan brief
show vlan id 10
show interfaces status
show interfaces FastEthernet0/2 switchport
show running-config interface FastEthernet0/2
```

Utilise ces commandes pour contrôler l'existence du VLAN, son nom, les ports membres et le mode access/trunk du port.

### Trunks et VLAN natif

```text
show interfaces trunk
show interfaces GigabitEthernet0/2 switchport
show logging
```

Vérifie le mode opérationnel, le VLAN natif, les VLAN autorisés et ceux qui sont réellement actifs sur le trunk. Un port configuré administrativement en trunk n'est pas, à lui seul, la preuve que tous les VLAN traversent correctement le lien.

### Table MAC et STP

```text
show mac address-table dynamic
show mac address-table dynamic vlan 10
show spanning-tree vlan 10
show spanning-tree vlan 20
```

La table MAC doit apprendre les adresses sur les ports attendus. Si la MAC d'un poste n'est pas apprise, le problème peut être en amont de la transmission ou le poste peut ne pas émettre au moment de la vérification. Si une MAC apparaît sur un port inattendu ou change souvent de port, recherche une topologie incorrecte, un déplacement de poste ou une boucle possible.

### Routage inter-VLAN

```text
show ip interface brief
show ip route
show ip arp
show running-config interface GigabitEthernet0/0.10
show running-config interface GigabitEthernet0/0.20
```

Sur un switch L3, ajoute l'inspection des interfaces VLAN et l'état du routage IP. Sur un routeur-on-a-stick, vérifie les sous-interfaces et le VLAN encapsulé.

### ACL et journaux

```text
show access-lists
show logging
```

Collecte les compteurs avant et après un test afin de voir si le paquet correspond à une règle. Ne tire pas de conclusion à partir d'une ACL uniquement parce qu'elle existe dans la configuration.


## 20. Défi final — Diagnostiquer sans connaître la panne injectée

Demande à une autre personne de modifier une seule des variables suivantes, sans t'indiquer laquelle :

- port access dans le mauvais VLAN ;
- VLAN retiré du trunk ;
- trunk transformé en port access ;
- VLAN natif incohérent ;
- interface désactivée ;
- sous-interface router-on-a-stick avec mauvais tag ;
- adresse IP, masque ou passerelle erronés ;
- ACL qui bloque un flux ;
- VLAN absent ;
- pool ou relais DHCP incorrect.

### Ta mission

Sans réinitialiser les équipements ni afficher d'emblée toute la configuration, applique une démarche structurée :

1. décris précisément le symptôme ;
2. choisis le test le plus discriminant ;
3. formule une hypothèse ;
4. collecte la sortie qui peut la confirmer ou l'infirmer ;
5. identifie la cause exacte ;
6. propose une correction minimale ;
7. fais valider T1 à T6 ou explique les tests qui ne sont pas pertinents pour cette panne ;
8. complète le rapport d'incident.

### Critères de réussite

- aucune modification aléatoire ;
- cause démontrée par au moins une preuve pertinente ;
- correction minimale et documentée ;
- tests positifs et négatifs refaits ;
- configuration de référence restaurée lorsque nécessaire.


## 21. Modèle de fiche d'incident

```text
ID de l'incident :
Date / heure :
Équipements et ports concernés :
VLAN concerné :
Source / destination du test :
Symptôme exact :
Impact utilisateur :
Dernier changement connu :
État initial observé :
Hypothèse 1 et preuve :
Hypothèse 2 et preuve :
Cause racine confirmée :
Correction appliquée :
Résultat des tests après correction :
Risque de régression contrôlé :
Action préventive :
```

Ne confonds pas la cause racine avec le symptôme. « Le ping échoue » est un symptôme ; « VLAN 10 absent de la liste autorisée du trunk SW1–SW2 » est une cause vérifiable.


## 22. Barème d'évaluation sur 100

| Compétence | Points |
|---|---:|
| Décrire le symptôme et la portée sans ambiguïté | 10 |
| Vérifier les ports et les VLAN access | 15 |
| Contrôler les trunks, VLAN natif et liste autorisée | 15 |
| Analyser FDB et STP | 10 |
| Diagnostiquer le routage inter-VLAN/SVI | 15 |
| Distinguer DHCP, adressage et filtrage | 10 |
| Collecter des preuves avant/après | 10 |
| Restaurer le fonctionnement sans régression | 10 |
| Rédiger un rapport clair | 5 |
| **Total** | **100** |

Une configuration qui fonctionne après plusieurs modifications non documentées ne prouve pas une maîtrise du dépannage. La compétence est démontrée lorsque la cause est comprise, la correction est limitée et la non-régression est testée.


## 23. Références officielles

- [Cisco — Configure Inter-VLAN Routing with Catalyst Switches](https://www.cisco.com/c/en/us/support/docs/lan-switching/inter-vlan-routing/41260-189.html) : routage inter-VLAN et commandes de vérification, dont l'état des trunks.
- [Cisco — Configure Inter-VLAN Routing with an External Router](https://www.cisco.com/c/en/us/support/docs/lan-switching/inter-vlan-routing/14976-50.html) : router-on-a-stick, 802.1Q, VLAN natif et vérification.
- [Cisco — Troubleshoot DHCP in Enterprise Networks](https://www.cisco.com/c/en/us/support/docs/ip/dynamic-address-allocation-resolution/27470-100.html) : distinction entre panne DHCP locale, relais DHCP et configuration du service.
- [Cisco — Troubleshoot DHCP on Catalyst 9000 DHCP Relay Agents](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/217429-troubleshoot-slow-or-intermittent-dhcp-o.html) : considérations de dépannage DHCP relay sur plateformes Catalyst 9000.

Les exemples de ce cahier sont pédagogiques. Consulte la documentation de la famille de switch et de la version IOS/IOS XE utilisée, car les capacités, noms d'interfaces, états et syntaxes peuvent varier.


## Conclusion

Le dépannage VLAN devient beaucoup plus rapide lorsque les tests sont organisés en couches : port et état physique, appartenance au VLAN, trunk, apprentissage MAC, STP, adressage IP, passerelle, routage et sécurité. Le test intra-VLAN permet notamment de séparer les problèmes de commutation des problèmes de routage inter-VLAN. De même, un trunk opérationnel ne garantit pas que chaque VLAN est autorisé, et une interface active ne garantit pas qu'elle est dans le bon VLAN.

La règle essentielle de ce laboratoire est simple : **observer, formuler une hypothèse, la tester, corriger une cause à la fois et vérifier qu'aucune autre communication n'a été cassée.**
