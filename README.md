# Skilltree

Application d'apprentissage réseau : arbre de compétences, validation par preuve
(quiz, lab, examen blanc, preuve manuelle).

## Exercices de saisie et sauvegardes

Les fichiers `content/quiz/<node_id>.json` et `content/exam/<node_id>.json`
acceptent les types `input` et `terminal`. Ils attendent une réponse texte dans
`answer`, un motif Python regex dans `regex`, et une explication facultative.
Les motifs terminaux sont comparés sans distinction de casse et les espaces
successifs de la commande sont normalisés.

```bash
python main.py backup
```

Cette commande crée dans `backups/` un instantané SQLite cohérent et une archive
ZIP de `content/`. La base utilise le journal SQLite WAL avec `synchronous=NORMAL`
pour mieux tolérer les arrêts brutaux tout en conservant de bonnes performances.

## Session du jour et radar

Le dashboard « Session du jour » interroge `GET /api/daily-plan` et propose
jusqu'à trois actions : réviser un nœud validé depuis plus de trois jours,
continuer un lab ou un défi commencé, ou découvrir un nœud disponible.

L'onglet Radar interroge `GET /api/stats`. Il agrège les tentatives par
catégorie, affiche le taux de réussite, le nombre de tentatives par nœud et les
nœuds ayant demandé plus de trois essais.

## Rechargement du contenu

Le bouton « Recharger les cours » de l'en-tête appelle
`POST /api/reload-content`. La route recharge `content/nodes.json`, les
exercices et les labs dans SQLite, puis l'interface rafraîchit l'arbre et la
session du jour. Les leçons Markdown sont relues depuis `content/lessons/` à
chaque ouverture d'un nœud.

## Thème et confort de lecture

Le bouton soleil/lune de l'en-tête bascule entre le thème sombre et le thème
clair `slate`. Le choix est conservé dans `localStorage` et appliqué avant le
premier rendu pour éviter un flash.

Les cours Markdown utilisent `@tailwindcss/typography` (chargé via CDN) avec
`prose` / `prose-invert`, une police de code JetBrains Mono / Fira Code et des
blocs `<pre>` à défilement horizontal. Le terminal des labs reprend l'apparence
d'une fenêtre VS Code avec en-tête, boutons de fenêtre, commandes cyan et
sorties grises.

La modale de cours propose un mode plein écran, une lecture vocale via
`edge-tts` et un bouton « Copier » sur chaque bloc de code. Le bouton « Passer à
l'exercice » reste collé en bas de la zone de lecture, qui est séparée
visuellement des exercices. Dans le terminal, `clear` et `cls` vident l'écran.
Le canvas de topologie utilise une hauteur de `85vh` et peut être exporté en PNG
avec `html2canvas`.

## Mémo et aide-mémoire

L'onglet « Mémo » charge `GET /api/flashcards`, qui lit
`content/flashcards/network.json`. Les cartes se retournent en 3D ; « Je savais »
retire la carte de la pile et « Je ne savais pas » la replace à la fin.

Dans un lab Docker, le bouton « Aide-mémoire » ouvre un panneau latéral
superposé au terminal avec les commandes Linux/IP, bridge et Cisco les plus
utiles. Le panneau se ferme par le bouton, le fond ou `Échap`.

## Voix, tuteur et sandbox

Le bouton « Écouter » appelle `GET /api/node/{node_id}/tts`. La route convertit
le Markdown en texte, génère un MP3 temporaire avec `edge-tts` et le renvoie en
streaming. La voix par défaut est `fr-FR-DeniseNeural` ; `fr-FR-HenriNeural` est
aussi acceptée.

Le bouton flottant « Poser une question » ouvre le tuteur IA. La route
`POST /api/node/{node_id}/ask` envoie le cours Markdown du nœud comme contexte
et la question à Groq (`llama-3.3-70b-versatile` par défaut, avec
`openai/gpt-oss-20b` en secours). Copie `.env.example` vers `.env`, renseigne
`GROQ_API_KEY`, puis redémarre le serveur. Le modèle peut être changé avec
`GROQ_MODEL`. Une ancienne valeur `llama3-8b-8192` est automatiquement remplacée
par le modèle principal. L'interface affiche un spinner pendant l'appel.

Pour les exercices `terminal`, le mode « Sandbox CLI » vérifie les commandes
contre `content/sandbox/cisco_basics.json` via
`POST /api/sandbox/check`, sans lancer Docker.

