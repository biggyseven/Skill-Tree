# QoS Voix et Vidéo — Débutant

**Module :** Voix & Collaboration · **Catégorie :** Voix  
**Identifiant de cours :** `voice-qos-debutant`

## Objectifs pédagogiques
- Comprendre délai, gigue, perte et bande passante pour les médias temps réel.
- Distinguer classification, marquage DSCP, files et congestion.
- Connaître EF (DSCP 46) comme marquage courant de la voix RTP, selon politique.
- Comprendre pourquoi la QoS doit être cohérente de bout en bout.

## Architecture et modèle mental
```text
Téléphone (marquage) → switch (classification/file) → routeur (congestion) → réseau → téléphone.
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
Mesurer latence, perte et gigue dans un scénario contrôlé ; vérifier le marquage DSCP et les compteurs de files.

### Livrables attendus
- Schéma annoté avec les frontières, interfaces et flux concernés.
- Tableau de paramètres et de mesures, avec unités et horodatages.
- Hypothèse de panne, preuves collectées et conclusion justifiée.
- Plan de validation et procédure de retour arrière.

## Erreurs fréquentes et garde-fous
**À éviter :** La QoS ne crée pas de bande passante supplémentaire. Le marquage seul n’assure pas un traitement prioritaire.

En production, respecter les autorisations, les fenêtres de changement et les règles de sécurité. Ne jamais inclure de secrets, données clients ou identifiants réels dans les captures et comptes rendus. Les commandes exactes varient selon la plateforme : vérifier la documentation constructeur et tester avant application.

## Exercices corrigés
1. **Pourquoi faut-il mesurer avant de modifier ?** Pour disposer d’un état de référence, tester l’hypothèse et pouvoir prouver l’effet réel du changement.
2. **Une seule métrique confirme-t-elle toujours la cause ?** Non. Croiser plusieurs sources et vérifier les dépendances de bout en bout.
3. **Que faire si le changement dégrade le service ?** Arrêter la progression, appliquer le retour arrière validé, confirmer le rétablissement et conserver les preuves.

## Défi final corrigé
**Scénario :** Exercice : audio haché pendant les sauvegardes. Examiner congestion, perte et gigue, puis proposer classification et file voix sans sur-prioriser tout le trafic.

**Correction attendue :** établir l’état initial, délimiter le domaine de panne, collecter des preuves non intrusives, tester une hypothèse à la fois, appliquer une correction limitée et réversible, puis vérifier le service et les indicateurs avant/après. Le rapport final doit expliquer la cause retenue, les autres hypothèses écartées, les risques résiduels et les actions préventives.

## Checklist de validation
- [ ] Objectif et périmètre documentés.
- [ ] Mesures initiales enregistrées.
- [ ] Changement testé et approuvé.
- [ ] Résultat fonctionnel et technique vérifié.
- [ ] Retour arrière connu et compte rendu terminé.
