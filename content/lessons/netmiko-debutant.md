# Scripting réseau avec Python et Netmiko — Niveau débutant

> **Encadré de mise en contexte**
>
> **Niveau :** Débutant  
> **Sujet :** Scripting réseau avec Python et Netmiko  
> **Place dans la série :** ce premier module pose les fondations que les niveaux Intermédiaire puis Expert réutiliseront. Il apprend à établir une session, exécuter des commandes de lecture seule, collecter proprement les sorties et traiter les erreurs. Les niveaux suivants conserveront cette même chaîne de travail en y ajoutant l'inventaire, le parsing structuré, les tests, les changements de configuration contrôlés et l'orchestration.
>
> **Public visé :** personnes qui administrent un réseau ou étudient les réseaux et souhaitent commencer l'automatisation sans devoir construire elles-mêmes un client SSH complet.
>
> **Prérequis :** savoir utiliser un terminal, connaître les notions d'adresse IP, de routeur, de commutateur et de SSH, et être disposé à lire quelques bases de Python. Le cours introduit progressivement les éléments de Python utilisés.
>
> **Objectif concret :** écrire un script qui se connecte à un équipement de laboratoire, exécute une commande d'information, affiche et sauvegarde la réponse, ferme la session et explique clairement ce qui s'est passé si l'opération échoue.
>
> **Matériel recommandé :** un routeur ou commutateur de laboratoire accessible par SSH, un simulateur ou une machine d'entraînement autorisée, Python installé, Netmiko installé dans un environnement virtuel et un compte réseau adapté. Les noms de commandes CLI varient selon les constructeurs et les systèmes d'exploitation.
>
> **Limite de sécurité :** les premières manipulations sont en lecture seule. N'exécutez les exemples qui modifient une configuration que sur un équipement de laboratoire dont vous avez l'autorisation explicite. Ne lancez pas un script sur toute une flotte avant de l'avoir testé sur une seule cible non critique.

## 1. Pourquoi automatiser le réseau ?

Imaginez qu'une équipe doive vérifier chaque matin la version logicielle de vingt commutateurs, l'état de leurs interfaces et le temps écoulé depuis le dernier redémarrage. La méthode manuelle consiste à ouvrir une session, saisir les commandes, copier les réponses, fermer la session, passer à l'équipement suivant puis réunir les informations. Elle fonctionne pour quelques appareils, mais elle devient lente et irrégulière lorsque le nombre de cibles augmente.

Un script permet de répéter une procédure de manière constante. Il peut se connecter à chaque équipement, envoyer les mêmes commandes autorisées, enregistrer les résultats dans un fichier distinct, signaler les équipements injoignables et produire un résumé. L'intérêt n'est pas seulement d'aller plus vite : c'est également de rendre la procédure répétable, traçable et plus facile à contrôler.

L'automatisation ne fait toutefois pas disparaître les problèmes. Un script peut envoyer une commande inadaptée à un système, interpréter incorrectement une sortie, utiliser de mauvais identifiants ou échouer sans que la personne qui l'a lancé le remarque. Une automatisation de qualité associe donc **commande, résultat, validation, journalisation et garde-fous**.

<!-- Schéma SVG animé intégré : Vue d'ensemble de l'automatisation réseau avec Python et Netmiko -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" role="img" aria-labelledby="nm01-title nm01-desc">
<title id="nm01-title">Vue d'ensemble de l'automatisation réseau avec Python et Netmiko</title><desc id="nm01-desc">Un script Python prépare une demande, Netmiko gère une session SSH, l'équipement exécute la commande et le résultat est sauvegardé puis vérifié.</desc>
<defs><linearGradient id="nm01-bg" x2="1" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#1c3550"/></linearGradient><linearGradient id="nm01-python" x2="0" y2="1"><stop stop-color="#3d6ba8"/><stop offset="1" stop-color="#27466f"/></linearGradient><marker id="nm01-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#6ee7f9"/></marker><filter id="nm01-glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><style>.nm01-h{font:700 27px system-ui;fill:#f8fafc}.nm01-sub{font:15px system-ui;fill:#bdcddd}.nm01-box{fill:#1e3651;stroke:#5d91b9;stroke-width:2}.nm01-py{fill:url(#nm01-python);stroke:#83b6fb;stroke-width:2}.nm01-ok{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm01-t{font:700 19px system-ui;fill:#f8fafc}.nm01-b{font:15px system-ui;fill:#d9e7f5}.nm01-line{fill:none;stroke:#6ee7f9;stroke-width:3;stroke-dasharray:10 8;marker-end:url(#nm01-arrow);animation:nm01-flow 1.25s linear infinite}.nm01-packet{fill:#fcd34d;stroke:#fff7c2;stroke-width:1;filter:url(#nm01-glow)}@keyframes nm01-flow{to{stroke-dashoffset:-36}}@media(prefers-reduced-motion:reduce){.nm01-line{animation:none}.nm01-packet{display:none}}</style></defs>
<rect width="1200" height="560" rx="24" fill="url(#nm01-bg)"/><text x="44" y="52" class="nm01-h">De l'intention au résultat vérifiable</text><text x="44" y="80" class="nm01-sub">L'automatisation utile ne se limite pas à envoyer une commande : elle collecte, contrôle et conserve une preuve.</text>
<g transform="translate(40 150)"><rect width="230" height="190" rx="18" class="nm01-py"/><text x="22" y="40" class="nm01-t">1 · Python</text><text x="22" y="76" class="nm01-b">Choisit la cible</text><text x="22" y="102" class="nm01-b">Prépare les commandes</text><text x="22" y="128" class="nm01-b">Applique les garde-fous</text><text x="22" y="154" class="nm01-b">Organise les résultats</text>
<rect x="270" width="230" height="190" rx="18" class="nm01-box"/><text x="292" y="40" class="nm01-t">2 · Netmiko</text><text x="292" y="76" class="nm01-b">Établit la session SSH</text><text x="292" y="102" class="nm01-b">Gère l'invite CLI</text><text x="292" y="128" class="nm01-b">Envoie les commandes</text><text x="292" y="154" class="nm01-b">Récupère la sortie</text>
<rect x="540" width="230" height="190" rx="18" class="nm01-box"/><text x="562" y="40" class="nm01-t">3 · Équipement</text><text x="562" y="76" class="nm01-b">Routeur / commutateur</text><text x="562" y="102" class="nm01-b">Authentifie l'utilisateur</text><text x="562" y="128" class="nm01-b">Exécute la commande</text><text x="562" y="154" class="nm01-b">Retourne le texte CLI</text>
<rect x="810" width="230" height="190" rx="18" class="nm01-ok"/><text x="832" y="40" class="nm01-t">4 · Contrôle</text><text x="832" y="76" class="nm01-b">Vérifie la sortie</text><text x="832" y="102" class="nm01-b">Enregistre un fichier</text><text x="832" y="128" class="nm01-b">Journalise le résultat</text><text x="832" y="154" class="nm01-b">Signale les erreurs</text>
<path class="nm01-line" d="M230 95 H260"/><path class="nm01-line" d="M500 95 H530"/><path class="nm01-line" d="M770 95 H800"/><circle class="nm01-packet" r="7"><animateMotion dur="6s" repeatCount="indefinite" path="M230 95 H1040"/></circle></g>
<rect x="42" y="390" width="1116" height="116" rx="16" fill="#0b1320" stroke="#36516c"/><text x="68" y="425" class="nm01-t">Principe essentiel</text><text x="68" y="457" class="nm01-b">Commencer par une commande de lecture seule, sauvegarder la sortie et vérifier ce que le script a réellement reçu.</text><text x="68" y="482" class="nm01-b">Un script qui se termine sans exception n'a pas nécessairement prouvé que l'opération réseau a réussi.</text></svg>

### 1.1 Quand un script est utile

Les premiers cas d'usage sont les tâches répétitives et principalement consultatives :

- collecter `show version` sur des équipements compatibles avec cette commande ;
- obtenir un aperçu des interfaces, des voisins ou des routes ;
- comparer les réponses avec un état de référence ;
- produire un rapport d'audit horodaté ;
- archiver les résultats d'une maintenance ;
- signaler qu'un appareil n'a pas répondu plutôt que d'abandonner toute la collecte.

Netmiko peut également transmettre des commandes de configuration. Cette possibilité est puissante, mais elle ne signifie pas qu'il soit prudent de débuter par des changements. Une bonne progression est : observer, enregistrer, vérifier, automatiser la répétition, puis seulement apprendre à modifier avec une validation explicite.

### 1.2 Qu'est-ce qu'on automatise exactement ?

Une session CLI (interface en ligne de commande) est la conversation qui se déroule lorsque l'administrateur se connecte à un équipement et saisit des commandes. Le système affiche une invite, par exemple `R1#`, attend une instruction puis renvoie du texte. Le texte précis et les invites dépendent du constructeur, du système d'exploitation, du niveau de privilège et du contexte de configuration.

Netmiko rend cette interaction plus simple depuis Python. La bibliothèque connaît différents types de plateformes et prend en charge une partie des détails de la session interactive. Le script peut alors se concentrer sur la cible, les commandes à envoyer et les résultats à conserver. Il reste indispensable de choisir le bon type d'appareil et de comprendre ce que fait chaque commande.

## 2. Les outils : Python, SSH et Netmiko

### 2.1 Python

Python est le langage qui orchestre le travail : variables pour stocker les paramètres, listes pour représenter plusieurs équipements, conditions pour prendre des décisions, boucles pour répéter des opérations, fonctions pour réutiliser du code, et fichiers pour conserver les résultats.

Le programme Python ne « connaît » pas automatiquement les commandes d'un routeur. Il doit ouvrir une connexion vers l'appareil et transmettre les instructions prévues par le système distant.

### 2.2 SSH

SSH (Secure Shell) est un protocole permettant d'établir une session distante protégée cryptographiquement. Dans une infrastructure courante, l'équipement écoute sur le port TCP 22, mais le port peut avoir été changé. Pour qu'une connexion fonctionne, plusieurs conditions doivent être réunies : route et filtrage compatibles, service SSH actif, compte autorisé, méthode d'authentification acceptée et clé d'hôte vérifiée selon la politique de l'organisation.

Le chiffrement de SSH ne dispense pas de vérifier l'identité du serveur. La première connexion à un hôte peut demander ou nécessiter la validation de sa clé d'hôte. Une automatisation de confiance ne doit pas transformer cette vérification en une simple formalité : confirmez la clé via une source fiable, et soyez particulièrement prudent si une clé connue change de façon inattendue. Netmiko expose notamment `ssh_strict=True` pour refuser une clé d'hôte inconnue et `system_host_keys=True` pour charger les clés du fichier `known_hosts` du système. Les scripts de connexion complets plus bas activent ces options. Il faut donc inscrire la clé de l'équipement dans le fichier de confiance selon la procédure de votre organisation avant de lancer le script ; si la clé n'est pas connue, l'échec est voulu et doit être résolu en vérifiant l'identité de l'hôte, pas en désactivant le contrôle.

### 2.3 Netmiko

Netmiko est une bibliothèque Python conçue pour simplifier les connexions SSH aux équipements réseau et l'interaction avec leur CLI. Elle vise notamment l'envoi de commandes d'exploitation et l'application de commandes de configuration, avec des comportements adaptés à plusieurs plateformes. Les méthodes courantes du débutant sont :

