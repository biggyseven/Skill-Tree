# Skill Tree — Module M3 (React Flow 12)

Ce paquet ajoute les six icônes SVG partagées, les six custom nodes, le `CableEdge`, l'enregistrement `nodeTypes`/`edgeTypes` et un petit canvas Vite de démonstration isolé. Il ne modifie pas l'API FastAPI, SQLite ni les fichiers existants de ces systèmes.

## Chemins livrés

- `static/icons/*.svg` : six icônes SVG demandées.
- `app/lab-workspace/public/icons/*.svg` : mêmes icônes servies directement par Vite.
- `app/lab-workspace/src/canvas/nodes/*.jsx` : composants de nodes et icône inline thémable.
- `app/lab-workspace/src/canvas/edges/CableEdge.jsx` : câble Bezier sélectionnable, avec état up/down et étiquette.
- `app/lab-workspace/src/canvas/nodeTypes.js` : registres stables.
- Un squelette Vite React minimal existe aussi car aucun `package.json` / projet Vite n'était présent dans le checkout inspecté.

## Lancer le canvas de démonstration

Dans PowerShell, depuis la racine du dépôt :

```powershell
cd .pp\lab-workspace
npm install
npm list @xyflow/react reactflow
npm run build
npm run dev
```

Vite affiche ensuite l'URL locale, généralement `http://127.0.0.1:5173`.

## Notes d'implémentation

- Package officiel utilisé : `@xyflow/react` `12.12.0` (et non le package legacy `reactflow`).
- Chaque node est fonctionnel et sans état local.
- Les quatre handles ont des IDs distincts : deux cibles à gauche, deux sources à droite. Les edges de démonstration référencent ces IDs explicitement.
- Les nodes utilisent des SVG inline pour que `currentColor` suive réellement les thèmes clair/sombre. Les six SVG autonomes correspondants sont également présents sous `static/icons/` comme demandé.
- Le canvas de démonstration n'est pas encore raccordé à FastAPI ; ce raccordement peut rester une étape ultérieure.
- Aucun paquet d'icônes tiers n'est ajouté.
