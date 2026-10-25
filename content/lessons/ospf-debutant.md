# OSPFv2 — Niveau Débutant

**Durée indicative :** 4 à 6 heures avec les laboratoires  
**Prérequis :** adressage IPv4, masque et sous-réseau, passerelle, table de routage, ping, bases de commutation Ethernet.  
**Environnement :** Cisco Packet Tracer ou maquette IOS/IOS XE ; idéalement Wireshark pour observer les paquets OSPF.

Ce cours est le premier niveau de la série OSPF. Il enseigne OSPFv2 pour IPv4 dans une **aire unique**, afin de comprendre les mécanismes fondamentaux avant les sujets plus avancés. Le cours **Intermédiaire** pourra approfondir les aires multiples, le DR/BDR, la conception des zones, les types de LSA, l’agrégation et le dépannage plus complexe. Le niveau **Expert** abordera la convergence à grande échelle, l’optimisation, la sécurité opérationnelle et les migrations.

Aucune métadonnée de type `node_id` ou `title` n’est nécessaire en tête du fichier. Les schémas SVG ci-dessous sont intégrés directement dans le Markdown : aucun dossier d’images séparé n’est nécessaire.

> **Cadre technique :** OSPFv2 est la version destinée au routage IPv4. OSPFv3 a été conçu pour IPv6 puis a évolué pour prendre en charge plusieurs familles d’adresses selon les implémentations. Ce cours se concentre volontairement sur OSPFv2. Les commandes sont des exemples Cisco IOS/IOS XE et peuvent différer selon le matériel ou l’image de simulation. RFC 2328 décrit les bases d’OSPFv2 ; la documentation du système utilisé reste nécessaire pour les détails de plateforme.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir :

- expliquer la différence entre routage statique et routage dynamique ;
- décrire OSPF comme un protocole IGP à état de liens ;
- comprendre la fonction du Router ID, des Hello, des LSA, de la LSDB et de l’algorithme SPF ;
- identifier les conditions minimales de formation d’un voisinage OSPF ;
- lire les états de voisinage les plus importants ;
- configurer OSPFv2 dans une aire unique sur trois routeurs Cisco compatibles ;
- interpréter le coût OSPF à un niveau introductif ;
- vérifier les routes apprises et diagnostiquer les erreurs de base ;
- expliquer pourquoi un voisin `FULL` ne garantit pas à lui seul la connectivité applicative de bout en bout.

## Comment suivre le cours

Lis d’abord la logique du protocole et les schémas dans l’ordre. Ensuite réalise le laboratoire de trois routeurs, sans ajouter d’aires supplémentaires. Pour chaque manipulation, relève l’état avant, effectue un changement ciblé, puis vérifie les voisins, la base de liens et la table de routage. Ne modifie pas plusieurs paramètres simultanément : si le résultat change, tu dois pouvoir attribuer ce changement à une cause identifiable.


## 1. Pourquoi utiliser OSPF ?

### 1.1 Routage statique et routage dynamique

Une route statique est ajoutée manuellement par l’administrateur. Elle est utile pour les petits réseaux, les routes par défaut ou les chemins qui ne doivent pas être appris dynamiquement. Mais quand le réseau grandit ou qu’un lien de transport tombe, des routes statiques peuvent demander des changements manuels, à moins d’être accompagnées de mécanismes de suivi et de routes de secours adaptés.

Un protocole de routage dynamique échange des informations entre routeurs et recalcule des chemins lorsque la topologie change. Cela ne signifie pas qu’il choisit toujours la route que l’administrateur aurait préférée : les métriques, les politiques et la conception doivent être réfléchies. Un protocole dynamique doit être configuré, vérifié et sécurisé.

| Aspect | Routes statiques | OSPF dynamique |
|---|---|---|
| Configuration initiale | Chaque route est définie manuellement | Les routeurs échangent des informations selon OSPF |
| Adaptation à une panne | Dépend de la configuration et des suivis ajoutés | Peut recalculer selon la nouvelle topologie |
| Exploitation à grande échelle | Peut devenir lourde à maintenir | Permet de diffuser la connaissance de topologie et d’automatiser le calcul |
| Contrôle du chemin | Très explicite pour chaque route | Dépend des métriques et de la sélection OSPF |
| Risque principal | Oubli de mise à jour ou chemin périmé | Mauvaise annonce, mauvaise métrique, voisinage incorrect ou conception défaillante |

### 1.2 Qu’est-ce qu’OSPF ?

OSPF signifie **Open Shortest Path First**. C’est un protocole de routage intérieur (*IGP*) à état de liens. Il est utilisé au sein d’un domaine administratif, par exemple un réseau d’entreprise. Contrairement à un protocole qui transmet uniquement une liste de destinations et une distance apprise du voisin, OSPF permet aux routeurs d’échanger des informations décrivant la topologie logique du réseau.

Chaque routeur OSPF construit une **base d’état de liens** (*Link-State Database*, LSDB) pour son aire. À partir de cette base, il calcule un arbre des plus courts chemins avec l’algorithme SPF associé à Dijkstra. Le routeur utilise ensuite les résultats pour proposer des routes à sa table de routage. La LSDB représente une vue de topologie, tandis que la table de routage contient les chemins retenus pour transmettre les paquets.

La distinction est essentielle : recevoir des informations OSPF ne veut pas dire installer immédiatement toutes les routes. Une route peut être absente parce que le réseau n’a pas été annoncé, que l’interface est passive, qu’une autre route est préférée, que la LSDB ne contient pas le lien attendu ou que le prochain saut ne peut pas être résolu.

