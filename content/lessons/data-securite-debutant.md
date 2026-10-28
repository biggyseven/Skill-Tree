# Chiffrement, RGPD et contrôle d'accès — Débutant

> **Mise en contexte.** Réduire l'exposition des données par classification, autorisation, chiffrement et contrôle du cycle de vie. Le fil rouge est protéger comptes, évaluations et données personnelles d'une plateforme. Travaillez sur des données synthétiques, avec des privilèges limités et un environnement réinitialisable. Vérifiez la documentation officielle de la version avant de transposer une commande ou une garantie.

## Introduction et objectifs

Ce cours relie chiffrement, rgpd et contrôle d'accès au cas concret « protéger comptes, évaluations et données personnelles d'une plateforme ». Il faut comprendre le contrat, la source de vérité, les effets secondaires et les preuves du résultat. Ce niveau vise à apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. À la fin, vous saurez définir des invariants, choisir les contrôles, construire des tests normaux et adversariaux, vérifier le résultat réel, diagnostiquer un incident et documenter les limites. Une absence d'exception ou une capture d'écran ne suffit pas à démontrer l'état métier.

## Prérequis et environnement

Références initiales : https://owasp.org/www-project-top-ten/, https://www.postgresql.org/docs/current/user-manag.html, https://eur-lex.europa.eu/eli/reg/2016/679/oj. Notez versions, paramètres, privilèges et état initial. Préparez une remise à zéro. N'utilisez pas de secrets ou données personnelles réelles. Les exemples doivent isoler les hypothèses pour pouvoir être reproduits par une autre personne.

## 1. Architecture et contrat

Décrivez la source, les producteurs, les transformations, l'état persistant et les consommateurs. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'autorité qui fait foi et les représentations dérivées. Le contrat précise entrées, valeurs admissibles, effets secondaires, erreurs, délais et postconditions. Cette étape distingue réussite technique et résultat fiable pour le métier.

## 2. Concepts essentiels

### 1. Classification des données

Le concept « Classification des données » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier classification des données, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 2. Authentification et autorisation

Le concept « Authentification et autorisation » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier authentification et autorisation, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 3. Moindre privilège

Le concept « Moindre privilège » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier moindre privilège, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 4. Chiffrement en transit

Le concept « Chiffrement en transit » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier chiffrement en transit, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 5. Chiffrement au repos

Le concept « Chiffrement au repos » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier chiffrement au repos, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 6. Gestion des clés

Le concept « Gestion des clés » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier gestion des clés, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 7. Secrets et comptes techniques

Le concept « Secrets et comptes techniques » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier secrets et comptes techniques, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 8. Masquage et minimisation

Le concept « Masquage et minimisation » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier masquage et minimisation, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 9. Audit et détection

Le concept « Audit et détection » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier audit et détection, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

### 10. Rétention et effacement

Le concept « Rétention et effacement » se comprend par la règle métier qu'il protège. Dans « protéger comptes, évaluations et données personnelles d'une plateforme », identifiez l'acteur qui produit l'information, le composant qui la traite et la propriété attendue par le consommateur. Construisez un exemple valide et un contre-exemple. Un test uniquement nominal peut masquer une erreur de modèle, une dépendance implicite ou une protection insuffisante.

Pour vérifier rétention et effacement, notez version, paramètres et préconditions, puis contrôlez la postcondition dans l'état réel. Si le test échoue, examinez données, contrat, droits, configuration et ordre d'exécution séparément. Ne désactivez pas un contrôle pour forcer la réussite. Expliquez le comportement d'une valeur absente, d'un doublon et d'une reprise après interruption, puis indiquez quelles métriques ou quels journaux expurgés permettent le diagnostic.

## 3. Méthode de conception et d'exploitation

### 1. Formaliser les invariants

Écrivez ce qui doit rester vrai dans protéger comptes, évaluations et données personnelles d'une plateforme : intégrité, unicité, ordre, confidentialité, fraîcheur ou état final. Chaque invariant doit être testable et associé à une source de vérité. Donnez un exemple permis et un exemple refusé. Si le résultat ne peut pas être contrôlé, précisez quel signal servira de preuve. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 2. Préparer les entrées