Le header affiche un streak basé sur la table `daily_streak`. Chaque tentative
enregistrée ajoute 5 minutes au jour courant ; `GET /api/streak` calcule les
jours consécutifs. Sans activité, le streak vaut 0 ; après une rupture de plus
d'un jour, le compteur repart à 1.

## Gamification : XP et niveaux

La table singleton `user_stats` conserve `total_xp` et `current_level` ;
`GET /api/user-stats` renvoie aussi le nom du niveau, le palier suivant et la
progression. Les gains sont attribués uniquement en cas de réussite :

| Preuve | XP |
|---|---:|
| Exercice (`quiz`) ou terminal | +10 |
| Lab | +50 |
| Examen | +100 |
| Diagnostic interactif | +20 |

Paliers : niveau 1 « Débutant » (0 XP), niveau 2 « Technicien » (500 XP),
niveau 3 « Admin » (1 500 XP), niveau 4 « Senior » (3 000 XP). Le badge du
header affiche le niveau, les XP totaux et une barre vers le palier suivant.

## Profil et certificat

`GET /api/profile` regroupe le streak, les nœuds validés, le pourcentage de
progression, le nombre de labs validés, les examens réussis et le niveau XP.
Le bandeau du Dashboard affiche ces accomplissements sous forme de badges. Le
bouton « Voir mon certificat » ouvre un certificat imprimable dont le nom vient
de `CERTIFICATE_NAME` dans `.env` (valeur par défaut : `Ton Nom`).

## Diagnostic interactif

`GET /api/diagnostics/{diag_id}` renvoie un arbre de décision public (sans les
flags de correction) depuis `content/diagnostics/`. L'onglet « Diagnostic »
affiche la situation, les choix et le parcours. À la fin,
`POST /api/diagnostics/{diag_id}/complete` valide le chemin et attribue les XP
si toutes les décisions sont correctes.

## Export de la topologie

Le canvas Drawflow peut être sauvegardé en base, téléchargé en JSON ou exporté
en PNG. L'export PNG utilise `html2canvas` depuis un CDN et télécharge
`topologie.png` dans le thème courant (fond noir ou `slate` clair).

## Mode examen

L'onglet Examen interroge `POST /api/exam/generate` avec une catégorie. L'API
tire jusqu'à 20 questions parmi les exercices des nœuds de cette catégorie et
crée une session serveur de 30 minutes. Les réponses et explications ne sont
pas renvoyées avant la soumission.

`POST /api/exam/submit` corrige la session, calcule le score et renvoie le
détail. Un examen est validé au-delà de 85 % ; le chronomètre est géré côté
interface et la session serveur conserve l'heure d'expiration.

## Labs Docker

Les labs Docker exécutent de vraies commandes dans un conteneur jetable, puis
valident l'état obtenu avec un script shell.

### Construire l'image

```bash
docker build -t skilltree/lab:latest docker/lab
```

Vérifier la présence de Docker et de l'image :

```bash
docker version
docker image inspect skilltree/lab:latest
```

### Formats de lab

Un lab texte (ancien format), corrigé par comparaison de texte :

```
content/labs/<node_id>.json
```

Un lab Docker, exécuté dans un conteneur. Le nom du dossier est libre ; c'est
`lab.json.node_id` qui identifie le nœud (un seul lab Docker par nœud) :

```
content/labs/lab_ospf/
├── lab.json      métadonnées, dont node_id
├── setup.sh      préparation de l'environnement (exécuté avant l'utilisateur)
├── consigne.md   consigne affichée telle quelle
└── check.sh      retourne 0 si l'état attendu est atteint, 1 sinon
```

`lab.json` :

```json
{
  "node_id": "vlan",
  "kind": "docker",
  "image": "skilltree/lab:latest",
  "timeout": 60,
  "prompt": "Configure le trunk sur Gi0/1.",
  "hint": "pense à switchport mode trunk"
}
```

Les labs `lab_dhcp`, `lab_acl`, `lab_tshoot_dns`, `lab_tshoot_route` et
`lab_tshoot_mtu` suivent ce format. Les labs de dépannage sont portés par des
nœuds dédiés qui dépendent de `troubleshooting`.

### Défis d'architecture