### Schéma 1 — Vue d’ensemble d’OSPF dans une aire

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 455" role="img" aria-label="OSPFv2 dans une aire unique" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="455" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">OSPFv2 dans une aire unique</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">OSPF échange des informations de topologie, puis chaque routeur calcule localement ses routes.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="70" y="165" width="190" height="92" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="165.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1</text>
<text x="165.0" y="214" text-anchor="middle" fill="#adbdcf" font-size="12">RID 1.1.1.1</text>
<text x="165.0" y="230" text-anchor="middle" fill="#adbdcf" font-size="12">LAN 192.0.2.0/24</text>
<rect x="385" y="165" width="190" height="92" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="480.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2</text>
<text x="480.0" y="214" text-anchor="middle" fill="#adbdcf" font-size="12">RID 2.2.2.2</text>
<text x="480.0" y="230" text-anchor="middle" fill="#adbdcf" font-size="12">Transit 10.0.12.0/30</text>
<rect x="700" y="165" width="190" height="92" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="795.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3</text>
<text x="795.0" y="214" text-anchor="middle" fill="#adbdcf" font-size="12">RID 3.3.3.3</text>
<text x="795.0" y="230" text-anchor="middle" fill="#adbdcf" font-size="12">LAN 198.51.100.0/24</text>
<line x1="260" y1="210" x2="385" y2="210" stroke="#45c7f5" stroke-width="5" stroke-linecap="round"/>
<line x1="575" y1="210" x2="700" y2="210" stroke="#45c7f5" stroke-width="5" stroke-linecap="round"/>
<text x="322" y="192" fill="#adbdcf" font-size="12" text-anchor="middle">Hello / DBD / LSU</text>
<text x="637" y="192" fill="#adbdcf" font-size="12" text-anchor="middle">LSA flooding</text>
<circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 260 210 L 385 210" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 700 210 L 575 210" dur="2.5s" begin="1s" repeatCount="indefinite"/></circle>
<rect x="90" y="320" width="780" height="72" rx="13" fill="#111c2a" stroke="#7dd3fc" stroke-width="2"/>
<text x="480.0" y="347" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Même aire : 0.0.0.0</text>
<text x="480.0" y="369" text-anchor="middle" fill="#adbdcf" font-size="12">Les routeurs apprennent la topologie de l’aire ; le calcul SPF est local à chaque routeur.</text>
<text x="480" y="425" text-anchor="middle" fill="#eef4fb" font-size="13">OSPF ne transmet pas simplement une route « toute prête » : il synchronise une base d’état de liens.</text>
<text x="480.0" y="438" text-anchor="middle" fill="#adbdcf" font-size="11">Topologie pédagogique. Les adresses en 192.0.2.0/24 et 198.51.100.0/24 sont réservées à la documentation.</text>
</svg>
</div>


**Lecture du schéma :** les routeurs échangent des messages OSPF sur les liens. Les mises à jour transportent des annonces d’état de liens ; chaque routeur maintient sa base et effectue localement son calcul SPF. Les points animés montrent un échange illustratif et ne représentent pas le débit ou la chronologie exacte du protocole.

### 1.3 OSPF ne remplace pas le plan d’adressage

OSPF peut propager des préfixes IPv4, mais il ne choisit pas à ta place les réseaux qui devraient exister. Avant de configurer le protocole, il faut connaître les adresses et les masques des interfaces, les liaisons entre routeurs et les LAN qui doivent être annoncés. Une erreur de masque ou une adresse incohérente peut empêcher la formation du voisinage ou annoncer un préfixe inattendu.

Utilise dans les laboratoires des plages dédiées à la documentation : `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` ainsi que les petits sous-réseaux `10.0.12.0/30` et `10.0.23.0/30`. Ces exemples ne sont pas un plan d’adressage à copier sur Internet ou dans un réseau de production.


## 2. Les notions qui structurent OSPF

### 2.1 Routeur OSPF et Router ID

Le **Router ID** est un identifiant de 32 bits, souvent représenté sous une forme ressemblant à une adresse IPv4. Ce n’est pas nécessairement une adresse IP attribuée à une interface. Il sert à distinguer les routeurs dans le domaine OSPF et participe à certaines élections et opérations du protocole.

Sur Cisco IOS/IOS XE, il est préférable de définir explicitement un Router ID stable, unique dans le domaine OSPF, plutôt que de dépendre d’une sélection automatique qui pourrait changer après la modification des interfaces. Si deux routeurs utilisent le même Router ID, l’état OSPF peut devenir incohérent. Dans un réseau existant, modifier le Router ID peut nécessiter de réinitialiser le processus ou les adjacences selon la plateforme : fais-le dans un laboratoire avant d’envisager une intervention réelle.

Exemple de configuration dans un routeur de laboratoire :

```cisco
router ospf 10
 router-id 1.1.1.1
```

Dans cet exemple, `10` est le **numéro de processus local** utilisé par la configuration Cisco. Ce numéro n’est pas le Router ID et n’a pas à être identique chez les voisins. Le Router ID est ici `1.1.1.1` et doit être unique dans le domaine concerné.

### 2.2 Process ID et Area ID : deux notions différentes

| Notion | Fonction | Doit-elle correspondre chez les voisins ? |
|---|---|---|
| Process ID Cisco | Identifie le processus OSPF dans la configuration locale | Pas nécessairement : c’est un paramètre local à l’équipement |
| Router ID | Identifie le routeur OSPF | Doit être unique dans le domaine OSPF |
| Area ID | Identifie l’aire associée à une interface OSPF | Les voisins qui établissent une adjacence sur le lien doivent avoir une configuration d’aire compatible, normalement le même Area ID |
| Adresse IP / masque | Définit le réseau d’interface IPv4 | Doit être compatible avec le lien réel ; une erreur peut bloquer le voisinage |
| Timers Hello/Dead | Règlent les messages Hello et la détection de voisin injoignable | Les valeurs pertinentes doivent correspondre sur le segment pour que le voisinage fonctionne normalement |

### 2.3 L’aire OSPF

Une aire est une partie logique d’un domaine OSPF. Les routeurs d’une même aire partagent une vue cohérente de la topologie de cette aire. L’usage des aires peut limiter l’étendue de certaines annonces et la quantité de calcul nécessaire dans des réseaux plus grands. Ce cours reste dans **l’aire 0**, appelée backbone, afin de construire une base solide sans introduire prématurément le routage inter-aires.

Pour un laboratoire mono-aire, toutes les interfaces participant au même réseau OSPF sont placées dans l’aire `0`. On peut représenter l’identifiant sous la forme `0`, `0.0.0.0` ou une autre représentation admise par le système ; la valeur numérique correspond à l’identifiant d’aire. Ne confonds pas l’aire 0 avec le numéro de processus local.

### 2.4 Les paquets OSPFv2

OSPFv2 utilise cinq types de paquets fondamentaux :

| Type | Nom | Rôle pédagogique |
|---:|---|---|
| 1 | Hello | Découvrir les voisins, maintenir le voisinage et participer à certaines élections |
| 2 | Database Description (DBD) | Échanger des résumés d’informations présentes dans la base de liens |
| 3 | Link-State Request (LSR) | Demander des annonces manquantes ou plus précises |
| 4 | Link-State Update (LSU) | Transporter une ou plusieurs LSA |
| 5 | Link-State Acknowledgment (LSAck) | Accuser réception de certaines annonces d’état de liens |

Une **LSA** (*Link-State Advertisement*) est une unité d’information décrivant une partie de la topologie ou d’autres informations OSPF selon le type. Une **LSU** (*Link-State Update*) est un type de paquet qui peut transporter plusieurs LSA. Ce ne sont pas des synonymes : l’un est une annonce, l’autre est un type de paquet OSPF qui transporte ces annonces.

