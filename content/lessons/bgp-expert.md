# BGP — Niveau Expert

**Durée indicative :** 6 à 10 heures selon les laboratoires et l’environnement de validation.  
**Prérequis :** maîtriser `bgp-debutant.md` et `bgp-intermediaire.md` : eBGP/iBGP, états TCP/BGP, attributs, politiques d’import/export, route reflectors, communautés, agrégation, RPKI/ROV de base et résolution du NEXT_HOP.  
**Environnements recommandés :** maquette FRRouting, Cisco IOS/IOS XE ou plateforme équivalente, deux ou trois domaines AS simulés, outils de capture, logs, et si possible un validateur RPKI/cache de test.

Ce cours constitue le troisième niveau de la série BGP. Il ne reprend pas pas à pas les bases du protocole ni la configuration d’un route reflector simple. Il traite BGP comme un service critique de contrôle du routage : politique inter-AS, résilience, sécurité, convergence, changement maîtrisé, observabilité et investigation reproductible.

> **Sécurité de laboratoire :** les AS `65010`, `65020`, `65030` et les préfixes `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` sont des exemples privés ou réservés à la documentation. N’annonce jamais de préfixes de test sur un peering réel. Toute expérimentation de route leak, invalidation RPKI ou retrait de route doit rester isolée et autorisée.

## Comment utiliser ce cours

Les schémas SVG sont intégrés directement dans ce fichier : il n’y a aucun dossier d’images externe. Les marqueurs animés indiquent un chemin logique ou une étape de traitement ; ils ne sont pas une mesure en temps réel et ne supposent pas que tous les routeurs implémentent une fonction identique. Si ton lecteur neutralise les animations SVG, les connecteurs et les légendes restent lisibles.

Travaille du design vers l’exploitation : architecture et contrat de peering, contrôle des annonces, validation RPKI/route leak, convergence et maintenance, puis diagnostic. Chaque laboratoire exige une hypothèse, une observation avant changement, un test discriminant, un critère de réussite et un retour arrière.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- concevoir une politique BGP multi-fournisseurs cohérente avec les rôles customer/provider/peer/route-server ;
- appliquer les mécanismes de prévention de fuite de routes tout en connaissant leurs limites ;
- intégrer RPKI Route Origin Validation dans une politique explicite et opérationnelle ;
- concevoir la redondance de route reflectors et évaluer les risques de réflexion/Next-Hop ;
- distinguer ADD-PATH, ECMP, multipath BGP, convergence et maintien de forwarding ;
- planifier une maintenance avec graceful shutdown plutôt qu’avec une fermeture brutale ;
- concevoir une agrégation sûre, sans recourir aux segments AS_SET désormais dépréciés ;
- séparer l’état de session, les routes reçues, les routes acceptées, le best path, la RIB, la FIB et la joignabilité applicative ;
- mener une investigation sur une fuite de route, un préfixe RPKI Invalid, une route non installée ou une panne après convergence ;
- produire un runbook et des preuves exploitables par une équipe NOC/engineering.


## 1. BGP comme contrat de politique, pas comme simple session

### 1.1 Les deux plans à séparer

Le plan de contrôle BGP transporte les préfixes, les attributs, les retraits et l’état de session. Le plan de données transfère les paquets selon la FIB, les interfaces, les encapsulations et les politiques de forwarding. Ces plans se rejoignent, mais la preuve qu’un fonctionne ne prouve pas l’autre.

Une session `Established` indique que la session est disponible pour échanger des messages, non que les préfixes attendus sont acceptés. Un préfixe présent dans la table BGP peut perdre l’élection, avoir un NEXT_HOP non résoluble ou ne pas être installé dans la RIB. Une route installée ne garantit pas que l’ACL, le chemin retour, le MTU ou le service distant fonctionne.

### Schéma 1 — Architecture multi-fournisseurs et décisions distinctes

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="510" viewBox="0 0 1000 510" role="img" aria-label="Architecture multi-fournisseurs : chemins et domaines de décision" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="510" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Architecture multi-fournisseurs : chemins et domaines de décision</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les sessions eBGP échangent des routes ; les politiques locales et celles des AS distants ne sont pas équivalentes.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="160" width="180" height="100" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="135.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65010</text><text x="135.0" y="208" text-anchor="middle" fill="#adbdcf" font-size="12">Entreprise / client</text><rect x="350" y="125" width="190" height="100" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="445.0" y="152" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65020</text><text x="445.0" y="173" text-anchor="middle" fill="#adbdcf" font-size="12">Transit fournisseur A</text><rect x="350" y="300" width="190" height="100" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="445.0" y="327" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65030</text><text x="445.0" y="348" text-anchor="middle" fill="#adbdcf" font-size="12">Transit fournisseur B</text><rect x="760" y="160" width="190" height="100" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="855.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65040</text><text x="855.0" y="208" text-anchor="middle" fill="#adbdcf" font-size="12">Réseau distant</text><path d="M 225 190 L 285 190 L 350 170" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="287" y="166" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="700">eBGP</text><path d="M 225 230 L 285 340 L 350 340" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="286" y="299" text-anchor="middle" fill="#c4b5fd" font-size="13" font-weight="700">eBGP</text><path d="M 540 170 L 640 170 L 760 190" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="645" y="150" text-anchor="middle" fill="#45c7f5" font-size="13" font-weight="700">eBGP</text><path d="M 540 340 L 650 340 L 760 230" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="656" y="325" text-anchor="middle" fill="#c4b5fd" font-size="13" font-weight="700">eBGP</text><text x="500" y="450" text-anchor="middle" fill="#adbdcf" font-size="13" font-weight="500">Deux chemins ne garantissent la résilience que si les dépendances et la politique sont réellement indépendantes.</text><text x="500" y="478" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="500">Trafic sortant : politique locale ; trafic entrant : décision distante, donc non garantie.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 225 190 L 285 190 L 350 170 L 540 170 L 640 170 L 760 190" dur="3s" begin="0s" repeatCount="indefinite"/></circle><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 225 230 L 285 340 L 350 340 L 540 340 L 650 340 L 760 230" dur="3.6s" begin="1.2s" repeatCount="indefinite"/></circle>
</svg></div>

Dans cette architecture, le réseau de l’AS 65010 dispose de deux fournisseurs. Les chemins illustrés montrent des relations eBGP ; ils ne signifient pas que le trafic entrant sera choisi par l’AS d’origine. Pour le trafic sortant, la préférence locale et les politiques internes jouent un rôle direct. Pour le trafic entrant, l’AS distant choisit selon ses propres politiques, les attributs qu’il reçoit et les autres chemins connus.

### 1.2 Modéliser la relation commerciale

Une politique BGP doit identifier au minimum le rôle du voisin : client, fournisseur, pair latéral, route server ou réseau interne. La même route ne doit pas forcément être annoncée à tous les voisins. Dans le modèle courant de relations, les routes clients et les routes locales peuvent être exportées plus largement que les routes apprises d’un fournisseur ou d’un pair. Les relations réelles peuvent être complexes ; une classification simpliste ne remplace pas un contrat ni la politique documentée.

Avant de créer une route-map, définis un tableau qui lie chaque voisin à son rôle, aux préfixes autorisés en entrée, aux préfixes autorisés en sortie, aux communautés attendues, au nombre maximal de routes et à la procédure d’urgence.

| Champ de contrat | Question opérationnelle |
|---|---|
| Rôle du voisin | Customer, provider, peer, route server ou relation particulière ? |
| Import | Quelles plages sont attendues ? Quelles longueurs maximales ? |
| Export | Quels préfixes locaux ou appris peuvent être annoncés à ce rôle ? |
| Attributs | Quelles communautés, LOCAL_PREF, MED ou autres marques sont contractuelles ? |
| Volume | Quel seuil `maximum-prefix` déclenche alerte ou arrêt ? |
| Sécurité | Quelle validation RPKI, quels contrôles d’AS_PATH, rôles et filtres sont actifs ? |
| Résilience | Quel chemin secondaire existe et quelle capacité lui reste-t-il ? |

### 1.3 Sortant et entrant : deux problèmes différents

