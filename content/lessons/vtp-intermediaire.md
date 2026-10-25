# VTP et gestion des VLANs — Intermédiaire

**Niveau :** Intermédiaire  
**Durée indicative :** 60 à 90 minutes  
**Prérequis :** maîtrise des VLAN d'accès, des trunks 802.1Q, des modes VTP, des notions de versions VTP et du numéro de révision abordés au niveau Débutant.

Ce cours part du principe que tu sais déjà ce qu'est un VLAN, pourquoi plusieurs commutateurs doivent avoir une base cohérente, et comment créer un domaine VTP simple. L'objectif est maintenant de savoir **exploiter VTP de façon contrôlée**, analyser ses mécanismes de synchronisation, planifier les changements et diagnostiquer les incidents qui apparaissent dans une architecture multi-commutateurs.

Les exemples utilisent la CLI Cisco IOS/IOS XE. Les commandes exactes, les valeurs par défaut et les fonctionnalités disponibles dépendent du modèle et de la version logicielle. Les commandes marquées comme spécifiques à VTPv3 ne doivent être exécutées que sur des équipements qui prennent en charge cette version.

> **Objectifs d'apprentissage**
>
> À la fin du cours, tu dois pouvoir :
>
> - interpréter les paramètres et l'état opérationnel d'un domaine avec `show vtp status` ;
> - expliquer les risques liés au numéro de révision et préparer un commutateur avant son raccordement ;
> - déployer VTPv3 avec un serveur primaire et distinguer ce rôle du simple mode serveur ;
> - choisir entre serveur, client, transparent et off selon un besoin d'exploitation ;
> - analyser les limites de la propagation VTP, notamment pour les VLAN étendus et le pruning ;
> - dépanner méthodiquement une base VLAN incohérente sans aggraver l'incident ;
> - rédiger un plan de changement, des contrôles et un retour arrière.


## 1. Analyse avancée du fonctionnement de VTP

### 1.1. Point de départ : ce que VTP garantit — et ne garantit pas

VTP aide à maintenir une base VLAN cohérente entre les commutateurs qui participent au même domaine avec des paramètres compatibles. Il ne garantit pas, à lui seul, que les terminaux communiqueront. Pour qu'un VLAN soit opérationnel sur un chemin, il faut notamment :

1. que le VLAN existe dans la base locale de chaque commutateur concerné ;
2. que les trunks nécessaires soient opérationnels ;
3. que le VLAN figure dans les listes de VLAN autorisés sur ces trunks ;
4. que STP autorise le chemin de transfert attendu ;
5. que les ports d'accès et les équipements de couche 3 soient correctement configurés.

La distinction essentielle en niveau intermédiaire est celle entre **synchronisation de la base**, **transport du VLAN** et **connectivité de bout en bout**. Ce sont trois contrôles différents.

```text
                 PLAN DE GESTION VTP
          domaine, version, authentification
                         |
                         v
               Base VLAN cohérente ?
                         |
                         v
                  Plan de transport
           trunks + VLAN autorisés + STP
                         |
                         v
                 Connectivité réelle
           ports d'accès + IP + passerelle
```

Une commande `show vlan brief` confirme la présence locale des VLAN ; elle ne prouve pas que le trunk vers le commutateur voisin transporte le VLAN, ni que le chemin STP est actif.

### Schéma animé — une modification VLAN circule dans le domaine

<figure class="lesson-figure" aria-label="Propagation des annonces VTP entre un serveur et des clients">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="270" viewBox="0 0 960 270" role="img" aria-labelledby="vtpflow-title vtpflow-desc">
  <title id="vtpflow-title">Propagation d'une annonce VTP</title>
  <desc id="vtpflow-desc">Un serveur VTP diffuse une mise à jour vers deux commutateurs clients par des trunks.</desc>
  <rect width="960" height="270" rx="18" fill="#0b1220"/>
  <text x="30" y="32" fill="#e2e8f0" font-size="18" font-weight="700" font-family="Arial, sans-serif">Plan de contrôle : la base VLAN est annoncée</text>
  <path d="M245 127 H365 M355 119 L365 127 L355 135" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M565 127 H685 M675 119 L685 127 L675 135" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="30" y="65" width="215" height="125" rx="14" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <rect x="48" y="80" width="78" height="22" rx="11" fill="#34d399"/>
  <text x="87" y="95" text-anchor="middle" fill="#052e22" font-size="11" font-weight="700" font-family="Arial, sans-serif">SOURCE</text>
  <text x="48" y="126" fill="#f8fafc" font-size="20" font-weight="700" font-family="Arial, sans-serif">SW1</text>
  <text x="48" y="148" fill="#a7f3d0" font-size="14" font-family="Arial, sans-serif">VTP Server</text>
  <text x="48" y="170" fill="#d1fae5" font-size="12" font-family="Arial, sans-serif">VLAN 10, 20, 30</text>
  <rect x="365" y="65" width="200" height="125" rx="14" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="385" y="112" fill="#f8fafc" font-size="20" font-weight="700" font-family="Arial, sans-serif">SW2</text>
  <text x="385" y="135" fill="#bae6fd" font-size="14" font-family="Arial, sans-serif">VTP Client</text>
  <text x="385" y="160" fill="#cbd5e1" font-size="12" font-family="Arial, sans-serif">Met à jour sa base</text>
  <rect x="685" y="65" width="245" height="125" rx="14" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="705" y="112" fill="#f8fafc" font-size="20" font-weight="700" font-family="Arial, sans-serif">SW3</text>
  <text x="705" y="135" fill="#bae6fd" font-size="14" font-family="Arial, sans-serif">VTP Client</text>
  <text x="705" y="160" fill="#cbd5e1" font-size="12" font-family="Arial, sans-serif">Reçoit la même annonce</text>
  <g transform="translate(250 127)"><circle r="7" fill="#a7f3d0" stroke="#ffffff" stroke-width="1.5"><animateMotion path="M 0 0 L 105 0" dur="2.2s" repeatCount="indefinite"/></circle></g>
  <g transform="translate(570 127)"><circle r="7" fill="#7dd3fc" stroke="#ffffff" stroke-width="1.5"><animateMotion path="M 0 0 L 105 0" dur="2.2s" begin="0.8s" repeatCount="indefinite"/></circle></g>
  <text x="480" y="222" text-anchor="middle" fill="#94a3b8" font-size="13" font-family="Arial, sans-serif">Les annonces VTP circulent sur le chemin de couche 2 compatible.</text>
  <text x="480" y="244" text-anchor="middle" fill="#fbbf24" font-size="12" font-family="Arial, sans-serif">La présence d'un VLAN ne garantit pas encore la connectivité des postes.</text>
</svg>
<figcaption>Les points animés symbolisent les annonces de contrôle : la version VTP, le domaine, l'authentification, les trunks et le mode des équipements doivent être compatibles.</figcaption>
</figure>

### 1.2. Lire `show vtp status` comme un diagnostic

Ne te limite pas à repérer le nom du domaine. La sortie de `show vtp status` permet généralement d'examiner plusieurs attributs utiles :

| Élément | Question à poser pendant le diagnostic |
|---|---|
| VTP Version | La version est-elle compatible avec les autres commutateurs concernés ? |
| Configuration Revision | La révision est-elle cohérente avec l'historique des changements attendu ? |
| VTP Operating Mode | Le commutateur est-il serveur, client, transparent ou off ? |
| VTP Domain Name | Le nom correspond-il au domaine visé ? |
| Pruning Mode | Le pruning est-il activé et son comportement est-il connu ? |
| VTP Password / Digest | L'authentification est-elle configurée et compatible, lorsque la plateforme expose ces champs ? |
| Primary Server (VTPv3) | Quel équipement détient le rôle primaire pour la base concernée ? |

Les champs exacts varient selon la plateforme et la version. Une sortie différente de celle d'un exemple de cours n'est pas nécessairement une anomalie : compare-la à la documentation de ton modèle.

Commandes de départ :

```cisco
enable
show vtp status
show vlan brief
show interfaces trunk
show running-config | include vtp
```

Sur certaines versions IOS, le filtrage `include` peut s'utiliser sur la configuration complète ; si cette forme n'est pas disponible dans l'environnement utilisé, affiche `show running-config` et relève manuellement les lignes VTP.

### 1.3. Numéro de révision : raisonner au-delà du nombre

Dans le fonctionnement classique de VTPv1/v2, le numéro de révision permet aux commutateurs de distinguer différents états de la base VLAN. Lorsqu'une modification de la base est enregistrée, la révision peut augmenter. Dans certaines conditions, une base reçue avec une révision supérieure peut être considérée comme plus récente et être utilisée pour synchroniser d'autres équipements du domaine.

