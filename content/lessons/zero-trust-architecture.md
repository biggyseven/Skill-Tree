# Cours Intensif – Zero Trust & Micro‑segmentation  
**Niveau : Admin Réseau Senior (CCIE)**  

---

## 1. Introduction & Pourquoi le Zero Trust ?

| **Mythe** | **Réalité Zero Trust** |
|-----------|------------------------|
| “Le périmètre protège” | Le périmètre n’existe plus – chaque accès est supposé non fiable |
| “Une fois authentifié, l’accès est libre” | Chaque requête est évaluée (identité, contexte, posture) |
| “Les firewalls suffisent” | Les firewalls sont des points d’application de politiques, pas des gardiens absolus |
| “Le VPN = confiance” | Le VPN ne garantit pas la légitimité du trafic interne |

*Le modèle Zero Trust (ZT) repose sur trois piliers fondamentaux* :

1. **Vérifier explicitement** – Authentification forte, autorisation basée sur le moindre privilège, validation continue.  
2. **Utiliser le moindre privilège** – Segmentation granulaire, “need‑to‑know”.  
3. **Assumer la compromission** – Journalisation, détection d’anomalies, réponses automatisées.

---

## 2. Concepts Clés

| Concept | Description | Exemple d’implémentation |
|---------|-------------|--------------------------|
| **Trust Zone** | Segment logique (ex. DMZ, zone de travail, zone de service) | VLAN + ACL + politique ZT |
| **Identity‑Based Access Control (IBAC)** | Décisions d’accès basées sur l’identité (user, service, device) | Cisco ISE + ACI contracts |
| **Continuous Evaluation** | Re‑évaluation à chaque hop / chaque session | Cisco Stealthwatch + NetFlow |
| **Policy Decision Point (PDP)** | Engine qui rend la décision (allow/deny) | Palo Alto PAN‑OS, Cisco Tetration |
| **Policy Enforcement Point (PEP)** | Point qui applique la décision (firewall, switch, hyper‑visor) | Cisco Nexus 9000, Linux eBPF |
| **Posture Assessment** | Vérification de la conformité du endpoint (AV, patch) | Cisco AMP, Qualys, OSSEC |

---

## 3. Architecture Zero Trust

```
+-------------------+          +-------------------+
|   Identity Store  |          |   Posture Engine  |
| (AD/LDAP/OIDC)    |          | (Qualys, SCC)     |
+---------+---------+          +----------+--------+
          |                               |
          |  AuthN / AuthZ                |
          v                               v
+-------------------+   Policy   +-------------------+
|   Policy Engine   |<-----------|   Policy DB       |
| (PDP)             |   Store    | (JSON/YAML)       |
+---------+---------+            +--------+----------+
          |                               |
          | Decision (allow/deny)         |
          v                               v
+-------------------+   Enforcement   +-------------------+
|   PEP (Switch)    |<----------------|   PEP (Host)      |
| (Cisco ACI)       |   (VXLAN, ACL)  | (Linux eBPF)      |
+-------------------+                 +-------------------+
```

*Les flux passent toujours par un **PEP** qui interroge le **PDP** (ou utilise des policies pré‑chargées).*

---

## 4. Micro‑segmentation – Définition & Objectifs

- **Granularité** : du réseau (VLAN, VXLAN) à la couche 7 (processus, conteneur).  
- **Isolation** : chaque workload possède son propre périmètre de confiance.  
- **Visibilité** : flux intra‑zone sont observés, catalogués, contrôlés.  

### 4.1. Modèles de micro‑segmentation

| Modèle | Niveau | Technologie | Cas d’usage |
|--------|--------|-------------|-------------|
| **Port‑Based** | L2/L3 | VLAN, ACL, VACL | Isolation de serveurs legacy |
| **IP‑Based** | L3/L4 | VXLAN, NSX‑T, ACI contracts | Multi‑tenant data centre |
| **Process‑Based** | L7 | eBPF, Calico, Cilium | Micro‑services, Kubernetes |
| **Identity‑Based** | L2‑L7 | ISE + ACI, Illumio Policy Compute Engine | BYOD, Zero Trust Network Access (ZTNA) |

---

## 5. Implémentation Zero Trust sur les Plateformes Cisco  

### 5.1. Cisco Identity Services Engine (ISE)

```bash
# Création d’un groupe d’utilisateurs
ise(config)# aaa group server radius ZT-Group
ise(config-radius-group)# server 10.10.10.10 auth-port 1812 acct-port 1813
ise(config-radius-group)# exit

# Attribution d’un rôle basé sur le groupe AD
ise(config)# policy-map type radius ZT-Policy
ise(config-pmap)# class ZT-Group
ise(config-pmap-c)# set authentication-method radius
ise(config-pmap-c)# set authorization-role ZT-Access
```

### 5.2. Cisco ACI – Contracts & Filters