LOCAL_PREF est un levier interne qui influence le choix du chemin sortant dans l’AS. AS_PATH prepending et MED peuvent influencer certaines décisions distantes, mais n’offrent aucune garantie universelle : le fournisseur peut préférer sa propre politique, une communauté peut être ignorée et une route plus spécifique peut gagner par longest-prefix match avant que les attributs de la route agrégée soient considérés.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" viewBox="0 0 1000 500" role="img" aria-label="Traffic engineering : sortie locale contre entrée distante" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Traffic engineering : sortie locale contre entrée distante</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les leviers sortants sont maîtrisés par l’AS local ; les leviers entrants influencent une décision externe.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="40" y="165" width="170" height="100" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="125.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65010</text><text x="125.0" y="213" text-anchor="middle" fill="#adbdcf" font-size="12">Réseau d’origine</text><rect x="365" y="115" width="200" height="95" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="465.0" y="142" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Transit A</text><text x="465.0" y="163" text-anchor="middle" fill="#adbdcf" font-size="12">LOCAL_PREF 200</text><rect x="365" y="300" width="200" height="95" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="465.0" y="327" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Transit B</text><text x="465.0" y="348" text-anchor="middle" fill="#adbdcf" font-size="12">LOCAL_PREF 150</text><rect x="760" y="165" width="200" height="100" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="860.0" y="192" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65100</text><text x="860.0" y="213" text-anchor="middle" fill="#adbdcf" font-size="12">Réseaux Internet</text><path d="M 210 195 L 275 195 L 365 162" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="282" y="173" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="700">Sortie A</text><path d="M 210 230 L 275 345 L 365 345" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="282" y="320" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="700">Sortie B</text><path d="M 565 162 L 665 162 L 760 195" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="665" y="144" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="700">eBGP</text><path d="M 565 345 L 665 345 L 760 230" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="665" y="325" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="700">eBGP</text><rect x="60" y="405" width="405" height="65" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/><text x="262.5" y="432" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Sortant : préférence locale</text><text x="262.5" y="453" text-anchor="middle" fill="#adbdcf" font-size="11">LOCAL_PREF choisit dans cet AS</text><rect x="535" y="405" width="405" height="65" rx="12" fill="#302919" stroke="#fbbf24" stroke-width="2"/><text x="737.5" y="432" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Entrant : décision de l’autre AS</text><text x="737.5" y="453" text-anchor="middle" fill="#adbdcf" font-size="11">prepend / MED / communauté : effet non garanti</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 210 195 L 275 195 L 365 162 L 565 162 L 665 162 L 760 195" dur="2.8s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

Le schéma distingue l’orientation de la décision. En ingénierie de trafic, formule l’objectif en termes mesurables : « les flux sortants vers telle destination doivent préférer A sauf si le suivi échoue », plutôt que « A doit toujours être le chemin utilisé ». Pour les flux entrants, la formulation correcte est une influence recherchée, accompagnée d’une méthode de mesure, et non une garantie.


## 2. Prévenir les fuites de routes

### 2.1 Ce qu’est une route leak

Une route leak se produit lorsqu’un préfixe est propagé au-delà de la politique attendue pour la relation entre AS. Par exemple, une route apprise d’un fournisseur est réannoncée vers un autre fournisseur comme si le réseau devait offrir du transit. Ce phénomène est différent d’un détournement d’origine : dans un leak, l’origine du préfixe peut rester légitime, tandis que la propagation devient incorrecte.

Le filtrage explicite des préfixes reste nécessaire. Il faut contrôler ce que le voisin annonce, ce qui est accepté, ce qui est sélectionné et ce qui est exporté. Le contrôle peut être basé sur des prefix-lists, des route-maps/policies, les communautés, des limites de nombre de préfixes et une politique cohérente avec le rôle du peering.

### 2.2 BGP Roles et attribut OTC

La RFC 9234 décrit la négociation d’un rôle BGP dans le message OPEN et l’attribut transitive **Only To Customer (OTC)** pour aider à prévenir ou détecter certains leaks. Les rôles typiques sont Provider, Customer, Peer, Route Server et RS-Client. Les deux côtés doivent configurer les rôles correspondants. En mode strict, une négociation absente ou incohérente peut empêcher l’établissement de la session ; la compatibilité des équipements doit donc être évaluée avant activation.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="490" viewBox="0 0 1000 490" role="img" aria-label="Prévention des route leaks : rôles BGP et attribut OTC" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Prévention des route leaks : rôles BGP et attribut OTC</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le rôle de peering décrit la relation commerciale ; le chemin rouge représente une annonce qui doit être bloquée.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="145" width="170" height="95" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="130.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65011</text><text x="130.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Client</text><rect x="320" y="145" width="170" height="95" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="405.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65020</text><text x="405.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Fournisseur</text><rect x="600" y="145" width="170" height="95" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="685.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65030</text><text x="685.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Pair</text><rect x="805" y="315" width="150" height="90" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="880.0" y="342" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">AS 65040</text><text x="880.0" y="363" text-anchor="middle" fill="#adbdcf" font-size="12">Autre fournisseur</text><path d="M 215 190 L 320 190" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="267" y="172" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">Customer ↔ Provider</text><path d="M 490 190 L 600 190" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="545" y="172" text-anchor="middle" fill="#45c7f5" font-size="11" font-weight="700">Provider ↔ Peer</text><path d="M 685 240 L 685 275 L 880 275 L 880 315" fill="none" stroke="#fb7185" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 5" opacity="1"/><text x="785" y="263" text-anchor="middle" fill="#fb7185" font-size="11" font-weight="700">Annonce interdite par politique</text><rect x="45" y="320" width="700" height="110" rx="12" fill="#142a2d" stroke="#5eead4" stroke-width="2"/><text x="395.0" y="347" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Contrôles de fuite</text><text x="395.0" y="368" text-anchor="middle" fill="#adbdcf" font-size="13">BGP Role négocié en OPEN  •  OTC dans UPDATE  •  filtres locaux conservés</text><text x="395" y="455" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">RFC 9234 réduit certains leaks liés aux relations provider/customer/peer ; il ne remplace pas toutes les politiques.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 215 190 L 320 190 L 490 190" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

L’OTC n’est pas un remplacement magique des filtres. Il peut réduire des leaks dus à une politique manuelle incohérente dans les relations couvertes, mais il ne détecte pas toutes les erreurs de préfixe, toutes les routes mal originées, toutes les erreurs locales ou toutes les relations complexes. Maintiens les listes de préfixes attendues, les rôles documentés, les tests d’export et les journaux.

### 2.3 La politique de propagation doit être vérifiable

Pour chaque voisin, définis des tests automatiques :

- les préfixes autorisés en réception apparaissent dans les routes acceptées ;
- un préfixe volontairement interdit n’est pas utilisable ;
- seules les routes autorisées sont visibles dans l’Adj-RIB-Out ou les commandes équivalentes ;
- les communautés et attributs obligatoires sont présents ;
- le nombre de routes est plausible et reste sous les seuils ;
- les routes reçues d’un fournisseur ne sont pas exportées à un autre fournisseur/peer en contradiction avec la politique ;
- une modification de rôle, de filtre ou d’OTC est testée avec une paire de voisins isolée avant le déploiement général.

### 2.4 Prévention opérationnelle d’une fuite

Une règle eBGP de sécurité comprend normalement une politique d’import et une politique d’export explicites. La RFC 8212 décrit le comportement par défaut recommandé pour éviter la propagation eBGP sans politique. Les implémentations et configurations déployées peuvent différer ; ne suppose jamais qu’un équipement applique déjà ce comportement : vérifie les politiques attachées et les annonces effectives.

Un inventaire de routes attendu est un artefact d’exploitation. Il doit contenir le préfixe, la longueur maximale, l’origine attendue, les voisins qui peuvent le recevoir, les communautés permises et le propriétaire du changement. Les objets générés automatiquement sont utiles mais doivent être testés : une erreur dans le générateur peut distribuer une fuite cohérente sur tous les routeurs.


## 3. RPKI/ROV : validation d’origine, pas de toute la route

### 3.1 Ce que vérifie ROV

Une ROA autorise un ASN à originer un préfixe et peut définir une longueur maximale. La validation d’origine compare une annonce BGP reçue aux VRP (Validated ROA Payloads) obtenus depuis la chaîne RPKI. Le résultat est en général **Valid**, **Invalid** ou **NotFound**.

