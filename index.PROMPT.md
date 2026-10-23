# Prompt d'utilisation : `index.html` (application Skill Tree)

Ce fichier accompagne `index.html`. Il explique comment installer la version corrigée, comment la tester, et quel prompt donner à ton outil de codage IA si un problème persiste.

---

## 1. Installation

1. Sauvegarde ton `index.html` actuel (par exemple `index.before.html`).
2. Remplace-le par le nouveau `index.html`, au même emplacement (le dossier servi par ton backend).
3. Vide le cache du navigateur : `Ctrl + Maj + R` (Windows/Linux) ou `Cmd + Maj + R` (Mac).
4. Ouvre la console du navigateur (`F12`, onglet Console) pour voir d'éventuelles erreurs rouges.

---

## 2. Ce qui a changé

| Zone | Correctif |
|---|---|
| Surface du cours | Fond **toujours sombre** (`.modal-panel`), même si le contenu injecté apporte ses propres couleurs |
| Textes du cours | Couleurs **forcées** (`!important`) sur paragraphes, listes, liens, titres, résumés, tableaux |
| Callouts | Fonds sombres pleins + texte clair (plus de vert clair sur vert clair) |
| Blocs de code | Texte `#e4e4e7`, police mono, pas de retour à la ligne, largeur 100 % |
| Tableaux | Pleine largeur, texte qui passe à la ligne ; défilement seulement si le tableau ne peut vraiment pas tenir |
| Schémas HTML (`<figure>`) | Rendus dans une carte claire avec texte foncé (ils sont conçus pour fond clair) |
| Cloche, profil, engrenage, boutique | Ils s'ouvraient puis se refermaient aussitôt : `@click.stop` sur le bouton et `@click.outside` sur le menu |
| Profil | Menu intégré à la place de `prompt()` (souvent bloqué dans les navigateurs intégrés) |
| Menu latéral | Retrait du fondu `x-transition` des onglets, retour en haut de page et `try/catch` dans `setTab` |
| Démarrage | Suppression du `x-init="init()"` en double (Alpine appelle déjà `init()`) |
| Cours | En-tête `## node_id` / `title:` masqué, balises HTML indentées de 4 espaces ou plus dé-indentées |

---

## 3. Checklist de test

- [ ] Clic sur la cloche : le menu reste ouvert ; clic ailleurs : il se ferme.
- [ ] Clic sur l'avatar : champ « Nom affiché » ; valider avec OK change le nom dans la barre latérale.
- [ ] Clic sur l'engrenage : menu (thème, rechargement, sauvegarde).
- [ ] Clic sur le diamant : la boutique s'ouvre ; clic sur le fond sombre : elle se ferme.
- [ ] Menu latéral : chaque entrée (Tableau de bord, Topologie, Radar, Mémo, Diagnostic, Examen) change bien le contenu.
- [ ] Ouvre un cours : titres blancs, texte gris clair, liens cyan, encadrés lisibles.
- [ ] Un bloc de code : texte clair, bouton Copier, défilement horizontal seulement pour les lignes très longues.
- [ ] Un tableau : il tient dans la largeur, sans barre de défilement.
- [ ] La console ne montre aucune erreur rouge.

---

## 4. Prompt à copier si un problème persiste

Colle ce prompt dans ton outil de codage IA avec le fichier `index.html` et **une capture d'écran du problème** :

```text
Rôle : expert frontend (Tailwind CSS + Alpine.js).
Contexte : voici mon index.html d'application de cours réseau (thème sombre). La version jointe a déjà reçu
des correctifs de contraste, de blocs de code, de tableaux et de menus (voir le fichier index.PROMPT.md).
Problème restant : [décris ce que tu vois et où, avec la capture].
Informations utiles : [colle ici les erreurs rouges de la console, ou les 15 premières lignes HTML du cours concerné].
Contraintes : ne change pas la structure globale ni le design de la page d'accueil ; modifie le minimum de CSS et
d'attributs Alpine.js nécessaire ; renvoie le fichier index.html complet et la liste exacte des lignes modifiées.
```

---

## 5. Si un schéma de cours reste illisible

Les schémas animés des cours sont du HTML intégré dans le Markdown. Le style les traite comme des cartes claires quand ils sont dans un `<figure>`, ou dans un élément ayant la classe `figure`, `lesson-figure` ou `diagram`.

Si ton schéma utilise une autre balise ou une autre classe, copie les 10 premières lignes de son HTML et indique-les à ton outil de codage IA : il ajoutera ce nom de classe à la règle « Figures / schémas HTML intégrés aux cours » dans le `<style>`.
