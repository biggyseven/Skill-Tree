# BGP — Niveau Intermédiaire

**Durée indicative :** 6 à 9 heures selon les laboratoires et l’environnement de simulation.  
**Prérequis :** avoir suivi `bgp-debutant.md` et savoir former une session eBGP simple, interpréter AS_PATH, examiner les attributs, distinguer une route reçue d’une route installée et appliquer une politique d’import/export élémentaire.  
**Environnement :** Cisco IOS/IOS XE, FRRouting ou une maquette équivalente ; Wireshark est utile pour observer les messages BGP. Les syntaxes varient selon les plateformes.

Ce cours est la suite de `bgp-debutant.md`. Il ne reprend pas pas à pas les bases eBGP, le port TCP 179 et les premières configurations. L’objectif est maintenant de concevoir des politiques qui restent lisibles, d’étendre iBGP au moyen de route reflectors, de manipuler les communautés, de résumer des préfixes correctement, d’agir sur la préférence de chemin et de diagnostiquer les écarts entre les routes reçues, acceptées, sélectionnées, installées et transmises.

> **Cadre de laboratoire :** les ASN privés `65010`, `65020`, `65030` et les préfixes `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` sont des exemples de documentation/laboratoire. N’utilise jamais une configuration d’exemple sur une session Internet réelle sans revue, politique d’import/export explicite, filtrage des préfixes, surveillance et plan de retour arrière.

## Objectifs d’apprentissage

À la fin du cours, tu devrais pouvoir :

- expliquer pourquoi le full mesh iBGP ne s’adapte pas bien à un grand nombre de routeurs ;
- configurer et diagnostiquer un route reflector dans un laboratoire ;
- suivre la propagation d’une route et distinguer les attributs de route reflectors de ceux de politique ;
- utiliser les communautés BGP comme marques explicites et documentées ;
- agréger des préfixes uniquement quand le résumé correspond au plan d’adressage ;
- comparer Local Preference, MED et AS_PATH Prepending sans supposer qu’ils garantissent tous le même résultat ;
- construire des politiques d’import/export testables et ciblées ;
- introduire les états de validation d’origine RPKI sans les confondre avec une validation complète du chemin AS_PATH ;
- diagnostiquer une route qui n’apparaît pas dans la RIB ou qui n’est pas transférée ;
- établir des contrôles opérationnels avant et après un changement BGP.

## Comment utiliser ce document et ses schémas

Les dix SVG sont intégrés directement dans ce fichier Markdown : aucun dossier d’images externe n’est nécessaire. Les lignes représentent les relations ou les chemins expliqués dans chaque légende. Les points animés ne représentent pas un minutage exact du protocole ; ils illustrent une direction d’annonce ou un chemin de trafic précis. Si ton lecteur neutralise les animations SVG, les libellés statiques et la légende restent utiles.

Lis les schémas 1 à 10 en parallèle des sections qui les suivent. Réalise les laboratoires dans l’ordre : route reflector, communautés, politiques, agrégation, préférence de chemin, validation de préfixes et incident multi-cause. Pour chaque test, conserve la configuration initiale, les sorties de commandes et un test de connectivité ciblé.


## 1. Du protocole de base à la politique opérateur

### 1.1 Une route passe plusieurs filtres

En débutant, on observe souvent si la session est `Established` et si une route figure dans la sortie de `show bgp ipv4 unicast`. En exploitation, ces deux observations ne suffisent pas. Il faut connaître le cycle de vie complet : annonce reçue, application de la politique d’import, éligibilité, comparaison des chemins candidats, sélection du meilleur chemin, installation éventuelle dans la RIB, programmation du forwarding et succès réel du trafic.

Une route peut manquer à chaque étape pour une cause différente : le voisin ne l’annonce pas, l’import la rejette, les attributs la rendent inéligible, le NEXT_HOP n’est pas résolu, une autre source de routage gagne la RIB, ou un problème de forwarding/ACL/retour fait échouer le trafic même lorsque la route est installée.

### Schéma 1 — Cycle de vie d’une route BGP

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Cycle de vie d’une route BGP" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Cycle de vie d’une route BGP</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Une route traverse plusieurs étapes avant de devenir utilisable dans le plan de données.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="175" width="150" height="100" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="110.0" y="202" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">eBGP voisin</text><text x="110.0" y="224" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">UPDATE + préfixe</text><path d="M 185 225 L 220 225" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 185 225 L 220 225" dur="2s" begin="0s" repeatCount="indefinite"/></circle><rect x="220" y="175" width="155" height="100" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="297.5" y="202" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique IN</text><text x="297.5" y="224" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">prefix-list / route-map</text><path d="M 375 225 L 410 225" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 375 225 L 410 225" dur="2s" begin="0.4s" repeatCount="indefinite"/></circle><rect x="410" y="175" width="155" height="100" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="487.5" y="202" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Adj-RIB-In</text><text x="487.5" y="224" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">routes reçues</text><path d="M 565 225 L 600 225" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 565 225 L 600 225" dur="2s" begin="0.8s" repeatCount="indefinite"/></circle><rect x="600" y="175" width="155" height="100" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="677.5" y="202" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Best path</text><text x="677.5" y="224" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">comparaison BGP</text><path d="M 755 225 L 790 225" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 755 225 L 790 225" dur="2s" begin="1.2s" repeatCount="indefinite"/></circle><rect x="790" y="175" width="175" height="100" rx="13" fill="#151f2d" stroke="#60a5fa" stroke-width="2"/><text x="877.5" y="202" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">RIB / FIB</text><text x="877.5" y="224" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">installation + transfert</text><rect x="65" y="330" width="870" height="95" rx="12" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="90" y="356" text-anchor="start" fill="#fbbf24" font-size="14" font-weight="700" font-family="Inter,Arial,sans-serif">À distinguer :</text><text x="90" y="382" text-anchor="start" fill="#eef4fb" font-size="15" font-weight="700" font-family="Inter,Arial,sans-serif">reçue ≠ acceptée ≠ meilleure ≠ installée ≠ trafic réellement transmis</text><text x="90" y="405" text-anchor="start" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Chaque étape possède sa propre vérification et ses propres causes de rejet.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Les noms Adj-RIB-In/Out décrivent le modèle BGP ; la visibilité exacte dépend de l’implémentation.</text>
</svg>
</div>

Ce schéma est le modèle de diagnostic central du cours. La route peut être reçue sans être acceptée, acceptée sans gagner le best path, meilleure sans être installée dans la RIB, ou installée sans que le trafic applicatif réussisse.

### 1.2 Tableaux de contrôle utiles

| Étape | Question à poser | Preuve à collecter |
|---|---|---|
| Session | Le voisin TCP/BGP est-il établi ? | État du voisin, logs, TCP/179 |
| Réception | Le préfixe est-il annoncé ? | Routes reçues ou capture UPDATE |
| Import | La politique l’accepte-t-elle ? | Prefix-list, route-map/policy, compteurs |
| Best path | Quel chemin est retenu et pourquoi ? | Attributs candidats et raison du best path |
| NEXT_HOP | Le prochain saut est-il résolu ? | RIB et IGP/connectivité du prochain saut |
| RIB/FIB | Le chemin est-il installé et programmé ? | Table de routage et commande de forwarding |
| Service | Le trafic arrive-t-il ? | Ping ciblé, traceroute, session applicative, capture |

Ne change jamais MED, LOCAL_PREF et AS_PATH simultanément pour résoudre une route manquante : tu détruirais la preuve permettant d’isoler la cause.


## 2. Passage à l’échelle : iBGP full mesh et route reflectors

