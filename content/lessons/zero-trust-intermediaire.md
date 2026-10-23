## node_id: zero-trust-intermediaire

title: Architecture Zero Trust - Intermédiaire

# Architecture Zero Trust - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** Architecture Zero Trust Débutant (`zero-trust-debutant`), compréhension des concepts IAM, contrôles d'accès basés sur l'identité (OAuth2/OIDC, SAML), et mécanismes de réseau fondamental (TLS, proxy, SDN).

Ce module approfondit l'implémentation pratique de l'architecture Zero Trust. Vous y découvrirez le **ZTNA (Zero Trust Network Access)**, l'évaluation dynamique du contexte (**Conditional Access / Continuous Adaptive Trust**), le **Device Trust**, la **Microsegmentation** applicative, ainsi que l'intégration du paradigme **SASE (Secure Access Service Edge)**.

## 1. ZTNA vs VPN Traditionnel

Le **Zero Trust Network Access (ZTNA)** redéfinit l'accès distant aux ressources internes en appliquant le principe de l'accès au niveau applicatif plutôt qu'au niveau réseau.

```
VPN TRADITIONNEL : Accès Réseau (L3/L4)
[ Client Distant ] ──(Tunnel IPsec/SSL)──> [ VPN Concentrator ] ──> [ Réseau Interne Complet ]
                                                                     (Mouvement latéral possible)

ZTNA : Accès Applicatif Isolant (L7)
[ Client Distant ] ──(TLS chiffré)──> [ ZTNA Gateway/Broker ] ──> [ Application A Uniquement ]
                                      (Évaluation Contextuelle)     (Pas d'accès aux autres IP/services)
```

### Comparaison Technique :

| Critère | VPN Traditionnel | ZTNA (Zero Trust Network Access) |
| ----- | ----- | ----- |
| **Périmètre d'accès** | Niveau Réseau (Couche 3/4) | Niveau Application (Couche 7) |
| **Visibilité des ressources** | IP et ports internes visibles par le client | Ressources invisibles (*Dark Cloud* / SDP) |
| **Réseau sous-jacent** | Extension du réseau d'entreprise | Réseau distant considéré comme hostile |
| **Mécanisme de connexion** | Entrant (*Inbound Connections*) | Sortant via Connecteur léger (*Outbound Connectors*) |
| **Contrôle continu** | Authentification au moment de l'établissement du tunnel | Évaluation continue du risque pendant toute la session |

## 2. Politique d'Accès Conditionnel & Continuous Adaptive Trust (CAE/CARTA)

Dans une architecture Zero Trust mûre, la décision d'accès n'est pas binaire ni ponctuelle. Elle s'appuie sur le modèle **CARTA** (*Continuous Adaptive Risk and Trust Assessment*) ou le protocole **CAE** (*Continuous Access Evaluation*).

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      ÉVALUATION DU CONTEXTE                           │
 ├───────────────────┬───────────────────┬────────────────────────────────┤
 │   Utilisateur     │     Appareil      │            Environnement       │
 │ - Rôle / Groupe   │ - État EDR/Antivirus│ - Géolocalisation / IP        │
 │ - Risque Identité │ - Conformité MDM  │ - Anomalie de comportement    │
 └─────────┬─────────┴─────────┬─────────┴────────────────┬───────────────┘
           │                   │                          │
           └───────────────────┼──────────────────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │   POLICY ENGINE / DECISION POINT   │
            └─────────────────┬──────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   [ ACCORDER ]        [ EXIGER MFA ]        [ BLOQUER ]
