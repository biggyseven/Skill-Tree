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

Un lab Docker, exécuté dans un conteneur :

```
content/labs/<node_id>/
├── lab.json      métadonnées
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

Le conteneur est lancé avec `--privileged` : `ip netns` a besoin de monter
`/run/netns`, et l'activation de `net.ipv4.ip_forward` par namespace exige
l'écriture dans `/proc/sys`, que Docker monte en lecture seule sans ce mode.
Le dossier du lab est monté en lecture seule sur `/lab`. Les commandes de l'utilisateur sont écrites dans
`/tmp/user.sh` puis exécutées avec `sh`. Le conteneur est toujours supprimé à
la fin, y compris en cas d'erreur ou de timeout.

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
