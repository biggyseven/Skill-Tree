# VTP et gestion des VLANs — Expert

**Niveau :** Expert  
**Durée indicative :** 90 à 150 minutes  
**Prérequis :** maîtriser le fonctionnement des VLAN et des trunks 802.1Q, les modes VTP, le numéro de révision, VTPv3, le serveur primaire, le pruning et le dépannage abordés aux niveaux Débutant et Intermédiaire.

Ce cours ne reprend pas la configuration VTP élémentaire étape par étape. Il traite VTP comme une fonction d'exploitation sensible : modèle de confiance, contrôle des changements, migration entre versions, diagnostic par preuves, analyse des annonces et procédures de récupération. L'objectif n'est pas de « faire fonctionner une commande », mais de pouvoir expliquer pourquoi une base VLAN a changé, déterminer l'étendue d'un incident et prouver qu'un changement est sûr.

> **Objectifs d'apprentissage**
>
> À la fin de ce cours, tu dois pouvoir :
>
> - modéliser les frontières de confiance et les sources autorisées de la base VLAN ;
> - expliquer les états VTPv3, la différence entre serveur et serveur primaire, et les bases de données distinctes ;
> - préparer une migration VTPv1/v2 vers VTPv3 en contrôlant les compatibilités et les possibilités de retour arrière ;
> - diagnostiquer des conflits, des erreurs de digest, des annonces absentes ou des divergences de base à partir de plusieurs preuves ;
> - analyser une capture VTP avec Wireshark et corréler les trames avec les compteurs du commutateur ;
> - distinguer une panne de synchronisation VTP d'une panne de transport de VLAN, STP ou routage ;
> - rédiger un plan de changement avec critères d'entrée, critères de succès, arrêt et retour arrière ;
> - concevoir une politique d'exploitation où la propagation centralisée est utilisée uniquement lorsqu'elle apporte un bénéfice démontré.

> **Important — plateforme de référence** : les exemples utilisent la CLI Cisco IOS/IOS XE et s'appuient sur la documentation Cisco disponible en octobre 2026. Les options, valeurs par défaut, champs de sortie et commandes disponibles varient selon le modèle et la version logicielle. Vérifie toujours les commandes sur l'équipement exact. Les manipulations qui peuvent modifier ou remplacer la base VLAN doivent être réalisées uniquement dans un laboratoire isolé ou dans une fenêtre de changement formellement approuvée.


## 1. VTP comme plan de contrôle et modèle de confiance

### 1.1. Le problème à résoudre n'est pas simplement « distribuer des VLAN »

Dans un campus multi-commutateurs, la base VLAN est une dépendance de couche 2. VTP peut diffuser les changements de cette base, mais il ne prouve pas que l'architecture entière est correcte. Une base synchronisée peut être uniformément erronée ; un VLAN peut exister partout et être bloqué par une liste de VLAN autorisés ; un trunk peut être opérationnel tout en omettant le VLAN requis ; STP peut bloquer le chemin ; la passerelle peut être absente.

Une exploitation experte sépare donc trois plans :

| Plan | Question clé | Preuves à collecter |
|---|---|---|
| **Gestion VTP** | Qui publie quelle base et qui l'accepte ? | domaine, version, mode, serveur primaire, compteurs, état du digest, historique du changement |
| **Transport de couche 2** | Le VLAN est-il présent et transporté sur chaque segment du chemin ? | `show vlan brief`, `show interfaces trunk`, état des ports, STP, table MAC |
| **Service de bout en bout** | Le terminal atteint-il les services attendus ? | adressage IP, passerelle, routage inter-VLAN, ACL, tests depuis les terminaux |

VTP est un protocole de plan de contrôle Cisco de couche 2. Ce n'est pas un protocole de routage, et ce n'est pas une garantie de disponibilité de bout en bout.

### 1.2. Définir une frontière de confiance VTP

Un domaine VTP doit être traité comme une frontière d'administration : les équipements qui y participent acceptent une partie des informations de contrôle provenant d'autres membres compatibles. Avant de choisir le mode VTP, réponds par écrit à ces questions :

1. Quelle équipe est responsable de la base VLAN de référence ?
2. Quels commutateurs sont autorisés à publier des modifications ?
3. Comment un nouvel équipement est-il inspecté avant d'être raccordé ?
4. Comment une base VLAN erronée est-elle détectée, et qui a le droit de la rétablir ?
5. Existe-t-il un inventaire daté de la base VLAN et une sauvegarde vérifiée ?
6. Comment les commutateurs qui ne doivent pas participer à VTP sont-ils isolés ?

Si l'organisation ne peut pas répondre à ces questions, activer la propagation automatique ne résout pas le défaut de processus : cela peut au contraire amplifier l'impact d'une erreur.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="vtptrust-title vtptrust-desc">
  <title id="vtptrust-title">Frontière de confiance du domaine VTP</title><desc id="vtptrust-desc">Une source autorisée publie la base VLAN vers les membres approuvés. Un commutateur inconnu demeure isolé tant que son état n'a pas été contrôlé.</desc>
  <rect width="960" height="300" rx="18" fill="#0b1220"/>
  <text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">VTP : propager uniquement depuis une source maîtrisée</text>
  <rect x="35" y="70" width="590" height="180" rx="16" fill="#102b28" stroke="#34d399" stroke-width="2" stroke-dasharray="8 5"/>
  <text x="55" y="96" fill="#6ee7b7" font-size="13" font-weight="700">DOMAINE APPROUVÉ</text>
  <rect x="65" y="125" width="150" height="75" rx="10" fill="#064e3b" stroke="#6ee7b7"/><text x="140" y="151" text-anchor="middle" fill="#ecfdf5" font-size="14" font-weight="700">Source</text><text x="140" y="171" text-anchor="middle" fill="#d1fae5" font-size="12">VTP primaire</text><text x="140" y="187" text-anchor="middle" fill="#d1fae5" font-size="11">base validée</text>
  <path d="M215 162 H290 M290 162 l-9 -6 M290 162 l-9 6" stroke="#34d399" stroke-width="3" fill="none"/>
  <rect x="300" y="125" width="120" height="75" rx="10" fill="#172554" stroke="#60a5fa"/><text x="360" y="151" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">SW-EDGE-1</text><text x="360" y="174" text-anchor="middle" fill="#bfdbfe" font-size="12">membre approuvé</text>
  <path d="M420 162 H475 M475 162 l-9 -6 M475 162 l-9 6" stroke="#60a5fa" stroke-width="3" fill="none"/>
  <rect x="485" y="125" width="110" height="75" rx="10" fill="#172554" stroke="#60a5fa"/><text x="540" y="151" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">SW-EDGE-2</text><text x="540" y="174" text-anchor="middle" fill="#bfdbfe" font-size="12">membre approuvé</text>
  <rect x="690" y="94" width="225" height="126" rx="14" fill="#3b1720" stroke="#fb7185" stroke-width="2"/><text x="802" y="123" text-anchor="middle" fill="#fecdd3" font-size="14" font-weight="700">Commutateur inconnu</text><text x="802" y="148" text-anchor="middle" fill="#ffe4e6" font-size="12">Ne pas raccorder</text><text x="802" y="166" text-anchor="middle" fill="#ffe4e6" font-size="12">avant inspection</text><text x="802" y="194" text-anchor="middle" fill="#fda4af" font-size="11">domaine · version · révision</text>
  <path d="M690 158 H650" stroke="#fb7185" stroke-width="3" stroke-dasharray="6 5"/><path d="M658 151 l-12 7 12 7" stroke="#fb7185" stroke-width="3" fill="none"/>
  <text x="480" y="278" text-anchor="middle" fill="#94a3b8" font-size="12">L'appartenance au domaine est une décision d'exploitation, pas une simple connexion physique.</text>
</svg>

### 1.3. Révision VTP : interpréter le signal, pas seulement le nombre

Le numéro de révision n'est pas un identifiant global de configuration, ni une preuve que la base est correcte. Il doit être interprété avec le domaine, la version, le mode, les paramètres d'authentification et le mécanisme VTP effectivement actif.

Dans les scénarios VTPv1/v2 classiques, une révision plus élevée peut amener les membres compatibles du domaine à accepter une base provenant d'un commutateur qui vient d'être raccordé. C'est pourquoi un équipement inconnu ne doit jamais être connecté directement à un domaine opérationnel avant inspection. L'expert ne se contente pas de constater « la révision est haute » : il vérifie si la base observée correspond à la base de référence, identifie l'événement qui a provoqué l'écart, et examine les changements effectifs de VLAN.

La comparaison de révision reste un indice ; elle ne remplace pas la comparaison de la base VLAN, le contrôle des trunks, ni l'analyse des journaux. En VTPv3, le modèle de serveur primaire améliore le contrôle des mises à jour, mais ne rend pas sans danger une modification non validée.

