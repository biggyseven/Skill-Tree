# Hachage et signatures

## Introduction

Une fonction de hachage cryptographique transforme une entrée de longueur quelconque en une empreinte de longueur fixe. Une fonction adaptée doit notamment rendre difficile la recherche d’une entrée correspondant à une empreinte et la découverte de deux entrées ayant la même empreinte.

Le hachage n’est pas du chiffrement : il ne permet pas de retrouver directement le message d’origine. Il sert à vérifier l’intégrité de fichiers, à construire des signatures numériques et à stocker les mots de passe avec des fonctions spécialisées, un sel unique et des paramètres de coût adaptés.

Une signature numérique combine une empreinte du message et une clé privée ; la vérification utilise la clé publique correspondante. Elle permet de vérifier l’origine et l’intégrité, mais ne rend pas automatiquement le contenu confidentiel. Tu apprendras à choisir le mécanisme approprié selon le besoin.

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