### 2.1 Pourquoi le full mesh augmente le coût d’exploitation

Avec `n` routeurs iBGP, un full mesh requiert `n × (n - 1) / 2` sessions entre toutes les paires. Avec quatre routeurs, cela représente six sessions ; avec 20 routeurs, 190 ; avec 100 routeurs, 4 950. Ces nombres ne comptent que les sessions, pas la charge de mises à jour, les politiques, les chemins candidats ou les besoins de supervision.

La règle iBGP historique empêche un routeur ordinaire de réannoncer à un autre voisin iBGP une route qu’il a lui-même apprise en iBGP. Le full mesh garantit que chaque routeur reçoit l’information directement d’un speaker qui peut l’annoncer selon les règles. Un **route reflector** (RR) fournit une alternative normalisée : il réfléchit certaines routes entre ses clients et d’autres voisins, avec des règles explicites pour éviter les boucles.

### Schéma 2 — Full mesh et route reflector

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Passer d’un full mesh iBGP au Route Reflection" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Passer d’un full mesh iBGP au Route Reflection</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Le RR distribue des routes iBGP selon les règles de réflexion définies par le protocole.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="105" width="435" height="340" rx="15" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="252" y="132" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700" font-family="Inter,Arial,sans-serif">iBGP full mesh</text><path d="M 145 205 L 365 205" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 145 205 L 145 355" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 145 205 L 365 355" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 365 205 L 145 355" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 365 205 L 365 355" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 145 355 L 365 355" fill="none" stroke="#8190a4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="90" y="180" width="110" height="50" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="145.0" y="207" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">R1</text><text x="145.0" y="229" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">iBGP</text><rect x="310" y="180" width="110" height="50" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="365.0" y="207" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">R2</text><text x="365.0" y="229" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">iBGP</text><rect x="90" y="330" width="110" height="50" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="145.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">R3</text><text x="145.0" y="379" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">iBGP</text><rect x="310" y="330" width="110" height="50" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="365.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">R4</text><text x="365.0" y="379" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">iBGP</text><text x="252" y="410" text-anchor="middle" fill="#fbbf24" font-size="13" font-weight="700" font-family="Inter,Arial,sans-serif">4 routeurs → 6 sessions iBGP</text><rect x="530" y="105" width="435" height="340" rx="15" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="748" y="132" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700" font-family="Inter,Arial,sans-serif">Route reflector</text><rect x="665" y="160" width="165" height="60" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="747.5" y="187" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">RR-1</text><text x="747.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">route reflector</text><path d="M 747 220 L 630 285" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="575" y="285" width="110" height="58" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="630.0" y="312" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">C1</text><text x="630.0" y="334" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">client</text><path d="M 747 220 L 755 285" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="700" y="285" width="110" height="58" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="755.0" y="312" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">C2</text><text x="755.0" y="334" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">client</text><path d="M 747 220 L 880 285" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="825" y="285" width="110" height="58" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="880.0" y="312" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">C3</text><text x="880.0" y="334" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">client</text><text x="748" y="388" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="700" font-family="Inter,Arial,sans-serif">3 clients + 1 RR → 3 sessions</text><text x="748" y="414" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Réduit le mesh ; ajoute une dépendance logique au RR</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Le nombre de sessions indiqué compte uniquement les sessions iBGP représentées dans chaque exemple.</text>
</svg>
</div>

Le full mesh assure la visibilité iBGP en créant une session entre chaque paire. Avec quatre speakers, il faut six sessions. Un RR central avec trois clients réduit l’exemple à trois sessions, mais fait de la conception du RR, de sa redondance et de sa politique de réflexion un sujet critique.

### Schéma 3 — Une route réfléchie

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Route reflection : origine, réflexion, réception" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Route reflection : origine, réflexion, réception</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Illustration d’un chemin de route entre un client d’un RR et un autre client.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="115" width="930" height="330" rx="15" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="500" y="143" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700" font-family="Inter,Arial,sans-serif">Un client apprend un préfixe via eBGP, puis l’annonce est réfléchie en iBGP</text><rect x="70" y="215" width="170" height="85" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="155.0" y="242" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">PE-1</text><text x="155.0" y="264" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">AS 65010 · origine</text><rect x="345" y="195" width="190" height="105" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="440.0" y="222" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">RR-1</text><text x="440.0" y="244" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">AS 65010 · cluster</text><rect x="700" y="215" width="190" height="85" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="795.0" y="242" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">PE-2</text><text x="795.0" y="264" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">client iBGP</text><path d="M 240 257 L 345 245" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 240 257 L 345 245" dur="2.6s" begin="0s" repeatCount="indefinite"/></circle><path d="M 535 245 L 700 257" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 535 245 L 700 257" dur="2.6s" begin="1s" repeatCount="indefinite"/></circle><rect x="80" y="335" width="220" height="27" rx="8" fill="#101a28" stroke="#fbbf24" stroke-width="1.5"/><text x="190.0" y="353" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700" font-family="Inter,Arial,sans-serif">Route apprise · attributs BGP</text><rect x="340" y="335" width="210" height="27" rx="8" fill="#101a28" stroke="#4ade80" stroke-width="1.5"/><text x="445.0" y="353" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700" font-family="Inter,Arial,sans-serif">Annonce réfléchie iBGP</text><rect x="635" y="335" width="250" height="27" rx="8" fill="#101a28" stroke="#c4b5fd" stroke-width="1.5"/><text x="760.0" y="353" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="700" font-family="Inter,Arial,sans-serif">ORIGINATOR_ID / CLUSTER_LIST</text><text x="500" y="405" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Les attributs anti-boucle de réflexion ne remplacent pas la politique d’import/export.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Les routes ne sont pas réfléchies comme une simple diffusion : les règles client/non-client et les attributs anti-boucle comptent.</text>
</svg>
</div>

Le client PE-1 apprend le préfixe en eBGP et l’annonce au RR. Le RR peut réfléchir les routes de clients vers d’autres clients, avec les règles du protocole. ORIGINATOR_ID et CLUSTER_LIST aident à éviter des boucles de réflexion ; ils ne remplacent pas l’analyse de politique.

### 2.2 Concepts du route reflector

- **Route reflector (RR)** : un speaker iBGP autorisé à réfléchir certaines routes apprises par iBGP vers d’autres voisins conformément à la RFC 4456.
- **Client** : voisin iBGP configuré en client du RR.
- **Non-client** : voisin iBGP ordinaire du RR.
- **ORIGINATOR_ID** : attribut optionnel non transitif permettant de porter le Router ID BGP du speaker à l’origine de la route réfléchie.
- **CLUSTER_LIST** : liste des identifiants de clusters route reflector traversés, utilisée pour détecter certaines boucles de réflexion.

Une route apprise d’un client peut être réfléchie vers les autres clients et certains non-clients conformément aux règles ; une route apprise d’un non-client est reflétée vers les clients conformément aux règles du protocole. N’essaie pas de simplifier cette logique en disant « tout ce qui arrive au RR est envoyé partout ». L’origine eBGP, le statut client/non-client, les attributs anti-boucle et la politique influencent le traitement.

### 2.3 Exemple de configuration Cisco IOS — un RR et deux clients

L’exemple est illustratif et doit être validé sur l’image logicielle utilisée. R1 est le RR dans l’AS privé 65010 ; R2 et R3 sont des clients. Le réseau de transport doit déjà fournir une connectivité IP entre les adresses de voisinage.

**R1 — route reflector :**

```text
router bgp 65010
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 route-reflector-client
 neighbor 192.0.2.3 remote-as 65010
 neighbor 192.0.2.3 route-reflector-client
```

