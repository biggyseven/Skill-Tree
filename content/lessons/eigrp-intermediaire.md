# EIGRP — Niveau Intermédiaire

**Durée indicative :** 5 à 7 heures avec les laboratoires  
**Prérequis :** maîtriser `eigrp-debutant.md` : voisinage, AS EIGRP, paquets, métrique composite, DUAL, successeur, feasible successor, FD/RD, tables de voisins/topologie et vérifications de base.  
**Environnement recommandé :** Cisco IOS/IOS XE ou un simulateur qui supporte les fonctions EIGRP requises ; Packet Tracer peut ne pas implémenter toutes les variantes. Un laboratoire isolé est obligatoire pour les tests de redistribution, de SIA et de modification des K-values.

Ce cours prolonge le niveau Débutant. On ne reprend pas pas à pas les bases du protocole : on les réutilise pour concevoir, configurer et dépanner des scénarios plus riches. Les sujets centraux sont le résumé de routes, le partage de charge à coût inégal avec `variance`, le mode nommé, les fonctions EIGRP stub, la redistribution contrôlée et les requêtes diffusées.

> **Cadre technique :** EIGRP est documenté dans la RFC 7868, une spécification informative et non une norme Internet Standards Track. Les commandes montrées sont des exemples Cisco IOS/IOS XE ; les possibilités et la syntaxe varient selon la version, le matériel et le mode classique/nommé. Les préfixes de documentation des exemples ne doivent pas être annoncés sur Internet.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- planifier et vérifier un résumé EIGRP sans masquer un réseau nécessaire ;
- expliquer pourquoi `variance` exige aussi le respect de la condition de faisabilité ;
- calculer les candidats au partage de charge et distinguer installation de routes et distribution réelle du trafic ;
- reconnaître la hiérarchie du mode nommé et transposer prudemment une configuration ;
- utiliser EIGRP stub pour caractériser un routeur de branche ;
- concevoir une redistribution entre EIGRP et OSPF avec métriques d’amorçage, filtres et tags anti-boucle ;
- suivre une computation ACTIVE et diagnostiquer des symptômes SIA ;
- dépanner en séparant voisinage, table topologique, RIB, prochain saut et service applicatif.

## Comment lire les SVG

Les huit schémas sont intégrés directement dans le Markdown. Les chemins et les valeurs sont légendés ; les marqueurs animés suivent les connecteurs qu’ils illustrent. Les animations ne sont pas une mesure réelle de la durée de convergence. Lorsque la précision des comparaisons est plus importante que le mouvement, un bloc peut rester statique.


## 1. Architecture de distribution EIGRP et conception de résumé

Un réseau de campus ou de succursales peut contenir de nombreux LAN. Les routeurs annoncent des préfixes à leurs voisins EIGRP, et les administrateurs peuvent choisir d’annoncer un préfixe résumé à une frontière appropriée. Contrairement à OSPF, EIGRP ne divise pas le domaine en aires ; il est donc incorrect d’appeler automatiquement un routeur de résumé « ABR ».

### Schéma 1 — Topologie et point de résumé

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 510" role="img" aria-label="Architecture EIGRP : topologie et frontière de résumé" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="510" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Architecture EIGRP : topologie et frontière de résumé</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les liaisons, LAN et préfixes sont explicités ; une route résumée représente plusieurs réseaux.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="145" width="170" height="72" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="135.0" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-BRANCH</text><text x="135.0" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">EIGRP AS 100</text><rect x="390" y="145" width="180" height="72" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="480.0" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-DIST</text><text x="480.0" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">summary boundary</text><rect x="735" y="145" width="170" height="72" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="820.0" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-CORE</text><text x="820.0" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">EIGRP AS 100</text><path d="M 220 181 L 390 181" fill="none" stroke="#45c7f5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="305" y="137" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="700">10.0.12.0/30</text><path d="M 570 181 L 735 181" fill="none" stroke="#45c7f5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="652" y="137" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="700">10.0.23.0/30</text><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 220 181 L 390 181" dur="2.3s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 570 181 L 735 181" dur="2.3s" begin="1.1s" repeatCount="indefinite"/>
</circle><path d="M 135 217 L 135 265 L 145 265 L 145 294" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="45" y="294" width="200" height="72" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="145.0" y="320" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">LAN local</text><text x="145.0" y="341" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">10.20.10.0/24</text><text x="480" y="254" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Exemple d’agrégation derrière R-DIST</text><rect x="280" y="280" width="140" height="54" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="350.0" y="306" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">10.10.0.0/24</text><text x="350.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">LAN / VLAN</text><path d="M 480 217 L 480 244 L 350 244 L 350 280" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="445" y="280" width="140" height="54" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="515.0" y="306" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">10.10.1.0/24</text><text x="515.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">LAN / VLAN</text><path d="M 480 217 L 480 244 L 515 244 L 515 280" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="610" y="280" width="140" height="54" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="680.0" y="306" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">10.10.2.0/24</text><text x="680.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">LAN / VLAN</text><path d="M 480 217 L 480 244 L 680 244 L 680 280" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="775" y="280" width="140" height="54" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="845.0" y="306" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">10.10.3.0/24</text><text x="845.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">LAN / VLAN</text><path d="M 480 217 L 480 244 L 845 244 L 845 280" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="115" y="405" width="730" height="55" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="480.0" y="431" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">R-DIST peut annoncer 10.10.0.0/22 vers l’amont</text><text x="480.0" y="452" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">À condition que l’agrégat couvre exactement les préfixes prévus</text><text x="480" y="482" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">EIGRP n’a pas d’aires : on parle ici de routeur frontière / point de résumé, pas d’ABR OSPF.</text>
</svg>
</div>

Lecture : R-DIST reçoit les réseaux internes et peut annoncer une route agrégée vers R-CORE. EIGRP ne possède pas le concept d’aire d’OSPF : R-DIST est ici un routeur de distribution qui applique un résumé. Le résumé annoncé doit correspondre exactement au plan d’adressage ; les préfixes utilisent des blocs de documentation.

### 1.1. Quand utiliser un résumé ?