| Méthode ou élément | Utilité |
|---|---|
| `ConnectHandler` | Construire et établir une session adaptée à la plateforme indiquée. |
| `device_type` | Choisir le pilote Netmiko correspondant à l'OS réseau. |
| `send_command()` | Envoyer une commande et recueillir sa sortie, habituellement pour une opération de lecture. |
| `send_config_set()` | Envoyer un ensemble de commandes de configuration sur les plateformes prises en charge. Cette méthode peut modifier l'équipement. |
| `disconnect()` | Fermer proprement la session. |
| `find_prompt()` | Lire l'invite de commande, utile pour le diagnostic lorsque c'est nécessaire. |

La liste exacte des plateformes et les détails des paramètres peuvent évoluer. Consultez le tableau des plateformes prises en charge et la documentation officielle correspondant à la version installée, plutôt que de supposer qu'un `device_type` donné est toujours valable.

<!-- Schéma SVG animé intégré : Les couches de l'automatisation SSH -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 590" role="img" aria-labelledby="nm02-title nm02-desc">
<title id="nm02-title">Les couches de l'automatisation SSH</title><desc id="nm02-desc">Python appelle Netmiko, Netmiko s'appuie sur les mécanismes SSH et TCP/IP, puis sur le CLI de l'équipement.</desc>
<defs><linearGradient id="nm02-bg" x2="0" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#172d43"/></linearGradient><marker id="nm02-arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker><style>.nm02-h{font:700 26px system-ui;fill:#f8fafc}.nm02-side-h{font:700 20px system-ui;fill:#f8fafc}.nm02-l{font:17px system-ui;fill:#dbeafe}.nm02-s{font:14px system-ui;fill:#bfd0e2}.nm02-layer{stroke-width:2}.nm02-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm02-arr);animation:nm02-dash 1s linear infinite}.nm02-dot{fill:#fbbf24;filter:url(#nm02-glow)}@keyframes nm02-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm02-flow{animation:none}.nm02-dot{display:none}}</style><filter id="nm02-glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect width="1200" height="590" rx="24" fill="url(#nm02-bg)"/><text x="42" y="48" class="nm02-h">Comprendre les responsabilités de chaque couche</text><text x="42" y="76" class="nm02-s">Quand une connexion échoue, ce découpage aide à localiser la panne au bon niveau.</text>
<g transform="translate(95 125)"><rect width="690" height="66" rx="12" fill="#1e3a8a" stroke="#60a5fa" class="nm02-layer"/><text x="24" y="28" class="nm02-l" font-weight="700">Script Python</text><text x="250" y="28" class="nm02-s">Variables, conditions, boucles, fichiers, rapports</text>
<rect y="82" width="690" height="66" rx="12" fill="#164e63" stroke="#67e8f9" class="nm02-layer"/><text x="24" y="110" class="nm02-l" font-weight="700">Netmiko</text><text x="250" y="110" class="nm02-s">Pilote de plateforme, invite, temporisations, lecture CLI</text>
<rect y="164" width="690" height="66" rx="12" fill="#334155" stroke="#94a3b8" class="nm02-layer"/><text x="24" y="192" class="nm02-l" font-weight="700">SSH / transport</text><text x="250" y="192" class="nm02-s">Authentification, chiffrement, TCP, port 22 par défaut</text>
<rect y="246" width="690" height="66" rx="12" fill="#365044" stroke="#6ee7b7" class="nm02-layer"/><text x="24" y="274" class="nm02-l" font-weight="700">CLI de l'équipement</text><text x="250" y="274" class="nm02-s">Commandes et réponses spécifiques au constructeur</text>
<path class="nm02-flow" d="M345 66 V78"/><path class="nm02-flow" d="M345 148 V160"/><path class="nm02-flow" d="M345 230 V242"/><circle class="nm02-dot" r="7"><animateMotion dur="5s" repeatCount="indefinite" path="M345 66 V78 V148 V160 V230 V242"/></circle></g>
<rect x="835" y="140" width="300" height="300" rx="18" fill="#0c1726" stroke="#475569"/><text x="860" y="174" class="nm02-side-h">Si quelque chose</text><text x="860" y="197" class="nm02-side-h">échoue…</text><text x="860" y="229" class="nm02-s">Réseau inaccessible ?</text><text x="878" y="249" class="nm02-l">→ IP, route, ACL, port</text><text x="860" y="279" class="nm02-s">Authentification refusée ?</text><text x="878" y="299" class="nm02-l">→ compte, clé, politique SSH</text><text x="860" y="329" class="nm02-s">Commande vide ou tronquée ?</text><text x="878" y="349" class="nm02-l">→ invite, pagination, délai</text><text x="860" y="379" class="nm02-s">Commande rejetée ?</text><text x="878" y="399" class="nm02-l">→ syntaxe / privilèges / OS</text>
<text x="96" y="500" class="nm02-s">Netmiko facilite l'interaction avec le CLI ; il ne remplace ni la connectivité IP, ni les droits d'accès, ni la compréhension des commandes.</text></svg>

### 2.4 Ce que Netmiko ne fait pas à votre place

Netmiko ne remplace pas le routage IP, les règles de pare-feu, les comptes d'administration, les sauvegardes ni la validation des résultats. Il ne peut pas garantir qu'une commande est pertinente pour votre environnement. Il ne transforme pas automatiquement toutes les réponses texte en données fiables. La décision de continuer, de s'arrêter ou de réparer appartient au script et à la procédure d'exploitation.

## 3. Préparer un environnement Python propre

Il est recommandé de travailler dans un environnement virtuel. Celui-ci isole les bibliothèques installées pour le projet de celles d'autres applications Python sur le même ordinateur. Il facilite les essais et limite les conflits de versions.

### 3.1 Vérifier Python

Ouvrez un terminal ou PowerShell et exécutez :

```bash
python --version
```

Selon le système, la commande disponible peut être `python3` plutôt que `python`. Sur Windows, le lanceur `py` peut être disponible :

```powershell
py --version
```

À la date de rédaction, la fiche PyPI de Netmiko 4.8.0 annonce Python 3.10 ou plus récent. Vérifiez la métadonnée et les notes de version au moment de l'installation, surtout si votre environnement d'entreprise impose une version précise de Python.

### 3.2 Créer le dossier du projet

```bash
mkdir netmiko-lab
cd netmiko-lab
```

Créez ensuite un environnement virtuel :

```bash
python -m venv .venv
```

Sur Windows PowerShell, activez-le avec :

```powershell
.\.venv\Scripts\Activate.ps1
```

Si la politique PowerShell bloque l'activation, ne modifiez pas arbitrairement les règles de sécurité du poste : utilisez la méthode autorisée par votre organisation ou appelez directement l'interpréteur de l'environnement virtuel.

Sur Linux ou macOS :

```bash
source .venv/bin/activate
```

Lorsque l'environnement est activé, le terminal affiche souvent `(.venv)` au début de l'invite. Ce marqueur est un indice, pas une preuve à lui seul. Vérifiez l'interpréteur actif si vous avez plusieurs installations Python.

### 3.3 Installer Netmiko et vérifier l'installation

```bash
python -m pip install --upgrade pip
python -m pip install netmiko
```

Pour afficher la version installée :

```bash
python -c "import netmiko; print(netmiko.__version__)"
```

Si l'import échoue, vérifiez que le bon environnement est activé, que l'installation n'a pas échoué et que le nom du paquet a été correctement saisi. Il est préférable d'utiliser `python -m pip` afin que `pip` corresponde à l'interpréteur Python employé pour exécuter le script.

### 3.4 Organisation minimale du projet

Une organisation simple peut ressembler à ceci :

```text
netmiko-lab/
├── .venv/
├── scripts/
│   └── premier_test.py
├── outputs/
└── README.md
```

Le dossier `.venv` contient l'environnement. `scripts` héberge le code. `outputs` reçoit les collectes. `README.md` peut documenter l'objectif, les prérequis, les commandes de lancement et les limites. Ne versionnez pas les identifiants, les clés privées ou les sorties contenant des informations sensibles.

## 4. Comprendre les informations de connexion

Pour se connecter, le script doit connaître au minimum l'hôte, le type d'appareil et l'identité à utiliser. Un dictionnaire Python permet de regrouper ces éléments en une seule variable.

```python
appareil = {
    "device_type": "cisco_ios",
    "host": "192.0.2.10",
    "username": "operateur",
    "password": "",  # à renseigner de manière sûre, pas dans le code
}
```

`192.0.2.10` est une adresse d'exemple tirée d'une plage réservée à la documentation. Remplacez-la par l'adresse d'un appareil de laboratoire qui vous appartient ou que vous êtes autorisé à administrer. `cisco_ios` est un exemple de `device_type` ; il ne convient pas automatiquement à Cisco NX-OS, IOS XR, Juniper Junos ou à une autre plateforme. Vérifiez la valeur dans les références de Netmiko.

Un dictionnaire associe des clés à des valeurs. Ici, `
 associe la clé `host` à l'adresse de l'équipement, la clé `username` au compte de connexion et la clé `password` au mot de passe. Il est important de ne pas confondre le nom de la variable et la valeur stockée à l'intérieur.

### 4.1 Ne pas écrire le mot de passe en clair dans le fichier

Le champ vide du premier exemple est intentionnel. Pour un exercice interactif, le module standard `getpass` permet de demander le mot de passe sans l'afficher à l'écran :

```python
from getpass import getpass

username = input("Nom d'utilisateur réseau : ")
password = getpass("Mot de passe réseau : ")
```

Cette méthode est suffisante pour un petit laboratoire lancé manuellement. Pour un service automatisé ou une exécution planifiée, utilisez le mécanisme de gestion des secrets approuvé dans votre environnement : coffre de secrets, compte de service à privilèges limités, identité machine ou clés administrées. Ne collez pas des mots de passe dans le code, dans une capture d'écran, dans un dépôt Git ou dans les journaux.

Les variables d'environnement peuvent dépanner certaines tâches mais ne sont pas un coffre-fort : elles peuvent être visibles à d'autres processus ou apparaître dans certains outils de diagnostic. Ne considérez pas une variable d'environnement comme une solution universelle de gestion des secrets.

### 4.2 Nommer clairement ses paramètres

Il est utile de distinguer :

- `host` : adresse IP ou nom d'hôte résolvable ;
- `port` : port TCP SSH, généralement 22 si non précisé ;
- `username` : compte distant ;
- `password` : secret d'authentification par mot de passe, si cette méthode est autorisée ;
- `device_type` : pilote de plateforme Netmiko ;
- `secret` : mot de passe de privilège sur les plateformes et configurations qui en ont besoin.

Le paramètre `secret` ne doit pas être ajouté automatiquement parce qu'un tutoriel l'utilise. Sa pertinence dépend du système et de la façon dont les privilèges sont configurés. Un utilisateur doit recevoir les droits minimum nécessaires à la tâche. Un compte de collecte ne devrait pas pouvoir modifier les interfaces si sa mission se limite à lire leur état.

## 5. Le premier script : connexion et commande en lecture seule

Le premier objectif n'est pas d'automatiser vingt appareils. Il est d'établir une connexion unique et de récupérer une commande connue, sans modifier la configuration. Pour une plateforme Cisco IOS de laboratoire, `show version` est un exemple de commande d'information. Sur une autre plateforme, la commande de lecture équivalente peut être différente.

Créez `scripts/premier_test.py` avec ce contenu, en remplaçant l'adresse de laboratoire et le type d'appareil si nécessaire :

```python
from getpass import getpass
from netmiko import ConnectHandler