**R2 — client :**

```text
router bgp 65010
 neighbor 192.0.2.1 remote-as 65010
```

**R3 — client :**

```text
router bgp 65010
 neighbor 192.0.2.1 remote-as 65010
```

Ces adresses sont réservées à la documentation. Dans une maquette réelle, remplace-les par les adresses de loopback ou de lien configurées. Pour des sessions fondées sur des loopbacks, assure-toi que le transport IGP, la source TCP et les options de voisinage sont cohérents.

Commandes de vérification typiques :

```text
show bgp ipv4 unicast summary
show bgp ipv4 unicast
show bgp ipv4 unicast neighbors 192.0.2.2 advertised-routes
show running-config
```

La syntaxe exacte de `show bgp` varie avec IOS/IOS XE et la plateforme. Utilise `show ip bgp` si c’est la syntaxe prise en charge par l’équipement.

### 2.4 Redondance des route reflectors

Un seul RR réduit le nombre de sessions mais devient une dépendance logique importante. De nombreux réseaux déploient au moins deux RR ou une conception hiérarchique. Une paire de RR n’implique pas automatiquement que tous les chemins seront visibles ou sélectionnés de manière identique : le placement, les sessions entre RR, les attributs, le cluster et les mécanismes de réflexion comptent.

Avant de déployer un deuxième RR :

1. documente les sessions entre clients et RR ;
2. vérifie l’unicité des Router ID et des identifiants de cluster attendus ;
3. décide comment les RR s’échangent leurs propres chemins ;
4. vérifie si les clients ont des sessions vers les deux RR ;
5. compare la route reçue de chaque RR et le résultat best path ;
6. simule la perte d’un RR et valide les chemins de remplacement.

### 2.5 Pièges du route reflection

Une topologie de réflexion mal conçue peut cacher des routes alternatives, créer des dépendances non évidentes ou entraîner des choix de chemin différents de ceux attendus. L’existence d’une route dans la table BGP du RR ne prouve pas qu’elle a été annoncée à chaque client. Examine les annonces spécifiques par voisin, les politiques, les attributs de réflexion et les sorties `advertised-routes` si elles existent sur la plateforme.


## 3. Communautés BGP : marquer la route plutôt que recopier des listes

### 3.1 La communauté est une étiquette, pas une commande universelle

Une communauté est un attribut attaché à une route BGP. Elle peut indiquer une classe de client, une région, une préférence ou une action attendue. Sa sémantique est définie par l’opérateur, les règles de service et les politiques configurées. Une communauté `65020:100` ne veut rien dire par elle-même pour tous les réseaux ; elle ne prend un sens que dans le système qui a documenté et interprète cette valeur.

Familles de communautés :

| Type | Représentation courante | Usage |
|---|---|---|
| Standard community | `ASN:valeur` dans la représentation usuelle à 16 bits | Marques de politique simples |
| Extended community | Attribut structuré, codé sur 8 octets | Cas d’usage avec sous-type et portée spécifiques, notamment certains environnements VPN |
| Large community | `ASN:valeur1:valeur2` | Espace plus large adapté aux ASN 32 bits et aux namespaces opérateur |

La RFC 1997 définit les communautés standard ; la RFC 4360 définit un format pour les communautés étendues, complété/actualisé par des documents ultérieurs ; la RFC 8092 définit les Large Communities. Consulte la norme et la documentation du constructeur pour la syntaxe exacte de la plateforme.

### Schéma 4 — Communautés et politique

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Communautés BGP : marquer, interpréter, appliquer une politique" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Communautés BGP : marquer, interpréter, appliquer une politique</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Une communauté transporte une étiquette qui peut être utilisée par les politiques de routage.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="45" y="190" width="170" height="85" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="130.0" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS 65010</text><text x="130.0" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">client</text><rect x="305" y="165" width="190" height="135" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="400.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS 65020</text><text x="400.0" y="214" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">opérateur </text><text x="400.0" y="231" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif"> ajoute une communauté</text><rect x="590" y="190" width="160" height="85" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="670.0" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique</text><text x="670.0" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">match community</text><rect x="820" y="190" width="135" height="85" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="887.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS 65030</text><text x="887.5" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">peer</text><path d="M 215 232 L 305 232" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 215 232 L 305 232" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle><path d="M 495 232 L 590 232" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 495 232 L 590 232" dur="2.5s" begin="0.7s" repeatCount="indefinite"/></circle><path d="M 750 232 L 820 232" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 750 232 L 820 232" dur="2.5s" begin="1.4s" repeatCount="indefinite"/></circle><rect x="120" y="340" width="760" height="84" rx="12" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="500" y="366" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700" font-family="Inter,Arial,sans-serif">Exemple privé de politique : 65020:100 = « client »</text><text x="500" y="392" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">La communauté est une étiquette définie par l’opérateur ; sa signification n’est pas universelle.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Exemple illustratif ; la valeur 65020:100 n’a de sens que si l’opérateur a documenté ce code.</text>
</svg>
</div>

La valeur de communauté utilisée est illustrative. Une communauté n’exécute pas une action par elle-même : une route-map ou une politique équivalente doit interpréter la marque et appliquer l’action attendue. Documente toujours le sens de chaque valeur.

### 3.2 Exemple de politique de communauté

Supposons que l’AS 65020 souhaite distinguer les routes de clients. L’opérateur choisit `65020:100` comme marque de catégorie « client ». Cette valeur est arbitraire et locale à l’exemple.

Le processus logique :

1. le routeur reçoit un préfixe d’un client, et vérifie d’abord qu’il fait partie des préfixes autorisés ;
2. une politique ajoute la communauté documentée ;
3. les politiques internes peuvent utiliser la marque pour affecter LOCAL_PREF, la politique d’export ou une autre action autorisée ;
4. à la sortie, la route n’est annoncée que si elle est permise à ce voisin ;
5. les communautés envoyées vers un tiers sont définies explicitement : certaines peuvent être supprimées, conservées ou transformées selon la politique.

### 3.3 Exemples Cisco IOS de communities

La syntaxe réelle varie. Exemple illustratif :

```text
ip community-list standard CLIENTS permit 65020:100
!
route-map CUSTOMER-IN permit 10
 set community 65020:100 additive
!
route-map PEER-OUT deny 10
 match community CLIENTS
!
route-map PEER-OUT permit 100
```

Ce fragment montre la forme générale, mais **ne doit pas être copié sans adaptation**. Une route-map doit être attachée au voisin correct, la logique de `deny`/`permit` doit correspondre au contrat de politique, et le résultat doit être vérifié avec les annonces réelles. Un ordre de séquences mal pensé peut bloquer tout l’export ou autoriser des routes inattendues. `additive` conserve les communautés existantes dans les implémentations qui supportent ce comportement ; sans cette option, le set peut les remplacer.

### 3.4 Communautés bien gouvernées

Un registre opérateur de communautés doit documenter la valeur, le propriétaire, l’origine de la marque, la portée prévue, les actions associées, si la marque doit être exportée, et les tests nécessaires. Les marques reçues d’un AS externe ne doivent pas être considérées automatiquement comme fiables. Un voisin peut ajouter ou modifier des communautés ; filtre ou réécris-les lorsque la politique l’exige.


## 4. Agrégation des préfixes

### 4.1 Pourquoi agréger ?

L’agrégation réduit le nombre de préfixes annoncés et permet de résumer un ensemble d’adresses derrière une frontière de routage. Elle est utile quand le plan d’adressage est hiérarchique. Elle devient dangereuse lorsque le résumé couvre des espaces qui ne sont pas réellement joignables ou qu’il masque des destinations manquantes.

