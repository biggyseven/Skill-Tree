# DHCP et DNS : Niveau Intermédiaire

Après avoir vu les bases, ce cours approfondit le fonctionnement technique, les configurations avancées et les mécanismes de sécurité liés aux services **DHCP** et **DNS**.

---

## 1. Approfondissement du DHCP

### 1.1 Le cycle de vie du bail DHCP (DHCP Lease)

Une adresse IP attribuée par DHCP n'est pas éternelle. Elle est prêtée sous forme de **bail** (*lease*) assorti d'une durée déterminée (ex. 8 heures, 24 heures, 7 jours).

#### Les phases de renouvellement :
* **$T_1$ (Timer 1 - Renouvellement) :** Arrivé à 50% du temps de bail, le client envoie un message `DHCPREQUEST` en **Unicast** directement au serveur DHCP d'origine pour prolonger son bail.
* **$T_2$ (Timer 2 - Re-liaison / Rebind) :** Si le serveur ne répond pas à 87.5% de la durée du bail, le client passe en mode `DHCPREQUEST` en **Broadcast** pour essayer d'obtenir une prolongation auprès de n'importe quel autre serveur DHCP disponible sur le réseau.
* **Expiration :** À 100% de la durée, si aucun serveur n'a répondu, le client libère l'adresse IP et retente un processus DORA complet.

---

### 1.2 Le Relais DHCP (DHCP Relay / Agent de Relais)

Par défaut, les messages de découverte DHCP (`DHCPDISCOVER`) sont envoyés en **Broadcast** (adresse `255.255.255.255`). Or, les routeurs bloquent les trames broadcast pour éviter d'inonder les autres réseaux.

#### Problème :
Comment attribuer des adresses à plusieurs sous-réseaux sans installer un serveur DHCP physique dans chaque VLAN/sous-réseau ?

#### Solution :
On configure un **Relais DHCP** (souvent via la commande `ip helper-address` sur les équipements Cisco).

```text
[ Client VLAN 10 ] 
       │ (Broadcast : DHCPDISCOVER)
       ▼
[ Routeur / Commutateur L3 ]  ──── (Unicast : IP du serveur DHCP) ────► [ Serveur DHCP ]
```

1. Le routeur reçoit le Broadcast sur l'interface du client.
2. Il transforme la requête en message **Unicast** à destination de l'adresse IP exacte du serveur DHCP.
3. Le serveur DHCP répond au routeur, qui retransmet ensuite la réponse au client.

---

### 1.3 Attributions fixes vs dynamiques

* **Attribution dynamique :** Le serveur choisit une IP libre dans une plage définies (*Scope* ou *Pool*).
* **Réservation DHCP (Static Lease) :** Associe de façon permanente une adresse IP fixe à l'**adresse MAC** spécifique d'un équipement (ex. imprimantes réseau, serveurs de fichiers).

---

## 2. Approfondissement du DNS

### 2.1 La Hiérarchie DNS

L'arborescence des noms de domaine fonctionne de droite à gauche, sous forme d'arbre inversé :

```text
               . (Racine / Root Zone)
         ┌─────┴─────┐
        .com        .org       .fr (TLD - Top Level Domain)
         │
    example.com                (Domaine de second niveau)
         │
    www.example.com            (Sous-domaine / FQDN)
```

* **Serveurs Racines (*Root Servers*) :** Il existe 13 ensembles de serveurs racines dans le monde (nommés de A à M). Ils orientent vers les serveurs de TLD.
* **TLD (*Top-Level Domain*) :** Gèrent les extensions `.com`, `.org`, `.fr`, etc.
* **Serveurs autoritaires :** Hébergent la zone DNS officielle du nom de domaine et fournissent les réponses finales.

---

### 2.2 Résolution Récursive vs Itérative