### Schéma animé — propagation et validation de l'annonce

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="vtpprop-title vtpprop-desc">
  <title id="vtpprop-title">Du changement VLAN à la validation</title><desc id="vtpprop-desc">Une modification contrôlée met à jour la base de référence, une annonce traverse le trunk, les membres compatibles mettent à jour leur base puis l'administrateur vérifie les résultats.</desc>
  <rect width="960" height="300" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Un changement n'est terminé qu'après vérification</text>
  <g font-family="Arial, sans-serif"><rect x="30" y="75" width="170" height="94" rx="12" fill="#0f2d29" stroke="#34d399" stroke-width="2"/><text x="115" y="103" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">1 · Changement</text><text x="115" y="127" text-anchor="middle" fill="#d1fae5" font-size="12">VLAN validé</text><text x="115" y="146" text-anchor="middle" fill="#d1fae5" font-size="12">dans le plan</text>
  <rect x="270" y="75" width="170" height="94" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="355" y="103" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">2 · Publication</text><text x="355" y="127" text-anchor="middle" fill="#dbeafe" font-size="12">annonce VTP</text><text x="355" y="146" text-anchor="middle" fill="#dbeafe" font-size="12">sur trunk</text>
  <rect x="510" y="75" width="170" height="94" rx="12" fill="#312e81" stroke="#a5b4fc" stroke-width="2"/><text x="595" y="103" text-anchor="middle" fill="#e0e7ff" font-size="14" font-weight="700">3 · Réception</text><text x="595" y="127" text-anchor="middle" fill="#e0e7ff" font-size="12">membres compatibles</text><text x="595" y="146" text-anchor="middle" fill="#e0e7ff" font-size="12">appliquent la base</text>
  <rect x="750" y="75" width="180" height="94" rx="12" fill="#3b1720" stroke="#fb7185" stroke-width="2"/><text x="840" y="103" text-anchor="middle" fill="#fecdd3" font-size="14" font-weight="700">4 · Validation</text><text x="840" y="127" text-anchor="middle" fill="#ffe4e6" font-size="12">VLAN + trunks</text><text x="840" y="146" text-anchor="middle" fill="#ffe4e6" font-size="12">+ services</text>
  <path d="M200 122 H263 M253 115 l10 7 -10 7" stroke="#94a3b8" stroke-width="2.5" fill="none"/><path d="M440 122 H503 M493 115 l10 7 -10 7" stroke="#94a3b8" stroke-width="2.5" fill="none"/><path d="M680 122 H743 M733 115 l10 7 -10 7" stroke="#94a3b8" stroke-width="2.5" fill="none"/>
  <circle cx="200" cy="122" r="5" fill="#fef08a" stroke="#fff7ed" stroke-width="1.5"><animateMotion path="M 0 0 L 63 0" dur="1.2s" repeatCount="indefinite"/></circle>
  <circle cx="440" cy="122" r="5" fill="#fef08a" stroke="#fff7ed" stroke-width="1.5"><animateMotion path="M 0 0 L 63 0" dur="1.2s" begin="0.4s" repeatCount="indefinite"/></circle>
  <circle cx="680" cy="122" r="5" fill="#fef08a" stroke="#fff7ed" stroke-width="1.5"><animateMotion path="M 0 0 L 63 0" dur="1.2s" begin="0.8s" repeatCount="indefinite"/></circle>
  <rect x="92" y="208" width="776" height="48" rx="10" fill="#111827" stroke="#475569"/><text x="480" y="228" text-anchor="middle" fill="#cbd5e1" font-size="13">Preuves : `show vtp status` · `show vtp counters` · `show vlan brief`</text><text x="480" y="245" text-anchor="middle" fill="#94a3b8" font-size="12">Puis `show interfaces trunk`, STP, table MAC et tests de bout en bout.</text></g>
</svg>

### 1.4. VTPv3 : base, instance et serveur primaire

VTPv3 introduit un contrôle plus strict des mises à jour et prend en charge des bases supplémentaires. Il faut distinguer :

- **mode serveur** : l'équipement est configuré pour fonctionner comme serveur VTP ;
- **serveur primaire** : état opérationnel obtenu par une action explicite, pour une base donnée ;
- **serveur secondaire** : reçoit les mises à jour et peut conserver les informations selon la version et la plateforme, sans être la source primaire autorisée pour les changements de base ;
- **base concernée** : par exemple la base VLAN ou la base MST ; la fonction primaire est associée à la base sélectionnée.

Un domaine VTPv3 peut exister sans serveur primaire actif en permanence. Le rôle primaire est requis pour publier des mises à jour de base au moyen du mécanisme prévu par VTPv3. Sur les plateformes documentées par Cisco, l'état primaire peut être perdu après un rechargement, un basculement ou une modification de paramètres du domaine : il doit donc être vérifié au moment d'un changement, et non supposé permanent.

La commande opérationnelle se lance généralement depuis le mode EXEC privilégié, sur une plateforme compatible :

```cisco
show vtp status
show vtp devices
! Lorsque la base VLAN est correcte et le changement autorisé :
vtp primary vlan
! La commande peut demander une confirmation et/ou le secret VTP.
```

`vtp primary vlan force` peut prendre le dessus sur des serveurs en conflit selon le comportement de la plateforme. **Ne l'utilise pas comme commande de dépannage par réflexe.** Avant de forcer un takeover, sauvegarde les états, identifie chaque serveur en conflit, compare les bases et obtiens l'autorisation explicite du responsable du changement.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="310" viewBox="0 0 960 310" role="img" aria-labelledby="vtpprimary-title vtpprimary-desc">
  <title id="vtpprimary-title">Serveur primaire VTPv3 et serveurs secondaires</title><desc id="vtpprimary-desc">Le serveur primaire autorisé publie la base VLAN de référence. Les serveurs secondaires reçoivent la mise à jour. Le rôle primaire doit être revalidé après certains événements opérationnels.</desc>
  <rect width="960" height="310" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">VTPv3 : autorité de publication de la base VLAN</text>
  <rect x="45" y="76" width="230" height="110" rx="14" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="160" y="103" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">SW-CORE-1</text><text x="160" y="128" text-anchor="middle" fill="#ecfdf5" font-size="14">VTP Server</text><text x="160" y="151" text-anchor="middle" fill="#ecfdf5" font-size="13">PRIMARY · VLAN DB</text><text x="160" y="171" text-anchor="middle" fill="#d1fae5" font-size="11">changement autorisé</text>
  <path d="M275 130 H365 M354 122 l11 8 -11 8" stroke="#34d399" stroke-width="3" fill="none"/>
  <rect x="375" y="76" width="205" height="110" rx="14" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="478" y="104" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">SW-CORE-2</text><text x="478" y="130" text-anchor="middle" fill="#dbeafe" font-size="14">Server secondaire</text><text x="478" y="151" text-anchor="middle" fill="#dbeafe" font-size="12">base reçue / sauvegardée</text>
  <path d="M580 130 H675 M664 122 l11 8 -11 8" stroke="#60a5fa" stroke-width="3" fill="none"/>
  <rect x="685" y="76" width="230" height="110" rx="14" fill="#1e293b" stroke="#a78bfa" stroke-width="2"/><text x="800" y="104" text-anchor="middle" fill="#ddd6fe" font-size="14" font-weight="700">SW-DIST-1</text><text x="800" y="130" text-anchor="middle" fill="#ede9fe" font-size="14">Membre VTPv3</text><text x="800" y="151" text-anchor="middle" fill="#ede9fe" font-size="12">base synchronisée</text>
  <circle cx="275" cy="130" r="5" fill="#fef08a" stroke="#fff7ed" stroke-width="1.5"><animateMotion path="M 0 0 L 90 0" dur="1.5s" repeatCount="indefinite"/></circle>
  <circle cx="580" cy="130" r="5" fill="#fef08a" stroke="#fff7ed" stroke-width="1.5"><animateMotion path="M 0 0 L 95 0" dur="1.5s" begin="0.6s" repeatCount="indefinite"/></circle>
  <rect x="90" y="222" width="780" height="52" rx="10" fill="#3b1720" stroke="#fb7185"/><text x="480" y="243" text-anchor="middle" fill="#fecdd3" font-size="13" font-weight="700">Après reload, switchover ou changement du domaine : revérifier l'état primaire.</text><text x="480" y="261" text-anchor="middle" fill="#ffe4e6" font-size="12">Ne pas employer `force` sans analyse des conflits et plan de changement.</text>
</svg>

### 1.5. VTPv3 et les bases de données distinctes

VTPv3 peut propager des informations associées à différentes bases. Dans les guides Cisco, la base VLAN et la base Multiple Spanning Tree (MST) font l'objet de fonctions distinctes. Il ne faut donc pas considérer qu'un seul état « VTP primaire » couvre nécessairement toutes les bases : la commande primaire doit sélectionner la base voulue, et la vérification doit porter sur la bonne instance.

Le fait de recevoir les VLAN ne prouve pas que la base MST est cohérente, et l'inverse est également vrai. Lors d'une modification d'architecture MST, documente séparément :

- la base VLAN et les identifiants réellement utilisés ;
- les régions MST, les noms/révisions et les correspondances VLAN-vers-instance ;
- l'état VTP et le type de base publié ;
- l'état STP effectif après le changement.

Ne migre pas simultanément les bases VLAN, les trunks et la conception STP sans étapes de validation intermédiaires. Les changements couplés rendent le retour arrière plus difficile et compliquent l'identification de la cause en cas de boucle ou de perte de trafic.

### 1.6. Interopérabilité et VLAN étendus : décider avant de migrer

VTPv1/v2 classiques propagent la plage normale de VLAN, alors que VTPv3 prend en charge la propagation de VLAN étendus (1006–4094) sur les équipements compatibles. VTP pruning, lui, reste une fonction de portée plus limitée : les guides Cisco indiquent qu'il s'applique aux VLAN 1–1005, et non aux VLAN étendus. La prise en charge précise et les VLAN réservés restent dépendants de la plateforme.