```bash
# Création d’un filtre (TCP 443)
apic# configure terminal
apic(config)# filter tcp-https
apic(config-filter)# entry 1
apic(config-filter-entry)# protocol tcp
apic(config-filter-entry)# destination-port eq 443
apic(config-filter-entry)# exit
apic(config)# contract zt-web-access
apic(config-contract)# filter tcp-https
apic(config-contract)# action permit

# Appliquer le contract entre deux EPG
apic(config)# epg app-frontend
apic(config-epg)# contract consumer zt-web-access
apic(config-epg)# contract provider zt-web-access
```

### 5.3. Cisco IOS‑XE – Enforcer avec Zone‑Based Policy Firewall (ZPF)

```bash
router(config)# zone security ZONE_INTERNAL
router(config)# zone security ZONE_DMZ
router(config)# zone-pair security ZP_INTERNAL_DMZ source ZONE_INTERNAL destination ZONE_DMZ
router(config-zone-pair)# service-policy type inspect ZP_INTERNAL_DMZ_POLICY
router(config)# class-map match-any ZP_INTERNAL_DMZ_CLASS
router(config-cmap)# match access-group name ACL_INT_TO_DMZ
router(config)# policy-map type inspect ZP_INTERNAL_DMZ_POLICY
router(config-pmap)# class ZP_INTERNAL_DMZ_CLASS
router(config-pmap-c)# inspect http
router(config-pmap-c)# inspect dns
```

### 5.4. Cisco Stealthwatch – Détection d’anomalies

```bash
# Enregistrement d’un nouveau Flow Collector
stealthwatch# configure terminal
stealthwatch(config)# flow-collector 10.20.30.40 port 2055
stealthwatch(config)# exit
# Création d’un profil de confiance
stealthwatch# policy trust-profile ZT-Profile
stealthwatch(policy)# add endpoint-group "App-Servers"
stealthwatch(policy)# add allowed‑protocol tcp 443
stealthwatch(policy)# commit
```

---

## 6. Implémentation Linux – eBPF & nftables  

### 6.1. eBPF avec Cilium (Kubernetes)

```bash
# Installation Cilium (Helm)
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.14.0 \
  --namespace kube-system \
  --set kubeProxyReplacement=partial \
  --set identityAllocationMode=crd

# Policy L7 – autoriser HTTP uniquement depuis le namespace frontend
cat <<EOF | kubectl apply -f -
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: allow-frontend-http
spec:
  endpointSelector:
    matchLabels:
      app: backend
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
EOF
```

### 6.2. nftables – Policy “Zero Trust” sur un serveur

```bash
# Reset complet
sudo nft flush ruleset

# Table de filtrage
sudo nft add table inet zt-filter

# Chaîne d’entrée – default drop
sudo nft add chain inet zt-filter input { type filter hook input priority 0 \; policy drop \; }

# Autoriser SSH depuis IP de management
sudo nft add rule inet zt-filter input ip saddr 192.0.2.10 tcp dport 22 ct state new,established accept

# Autoriser HTTP uniquement depuis le réseau de l’application
sudo nft add rule inet zt-filter input ip saddr 10.10.0.0/16 tcp dport 80 ct state new,established accept

# Autoriser le trafic de retour
sudo nft add rule inet zt-filter input ct state established,related accept
```

### 6.3. Open Policy Agent (OPA) – Décision dynamique

```bash
# Exemple de policy Rego (policy.rego)
package zt.authz

default allow = false

allow {
    input.user == "alice"
    input.action == "read"
    input.resource == "db1"
    input.context.time_of_day >= 9
    input.context.time_of_day <= 18
}
```

```bash
# Test de la policy
opa eval -i input.json -d policy.rego "data.zt.authz.allow"
```

---

## 7. Comparatif des Solutions de Micro‑segmentation

| Vendor | Type | Integration | Policy Language | Visibility | Performance Impact |
|--------|------|-------------|-----------------|------------|--------------------|
| **Cisco ACI** | Hardware‑centric (VXLAN) | Full avec ISE, Cisco DNA Center | Cisco APIC GUI + JSON | Flow‑aware (Stealthwatch) | < 5 % (ASIC) |
| **VMware NSX‑T** | Hyper‑visor + VDS | vCenter, vRealize | NSX Policy (YAML) | Distributed IDS/IPS | < 7 % (DPDK) |
| **Illumio PCE** | Agent‑based | Cloud (AWS, Azure) | Illumio Policy (Web UI) | Real‑time flow map | < 3 % (kernel) |
| **Calico (Project)** | L3/L4 + eBPF | Kubernetes, OpenStack | YAML (NetworkPolicy) | BGP/IP‑in‑IP | < 2 % (eBPF) |
| **Palo Alto Prisma Access** | Cloud‑native ZTNA | IdP (SAML, OIDC) | Policy Studio | Cloud‑based telemetry | N/A (SaaS) |

---

## 8. Cycle de Vie d’une Politique Zero Trust  

```
+-------------------+      +--------------------+      +-------------------+
| 1. Discovery      | ---> | 2. Modélisation    | ---> | 3. Déploiement    |
| (Flow, Asset)    |      | (Trust Zones)      |      | (PEP, PDP)        |
+-------------------+      +--------------------+      +-------------------+
        ^                           |                         |
        |                           v                         v
+-------------------+      +--------------------+      +-------------------+
| 6. Retrait /      | <--- | 5. Audits & Revues | <--- | 4. Monitoring &   |
|    Décommission  |      | (Compliance)       |      |   Alerting        |
+-------------------+      +--------------------+      +-------------------+
```