Le danger n'est donc pas simplement « une grande révision ». Le vrai risque est **une base VLAN inattendue qui est acceptée comme plus récente**, à cause d'une combinaison de domaine, version, paramètres d'authentification, mode et logique de synchronisation compatibles.

Exemple conceptuel en v1/v2 :

```text
Domaine CAMPUS-LAB

Réseau existant :
SW1  révision 18  VLAN 10,20,30,40  (base attendue)
SW2  révision 18  VLAN 10,20,30,40
SW3  révision 18  VLAN 10,20,30,40

Commutateur inconnu préparé ailleurs :
SW-X révision 42  VLAN 10,99        (base inattendue)

Si SW-X est raccordé sans contrôle et que les conditions VTP
permettent l'acceptation de sa base, l'état du domaine peut être
modifié de façon non souhaitée.
```

Ce schéma illustre un risque historique, et ne décrit pas toutes les règles de VTPv3. Il ne faut pas appliquer automatiquement à VTPv3 le même modèle de propagation qu'à v1/v2 : v3 ajoute le mécanisme de serveur primaire et des contrôles supplémentaires.

**Règle d'exploitation :** une révision élevée n'est ni une preuve d'attaque ni une preuve de bonne configuration. Elle doit être expliquée par un historique de changements. Une révision inattendue sur un commutateur inconnu est un motif de suspension du raccordement, pas une invitation à brancher l'équipement pour voir ce qui se passe.

### Schéma animé — pourquoi un commutateur inconnu est risqué

<figure class="lesson-figure" aria-label="Risque d'une base VLAN inattendue avec une révision VTP supérieure">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="vtprev-title vtrev-desc">
  <title id="vtprev-title">Une révision supérieure n'est pas forcément une meilleure base</title>
  <desc id="vtrev-desc">Un commutateur inconnu a une révision plus élevée et une liste de VLAN différente ; son raccordement sans contrôle présente un risque dans certains scénarios VTP historiques.</desc>
  <rect width="960" height="300" rx="18" fill="#0b1220"/>
  <text x="28" y="32" fill="#e2e8f0" font-size="18" font-weight="700" font-family="Arial, sans-serif">Avant le raccordement : inspecter la base et la révision</text>
  <rect x="28" y="70" width="375" height="145" rx="14" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <text x="50" y="100" fill="#a7f3d0" font-size="12" font-weight="700" font-family="Arial, sans-serif">DOMAINE EN PRODUCTION</text>
  <text x="50" y="130" fill="#f8fafc" font-size="20" font-weight="700" font-family="Arial, sans-serif">SW1 / SW2 / SW3</text>
  <text x="50" y="158" fill="#d1fae5" font-size="16" font-family="Arial, sans-serif">Révision : 18</text>
  <text x="50" y="183" fill="#d1fae5" font-size="14" font-family="Arial, sans-serif">VLAN attendus : 10, 20, 30, 40</text>
  <rect x="648" y="70" width="284" height="145" rx="14" fill="#3b1720" stroke="#fb7185" stroke-width="2"/>
  <text x="670" y="100" fill="#fda4af" font-size="12" font-weight="700" font-family="Arial, sans-serif">ÉQUIPEMENT INCONNU</text>
  <text x="670" y="130" fill="#fff1f2" font-size="20" font-weight="700" font-family="Arial, sans-serif">SW-X</text>
  <text x="670" y="158" fill="#fecdd3" font-size="16" font-family="Arial, sans-serif">Révision : 42</text>
  <text x="670" y="183" fill="#fecdd3" font-size="14" font-family="Arial, sans-serif">VLAN : 10, 99</text>
  <path d="M645 145 H430 M440 137 L430 145 L440 153" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="8 6" stroke-linecap="round" stroke-linejoin="round"/>
  <g transform="translate(640 145)"><circle r="8" fill="#fb7185" stroke="#fff1f2" stroke-width="1.5"><animateMotion path="M 0 0 L -195 0" dur="2.8s" repeatCount="indefinite"/></circle></g>
  <circle cx="535" cy="145" r="21" fill="#450a0a" stroke="#f87171" stroke-width="2"/>
  <path d="M526 136 L544 154 M544 136 L526 154" stroke="#fecaca" stroke-width="4" stroke-linecap="round"/>
  <text x="480" y="245" text-anchor="middle" fill="#fda4af" font-size="13" font-weight="700" font-family="Arial, sans-serif">Ne pas raccorder sans procédure de préparation</text>
  <text x="480" y="269" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="Arial, sans-serif">Scénario de risque historique v1/v2, si les conditions d'acceptation sont réunies.</text>
</svg>
<figcaption>La révision 42 ne signifie pas que la base est meilleure : la liste VLAN de SW-X est inattendue. Isole l'équipement, sauvegarde son état et applique la procédure adaptée au modèle avant raccordement.</figcaption>
</figure>

### 1.4. Procédure contrôlée avant d'ajouter un commutateur

Avant le raccordement d'un nouveau commutateur dans un domaine VTP existant :

1. **Isoler l'équipement.** Ne le relie pas directement aux trunks du réseau de production pendant l'inspection initiale.
2. **Sauvegarder l'état reçu.** Enregistre sa configuration et les sorties utiles des commandes de diagnostic.
3. **Inspecter VTP.** Relève le domaine, le mode, la version, la révision et les paramètres d'authentification disponibles.
4. **Comparer la base VLAN.** Vérifie les identifiants, noms et VLAN réservés ou spéciaux présents sur l'équipement.
5. **Choisir la procédure de préparation.** Utilise la méthode documentée pour le modèle et la version logicielle afin de neutraliser le risque d'une ancienne base.
6. **Vérifier hors production.** Confirme le domaine, le mode attendu et l'état de la base avant d'établir les trunks de raccordement.
7. **Raccorder et surveiller.** Contrôle ensuite `show vtp status`, `show vlan brief` et `show interfaces trunk` sur les équipements concernés.

Il n'existe pas une procédure universelle et sûre de remise à zéro valable pour toutes les plateformes Cisco. Selon le modèle et le logiciel, les mécanismes de stockage de la base VLAN diffèrent. N'efface pas arbitrairement des fichiers de base ni la configuration d'un commutateur de production : sauvegarde, vérifie la documentation du modèle, puis suis la procédure constructeur.

### 1.5. Domaine VTP, trunk et propagation : diagnostiquer de proche en proche

Pour qu'une annonce VTP atteigne les commutateurs concernés, il faut un chemin de commutation de couche 2 compatible. Dans un réseau à plusieurs trunks, inspecte le chemin complet plutôt que seulement le lien du serveur vers le premier client.

Exemple :

```text
SW1 (serveur) ===== SW2 (transit) ===== SW3 (client)
     trunk A-B             trunk B-C

La base VLAN ne se synchronise pas sur SW3.

Contrôles :
  1. Domaine/version/authentification sur SW1, SW2 et SW3
  2. État opérationnel du trunk A-B
  3. État opérationnel du trunk B-C
  4. Mode VTP de SW2 et comportement de relais de la version
  5. État local de la base sur SW3
```

Un switch transparent ne synchronise pas sa propre base VLAN à partir des annonces reçues. Selon la version VTP, il peut cependant relayer des annonces. Un équipement en mode off, lorsqu'il est pris en charge, ne relaie pas les annonces. Ce comportement doit être intégré au plan de chemin et vérifié sur la version réelle.

Les annonces VTP et les VLAN utilisateur n'ont pas la même fonction. La présence d'un trunk opérationnel n'assure pas que tous les VLAN utilisateur sont autorisés sur ce trunk ; de même, le fait de limiter les VLAN utilisateur sur un trunk ne doit pas être confondu avec une vérification du transport des annonces de contrôle.

### Schéma animé — synchronisation VTP et transport des données sont deux choses différentes

