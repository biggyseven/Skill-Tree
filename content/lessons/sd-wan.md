# SD-WAN : Architecture, Implémentation et Dépannage – Cours Intensif CCIE

## 1. Introduction

Le SD-WAN (Software-Defined Wide Area Network) représente une évolution majeure dans la gestion des réseaux distribués. Contrairement aux solutions traditionnelles basées sur des routeurs VPN statiques, le SD-WAN utilise une plateforme logicielle centralisée pour orchestrer dynamiquement le trafic entre sites distants. Cette architecture permet d'optimiser l'utilisation des liens sous-utilisés, d'améliorer la résilience du réseau et de réduire considérablement les coûts opérationnels.

### 1.1 Définition et objectifs

Le SD-WAN est un ensemble de fonctionnalités incluses dans un logiciel qui permet de :
- **Segmenter le trafic** selon des politiques configurables
- **Affecter automatiquement** les flux sur les meilleurs liens disponibles
- **Réduire la dépendance** aux VPN classiques en utilisant des transports multiples (MPLS, LTE, Wi-Fi)
- **Centraliser la gestion** via une interface cloud ou on-premise

### 1.2 Bénéfices clés

| Bénéfice | Description |
|-----------|-------------|
| Réduction des coûts | Moins de câbles MPLS et optimisation du trafic |
| Haute disponibilité | Redirection automatique du trafic en cas de défaillance |
| Performance accrue | Utilisation dynamique des liens et QoS intelligent |
| Flexibilité | Accès rapide à de nouveaux sites via des connexions Internet standard |

---

## 2. Architecture SD-WAN

L'architecture d'un système SD-WAN suit une topologie hiérarchique distribuée mais centralisée.

```
                    ┌─────────────────────────────┐
                    │         Cisco VMM (Cloud)   │
                    │      (orchestrateur)        │
                    └───┬────────────┬──────────┘
                       │            │
          ┌────────────▼─────┐     ┌─▼────────────┐
          │  Site A (Edge)  │     │  Site B (Edge)│
          │  + SD-WAN Edge  │     │  + SD-WAN Edge│
          └─────────────────┘     └───────────────┘
```

### 2.1 Composants principaux

1. **SD-WAN Edge Device** – Matériel gérant le tunneling et la translation IP/IPsec
2. **Controller / VMM** – Plateforme centrale pour la configuration et la surveillance
3. **Orchestration** – Moteur logique échangeant des informations entre sites
4. **Transport Layer** – Liens physiques vers Internet (WAN) et MPLS

---

## 3. Topologie et Flux de Données

### 3.1 Schéma ASCII du trafic SD-WAN

```
                    Internet (WAN)                     Internet (WAN)
                         |                                   |
                         ▼                                   ▼
               +-------------+                           +-------------+
               |  Site A     |                           |  Site B     |
               |  (Edge)     | <- Trafic 1: App/Voix    |  (Edge)     |
               +------+------+                           +------+------+
                      │                                             │
                      │  Trafic optimisé (gREAT/PCF)                │
                      │                                             │
              +--------+-----------+                  +----------+----------+
              │                                 │                   │
              ▼                                 ▼                   ▼
       [SD-WAN Controller] <---> [SD-WAN Edge A] <---> [Internet]     [SD-WAN Edge B]
              │                               ▲                        │
              │  Politique de segmentation     │ QoS dynamique           │
              │                                │                        │
              └────────────────────────────────┴─────────────────────────┘
                              Centralized Orchestration

### 3.2 Processus de routage SD-WAN

1. **Collecte de métriques** – Les edge devices rapportent leur état network
2. **Calcul de la meilleure donnée** – Le controller choisit le lien optimal
3. **Migration dynamique** – Le trafic est redirigé vers le nouveau chemin
4. **Sécurité applicative** – Chiffrement end-to-end sur chaque lien

---

## 4. Protocoles et Technologies SD-WAN

### 4.1 Protocoles de transport

| Protocole | Rôle | Avantage |
|-----------|------|----------|
| **GRE** | Encapsulation des flux IP sur un réseau IP sous-jacent | Compatible avec tout WAN |
| **IPsec** | Chiffrement de bout en bout du trafic | Sécurité forte |
| **MPLS** | Voie pré-sécurisée avec QoS garantie | Latence stable |
| **UDP/IPv6** | Transport natif pour les capacités modernes | Performance élevée |

### 4.2 Modèle de tunneling SD-WAN

Le SD-WAN peut utiliser plusieurs tunnels simultanés :

- **Dual-Homed** – Deux interfaces distinctes vers Internet
- **Multipath** – Plusieurs tunnels actifs pour la redondance
- **Single-Homed** – Un seul lien principal avec failover

```
Tunnel A (MTU 1500) → Site A ↔ Internet
Tunnel B (MTU 2000) → Site A ↔ Internet
               ↓
            Contrôleur SD-WAN
