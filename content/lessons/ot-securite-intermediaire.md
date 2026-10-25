# Cybersécurité OT — Intermédiaire

**Module :** Réseaux Industriels (OT) · **Catégorie :** OT/ICS  
**Identifiant de cours :** `ot-securite-intermediaire`

## Objectifs pédagogiques
- Construire des zones et conduits à partir de la criticité et des communications nécessaires.
- Concevoir une DMZ industrielle pour éviter les chemins directs entre IT et automates.
- Contrôler les accès fournisseurs, comptes privilégiés et stations d’ingénierie.
- Définir une gestion des changements, une surveillance passive et une réponse initiale aux incidents.

## 1. Zones et conduits
Une **zone** regroupe des actifs partageant des exigences de sécurité similaires. Un **conduit** définit les communications autorisées entre zones. La segmentation doit être fondée sur l’inventaire et la connaissance des flux, pas seulement sur les sous-réseaux IP.

Pour chaque flux, documenter :
- source et destination précises ;
- protocole, port et sens d’initiation ;
- justification opérationnelle et propriétaire ;
- fréquence, fenêtre et impact d’une interruption ;
- méthode de test et preuve de validation.

Appliquer le refus par défaut, mais ne pas activer une règle de blocage sans avoir identifié les dépendances du procédé.

## 2. Architecture de référence
```text
Réseau IT
   |
[Pare-feu IT/DMZ]
   |
DMZ industrielle
  +-- Bastion avec MFA
  +-- Relais de fichiers contrôlés
  +-- Réplication Historian
   |
[Pare-feu industriel : règles explicites]
   |
Zone SCADA / HMI / serveurs OT
   |
[Frontière de cellule]
   |
PLC / DCS / équipements de terrain
```
Les services de la DMZ ne doivent pas devenir un pont général entre IT et OT. Les transferts de fichiers doivent être contrôlés et les accès d’administration doivent passer par des chemins prévus.

## 3. Identité et accès fournisseur
- Utiliser des comptes nominatifs, MFA pour les accès distants et le moindre privilège.
- Activer l’accès fournisseur uniquement après approbation, pour une durée définie.
- Séparer les comptes d’administration IT, d’ingénierie OT et les comptes de service.
- Retirer les accès devenus inutiles et protéger les secrets.
- Journaliser les connexions et, lorsque cela est adapté, les sessions de bastion.
- Préparer un processus d’urgence sans réutiliser un compte partagé permanent.

## 4. Gestion des vulnérabilités et changements
Une vulnérabilité doit être évaluée selon l’exposition, l’impact sur la sûreté, les possibilités de mitigation, la compatibilité et la fenêtre de maintenance. Le correctif doit être testé sur une plateforme représentative lorsque c’est possible. Prévoir sauvegarde, approbation, critères de succès et retour arrière avant le changement.

Les scans actifs peuvent perturber certains équipements anciens. Privilégier l’inventaire passif et les sources constructeur lorsque les tests actifs ne sont pas explicitement autorisés.

## 5. Surveillance et réponse
Établir une baseline des communications normales. Rechercher les nouveaux flux, connexions hors fenêtre, scans, changements de logique PLC et accès d’ingénierie inattendus. Corréler les journaux de pare-feu, bastion, stations d’ingénierie et serveurs de supervision.

En cas d’alerte : protéger les personnes, alerter l’équipe OT, préserver les preuves, évaluer le rôle de l’actif et choisir le confinement avec les responsables du procédé. Une isolation brutale peut supprimer des fonctions de contrôle ou de supervision.

## TP — Matrice de flux minimale
À partir d’un schéma comprenant IT, DMZ, SCADA, Historian, station d’ingénierie et deux cellules PLC :
1. Construire la matrice source/destination/protocole/sens/justification.
2. Identifier les flux directs IT → PLC à supprimer après validation.
3. Définir l’accès fournisseur via bastion, MFA, approbation et expiration.
4. Rédiger une procédure de changement avec sauvegarde et retour arrière.
5. Décrire une méthode passive pour enquêter sur un nouveau flux vers un PLC.

## Exercices corrigés
1. **Pourquoi les zones ne correspondent-elles pas toujours à des VLAN ?** Une zone représente une frontière de confiance et des exigences de sécurité ; plusieurs réseaux peuvent appartenir à une zone, et un VLAN seul ne fournit pas une politique complète.
2. **Quel est l’intérêt de la DMZ ?** Servir d’intermédiaire contrôlé pour les services partagés, sans autoriser un accès direct généralisé.
3. **Pourquoi tester les correctifs ?** Pour réduire le risque d’incompatibilité, de redémarrage imprévu ou de perturbation du procédé.
4. **Quelle est la première réaction à un flux anormal ?** Préserver les preuves et coordonner l’analyse avec l’équipe OT avant toute action susceptible d’affecter la production.

## Défi final corrigé
Une station d’ingénierie initie des communications vers un PLC qu’elle ne devrait pas gérer. Préserver les journaux, confirmer la relation par observation passive, vérifier la fenêtre de maintenance et contacter l’équipe OT. Si le risque est confirmé, suspendre l’accès par le mécanisme contrôlé le moins perturbateur, protéger la configuration du PLC, rechercher la cause et valider le fonctionnement avant de rétablir les accès. Documenter les règles correctives et les tests de non-régression.

## Références
- IEC 62443 : https://www.iec.ch/
- NIST SP 800-82 Rev. 3 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
- CISA Industrial Control Systems : https://www.cisa.gov/topics/industrial-control-systems
