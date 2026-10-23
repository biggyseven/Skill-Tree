# Comprendre la VRF (Virtual Routing and Forwarding) : Niveau Débutant

Dans les réseaux informatiques traditionnels, un routeur possède **une seule table de routage**. Cela signifie que toutes les interfaces du routeur partagent les mêmes règles de navigation. 

La technologie **VRF (Virtual Routing and Forwarding)** permet de diviser un routeur physique en plusieurs routeurs virtuels indépendants.

---

## 1. L'Analogie de l'Immeuble et des Ascenseurs

Pour bien comprendre la VRF, imaginez un grand immeuble de bureaux partagé par deux entreprises concurrentes : **Entreprise A** et **Entreprise B**.

* **Sans VRF (Réseau classique) :** Il n'y a qu'un seul couloir principal et un seul ascenseur. Tout le monde se croise, et il faut installer des gardiens (des pare-feux/ACLs) à chaque porte pour s'assurer que l'Entreprise A ne rentre pas dans les bureaux de l'Entreprise B.
* **Avec VRF (Réseau virtualisé) :** L'immeuble crée deux réseaux de couloirs et d'ascenseurs totalement séparés. L'Entreprise A ne peut physique ou logiquement jamais croiser l'Entreprise B. Pour elles, c'est comme si elles occupaient deux bâtiments distincts, même si la structure en béton (le matériel du routeur) est la même.

---

## 2. Pourquoi utilise-t-on la VRF ?

### A. L'Isolation et la Sécurité
La VRF permet de séparer le trafic réseau de différents services ou clients sur le même équipement physique sans qu'ils puissent communiquer entre eux par défaut.

### B. Le Chevauchement d'Adresses IP (*Overlapping IP Addresses*)
Sans VRF, deux équipements connectés à un même routeur ne peuvent pas avoir la même adresse IP. 

Avec la VRF, comme chaque table de routage est isolée :
* Le client A peut utiliser le réseau `192.168.1.0/24` dans la **VRF_A**.
* Le client B peut utiliser le **même** réseau `192.168.1.0/24` dans la **VRF_B**.
* Le routeur ne sera pas confus, car il regarde la table de routage spécifique à chaque VRF.

```
                  ┌─────────────────────────────────┐
                  │         ROUTEUR PHYSIQUE        │
                  │                                 │
 [ Client A ] ───►│ (Interface 1)   (Interface 2)   │◄─── [ Client B ]
 IP: 192.168.1.10 │      │                │        │     IP: 192.168.1.10
                  │      ▼                ▼        │
                  │  ┌─────────┐      ┌─────────┐  │
                  │  │ Table   │      │ Table   │  │
                  │  │ Routage │      │ Routage │  │
                  │  │  VRF A  │      │  VRF B  │  │
                  │  └─────────┘      └─────────┘  │
                  └─────────────────────────────────┘
```

---

## 3. Les Cas d'Usage Principaux

1. **Les Opérateurs Télécoms (Fournisseurs d'Accès) :**
   Permet d'interconnecter les différents sites d'un client entreprise via un réseau privé virtuel (MPLS VPN) en garantissant l'isolation par rapport aux autres clients.
2. **Les Réseaux d'Entreprise (Corporate Networks) :**
   Séparer le réseau des **Invités (Guest)**, le réseau de la **Comptabilité** et le réseau des **Caméras de Surveillance (IoT/CCTV)**.
3. **L'Administration des Équipements (Management VRF) :**
   Isoler le flux de gestion des routeurs/switchs (SSH, SNMP, Syslog) du trafic des utilisateurs pour éviter les attaques.

---

## 4. Aperçu d'une Configuration de Base (Cisco IOS)

Créer et assigner une VRF se fait en deux étapes simples :

### Étape 1 : Créer la VRF
```text
Router(config)# ip vrf CLIENT_A
```

### Étape 2 : Assigner une interface à la VRF
```text
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip vrf forwarding CLIENT_A
Router(config-if)# ip address 10.0.0.1 255.255.255.0
```

> **Attention :** Lorsque vous associez une VRF à une interface, l'adresse IP de l'interface est automatiquement supprimée par le routeur. Il faut la réinterroger juste après !

---

## 5. Commandes de Vérification Utiles

* **Voir toutes les VRF configurées :**
  `show ip vrf`
* **Consulter la table de routage d'une VRF spécifique :**
  `show ip route vrf CLIENT_A`
* **Lancer un Ping depuis une VRF :**
  `ping vrf CLIENT_A 10.0.0.2`

---

## 6. Synthèse

* **VRF** = Virtualisation de la table de routage au Niveau 3 (L3).
* Elle offre l'**isolation**, la **sécurité** et autorise le **chevauchement d'adresses IP**.
* Chaque interface du routeur appartient soit à la table globale (*Global Routing Table*), soit à une VRF spécifique.