```

---

## 5. Comparaison des Solutions Réseau

### 5.1 Tableau comparatif SD-WAN vs Solutions Traditionnelles

| Critère | VPN Classique | Load Balancer | SD-WAN |
|---------|---------------|---------------|--------|
| Configuration | Statique, manuelle | Manuelle | Automatique |
| Optimisation du trafic | Non (via NAT) | Limited | Dynamique multi-traffic |
| Résilience | Basique (failover simple) | Dépendante du LB | Multi-failover intelligent |
| MTU | 1500 bytes | 1500 bytes | Jusqu'à 9000 bytes |
| Segmentation | Séparation physique | Application-level | Policy-based steering |
| Coût MPLS | Élevé | Moyen | Faible (Internet native) |
| Visibilité | Limitée | Faible | Complète via VMM |

### 5.2 Tableau comparatif détaillé des fonctionnalités SD-WAN

| Fonctionnalité | Description technique |
|----------------|-----------------------|
| **Traffic Engineering** | Algorithme basé sur le coût et la latence pour choisir les chemins |
| **Application-Aware Routing** | Identification du type de charge (voix, vidéo, data) et adaptation du protocole |
| **Zero-Touch Provisioning** | Installation automatique des appliances lors du déploiement |
| **Global Server Management** | Supervision centralisée des performances et des incidents |
| **QoS Adaptive** | Priorisation dynamique basée sur le SLA applicatif |

---

## 6. Implémentation sur Cisco SD-WAN (Viscosity)

Les plateformes Cisco SD-WAN incluent **Cisco Viscosity**, **ASA** ou **MCS**. Voici les commandes essentielles.

### 6.1 Activation et configuration de base

```bash
! Sous le device edge SD-WAN Cisco (ex: Cisco SD-WAN Edge Board)
enable
config t
!--- Activer le module SD-WAN ---
service stack sdwan
!--- Définir les interfaces WAN (Internet) -->
interface GigabitEthernet0/0/0
 description WAN_INTERFACE
 ip address 192.168.100.1 255.255.255.0
!
interface GigabitEthernet0/0/1
 description WAN_OUTER_LINK
 ip address 198.51.100.2 255.255.255.224
!
!--- Créer le pool SD-WAN (site grouping) -->
sd-wan site-group global_site
add-site "Site_A" id=100 default_behavior=active
add-site "Site_B" id=101 default_behavior=active
add-site "Site_C" id=102 default_behavior=active
!
!--- Configurer le traffic policy -->
sd-wan traffic-policy create app_policy
set priority voice
set bandwidth min=500k max=4000k
set application=Voice
set destination=public
!
sd-wan traffic-policy apply
```

### 6.2 Configuration du controller VMM (Cisco SD-WAN Manager)

```bash
! Sur le serveur du VMM (Linux ou Windows)
# Allocation d'un nom d'hôte unique
set vmm-hostname sdwan-core01
set vmm-subnet vmn-global
set vmm-region us-west-2
set vmm-provider internet

# Connexion au controller via SSH
ssh user@sandbox.sdwan.com
telnet sdwan-core01 22

# Exemple de commande pour activer le SD-WAN sur un edge
sdwan enable
sdwan config mode interface gigabitethernet0/0/1
sdwan set flow-threshold 80
sdwan start traffic

! Surveillance
show sdwan summary
show vmserver status
show vmserver connections
```

### 6.3 Sécurité : IPsec et Tunnels

```bash
! Créer un groupe de tunnel GRE sécurisé
ipx group-create GRE_TUNNEL 1

! Associer le groupe au port SD-WAN
interfaces GigabitEthernet0/0/1
 ipx tunnel name GRE_TUNNEL group-id=1 proto-ipsec udp-port 500
!

! Enregistrer le secret IPsec (partagé avec les autres sites)
encryption ciphers aes-256-gcm
key-material shared-key-id=CISKEY
!

! Activer le tunnel de gros volume (VPN)
ipsec transform-set SVWAN-secret esp-aes-256 esp-sha2-128
tunnel-identity host site_a
connect-ipsec-attributes {
    key-identification-mode remote-certificate
    rekey-attribute id=rekey_interval
}
```

### 6.4 Commande Linux pour la supervision SD-WAN

```bash
#!/bin/bash
# Script de monitoring SD-WAN sur un edge Cisco avec Viscosity CLI