Le point critique pour une migration est qu'un équipement VTPv3 qui possède des VLAN étendus n'est pas un candidat à une simple rétrogradation v1/v2. Il faut tester les fonctions employées et traiter l'aller/retour comme un projet de migration, pas comme une commande isolée.

| Sujet | Question experte avant changement |
|---|---|
| Version | La plateforme prend-elle en charge la version cible et les fonctionnalités utilisées ? |
| Domaine | Tous les équipements visés appartiennent-ils au même domaine prévu ? |
| Authentification | Le secret et son mode de stockage sont-ils compatibles et connus des administrateurs autorisés ? |
| VLAN étendus | Le plan utilise-t-il des VLAN 1006–4094, et quelles plateformes doivent recevoir leur définition ? |
| Pruning | Le besoin concerne-t-il des VLAN éligibles et tous les liens ont-ils été cartographiés ? |
| Équipements anciens | Les commutateurs hérités traitent-ils correctement les annonces reçues et transmettent-ils celles nécessaires ? |
| Retour arrière | Peut-on revenir à la version précédente sans perdre une fonction de base ou la cohérence du plan VLAN ? |

**Règle pratique :** n'assume jamais une compatibilité parce que deux commutateurs partagent le même nom de domaine. Le nom de domaine n'est qu'un des paramètres du plan de contrôle.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="305" viewBox="0 0 960 305" role="img" aria-labelledby="vtpmatrix-title vtpmatrix-desc">
  <title id="vtpmatrix-title">Choisir une trajectoire de migration VTP</title><desc id="vtpmatrix-desc">L'audit des versions, bases VLAN et fonctions décide si la migration peut continuer en laboratoire ou doit être arrêtée pour traiter une incompatibilité.</desc>
  <rect width="960" height="305" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Une migration commence par l'inventaire</text>
  <rect x="340" y="58" width="280" height="57" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="480" y="82" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">Auditer tous les équipements</text><text x="480" y="101" text-anchor="middle" fill="#bfdbfe" font-size="12">version · base VLAN · authentification</text>
  <path d="M480 115 V140 M480 140 H240 V160 M480 140 H720 V160" stroke="#94a3b8" stroke-width="2.5" fill="none"/><path d="M233 151 l7 9 7 -9 M713 151 l7 9 7 -9" stroke="#94a3b8" stroke-width="2.5" fill="none"/>
  <rect x="50" y="160" width="380" height="68" rx="12" fill="#0f2d29" stroke="#34d399" stroke-width="2"/><text x="240" y="185" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">Compatibilité démontrée</text><text x="240" y="205" text-anchor="middle" fill="#d1fae5" font-size="12">Poursuivre en laboratoire et valider</text>
  <rect x="530" y="160" width="380" height="68" rx="12" fill="#3b1720" stroke="#fb7185" stroke-width="2"/><text x="720" y="185" text-anchor="middle" fill="#fecdd3" font-size="14" font-weight="700">Incompatibilité ou inconnue</text><text x="720" y="205" text-anchor="middle" fill="#ffe4e6" font-size="12">Arrêter, isoler, documenter, remédier</text>
  <path d="M240 228 V251 H720 V228" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5" fill="none"/><text x="480" y="273" text-anchor="middle" fill="#cbd5e1" font-size="12">Aucun changement en production avant validation des critères et du retour arrière.</text>
  <circle cx="480" cy="115" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 0 25 L -240 25 L -240 45" dur="2.8s" repeatCount="indefinite"/></circle>
  <circle cx="480" cy="140" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 240 0 L 240 20" dur="2.8s" begin="1.2s" repeatCount="indefinite"/></circle>
</svg>

### 1.7. Le pruning n'est pas une politique de sécurité

VTP pruning limite certains trafics de diffusion, multicast et unicast inconnu sur les trunks qui n'ont pas besoin de les transporter jusqu'aux segments aval. Il ne remplace pas les listes de VLAN autorisés, les ACL, la segmentation, les protections de ports ou une politique de filtrage. Le pruning concerne la diffusion de certains trafics, et non la suppression du VLAN de la base.

Pour expertiser un incident après activation du pruning, sépare les vérifications :

1. le VLAN existe-t-il dans la base locale ?
2. le trunk est-il opérationnel ?
3. le VLAN est-il autorisé par la configuration ?
4. le VLAN est-il actif sur le trunk et non pruné dans les conditions testées ?
5. STP permet-il le chemin ?
6. le trafic testé relève-t-il du type de trafic affecté par pruning ?

Sur les équipements compatibles, VTP pruning reste limité à la plage 1–1005. Vérifie la documentation du modèle et les résultats réels plutôt que de généraliser la fonction à tous les VLAN étendus.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="vtpprune-title vtpprune-desc">
  <title id="vtpprune-title">Effet conceptuel du VTP pruning</title><desc id="vtpprune-desc">Le trafic de diffusion est transmis vers les trunks nécessaires à atteindre un VLAN actif en aval et n'est pas envoyé sur une branche qui n'en a pas besoin, quand les conditions d'éligibilité le permettent.</desc>
  <rect width="960" height="300" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Pruning : réduire le transit inutile, pas supprimer le VLAN</text>
  <rect x="40" y="92" width="170" height="90" rx="12" fill="#0f2d29" stroke="#34d399" stroke-width="2"/><text x="125" y="120" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">SW-DIST</text><text x="125" y="143" text-anchor="middle" fill="#d1fae5" font-size="12">VLAN 20 actif</text><text x="125" y="161" text-anchor="middle" fill="#d1fae5" font-size="12">diffusion locale</text>
  <path d="M210 125 H365 L435 90 H540" stroke="#34d399" stroke-width="4" fill="none"/><path d="M530 82 l10 8 -10 8" stroke="#34d399" stroke-width="3" fill="none"/><rect x="550" y="57" width="170" height="68" rx="10" fill="#172554" stroke="#60a5fa"/><text x="635" y="82" text-anchor="middle" fill="#bfdbfe" font-size="13" font-weight="700">Branche utile</text><text x="635" y="103" text-anchor="middle" fill="#dbeafe" font-size="12">VLAN présent</text><rect x="760" y="57" width="155" height="68" rx="10" fill="#0f2d29" stroke="#34d399"/><text x="837" y="82" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">SW-ACCÈS</text><text x="837" y="103" text-anchor="middle" fill="#d1fae5" font-size="12">destination VLAN 20</text><path d="M720 91 H753 M743 83 l10 8 -10 8" stroke="#60a5fa" stroke-width="3" fill="none"/>
  <path d="M210 155 H370 L440 212 H545" stroke="#fb7185" stroke-width="3" stroke-dasharray="8 6" fill="none"/><path d="M533 202 l12 10 -12 10" stroke="#fb7185" stroke-width="3" fill="none"/><path d="M398 190 L426 234 M426 190 L398 234" stroke="#fb7185" stroke-width="4"/><rect x="550" y="185" width="170" height="58" rx="10" fill="#3b1720" stroke="#fb7185"/><text x="635" y="208" text-anchor="middle" fill="#fecdd3" font-size="13" font-weight="700">Branche inutile</text><text x="635" y="227" text-anchor="middle" fill="#ffe4e6" font-size="12">trafic éligible limité</text><text x="480" y="276" text-anchor="middle" fill="#94a3b8" font-size="12">Le trunk peut rester opérationnel et le VLAN autorisé même si le trafic éligible n'est pas relayé sur cette branche.</text>
  <circle cx="210" cy="125" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 155 0 L 225 -35 L 330 -35" dur="3.2s" repeatCount="indefinite"/></circle>
</svg>

### 1.8. Modes transparent/off et VTP par interface

Le mode transparent conserve une base VLAN locale qui n'est pas synchronisée avec la base reçue. Selon VTPv2/v3 et la plateforme, les annonces reçues peuvent néanmoins être relayées sur les trunks. Le mode off, lorsqu'il est disponible, fonctionne de manière similaire pour la base locale, mais ne relaie pas les annonces. Il faut vérifier le comportement effectif de la version logicielle et ne pas confondre la fonction VTP d'un commutateur avec l'état de ses trunks.

Certaines plateformes IOS XE documentent aussi un contrôle de VTP par interface trunk, utile pour préciser sur quels ports une instance VTP peut émettre ou recevoir. La commande exacte dépend de la plateforme. Avant de l'utiliser, consulte `vtp interface ?` ou la référence CLI du logiciel installé et vérifie avec les commandes d'observation disponibles, notamment `show vtp interface` si prise en charge.

La règle d'architecture est la suivante : les trunks physiques à travers lesquels VTP doit transiter doivent être identifiés et leur rôle documenté. Une restriction VTP par interface doit être cohérente des deux côtés et ne doit pas être utilisée à la place d'une liste explicite des VLAN transportés.

### 1.9. Authentification, stockage du secret et sécurité des opérations

Le mot de passe VTP contribue à l'acceptation des annonces dans les conditions prévues par la version ; ce n'est pas une protection universelle du réseau. Il ne remplace pas une administration sécurisée, les protections des trunks, le contrôle d'accès à la CLI, ni la gestion des changements.

VTPv3 fournit des options d'authentification améliorées sur les plateformes compatibles. Certaines documentations Cisco décrivent les mots-clés `hidden` et `secret`, dont le sens et la syntaxe doivent être confirmés dans la version cible. Un secret masqué dans la configuration n'élimine pas le besoin de le conserver en lieu sûr : une opération de takeover peut demander à nouveau le mot de passe.

