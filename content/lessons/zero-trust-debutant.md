## node_id: zero-trust-debutant

title: Architecture Zero Trust - Débutant

# Architecture Zero Trust - Débutant

**Niveau :** Débutant  
**Prérequis :** Notions de base en réseau (IP, DNS, modèle OSI) et en sécurité informatique (mots de passe, authentification, pare-feu).

Ce module introduit le paradigme moderne de sécurité informatique **Zero Trust** (Confiance Zéro). Il explique la transition de la sécurité périmétrique traditionnelle vers un modèle axé sur l'identité et la vérification continue.

---

## 1. Du Modèle Traditionnel au Zero Trust

### La Sécurité Périmétrique (« Château et Fossé »)

Pendant des décennies, la sécurité des réseaux reposait sur le modèle périmétrique :
* **Réseau Interne (Intranet) :** Supposé sûr et digne de confiance.
* **Réseau Externe (Internet) :** Considéré comme hostile.
* **Périmètre :** Protégé par des pare-feux, des VPN et des IDS/IPS.

```
       [ INTERNET ] (Hostile)
            │
            ▼
   ┌─────────────────┐
   │    Pare-feu     │  <-- Le "Fossé"
   └────────┬────────┘
            │
   ────────────────────────────── Périmètre de confiance
            │
   ┌────────┴────────┐
   │ Réseau Interne  │  <-- Le "Château" (Confiance implicite)
   │  (Serveurs, IP) │
   └─────────────────┘
```

**Le Problème :** Une fois le périmètre franchi (ex: phishing, compromis de compte, mouvement latéral), l'attaquant bénéficie d'une confiance implicite sur l'ensemble du réseau interne.

---

## 2. Les Principes Fondamentaux du Zero Trust

Le modèle Zero Trust repose sur le principe central : **« Ne jamais faire confiance, toujours vérifier »** (*Never Trust, Always Verify*).

```
          ┌────────────────────────────────────────────────────────┐
          │                    IDENTITÉ & APPAREIL                 │
          └───────────────────────────┬────────────────────────────┘
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │    ÉVALUATION DU CONTEXTE & POLITIQUES           │
             │   - Utilisateur vérifié ?                        │
             │   - Appareil conforme ?                          │
             │   - Contexte réseau / heure cohérent ?           │
             └────────────────────────┬─────────────────────────┘
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │       ACCÈS STRICTEMENT LIMITÉ & ÉPHÉMÈRE        │
             │            (Privilège Minimum - Least Privilege) │
             └──────────────────────────────────────────────────┘
```

### Les 3 Piliers Clés :

1. **Vérifier Explicitement (*Verify Explicitly*) :** Authentifier et autoriser systématiquement en fonction de toutes les données contextuelles disponibles (identité de l'utilisateur, état de l'appareil, localisation, comportement, type de ressource).
2. **Appliquer le Moindre Privilège (*Least Privilege Access*) :** Limiter l'accès au strict minimum nécessaire (*Just-In-Time* et *Just-Enough-Access* - JIT/JEA).
3. **Supposer la Compromission (*Assume Breach*) :** Concevoir le système en partant du principe qu'un composant est déjà compromis :
   * Chiffrer tout le trafic (en transit et au repos).
   * Micro-segmenter le réseau pour empêcher les déplacements latéraux.
   * Collecter les télémétries et analyser le comportement en temps réel.

---

## 3. Les Composants d'une Architecture Zero Trust

L'architecture NIST SP 800-207 définit la structure standard d'un environnement Zero Trust :

```
    [ Demande d'Accès ] 
            │
            ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                 Control Plane (Plan de Contrôle)                │
  │                                                                 │
  │   ┌──────────────────────────┐    ┌──────────────────────────┐  │
  │   │  Policy Engine (PE)      │───>│ Policy Administrator(PA) │  │
  │   │  (Moteur de Décision)    │    │ (Générateur d'Accès)     │  │
  │   └──────────────────────────┘    └────────────┬─────────────┘  │
  └────────────────────────────────────────────────┼────────────────┘
                                                   │ Ordre d'accès
                                                   ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                   Data Plane (Plan de Données)                  │
  │                                                                 │
  │  [ Sujet / Client ] ──────────> ┌──────────────────────────┐    │
  │                                 │ Policy Enforcement Point │    │
  │                                 │ (PEP - Exécutant)        │    │
  │                                 └────────────┬─────────────┘    │
  │                                              │                  │
  │                                              ▼                  │
  │                                        [ Ressource ]            │
  └─────────────────────────────────────────────────────────────────┘
```

* **Policy Enforcement Point (PEP) :** Composant qui intercepte, inspecte et autorise/bloque la connexion entre un sujet et une ressource.
* **Policy Engine (PE) :** Le "cerveau" qui évalue les règles de sécurité et prend la décision d'accorder ou de refuser l'accès.
* **Policy Administrator (PA) :** Composant qui communique avec le PEP pour établir ou fermer la session autorisée par le PE.

---

## 4. Vocabulaire Essentiel

| Terme | Description |
| :--- | :--- |
| **MFA (Multi-Factor Authentication)** | Validation de l'identité par au moins deux facteurs distincts (ex: Mot de passe + Application Authenticator). |
| **SSO (Single Sign-On)** | Authentification unique permettant d'accéder à plusieurs applications avec un seul jeu d'identifiants. |
| **Microsegmentation** | Découpage fin du réseau en zones isolées pour empêcher le mouvement latéral des attaques. |
| **IdP (Identity Provider)** | Service qui gère et authentifie les identités numériques (ex: Microsoft Entra ID, Okta). |
| **ZTNA (Zero Trust Network Access)** | Technologie remplaçant le VPN traditionnel en accordant un accès granulaire applicatif par applicatif. |

---

## 5. Bonnes Pratiques pour débuter la transition

1. **Identifier les Ressources Critiques (DAAS) :**
   * **Data** (Données sensibles)
   * **Applications** (Systèmes métiers)
   * **Assets** (Équipements et objets IoT)
   * **Services** (DNS, Active Directory, API)
2. **Généraliser le MFA et le SSO :** Bloquer toute authentification mono-facteur.
3. **Éliminer la confiance basée sur l'adresse IP :** Une IP interne ne doit plus garantir un accès direct à un service.
4. **Visibilité & Monitoring :** Centraliser les logs (SIEM) pour détecter immédiatement tout comportement anormal.

---

## Points à retenir

* Zero Trust n'est pas un produit unique, mais une **stratégie/architecture de sécurité**.
* L'identité (Utilisateur + Appareil) devient le **nouveau périmètre**.
* Toute demande d'accès doit être **authentifiée, autorisée et chiffrée** indépendamment du réseau d'origine.
* Supposer l'attaque (*Assume Breach*) permet d'isoler rapidement les menaces grâce à la **microsegmentation**.