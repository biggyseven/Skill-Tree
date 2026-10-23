<style>
.ec-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.1rem 0;padding:.65rem;border:1px solid #26384d;border-radius:14px;background:#080d16;color:#e8eff9;box-sizing:border-box}
.ec-diagram svg{display:block;width:100%;height:auto;max-width:100%}
.ec-flow{stroke-dasharray:9 7;animation:ecDash 2.3s linear infinite}
@keyframes ecDash{to{stroke-dashoffset:-32}}
@media(prefers-reduced-motion:reduce){.ec-flow{animation:none!important}}
</style>
# Agrégation de liens (EtherChannel/LACP) — Niveau Expert

**Niveau :** Expert  
**Domaine :** ingénierie réseau, switching, haute disponibilité, interopérabilité multiconstructeurs et exploitation.  
**Prérequis :** VLAN/trunk, Ethernet, STP, bases du routage, interface logique, adressage IP et commandes d’observation d’un commutateur.  
**Objectif :** concevoir, déployer, diagnostiquer et faire évoluer des LAG/LACP sur des environnements à plusieurs constructeurs, en comprenant le plan de contrôle, le hachage des flux, les limites de redondance, les états de sélection et les conditions de récupération après panne.

> **Cadre d’utilisation :** effectuer les laboratoires et changements uniquement sur des équipements autorisés. Une erreur d’agrégation peut créer une boucle L2, isoler un serveur, réduire la capacité disponible ou perturber plusieurs VLAN. Sauvegarder les configurations, documenter les dépendances et préparer un rollback testable avant toute intervention en production.

## Parcours du cours

1. Modèle de service et précision des termes : LAG, EtherChannel, LACP et multi-châssis.
2. Fonctionnement approfondi de LACP : acteur, partenaire, identifiants, clés et états.
3. Interopérabilité multiconstructeurs et contrat de configuration commun.
4. Répartition des flux, hachage, polarisation, capacité et mesure.
5. MLAG, vPC, VSX, MC-LAG et multihoming EVPN : ce que LACP ne fait pas.
6. Pannes partielles, temporisateurs, min-links, standby et récupération.
7. Configurations comparées et méthodes de validation.
8. Dépannage expert, capture LACP et lecture des compteurs.
9. Déploiements, migrations, changement de vitesse et rollback.
10. Laboratoires, scénarios de panne, exercices et corrigés.

## 1. Définir le service avant de configurer les ports

### 1.1 Les quatre notions à ne pas confondre

- **LAG (Link Aggregation Group)** : groupe logique constitué de liens Ethernet parallèles. Il masque une partie de la complexité des membres à la couche supérieure. Le comportement exact dépend du niveau L2 ou L3 et de la plateforme.
- **LACP (Link Aggregation Control Protocol)** : protocole normalisé qui échange l’état et l’identité des ports pour permettre la sélection coordonnée de membres compatibles. Il n’est pas le mécanisme de transport du trafic utilisateur.
- **EtherChannel / Port-Channel / port-channel / ae / lag / bond** : noms utilisés selon les fournisseurs et systèmes pour désigner l’agrégat logique ou son interface.
- **MLAG / vPC / VSX / MC-LAG / EVPN multihoming** : mécanismes d’architecture permettant à un agrégat d’être raccordé à plusieurs châssis ou à un ensemble de pairs. LACP tout seul ne rend pas deux commutateurs indépendants équivalents à un seul partenaire.

La norme IEEE 802.1AX définit la Link Aggregation. Elle décrit le principe d’agréger plusieurs liens point à point pour qu’un client MAC les traite comme un lien, ainsi que les mécanismes de distribution des conversations. L’implémentation, les limites de membres, les noms de commandes, les fonctions multichâssis et les comportements de secours diffèrent selon le système. Voir les références en fin de cours.

### 1.2 Ce qu’un LAG apporte — et ce qu’il ne promet pas

Un agrégat bien conçu améliore la capacité totale disponible pour plusieurs conversations et peut préserver la connectivité lorsqu’un membre disparaît. Il n’offre pas automatiquement :

- une multiplication par N de la vitesse d’un seul flux TCP ;
- une répartition exactement uniforme de la charge entre les membres ;
- une protection contre la panne du châssis unique où aboutissent tous les câbles ;
- une détection instantanée de chaque panne physique, optique, logique ou de forwarding ;
- une compatibilité entre n’importe quelles combinaisons de vitesse, FEC, MTU, VLAN, modes L2/L3 et paramètres de plateforme ;
- une cohérence de configuration entre deux commutateurs multichâssis si le mécanisme peer ne synchronise pas le paramètre concerné.