Définissez types, unités, bornes, valeurs optionnelles, provenance et version. Préparez des cas adversariaux : doublon, valeur vide, schéma inconnu, taille inhabituelle ou référence absente. Les données synthétiques permettent de reproduire le cas sans exposer des personnes. Modifiez une hypothèse à la fois et consignez les résultats. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 3. Choisir le contrôle

Placez le contrôle où il peut empêcher l'état invalide : contrainte persistante, validation de contrat, transaction, contrôle d'accès ou test d'intégration. Un contrôle tardif peut signaler l'erreur sans empêcher sa propagation. Séparez garanties, alertes et bonnes pratiques. Vérifiez la portée du mécanisme dans la version réelle. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 4. Gérer les erreurs

Classez les erreurs en entrée invalide, incompatibilité, accès interdit, saturation, conflit concurrent et problème transitoire. Définissez une réponse par catégorie. Les erreurs permanentes sont rejetées ou mises en quarantaine avec une raison exploitable. Une reprise temporaire est bornée et ne répète jamais aveuglément un effet non idempotent. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 5. Protéger les reprises

Un appel peut être répété après timeout, un worker redémarré ou un lot rejoué. Définissez l'identifiant de l'action métier unique et vérifiez le résultat enregistré avant de produire un nouvel effet. Testez reprises séquentielles et concurrentes. Si le traitement déclenche un système externe, décrivez comment réconcilier les états en cas de panne. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 6. Mesurer avant optimisation

Établissez une référence : latence, débit, consommation, fraîcheur, taille ou taux d'erreur. Décrivez le profil de charge. Changez un facteur à la fois et répétez la mesure. Une solution correcte sur quelques lignes peut échouer lorsque volume, distribution ou concurrence changent. L'optimisation doit préserver l'exactitude. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 7. Limiter les privilèges

Séparez les rôles runtime, migration, reporting et administration. Les secrets restent hors du dépôt et les entrées sont paramétrées ou validées. Testez un accès autorisé et un accès interdit par le vrai chemin technique. Les journaux doivent fournir un contexte utile sans recopier les données sensibles. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 8. Faire évoluer sans rupture

Une évolution peut toucher consommateurs, jobs, rapports et scripts. Ajoutez une structure compatible, migrez les données, comparez les résultats et retirez l'ancien chemin après vérification. Le backfill est borné et déterministe. Testez base vide et base historique, puis prévoyez un critère d'arrêt si les écarts dépassent la tolérance. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 9. Rendre l'état observable

Suivez volume, durée, erreurs, fraîcheur, rejets, divergences et ressources. Chaque alerte possède un seuil, un propriétaire et une action documentée. Utilisez des identifiants de corrélation, expurgez les valeurs privées et vérifiez que le signal est actionnable. Une journalisation trop abondante peut devenir un risque de confidentialité. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 10. Préparer la reprise

Décrivez le retour vers un état connu. Comptez les éléments touchés avant réparation, testez sur une copie, définissez un critère d'arrêt et conservez une trace. Après application, vérifiez les invariants et réconciliez les systèmes externes. Redémarrer un service ne prouve pas l'intégrité des données. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 11. Comparer les options

Comparez les mécanismes selon intégrité, simplicité, disponibilité, coût, latence, sécurité et exploitabilité. Une solution plus sophistiquée n'est pas forcément plus robuste si l'équipe ne sait pas l'exploiter. Documentez options, hypothèses, risques acceptés, mesures et conditions de réévaluation. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

### 12. Automatiser les preuves

Les tests couvrent le nominal, une limite, une erreur, un doublon et une reprise. Un test échoue lorsque l'invariant n'est plus respecté et expose le contexte de diagnostic. Gardez les données synthétiques et les scripts versionnés afin qu'un autre opérateur puisse recréer le résultat. Au niveau débutant, il faut apprendre le vocabulaire, mettre en place un exemple sûr et vérifier le résultat. La conclusion distingue les faits observés, les hypothèses et les risques résiduels. Un contrôle n'est acquis que si le test peut être répété et comparé.

## 4. Atelier pratique

### Étape 1 — Définir le contrat

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 2 — Créer un environnement isolé

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 3 — Capturer l'état initial

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 4 — Exécuter le cas nominal

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 5 — Ajouter un cas adverse

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 6 — Simuler un échec contrôlé

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 7 — Rejouer la demande

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 8 — Mesurer une variante

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 9 — Tester les autorisations

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