Le résumé est utile si les préfixes forment un bloc contigu cohérent et si l’organisation du réseau permet de représenter ce bloc sans annoncer une destination qui ne doit pas être considérée comme accessible. Il réduit le nombre d’entrées apprises ailleurs et peut réduire le nombre de changements visibles au-delà de la frontière du résumé.

Mais un résumé cache aussi de l’information détaillée. Si un réseau spécifique disparaît, l’amont peut continuer à connaître l’agrégat. Il faut donc comprendre ce qu’il advient du trafic destiné au sous-préfixe absent.

### 1.2. Vérifier le bloc d’agrégation

Les quatre préfixes suivants :

- `10.10.0.0/24`
- `10.10.1.0/24`
- `10.10.2.0/24`
- `10.10.3.0/24`

forment le résumé `10.10.0.0/22`. Le `/22` couvre précisément 10.10.0.0 à 10.10.3.255. Il ne couvre pas `10.10.4.0/24`.

Avant d’activer un résumé, documente les routes couvertes, les routes qui doivent rester spécifiques, les emplacements de rejet et les conséquences d’une perte de sous-préfixe.

### 1.3. Exemple de résumé Cisco IOS

Une commande classique possible est configurée sur l’interface qui annonce le résumé. La syntaxe exacte varie selon la plateforme et le mode EIGRP :

```cisco
interface GigabitEthernet0/1
 ip summary-address eigrp 100 10.10.0.0 255.255.252.0
```

Ne copie pas cet exemple sans vérifier que l’interface est bien celle où le résumé doit être annoncé et que les quatre préfixes réels appartiennent au bloc. Le comportement de route de rejet vers Null0, les préférences et les détails d’affichage doivent être vérifiés sur la version utilisée.

## 2. Résumé, route Null0 et prévention des trous noirs

### Schéma 4 — Résumé et route Null0

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Agrégation EIGRP et risque de trou noir" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Agrégation EIGRP et risque de trou noir</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le Null0 est une route de rejet de dernier recours ; il ne remplace pas les routes spécifiques actives.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="135" width="180" height="72" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="140.0" y="161" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">LAN /24 × 4</text><text x="140.0" y="182" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">10.10.0.0 à 10.10.3.0</text><rect x="365" y="135" width="210" height="72" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="470.0" y="161" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-DIST</text><text x="470.0" y="182" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Point de résumé</text><rect x="730" y="135" width="180" height="72" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="820.0" y="161" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-CORE</text><text x="820.0" y="182" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Reçoit /22</text><path d="M 230 171 L 365 171" fill="none" stroke="#4ade80" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 575 171 L 730 171" fill="none" stroke="#fbbf24" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="652" y="132" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">10.10.0.0/22</text><circle r="5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 575 171 L 730 171" dur="2.4s" begin="0s" repeatCount="indefinite"/>
</circle><rect x="365" y="285" width="210" height="70" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="470.0" y="311" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Route de résumé</text><text x="470.0" y="332" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">10.10.0.0/22</text><rect x="365" y="385" width="210" height="66" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/><text x="470.0" y="411" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">Null0 (discard)</text><text x="470.0" y="432" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Évite une boucle pour le trafic sans route plus précise</text><path d="M 470 207 L 470 285" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 470 355 L 470 385" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="620" y="315" text-anchor="start" fill="#edf4fb" font-size="12" font-weight="700">Si 10.10.2.0/24 disparaît</text><text x="620" y="337" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400">l’agrégat peut encore exister ;</text><text x="620" y="356" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400">un trou noir est possible si le trafic</text><text x="620" y="375" text-anchor="start" fill="#adbdcf" font-size="11" font-weight="400">arrive sans route plus précise.</text><text x="480" y="477" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="600">Le résumé doit être aligné sur le plan d’adressage et testé lors de la perte d’un sous-préfixe.</text>
</svg>
</div>

Un résumé peut rester annoncé alors qu’un sous-préfixe n’est plus présent. Une route Null0 associée à l’agrégat peut éviter que des paquets non couverts par une route plus précise rebouclent ailleurs ; elle provoque cependant un rejet intentionnel pour les destinations qui ne disposent pas de route plus spécifique. Il faut simuler la perte d’un préfixe pour vérifier le résultat.

### 2.1. Pourquoi un agrégat peut masquer une panne

Suppose que le cœur n’apprenne plus le préfixe `10.10.2.0/24`, mais continue à recevoir `10.10.0.0/22` depuis la distribution. Pour le cœur, l’agrégat semble toujours annoncé. Un paquet vers une adresse du préfixe disparu peut donc être dirigé vers la distribution, puis rejeté si aucune route plus précise n’existe.

Ce comportement n’est pas automatiquement une erreur : c’est parfois ce qui évite les boucles de routage. Le risque apparaît lorsque l’administrateur pense que l’agrégat garantit l’accès à toutes les destinations couvertes, même si une destination est absente.

### 2.2. Plan de validation d’un résumé

1. Liste les routes spécifiques qui appartiennent à l’agrégat.
2. Vérifie la route résumé et l’interface sur laquelle elle est annoncée.
3. Collecte la table de routage avant la modification.
4. Perds volontairement un sous-préfixe dans le laboratoire.
5. Observe si le résumé continue d’être annoncé.
6. Envoie un test vers le préfixe retiré et vérifie où le paquet est abandonné.
7. Restaure la route et confirme le retour du trafic.

Ne teste pas cette séquence sur une agrégation de production sans fenêtre de changement : un résumé trop large peut masquer d’autres réseaux manquants.


## 3. Partage de charge à coût inégal avec `variance`

EIGRP peut installer plusieurs chemins de coûts différents lorsque plusieurs conditions sont respectées. Il faut distinguer trois décisions :

1. **Faisabilité :** le chemin est-il admissible sans boucle selon la condition DUAL ?
2. **Variance :** son coût total est-il inférieur ou égal au meilleur coût multiplié par le facteur configuré ?
3. **Forwarding :** si plusieurs routes sont installées dans la RIB, comment la plateforme distribue-t-elle le trafic entre elles ?

`variance` n’annule pas la condition de faisabilité. Une route plus chère qui ne satisfait pas la condition de faisabilité ne doit pas être ajoutée au partage de charge simplement parce que sa métrique est dans le seuil numérique.