<figure class="lesson-figure" aria-label="Un trunk peut transporter les annonces VTP mais bloquer un VLAN utilisateur non autorisé">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="vtptrunk-title vtptrunk-desc">
  <title id="vtptrunk-title">Synchronisation correcte, transport du VLAN 30 incorrect</title>
  <desc id="vtptrunk-desc">Les deux bases contiennent le VLAN 30, mais le trunk n'autorise que les VLAN 10 et 20 : les données VLAN 30 ne traversent pas.</desc>
  <rect width="960" height="330" rx="18" fill="#0b1220"/>
  <text x="28" y="31" fill="#e2e8f0" font-size="18" font-weight="700" font-family="Arial, sans-serif">Vérifie séparément le plan de contrôle et le plan de données</text>
  <rect x="28" y="57" width="250" height="112" rx="13" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <text x="48" y="83" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW1 · Server</text>
  <text x="48" y="108" fill="#d1fae5" font-size="13" font-family="Arial, sans-serif">Base VLAN : 10, 20, 30</text>
  <text x="48" y="133" fill="#a7f3d0" font-size="12" font-family="Arial, sans-serif">Annonce envoyée</text>
  <rect x="682" y="57" width="250" height="112" rx="13" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="702" y="83" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW2 · Client</text>
  <text x="702" y="108" fill="#bae6fd" font-size="13" font-family="Arial, sans-serif">Base VLAN : 10, 20, 30</text>
  <text x="702" y="133" fill="#bae6fd" font-size="12" font-family="Arial, sans-serif">VLAN 30 connu localement</text>
  <path d="M278 100 H682 M670 92 L682 100 L670 108" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <g transform="translate(290 100)"><circle r="6" fill="#7dd3fc" stroke="#ffffff" stroke-width="1.5"><animateMotion path="M 0 0 L 365 0" dur="3s" repeatCount="indefinite"/></circle></g>
  <text x="480" y="80" text-anchor="middle" fill="#7dd3fc" font-size="12" font-weight="700" font-family="Arial, sans-serif">ANNONCE VTP</text>
  <path d="M278 224 H420 M540 224 H682" fill="none" stroke="#f87171" stroke-width="4" stroke-dasharray="7 6" stroke-linecap="round"/>
  <g transform="translate(290 224)"><circle r="6" fill="#fb7185" stroke="#fff1f2" stroke-width="1.5"><animateMotion path="M 0 0 L 115 0 L 48 0" dur="2.1s" repeatCount="indefinite"/></circle></g>
  <circle cx="480" cy="224" r="22" fill="#450a0a" stroke="#f87171" stroke-width="2"/>
  <path d="M470 214 L490 234 M490 214 L470 234" stroke="#fecaca" stroke-width="4" stroke-linecap="round"/>
  <text x="480" y="197" text-anchor="middle" fill="#fda4af" font-size="12" font-weight="700" font-family="Arial, sans-serif">TRUNK</text>
  <text x="480" y="260" text-anchor="middle" fill="#fecaca" font-size="13" font-weight="700" font-family="Arial, sans-serif">VLAN autorisés : 10, 20 — VLAN 30 absent</text>
  <text x="480" y="295" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial, sans-serif">Résultat : la base est synchronisée, mais le trafic utilisateur du VLAN 30 est bloqué sur ce lien.</text>
</svg>
<figcaption>Pour prouver la connectivité, combine `show vtp status`, `show vlan brief` et `show interfaces trunk`. La liste de VLAN autorisés se contrôle indépendamment de la présence du VLAN dans la base.</figcaption>
</figure>

### 1.6. Choisir le mode d'exploitation selon le besoin

Le choix du mode est une décision d'architecture et d'exploitation, pas uniquement une préférence de syntaxe.

| Besoin | Choix souvent adapté | Conditions et précautions |
|---|---|---|
| Administrer une base VLAN centralisée dans un petit domaine contrôlé | Server + clients, si la plateforme et le processus le justifient | Protéger le serveur, contrôler les changements et vérifier les révisions |
| Utiliser VTPv3 avec contrôle d'autorité sur la base | Server VTPv3 avec primaire défini | Promouvoir le primaire selon la procédure et documenter les rôles |
| Gérer les VLAN localement sans synchroniser la base reçue | Transparent | Prévoir la cohérence manuelle ; comprendre le relais d'annonces selon la version |
| Ne participer ni au traitement ni au relais des annonces VTP | Off, si disponible | Vérifier la prise en charge sur le modèle utilisé |
| Ne pas dépendre de VTP pour un réseau simple ou très contrôlé | Gestion locale transparente/off | Mettre en place un inventaire des VLAN et une procédure cohérente de changements |

Dans un environnement de production, la bonne question n'est pas « quel mode est le meilleur dans tous les cas ? », mais « quel modèle de gestion réduit le plus le risque et l'effort pour cette architecture ? » VTP simplifie la diffusion mais augmente le rayon d'impact possible d'une modification mal maîtrisée.

### 1.7. VTPv3 : mode serveur et serveur primaire

VTPv3 distingue le mode opérationnel serveur du rôle de **serveur primaire** pour une base de données donnée. Un commutateur peut fonctionner en mode serveur VTPv3 sans être celui qui détient actuellement le rôle primaire. Le mécanisme primaire sert à encadrer l'autorité qui publie les changements de base.

Points à retenir :

- le rôle primaire est associé à une base prise en charge, par exemple la base VLAN ;
- l'opération de promotion se réalise en mode EXEC privilégié sur les plateformes qui prennent en charge la commande ;
- une prise de contrôle peut avertir ou écraser les états concurrents selon la commande, la confirmation et les options utilisées ;
- l'option `force`, lorsqu'elle est disponible, peut avoir des effets sur les serveurs concurrents et ne doit pas être utilisée par réflexe ;
- certains événements peuvent faire perdre l'état primaire et nécessiter une nouvelle promotion suivant le comportement de la plateforme.

Exemple illustratif VTPv3 sur une plateforme compatible :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode server
vtp version 3
end

