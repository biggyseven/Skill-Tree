# VPN Site-to-Site et d'accès distant

## Introduction

Un réseau privé virtuel (VPN) crée un canal protégé au-dessus d’un réseau non entièrement maîtrisé. Un VPN site-à-site relie généralement des réseaux via des passerelles, alors qu’un VPN d’accès distant connecte un utilisateur ou un appareil à l’organisation.

IPsec protège le trafic au niveau IP et IKEv2 sert couramment à négocier paramètres, identités et clés des associations de sécurité. Les deux extrémités doivent être cohérentes sur les algorithmes, sélecteurs de trafic, durées de vie et réseaux concernés.

Un tunnel chiffré ne rend pas automatiquement fiable le poste distant. Il faut aussi contrôler l’identité, limiter les routes et les privilèges, appliquer la MFA à l’accès distant et surveiller l’état des tunnels ainsi que les échecs de négociation.

## Concepts clés

- **Site-to-Site** : tunnel entre passerelles réseau.
- **Accès distant** : connexion d’un utilisateur ou d’un poste.
- **IKEv2** : négociation des paramètres et des clés.
- **Sélecteurs** : flux ou sous-réseaux protégés dans le tunnel.

## Méthode pratique

1. Vérifie les sous-réseaux et leurs éventuels chevauchements.
2. Compare les paramètres IKE/IPsec et les identités.
3. Vérifie routes, filtrage et trafic retour.
4. Ajoute MFA et privilèges minimaux pour l’accès distant.

## À retenir

La sécurité d’un VPN dépend autant des identités et des routes que du chiffrement.