Bonnes pratiques :

- répartir les secrets uniquement aux administrateurs qui en ont besoin ;
- éviter d'inclure la clé réelle dans des captures, tickets ou exemples de documentation ;
- vérifier explicitement que les équipements utilisent les mêmes paramètres d'authentification requis ;
- traiter une erreur de digest ou de mot de passe comme un problème à investiguer, pas comme une invitation à désactiver la sécurité ;
- sauvegarder les configurations et la base de référence avant toute rotation ;
- tester le changement de secret sur une maquette représentative avant la production.

### 1.10. Données persistantes : running-config, startup-config et base VLAN

Une confusion fréquente est de croire que `copy running-config startup-config` sauvegarde obligatoirement chaque état VTP et la base VLAN de la même manière sur toutes les versions. La base VLAN/VTP peut être conservée par des mécanismes différents selon le mode, la version et la plateforme. Le mode transparent présente également des particularités de persistance du mode et du nom de domaine dans la configuration.

Un plan de sauvegarde expert doit identifier et vérifier séparément :

- la configuration active et la configuration de démarrage ;
- les informations VTP et le domaine ;
- la liste réelle des VLAN, leurs noms et types ;
- l'état du serveur primaire VTPv3 pour la base concernée ;
- les trunks et les VLAN autorisés ;
- les paramètres STP/MST associés ;
- la preuve que les fichiers de sauvegarde peuvent être relus et utilisés pour restaurer une base cohérente.

Ne supprime pas un fichier de base VLAN ni ne restaure une sauvegarde dans le but de « remettre la révision à zéro » sans suivre une procédure spécifique à la plateforme. En production, une manipulation directe du stockage est une action à haut risque.


## 2. Observabilité : transformer les commandes en preuves

### 2.1. Jeu minimal de commandes d'observation

Les sorties exactes varient selon le matériel et le logiciel, mais les commandes suivantes constituent un point de départ utile lorsque le modèle les prend en charge.

```cisco
show vtp status
show vtp counters
show vtp devices
show vtp devices conflict
show vtp interface
show vtp password
show vlan brief
show interfaces trunk
show interfaces status
show spanning-tree vlan 20
show mac address-table dynamic vlan 20
show logging
```

Toutes les commandes VTP ne sont pas disponibles sur chaque équipement. Par exemple, `show vtp devices` et la vue `conflict` sont associés à VTPv3 sur les plateformes qui les prennent en charge. Une commande non reconnue doit être remplacée par sa variante documentée ; elle ne prouve pas, à elle seule, qu'un mécanisme est inactif.

### 2.2. Interpréter `show vtp status`

Ne lis pas la sortie ligne par ligne sans contexte. Construis plutôt une fiche d'état :

| Champ ou information | Ce que tu dois en déduire | Ce que cela ne prouve pas |
|---|---|---|
| Version en cours | Version réellement utilisée par ce commutateur | Compatibilité complète de tous les voisins |
| Nom du domaine | Domaine configuré ou appris | Que la base est souhaitée et correcte |
| Mode opératoire | Serveur, client, transparent ou off selon le support | Que les annonces circulent réellement sur tous les trunks |
| Révision de configuration | État relatif de la base dans les mécanismes qui utilisent ce numéro | Qu'une révision élevée est valide ou qu'un service fonctionne |
| Nombre de VLAN | État local annoncé par la sortie | Que la liste est identique au fichier de référence |
| État primaire, si affiché | Autorité de publication de la base VTPv3 concernée | Que toutes les autres bases (ex. MST) ont le même état |
| État digest/authentification | Indice lié à l'intégrité/acceptation des annonces | Que la politique d'administration est sûre |

La preuve de cohérence est obtenue en comparant les résultats aux valeurs attendues et en vérifiant les équipements du chemin. Prends des sorties datées avant et après un changement pour permettre une comparaison fiable.

### 2.3. Utiliser les compteurs VTP

`show vtp counters` peut exposer des compteurs d'annonces récapitulatives, d'annonces de sous-ensemble, de requêtes ou d'erreurs de révision/digest selon la plateforme. Compare les compteurs avant et après une opération contrôlée :

1. relève les compteurs sur les deux extrémités ;
2. effectue une modification uniquement dans un laboratoire ;
3. relève de nouveau les compteurs ;
4. compare l'évolution aux événements attendus ;
5. vérifie simultanément la base VLAN et l'état du trunk.

Un compteur qui augmente montre qu'un type de message a été observé ou transmis selon sa définition. Il ne prouve pas à lui seul que la base a été appliquée. Une absence d'incrément peut signifier aucun changement, aucun message correspondant, une absence de trunk VTP, une restriction d'interface ou un détail de l'implémentation. Il faut corréler les données.

### 2.4. Analyse de trames avec Wireshark

Une capture peut confirmer si des messages de contrôle VTP sont visibles sur le segment étudié. Le trafic VTP est de couche 2 : un filtre IP générique n'est donc pas le bon point de départ. Sur les environnements où l'adresse de destination Cisco 01:00:0c:cc:cc:cc apparaît, ce filtre Ethernet peut aider à repérer le trafic de contrôle Cisco :

```text
eth.dst == 01:00:0c:cc:cc:cc
```

Ce filtre peut aussi afficher d'autres protocoles Cisco ; il ne signifie donc pas que chaque trame sélectionnée est VTP. Si le décodeur reconnaît VTP, applique ensuite le filtre d'affichage de protocole proposé par la version de Wireshark, par exemple `vtp`, puis inspecte l'arbre de décodage. Le filtre d'affichage disponible dépend de la version du logiciel et des trames capturées.

Méthode de capture :

1. capture sur un lien trunk entre deux commutateurs du domaine, pas sur un port d'accès ordinaire ;
2. enregistre une courte capture de référence sans changement ;
3. en laboratoire, déclenche un changement de VLAN autorisé ;
4. capture les trames, horaires, directions et adresses source/destination ;
5. corrèle les trames avec `show vtp counters` sur les deux commutateurs ;
6. vérifie l'évolution de la base VLAN à la fin ;
7. conserve la capture sans secrets et avec une note précisant la version du commutateur.

La capture seule ne donne pas le contexte administratif complet : elle ne te dit pas si un VLAN vu dans l'annonce est approuvé, ni si les terminaux disposent d'une connectivité opérationnelle.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="310" viewBox="0 0 960 310" role="img" aria-labelledby="vtpcap-title vtpcap-desc">
  <title id="vtpcap-title">Corréler une capture avec les compteurs et la base VLAN</title><desc id="vtpcap-desc">Trois sources de preuves indépendantes sont collectées : trames sur le trunk, compteurs VTP et base VLAN locale. Leur corrélation aide à établir la cause sans s'appuyer sur une seule sortie.</desc>
  <rect width="960" height="310" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Une conclusion fiable repose sur plusieurs sources</text>
  <rect x="55" y="76" width="230" height="100" rx="13" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="170" y="103" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">Capture Wireshark</text><text x="170" y="128" text-anchor="middle" fill="#dbeafe" font-size="12">les trames sont-elles visibles ?</text><text x="170" y="148" text-anchor="middle" fill="#dbeafe" font-size="12">qui parle et quand ?</text>
  <rect x="365" y="76" width="230" height="100" rx="13" fill="#312e81" stroke="#a5b4fc" stroke-width="2"/><text x="480" y="103" text-anchor="middle" fill="#e0e7ff" font-size="14" font-weight="700">Compteurs VTP</text><text x="480" y="128" text-anchor="middle" fill="#e0e7ff" font-size="12">émission / réception</text><text x="480" y="148" text-anchor="middle" fill="#e0e7ff" font-size="12">erreurs ou requêtes ?</text>
  <rect x="675" y="76" width="230" height="100" rx="13" fill="#0f2d29" stroke="#34d399" stroke-width="2"/><text x="790" y="103" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">Base VLAN locale</text><text x="790" y="128" text-anchor="middle" fill="#d1fae5" font-size="12">VLAN attendus présents ?</text><text x="790" y="148" text-anchor="middle" fill="#d1fae5" font-size="12">avant / après comparés ?</text>
  <path d="M170 176 V214 H480 M480 176 V214 M790 176 V214 H480 V234" stroke="#94a3b8" stroke-width="2.5" fill="none"/><path d="M472 224 l8 10 8 -10" stroke="#94a3b8" stroke-width="2.5" fill="none"/><rect x="300" y="235" width="360" height="44" rx="10" fill="#1e293b" stroke="#64748b"/><text x="480" y="253" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="700">Hypothèse corroborée</text><text x="480" y="270" text-anchor="middle" fill="#cbd5e1" font-size="11">+ trunk · STP · table MAC · test service</text>
  <circle cx="170" cy="176" r="5" fill="#7dd3fc" stroke="#e0f2fe"><animateMotion path="M 0 0 L 0 38 L 310 38" dur="3s" repeatCount="indefinite"/></circle>
  <circle cx="480" cy="176" r="5" fill="#c4b5fd" stroke="#ede9fe"><animateMotion path="M 0 0 L 0 38" dur="1.8s" begin="0.4s" repeatCount="indefinite"/></circle>
  <circle cx="790" cy="176" r="5" fill="#86efac" stroke="#dcfce7"><animateMotion path="M 0 0 L 0 38 L -310 38 L -310 58" dur="3s" begin="0.8s" repeatCount="indefinite"/></circle>
</svg>

### 2.5. Construire une ligne de temps d'incident