### Schéma 5 — Agrégation sans erreur de couverture

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Agrégation BGP : quatre /24 deviennent un /22" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Agrégation BGP : quatre /24 deviennent un /22</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">L’agrégat réduit le volume d’annonces mais représente plusieurs préfixes plus spécifiques.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="105" width="440" height="335" rx="14" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="255" y="133" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Préfixes détaillés à l’origine</text><rect x="70" y="170" width="270" height="35" rx="8" fill="#151f2d" stroke="#45c7f5" stroke-width="1.5"/><text x="205" y="193" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="600" font-family="Inter,Arial,sans-serif">198.51.100.0/24</text><path d="M 340 187 L 425 240" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="70" y="225" width="270" height="35" rx="8" fill="#151f2d" stroke="#45c7f5" stroke-width="1.5"/><text x="205" y="248" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="600" font-family="Inter,Arial,sans-serif">198.51.101.0/24</text><path d="M 340 242 L 425 240" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="70" y="280" width="270" height="35" rx="8" fill="#151f2d" stroke="#45c7f5" stroke-width="1.5"/><text x="205" y="303" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="600" font-family="Inter,Arial,sans-serif">198.51.102.0/24</text><path d="M 340 297 L 425 240" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="70" y="335" width="270" height="35" rx="8" fill="#151f2d" stroke="#45c7f5" stroke-width="1.5"/><text x="205" y="358" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="600" font-family="Inter,Arial,sans-serif">198.51.103.0/24</text><path d="M 340 352 L 425 240" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="425" y="205" width="80" height="70" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="465.0" y="232" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">ABR</text><path d="M 505 240 L 600 240" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 505 240 L 600 240" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle><rect x="600" y="192" width="320" height="98" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="760.0" y="219" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Résumé annoncé</text><text x="760.0" y="241" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">198.51.100.0/22</text><text x="760" y="316" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Le /22 couvre exactement les quatre /24 ci-dessus.</text><text x="760" y="343" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Attention : la route de résumé peut attirer du trafic</text><text x="760" y="361" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">pour un sous-réseau absent si la politique est incorrecte.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Exemple d’agrégation alignée : 198.51.100.0/22 couvre 198.51.100.0 à 198.51.103.255.</text>
</svg>
</div>

Les quatre réseaux /24 sont contigus et alignés ; ils peuvent être représentés par un /22. Avant d’annoncer ce résumé, confirme que tous les sous-réseaux inclus sont sous contrôle et qu’une route de rejet ou une autre protection empêche une boucle vers des destinations absentes, selon la plateforme.

### 4.2 Vérifier le calcul du résumé

Quatre préfixes contigus `198.51.100.0/24`, `198.51.101.0/24`, `198.51.102.0/24` et `198.51.103.0/24` peuvent être représentés par `198.51.100.0/22`. Cette conclusion repose sur l’alignement du préfixe : un /22 avance par blocs de quatre /24 à la troisième partie dans cet exemple.

N’agrège pas quatre réseaux uniquement parce qu’ils se suivent dans une liste. Ils doivent être contigus, correctement alignés, sous ta responsabilité et avec la route de forwarding correspondante. Si un des sous-réseaux devient absent, le résumé peut encore attirer le trafic vers la frontière du résumé. Selon la plateforme et la configuration, une route de rejet/Null0 ou une autre protection peut être nécessaire pour éviter une boucle de routage. Vérifie le comportement réel.

### 4.3 Politique d’agrégation et attributs

Une route agrégée peut présenter des attributs qui ne sont pas la simple copie de chaque préfixe plus spécifique. BGP comporte des règles et options d’agrégation, et certaines plateformes offrent des options qui influencent l’annonce des préfixes composants. Le résultat doit être contrôlé en examinant l’agrégat annoncé, les composants, le NEXT_HOP et les attributs. Ne suppose pas qu’un résumé conserve sans changement tous les attributs des réseaux spécifiques.

### 4.4 Laboratoire d’agrégation

1. configure quatre routes /24 contiguës en laboratoire ;
2. vérifie qu’elles sont présentes dans la RIB ;
3. configure l’agrégat /22 dans BGP selon la plateforme ;
4. examine la route locale puis l’annonce sortante ;
5. retire un préfixe composant et observe si le résumé demeure, selon la méthode de configuration ;
6. vérifie la route de rejet éventuelle et teste les destinations des quatre composants ;
7. consigne la politique de retrait et le comportement en cas de panne d’un sous-réseau.


## 5. Préférer un chemin : LOCAL_PREF, MED et AS_PATH

### 5.1 LOCAL_PREF

LOCAL_PREF est un attribut well-known discretionary utilisé à l’intérieur d’un AS pour indiquer quel chemin est préféré. Une valeur plus élevée est généralement préférée par le processus BGP de cet AS, suivant la politique et l’ordre de décision de l’implémentation. LOCAL_PREF n’est généralement pas propagé aux voisins eBGP comme un attribut de préférence globale.

Utilise LOCAL_PREF lorsque ton objectif est de choisir un point de sortie de ton AS vers une destination. Par exemple, un AS peut préférer son fournisseur A pour le trafic sortant et conserver le fournisseur B comme solution alternative. Il faut s’assurer que les routeurs de l’AS appliquent une politique cohérente à l’ensemble des chemins concernés.

### 5.2 MED

MED (*Multi-Exit Discriminator*) permet généralement de communiquer à un AS voisin une préférence relative entre plusieurs points d’entrée vers l’AS d’origine. Une valeur plus faible est généralement préférable lorsque les chemins sont comparés conformément aux règles de la plateforme. La comparaison du MED dépend toutefois de la configuration et du contexte — par exemple, les chemins provenant du même AS voisin sont souvent comparés par défaut alors que les comparaisons inter-AS peuvent être conditionnelles ou configurables.

N’utilise pas MED comme s’il s’agissait d’un LOCAL_PREF partagé sur Internet. MED exprime une indication vers le voisin qui peut l’interpréter selon sa politique ; il ne garantit pas à lui seul le chemin choisi par l’autre AS.

### 5.3 AS_PATH Prepending

L’AS_PATH contient des informations sur les AS traversés. Ajouter plusieurs occurrences de son propre ASN à une annonce peut faire apparaître un chemin plus long aux réseaux distants, ce qui peut influencer leur sélection. Ce mécanisme est souvent appelé *AS-path prepending*.

Le prepending ne garantit pas le chemin entrant : un voisin peut préférer LOCAL_PREF, une communauté, un contrat commercial ou une autre règle avant d’examiner la longueur d’AS_PATH. Il peut aussi recevoir des routes concurrentes qui ont des attributs plus préférables. Mesure le résultat réellement observé depuis plusieurs réseaux de contrôle lorsque c’est pertinent.