! En EXEC privilégié, après vérification du domaine et de la base :
vtp primary vlan
show vtp status
```

La disponibilité et la syntaxe de ces commandes doivent être vérifiées sur le matériel et le logiciel réels. Certaines implémentations présentent des différences ou exigent des étapes préalables. N'exécute pas de commande de promotion sur un réseau de production sans avoir confirmé l'équipement cible, la base sélectionnée et l'autorité attendue.

### Schéma animé — le serveur primaire VTPv3

<figure class="lesson-figure" aria-label="Rôle du serveur primaire VTPv3 dans les modifications de la base VLAN">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="290" viewBox="0 0 960 290" role="img" aria-labelledby="vtp3-title vtp3-desc">
  <title id="vtp3-title">Le serveur primaire VTPv3 publie les modifications de la base sélectionnée</title>
  <desc id="vtp3-desc">Un serveur primaire, un serveur VTP ordinaire et un client ont des rôles distincts. Le serveur primaire autorisé publie la modification de base VLAN.</desc>
  <rect width="960" height="290" rx="18" fill="#0b1220"/>
  <text x="28" y="32" fill="#e2e8f0" font-size="18" font-weight="700" font-family="Arial, sans-serif">VTPv3 : ne confonds pas mode serveur et serveur primaire</text>
  <path d="M250 90 H370 M595 90 H710" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>
  <path d="M360 82 L370 90 L360 98 M700 82 L710 90 L700 98" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <g transform="translate(260 90)"><circle r="7" fill="#a7f3d0" stroke="#ffffff" stroke-width="1.5"><animateMotion path="M 0 0 L 440 0" dur="3.4s" repeatCount="indefinite"/></circle></g>
  <rect x="30" y="108" width="220" height="110" rx="14" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <rect x="47" y="121" width="158" height="23" rx="11" fill="#34d399"/>
  <text x="126" y="137" text-anchor="middle" fill="#052e22" font-size="11" font-weight="700" font-family="Arial, sans-serif">SERVEUR PRIMAIRE</text>
  <text x="48" y="171" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW1</text>
  <text x="48" y="195" fill="#a7f3d0" font-size="12" font-family="Arial, sans-serif">Autorisé à publier</text>
  <rect x="370" y="108" width="225" height="110" rx="14" fill="#342817" stroke="#fbbf24" stroke-width="2"/>
  <text x="390" y="143" fill="#fef3c7" font-size="12" font-weight="700" font-family="Arial, sans-serif">MODE SERVEUR</text>
  <text x="390" y="171" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW2</text>
  <text x="390" y="195" fill="#fde68a" font-size="12" font-family="Arial, sans-serif">Pas forcément primaire</text>
  <rect x="710" y="108" width="220" height="110" rx="14" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="730" y="151" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW3</text>
  <text x="730" y="175" fill="#bae6fd" font-size="14" font-family="Arial, sans-serif">VTP Client</text>
  <text x="730" y="197" fill="#cbd5e1" font-size="12" font-family="Arial, sans-serif">Reçoit la base publiée</text>
  <text x="480" y="248" text-anchor="middle" fill="#fbbf24" font-size="13" font-weight="700" font-family="Arial, sans-serif">Le rôle primaire concerne une base précise, par exemple la base VLAN.</text>
  <text x="480" y="270" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="Arial, sans-serif">Contrôle la prise en charge et la syntaxe sur la version IOS/IOS XE utilisée.</text>
</svg>
<figcaption>VTPv3 ajoute une autorité primaire pour la base concernée. Avant d'utiliser `vtp primary vlan`, vérifie la version, la syntaxe et les implications sur l'équipement réel.</figcaption>
</figure>

### 1.8. Déployer VTPv3 sans confondre la version avec l'architecture

Une migration vers VTPv3 n'est pas simplement l'exécution de `vtp version 3` sur tous les commutateurs. Avant la migration, il faut connaître :

- les versions et fonctionnalités prises en charge par chaque modèle ;
- le domaine et les paramètres d'authentification actuels ;
- les VLAN présents et leur source de référence ;
- les éventuels VLAN de plage étendue ;
- l'état VTPv3 attendu et le rôle primaire prévu ;
- les dépendances entre VLAN, trunks, STP et services de production ;
- la procédure de retour arrière et ses limites.

Plan de migration générique :

1. Constituer une sauvegarde vérifiée des configurations et un inventaire de la base VLAN.
2. Vérifier la compatibilité de chaque commutateur et choisir une fenêtre de changement.
3. Préparer une procédure adaptée à la gamme et à la version IOS/IOS XE ; ne pas improviser une séquence universelle.
4. Migrer selon l'ordre recommandé par Cisco pour la plateforme choisie.
5. Définir l'équipement autorisé à être primaire pour la base VLAN.
6. Contrôler le domaine, la version active, le rôle primaire, la base VLAN et les trunks après chaque étape.
7. Tester les services dépendants et consigner les résultats.

Il ne faut pas mélanger au hasard des commandes issues de guides pour différentes familles Catalyst. Les paramètres par défaut et les syntaxes changent d'une famille à l'autre.

### 1.9. VLAN de plage normale et plage étendue

La différence entre plage normale et plage étendue est importante dès que la base dépasse les usages courants.

| Plage d'identifiants | Comportement VTP à connaître |
|---|---|
| VLAN 1 à 1005 | Plage historique normale ; VTPv1/v2 propagent la base de VLAN de cette plage sous réserve des VLAN réservés et de la plateforme |
| VLAN 1002 à 1005 | Identifiants historiquement réservés sur de nombreuses plateformes ; ne pas les traiter comme des VLAN utilisateur ordinaires |
| VLAN 1006 à 4094 | Plage étendue ; la propagation via VTP nécessite VTPv3 et une plateforme compatible |

La possibilité de créer localement un VLAN de plage étendue ne prouve pas que sa définition sera propagée par v1/v2. Elle ne prouve pas non plus que le commutateur supporte la même limite fonctionnelle que les autres membres du domaine.

Exemple conceptuel : si un plan de réseau exige VLAN 1200 et VLAN 2400, valide d'abord la prise en charge de VTPv3 par les commutateurs, l'état de la base VLAN, la méthode de diffusion attendue et les restrictions éventuelles. Ne change pas de version uniquement parce qu'une commande de création locale échoue à se synchroniser.

### 1.10. Pruning VTP : ce qui peut être supprimé du transit

Le pruning VTP réduit certaines diffusions inutiles sur un trunk lorsque les équipements en aval n'ont pas besoin du VLAN concerné. Il ne supprime pas le VLAN de la base, n'assigne pas les ports et ne remplace pas la liste explicite des VLAN autorisés.

Trois notions doivent être distinguées :

- **VLAN existant** : il figure dans la base du commutateur ;
- **VLAN autorisé** : la configuration du trunk permet à ce VLAN de traverser le lien ;
- **VLAN éligible au pruning** : le VLAN peut être candidat à l'élagage selon l'état de la fonction et les besoins signalés par la topologie.

Sur les plateformes Cisco documentées, VLAN 1 et les VLAN 1002 à 1005 ne sont pas éligibles au pruning ; les VLAN de plage étendue ne le sont pas non plus. Les VLAN éligibles par défaut et l'étendue d'application du pruning varient selon la version : en v1/v2, son activation sur le serveur peut s'appliquer au domaine ; en VTPv3, il peut être nécessaire de l'activer explicitement sur chaque équipement. Vérifie la documentation de la version exacte.

Avant d'activer le pruning :

1. cartographier les VLAN utilisés derrière chaque trunk ;
2. confirmer les VLAN autorisés et les chemins redondants ;
3. sauvegarder et documenter l'état initial ;
4. activer dans une fenêtre de changement ;
5. vérifier les états de pruning et tester les services qui dépendent du transit.

Le pruning n'est pas une frontière de sécurité. Pour limiter réellement le transport, configure aussi les listes explicites de VLAN autorisés sur les trunks et contrôle-les régulièrement.

### Schéma animé — rôle du VTP pruning

<figure class="lesson-figure" aria-label="Schéma du VTP pruning : les floods éligibles continuent sur une branche qui utilise le VLAN et sont limités sur une branche qui n'en a pas besoin">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="pruning-title pruning-desc">
  <title id="pruning-title">VTP pruning : limiter les floods inutiles sans supprimer le VLAN</title>
  <desc id="pruning-desc">Depuis SW1, un flux de diffusion éligible du VLAN 20 suit le trunk vers SW2, où le VLAN est utilisé. Sur la branche vers SW3, qui n'a aucun port de ce VLAN en aval, le trafic éligible est limité par le pruning. Le trunk et la définition du VLAN ne sont pas supprimés.</desc>
  <rect width="960" height="330" rx="18" fill="#0b1220"/>
  <text x="480" y="31" text-anchor="middle" fill="#e2e8f0" font-size="19" font-weight="700" font-family="Arial, sans-serif">VTP pruning : où le flood du VLAN 20 est-il nécessaire ?</text>
  <rect x="30" y="110" width="190" height="112" rx="14" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <text x="52" y="143" fill="#f8fafc" font-size="18" font-weight="700" font-family="Arial, sans-serif">SW1</text>
  <text x="52" y="166" fill="#a7f3d0" font-size="14" font-family="Arial, sans-serif">Distribution</text>
  <text x="52" y="192" fill="#d1fae5" font-size="12" font-family="Arial, sans-serif">VLAN 10 · 20 · 30</text>

  <rect x="560" y="52" width="350" height="83" rx="14" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="585" y="80" fill="#f8fafc" font-size="17" font-weight="700" font-family="Arial, sans-serif">SW2 · Branche A</text>
  <text x="585" y="102" fill="#bae6fd" font-size="13" font-family="Arial, sans-serif">VLAN 20 utilisé en aval</text>
  <text x="585" y="120" fill="#cbd5e1" font-size="12" font-family="Arial, sans-serif">Le flood éligible doit continuer</text>

  <rect x="560" y="195" width="350" height="83" rx="14" fill="#2b1b25" stroke="#fb7185" stroke-width="2" stroke-dasharray="7 5"/>
  <text x="585" y="222" fill="#fff1f2" font-size="17" font-weight="700" font-family="Arial, sans-serif">SW3 · Branche B</text>
  <text x="585" y="244" fill="#fecdd3" font-size="13" font-family="Arial, sans-serif">Aucun besoin du VLAN 20 en aval</text>
  <text x="585" y="262" fill="#ffe4e6" font-size="12" font-family="Arial, sans-serif">Le flood éligible peut être élagué</text>

  <!-- Chemin utile : la ligne et l'animation suivent exactement les mêmes coordonnées. -->
  <path d="M220 142 H330 L400 94 H548" fill="none" stroke="#38bdf8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M538 86 L548 94 L538 102" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="220" cy="142" r="6" fill="#7dd3fc" stroke="#e0f2fe" stroke-width="1.5">
    <animateMotion path="M 0 0 L 110 0 L 180 -48 L 328 -48" dur="3.8s" repeatCount="indefinite"/>
  </circle>

  <!-- Branche élaguée : le X marque l'arrêt du flood illustré, pas la coupure du trunk. -->
  <path d="M220 188 H330 L390 230 H430" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="8 7" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>
  <path d="M450 230 H510" fill="none" stroke="#fb7185" stroke-width="2.5" stroke-dasharray="4 8" opacity="0.3"/>
  <circle cx="440" cy="230" r="15" fill="#450a0a" stroke="#f87171" stroke-width="2"/>
  <path d="M434 224 L446 236 M446 224 L434 236" stroke="#fecaca" stroke-width="3.5" stroke-linecap="round"/>
  <text x="475" y="211" text-anchor="middle" fill="#fda4af" font-size="11" font-weight="700" font-family="Arial, sans-serif">FLOOD LIMITÉ</text>
  <text x="480" y="309" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="Arial, sans-serif">Le pruning limite certains floods ; il ne supprime ni le VLAN de la base ni l'autorisation du trunk.</text>
</svg>
<figcaption>Le point bleu suit uniquement le chemin où le VLAN 20 est nécessaire. Le X représente la limitation de certains trafics de diffusion, multicast et unicast inconnu vers une branche qui n'en a pas besoin. Les trunks restent opérationnels ; les effets exacts dépendent de l'éligibilité du VLAN, de la version et de la topologie.</figcaption>
</figure>

### 1.11. Base VLAN et configuration de démarrage : deux plans à contrôler

Il faut distinguer la configuration IOS classique (interfaces, descriptions, paramètres VTP et autres commandes) de la base VLAN et des mécanismes qui la conservent. Les modalités de stockage et de sauvegarde varient en fonction de la famille du commutateur, de la version VTP et du logiciel.

La commande suivante sauvegarde généralement la configuration active vers la configuration de démarrage :

```cisco
copy running-config startup-config
```

Mais elle ne doit pas être considérée comme une preuve universelle que toute base VLAN et tous les états VTP sont sauvegardés de la même façon. Les procédures d'exploitation doivent préciser comment sauvegarder, inspecter et restaurer la base VLAN sur la plateforme concernée. Une sauvegarde complète inclut les éléments réellement nécessaires à la récupération, pas uniquement la sortie d'une commande.

### 1.12. VTP et sécurité des trunks

Une base VTP cohérente ne protège pas contre un trunk mal configuré. Une pratique d'exploitation robuste consiste à :

- configurer explicitement en trunk les interfaces destinées aux liaisons entre commutateurs, si la plateforme le permet ;
- limiter chaque trunk aux VLAN nécessaires à son rôle ;
- désactiver ou sécuriser les interfaces inutilisées selon la politique de l'organisation ;
- contrôler les négociations dynamiques et les comportements de trunk spécifiques à la plateforme ;
- protéger l'accès de gestion des commutateurs ;
- documenter quels équipements ont le droit de modifier la base VLAN.

N'utilise pas VTP comme contrôle d'accès réseau. L'authentification VTP concerne les annonces et ne remplace pas la protection de la console, des sessions SSH, des comptes privilégiés ou des interfaces physiques.

### 1.13. Construire une preuve de synchronisation

Pour démontrer qu'une modification a été propagée correctement, collecte des preuves à plusieurs niveaux. Un seul indicateur ne suffit pas.

| Niveau de contrôle | Commandes indicatives | Résultat attendu |
|---|---|---|
| Paramètres du domaine | `show vtp status` | Domaine/version/mode conformes au plan |
| Base VLAN locale | `show vlan brief` | VLAN et noms attendus présents |
| Transport | `show interfaces trunk` | Trunks opérationnels et VLAN nécessaires autorisés |
| État de couche 2 | `show spanning-tree vlan 20` | Chemin cohérent avec la topologie prévue |
| Apprentissage MAC | `show mac address-table dynamic vlan 20` | Adresses apprises sur les ports attendus, si du trafic a été généré |
| Connectivité | Tests de ping et tests applicatifs appropriés | Service réellement fonctionnel, sans confondre ping et validation complète |

Garde des sorties avant et après le changement. Elles facilitent la comparaison et évitent de te fier à la mémoire ou à une impression visuelle.

### 1.14. Exemple de décision d'architecture

Une entreprise exploite six commutateurs sur un même site. Elle crée rarement de nouveaux VLAN, mais une erreur de diffusion à l'ensemble du site aurait un impact important. Deux choix peuvent être évalués :

**Option A — VTP centralisé.** Un nombre limité de commutateurs autorisés gère la base et les autres la synchronisent. Cette option réduit la répétition de tâches mais impose une procédure stricte d'administration, de contrôle de révision, de préparation des nouveaux équipements et de restauration.

**Option B — gestion locale en transparent/off.** Chaque commutateur maintient sa base. Cette option réduit la propagation automatique d'une base incorrecte, mais augmente le risque de dérive entre commutateurs si l'équipe ne dispose pas d'un inventaire fiable, de configurations standardisées et de contrôles réguliers.

La décision dépend du modèle opérationnel, de la compatibilité et de la capacité de l'équipe à maintenir la cohérence. Il n'existe pas de choix universel : un domaine VTP bien gouverné peut être efficace, tandis qu'une configuration locale bien automatisée peut être plus adaptée à d'autres réseaux.


## 2. Configuration et pratique intermédiaire

### 2.1. Laboratoire : architecture et règles de départ

Le laboratoire utilise trois commutateurs Cisco Catalyst ou simulateurs compatibles. Il est destiné à un environnement isolé, tel que Cisco Packet Tracer lorsque les fonctions nécessaires y sont simulées, ou un lab physique qui ne transporte aucun trafic de production.

```text
                      CAMPUS-LAB

       +-------------------+       +-------------------+
       | SW1               |=======| SW2               |
       | VTP serveur       | trunk | VTP client        |
       | base de référence |       | contrôle local    |
       +-------------------+       +-------------------+
                 |
                 | trunk
                 |
       +-------------------+
       | SW3               |
       | VTP transparent   |
       | base locale       |
       +-------------------+