- **Valid** : au moins une autorisation correspond au préfixe annoncé et à l’ASN d’origine selon la longueur autorisée.
- **Invalid** : les données d’autorisation connues ne valident pas l’annonce, par exemple origine différente ou longueur trop spécifique par rapport à `maxLength`.
- **NotFound** : aucune autorisation couvrant le cas n’est connue par le validateur. Ce n’est pas une preuve d’illégitimité.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" viewBox="0 0 1000 500" role="img" aria-label="RPKI Route Origin Validation : trois états, trois décisions possibles" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">RPKI Route Origin Validation : trois états, trois décisions possibles</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Invalid est une preuve de non-conformité à un ROA applicable ; NotFound signifie seulement absence d’autorisation connue.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="155" width="170" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="120.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Annonce BGP</text><text x="120.0" y="203" text-anchor="middle" fill="#adbdcf" font-size="12">Préfixe + ASN origine</text><rect x="270" y="155" width="190" height="90" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="365.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Cache RPKI</text><text x="365.0" y="203" text-anchor="middle" fill="#adbdcf" font-size="12">ROA / VRP disponibles</text><rect x="525" y="125" width="180" height="95" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/><text x="615.0" y="152" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Valid</text><text x="615.0" y="173" text-anchor="middle" fill="#adbdcf" font-size="11">Préfixe + origine autorisés</text><rect x="525" y="245" width="180" height="95" rx="12" fill="#321c25" stroke="#fb7185" stroke-width="2"/><text x="615.0" y="272" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Invalid</text><text x="615.0" y="293" text-anchor="middle" fill="#adbdcf" font-size="11">Origine ou longueur interdite</text><rect x="525" y="365" width="180" height="75" rx="12" fill="#302919" stroke="#fbbf24" stroke-width="2"/><text x="615.0" y="392" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">NotFound</text><text x="615.0" y="413" text-anchor="middle" fill="#adbdcf" font-size="11">Aucun ROA applicable</text><rect x="780" y="180" width="180" height="100" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="870.0" y="207" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Politique locale</text><text x="870.0" y="228" text-anchor="middle" fill="#adbdcf" font-size="11">Accepter / déprioriser / rejeter</text><path d="M 205 200 L 270 200" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="238" y="184" text-anchor="middle" fill="#45c7f5" font-size="11" font-weight="500">Validation</text><path d="M 460 185 L 490 185 L 490 170 L 525 170" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 460 200 L 490 200 L 490 290 L 525 290" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 460 215 L 490 215 L 490 400 L 525 400" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 705 170 L 740 170 L 740 220 L 780 220" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 705 290 L 745 290 L 780 250" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 705 400 L 750 400 L 750 270 L 780 270" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="500" y="465" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">ROV valide l’origine, pas tout le chemin AS_PATH, la légitimité commerciale ni la sécurité du paquet.</text><circle r="6" fill="#fb7185" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 205 200 L 270 200 L 460 200 L 490 200 L 490 290 L 525 290" dur="3s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

ROV valide l’origine annoncée, non tout l’AS_PATH, la relation commerciale, la qualité de la route, la légitimité de chaque annonce intermédiaire ou la sûreté du trafic utilisateur. Il faut le combiner à la politique de peering, au contrôle des préfixes, au contrôle des leaks et à la surveillance.

### 3.2 Politique Invalid / NotFound

Une politique de sécurité courante rejette les annonces `Invalid`, à condition que l’écosystème RPKI soit opérationnel et que les incidents soient traités. Le cas `NotFound` demande une décision de politique explicite : acceptation normale avec marquage, préférence réduite, ou traitement spécifique selon le voisin et le contexte. Rejeter indistinctement NotFound peut retirer beaucoup de routes légitimes qui n’ont pas de ROA publié.

Une ROA avec `maxLength` trop large peut autoriser des annonces plus spécifiques que prévu. À l’inverse, un `maxLength` trop étroit peut invalider de vraies annonces. Le propriétaire des ressources doit coordonner le changement de ROA et le déploiement BGP, puis surveiller les états de validation.

### 3.3 Validateur, cache et routeur

Le routeur ne vérifie pas nécessairement chaque signature RPKI en ligne à chaque UPDATE. Il reçoit généralement l’état de validation d’un cache/serveur RTR, selon le protocole et l’implémentation. La disponibilité du cache, la fraîcheur des données et le comportement à la perte du cache font donc partie du runbook. Un état de cache expiré ne doit pas être traité sans politique claire.

Les contrôles incluent : état de la session RTR, âge des données, nombre de VRP, compte des routes Valid/Invalid/NotFound, changements brusques d’état et impact sur les routes. Avant de mettre en place le rejet global d’Invalid, exécute une phase d’observation et traite les invalides existants avec les propriétaires des préfixes.


## 4. Architecture iBGP à grande échelle : route reflectors

### 4.1 Redondance des RR

Les route reflectors réduisent le besoin de full mesh iBGP, mais ils ajoutent des règles de réflexion et des attributs anti-boucle comme ORIGINATOR_ID et CLUSTER_LIST. Une architecture avec deux RR ne devient pas automatiquement redondante : les clients doivent être reliés selon un plan connu, les Cluster ID doivent être choisis avec attention, le NEXT_HOP doit rester résoluble et les politiques doivent être cohérentes entre les deux vues.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="510" viewBox="0 0 1000 510" role="img" aria-label="Redondance des route reflectors : clients et sessions" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="510" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Redondance des route reflectors : clients et sessions</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Une paire de RR peut améliorer la disponibilité, mais ne répare pas une erreur de NEXT_HOP ou une politique incohérente.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="195" width="170" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="130.0" y="222" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Client C1</text><text x="130.0" y="243" text-anchor="middle" fill="#adbdcf" font-size="12">iBGP</text><rect x="45" y="330" width="170" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="130.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Client C2</text><text x="130.0" y="378" text-anchor="middle" fill="#adbdcf" font-size="12">iBGP</text><rect x="360" y="150" width="190" height="100" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="455.0" y="177" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">RR-1</text><text x="455.0" y="198" text-anchor="middle" fill="#adbdcf" font-size="12">Cluster ID A</text><rect x="360" y="330" width="190" height="100" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="455.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">RR-2</text><text x="455.0" y="378" text-anchor="middle" fill="#adbdcf" font-size="12">Cluster ID B</text><rect x="760" y="235" width="180" height="100" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="850.0" y="262" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Edge eBGP</text><text x="850.0" y="283" text-anchor="middle" fill="#adbdcf" font-size="12">Routes externes</text><path d="M 215 240 L 285 240 L 360 190" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 215 370 L 285 370 L 360 380" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 215 240 L 285 240 L 285 380 L 360 380" fill="none" stroke="#34475d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><path d="M 215 370 L 280 370 L 280 200 L 360 200" fill="none" stroke="#34475d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><path d="M 760 270 L 650 270 L 650 195 L 550 195" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 760 300 L 700 300 L 700 380 L 550 380" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="650" y="180" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">iBGP</text><text x="665" y="365" text-anchor="middle" fill="#c4b5fd" font-size="11" font-weight="700">iBGP</text><path d="M 455 250 L 455 330" fill="none" stroke="#5eead4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5 5" opacity="1"/><text x="475" y="293" text-anchor="middle" fill="#5eead4" font-size="11" font-weight="700">iBGP entre RR</text><text x="500" y="465" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">Les RR évitent un full mesh ; deux RR sont utiles seulement si clients, clusters et annonces sont conçus de façon cohérente.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 760 270 L 650 270 L 650 195 L 550 195" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 360 190 L 285 240 L 215 240" dur="1.8s" begin="0.8s" repeatCount="indefinite"/></circle><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 760 300 L 700 300 L 700 380 L 550 380" dur="2.5s" begin="0.8s" repeatCount="indefinite"/></circle><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 360 380 L 285 370 L 215 370" dur="1.8s" begin="1.6s" repeatCount="indefinite"/></circle>
</svg></div>

Un client connecté à RR-1 et RR-2 peut recevoir des copies de chemins identiques ou différents, selon l’origine, les politiques et les règles d’annonce. Deux RR qui ne partagent pas la même politique peuvent produire des résultats différents. Le fait qu’un voisinage soit `Established` ne prouve pas que le préfixe est réfléchi, accepté ou choisi par le client.

### 4.2 ORIGINATOR_ID et CLUSTER_LIST

