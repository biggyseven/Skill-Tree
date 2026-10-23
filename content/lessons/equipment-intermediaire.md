# Équipements réseau L1/L2 — Niveau intermédiaire

> **Fichier :** `equipment-intermediaire.md`  
> **Niveau :** Intermédiaire  
> **Prérequis :** bases de l’Ethernet, de l’adressage IP et du rôle des switches.  
> **Objectif :** analyser les tables MAC, concevoir des VLAN et trunks, comprendre STP/RSTP, l’agrégation, LLDP, PoE et les métriques d’exploitation, puis appliquer une procédure de dépannage structurée.

## 1. Rappel opérationnel : séparer les mécanismes

Les couches L1 et L2 sont liées, mais une panne physique ne se diagnostique pas comme une incohérence de VLAN. Une interface peut être **up** physiquement tout en étant dans le mauvais VLAN ; elle peut appartenir au bon VLAN tout en étant bloquée par STP ; elle peut être transférée correctement à L2 et échouer ensuite au routage IP.

| Plan | Objets étudiés | Question d’exploitation |
|---|---|---|
| L1 | Média, transceiver, puissance optique, autonegotiation, compteurs PHY | Le lien est-il stable et dans les paramètres attendus ? |
| L2 | MAC source/destination, VLAN, trunk, STP, LACP, contrôle d’accès | La trame peut-elle atteindre le bon port dans le bon domaine L2 ? |
| L3 (diagnostic de frontière) | SVI, passerelle, routes IP, ACL L3 | Le trafic inter-réseaux est-il acheminé et autorisé ? |

## 2. Apprentissage et transfert de la table MAC