### Schéma 2 — Échanges OSPF durant la formation du voisinage

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Les cinq types de paquets OSPFv2" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Les cinq types de paquets OSPFv2</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les types ont des rôles distincts durant la découverte, la synchronisation et le maintien.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="170" width="130" height="88" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="100.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">1 · Hello</text>
<text x="100.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">découverte</text>
<rect x="225" y="170" width="130" height="88" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="290.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">2 · DBD</text>
<text x="290.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">résumés LSDB</text>
<rect x="415" y="170" width="130" height="88" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="480.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">3 · LSR</text>
<text x="480.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">demande LSA</text>
<rect x="605" y="170" width="130" height="88" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="670.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">4 · LSU</text>
<text x="670.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">LSA transportées</text>
<rect x="795" y="170" width="130" height="88" rx="13" fill="#172333" stroke="#7dd3fc" stroke-width="2"/>
<text x="860.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">5 · LSAck</text>
<text x="860.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">accusé</text>
<line x1="165" y1="214" x2="225" y2="214" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 217 208 L 225 214 L 217 220" fill="none" stroke="#eef4fb" stroke-width="2"/>
<line x1="355" y1="214" x2="415" y2="214" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 407 208 L 415 214 L 407 220" fill="none" stroke="#eef4fb" stroke-width="2"/>
<line x1="545" y1="214" x2="605" y2="214" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 597 208 L 605 214 L 597 220" fill="none" stroke="#eef4fb" stroke-width="2"/>
<line x1="735" y1="214" x2="795" y2="214" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 787 208 L 795 214 L 787 220" fill="none" stroke="#eef4fb" stroke-width="2"/>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 165 214 L 225 214 L 355 214 L 415 214" dur="3.2s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 545 214 L 605 214 L 735 214 L 795 214" dur="3.2s" begin="1s" repeatCount="indefinite"/></circle>
<rect x="95" y="325" width="770" height="75" rx="13" fill="#111c2a" stroke="#fb7185" stroke-width="2"/>
<text x="480.0" y="352" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Attention au vocabulaire</text>
<text x="480.0" y="374" text-anchor="middle" fill="#adbdcf" font-size="12">Une LSU transporte une ou plusieurs LSA ; une LSA n’est pas un type de paquet OSPF autonome.</text>
<text x="480.0" y="483" text-anchor="middle" fill="#adbdcf" font-size="11">Schéma conceptuel : la chronologie exacte dépend du contexte de voisinage et des échanges en cours.</text>
</svg>
</div>


Le schéma représente les fonctions des paquets dans un échange général. En pratique, les messages peuvent se répéter, certains échanges sont conditionnels et une adjacence déjà établie ne rejoue pas constamment toute la séquence.


## 3. Les Hello et le voisinage

### 3.1 Découverte des voisins

Les paquets Hello permettent à un routeur de découvrir les routeurs OSPF présents sur le lien et de suivre leur disponibilité. Si aucun Hello valide ne parvient à un routeur dans le délai prévu, celui-ci peut considérer le voisin comme injoignable et recalculer les routes selon le changement de topologie. Les intervalles exacts dépendent du type de réseau et de la configuration ; certaines valeurs courantes en Ethernet sont souvent enseignées en laboratoire, mais ne doivent pas être traitées comme universelles.

Pour que les voisins puissent former une relation normale, plusieurs paramètres doivent être compatibles : aire, sous-réseau et type de lien adaptés, timers Hello/Dead, options, authentification lorsqu’elle est utilisée et autres contraintes selon l’implémentation. Une simple connectivité IP entre deux interfaces n’assure donc pas que le voisinage OSPF va se former.

### 3.2 Les états les plus importants

| État | Interprétation générale | Première action utile |
|---|---|---|
| Down | Aucun Hello valide n’est actuellement retenu comme provenant du voisin | Vérifier lien, adresse, activation OSPF et filtrage |
| Init | Un Hello a été reçu, mais l’échange bidirectionnel n’est pas encore confirmé | Vérifier si le routeur local apparaît dans la liste des voisins annoncés par l’autre |
| 2-Way | La communication Hello est bidirectionnelle | Sur Ethernet broadcast, un état 2-WAY entre deux routeurs DROTHER peut être normal |
| ExStart | Les voisins négocient certains paramètres de synchronisation de base de liens | Examiner MTU, Router ID, type de réseau et journaux si l’état persiste |
| Exchange | Les résumés de LSDB sont échangés | Comparer DBD, options et cohérence des bases |
| Loading | Des LSA supplémentaires sont demandées et chargées | Chercher des requêtes sans réponse, pertes ou incohérences |
| Full | Les bases pertinentes sont synchronisées pour l’adjacence | Vérifier les routes et le transfert effectif des paquets |

### Schéma 3 — Lecture des états de voisinage

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 520" role="img" aria-label="Formation d’une adjacence OSPF" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="520" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Formation d’une adjacence OSPF</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les états progressent après réception de paquets valides et synchronisation de la base de liens.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="95.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">DOWN</text>
<text x="95.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">aucun Hello valide</text>
<rect x="190" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="250.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">INIT</text>
<text x="250.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">Hello reçu</text>
<rect x="345" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="405.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">2-WAY</text>
<text x="405.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">bidirectionnel</text>
<rect x="500" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="560.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">EXSTART</text>
<text x="560.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">maître/esclave DBD</text>
<rect x="655" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="715.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">EXCHANGE</text>
<text x="715.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">résumés LSDB</text>
<rect x="810" y="160" width="120" height="86" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="870.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">FULL</text>
<text x="870.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="10">bases synchronisées</text>
<line x1="155" y1="203" x2="190" y2="203" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 182 197 L 190 203 L 182 209" fill="none" stroke="#adbdcf" stroke-width="2"/>
<line x1="310" y1="203" x2="345" y2="203" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 337 197 L 345 203 L 337 209" fill="none" stroke="#adbdcf" stroke-width="2"/>
<line x1="465" y1="203" x2="500" y2="203" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 492 197 L 500 203 L 492 209" fill="none" stroke="#adbdcf" stroke-width="2"/>
<line x1="620" y1="203" x2="655" y2="203" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 647 197 L 655 203 L 647 209" fill="none" stroke="#adbdcf" stroke-width="2"/>
<line x1="775" y1="203" x2="810" y2="203" stroke="#34475d" stroke-width="3" stroke-linecap="round"/>
<path d="M 802 197 L 810 203 L 802 209" fill="none" stroke="#adbdcf" stroke-width="2"/>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 155 203 L 190 203 L 310 203 L 345 203" dur="3s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 465 203 L 500 203 L 620 203 L 655 203 L 775 203 L 810 203" dur="4s" begin="1s" repeatCount="indefinite"/></circle>
<rect x="80" y="305" width="360" height="100" rx="13" fill="#111c2a" stroke="#fb7185" stroke-width="2"/>
<text x="260.0" y="332" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Si rien n’apparaît</text>
<text x="260.0" y="354" text-anchor="middle" fill="#adbdcf" font-size="12">Vérifier interface, adressage, multicast,</text>
<text x="260.0" y="370" text-anchor="middle" fill="#adbdcf" font-size="12">area, timers, authentification et ACL.</text>
<rect x="520" y="305" width="360" height="100" rx="13" fill="#111c2a" stroke="#fbbf24" stroke-width="2"/>
<text x="700.0" y="332" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Si EXSTART / EXCHANGE bloque</text>
<text x="700.0" y="354" text-anchor="middle" fill="#adbdcf" font-size="12">Comparer MTU, Router ID, base de liens et</text>
<text x="700.0" y="370" text-anchor="middle" fill="#adbdcf" font-size="12">journaux avant de toucher aux timers.</text>
<text x="480" y="455" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Sur Ethernet broadcast, 2-WAY entre deux routeurs DROTHER peut être normal.</text>
<text x="480.0" y="503" text-anchor="middle" fill="#adbdcf" font-size="11">États fréquents simplifiés ; transitions et affichage dépendent du type de réseau et de l’implémentation.</text>
</svg>
</div>