### Schéma 6 — Ingénierie de trafic

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Ingénierie de trafic : outbound et inbound ne sont pas identiques" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Ingénierie de trafic : outbound et inbound ne sont pas identiques</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">LOCAL_PREF est généralement un levier interne de sortie ; les annonces vers le voisin tentent d’influencer le trafic entrant.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="110" width="455" height="335" rx="14" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="260" y="138" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Trafic sortant de notre AS</text><rect x="70" y="220" width="130" height="70" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="135.0" y="247" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Réseau</text><text x="135.0" y="269" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">AS 65020</text><rect x="290" y="170" width="160" height="62" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="370.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">UP-1</text><text x="370.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">LocalPref 200</text><rect x="290" y="275" width="160" height="62" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="370.0" y="302" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">UP-2</text><text x="370.0" y="324" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">LocalPref 100</text><path d="M 200 240 L 290 201" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 200 250 L 290 306" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><text x="265" y="385" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">LOCAL_PREF influence le choix interne</text><rect x="520" y="110" width="445" height="335" rx="14" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="742" y="138" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Trafic entrant vers notre AS</text><rect x="555" y="220" width="135" height="70" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="622.5" y="247" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Voisin</text><text x="622.5" y="269" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">réseau externe</text><rect x="805" y="170" width="125" height="62" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="867.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Lien A</text><text x="867.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">annonce normale</text><rect x="805" y="275" width="125" height="62" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="867.5" y="302" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Lien B</text><text x="867.5" y="324" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">AS_PATH prepend</text><path d="M 690 240 L 805 201" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 690 250 L 805 306" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><text x="742" y="385" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Prepending / MED influencent, sans garantir</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Le comportement dépend des politiques des AS voisins ; ne promets jamais qu’un prepend imposera une route entrante.</text>
</svg>
</div>

LOCAL_PREF est normalement diffusé à l’intérieur de l’AS et décide notamment du chemin sortant préféré. MED propose une préférence d’entrée au voisin, avec des règles de comparaison dépendantes. AS-path prepending peut influencer le trafic entrant sans le garantir.

### 5.4 La politique doit correspondre au sens du trafic

- **Trafic sortant depuis notre AS :** LOCAL_PREF peut choisir quel fournisseur est utilisé.
- **Trafic entrant vers notre AS :** les annonces, les communautés convenues avec les fournisseurs, MED ou AS_PATH prepending peuvent influencer certains choix à distance.
- **NEXT_HOP :** le chemin n’est pas exploitable si le prochain saut ne peut pas être résolu.
- **Best path :** l’ordre exact comporte plusieurs critères et dépend de l’implémentation ; ne le résume pas à la seule longueur d’AS_PATH.

### 5.5 Exemple de vérification

Avant de modifier une préférence, collecte les routes candidates et attributs :

```text
show bgp ipv4 unicast 203.0.113.0/24
show bgp ipv4 unicast neighbors 192.0.2.1 received-routes
show bgp ipv4 unicast neighbors 192.0.2.1 advertised-routes
show ip route 203.0.113.0
```

Les commandes affichant les routes reçues dépendent des fonctionnalités d’enregistrement et du système utilisé ; la commande exacte peut différer. Confirme que les chemins sont bien présents, puis identifie le critère qui fait gagner le meilleur chemin. Les valeurs d’exemple ne constituent pas une recommandation générale.


## 6. Politiques d’import et d’export : fermer le périmètre

### 6.1 Politiques par voisin

La politique d’import définit les routes qu’un routeur accepte de considérer depuis un voisin. La politique d’export définit les routes qu’il a le droit d’annoncer à ce voisin. Elles doivent être pensées ensemble et correspondre au rôle de la session : client, pair, fournisseur, interconnexion privée ou session interne.

### Schéma 7 — Import et export

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Politique BGP : contrôler l’import et l’export" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Politique BGP : contrôler l’import et l’export</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Le filtrage doit être explicite et doit être vérifié sur la session réelle.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="40" y="190" width="155" height="90" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="117.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS voisin</text><text x="117.5" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">annonces entrantes</text><rect x="260" y="160" width="205" height="145" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="362.5" y="187" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique IN</text><text x="362.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">prefix-list + attributs</text><rect x="535" y="160" width="190" height="145" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="630.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Décision locale</text><text x="630.0" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">accepté / rejeté</text><rect x="795" y="190" width="165" height="90" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="877.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS distant</text><text x="877.5" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">annonces sortantes</text><path d="M 195 235 L 260 235" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 195 235 L 260 235" dur="2s" begin="0s" repeatCount="indefinite"/></circle><path d="M 465 235 L 535 235" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 465 235 L 535 235" dur="2s" begin="0.5s" repeatCount="indefinite"/></circle><path d="M 725 235 L 795 235" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 725 235 L 795 235" dur="2s" begin="1s" repeatCount="indefinite"/></circle><rect x="110" y="345" width="780" height="75" rx="12" fill="#101a28" stroke="#34475d" stroke-width="1.5"/><text x="500" y="372" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700" font-family="Inter,Arial,sans-serif">IN : ce que j’accepte       OUT : ce que j’annonce</text><text x="500" y="398" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Politique par voisin et par famille d’adresses ; refus implicite à vérifier selon l’OS.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Une session Established sans politique sûre peut représenter un risque de fuite de routes.</text>
</svg>
</div>

Sépare les annonces entrantes des annonces sortantes. Les politiques doivent couvrir tous les voisins eBGP et toutes les familles d’adresses utilisées. RFC 8212 recommande le comportement fermé en l’absence de politiques explicites ; vérifie les options et le comportement effectif de ton implémentation.

### 6.2 Prefix-list : écrire ce qui est permis

Une prefix-list permet de correspondre à des préfixes et, selon la syntaxe, à des plages de longueurs. Il faut comprendre la différence entre une correspondance exacte et une correspondance qui autorise des sous-préfixes. Une règle qui vise `198.51.100.0/24` exactement n’est pas équivalente à une règle qui autorise de nombreux préfixes plus spécifiques contenus dans cette plage.

Pour chaque voisin eBGP, maintiens une liste de préfixes annoncés attendus et une politique d’import adaptée à la relation. La politique peut être différente entre un client et un pair ; n’utilise pas une règle universelle qui annonce tout à tout le monde.

### 6.3 RFC 8212 : ne pas compter sur des politiques permissives implicites

RFC 8212 définit un comportement qui empêche les routes eBGP d’être éligibles à la décision sans politique d’import explicite et empêche l’annonce sans politique d’export explicite, sous réserve des options et du comportement réel de l’implémentation. Tous les équipements n’ont pas nécessairement ce mode activé par défaut. Configure et vérifie la politique plutôt que de supposer que la plateforme bloque automatiquement.

### 6.4 Limiter le nombre de préfixes

Une limite de préfixes (*maximum-prefix* ou équivalent) aide à détecter une hausse inattendue du nombre de routes reçues. Ce n’est pas un substitut au filtrage. Une limite trop basse peut interrompre légitimement une session ; une limite trop élevée peut ne pas arrêter une fuite significative. Définis des seuils selon l’inventaire autorisé, avec alerte et procédure d’incident.

### 6.5 Prévenir les fuites de routes

Une fuite de routes se produit lorsqu’une information de routage est propagée au-delà de l’intention de la politique. Les causes peuvent être une route-map trop permissive, un mauvais rôle de session, une redistribution inappropriée ou une configuration d’export copiée sans adaptation. Pour réduire le risque :

- applique des politiques d’import et d’export à chaque session eBGP ;
- contrôle les préfixes, les longueurs, les ASN et les familles activées ;
- attache les politiques au bon voisin et à la bonne direction ;
- vérifie les annonces sortantes réelles après changement ;
- surveille les variations de nombre de routes, les nouveaux origin AS et les annonces inattendues ;
- prépare une procédure de retrait rapide qui ne supprime pas inutilement tout le processus BGP.


## 7. RPKI / ROA : valider l’origine d’un préfixe

RPKI permet de publier et valider des Route Origin Authorizations (ROA). Une ROA indique qu’un ASN est autorisé à originer un préfixe dans les limites de longueur qui y sont définies. La validation d’origine classe typiquement une annonce en **Valid**, **Invalid** ou **NotFound** selon les données validées disponibles.