VLAN de test : 10 ADMIN-LAB, 20 USERS-LAB, 30 VOIP-LAB
Les noms et ports sont illustratifs : adapte-les à ton équipement.
```

Précautions :

- ne connecte pas le lab à ton LAN domestique ou professionnel sans une séparation adaptée ;
- ne réutilise pas un nom de domaine VTP de production dans un lab relié au réseau réel ;
- vérifie que les commandes sont prises en charge par le simulateur ;
- sauvegarde les fichiers de projet et les configurations avant les exercices ;
- réalise les scénarios de révision uniquement dans l'environnement isolé.

### 2.2. Phase A : relever l'état initial

Sur chaque commutateur, commence par collecter les sorties :

```cisco
show version
show vtp status
show vlan brief
show interfaces trunk
show running-config
```

Crée une fiche par équipement :

| Champ | SW1 | SW2 | SW3 |
|---|---|---|---|
| Nom du domaine | À relever | À relever | À relever |
| Version VTP | À relever | À relever | À relever |
| Mode | À relever | À relever | À relever |
| Révision | À relever | À relever | À relever |
| VLAN attendus | À relever | À relever | À relever |
| Trunks opérationnels | À relever | À relever | À relever |

Cette phase n'est pas une formalité. Le même dépannage sera beaucoup plus rapide si tu sais ce qui était présent avant le changement.

### 2.3. Phase B : préparer un domaine contrôlé

Sur les équipements compatibles avec les commandes VTP classiques, une configuration de lab peut ressembler à ceci.

**SW1 — serveur VTP :**

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode server
vtp version 2
end
show vtp status
```

**SW2 — client VTP :**

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode client
vtp version 2
end
show vtp status
```

**SW3 — base locale indépendante :**

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode transparent
vtp version 2
end
show vtp status
```

Ces blocs sont des exemples pour un matériel qui accepte ces commandes. Le nom du domaine, le mode et la version doivent être compatibles avec le plan prévu. Si le lab supporte VTPv3 et que tu souhaites tester son serveur primaire, réalise la migration dans une phase distincte au lieu de mélanger v2 et v3 au hasard.

Pour ce premier scénario intermédiaire, configure les trunks explicitement sur les interfaces de liaison, puis vérifie le statut sur les deux extrémités. Exemple de syntaxe classique :

```cisco
configure terminal
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
end
show interfaces trunk
```

Les noms d'interface, l'encapsulation et les commandes acceptées varient selon la plateforme. Adapte l'interface distante et vérifie les états opérationnels avant de continuer.

### 2.4. Phase C : créer une base de référence

Sur SW1, après avoir contrôlé le domaine et le mode serveur :

```cisco
configure terminal
vlan 10
 name ADMIN-LAB
vlan 20
 name USERS-LAB
vlan 30
 name VOIP-LAB
end
show vlan brief
show vtp status
```

Sur SW2, laisse le temps à la synchronisation de se produire puis vérifie :

```cisco
show vtp status
show vlan brief
```

Résultat attendu : la base de SW2 reflète les VLAN diffusés par SW1 selon le mode, la version et les capacités de la plateforme. SW3 est en mode transparent ; il garde sa base locale indépendante. Ne t'attends donc pas à ce qu'il adopte automatiquement les trois VLAN simplement parce qu'il reçoit des annonces.

Pour tester le trafic utilisateur, configure ensuite les ports d'accès et les trunks nécessaires. La propagation VTP n'affecte pas automatiquement un port d'accès et ne configure pas d'adressage IP.

### 2.5. Phase D : diagnostiquer une mauvaise synchronisation

Simule une panne non destructive, par exemple une différence de domaine dans le lab. Sur SW2, relève l'état avant de faire la modification :

```cisco
show vtp status
show vlan brief
```

Dans le cadre du lab seulement, configure temporairement un nom de domaine différent :

```cisco
configure terminal
vtp domain CAMPUS-TEST
end
show vtp status
```

Observe la différence entre les paramètres de SW1 et de SW2, puis restaure le domaine convenu :

```cisco
configure terminal
vtp domain CAMPUS-LAB
end
show vtp status
show vlan brief
```