Ces attributs servent à prévenir certaines boucles de réflexion. Lorsqu’un route reflector annonce une route iBGP selon les règles applicables, il renseigne les attributs appropriés pour permettre à d’autres RR de détecter un retour vers le routeur d’origine ou vers un cluster déjà traversé. Ils ne sont pas des outils généraux pour détecter tous les chemins incorrects ; ils suivent les règles du mécanisme de route reflection.

### 4.3 Next-Hop et IGP

iBGP préserve souvent le NEXT_HOP reçu pour certaines routes, sauf configuration de réécriture. Le réseau IGP doit permettre de résoudre ce prochain saut. Si le RR possède une route mais que le client ne peut pas résoudre son NEXT_HOP, la route peut rester non installée ou non utilisable. `next-hop-self` peut résoudre certaines architectures, mais change la sémantique de chemin et doit être appliqué en connaissance de cause.

### 4.4 Route reflection et diversité des chemins

Un RR traditionnel annonce souvent un seul meilleur chemin à ses clients pour une route donnée, avec les règles de réflexion définies par la spécification. Cette propriété peut masquer un chemin alternatif qui serait intéressant pour un client dont la topologie ou la sortie préférée diffère. Des fonctions comme ORR (Optimal Route Reflection) ou ADD-PATH répondent à des besoins précis, mais elles dépendent du support de la plateforme, de la topologie et de la politique. Elles ne doivent pas être activées comme une option universelle sans mesurer la charge et l’effet sur les routes.


## 5. ADD-PATH, multipath et ECMP : ne pas les confondre

ADD-PATH permet, lorsque la capacité correspondante est négociée, d’annoncer plusieurs chemins pour un même préfixe. Les Path Identifier distinguent les chemins dans le contexte défini par la capacité. Cela ne veut pas automatiquement dire que le récepteur installe tous les chemins, les utilise en ECMP ou qu’ils sont interchangeables sans impact de sécurité.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="480" viewBox="0 0 1000 480" role="img" aria-label="BGP ADD-PATH : annoncer plusieurs chemins sans confondre avec ECMP" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">BGP ADD-PATH : annoncer plusieurs chemins sans confondre avec ECMP</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le comportement dépend de la capacité négociée, de la politique d’envoi et de la capacité du récepteur.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="190" width="165" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="117.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Routeur A</text><text x="117.5" y="238" text-anchor="middle" fill="#adbdcf" font-size="12">Deux chemins</text><rect x="280" y="105" width="165" height="90" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="362.5" y="132" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Chemin P1</text><text x="362.5" y="153" text-anchor="middle" fill="#adbdcf" font-size="12">Path-ID 101</text><rect x="280" y="315" width="165" height="90" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="362.5" y="342" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Chemin P2</text><text x="362.5" y="363" text-anchor="middle" fill="#adbdcf" font-size="12">Path-ID 202</text><rect x="505" y="180" width="180" height="130" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="595.0" y="207" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Export BGP</text><text x="595.0" y="228" text-anchor="middle" fill="#adbdcf" font-size="12">Politique par voisin</text><rect x="790" y="105" width="175" height="95" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="877.5" y="132" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Voisin X</text><text x="877.5" y="153" text-anchor="middle" fill="#adbdcf" font-size="11">ADD-PATH : P1 + P2</text><rect x="790" y="315" width="175" height="95" rx="12" fill="#172333" stroke="#fb7185" stroke-width="2"/><text x="877.5" y="342" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Voisin Y</text><text x="877.5" y="363" text-anchor="middle" fill="#adbdcf" font-size="11">Chemin sélectionné seul</text><path d="M 200 220 L 240 220 L 240 150 L 280 150" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 200 250 L 240 250 L 240 360 L 280 360" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 445 150 L 475 150 L 475 210 L 505 210" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 445 360 L 475 360 L 475 260 L 505 260" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 685 210 L 730 210 L 730 145 L 790 145" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 685 260 L 750 260 L 750 170 L 790 170" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 685 285 L 730 285 L 730 360 L 790 360" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="755" y="125" text-anchor="middle" fill="#4ade80" font-size="10" font-weight="700">Path-ID 101</text><text x="755" y="195" text-anchor="middle" fill="#c4b5fd" font-size="10" font-weight="700">Path-ID 202</text><text x="742" y="340" text-anchor="middle" fill="#fb7185" font-size="10" font-weight="700">Best path</text><text x="500" y="450" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">ADD-PATH transporte plusieurs chemins vers X ; Y reçoit seulement celui annoncé par la politique classique.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 200 220 L 240 220 L 240 150 L 280 150 L 445 150 L 475 150 L 475 210 L 505 210 L 685 210 L 730 210 L 730 145 L 790 145" dur="3.6s" begin="0s" repeatCount="indefinite"/></circle><circle r="6" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 200 250 L 240 250 L 240 360 L 280 360 L 445 360 L 475 360 L 475 260 L 505 260 L 685 260 L 750 260 L 750 170 L 790 170" dur="3.8s" begin="1.1s" repeatCount="indefinite"/></circle><circle r="6" fill="#fb7185" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 685 285 L 730 285 L 730 360 L 790 360" dur="2.7s" begin="0.7s" repeatCount="indefinite"/></circle>
</svg></div>

| Mécanisme | Fonction | Ce qu’il ne garantit pas |
|---|---|---|
| ADD-PATH | Envoyer plusieurs chemins BGP pour un préfixe | L’installation de tous les chemins ou le partage du trafic |
| BGP multipath | Permettre l’installation de plusieurs chemins jugés équivalents par l’implémentation/politique | Que chaque route reçue soit éligible à ECMP |
| ECMP/FIB | Répartir le forwarding entre plusieurs prochains sauts | Une distribution égale pour chaque flux, ni absence de réordonnancement |
| Route reflector | Propager certaines routes iBGP selon les règles de réflexion | L’optimalité pour chaque client ou une visibilité exhaustive de tous les chemins |

Lors d’un audit, mesure le nombre de chemins dans Adj-RIB-In, les chemins sélectionnés dans BGP, les routes installées dans la RIB et les next-hops réels de la FIB. Ces chiffres peuvent différer sans qu’il s’agisse nécessairement d’un défaut.


## 6. Convergence, rétractation et maintenance contrôlée

### 6.1 Retrait et convergence

Lorsqu’un chemin disparaît, BGP peut envoyer un retrait d’annonce et ses voisins recalculent leurs routes candidates. La durée du rétablissement dépend du mécanisme de détection, de la propagation, du nombre d’updates, de la sélection des chemins, de la résolution des next-hops et de la mise à jour de la FIB. Il faut séparer la détection de la panne, le traitement BGP et le forwarding.

Les mécanismes de détection rapide comme BFD peuvent réduire le temps de détection, mais ne remplacent pas le calcul BGP, l’installation des routes ni la convergence applicative. Une configuration BFD trop agressive peut augmenter les bascules sur un lien chargé ou instable ; teste les temporisateurs, la capacité des CPU et le comportement de la plateforme.

### 6.2 Graceful Restart et ses limites

Graceful Restart peut permettre de préserver temporairement le forwarding pendant le redémarrage d’un processus de contrôle lorsque les conditions et capacités le permettent. Il est inadapté à certains défauts où les routes conservées sont devenues incorrectes ou où le plan de données n’est pas réellement opérationnel. Un routeur ne doit pas être déclaré résilient simplement parce que le voisinage garde une apparence de continuité.

Définis la nature de l’événement : redémarrage logiciel avec forwarding continu, panne matérielle, perte de lien, perte de route amont, ou route leak. L’action et le comportement attendu ne sont pas les mêmes. Mesure les routes stale, les durées, les chemins retenus et la capacité à invalider les informations périmées.

### 6.3 Graceful shutdown pendant la maintenance