### Schéma 2 — Variance et chemins à coût inégal

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Variance : partager la charge à coût inégal" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Variance : partager la charge à coût inégal</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Un chemin alternatif doit respecter la faisabilité ET le seuil variance × meilleure métrique.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="205" width="145" height="74" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="117.5" y="231" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R1</text><text x="117.5" y="252" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">FD de référence = 100</text><rect x="340" y="125" width="160" height="75" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="420.0" y="151" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R2</text><text x="420.0" y="172" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">RD = 80</text><rect x="340" y="310" width="160" height="75" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="420.0" y="336" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R3</text><text x="420.0" y="357" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">RD = 90</text><rect x="735" y="205" width="175" height="74" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="822.5" y="231" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">D</text><text x="822.5" y="252" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">préfixe destination</text><path d="M 190 222 L 250 222 L 250 162 L 340 162" fill="none" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 500 162 L 610 162 L 610 222 L 735 222" fill="none" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 190 260 L 250 260 L 250 348 L 340 348" fill="none" stroke="#fbbf24" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 500 348 L 610 348 L 610 260 L 735 260" fill="none" stroke="#fbbf24" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="265" y="145" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">coût lien R1–R2 = 20</text><text x="265" y="332" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700">coût lien R1–R3 = 50</text><text x="620" y="145" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">total = 20 + 80 = 100</text><text x="620" y="332" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700">total = 50 + 90 = 140</text><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 190 222 L 250 222 L 250 162 L 340 162 L 500 162 L 610 162 L 610 222 L 735 222" dur="3.2s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 190 260 L 250 260 L 250 348 L 340 348 L 500 348 L 610 348 L 610 260 L 735 260" dur="3.8s" begin="1s" repeatCount="indefinite"/>
</circle><rect x="55" y="420" width="400" height="58" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="255.0" y="446" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Chemin principal : métrique 100</text><text x="255.0" y="467" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">RD 80 &lt; FD 100</text><rect x="505" y="420" width="400" height="58" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="705.0" y="446" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Chemin alternatif : métrique 140</text><text x="705.0" y="467" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">RD 90 &lt; FD 100 ; variance 2 ⇒ seuil 200</text>
</svg>
</div>

Calcul illustratif : le chemin via R2 a un coût total 20 + 80 = 100 ; via R3, 50 + 90 = 140. Avec variance 2, le seuil métrique est 2 × 100 = 200. La route via R3 respecte à la fois le seuil et la condition de faisabilité (RD 90 < FD 100). Le fait de configurer variance seul ne rend pas admissible un chemin qui échoue à la condition de faisabilité.

### 3.1. Le calcul du seuil

Si le meilleur coût EIGRP d’une destination est 100 et que `variance 2` est configuré, la borne métrique est :

\[
100 \times 2 = 200
\]

Un chemin alternatif dont le coût total est 140 respecte cette borne. Il ne sera toutefois admissible que s’il passe aussi le test de faisabilité et les autres contrôles de validité. Les comparaisons doivent employer les métriques réellement affichées par EIGRP, pas des chiffres improvisés à partir du débit nominal.

### 3.2. Configuration illustratrice

```cisco
router eigrp 100
 variance 2
```

Le facteur par défaut est 1 dans les configurations Cisco usuelles, ce qui correspond au partage à coût égal. Une valeur supérieure permet de prendre en compte certains chemins de métrique plus élevée, si la faisabilité est satisfaite.

Avant d’appliquer la commande, confirme qu’il existe un besoin réel de partage, que les chemins alternatifs sont stables et que leurs capacités sont appropriées. Un chemin de plus faible qualité qui participe au transfert peut augmenter le délai ou créer une asymétrie.

### 3.3. Installation des routes et distribution du trafic

EIGRP sélectionne et installe les routes admissibles ; la distribution des paquets est effectuée par le mécanisme de transfert du routeur. Le trafic ne sera pas nécessairement réparti équitablement entre les liens. L’algorithme de hachage et les politiques de `traffic-share` disponibles dépendent du système.

Mesure les flux réels avec plusieurs conversations de test. Un unique flux peut ne pas utiliser tous les chemins en parallèle. Vérifie aussi le comportement quand un chemin alternatif tombe : l’installation de plusieurs routes ne supprime pas la nécessité de vérifier la convergence et la capacité restante.

## 4. Mode nommé EIGRP

Le mode nommé fournit une structure de configuration hiérarchique et peut prendre en charge les familles d’adresses et les options associées selon la plateforme. Il ne faut pas supposer qu’une commande du mode classique existe au même niveau dans le mode nommé.

### Schéma 3 — Mode nommé : hiérarchie de configuration

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="EIGRP nommé : lire la hiérarchie de configuration" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">EIGRP nommé : lire la hiérarchie de configuration</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">La syntaxe dépend d’IOS/IOS XE et du type de configuration ; les sous-modes ont des responsabilités distinctes.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="70" y="115" width="820" height="58" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="480.0" y="141" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">router eigrp CAMPUS</text><text x="480.0" y="162" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Déclare une configuration nommée ; cela seul ne crée pas encore l’AF active.</text><path d="M 480 173 L 480 205" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="130" y="205" width="700" height="65" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="480.0" y="231" text-anchor="middle" fill="#edf4fb" font-size="15" font-weight="700">address-family ipv4 unicast autonomous-system 100</text><text x="480.0" y="252" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Famille IPv4 + AS de routage</text><path d="M 480 270 L 480 300 L 250 300 L 250 326" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 480 300 L 710 300 L 710 326" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="55" y="326" width="390" height="76" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="250.0" y="352" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">af-interface default</text><text x="250.0" y="373" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Paramètres d’interface</text><rect x="515" y="326" width="390" height="76" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="710.0" y="352" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">topology base</text><text x="710.0" y="373" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Options topologiques : variance, redistribution selon AF</text><path d="M 250 402 L 250 426" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 710 402 L 710 426" fill="none" stroke="#c4b5fd" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="55" y="426" width="390" height="54" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="250.0" y="452" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">passive-interface / hello-interval</text><text x="250.0" y="473" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Exemple de paramètres d’interface</text><rect x="515" y="426" width="390" height="54" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="710.0" y="452" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">variance / route-map / metric</text><text x="710.0" y="473" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Vérifier la syntaxe prise en charge</text>
</svg>
</div>