Le résultat exact dépend du système simulé et de la base déjà présente. L'objectif est d'apprendre à expliquer le symptôme à partir des paramètres observés, plutôt que de multiplier les modifications aléatoires.

### 2.6. Phase E : tester un trunk qui n'autorise pas le VLAN

Dans le lab, suppose que le VLAN 20 existe des deux côtés, mais n'est pas autorisé sur le trunk entre SW1 et SW2. Relève d'abord la liste effective :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/1 switchport
show vlan brief
```

Si le plan prévoit le VLAN 20, adapte la liste avec la syntaxe correspondant à l'équipement. Sur certaines plateformes, une commande d'ajout conserve la liste existante ; une commande sans le mot-clé `add` peut remplacer la liste. Ne remplace jamais une liste sans connaître les autres VLAN qui en dépendent.

Après correction, exécute à nouveau :

```cisco
show interfaces trunk
show vlan brief
show spanning-tree vlan 20
```

Retiens le résultat central : **un VLAN connu localement peut rester inutilisable sur un lien qui ne le transporte pas**. VTP et les listes de VLAN autorisés répondent à deux questions différentes.

### 2.7. Phase F : préparer l'analyse du numéro de révision

Ce scénario doit rester dans un simulateur ou un environnement entièrement isolé. Le but est d'observer la révision, pas de provoquer une perte de service.

1. Relever `show vtp status` sur les commutateurs du lab.
2. Créer une modification contrôlée sur le serveur et observer l'évolution de la révision lorsque la plateforme l'expose.
3. Documenter les VLAN présents avant et après.
4. Comparer la valeur attendue à celle observée.
5. Restaurer la base de référence par une procédure contrôlée et vérifier le résultat.

Ne cherche pas à provoquer volontairement une propagation destructrice à partir d'une base « plus récente ». Un exercice de lecture de sorties et d'explication du mécanisme suffit à apprendre le risque. Si un formateur souhaite démontrer le comportement historique de v1/v2, il doit préparer une topologie isolée, un plan de restauration et une version connue avant de commencer.

### 2.8. Phase G : aperçu du serveur primaire VTPv3

Uniquement si tous les équipements utilisés prennent en charge VTPv3, crée un lab dédié à cette version. Avant la configuration, relève la version, le domaine, la base VLAN et les restrictions du simulateur. Suis ensuite la procédure Cisco propre à la gamme.

Exemple illustratif pour un commutateur choisi comme candidat serveur primaire :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp mode server
vtp version 3
end

! Vérifier d'abord le domaine et les états des équipements
show vtp status

! Promotion de la base VLAN en mode EXEC privilégié,
! uniquement sur une plateforme compatible et dans le lab :
vtp primary vlan
show vtp status
```

Ne copie pas `vtp primary vlan force` sans raison. L'option `force`, lorsqu'elle est prise en charge, peut forcer une prise de contrôle malgré des états concurrents. Elle ne constitue pas la méthode de dépannage par défaut.

Contrôles attendus :

- VTPv3 est actif sur les équipements préparés ;
- le domaine correspond au plan ;
- le commutateur primaire est celui qui a été choisi et documenté ;
- les VLAN et les annonces se comportent conformément à la documentation de la plateforme ;
- les trunks et les VLAN autorisés sont corrects.

### 2.9. Phase H : étude des VLAN de plage étendue

Si le simulateur et la gamme prennent en charge la fonction, établis pourquoi une configuration VTPv1/v2 peut ne pas propager la définition d'un VLAN de plage étendue. Dans la documentation de la plateforme, identifie la version nécessaire à la propagation de VLAN 1006 à 4094, puis vérifie l'état réel après configuration.

Ne déduis pas qu'une commande acceptée localement signifie que le VLAN a été distribué au domaine. Compare :

```cisco
show vtp status
show vlan brief
show interfaces trunk
```

Observe les limites de ton environnement. Certains simulateurs ne reproduisent pas toutes les fonctions de VTPv3 ; un résultat absent dans un simulateur peut donc refléter une limitation de l'outil plutôt qu'une erreur de conception.

### 2.10. Rapport de fin de laboratoire

Ton rapport doit contenir :

1. un schéma avec le rôle VTP de chaque commutateur et les trunks ;
2. les valeurs initiales puis finales de domaine, version, mode et révision ;
3. les sorties `show vtp status`, `show vlan brief` et `show interfaces trunk` avant et après les changements ;
4. les VLAN autorisés par trunk et les ports d'accès associés ;
5. une explication d'au moins un incident testé ;
6. la cause racine, la correction et les tests qui démontrent le retour à l'état attendu ;
7. les limites rencontrées dans le simulateur ou sur le modèle utilisé.

Un bon rapport explique pourquoi le problème s'est produit et comment sa résolution a été validée. Une liste de commandes sans analyse ne suffit pas.


## 3. Dépannage structuré et sécurité opérationnelle

### 3.1. Méthode en couches : VTP, trunk, VLAN, STP, IP

Lorsqu'un poste n'accède plus à une ressource après une modification de VLAN, suis une séquence de diagnostic stable :

**Étape 1 — VTP :** compare domaine, version, mode, révision et authentification sur les équipements concernés. Pour VTPv3, relève également le rôle primaire pour la base concernée si cette information est exposée.

**Étape 2 — Base locale :** vérifie que le VLAN est présent et que son identifiant correspond au plan.

**Étape 3 — Trunks :** vérifie chaque lien du chemin, les VLAN autorisés, les états opérationnels et les éventuelles divergences entre les deux extrémités.

**Étape 4 — STP et couche 2 :** examine l'état de transfert pour le VLAN et l'apprentissage des adresses MAC.

**Étape 5 — IP et couche 3 :** seulement lorsque la continuité de couche 2 est confirmée, vérifie l'adresse, le masque, la passerelle, le routage et les politiques de sécurité.

```text
Symptôme : poste inaccessible
          |
          v
VLAN présent sur chaque switch ? ---- Non ---> vérifier VTP / base locale
          |
         Oui
          v
VLAN autorisé sur chaque trunk ? ----- Non ---> corriger la liste du trunk
          |
         Oui
          v
STP et MAC cohérents ? --------------- Non ---> diagnostiquer la couche 2
          |
         Oui
          v
IP / passerelle / routage / ACL
```

Cette méthode évite de changer simultanément VTP, les trunks et l'adressage, ce qui rendrait la cause racine beaucoup plus difficile à établir.

### Schéma animé — ordre de diagnostic quand un VLAN ne fonctionne pas

<figure class="lesson-figure" aria-label="Séquence de diagnostic VTP, trunks, base VLAN puis connectivité">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="250" viewBox="0 0 960 250" role="img" aria-labelledby="diag-title diag-desc">
  <title id="diag-title">Diagnostic méthodique d'un VLAN</title>
  <desc id="diag-desc">Quatre étapes se suivent : vérifier l'état VTP, vérifier les trunks, examiner la base VLAN et enfin tester la connectivité réelle.</desc>
  <rect width="960" height="250" rx="18" fill="#0b1220"/>
  <text x="28" y="32" fill="#e2e8f0" font-size="18" font-weight="700" font-family="Arial, sans-serif">Procède de gauche à droite : ne saute pas directement au test IP</text>
  <path d="M220 92 H265 M450 92 H495 M680 92 H725" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
  <path d="M255 84 L265 92 L255 100 M485 84 L495 92 L485 100 M715 84 L725 92 L715 100" fill="none" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <g transform="translate(45 92)"><circle r="6" fill="#a7f3d0" stroke="#ffffff" stroke-width="1.5"><animateMotion path="M 0 0 L 850 0" dur="6s" repeatCount="indefinite"/></circle></g>
  <rect x="30" y="112" width="190" height="95" rx="12" fill="#102d27" stroke="#34d399" stroke-width="2"/>
  <text x="47" y="140" fill="#a7f3d0" font-size="11" font-weight="700" font-family="Arial, sans-serif">ÉTAPE 1</text>
  <text x="47" y="165" fill="#f8fafc" font-size="15" font-weight="700" font-family="Arial, sans-serif">show vtp status</text>
  <text x="47" y="187" fill="#d1fae5" font-size="11" font-family="Arial, sans-serif">Domaine, mode, version</text>
  <rect x="265" y="112" width="185" height="95" rx="12" fill="#12243a" stroke="#38bdf8" stroke-width="2"/>
  <text x="282" y="140" fill="#bae6fd" font-size="11" font-weight="700" font-family="Arial, sans-serif">ÉTAPE 2</text>
  <text x="282" y="165" fill="#f8fafc" font-size="14" font-weight="700" font-family="Arial, sans-serif">show interfaces trunk</text>
  <text x="282" y="187" fill="#cbd5e1" font-size="11" font-family="Arial, sans-serif">Trunks et VLAN autorisés</text>
  <rect x="495" y="112" width="185" height="95" rx="12" fill="#27213d" stroke="#a78bfa" stroke-width="2"/>
  <text x="512" y="140" fill="#ddd6fe" font-size="11" font-weight="700" font-family="Arial, sans-serif">ÉTAPE 3</text>
  <text x="512" y="165" fill="#f8fafc" font-size="15" font-weight="700" font-family="Arial, sans-serif">show vlan brief</text>
  <text x="512" y="187" fill="#ddd6fe" font-size="11" font-family="Arial, sans-serif">Présence locale du VLAN</text>
  <rect x="725" y="112" width="205" height="95" rx="12" fill="#342817" stroke="#fbbf24" stroke-width="2"/>
  <text x="742" y="140" fill="#fde68a" font-size="11" font-weight="700" font-family="Arial, sans-serif">ÉTAPE 4</text>
  <text x="742" y="165" fill="#f8fafc" font-size="14" font-weight="700" font-family="Arial, sans-serif">Tester le chemin</text>
  <text x="742" y="187" fill="#fef3c7" font-size="11" font-family="Arial, sans-serif">STP, MAC, IP, passerelle</text>
  <text x="480" y="231" text-anchor="middle" fill="#94a3b8" font-size="12" font-family="Arial, sans-serif">Si une étape échoue, corrige-la puis vérifie à nouveau avant de passer à la suivante.</text>