En situation de panne, l'heure d'une observation vaut presque autant que la valeur observée. Construis une chronologie simple :

| Heure | Événement / observation | Équipement | Preuve | Hypothèse en cours |
|---|---|---|---|---|
| T−10 min | VLAN 20 présent | SW-DIST-1 | sortie enregistrée | état normal |
| T0 | changement approuvé ou événement non identifié | SW-CORE-1 | ticket/log/console | événement déclencheur |
| T+1 min | compteurs VTP et base relus | SW-CORE-1 / SW-DIST-1 | commandes et capture | propagation ou défaut de transport |
| T+5 min | trunks, STP, table MAC testés | chemin concerné | sorties datées | étendue réelle |
| T+10 min | mesure de confinement / restauration | équipement contrôlé | journal d'action | retour à l'état validé |

Ne réinitialise pas prématurément les compteurs et ne remplace pas la base de référence avant d'avoir collecté les preuves nécessaires. Tu risquerais d'effacer l'indice qui permet de comprendre l'origine de l'incident.


## 3. Déploiement avancé et migration

### 3.1. Étape 0 — décision d'architecture

Avant toute migration, justifie pourquoi VTP est utilisé. VTPv3 est recommandé par les guides Cisco pour les nouveaux déploiements qui ont besoin de VTP sur des plateformes compatibles, mais ce conseil ne signifie pas qu'il faut activer VTP dans chaque réseau. Une gestion locale explicite en mode transparent/off peut être plus appropriée si la centralisation ne répond pas à un besoin concret.

Décisions à documenter :

- portée du domaine et frontières de site ;
- base VLAN autoritaire et procédure de changement ;
- versions et capacités de tous les commutateurs ;
- usage éventuel de VLAN étendus, PVLAN ou base MST ;
- gestion des secrets et des accès administratifs ;
- mécanisme de surveillance et de retour arrière ;
- règles d'intégration des nouveaux commutateurs.

### 3.2. Étape 1 — inventaire et export des états

Exécute des commandes d'observation sur tous les commutateurs concernés. Adapte le jeu de commandes à la plateforme :

```cisco
show version
show vtp status
show vtp counters
show vtp devices
show vlan brief
show interfaces trunk
show spanning-tree summary
show running-config
show startup-config
```

Consigne au minimum : hostname, modèle, version IOS/IOS XE, domaine, version VTP en cours, mode, révision, VLAN locaux, VLAN étendus, trunks actifs, liste autorisée par trunk, mode STP/MST, secrets configurés (sans les recopier en clair) et rôle primaire éventuel.

Crée un inventaire comparatif. L'écart entre deux commutateurs peut être attendu si l'un est transparent/off ; sinon il doit être expliqué avant de continuer.

### 3.3. Étape 2 — sauvegarde et base de référence

Une sauvegarde valide ne se limite pas à exécuter une commande. Il faut vérifier qu'elle correspond au bon équipement et au bon instant, qu'elle peut être relue, et qu'elle contient les données nécessaires au rétablissement. Pour la base VLAN, exporte ou consigne la liste attendue, les identifiants, noms et types de VLAN, et les éléments de conception qui lient les VLAN aux trunks et services.

Prépare :

- les configurations avant changement ;
- une liste VLAN de référence et sa date ;
- les valeurs attendues pour les paramètres VTP ;
- un diagramme de topologie trunk ;
- le plan de retour arrière et les personnes autorisées à le déclencher ;
- les tests de succès mesurables.

### 3.4. Étape 3 — maquette de migration VTPv3

La maquette doit inclure les modèles logiciels représentatifs, les trunks, les bases VLAN, l'authentification et la base MST si celle-ci est concernée. Les fonctions VTPv3 ne sont pas uniformément ém ulées par tous les simulateurs. Packet Tracer et d'autres simulateurs peuvent ne pas reproduire tous les détails de VTPv3, du serveur primaire, de l'authentification ou des VLAN étendus. Si l'outil ne prend pas en charge une fonctionnalité, ne considère pas le test comme une preuve : utilise un environnement IOS/IOS XE compatible.

Scénarios à tester au minimum :

1. propagation d'un VLAN ajouté sur la base de référence ;
2. changement de nom de VLAN et vérification des membres ;
3. incohérence de domaine ou de mot de passe ;
4. perte ou changement d'état du serveur primaire ;
5. conflit de serveurs VTPv3 ;
6. VLAN étendu avec les équipements qui doivent le recevoir ;
7. trunk opérationnel mais VLAN retiré de la liste autorisée ;
8. configuration de pruning sur une branche où le trafic est ou n'est pas requis ;
9. redémarrage et vérification des états persistants ;
10. retour à la base et à la version précédentes selon la procédure approuvée.

### 3.5. Étape 4 — activer VTPv3 de façon coordonnée