### Schéma 8 — Fuite de routes

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Fuite de routes : où placer les barrières" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Fuite de routes : où placer les barrières</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">La route leak se produit quand un préfixe est propagé au-delà de l’intention de politique.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="35" y="190" width="160" height="85" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="115.0" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Client AS</text><text x="115.0" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">route légitime</text><rect x="280" y="190" width="175" height="85" rx="13" fill="#151f2d" stroke="#45c7f5" stroke-width="2"/><text x="367.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS 65020</text><text x="367.5" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">transit</text><rect x="545" y="190" width="175" height="85" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="632.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">AS 65030</text><text x="632.5" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">peer</text><rect x="805" y="190" width="160" height="85" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="885.0" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Autre réseau</text><text x="885.0" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">destination</text><path d="M 195 232 L 280 232" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 195 232 L 280 232" dur="2.2s" begin="0s" repeatCount="indefinite"/></circle><path d="M 455 232 L 545 232" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 455 232 L 545 232" dur="2.2s" begin="0.6s" repeatCount="indefinite"/></circle><path d="M 720 232 L 805 232" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 720 232 L 805 232" dur="2.2s" begin="1.2s" repeatCount="indefinite"/></circle><rect x="145" y="340" width="710" height="80" rx="12" fill="#281820" stroke="#fb7185" stroke-width="2"/><text x="500" y="368" text-anchor="middle" fill="#fb7185" font-size="15" font-weight="700" font-family="Inter,Arial,sans-serif">Route leak : une route reçue est réannoncée hors politique</text><text x="500" y="395" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Barrières : import/export explicites, préfixes attendus, max-prefix, surveillance</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Le schéma est conceptuel : la relation client/transit/peer détermine les politiques attendues.</text>
</svg>
</div>

Une annonce reçue d’un client ne doit pas automatiquement être exportée vers tous les voisins. La relation contractuelle ou logique (client, pair, fournisseur, interne) détermine ce qui peut être annoncé. Les filtres de préfixes, communautés, maximum de préfixes et alertes peuvent réduire le risque.


### Schéma 9 — Validation RPKI d’origine

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="RPKI / ROA : trois états de validation d’origine" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">RPKI / ROA : trois états de validation d’origine</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">La validation compare le préfixe annoncé, sa longueur et l’ASN d’origine à des ROA validés.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="40" y="195" width="185" height="95" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="132.5" y="222" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Route reçue</text><text x="132.5" y="244" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">préfixe + origin AS</text><path d="M 225 242 L 285 242" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 225 242 L 285 242" dur="2s" begin="0s" repeatCount="indefinite"/></circle><rect x="285" y="190" width="200" height="105" rx="13" fill="#151f2d" stroke="#c4b5fd" stroke-width="2"/><text x="385.0" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Validation ROA</text><text x="385.0" y="239" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">préfixe / longueur / ASN</text><path d="M 485 242 L 505 242" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 505 176 L 505 336" fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M 505 176 L 535 176" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 505 256 L 535 256" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 505 336 L 535 336" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 485 242 L 505 242" dur="2s" begin="0.4s" repeatCount="indefinite"/></circle><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 505 176 L 535 176" dur="2s" begin="0.7s" repeatCount="indefinite"/></circle><circle r="6" fill="#fb7185" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 505 256 L 535 256" dur="2s" begin="1s" repeatCount="indefinite"/></circle><circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.7"><animateMotion path="M 505 336 L 535 336" dur="2s" begin="1.3s" repeatCount="indefinite"/></circle><rect x="535" y="145" width="160" height="62" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="615.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Valid</text><text x="615.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">autorisé</text><rect x="535" y="225" width="160" height="62" rx="13" fill="#151f2d" stroke="#fb7185" stroke-width="2"/><text x="615.0" y="252" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Invalid</text><text x="615.0" y="274" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">contradit le ROA</text><rect x="535" y="305" width="160" height="62" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="615.0" y="332" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">NotFound</text><text x="615.0" y="354" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">aucun ROA couvrant</text><path d="M 695 176 L 765 176" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 695 256 L 765 256" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 695 336 L 765 336" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="765" y="145" width="185" height="62" rx="13" fill="#151f2d" stroke="#4ade80" stroke-width="2"/><text x="857.5" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique</text><text x="857.5" y="194" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">accepte souvent</text><rect x="765" y="225" width="185" height="62" rx="13" fill="#151f2d" stroke="#fb7185" stroke-width="2"/><text x="857.5" y="252" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique</text><text x="857.5" y="274" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">peut rejeter</text><rect x="765" y="305" width="185" height="62" rx="13" fill="#151f2d" stroke="#fbbf24" stroke-width="2"/><text x="857.5" y="332" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">Politique</text><text x="857.5" y="354" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">décision locale</text><text x="500" y="420" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">RPKI origin validation ne valide pas l’AS_PATH entier et ne remplace pas les filtres.</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Le traitement de Valid / Invalid / NotFound doit être défini par une politique et un plan de retour arrière.</text>
</svg>
</div>

RPKI Route Origin Validation compare le préfixe, la longueur et l’ASN d’origine annoncés aux ROA valides. Valid, Invalid et NotFound sont des états de validation ; la politique locale décide ensuite comment les routes sont traitées. RPKI ne prouve pas à lui seul que tout AS_PATH est authentique.

### 7.1 Ce que RPKI valide — et ne valide pas

La validation d’origine vérifie notamment si l’ASN d’origine et le préfixe/longueur sont autorisés par les ROA. Elle ne valide pas cryptographiquement chaque AS intermédiaire dans AS_PATH et ne prouve pas que le service distant fonctionne. Les états Valid/Invalid/NotFound doivent être traités par une politique locale clairement définie.

- **Valid :** l’annonce correspond à une autorisation validée.
- **Invalid :** une ROA validée contredit l’ASN d’origine ou les limites de longueur du préfixe annoncé.
- **NotFound :** aucune autorisation applicable n’a permis de valider ou invalider l’annonce.

Évite d’affirmer que NotFound signifie « malveillant » ou que Valid garantit le chemin entier. Une politique courante consiste à pénaliser ou rejeter les routes Invalid, mais la décision doit être documentée, surveillée et alignée avec la politique opérateur.

### 7.2 Sources de validation et caches

Le routeur ne consulte pas nécessairement directement chaque ROA. Une infrastructure RPKI fournit des données validées, souvent via un cache RTR. La disponibilité du cache, les délais d’actualisation, les états périmés et le comportement de repli doivent être compris. Lors d’un incident, vérifie séparément la connectivité au cache, les données de validation et la politique BGP qui traite les états.


## 8. NEXT_HOP, IGP et séparation du plan de contrôle et du forwarding

Une route BGP choisie n’est pas automatiquement exploitable si le prochain saut n’est pas résolu. En iBGP, le NEXT_HOP d’une route externe peut rester l’adresse du routeur d’entrée. Les routeurs internes doivent alors savoir atteindre ce NEXT_HOP au moyen de l’IGP ou d’une route appropriée. Les détails changent selon la topologie, les options `next-hop-self` et la plateforme.