### Étape 10 — Réinitialiser et documenter

Pour « protéger comptes, évaluations et données personnelles d'une plateforme », écrivez ce qui sera vérifié, préparez des données synthétiques, notez paramètres et observez l'état réel. Ajoutez un cas où la règle doit refuser l'opération. Simulez une interruption dans le laboratoire, vérifiez quels effets ont déjà été appliqués et décrivez le retour à un état connu. Enregistrez les résultats et limites de version. L'étape est terminée lorsque quelqu'un d'autre peut la répéter sans étape cachée.

## 5. Diagnostics guidés

### Cas 1 — résultat incomplet

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à moindre privilège. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 2 — doublon après relance

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à chiffrement en transit. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 3 — latence élevée

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à chiffrement au repos. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 4 — valeur absente mal interprétée

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à gestion des clés. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 5 — version inattendue

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à secrets et comptes techniques. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 6 — accès non autorisé

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à masquage et minimisation. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 7 — opération partielle

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à audit et détection. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 8 — écart entre source et sortie

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à rétention et effacement. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 9 — charge déséquilibrée

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à classification des données. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 10 — consommateur incompatible

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à authentification et autorisation. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 11 — alerte non actionnable

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à moindre privilège. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

### Cas 12 — restauration non démontrée

Dans « protéger comptes, évaluations et données personnelles d'une plateforme », le symptôme peut être lié à chiffrement en transit. Fixez période, versions, entrées et postcondition, puis réduisez le cas jusqu'à obtenir une reproduction minimale. Séparez les hypothèses liées aux données, au contrat, aux privilèges, aux ressources et à l'ordre des opérations. Préservez les journaux utiles sans exposer de secrets. La correction doit préserver les données valides, traiter la cause et pouvoir être rejouée. Confirmez le cas normal et ajoutez une régression automatisée.

## 6. Exercices avec corrigés

### Exercice 1 — Formaliser une règle

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier moindre privilège et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 2 — Choisir un contrôle

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier gestion des clés et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 3 — Identifier la source de vérité

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier audit et détection et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 4 — Gérer une entrée invalide

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier authentification et autorisation et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 5 — Interpréter une mesure

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier chiffrement au repos et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 6 — Protéger une reprise

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier masquage et minimisation et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 7 — Planifier une évolution

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier classification des données et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 8 — Séparer les privilèges

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier chiffrement en transit et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 9 — Détecter une dérive

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier secrets et comptes techniques et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

### Exercice 10 — Prouver une restauration

**Énoncé.** Pour « protéger comptes, évaluations et données personnelles d'une plateforme », expliquez comment vérifier rétention et effacement et prouver le résultat.

**Corrigé.** Définissez préconditions et postconditions, utilisez des données synthétiques et contrôlez l'état réellement obtenu. Ajoutez un test négatif. Consignez versions, entrées, objets touchés, erreurs et limites. Si une reprise est possible, rejouez le même identifiant pour vérifier qu'elle ne produit pas un second effet métier. Expliquez la règle retenue et ce qui reste hors du périmètre du test.

## 7. Études de cas supplémentaires

### Cas d'étude 1 — Moindre privilège

Le symptôme est : traitement incomplet sur données variées. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez moindre privilège, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 2 — Chiffrement au repos

Le symptôme est : demande répétée après timeout. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez chiffrement au repos, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 3 — Secrets et comptes techniques

Le symptôme est : ancienne version active pendant déploiement. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez secrets et comptes techniques, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 4 — Audit et détection

Le symptôme est : résultats différents entre environnements. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez audit et détection, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 5 — Classification des données

Le symptôme est : croissance rapide du volume. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez classification des données, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 6 — Moindre privilège

Le symptôme est : accès hors périmètre. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez moindre privilège, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 7 — Chiffrement au repos

Le symptôme est : job terminé sans preuve de qualité. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez chiffrement au repos, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 8 — Secrets et comptes techniques

Le symptôme est : réparation manuelle sans procédure. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez secrets et comptes techniques, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 9 — Audit et détection

Le symptôme est : optimisation rapide en lecture mais coûteuse en écriture. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez audit et détection, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

### Cas d'étude 10 — Classification des données

