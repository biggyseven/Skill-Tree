---
node_id: voice-cucm-debutant
title: Téléphonie IP (CUCM)
---

# Téléphonie IP avec Cisco Unified Communications Manager (CUCM)

## Objectifs
Comprendre les composants d'une solution de téléphonie IP, les objets de base de CUCM, le chemin d'un appel et les contrôles de premier niveau. Ce cours est d'introduction : les menus varient selon la version CUCM et les droits attribués.

## 1. Architecture

```text
Téléphone IP A ----                          VLAN voix / LAN
Téléphone IP B ------ Switch ---- Routeur / WAN ---- Site distant
                         |
                         +---- CUCM (call control)
                         +---- TFTP / services
                         +---- passerelle PSTN / SBC
```

CUCM fournit le contrôle d'appel : enregistrement des téléphones, numérotation, routage, fonctionnalités et politiques. Le média audio/vidéo est généralement transporté directement entre terminaux ou via des ressources média/passerelles selon la topologie. Le serveur CUCM n'est donc pas nécessairement dans le chemin RTP de chaque appel.

## 2. Concepts essentiels

- **Device / téléphone** : équipement enregistré, souvent identifié par son adresse MAC.
- **Directory Number (DN)** : numéro ou extension associé à une ligne.
- **Line appearance** : association entre une ligne et un téléphone.
- **Device Pool** : paramètres communs, notamment région, date/heure et emplacement.
- **Region** : règles de codec entre régions.
- **Location** : contrôle de bande passante pour certains appels inter-sites.
- **CSS (Calling Search Space)** : ensemble de partitions accessibles pour la numérotation.
- **Partition** : groupe logique d'objets de numérotation.
- **Route Pattern / Route List / Route Group** : objets de sélection de routes externes.
- **TFTP** : distribution de configurations et fichiers nécessaires aux téléphones.

## 3. Flux d'un appel interne

```text
Téléphone A -> CUCM : demande d'appel vers extension 2002
CUCM -> Téléphone A : autorise et indique la destination
Téléphone B <-> CUCM : sonnerie / état d'appel
Téléphone A <================> Téléphone B
                RTP audio
```

La signalisation et le média sont différents : SIP/SCCP et les messages de contrôle établissent l'appel ; RTP transporte habituellement l'audio. Un appel peut sonner sans audio si le chemin RTP, les ACL, le NAT ou les paramètres média sont incorrects.

## 4. Mise en service, démarche générale

1. Vérifier le VLAN voix, DHCP et options nécessaires au modèle de téléphone.
2. Confirmer la connectivité vers les services CUCM/TFTP et la résolution DNS si utilisée.
3. Dans l'interface d'administration, vérifier l'existence du téléphone, son adresse MAC et son Device Pool.
4. Créer ou associer une ligne (DN) et définir sa partition.
5. Configurer le CSS d'appelant et vérifier que la destination est accessible.
6. Appliquer les paramètres puis redémarrer uniquement lorsque nécessaire et selon la fenêtre de changement.
7. Vérifier l'enregistrement et passer un appel de test.

Ne pas exposer l'interface d'administration sur Internet ; utiliser des comptes nominatifs, des rôles minimaux et une gestion contrôlée des changements.

## 5. Dépannage de premier niveau

| Symptôme | Contrôles prioritaires |
|---|---|
| Téléphone non enregistré | alimentation/PoE, VLAN voix, DHCP, TFTP, réseau et certificat |
| Extension inconnue | DN, partition, CSS appelant, format de numérotation |
| Appel externe impossible | route pattern, route list/group, passerelle, restrictions |
| Appel établi sans audio | RTP, ACL/firewall, NAT, codecs et adresses média |
| Audio unidirectionnel | chemin retour, NAT/ACL, sous-réseaux et annonces SDP |

Distinguer la panne de signalisation de la panne média. Consigner l'heure, les numéros concernés, le site, le modèle de téléphone et le résultat des tests.

## 6. TP guidé

Dans un environnement de laboratoire :
1. Définir deux téléphones de test et deux extensions (1001 et 1002).
2. Vérifier leur enregistrement et leur association à la bonne ligne.
3. Vérifier que le CSS autorise l'appel entre extensions.
4. Tester l'appel, puis examiner journaux et traces si l'appel échoue.
5. Couper volontairement la route RTP dans un simulateur contrôlé et reconnaître la différence entre appel établi et audio fonctionnel.

## Exercices corrigés
1. **CUCM transporte-t-il toujours le média ?** Non, il contrôle généralement l'appel ; RTP peut circuler directement entre terminaux.
2. **Que détermine le CSS ?** Les partitions dans lesquelles le téléphone peut résoudre une destination.
3. **Le téléphone sonne mais il n'y a pas d'audio :** examiner RTP, ACL, NAT, SDP et codecs, pas seulement le DN.
4. **Le téléphone ne reçoit pas sa configuration :** vérifier VLAN voix, DHCP, TFTP et connectivité.

## Défi final corrigé
Deux extensions internes s'appellent, mais un seul côté entend l'autre. Vérifier d'abord que la signalisation est établie, puis comparer les adresses et ports annoncés dans SDP avec les flux RTP observés, inspecter les ACL/NAT dans les deux sens et confirmer la cohérence des codecs. Ne modifier la configuration qu'après avoir isolé le point de rupture.

## Glossaire et références
**CUCM** : contrôle d'appels. **DN** : numéro de répertoire. **CSS/Partition** : règles d'accès aux destinations. **RTP** : transport média. **TFTP** : transfert des fichiers de configuration.
- Cisco Unified Communications : https://www.cisco.com/c/en/us/products/unified-communications/index.html