La procédure exacte dépend de l'IOS/IOS XE. Sur les plateformes qui prennent en charge la syntaxe classique, une préparation peut ressembler à ceci :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp version 3
vtp mode server
! Mot de passe : appliquer la syntaxe documentée pour la version cible.
! Exemple quand l'option est prise en charge :
! vtp password <SECRET_DE_LAB> hidden
end
copy running-config startup-config
show vtp status
```

Applique la version cible à chaque équipement concerné conformément au plan de migration et aux recommandations de la plateforme ; VTPv3 n'est pas activé de la même manière automatique que certains comportements v1/v2. Ne copie pas l'exemple tel quel en production, ne mets pas un secret réel dans un dépôt de cours et n'assume pas que `hidden` est disponible sur chaque IOS.

Après configuration, compare le domaine, la version en cours, le mode et l'état de la base. Ne promeus pas un serveur primaire avant d'avoir déterminé quelle base est la source de vérité.

### 3.6. Étape 5 — valider le serveur primaire et la base publiée

Sur le candidat primaire :

1. confirme que les VLAN et leurs noms correspondent à la base approuvée ;
2. compare le plan des VLAN étendus et des VLAN spéciaux avec les capacités de chaque voisin ;
3. vérifie l'état des trunks et la continuité attendue ;
4. relève les états VTP des serveurs et les conflits éventuels ;
5. effectue le takeover de la base voulue pendant la fenêtre autorisée ;
6. réponds à la confirmation seulement après validation formelle ;
7. confirme l'état VTPv3 sur le serveur et les membres ;
8. vérifie la base sur un ensemble représentatif de commutateurs ;
9. teste des ports d'accès, les VLAN transportés et les services concernés.

Exemples de commandes d'observation et, si elles sont disponibles, d'opération :

```cisco
show vtp status
show vtp devices
show vtp devices conflict
! Action à exécuter uniquement après autorisation et comparaison de la base :
vtp primary vlan
```

La commande `vtp primary vlan` est un acte de contrôle, pas une commande d'inspection. N'exécute pas `force` pour contourner une confirmation ou un conflit sans comprendre la base qui sera publiée.

### 3.7. Étape 6 — surveillance post-changement

Définis une courte période d'observation après la migration. Compare les données avant/après et teste au moins un terminal ou service pour chacun des VLAN critiques. Ne valide pas un changement simplement parce qu'aucune alerte n'est apparue.

Critères de succès possibles :

- tous les équipements attendus affichent le domaine et la version prévus ;
- l'état primaire est conforme pour la base concernée ;
- aucun conflit VTPv3 inexpliqué n'est présent ;
- la liste des VLAN, noms et types correspond à la référence ;
- tous les trunks requis sont opérationnels et transportent les VLAN attendus ;
- aucune anomalie STP/MST n'est constatée ;
- les services de test réussissent ;
- la configuration et l'inventaire après changement ont été sauvegardés.

### 3.8. Plan de retour arrière et limites de réversibilité

Un retour arrière n'est crédible que si ses préconditions sont connues. Le retour d'une version VTPv3 vers v1/v2 peut être impossible ou inadapté si l'architecture utilise des VLAN étendus ou des fonctions non compatibles. Le plan doit donc décider avant le changement si le retour consiste à restaurer une base, repasser temporairement une frontière en transparent/off, revenir à une version antérieure, ou poursuivre la remédiation sans downgrade.

Ne remplace pas un retour arrière planifié par une commande de reset improvisée. Définis précisément :

- le signal qui déclenche l'arrêt ;
- la personne qui autorise le retour ;
- les changements qu'on annule et ceux qu'on ne peut pas annuler ;
- la base de référence à restaurer ;
- les étapes empêchant une base erronée de se propager à nouveau ;
- les tests prouvant que la situation est revenue à un état acceptable.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="320" viewBox="0 0 960 320" role="img" aria-labelledby="vtpchange-title vtpchange-desc">
  <title id="vtpchange-title">Porte de changement et retour arrière</title><desc id="vtpchange-desc">Une migration doit passer par l'inventaire, la sauvegarde et la validation en laboratoire. Si les critères de succès échouent, une porte d'arrêt mène à un retour arrière documenté.</desc>
  <rect width="960" height="320" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Aucun changement ne part sans porte de contrôle</text>
  <g font-family="Arial,sans-serif"><rect x="45" y="74" width="180" height="65" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="135" y="99" text-anchor="middle" fill="#bfdbfe" font-size="13" font-weight="700">1 · Inventaire</text><text x="135" y="119" text-anchor="middle" fill="#dbeafe" font-size="12">état de référence</text><rect x="275" y="74" width="180" height="65" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="365" y="99" text-anchor="middle" fill="#bfdbfe" font-size="13" font-weight="700">2 · Sauvegarde</text><text x="365" y="119" text-anchor="middle" fill="#dbeafe" font-size="12">restauration vérifiée</text><rect x="505" y="74" width="180" height="65" rx="11" fill="#312e81" stroke="#a5b4fc" stroke-width="2"/><text x="595" y="99" text-anchor="middle" fill="#e0e7ff" font-size="13" font-weight="700">3 · Changement</text><text x="595" y="119" text-anchor="middle" fill="#e0e7ff" font-size="12">fenêtre autorisée</text><rect x="735" y="74" width="180" height="65" rx="11" fill="#0f2d29" stroke="#34d399" stroke-width="2"/><text x="825" y="99" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">4 · Vérification</text><text x="825" y="119" text-anchor="middle" fill="#d1fae5" font-size="12">critères objectifs</text>
  <path d="M225 106 H268 M258 99 l10 7 -10 7 M455 106 H498 M488 99 l10 7 -10 7 M685 106 H728 M718 99 l10 7 -10 7" stroke="#94a3b8" stroke-width="2.5" fill="none"/>
  <path d="M825 139 V180 H620 V205" stroke="#fb7185" stroke-width="2.5" stroke-dasharray="7 5" fill="none"/><path d="M612 195 l8 10 8 -10" stroke="#fb7185" stroke-width="2.5" fill="none"/><rect x="420" y="205" width="400" height="65" rx="11" fill="#3b1720" stroke="#fb7185" stroke-width="2"/><text x="620" y="230" text-anchor="middle" fill="#fecdd3" font-size="14" font-weight="700">Critères échoués → STOP</text><text x="620" y="250" text-anchor="middle" fill="#ffe4e6" font-size="12">appliquer le retour arrière convenu</text><path d="M420 238 H165 V140" stroke="#fb7185" stroke-width="2" stroke-dasharray="7 5" fill="none"/><path d="M157 150 l8 -10 8 10" stroke="#fb7185" stroke-width="2" fill="none"/><text x="480" y="300" text-anchor="middle" fill="#94a3b8" font-size="12">Le retour arrière doit être défini et testé avant le début de la fenêtre de changement.</text></g>
  <circle cx="225" cy="106" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 43 0" dur="1s" repeatCount="indefinite"/></circle>
  <circle cx="455" cy="106" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 43 0" dur="1s" begin="0.35s" repeatCount="indefinite"/></circle>
  <circle cx="685" cy="106" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 43 0" dur="1s" begin="0.7s" repeatCount="indefinite"/></circle>
</svg>


## 4. Diagnostic expert par symptômes

### 4.1. Les VLAN disparaissent sur plusieurs commutateurs

**Priorité :** limiter la propagation d'une éventuelle base incorrecte sans détruire les preuves.

1. Identifie l'étendue : quels commutateurs, VLAN et services sont affectés ?
2. Collecte `show vtp status`, `show vtp counters`, la sortie `show vlan brief` et les journaux sur les équipements critiques.
3. Repère le dernier événement connu : changement de VLAN, ajout d'un commutateur, reload, takeover ou modification d'authentification.
4. Compare les informations aux sauvegardes datées ; ne te fie pas uniquement à un numéro de révision.
5. Vérifie les trunks et STP pour déterminer si les VLAN ont disparu de la base ou sont simplement bloqués dans le transport.
6. Si une base erronée continue à être publiée, suis la procédure d'incident et d'isolation approuvée ; n'improvise pas un changement de domaine en production.
7. Restaure depuis une source de vérité validée, en respectant la version et l'autorité de base actives.
8. Vérifie chaque VLAN critique et les services de bout en bout avant de déclarer l'incident clos.

### 4.2. Les compteurs augmentent, mais la base n'est pas attendue

Une trame reçue n'est pas égale à une mise à jour acceptée. Vérifie le domaine, la version, l'authentification, le mode, la compatibilité des annonces et l'état primaire si VTPv3 est en jeu. Inspecte les messages d'erreur et la capture lorsque possible. Vérifie ensuite si la base de référence est celle qui doit réellement être publiée.

### 4.3. Aucune annonce visible dans la capture

Procède du physique vers le protocole :

1. le port est-il up/up ?
2. la liaison est-elle réellement un trunk opérationnel ?
3. la capture est-elle prise sur le bon lien, au bon moment, et dans le bon sens ?
4. VTP est-il activé globalement et, si la plateforme le permet, sur l'interface concernée ?
5. les compteurs changent-ils pendant l'opération ?
6. le protocole de capture reconnaît-il le message ou faut-il examiner le trafic Cisco de couche 2 ?

Ne conclus pas à un défaut de VTP si la capture est faite sur un port miroir mal configuré ou si le changement déclencheur n'a pas eu lieu.

### 4.4. Le domaine semble cohérent mais un seul VLAN ne traverse pas

Ce symptôme pointe souvent vers le transport de couche 2, pas vers la synchronisation : vérifie la présence du VLAN aux commutateurs du chemin, la liste autorisée de chaque trunk, son état opérationnel, STP, l'apprentissage MAC, le port d'accès et les tests IP. Ne crée pas une autre fois le VLAN sur le serveur VTP avant d'avoir prouvé qu'il est absent de la base : cela peut augmenter la confusion et modifier l'état du domaine inutilement.

### 4.5. `show vtp devices conflict` affiche un conflit

Sur les plateformes VTPv3 qui prennent en charge cette commande, conserve la sortie et relève l'identité du serveur primaire en conflit, la base concernée et le contexte du changement. Compare la base de chaque candidat avec l'inventaire de référence. Ne traite pas le conflit avec un takeover forcé avant d'avoir identifié quel état doit gagner. La résolution est une décision de changement : choisir la base, obtenir l'autorisation, prendre une sauvegarde, résoudre le conflit selon la procédure documentée, puis contrôler la cohérence du domaine.

### 4.6. Après un reload ou un basculement, l'état primaire a changé

Le rôle primaire VTPv3 n'est pas à supposer permanent. Vérifie `show vtp status` et les commandes d'observation VTPv3 disponibles. Confirme la base concernée, l'identité de l'autorité de publication et l'absence de conflit. N'initie pas de changement de base simplement pour faire disparaître un indicateur de statut ; détermine si une mise à jour est requise et autorisée.

### 4.7. L'ajout de VLAN étendus semble réussir localement mais échoue ailleurs

Vérifie la version VTPv3 sur les équipements qui doivent recevoir la base, la gamme et le logiciel, les limites de la plateforme, l'état des trunks et les listes de VLAN autorisés. Un VLAN présent localement ne constitue pas une preuve qu'il est propagé à travers tout le domaine. Évalue aussi si un membre ancien doit rester en mode transparent/off ou être remplacé dans le périmètre de propagation.

### 4.8. Après activation du pruning, une application semble perdre sa connectivité

Le pruning n'est pas le premier suspect automatique. Vérifie l'éligibilité du VLAN à la fonction, la topologie aval, le trunk, la liste autorisée, l'état STP, l'emplacement réel de la destination et le type de trafic. N'oublie pas que la portée documentée du pruning s'arrête aux VLAN 1–1005. Toute désactivation ou réactivation doit suivre le processus de changement et être testée sur les ports et services concernés.

### Schéma animé — arbre de diagnostic

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-labelledby="vtpdiag-title vtpdiag-desc">
  <title id="vtpdiag-title">Arbre de décision pour une panne VLAN</title><desc id="vtpdiag-desc">Le diagnostic examine d'abord la base VTP, ensuite le trunk et la liste autorisée, puis STP, l'apprentissage MAC et les services IP.</desc>
  <rect width="960" height="340" rx="18" fill="#0b1220"/><text x="480" y="30" text-anchor="middle" fill="#e2e8f0" font-size="20" font-weight="700">Suivre la couche fautive au lieu de modifier VTP au hasard</text>
  <rect x="320" y="55" width="320" height="48" rx="10" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="480" y="75" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">1 · VLAN présent dans la base locale ?</text><text x="480" y="92" text-anchor="middle" fill="#bfdbfe" font-size="11">show vlan brief / VTP status</text>
  <path d="M480 103 V127 H235 V145 M480 127 H725 V145" stroke="#94a3b8" stroke-width="2.3" fill="none"/>
  <rect x="55" y="145" width="360" height="57" rx="10" fill="#3b1720" stroke="#fb7185"/><text x="235" y="168" text-anchor="middle" fill="#fecdd3" font-size="13" font-weight="700">NON → Base VTP / mode / version</text><text x="235" y="187" text-anchor="middle" fill="#ffe4e6" font-size="11">domain, auth, primary, annonces, révision</text>
  <rect x="545" y="145" width="360" height="57" rx="10" fill="#0f2d29" stroke="#34d399"/><text x="725" y="168" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">OUI → Le trunk transporte le VLAN ?</text><text x="725" y="187" text-anchor="middle" fill="#d1fae5" font-size="11">show interfaces trunk / VLAN autorisés</text>
  <path d="M725 202 V226 H480 V244" stroke="#94a3b8" stroke-width="2.3" fill="none"/><path d="M472 234 l8 10 8 -10" stroke="#94a3b8" stroke-width="2.3" fill="none"/><rect x="295" y="244" width="370" height="55" rx="10" fill="#312e81" stroke="#a5b4fc"/><text x="480" y="266" text-anchor="middle" fill="#e0e7ff" font-size="13" font-weight="700">Trunk correct → STP / MAC / IP</text><text x="480" y="285" text-anchor="middle" fill="#e0e7ff" font-size="11">chemin, port d'accès, passerelle, ACL</text>
  <text x="480" y="324" text-anchor="middle" fill="#94a3b8" font-size="12">Conserve les sorties avant/après et valide chaque couche indépendamment.</text>
  <circle cx="480" cy="103" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 0 24 L -245 24 L -245 42" dur="3s" repeatCount="indefinite"/></circle>
  <circle cx="480" cy="127" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 245 0 L 245 18" dur="3s" begin="0.7s" repeatCount="indefinite"/></circle>
  <circle cx="725" cy="202" r="5" fill="#fef08a" stroke="#fff7ed"><animateMotion path="M 0 0 L 0 24 L -245 24 L -245 42" dur="3s" begin="1.4s" repeatCount="indefinite"/></circle>
</svg>


## 5. Laboratoires experts

### 5.1. Règles de sécurité du laboratoire

Ces exercices doivent être exécutés sur une topologie isolée. N'utilise pas un domaine VTP de production pour provoquer une erreur de révision, tester un conflit primaire ou simuler une base incorrecte. Sauvegarde les états initiaux. Utilise des noms de domaine de laboratoire, des VLAN de test et des équipements virtuels/hardware prévus pour l'exercice.

**Topologie de référence :**

```text
                SW-CORE (base de référence)
                   /                \
                trunk               trunk
                 /                    \
          SW-DIST-1                 SW-DIST-2
              |                         |
          PC-TEST-A                 PC-TEST-B