Le but du dépannage n’est pas de forcer un voisin à `FULL` par une série de changements au hasard. Il faut trouver le premier état qui ne progresse plus, identifier les paramètres concernés, formuler une hypothèse, collecter une preuve, puis effectuer une modification contrôlée.

### 3.3 Multicast OSPFv2

Sur les réseaux broadcast et certains liens point-à-point, OSPFv2 utilise des adresses multicast connues, notamment `224.0.0.5` (AllSPFRouters) et `224.0.0.6` (AllDRouters). Ces adresses sont utiles à reconnaître dans une capture, mais leur usage effectif dépend du type de réseau et de la fonction du paquet. Sur d’autres types de réseaux, les modes de découverte et de transport peuvent être différents.

Dans Wireshark, filtre de départ possible :

```text
ospf
```

On peut aussi filtrer sur le protocole IP ou les destinations multicast pertinentes. La syntaxe exacte d’un filtre dépend de l’outil et de sa version. Dans la capture, compare les paquets Hello, le Router ID source, l’aire, les timers et les indications d’authentification si présentes.


## 4. DR et BDR sur Ethernet

### 4.1 Pourquoi élire un DR ?

Sur un réseau broadcast où plusieurs routeurs sont présents, OSPF élit un **Designated Router (DR)** et un **Backup Designated Router (BDR)**. Cette organisation réduit la nécessité pour chaque routeur de former une adjacence complète avec tous les autres routeurs du segment. Les autres routeurs sont couramment appelés DROTHER.

Le DR et le BDR ne sont pas des routeurs « plus puissants » en général ; il s’agit de rôles OSPF sur le segment. L’élection s’appuie notamment sur la priorité d’interface, puis sur le Router ID pour départager les candidats. Une priorité d’interface de zéro exclut généralement un routeur de l’élection. Le comportement de préemption doit être compris : l’ajout ultérieur d’un routeur avec une priorité plus haute ne force pas toujours une nouvelle élection immédiate dans le sens que l’on imagine.

### Schéma 4 — DR/BDR et adjacences

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="OSPF sur un LAN Ethernet : DR et BDR" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">OSPF sur un LAN Ethernet : DR et BDR</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Sur un segment multi-accès, DR/BDR réduisent le nombre d’adjacences complètes nécessaires.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="65" y="155" width="165" height="75" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="147.5" y="182" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1 · DR</text>
<text x="147.5" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">Priorité plus élevée</text>
<rect x="397" y="125" width="165" height="75" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="479.5" y="152" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2 · BDR</text>
<text x="479.5" y="174" text-anchor="middle" fill="#adbdcf" font-size="12">Secours du DR</text>
<rect x="730" y="155" width="165" height="75" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="812.5" y="182" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3 · DROTHER</text>
<text x="812.5" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">Routeur ordinaire</text>
<rect x="397" y="300" width="165" height="75" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="479.5" y="327" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R4 · DROTHER</text>
<text x="479.5" y="349" text-anchor="middle" fill="#adbdcf" font-size="12">Routeur ordinaire</text>
<line x1="145" y1="270" x2="813" y2="270" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/>
<line x1="147" y1="230" x2="147" y2="270" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/>
<line x1="480" y1="200" x2="480" y2="270" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/>
<line x1="812" y1="230" x2="812" y2="270" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/>
<line x1="480" y1="270" x2="480" y2="300" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/>
<text x="480" y="254" text-anchor="middle" fill="#c4b5fd" font-size="13" font-weight="700">Segment Ethernet partagé</text>


<text x="480" y="425" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">FULL vers DR/BDR ; 2-WAY entre DROTHER peut être attendu.</text>
<text x="480" y="448" text-anchor="middle" fill="#adbdcf" font-size="12">Élection fondée sur la priorité puis le Router ID ; les élections ne préemptent pas toujours comme on l’imagine.</text>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 147 270 L 147 230" dur="2.8s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 812 270 L 812 230" dur="2.8s" begin="1s" repeatCount="indefinite"/></circle>
</svg>
</div>


Sur un segment Ethernet, deux DROTHER peuvent rester en état 2-WAY l’un avec l’autre, tandis qu’ils forment une adjacence FULL avec le DR et le BDR. Ne diagnostique donc pas automatiquement tout état 2-WAY comme une panne ; interprète-le selon le type d’interface et les rôles élus.

### 4.2 Priorité et Router ID

Les paramètres d’élection doivent être définis intentionnellement dans un réseau où le choix du DR/BDR importe. Une priorité élevée ne remplace pas une bonne conception des rôles, et un Router ID doit rester unique. Avant une modification, relève le DR et le BDR actuels, vérifie le coût et la priorité sur les interfaces, puis considère si le changement déclenchera un impact sur les adjacences.


## 5. LSDB, SPF et installation des routes

### 5.1 De l’information à la décision de routage

Les routeurs OSPF ne se contentent pas d’additionner les métriques annoncées par un voisin. Ils maintiennent une base d’état de liens représentant la topologie de l’aire, puis calculent le meilleur chemin vers les destinations connues. L’algorithme SPF détermine un arbre de cheminement à partir du routeur local. La table de routage contient ensuite les routes retenues, en concurrence éventuelle avec d’autres protocoles.

Sur Cisco IOS/IOS XE, OSPF apparaît classiquement avec le code de route `O` dans `show ip route` pour une route intra-aire. Les routes inter-aires et externes ont d’autres codes dans une configuration multi-aires ou avec redistribution ; ce niveau débutant se concentre sur les routes intra-aire.