### Schéma 10 — Arbre de diagnostic

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Diagnostic BGP : suivre le cycle de la route" style="display:block;width:100%;max-width:1000px;height:auto;font-family:Inter,Arial,sans-serif">
<rect x="0" y="0" width="1000" height="540" rx="16" fill="#0b111b" stroke="#0b111b" stroke-width="0"/>
<text x="28" y="34" text-anchor="start" fill="#eef4fb" font-size="22" font-weight="700" font-family="Inter,Arial,sans-serif">Diagnostic BGP : suivre le cycle de la route</text>
<text x="29" y="60" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400" font-family="Inter,Arial,sans-serif">Toujours déterminer à quelle étape la route disparaît avant de changer les attributs.</text>
<path d="M 28 78 L 972 78" fill="none" stroke="#34475d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="80" y="115" width="840" height="68" rx="12" fill="#152436" stroke="#45c7f5" stroke-width="2"/><text x="500" y="143" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">1. Session</text><text x="500" y="165" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">TCP/179 · ASN · état Established ?</text><path d="M 500 183 L 500 210" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="80" y="210" width="840" height="68" rx="12" fill="#152436" stroke="#c4b5fd" stroke-width="2"/><text x="500" y="238" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">2. Réception et politique</text><text x="500" y="260" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Route reçue ? Import IN l’accepte ?</text><path d="M 500 278 L 500 305" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="80" y="305" width="840" height="68" rx="12" fill="#152436" stroke="#4ade80" stroke-width="2"/><text x="500" y="333" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">3. Best path et NEXT_HOP</text><text x="500" y="355" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Chemin candidat ? Attributs ? Prochain saut résolu ?</text><path d="M 500 373 L 500 400" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="80" y="400" width="840" height="68" rx="12" fill="#152436" stroke="#fbbf24" stroke-width="2"/><text x="500" y="428" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700" font-family="Inter,Arial,sans-serif">4. RIB / FIB / trafic</text><text x="500" y="450" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400" font-family="Inter,Arial,sans-serif">Route installée ? ACL / retour / application ?</text>
<text x="28" y="515" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400" font-family="Inter,Arial,sans-serif">Collecte les sorties avant/après et teste le trafic réel ; Established n’est qu’un point de départ.</text>
</svg>
</div>

Respecte cet ordre avant de changer un attribut. Vérifie d’abord la session, puis la réception/politique, le best path et le NEXT_HOP, enfin la RIB/FIB et le trafic de bout en bout.

### 8.1 Symptôme : route BGP présente mais absente de la RIB

Ordre de contrôle conseillé :

1. le préfixe figure-t-il dans la table BGP et quels sont les chemins candidats ?
2. le chemin a-t-il passé les politiques d’import ?
3. quel est son état d’éligibilité et quel chemin est sélectionné ?
4. le NEXT_HOP est-il résolu dans la table de routage ?
5. une route connectée, statique ou issue d’un autre protocole est-elle préférée ?
6. la route apparaît-elle dans la RIB, puis dans le forwarding ?

Une route dans la table BGP peut ne pas être installée en raison d’un prochain saut inaccessible, d’une meilleure route provenant d’une autre source ou d’une autre règle d’éligibilité. Ne résous pas automatiquement le problème en ajoutant `next-hop-self` : vérifie d’abord le modèle de routage et le chemin attendu.


## 9. Laboratoires pratiques

Tous les laboratoires sont destinés à un simulateur ou à une maquette contrôlée. Les préfixes de documentation ne doivent pas être annoncés sur Internet.

### Laboratoire 1 — Construire un route reflector

**But :** remplacer un petit full mesh iBGP par un RR.

1. Configure un AS privé de test avec trois routeurs internes.
2. Vérifie les sessions full mesh et note le nombre de sessions.
3. Reconfigure un routeur comme RR et les deux autres comme clients.
4. Annonce un préfixe depuis une session eBGP de laboratoire ou une route d’exemple validée.
5. Vérifie sa réception sur l’autre client et examine les attributs liés à la réflexion.
6. Teste la perte du RR et observe le comportement de routage.

**Livrable :** schéma avant/après, sortie de la table BGP et explication du chemin de la route.

### Laboratoire 2 — Marquer des routes par communauté

1. Crée une communauté opérateur de test et documente sa signification.
2. Attache-la aux routes reçues d’un client simulé.
3. Vérifie que la communauté apparaît dans la table BGP.
4. Utilise-la dans une politique de sortie vers un autre voisin de test.
5. Prouve qu’une route attendue est marquée et qu’une route non autorisée reste filtrée.

**Critère :** ne suppose pas le résultat depuis la seule configuration ; vérifie les routes et annonces réellement observées.

### Laboratoire 3 — Agréger quatre /24

1. Prépare les quatre /24 indiqués dans le schéma 5.
2. Vérifie l’existence des routes spécifiques dans la RIB.
3. Configure l’agrégat correspondant selon la plateforme.
4. Vérifie le résumé annoncé et les routes plus spécifiques.
5. Retire un préfixe spécifique dans le laboratoire et observe le comportement du résumé.
6. Documente la protection retenue contre les destinations absentes.

### Laboratoire 4 — Comparer LOCAL_PREF et AS_PATH Prepending

1. Fais annoncer le même préfixe à travers deux chemins de laboratoire.
2. Observe les attributs sur les deux routeurs de l’AS destinataire.
3. Modifie seulement LOCAL_PREF dans l’AS qui choisit son chemin sortant.
4. Restaure puis teste une annonce avec AS_PATH prepending côté origine.
5. Compare le chemin sortant local et le chemin choisi par un AS distant de test.

**Conclusion attendue :** ces leviers ont des portées différentes et ne garantissent pas les décisions de politique d’un autre AS.

### Laboratoire 5 — Appliquer une politique fermée eBGP

1. Définis les préfixes attendus, les préfixes interdits et le rôle du voisin.
2. Crée une politique d’import et une politique d’export séparées.
3. Attache explicitement les deux politiques au voisin de test.
4. Vérifie les routes reçues, acceptées et annoncées.
5. Introduis un préfixe supplémentaire dans le réseau de test et confirme qu’il n’est pas annoncé si la politique doit le bloquer.

### Laboratoire 6 — Valider les états RPKI

Dans un environnement qui dispose d’un cache RPKI et de la fonction d’origin validation :

1. identifie les routes de test et les ROA qui les couvrent ;
2. affiche les états Valid/Invalid/NotFound selon les commandes de la plateforme ;
3. vérifie la politique appliquée à chaque catégorie ;
4. utilise une annonce de laboratoire adaptée pour illustrer chaque état ;
5. consigne pourquoi un état de validation ne décrit pas toute la chaîne AS_PATH.

Ne crée ni ne modifie de ROA de production pour les besoins du laboratoire.

### Laboratoire 7 — Route BGP reçue, mais non installée

1. construis un cas où le préfixe apparaît dans BGP mais n’est pas retenu dans la RIB ;
2. relève best path, NEXT_HOP, route de résolution et éventuelles routes concurrentes ;
3. forme une hypothèse unique ;
4. corrige la cause dans la maquette et prouve la modification du résultat ;
5. vérifie la connectivité de bout en bout.

### Laboratoire 8 — Incident de fuite de routes simulé

1. établis un AS client, un AS transit et un AS pair dans une maquette isolée ;
2. note les préfixes qui doivent être exportés selon chaque relation ;
3. injecte un préfixe non autorisé dans le réseau de laboratoire ;
4. vérifie si les politiques empêchent son export ;
5. examine le compteur de routes, les annonces sortantes et les logs ;
6. corrige la politique et confirme le retrait de l’annonce incorrecte.


## 10. Checklist opérationnelle d’un changement BGP

### Avant le changement

- [ ] Sauvegarder la configuration et enregistrer la version logicielle.
- [ ] Identifier les voisins touchés, leur rôle et les familles d’adresses activées.
- [ ] Capturer `summary`, routes BGP pertinentes, RIB et annonces sortantes.
- [ ] Documenter les préfixes attendus en entrée et en sortie.
- [ ] Définir les critères de réussite, l’alerte et le retour arrière.

