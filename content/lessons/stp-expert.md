# MSTP, Sécurité et Convergence Avancée

**Niveau :** Administrateur Réseau Senior / Expert

Dans un grand réseau avec 500 VLANs, faire tourner une instance STP par VLAN (PVST+) consomme énormément de CPU. De plus, un utilisateur malveillant pourrait brancher un switch et devenir Root Bridge. Bienvenue dans le monde de MSTP et de la sécurité STP.

> **Analogie** : MSTP, c'est comme faire du covoiturage. Au lieu d'avoir 500 voitures (VLANs) qui font le même trajet, on regroupe les passagers par destination (Instances MST) pour optimiser l'espace.


## 1. MSTP (Multiple Spanning Tree Protocol - 802.1s)

MSTP permet de regrouper plusieurs VLANs dans une même **instance STP**. Par exemple : les VLANs 10 et 20 utilisent l'Instance 1, et les VLANs 30 et 40 utilisent l'Instance 2. Vous pouvez ainsi équilibrer la charge (Load Balancing) sur différents liens.

```text
Switch(config)# spanning-tree mode mst
Switch(config)# spanning-tree mst configuration
Switch(config-mst)# name MON_RESEAU
Switch(config-mst)# instance 1 vlan 10,20
2. La Sécurisation de STP (STP Hardening)
STP est un protocole vulnérable. N'importe qui peut brancher un switch et envoyer des BPDU pour perturber le réseau.

A. BPDU Guard (Protection des ports d'accès)
Si un utilisateur branche un switch sur sa prise murale (port configuré avec PortFast), il pourrait envoyer des BPDU et devenir Root Bridge. BPDU Guard écoute les BPDU sur les ports PortFast. Si un BPDU est reçu, le port passe immédiatement en err-disabled (bloqué).

text
interface FastEthernet0/1
 spanning-tree portfast
 spanning-tree bpduguard enable
B. Root Guard (Protection contre les Root Bridge pirates)
Empêche un switch non autorisé de devenir Root Bridge. Si un BPDU avec une priorité plus basse est reçu sur ce port, le switch le met en état "root-inconsistent" (bloqué).

text
interface GigabitEthernet0/1
 spanning-tree guard root
C. Loop Guard (Protection contre les liens unidirectionnels)
Si un câble est défectueux et ne transporte les BPDU que dans un sens, le switch pourrait croire que la topologie a changé et créer une boucle. Loop Guard empêche cela.

3. Les attaques par manipulation de la topologie
Un pirate peut envoyer de faux BPDU pour se déclarer Root Bridge. S'il devient Root Bridge, tout le trafic passe par son PC, il peut alors l'intercepter (Man-in-the-Middle).

🛑 Danger : Un mauvais design STP (par exemple, un Root Bridge dans un bureau) peut entraîner des latences énormes. Le Root Bridge doit toujours être le switch le plus central de votre réseau.