### Schéma 5 — LSA, LSDB, calcul SPF et RIB

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Du LSA à la route installée" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Du LSA à la route installée</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">OSPF distingue l’information de topologie, le calcul SPF et l’installation dans la table de routage.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="170" width="175" height="100" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="122.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Voisins OSPF</text>
<text x="122.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12">DBD / LSU / LSAck</text>
<rect x="270" y="170" width="190" height="100" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="365.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">LSDB</text>
<text x="365.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="12">Base d’état de liens</text>
<rect x="520" y="170" width="175" height="100" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="607.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">SPF (Dijkstra)</text>
<text x="607.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">Arbre des plus courts chemins</text>
<rect x="755" y="170" width="170" height="100" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="840.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">RIB / FIB</text>
<text x="840.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">Route installée puis transfert</text>
<line x1="210" y1="220" x2="270" y2="220" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/>
<line x1="460" y1="220" x2="520" y2="220" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/>
<line x1="695" y1="220" x2="755" y2="220" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/>
<path d="M 260 214 L 270 220 L 260 226" fill="none" stroke="#eef4fb" stroke-width="2"/>
<path d="M 510 214 L 520 220 L 510 226" fill="none" stroke="#eef4fb" stroke-width="2"/>
<path d="M 745 214 L 755 220 L 745 226" fill="none" stroke="#eef4fb" stroke-width="2"/>
<circle r="5" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 210 220 L 270 220" dur="2s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 460 220 L 520 220" dur="2s" begin="0.6s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 695 220 L 755 220" dur="2s" begin="1.2s" repeatCount="indefinite"/></circle>
<rect x="95" y="330" width="770" height="70" rx="13" fill="#111c2a" stroke="#fb7185" stroke-width="2"/>
<text x="480.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Une LSA reçue ≠ route garantie</text>
<text x="480.0" y="379" text-anchor="middle" fill="#adbdcf" font-size="12">La route dépend de la base cohérente, du calcul SPF, de la sélection de route et de sa résolution.</text>
<text x="480.0" y="473" text-anchor="middle" fill="#adbdcf" font-size="11">La base d’état de liens doit être cohérente au sein de l’aire ; les routes installées peuvent différer selon les autres sources.</text>
</svg>
</div>


Ce schéma distingue les étapes. Une LSA reçue n’est pas une route installée. Si la base est synchronisée mais qu’un préfixe n’apparaît pas, vérifie que le réseau est bien décrit par une LSA appropriée, que le calcul l’inclut et que la sélection de route permet son installation.

### 5.2 Le coût OSPF

OSPF utilise une métrique de coût pour sélectionner des chemins. Sur les plateformes Cisco, le coût est généralement lié à la bande passante de référence et à la bande passante de l’interface, mais les valeurs réelles dépendent de la configuration et de l’implémentation. Une mauvaise bande passante déclarée ou une référence non adaptée peut produire des chemins inattendus, surtout sur les réseaux modernes où plusieurs liens possèdent des débits très élevés.

Pour deux chemins vers une même destination, OSPF compare les coûts cumulés. Un coût plus faible est préféré. Si plusieurs chemins ont un coût égal, l’implémentation peut installer plusieurs chemins à coût égal (ECMP) selon la configuration et les limites de la plateforme. Il ne faut pas confondre ECMP avec une agrégation LACP : ce sont des mécanismes différents et situés à des niveaux différents.

### Schéma 6 — Calcul d’un chemin de coût minimal

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Choix d’un chemin : comparer les coûts OSPF" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Choix d’un chemin : comparer les coûts OSPF</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Illustration : le chemin à coût total inférieur est préféré pour une même destination.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="205" width="140" height="80" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="120.0" y="232" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1</text>
<text x="120.0" y="254" text-anchor="middle" fill="#adbdcf" font-size="12">Source</text>
<rect x="330" y="115" width="150" height="80" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="405.0" y="142" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2</text>
<text x="405.0" y="164" text-anchor="middle" fill="#adbdcf" font-size="12">Relais</text>
<rect x="330" y="305" width="150" height="80" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="405.0" y="332" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3</text>
<text x="405.0" y="354" text-anchor="middle" fill="#adbdcf" font-size="12">Relais</text>
<rect x="635" y="205" width="140" height="80" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="705.0" y="232" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R4</text>
<text x="705.0" y="254" text-anchor="middle" fill="#adbdcf" font-size="12">Destination</text>
<path d="M 190 220 L 250 220 L 250 155 L 330 155" fill="none" stroke="#4ade80" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 155 L 555 155 L 555 220 L 635 220" fill="none" stroke="#4ade80" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 190 260 L 250 260 L 250 345 L 330 345" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 345 L 555 345 L 555 260 L 635 260" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="260" y="145" fill="#4ade80" font-size="12" text-anchor="middle" font-weight="700">10</text>
<text x="590" y="190" fill="#4ade80" font-size="12" text-anchor="middle" font-weight="700">10</text>
<text x="260" y="330" fill="#fbbf24" font-size="12" text-anchor="middle" font-weight="700">25</text>
<text x="590" y="295" fill="#fbbf24" font-size="12" text-anchor="middle" font-weight="700">25</text>
<text x="555" y="137" fill="#4ade80" font-size="13" text-anchor="middle" font-weight="700">coût total illustratif : 20</text>
<text x="555" y="374" fill="#fbbf24" font-size="13" text-anchor="middle" font-weight="700">coût total illustratif : 50</text>
<circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 190 220 L 250 220 L 250 155 L 330 155 L 480 155 L 555 155 L 555 220 L 635 220" dur="3.8s" begin="0s" repeatCount="indefinite"/></circle>
<text x="480" y="445" text-anchor="middle" fill="#eef4fb" font-size="13">Les valeurs sont pédagogiques : le coût dépend du calcul et de la configuration des interfaces.</text>
</svg>
</div>


Les nombres du schéma sont pédagogiques. Ne déduis pas le coût exact de production à partir du seul débit nominal : inspecte les paramètres OSPF effectifs et les sorties des commandes.

### 5.3 Commandes de vérification

```cisco
show ip route ospf
show ip route
show ip ospf database
show ip ospf interface brief
show ip ospf neighbor
show ip protocols
```

La disponibilité et la syntaxe des variantes peuvent différer. Si la commande `show ip ospf interface brief` n’est pas reconnue, utilise l’aide locale (`show ip ospf ?`) et les commandes de la version IOS/IOS XE réellement utilisée.


## 6. Laboratoire guidé : trois routeurs, aire 0

### 6.1 Topologie et plan d’adressage

Le laboratoire utilise trois routeurs reliés en chaîne. Chaque routeur possède un LAN distinct et participe à l’aire OSPF `0.0.0.0`. Les adresses publiques de test présentées ci-dessous sont des plages de documentation, pas des adresses à déployer dans un réseau public réel.