def main():
    hote = "192.0.2.10"  # adresse d'exemple : remplacez-la
    type_appareil = "cisco_ios"  # à adapter à la plateforme réelle

    utilisateur = input("Nom d'utilisateur réseau : ")
    mot_de_passe = getpass("Mot de passe réseau : ")

    parametres = {
        "device_type": type_appareil,
        "host": hote,
        "username": utilisateur,
        "password": mot_de_passe,
        # Refuser les clés d'hôte inconnues et utiliser le fichier known_hosts.
        "ssh_strict": True,
        "system_host_keys": True,
    }

    connexion = None
    try:
        print(f"Connexion à {hote}...")
        connexion = ConnectHandler(**parametres)
        print("Session établie. Exécution de la commande...")

        sortie = connexion.send_command("show version", read_timeout=30)
        print(sortie)

    except Exception as erreur:
        # Pour un premier exercice, afficher l'erreur aide à diagnostiquer.
        # Un outil de production utilisera une gestion d'erreurs plus précise.
        print(f"Échec pour {hote} : {erreur}")

    finally:
        if connexion is not None:
            connexion.disconnect()
            print("Session fermée.")


if __name__ == "__main__":
    main()
```

Exécutez le script depuis le dossier du projet, avec l'environnement virtuel activé :

```bash
python scripts/premier_test.py
```

Le déroulement attendu est le suivant : le programme demande le nom d'utilisateur, demande le mot de passe sans l'afficher, tente d'établir la session SSH, envoie la commande et imprime la sortie. La session est ensuite fermée. En cas d'erreur, le message aide à orienter le diagnostic.

### 5.1 Que signifie `ConnectHandler(**parametres)` ?

`ConnectHandler` est la fonction Netmiko chargée de préparer une connexion selon le type d'appareil et les paramètres fournis. Les deux astérisques `**` demandent à Python de transmettre les paires clé-valeur du dictionnaire comme arguments nommés. C'est une manière compacte d'écrire une connexion sans répéter chaque argument à la main.

`connexion` devient l'objet qui représente la session. La méthode `send_command()` envoie la commande puis lit la réponse. Ici, `read_timeout=30` indique un délai de lecture plus long que certaines valeurs par défaut ; ce n'est pas une promesse que toute commande finira en trente secondes, ni une raison de fixer des délais énormes partout. Choisissez les délais selon la commande, la plateforme et le volume de sortie.

Le bloc `try` contient les étapes qui risquent d'échouer. `except` intercepte ici une exception pour que le message soit visible. `finally` exécute sa partie même lorsqu'une erreur se produit, ce qui aide à fermer une session ouverte. Pour un programme plus avancé, il faut distinguer les erreurs de réseau, d'authentification, de plateforme et de traitement de données plutôt que de toutes les traiter de la même manière.

`if __name__ == "__main__":` signifie que `main()` est appelée lorsque ce fichier est exécuté directement, mais pas automatiquement lorsqu'un autre script l'importe. Cette structure rend le code plus facile à tester et à réutiliser.

<!-- Schéma SVG animé intégré : Cycle de vie d'une session Netmiko -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" role="img" aria-labelledby="nm03-title nm03-desc"><title id="nm03-title">Cycle de vie d'une session Netmiko</title><desc id="nm03-desc">Préparer les paramètres, connecter, exécuter une commande, lire le résultat et fermer la session, même en cas d'erreur.</desc>
<defs><linearGradient id="nm03-bg" x2="1" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#1b344c"/></linearGradient><marker id="nm03-m" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#6ee7f9"/></marker><style>.nm03-h{font:700 26px system-ui;fill:#f8fafc}.nm03-b{font:15px system-ui;fill:#dbeafe}.nm03-n{font:700 18px system-ui;fill:#f8fafc}.nm03-node{fill:#1d3853;stroke:#68b5df;stroke-width:2}.nm03-green{fill:#153d35;stroke:#6ee7b7;stroke-width:2}.nm03-red{fill:#492b35;stroke:#fda4af;stroke-width:2}.nm03-e{fill:none;stroke:#6ee7f9;stroke-width:3;stroke-dasharray:9 8;marker-end:url(#nm03-m);animation:nm03-flow 1.1s linear infinite}.nm03-dot{fill:#fde68a;stroke:#fff;stroke-width:1}@keyframes nm03-flow{to{stroke-dashoffset:-34}}@media(prefers-reduced-motion:reduce){.nm03-e{animation:none}.nm03-dot{display:none}}</style></defs><rect width="1200" height="560" rx="24" fill="url(#nm03-bg)"/><text x="44" y="50" class="nm03-h">Une session se ferme toujours proprement</text><text x="44" y="78" class="nm03-b">Le bloc try/finally garantit la fermeture même si une commande échoue.</text>
<g><rect x="55" y="145" width="200" height="100" rx="16" class="nm03-node"/><text x="78" y="178" class="nm03-n">1. Préparer</text><text x="78" y="207" class="nm03-b">Cible et identifiants</text><rect x="310" y="145" width="200" height="100" rx="16" class="nm03-node"/><text x="333" y="178" class="nm03-n">2. Connecter</text><text x="333" y="207" class="nm03-b">ConnectHandler(...)</text><rect x="565" y="145" width="200" height="100" rx="16" class="nm03-node"/><text x="588" y="178" class="nm03-n">3. Interroger</text><text x="588" y="207" class="nm03-b">send_command(...)</text><rect x="820" y="145" width="200" height="100" rx="16" class="nm03-green"/><text x="843" y="178" class="nm03-n">4. Vérifier</text><text x="843" y="207" class="nm03-b">Sortie et statut</text><rect x="455" y="365" width="290" height="100" rx="16" class="nm03-green"/><text x="485" y="398" class="nm03-n">5. Déconnecter</text><text x="485" y="427" class="nm03-b">disconnect() dans finally</text><path class="nm03-e" d="M255 195 H302"/><path class="nm03-e" d="M510 195 H557"/><path class="nm03-e" d="M765 195 H812"/><path class="nm03-e" d="M920 245 V315 H600 V357"/><path class="nm03-e" d="M410 245 V290 H475 V357"/><circle class="nm03-dot" r="7"><animateMotion dur="5s" repeatCount="indefinite" path="M255 195 H302 H510 H557 H765 H812 H920 V315 H600 V357"/></circle></g>
<rect x="790" y="365" width="355" height="100" rx="16" class="nm03-red"/><text x="815" y="397" class="nm03-n">Erreur à n'importe quelle étape ?</text><text x="815" y="426" class="nm03-b">Journaliser, puis fermer la session.</text><text x="56" y="510" class="nm03-b">Un équipement indisponible ne doit pas empêcher le script de terminer proprement le traitement des autres cibles.</text></svg>

### 5.2 Ce que vous devez vérifier à la fin

Ne vous contentez pas de voir un message « terminé ». Vérifiez les points suivants :

1. Le nom d'hôte et le `device_type` correspondent réellement à la machine cible.
2. La session a atteint l'invite attendue et la commande est adaptée au système.
3. La sortie contient bien les informations attendues ; une chaîne vide ou un message d'erreur CLI ne doit pas être assimilé à une réussite.
4. La session est fermée après l'opération.
5. Le script ne révèle aucun secret dans la sortie ou dans l'historique du terminal.

Un message de commande invalide affiché par l'équipement peut être retourné comme du texte plutôt qu'être signalé par une exception Python. C'est pourquoi le script doit valider la sortie, pas uniquement surveiller les exceptions.

## 6. Une sortie réseau, c'est d'abord du texte

Netmiko renvoie fréquemment le résultat d'une commande comme une chaîne de caractères Python (`str`). L'objet peut contenir plusieurs lignes, des espaces, des en-têtes, des colonnes, des messages de pagination selon les circonstances, voire des diagnostics de l'équipement.

La variable suivante n'est pas une liste d'interfaces directement exploitable ; c'est du texte :

```python
sortie = connexion.send_command("show ip interface brief")
print(type(sortie))  # <class 'str'>
```

Pour les premiers exercices, le plus important est de conserver la sortie brute avant toute transformation. Ensuite, vous pouvez séparer les lignes et effectuer une recherche simple. Ne partez pas du principe que le même ordre de colonnes, les mêmes noms d'interface et les mêmes phrases existent sur tous les constructeurs.

### 6.1 Séparer la sortie en lignes

```python
lignes = sortie.splitlines()

for ligne in lignes:
    print(ligne)
```

`splitlines()` transforme une chaîne multi-lignes en une liste, une entrée par ligne. Une boucle `for` visite alors les lignes une par une. C'est un premier outil simple pour filtrer ou examiner une sortie.

### 6.2 Rechercher un indice de manière prudente

```python
if "Version" in sortie:
    print("Le mot 'Version' apparaît dans la sortie.")
else:
    print("Le mot 'Version' n'a pas été trouvé.")