La RFC 8326 définit la communauté bien connue GRACEFUL_SHUTDOWN pour réduire les pertes lors d’un arrêt planifié. Le processus consiste typiquement à marquer les routes et réduire leur préférence en amont de l’arrêt, laisser le trafic se déplacer vers les alternatives, valider le déplacement, puis fermer la session. Le support et les étapes exactes sont dépendants des opérateurs et des plateformes.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="480" viewBox="0 0 1000 480" role="img" aria-label="Maintenance BGP : séquence de graceful shutdown" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Maintenance BGP : séquence de graceful shutdown</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Appliquer la communauté et la politique appropriées, vérifier le déplacement du trafic, puis fermer la session.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="40" y="145" width="190" height="95" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="135.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Avant maintenance</text><text x="135.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Chemin normalement préféré</text><rect x="285" y="145" width="190" height="95" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="380.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Marquage</text><text x="380.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">GRACEFUL_SHUTDOWN</text><rect x="530" y="145" width="190" height="95" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="625.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Retrait progressif</text><text x="625.0" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Alternatives sélectionnées</text><rect x="775" y="145" width="185" height="95" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="867.5" y="172" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Arrêt contrôlé</text><text x="867.5" y="193" text-anchor="middle" fill="#adbdcf" font-size="12">Session fermée ensuite</text><path d="M 230 192 L 285 192" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 475 192 L 530 192" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 720 192 L 775 192" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="285" y="300" width="435" height="90" rx="12" fill="#321c25" stroke="#fb7185" stroke-width="2"/><text x="502.5" y="327" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Important</text><text x="502.5" y="348" text-anchor="middle" fill="#adbdcf" font-size="12">Réduire la préférence d’abord ; attendre la convergence mesurée</text><path d="M 380 240 L 380 300" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><path d="M 625 240 L 625 300" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><text x="500" y="445" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">Le graceful shutdown réduit les pertes lors d’un changement planifié ; il ne promet pas une interruption nulle.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 230 192 L 285 192 L 475 192 L 530 192 L 720 192 L 775 192" dur="4s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

Ne ferme pas immédiatement une session en espérant que tous les voisins ont déjà convergé. Le runbook doit comprendre le délai d’observation, des tests de trafic, la procédure de restauration et une condition explicite pour abandonner l’opération.


## 7. Agrégation en 2026 : sécurité de la portée et d’AS_PATH

### 7.1 Pourquoi agréger ?

L’agrégation réduit le nombre de préfixes annoncés et peut stabiliser la table BGP. Elle est correcte lorsque le résumé représente un ensemble bien défini, que le chemin de forwarding vers tous les sous-réseaux couverts est maîtrisé et que les routes détaillées sont annoncées aux voisins qui en ont besoin. Une agrégation qui couvre une adresse non réellement desservie peut créer un trou noir si le routeur accepte le paquet mais n’a aucun chemin plus spécifique.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" viewBox="0 0 1000 500" role="img" aria-label="Agrégation BGP : résumé exact, trous noirs et AS_PATH" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Agrégation BGP : résumé exact, trous noirs et AS_PATH</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">L’agrégat doit correspondre au plan d’adressage et disposer d’un traitement explicite des destinations non couvertes.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="40" y="120" width="240" height="130" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="160.0" y="147" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Routes spécifiques</text><text x="160.0" y="168" text-anchor="middle" fill="#adbdcf" font-size="11">198.51.100.0/24</text><text x="160.0" y="185" text-anchor="middle" fill="#adbdcf" font-size="11">198.51.101.0/24</text><text x="160.0" y="202" text-anchor="middle" fill="#adbdcf" font-size="11">198.51.102.0/24</text><text x="160.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="11">198.51.103.0/24</text><rect x="340" y="135" width="220" height="105" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="450.0" y="162" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Agrégateur AS 65010</text><text x="450.0" y="183" text-anchor="middle" fill="#adbdcf" font-size="12">Annonce résumé</text><text x="450.0" y="200" text-anchor="middle" fill="#adbdcf" font-size="12">198.51.100.0/22</text><rect x="680" y="135" width="250" height="105" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="805.0" y="162" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Voisin AS 65020</text><text x="805.0" y="183" text-anchor="middle" fill="#adbdcf" font-size="12">Reçoit le résumé</text><text x="805.0" y="200" text-anchor="middle" fill="#adbdcf" font-size="12">AS_PATH explicite</text><path d="M 280 185 L 340 185" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 560 185 L 680 185" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="95" y="310" width="330" height="100" rx="12" fill="#321c25" stroke="#fb7185" stroke-width="2"/><text x="260.0" y="337" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Destination couverte mais absente</text><text x="260.0" y="358" text-anchor="middle" fill="#adbdcf" font-size="12">Risque de trou noir / discard contrôlé</text><rect x="560" y="310" width="340" height="100" rx="12" fill="#302919" stroke="#fbbf24" stroke-width="2"/><text x="730.0" y="337" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Agrégation sûre</text><text x="730.0" y="358" text-anchor="middle" fill="#adbdcf" font-size="12">Pas d’AS_SET/AS_CONFED_SET</text><text x="730.0" y="375" text-anchor="middle" fill="#adbdcf" font-size="12">selon RFC 9774</text><path d="M 450 240 L 275 310" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><path d="M 450 240 L 700 310" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="500" y="460" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">Un résumé représente un ensemble exact de préfixes ; ne l’annonce pas si la couverture ou l’origine n’est pas maîtrisée.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 245 185 L 340 185 L 560 185 L 680 185" dur="2.6s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

### 7.2 Risque lié aux segments AS_SET

La RFC 9774, publiée en mai 2025, déprécie l’origine de routes BGP contenant AS_SET et AS_CONFED_SET et met à jour la spécification BGP. Les conceptions modernes doivent éviter de compter sur ces segments dans les agrégations. L’agrégation doit produire un AS_PATH explicite et cohérent avec les règles actuelles, et l’origine déclarée doit être cohérente avec les ROA lorsque RPKI est utilisé.

Ne construis pas une agrégation avant de définir : préfixes contributeurs, stabilité de l’origine, relations d’export, politiques de plus spécifiques, comportement de discard pour les destinations non couvertes, ROA du résumé et du détail, et plan de rollback. Un résumé peut réduire la visibilité d’une panne plus spécifique, donc les alertes doivent surveiller les préfixes contributeurs aussi bien que le résumé.

### 7.3 Les routes plus spécifiques priment

Le longest-prefix match du plan de données fait qu’un préfixe plus spécifique peut attirer le trafic même si le résumé est annoncé. La politique BGP décide de la route de chaque préfixe reçu, mais le transfert final applique la route la plus spécifique installée. Avant un changement, vérifie le résumé, les préfixes plus spécifiques et le comportement lorsque l’un d’eux disparaît.


## 8. Pipeline de traitement et diagnostic RIB/FIB

Une investigation experte doit faire apparaître à quelle étape l’annonce se perd : réception, politique d’import, validation, sélection, résolution du NEXT_HOP, installation dans la RIB, installation dans la FIB ou transfert effectif. Une session saine ne prouve pas que la chaîne est saine.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="475" viewBox="0 0 1000 475" role="img" aria-label="Pipeline d’une route BGP : de la réception au forwarding" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="475" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Pipeline d’une route BGP : de la réception au forwarding</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">La présence d’une route dans une étape ne prouve pas qu’elle passe à la suivante.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="30" y="125" width="155" height="85" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="107.5" y="152" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Adj-RIB-In</text><text x="107.5" y="173" text-anchor="middle" fill="#adbdcf" font-size="12">Route reçue</text><rect x="215" y="125" width="155" height="85" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="292.5" y="152" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Import Policy</text><text x="292.5" y="173" text-anchor="middle" fill="#adbdcf" font-size="12">Filtre / marquage</text><rect x="400" y="125" width="155" height="85" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="477.5" y="152" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">RPKI / Rôle</text><text x="477.5" y="173" text-anchor="middle" fill="#adbdcf" font-size="12">Validation + leak</text><rect x="585" y="125" width="155" height="85" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/><text x="662.5" y="152" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Best Path</text><text x="662.5" y="173" text-anchor="middle" fill="#adbdcf" font-size="12">Chemin candidat</text><rect x="770" y="125" width="190" height="85" rx="12" fill="#172333" stroke="#5eead4" stroke-width="2"/><text x="865.0" y="152" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">RIB / FIB</text><text x="865.0" y="173" text-anchor="middle" fill="#adbdcf" font-size="11">Route installée / transfert</text><path d="M 185 168 L 215 168" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 370 168 L 400 168" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 555 168 L 585 168" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 740 168 L 770 168" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="80" y="290" width="360" height="95" rx="12" fill="#321c25" stroke="#fb7185" stroke-width="2"/><text x="260.0" y="317" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Route acceptée mais non installée</text><text x="260.0" y="338" text-anchor="middle" fill="#adbdcf" font-size="12">NEXT_HOP / préférence RIB / inéligibilité</text><rect x="560" y="290" width="360" height="95" rx="12" fill="#302919" stroke="#fbbf24" stroke-width="2"/><text x="740.0" y="317" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Route installée, trafic en échec</text><text x="740.0" y="338" text-anchor="middle" fill="#adbdcf" font-size="12">FIB / ACL / route retour / service</text><path d="M 660 210 L 660 255 L 260 255 L 260 290" fill="none" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><path d="M 860 210 L 860 255 L 740 255 L 740 290" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5" opacity="1"/><text x="500" y="435" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">Chaque étape possède une preuve différente : session, route reçue, policy, best path, RIB, FIB puis test applicatif.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 30 168 L 185 168 L 215 168 L 370 168 L 400 168 L 555 168 L 585 168 L 740 168 L 770 168" dur="4s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