</svg>
<figcaption>Cette séquence sépare les causes possibles et évite de conclure qu'un problème IP est forcément un problème VTP.</figcaption>
</figure>

### 3.2. Symptôme : les VLAN ont disparu sur plusieurs commutateurs

Une disparition simultanée de VLAN peut être compatible avec un changement de base VTP, mais elle ne suffit pas à le prouver. Il faut vérifier l'état réel et l'étendue de l'incident.

Actions prioritaires :

1. suspendre les changements non essentiels et prévenir le responsable réseau ;
2. collecter `show vtp status`, `show vlan brief` et `show interfaces trunk` sur plusieurs équipements ;
3. déterminer à quel moment la base a changé et identifier les équipements ajoutés ou modifiés ;
4. préserver les sorties, journaux et sauvegardes disponibles ;
5. comparer la base actuelle à la base de référence validée ;
6. restaurer une base cohérente par la procédure adaptée à la plateforme et à la version ;
7. tester les VLAN, trunks, ports d'accès, passerelles et services affectés ;
8. documenter les actions, l'heure et le résultat.

Évite de modifier immédiatement le domaine ou la version sur tous les équipements. Cela peut introduire de nouveaux changements d'état et détruire des indices utiles.

### 3.3. Symptôme : VTP ne synchronise pas un client

Effectue une comparaison côté serveur et côté client :

```cisco
show vtp status
show interfaces trunk
show vlan brief
show logging
```

Vérifie dans cet ordre :

- domaine attendu et domaine réellement configuré ;
- version VTP et capacités de chaque commutateur ;
- mot de passe ou paramètres d'authentification lorsqu'ils sont utilisés ;
- mode VTP et fonction de l'équipement intermédiaire ;
- présence d'un chemin de trunks opérationnels ;
- rôle de serveur primaire si VTPv3 est employé ;
- prise en charge par la plateforme des fonctions recherchées.

Ne change pas de version pour « essayer ». Un changement de version doit être une décision planifiée, et non une manipulation aléatoire pendant le diagnostic.

### 3.4. Symptôme : le VLAN apparaît, mais aucune trame ne traverse

Si le VLAN existe dans la base locale, cela signifie uniquement qu'il est connu localement. Vérifie le port source et le port destination, la liste autorisée du trunk, STP, les adresses MAC apprises et l'état des interfaces.

```cisco
show vlan brief
show interfaces status
show interfaces trunk
show spanning-tree vlan 20
show mac address-table dynamic vlan 20
```

Adapte le numéro 20 au VLAN concerné. Si le trafic doit traverser plusieurs commutateurs, inspecte chaque lien du chemin. Pour une communication entre deux VLAN différents, il faut aussi une fonction de routage inter-VLAN configurée et autorisée.

### 3.5. Symptôme : un nouveau commutateur provoque des changements inattendus

Le nouveau commutateur doit être traité comme une source inconnue jusqu'à ce que son état soit validé. Ne pars pas du principe que son numéro de révision est nul parce qu'il a été acheté récemment ou qu'il a redémarré.

Dans l'environnement isolé, collecte l'état avant raccordement. En production, suis la procédure approuvée : inspection, sauvegarde, préparation documentée, validation de la base et raccordement surveillé. Si l'incident a déjà commencé, évite de déconnecter/reconnecter répétitivement les liens sans plan, car cela peut rendre l'analyse de l'événement plus difficile.

Pour un domaine v1/v2, garde à l'esprit le risque lié à une révision supérieure et à une base inattendue. Pour v3, analyse aussi l'autorité primaire et les règles de prise de contrôle ; ne transpose pas sans vérification tous les comportements historiques des anciennes versions.

### 3.6. Symptôme : l'activation du pruning modifie la connectivité attendue

Contrôle l'éligibilité des VLAN, l'état du pruning, les VLAN effectivement nécessaires derrière chaque trunk et la liste de VLAN autorisés. Les VLAN non éligibles ne seront pas supprimés par le pruning ; une fonction de pruning active ne remplace pas une liste d'autorisation bien conçue.

Vérifie la documentation de ta version : le mode d'activation et l'étendue de propagation ne sont pas identiques dans tous les scénarios VTP. Si la topologie contient des équipements transparents, étudie également les recommandations du constructeur avant d'activer la fonction.

### 3.7. Séquence de changement : ajouter, renommer ou supprimer un VLAN

Un changement de VLAN doit être traité comme une modification de service, car il peut affecter plusieurs commutateurs et terminaux.

**Avant le changement**

- identifier le VLAN, son objectif, son sous-réseau et ses services ;
- déterminer les commutateurs et trunks concernés ;
- vérifier le mode et la version VTP de la zone ;
- capturer l'état initial de la base VLAN, des trunks et de STP ;
- confirmer la sauvegarde et définir le retour arrière ;
- obtenir l'autorisation appropriée pour le changement.

**Pendant le changement**

- utiliser le commutateur autorisé à modifier la base ;
- exécuter une seule catégorie de changement à la fois ;
- vérifier que la modification a été appliquée à la base source ;
- observer la synchronisation sans effectuer immédiatement d'autres modifications non liées.

**Après le changement**

- vérifier tous les commutateurs concernés ;
- contrôler la liste des VLAN autorisés sur les trunks et l'état STP ;
- tester les ports et les services associés ;
- sauvegarder les états validés selon les procédures du modèle ;
- consigner le changement et les preuves de validation.

Supprimer un VLAN en production exige davantage de prudence qu'en créer un : des ports peuvent être affectés et des services dépendants peuvent être interrompus. Ne supprime jamais un VLAN uniquement parce qu'il semble inutilisé ; vérifie son utilisation réelle et son propriétaire.

### 3.8. Préparer un retour arrière crédible

Un plan de retour arrière doit dire ce qui sera restauré, par qui, dans quel ordre, avec quelles données et comment le résultat sera validé. « Remettre comme avant » n'est pas une procédure exploitable.

Une procédure peut contenir :

- le plan VLAN validé avant le changement ;
- les configurations sauvegardées et les sorties de référence ;
- la liste des équipements à vérifier ;
- la méthode de restauration adaptée à VTP et au modèle ;
- les tests d'acceptation ;
- les critères permettant de déclarer le service rétabli ;
- le contact de l'équipe responsable et la trace des commandes exécutées.

Pour les changements VTP, ne suppose pas que restaurer uniquement `running-config` annule nécessairement toute modification de la base VLAN sur toutes les plateformes. La récupération doit s'appuyer sur la documentation technique du système utilisé.

### 3.9. Bonnes pratiques d'exploitation

1. **Limiter les changements de base.** Documente quel équipement ou quel rôle est autorisé à publier les modifications VLAN.
2. **Ne pas raccorder à l'aveugle.** Prépare les équipements neufs ou de retour d'atelier avant leur branchement sur les trunks du domaine.
3. **Conserver un inventaire.** Note le domaine, le mode, la version, le rôle primaire éventuel, les trunks et les VLAN locaux.
4. **Garder les trunks explicites.** N'autorise que les VLAN nécessaires et vérifie les deux extrémités.
5. **Sauvegarder et tester la restauration.** Les sauvegardes doivent être accessibles et pertinentes pour la plateforme.
6. **Séparer les changements.** Ne change pas la version VTP, les VLAN autorisés, STP et l'adressage dans une seule intervention si ce n'est pas nécessaire.
7. **Surveiller les événements.** Une variation de la base ou des pertes simultanées de VLAN méritent un examen rapide.
8. **Connaître les limites du simulateur.** Packet Tracer et d'autres outils peuvent ne pas reproduire toutes les subtilités d'une plateforme physique ou de VTPv3.