```

Cela prouve uniquement que le mot apparaît ou n'apparaît pas dans le texte reçu. Cela ne prouve pas que la version a été identifiée correctement. Pour produire des données fiables, définissez une règle de parsing précise et testez-la sur des exemples connus de la plateforme visée.

### 6.3 Le piège du texte propre en apparence

Deux équipements peuvent présenter les mêmes informations sous des formats différents : noms de colonnes modifiés, espaces multiples, unités, traductions, versions logicielles ou commandes distinctes. Une expression régulière qui marche sur un appareil peut mal analyser le résultat d'un autre.

Conservez donc deux types de fichiers : la sortie brute originale et, si vous avez besoin de rapports automatisés, les données extraites séparément. Lorsqu'un parseur ne reconnaît pas une sortie, signalez l'écart. N'inventez pas de valeur par défaut silencieuse qui pourrait donner l'impression qu'une interface est opérationnelle alors que les données n'ont pas pu être lues.

<!-- Schéma SVG animé intégré : Du texte CLI à une donnée exploitable -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 540" role="img" aria-labelledby="nm04-title nm04-desc"><title id="nm04-title">Du texte CLI à une donnée exploitable</title><desc id="nm04-desc">Une sortie brute est enregistrée, normalisée, extraite en champs, validée et transformée en rapport.</desc>
<defs><linearGradient id="nm04-bg" x2="1" y2="0"><stop stop-color="#101827"/><stop offset="1" stop-color="#1c344b"/></linearGradient><marker id="nm04-arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker><style>.nm04-h{font:700 26px system-ui;fill:#f8fafc}.nm04-t{font:700 18px system-ui;fill:#f8fafc}.nm04-s{font:14px system-ui;fill:#dbeafe}.nm04-n{fill:#1e3a5f;stroke:#60a5fa;stroke-width:2}.nm04-g{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm04-e{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm04-arr);animation:nm04-dash 1s linear infinite}.nm04-p{fill:#fcd34d}@keyframes nm04-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm04-e{animation:none}.nm04-p{display:none}}</style></defs><rect width="1200" height="540" rx="24" fill="url(#nm04-bg)"/><text x="42" y="48" class="nm04-h">Ne pas confondre la sortie texte et les données validées</text><text x="42" y="76" class="nm04-s">Netmiko fournit souvent du texte : l'analyse et la validation restent à concevoir dans le script.</text>
<rect x="40" y="155" width="190" height="120" rx="15" class="nm04-n"/><text x="60" y="190" class="nm04-t">Sortie brute</text><text x="60" y="220" class="nm04-s">CLI complète</text><text x="60" y="244" class="nm04-s">Pas encore un objet</text><rect x="280" y="155" width="190" height="120" rx="15" class="nm04-n"/><text x="300" y="190" class="nm04-t">Parser</text><text x="300" y="220" class="nm04-s">Lignes / regex</text><text x="300" y="244" class="nm04-s">Format connu</text><rect x="520" y="155" width="190" height="120" rx="15" class="nm04-n"/><text x="540" y="190" class="nm04-t">Champs</text><text x="540" y="220" class="nm04-s">interface, état</text><text x="540" y="244" class="nm04-s">adresse, version</text><rect x="760" y="155" width="190" height="120" rx="15" class="nm04-n"/><text x="780" y="190" class="nm04-t">Validation</text><text x="780" y="220" class="nm04-s">types et valeurs</text><text x="780" y="244" class="nm04-s">cas inattendus</text><rect x="1000" y="155" width="160" height="120" rx="15" class="nm04-g"/><text x="1020" y="190" class="nm04-t">Rapport</text><text x="1020" y="220" class="nm04-s">JSON / CSV</text><text x="1020" y="244" class="nm04-s">ou tableau</text><path class="nm04-e" d="M230 215 H272"/><path class="nm04-e" d="M470 215 H512"/><path class="nm04-e" d="M710 215 H752"/><path class="nm04-e" d="M950 215 H992"/><circle class="nm04-p" r="7"><animateMotion dur="5s" repeatCount="indefinite" path="M230 215 H272 H470 H512 H710 H752 H950 H992"/></circle>
<rect x="42" y="340" width="1118" height="110" rx="15" fill="#0b1320" stroke="#475569"/><text x="67" y="377" class="nm04-t">Exemple de garde-fou</text><text x="67" y="407" class="nm04-s">Si le parseur attend une colonne « Status » mais que la plateforme affiche un autre format, signaler l'écart.</text><text x="67" y="430" class="nm04-s">Ne jamais transformer silencieusement une sortie inconnue en données qui paraissent valides.</text></svg>

## 7. Sauvegarder les résultats dans des fichiers

Une sortie affichée à l'écran disparaît facilement dans l'historique du terminal. Une sortie sauvegardée devient une preuve réutilisable, que vous pouvez comparer à une collecte ultérieure. La sauvegarde doit inclure un nom pertinent, l'identification de l'équipement, la commande et idéalement la date de collecte.

### 7.1 Créer un dossier de sortie

Le module standard `pathlib` simplifie la manipulation de chemins. Ajoutez ceci au début du script :

```python
from pathlib import Path

DOSSIER_SORTIE = Path("outputs")
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
```

`mkdir()` crée le dossier s'il n'existe pas. `exist_ok=True` évite une erreur si le dossier est déjà présent. Le chemin est relatif au répertoire courant depuis lequel vous exécutez le script, donc lancez le programme depuis le dossier du projet ou utilisez un chemin de projet explicitement défini.

### 7.2 Écrire la sortie avec UTF-8

```python
fichier = DOSSIER_SORTIE / "R1__show-version.txt"
fichier.write_text(sortie, encoding="utf-8")
print(f"Sortie enregistrée dans {fichier}")
```

La chaîne de sortie est écrite avec l'encodage UTF-8. Le nom du fichier utilise le nom de l'équipement et une description de la commande. Pour un système qui collecte plusieurs fois par jour, ajoutez un horodatage afin d'éviter d'écraser la collecte précédente.

### 7.3 Nommer les fichiers de façon sûre

N'utilisez pas directement des noms venant d'un inventaire externe sans les valider : un nom peut contenir des barres obliques, des caractères inhabituels ou des chemins qui ne devraient pas être interprétés comme des noms de fichier. Dans un petit projet, imposez une convention simple comme `R1`, `SW1` et `FW-LAB`. Dans un projet plus important, normalisez les noms avant de créer les fichiers.

La sortie d'un équipement peut contenir des adresses, des noms internes ou des éléments sensibles. Restreignez les droits du dossier, ne l'envoyez pas vers un service public sans validation et appliquez les règles de conservation de votre organisation.

## 8. Automatiser plusieurs équipements, pas à pas

La première boucle multi-équipements doit être simple et séquentielle : un seul appareil est traité à la fois. Cette méthode rend le diagnostic plus facile. La parallélisation peut être ajoutée plus tard, après avoir traité correctement les erreurs, les limites de connexions, la charge des équipements et le contrôle des changements.

### 8.1 Représenter un inventaire en Python

```python
equipements = [
    {"name": "R1", "host": "192.0.2.10", "device_type": "cisco_ios"},
    {"name": "SW1", "host": "192.0.2.20", "device_type": "cisco_ios"},
]
```

Cette liste contient deux dictionnaires. La clé `name` est un nom de référence destiné au rapport ; `host` est l'adresse réseau ; `device_type` détermine le pilote Netmiko. Les deux adresses sont des exemples documentaires : elles ne sont pas des cibles accessibles sur votre réseau.

Pour le débutant, l'inventaire peut être écrit directement dans le code. Plus tard, vous apprendrez à le charger depuis un fichier YAML ou CSV, à vérifier son contenu et à séparer les données d'environnement de la logique du script.

### 8.2 Partager les identifiants au lieu de les recopier

Dans de nombreux laboratoires, les équipements d'un groupe utilisent un même compte de lecture. Dans une infrastructure réelle, il est préférable d'employer les comptes et secrets autorisés par la politique de l'organisation. Voici le principe pour demander les identifiants une seule fois :

```python
from getpass import getpass

utilisateur = input("Nom d'utilisateur : ")
mot_de_passe = getpass("Mot de passe : ")
```

Le code de connexion peut ensuite préparer le dictionnaire complet pour chaque équipement :

```python
parametres = {
    "device_type": equipement["device_type"],
    "host": equipement["host"],
    "username": utilisateur,
    "password": mot_de_passe,
    "ssh_strict": True,
    "system_host_keys": True,
}
connexion = ConnectHandler(**parametres)
```

Cette approche évite de recopier le secret dans chaque entrée de l'inventaire. Elle ne garantit pas que tous les appareils partagent réellement le même compte ou la même politique d'authentification ; vérifiez le modèle d'accès avant de l'adopter.

### 8.3 Un collecteur multi-équipements complet en lecture seule

Le script suivant illustre un petit projet complet : chaque équipement est traité indépendamment, la sortie est écrite dans son propre fichier, les erreurs sont conservées dans un résumé et les autres appareils continuent d'être traités. Cet exemple est destiné à un laboratoire où la commande `show version` convient au type d'équipement déclaré.

```python
from datetime import datetime
from getpass import getpass
from pathlib import Path
import re

from netmiko import ConnectHandler

EQUIPEMENTS = [
    {"name": "R1", "host": "192.0.2.10", "device_type": "cisco_ios"},
    {"name": "SW1", "host": "192.0.2.20", "device_type": "cisco_ios"},
]
DOSSIER_SORTIE = Path("outputs")
COMMANDE = "show version"