### Pendant le changement

- [ ] Modifier une politique ou un attribut à la fois.
- [ ] Vérifier la session et les logs avant de conclure.
- [ ] Examiner les routes reçues, sélectionnées et annoncées.
- [ ] Surveiller le nombre de préfixes et les changements de best path.
- [ ] Ne pas retirer le processus entier lorsqu’un changement de politique ciblé suffit.

### Après le changement

- [ ] Comparer les routes installées aux routes attendues.
- [ ] Vérifier les annonces sortantes par voisin.
- [ ] Tester le chemin aller et le chemin retour.
- [ ] Valider les services applicatifs concernés.
- [ ] Archiver les sorties de commandes, captures et la chronologie.


## 11. Évaluation corrigée

### Questions

1. Pourquoi un RR peut-il réduire le nombre de sessions mais devenir un composant logique important ?
2. Quelle est la différence entre une communauté et une politique ?
3. Pourquoi `65020:100` n’a-t-il pas de signification universelle ?
4. Quels préfixes IPv4 sont couverts par `198.51.100.0/22` dans le schéma ?
5. Pourquoi l’agrégation peut-elle créer un problème de trou noir ?
6. Quelle est la différence entre LOCAL_PREF et MED ?
7. Pourquoi AS_PATH prepending ne garantit-il pas le chemin d’entrée ?
8. Quelle est la fonction d’une politique d’import et d’une politique d’export ?
9. Que spécifie RFC 8212 lorsque les politiques eBGP explicites sont absentes ?
10. Quels éléments sont comparés dans une validation d’origine RPKI ?
11. Pourquoi RPKI `Valid` ne prouve-t-il pas que l’AS_PATH entier est authentique ?
12. Pourquoi un NEXT_HOP inaccessible peut-il rendre une route non utilisable ?
13. Que faut-il examiner si une route apparaît dans la table BGP mais pas dans la RIB ?
14. Pourquoi faut-il vérifier les routes annoncées au voisin au lieu de se fier uniquement à la configuration ?
15. Quels indicateurs peuvent aider à détecter une fuite de routes ?

### Corrigés

**1.** Le RR remplace de nombreuses sessions pair-à-pair par des sessions client-RR, mais les routes et leur propagation dépendent alors de sa topologie, sa disponibilité et ses règles de réflexion. Il faut éviter le point de défaillance unique et contrôler la redondance du RR.

**2.** La communauté est une étiquette d’attribut portée par la route ; la politique est la règle qui décide quoi faire quand cette étiquette est présente.

**3.** Les valeurs de communauté sont interprétées par le système qui les définit. Sans convention opérateur, le code n’impose aucune action standard.

**4.** Il couvre `198.51.100.0/24`, `198.51.101.0/24`, `198.51.102.0/24` et `198.51.103.0/24` : quatre réseaux contigus dans un bloc /22 aligné.

**5.** Le résumé peut rester annoncé alors qu’un composant est absent. Le trafic correspondant atteint la frontière qui annonce l’agrégat mais peut ne pas trouver de destination valide. Une conception de rejet et un retrait cohérent du résumé peuvent être nécessaires selon la configuration.

**6.** LOCAL_PREF influence le choix interne du chemin sortant dans un AS. MED est une indication de préférence d’entrée envoyée à un AS voisin, avec une comparaison dépendante des règles et de la configuration.

**7.** Un AS distant peut préférer LOCAL_PREF, des communautés ou une autre politique avant de considérer la longueur d’AS_PATH. Le prepend n’est qu’une influence, pas une commande à distance.

**8.** La politique d’import contrôle les routes qu’un routeur accepte de considérer depuis un voisin ; la politique d’export contrôle les routes qu’il annonce à ce voisin.

**9.** RFC 8212 définit un comportement fermé : sans politique d’import explicite, les routes eBGP ne sont pas éligibles au processus de décision ; sans politique d’export explicite, elles ne doivent pas être annoncées, sous réserve des options et du comportement effectif de l’implémentation.

**10.** La validation compare le préfixe, la longueur maximale autorisée et l’ASN d’origine avec les ROA validés applicables.

**11.** RPKI origin validation concerne l’autorisation d’originer un préfixe. Elle ne fournit pas une authentification cryptographique complète de chaque AS de l’AS_PATH.

**12.** BGP peut connaître la route, mais la résolution du prochain saut échoue : le routeur ne dispose alors pas d’un chemin transférable vers le next hop.

**13.** Examiner les chemins candidats, la politique d’import, l’éligibilité, le best path, la résolution du next hop et les routes concurrentes dans la RIB.

**14.** La configuration définit une intention ; une erreur de politique, une famille d’adresses inactive ou le comportement de la plateforme peut faire différer les annonces réelles.

**15.** Les filtres de préfixes, les compteurs de routes, les alertes de variations inhabituelles, les logs de politiques et les annonces sortantes comparées à un inventaire attendu.


## 12. Glossaire ciblé

| Terme | Signification opérationnelle |
|---|---|
| Adj-RIB-In | Vue des routes reçues d’un voisin, selon les capacités de l’implémentation |
| Adj-RIB-Out | Routes préparées pour l’annonce à un voisin |
| AS_PATH | Séquence d’AS indiquant le chemin d’origine annoncé |
| Best path | Chemin sélectionné par la procédure de décision BGP locale |
| Community | Étiquette BGP définie par une convention et interprétée par une politique |
| eBGP / iBGP | Session entre AS différents / au sein du même AS |
| Large Community | Attribut de communauté utilisant trois champs d’entiers 32 bits |
| LOCAL_PREF | Préférence interne d’un chemin dans un AS |
| MED | Indication de préférence d’entrée donnée à un voisin |
| NEXT_HOP | Adresse du prochain saut nécessaire à la résolution du chemin |
| Route reflector | Speaker iBGP qui réfléchit certaines routes selon les règles prévues |
| ROA / RPKI | Autorisation signée liant un préfixe, une longueur et un ASN d’origine autorisé |
| Route leak | Propagation d’une route en dehors de l’intention de la politique |


## 13. Références techniques

Les exemples de configuration sont pédagogiques. Pour un déploiement réel, sélectionne le guide de la version et de la plateforme utilisées.

- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : https://www.rfc-editor.org/rfc/rfc4271.html
- **RFC 4456 — BGP Route Reflection** : https://www.rfc-editor.org/rfc/rfc4456.html
- **RFC 1997 — BGP Communities Attribute** : https://www.rfc-editor.org/rfc/rfc1997.html
- **RFC 4360 — BGP Extended Communities Attribute** : https://www.rfc-editor.org/rfc/rfc4360.html
- **RFC 8092 — BGP Large Communities Attribute** : https://www.rfc-editor.org/rfc/rfc8092.html
- **RFC 8212 — Default eBGP Route Propagation Behavior without Policies** : https://www.rfc-editor.org/rfc/rfc8212.html
- **RFC 7908 — Problem Definition and Classification of BGP Route Leaks** : https://www.rfc-editor.org/rfc/rfc7908.html
- **RFC 9582 — A Profile for Route Origin Authorizations (ROAs)** : https://www.rfc-editor.org/rfc/rfc9582.html
- **Cisco — BGP Configuration Guide** : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software/products-installation-and-configuration-guides-list.html

## Préparation au niveau Expert

Le niveau Expert partira des acquis de ce cours et approfondira les stratégies multi-fournisseurs, le contrôle fin d’ingénierie de trafic, la résilience des route reflectors, la sécurité du plan de routage, l’automatisation des politiques et le diagnostic de fuites ou d’instabilité à grande échelle.