Les blocs décrivent une structure de configuration, pas des chemins de paquets. En mode nommé, la famille d’adresses, l’AS et les sous-modes de topologie/interface ont des rôles distincts. Vérifie la syntaxe sur l’image IOS/IOS XE ; les capacités et commandes ne sont pas identiques sur toutes les plateformes.

### 4.1. Lire la hiérarchie avant de configurer

- Le nom du processus EIGRP sert à identifier la configuration nommée.
- `address-family` associe la configuration à une famille d’adresses et à un AS.
- Le sous-mode `af-interface` contient des paramètres d’interface tels que `passive-interface` ou certains paramètres de temporisation.
- Le sous-mode de topologie organise certaines options comme les stratégies de métrique ou la redistribution, selon la plateforme.

Cette hiérarchie est conceptuelle ; l’ensemble exact des sous-commandes dépend de l’IOS/IOS XE et des fonctionnalités activées. Vérifie les commandes prises en charge dans l’aide de l’équipement.

### 4.2. Exemple simplifié de syntaxe nommée

```cisco
router eigrp CAMPUS
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.0 0.0.255.255
  af-interface default
   passive-interface
  exit-af-interface
  af-interface GigabitEthernet0/1
   no passive-interface
  exit-af-interface
  topology base
   variance 2
  exit-af-topology
 exit-address-family
```

Cet exemple illustre l’organisation du mode nommé ; il ne constitue pas une configuration universelle. La syntaxe exacte des interfaces, les commandes de topologie et les fonctions disponibles doivent être vérifiées sur la plateforme. La politique doit laisser les interfaces de transit nécessaires actives tout en empêchant les adjacences indésirables sur les LAN d’utilisateurs.

### 4.3. Migrer du mode classique au mode nommé

Ne configure pas les deux formes à l’aveugle en pensant que l’une remplace automatiquement l’autre. Pour une migration contrôlée :

1. sauvegarde la configuration ;
2. documente les interfaces participantes, l’AS, les filtres et les K-values ;
3. vérifie les fonctions prises en charge par la version ;
4. prépare un plan de migration et un retour arrière ;
5. effectue le changement dans une maquette ;
6. compare les voisins, les routes, les métriques et les tests applicatifs.


## 5. EIGRP stub et topologies de branche

La fonction EIGRP stub permet de signaler qu’un routeur est une branche et qu’il ne doit pas être traité comme un transit général. Elle peut réduire certaines requêtes diffusées vers des routes que le routeur stub ne dessert pas. Ce mécanisme n’est pas identique aux aires stub d’OSPF.

### Schéma 6 — EIGRP stub en branche

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 485" role="img" aria-label="EIGRP stub : limiter les attentes de transit" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="485" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">EIGRP stub : limiter les attentes de transit</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Un routeur de branche annonce les classes de routes prévues ; il ne doit pas être conçu comme un transit général.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="55" y="160" width="170" height="74" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="140.0" y="186" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-HUB</text><text x="140.0" y="207" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">EIGRP core</text><rect x="390" y="160" width="180" height="74" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="480.0" y="186" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-DIST</text><text x="480.0" y="207" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Routeur intermédiaire</text><rect x="725" y="160" width="180" height="74" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="815.0" y="186" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-BRANCH</text><text x="815.0" y="207" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">EIGRP stub</text><path d="M 225 197 L 390 197" fill="none" stroke="#45c7f5" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="307" y="151" text-anchor="middle" fill="#45c7f5" font-size="11" font-weight="700">Transit</text><path d="M 570 197 L 725 197" fill="none" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="648" y="151" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">Lien vers la branche</text><circle r="4.5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 225 197 L 390 197" dur="2.5s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 570 197 L 725 197" dur="2.5s" begin="1s" repeatCount="indefinite"/>
</circle><rect x="690" y="290" width="250" height="80" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="815.0" y="316" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">Préfixes annoncés</text><text x="815.0" y="337" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Connected / summary selon config</text><path d="M 815 234 L 815 290" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="35" y="300" width="290" height="82" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="180.0" y="326" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Avantage</text><text x="180.0" y="347" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Le voisin apprend que la branche est stub ; certaines requêtes inutiles sont limitées.</text><rect x="345" y="300" width="290" height="82" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="490.0" y="326" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Limite</text><text x="490.0" y="347" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Stub ne remplace ni un plan de routes ni les filtres d’annonce.</text><text x="480" y="430" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">EIGRP stub n’est pas un « area stub » OSPF : c’est une indication de rôle de routeur dans EIGRP.</text><text x="480" y="453" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Les types de routes annoncées et la syntaxe dépendent du mode EIGRP et de la plateforme.</text>
</svg>
</div>

Le mode stub annonce aux voisins le rôle de routeur de bord de branche et peut limiter certaines requêtes diffusées vers des chemins qu’il ne dessert pas. Ce n’est pas une aire stub comme dans OSPF. Les familles de routes annoncées (connected, summary, static, redistributed, selon la syntaxe) doivent être définies explicitement.

### 5.1. Quand envisager le mode stub

Le mode stub est adapté à certaines succursales qui n’ont qu’un lien logique vers le reste du domaine et ne servent pas de transit entre d’autres routeurs. Il faut cependant être sûr que le routeur n’est pas supposé relayer des routes externes ou des routes provenant d’autres voisins.

Dans la syntaxe classique IOS, une configuration courante peut ressembler à :

```cisco
router eigrp 100
 eigrp stub connected summary
```

Les options valides sont liées au mode, à la plateforme et à la version. Les types de routes annoncés doivent correspondre à la topologie réelle. Une branche configurée en stub ne doit pas être utilisée comme routeur de transit général simplement parce qu’elle possède un voisinage.

### 5.2. Stub ne signifie pas « aucune Query ne me parviendra jamais »

Interprète correctement le mécanisme : il s’agit d’une annonce de rôle qui permet aux voisins de limiter certaines requêtes et attentes. Les routes originées par le stub, les options sélectionnées et le comportement de la plateforme restent importants. Ne fonde pas la procédure de dépannage sur une phrase absolue telle que « un stub ne reçoit jamais de Query ».