print_status() {
    sdwan show all | grep -i "status"
}

monitor_traffic() {
    # Montrer le trafic par application
    sdwan show applications detailed
    
    # Voir les politiques actives
    sdwan show policies
}

# Exporter les logs JSON pour analyse
export_logs sdwan all > /var/log/sdwan.log.json
```

---

## 7. Dépannage SD-WAN – Atelier Pratique

### 7.1 Scénario de dépannage : Perte de connectivité

**Problème** : Le site B ne reçoit plus les requêtes depuis le site A malgré une connexion IP visible.

**Étapes diagnostiques :**

1. **Vérifier la connectivité IP**
   ```bash
   ping -c 10 10.0.0.1  # Adresse du site A
   ping -c 10 198.51.100.2  # Adresse du site B
   ```
   *Résultat attendu* : Si le ping échoue, vérifier le routage BGP ou OSPF côté edge.

2. **Vérifier le tunnel SD-WAN**
   ```bash
   sdwan show tunnels
   ! Chercher le tunnel vers le site B
   ! Attendre la phase de convergence (Timeout par défaut 30s)
   ```

3. **Analyser les métriques de performance**
   ```bash
   sdwan show flows
   ! Regarder la latence et le jitter sur le tunnel
   ```

4. **Consulter les journaux d'erreur**
   ```bash
   ifconfig-audit log | grep -i error
   sdwan diagnose errors
   ```

5. **Redémarrer le service SD-WAN**
   ```bash
   sudo systemctl restart sdwan
   ```

**Solution typique** : Si le tunnel est dénié, vérifier le **policy session timeout**. Par défaut, un timeout de 60 secondes si aucune action n'est prise. Augmenter le `max-timeout` dans la configuration :

```json
{
  "timeout": {
    "default": 300,
    "voice": 600,
    "data": 360
  }
}
```

### 7.2 Scénario de dépannage : QoS inadapté

**Problème** : La voix (Zoom/Teams) subit du delay alors que la vidéo est fluide.

**Diagnostic :**
```bash
! Mesurer la latence sur le tunnel
traceroute -m 20 sdwan-edge-1

! Vérifier le ratio RTP sur le flux audio
show vmcaps qos statistics
```

**Solution :**
1. Ajuster le seuil de priorité dans la politique :
   ```bash
   sdwan traffic-policy update app_policy --priority=voice --min-bandwidth=1000k
   ```
2. Limiter le débit de la voix avec un débit maximum :
   ```bash
   sdwan traffic-policy update app_policy --priority=voice --bandwidth-limit=2500k
   ```

### 7.3 Checklist de dépannage SD-WAN

- [ ] Les interfaces upstream et downstream ont-elles un état `up`?
- [ ] Le tunnel SD-WAN est-il bien formé (`show tunnels`) ?
- [ ] Les politiques de trafic sont-elles appliquées (`show policies active`) ?
- [ ] Y a-t-il des erreurs IPsec (handshake failures) ?
- [ ] Les MTUs sont-elles correctement négociées (option `mtu`) ?
- [ ] Les routes BGP sont-elles synchronisées entre les sites ?

---

## 8. Bonnes Pratiques et Recommandations

1. **Planification du MTU**  
   Paramétrer le MTU à 9000 bytes pour éviter les fragments et améliorer les performances VoIP.

2. **Optimisation de la bande passante**  
   Utiliser le **Multi-Pathing** pour distributez la charge entre plusieurs liens WAN.

3. **Politique de sécurité stricte**  
   Activer le chiffrement IPsec sur tous les tunnels et implémenter des certificats auto-signés pour l'authentification mutuelle.

4. **Automatisation**  
   Employer Ansible ou Terraform pour le provisioning des configurations SD-WAN de manière reproductible.

5. **Monitoring continu**  
   Configurer des alertes sur la latence, le jitter et la perte de paquets via SNMP ou l'intégration CloudWatch/Azure Monitor.

---

## 9. Conclusion

Le SD-WAN constitue une solution incontournable pour les organisations souhaitant moderniser leur infrastructure réseau. En centralisant la gestion du trafic et en optimisant l'utilisation des ressources WAN, il permet de réduire les coûts, d'améliorer la résilience et de simplifier le déploiement de nouvelles sites. La maîtrise des commandes Cisco et des mécanismes de configuration de VMM est essentielle pour réussir cette transition.

La combinaison de la flexibilité des tunnels multiples, de l'orchestration centralisée et de la sécurité intégrée fait du SD-WAN la plateforme privilégiée pour les architectures hybrides et les environnements multi-cloud.

---

*Fin du cours.*