### 8.1. Étape 1 – Discovery automatisée

- **Cisco Stealthwatch** : `ssm capture start`  
- **nmap + scripts** : `nmap -sS -p- -T4 10.0.0.0/16 -oX discovery.xml`  
- **OPA + Terraform** : génération d’inventaire.

### 8.2. Étape 2 – Modélisation des Trust Zones

| Zone | Critères | Exemple de policy |
|------|----------|-------------------|
| **ZT‑DMZ** | Externe, services web, besoin de TLS | `allow src=any dst=10.10.0.0/24 dport=443 proto=tcp` |
| **ZT‑APP** | Backend, accès DB uniquement | `allow src=10.10.0.0/24 dst=10.20.0.0/24 dport=5432 proto=tcp` |
| **ZT‑ADMIN** | Gestion, SSH, SNMP | `allow src=192.0.2.0/24 dst=10.0.0.0/16 dport=22,161 proto=udp/tcp` |

### 8.3. Étape 3 – Déploiement via IaC (Ansible)

```yaml
- name: Deploy Zero Trust contracts on ACI
  hosts: apic
  connection: local
  gather_facts: false
  tasks:
    - name: Create filter for HTTPS
      aci_filter:
        host: "{{ apic_host }}"
        username: "{{ apic_user }}"
        password: "{{ apic_pass }}"
        filter: tcp-https
        entry:
          - name: "1"
            ether_type: ip
            protocol: tcp
            dest_port: "443"
    - name: Create contract
      aci_contract:
        host: "{{ apic_host }}"
        username: "{{ apic_user }}"
        password: "{{ apic_pass }}"
        contract: zt-web-access
        filter: tcp-https
        scope: tenant
        state: present
```

---

## 9. Sécurité & Conformité  

| Norme | Exigence ZT | Implémentation concrète |
|-------|-------------|------------------------|
| **PCI‑DSS** | Segmentation des données de carte | VLAN + ACL + monitoring Stealthwatch |
| **HIPAA** | Accès basé sur le rôle | ISE + AD groups + contracts ACI |
| **GDPR** | Droit à l’effacement & audit | OPA logs + Elasticsearch + Kibana |
| **NIST 800‑53** | Contrôle AC‑3 (Least Privilege) | Micro‑segmentation + MFA + posture checks |

- **Journalisation** : Syslog centralisé (Cisco -> Logstash), **Cef** pour SIEM.  
- **Détection d’anomalies** : Machine Learning sur flux (Stealthwatch, Splunk UEBA).  
- **Réponse automatisée** : `Cisco DNA Center` → `playbook` qui isole un endpoint via `ACI contract delete`.

---

## 10. Performance & Optimisation  

| Optimisation | Impact | Méthode |
|--------------|--------|---------|
| **Offload matériel** | Réduction latence | Utiliser ASIC sur Nexus 9000, FEX |
| **eBPF JIT** | Trafic ultra‑rapide | Activer `bpfilter` et `bpf_jit_enable=1` |
| **Policy Caching** | Moins de requêtes PDP | TTL de 30 s sur Cisco ISE |
| **Compression VXLAN** | Réduction bande passante | `system vxlan compression` sur ACI |
| **Segment‑aware routing** | Évite le “hairpin” | BGP EVPN + route‑targets spécifiques |

---

## 11. Atelier de Dépannage – Scénario “Isolation Inattendue”

### 11.1. Contexte

- Un serveur **app‑db01** (10.20.0.10) ne répond plus aux requêtes depuis le serveur **app‑web01** (10.10.0.20).  
- Les deux appartiennent à des EPG différents, reliés par le contract **zt-db-access**.  
- Aucun changement de configuration n’a été appliqué récemment.

### 11.2. Objectifs

1. Vérifier la **connectivité L2/L3**.  
2. Inspecter les **politiques ACI** (contracts, filters).  
3. Analyser les **logs d’authentification** (ISE).  
4. Utiliser **Stealthwatch** pour visualiser le flux.  
5. Corriger le problème et valider.

### 11.3. Étapes de dépannage

| Étape | Action | Commande / UI | Résultat attendu |
|-------|--------|---------------|------------------|
| 1️⃣ | Ping depuis `app-web01` | `ping 10.20.0.10 -c 4` | 0% loss si L2/L3 OK |
| 2️⃣ | Vérifier ARP | `arp -n | grep 10.20.0.10` | MAC du switch ACI |
| 3️⃣ | Traceroute | `traceroute 10.20.0.10` | 1‑hop (leaf) → 2‑hop (spine) |
| 4️⃣ | Inspecter le contrat sur APIC | **APIC GUI → Tenants → App → Contracts → zt-db-access** | Doit contenir le filtre `tcp-5432` |
| 5️⃣ | Vérifier les