Le symptôme est : restauration sans réconciliation. Pour « protéger comptes, évaluations et données personnelles d'une plateforme », collectez versions et paramètres, créez une reproduction réduite et distinguez les causes possibles. Inspectez classification des données, vérifiez les effets déjà appliqués et comparez l'état de référence à l'état obtenu. La solution doit avoir un périmètre borné, une procédure de retour à l'état connu et un contrôle final. Conservez une preuve de correction et un test qui détectera le même défaut en exploitation. Documentez le compromis et le risque résiduel.

## 8. Défi final avec correction

### Énoncé

Concevez une solution pour « protéger comptes, évaluations et données personnelles d'une plateforme » qui applique les principes de chiffrement, rgpd et contrôle d'accès. Livrez contrat d'entrée-sortie, modèle ou architecture, contrôles d'intégrité et de sécurité, tests, métriques et procédure d'exploitation. La solution gère entrée invalide, demande répétée, interruption et évolution de version. Expliquez les garanties démontrées et les risques dépendant de la technologie.

### Correction détaillée

Définissez la source de vérité et les invariants métier. Choisissez le contrôle capable de protéger chacun d'eux : contrainte, validation de contrat, transaction, autorisation ou test de pipeline. Préparez un environnement isolé avec cas nominal, limite et entrée invalide. Enregistrez les versions et contrôlez l'état réel à chaque frontière ; un message de succès ne suffit pas.

Rendez la reprise bornée et répétable, distinguez erreurs permanentes et transitoires et empêchez un rejeu de créer un doublon. Définissez métriques, seuils, propriétaires d'alerte et runbook. Mesurez toute optimisation à charge équivalente. Pour faire évoluer le contrat, maintenez la compatibilité, migrez par étapes, comparez les résultats et retirez l'ancien chemin seulement après validation.

En cas d'incident, préservez les preuves, comptez le périmètre touché et testez la réparation sur copie. Après reprise, vérifiez les invariants et réconciliez les consommateurs externes. Le livrable doit permettre à un autre apprenant de reconstruire l'environnement et de répéter les tests sans étape manuelle cachée.

## 9. Schémas de référence

```mermaid
flowchart TD
 A[Besoin métier] --> B[Contrat et entrées]
 B --> C[Contrôles adaptés]
 C --> D[Traitement]
 D --> E[Résultat observable]
 E --> F[Validation et audit]
 F --> G[Surveillance et reprise]
```

```mermaid
sequenceDiagram
 participant U as Producteur
 participant S as Service
 participant D as Système cible
 U->>S: Demande avec identifiant
 S->>S: Valider contrat et droits
 S->>D: Appliquer opération
 D-->>S: Résultat observable
 S->>S: Vérifier postconditions
 S-->>U: Résultat traçable
```

```mermaid
flowchart LR
 A[Source] --> B[Validation]
 B --> C[Transformation]
 C --> D[Publication]
 D --> E[Contrôle qualité]
 E --> F{Conforme ?}
 F -- Oui --> G[Consommateurs]
 F -- Non --> H[Quarantaine]
```

```mermaid
flowchart TD
 A[Détecter l'écart] --> B[Préserver les preuves]
 B --> C[Identifier la source]
 C --> D[Test sur copie]
 D --> E{Contrôles validés ?}
 E -- Non --> F[Arrêter]
 E -- Oui --> G[Correction bornée]
 G --> H[Vérification finale]
```

```mermaid
flowchart LR
 A[Version actuelle] --> B[Évolution compatible]
 B --> C[Migration vérifiée]
 C --> D[Comparaison]
 D --> E[Validation]
 E --> F[Retrait différé]
```

## 10. Checklist de maîtrise

- Besoin et invariants formalisés.
- Versions, entrées et droits contrôlés.
- Cas normaux, limites, erreurs et répétitions testés.
- Reprises bornées et idempotentes.
- Mesures de qualité et performance disponibles.
- Changements compatibles et vérifiés.
- Logs expurgés de données sensibles inutiles.
- Restauration ou reprise réellement testée.
- Scripts de test reproductibles.
- Hypothèses et risques résiduels documentés.

## 11. Références techniques

- https://owasp.org/www-project-top-ten/
- https://www.postgresql.org/docs/current/user-manag.html
- https://eur-lex.europa.eu/eli/reg/2016/679/oj

Vérifiez la documentation de la version utilisée avant toute commande en production. Les règles internes de sécurité, conformité et exploitation complètent ces références.