### 8.1 Une route est reçue mais rejetée

Vérifie l’Adj-RIB-In ou l’équivalent, les politiques entrantes, les règles RPKI, les attributs obligatoires et la famille d’adresses activée. Compare la configuration rendue et l’état réellement appliqué ; sur des systèmes avec policy compilation, une route-map générée peut ne pas être attachée comme prévu.

### 8.2 La route est acceptée mais pas installée

Vérifie le best path, le NEXT_HOP, les routes concurrentes et la résolution récursive. Une route peut être valide du point de vue du protocole sans être le chemin retenu pour la RIB. Cherche les raisons d’inéligibilité indiquées par l’implémentation au lieu de modifier les attributs au hasard.

### 8.3 La route est installée mais le trafic échoue

Vérifie la FIB, les interfaces de sortie, les ACL, les politiques de forwarding, la route de retour, les filtres anti-spoofing, les MTU, le NAT éventuel et le service. Capture aux points appropriés et note le sens du paquet. Un ping échoué n’isole pas la cause ; utilise une transaction ou un test applicatif représentatif.


## 9. Sécuriser le plan de routage

### 9.1 Baseline de session

Pour chaque voisin eBGP, définis explicitement les adresses de peering, ASN, source de session, familles d’adresses, politique d’entrée et sortie, mécanismes d’authentification disponibles, limites de préfixes, timers, journaux et contacts d’escalade. N’active pas un voisinage sans définir ce qu’il est autorisé à annoncer et recevoir.

### 9.2 Filtres d’annonces

Les contrôles incluent une liste d’origines ou de préfixes attendus, des limites de longueur, les routes non routables/bogons selon la politique, une limite `maximum-prefix`, un contrôle de route leak et une politique explicite d’export. Les listes doivent être maintenues et validées : un filtre obsolète peut provoquer une panne aussi bien qu’une fuite.

Le maximum-prefix doit avoir un seuil basé sur les routes normales et la croissance observée ; un seuil trop bas peut couper une session légitime et un seuil trop élevé perd son utilité. Définis ce qui arrive à l’approche du seuil : alerte, action préventive ou arrêt de session selon la plateforme et le risque. Vérifie la politique de redémarrage si un seuil est franchi.

### 9.3 Sécurité des sessions

La sécurité opérationnelle peut comporter des ACL limitant TCP/179 aux pairs connus, la protection de la source de peering, GTSM/TTL security quand elle est appropriée et supportée, l’authentification de session selon les capacités de la plateforme, la journalisation, la limitation de ressources et les procédures de rotation. Aucun mécanisme de session ne prouve à lui seul que toutes les annonces reçues sont légitimes.

Ne place pas de secret réel dans un cours ou dans un dépôt. Les commandes d’authentification changent selon les systèmes et les versions ; l’exemple de laboratoire doit utiliser un secret jetable et être éliminé après l’exercice.

### 9.4 RPKI, BGP Roles et limites de validation

ROV et OTC répondent à des classes différentes de problèmes. ROV valide l’association préfixe/origine ; les rôles BGP/OTC aident à contrôler la propagation vis-à-vis d’une relation provider/customer/peer. Les filtres d’export contrôlent encore ce que l’AS décide d’annoncer. Combine les contrôles et surveille leur état au lieu de les considérer comme substituts.

### 9.5 Journaux et traçabilité

Conserve les transitions de session, les NOTIFICATION, les retraits massifs, les variations inhabituelles de nombre de préfixes, les changements RPKI, les routes exportées et les résultats de validation. Les horloges des équipements, du route collector, du validateur et du système de tickets doivent être suffisamment synchronisées pour reconstruire l’ordre des événements.


## 10. Route leaks : analyse et réponse à incident

Lorsqu’une fuite est suspectée, ne commence pas par réinitialiser tous les peers. Conserve les informations de contrôle avant la correction si cela ne retarde pas le confinement nécessaire : heure de début, préfixes concernés, AS_PATH, communautés, peer d’entrée, peer d’export, statut RPKI, politiques actives et état des routes dans la RIB/FIB.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="525" viewBox="0 0 1000 525" role="img" aria-label="Diagnostic de fuite de routes : de l’observation à la remédiation" font-family="Inter,Arial,sans-serif">
<rect width="1000" height="525" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Diagnostic de fuite de routes : de l’observation à la remédiation</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Ne confonds pas route leak, route origin invalid et panne de forwarding : ces hypothèses exigent des preuves distinctes.</text>
<line x1="28" y1="78" x2="972" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="365" y="105" width="270" height="75" rx="12" fill="#321c25" stroke="#fb7185" stroke-width="2"/><text x="500.0" y="132" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Route leak suspectée</text><text x="500.0" y="153" text-anchor="middle" fill="#adbdcf" font-size="12">Préfixe annoncé hors politique</text><rect x="45" y="255" width="250" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="170.0" y="282" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Origine du préfixe</text><text x="170.0" y="303" text-anchor="middle" fill="#adbdcf" font-size="12">RIB locale / ROA / propriétaire</text><rect x="375" y="255" width="250" height="90" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="500.0" y="282" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Politique du peer</text><text x="500.0" y="303" text-anchor="middle" fill="#adbdcf" font-size="12">Rôle / OTC / import-export</text><rect x="705" y="255" width="250" height="90" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="830.0" y="282" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Propagation observée</text><text x="830.0" y="303" text-anchor="middle" fill="#adbdcf" font-size="12">Adj-RIB-Out / looking glass</text><path d="M 450 180 L 170 255" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 500 180 L 500 255" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 550 180 L 830 255" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><rect x="170" y="390" width="660" height="75" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/><text x="500.0" y="417" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Décision de remédiation</text><text x="500.0" y="438" text-anchor="middle" fill="#adbdcf" font-size="12">Filtrer / corriger rôle / corriger ROA / retrait coordonné / post-mortem</text><path d="M 170 345 L 300 390" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 500 345 L 500 390" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><path d="M 830 345 L 700 390" fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="1"/><text x="500" y="490" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="500">Préserver logs, timestamps, mises à jour BGP et portée d’impact avant toute réinitialisation massive.</text><circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 500 180 L 500 255 L 500 345 L 500 390" dur="3.2s" begin="0s" repeatCount="indefinite"/></circle>
</svg></div>

### 10.1 Séquence de réponse

1. **Détecter :** confirmer les préfixes, les voisins et la durée. Distinguer une fuite de route d’une simple annonce plus spécifique légitime.
2. **Évaluer :** identifier le chemin, l’impact de trafic et les services touchés.
3. **Confiner :** appliquer le filtre le plus ciblé aux annonces fautives, en tenant compte de l’effet sur les routes légitimes.
4. **Vérifier :** confirmer le retrait chez le voisin attendu et aux points d’observation. Les caches ou collecteurs peuvent montrer des états décalés.
5. **Corriger la cause :** rôle, politique export, communauté, origine, génération d’agrégat ou automatisation fautive.
6. **Prévenir la récidive :** test négatif dans CI, monitoring du préfixe, revue de la politique et runbook mis à jour.

### 10.2 Distinguer les incidents

| Observation | Hypothèses principales | Preuve discriminante |
|---|---|---|
| Préfixe connu avec AS_PATH inattendu | Leak, annonce via un transit ou erreur de politique | Route reçue, export exact, rôle de peering |
| RPKI Invalid | Origine non autorisée ou longueur supérieure au maxLength | ROA/VRP, préfixe reçu, ASN origine |
| Session up, zéro route | Politique fermée, famille inactive, voisin n’annonçant rien | Adj-RIB-In/Out, AFI/SAFI, filtres |
| Route BGP active mais RIB absente | NEXT_HOP non résolu ou route concurrente | Affichage best path, table IGP, RIB |
| Route dans RIB, trafic absent | FIB, ACL, asymétrie, MTU ou service | Compteurs, captures multi-points, test appli |
| Explosion du nombre de préfixes | Leak, route server ou filtre trop large | Courbe de préfixes, annonce par voisin |