## 6. Redistribution entre EIGRP et OSPF

La redistribution permet d’introduire des routes d’un protocole dans un autre. Elle est utile lors d’une migration, d’un réseau multi-protocoles ou d’une frontière administrative. Elle constitue aussi une zone de risque : sans contrôle, les routes peuvent être réinjectées, les métriques peuvent être inadaptées et des boucles peuvent apparaître.

### Schéma 5 — Redistribution et tags anti-boucle

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 495" role="img" aria-label="Redistribution bidirectionnelle avec tags anti-boucle" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="495" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Redistribution bidirectionnelle avec tags anti-boucle</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les tags marquent une route quand elle traverse le point de redistribution ; la politique opposée bloque son retour.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="155" width="205" height="78" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="147.5" y="181" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Domaine EIGRP</text><text x="147.5" y="202" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">AS 100 · routes internes</text><rect x="375" y="155" width="210" height="78" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="480.0" y="181" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-BORDER</text><text x="480.0" y="202" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Redistribution contrôlée</text><rect x="705" y="155" width="205" height="78" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="807.5" y="181" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Domaine OSPF</text><text x="807.5" y="202" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Area 0 · routes internes</text><path d="M 250 178 L 375 178" fill="none" stroke="#4ade80" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 585 178 L 705 178" fill="none" stroke="#c4b5fd" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="310" y="162" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">EIGRP → OSPF</text><text x="645" y="162" text-anchor="middle" fill="#c4b5fd" font-size="11" font-weight="700">OSPF → EIGRP</text><circle r="4.8" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 250 178 L 375 178 L 585 178 L 705 178" dur="3.6s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4.8" fill="#c4b5fd" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 705 211 L 585 211 L 375 211 L 250 211" dur="3.6s" begin="1.3s" repeatCount="indefinite"/>
</circle><rect x="40" y="295" width="430" height="115" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="255.0" y="321" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Sens EIGRP → OSPF</text><text x="255.0" y="342" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Tag 100 sur les routes injectées ; au retour OSPF → EIGRP, refuser tag 100.</text><rect x="490" y="295" width="430" height="115" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/><text x="705.0" y="321" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Sens OSPF → EIGRP</text><text x="705.0" y="342" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Tag 200 sur les routes injectées ; au retour EIGRP → OSPF, refuser tag 200.</text><text x="480" y="446" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="600">Les tags sont une convention locale de politique : choisis des valeurs documentées et filtre dans les deux directions.</text><text x="480" y="468" text-anchor="middle" fill="#fb7185" font-size="12" font-weight="600">Redistribution bidirectionnelle sans contrôle de boucle = risque de réinjection et de chemins instables.</text>
</svg>
</div>

La politique de tags doit être symétrique et explicite. Exemple de convention : tag 100 pour les routes importées d’EIGRP vers OSPF ; empêcher leur réimportation d’OSPF vers EIGRP. Tag 200 pour les routes importées d’OSPF vers EIGRP ; empêcher leur réimportation d’EIGRP vers OSPF. Le tag seul ne protège de rien sans filtre sur le chemin de retour.

### 6.1. Trois contrôles indispensables

**Métrique de départ.** Une route redistribuée doit recevoir les attributs ou métriques nécessaires au protocole destinataire. Selon la syntaxe classique, EIGRP peut exiger une métrique composite pour certaines routes injectées depuis un protocole qui ne fournit pas les mêmes composants.

**Filtrage des préfixes.** Définis exactement quels réseaux doivent traverser la frontière. Ne redistribue pas indistinctement toutes les routes statiques, connectées ou apprises.

**Tags anti-boucle.** Les tags doivent être associés à des politiques appliquées dans le sens inverse pour éviter qu’une route revienne à son protocole d’origine.

### 6.2. Exemple illustratif de tags

Convention de ce cours :

- tag `100` : routes injectées d’EIGRP vers OSPF ; à leur retour potentiel d’OSPF vers EIGRP, les bloquer ;
- tag `200` : routes injectées d’OSPF vers EIGRP ; à leur retour potentiel d’EIGRP vers OSPF, les bloquer.

Le numéro de tag est une convention locale. Il n’a aucune propriété anti-boucle par lui-même : c’est la route-map ou la politique qui compare le tag et rejette la route. Les commandes diffèrent selon le protocole, le mode de configuration et la plate-forme ; il faut vérifier les entrées de route-map, l’ordre des séquences et le comportement implicite en fin de liste.

### 6.3. Mise en œuvre dans un laboratoire

1. Construis un domaine EIGRP AS 100 et un domaine OSPF area 0, raccordés à un routeur de frontière.
2. Annonce un LAN de test dans chaque domaine.
3. Vérifie les routes avant toute redistribution.
4. Redistribue un seul sens avec une métrique explicitement définie.
5. Contrôle le préfixe résultant et ses attributs.
6. Ajoute les tags et les filtres du sens inverse.
7. Teste une route non autorisée et vérifie qu’elle n’est ni acceptée ni réannoncée.
8. Répète pour le second sens uniquement après validation du premier.

Une session ou une route présente ne suffit pas à prouver que la redistribution est correcte : inspecte la table, les tags, les filtres et la route retour.


## 7. DUAL en ACTIVE, QUERY/REPLY et SIA

Une computation diffusée peut être nécessaire lorsque le successeur devient inutilisable et qu’aucun feasible successor admissible n’est disponible. EIGRP interroge alors les voisins qui peuvent avoir une information utile et attend les réponses nécessaires pour terminer le calcul.