### Schéma 7 — Maquette mono-aire

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Laboratoire de base : trois routeurs, aire 0" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Laboratoire de base : trois routeurs, aire 0</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Chaque routeur annonce ses réseaux connectés dans la même aire. Les préfixes sont réservés à la documentation.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="70" y="170" width="185" height="95" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="162.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1</text>
<text x="162.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12">RID 1.1.1.1</text>
<text x="162.5" y="235" text-anchor="middle" fill="#adbdcf" font-size="12">LAN 192.0.2.0/24</text>
<rect x="388" y="170" width="185" height="95" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="480.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2</text>
<text x="480.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12">RID 2.2.2.2</text>
<text x="480.5" y="235" text-anchor="middle" fill="#adbdcf" font-size="12">LAN 198.51.100.0/24</text>
<rect x="706" y="170" width="185" height="95" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="798.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3</text>
<text x="798.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12">RID 3.3.3.3</text>
<text x="798.5" y="235" text-anchor="middle" fill="#adbdcf" font-size="12">LAN 203.0.113.0/24</text>
<line x1="255" y1="215" x2="388" y2="215" stroke="#45c7f5" stroke-width="5" stroke-linecap="round"/>
<line x1="573" y1="215" x2="706" y2="215" stroke="#45c7f5" stroke-width="5" stroke-linecap="round"/>
<text x="322" y="194" fill="#adbdcf" font-size="12" text-anchor="middle">10.0.12.0/30</text>
<text x="640" y="194" fill="#adbdcf" font-size="12" text-anchor="middle">10.0.23.0/30</text>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 255 215 L 388 215" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 573 215 L 706 215" dur="2.5s" begin="0.8s" repeatCount="indefinite"/></circle>
<rect x="95" y="330" width="770" height="80" rx="13" fill="#111c2a" stroke="#7dd3fc" stroke-width="2"/>
<text x="480.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Critère de succès</text>
<text x="480.0" y="379" text-anchor="middle" fill="#adbdcf" font-size="12">Voisinages attendus, réseaux distants dans la table de routage,</text>
<text x="480.0" y="395" text-anchor="middle" fill="#adbdcf" font-size="12">pings ciblés et sorties de commandes archivées.</text>
</svg>
</div>


| Équipement | Interface / segment | Adresse d’exemple | Router ID |
|---|---|---|---|
| R1 | LAN | `192.0.2.1/24` | `1.1.1.1` |
| R1–R2 | Transit | `10.0.12.1/30` ↔ `10.0.12.2/30` | — |
| R2 | LAN | `198.51.100.1/24` | `2.2.2.2` |
| R2–R3 | Transit | `10.0.23.1/30` ↔ `10.0.23.2/30` | — |
| R3 | LAN | `203.0.113.1/24` | `3.3.3.3` |

Les interfaces de transit sont directement connectées entre routeurs. La topologie de laboratoire suppose que les adresses sont configurées et que les interfaces sont actives. Ajuste les noms d’interface à ton matériel ou au modèle Packet Tracer.

### 6.2 Activer OSPF sur R1

Exemple de configuration avec les commandes `network` et un masque générique (*wildcard mask*) :

```cisco
configure terminal
router ospf 10
 router-id 1.1.1.1
 network 192.0.2.0 0.0.0.255 area 0
 network 10.0.12.0 0.0.0.3 area 0
 passive-interface GigabitEthernet0/0
end
```

Dans cet exemple, `GigabitEthernet0/0` est supposée être l’interface du LAN client. `passive-interface` garde le réseau connecté annoncé par OSPF, mais évite d’essayer d’établir des voisinages OSPF sur l’interface passive, ce qui convient généralement à un LAN d’utilisateurs sans routeur OSPF. Adapte l’interface à la maquette ; n’applique pas passivement toutes les interfaces sans réfléchir.

Le masque générique inverse les bits du masque de sous-réseau : `0.0.0.255` correspond au masque `255.255.255.0`, et `0.0.0.3` correspond à `255.255.255.252`. La commande `network` sert à sélectionner les interfaces locales qui doivent participer au processus/à l’aire selon les règles Cisco ; elle ne crée pas elle-même un sous-réseau IP.

### 6.3 Configuration de R2 et R3

Sur R2 :

```cisco
configure terminal
router ospf 10
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
 network 198.51.100.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end
```

Sur R3 :

```cisco
configure terminal
router ospf 10
 router-id 3.3.3.3
 network 10.0.23.0 0.0.0.3 area 0
 network 203.0.113.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/0
end
```

Ici encore, `GigabitEthernet0/0` est supposée être l’interface LAN. Sur une autre maquette, vérifie les interfaces avec `show ip interface brief` avant de coller la configuration. L’interface de transit entre routeurs ne doit pas être passive si l’objectif est d’établir un voisinage OSPF par ce lien.

### 6.4 Vérifier les voisinages