### 3.10. Fiche de commandes de référence

| Commande | Quand l'utiliser | Attention |
|---|---|---|
| `show vtp status` | Vérifier domaine, version, mode et révision | Les champs dépendent de la plateforme |
| `show vlan brief` | Vérifier la base VLAN locale | Ne prouve pas que tous les trunks transportent le VLAN |
| `show interfaces trunk` | Examiner trunks et VLAN autorisés/actifs | Contrôler chaque lien utile au chemin |
| `show interfaces status` | Repérer les interfaces inactives ou inattendues | Adapter au type de port et à la plateforme |
| `show spanning-tree vlan 20` | Examiner l'état STP du VLAN 20 | Remplacer 20 par le VLAN en cours de diagnostic |
| `show mac address-table dynamic vlan 20` | Vérifier l'apprentissage MAC | La syntaxe peut varier ; du trafic doit avoir été généré |
| `show running-config` | Lire les paramètres configurés | Les informations de la base VLAN peuvent être conservées séparément |
| `show logging` | Rechercher des événements et messages | Les journaux peuvent être limités ou volatils |
| `copy running-config startup-config` | Sauvegarder la configuration active | Ne suppose pas que cela sauvegarde tous les éléments de la base de la même façon partout |
| `vtp primary vlan` | Promouvoir un primaire VLAN VTPv3 | EXEC privilégié, uniquement si pris en charge et après vérification du plan |

### 3.11. Sources techniques à consulter

Consulte toujours le guide correspondant à la gamme et à la version logicielle avant une intervention réelle :

- Cisco, **Configure VTP on Catalyst Switches** : https://www.cisco.com/c/en/us/support/docs/lan-switching/vtp/98154-conf-vlan.html
- Cisco, **VLAN Configuration Guide — Configure VTP (IOS XE)** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html
- Cisco, **Configuration Guide Catalyst 9400 — Configuring VTP** : https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9400/software/26-x/configuration_guide/vlan/b_26x_vlan_9400_cg/configuring_vtp.html

Ces documents décrivent les restrictions, les procédures VTPv3, les modes, le pruning et les exigences de synchronisation propres aux plateformes. Les commandes de ce cours restent des exemples pédagogiques à adapter.


## 4. Mise en situation et auto-évaluation

### 4.1. Cas pratique : le VLAN 30 n'est plus disponible

Une équipe crée le VLAN 30 `VOIP-LAB` sur le serveur VTP. `show vlan brief` indique le VLAN 30 sur SW1 et SW2, mais un téléphone raccordé derrière SW3 ne rejoint plus son service. Les autres VLAN fonctionnent normalement.

Réponds aux questions avant de lire la correction :

1. Quelle commande vérifies-tu en premier pour confirmer que la base locale de SW3 contient le VLAN 30 ?
2. Pourquoi la présence du VLAN sur SW3 ne prouve-t-elle pas que le téléphone peut utiliser le réseau ?
3. Quelles commandes permettent de vérifier le trunk et la présence du VLAN sur le chemin ?
4. Pourquoi est-il prématuré de modifier la version VTP ?

**Correction attendue :**

1. `show vlan brief` sur SW3.
2. Le VLAN peut exister localement mais être absent de la liste autorisée d'un trunk, bloqué sur le chemin STP, ou mal associé au port d'accès. L'adressage ou le service de couche 3 peut aussi être en cause.
3. `show interfaces trunk`, puis les commandes d'interface appropriées et `show spanning-tree vlan 30` sur les commutateurs du chemin.
4. La synchronisation de la base semble déjà avoir atteint SW3 ; il faut d'abord examiner le transport, le port d'accès, STP et le service avant de modifier un paramètre central qui pourrait affecter le domaine entier.

### 4.2. Cas pratique : un commutateur rejoint le domaine

Un commutateur revient d'un autre site. Son nom de domaine semble identique au domaine du siège. Avant raccordement, `show vtp status` indique une révision 56, alors que les commutateurs du siège utilisent une révision 21. L'équipe ignore si sa base VLAN est à jour.

**Décision attendue :** ne pas raccorder directement le commutateur au domaine de production. Isoler l'équipement, sauvegarder sa configuration, examiner sa base, sa version et son authentification, puis appliquer la procédure de préparation adaptée au modèle. La différence de révision ne prouve pas à elle seule que la base est mauvaise, mais elle doit être expliquée avant l'intégration.

### 4.3. Cas pratique : migration vers VTPv3

Une entreprise souhaite créer des VLAN de plage étendue et mieux contrôler les changements de base. Trois commutateurs sont d'un modèle récent, mais le quatrième est d'une ancienne gamme.

**Décision attendue :** ne pas lancer la migration avant d'avoir vérifié les capacités exactes de chaque commutateur. Confirmer la prise en charge de VTPv3 et des VLAN de plage étendue, documenter la base de référence, préparer le rôle primaire, choisir une procédure de migration adaptée à la gamme et définir un retour arrière. Si un équipement ne prend pas en charge les fonctionnalités requises, l'architecture doit être revue avant le changement.

### 4.4. Questions de validation

1. Quelle différence fais-tu entre la présence d'un VLAN dans la base locale et son autorisation sur un trunk ?
2. Pourquoi une révision VTP élevée ne prouve-t-elle pas à elle seule qu'une configuration est erronée ?
3. Quel rôle le serveur primaire introduit-il en VTPv3 ?
4. Pourquoi un changement de version VTP ne doit-il pas être utilisé comme première tentative de dépannage ?
5. Quel est l'objectif du pruning VTP et quelles sont ses limites ?
6. Pourquoi faut-il vérifier les capacités du matériel avant de planifier une migration vers VTPv3 ?
7. Quelles preuves faut-il collecter avant et après une modification VLAN ?
8. Pourquoi la commande de sauvegarde de la configuration ne doit-elle pas être considérée comme une preuve universelle de sauvegarde de tous les états VLAN ?

### 4.5. Réponses synthétiques

1. La base locale indique que le commutateur connaît le VLAN ; la liste du trunk décide quels VLAN ce lien accepte de transporter.
2. La révision reflète un état de configuration et son historique ; elle doit être comparée à la base attendue et aux changements documentés.
3. Le primaire établit une autorité de publication pour la base concernée, avec un mécanisme de prise de contrôle propre à VTPv3.
4. Un changement de version peut affecter tout le domaine et compliquer le diagnostic ; il faut commencer par comparer les paramètres, la base et les trunks.
5. Le pruning limite certains trafics diffusés inutiles sur les trunks. Il ne remplace ni les VLAN autorisés explicites ni les contrôles de sécurité ; certains VLAN ne sont pas éligibles et le comportement varie selon la version.
6. Les versions logicielles, la gamme et les fonctionnalités supportées diffèrent ; une migration incomplète peut empêcher la synchronisation voulue.
7. Les sorties de `show vtp status`, `show vlan brief`, `show interfaces trunk`, des commandes STP pertinentes, les configurations sauvegardées et les résultats des tests de service.
8. Le stockage et la restauration de la base VLAN varient selon les plateformes, les versions et les modes VTP ; les procédures de sauvegarde doivent être vérifiées pour le modèle exact.


## Points à retenir

- **Inspecte avant de raccorder.** Pour un équipement inconnu, relève le domaine, le mode, la version, la révision et la base VLAN avant de l'intégrer.
- **VTPv3 ajoute un rôle primaire.** Le mode serveur n'est pas équivalent au rôle de serveur primaire ; la promotion doit être contrôlée et documentée.
- **VLAN connu ne signifie pas VLAN transporté.** Vérifie la base locale, les trunks, leurs VLAN autorisés, STP et les tests de connectivité.
- **VLAN étendus et pruning ont des limites.** La compatibilité varie selon les versions et les plateformes ; appuie-toi sur le guide du matériel utilisé.
- **Dépanne dans un ordre stable.** Ne change pas simultanément VTP, trunking, STP et adressage sans raison.
- **Un changement doit être réversible.** Prévois des sauvegardes vérifiées, des contrôles avant/après, des tests d'acceptation et un plan de retour arrière.

Le niveau intermédiaire ne consiste pas à mémoriser davantage de commandes : il consiste à savoir **prévoir l'impact d'un changement, recueillir des preuves, isoler la cause et restaurer un état cohérent**.
