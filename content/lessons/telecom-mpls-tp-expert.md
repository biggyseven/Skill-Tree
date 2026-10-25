# MPLS-TP & Métro Ethernet — Expert

**Module :** Opérateurs & Télécoms · **Catégorie :** Télécoms  
**Identifiant de cours :** `telecom-mpls-tp-expert`

## Objectifs pédagogiques
- Concevoir transport déterministe avec OAM, protection et objectifs de restauration.
- Analyser protection linéaire/chemin, défauts, réversion et risques de boucles.
- Définir QoS, ingénierie de capacité, MTU et segmentation de services.
- Établir des procédures d’acceptation, de maintenance et de RCA.

## Architecture et modèle mental
```text
CE — UNI — PE — LSP de travail ║ LSP de protection — PE — UNI — CE ; OAM surveille continuité et défauts.
```

Les équipements et interfaces exacts dépendent du fournisseur et de la version. Distinguer systématiquement le plan de contrôle, le plan de données, les services de gestion et le procédé métier. Avant une intervention, définir le périmètre, les critères de succès, les risques et le retour arrière.

## Méthode de travail
1. **Observer** l’état initial, les compteurs, les journaux et les dépendances.
2. **Formuler une hypothèse** à partir d’un symptôme mesurable plutôt que de modifier plusieurs paramètres à la fois.
3. **Tester en environnement maîtrisé** et conserver les résultats avant/après.
4. **Appliquer un changement limité**, autorisé et réversible.
5. **Valider de bout en bout** avec un test fonctionnel et des métriques techniques.
6. **Documenter** configuration, limites connues, décisions et plan de retour arrière.

## Travaux pratiques
Construire une matrice service/LSP, capacité réservée, classe QoS, délai de restauration cible, seuils d’alarme et critères de bascule ; simuler une coupure en laboratoire.

### Livrables attendus
- Schéma annoté avec les frontières, interfaces et flux concernés.
- Tableau de paramètres et de mesures, avec unités et horodatages.
- Hypothèse de panne, preuves collectées et conclusion justifiée.
- Plan de validation et procédure de retour arrière.

## Erreurs fréquentes et garde-fous
**À éviter :** Une protection configurée n’est pas prouvée avant un test contrôlé. Vérifier chemin réellement indépendant, convergence, pertes, réversion et impact sur les autres services.

En production, respecter les autorisations, les fenêtres de changement et les règles de sécurité. Ne jamais inclure de secrets, données clients ou identifiants réels dans les captures et comptes rendus. Les commandes exactes varient selon la plateforme : vérifier la documentation constructeur et tester avant application.

## Exercices corrigés
1. **Pourquoi faut-il mesurer avant de modifier ?** Pour disposer d’un état de référence, tester l’hypothèse et pouvoir prouver l’effet réel du changement.
2. **Une seule métrique confirme-t-elle toujours la cause ?** Non. Croiser plusieurs sources et vérifier les dépendances de bout en bout.
3. **Que faire si le changement dégrade le service ?** Arrêter la progression, appliquer le retour arrière validé, confirmer le rétablissement et conserver les preuves.

## Défi final corrigé
**Scénario :** Défi : une coupure déclenche la protection mais le trafic reste perdu. Vérifier détection OAM, association du chemin de protection, capacité disponible, MTU et configuration aux deux extrémités ; documenter les preuves.

**Correction attendue :** établir l’état initial, délimiter le domaine de panne, collecter des preuves non intrusives, tester une hypothèse à la fois, appliquer une correction limitée et réversible, puis vérifier le service et les indicateurs avant/après. Le rapport final doit expliquer la cause retenue, les autres hypothèses écartées, les risques résiduels et les actions préventives.

## Checklist de validation
- [ ] Objectif et périmètre documentés.
- [ ] Mesures initiales enregistrées.
- [ ] Changement testé et approuvé.
- [ ] Résultat fonctionnel et technique vérifié.
- [ ] Retour arrière connu et compte rendu terminé.