Sur chaque routeur :

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip protocols
```

Dans la topologie en chaîne, R1 doit normalement former un voisinage avec R2 sur son transit ; R3 forme un voisinage avec R2. R1 n’a pas de lien direct vers R3 et ne doit donc pas apparaître comme voisin direct de R3 dans ce schéma. Il peut toutefois apprendre le LAN de R3 via OSPF si l’ensemble de la configuration est correct.

### 6.5 Vérifier les routes et la connectivité

```cisco
show ip route ospf
show ip route 203.0.113.0
ping 203.0.113.1
traceroute 203.0.113.1
```

Le routeur R1 devrait apprendre la route du LAN de R3 avec le code OSPF approprié à une route intra-aire. Un ping doit être exécuté depuis le routeur ou un hôte correctement adressé. Un résultat de ping seul ne prouve pas que la totalité du plan de routage, du DNS et des applications fonctionne ; observe aussi la route choisie et le prochain saut.

### Critères de réussite

- [ ] Les interfaces de transit sont `up/up` et les sous-réseaux sont corrects.
- [ ] Chaque routeur a un Router ID unique.
- [ ] Les voisinages attendus apparaissent sans oscillation.
- [ ] Les réseaux LAN utiles sont annoncés et visibles dans les tables distantes.
- [ ] Le trafic de bout en bout passe par le chemin attendu.
- [ ] Les sorties de commandes et l’état final sont enregistrés.


## 7. Méthode de dépannage

### 7.1 Voisin absent

Si `show ip ospf neighbor` n’affiche aucun voisin, cela signifie généralement que le routeur ne reçoit pas de Hello valide provenant d’un voisin attendu. Vérifie dans l’ordre : état de l’interface, adresse IP et masque, activation d’OSPF sur l’interface, sous-réseau partagé, filtrage multicast ou ACL, aire, timers et authentification si configurée.

Commandes de départ :

```cisco
show ip interface brief
show ip ospf interface
show ip protocols
show running-config | section router ospf
show logging
```

Le format des filtres `show running-config` et la disponibilité de certaines commandes dépendent de l’image. Si un filtre n’est pas supporté, affiche la configuration complète ou la section équivalente disponible.

### 7.2 État INIT

Un voisin qui reste en `INIT` a envoyé un Hello qui a été reçu, mais la relation bidirectionnelle n’a pas été confirmée. Vérifie si le Hello contient le Router ID local dans la liste de voisins. Cherche une différence de type de réseau, des problèmes multicast, une liaison unidirectionnelle ou une configuration qui fait que les routeurs ne reçoivent pas les messages attendus dans les deux directions.

### 7.3 État 2-WAY

Sur un segment Ethernet broadcast, `2-WAY` peut être normal entre deux routeurs DROTHER. Vérifie les rôles DR/BDR et le type de réseau avant de décider que l’adjacence est bloquée. Sur un lien point-à-point, le comportement attendu n’est pas le même qu’entre deux DROTHER sur un LAN broadcast.

### 7.4 États EXSTART ou EXCHANGE persistants

Quand le voisinage n’avance pas au-delà d’EXSTART ou EXCHANGE, vérifie la MTU, le Router ID, les paramètres DBD, les options, les logs et la cohérence de l’aire. Une différence de MTU peut notamment empêcher l’échange normal des descriptions de base de liens sur certaines implémentations. Ne baisse pas aveuglément la MTU : d’abord, trouve la différence réelle et valide pourquoi elle existe.

### 7.5 Voisin FULL mais route manquante

Un voisin FULL signifie que la base pertinente a été synchronisée dans le cadre de cette adjacence ; cela ne garantit pas qu’un réseau précis soit annoncé. Vérifie si l’interface correspondant au LAN est sélectionnée dans le processus OSPF, si elle n’est pas mal configurée, si le préfixe est réellement connecté, si une interface passive est utilisée intentionnellement, et si la LSA attendue figure dans la base.

### Schéma 8 — Arbre de dépannage OSPF

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.5rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 550" role="img" aria-label="Arbre de dépannage OSPF" style="display:block;width:100%;max-width:960px;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="960" height="550" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Arbre de dépannage OSPF</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Choisir le prochain test à partir de l’état observé, pas à partir d’une supposition.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="335" y="105" width="290" height="65" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="480.0" y="132" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Voisin OSPF visible ?</text>
<text x="480.0" y="154" text-anchor="middle" fill="#adbdcf" font-size="11">show ip ospf neighbor</text>
<rect x="30" y="245" width="255" height="80" rx="13" fill="#172333" stroke="#fb7185" stroke-width="2"/>
<text x="157.5" y="272" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">NON</text>
<text x="157.5" y="294" text-anchor="middle" fill="#adbdcf" font-size="11">interface / Hello / area / timers / ACL</text>
<rect x="350" y="245" width="255" height="80" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="477.5" y="272" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">2-WAY</text>
<text x="477.5" y="294" text-anchor="middle" fill="#adbdcf" font-size="11">broadcast : vérifier le rôle DR/BDR</text>
<rect x="670" y="245" width="255" height="80" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="797.5" y="272" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">EXSTART / EXCHANGE</text>
<text x="797.5" y="294" text-anchor="middle" fill="#adbdcf" font-size="11">MTU / DBD / Router ID / logs</text>
<path d="M 380 170 L 160 245" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 170 L 480 245" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 580 170 L 795 245" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="175" y="390" width="260" height="75" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="305.0" y="417" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">FULL mais route absente</text>
<text x="305.0" y="439" text-anchor="middle" fill="#adbdcf" font-size="11">réseau annoncé ? passive ? filtre ?</text>
<rect x="525" y="390" width="260" height="75" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="655.0" y="417" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">FULL et route présente</text>
<text x="655.0" y="439" text-anchor="middle" fill="#adbdcf" font-size="11">next-hop / ACL / route retour / service</text>
<path d="M 160 325 L 160 360 L 305 360 L 305 390" fill="none" stroke="#34475d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 795 325 L 795 360 L 655 360 L 655 390" fill="none" stroke="#34475d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="480" y="505" text-anchor="middle" fill="#adbdcf" font-size="12">Toujours capturer l’état initial avant de modifier timers, MTU ou configuration OSPF.</text>
</svg>
</div>


Cette démarche réduit les changements inutiles : on part de l’état observé, on choisit la vérification suivante, puis on confirme le résultat avant toute correction.


## 8. Sécurité et bonnes pratiques de débutant

OSPF échange des informations de routage. Un voisinage établi avec un équipement non autorisé peut introduire des informations de topologie qui influencent le trafic. La sécurité ne consiste pas à cacher les routes : elle consiste à limiter qui peut participer au protocole et à contrôler les annonces et les changements de configuration.

Bonnes pratiques générales :

- ne fais pas fonctionner OSPF sur des interfaces où aucun voisin OSPF n’est attendu ; utilise des interfaces passives lorsque cela convient au besoin de publication du réseau ;
- définis des Router ID uniques et documentés ;
- vérifie les réseaux annoncés et les interfaces sélectionnées par les commandes `network` ;
- emploie l’authentification et les mécanismes recommandés lorsqu’ils sont pris en charge et nécessaires à l’architecture ;
- garde les secrets hors des captures, journaux et documents non protégés ;
- surveille les changements de voisinage et les changements de route ;
- capture l’état initial avant un changement de priorité, de coût, de réseau ou d’authentification ;
- ne tente pas de résoudre un problème de voisinage en désactivant globalement les contrôles de sécurité.

La méthode d’authentification disponible varie selon la version et la plateforme. RFC 5709 décrit une extension d’authentification cryptographique OSPFv2 avec HMAC-SHA, mais l’implémentation réelle doit être vérifiée sur l’équipement utilisé. L’authentification ne remplace ni les filtres de contrôle, ni la protection du plan de management, ni la maîtrise des accès administratifs.


## 9. Laboratoires complémentaires

### Laboratoire A — Modifier le coût d’un lien

1. Établis la topologie et vérifie que tous les voisins sont stables.
2. Releve les coûts des interfaces et la route d’un préfixe distant.
3. Modifie le coût OSPF sur une interface de transit dans la maquette.
4. Vérifie la mise à jour de la route et le prochain saut.
5. Restaure la valeur initiale et prouve que le chemin revient à l’état attendu.

**Livrable :** sorties de `show ip ospf interface`, `show ip route` et explication des décisions de sélection.

### Laboratoire B — Casser volontairement un paramètre de voisinage

Dans une maquette isolée, change temporairement une valeur de timer ou le paramètre d’aire d’un côté seulement. Observe l’état du voisin, puis restaure le paramètre et consigne la récupération. N’effectue jamais cette expérience sur un réseau de production.

**Livrable :** hypothèse initiale, symptôme, sortie de commande, correction et état final.

### Laboratoire C — Examiner une capture OSPF

1. Lance une capture sur un lien de transit de la maquette.
2. Filtre le protocole OSPF.
3. Identifie un paquet Hello, les Router ID et l’aire annoncée.
4. Si une synchronisation de base a lieu, identifie DBD, LSR, LSU et LSAck selon les paquets présents.
5. Explique quels champs ou événements permettent d’appuyer l’hypothèse de dépannage.

### Laboratoire D — Diagnostic de bout en bout

Fais vérifier par une machine source le service situé derrière le dernier routeur. Si le voisinage OSPF est FULL mais le service échoue, collecte la route, la route de retour, le prochain saut, l’état des interfaces et le résultat de tests ciblés. Distingue une route absente, un prochain saut non joignable, une ACL, une panne applicative et un test ICMP filtré.


## 10. Évaluation avec corrigés

### Questions

1. OSPF est-il un IGP ou un EGP ?
2. Quelle différence existe entre le Process ID Cisco et le Router ID ?
3. À quoi sert l’aire OSPF ?
4. Pourquoi deux routeurs peuvent-ils se pinguer sans former un voisinage OSPF ?
5. Que transporte une LSU et qu’est-ce qu’une LSA ?
6. Quelle différence existe entre LSDB, SPF et table de routage ?
7. Dans quel état le voisinage est-il considéré comme pleinement synchronisé ?
8. Pourquoi l’état 2-WAY n’est-il pas toujours une panne sur Ethernet ?
9. Que vérifies-tu lorsqu’un voisin reste en EXSTART ?
10. Un voisin FULL garantit-il que le LAN distant est annoncé ?
11. À quoi sert le DR sur un réseau broadcast multi-accès ?
12. Pourquoi faut-il observer le coût réellement utilisé par OSPF au lieu de déduire le chemin depuis le débit nominal ?
13. Que signifie une interface passive dans OSPF sur une configuration Cisco typique ?
14. Pourquoi faut-il définir des Router ID uniques ?
15. Cite au moins quatre contrôles utiles lorsqu’aucun voisin n’apparaît.

### Corrigés

**1.** OSPF est un protocole de routage intérieur, un IGP, couramment utilisé au sein d’un domaine administratif.

**2.** Le Process ID est un identifiant local à la configuration Cisco du processus. Le Router ID est l’identité OSPF du routeur et doit être unique dans le domaine.

**3.** L’aire segmente la topologie OSPF. Dans ce cours, une seule aire, `0`, est utilisée pour apprendre les bases sans ajouter la complexité inter-aires.

**4.** Les voisins doivent aussi avoir des paramètres OSPF compatibles : aire, timers, sous-réseau, type de réseau, authentification et options pertinentes. La connectivité IP n’est qu’une partie des conditions.

**5.** Une LSU est un type de paquet OSPF qui transporte une ou plusieurs LSA. Une LSA est une annonce décrivant des informations de topologie ou de routage selon son type.

**6.** La LSDB contient la représentation de topologie connue dans l’aire. SPF calcule les chemins à partir de cette base. La table de routage contient les routes retenues par le système après sélection et résolution.

**7.** `FULL` indique une adjacence entièrement établie et une base de liens synchronisée selon les règles du voisinage.

**8.** Sur un segment broadcast, des routeurs DROTHER peuvent rester en 2-WAY entre eux tout en étant FULL avec le DR et le BDR. Il faut interpréter l’état selon le rôle et le type de réseau.

**9.** Vérifie la MTU, les Router ID, les paramètres DBD, les options, le type de réseau et les journaux, avant d’effectuer une correction ciblée.

**10.** Non. Le préfixe doit avoir été annoncé et figurer dans l’information appropriée. Vérifie la sélection de l’interface, la configuration `network`, les interfaces passives, la LSDB et la table de routage.

**11.** Le DR coordonne une partie de la distribution des informations sur le segment multi-accès et réduit le nombre d’adjacences complètes nécessaires.

**12.** Le coût dépend de la configuration et du calcul de bande passante de référence. Une déclaration incohérente peut produire une sélection inattendue, quel que soit le débit nominal du lien.

**13.** L’interface n’établit pas de voisinage OSPF sur ce réseau, mais le réseau connecté peut toujours être annoncé dans OSPF selon la configuration du processus.

**14.** Le Router ID sert à identifier chaque routeur dans le protocole. Un doublon peut perturber la stabilité et l’interprétation des informations OSPF.

**15.** État de l’interface, adressage/mask, OSPF activé sur l’interface, connectivité du lien, aire, timers, type de réseau, authentification, ACL/multicast et logs.


## 11. Fiche de révision

- OSPFv2 est un IGP à état de liens utilisé pour IPv4.
- Le Router ID identifie un routeur OSPF ; le Process ID Cisco est un identifiant local.
- Les routeurs d’une même aire synchronisent la base d’état de liens pertinente.
- Les Hello servent à découvrir les voisins et maintenir le voisinage.
- DBD, LSR, LSU et LSAck participent à la synchronisation des informations de liens.
- LSA et LSU ne sont pas synonymes.
- SPF calcule un arbre de chemins depuis la LSDB ; la table de routage contient ensuite les routes retenues.
- Sur Ethernet broadcast, le DR/BDR réduisent les adjacences complètes nécessaires.
- Le coût OSPF dépend des paramètres effectifs de l’interface et du protocole.
- `FULL` est un état de voisinage, pas une garantie de connectivité applicative totale.
- Un dépannage efficace progresse de l’interface au voisinage, puis à la LSDB, aux routes et au test de bout en bout.
- Ne change qu’un paramètre à la fois et conserve une preuve avant/après.

## 12. Références techniques

- **IETF — RFC 2328, OSPF Version 2** : https://www.rfc-editor.org/rfc/rfc2328.html
- **Cisco — OSPF Configuration Guide, IOS XE** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/ospf/ospf-configuration-guide/ospf.html
- **Cisco — Troubleshoot OSPF Neighbor Problems** : https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/13699-29.html
- **RFC 5709 — OSPFv2 HMAC-SHA Cryptographic Authentication** : https://www.rfc-editor.org/rfc/rfc5709.html

Ces références décrivent les principes du protocole ou les fonctions d’une plateforme précise. Les commandes doivent être validées contre le modèle, l’image logicielle et la topologie utilisés en laboratoire ou en production.


## Préparation au niveau Intermédiaire

Le prochain niveau réutilisera le Router ID, les paquets OSPF, les états de voisinage, la LSDB, SPF, les coûts et l’aire unique. Il approfondira la conception multi-aires, les types de LSA, les rôles ABR/ASBR, l’agrégation, les zones stub/NSSA et les stratégies de dépannage plus avancées.