<svg xmlns="http://www.w3.org/2000/svg" width="980" height="390" viewBox="0 0 980 390" role="img" aria-labelledby="int1-title int1-desc" style="width:100%;max-width:980px;height:auto;display:block">
<title id="int1-title">Apprentissage d’une table MAC</title><desc id="int1-desc">Un switch apprend l’adresse MAC source d’une trame sur le port d’entrée puis utilise sa table MAC pour transmettre une trame unicast connue vers le port de destination.</desc>
<defs><marker id="int1-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#4de0c1"/></marker><style>.i1bg{fill:#0a1220}.i1c{fill:#151f32;stroke:#344660;stroke-width:1.4}.i1h{font:700 17px sans-serif;fill:#f1f5f9}.i1t{font:13px sans-serif;fill:#cbd5e1}.i1s{font:12px sans-serif;fill:#9fb0c8}.i1f{fill:none;stroke:#4de0c1;stroke-width:3;stroke-dasharray:9 7;marker-end:url(#int1-arr);animation:int1-flow 1.6s linear infinite}@keyframes int1-flow{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.i1f{animation:none}}</style></defs>
<rect class="i1bg" width="980" height="390" rx="18"/><text class="i1h" x="28" y="34">Exemple : une trame connue est dirigée vers le port appris</text>
<rect class="i1c" x="25" y="75" width="205" height="82" rx="10"/><text class="i1h" x="127" y="103" text-anchor="middle">PC-A · port 1</text><text class="i1t" x="127" y="128" text-anchor="middle">MAC A → MAC C</text>
<rect class="i1c" x="365" y="72" width="250" height="92" rx="10"/><text class="i1h" x="490" y="101" text-anchor="middle">Switch L2</text><text class="i1t" x="490" y="125" text-anchor="middle">Apprend MAC A sur port 1</text><text class="i1s" x="490" y="146" text-anchor="middle">Recherche MAC C dans le VLAN</text>
<rect class="i1c" x="750" y="75" width="205" height="82" rx="10"/><text class="i1h" x="852" y="103" text-anchor="middle">PC-C · port 7</text><text class="i1t" x="852" y="128" text-anchor="middle">MAC C</text>
<path class="i1f" d="M230 116 H365"/><path class="i1f" d="M615 116 H750"/>
<rect x="270" y="204" width="440" height="136" rx="12" fill="#102b36" stroke="#267e86"/><text x="292" y="232" style="font:700 16px sans-serif;fill:#99f6e4">Table d’adresses MAC (exemple)</text><text class="i1t" x="292" y="260">VLAN 10 | MAC A | port 1</text><text class="i1t" x="292" y="284">VLAN 10 | MAC C | port 7</text><text class="i1t" x="292" y="312">Destination connue : unicast vers port 7</text><text class="i1s" x="28" y="370">La table est apprise à partir des MAC source ; une entrée expirée peut être apprise à nouveau.</text></svg>

### 2.1. Apprentissage

Un switch apprend normalement l’association **VLAN + MAC source + port d’entrée** lorsqu’il reçoit une trame admissible. Une entrée dynamique peut expirer ; une MAC déplacée peut être réapprise sur un autre port selon les règles du système. Les adresses statiques ou sécurisées obéissent à la configuration de la plateforme.

### 2.2. Comportement à la destination

- **Unicast connu :** transmission vers le port attendu dans le VLAN concerné, sauf cas spécial comme le port d’entrée.
- **Unicast inconnu :** flooding vers les ports éligibles du VLAN, selon les politiques et filtres de la plateforme.
- **Broadcast :** distribution dans le domaine de broadcast VLAN, sauf contrôles de limitation ou filtrage.
- **Multicast :** peut être diffusé à l’ensemble des ports concernés si aucune optimisation n’est active ; IGMP/MLD snooping peut limiter la distribution pour certains groupes.

Le *flooding* dans un VLAN ne signifie pas automatiquement que le switch est défectueux. Il peut être normal après expiration d’une entrée ou pour une destination inconnue.

### 2.3. Vérifications

La commande de consultation de la table MAC varie selon la marque et le système. Exemples typiques à adapter :

```text
show mac address-table
show mac address-table vlan 10
show interfaces status
show interfaces counters errors
```

Ces lignes sont de style Cisco IOS et ne sont pas des commandes universelles. Toujours confirmer la syntaxe de l’OS réseau en exploitation.

## 3. VLAN et ports d’accès

Un VLAN constitue un domaine de diffusion logique. Des hôtes placés dans des VLAN différents ne sont pas mis en communication par le seul switching L2 ; un routeur ou une fonction de couche 3 doit effectuer le routage inter-VLAN, sous réserve des politiques de sécurité.

Un port d’accès est généralement affecté à un VLAN non tagué pour le terminal. Les paramètres précis d’un port d’accès dépendent du constructeur ; ne jamais supposer qu’un port non configuré rejoint le VLAN souhaité.

## 4. Trunk Ethernet et balisage 802.1Q

<svg xmlns="http://www.w3.org/2000/svg" width="980" height="420" viewBox="0 0 980 420" role="img" aria-labelledby="int2-title int2-desc" style="width:100%;max-width:980px;height:auto;display:block">
<title id="int2-title">VLAN et trunk 802.1Q entre deux switches</title><desc id="int2-desc">Un PC utilisateur appartient au VLAN 10 et est connecté au switch A. Un serveur appartient au VLAN 20 et est connecté au switch B. Le trunk entre les switches transporte les deux VLAN avec balisage 802.1Q selon la configuration.</desc>
<defs><marker id="int2-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#60a5fa"/></marker><style>.i2bg{fill:#0a1220}.i2c{fill:#151f32;stroke:#344660;stroke-width:1.4}.i2h{font:700 17px sans-serif;fill:#f1f5f9}.i2t{font:13px sans-serif;fill:#cbd5e1}.i2s{font:12px sans-serif;fill:#9fb0c8}.i2l{fill:none;stroke:#60a5fa;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#int2-arr);animation:int2-flow 1.7s linear infinite}@keyframes int2-flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.i2l{animation:none}}</style></defs>
<rect class="i2bg" width="980" height="420" rx="18"/><text class="i2h" x="28" y="34">Le trunk transporte plusieurs VLAN entre les switches</text>
<rect class="i2c" x="25" y="82" width="190" height="80" rx="10"/><text class="i2h" x="120" y="110" text-anchor="middle">PC utilisateurs</text><text class="i2t" x="120" y="134" text-anchor="middle">VLAN 10 / access</text>
<rect class="i2c" x="270" y="82" width="180" height="80" rx="10"/><text class="i2h" x="360" y="110" text-anchor="middle">Switch A</text><text class="i2t" x="360" y="134" text-anchor="middle">Port access VLAN 10</text>
<rect class="i2c" x="530" y="82" width="180" height="80" rx="10"/><text class="i2h" x="620" y="110" text-anchor="middle">Switch B</text><text class="i2t" x="620" y="134" text-anchor="middle">Port access VLAN 20</text>
<rect class="i2c" x="765" y="82" width="190" height="80" rx="10"/><text class="i2h" x="860" y="110" text-anchor="middle">Serveur</text><text class="i2t" x="860" y="134" text-anchor="middle">VLAN 20 / access</text>
<path class="i2l" d="M215 122 H270"/><path class="i2l" d="M450 122 H530"/><path class="i2l" d="M710 122 H765"/><text class="i2s" x="490" y="99" text-anchor="middle">Trunk 802.1Q</text>
<rect x="25" y="224" width="445" height="125" rx="10" fill="#102b36" stroke="#267e86"/><text x="45" y="251" style="font:700 15px sans-serif;fill:#99f6e4">VLAN 10</text><text class="i2t" x="45" y="276">• Domaine de diffusion logique des utilisateurs.</text><text class="i2t" x="45" y="300">• Son trafic traverse le trunk si VLAN 10 y est autorisé.</text><text class="i2t" x="45" y="324">• Un VLAN n’est pas, à lui seul, une frontière L3.</text>
<rect x="492" y="224" width="463" height="125" rx="10" fill="#28213b" stroke="#8564a8"/><text x="512" y="251" style="font:700 15px sans-serif;fill:#e9d5ff">VLAN 20</text><text class="i2t" x="512" y="276">• Le serveur reste dans son propre domaine L2.</text><text class="i2t" x="512" y="300">• Son trafic traverse le trunk si VLAN 20 y est autorisé.</text><text class="i2t" x="512" y="324">• La communication entre VLAN nécessite une fonction L3.</text>
<text class="i2s" x="25" y="382">Les deux extrémités du trunk doivent être cohérentes ; autoriser uniquement les VLAN nécessaires.</text><text class="i2s" x="25" y="402">Le tag 802.1Q identifie le VLAN transporté sur le lien trunk, selon les règles de la norme.</text></svg>

Un trunk transporte le trafic de plusieurs VLAN entre des switches ou entre un switch et un équipement L3/serveur qui prend en charge les VLAN tagués. La balise VLAN 802.1Q transporte l’identifiant du VLAN dans la trame taguée selon le format de la norme et la configuration.

Bonnes pratiques :

- autoriser uniquement les VLAN requis sur le trunk ;
- vérifier la liste des VLAN autorisés et leur présence effective des deux côtés ;
- harmoniser la configuration du VLAN natif si cette notion est utilisée ;
- éviter de laisser une négociation automatique ou un trunk inattendu sur les ports de terminaux ;
- ne pas assimiler le trunk à un mécanisme de chiffrement ou de sécurité complet.

Le VLAN natif, lorsqu’il est utilisé, doit être traité de manière explicite. Une incohérence entre extrémités peut faire apparaître des trames dans le mauvais VLAN ou rendre la communication imprévisible selon l’implémentation.

## 5. Spanning Tree : empêcher les boucles L2

Une boucle Ethernet de couche 2 peut provoquer une multiplication des broadcasts, des trames dupliquées et des changements rapides de la table MAC. STP et ses variantes organisent la topologie pour maintenir un chemin logique sans boucle, tout en permettant un chemin de secours.

<svg xmlns="http://www.w3.org/2000/svg" width="980" height="390" viewBox="0 0 980 390" role="img" aria-labelledby="int3-title int3-desc" style="width:100%;max-width:980px;height:auto;display:block">
<title id="int3-title">Boucle L2 et rôle du spanning tree</title><desc id="int3-desc">Deux switches sont reliés par deux chemins physiques. STP ou RSTP maintient un chemin de secours bloqué logiquement afin d’éviter une boucle de commutation.</desc>
<defs><style>.i3bg{fill:#0a1220}.i3c{fill:#151f32;stroke:#344660;stroke-width:1.4}.i3h{font:700 17px sans-serif;fill:#f1f5f9}.i3t{font:13px sans-serif;fill:#cbd5e1}.i3s{font:12px sans-serif;fill:#9fb0c8}.i3a{fill:none;stroke:#4de0c1;stroke-width:3;stroke-dasharray:8 7;animation:i3flow 1.6s linear infinite}.i3blocked{fill:none;stroke:#f87171;stroke-width:3;stroke-dasharray:4 7}@keyframes i3flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.i3a{animation:none}}</style></defs>
<rect class="i3bg" width="980" height="390" rx="18"/><text class="i3h" x="28" y="34">Redondance physique sans boucle logique active</text>
<rect class="i3c" x="100" y="114" width="250" height="84" rx="12"/><text class="i3h" x="225" y="148" text-anchor="middle">Switch A</text><text class="i3t" x="225" y="173" text-anchor="middle">Pont racine dans cet exemple</text>
<rect class="i3c" x="630" y="114" width="250" height="84" rx="12"/><text class="i3h" x="755" y="148" text-anchor="middle">Switch B</text><text class="i3t" x="755" y="173" text-anchor="middle">Chemins alternatifs</text>
<path class="i3a" d="M350 132 C430 92 550 92 630 132"/><text class="i3s" x="490" y="84" text-anchor="middle">Chemin actif</text>
<path class="i3blocked" d="M350 181 C430 242 550 242 630 181"/><text x="490" y="269" text-anchor="middle" style="font:700 14px sans-serif;fill:#fca5a5">Chemin redondant bloqué par STP/RSTP</text>
<rect x="145" y="302" width="690" height="55" rx="10" fill="#302127" stroke="#9f4551"/><text class="i3t" x="490" y="325" text-anchor="middle">Sans contrôle de boucle : tempêtes broadcast, duplication</text><text class="i3t" x="490" y="345" text-anchor="middle">de trames et instabilité de la table MAC sont possibles.</text></svg>

### 5.1. Ce que fait STP/RSTP

- construit une topologie L2 logique sans boucle active ;
- sélectionne un bridge racine selon les paramètres de priorité et l’identifiant du bridge ;
- détermine les rôles et états des ports ;
- bloque logiquement certains chemins redondants, puis peut réactiver un chemin après un changement de topologie.

La couleur rouge sur le schéma indique un chemin de secours bloqué logiquement, pas nécessairement un câble débranché.

### 5.2. Pratiques d’exploitation

- choisir et documenter le root bridge attendu ;
- ne pas connecter de boucles non prévues ;
- utiliser les fonctions edge/portfast, BPDU Guard, Root Guard ou Loop Guard uniquement selon la conception et le support de la plateforme ;
- vérifier les voisins, les rôles de ports et les changements de topologie ;
- valider l’effet d’une coupure de câble et d’un redémarrage avant la production.

Les noms et comportements précis des protections sont dépendants du constructeur. Une fonction edge mal placée sur un lien inter-switch peut accélérer une erreur au lieu de la prévenir.

## 6. Agrégation de liens : LACP et limites

L’agrégation de liens permet à plusieurs liens physiques compatibles de former un lien logique (*Link Aggregation Group*, LAG). LACP est utilisé pour négocier et surveiller la participation des membres lorsque les deux côtés le prennent en charge et sont configurés de manière compatible.

Elle peut améliorer la capacité agrégée et la tolérance à une panne de membre, mais **ne transforme pas nécessairement quatre liens de 1 Gbit/s en un seul flux de 4 Gbit/s**. La distribution est généralement effectuée par hachage de champs, et un flux unique peut rester limité à un seul membre. La méthode dépend du constructeur et de la configuration.

Contrôles à faire :

- nombre de membres actifs et état du LAG ;
- vitesse, duplex, média et configuration concordants ;
- VLANs autorisés et MTU cohérents ;
- paramètres LACP des deux côtés ;
- répartition des flux et compteurs par membre ;
- limites matérielles et prise en charge du LAG dans la topologie.

Ne pas connecter simplement des liens redondants entre deux switches en supposant que LACP préviendra une boucle. LACP et STP ont des rôles différents.

## 7. LLDP : cartographier les voisins

LLDP (*Link Layer Discovery Protocol*) annonce et apprend certaines informations de voisinage de manière standardisée. Il peut aider à associer un port à un switch voisin, un téléphone IP ou un point d’accès. Il s’agit d’un outil d’inventaire et de diagnostic, pas d’une autorisation de sécurité en soi.

Exemples de commandes selon l’OS réseau :

```text
show lldp neighbors
show lldp neighbors detail
```

Si LLDP est désactivé, la découverte peut être vide même si le câble et le lien fonctionnent. Inversement, la présence d’un voisin LLDP ne prouve pas que le VLAN et l’accès IP sont correctement configurés.

## 8. PoE : puissance, classes et budget

La conception PoE ne se limite pas à savoir si le port est étiqueté « PoE ». Le PSE annonce et fournit l’alimentation selon les mécanismes du standard et les capacités de l’appareil alimenté. Le budget disponible au niveau du châssis peut être inférieur à la somme théorique des puissances de port.

Pour chaque projet, relever :

- les standards PoE pris en charge par le switch et les terminaux ;
- la puissance maximale fournie par port et le budget global ;
- le nombre de ports PoE chargés simultanément ;
- la puissance réellement requise par les AP/caméras/téléphones ;
- les pertes de câblage, la température, la redondance électrique et le comportement après redémarrage.

Ne pas annoncer une puissance universelle sans préciser le type, la classe, la puissance à la source ou au terminal et les conditions de câble. Utiliser les spécifications du fabricant et le texte IEEE applicable.

## 9. Diagnostic L1/L2 : méthode intermédiaire

### Étape 1 — Valider le média

- vérifier l’état du port, la vitesse et le duplex ;
- examiner les compteurs d’erreurs et les transitions link up/down ;
- confirmer que les modules optiques, la fibre et les longueurs d’onde sont compatibles ;
- remplacer provisoirement par un composant connu comme fonctionnel quand cela est permis.

### Étape 2 — Valider la commutation

- consulter la table MAC sur le VLAN concerné ;
- vérifier le port d’apprentissage de la MAC du terminal ;
- confirmer le mode du port (access/trunk) et le VLAN d’accès ;
- examiner les VLANs autorisés sur le trunk ;
- examiner STP et les états de port ;
- inspecter les erreurs, drops, compteurs de broadcast et événements de changement de topologie.

### Étape 3 — Valider les frontières

Si la trame atteint la bonne passerelle mais que le réseau distant est inaccessible, examiner la route, l’ACL, le pare-feu, le DNS et l’application. Un cours L1/L2 ne dispense pas de vérifier L3 lorsque les preuves montrent que la commutation fonctionne.

## 10. Étude de cas

Trois symptômes se produisent sur un étage :

1. un PC ne monte pas le lien ;
2. un téléphone IP démarre mais ne reçoit pas le bon VLAN voix ;
3. après l’ajout d’un câble entre switches, le réseau subit des interruptions.

**Approche proposée :**

- Pour le PC, commencer par l’état physique, le port, le câble, la carte et la négociation.
- Pour le téléphone, vérifier le modèle de déploiement voix/données, les options d’attribution de VLAN, les politiques du port, le LLDP-MED si utilisé et la configuration constructeur.
- Pour les interruptions après l’ajout du câble, retirer le changement uniquement selon une procédure contrôlée, examiner STP et les logs, vérifier les liens agrégés et confirmer qu’aucune boucle non prévue ne subsiste.

Ne pas corriger trois symptômes en changeant au hasard les VLAN, les vitesses et les paramètres STP à la fois.

## 11. Exercices et corrigés

**Exercice A :** deux postes dans des VLAN différents se trouvent sur le même switch. Pourquoi ne communiquent-ils pas directement par L2 ?  
**Corrigé :** les VLAN séparent les domaines L2. Il faut un service L3 pour transférer entre les sous-réseaux, et les règles de routage/filtrage doivent le permettre.

**Exercice B :** un LAG possède quatre membres de 1 Gbit/s, mais un transfert TCP unique dépasse difficilement 1 Gbit/s. Cela prouve-t-il une panne ?  
**Corrigé :** non. Le hachage peut affecter un flux unique à un seul membre. Examiner plusieurs flux, la méthode de hash, les membres actifs et les compteurs.

**Exercice C :** une MAC change souvent de port dans la même seconde. Quelles hypothèses vérifier ?  
**Corrigé :** boucle L2, chemin redondant mal configuré, terminal déplacé, teaming/virtualisation ou MAC flottante. Examiner les logs, STP, LAG, la topologie physique et les changements récents.

## 12. Validation avant mise en service

- [ ] VLAN de chaque port documenté.
- [ ] Trunks limités aux VLAN requis.
- [ ] STP/RSTP et bridge racine attendus confirmés.
- [ ] LAG/LACP configuré des deux côtés, avec membres cohérents.
- [ ] PoE calculé sur la charge réelle et la marge de croissance.
- [ ] Table MAC, LLDP, compteurs d’erreur et état optique accessibles à l’équipe support.
- [ ] Test de panne et procédure de retour arrière documentés.

## Références techniques

- [IEEE 802.3 — Ethernet Working Group](https://www.ieee802.org/3/) : famille de normes Ethernet, couches physiques et MAC.
- [IEEE 802.1Q-2022 — Bridges and Bridged Networks](https://standards.ieee.org/ieee/802.1q/10323/) : pontage et VLAN ; consulter les amendements applicables.
- [IEEE 802.1AX-2020 — Link Aggregation](https://standards.ieee.org/ieee/149/6768/) : agrégation de liens.
- [IEEE 802.1AB-2026 — Connectivity Discovery](https://standards.ieee.org/ieee/802.1AB/11787/) : découverte de voisins LLDP.
- [IEEE 802.11-2024 — Wireless LAN MAC and PHY](https://standards.ieee.org/ieee/802.11/10548/) : réseau local sans fil.
- [IEEE 802.1X-2020 — Port-Based Network Access Control](https://standards.ieee.org/ieee/C2/10774/802.1X/7345/) : contrôle d’accès par port.
- [IEEE/ISO/IEC 8802-3:2026 — Ethernet](https://www.iso.org/standard/89414.html) : édition ISO/IEC/IEEE publiée en août 2026.
- [IEEE 802.3bt — alimentation PoE sur quatre paires](https://standards.ieee.org/ieee/8802-3_2021_Amd2/10811/).

> Les pages de standards servent à vérifier l’édition et le statut. Pour une installation contractuelle, utiliser le texte normatif applicable, les prescriptions du pays, les règles du bâtiment, ainsi que les documents du constructeur ; ne pas déduire une conformité complète à partir de ce cours seul.