## 11. Laboratoires experts

Les labs sont conçus pour un environnement isolé. Chaque compte rendu doit inclure topologie, configuration, hypothèse, mesure de départ, modification, sortie observée, preuve de réussite et rollback. Les fonctionnalités avancées peuvent nécessiter FRRouting, une image IOS/IOS XE spécifique ou un routeur de test compatible ; Packet Tracer ne simule pas nécessairement chaque capacité de sécurité BGP.

### Laboratoire 1 — Contrat multi-fournisseurs

Construis AS 65010 avec deux fournisseurs simulés. Définis les routes autorisées, les filtres IN/OUT, le rôle de chaque peer et la préférence locale sortante. Vérifie les annonces réellement envoyées. Injecte une route de test interdite et démontre qu’elle n’est ni acceptée ni réannoncée.

**Livrables :** tableau par peer, captures des annonces, politique attachée, preuves de rejet.

### Laboratoire 2 — Route leak et OTC

Dans une maquette qui supporte RFC 9234, forme des sessions avec rôles compatibles. Simule la tentative de propager une route fournisseur vers un autre fournisseur/peer. Vérifie la négociation de rôles, l’attribut OTC et la politique explicite. Si la plateforme n’implémente pas cette fonction, documente la limite et réalise l’exercice avec filtres conventionnels sans prétendre avoir testé OTC.

### Laboratoire 3 — Validation RPKI

Prépare un validateur et des VRP de laboratoire. Teste trois annonces : une valide, une dont l’origine ne correspond pas, et une route sans ROA applicable. Observe les états. Teste une politique qui rejette Invalid tout en traitant NotFound selon une règle explicite. Ne connecte pas le test à un peering public.

### Laboratoire 4 — Deux route reflectors

Configure un RR pair ou deux RR selon la plate-forme. Vérifie les sessions des clients, les attributs ORIGINATOR_ID/CLUSTER_LIST quand visibles, le NEXT_HOP et la route effectivement retenue. Coupe un RR de manière contrôlée et mesure la convergence. Compare le résultat avec une architecture où les clients ne sont connectés qu’à un seul RR.

### Laboratoire 5 — ADD-PATH contre multipath

Si le support existe, active ADD-PATH de façon compatible des deux côtés et compare les chemins annoncés et reçus. Vérifie séparément le nombre de chemins BGP, les routes installées dans la RIB et les next-hops FIB. Si la plate-forme n’offre pas ADD-PATH, remplace par une analyse de sortie de route-collector ou une maquette documentaire, en indiquant clairement la limite de simulation.

### Laboratoire 6 — Maintenance graceful shutdown

Avec un pair de test, annonce un préfixe par deux chemins. Marque le chemin maintenu avec la communauté GRACEFUL_SHUTDOWN et la préférence prescrite par le runbook. Vérifie la sélection du chemin alternatif avant de fermer la session. Mesure perte de paquets et retour arrière. Ne suppose pas que l’autre AS respecte la communauté sans configuration.

### Laboratoire 7 — Agrégation et trou noir potentiel

Prépare quatre `/24` de documentation pouvant être résumés en un `/22`. Vérifie les contributeurs, crée un résumé selon la syntaxe de la plateforme, teste l’export puis retire un contributeur. Vérifie les routes spécifiques, la route de discard si nécessaire, le résultat RPKI et l’AS_PATH. Assure-toi que l’agrégat n’est pas annoncé à un AS contributeur contrairement aux recommandations modernes.

### Laboratoire 8 — Incident multi-cause

Prépare une situation où la session est `Established`, mais le trafic échoue. Les symptômes possibles doivent être séparés : policy d’import, NEXT_HOP non résolu, RPKI Invalid, route concurrente, filtre FIB ou route retour. N’applique qu’une cause à la fois. Le livrable doit montrer le test qui élimine chaque hypothèse et pas uniquement la commande finale de correction.


## 12. Évaluation avec corrigés

### Questions

1. Quelle différence existe entre un route leak et un détournement d’origine ?
2. Que vérifie RPKI ROV, et que ne vérifie-t-il pas ?
3. Pourquoi `NotFound` ne signifie-t-il pas automatiquement `Invalid` ?
4. Quelle valeur ajoutent les rôles BGP et OTC de RFC 9234 ?
5. Pourquoi les filtres IN et OUT restent-ils nécessaires avec OTC ?
6. Quels sont les rôles d’ORIGINATOR_ID et CLUSTER_LIST dans route reflection ?
7. ADD-PATH et ECMP sont-ils équivalents ?
8. Pourquoi une route peut-elle être acceptée par BGP mais absente de la RIB ?
9. Pourquoi LOCAL_PREF est-il surtout un levier de sortie locale ?
10. Pourquoi le prepend ne garantit-il pas le chemin entrant voulu ?
11. Quels risques se cachent derrière un résumé trop large ?
12. Quelle conséquence opérationnelle découle de RFC 9774 pour l’agrégation et AS_SET ?
13. Pourquoi BFD ne garantit-il pas à lui seul une convergence applicative rapide ?
14. Quand Graceful Restart peut-il être risqué ?
15. À quoi sert la communauté GRACEFUL_SHUTDOWN ?
16. Quels contrôles faut-il comparer lorsqu’une route est dans la BGP table mais le trafic échoue ?
17. Pourquoi le nombre de préfixes reçu par peer est-il un indicateur important ?
18. À quoi sert un maximum-prefix et pourquoi faut-il en choisir soigneusement le seuil ?
19. Quelle preuve permet de dire qu’une route a bien été exportée vers un peer ?
20. Quelles données préserver avant de confiner un leak si le temps le permet ?

### Corrigés commentés

**1.** Un leak concerne la propagation contraire à la politique ; un hijack d’origine implique souvent que le préfixe est originaire d’un ASN non autorisé. Les deux peuvent interagir, mais ce ne sont pas les mêmes événements.

**2.** ROV vérifie le couple préfixe/longueur et ASN d’origine vis-à-vis des ROA/VRP. Il ne prouve pas tout l’AS_PATH, la relation commerciale ou la disponibilité du service.

**3.** `NotFound` signifie qu’aucune autorisation applicable n’est présente dans les données de validation. L’absence d’une ROA n’est pas une preuve que le préfixe est mal originaire.

**4.** Les rôles décrivent la relation eBGP dans l’OPEN ; OTC permet d’identifier des routes dont la propagation est restreinte. Cela réduit certains leaks liés à des relations provider/customer/peer.

**5.** OTC ne remplace pas la liste des préfixes autorisés, ne corrige pas toutes les erreurs locales et ne couvre pas toutes les relations complexes. Les politiques explicitent les routes attendues et les limites d’export.

**6.** Ils aident à prévenir certaines boucles de réflexion : l’origine et les clusters déjà traversés peuvent être identifiés selon les règles de route reflection.

**7.** Non. ADD-PATH permet d’annoncer plusieurs chemins ; ECMP concerne l’installation et l’utilisation de plusieurs next-hops dans le forwarding. La politique et l’implémentation décident de l’usage.

**8.** Le chemin peut perdre le best-path, avoir un NEXT_HOP non résolu, être inéligible ou être supplanté par une route préférée dans la RIB.

**9.** LOCAL_PREF exprime une préférence dans le domaine interne BGP. Les voisins externes n’en reçoivent pas la sémantique habituelle ; il faut gérer l’export selon les politiques.

**10.** L’AS distant peut ignorer le prepend, préférer LOCAL_PREF ou un autre attribut, ou sélectionner un préfixe plus spécifique. Le prepend est une influence, pas une garantie.

**11.** Un résumé peut attirer du trafic vers des destinations absentes et masquer des pannes plus spécifiques. Il faut analyser les contributeurs, les routes de discard, la ROA et les règles d’export.

**12.** RFC 9774 déprécie l’origine de routes qui contiennent des segments AS_SET/AS_CONFED_SET. Les conceptions ne doivent plus compter sur ces types pour représenter les AS d’une agrégation.

**13.** BFD accélère la détection de certaines pannes ; BGP doit encore mettre à jour les routes et la FIB, et l’application doit retrouver son chemin.