### Schéma 7 — QUERY / REPLY et SIA

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="Query / Reply : suivre la portée d’un calcul diffusé" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Query / Reply : suivre la portée d’un calcul diffusé</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les requêtes parcourent les voisins concernés ; une convergence sûre dépend des réponses attendues et de la topologie.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="165" width="160" height="76" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/><text x="125.0" y="191" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R1</text><text x="125.0" y="212" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Perte du successor</text><rect x="280" y="165" width="160" height="76" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="360.0" y="191" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R2</text><text x="360.0" y="212" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Voisin de transit</text><rect x="515" y="165" width="160" height="76" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="595.0" y="191" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R3</text><text x="595.0" y="212" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Voisin de transit</text><rect x="750" y="165" width="160" height="76" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="830.0" y="191" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R4</text><text x="830.0" y="212" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Branche distante</text><path d="M 205 184 L 280 184" fill="none" stroke="#fbbf24" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 440 184 L 515 184" fill="none" stroke="#fbbf24" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 675 184 L 750 184" fill="none" stroke="#fbbf24" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="242" y="156" text-anchor="middle" fill="#fbbf24" font-size="10.5" font-weight="700">QUERY</text><text x="477" y="156" text-anchor="middle" fill="#fbbf24" font-size="10.5" font-weight="700">QUERY</text><text x="712" y="156" text-anchor="middle" fill="#fbbf24" font-size="10.5" font-weight="700">QUERY</text><circle r="4.5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 205 184 L 280 184 L 440 184 L 515 184 L 675 184 L 750 184" dur="4s" begin="0s" repeatCount="indefinite"/>
</circle><path d="M 750 220 L 675 258 L 515 258 L 440 258 L 280 258 L 205 220" fill="none" stroke="#4ade80" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" opacity="1" stroke-dasharray="7 5"/><text x="480" y="250" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">REPLY remonte vers le demandeur</text><rect x="95" y="315" width="770" height="64" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/><text x="480.0" y="341" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">SIA / calcul qui reste ACTIVE</text><text x="480.0" y="362" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Si une réponse attendue tarde, vérifie perte de voisin, portée des Query, charge et version.</text><text x="480" y="425" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">Le schéma montre une propagation possible dans un domaine non-stub ; ce n’est pas une garantie que chaque route déclenche toutes ces Query.</text><text x="480" y="450" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="600">Horodate les événements et compare les voisins réellement interrogés avec la topologie observée.</text>
</svg>
</div>

Lorsqu’une route entre en ACTIVE, DUAL peut envoyer des Query à des voisins appropriés et attendre les Reply. Une réponse manquante ou retardée peut prolonger la computation et provoquer des symptômes SIA. Le schéma illustre un domaine de transit non-stub ; la portée exacte des messages dépend de la route, des voisins et des optimisations de l’implémentation.

### 7.1. Symptômes possibles

- Une destination reste dans l’état ACTIVE plus longtemps que prévu.
- Un routeur attend des réponses de voisins qui sont instables ou injoignables.
- Des adjacences se réinitialisent pendant une computation.
- Un changement de topologie produit une charge de contrôle importante.
- Le trafic se rétablit à un rythme différent de celui des adjacences.

Ces symptômes demandent une enquête, pas un ajustement immédiat de timers. Une SIA peut apparaître quand une réponse attendue ne revient pas dans les délais propres à l’implémentation, mais la cause réelle peut se trouver sur un lien distant, un voisin intermédiaire, une forte charge ou un défaut logiciel.

### 7.2. Méthode d’analyse

1. Repère le préfixe concerné et l’heure du passage à ACTIVE.
2. Collecte la table topologique sur le routeur qui calcule.
3. Identifie les voisins qui ont reçu une Query et ceux dont la réponse est attendue, selon les moyens de diagnostic disponibles.
4. Compare les événements de chaque routeur à la même heure.
5. Vérifie l’interface et la stabilité des adjacences intermédiaires.
6. N’ajuste les paramètres qu’après avoir établi la cause probable.
7. Répète le scénario en laboratoire et documente la portée de la computation.

L’outil et la sortie exacte dépendent de l’IOS/IOS XE. Certaines versions disposent de commandes de journalisation ou d’analyse de DUAL qui ne sont pas disponibles partout.


## 8. Diagnostic avancé par étapes

### Schéma 8 — Pipeline de diagnostic

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 470" role="img" aria-label="Diagnostic EIGRP : du voisin au service" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="470" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Diagnostic EIGRP : du voisin au service</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Une procédure en couches évite de corriger la métrique alors que la panne est ailleurs.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="145" width="165" height="75" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/><text x="117.5" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">1. Voisins</text><text x="117.5" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">show ... neighbors</text><rect x="225" y="145" width="165" height="75" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2.4"/><text x="307.5" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">2. Topologie</text><text x="307.5" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">routes / DUAL</text><rect x="415" y="145" width="165" height="75" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/><text x="497.5" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">3. RIB</text><text x="497.5" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">route installée ?</text><rect x="605" y="145" width="165" height="75" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="687.5" y="171" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">4. FIB / NH</text><text x="687.5" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">transfert / next-hop</text><rect x="795" y="145" width="130" height="75" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/><text x="860.0" y="171" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">5. Service</text><text x="860.0" y="192" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">test réel</text><path d="M 200 182 L 225 182" fill="none" stroke="#5d7189" stroke-width="3.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 390 182 L 415 182" fill="none" stroke="#5d7189" stroke-width="3.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 580 182 L 605 182" fill="none" stroke="#5d7189" stroke-width="3.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 770 182 L 795 182" fill="none" stroke="#5d7189" stroke-width="3.3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><circle r="4" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 200 182 L 225 182" dur="2.3s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4" fill="#c4b5fd" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 390 182 L 415 182" dur="2.3s" begin="0.5s" repeatCount="indefinite"/>
</circle><circle r="4" fill="#4ade80" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 580 182 L 605 182" dur="2.3s" begin="1s" repeatCount="indefinite"/>
</circle><circle r="4" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.5">
<animateMotion path="M 770 182 L 795 182" dur="2.3s" begin="1.5s" repeatCount="indefinite"/>
</circle><rect x="50" y="285" width="400" height="82" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/><text x="250.0" y="311" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Voisin absent</text><text x="250.0" y="332" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">AS, interface, subnet, K-values, auth, ACL, passive-interface</text><rect x="510" y="285" width="400" height="82" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/><text x="710.0" y="311" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Route/service absent</text><text x="710.0" y="332" text-anchor="middle" fill="#adbdcf" font-size="11.5" font-weight="400">RIB, prochain saut, route retour, filtrage et application</text><path d="M 117 220 L 117 254 L 250 254 L 250 285" fill="none" stroke="#fb7185" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 862 220 L 862 254 L 710 254 L 710 285" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="480" y="415" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Ne confonds jamais adjacence, route topologique, route installée et flux réellement fonctionnel.</text><text x="480" y="440" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Collecte une preuve à chaque étape avant de modifier la configuration.</text>
</svg>
</div>