def nom_fichier_sur(nom):
    """Conserver lettres, chiffres, tirets et underscores dans un nom."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", nom)


def collecter(equipement, utilisateur, mot_de_passe):
    connexion = None
    nom = equipement["name"]
    hote = equipement["host"]

    try:
        parametres = {
            "device_type": equipement["device_type"],
            "host": hote,
            "username": utilisateur,
            "password": mot_de_passe,
            "ssh_strict": True,
            "system_host_keys": True,
        }
        print(f"[{nom}] Connexion à {hote}...")
        connexion = ConnectHandler(**parametres)
        sortie = connexion.send_command(COMMANDE, read_timeout=30)

        if not sortie.strip():
            raise ValueError("La commande a renvoyé une sortie vide.")

        horodatage = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
        nom_sain = nom_fichier_sur(nom)
        fichier = DOSSIER_SORTIE / f"{nom_sain}__show-version__{horodatage}.txt"
        fichier.write_text(sortie, encoding="utf-8")

        print(f"[{nom}] OK — sortie écrite dans {fichier}")
        return {"name": nom, "status": "ok", "file": str(fichier), "error": ""}

    except Exception as erreur:
        # N'inclure aucun mot de passe dans ce message.
        message = f"{type(erreur).__name__}: {erreur}"
        print(f"[{nom}] ÉCHEC — {message}")
        return {"name": nom, "status": "error", "file": "", "error": message}

    finally:
        if connexion is not None:
            connexion.disconnect()


def main():
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    utilisateur = input("Nom d'utilisateur : ")
    mot_de_passe = getpass("Mot de passe : ")

    resultats = []
    for equipement in EQUIPEMENTS:
        resultat = collecter(equipement, utilisateur, mot_de_passe)
        resultats.append(resultat)

    reussites = sum(r["status"] == "ok" for r in resultats)
    echecs = len(resultats) - reussites
    print(f"Résumé : {reussites} succès, {echecs} échec(s).")

    rapport = ["name,status,file,error"]
    for resultat in resultats:
        # Remplacement simplifié des virgules pour cet exemple de CSV.
        # Un export CSV de production doit utiliser le module csv.
        erreur = resultat["error"].replace(",", ";")
        rapport.append(
            f"{resultat['name']},{resultat['status']},{resultat['file']},{erreur}"
        )
    (DOSSIER_SORTIE / "resume.csv").write_text(
        "\n".join(rapport) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
```

Ce code montre les concepts importants mais reste un exemple pédagogique. Pour un traitement CSV robuste, utilisez `csv.DictWriter` afin de gérer correctement les guillemets, séparateurs et retours à la ligne. Dans un service exploité en continu, affinez les exceptions capturées, ajoutez des journaux structurés, définissez une politique de gestion des identifiants et validez la politique de vérification SSH. N'avalez pas silencieusement une exception et ne vous contentez pas d'un seul compteur global : chaque résultat doit indiquer de quel équipement il provient.

<!-- Schéma SVG animé intégré : Boucle de collecte sur plusieurs équipements -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" role="img" aria-labelledby="nm05-title nm05-desc"><title id="nm05-title">Boucle de collecte sur plusieurs équipements</title><desc id="nm05-desc">Le script parcourt une liste de trois appareils, traite chacun séparément, enregistre chaque sortie et continue après une erreur.</desc>
<defs><linearGradient id="nm05-bg" x2="0" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#172b40"/></linearGradient><marker id="nm05-a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker><style>.nm05-h{font:700 26px system-ui;fill:#f8fafc}.t{font:700 18px system-ui;fill:#f8fafc}.s{font:14px system-ui;fill:#dbeafe}.nm05-b{font:15px system-ui;fill:#dbeafe}.nm05-n{font:700 18px system-ui;fill:#f8fafc}.nm05-node{fill:#203a55;stroke:#60a5fa;stroke-width:2}.nm05-good{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm05-bad{fill:#4a2933;stroke:#fb7185;stroke-width:2}.nm05-edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm05-a)}.nm05-p{fill:#fcd34d;stroke:#fff7ca}@media(prefers-reduced-motion:reduce){.nm05-p{display:none}}</style></defs><rect width="1200" height="560" rx="24" fill="url(#nm05-bg)"/><text x="42" y="50" class="nm05-h">Un équipement à la fois, sans perdre le reste de la flotte</text><text x="42" y="78" class="nm05-b">Le premier script multi-équipements doit privilégier la visibilité et la résilience, pas la vitesse.</text>
<rect x="55" y="130" width="230" height="92" rx="16" class="nm05-node"/><text x="80" y="166" class="nm05-n">Liste des équipements</text><text x="80" y="194" class="nm05-b">R1 · SW1 · R2</text>
<rect x="360" y="130" width="230" height="92" rx="16" class="nm05-node"/><text x="385" y="166" class="nm05-n">Boucle for</text><text x="385" y="194" class="nm05-b">Traiter une cible</text>
<rect x="665" y="130" width="230" height="92" rx="16" class="nm05-node"/><text x="690" y="166" class="nm05-n">Session SSH</text><text x="690" y="194" class="nm05-b">Connexion + commande</text>
<rect x="970" y="130" width="180" height="92" rx="16" class="nm05-good"/><text x="990" y="166" class="nm05-n">Résultat</text><text x="990" y="194" class="nm05-b">Fichier / journal</text>
<path class="nm05-edge" d="M285 176 H352"/><path class="nm05-edge" d="M590 176 H657"/><path class="nm05-edge" d="M895 176 H962"/><circle class="nm05-p" r="7"><animateMotion dur="4s" repeatCount="indefinite" path="M285 176 H352 H590 H657 H895 H962"/></circle>
<path class="nm05-edge" d="M1060 222 V300 H475 V230"/><text x="690" y="289" class="nm05-b">Passer à la cible suivante</text><rect x="135" y="350" width="405" height="105" rx="16" class="nm05-bad"/><text x="160" y="383" class="nm05-n">Si R1 échoue</text><text x="160" y="412" class="nm05-b">Enregistrer l'erreur, puis poursuivre</text><text x="160" y="437" class="nm05-b">R1 ne doit pas bloquer SW1 et R2.</text><rect x="640" y="350" width="510" height="105" rx="16" fill="#0b1320" stroke="#475569"/><text x="665" y="383" class="nm05-n">Rapport de fin</text><text x="665" y="412" class="nm05-b">Succès : 2 · Échecs : 1 · Durée : mesurée</text><text x="665" y="437" class="nm05-b">Chaque ligne doit identifier précisément l'équipement.</text></svg>

### 8.4 Pourquoi `finally` est important dans une boucle

Si une connexion est ouverte et qu'une lecture se termine par une erreur, la session doit être fermée. Sans nettoyage, un programme peut laisser des connexions inutiles, épuiser le nombre de sessions accepté par l'équipement ou compliquer le diagnostic. Le bloc `finally` sert à exécuter le nettoyage dans le chemin normal comme dans le chemin d'erreur.

Le script retourne un résultat par équipement plutôt que de simplement imprimer une erreur. Cette structure permet d'écrire ensuite un tableau ou un rapport : un appareil est en succès, un autre est en échec, et la collecte globale continue. Il devient possible de relancer uniquement les appareils concernés au lieu de recommencer tout le travail.

## 9. Boucles, conditions et fonctions : le minimum de Python à connaître

### 9.1 La boucle `for`

Une boucle `for` répète un bloc d'instructions pour chaque élément d'une séquence :

```python
noms = ["R1", "SW1", "R2"]

for nom in noms:
    print(f"Traitement de {nom}")
```

Les instructions indentées appartiennent à la boucle. En Python, l'indentation n'est pas décorative : elle détermine la structure du programme. Utilisez une indentation cohérente, généralement quatre espaces par niveau.

### 9.2 La condition `if`

```python
if sortie.strip():
    print("La sortie n'est pas vide.")
else:
    print("La sortie est vide ou composée d'espaces.")
```

`strip()` retire les espaces et retours en début et fin de chaîne. L'expression teste si du contenu subsiste. Cela constitue un contrôle utile, mais la sortie non vide peut encore contenir un message d'erreur CLI ; il faut donc définir ce que l'on attend réellement.

### 9.3 La fonction

Une fonction regroupe des instructions et peut retourner un résultat :

```python
def nommer_fichier(nom, commande):
    return f"{nom}__{commande.replace(' ', '-')}.txt"

print(nommer_fichier("R1", "show version"))
```

Une fonction de collecte peut recevoir l'adresse et les paramètres d'un équipement, puis retourner un statut. Cette séparation facilite les tests et évite de réécrire le même code dans plusieurs branches. Des fonctions courtes et bien nommées sont souvent plus faciles à comprendre que de longs blocs contenant toutes les étapes à la fois.

### 9.4 Comprendre `return` et `print`

`print()` écrit du texte dans le terminal. `return` renvoie une valeur à la fonction appelante. Les deux opérations sont différentes : pour préparer un rapport, retourner un dictionnaire structuré est souvent plus pratique que d'imprimer tous les détails depuis la fonction elle-même.

### 9.5 La signification de `None`

`None` représente l'absence de valeur. Dans le premier script, `connexion = None` signifie qu'aucune session n'a encore été créée. Le test `if connexion is not None` permet donc d'appeler `disconnect()` uniquement si la variable contient un objet de connexion.

## 10. Commandes d'exploitation et commandes de configuration

Il faut comprendre clairement la différence entre lire l'état d'un équipement et le modifier.

### 10.1 Lecture seule : `send_command()`

Exemples classiques sur une plateforme Cisco IOS, si les commandes sont prises en charge :

```python
sortie_version = connexion.send_command("show version")
sortie_interfaces = connexion.send_command("show ip interface brief")
sortie_routes = connexion.send_command("show ip route")
```

Ces exemples sont des commandes d'observation. Elles ne devraient pas modifier la configuration. Les commandes équivalentes d'un autre constructeur peuvent être différentes. Même une commande qui semble informative peut être coûteuse sur certains équipements, donc vérifiez les pratiques de la plateforme et évitez d'interroger trop fréquemment les systèmes à forte charge.

### 10.2 Configuration : `send_config_set()`

`send_config_set()` envoie un ensemble de commandes de configuration. Selon l'appareil, la liste peut changer des interfaces, des routes, des politiques de sécurité, des paramètres de journalisation ou d'autres éléments opérationnels. Il ne faut donc jamais remplacer automatiquement chaque `send_command()` par `send_config_set()`.

Voici un exemple exclusivement pédagogique à exécuter dans un laboratoire Cisco IOS isolé, après avoir compris le changement :

```python
commandes_configuration = [
    "interface Loopback123",
    "description LAB-PYTHON-NETMIKO",
    "ip address 192.0.2.123 255.255.255.255",
]

# Cette opération crée ou modifie une configuration.
# Ne l'exécutez pas sur un réseau de production sans autorisation,
# revue, fenêtre de changement et plan de retour arrière.
# sortie_config = connexion.send_config_set(commandes_configuration)
# print(sortie_config)
```

L'appel est commenté intentionnellement : copier-coller le cours ne doit pas appliquer le changement. L'interface Loopback123 est un exemple de laboratoire, pas une recommandation de nommage ou d'adressage pour une organisation réelle. Avant d'appliquer une configuration, confirmez la plateforme, la syntaxe, les prérequis, la portée, les dépendances et le moyen de vérifier le résultat.

### 10.3 Le principe de la pré-vérification et de la post-vérification

Une procédure de changement responsable enregistre l'état initial, applique la modification autorisée, puis vérifie l'état obtenu. Une commande qui ne retourne pas d'exception Python peut tout de même avoir été rejetée par le CLI. Il faut comparer les observations avant et après, et rechercher les messages d'erreur dans la sortie.

Pour un changement qui peut interrompre la connectivité, prévoyez une méthode de récupération indépendante de la session affectée, ainsi qu'une sauvegarde ou une méthode de retour arrière validée. Une commande de sauvegarde de configuration peut être spécifique à une plateforme ; elle ne doit pas être envoyée aveuglément à tous les appareils.

<!-- Schéma SVG animé intégré : Garde-fous avant un changement de configuration -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 570" role="img" aria-labelledby="nm06-title nm06-desc"><title id="nm06-title">Garde-fous avant un changement de configuration</title><desc id="nm06-desc">Une modification suit les étapes autorisation, pré-vérification, aperçu, validation humaine, application, post-vérification et arrêt ou retour arrière documenté.</desc>
<defs><linearGradient id="nm06-bg" x2="1" y2="1"><stop stop-color="#101827"/><stop offset="1" stop-color="#203348"/></linearGradient><marker id="nm06-ar" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#6ee7f9"/></marker><style>.nm06-h{font:700 26px system-ui;fill:#f8fafc}.nm06-t{font:700 17px system-ui;fill:#f8fafc}.nm06-s{font:14px system-ui;fill:#dbeafe}.nm06-blue{fill:#1e3a5f;stroke:#60a5fa;stroke-width:2}.nm06-green{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm06-red{fill:#4b2833;stroke:#fb7185;stroke-width:2}.nm06-e{fill:none;stroke:#6ee7f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm06-ar);animation:nm06-dash 1s linear infinite}@keyframes nm06-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm06-e{animation:none}}</style></defs><rect width="1200" height="570" rx="24" fill="url(#nm06-bg)"/><text x="40" y="48" class="nm06-h">Une configuration n'est jamais un simple « send »</text><text x="40" y="76" class="nm06-s">Pour apprendre, utiliser un lab isolé et une modification réversible. En production, suivre le processus de changement approuvé.</text>
<g><rect x="40" y="130" width="210" height="98" rx="14" class="nm06-blue"/><text x="60" y="164" class="nm06-t">1. Autorisation</text><text x="60" y="192" class="nm06-s">Cible et périmètre</text><rect x="285" y="130" width="210" height="98" rx="14" class="nm06-blue"/><text x="305" y="164" class="nm06-t">2. Pré-vérifier</text><text x="305" y="192" class="nm06-s">État initial / sauvegarde</text><rect x="530" y="130" width="210" height="98" rx="14" class="nm06-blue"/><text x="550" y="164" class="nm06-t">3. Aperçu</text><text x="550" y="192" class="nm06-s">Diff / commandes planifiées</text><rect x="775" y="130" width="210" height="98" rx="14" class="nm06-green"/><text x="795" y="164" class="nm06-t">4. Validation</text><text x="795" y="192" class="nm06-s">Approbation explicite</text><rect x="1020" y="130" width="145" height="98" rx="14" class="nm06-red"/><text x="1037" y="164" class="nm06-t">5. Appliquer</text><text x="1037" y="192" class="nm06-s">Un lot limité</text><path class="nm06-e" d="M250 179 H277"/><path class="nm06-e" d="M495 179 H522"/><path class="nm06-e" d="M740 179 H767"/><path class="nm06-e" d="M985 179 H1012"/>
<path class="nm06-e" d="M1090 228 V300 H880 V337"/><rect x="690" y="337" width="380" height="91" rx="14" class="nm06-green"/><text x="715" y="372" class="nm06-t">6. Post-vérifier</text><text x="715" y="400" class="nm06-s">Tester le service, comparer l'état</text><path class="nm06-e" d="M690 382 H590"/><rect x="205" y="337" width="385" height="91" rx="14" class="nm06-blue"/><text x="230" y="372" class="nm06-t">7. Documenter</text><text x="230" y="400" class="nm06-s">Résultat, preuve et décision</text></g>
<rect x="40" y="468" width="1125" height="64" rx="13" fill="#0b1320" stroke="#fb7185"/><text x="64" y="494" class="nm06-t">Stop si l'état initial est inconnu, si la cible ne correspond pas ou si la vérification échoue.</text><text x="64" y="518" class="nm06-s">Le retour arrière doit être préparé, testé si possible et compatible avec la plateforme : il n'est pas magique.</text></svg>

## 11. Gérer les erreurs avec méthode

Les erreurs font partie de l'automatisation. Le bon comportement n'est pas de prétendre qu'elles n'arrivent jamais, mais de les rendre visibles, de limiter leur portée et d'enregistrer suffisamment d'informations pour les résoudre.

### 11.1 Les catégories d'erreur fréquentes

| Symptôme | Causes possibles | Première vérification |
|---|---|---|
| Délai dépassé | Route absente, filtrage, équipement hors ligne, SSH lent | Test de connectivité et service SSH depuis le même poste. |
| Authentification refusée | Mauvais compte, mot de passe incorrect, clé absente, politique d'accès | Identifiants, méthode autorisée et journaux d'authentification. |
| Erreur de clé d'hôte | Clé inconnue, clé modifiée, mauvaise cible ou intervention légitime | Vérifier l'empreinte par un canal de confiance. |
| Invite non reconnue | `device_type` incorrect, invite personnalisée, mode inattendu | Vérifier le pilote et la session interactive manuelle. |
| Sortie coupée ou lente | Commande volumineuse, délai de lecture trop court, pagination | Examiner la commande, les temporisations et les options compatibles. |
| Commande rejetée | Syntaxe incompatible, privilèges insuffisants, mauvais mode CLI | Tester manuellement sur le même système et consulter la documentation du constructeur. |
| Fichier non créé | Dossier absent, permissions, chemin inattendu | Afficher le chemin courant, vérifier les droits et l'existence du dossier. |
| Plusieurs appareils en échec | Identifiants communs incorrects, routage ou ACL, erreur d'inventaire | Examiner d'abord les éléments partagés avant de conclure à plusieurs pannes indépendantes. |

### 11.2 Séparer les erreurs de connexion des erreurs d'analyse

Une erreur de connexion intervient avant que le script ait obtenu une sortie. Une erreur d'analyse intervient après la collecte, quand le script essaie de lire ou de transformer le texte. Ces deux catégories demandent des informations différentes. Dans le premier cas, l'adresse, le port, le compte et le message SSH sont précieux. Dans le second, conservez l'échantillon brut, la version de commande et les champs que le parseur attendait.

Évitez de mettre tout le programme dans un seul `try/except` qui affiche simplement « erreur ». Une telle approche cache l'étape où le problème est apparu et rend difficile la distinction entre un équipement inaccessible et une sortie malformée. Dans le petit script du cours, le traitement reste simple, mais à mesure que le projet grandit, structurez les exceptions par étape.

### 11.3 Ne pas ignorer les erreurs

Ce motif est à éviter :

```python
try:
    sortie = connexion.send_command("show version")
except Exception:
    pass  # Mauvaise pratique : l'erreur disparaît.
```

Un échec silencieux peut faire croire qu'une collecte est complète alors qu'elle ne l'est pas. Au minimum, indiquez l'équipement, l'étape et le type d'erreur. Ne consignez pas de mot de passe, de clé privée ou de jeton. Les sorties réseau elles-mêmes peuvent contenir des informations confidentielles : contrôlez les accès aux journaux et aux répertoires de collecte.

### 11.4 Distinguer erreur Python et erreur CLI

Une commande invalide peut être acceptée par la couche SSH et exécutée par la CLI, qui renvoie un texte comme « commande inconnue » ou « syntaxe incorrecte ». Python reçoit alors une sortie textuelle, sans nécessairement lever d'exception. C'est pourquoi les scripts fiables examinent les résultats, et pas uniquement les exceptions.

Une stratégie d'apprentissage consiste à faire un test volontairement invalide dans un environnement de laboratoire, à observer la sortie, puis à définir une règle de détection adaptée à la plateforme. Ne déployez pas une recherche générique de mot comme `Invalid` sans connaître les messages possibles : la langue, la version et le contexte peuvent changer.

<!-- Schéma SVG animé intégré : Arbre de diagnostic des erreurs Netmiko -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 610" role="img" aria-labelledby="nm07-title nm07-desc"><title id="nm07-title">Arbre de diagnostic des erreurs Netmiko</title><desc id="nm07-desc">Départ depuis une connexion qui échoue, puis séparation connectivité, authentification, prompt ou commande et sortie.</desc>
<defs><linearGradient id="nm07-bg" x2="0" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#1a3046"/></linearGradient><marker id="nm07-ar" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker><style>.nm07-h{font:700 25px system-ui;fill:#f8fafc}.nm07-t{font:700 17px system-ui;fill:#f8fafc}.nm07-b{font:14px system-ui;fill:#dbeafe}.nm07-q{fill:#1e3a5f;stroke:#67e8f9;stroke-width:2}.nm07-yes{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm07-no{fill:#4b2833;stroke:#fb7185;stroke-width:2}.nm07-e{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm07-ar);animation:nm07-dash 1s linear infinite}@keyframes nm07-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm07-e{animation:none}}</style></defs><rect width="1200" height="610" rx="24" fill="url(#nm07-bg)"/><text x="40" y="48" class="nm07-h">Diagnostiquer par étapes, sans tout changer à la fois</text><rect x="400" y="78" width="400" height="68" rx="14" class="nm07-q"/><text x="435" y="106" class="nm07-t">La connexion SSH s'établit-elle ?</text><text x="435" y="128" class="nm07-b">Timeout / refus / clé d'hôte / auth</text>
<path class="nm07-e" d="M490 146 L270 203"/><path class="nm07-e" d="M710 146 L930 203"/><text x="355" y="170" class="nm07-b">Non</text><text x="800" y="170" class="nm07-b">Oui</text>
<rect x="70" y="203" width="405" height="91" rx="14" class="nm07-no"/><text x="95" y="237" class="nm07-t">Contrôler le transport</text><text x="95" y="264" class="nm07-b">Route, ACL, port, service SSH, temps</text><rect x="725" y="203" width="405" height="91" rx="14" class="nm07-q"/><text x="750" y="237" class="nm07-t">La commande renvoie-t-elle la sortie attendue ?</text><text x="750" y="264" class="nm07-b">Invite, privilèges, syntaxe, pagination</text>
<path class="nm07-e" d="M840 294 L700 354"/><path class="nm07-e" d="M1010 294 L1040 354"/><text x="765" y="325" class="nm07-b">Non</text><text x="1040" y="325" class="nm07-b">Oui</text><rect x="520" y="354" width="350" height="91" rx="14" class="nm07-no"/><text x="545" y="388" class="nm07-t">Vérifier la plateforme</text><text x="545" y="415" class="nm07-b">device_type, prompt, commande CLI</text><rect x="900" y="354" width="250" height="91" rx="14" class="nm07-yes"/><text x="925" y="388" class="nm07-t">Valider la sortie</text><text x="925" y="415" class="nm07-b">Contenu, horodatage, fichier</text>
<rect x="70" y="492" width="1060" height="70" rx="13" fill="#0b1320" stroke="#475569"/><text x="95" y="520" class="nm07-t">Toujours collecter un indice</text><text x="95" y="544" class="nm07-b">Message d'erreur complet, cible, heure, étape et test qui a réussi ou échoué.</text></svg>

## 12. Sécurité de base pour un script de réseau

L'automatisation peut amplifier une erreur : une instruction manuelle incorrecte touche un appareil, alors qu'une boucle mal conçue peut toucher tous les appareils d'un inventaire. La sécurité et la sûreté opérationnelle sont donc des éléments du programme, pas des ajouts après coup.

### 12.1 Utiliser un compte à privilèges limités

Si le script collecte des informations, attribuez-lui un accès limité aux commandes de consultation nécessaires. Ne donnez pas systématiquement les droits d'administration complète. Les privilèges minimum limitent l'impact d'un bug, d'un poste compromis ou d'une mauvaise utilisation du script.

### 12.2 Vérifier l'identité du serveur SSH

L'authentification du client et la vérification de l'identité du serveur sont deux choses distinctes. Un utilisateur peut entrer un mot de passe correct sur un hôte qui n'est pas le bon, ou sur un hôte dont l'identité est usurpée. Vérifiez l'empreinte de clé d'hôte à l'aide d'une source fiable et suivez les mécanismes et politiques supportés par la version de Netmiko et le système de votre organisation.

Ne désactivez pas les vérifications de clé d'hôte uniquement pour éviter un avertissement pendant un exercice. Les paramètres Netmiko `ssh_strict=True` et `system_host_keys=True` présentés dans les scripts font échouer la connexion si l'identité du serveur n'est pas reconnue dans les clés de confiance chargées. Si votre laboratoire utilise un mécanisme de confiance simplifié, indiquez précisément cette limite et ne recopiez pas cette configuration telle quelle dans un environnement de production. Une modification inattendue de clé connue mérite une investigation avant de poursuivre. Un utilitaire qui récupère une clé depuis le réseau peut aider à préparer une entrée, mais il ne confirme pas à lui seul que la clé appartient au bon équipement : l'empreinte doit être vérifiée par un canal fiable.

### 12.3 Protéger les fichiers et sorties

Une sortie `show running-config` peut contenir des noms, des adresses, des éléments de topologie et parfois des secrets mal protégés ou des données internes. Les sorties d'exploitation peuvent elles-mêmes être sensibles. Les sauvegardes doivent avoir des permissions appropriées, un emplacement approuvé, une durée de conservation définie et un accès contrôlé.

Ne publiez pas les captures ou fichiers de collecte dans un dépôt ouvert. Ne les envoyez pas à une personne non autorisée. Avant de partager un extrait pour demander de l'aide, retirez les secrets et les éléments identifiants selon une procédure cohérente, sans altérer les données nécessaires au diagnostic.

### 12.4 Limiter la portée d'une exécution

Commencez avec une seule cible. Ajoutez un second appareil de laboratoire après validation. Utilisez un inventaire explicite et relisez-le avant le lancement. Pour une action de configuration, vérifiez à nouveau le nom de l'appareil, les commandes, le nombre de cibles et l'environnement. Un filtre ou une liste d'exclusion ne constitue pas un garde-fou suffisant si la portée réelle n'est pas confirmée.

## 13. Un mini-projet de débutant : collecte quotidienne

Le mini-projet rassemble les notions des sections précédentes. Sa version initiale doit rester sans modification de configuration.

### 13.1 Besoin

Chaque jour, l'équipe veut conserver une sortie `show version` pour deux appareils de laboratoire. Le rapport doit identifier l'équipement, indiquer si la collecte a réussi, enregistrer l'emplacement du fichier et préserver le message d'erreur si la connexion échoue.

### 13.2 Critères de réussite

Le projet est réussi lorsque :

- la collecte s'exécute sur chaque appareil indépendamment ;
- un appareil inaccessible ne bloque pas l'autre ;
- le résultat de chaque cible est identifié sans ambiguïté ;
- une sortie vide n'est pas automatiquement considérée comme une réussite ;
- les sorties sont sauvegardées avec un encodage cohérent ;
- le rapport final compte les succès et les échecs ;
- aucun mot de passe n'apparaît dans les fichiers ou les logs ;
- la session est fermée même après une exception.

### 13.3 Améliorations progressives

Une fois ce comportement confirmé, ajoutez une commande de lecture supplémentaire. Puis ajoutez un horodatage et une durée d'exécution. Ensuite, comparez deux collectes pour détecter les changements inattendus. Enfin, externalisez l'inventaire vers un fichier et validez les données avant de lancer la connexion.

N'ajoutez pas toutes les fonctionnalités en même temps. Lorsqu'un script échoue, une seule nouvelle complexité rend la cause plus facile à trouver. Conservez quelques sorties de référence, qui serviront de tests pour les modifications du parseur ou du format de rapport.

<!-- Schéma SVG animé intégré : Pipeline du mini-projet de collecte -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 570" role="img" aria-labelledby="nm08-title nm08-desc"><title id="nm08-title">Mini-projet : sauvegarder des sorties réseau</title><desc id="nm08-desc">Inventaire, connexion, commande show, sauvegarde dans un fichier individuel, validation et résumé final.</desc>
<defs><linearGradient id="nm08-bg" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#20364c"/></linearGradient><marker id="nm08-ar" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker><style>.nm08-h{font:700 26px system-ui;fill:#f8fafc}.nm08-t{font:700 18px system-ui;fill:#f8fafc}.nm08-s{font:14px system-ui;fill:#dbeafe}.nm08-n{fill:#1d3853;stroke:#60a5fa;stroke-width:2}.nm08-g{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm08-e{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm08-ar);animation:nm08-dash 1s linear infinite}@keyframes nm08-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm08-e{animation:none}}</style></defs><rect width="1200" height="570" rx="24" fill="url(#nm08-bg)"/><text x="42" y="48" class="nm08-h">Projet guidé : collecte en lecture seule</text><text x="42" y="76" class="nm08-s">Objectif : produire des preuves organisées, même lorsque l'un des équipements ne répond pas.</text>
<rect x="40" y="145" width="200" height="104" rx="15" class="nm08-n"/><text x="61" y="180" class="nm08-t">Inventaire</text><text x="61" y="208" class="nm08-s">hosts + device_type</text><rect x="280" y="145" width="200" height="104" rx="15" class="nm08-n"/><text x="301" y="180" class="nm08-t">Connexion SSH</text><text x="301" y="208" class="nm08-s">authentifier proprement</text><rect x="520" y="145" width="200" height="104" rx="15" class="nm08-n"/><text x="541" y="180" class="nm08-t">Commande show</text><text x="541" y="208" class="nm08-s">ex. show version</text><rect x="760" y="145" width="200" height="104" rx="15" class="nm08-n"/><text x="781" y="180" class="nm08-t">Fichier</text><text x="781" y="208" class="nm08-s">un fichier par cible</text><rect x="1000" y="145" width="160" height="104" rx="15" class="nm08-g"/><text x="1020" y="180" class="nm08-t">Résumé</text><text x="1020" y="208" class="nm08-s">succès / erreur</text><path class="nm08-e" d="M240 197 H272"/><path class="nm08-e" d="M480 197 H512"/><path class="nm08-e" d="M720 197 H752"/><path class="nm08-e" d="M960 197 H992"/>
<rect x="70" y="325" width="480" height="150" rx="16" fill="#0b1320" stroke="#475569"/><text x="95" y="360" class="nm08-t">Dossier de collecte</text><text x="95" y="393" class="nm08-s">outputs/</text><text x="115" y="420" class="nm08-s">R1__show-version.txt</text><text x="115" y="445" class="nm08-s">SW1__show-version.txt</text><rect x="610" y="325" width="520" height="150" rx="16" fill="#0b1320" stroke="#475569"/><text x="635" y="360" class="nm08-t">Rapport d'exécution</text><text x="635" y="393" class="nm08-s">date UTC ou fuseau documenté · durée</text><text x="635" y="420" class="nm08-s">état par appareil · erreur sans mot de passe</text><text x="635" y="445" class="nm08-s">commandes exécutées · version du script</text><text x="42" y="525" class="nm08-s">Ce projet ne modifie aucune configuration ; la conservation des sorties reste une responsabilité de sécurité.</text></svg>

### 13.4 Extensions possibles sans toucher à la configuration

1. Collecter la date et l'heure de l'équipement si la commande de consultation est prise en charge.
2. Compter les interfaces dans une sortie dont le format est connu.
3. Générer un CSV à partir des statuts de collecte à l'aide de `csv.DictWriter`.
4. Écrire un journal d'exécution avec `logging`.
5. Ajouter une validation des noms et des types de plateforme dans l'inventaire.
6. Calculer un hash des fichiers collectés pour repérer une altération ultérieure, en sachant qu'un hash ne prouve pas que la capture ou la collecte était complète.
7. Ajouter un mode simulation qui affiche les actions prévues sans se connecter ni modifier quoi que ce soit.

## 14. Introduction à la journalisation avec `logging`

`print()` est utile dans les premiers essais, mais les scripts maintenus par une équipe gagnent à utiliser le module standard `logging`. La journalisation peut distinguer un événement informatif d'un avertissement ou d'une erreur, inclure un horodatage et diriger les messages vers la console ou un fichier.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.info("Début de la collecte")
logging.warning("Une cible n'a pas répondu")
logging.error("La collecte d'un appareil a échoué")
```

Utilisez `logging.info()` pour les événements normaux, `logging.warning()` pour une situation inattendue mais gérable, et `logging.error()` pour un échec. Un log utile comprend généralement le nom de la cible, l'étape, un statut, éventuellement la durée et le type d'erreur. Le message ne doit pas contenir de mot de passe. Évitez également d'imprimer la totalité des sorties sensibles dans les logs généraux si elles sont déjà sauvegardées dans un répertoire sécurisé.

Pour aller plus loin, les étapes peuvent être chronométrées avec le module `time` ou `time.perf_counter()`. Comparez les durées de la même opération dans des conditions similaires : une lenteur peut venir du réseau, du temps de réponse du CLI ou de la quantité de texte transférée.

## 15. Les erreurs typiques du débutant et comment les éviter

### Erreur 1 — Mauvais `device_type`

Le type déclaré doit correspondre à la plateforme et au système d'exploitation exécuté sur l'équipement. Un nom commercial générique ne suffit pas. Confirmez la valeur prise en charge dans la documentation de la version installée. Un mauvais pilote peut provoquer des problèmes de préparation de session, d'invite ou de gestion des commandes.

### Erreur 2 — Copier une commande CLI d'un constructeur à un autre

Les commandes d'affichage et de configuration varient selon les OS, même lorsque les équipements ont une fonction similaire. Gardez l'inventaire et les commandes associés à une plateforme connue. Pour un parc multi-constructeur, le code pourra choisir les commandes par type d'appareil, après des tests dédiés.

### Erreur 3 — Mettre tous les mots de passe dans le fichier

Ne placez pas les secrets dans l'inventaire. Utilisez une méthode de gestion des secrets approuvée, limitez les privilèges et contrôlez les fichiers. Un fichier de code partagé n'est pas un endroit approprié pour des identifiants réels.

### Erreur 4 — Penser qu'une exception signifie toujours « réseau en panne »

Un échec peut provenir des identifiants, de la clé d'hôte, d'une dépendance Python ou du choix du pilote. Lisez le message complet, identifiez l'étape et testez chaque couche. Ne changez pas simultanément le port, les identifiants, le pilote et les temporisations : vous ne saurez plus quelle modification a résolu ou aggravé le problème.

### Erreur 5 — Oublier la fermeture de la session

Fermez proprement toute session ouverte. Dans les exemples du cours, `finally` remplit cette fonction. Une session abandonnée peut consommer les ressources de l'équipement et brouiller les essais suivants.

### Erreur 6 — Accepter une sortie vide comme réussite

Une chaîne vide peut signaler une commande qui n'a rien retourné, un problème de lecture ou une condition inattendue. Vérifiez le résultat prévu. Pour certaines commandes, une sortie vide est légitime ; le critère doit donc être spécifique à la commande, pas systématiquement imposé à tous les cas.

### Erreur 7 — Lancer la boucle sur tout le parc dès le premier essai

Testez une cible, puis un petit lot de laboratoire. Les problèmes d'inventaire, de privilèges ou de commande se multiplient lorsque le script est lancé à grande échelle. Une collecte séquentielle est plus lente qu'une exécution concurrente, mais elle est généralement plus simple à comprendre pour commencer.

### Erreur 8 — Confondre collecte réussie et diagnostic correct

Un script peut parfaitement récupérer une sortie qui révèle un état problématique. Le succès technique de la connexion n'est pas le succès opérationnel de l'équipement. Les futurs niveaux apprendront à transformer les sorties en données puis à vérifier des conditions attendues.

## 16. Exercices pratiques gradués

Effectuez ces exercices sur un environnement de laboratoire autorisé. Conservez le code et les sorties de référence afin de pouvoir expliquer vos résultats.

### Exercice 1 — Première session

Écrivez un script qui se connecte à un équipement, exécute une commande de lecture seule et affiche la sortie. Ajoutez un bloc de fermeture propre. Indiquez quels paramètres sont spécifiques à la plateforme.

**Critère de réussite :** vous pouvez expliquer chaque ligne qui établit la connexion, la commande envoyée et la fermeture de la session.

### Exercice 2 — Écriture dans un fichier

Modifiez le script afin d'enregistrer la sortie dans `outputs/`. Le nom du fichier doit inclure le nom de l'équipement et la commande. Vérifiez que le fichier n'est pas créé dans un dossier inattendu.

**Critère de réussite :** une autre personne peut retrouver quelle sortie correspond à quel appareil sans ouvrir tous les fichiers.

### Exercice 3 — Plusieurs équipements

Ajoutez un deuxième appareil de laboratoire à l'inventaire. Utilisez une boucle `for` et affichez un statut pour chaque cible. Provoquez un échec contrôlé, par exemple avec une adresse de test non routable, uniquement dans l'environnement autorisé.

**Critère de réussite :** le résultat du second équipement est toujours traité et le rapport indique quel appareil a échoué.

### Exercice 4 — Détecter une sortie inattendue

Choisissez une commande connue, puis simulez une commande incorrecte en laboratoire. Examinez ce que Netmiko renvoie. Ajoutez une validation qui distingue une réponse acceptable d'un message d'erreur CLI connu.

**Critère de réussite :** le programme ne confond plus automatiquement une réponse textuelle avec une opération réussie.

### Exercice 5 — Rapport d'exécution

Créez un fichier CSV qui contient au moins le nom de l'appareil, son adresse, le statut, le chemin du résultat et le message d'erreur. Pour un vrai CSV, utilisez le module standard `csv` au lieu de construire les lignes par concaténation de chaînes.

**Critère de réussite :** le fichier s'ouvre correctement même si un champ contient une virgule ou un retour à la ligne.

### Exercice 6 — Réduire le risque

Créez un mode qui imprime la liste des équipements et la commande prévue, sans établir de session. Comparez le périmètre affiché avec l'inventaire. Écrivez ensuite une courte procédure de lancement.

**Critère de réussite :** vous pouvez vérifier la cible et la portée avant l'exécution réelle.

### Exercice 7 — Changement contrôlé, uniquement en laboratoire

À ce stade seulement, étudiez un exemple de configuration réversible sur une instance isolée. Écrivez le plan de changement et la commande de vérification avant d'écrire l'appel `send_config_set()`. Faites relire le plan et préparez le retour arrière avant application.

**Critère de réussite :** vous pouvez démontrer l'état initial, la modification, la validation après changement et la méthode de récupération. Si un environnement de laboratoire adapté n'est pas disponible, réalisez l'exercice sous forme de plan papier sans exécuter la modification.

## 17. Questions de révision

1. Quelle est la différence entre Python, SSH et Netmiko ?
2. Pourquoi `device_type` doit-il correspondre à la plateforme réelle ?
3. Quelle est la différence entre `send_command()` et `send_config_set()` ?
4. Pourquoi le mot de passe ne doit-il pas être écrit dans le code source ?
5. Que garantit le bloc `finally` dans le premier script ?
6. Pourquoi un script peut-il recevoir un texte d'erreur CLI sans lever d'exception Python ?
7. Pourquoi vaut-il mieux traiter les appareils un par un lors des premiers essais ?
8. Quelles informations minimales doivent apparaître dans un rapport d'échec ?
9. Pourquoi la vérification de la clé d'hôte SSH reste-t-elle importante ?
10. Pourquoi une connexion réussie ne prouve-t-elle pas que le service réseau fonctionne comme attendu ?

### Éléments de réponse

1. Python orchestre la logique ; SSH transporte et protège la session distante ; Netmiko facilite l'interaction avec le CLI de plusieurs plateformes.
2. Le pilote adapte le comportement de session aux caractéristiques de la plateforme. Un mauvais choix peut perturber la connexion ou la lecture des commandes.
3. `send_command()` sert généralement à exécuter des commandes d'exploitation ; `send_config_set()` transmet des commandes qui peuvent modifier la configuration.
4. Le code est souvent copié, archivé et partagé. Un secret écrit en clair peut fuiter dans un dépôt, une capture d'écran, un journal ou un paquet de livraison.
5. `finally` permet d'exécuter le nettoyage même si une exception survient, sous réserve que le programme ait atteint le bloc et que la fermeture soit possible.
6. Le CLI peut exécuter la commande puis renvoyer un texte d'erreur, tandis que la communication SSH a fonctionné normalement.
7. Le traitement séquentiel facilite l'observation du déroulement, réduit les variables et permet de diagnostiquer chaque appareil séparément.
8. Identité de la cible, étape de l'échec, heure, type ou message d'erreur, statut et action suivante recommandée, sans secret.
9. Une session chiffrée ne suffit pas à prouver que le serveur contacté est bien celui attendu ; la clé d'hôte contribue à vérifier l'identité du serveur.
10. La commande peut avoir été rejetée, l'application peut être défaillante ou la sortie peut signaler un état non conforme. Il faut valider le résultat opérationnel.

## 18. Préparer la suite : le lien avec les niveaux suivants

Le niveau Débutant construit la chaîne fondamentale : choisir une cible, préparer des paramètres, ouvrir une session, envoyer une commande, récupérer un résultat, traiter l'échec et fermer la connexion. Les niveaux suivants ne vont pas remplacer cette chaîne ; ils vont l'enrichir.

Au niveau **Intermédiaire**, la liste d'appareils sera déplacée dans un inventaire externe. Les sorties brutes seront transformées en données structurées, les tests de validation seront ajoutés, les logs seront plus précis et les changements seront comparés à un état attendu avant d'être appliqués. Vous apprendrez à employer des outils de parsing lorsque le format CLI s'y prête, tout en conservant la sortie originale pour audit.

Au niveau **Expert**, l'accent portera sur la conception du déploiement, les lots contrôlés, les pré-vérifications, les validations après changement, la stratégie de retour arrière, l'observabilité, la gestion des secrets à l'échelle et l'orchestration. Les scripts devront être testés, mesurables et adaptés à des défaillances partielles.

<!-- Schéma SVG animé intégré : Progression pédagogique de l'automatisation réseau -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520" role="img" aria-labelledby="nm09-title nm09-desc"><title id="nm09-title">Progression de la série d'automatisation réseau</title><desc id="nm09-desc">Trois étapes liées : débutant apprend une session et des commandes en lecture seule ; intermédiaire ajoute inventaire et validation ; expert ajoute tests, déploiement contrôlé, observabilité et gestion du changement.</desc>
<defs><linearGradient id="nm09-bg" x2="0" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#1a3147"/></linearGradient><marker id="nm09-arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#6ee7f9"/></marker><style>.nm09-h{font:700 26px system-ui;fill:#f8fafc}.nm09-t{font:700 22px system-ui;fill:#f8fafc}.nm09-s{font:15px system-ui;fill:#dbeafe}.nm09-n{fill:#1e3a5f;stroke:#60a5fa;stroke-width:2}.nm09-m{fill:#164e63;stroke:#67e8f9;stroke-width:2}.nm09-e{fill:#143d37;stroke:#6ee7b7;stroke-width:2}.nm09-line{fill:none;stroke:#6ee7f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#nm09-arr);animation:nm09-dash 1s linear infinite}@keyframes nm09-dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.nm09-line{animation:none}}</style></defs><rect width="1200" height="520" rx="24" fill="url(#nm09-bg)"/><text x="42" y="48" class="nm09-h">Chaque niveau réutilise les acquis du précédent</text>
<rect x="45" y="120" width="330" height="280" rx="18" class="nm09-n"/><text x="75" y="165" class="nm09-t">Débutant</text><text x="75" y="201" class="nm09-s">• SSH et première session</text><text x="75" y="231" class="nm09-s">• commandes read-only</text><text x="75" y="261" class="nm09-s">• variables et dictionnaires</text><text x="75" y="291" class="nm09-s">• boucle simple</text><text x="75" y="321" class="nm09-s">• erreurs et fichiers</text><text x="75" y="365" class="nm09-s">Résultat : collecte fiable</text>
<rect x="435" y="120" width="330" height="280" rx="18" class="nm09-m"/><text x="465" y="165" class="nm09-t">Intermédiaire</text><text x="465" y="201" class="nm09-s">• inventaire externe et YAML</text><text x="465" y="231" class="nm09-s">• parsing et modèles de données</text><text x="465" y="261" class="nm09-s">• tests et comparaison</text><text x="465" y="291" class="nm09-s">• secrets / logs structurés</text><text x="465" y="321" class="nm09-s">• lots contrôlés</text><text x="465" y="365" class="nm09-s">Résultat : audit reproductible</text>
<rect x="825" y="120" width="330" height="280" rx="18" class="nm09-e"/><text x="855" y="165" class="nm09-t">Expert</text><text x="855" y="201" class="nm09-s">• stratégie de déploiement</text><text x="855" y="231" class="nm09-s">• pré/post-checks et rollback</text><text x="855" y="261" class="nm09-s">• concurrence et orchestration</text><text x="855" y="291" class="nm09-s">• observabilité et validation</text><text x="855" y="321" class="nm09-s">• intégration / politiques</text><text x="855" y="365" class="nm09-s">Résultat : changement gouverné</text>
<path class="nm09-line" d="M375 260 H427"/><path class="nm09-line" d="M765 260 H817"/><text x="45" y="462" class="nm09-s">On ne saute pas les fondations : on complexifie la même chaîne en ajoutant des contrôles et de la preuve.</text></svg>

Le principe reste identique à chaque niveau : **commencer par une hypothèse claire, observer avec une méthode reproductible, préserver les preuves, valider le résultat et annoncer les limites**. Plus l'action est risquée, plus la vérification et la gouvernance doivent être fortes.

## 19. Références et documentation officielle

Consultez les sources officielles au moment de mettre en place votre environnement, car les versions, les plateformes et les paramètres peuvent évoluer.

- [Netmiko sur PyPI](https://pypi.org/project/netmiko/) — version publiée, métadonnées, dépendances et instructions d'installation.
- [Dépôt GitHub officiel de Netmiko](https://github.com/ktbyers/netmiko) — code source, exemples, liste de plateformes et notes de contribution.
- [Documentation de l'API Netmiko](https://ktbyers.github.io/netmiko/) — méthodes de connexion, paramètres et comportement de l'API.
- [Guide de Netmiko](https://github.com/ktbyers/netmiko/blob/develop/README.md) — présentation et exemples de démarrage.
- [Documentation Python](https://docs.python.org/3/) — syntaxe du langage, environnements virtuels, fichiers, exceptions, `pathlib`, `logging` et module `csv`.
- [Documentation Paramiko](https://docs.paramiko.org/en/stable/) — détails SSH sous-jacents, notamment le traitement des clés d'hôte. Netmiko étant une couche de plus haut niveau, vérifiez toujours les paramètres réellement exposés par votre version.

La référence PyPI consultée pour la rédaction indiquait Netmiko 4.8.0, publié en septembre 2026, et une exigence Python déclarée de 3.10 ou plus récent. Cette indication est datée et doit être revérifiée au moment où vous installerez ou mettrez à jour le logiciel. Évitez de supposer que le dernier numéro de version est identique dans tous les environnements : une organisation peut volontairement verrouiller une version testée.

## 20. Liste de contrôle avant chaque exécution

Avant de lancer le script, prenez quelques secondes pour confirmer les points ci-dessous :

- [ ] Le dossier et l'environnement Python actifs sont ceux du projet.
- [ ] La version de Netmiko installée est connue et compatible avec la plateforme visée.
- [ ] L'adresse, le nom logique et le `device_type` sont exacts.
- [ ] Le compte utilisé est autorisé et dispose des privilèges minimum nécessaires.
- [ ] La politique de vérification de la clé d'hôte est respectée.
- [ ] La commande a été vérifiée manuellement sur une cible de test.
- [ ] Le premier passage est limité à une cible ou à un petit lot contrôlé.
- [ ] Le dossier de sortie existe et ses droits sont appropriés.
- [ ] Les exceptions sont visibles et les sessions se ferment correctement.
- [ ] Les données collectées peuvent contenir des informations sensibles et sont protégées.
- [ ] Toute action de configuration est bloquée par défaut, revue avant application et accompagnée d'un plan de vérification.

## Conclusion

Python donne les outils pour décrire une procédure ; SSH fournit une session distante protégée ; Netmiko simplifie l'interaction avec le CLI de l'équipement. Ensemble, ils permettent de passer d'une suite d'actions manuelles à une procédure répétable. Mais la valeur du script dépend de la qualité de ses hypothèses, de la sécurité de ses identifiants, du traitement des erreurs et de la validation de ses résultats.

Commencez avec une seule commande de lecture, un seul appareil et un fichier de sortie. Quand ce premier cycle devient compréhensible et reproductible, introduisez une boucle, puis un rapport et des contrôles supplémentaires. Ne passez aux changements de configuration qu'après avoir compris la portée de chaque commande, défini les vérifications avant et après, et préparé une méthode de récupération.

L'objectif du niveau Débutant n'est pas de produire immédiatement un moteur d'automatisation massif. C'est d'acquérir une base propre, prudente et compréhensible, sur laquelle les niveaux Intermédiaire et Expert pourront construire des outils plus complets sans perdre la traçabilité.