**14.** Il peut maintenir des routes stale si le forwarding est déjà incorrect. Il faut vérifier la nature de la panne, les capacités négociées et les temporisations.

**15.** Elle permet de signaler une maintenance planifiée et, avec la politique appropriée, de réduire la préférence des routes afin que le trafic se déplace avant la fermeture.

**16.** BGP best path, NEXT_HOP, RIB, FIB, ACL, route retour, MTU, session de pare-feu et disponibilité du service. Capture à plusieurs points si nécessaire.

**17.** Une variation peut révéler un leak, un filtre cassé, une annonce massive ou un changement non prévu. Le volume doit être comparé à une baseline.

**18.** Il limite une propagation excessive ou une explosion de routes. Un seuil trop faible coupe le service ; trop élevé, il protège peu. Baseline, croissance et comportement au franchissement doivent être documentés.

**19.** Une vue Adj-RIB-Out ou commande équivalente montrant le préfixe et ses attributs vers ce voisin, idéalement complétée par la vue côté réception ou un collecteur externe.

**20.** Horodatages, préfixes, AS_PATH, communauté, peer d’entrée/sortie, état RPKI, politiques actives, nombre de routes et symptômes de forwarding. Le confinement ne doit toutefois pas être retardé si le risque exige une action immédiate.


## 13. Runbook de changement BGP expert

### Avant

- [ ] Énoncer la route ou le comportement cible sans ambiguïté.
- [ ] Capturer la configuration et les sorties de référence, avec versions et timestamps.
- [ ] Lister tous les peers affectés et les préfixes concernés.
- [ ] Vérifier les filtres IN/OUT, rôles, communautés, RPKI et maximum-prefix.
- [ ] Préparer le test de route/forwarding et la méthode de rollback.
- [ ] Définir le seuil d’arrêt : perte de session, retrait inattendu, croissance de routes ou perte de service.

### Pendant

- [ ] Changer une seule famille ou politique significative à la fois.
- [ ] Lire les routes reçues, acceptées, best path et exportées.
- [ ] Vérifier la RIB/FIB et une sonde de service depuis un point utilisateur.
- [ ] Surveiller le nombre de routes, les NOTIFICATION, les retraits et les états RPKI.
- [ ] Interrompre l’opération si la portée réelle diffère du plan approuvé.

### Après

- [ ] Vérifier tous les voisins et les préfixes critiques.
- [ ] Vérifier la route de retour et le forwarding réel.
- [ ] Comparer la politique calculée à la politique attendue.
- [ ] Exécuter un test négatif : une route interdite doit rester rejetée.
- [ ] Conserver les preuves et mettre à jour diagramme, inventaire et runbook.


## 14. Commandes et observabilité : quoi prouver

Les commandes ci-dessous sont des familles de commandes Cisco/FRR indicatives. Le nom exact et le format dépendent du logiciel. Vérifie le manuel de la plateforme et préfère les commandes de consultation au début d’une enquête.

| Objectif | Cisco IOS/IOS XE (souvent) | FRRouting (souvent) | Preuve attendue |
|---|---|---|---|
| État des peers | `show ip bgp summary` | `show bgp summary` | Session, durée, compte de préfixes |
| Routes BGP | `show ip bgp` | `show bgp ipv4 unicast` | Préfixes et chemins candidats |
| Un préfixe | `show ip bgp 203.0.113.0` | `show bgp ipv4 unicast 203.0.113.0/24` | Attributs, best path, raison de décision si fournie |
| Routes annoncées | `show ip bgp neighbors ... advertised-routes` | commande équivalente selon version | Adj-RIB-Out vers un peer |
| Routes reçues | commande `received-routes` si soft-reconfiguration/capacités prises en charge | commande `received-routes` selon version | Ce qui est reçu avant/après policy selon les capacités |
| Route RIB | `show ip route 203.0.113.0` | `show ip route 203.0.113.0/24` | Route installée et source |
| Résolution next-hop | `show ip route <next-hop>` | `show ip route <next-hop>` | Chemin pour atteindre le next-hop |
| RPKI | commandes RPKI dépendantes de version | `show rpki`/commande équivalente selon version | État de cache et validation |
| Logs | `show logging` | logs système | Chronologie d’événements |

Ne traite pas une commande d’exemple comme un contrat universel. La même sortie peut omettre des routes non éligibles, ne présenter que le best path ou dépendre d’une fonction de conservation de routes reçues. Documente exactement ce que la commande prouve et ce qu’elle ne montre pas.


## 15. Glossaire d’exploitation

| Terme | Sens utile en production |
|---|---|
| Adj-RIB-In | Vue des routes reçues d’un voisin, avec détails qui dépendent des capacités de l’implémentation |
| Adj-RIB-Out | Routes préparées pour l’annonce à un voisin |
| Best path | Chemin retenu par le processus local de décision BGP |
| OTC | Attribut Only To Customer associé à certains contrôles de fuite de routes |
| ROV | Validation d’origine de route à partir de ROA/VRP |
| ROA / VRP | Autorisation signée / représentation validée utilisée par le routeur pour la validation |
| RIB | Table de routage générale qui reçoit les routes retenues par les protocoles |
| FIB | Structure de transfert utilisée pour diriger les paquets |
| Route leak | Propagation contraire à la politique de routage prévue |
| Route reflector | Routeur qui réfléchit certaines routes iBGP selon les règles établies |
| ORIGINATOR_ID | Attribut utilisé pour identifier le routeur originel d’une route réfléchie |
| CLUSTER_LIST | Liste des clusters de route reflectors traversés dans le mécanisme prévu |
| ADD-PATH | Capacité qui permet d’annoncer plus d’un chemin pour un préfixe |
| ECMP | Utilisation de plusieurs next-hops de coût ou qualité équivalente selon la politique |
| Graceful shutdown | Signal et procédure de maintenance qui préparent le retrait d’un chemin |
| Maximum-prefix | Limite opérationnelle sur le nombre de routes reçues d’un voisin |
| AS_SET | Segment d’AS_PATH dont l’origine de nouvelles annonces est dépréciée par RFC 9774 |


## 16. Références techniques

Les RFC fixent les règles de protocole mais ne garantissent pas que toutes les plateformes présentent les mêmes commandes, capacités ou valeurs par défaut. Pour tout changement, consulter la documentation de la version installée.

- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : https://www.rfc-editor.org/rfc/rfc4271.html
- **RFC 4456 — BGP Route Reflection** : https://www.rfc-editor.org/rfc/rfc4456.html
- **RFC 8212 — Default External BGP (EBGP) Route Propagation Behavior without Policies** : https://www.rfc-editor.org/rfc/rfc8212.html
- **RFC 7454 — BGP Operations and Security** : https://www.rfc-editor.org/rfc/rfc7454.html
- **RFC 8326 — Graceful BGP Session Shutdown** : https://www.rfc-editor.org/rfc/rfc8326.html
- **RFC 9234 — Route Leak Prevention and Detection Using Roles in UPDATE and OPEN Messages** : https://www.rfc-editor.org/rfc/rfc9234.html
- **RFC 9582 — A Profile for Route Origin Authorizations (ROAs)** : https://www.rfc-editor.org/rfc/rfc9582.html
- **RFC 7911 — Advertisement of Multiple Paths in BGP** : https://www.rfc-editor.org/rfc/rfc7911.html
- **RFC 9774 — Deprecation of AS_SET and AS_CONFED_SET in BGP** (publié en mai 2025) : https://www.rfc-editor.org/rfc/rfc9774.html
- **Cisco — BGP Configuration Guide** : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software/products-installation-and-configuration-guides-list.html

## Conclusion — Une politique prouvée vaut mieux qu’une route supposée

Au niveau expert, la difficulté n’est plus seulement de faire monter une session ou de recevoir un préfixe. Il faut démontrer pourquoi une route est acceptée, pourquoi elle est choisie, à qui elle est annoncée, si son origine et sa propagation respectent la politique, si elle est réellement installée, et si le trafic utilise le chemin attendu.

La discipline essentielle est la suivante : **conception explicite, politiques fermées, validation en couches, mesure avant/après et changements réversibles**. BGP contrôle la joignabilité annoncée ; la disponibilité réelle exige aussi un plan de données fonctionnel, des services sains et une supervision qui sait détecter les écarts.