```text
[ Client ] ──(1) Requête Récursive──► [ Résolveur DNS (ex: 8.8.8.8) ]
                                             │
                                             ├──(2) Requête Itérative──► [ Serveur Racine . ]
                                             │◄─(3) Réponse : voir TLD .com ─┘
                                             │
                                             ├──(4) Requête Itérative──► [ Serveur TLD .com ]
                                             │◄─(5) Réponse : voir NS de example.com ┘
                                             │
                                             ├──(6) Requête Itérative──► [ Serveur Autoritaire ]
                                             │◄─(7) Réponse : IP de www.example.com ──┘
                                             │
[ Client ] ◄──(8) Adresse IP retournée ──────┘
```

1. **Requête Récursive :** Le client demande au résolveur local : *"Trouve-moi l'IP exacte, fais tout le travail à ma place."*
2. **Requête Itérative :** Le résolveur interroge successivement la chaîne de serveurs : *"Connais-tu cette IP ? Non ? Indique-moi quel serveur interroger ensuite."*

---

### 2.3 Les principaux enregistrements DNS (DNS Records)

| Type | Nom complet | Rôle | Exemple de valeur |
| :--- | :--- | :--- | :--- |
| **A** | Address | Associe un nom d'hôte à une adresse IPv4 | `example.com` $\rightarrow$ `93.184.216.34` |
| **AAAA** | IPv6 Address | Associe un nom d'hôte à une adresse IPv6 | `example.com` $\rightarrow$ `2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Canonical Name | Alias d'un autre nom de domaine | `blog.example.com` $\rightarrow$ `example.com` |
| **MX** | Mail Exchange | Définit les serveurs de messagerie du domaine | `example.com` $\rightarrow$ `mail.example.com` (Prio: 10) |
| **NS** | Name Server | Indique les serveurs autoritaires de la zone | `example.com` $\rightarrow$ `ns1.example.com` |
| **TXT** | Text Record | Stocke du texte (utilisé pour la sécurité des e-mails : SPF, DKIM, DMARC) | `v=spf1 include:_spf.google.com ~all` |
| **PTR** | Pointer | Résolution inverse (IP vers Nom) | `34.216.184.93.in-addr.arpa` $\rightarrow$ `example.com` |

---

## 3. Sécurité et Vulnérabilités Courantes

### 3.1 Risques liés au DHCP
* **DHCP Spoofing / Rogue DHCP :** Un pirate installe un faux serveur DHCP sur le réseau local pour distribuer sa propre passerelle ou son propre serveur DNS, lui permettant d'effectuer une attaque *Man-in-the-Middle* (MitM).
  * *Protection :* Activation du **DHCP Snooping** sur les commutateurs réseau.
* **DHCP Starvation Attack :** Attaque par saturation consistant à envoyer des milliers de fausses adresses MAC pour épuiser la plage d'adresses IP du serveur DHCP officiel.

### 3.2 Risques liés au DNS
* **DNS Cache Poisoning (Empoisonnement de cache) :** Injection de fausses données dans le cache d'un serveur DNS pour rediriger les utilisateurs vers des sites malveillants.
  * *Protection :* Utilisation de **DNSSEC** (signatures cryptographiques des enregistrements).
* **DNS Tunneling :** Utilisation du protocole DNS pour faire sortir clandestinement des données ou contourner un pare-feu/portail captif.

---

## 4. Exercice de Synthèse

Imaginez que vous administriez un réseau d'entreprise réparti sur deux VLANs (VLAN 10 pour le personnel, VLAN 20 pour les invités).

1. Pourquoi est-il nécessaire d'avoir un **Agent de Relais DHCP** si le serveur DHCP se trouve dans le VLAN 100 d'administration ?
2. Quel type d'enregistrement DNS devez-vous créer pour associer le sous-domaine `mail.monentreprise.com` à l'adresse IP IPv4 de votre serveur SMTP ?
3. Si la résolution DNS d'un poste client fonctionne mais que les requêtes sont très lentes, quel paramètre de temps de bail ou de TTL (Time-To-Live) DNS pourriez-vous vérifier ou ajuster ?