Domaine de laboratoire : VTP-LAB-EXPERT
VLAN de test : 110 (USERS-A), 120 (USERS-B), 130 (MONITORING)
```

Adapte les interfaces à la plateforme. Vérifie d'abord que les trois commutateurs et les deux postes sont réellement isolés de toute autre topologie.

### 5.2. Lab A — cartographier le domaine sans le modifier

**But :** produire une fiche d'état de référence avant toute modification.

Sur chaque commutateur, récupère les commandes disponibles :

```cisco
show version
show vtp status
show vtp counters
show vtp devices
show vtp interface
show vlan brief
show interfaces trunk
show spanning-tree summary
show running-config
```

**Travail demandé :**

1. construire un tableau des paramètres VTP et des capacités de chaque commutateur ;
2. identifier la source de vérité prévue pour la base VLAN ;
3. comparer les VLAN et noter toute divergence ;
4. cartographier chaque trunk et sa liste autorisée ;
5. identifier les champs qui ne sont pas disponibles sur la plateforme et choisir des preuves alternatives ;
6. rédiger une conclusion qui distingue les faits, les hypothèses et les inconnues.

**Livrable attendu :** une fiche d'état avant changement, datée et relue par un autre administrateur.

### 5.3. Lab B — analyser une annonce avec Wireshark

**But :** corréler la capture de contrôle avec la base et les compteurs.

1. capture sur le trunk entre SW-CORE et SW-DIST-1 ;
2. relève les compteurs VTP avant le test ;
3. crée le VLAN 130 sur la source de référence dans le domaine isolé ;
4. capture pendant le changement ;
5. relève les compteurs une seconde fois ;
6. vérifie `show vlan brief` sur les équipements prévus ;
7. classe les observations : trame vue, annonce reconnue, compteur changé, base modifiée, connectivité validée.

**Questions :**

- Les quatre preuves évoluent-elles toujours en même temps ?
- Que peut-on conclure si la trame est visible mais que la base du voisin reste inchangée ?
- Que peut-on conclure si le VLAN apparaît dans la base mais que le terminal reste inaccessible ?
- Pourquoi un filtre de destination Cisco ne prouve-t-il pas que chaque trame est VTP ?

### 5.4. Lab C — conflit de serveur primaire en VTPv3

**Condition :** utiliser uniquement un système qui prend explicitement en charge VTPv3 et les commandes d'observation/gestion associées.

**But :** apprendre à résoudre un conflit avec preuve plutôt qu'en forçant le takeover.

1. établis une base de référence contenant les VLAN 110, 120 et 130 ;
2. vérifie le domaine, le mode, la version, l'authentification et l'état primaire ;
3. relève `show vtp devices` et `show vtp devices conflict` si disponibles ;
4. provoque uniquement dans la maquette le scénario contrôlé de conflit défini par la documentation de la version ;
5. sauvegarde les sorties des deux candidats ;
6. compare les bases et désigne celle qui doit être conservée ;
7. résous le conflit selon la procédure documentée, sans utiliser `force` avant autorisation ;
8. vérifie le statut primaire, la cohérence de la base, les trunks, STP et la connectivité.

**Critère de réussite :** tu peux justifier par écrit pourquoi une base doit gagner, plutôt que de dire seulement « la commande a fonctionné ».

### 5.5. Lab D — déboguer un VLAN absent sur un trunk

**But :** distinguer la gestion de base du transport réel.

Dans la maquette, retire volontairement le VLAN 120 de la liste autorisée sur un seul trunk (et sur aucun autre port) ; consigne l'état initial pour le restaurer exactement.

```cisco
show vlan brief
show interfaces trunk
show spanning-tree vlan 120
show mac address-table dynamic vlan 120
```

Travail demandé : montrer que le VLAN peut exister dans la base tout en étant absent du transport sur un segment précis. Remets ensuite la liste autorisée conformément à la configuration de référence et prouve la restauration.

Ne remplace pas la liste autorisée complète par une petite liste sans vérifier l'effet des commandes. Certaines variantes IOS remplacent la liste existante au lieu d'y ajouter un VLAN.

### 5.6. Lab E — migration simulée vers VTPv3

**But :** rédiger une procédure de migration contrôlée.

Le lab peut être pratique si l'environnement prend en charge tous les éléments ; sinon, réalise une revue de conception sur papier et marque clairement les étapes non testées.

| Phase | Action | Preuve obligatoire | Condition d'arrêt |
|---|---|---|---|
| 1 | inventaire complet | états VTP, VLAN, trunks, version | équipement non identifié |
| 2 | sauvegarde | export lisible et liste VLAN | restauration non vérifiée |
| 3 | maquette | résultat des scénarios critiques | conflit ou fonction non supportée |
| 4 | transition version | version réellement active sur les membres prévus | membre incompatible non isolé |
| 5 | serveur primaire | état primaire et base validée | base de référence ambiguë |
| 6 | tests de service | VLAN, trunk, STP, table MAC, IP | perte d'un service critique |
| 7 | clôture | inventaire final et compte-rendu | preuves manquantes |

**Livrable :** un runbook d'une page avec opérateur, relecteur, heure de changement, commandes, résultats attendus, seuil d'arrêt et retour arrière.

### 5.7. Lab F — créer un rapport d'incident reproductible

Choisis l'un des cas suivants : aucun message VTP visible, erreur d'authentification/digest, disparition d'un VLAN, conflit primaire ou VLAN bloqué sur un trunk.

Le rapport doit inclure :

- symptôme exact et heure de début ;
- topologie et équipements concernés ;
- état initial attendu et éléments de preuve ;
- commandes et captures réalisées ;
- hypothèses classées par probabilité, avec éléments pour/contre ;
- action de confinement et autorité qui l'a approuvée ;
- correction réalisée ;
- tests de restauration et résultats ;
- mesures préventives.

Une conclusion comme « redémarrage effectué et c'est revenu » est insuffisante sans cause démontrée, preuves avant/après et contrôle des effets secondaires.


## 6. Études de cas

### 6.1. Cas — la base est identique, mais l'application ne passe plus

**Situation :** SW-CORE, SW-DIST-1 et SW-DIST-2 montrent le VLAN 120. Les équipes affirment pourtant que l'application hébergée derrière SW-DIST-2 n'est plus joignable depuis le service correspondant.

**Approche attendue :** ne pas modifier la base VTP. Compare les trunks sur tout le chemin, la liste autorisée, l'état opérationnel, STP, la table MAC, le port d'accès, l'IP et la passerelle. Localise le premier segment où l'état diverge. Si le VLAN est localement présent mais absent du trunk, la cause est au niveau du transport, pas de la distribution VTP.

### 6.2. Cas — un nouveau commutateur porte une configuration inconnue

**Situation :** un équipement recyclé est ajouté au réseau pour remplacer un commutateur en panne. Il annonce le même domaine qu'un groupe VTPv1/v2 et affiche une révision inattendue.

**Approche attendue :** isoler l'équipement, relever version, mode, domaine, révision et liste VLAN ; comparer avec la référence ; suivre la procédure de préparation propre à la plateforme ; ne le raccorder que lorsque sa participation est conforme. Dans les versions historiques, la révision plus élevée et des paramètres compatibles peuvent conduire les membres à accepter une base indésirable. Dans tous les cas, il faut se fier à la procédure et aux preuves, pas à l'hypothèse qu'un matériel recyclé serait « vierge ».

### 6.3. Cas — deux serveurs VTPv3 paraissent primaires

**Situation :** les commandes d'observation sur la plateforme indiquent un conflit associé à des serveurs ou à une base.

**Approche attendue :** collecter l'état des deux serveurs et la base en cours, identifier si le conflit concerne la base VLAN ou MST, désigner une base de référence, sauvegarder et obtenir l'autorisation. Résoudre le conflit par la procédure supportée, puis vérifier le domaine, les membres, la base, les VLAN transportés et les services. Ne pas lancer immédiatement `vtp primary ... force`.

### 6.4. Cas — les VLAN étendus ne suivent pas la migration

**Situation :** le VLAN 1800 est configuré sur le commutateur de référence mais n'apparaît pas sur un membre héritant d'une configuration antérieure.

**Approche attendue :** vérifier les versions réellement actives, la compatibilité du membre, la plage VLAN prise en charge, le domaine, l'authentification et les trunks. La propagation des VLAN étendus dépend de VTPv3 et des capacités de la plateforme. Un équipement qui ne peut pas les traiter ne doit pas être compté comme une destination correctement synchronisée.


## 7. Validation des connaissances

### 7.1. Questions

**Question 1.** Une révision VTP élevée signifie-t-elle que la base VLAN est correcte ? Explique.

**Question 2.** Quelle est la différence entre un équipement en mode serveur VTPv3 et un serveur primaire pour la base VLAN ?

**Question 3.** Pourquoi faut-il vérifier séparément la base VLAN et la base MST dans un domaine VTPv3 qui utilise MST ?

**Question 4.** Quelle conclusion est permise si `show vtp counters` confirme la réception d'annonces, mais que le VLAN voulu n'apparaît pas dans la base locale ?

**Question 5.** Un VLAN existe sur les deux extrémités d'un trunk, mais les terminaux ne communiquent pas. Cite au moins quatre contrôles hors VTP.

**Question 6.** Pourquoi un retour VTPv3 vers v1/v2 doit-il être planifié avant la migration si des VLAN étendus sont utilisés ?

**Question 7.** Le filtre `eth.dst == 01:00:0c:cc:cc:cc` suffit-il à identifier uniquement les trames VTP ? Pourquoi ?

**Question 8.** Dans quelles conditions la commande `vtp primary vlan force` est-elle appropriée ?

**Question 9.** Quelle est la différence opérationnelle entre mode transparent et mode off, sous réserve du comportement de la plateforme ?

**Question 10.** Le pruning VTP supprime-t-il le VLAN de la base ? Sur quelles plages de VLAN est-il généralement applicable selon la documentation Cisco actuelle ?

**Question 11.** Un simulateur ne montre pas le comportement du serveur primaire VTPv3. Peut-on conclure que le réseau réel se comportera de la même manière ?

**Question 12.** Pourquoi sauvegarder séparément la configuration, la base VLAN et les états VTP avant un changement ?

**Question 13.** Cite les preuves minimales à recueillir pour montrer qu'un nouveau VLAN a bien été publié, reçu et rendu utilisable.

**Question 14.** Après un reload, le serveur primaire n'est plus celui attendu. Quelle est la première attitude correcte ?

**Question 15.** Décris une séquence d'arrêt sûre si, après migration, un VLAN critique disparaît sur plusieurs commutateurs.

### 7.2. Corrigé

**1.** Non. La révision est un élément de contexte pour les mécanismes qui l'utilisent. Elle ne prouve ni que la base correspond à la référence, ni que les trunks, STP ou les services sont opérationnels.

**2.** Le mode serveur décrit le mode VTP configuré. Le statut primaire est un état opérationnel explicite pour une base donnée, permettant au serveur primaire autorisé de publier les mises à jour associées.

**3.** VTPv3 peut gérer des bases distinctes. L'état primaire, la cohérence et les changements doivent être vérifiés pour la base réellement concernée ; synchronisation VLAN ne signifie pas automatiquement cohérence MST.

**4.** Seule la réception de messages a été observée. Il faut contrôler domaine, version, authentification, mode, compatibilité des annonces et état de la base, puis recueillir les erreurs et une capture si nécessaire.

**5.** État trunk opérationnel, liste VLAN autorisée, STP, apprentissage MAC, port d'accès, câblage/état physique, adressage IP, passerelle, routage, ACL et politiques de sécurité.

**6.** Les VLAN étendus (1006–4094) sont pris en charge par VTPv3 sur les plateformes compatibles, pas par VTPv1/v2 classiques pour la propagation. Le downgrade peut donc ne pas préserver le comportement attendu.

**7.** Non. L'adresse est utilisée par plusieurs protocoles de contrôle Cisco ; elle peut aider à trouver des trames mais ne prouve pas que chacune est VTP. Il faut examiner le décodage et le contexte.

**8.** Uniquement lorsque le conflit a été compris, que la base autoritaire est validée, qu'une sauvegarde existe, que le changement est approuvé et que la procédure du modèle permet l'action forcée. Ce n'est pas un raccourci général de diagnostic.

**9.** Le mode transparent maintient une base locale indépendante et peut relayer certaines annonces en v2/v3. Le mode off, lorsqu'il existe, conserve une base locale tout en ne relayant pas les annonces. Vérifier le logiciel et la documentation exacts.

**10.** Non. Le pruning limite certains trafics de flooding sur les branches où ils ne sont pas nécessaires. La documentation Cisco indique une portée VTP pruning limitée aux VLAN 1–1005 ; les VLAN 1006–4094 ne sont pas couverts par cette fonction.

**11.** Non. La maquette ne valide que les comportements effectivement émulés. Il faut tester avec une plateforme/IOS compatible ou documenter la fonctionnalité comme non vérifiée.

**12.** Parce que la configuration de démarrage, les informations VTP et la base VLAN ne sont pas nécessairement stockées/restaurées de façon identique sur toutes les versions et tous les modes. Une sauvegarde doit être vérifiée et adaptée au mécanisme de persistance réel.

**13.** État de la source avant/après, compteurs ou capture d'annonce, base VLAN locale sur la source et les membres attendus, état des trunks et VLAN autorisés, STP/table MAC, test de connectivité ou de service.

**14.** Collecter les états actuels, vérifier la base attendue et rechercher reload/switchover ou changement de paramètres. Ne pas publier une nouvelle base avant d'avoir confirmé l'autorité et la nécessité du takeover.

**15.** Stopper les autres changements, collecter sorties et journaux, identifier la portée, déterminer si la base est absente ou si le transport est bloqué, isoler la source de propagation suspecte selon la procédure approuvée, restaurer une source de vérité validée, puis vérifier chaque VLAN critique et chaque service avant clôture.


## 8. Runbook synthétique de l'administrateur expert

### Avant un changement

- [ ] L'objectif architectural de VTP est documenté.
- [ ] Les modèles et versions logicielles de tous les membres sont inventoriés.
- [ ] Le domaine, les modes, les versions et l'authentification sont vérifiés.
- [ ] La base VLAN et, si concerné, la base MST sont sauvegardées et comparées à la référence.
- [ ] Les trunks, listes autorisées, chemins STP/MST et services impactés sont cartographiés.
- [ ] Le test a été réalisé dans une maquette supportant réellement les fonctions requises.
- [ ] Les critères d'arrêt et la procédure de retour arrière sont écrits et relus.

### Pendant un changement

- [ ] Une seule modification principale est effectuée à la fois.
- [ ] Le changement est appliqué par la source autorisée.
- [ ] L'état VTP et les compteurs sont relus.
- [ ] La base réelle est comparée à la référence, pas seulement la révision.
- [ ] Les conflits primaires ne sont pas contournés sans analyse et autorisation.
- [ ] Les commandes ayant un effet de remplacement ou de takeover sont traitées comme des opérations à risque.

### Après un changement

- [ ] Tous les membres attendus ont les paramètres et l'état prévus.
- [ ] La base VLAN/MST correspond à la référence.
- [ ] Les trunks transportent les VLAN requis ; le pruning n'a pas supprimé le transit nécessaire.
- [ ] STP/MST est stable et les tables MAC montrent l'apprentissage attendu.
- [ ] Les tests de services réussissent depuis les segments concernés.
- [ ] Les configurations, sorties, captures et décisions sont archivées.
- [ ] La documentation et la base de référence sont mises à jour.


## 9. Références techniques

Les références officielles doivent être choisies en fonction du matériel et de la version IOS/IOS XE exacts :

- Cisco, **VLAN Configuration Guide — Configure VTP**, guide IOS XE, comprenant les modes, annonces, VTPv3, mot de passe, serveur primaire, pruning et commandes de supervision : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html
- Cisco, **Configure VTP on Catalyst Switches** (document de support, mis à jour le 18 août 2026) : https://www.cisco.com/c/en/us/support/docs/lan-switching/vtp/98154-conf-vlan.html

Les points ci-dessus s'appuient sur ces guides Cisco pour les fonctions dépendantes de la version. Les schémas animés et procédures de diagnostic sont des supports pédagogiques ; ils ne remplacent ni la documentation de la plateforme, ni un plan de changement approuvé.

## Points à retenir

- **VTP est une fonction de gestion du plan de contrôle.** Il peut distribuer une base VLAN, mais ne prouve pas à lui seul que les trunks, STP, l'adressage IP et les services fonctionnent.
- **Une révision n'est pas une preuve de justesse.** Compare la base réelle à une référence approuvée et conserve l'état avant/après.
- **VTPv3 renforce le contrôle des mises à jour**, notamment avec le statut de serveur primaire par base, et apporte la propagation des VLAN étendus sur les plateformes compatibles. Le statut primaire doit être revérifié après les événements opérationnels pertinents.
- **Les changements VTP sont des opérations à fort impact potentiel.** Inventaire, sauvegarde vérifiée, test compatible, critères d'arrêt et retour arrière doivent précéder toute migration.
- **Le diagnostic expert triangule les preuves** : `show vtp status`, compteurs, capture de couche 2, base VLAN, trunks, STP, table MAC et tests de services.