(Accès à l'app)    (Facteur additionnel)   (Session terminée)
```

### Détection des Signaux de Risque :

* **Impossible Travel (Voyage impossible) :** Connexion depuis Paris puis 5 minutes plus tard depuis Tokyo.
* **Appareil non conforme :** Désactivation de l'Agent EDR ou système non mis à jour.
* **Risque utilisateur :** Identifiants détectés dans une fuite de données externe (*Leaked Credentials*).

## 3. Device Trust & Posture d'Appareil

L'identité de l'utilisateur ne suffit pas : l'appareil à partir duquel s'effectue la demande doit également être vérifié avant et pendant l'accès.

### Étapes d'évaluation de la posture (*Health Check*) :

1. **Vérification d'Identité de l'Appareil :** Utilisation de certificats x509 délivrés par la PKI d'entreprise ou puces **TPM (Trusted Platform Module)**.
2. **Conformité OS & Patch Management :** Inscription préalable dans une solution **MDM/UEM** (ex: Microsoft Intune, VMware Workspace ONE, Jamf).
3. **Agent de Sécurité Actif :** Validation que l'agent **EDR (Endpoint Detection and Response)** est fonctionnel et remonte un état sain à la plateforme de gestion.

## 4. Microsegmentation & Software-Defined Perimeter (SDP)

La microsegmentation consiste à isoler logiquement les charges de travail (*workloads*) au sein même du datacenter ou du Cloud.

```
SANS MICROSEGMENTATION (Zone Réseau Unique) :
[ Web Server ] ───> [ App Server ] ───> [ Database Server ]
      │                   ▲
      └──(Mouvement)──────┘  <-- Une compromission du Web Server donne accès direct à la DB.

AVEC MICROSEGMENTATION (Contrôles Applicatifs Stricts) :
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Zone Web      │     │  Zone App      │     │  Zone Database │
│ [ Web Server ] │ ──> │ [ App Server ] │ ──> │ [ DB Server ]  │
└────────────────┘     └────────────────┘     └────────────────┘
      │                          │
      └─────── x BLOQUÉ x ───────┘  (Pas de règle d'autorisation directe)
```

### Méthodes d'implémentation de la Microsegmentation :

* **Réseau / Overlay (SDN) :** Utilisation de réseaux virtuels VXLAN et règles de sécurité distribuées (ex: VMware NSX, AWS Security Groups).
* **Basée sur l'Hôte (Host-Based) :** Agents légers installés sur chaque OS contrôlant les pare-feux locaux (iptables/Windows Firewall) via un orchestrateur central.
* **Conteneurs / Service Mesh :** Utilisation d'un Proxy Sidecar (ex: Envoy dans Istio) imposant **mTLS (Mutual TLS)** et l'autorisation RBAC au niveau des microservices Kubernetes.

## 5. Convergence Zero Trust & SASE (Secure Access Service Edge)

Le modèle **SASE** formalise la convergence entre le réseau étendu WAN (SD-WAN) et les services de sécurité réseau natifs du Cloud (Security as a Service).

```
                       ┌─────────────────────────────────────────────────┐
                       │                   SASE CLOUD                    │
                       │                                                 │
                       │   ┌──────────┐  ┌──────────┐  ┌─────────────┐   │
                       │   │   ZTNA   │  │   SWG    │  │    CASB     │   │
                       │   └──────────┘  └──────────┘  └─────────────┘   │
                       │   ┌─────────────────────────────────────────┐   │
                       │   │         FWaaS (Firewall as a Service)  │   │
                       │   └─────────────────────────────────────────┘   │
                       └────────────────────────▲────────────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 │                              │                              │
         [ Utilisateur Distant ]        [ Agence / Branch ]           [ Multi-Cloud ]
```

* **ZTNA :** Accès privé et sécurisé aux applications internes.
* **SWG (Secure Web Gateway) :** Protection et filtrage lors de la navigation sur le Web externe.
* **CASB (Cloud Access Security Broker) :** Sécurisation et contrôle de l'utilisation des applications SaaS (ex: Microsoft 365, Salesforce).
* **FWaaS (Firewall as a Service) :** Inspection centralisée du trafic entrant et sortant dans le Cloud.

## Commandes et Outils de Vérification (Exemples d'Analyse)

| Commande / Outil | Description / Objectif |
| ----- | ----- |
| `openssl s_client -connect app.company.com:443 -tls1_3` | Inspecte et valide la négociation TLS 1.3 pour garantir le chiffrement des flux Zero Trust. |
| `kubectl exec -it <pod> -- curl -v https://service-b.namespace` | Vérifie l'enforcement du mTLS au sein d'un Service Mesh (Istio/Envoy). |
| **Log Analytics / SIEM (Sentinel, Splunk)** | Permet de corréler les événements d'authentification contextuelle et d'identifier les refus d'accès conditionnel. |

## Points à retenir

* **ZTNA vs VPN :** Le ZTNA offre un accès applicatif granulaire L7 (connexions sortantes), remplaçant l'accès réseau L3 du VPN.
* **Évaluation Continue :** L'authentification n'est pas un événement unique ; les conditions d'accès sont réévaluées en continu (CARTA/CAE).
* **Posture de l'Appareil :** L'accès requiert la combinaison d'une identité utilisateur forte et d'un appareil sain/conforme.
* **Microsegmentation :** Cruciale pour empêcher les déplacements latéraux en cas d'intrusion réseau.