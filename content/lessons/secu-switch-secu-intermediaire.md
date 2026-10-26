# Sécurité des commutateurs (Couche 2)

## Introduction

La couche 2 est exposée aux erreurs et aux attaques qui manipulent les adresses MAC, les VLAN, DHCP, ARP ou Spanning Tree. Un commutateur doit donc être durci même lorsqu’il ne route pas entre les réseaux.

Port Security peut limiter les adresses MAC admises ; DHCP Snooping distingue les ports DHCP approuvés ; Dynamic ARP Inspection peut réduire certaines usurpations ARP. Les trunks doivent être limités aux VLAN nécessaires et les ports inutilisés désactivés.

Les protections STP, comme BPDU Guard sur les ports d’accès appropriés, empêchent un équipement inattendu d’influencer la topologie. Chaque mécanisme doit être configuré selon le rôle du port et supervisé pour éviter les interruptions causées par un mauvais réglage.

## Concepts clés

- **Port Security** : limite ou surveille les adresses MAC par port.
- **DHCP Snooping** : filtre les réponses DHCP venant de ports non fiables.
- **DAI** : contrôle les messages ARP à partir d’informations de confiance.
- **BPDU Guard** : protège les ports d’accès contre des BPDU inattendues.

## Méthode pratique

1. Inventorie les ports et désactive ceux sans usage.
2. Limite les VLAN autorisés sur les trunks.
3. Marque comme fiables uniquement les ports qui le nécessitent.
4. Observe compteurs et journaux après activation.

## À retenir

Les protections L2 doivent correspondre à la topologie et au rôle de chaque port.