Commence par la présence des voisins, puis compare la table topologique, la RIB, la résolution du prochain saut et le trafic réel. Un voisin stable ne garantit pas qu’un préfixe est annoncé, qu’un chemin est installé, ni que le service fonctionne.

### 8.1. Voisinage manquant

- Confirme l’interface, l’adresse et le masque.
- Vérifie l’AS EIGRP et les K-values.
- Vérifie les interfaces passives et la correspondance `network`.
- Inspecte les filtres, l’authentification et les journaux.
- Évite de modifier les métriques tant que l’adjacence ne fonctionne pas.

### 8.2. Voisinage présent, route absente

- Confirme que le préfixe existe sur son routeur d’origine.
- Vérifie les réseaux annoncés, les filtres et les résumés.
- Examine la table topologique et la route de chaque voisin.
- Vérifie l’état PASSIVE/ACTIVE et le chemin retenu par DUAL.
- Compare la table topologique et la RIB.

### 8.3. Route présente, trafic en échec

- Confirme le prochain saut et l’interface de sortie.
- Examine la route de retour et les politiques de filtrage.
- Vérifie si le résumé masque une route spécifique absente.
- Teste un service réel plutôt que de conclure à partir d’un seul ping.
- Vérifie la distribution de charge si plusieurs routes sont installées.


## 9. Laboratoires pratiques

Tous les laboratoires doivent être exécutés dans un simulateur ou une maquette contrôlée. N’expérimente pas avec la redistribution, la variance, les K-values ou les routes résumées sur un réseau de production sans fenêtre de changement et validation préalable.

### Laboratoire 1 — Résumé de quatre /24

1. Configure quatre LAN contigus : `10.10.0.0/24` à `10.10.3.0/24`.
2. Vérifie que les routes spécifiques existent.
3. Configure l’annonce du résumé `10.10.0.0/22` vers l’amont.
4. Contrôle les routes apprises par le routeur amont.
5. Retire un sous-préfixe dans le laboratoire.
6. Observe si le résumé reste annoncé et où le trafic destiné au sous-préfixe disparaît.
7. Restaure et documente les résultats.

**Livrable :** tableau avant/après, capture des routes, justification du traitement de route absente.

### Laboratoire 2 — Variance avec métriques contrôlées

1. Crée deux chemins vers le même préfixe.
2. Relève FD, RD et métrique totale de chaque chemin.
3. Vérifie la faisabilité avant d’activer la variance.
4. Configure `variance 2` sur le routeur approprié.
5. Vérifie les routes installées.
6. Mesure plusieurs flux de test pour voir comment la plateforme répartit le trafic.
7. Retire la variance et compare.

**Livrable :** calcul du seuil, justification de chaque chemin admis ou exclu.

### Laboratoire 3 — Mode nommé

1. Sauvegarde la configuration d’un laboratoire fonctionnel.
2. Lis la hiérarchie du mode nommé et les commandes prises en charge.
3. Prépare l’équivalent du processus d’exercice dans une maquette.
4. Configure uniquement les interfaces nécessaires.
5. Compare voisins, routes et métriques avant/après.
6. Vérifie que le LAN ne forme pas de voisinage indésirable.
7. Documente les différences de syntaxe et le retour arrière.

### Laboratoire 4 — EIGRP stub en branche

1. Construis un hub et deux branches, dont une petite branche sans rôle de transit.
2. Vérifie quelles routes la branche annonce avant d’activer le stub.
3. Active l’option stub adaptée à la plateforme.
4. Compare les routes, le rôle annoncé et les comportements de requête.
5. Vérifie qu’une branche ne sert pas involontairement de transit.
6. Restaure la configuration et explique la portée du mécanisme.

### Laboratoire 5 — Redistribution avec tags

1. Configure un domaine EIGRP et un domaine OSPF isolés.
2. Configure la redistribution d’un seul sens et une métrique connue.
3. Applique un tag aux routes injectées.
4. Vérifie leur présence et leur tag.
5. Applique une politique inverse qui rejette le tag correspondant.
6. Teste un préfixe qui ne doit pas traverser la frontière.
7. Répète pour l’autre sens en utilisant le second tag.
8. Prouve que les routes ne sont pas réinjectées.

### Laboratoire 6 — Investigation d’une route ACTIVE

1. Prépare une topologie avec trois routeurs ou plus et deux chemins vers une destination.
2. Collecte une référence de la table topologique.
3. Perds le successor dans le simulateur.
4. Observe la bascule si un feasible successor existe ; sinon recueille les informations sur les Query/Reply et les changements d’état.
5. Corrèle les événements aux routeurs concernés.
6. Explique pourquoi la route est restée ACTIVE ou pourquoi elle a basculé rapidement.

### Laboratoire 7 — Résumé qui masque un préfixe manquant

1. Configure un résumé et vérifie les routes spécifiques.
2. Retire temporairement un réseau plus spécifique.
3. Teste une destination de ce réseau depuis l’amont.
4. Identifie le point du rejet et la route sélectionnée.
5. Évalue si le résumé, le Null0 et les routes spécifiques produisent le comportement prévu.
6. Restaure l’état initial.

### Laboratoire 8 — Diagnostic de bout en bout

Introduis un seul défaut contrôlé : route retour absente, filtre, résumé incorrect ou service arrêté. Garde le voisinage EIGRP opérationnel. Utilise le pipeline du schéma 8 pour démontrer à quelle étape la panne apparaît.


## 10. Évaluation avec corrigés

**1. EIGRP possède-t-il des aires comme OSPF ?**  
Non. EIGRP utilise un domaine/AS de routage et peut appliquer des résumés, mais ne possède pas le modèle d’aires OSPF ni de routeur ABR.

**2. À quoi sert un résumé ?**  
À représenter un ensemble contigu de préfixes par une route agrégée, afin de réduire l’information annoncée ailleurs. Il doit être aligné sur le plan d’adressage et testé lors de la perte d’un sous-préfixe.

