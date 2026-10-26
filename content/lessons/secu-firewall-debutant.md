# Introduction aux pare-feu

## Introduction

Un pare-feu contrôle les flux réseau selon une politique définie : adresses source et destination, ports, protocoles, interfaces et parfois état des connexions ou contenu applicatif. Il peut être logiciel sur un hôte, intégré à un routeur ou déployé comme équipement dédié.

Une politique sûre autorise explicitement les communications nécessaires et bloque le reste, avec des règles documentées et ordonnées. Un pare-feu à états suit les connexions pour distinguer le trafic associé à une session autorisée des paquets inattendus ; un pare-feu applicatif peut appliquer des contrôles plus proches des protocoles métier.

Un pare-feu ne corrige pas toutes les vulnérabilités : il faut également sécuriser les endpoints, gérer les identités, journaliser les événements et réviser les règles. Tu apprendras à lire une règle, à comprendre le sens entrant ou sortant et à vérifier qu’une exception ne crée pas une ouverture excessive.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- expliquer les concepts fondamentaux associés à ce sujet ;
- reconnaître les erreurs courantes et leurs conséquences ;
- choisir des mesures de protection proportionnées et justifier leur utilité.

## Démarche pratique

1. Identifie l’actif à protéger et le besoin de sécurité concerné.
2. Décris le scénario de risque sans confondre menace, faiblesse et impact.
3. Choisis un contrôle adapté, puis vérifie son fonctionnement.
4. Documente le résultat et prévois une révision régulière.

## À retenir

La cybersécurité repose sur plusieurs couches de protection, une configuration maintenue et une vérification régulière. Aucun outil isolé ne suffit à supprimer tous les risques.