Un nœud `architecture` peut définir son défi directement dans `nodes.json` avec
`challenge`, ou pointer vers un fichier JSON avec `challenge_file` :

```json
{
  "id": "challenge-vlan",
  "type": "architecture",
  "requirements": [{"kind": "manual", "min_score": 100}],
  "challenge_file": "challenges/challenge-vlan.json"
}
```

Le fichier contient `time_limit` et `expected_topology`. Le contrôle compare le
nombre de nœuds par type et les connexions entre types ; il ne vérifie pas la
configuration VLAN ou OSPF elle-même. Les fichiers fournis sont
`challenge-vlan.json`, `challenge-ospf.json` et `challenge-cloud.json`.

Les nœuds `dns-advanced`, `ntp-syslog`, `firewall`, `vpn` et `aaa` complètent
les sections Services et Sécurité. Les labs `lab_dns_adv` et `lab_firewall`
couvrent respectivement une zone dnsmasq avec A/CNAME et un firewall stateful
avec conntrack.

Le conteneur est lancé avec `--privileged` : `ip netns` a besoin de monter
`/run/netns`, et l'activation de `net.ipv4.ip_forward` par namespace exige
l'écriture dans `/proc/sys`, que Docker monte en lecture seule sans ce mode.
Le dossier du lab est monté en lecture seule sur `/lab`. Les commandes de l'utilisateur sont écrites dans
`/tmp/user.sh` puis exécutées avec `sh`. Le conteneur est toujours supprimé à
la fin, y compris en cas d'erreur ou de timeout.

### Lab OSPF

Le nœud `ospf` propose un transit entre deux routeurs Linux. Le dossier
`content/labs/lab_ospf/` contient quatre namespaces : `h1`, `r1`, `r2` et `h2`.
Les deux LAN distants sont `192.168.10.0/24` et `192.168.20.0/24`, reliés par
`10.255.0.0/30`. Le forwarding est déjà actif et les hôtes ont leur passerelle ;
l'exercice consiste à ajouter les routes vers chaque LAN distant.

```bash
python main.py labd ospf
```

Une solution statique :

```text
ip netns exec r1 ip route add 192.168.20.0/24 via 10.255.0.2
ip netns exec r2 ip route add 192.168.10.0/24 via 10.255.0.1
```

Le `check.sh` valide le ping dans les deux sens. Une image enrichie avec BIRD
ou FRRouting peut aussi être utilisée ; le contrôle reste fondé sur la
connectivité de bout en bout.

### Lab de dépannage VLAN

Le nœud `lab_troubleshoot_vlan` place deux namespaces derrière un bridge Linux
avec filtrage VLAN. Une erreur L2 volontaire empêche le ping : le port de
`ns2` est dans le VLAN 60 alors que celui de `ns1` est dans le VLAN 50.
L'utilisateur doit inspecter `bridge vlan show`, identifier le mauvais PVID et
corriger l'affectation.

```bash
python main.py labd lab_troubleshoot_vlan
```

Le `check.sh` valide le ping dans les deux sens une fois le VLAN corrigé.

### Labs interactifs depuis le navigateur

La modale d'un nœud de lab Docker propose un terminal web :

- `POST /api/lab/start` démarre un conteneur et renvoie un `lab_id` opaque ;
- `POST /api/lab/exec` exécute une commande avec un timeout et renvoie
  `stdout`, `stderr` et le code de sortie ;
- `POST /api/lab/validate` lance `check.sh`, enregistre la tentative puis
  détruit le conteneur.

Le conteneur reste actif au maximum une heure. Les routes `/api/lab/*`
exécutent des commandes dans un conteneur `--privileged` : elles sont prévues
pour un usage local ou derrière une authentification et ne doivent pas être
exposées directement sur Internet.

### Commandes

```bash
python main.py labd <node_id>        # lab Docker interactif
python main.py lab-shell <node_id>   # shell de debug dans le conteneur, sans validation
python main.py lab <node_id> <réponse>  # lab texte historique
```

`labd` refuse le nœud si le lab n'est pas de type Docker :

```
Ce nœud n'a pas de lab docker.
```

### Dépannage

- Docker absent : « Docker n'est pas installé ou n'est pas dans le PATH. »
- Image absente : « L'image skilltree/lab:latest est absente. Lance : docker build -t skilltree/lab:latest docker/lab »
- Timeout : « Le lab a dépassé le temps limite (<timeout>s). »