**3. Que fait `variance 2` si le meilleur coût est 100 ?**  
Le seuil de coût pour une route alternative est 200. La route doit aussi être loop-free selon les exigences EIGRP, notamment satisfaire la condition de faisabilité.

**4. Si RD est supérieure à FD, une route peut-elle quand même être sans boucle ?**  
Oui. La condition de faisabilité est suffisante, pas nécessaire. Le chemin n’est pas qualifié de feasible successor par ce test, même s’il pourrait être sans boucle.

**5. Pourquoi un chemin admissible à variance peut-il ne pas être installé ?**  
Parce qu’il ne satisfait pas la condition de faisabilité, dépasse le seuil métrique, est inéligible pour une autre raison, ou qu’une contrainte de plateforme/configuration limite son installation.

**6. EIGRP répartit-il lui-même les paquets comme un load balancer applicatif ?**  
Non. EIGRP sélectionne et installe les routes admissibles ; le plan de transfert du routeur traite la distribution des paquets selon les chemins installés et les mécanismes de la plateforme.

**7. Quelle différence entre mode classique et mode nommé ?**  
Le mode classique configure un processus associé à un numéro d’AS. Le mode nommé organise la configuration dans une hiérarchie comprenant familles d’adresses et sous-modes d’interface/topologie. La syntaxe et les fonctions diffèrent selon la version.

**8. Le mode stub bloque-t-il absolument toutes les Query ?**  
Non. Il indique le rôle du routeur et limite certains comportements de requête/propagation. La portée exacte dépend des routes annoncées, des options et de la plateforme.

**9. Pourquoi faut-il une métrique lors de la redistribution ?**  
Les protocoles peuvent utiliser des métriques différentes. Le protocole de destination a besoin de valeurs adaptées à sa propre décision de routage ; une route sans métrique appropriée peut ne pas être injectée comme prévu.

**10. Un tag de route empêche-t-il à lui seul une boucle ?**  
Non. Le tag sert à marquer la route ; une politique doit vérifier le tag et empêcher la réinjection dans le protocole d’origine.

**11. Que signifie un état DUAL ACTIVE ?**  
Une computation diffusée est en cours pour la destination et le routeur peut attendre les réponses des voisins interrogés. Il faut examiner l’étendue des Query et l’état des adjacences.

**12. À quoi renvoie un symptôme SIA ?**  
À une computation ACTIVE qui ne s’achève pas comme prévu dans les délais de l’implémentation. Il faut chercher les réponses manquantes ou tardives et l’instabilité sous-jacente.

**13. Un voisin présent prouve-t-il que toutes les routes sont installées ?**  
Non. Il faut inspecter les annonces, la table topologique, la sélection DUAL et la RIB.

**14. Pourquoi vérifier Null0 sur un résumé ?**  
Une route de rejet peut éviter les boucles pour du trafic à l’intérieur d’un agrégat qui n’a pas de route plus précise. Elle peut aussi provoquer un rejet attendu pour un sous-préfixe absent ; il faut en connaître le comportement.

**15. Quelle séquence de diagnostic appliquer à une panne EIGRP ?**  
Voisins → table topologique/DUAL → RIB → prochain saut/forwarding → route retour et application, tout en collectant les preuves avant modification.


## 11. Checklist de changement

### Avant
- [ ] Sauvegarder la configuration et relever la version.
- [ ] Cartographier les voisins, préfixes, métriques, résumés et politiques.
- [ ] Calculer les blocs d’agrégation et les chemins candidats variance.
- [ ] Définir le plan de test, les critères de réussite et le retour arrière.
- [ ] Vérifier les fonctions exactes prises en charge par la plateforme.

### Pendant
- [ ] Modifier une seule variable à la fois.
- [ ] Surveiller les voisins et les états DUAL.
- [ ] Comparer la table topologique à la RIB.
- [ ] Vérifier les résumés et les tags de routes aux frontières.
- [ ] Ne pas laisser une redistribution temporaire sans filtre.

### Après
- [ ] Vérifier route aller et route retour.
- [ ] Tester les applications et plusieurs flux si variance est activée.
- [ ] Inspecter logs, routes et état de voisinage.
- [ ] Restaurer les paramètres de test non nécessaires.
- [ ] Mettre à jour la topologie, les politiques et les preuves.


## 12. Glossaire ciblé

| Terme | Signification |
|---|---|
| Résumé | Agrégation de préfixes en une route plus large |
| Null0 | Interface logique de rejet utilisée pour certains cas de routage |
| Variance | Facteur autorisant l’installation de certains chemins de coût inégal |
| Feasible successor | Chemin admissible selon la condition de faisabilité DUAL |
| Mode nommé | Modèle de configuration EIGRP hiérarchique |
| Stub | Indication qu’un routeur est une branche et n’est pas un transit général |
| Redistribution | Importation de routes entre protocoles |
| Route tag | Marqueur transporté avec la route pour soutenir les politiques |
| Query / Reply | Messages utilisés pour une computation diffusée DUAL |
| ACTIVE | État durant lequel une computation DUAL reste en cours |
| SIA | Stuck-in-Active, computation qui ne termine pas comme attendu |
| RIB | Table générale de routage du système |

## Références techniques

- **RFC 7868 — Cisco’s Enhanced Interior Gateway Routing Protocol (EIGRP)** : https://www.rfc-editor.org/rfc/rfc7868.html
- **Cisco — Configuring EIGRP, IOS/IOS XE** : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/configuration/15-2s/config-eigrp.html
- **Cisco — EIGRP Unequal Cost Path Load Balancing / `variance`** : https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/13677-19.html
- **Cisco — EIGRP Command Reference, variance** : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-s1.html

La RFC 7868 est une description informative du protocole. La configuration exacte et les limites doivent être vérifiées dans le guide correspondant au modèle et à la version utilisés.

## Préparation au niveau Expert

Le niveau Expert partira de ce cours et approfondira le design EIGRP à grande échelle, la redistribution multi-protocoles plus complexe, la convergence sur topologies multi-chemins, les scénarios de défaut et l’automatisation de la validation. Il réutilisera les notions acquises sans répéter toutes les commandes de base.