### Schéma 1 — Du lien physique à l’interface logique

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 360" role="img" aria-label="Quatre liens Ethernet physiques entre un serveur et un commutateur sont agrégés en un lien logique Port-Channel. Le trafic est réparti par flux, pas nécessairement paquet par paquet."><defs><marker id="ec1a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec1b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker></defs><style>.t{font:600 16px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.f{fill:none;stroke:#66d9ff;stroke-width:2.8;marker-end:url(#ec1a)}.g{fill:none;stroke:#75e6b0;stroke-width:2.8;marker-end:url(#ec1b)}.flow{stroke-dasharray:9 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="24" y="58" width="170" height="110" rx="12" fill="#142b42" stroke="#66d9ff" stroke-width="2"/><text x="109" y="91" class="t">Serveur</text><text x="109" y="115" class="s">NIC / bond0</text><text x="109" y="136" class="s">Une interface logique</text><rect x="726" y="58" width="170" height="110" rx="12" fill="#16372d" stroke="#75e6b0" stroke-width="2"/><text x="811" y="91" class="t">Switch</text><text x="811" y="115" class="s">Port-Channel / ae / lag</text><text x="811" y="136" class="s">Une interface logique</text><path d="M194 86 C330 30 590 30 726 86" class="f flow" marker-end="url(#ec1a)"/><path d="M194 108 C345 77 575 77 726 108" class="f flow" marker-end="url(#ec1a)"/><path d="M194 130 C345 154 575 154 726 130" class="g flow" marker-end="url(#ec1b)"/><path d="M194 151 C330 205 590 205 726 151" class="g flow" marker-end="url(#ec1b)"/><text x="460" y="35" class="s">LACP négocie les membres (si activé aux deux extrémités)</text><rect x="263" y="227" width="394" height="74" rx="12" fill="#101b29" stroke="#405773" stroke-width="1.6"/><text x="460" y="254" class="t">LAG : lien logique</text><text x="460" y="276" class="s">4 × 10 Gb/s = jusqu’à 40 Gb/s agrégés</text><text x="460" y="293" class="s">pour plusieurs flux bien répartis, pas pour un flux unique garanti</text><path d="M460 168V222" stroke="#8aa7c7" stroke-width="1.8" stroke-dasharray="4 5" fill="none"/><text x="460" y="337" class="s">Un membre défaillant est retiré; les flux sont redistribués selon le hachage et la plateforme.</text></svg></div>

### 1.3 L2 et L3 : deux modèles différents

Un LAG **Layer 2** se comporte généralement comme un seul port logique vis-à-vis du VLAN tagging, du trunking et de STP. Les détails de STP et de l’interface logical port diffèrent selon le produit. Tous les membres doivent porter des paramètres compatibles, notamment le mode access/trunk, la VLAN native et l’ensemble des VLAN autorisées lorsqu’ils s’appliquent.

Un LAG **Layer 3** expose une interface routée logique portant l’adresse IP ou participant au protocole de routage. Les adresses ne doivent généralement pas être configurées individuellement sur les interfaces physiques membres : cela dépend du modèle du système, mais dans le modèle classique l’adressage est porté par l’interface agrégée. Vérifie toujours la documentation de la plateforme.

### 1.4 Capacité nominale, capacité utile et duplex

Quatre membres 10 Gb/s donnent une capacité nominale d’agrégat de 40 Gb/s dans chaque sens en full-duplex, sous réserve que les quatre membres soient actifs et utilisables. Cela ne signifie pas qu’un seul transfert atteindra 40 Gb/s. Un algorithme de distribution qui conserve l’ordre des paquets affecte généralement une conversation à un membre selon un hachage. Si les conversations sont peu nombreuses ou si leurs clés entrent en collision, l’usage peut être fortement déséquilibré.

Dans un calcul de dimensionnement, prévois la capacité après panne :

\[
C_{N-1} = (N-1) \times C_{membre}
\]

Cette formule simple suppose des membres de même capacité, tous actifs et aucune autre contrainte. Si le service exige au moins 25 Gb/s utiles lors de la perte d’un lien, quatre membres de 10 Gb/s fournissent 30 Gb/s nominaux après la panne d’un membre, mais il faut encore tenir compte de l’overhead, des limites de flux, des buffers, du trafic en rafale et de la distribution réelle.

## 2. LACP en profondeur

### 2.1 L’acteur et le partenaire

Dans chaque échange, l’**actor** est le système local qui émet son état LACP ; le **partner** est le système distant décrit dans les informations reçues. Chaque extrémité possède un identifiant système composé d’une priorité système et d’une adresse MAC, ainsi qu’un identifiant et une priorité de port. Les champs et états échangés permettent aux systèmes de déterminer si les ports sont destinés au même agrégateur et si la sélection peut être synchronisée.

Conceptuellement, les informations importantes sont :

- **System ID / System Priority** : identifie l’équipement partenaire et participe aux décisions qui demandent une comparaison de priorité.
- **Port ID / Port Priority** : identifie le port local dans le système et influence certaines sélections en cas de contrainte de membres.
- **Key (clé d’agrégateur)** : exprime la compatibilité d’agrégateur, déterminée ou configurée selon le système et l’interface. Une même valeur textuelle sur plusieurs fournisseurs n’est pas une exigence universelle ; il faut que le modèle et la configuration produisent des ports compatibles.
- **État du port** : indique notamment les capacités et l’état de synchronisation, de collecte et de distribution. L’interprétation de la sortie CLI nécessite de lire la terminologie de la version installée.

### 2.2 Active, passive et statique

En mode **active**, un port émet des LACPDU et répond aux LACPDU reçues. En mode **passive**, il répond mais n’initie pas l’échange. Active-active et active-passive peuvent négocier ; passive-passive n’initie pas les échanges et ne forme donc normalement pas le LAG dynamique. Le mode exact affiché et les valeurs par défaut varient selon l’OS.

Un LAG **statique** est configuré sans négociation LACP. Il peut être adapté à certains équipements ou contextes contrôlés, mais il perd les signaux de négociation de partenaire et rend certaines erreurs de câblage ou de groupement plus difficiles à détecter. Ne mélange pas un côté statique avec un côté LACP en supposant que le résultat sera standard et fiable : le comportement dépend du système, et la configuration doit correspondre de part et d’autre.

### Schéma 2 — Échange LACP et sélection d’un membre

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 370" role="img" aria-label="Échange LACP entre acteur local et partenaire : System ID, clé d'agrégateur, identifiants et états des ports sont échangés; les deux côtés sélectionnent des membres compatibles."><defs><marker id="ec2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec2b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker></defs><style>.t{font:600 16px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.5;marker-end:url(#ec2a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.5;marker-end:url(#ec2b)}.flow{stroke-dasharray:9 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="42" y="42" width="250" height="110" rx="12" fill="#142b42" stroke="#66d9ff" stroke-width="2"/><text x="167" y="71" class="t">Acteur A</text><text x="167" y="95" class="s">System ID + priorité</text><text x="167" y="115" class="s">Port ID + clé d’agrégateur</text><text x="167" y="135" class="s">État LACP local</text><rect x="628" y="42" width="250" height="110" rx="12" fill="#16372d" stroke="#75e6b0" stroke-width="2"/><text x="753" y="71" class="t">Partenaire B</text><text x="753" y="95" class="s">System ID + priorité</text><text x="753" y="115" class="s">Port ID + clé d’agrégateur</text><text x="753" y="135" class="s">État LACP local</text><path d="M292 77H623" class="a flow" marker-end="url(#ec2a)"/><text x="458" y="64" class="s">LACPDU →</text><path d="M628 121H297" class="b flow" marker-end="url(#ec2b)"/><text x="458" y="145" class="s">← LACPDU</text><rect x="242" y="198" width="436" height="70" rx="12" fill="#33291b" stroke="#ffca72" stroke-width="1.8"/><text x="460" y="225" class="t">Sélection des membres</text><text x="460" y="247" class="s">Identité partenaire cohérente · key compatible · état synchronisé</text><path d="M167 152V178H350V193" stroke="#7d9bb8" stroke-width="1.8" fill="none"/><path d="M753 152V178H570V193" stroke="#7d9bb8" stroke-width="1.8" fill="none"/><rect x="64" y="302" width="354" height="44" rx="9" fill="#16372d" stroke="#75e6b0"/><text x="241" y="329" class="s">Membre sélectionné : collecte/distribution active</text><rect x="502" y="302" width="354" height="44" rx="9" fill="#3a2026" stroke="#ff8d91"/><text x="679" y="329" class="s">Membre non sélectionné : standby / individual / suspendu</text><path d="M352 268V291H241V297" stroke="#75e6b0" stroke-width="1.8" fill="none"/><path d="M568 268V291H679V297" stroke="#ff8d91" stroke-width="1.8" fill="none"/></svg></div>

### 2.3 États et disponibilité du membre

La commande de statut doit permettre de distinguer au minimum :

1. **Lien physique up** : signal reçu, vitesse et couche physique acceptées. Cela ne garantit pas la sélection LACP.
2. **LACP reçu** : les LACPDU arrivent du bon partenaire. Un lien up sans partenaire attendu pointe vers une incohérence de mode, de câblage, d’interface ou de protocole.
3. **Membre compatible et sélectionné** : le port appartient au bon agrégateur et respecte les contraintes de capacité, de vitesse et d’administration.
4. **Synchronisation et collecte/distribution** : le membre est autorisé à recevoir et/ou à émettre le trafic utilisateur selon l’état LACP et les règles locales.
5. **Agrégat opérationnel** : l’interface logique est up selon les conditions de la plateforme, y compris toute politique `min-links` ou équivalente.

Ne te contente pas d’un message “LACP up”. Vérifie combien de membres sont réellement sélectionnés et actifs, si les bons System ID et port ID sont vus, et si le trafic utilisateur augmente les compteurs des membres attendus.

### 2.4 Temporisateurs fast et slow

LACP peut utiliser un mode de périodicité rapide ou lente. Le mode rapide envoie des LACPDU plus fréquemment et peut accélérer la détection de la perte de contact protocolair, à condition que les deux systèmes et la plateforme appliquent le comportement attendu. Les détails du timeout et les options de configuration varient.

Un mode rapide n’accélère pas nécessairement la détection d’une panne de forwarding où le lien physique reste up et les LACPDU continuent à être échangées. C’est le cas d’une blackhole interne, d’un problème de VLAN ou d’un chemin de données endommagé mais d’un control plane actif. Il faut des sondes de service, des compteurs, de l’OAM ou un mécanisme spécifique pour de tels cas.

### 2.5 LACP n’est pas un test applicatif

LACP valide la relation logique des membres. Il ne prouve pas que :

- le VLAN nécessaire est autorisé sur un trunk ;
- la MTU de bout en bout est correcte ;
- un routeur a la route retour ;
- les ACL sont compatibles ;
- les flux sont répartis selon le besoin métier ;
- l’application répond ;
- le peer-link MLAG ou une fonction de synchronisation est sain dans toutes les situations.

Un LAG peut être pleinement opérationnel tout en transportant un service cassé. Une validation de production doit donc inclure la couche physique, LACP, l’interface logique, le VLAN ou le routage, puis le test applicatif.

## 3. Interopérabilité multiconstructeurs

### 3.1 Concevoir un contrat de configuration neutre

Pour réunir des constructeurs différents, rédige un contrat avant les commandes. Il doit inclure :

- identité des extrémités et ports physiques associés ;
- nombre prévu de membres, vitesses, types de transceivers, FEC et breakout ;
- type de LAG : LACP dynamique ou statique, niveau L2 ou L3 ;
- mode actif/passif et périodicité LACP lorsque configurable ;
- nombre minimal de membres pour que le service soit déclaré disponible ;
- VLAN access ou trunk, VLAN native/tagging et liste des VLAN autorisées ;
- MTU de trame, prise en charge jumbo frame et politique de validation ;
- paramètres L3 : adresses, protocoles, timers, ACL/filters et routage ;
- algorithme de distribution ou champs de hachage ;
- gestion des liens non sélectionnés, fallback, standby et comportement au redémarrage ;
- méthode de surveillance, compteurs de référence, test de panne et rollback.

La configuration ne doit pas nécessairement être identique dans sa syntaxe ; elle doit produire un comportement compatible. Une configuration « ressemblante » n’est pas une preuve de compatibilité.

### 3.2 Compatibilité du plan physique

Vérifie chaque lien, pas uniquement le groupe : vitesse négociée, duplex, FEC (pour certaines vitesses optiques/cuivre), transceiver supporté, type de breakout, longueur/fibre, polarité optique, erreurs CRC et compteurs de signal. Deux membres placés dans le même LAG mais configurés à des vitesses ou paramètres incompatibles peuvent être rejetés, suspendus ou traités de manière différente selon la plate-forme.

Évite les changements de vitesse et de FEC simultanés sur tous les membres. Une migration contrôlée change un membre ou un petit lot, contrôle sa sélection et le trafic, puis poursuit si l’état est sain.

### 3.3 Compatibilité Layer 2

Pour un LAG de trunk interconstructeur, aligne :

- les VLAN autorisées, sans différence accidentelle entre membres ;
- la VLAN native et le traitement des trames non taguées ;
- le tagging des VLAN de service ;
- le MTU et les conventions de mesure (taille Ethernet avec ou sans FCS selon les interfaces) ;
- les paramètres de sécurité du port ;
- l’appartenance au STP, les protections contre boucles et les limites d’apprentissage MAC.

Une différence de VLAN native peut être particulièrement trompeuse : les trames non taguées peuvent être classées dans des VLAN différents, même lorsque les VLAN taguées semblent fonctionner. La validation doit inclure des tests pour les VLAN critiques, pas uniquement un ping dans un seul segment.

### 3.4 Compatibilité Layer 3

Sur une agrégation routée, compare l’adressage de l’interface logique, la MTU IP, les paramètres ARP/ND, les routes et les adjacences de routage. Dans les protocoles dynamiques, évite de mélanger sans analyse des timers incompatibles, des authentifications, des MTU de contrôle ou des paramètres de multipath inattendus. La distribution LAG et l’ECMP de couche 3 peuvent se superposer : le trafic est d’abord réparti entre chemins ECMP puis entre membres du LAG, ou l’ordre inverse selon les points d’entrée et la plateforme. Cette hiérarchie peut produire une polarisation.

### 3.5 Exemples de correspondance de termes

| Concept | Cisco IOS XE | Arista EOS | Juniper Junos | Aruba CX | Linux |
|---|---|---|---|---|---|
| Interface logique typique | `Port-channel10` | `Port-Channel10` | `ae0` | `lag 10` | `bond0` |
| Membre physique | `channel-group 10` | `channel-group 10 mode active` | `802.3ad ae0` / groupe correspondant | `lag 10` | `bond0` esclave/member |
| LACP dynamique | `active` / `passive` | `active` / `passive` selon syntaxe/version | `active` / `passive` | `active` / `passive` | `mode 802.3ad` |
| Observation utile | `show etherchannel summary`, `show lacp` selon plateforme | `show port-channel summary`, `show lacp` | `show lacp interfaces`, `show interfaces ae0` | `show lacp interfaces`, `show interface lag` selon version | `cat /proc/net/bonding/bond0`, `ip -d link` |

Ce tableau est une carte de vocabulaire, pas une recette copiée-collée. Les options disponibles peuvent changer selon le modèle matériel, le train logiciel, le rôle L2/L3 et l’interface de management. Utilise la documentation qui correspond à la version déployée.

### Schéma 3 — Contrat d’interopérabilité

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" role="img" aria-label="Un hôte Linux est agrégé en LACP vers un switch Cisco ou Arista sur une interface Port-Channel, et un second exemple montre un routeur Juniper vers Aruba CX. Les paramètres de VLAN, MTU, vitesse et mode LACP doivent être compatibles sans exiger une syntaxe identique."><defs><marker id="ec8a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec8b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:11.5px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.5;marker-end:url(#ec8a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.5;marker-end:url(#ec8b)}.flow{stroke-dasharray:8 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="25" y="38" width="225" height="88" rx="11" fill="#142b42" stroke="#66d9ff"/><text x="137" y="65" class="t">Linux server</text><text x="137" y="87" class="s">bond0 · mode 802.3ad</text><text x="137" y="106" class="s">LACP active / miimon</text><rect x="350" y="38" width="225" height="88" rx="11" fill="#16372d" stroke="#75e6b0"/><text x="462" y="65" class="t">Cisco / Arista</text><text x="462" y="87" class="s">Port-Channel / port-channel</text><text x="462" y="106" class="s">LACP active ou passive</text><path d="M250 61H345" class="a flow" marker-end="url(#ec8a)"/><path d="M350 101H255" class="b flow" marker-end="url(#ec8b)"/><text x="299" y="48" class="s">LACP</text><rect x="25" y="175" width="225" height="88" rx="11" fill="#142b42" stroke="#66d9ff"/><text x="137" y="202" class="t">Juniper</text><text x="137" y="224" class="s">ae0 · aggregated-ether-options</text><text x="137" y="243" class="s">LACP active</text><rect x="350" y="175" width="225" height="88" rx="11" fill="#16372d" stroke="#75e6b0"/><text x="462" y="202" class="t">Aruba CX</text><text x="462" y="224" class="s">lag 10 · LACP active</text><text x="462" y="243" class="s">Trunk / VLAN autorisées</text><path d="M250 198H345" class="a flow" marker-end="url(#ec8a)"/><path d="M350 238H255" class="b flow" marker-end="url(#ec8b)"/><rect x="625" y="62" width="270" height="180" rx="12" fill="#101b29" stroke="#405773"/><text x="760" y="89" class="t">Contrat d’interopérabilité</text><text x="760" y="116" class="s">Même objectif de LAG</text><text x="760" y="139" class="s">Membres de vitesse compatible</text><text x="760" y="162" class="s">VLAN / native / MTU alignés</text><text x="760" y="185" class="s">Trunk vs routé cohérent</text><text x="760" y="208" class="s">LACP IDs/états cohérents</text><text x="460" y="302" class="s">Les noms de commandes diffèrent; vérifier la référence officielle pour l’OS et la version exacts.</text><path d="M575 82H619" class="a" marker-end="url(#ec8a)"/><path d="M575 219H602V233H619" class="b" marker-end="url(#ec8b)"/></svg></div>

## 4. Répartition des flux : la réalité de la capacité

### 4.1 Pourquoi on utilise un hachage

Pour éviter la réorganisation des paquets, de nombreuses implémentations utilisent un hachage stable basé sur tout ou partie des informations de flux, puis choisissent un membre. Les champs potentiels comprennent MAC source/destination, IP source/destination, protocole L4, ports TCP/UDP et d’autres métadonnées selon l’équipement. L’ensemble exact de champs et le calcul peuvent être configurables et diffèrent entre la pile Linux, les commutateurs et les ASIC.

Le hachage est une fonction de distribution, pas un ordonnanceur qui mesure en temps réel les files d’attente pour envoyer chaque paquet sur le lien le moins chargé. Deux gros flux peuvent entrer en collision et saturer le même membre alors que d’autres sont sous-utilisés. Les flux d’un même couple ou ceux qui partagent une partie importante du tuple peuvent aussi se distribuer de façon inattendue.

### Schéma 4 — Hachage et collisions de flux

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 350" role="img" aria-label="Plusieurs flux passent par un algorithme de hachage basé sur les adresses MAC, IP et ports, puis sont affectés à un membre physique. Des collisions peuvent envoyer plusieurs flux sur le même membre."><defs><marker id="ec3a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec3b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.5;marker-end:url(#ec3a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.5;marker-end:url(#ec3b)}.flow{stroke-dasharray:9 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="22" y="44" width="220" height="246" rx="12" fill="#142b42" stroke="#66d9ff"/><text x="132" y="73" class="t">Flux entrants</text><text x="132" y="104" class="s">F1 : client A → serveur 1</text><text x="132" y="132" class="s">F2 : client B → serveur 2</text><text x="132" y="160" class="s">F3 : client C → serveur 3</text><text x="132" y="188" class="s">F4 : client D → serveur 4</text><text x="132" y="231" class="s">MAC · IP · ports L4</text><text x="132" y="253" class="s">selon capacités</text><rect x="330" y="90" width="255" height="156" rx="12" fill="#33291b" stroke="#ffca72" stroke-width="2"/><text x="457" y="121" class="t">Hash / distribution</text><text x="457" y="149" class="s">Tuple choisi par l’OS ou le switch</text><text x="457" y="173" class="s">Fonction de hachage → bucket</text><text x="457" y="197" class="s">bucket → membre actif</text><text x="457" y="222" class="s">Pas de garantie d’équité parfaite</text><path d="M242 122H324" class="a flow" marker-end="url(#ec3a)"/><path d="M242 166H324" class="a flow" marker-end="url(#ec3a)"/><path d="M242 210H324" class="a flow" marker-end="url(#ec3a)"/><rect x="676" y="42" width="220" height="250" rx="12" fill="#16372d" stroke="#75e6b0"/><text x="786" y="71" class="t">Membres physiques</text><rect x="704" y="91" width="164" height="38" rx="8" fill="#214a3a" stroke="#75e6b0"/><text x="786" y="115" class="s">Membre 1 : F1 + F4</text><rect x="704" y="143" width="164" height="38" rx="8" fill="#214a3a" stroke="#75e6b0"/><text x="786" y="167" class="s">Membre 2 : F2</text><rect x="704" y="195" width="164" height="38" rx="8" fill="#214a3a" stroke="#75e6b0"/><text x="786" y="219" class="s">Membre 3 : F3</text><rect x="704" y="247" width="164" height="28" rx="7" fill="#3a2026" stroke="#ff8d91"/><text x="786" y="266" class="s">Membre 4 : peu utilisé</text><path d="M585 127H670" class="b flow" marker-end="url(#ec3b)"/><path d="M585 167H670" class="b flow" marker-end="url(#ec3b)"/><path d="M585 207H670" class="b flow" marker-end="url(#ec3b)"/><text x="460" y="320" class="s">Un flux TCP unique est généralement épinglé à un membre ; plusieurs flux donnent une meilleure chance de répartir la charge.</text></svg></div>

### 4.2 Un seul flux ou de nombreux flux

Dans le modèle habituel, les paquets d’une conversation restent sur un même membre physique dans un sens pour préserver l’ordre. Le débit maximal d’une session unique se rapproche donc du débit d’un seul membre, pas de la somme de tous les membres. Les détails dépendent du mécanisme de distribution et du protocole; ne suppose pas qu’un flux unique puisse exploiter automatiquement l’ensemble du LAG.

Pour mesurer correctement :

1. utilise plusieurs sessions en parallèle, tout en mesurant séparément les flux individuels ;
2. mesure dans les deux directions ;
3. surveille chaque membre plutôt que le seul compteur logique ;
4. teste différents couples de sources/destinations et ports ;
5. observe les drops, les erreurs, l’occupation des buffers et les changements de hachage ;
6. sépare débit applicatif, débit L2 et overhead de protocole.

### 4.3 Polarisation et hachages emboîtés

Une fabric avec plusieurs niveaux de multipath peut appliquer un hash à plusieurs endroits : hachage de l’hôte vers ses ports, distribution par un switch, ECMP vers un next-hop, puis distribution dans un LAG en aval. Si ces mécanismes utilisent des champs ou seeds corrélés, les flux peuvent être concentrés sur un sous-ensemble de liens. C’est souvent appelé polarisation.

Les possibilités de mitigation sont spécifiques à la plateforme : choisir d’autres champs de hachage, activer un hash symétrique ou un seed lorsque disponible, augmenter la diversité de tuples, ajuster les chemins ECMP, utiliser des mécanismes de flowlet/adaptive load balancing quand ils sont réellement pris en charge, ou revoir l’architecture. Une modification du hash peut redistribuer brutalement les flux existants ; le risque de réordonnancement, de pertes transitoires ou de perturbation des sessions doit être évalué.

### 4.4 Sens aller et sens retour

Un LAG full-duplex dispose de sa capacité dans chaque sens, mais les choix de membres ne sont pas nécessairement identiques pour le retour. Le hachage peut être symétrique ou directionnel selon l’équipement. Deux endpoints peuvent observer un comportement différent sur une même conversation parce que les équipements d’extrémité et les ASIC n’utilisent pas les mêmes champs. Compare les compteurs et captures sur les deux côtés.

### 4.5 Capacité N-1 et seuils `min-links`

Un seuil `min-links` (ou équivalent) définit le nombre minimum de membres actifs requis pour que le LAG soit considéré opérationnel. Un seuil élevé peut empêcher le service de fonctionner dans un état dégradé mais encore utile; un seuil bas peut maintenir un service up avec trop peu de capacité pour la charge réelle.

Pour définir ce seuil, ne choisis pas arbitrairement « la moitié des ports ». Il faut relier la décision à :

- le débit de pointe et l’utilisation attendue ;
- la capacité restante lors de chaque scénario de panne acceptable ;
- la possibilité qu’un seul membre transporte une conversation critique ;
- les exigences de service et les alarmes ;
- les comportements de bascule de couche supérieure ;
- les temps de convergence et les conséquences d’un LAG qui se ferme.

Un LAG déclaré `up` est un indicateur de connectivité, pas un engagement de capacité. La supervision doit signaler la baisse de nombre de membres même si l’état logique reste up.

### 4.6 Mesurer une répartition réellement déséquilibrée

Ne conclus pas que le hash est défectueux à partir d’un snapshot instantané. Surveille plusieurs intervalles et compare : octets/s et paquets/s par membre, direction de chaque compteur, drops, erreurs, tailles de paquets et durées des flux. Les débits moyens peuvent cacher les microbursts. Un seul lien peut dropper des paquets pendant que le LAG agrégé paraît n’utiliser que 45 % de sa capacité théorique.

Des métriques pratiques :

- **utilisation par membre** : débit membre / débit nominal du membre ;
- **dispersion** : écart entre le membre le plus et le moins chargé, interprété avec le nombre et la nature des flux ;
- **capacité restante** : somme des membres encore actifs après panne ;
- **ratio de perte** : pertes observées rapportées au volume observé, avec attention aux drops au point de capture ;
- **impact applicatif** : latence, retries, pertes applicatives et SLO, pas seulement lien up/down.

## 5. Multi-châssis et haute disponibilité

### 5.1 Pourquoi deux liens vers deux switches ne suffisent pas

Si un serveur câble deux NIC vers deux commutateurs indépendants, la création d’un seul LAG côté serveur ne suffit pas à faire de ces ports un groupe cohérent. Chaque commutateur présente son propre System ID et ses propres décisions de forwarding. Selon la configuration, l’hôte peut voir un partenaire différent ou des membres incompatibles, ou le réseau peut créer un chemin L2 asymétrique.

Il faut soit une architecture où les commutateurs apparaissent à l’hôte comme un seul système logique (par exemple stack/châssis virtuel supporté), soit une technologie multichâssis compatible des deux côtés, soit un protocole d’hôte et une architecture spécifiquement conçus pour le multihoming.

### Schéma 5 — MLAG n’est pas fourni par LACP seul

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390" role="img" aria-label="Un serveur est connecté par deux liens à deux switches distincts qui coopèrent via une technologie multichâssis. Les deux liens apparaissent comme un seul agrégat au serveur. Les échanges peer-link et keepalive sont deux fonctions distinctes."><defs><marker id="ec4a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec4b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#c4a1ff"/></marker><marker id="ec4c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ffca72"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.7;marker-end:url(#ec4a)}.b{fill:none;stroke:#c4a1ff;stroke-width:2.4;marker-end:url(#ec4b)}.c{fill:none;stroke:#ffca72;stroke-width:2;marker-end:url(#ec4c)}.flow{stroke-dasharray:9 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="360" y="18" width="200" height="64" rx="11" fill="#142b42" stroke="#66d9ff" stroke-width="2"/><text x="460" y="44" class="t">Serveur / NIC Team</text><text x="460" y="65" class="s">Un seul LAG côté hôte</text><rect x="45" y="140" width="310" height="102" rx="12" fill="#16372d" stroke="#75e6b0" stroke-width="2"/><text x="200" y="168" class="t">Switch A</text><text x="200" y="192" class="s">Pair vPC / MLAG / VSX</text><text x="200" y="216" class="s">Membres LAG sélectionnés</text><rect x="565" y="140" width="310" height="102" rx="12" fill="#16372d" stroke="#75e6b0" stroke-width="2"/><text x="720" y="168" class="t">Switch B</text><text x="720" y="192" class="s">Pair vPC / MLAG / VSX</text><text x="720" y="216" class="s">Membres LAG sélectionnés</text><path d="M405 82L245 134" class="a flow" marker-end="url(#ec4a)"/><path d="M515 82L675 134" class="a flow" marker-end="url(#ec4a)"/><text x="460" y="160" class="s">Peer-link</text><path d="M355 180H560" class="b flow" marker-end="url(#ec4b)"/><path d="M565 194H360" class="b flow" marker-end="url(#ec4b)"/><text x="460" y="221" class="s">Keepalive sur chemin distinct</text><path d="M355 241H560" class="c" stroke-dasharray="3 5" marker-end="url(#ec4c)"/><path d="M565 251H360" class="c" stroke-dasharray="3 5" marker-end="url(#ec4c)"/><rect x="92" y="282" width="736" height="70" rx="12" fill="#101b29" stroke="#405773"/><text x="460" y="308" class="t">Condition essentielle</text><text x="460" y="331" class="s">Les pairs doivent coopérer via une technologie compatible ; LACP seul ne crée pas un switch logique à deux châssis.</text><path d="M200 242V272" stroke="#7b9ab8" stroke-width="1.5" stroke-dasharray="4 5" fill="none"/><path d="M720 242V272" stroke="#7b9ab8" stroke-width="1.5" stroke-dasharray="4 5" fill="none"/></svg></div>

### 5.2 Les familles d’implémentation

- **Cisco vPC** : permet à un équipement en aval de former un agrégat vers deux switches Nexus membres d’un domaine vPC. Les rôles, peer-link, mécanisme de keepalive, compatibilité des paramètres et comportements de partition doivent être vérifiés dans le guide correspondant à la version NX-OS.
- **Arista MLAG** : permet également une agrégation vers deux switches en paire MLAG. Le peer-link, les VLAN, les rôles et les conditions de split-brain font partie du plan de conception.
- **HPE Aruba VSX** : architecture de paire conçue pour une coordination entre deux châssis. La topologie inter-switch, la synchronisation, les paramètres et les comportements diffèrent de vPC et MLAG.
- **Juniper MC-LAG** : un ensemble de fonctions multichâssis qui exige des paramètres cohérents, notamment l’identité système et les états de redondance suivant la solution retenue. Juniper propose aussi d’autres architectures de multihoming, dont EVPN.
- **EVPN multihoming** : utilise BGP EVPN et l’identifiant Ethernet Segment (ESI) pour annoncer le multihoming d’un segment. Ce n’est pas interchangeable avec une configuration MC-LAG classique ; la conception, le split-horizon et la convergence suivent le modèle EVPN.

Ces noms ne sont pas des synonymes parfaits. Ne raccorde pas les peers de domaines multichâssis de différents constructeurs à un unique downstream LAG en supposant que vPC, MLAG et VSX sont des standards identiques. L’interopérabilité au niveau LACP entre un serveur et un système de commutation est un sujet distinct de la coordination entre les switches pairs.

### 5.3 Peer-link et keepalive

Le **peer-link** ou lien de synchronisation transporte les informations nécessaires à la coordination et, selon l’architecture, certains flux de données. Le **keepalive** sert à déterminer si le pair est joignable via un chemin indépendant. Il ne faut pas concevoir le keepalive comme un remplacement du peer-link ou inversement.

En cas de perte du peer-link, les deux switches peuvent se retrouver avec des vues divergentes de l’état du domaine. Le comportement de protection dépend de l’implémentation et de ses politiques : un côté peut suspendre certains membres, certains VLAN ou un port-channel. Comprends et teste ce scénario avant mise en service.

### 5.4 Single-homed vs dual-homed

Une agrégation de plusieurs liens entre un serveur et un seul switch améliore la résilience au défaut d’un câble/port mais pas à la perte complète du switch. Deux switches sans multichâssis peuvent offrir une haute disponibilité par active/standby au niveau de l’hôte, mais ce n’est pas équivalent à un seul LAG actif réparti vers les deux châssis. Choisis explicitement l’objectif : capacité, redondance de lien, redondance de châssis, ou maintien de session de bout en bout.

### 5.5 Split-brain et rôle du plan de contrôle

Le split-brain survient quand les composants d’un domaine redondant ne peuvent plus se coordonner et peuvent croire que l’autre a disparu. Un défaut de lien entre pairs, combiné à une perte ou un défaut de keepalive, peut être particulièrement risqué. Le résultat dépend de l’architecture, des priorités, du fencing et des politiques de suspension.

Les tests de résilience doivent considérer :

- perte d’un lien membre ;
- perte d’un module/line card ou d’un groupe de ports ;
- perte d’un peer-link ;
- perte du keepalive avec peer-link sain ;
- partition plus complexe où les deux plans de contrôle perdent des informations ;
- redémarrage, switchover, mise à niveau ou remplacement d’un pair ;
- récupération du peer-link et réconciliation de l’état.

La validation doit mesurer les pertes et les temps de convergence vus par les applications. Une sortie CLI « healthy » ne remplace pas une mesure de trafic et un test de service.

## 6. Défaillances, convergence et comportements de repli

### 6.1 Le lien physique est up, mais le membre n’est pas sélectionné

Causes fréquentes : le LACP n’est pas configuré des deux côtés, les deux côtés sont passifs, les ports sont rattachés au mauvais groupe, le System ID vu n’est pas celui attendu, paramètres L2 différents, mode access/trunk incohérent, vitesse/fonction PHY incompatible, limite de membres atteinte, port suspendu par une protection, ou membre en standby parce qu’une limite active est configurée.

Démarche : identifier l’interface logique attendue, afficher le statut LACP sur les deux extrémités, vérifier actor/partner System ID et état, inspecter les causes de suspension, puis comparer les paramètres du port physique avec le modèle de configuration de l’agrégat. N’écrase pas la configuration à l’aveugle ; recueille d’abord les sorties de référence.

### 6.2 Panne brutale d’un membre

Quand la perte est détectée, le membre défaillant est retiré de la distribution. Les flux qui lui étaient affectés sont remappés vers les membres encore admissibles. Certains paquets peuvent être perdus ou réordonnés durant la transition ; les sessions TCP se rétablissent parfois, mais l’application peut voir un timeout. La perturbation dépend du mécanisme de détection, du volume, du hachage, des buffers, de la convergence et du nombre de membres restants.

### Schéma 6 — État du membre et comportement lors d’une panne

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 350" role="img" aria-label="Machine à états simplifiée : lien physique, négociation LACP, membre sélectionné et distribution; lors d'une panne le membre est retiré, les flux sont remappés et l'agrégat demeure actif si des membres restent disponibles."><defs><marker id="ec5a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec5b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker><marker id="ec5c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ff8d91"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:11.5px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.3;marker-end:url(#ec5a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.3;marker-end:url(#ec5b)}.c{fill:none;stroke:#ff8d91;stroke-width:2.3;marker-end:url(#ec5c)}.flow{stroke-dasharray:8 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="20" y="55" width="155" height="66" rx="10" fill="#142b42" stroke="#66d9ff"/><text x="97" y="80" class="t">Lien up</text><text x="97" y="102" class="s">Signal physique OK</text><rect x="212" y="55" width="155" height="66" rx="10" fill="#33291b" stroke="#ffca72"/><text x="289" y="80" class="t">LACP échange</text><text x="289" y="102" class="s">Actif / passif</text><rect x="404" y="55" width="155" height="66" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="481" y="80" class="t">Membre choisi</text><text x="481" y="102" class="s">Synchronized / Collecting</text><rect x="596" y="55" width="155" height="66" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="673" y="80" class="t">Trafic actif</text><text x="673" y="102" class="s">Hashing</text><path d="M175 88H207" class="a flow" marker-end="url(#ec5a)"/><path d="M367 88H399" class="a flow" marker-end="url(#ec5a)"/><path d="M559 88H591" class="b flow" marker-end="url(#ec5b)"/><rect x="388" y="210" width="205" height="70" rx="10" fill="#3a2026" stroke="#ff8d91" stroke-width="2"/><text x="490" y="238" class="t">Défaillance détectée</text><text x="490" y="259" class="s">LOS, LACP timeout, erreur locale…</text><path d="M673 121V181H490V204" class="c" marker-end="url(#ec5c)"/><rect x="655" y="210" width="225" height="70" rx="10" fill="#142b42" stroke="#66d9ff"/><text x="767" y="238" class="t">Remappage</text><text x="767" y="259" class="s">Flux redistribués vers membres restants</text><path d="M593 245H649" class="a flow" marker-end="url(#ec5a)"/><rect x="34" y="210" width="270" height="70" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="169" y="238" class="t">Port-Channel reste up*</text><text x="169" y="259" class="s">Si min-links et membres restants l’autorisent</text><path d="M388 245H310" class="b" marker-end="url(#ec5b)"/><text x="460" y="321" class="s">*La convergence, les pertes brèves et la capacité restante dépendent de la plateforme, des timers et du trafic.</text></svg></div>

### 6.3 Panne silencieuse du plan de données

Une panne du forwarding peut laisser l’interface physique et LACP actifs. Exemples : une erreur de VLAN sur un chemin, un ACL erroné, une carte de ligne qui ne transmet pas correctement, une asymétrie de filtre ou un problème de matériel. LACP n’étant pas un test de service de bout en bout, les membres peuvent rester sélectionnés.

Pour détecter ce type de panne, combine des tests de flux synthétiques, le monitoring de drops/CRC/queue, la supervision des VLAN, les compteurs par port, la capture aux extrémités et, si disponible, un mécanisme d’OAM. Définis l’alerte à partir du symptôme réel, pas uniquement de l’état de lien.

### 6.4 Fast LACP et convergence

Le réglage des timers implique un compromis. Une détection plus rapide peut limiter la durée pendant laquelle un membre non joignable demeure dans la distribution, mais elle augmente le nombre de messages de contrôle et peut rendre plus visibles des pertes transitoires de LACPDU. Les détails d’interopérabilité entre fournisseurs doivent être confirmés dans la documentation de chacun.

Il faut différencier :

- délai de détection physique (LOS, link down) ;
- délai de détection de perte des LACPDU ;
- délai de propagation de l’état dans le système et la table de distribution ;
- délai de convergence de STP, du routage, d’ARP/ND et des applications ;
- temps nécessaire au flux pour reprendre après un remappage.

Mesure la durée entre l’événement injecté et le rétablissement du service. Une commande de timer rapide ne garantit pas un rétablissement applicatif sub-seconde.

### 6.5 LACP fallback, standalone et ports suspendus

Certaines plateformes possèdent des fonctions de fallback ou de comportement individual/standalone lorsque LACP n’est pas encore négocié ou lorsque le partenaire attendu n’est pas là. Elles peuvent être utiles pour des mécanismes de démarrage réseau, mais aussi ouvrir un risque de forwarding inattendu si un lien isolé commence à transmettre.

Avant d’activer un mode fallback : vérifier sa définition précise, les conditions d’entrée/de sortie, la VLAN ou le profil appliqué, la manière dont le port rejoint ultérieurement le LAG, et l’effet sur STP, la sécurité des ports, DHCP et PXE. N’assume pas que les modes fallback de deux fournisseurs se comportent identiquement.

### 6.6 Min-links et politique de dégradation

Il y a deux choix légitimes selon le service : rester `up` avec un nombre réduit de membres et fonctionner à capacité dégradée, ou faire tomber le LAG si la capacité devient insuffisante pour offrir un service acceptable. Le deuxième choix peut forcer une bascule de niveau supérieur, mais il peut aussi couper un trafic qui aurait continué à fonctionner.

Il faut définir le comportement attendu avec l’application et l’architecture. Documente : seuil, alarmes, comportement de routage/STP, dépendances et temps de reprise. Teste au moins un scénario sous le seuil et un scénario au-dessus du seuil.

## 7. Configurations de référence et pratiques multiconstructeurs

### 7.1 Exemple Cisco IOS XE — L2 EtherChannel LACP

Exemple de principe, à adapter au modèle et à la version. Le switch distant doit disposer d’un agrégat compatible, et les ports physiques doivent être propres ou préparés avant leur appartenance au channel.

```text
interface range GigabitEthernet1/0/1-2
 description Uplink-LAG-LAB
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 channel-group 10 mode active
 no shutdown
!
interface Port-channel10
 description Uplink-LAG-LAB
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
!
end
```

Bonnes pratiques : vérifier l’alignement VLAN sur port-channel et membres selon les règles de la plateforme ; appliquer les paramètres de L2 au port logique là où c’est requis ; confirmer que les deux membres ont le même état de vitesse/duplex ; utiliser `show etherchannel summary`, les commandes LACP et l’état interface pour voir les membres sélectionnés. La configuration réelle dépend du type de switch et du train IOS XE.

### 7.2 Exemple Cisco IOS XE — L3 EtherChannel

```text
interface range TenGigabitEthernet1/0/1-2
 description Routed-LAG-LAB
 no switchport
 channel-group 20 mode active
 no shutdown
!
interface Port-channel20
 description Routed-LAG-LAB
 no switchport
 ip address 192.0.2.1 255.255.255.252
 no shutdown
```

Cette illustration montre le modèle logique habituel : l’adresse IP est portée par le port-channel. Sur la plateforme cible, confirme le support, l’ordre de migration et les implications du protocole de routage. Ne transpose pas ce snippet à un switch où les noms d’interfaces, la syntaxe L3 ou les restrictions de matériel diffèrent.

### 7.3 Exemple Arista EOS — LACP

```text
interface Ethernet1
   description Uplink-to-peer-1
   channel-group 10 mode active
!
interface Ethernet2
   description Uplink-to-peer-2
   channel-group 10 mode active
!
interface Port-Channel10
   description Uplink-LAG-LAB
   switchport mode trunk
   switchport trunk allowed vlan 10,20,30
```

Vérifie la syntaxe exacte avec la version EOS et les capacités du matériel. Les commandes d’observation usuelles incluent les sorties de résumé des port-channels, d’état LACP et les compteurs d’interfaces ; le hachage et certaines fonctions de fallback ont leurs propres options selon la version.

### 7.4 Exemple Juniper Junos — Aggregated Ethernet

Illustration simplifiée pour un agrégat L2. Les ports membres doivent être rattachés au nombre de liens agrégés supporté par le matériel et la configuration de l’interface logique doit être alignée à l’objectif du service.

```text
set chassis aggregated-devices ethernet device-count 1
set interfaces ge-0/0/0 ether-options 802.3ad ae0
set interfaces ge-0/0/1 ether-options 802.3ad ae0
set interfaces ae0 aggregated-ether-options lacp active
set interfaces ae0 unit 0 family ethernet-switching interface-mode trunk
set interfaces ae0 unit 0 family ethernet-switching vlan members [ VLAN10 VLAN20 VLAN30 ]
```

Selon la plateforme et le type de configuration, les noms de famille, le style `set` ou bloc, l’assignation VLAN, et la prise en charge L2/L3 varient. Utilise `show lacp interfaces`, `show interfaces ae0 extensive` et la documentation Junos associée.

### 7.5 Exemple Aruba CX — LAG LACP

Exemple de structure, à ajuster selon la version AOS-CX et le mode de configuration du port :

```text
interface lag 10
    description Uplink-LAG-LAB
    no shutdown
    no routing
    vlan trunk allowed 10,20,30
    lacp mode active
!
interface 1/1/1
    no shutdown
    lag 10
!
interface 1/1/2
    no shutdown
    lag 10
```

Vérifier dans le guide de la version si des options complémentaires, notamment la vitesse, la description, la native VLAN, le type de port ou les contraintes de membres, sont nécessaires. Dans AOS-CX, des commandes d’interface peuvent remplacer des attributs incompatibles ; lis les avertissements et contrôles avant d’appliquer une configuration à grande échelle.

### 7.6 Exemple Linux bonding — mode 802.3ad

L’extrait suivant illustre les éléments du mode de bonding LACP, pas un fichier réseau complet valable sur toutes les distributions :

```text
# Exemple de paramètres exposés par le driver bonding
mode=802.3ad
miimon=100
lacp_rate=fast
xmit_hash_policy=layer3+4
```

Le chargement et l’application diffèrent selon NetworkManager, systemd-networkd, Netplan, scripts réseau ou configuration du noyau. Confirme dans la documentation du driver bonding que la clé de hachage est supportée et comprise pour la version utilisée. `miimon` mesure le lien physique via le mécanisme pris en charge ; ce n’est pas à lui seul un test applicatif ni un remplacement universel des signaux LACP.

Inspection courante :

```bash
cat /proc/net/bonding/bond0
ip -d link show bond0
ip -s link show bond0
ethtool eth0
```

L’état `/proc/net/bonding/bond0` peut exposer le mode, les interfaces esclaves, l’état MII, l’état agrégateur et les informations de partenaire. Conserve les sorties des interfaces physiques et de l’agrégat dans le même intervalle temporel.

### 7.7 Matrice de validation interconstructeur

| Contrôle | Extrémité A | Extrémité B | Critère de réussite |
|---|---|---|---|
| Physique | lien, vitesse, FEC, CRC | mêmes informations | tous les membres concernés sont stables, sans erreur anormale |
| LACP | actor/partner, état, key | partner correspond aux bons ports | membres attendus synchronisés, actifs et en collecte/distribution |
| Agrégat | statut interface logique | statut de l’interface logique distante | états cohérents et nombre de membres attendu |
| L2 | VLAN, native, MTU | VLAN, native, MTU | mêmes conventions de service sur le chemin |
| L3 | IP, ARP/ND, routes | IP, ARP/ND, routes | voisinage et acheminement aller-retour fonctionnels |
| Hachage | compteurs par membre | compteurs par membre | distribution acceptable pour le profil de trafic |
| Résilience | perte de membre simulée | observation correspondante | service maintenu selon les critères et capacité approuvés |
| Exploitation | alarmes/logs | alarmes/logs | panne et restauration visibles, actions documentées |

## 8. Dépannage expert

### 8.1 Préserver l’état avant de changer quelque chose

Avant d’exécuter `shutdown`, de retirer des ports du LAG ou de modifier un hash, relève : date/heure, topologie, membres attendus, état de chaque port, état LACP, compteurs et logs, paramètres du logical interface, nombre actif de membres, débit par membre, erreurs et impact utilisateur. Une capture LACP est utile lorsque le partenaire reste inconnu ou lorsque les états divergent.

Le premier objectif est de réduire le nombre d’hypothèses tout en évitant d’aggraver la panne. Ne déplace pas plusieurs membres en même temps : tu pourrais faire tomber le LAG sous `min-links` ou créer une partition d’architecture.

### 8.2 Arbre de décision de dépannage

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390" role="img" aria-label="Arbre de dépannage : l'agrégat est-il up? Sinon inspecter physique et LACP; s'il est up mais dégradé, inspecter membres, erreurs, hash, VLAN, MTU, MLAG, min-links, compteurs et capture LACP."><defs><marker id="ec6a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec6b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:11.5px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.4;marker-end:url(#ec6a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.4;marker-end:url(#ec6b)}.flow{stroke-dasharray:8 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="300" y="18" width="320" height="58" rx="10" fill="#142b42" stroke="#66d9ff" stroke-width="2"/><text x="460" y="42" class="t">Symptôme : agrégat en panne ou lent</text><text x="460" y="61" class="s">Définir impact, heure, direction et ports concernés</text><rect x="44" y="132" width="365" height="70" rx="10" fill="#33291b" stroke="#ffca72"/><text x="226" y="159" class="t">Agrégat down ?</text><text x="226" y="181" class="s">Lien physique · LACP · compatibilité · min-links</text><rect x="511" y="132" width="365" height="70" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="694" y="159" class="t">Agrégat up, mais problème ?</text><text x="694" y="181" class="s">Débit · perte · latence · flux inégalement répartis</text><path d="M405 76L230 126" class="a" marker-end="url(#ec6a)"/><text x="302" y="99" class="s">Oui / down</text><path d="M515 76L688 126" class="b" marker-end="url(#ec6b)"/><text x="620" y="99" class="s">Non / up</text><rect x="20" y="254" width="425" height="89" rx="10" fill="#101b29" stroke="#405773"/><text x="232" y="278" class="t">Contrôles côté agrégat</text><text x="232" y="300" class="s">État actor/partner · system ID/key · selected ports</text><text x="232" y="319" class="s">VLAN/trunk · speed/MTU · err-disable · câblage</text><rect x="475" y="254" width="425" height="89" rx="10" fill="#101b29" stroke="#405773"/><text x="687" y="278" class="t">Contrôles de performance</text><text x="687" y="300" class="s">Compteurs par membre · drops/CRC · hash · microbursts</text><text x="687" y="319" class="s">MLAG/peer-link · direction retour · congestion</text><path d="M226 202V248" class="a flow" marker-end="url(#ec6a)"/><path d="M694 202V248" class="b flow" marker-end="url(#ec6b)"/><text x="460" y="372" class="s">Ne pas modifier les deux extrémités simultanément avant d’avoir capturé l’état et les compteurs.</text></svg></div>

### 8.3 LAG down : checklist d’investigation

1. **Vérifier l’interface logique** sur les deux extrémités : statut administratif/opérationnel, logs récents et membres associés.
2. **Vérifier chaque membre physique** : lien, vitesse, FEC, erreurs, transceiver, câblage et configuration.
3. **Vérifier LACP** : actif/passif, System ID reçu, clés, port ID, état synchronisé, collecte/distribution, membre sélectionné ou suspendu.
4. **Comparer l’interface logique** : mode L2/L3, VLAN, native VLAN, MTU, paramètres routés, policy et restrictions de plateforme.
5. **Vérifier les limites** : nombre maximal de membres, nombre maximal actif, `min-links`, standby, member priority ou protection de port.
6. **Si multi-châssis** : état peer-link/keepalive, compatibilité des deux peers, cohérence des VLAN, rôle de domaine et conditions split-brain.
7. **Valider la donnée utilisateur** : trafic dans les deux sens, apprentissage MAC/ARP/ND, routage, ping avec tailles adaptées et test applicatif.

### 8.4 Agrégat up mais débit mauvais

Le LAG logique peut être opérationnel tout en ayant une ou plusieurs interfaces physiques qui ne transmettent pas utilement le trafic. Compare les compteurs par membre : débit, erreurs CRC, drops, collisions si la technologie les expose, pauses, discard de queue, taux de paquets, erreurs de FEC et utilisation de chaque sens. Un seul membre presque saturé avec trois membres très bas peut être compatible avec le hachage et un faible nombre de flux.

Teste avec plus de flux, puis compare la distribution. Vérifie également les champs de hash configurés de part et d’autre : la direction du trafic sur chaque équipement n’utilise pas forcément les mêmes informations. Si les queues se remplissent sur un seul membre, un changement de hash ou de topologie doit faire l’objet d’un test limité et d’un plan de retour arrière.

### 8.5 VLAN manquante, perte sélective ou MTU

Si seules certaines applications échouent, ne présume pas immédiatement d’un défaut LACP. Vérifie le VLAN où le flux est censé circuler, les tags observés, la VLAN native, STP, la table MAC, les ACL et les politiques de sécurité. Pour un symptôme de paquets volumineux bloqués, compare MTU L2/L3, MSS, fragmentation/PMTUD et taille réellement capturée. Une MTU cohérente sur le port-channel doit aussi être cohérente sur les éléments de chemin nécessaires.

### 8.6 Capturer et lire LACP

LACP utilise des trames Slow Protocols. Une capture Ethernet peut identifier le protocole via EtherType `0x8809` et la destination réservée `01:80:C2:00:00:02` sur un segment Ethernet approprié. Les comportements de capture dépendent du point d’observation, des règles de commutation et des limites de capture ; le fait de ne pas voir une trame sur un port SPAN n’établit pas à lui seul que le pair n’en émet pas.

Utilise un port miroir ou une capture locale autorisée, filtre les échanges LACP disponibles, et compare les trames émises dans les deux sens. Les détails de dissecteur et de filtre Wireshark peuvent changer selon la version, donc confirme la syntaxe dans la documentation installée. En plus du PCAP, garde la sortie des commandes d’état ; le paquet montre ce qui a été échangé, la CLI peut montrer comment la plateforme a interprété l’état.

### 8.7 Ne pas se laisser tromper par les compteurs cumulés

Un compteur d’erreurs qui augmente depuis des semaines ne prouve pas que l’incident courant provient de ce port. Collecte deux snapshots avec un intervalle connu, calcule le delta et compare à la quantité de trafic. Documente tout effacement de compteurs et les changements d’interface, car ils changent le contexte d’interprétation.

### 8.8 Procédure de dépannage en production

- Définir l’impact : quel service, quel sens, quels VLAN/VRF, quels clients ?
- Vérifier le service depuis un point de vue utilisateur et relever l’heure exacte.
- Collecter état logique, état LACP, membres actifs, logs et compteurs par membre des deux côtés.
- Comparer les sorties et repérer le premier point de divergence observable.
- Formuler une hypothèse qui prédit un résultat mesurable.
- Effectuer un test ciblé et réversible, idéalement sur un flux ou un membre non critique.
- Vérifier si la mesure attendue s’est produite et si l’impact a changé.
- Ne généraliser la correction qu’après validation et sauvegarder l’état final.

## 9. Opérations, changements et migrations

### 9.1 Avant le changement

- Confirmer le propriétaire du service, les dépendances et la fenêtre autorisée.
- Exporter la configuration des deux extrémités et de la paire multichâssis.
- Établir un état de référence : membres, débit, drops, latence, alarmes, sessions et tests applicatifs.
- Préparer le contrat de configuration et vérifier la compatibilité matérielle/logicielle.
- Vérifier la capacité restante si un ou plusieurs liens doivent être déplacés ou arrêtés.
- Établir les critères d’abandon : perte de membre, erreur croissante, VLAN absent, perte de sessions, dégradation SLO ou non-respect du temps prévu.
- Préparer une configuration de retour arrière et identifier le chemin de management hors bande.

### 9.2 Migration d’un LAG existant

La bonne séquence dépend de l’état initial et du support de la plateforme. En règle générale, planifie une transition contrôlée plutôt qu’un basculement simultané de toutes les interfaces :

1. créer l’interface logique, si possible sans perturber les liens existants ;
2. configurer les deux extrémités avec un profil compatible ;
3. déplacer ou ajouter un membre de manière contrôlée ;
4. confirmer la sélection LACP, l’état L2/L3 et la distribution ;
5. déplacer le membre suivant seulement si les critères de test passent ;
6. réaliser des tests applicatifs et vérifier les compteurs ;
7. mettre à jour la documentation et sauvegarder les configs.

Si la plateforme ne permet pas de créer l’agrégat sans migrer les liens existants, la fenêtre peut exiger une coupure explicite. Ne promets pas une migration sans coupure avant d’avoir confirmé les mécanismes de coexistence de l’ancienne et nouvelle configuration.

### Schéma 7 — Migration contrôlée et rollback

<div class="ec-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 340" role="img" aria-label="Séquence de migration sécurisée : inventaire et sauvegarde, créer l'agrégat logique des deux côtés, vérifier membres/LACP, migrer un lien à la fois, valider les flux puis documenter; une branche rollback protège le service."><defs><marker id="ec7a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="ec7b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#75e6b0"/></marker><marker id="ec7c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ff8d91"/></marker></defs><style>.t{font:600 13px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:11px system-ui,sans-serif;fill:#bdcce0;text-anchor:middle}.a{fill:none;stroke:#66d9ff;stroke-width:2.3;marker-end:url(#ec7a)}.b{fill:none;stroke:#75e6b0;stroke-width:2.3;marker-end:url(#ec7b)}.c{fill:none;stroke:#ff8d91;stroke-width:2.3;marker-end:url(#ec7c)}.flow{stroke-dasharray:8 7;animation:ecDash 2.3s linear infinite}@keyframes ecDash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="20" y="46" width="160" height="76" rx="10" fill="#142b42" stroke="#66d9ff"/><text x="100" y="72" class="t">1. Préparer</text><text x="100" y="94" class="s">Inventaire / sauvegarde</text><text x="100" y="109" class="s">Fenêtre / rollback</text><rect x="206" y="46" width="160" height="76" rx="10" fill="#142b42" stroke="#66d9ff"/><text x="286" y="72" class="t">2. Préconfigurer</text><text x="286" y="94" class="s">LAG aux deux bouts</text><text x="286" y="109" class="s">Sans déplacer tout le trafic</text><rect x="392" y="46" width="160" height="76" rx="10" fill="#33291b" stroke="#ffca72"/><text x="472" y="72" class="t">3. Tester LACP</text><text x="472" y="94" class="s">1 membre test si possible</text><text x="472" y="109" class="s">VLAN / MTU / état</text><rect x="578" y="46" width="160" height="76" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="658" y="72" class="t">4. Migrer</text><text x="658" y="94" class="s">Un lien à la fois</text><text x="658" y="109" class="s">Observer la capacité</text><rect x="764" y="46" width="136" height="76" rx="10" fill="#16372d" stroke="#75e6b0"/><text x="832" y="72" class="t">5. Valider</text><text x="832" y="94" class="s">Tests bidirectionnels</text><text x="832" y="109" class="s">Journal / clôture</text><path d="M180 84H201" class="a flow" marker-end="url(#ec7a)"/><path d="M366 84H387" class="a flow" marker-end="url(#ec7a)"/><path d="M552 84H573" class="a flow" marker-end="url(#ec7a)"/><path d="M738 84H759" class="b flow" marker-end="url(#ec7b)"/><rect x="170" y="208" width="580" height="76" rx="12" fill="#3a2026" stroke="#ff8d91" stroke-width="2"/><text x="460" y="235" class="t">Critère de rollback</text><text x="460" y="257" class="s">Membre non sélectionné, perte/erreurs anormales, VLAN manquant,</text><text x="460" y="273" class="s">dégradation SLO ou risque de capacité insuffisante</text><path d="M472 122V170H460V202" class="c" marker-end="url(#ec7c)"/><text x="460" y="316" class="s">Rollback préparé avant changement : restaurer la configuration connue et contrôler le service, pas uniquement le lien.</text></svg></div>

### 9.3 Changer le hachage en production

Une modification du hash peut remapper un grand nombre de flux. Les impacts possibles incluent des microcoupures, une réorganisation ponctuelle des paquets, une redistribution brutale des queues, ou une amélioration inattendue d’un groupe mais une régression d’un autre. Avant le changement, enregistre les membres actifs et la distribution des flux ; après le changement, vérifie immédiatement la latence, les pertes, la répartition et les sessions applicatives.

Prévois un retour arrière vers l’algorithme précédent. Si tu ne peux pas mesurer le trafic par membre, ne considère pas la modification comme validée uniquement parce que la commande est acceptée.

### 9.4 Ajouter des membres ou changer de vitesse

L’ajout augmente le nombre de buckets possibles et peut déplacer les flux. Assure-toi que le châssis, le module, les ports, le transceiver, la version logicielle et la licence éventuelle supportent le débit souhaité. Lors d’un passage 10G à 25G ou 40G, vérifier les modes de breakout et la FEC est souvent aussi important que la configuration logique.

Ne suppose pas que deux membres de vitesse différente sont agrégés de manière proportionnelle. Certaines plates-formes exigent des vitesses identiques dans un même groupe, d’autres ont des restrictions précises. Quand des liens de vitesse différente sont autorisés, l’algorithme peut quand même répartir les flux sans tenir parfaitement compte de la capacité effective. Consulte les restrictions du produit et fais des tests.

### 9.5 Mise à niveau logicielle et firmware

Avant upgrade d’un domaine de commutation ou d’un serveur, vérifie les notes de version : interopérabilité LACP, stabilité du driver, bugs du hash, comportement des membres standby, limitations de MLAG, et changements de configuration. Mets à jour un pair ou une extrémité à la fois si l’architecture le permet, suis le scénario officiel de mise à niveau et prévois la restauration ou la bascule attendue.

Pour les serveurs, les pilotes de cartes, le firmware NIC, les modules du noyau et les configurations réseau doivent être considérés ensemble. Un changement de driver peut changer le comportement de bonding ou les champs de hash. L’étape de validation doit être la même que celle utilisée pour le réseau : status, compteurs, tests de service et observation en cas de membre absent.

### 9.6 Journal de changement — modèle réutilisable

```text
CHANGEMENT : CHG-____
Service / hôtes concernés :
Topologie et interfaces :
Objectif métier :
État avant changement (membres, trafic, erreurs, tests) :
Risques connus :
Préconditions et validations :
Étapes numérotées :
Critères de réussite mesurables :
Critères de rollback :
Procédure de rollback :
Personne de décision / personne d’exécution :
Heure début / heure fin :
Résultats observés :
Écart / anomalie :
Configuration finale sauvegardée : oui / non
Suivi requis :
```

## 10. Supervision et indicateurs de service

Une supervision adaptée distingue l’état du port logique du bon fonctionnement du service. Au minimum, collecte :

- statut de l’interface logique ;
- nombre de membres sélectionnés / actifs / standby ;
- état LACP actor/partner et changements de partenaire ;
- transitions et flap des interfaces physiques ;
- erreurs physiques, CRC, FEC, drops et erreurs de queue ;
- débit et paquets par membre dans les deux sens ;
- état du peer-link et des keepalives en MLAG/VSX/vPC/MC-LAG ;
- échecs des tests synthétiques et latence service ;
- configuration attendue comparée à la configuration active.

Exemples de règles : alerte lorsque le nombre de membres diminue, seuil sur la capacité résiduelle, alarme si le LAG se retrouve sous le niveau conçu, détection de flap, différentiel d’erreurs physique, perte de heartbeat multichâssis et test utilisateur en échec. Les seuils doivent être adaptés au profil de service ; une valeur universelle serait trompeuse.

Un tableau de bord ne devrait pas seulement afficher “LAG up”. Il doit permettre de répondre en moins d’une minute à : combien de membres fonctionnent, sont-ils les bons, quel membre est chargé, y a-t-il des erreurs, le pair redondant est-il sain, et l’application est-elle joignable ?

## 11. Sécurité et stabilité opérationnelle

### 11.1 Limiter les effets de bord

- Ne pas agréger des interfaces qui aboutissent à des domaines de panne différents sans une architecture multi-châssis supportée.
- Désactiver les ports inutilisés et documenter chaque membre prévu.
- Contrôler les VLAN autorisées et éviter de propager inutilement les VLAN de management ou de stockage.
- Appliquer les mêmes politiques de sécurité et de filtrage à l’interface logique et aux membres selon les règles de la plateforme.
- Protéger les canaux de management et contrôler les permissions des comptes réseau.
- Surveiller les changements de System ID, de partner et les membres inconnus.
- Éviter les modes fallback/standalone non documentés sur les liens de production.

### 11.2 Boucles et STP

Un EtherChannel L2 correctement formé est généralement vu comme un lien logique par STP, mais un mauvais montage, une configuration statique incohérente ou un état partiellement actif peut créer des chemins inattendus. Ne désactive pas STP pour « faire fonctionner le port-channel ». Il faut résoudre la cause : VLAN mismatch, membres incompatibles, mauvais câblage, ou architecture multichâssis incomplète.

### 11.3 Gestion de la donnée de capture

Les captures LACP peuvent révéler les adresses MAC d’infrastructure, la topologie et des détails de configuration. Les captures générales des interfaces peuvent aussi contenir les communications métier. Stocke les artefacts de diagnostic avec accès limité, durée de conservation définie et suppression contrôlée.

## 12. Laboratoires guidés

### Laboratoire A — Hôte Linux vers switch multiconstructeur

**Contexte :** serveur Linux à deux interfaces 10G reliées à un switch, avec un LAG LACP. Le serveur doit communiquer sur plusieurs VLANs via un trunk.

**Objectifs :** créer le bonding 802.3ad, vérifier l’état LACP, valider le trunk et mesurer les compteurs par membre.

**Procédure :**

1. Inventorier les interfaces et vérifier vitesse, FEC, erreurs et drivers.
2. Définir côté switch l’interface logique et le profil trunk attendu.
3. Créer le bonding selon la distribution Linux, puis attacher les interfaces physiques.
4. Vérifier `cat /proc/net/bonding/bond0`, `ip -d link` et l’état du port-channel.
5. Vérifier que l’actor Linux voit le partenaire prévu et que les deux membres sont actifs.
6. Tester une adresse de chaque VLAN autorisée, puis valider la route aller-retour.
7. Générer plusieurs flux et relever les compteurs pour chaque membre.
8. Couper un membre de test, vérifier le maintien de service et mesurer les pertes/convergence.
9. Remettre le membre en service et observer la redistribution.

**Critères de réussite :** membres attendus sélectionnés, VLAN cohérentes, aucune erreur nouvelle non expliquée, service opérationnel et rapport de tests documenté.

### Laboratoire B — Deux switches en MLAG

**Contexte :** un serveur a deux liens connectés à deux switches en paire multi-châssis. Le serveur doit voir une seule agrégation logique.

**Précautions :** réaliser ce laboratoire sur du matériel et des versions officiellement compatibles. Ne remplace pas la technologie du constructeur par un « MLAG générique ».

**Tests à exécuter :**

1. contrôler l’état des pairs, du peer-link et du mécanisme de keepalive ;
2. valider le LAG du serveur et les états LACP des ports aux deux switches ;
3. tester le trafic bidirectionnel ;
4. couper un membre côté A ;
5. couper un membre côté B ;
6. interrompre le peer-link selon la procédure officielle et observer la protection attendue ;
7. vérifier le scénario keepalive indisponible avec peer-link sain ;
8. restaurer les liens et vérifier la réconciliation sans boucles ni MAC flapping.

Ne déclenche les tests peer-link/split-brain qu’en laboratoire ou dans une fenêtre autorisée avec un plan de récupération et accès hors bande.

### Laboratoire C — Mauvaise répartition de flux

**Symptôme :** Port-Channel 4 × 10G est up, mais un membre est proche de 100 % et trois autres restent sous 20 %.

**Démarche :**

1. comparer les octets/paquets et les drops par membre pendant plusieurs intervalles ;
2. confirmer si la charge correspond à un seul flux ou à plusieurs conversations ;
3. identifier les champs du hash et le nombre de tuples réellement observés ;
4. tester plusieurs sessions indépendantes, en isolant les mesures de chaque test ;
5. vérifier si la charge est concentrée au même membre sur les deux extrémités ;
6. inspecter les queues et le niveau d’ECMP en amont/aval ;
7. si nécessaire, élaborer une modification du hash contrôlée puis comparer les métriques.

**Conclusion attendue :** expliquer avec preuves si le comportement est normal pour le hash, si un champ de distribution est inadapté, si le nombre de flux est insuffisant, ou si une congestion/erreur physique intervient. Ne qualifie pas le hachage de « mauvais » sans données suffisantes.

### Laboratoire D — Pas de LACP malgré des liens up

**Contexte :** deux interfaces Ethernet ont leur signal physique, mais aucun membre n’est sélectionné.

**Hypothèses :** configuration LACP absente sur un côté, passive/passive, mauvais port-channel, mauvais System ID, paramètres de membre incompatibles, vitesse/duplex/FEC ou limite matérielle.

**Ordre de test :** capturer l’état CLI des deux côtés ; vérifier le mode LACP ; confirmer le port distant associé ; inspecter le System ID partenaire et les états ; comparer vitesse et paramètres ; vérifier si le port est suspendu ; ensuite seulement faire un changement ciblé.

**Critère de conclusion :** l’hypothèse est confirmée par une différence observable et la correction est validée par la sélection du membre et le trafic de service.

## 13. Scénarios d’incident avancés

### Scénario 1 — Le LAG reste up mais le débit chute à la moitié

Quatre liens de même capacité sont attendus ; deux deviennent non sélectionnés après une opération de maintenance. L’interface logique reste up. La première tâche n’est pas de redémarrer LACP : déterminer si le nombre de membres actifs correspond au seuil de conception, identifier la raison d’exclusion, mesurer la capacité restante et confirmer si l’application est réellement saturée. Vérifier les logs du changement et les erreurs physiques au même instant. Décider de restaurer les membres ou d’assumer temporairement l’état dégradé selon les critères préapprouvés.

### Scénario 2 — Membres actifs mais certains VLAN ne passent pas

Un trunk LACP fonctionne pour VLAN 10 mais pas pour VLAN 30. Cela indique que LACP ne suffit pas à expliquer le problème. Comparer VLAN allowed/native sur l’interface logique et les membres, STP, tables MAC, tags observés et les ACL. Vérifier les deux sens et, si le trafic traverse une paire multichâssis, confirmer la cohérence du domaine et des VLAN autorisées sur le peer-link lorsque requis.

### Scénario 3 — Flap du LAG sans perte physique évidente

Collecter les journaux des deux côtés avec les timestamps, surveiller les transitions d’état LACP, les changes de partner, les resets d’interface, erreurs et charge CPU du control plane. Vérifier si les LACPDU sont perdues, si la configuration change via automation, ou si un mécanisme de protection suspend l’interface. Évite d’allonger les timers comme première réponse : tu pourrais masquer une cause sans la corriger.

### Scénario 4 — Un seul grand transfert est lent, plusieurs petits transferts vont bien

Vérifier le débit du flux individuel par rapport au débit d’un membre. C’est compatible avec une distribution par flux. Contrôler aussi la fenêtre TCP, les pertes, le RTT, les contraintes d’application et le hachage. Le total agrégé peut être élevé parce que d’autres conversations utilisent les membres restants. Si le besoin réel est d’accélérer une seule session, évaluer les choix applicatifs ou d’architecture au lieu de promettre un débit individuel égal à la somme des liens.

### Scénario 5 — LACP forme le groupe côté hôte mais pas le côté switch attendu

Le serveur voit un System ID ou plusieurs partenaires inattendus. Vérifier si les deux câbles sont réellement raccordés au même système logique, si la paire MLAG est active, si le domaine et les interfaces sont inclus, et si le serveur utilise un mode spécial de teaming/fallback. LACP n’agrège pas des partenaires indépendants comme si le domaine multi-châssis existait.

## 14. Modèles opérationnels réutilisables

### 14.1 Fiche d’inventaire d’un LAG

```text
ID du service :
Nom de l’agrégat :
Type : L2 / L3
Technologie : LACP / statique / MLAG / EVPN multihoming
Équipement A + version :
Équipement B + version :
Pair multichâssis / domaine (si applicable) :
Membres locaux ↔ distants :
Vitesse / transceiver / FEC :
MTU attendue :
VLAN ou interface L3 :
Mode LACP / timers :
Nombre actif / min-links :
Algorithme/champs de hachage :
Débit attendu et capacité N-1 :
Tests de santé / seuils d’alerte :
Lien vers la configuration sauvegardée :
Date de dernière validation :
```

### 14.2 Checklist de mise en service

- [ ] Modèles matériels, versions et limites de membres vérifiés.
- [ ] Compatibilité transceivers, vitesse, FEC et câblage confirmée.
- [ ] Contrat neutre L2/L3 et VLAN validé sur les deux extrémités.
- [ ] LACP est activé et au moins une extrémité peut initier les échanges.
- [ ] Bons System ID/partner IDs et bons membres sélectionnés.
- [ ] Nombre de membres actifs conforme à la conception et à `min-links`.
- [ ] Compteurs physiques sans hausse anormale d’erreurs ou de drops.
- [ ] Trafic de chaque VLAN/VRF ou chaque réseau routé testé dans les deux sens.
- [ ] Répartition de charge mesurée avec un ensemble de flux représentatif.
- [ ] Test contrôlé de perte d’un membre et temps de reprise enregistrés.
- [ ] Pour MLAG/VSX/vPC/MC-LAG : états des pairs et tests de panne validés.
- [ ] Supervision, contacts, rollback et sauvegarde documentés.

### 14.3 Rapport de diagnostic

```text
INCIDENT : INC-____
Heure de début / fin :
Services et utilisateurs affectés :
Topologie (schéma ou lien) :
Symptôme observé :
État LAG et nombre de membres attendus / actifs :
État LACP actor/partner :
Compteurs et débit par membre :
Logs / captures / horodatages :
Hypothèses classées :
Tests exécutés et résultats :
Cause confirmée (avec preuve) :
Correction effectuée :
Résultat après correction :
Risque résiduel / suivi :
```

## 15. Quiz de niveau expert

**Question 1.** Deux extrémités sont en passive LACP. Pourquoi un agrégat dynamique peut-il ne pas se former ?  
**Question 2.** Avec un LAG de 4 × 10 Gb/s, un seul flux TCP atteint environ 9 Gb/s tandis que plusieurs flux atteignent une somme de 30 Gb/s. Est-ce forcément un défaut ?  
**Question 3.** Deux switches indépendants reçoivent chacun un câble du serveur. Pourquoi la configuration LACP côté serveur ne crée-t-elle pas à elle seule un LAG fiable vers les deux switches ?  
**Question 4.** Le port-channel est up mais VLAN 30 ne fonctionne pas. Quel plan d’investigation privilégier ?  
**Question 5.** Pourquoi une option LACP rapide ne résout-elle pas toujours une panne silencieuse de forwarding ?  
**Question 6.** Quel est le risque de changer le hash d’un LAG pendant une période de charge élevée ?  
**Question 7.** Quelle décision se cache derrière `min-links` et comment la justifier ?  
**Question 8.** Quelle est la différence entre peer-link et keepalive dans une architecture multichâssis ?  
**Question 9.** Quels indicateurs doivent être collectés pour prouver une répartition déséquilibrée ?  
**Question 10.** Pourquoi comparer seulement l’état “up” à chaque extrémité est-il insuffisant pour clôturer une mise en service ?

### Corrigé

1. Aucune extrémité n’initie la négociation ; au moins une doit être active pour lancer l’échange dans le modèle habituel.
2. Non. Le hash épingle généralement une conversation à un membre. L’agrégat répartit plusieurs flux, pas nécessairement un flux unique.
3. Les deux switches présentent des identités indépendantes et n’échangent pas la coordination exigée pour un agrégat multichâssis. Il faut un système logique commun, un mécanisme MLAG compatible ou une architecture multihoming conçue à cet effet.
4. Examiner trunk/native/allowed VLAN, tags, STP, table MAC, filtres, chemins aller-retour et cohérence de la paire multichâssis. LACP `up` ne valide pas la configuration VLAN.
5. Le timer accélère la détection de la perte de LACPDU, mais un plan de données défaillant peut laisser le lien et les LACPDU actifs.
6. Une grande partie des flux peut être remappée, avec pertes/réordonnancement transitoires et changements de congestion. Mesurer avant/après et préparer le rollback.
7. Le minimum de membres requis pour que le service reste déclaré disponible. Il doit refléter la capacité utile minimale et le comportement du niveau supérieur en panne.
8. Le peer-link assure la coordination et peut transporter certains flux selon l’architecture ; le keepalive sert généralement à vérifier la joignabilité du pair via un chemin distinct. Le détail dépend du fournisseur.
9. Débits et paquets par membre dans les deux sens, drops/queues/erreurs, durée d’observation, nombre de flux et profil de charge ; il faut séparer l’effet du hash d’une anomalie physique.
10. Il faut vérifier les membres sélectionnés, les VLAN ou routes, la capacité, la résilience, les compteurs, le comportement du peer et les tests de service, pas seulement l’état de lien.

## 16. Références techniques

Les commandes et options exactes doivent être vérifiées sur la version de logiciel et le modèle matériels déployés.

- **IEEE 802.1AX — Link Aggregation :** https://standards.ieee.org/ieee/802.1AX/6768/ — principe normalisé de l’agrégation de liens et révisions de la norme.
- **IEEE 802.1AX, aperçu de la révision :** https://1.ieee.org/tsn/802-1ax-rev/ — modèle de LAG, résilience et concepts du standard.
- **Cisco IOS XE, EtherChannel / LACP :** https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/etherchannel/etherchannel-configuration-guide/etherchannels.html — modes LACP et contraintes de formation de l’EtherChannel.
- **Juniper, configuration LACP sur Aggregated Ethernet :** https://www.juniper.net/documentation/us/en/software/junos/fusion-enterprise/topics/task/interfaces-configuring-aggregated-ethernet-lacp-l2.html — active/passive, actor/partner et considérations MC-LAG.
- **Juniper, interfaces Aggregated Ethernet :** https://www.juniper.net/documentation/us/en/software/junos/interfaces-ethernet/topics/topic-map/aggregated-ethernet-interfaces-lacp-configure.html — configuration et observation LACP dans Junos.
- **HPE Aruba, configuration LAG :** https://arubanetworking.hpe.com/techdocs/hpe-central/content/get-started-with-hpe-aruba-networking-central/configuring-lag.html — modes LACP, statique, VLAN et paramètres LAG.
- **Linux kernel, bonding driver :** https://docs.kernel.org/networking/bonding.html — comportement du driver bonding, modes, options et inspection.
- **Arista EOS :** consulter le guide de la version EOS déployée, sections Port-Channel, LACP, load balancing et MLAG : https://www.arista.com/en/support/product-documentation

## 17. Synthèse opérationnelle

L’expert ne traite pas EtherChannel/LACP comme une simple commande pour « multiplier le débit ». Il conçoit le groupe comme un service : sélection des membres, compatibilité L2/L3, capacité N-1, distribution des conversations, interopérabilité et comportement de panne. LACP valide un contrat de lien logique ; il ne remplace ni la validation du plan de données, ni les tests applicatifs, ni la coordination multichâssis.

La méthode robuste consiste à documenter le résultat attendu, observer les deux extrémités, regarder les membres individuellement, tester dans les deux sens, simuler les pannes autorisées, mesurer l’impact et sauvegarder une configuration connue comme saine. Le système est prêt lorsque le lien, le protocole, la capacité, le plan de données et le service métier sont tous validés — et que l’équipe sait comment revenir en arrière.
