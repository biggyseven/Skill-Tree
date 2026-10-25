# Architecture Réseau — Niveau Intermédiaire

> **Parcours :** Réseaux informatiques · **Niveau :** Intermédiaire · **Fichier :** `archi-reseau-intermediaire.md`  
> **Public :** personnes maîtrisant les bases d’un LAN, les VLAN, l’adressage IPv4, les rôles des switches/routeurs et les principes élémentaires de routage.  
> **Objectif :** passer de la lecture d’un réseau simple à la conception, la justification et la validation d’une architecture d’entreprise de taille moyenne.

## Place dans le parcours

Le niveau Débutant présente les équipements, les topologies, le modèle hiérarchique, les VLAN, l’adressage, les services et les bases de sécurité. Ce niveau ne répète pas ces définitions une par une : il les transforme en décisions d’architecture, compare plusieurs options, identifie les compromis et introduit la validation opérationnelle. Le niveau Expert pourra ensuite approfondir les grands campus, les réseaux multi-sites, les architectures routées à grande échelle, l’automatisation et les scénarios de résilience avancée.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir :

- choisir entre une architecture à deux couches, à trois couches ou un accès routé, en expliquant les compromis ;
- définir des domaines de panne, des frontières L2/L3 et une stratégie de passerelles redondantes ;
- construire un plan IPv4/IPv6, réserver des blocs et comprendre les conditions d’un résumé de routes ;
- concevoir la segmentation par fonction et par niveau de confiance, sans multiplier les VLAN sans raison ;
- documenter les chemins nominal et de secours, les protocoles de convergence et les dépendances ;
- choisir des mesures de capacité, QoS et supervision alignées sur les besoins métier ;
- produire une architecture logique, une nomenclature et un plan de test exploitable par une équipe technique.

## Prérequis et méthode de travail

Tu dois déjà reconnaître une adresse IP/prefixe, une passerelle, un VLAN, un trunk, une route et le rôle d’un pare-feu. Si l’un de ces concepts reste flou, reviens au cours `archi-reseau-debutant.md`. Pour chaque schéma, identifie les chemins de données, les points de contrôle et les points de panne. Pour chaque décision, note : **besoin → choix → compromis → preuve de validation**.


## 1. Partir des besoins et non des équipements

Une architecture ne devrait pas commencer par l’achat d’un switch ou le choix d’un protocole de routage. Elle commence par les usages à prendre en charge, les contraintes, les niveaux de service et les conséquences d’une interruption.

### 1.1 Recueillir les besoins métier

Interroge les propriétaires des services et les utilisateurs techniques :

| Dimension | Questions à poser | Conséquence pour le design |
|---|---|---|
| Utilisateurs | Combien aujourd’hui et dans trois ans ? Où travaillent-ils ? | Nombre de ports, Wi-Fi, capacité des uplinks |
| Applications | ERP, voix, visioconférence, sauvegarde, SaaS, services locaux ? | Latence, débit, segmentation, QoS |
| Disponibilité | Quelles interruptions sont acceptables ? À quelle heure peut-on maintenir ? | Redondance, fenêtres de changement, procédure de secours |
| Sécurité | Quelles données sont sensibles ? Quels accès doivent être isolés ? | Zones, ACL, pare-feu, identité, journalisation |
| Exploitation | Qui dépanne ? Quels outils et compétences sont disponibles ? | Simplicité, supervision, documentation |
| Budget | Investissement initial ou coût sur plusieurs années ? | Dimensionnement, support, pièces de rechange |
| Conformité | Quelles obligations de journalisation ou de séparation ? | Rétention, contrôles d’accès, preuves d’audit |

Les demandes vagues comme « réseau rapide et sécurisé » doivent devenir des exigences testables. Par exemple : « une perte d’un lien d’accès ne doit pas interrompre les applications critiques plus de X secondes » est mesurable ; « le réseau doit être très disponible » ne l’est pas tant que le seuil n’est pas défini.

### 1.2 Distinguer disponibilité et résilience

La **disponibilité** se mesure sur une période ; la **résilience** décrit la capacité à continuer ou à récupérer après un incident. Deux liens ne signifient pas automatiquement une architecture résiliente : ils peuvent partager le même conduit, le même opérateur, le même équipement d’agrégation ou la même alimentation.

Il faut distinguer :

- **redondance de lien** : un câble ou une optique peut tomber sans isoler le site ;
- **redondance d’équipement** : la panne d’un switch, routeur ou pare-feu ne supprime pas toute la fonction ;
- **redondance de chemin** : le trafic possède un trajet alternatif indépendant ;
- **redondance de service** : les services DNS, DHCP, AAA, supervision et authentification restent joignables ;
- **diversité de risque** : les chemins de secours ne partagent pas le même point physique ou opérationnel critique.

### 1.3 Créer une matrice exigences-tests

| Exigence | Décision d’architecture | Test de validation | Preuve attendue |
|---|---|---|---|
| Perte d’un uplink tolérée | Deux uplinks et mécanisme de convergence adapté | Couper un lien en fenêtre de test | Durée de perte observée, état des liens |
| Réseau invité isolé | VLAN et politique vers Internet uniquement | Depuis un client invité, tester les préfixes internes | Échecs attendus et journaux |
| Téléphonie prioritaire en congestion | Politique QoS cohérente de bout en bout | Générer une charge contrôlée | Latence/perte et compteurs de files |
| Adresses réutilisables entre sites | Plan IP hiérarchique sans chevauchement | Vérifier les préfixes dans l’inventaire | Export de plan IP et table de routage |

**Règle pratique :** si une exigence n’a ni décision explicite ni test, elle risque d’être oubliée lors de l’implémentation.


## 2. Choisir le modèle de campus

Un modèle d’architecture n’est pas une recette universelle. Il organise les fonctions, les frontières de panne et les flux de trafic. La bonne solution dépend surtout de la taille, des contraintes de câblage, de la densité, de la capacité des équipements et du modèle opérationnel de l’entreprise.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520"><rect x="1" y="1" width="1098" height="518" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Architecture de campus : choisir le bon modèle</text><line x1="275" y1="170" x2="275" y2="205" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="165" y1="205" x2="385" y2="205" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="165" y1="205" x2="165" y2="230" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="165.0" y1="230.0" x2="159.3" y2="220.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="165.0" y1="230.0" x2="170.7" y2="220.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="385" y1="205" x2="385" y2="230" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="385.0" y1="230.0" x2="379.3" y2="220.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="385.0" y1="230.0" x2="390.7" y2="220.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="165" y1="292" x2="165" y2="328" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="385" y1="292" x2="385" y2="328" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="80" y1="328" x2="470" y2="328" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="80" y1="328" x2="80" y2="352" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="80.0" y1="352.0" x2="74.3" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="80.0" y1="352.0" x2="85.7" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275" y1="328" x2="275" y2="352" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="352.0" x2="269.3" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="352.0" x2="280.7" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="470" y1="328" x2="470" y2="352" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="470.0" y1="352.0" x2="464.3" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="470.0" y1="352.0" x2="475.7" y2="342.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="825" y1="170" x2="825" y2="205" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="655" y1="205" x2="995" y2="205" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="655" y1="205" x2="655" y2="230" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="655.0" y1="230.0" x2="649.3" y2="220.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="655.0" y1="230.0" x2="660.7" y2="220.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="995" y1="205" x2="995" y2="230" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="995.0" y1="230.0" x2="989.3" y2="220.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="995.0" y1="230.0" x2="1000.7" y2="220.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="725" y1="296" x2="725" y2="330" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="925" y1="296" x2="925" y2="330" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="650" y1="330" x2="1000" y2="330" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="650" y1="330" x2="650" y2="352" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="650.0" y1="352.0" x2="644.3" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="650.0" y1="352.0" x2="655.7" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="825" y1="330" x2="825" y2="352" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="825.0" y1="352.0" x2="819.3" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="825.0" y1="352.0" x2="830.7" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="1000" y1="330" x2="1000" y2="352" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="1000.0" y1="352.0" x2="994.3" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="1000.0" y1="352.0" x2="1005.7" y2="342.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><rect x="50" y="105" width="450" height="65" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="275.0" y="132.96" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f8fafc" text-anchor="middle">Modele 3 couches</text><text x="275.0" y="154.96" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#cbd5e1" text-anchor="middle">Acces / Distribution / Coeur</text><rect x="600" y="105" width="450" height="65" rx="12" fill="#102a43" stroke="#4ade80" stroke-width="2"/><text x="825.0" y="132.96" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f8fafc" text-anchor="middle">Modele 2 couches</text><text x="825.0" y="154.96" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#cbd5e1" text-anchor="middle">Acces + coeur-distribution fusionnes</text><rect x="75" y="230" width="180" height="62" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="165.0" y="257.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Distribution A</text><text x="165.0" y="275.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">SVI, politiques</text><rect x="295" y="230" width="180" height="62" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="385.0" y="257.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Distribution B</text><text x="385.0" y="275.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">SVI, politiques</text><rect x="25" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="80.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 1</text><text x="80.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Etage 1</text><rect x="220" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="275.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 2</text><text x="275.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Etage 2</text><rect x="415" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="470.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 3</text><text x="470.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Etage 3</text><rect x="655" y="230" width="140" height="66" rx="12" fill="#102a43" stroke="#4ade80" stroke-width="2"/><text x="725.0" y="259.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Bloc L3</text><text x="725.0" y="277.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Paire redondante</text><rect x="855" y="230" width="140" height="66" rx="12" fill="#102a43" stroke="#4ade80" stroke-width="2"/><text x="925.0" y="259.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Bloc L3</text><text x="925.0" y="277.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Paire redondante</text><rect x="595" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="650.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 1</text><text x="650.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Site compact</text><rect x="770" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="825.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 2</text><text x="825.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Site compact</text><rect x="945" y="352" width="110" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="1000.0" y="377.1" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces 3</text><text x="1000.0" y="395.1" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Site compact</text><text x="275" y="455" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#bae6fd" text-anchor="middle">Plus de separation des fonctions</text><text x="825" y="455" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#bbf7d0" text-anchor="middle">Moins de couches, moins de sauts</text></svg>

### 2.1 Architecture à trois couches

- **Accès :** ports terminaux, PoE, contrôle de bord, VLAN si le domaine L2 est conservé jusqu’à la distribution.
- **Distribution :** agrégation de l’accès, fonctions L3, politiques et limites de propagation des pannes selon le design.
- **Cœur :** transport rapide et prévisible entre blocs de distribution, services centraux et WAN. Il doit rester aussi simple que possible.

Ce modèle peut être utile dans un campus étendu, un environnement avec de nombreux bâtiments ou lorsque les fonctions de politique et de transport doivent rester distinctes. Il a un coût en équipements, liens et opérations. Il faut éviter de conserver trois couches uniquement par tradition si elles n’apportent aucun bénéfice concret.

### 2.2 Architecture à deux couches ou cœur-distribution fusionné

Dans un site plus compact, la distribution et le cœur peuvent être combinés. Le nombre de sauts et d’équipements baisse, mais la paire combinée devient un domaine de panne important et doit être dimensionnée pour le rôle cumulé. Le design doit préciser si les deux membres sont indépendants, comment les passerelles sont redondées et ce qui se passe en cas de séparation de la paire.

### 2.3 Accès L2 ou accès routé

**Accès L2 :** les VLAN traversent les uplinks vers une frontière de routage supérieure. C’est familier, permet certains besoins de mobilité L2 et reste pratique sur des réseaux simples. Le coût est un domaine L2 plus étendu, des dépendances à Spanning Tree et la nécessité d’éviter les trunks inutiles.

**Accès routé (L3 jusqu’à l’accès) :** les liens montants sont des liaisons routées et chaque bloc peut avoir une frontière de panne plus petite. Le routage dynamique peut offrir des chemins alternatifs sans étendre le domaine L2. Le design exige une stratégie d’adressage, de routage, de passerelles et de services qui corresponde à cette frontière.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="490" viewBox="0 0 1100 490"><rect x="1" y="1" width="1098" height="488" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces couche 2 ou acces routé : deux modèles</text><line x1="130" y1="155" x2="130" y2="205" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="130.0" y1="205.0" x2="124.3" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="130.0" y1="205.0" x2="135.7" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275" y1="155" x2="275" y2="205" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="205.0" x2="269.3" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="205.0" x2="280.7" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="420" y1="155" x2="420" y2="205" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="420.0" y1="205.0" x2="414.3" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="420.0" y1="205.0" x2="425.7" y2="195.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="130" y1="263" x2="130" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="130" y1="300" x2="275" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="275" y1="263" x2="275" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="275" y1="300" x2="275" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="420" y1="263" x2="420" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="420" y1="300" x2="275" y2="300" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/><line x1="275" y1="300" x2="275" y2="330" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="330.0" x2="269.3" y2="320.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="330.0" x2="280.7" y2="320.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="670" y1="155" x2="670" y2="205" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="670.0" y1="205.0" x2="664.3" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="670.0" y1="205.0" x2="675.7" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="820" y1="155" x2="820" y2="205" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="820.0" y1="205.0" x2="814.3" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="820.0" y1="205.0" x2="825.7" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="970" y1="155" x2="970" y2="205" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="970.0" y1="205.0" x2="964.3" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="970.0" y1="205.0" x2="975.7" y2="195.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="670" y1="263" x2="670" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="670" y1="300" x2="820" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="820" y1="263" x2="820" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="820" y1="300" x2="820" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="970" y1="263" x2="970" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="970" y1="300" x2="820" y2="300" stroke="#4ade80" stroke-width="2" stroke-linecap="round"/><line x1="820" y1="300" x2="820" y2="330" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="820.0" y1="330.0" x2="814.3" y2="320.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="820.0" y1="330.0" x2="825.7" y2="320.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><rect x="40" y="95" width="480" height="60" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="280.0" y="120.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces L2 traditionnel</text><text x="280.0" y="142.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">VLAN et trunk vers la distribution</text><rect x="580" y="95" width="480" height="60" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="820.0" y="120.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces routé (L3)</text><text x="820.0" y="142.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Liens point-a-point et routage jusqu’a l’acces</text><rect x="82" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="130.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="130.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">VLAN L2</text><rect x="227" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="275.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="275.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">VLAN L2</text><rect x="372" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="420.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="420.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">VLAN L2</text><rect x="120" y="330" width="340" height="62" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="290.0" y="357.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Distribution L3</text><text x="290.0" y="375.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">SVI, STP, HSRP/VRRP selon design</text><rect x="622" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="670.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="670.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">L3</text><rect x="772" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="820.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="820.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">L3</text><rect x="922" y="205" width="96" height="58" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="970.0" y="229.76" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="middle">SW acces</text><text x="970.0" y="247.76" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">L3</text><rect x="660" y="330" width="320" height="62" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="820.0" y="357.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Coeur / routage</text><text x="820.0" y="375.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">OSPF, IS-IS ou routes statiques</text><text x="280" y="440" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#bae6fd" text-anchor="middle">Avantage : domaine L2 structure</text><text x="820" y="440" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#bbf7d0" text-anchor="middle">Avantage : panne contenue, convergence L3</text></svg>

### 2.4 Questions de décision

| Question | Si la réponse est « oui » | Piste à étudier |
|---|---|---|
| Les VLAN doivent-ils réellement s’étendre sur plusieurs bâtiments ? | Oui | Garder une extension L2 justifiée ; sinon privilégier des frontières routées |
| La perte d’un switch d’accès doit-elle rester limitée à ses utilisateurs ? | Oui | Uplinks, redondance et domaines de panne explicites |
| La distribution doit-elle appliquer de nombreuses politiques différentes ? | Oui | Séparer les fonctions ou documenter précisément leur emplacement |
| L’équipe maîtrise-t-elle OSPF/IS-IS et le dépannage L3 ? | Non | Éviter une complexité L3 que l’équipe ne peut pas exploiter |
| La croissance prévue est-elle importante ? | Oui | Réserver des blocs et concevoir des chemins évolutifs dès le départ |

Il n’est pas nécessaire de choisir le design le plus sophistiqué. Il faut choisir celui qui satisfait les exigences avec le moins de complexité inutile.


## 3. Concevoir la segmentation logique

La segmentation limite les domaines de diffusion, facilite l’application de politiques et rend les incidents plus faciles à contenir. Elle n’est pas une fin en soi. Créer un VLAN par utilisateur ou par application sans stratégie de sécurité, d’adressage et d’exploitation peut accroître la complexité sans réel gain.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Segmentation logique : VLAN, sous-reseaux et passerelles</text><line x1="175" y1="181" x2="175" y2="208" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="175" y1="208" x2="410" y2="208" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="410" y1="208" x2="410" y2="235" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="410.0" y1="235.0" x2="404.3" y2="225.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="410.0" y1="235.0" x2="415.7" y2="225.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="550" y1="181" x2="550" y2="235" stroke="#c084fc" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="235.0" x2="544.3" y2="225.6" stroke="#c084fc" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="235.0" x2="555.7" y2="225.6" stroke="#c084fc" stroke-width="3" stroke-linecap="round"/><line x1="925" y1="181" x2="925" y2="208" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="925" y1="208" x2="690" y2="208" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="690" y1="208" x2="690" y2="235" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="690.0" y1="235.0" x2="684.3" y2="225.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="690.0" y1="235.0" x2="695.7" y2="225.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="550" y1="327" x2="550" y2="375" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="375.0" x2="544.3" y2="365.6" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="375.0" x2="555.7" y2="365.6" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><rect x="40" y="95" width="270" height="86" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="175.0" y="132.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">VLAN 10</text><text x="175.0" y="154.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Utilisateurs / 10.10.10.0/24</text><rect x="415" y="95" width="270" height="86" rx="12" fill="#2b1d42" stroke="#c084fc" stroke-width="2"/><text x="550.0" y="132.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">VLAN 20</text><text x="550.0" y="154.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Voix / 10.10.20.0/24</text><rect x="790" y="95" width="270" height="86" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="925.0" y="132.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">VLAN 30</text><text x="925.0" y="154.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Serveurs / 10.10.30.0/24</text><rect x="310" y="235" width="480" height="92" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="550.0" y="276.46" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f8fafc" text-anchor="middle">Commutateur L3 / passerelles SVI</text><text x="550.0" y="298.46" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#cbd5e1" text-anchor="middle">.10.10 / .20.10 / .30.10  -  routage inter-VLAN</text><rect x="360" y="375" width="380" height="65" rx="12" fill="#3b1d24" stroke="#fb7185" stroke-width="2"/><text x="550.0" y="402.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Pare-feu / ACL selon le besoin</text><text x="550.0" y="424.28" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Controler les echanges autorises</text><text x="550" y="468" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#e2e8f0" text-anchor="middle">Un VLAN definit un domaine L2 ; un sous-reseau IP et une passerelle organisent le L3.</text></svg>

### 3.1 Définir une taxonomie de VLAN

Les noms doivent refléter une fonction ou une zone stable, non une personne :

- utilisateurs internes ;
- téléphonie ;
- imprimantes et périphériques ;
- serveurs applicatifs ;
- gestion d’infrastructure ;
- Wi-Fi entreprise ;
- Wi-Fi invité ;
- IoT/caméras ;
- DMZ ou services exposés, si le modèle de sécurité le prévoit.

Chaque VLAN doit avoir un propriétaire, une plage IP, une passerelle, des serveurs DHCP/DNS, une politique d’accès et une justification de sa portée. Les équipements de gestion doivent être séparés du trafic utilisateur ordinaire, avec un accès administratif limité.

### 3.2 VLAN, sous-réseau et zone de sécurité : notions distinctes

Un VLAN est un domaine de couche 2. Un sous-réseau IP est un préfixe de couche 3. Une zone de sécurité est un regroupement de ressources ou d’interfaces soumis à une politique cohérente. Ils sont souvent associés un à un dans un campus, mais ce n’est pas une loi universelle.

L’association 1 VLAN ↔ 1 sous-réseau simplifie de nombreux réseaux d’accès, car elle facilite le dépannage et les passerelles. Toutefois, la segmentation de sécurité doit être appliquée par des contrôles adaptés : les VLAN ne filtrent pas à eux seuls les communications routées.

### 3.3 Inter-VLAN : où appliquer la politique ?

Le routage inter-VLAN peut se faire sur un commutateur multicouche via des interfaces virtuelles (SVI), ou via un routeur/pare-feu selon la taille et la politique. Le choix modifie la capacité, la latence, la visibilité et l’endroit où les règles sont contrôlées.

- **SVI sur switch L3 :** efficace pour de nombreux flux internes ; utilise ACL si elles sont adaptées aux besoins ; il faut vérifier où les journaux et l’inspection doivent être effectués.
- **Passage via pare-feu :** offre une politique d’état et une visibilité plus riches ; attention au débit, aux interfaces, aux sessions et à la symétrie des chemins.
- **Modèle hybride :** certaines communications restent au niveau L3 du campus, tandis que les zones à confiance différente traversent le pare-feu.

La décision doit être écrite dans la matrice de flux. Éviter de placer un pare-feu dans un chemin sans mesurer son débit soutenu, le nombre de sessions et le comportement en cas de perte d’un membre.


## 4. Plan d’adressage IPv4 et IPv6

Un plan d’adressage intermédiaire organise les préfixes par site, fonction et évolution attendue. Le plan doit empêcher les chevauchements, simplifier les résumés de routes et éviter une renumérotation générale à chaque extension.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Plan d’adressage : hierarchie, resumés et limites de panne</text><line x1="550" y1="151" x2="550" y2="185" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="155" y1="185" x2="945" y2="185" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="155" y1="185" x2="155" y2="220" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="155.0" y1="220.0" x2="149.3" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="155.0" y1="220.0" x2="160.7" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="418" y1="185" x2="418" y2="220" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="418.0" y1="220.0" x2="412.3" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="418.0" y1="220.0" x2="423.7" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="682" y1="185" x2="682" y2="220" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="682.0" y1="220.0" x2="676.3" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="682.0" y1="220.0" x2="687.7" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="945" y1="185" x2="945" y2="220" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="945.0" y1="220.0" x2="939.3" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="945.0" y1="220.0" x2="950.7" y2="210.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><rect x="365" y="85" width="370" height="66" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="550.0" y="113.46000000000001" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f8fafc" text-anchor="middle">Bloc du site</text><text x="550.0" y="135.46" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#cbd5e1" text-anchor="middle">10.40.0.0/16</text><rect x="40" y="220" width="230" height="78" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="155.0" y="255.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Campus</text><text x="155.0" y="273.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">10.40.0.0/18</text><rect x="303" y="220" width="230" height="78" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="418.0" y="255.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Datacenter</text><text x="418.0" y="273.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">10.40.64.0/19</text><rect x="567" y="220" width="230" height="78" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="682.0" y="255.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">WAN</text><text x="682.0" y="273.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">10.40.96.0/20</text><rect x="830" y="220" width="230" height="78" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="945.0" y="255.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Services</text><text x="945.0" y="273.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">10.40.112.0/20</text><text x="550" y="354" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">Reserver des plages par fonction et par site ; documenter les exceptions.</text><text x="550" y="395" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#fcd34d" text-anchor="middle">Le résumé n’est sûr que si les prefixes inclus sont réellement joignables par l’annonce.</text><text x="550" y="438" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#cbd5e1" text-anchor="middle">Eviter les chevauchements entre LAN, VPN, cloud et partenaires.</text></svg>

### 4.1 Méthode pour construire un plan IPv4

1. Lister les sites, zones, fonctions et tailles attendues.
2. Réserver un bloc global par entreprise ou grand périmètre, selon les contraintes existantes.
3. Attribuer des sous-blocs alignés aux sites ou fonctions ; garder des plages de croissance.
4. Documenter les sous-réseaux utilisateur, serveurs, gestion, transit et loopbacks séparément.
5. Contrôler les chevauchements avec VPN, cloud, partenaires, acquisitions et environnements de laboratoire.
6. Vérifier que les routes résumées ne couvrent pas des préfixes qui ne sont pas réellement joignables par le point annonçant le résumé.

### 4.2 Exemple d’allocation

Supposons un bloc privé `10.40.0.0/16`. Une organisation pourrait allouer un `/18` au campus, un `/19` au datacenter, un `/20` aux liens WAN et un `/20` aux services partagés. Les tailles ci-dessus ne sont qu’un exemple de méthode ; elles doivent être confirmées à partir des besoins et du nombre de sous-réseaux. Il ne faut pas recopier des préfixes d’exemple dans un réseau existant sans vérifier les conflits.

Pour une allocation plus fine, définir la taille nécessaire à partir du nombre d’hôtes et de la marge de croissance. Un préfixe `/24` comporte 256 adresses IPv4 au total, mais le nombre utilisable dépend du contexte et du design ; sur un LAN IPv4 classique, deux adresses sont réservées au réseau et au broadcast. Sur des liens point-à-point, des préfixes plus petits peuvent être adaptés si les équipements et conventions le permettent.

### 4.3 Résumé de routes et agrégation

L’agrégation simplifie les tables de routage et réduit le nombre d’annonces, mais elle introduit une obligation de cohérence. Une annonce `10.40.0.0/16` est acceptable uniquement si le routeur qui l’annonce peut acheminer correctement vers tous les sous-réseaux que le résumé prétend couvrir, ou si les trous sont traités consciemment.

À vérifier :

- le préfixe résumé est-il aligné sur une frontière CIDR valide ?
- tous les sous-réseaux concernés existent-ils ou sont-ils prévus ?
- une route moins spécifique ne masque-t-elle pas une panne en attirant du trafic vers un équipement qui n’a plus de chemin ?
- les filtres d’export/import autorisent-ils uniquement les préfixes prévus ?

### 4.4 IPv6 : intégrer le préfixe global au design

IPv6 doit être planifié en parallèle et non ajouté à la dernière minute. Documenter les préfixes, les Router Advertisements, DHCPv6 selon les besoins, DNS AAAA/PTR, les politiques de filtrage et les mécanismes de supervision. La taille d’un sous-réseau utilisateur IPv6 est souvent un `/64`, mais les conventions de l’organisation et les contraintes de la plateforme doivent guider le plan.

IPv6 n’est pas une version « sans sécurité » ni un système à traiter uniquement par NAT. Le filtrage, la maîtrise des Router Advertisements, la surveillance ND et la gestion des adresses restent essentiels. Vérifier aussi les chemins de retour : un service joignable en IPv4 ne l’est pas nécessairement en IPv6 et inversement.


## 5. Redondance et domaines de panne

La redondance se conçoit en partant de la panne que l’on souhaite tolérer. Un lien secondaire ne garantit pas un secours si la route alternative dépend du même port-channel, de la même alimentation, du même chemin de fibre ou d’un seul opérateur.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="510" viewBox="0 0 1100 510"><rect x="1" y="1" width="1098" height="508" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Redondance utile : chemins, equipements et domaines de panne</text><line x1="205" y1="157" x2="270" y2="230" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="270.0" y1="230.0" x2="259.5" y2="226.8" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="270.0" y1="230.0" x2="268.1" y2="219.2" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="895" y1="157" x2="830" y2="230" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="830.0" y1="230.0" x2="831.9" y2="219.2" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="830.0" y1="230.0" x2="840.5" y2="226.8" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="430" y1="267" x2="670" y2="267" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="670.0" y1="267.0" x2="660.6" y2="272.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="670.0" y1="267.0" x2="660.6" y2="261.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="800" y1="305" x2="700" y2="365" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="700.0" y1="365.0" x2="705.1" y2="355.2" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="700.0" y1="365.0" x2="711.0" y2="365.1" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="300" y1="305" x2="400" y2="365" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="400.0" y1="365.0" x2="389.0" y2="365.1" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="400.0" y1="365.0" x2="394.9" y2="355.2" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><rect x="80" y="95" width="250" height="62" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="205.0" y="120.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces A</text><text x="205.0" y="142.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Lien vers distribution</text><rect x="770" y="95" width="250" height="62" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="895.0" y="120.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Acces B</text><text x="895.0" y="142.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Lien vers distribution</text><rect x="170" y="230" width="260" height="75" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="300.0" y="262.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Distribution A</text><text x="300.0" y="284.28" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Passerelle active ou membre</text><rect x="670" y="230" width="260" height="75" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="800.0" y="262.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Distribution B</text><text x="800.0" y="284.28" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Passerelle secours ou pair</text><rect x="365" y="365" width="370" height="68" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="550.0" y="393.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Coeur / WAN</text><text x="550.0" y="415.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Chemins independants si possibles</text><text x="550" y="205" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#fcd34d" text-anchor="middle">Lien peer / adjacency</text><text x="550" y="470" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#e2e8f0" text-anchor="middle">Tester la perte d’un lien, d’un equipement, d’une alimentation et d’un chemin amont.</text></svg>

### 5.1 Construire une matrice de panne

| Incident | Détection | Comportement attendu | Test |
|---|---|---|---|
| Perte d’un membre d’un agrégat | État d’interface/LACP | Continuité si capacité restante suffisante | Déconnecter un lien en test |
| Perte d’un switch d’accès | Voisins/up-links/sondes | Perte limitée aux ports dépendants | Couper l’équipement de test |
| Perte d’une passerelle | FHRP, tracking ou routage | Nouvelle passerelle active/chemin disponible | Simuler panne et vérifier ARP/ND, route, sessions |
| Perte d’un circuit WAN | Interface, BFD ou sonde | Bascule vers le chemin alternatif | Couper le lien ou simuler une panne de service |
| Perte d’un DNS/DHCP/AAA | Supervision de service | Serveur secondaire ou procédure de secours | Arrêter le service dans un environnement de test |
| Séparation de deux équipements redondants | Keepalive/peer-link selon plateforme | Eviter split-brain ou boucle | Tester conformément au guide constructeur |

### 5.2 Passerelles de premier saut

HSRP, VRRP ou d’autres mécanismes de passerelle redondante peuvent présenter une adresse IP virtuelle aux clients. La conception doit préciser la priorité, la préemption ou son absence, les minuteries, le suivi d’uplink et les risques liés au retour au nominal. Les comportements exacts dépendent du protocole et de la plateforme.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="490" viewBox="0 0 1100 490"><rect x="1" y="1" width="1098" height="488" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Passerelle redondante : adresse virtuelle et etat des pairs</text><line x1="325" y1="140" x2="420" y2="120" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="420.0" y1="120.0" x2="412.0" y2="127.6" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="420.0" y1="120.0" x2="409.6" y2="116.3" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="485" y1="159" x2="405" y2="245" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="405.0" y1="245.0" x2="407.2" y2="234.2" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="405.0" y1="245.0" x2="415.6" y2="242.0" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="650" y1="159" x2="730" y2="245" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="730.0" y1="245.0" x2="719.4" y2="242.0" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="730.0" y1="245.0" x2="727.8" y2="234.2" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="520" y1="281" x2="610" y2="281" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="610.0" y1="281.0" x2="600.6" y2="286.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="610.0" y1="281.0" x2="600.6" y2="275.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="490" y1="417" x2="610" y2="417" stroke="#fbbf24" stroke-width="2" stroke-linecap="round"/><line x1="610.0" y1="417.0" x2="600.6" y2="422.7" stroke="#fbbf24" stroke-width="2" stroke-linecap="round"/><line x1="610.0" y1="417.0" x2="600.6" y2="411.3" stroke="#fbbf24" stroke-width="2" stroke-linecap="round"/><rect x="55" y="105" width="270" height="74" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="190.0" y="136.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Clients VLAN 10</text><text x="190.0" y="158.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Passerelle : 10.10.10.1</text><rect x="420" y="85" width="300" height="74" rx="12" fill="#3b1d24" stroke="#fb7185" stroke-width="2"/><text x="570.0" y="116.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">VIP du groupe FHRP</text><text x="570.0" y="138.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">10.10.10.1 - passerelle logique</text><rect x="275" y="245" width="245" height="72" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="397.5" y="275.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Switch L3 A</text><text x="397.5" y="297.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">SVI : 10.10.10.2</text><rect x="610" y="245" width="245" height="72" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="732.5" y="275.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Switch L3 B</text><text x="732.5" y="297.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">SVI : 10.10.10.3</text><text x="565" y="218" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#fcd34d" text-anchor="middle">Etat et hellos entre pairs</text><text x="550" y="355" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">La VIP est annoncee par le membre actif selon le protocole et son etat.</text><rect x="100" y="390" width="390" height="55" rx="12" fill="#132238" stroke="#fbbf24" stroke-width="2"/><text x="295.0" y="413.6" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Surveillance</text><text x="295.0" y="431.6" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Etat local + suivi du chemin amont</text><rect x="610" y="390" width="390" height="55" rx="12" fill="#132238" stroke="#fbbf24" stroke-width="2"/><text x="805.0" y="413.6" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f8fafc" text-anchor="middle">Bascule</text><text x="805.0" y="431.6" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Delai, seuil de perte et retour au nominal</text></svg>

Une erreur courante consiste à suivre uniquement l’état physique de l’interface locale. L’interface peut rester active alors que le chemin amont ou le service est inaccessible. Un tracking plus utile dépend du service : état d’un voisin, état d’une route, sonde IP SLA ou objet suivi supporté par la plateforme. L’usage de sondes doit être calibré pour ne pas déclencher des bascules sur des pertes isolées et transitoires.

### 5.3 Agrégation de liens

LACP peut former un agrégat logique à partir de plusieurs liens physiques, dans les limites de la plateforme et du design. Il augmente la capacité disponible selon le hachage des flux et améliore la tolérance à la perte d’un membre. Il ne transforme pas nécessairement deux liens 1 Gbit/s en un seul flux à 2 Gbit/s : un flux donné reste généralement distribué selon une clé de hachage et peut être limité par un seul membre.

Documenter les paramètres LACP, le côté actif/passif si applicable, la cohérence des VLAN et MTU sur tous les membres, les capacités en cas de perte d’un lien, ainsi que la diversité physique réelle. Un agrégat sur un seul équipement de destination ne protège pas automatiquement contre la panne de cet équipement.

### 5.4 Spanning Tree et boucle L2

Dans un domaine Ethernet L2 redondant, STP/RSTP/MST ou un mécanisme équivalent empêche certaines boucles en bloquant des chemins. La redondance physique et le transfert simultané par tous les liens ne sont donc pas synonymes. Le design doit définir le root bridge, les liens d’accès, les protections de ports et les chemins qui doivent être bloqués ou utilisés.

- Fixer la racine STP sur des équipements prévus à cet effet.
- Utiliser PortFast/edge uniquement sur les ports terminaux correspondants.
- Appliquer BPDU Guard là où les ports edge ne doivent pas recevoir de BPDU, selon la politique de l’entreprise.
- Tester les liens redondants et surveiller les changements de topologie.
- Éviter les VLAN étendus sans besoin précis.

Les noms de commandes et la syntaxe varient selon Cisco IOS, IOS XE, NX-OS et d’autres systèmes. Valider la commande exacte sur l’équipement cible avant déploiement.


## 6. Routage et frontières L2/L3

Le routage est un élément de la conception des domaines de panne et du chemin des flux, pas seulement un protocole à activer. Les routes statiques peuvent convenir à des liaisons simples et stables ; OSPF ou IS-IS sont courants dans des domaines IGP ; BGP est généralement utilisé aux frontières d’administration, notamment entre systèmes autonomes ou dans certaines fabric/architectures de grande taille.

### 6.1 Décider où se termine le domaine L2

Une frontière L3 proche de l’accès réduit l’extension des domaines de diffusion et peut faciliter la convergence. Une extension L2 peut être nécessaire dans certains environnements, mais augmente la surface de panne et les dépendances à STP, aux trunks et à la cohérence des VLAN. Pour chaque extension, préciser l’usage qui l’impose et la procédure de dépannage.

### 6.2 Choisir un protocole dynamique

| Critère | Routes statiques | OSPF / IS-IS | BGP |
|---|---|---|---|
| Usage typique | Petit nombre de chemins prévisibles | Routage interne à un domaine | Politique entre domaines ou grandes fabrics |
| Adaptation aux changements | Manuelle ou mécanismes supplémentaires | Calcul dynamique selon topologie et métriques | Politique et attributs de chemins, selon configuration |
| Complexité | Faible au départ, croissante avec le nombre | Modérée à élevée selon le design | Élevée si politiques et échelle importantes |
| Risque de mauvais design | Oubli de route de secours, boucle/blackhole statique | Mauvaise hiérarchie, redistribution, métriques | Filtres, fuite de routes, attributs et politiques trop larges |

Le choix dépend de la topologie, des compétences et des besoins. Un protocole plus complexe n’est pas forcément plus fiable si ses politiques ne sont ni documentées ni testées.

### 6.3 Convergence : plusieurs délais s’additionnent

Le rétablissement perçu dépend de la détection de panne, de la mise à jour de la topologie, du calcul de route, de l’installation dans la RIB/FIB, du comportement ARP/ND, des protocoles de passerelle, du pare-feu et de l’application. Une seule minuterie ne représente donc pas la convergence de bout en bout.

Mesurer une chronologie :

1. instant de la panne physique ou logique ;
2. détection par l’interface, le voisin ou la sonde ;
3. retrait du chemin invalide ;
4. choix et installation du nouveau prochain saut ;
5. résolution L2/ND et reprise d’acheminement ;
6. rétablissement des sessions applicatives, si elles peuvent survivre au changement.

### 6.4 ECMP, asymétrie et état des pare-feux

L’ECMP peut répartir les flux sur plusieurs prochains sauts équivalents. Le résultat dépend du hachage et de la topologie. En cas de routage asymétrique, le retour d’un flux peut traverser un autre pare-feu ou une autre interface que l’aller. Les pare-feux avec suivi d’état, les systèmes NAT et certaines applications peuvent mal supporter cette asymétrie si elle n’est pas prévue.

Avant d’activer plusieurs chemins, cartographier les flux qui doivent traverser une même frontière de sécurité, vérifier l’état des sessions pendant une bascule et mesurer si le partage de charge est équilibré. Le nombre de routes égales ne garantit pas une répartition parfaite des octets.


## 7. Pare-feu, zones et matrice de flux

La segmentation réseau aide à organiser les contrôles, mais une politique de sécurité doit être formulée en termes de source, destination, protocole/port, justification, propriétaire et durée de validité éventuelle.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Zones de securite : separer les niveaux de confiance</text><line x1="155" y1="190" x2="220" y2="270" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="220.0" y1="270.0" x2="209.6" y2="266.3" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="220.0" y1="270.0" x2="218.5" y2="259.1" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/><line x1="455" y1="190" x2="455" y2="270" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="455.0" y1="270.0" x2="449.3" y2="260.6" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="455.0" y1="270.0" x2="460.7" y2="260.6" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="730" y1="190" x2="660" y2="270" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="660.0" y1="270.0" x2="661.8" y2="259.2" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="660.0" y1="270.0" x2="670.5" y2="266.7" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><line x1="970" y1="190" x2="750" y2="300" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="750.0" y1="300.0" x2="755.8" y2="290.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="750.0" y1="300.0" x2="761.0" y2="300.9" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><rect x="40" y="110" width="230" height="80" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="155.0" y="145.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Utilisateurs</text><text x="155.0" y="167.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Postes geres</text><rect x="340" y="110" width="230" height="80" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="455.0" y="145.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Zone serveurs</text><text x="455.0" y="167.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Services internes</text><rect x="640" y="110" width="180" height="80" rx="12" fill="#3b1d24" stroke="#fb7185" stroke-width="2"/><text x="730.0" y="145.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">DMZ</text><text x="730.0" y="167.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Services publies</text><rect x="880" y="110" width="180" height="80" rx="12" fill="#3f2a16" stroke="#fbbf24" stroke-width="2"/><text x="970.0" y="145.12" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Internet</text><text x="970.0" y="167.12" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Zone non fiable</text><rect x="350" y="270" width="400" height="80" rx="12" fill="#321b37" stroke="#e879f9" stroke-width="2"/><text x="550.0" y="304.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Pare-feu / politique</text><text x="550.0" y="326.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">Regles explicites, journalisation, inspection</text><text x="550" y="405" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">Refuser par defaut ; ouvrir seulement les flux justifies par une application.</text><text x="550" y="444" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#cbd5e1" text-anchor="middle">Les flux de retour, DNS, administration et supervision doivent etre explicitement consideres.</text></svg>

### 7.1 Construire une matrice de flux

| Source | Destination | Service | Décision proposée | Justification |
|---|---|---|---|---|
| Postes gérés | DNS internes | DNS TCP/UDP | Autoriser | Résolution interne |
| Postes invités | Réseaux privés de l’entreprise | Tous sauf exception validée | Refuser | Isolation des invités |
| Serveurs applicatifs | Base de données | Port documenté de l’application | Autoriser selon identité/zone | Dépendance applicative |
| Admins via bastion | Équipements de gestion | SSH/HTTPS/SNMPv3 selon besoin | Autoriser, journaliser | Administration limitée |
| Internet | DMZ | Services publiés seulement | Autoriser précisément | Publication contrôlée |
| Utilisateurs | Interfaces de gestion réseau | Non nécessaire | Refuser | Réduction de la surface d’attaque |

Cette matrice est illustrative. Les ports ne doivent pas être ouverts « parce qu’ils sont habituels » : ils doivent être confirmés par le service et l’application. Prévoir aussi les flux retour, DNS, NTP, supervision, sauvegarde, AAA, mise à jour et gestion de certificats.

### 7.2 Plan de management séparé

L’administration des équipements doit utiliser des chemins et identités maîtrisés. Selon le contexte, utiliser un VLAN ou réseau de management, un bastion, l’authentification centralisée, des clés/certificats, le chiffrement, des ACL strictes et la journalisation. Le réseau de management lui-même doit être surveillé et protégé ; un VLAN de gestion sans contrôle d’accès n’est pas une garantie suffisante.

### 7.3 DMZ et services exposés

Les services publiés doivent être isolés des postes internes et des backends plus sensibles. Une architecture DMZ doit documenter les flux entrants, sortants et latéraux. Une règle autorisant la DMZ à joindre librement le LAN interne annule une partie du bénéfice de la séparation. Il faut également définir qui assure les mises à jour, la collecte des journaux, les sauvegardes et la réponse aux compromissions.


## 8. WAN, multi-sites et services cloud

Une conception WAN doit préciser la connectivité par site, les chemins primaires et de secours, les critères de bascule, les préfixes annoncés, les règles de sécurité et les dépendances à l’opérateur. Plusieurs circuits ne procurent une indépendance réelle que si les risques communs sont maîtrisés.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Architecture WAN : double acces et chemins documentes</text><line x1="225" y1="155" x2="325" y2="119" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="325.0" y1="119.0" x2="318.1" y2="127.6" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="325.0" y1="119.0" x2="314.2" y2="116.8" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="225" y1="185" x2="325" y2="307" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="325.0" y1="307.0" x2="314.6" y2="303.4" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="325.0" y1="307.0" x2="323.5" y2="296.1" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="515" y1="119" x2="615" y2="155" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="615.0" y1="155.0" x2="604.2" y2="157.2" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="615.0" y1="155.0" x2="608.1" y2="146.4" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/><line x1="515" y1="307" x2="615" y2="185" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="615.0" y1="185.0" x2="613.5" y2="195.9" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="615.0" y1="185.0" x2="604.6" y2="188.6" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="805" y1="174" x2="900" y2="174" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="900.0" y1="174.0" x2="890.6" y2="179.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="900.0" y1="174.0" x2="890.6" y2="168.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><rect x="35" y="135" width="190" height="78" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="130.0" y="168.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Site A</text><text x="130.0" y="190.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">LAN / SD-WAN edge</text><rect x="325" y="80" width="190" height="78" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="420.0" y="115.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">WAN operateur 1</text><text x="420.0" y="133.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">MPLS / Internet</text><rect x="325" y="270" width="190" height="78" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="420.0" y="305.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">WAN operateur 2</text><text x="420.0" y="323.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Internet / 4G-5G</text><rect x="615" y="135" width="190" height="78" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="710.0" y="168.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Site B</text><text x="710.0" y="190.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">LAN / SD-WAN edge</text><rect x="900" y="135" width="165" height="78" rx="12" fill="#3b1d24" stroke="#fb7185" stroke-width="2"/><text x="982.5" y="168.78" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">Datacenter</text><text x="982.5" y="190.78" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#cbd5e1" text-anchor="middle">FW / services</text><text x="420" y="43" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#bfdbfe" text-anchor="middle">Chemin nominal</text><text x="420" y="390" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#bbf7d0" text-anchor="middle">Chemin de secours : mesurer et tester le delai de bascule</text><text x="550" y="443" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#e2e8f0" text-anchor="middle">VPN chiffre ne remplace pas le filtrage, l’identite ni la supervision.</text></svg>

### 8.1 Comparer les modèles

- **VPN site-à-site sur Internet :** peut être économique et flexible ; dépend de la qualité des accès Internet, de la capacité de chiffrement et du design de routage.
- **Liaison opérateur privée/MPLS :** peut offrir un modèle de service contractuel ; ne dispense pas du chiffrement si celui-ci est requis par la politique.
- **SD-WAN :** peut centraliser la sélection de chemin, les politiques et les overlays ; il ajoute une dépendance à l’orchestration, aux contrôleurs et à la qualité des underlays.
- **Accès direct cloud :** rapproche le trafic des services cloud ; impose de contrôler DNS, identité, filtrage, journalisation et chemins entre sites.

Les noms commerciaux ne remplacent pas l’architecture. Documenter le chemin effectif d’un flux, le point d’application des politiques et le comportement en cas de panne.

### 8.2 Double accès et bascule

Un circuit de secours doit être dimensionné pour les services prioritaires lors d’une panne. Si le circuit principal transporte normalement 500 Mbit/s et que le secours ne peut fournir que 50 Mbit/s, il faut décider quels usages sont limités en mode dégradé. La bascule doit être testée depuis les applications, pas seulement en vérifiant que l’interface secondaire est up.

### 8.3 Routes et chevauchements de préfixes

Les chevauchements d’adresses deviennent particulièrement problématiques avec les acquisitions, partenaires, VPN et comptes cloud multiples. Un plan IP doit prévoir une résolution de conflit : renumérotation, NAT temporaire, proxy ou segmentation adaptée. Le NAT peut permettre une coexistence dans certains cas mais ajoute complexité, limitations de bout en bout et difficultés de dépannage ; ce n’est pas un substitut universel à un plan d’adressage cohérent.


## 9. Qualité de service et capacité

La QoS gère la contention ; elle n’ajoute pas de bande passante. Elle classe certains paquets, applique un marquage et choisit comment servir ou limiter les files en période de congestion.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">QoS de bout en bout : classer, marquer, mettre en file</text><line x1="225" y1="195" x2="285" y2="195" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="285.0" y1="195.0" x2="275.6" y2="200.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="285.0" y1="195.0" x2="275.6" y2="189.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="475" y1="195" x2="535" y2="195" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="535.0" y1="195.0" x2="525.6" y2="200.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="535.0" y1="195.0" x2="525.6" y2="189.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="755" y1="195" x2="815" y2="195" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="815.0" y1="195.0" x2="805.6" y2="200.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="815.0" y1="195.0" x2="805.6" y2="189.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="480" y1="348" x2="620" y2="348" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/><line x1="620.0" y1="348.0" x2="610.6" y2="353.7" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/><line x1="620.0" y1="348.0" x2="610.6" y2="342.3" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/><rect x="35" y="150" width="190" height="90" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="130.0" y="191.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Classification</text><text x="130.0" y="209.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Application / port / ACL</text><rect x="285" y="150" width="190" height="90" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="380.0" y="191.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Marquage</text><text x="380.0" y="209.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">DSCP / CoS selon politique</text><rect x="535" y="150" width="220" height="90" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="645.0" y="191.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">File d’attente</text><text x="645.0" y="209.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Priorite / partage / limitation</text><rect x="815" y="150" width="250" height="90" rx="12" fill="#3b1d24" stroke="#fb7185" stroke-width="2"/><text x="940.0" y="191.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Sortie congestionnee</text><text x="940.0" y="209.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Ordonnancement et drop</text><rect x="130" y="315" width="350" height="65" rx="12" fill="#132238" stroke="#a78bfa" stroke-width="2"/><text x="305.0" y="343.94" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Temps reel</text><text x="305.0" y="361.94" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Voix / controle sensible a la latence</text><rect x="620" y="315" width="350" height="65" rx="12" fill="#132238" stroke="#94a3b8" stroke-width="2"/><text x="795.0" y="343.94" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Donnees best effort</text><text x="795.0" y="361.94" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Web / transfert / sauvegarde</text><text x="550" y="427" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">Une marque DSCP n’a d’effet que si chaque saut applique une politique compatible.</text></svg>

### 9.1 Définir des classes à partir des usages

| Classe possible | Exemple d’usage | Mesures prioritaires | Précaution |
|---|---|---|---|
| Temps réel interactif | Voix, visioconférence | Latence, jitter, pertes | Une priorité stricte doit être plafonnée pour ne pas affamer les autres classes |
| Contrôle réseau | Protocoles de contrôle et gestion | Disponibilité, faible perte | Ne pas autoriser un utilisateur à s’attribuer cette classe |
| Applications métier | ERP, appels API | Temps de réponse et débit | Identifier le trafic de manière fiable |
| Transfert de données | Sauvegarde, réplication | Débit et fenêtres de transfert | Peut saturer un WAN si non limité |
| Best effort | Navigation et usage courant | Expérience globale | Classe résiduelle, mais à dimensionner |

### 9.2 Cohérence de bout en bout

Un marquage à l’entrée ne suffit pas. Chaque saut doit préserver ou réévaluer les champs selon la politique. Certains opérateurs réécrivent ou ignorent le DSCP. La politique de congestion et les buffers de la plate-forme comptent autant que les marques. Mesurer les files, drops, délais et performances applicatives.

### 9.3 Dimensionner par scénarios

Ne pas dimensionner uniquement sur le débit moyen. Examiner les pics, les sauvegardes, les mises à jour, les conférences, la croissance et la panne d’un lien. La capacité dégradée doit être une décision : quelles applications restent prioritaires, quelles opérations peuvent attendre et quelles alarmes signalent une saturation durable ?

### 9.4 Multiplier les mesures

Le débit d’interface, le volume IP, la latence, la perte et les temps applicatifs racontent des choses différentes. Utiliser la supervision SNMP/streaming telemetry, Syslog, NetFlow/IPFIX, sondes actives et compteurs QoS lorsque disponibles. Synchroniser les horloges facilite la corrélation.


## 10. Supervision et exploitation

La supervision fait partie de l’architecture, pas d’une étape secondaire après l’installation.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="500" viewBox="0 0 1100 500"><rect x="1" y="1" width="1098" height="498" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Observabilite reseau : trois sources complementaires</text><line x1="195" y1="200" x2="550" y2="275" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="539.6" y2="278.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="542.0" y2="267.4" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550" y1="200" x2="550" y2="275" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="544.3" y2="265.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="555.7" y2="265.6" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="905" y1="200" x2="550" y2="275" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="558.0" y2="267.4" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="550.0" y1="275.0" x2="560.4" y2="278.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><rect x="45" y="110" width="300" height="90" rx="12" fill="#102a43" stroke="#38bdf8" stroke-width="2"/><text x="195.0" y="151.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Telemetrie / SNMP</text><text x="195.0" y="169.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">CPU, interfaces, erreurs, files</text><rect x="400" y="110" width="300" height="90" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="550.0" y="151.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Syslog / traps</text><text x="550.0" y="169.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">Evenements, changements, alertes</text><rect x="755" y="110" width="300" height="90" rx="12" fill="#12352b" stroke="#4ade80" stroke-width="2"/><text x="905.0" y="151.44" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Sondes actives</text><text x="905.0" y="169.44" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#cbd5e1" text-anchor="middle">IP SLA, RTT, perte, jitter</text><rect x="300" y="275" width="500" height="85" rx="12" fill="#321b37" stroke="#e879f9" stroke-width="2"/><text x="550.0" y="312.62" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f8fafc" text-anchor="middle">Plateforme de supervision</text><text x="550.0" y="334.62" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#cbd5e1" text-anchor="middle">Correlation, seuils, historique, tableaux de bord</text><text x="550" y="417" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">L’alarme doit indiquer quoi, ou, depuis quand, avec quel impact et quelle preuve.</text><text x="550" y="455" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#cbd5e1" text-anchor="middle">Definir retention, droits d’acces, synchronisation horaire et test des notifications.</text></svg>

### 10.1 Les quatre plans à documenter

1. **Plan de données :** comment les paquets sont transportés ?
2. **Plan de contrôle :** comment les chemins sont-ils calculés ou appris ?
3. **Plan de management :** comment les équipements sont-ils configurés, authentifiés et surveillés ?
4. **Plan de service :** le DNS, DHCP, AAA, les applications et les services métiers sont-ils réellement utilisables ?

Une interface up/up ne prouve pas qu’un service fonctionne. Un voisin de routage établi ne prouve pas qu’un chemin complet est correct. Une sonde qui ping une adresse ne prouve pas que l’application sur cette adresse répond convenablement.

### 10.2 Construire les tableaux de bord utiles

- **Santé physique :** état, erreurs, discards, optique, PoE, changements fréquents.
- **Réseau :** voisins, routes, changements de topologie, CPU, mémoire, table de routage, buffers.
- **Service :** disponibilité DNS/DHCP/AAA, latence vers applications, pertes, temps d’authentification.
- **Sécurité :** changements de configuration, échecs d’authentification, accès administratifs, journaux du pare-feu.
- **Capacité :** tendance du débit, interfaces critiques, files QoS, capacité de secours.

Les seuils doivent être adaptés à l’usage. Un seuil unique d’utilisation à 80 % appliqué à toutes les interfaces n’est pas une politique de capacité suffisante ; un lien de sauvegarde et un lien voix n’ont pas les mêmes profils. Combiner seuil, durée, tendance et gravité métier pour limiter les alertes inutiles.

### 10.3 Journaux, temps et rétention

Synchroniser les équipements et systèmes de collecte avec une source horaire approuvée. Définir une rétention conforme aux besoins de diagnostic et aux contraintes applicables. Restreindre l’accès aux journaux, car ils peuvent contenir des adresses, identifiants, noms de services ou informations sensibles. Tester les notifications et prévoir un mode opératoire quand la plateforme de supervision est elle-même indisponible.


## 11. Sécurité d’accès et durcissement

La sécurité du réseau doit réduire la probabilité d’erreur, limiter les privilèges et conserver des éléments de preuve. Aucun paramètre isolé ne garantit un réseau sûr.

### 11.1 Mesures sur les ports d’accès

Selon le constructeur et le besoin, étudier :

- désactiver ou isoler les ports inutilisés ;
- limiter les VLAN autorisés sur les trunks et éviter les trunks automatiques inutiles ;
- employer des protections STP appropriées sur les ports terminaux ;
- maîtriser DHCP, ARP et IPv6 RA lorsque les équipements le permettent ;
- appliquer un contrôle d’accès à l’identité quand le besoin et l’infrastructure le justifient ;
- attribuer les privilèges d’administration selon le rôle et journaliser les changements.

Les fonctionnalités comme DHCP Snooping, Dynamic ARP Inspection, RA Guard et 802.1X ont des dépendances d’architecture et de compatibilité. Déployer d’abord en environnement de test, documenter les exemptions et prévoir la récupération en cas de blocage légitime.

### 11.2 Gestion des secrets et du changement

Éviter les secrets partagés en clair dans les dépôts de configurations. Restreindre les comptes locaux d’urgence, utiliser une gestion de secrets adaptée, tester le contrôle d’accès AAA et documenter le mode hors ligne si les serveurs AAA sont indisponibles. Le fichier de configuration ne doit pas être envoyé à un canal public sans assainissement.

### 11.3 Protection du plan de management

Limiter les sources administratives, préférer les protocoles chiffrés et contrôler l’accès aux interfaces web/CLI. Ne pas exposer SNMP en lecture/écriture à des sources non maîtrisées ; utiliser une version et un modèle de sécurité supportés. Sauvegarder les configurations, protéger les archives et tester la restauration plutôt que de considérer la sauvegarde comme suffisante à elle seule.


## 12. Wi-Fi et accès filaire : même architecture, contraintes différentes

Le réseau sans fil partage le plan IP et les politiques d’entreprise, mais son milieu radio ajoute de la capacité partagée, de l’interférence, de la couverture et de la mobilité. La conception doit spécifier les SSID réellement nécessaires, les VLAN/roles associés, les contrôles d’accès et la façon de diagnostiquer un problème radio par rapport à un problème IP.

### 12.1 Principes de conception Wi-Fi

- planifier la couverture à partir de l’environnement, des matériaux, de la densité et des applications ;
- éviter de créer des SSID en nombre excessif, car chacun ajoute de la signalisation et de l’exploitation ;
- séparer accès invité, accès entreprise et IoT si les besoins de confiance diffèrent ;
- documenter l’authentification, l’itinérance, la politique de segmentation et l’accès aux services ;
- surveiller le temps d’association, les échecs d’authentification, la qualité radio et les pertes en plus des seuls indicateurs IP.

### 12.2 Identifier la couche responsable

Un client qui ne se connecte pas peut être bloqué avant l’obtention d’une adresse IP. Un client qui obtient une adresse mais n’accède pas à un service présente probablement un autre type de problème. Le diagnostic doit séparer association radio, authentification, VLAN/role, DHCP, DNS, passerelle, route, pare-feu et application.


## 13. Documentation technique de l’architecture

Une architecture exploitable doit être compréhensible par la personne qui prend l’astreinte sans avoir participé au projet initial.

### 13.1 Documents minimaux

| Document | Contenu attendu |
|---|---|
| Diagramme physique | Baies, ports, liens, type de support, débits, chemins physiques |
| Diagramme logique | VLAN, préfixes, passerelles, zones, liens L2/L3, routes importantes |
| Plan IP | Site, fonction, préfixe, usage, propriétaire, DHCP/statique, réservation |
| Matrice de flux | Source, destination, service, justification, propriétaire, règle de sécurité |
| Inventaire | Modèle, système/firmware, rôle, emplacement, support, fin de vie si connue |
| Plan de résilience | Pannes couvertes, mode dégradé, dépendances communes, résultats des tests |
| Plan d’exploitation | Supervision, sauvegarde, accès admin, procédures, contacts et escalade |
| Historique des changements | Demande, risque, fenêtre, sauvegarde, étapes, contrôle, rollback |

### 13.2 Règles de lisibilité des schémas

Un diagramme doit montrer une idée claire par page. Séparer, par exemple, un schéma physique d’un diagramme des zones de sécurité et d’un plan d’adressage. Étiqueter les interfaces, les VLAN, les préfixes et la vitesse des liens critiques. Représenter les chemins de secours différemment et ajouter une légende. Les lignes croisées et les noms génériques « Switch 1 » deviennent difficiles à maintenir ; utiliser une convention de nommage stable.


## 14. Laboratoire guidé : concevoir un campus d’entreprise

### 14.1 Scénario

Une entreprise possède un siège avec deux étages, un petit local serveur et une connexion WAN. Elle prévoit 120 utilisateurs, 20 téléphones IP, 12 imprimantes, 8 points d’accès, 10 caméras et une extension dans l’année suivante. Les services essentiels sont DNS, DHCP, annuaire, applications métier, accès Internet et sauvegarde. Le réseau invité ne doit pas accéder aux ressources internes.

### 14.2 Hypothèses de travail

- Les capacités et licences des équipements sont à vérifier auprès de la documentation du matériel retenu.
- Les exemples de préfixes sont pédagogiques et doivent être contrôlés pour éviter tout chevauchement.
- Les exigences de disponibilité doivent être confirmées par le propriétaire métier.
- Le pare-feu et le réseau de management sont des zones de sécurité explicites.

### 14.3 Proposition logique initiale

| Fonction | VLAN d’exemple | Préfixe d’exemple | Politique de base |
|---|---:|---|---|
| Utilisateurs siège | 10 | `10.40.10.0/24` | Accès aux services autorisés |
| Voix | 20 | `10.40.20.0/24` | Contrôleur téléphonique et services requis |
| Imprimantes | 30 | `10.40.30.0/24` | Accès limité depuis les postes et outils admin |
| Serveurs | 40 | `10.40.40.0/24` | Filtrage par application |
| Wi-Fi entreprise | 50 | `10.40.50.0/24` | Politique selon identité |
| Wi-Fi invité | 60 | `10.40.60.0/24` | Internet seulement, isolation des clients selon besoin |
| IoT/caméras | 70 | `10.40.70.0/24` | Flux vers NVR/serveurs strictement requis |
| Management | 90 | `10.40.90.0/24` | Accès depuis le bastion ou poste admin autorisé |

Ces préfixes et VLAN ne sont pas une configuration universelle. Leur but est de montrer une allocation lisible. Adapter les plages à l’inventaire et au nombre réel de terminaux. La passerelle peut se situer sur une paire L3 ou un pare-feu selon le design.

### 14.4 Exercices de conception

1. Dessine le modèle 2 couches et le modèle 3 couches. Choisis-en un et justifie ton choix en termes de coût, de panne et d’exploitation.
2. Définis la frontière L2/L3. Si un VLAN s’étend entre deux étages, explique le besoin qui le justifie.
3. Établis une matrice de flux entre utilisateurs, serveurs, imprimantes, caméras, invités et management.
4. Propose une stratégie de passerelle redondante, en précisant ce que la redondance ne couvre pas.
5. Décris le comportement lors de la perte du lien WAN principal puis lors de la perte d’un switch d’accès.
6. Définis 10 mesures de supervision et trois alertes prioritaires.
7. Rédige une procédure de changement pour remplacer un uplink, avec vérification et rollback.

### 14.5 Checklist de validation du laboratoire

- [ ] Les préfixes ne se chevauchent pas et sont documentés.
- [ ] Chaque VLAN possède une passerelle et une politique décrites.
- [ ] Les invités ne peuvent pas atteindre les préfixes internes non autorisés.
- [ ] Les services DNS/DHCP et les dépendances AAA sont testés.
- [ ] Le comportement de la redondance est vérifié, pas seulement supposé.
- [ ] Le trafic de gestion est limité aux sources administratives prévues.
- [ ] Les chemins de secours sont documentés et mesurés.
- [ ] Les journaux et alertes remontent vers la supervision.
- [ ] Les configurations sont sauvegardées et la procédure de rollback est disponible.
- [ ] L’architecture finale correspond au réseau réellement installé.


## 15. Études de cas

### Cas A — Les utilisateurs perdent l’accès quand un trunk change

**Symptômes :** la connectivité de certains VLAN disparaît après un changement d’uplink, alors que l’interface est active.

**Hypothèses à tester :** VLAN non autorisé sur le trunk, native VLAN incohérent, agrégat mal formé, convergence STP, mauvaise affectation de port, SVI inactive, route/ACL ou erreur de configuration. Ne pas changer plusieurs paramètres à la fois.

**Démarche :** comparer avant/après les trunks, vérifier les VLAN autorisés et l’état STP, examiner l’agrégat, tester un client de chaque VLAN affecté, puis vérifier la passerelle et les routes. Capturer les états de référence avant de modifier la configuration.

### Cas B — Le lien de secours existe mais les applications restent injoignables

**Hypothèses :** route par défaut non changée, tracking uniquement physique, tunnel VPN non établi, routes retour manquantes, politique du pare-feu attachée au mauvais chemin, résolution DNS ou NAT dépendant du circuit principal.

**Démarche :** valider l’état du circuit, du tunnel, du routage aller-retour et de la politique. Tester une adresse IP puis un nom DNS puis le port applicatif. Comparer la table de routage avant/après et consulter les journaux. La bascule réseau peut avoir fonctionné tandis qu’une dépendance applicative n’a pas basculé.

### Cas C — Les sauvegardes saturent le WAN

**Hypothèses :** horaire non aligné sur les contraintes, absence de limitation, classification QoS incorrecte, sauvegardes multiples, capacité de secours insuffisante.

**Démarche :** mesurer les interfaces, les flux et les files, identifier le trafic effectif, déplacer ou limiter les opérations si métier-compatible, appliquer des politiques cohérentes et tester la latence des applications critiques. Ne pas attribuer une classe prioritaire à une application sans vérifier qu’elle est réellement identifiée.

### Cas D — L’équipe reçoit trop d’alertes

**Hypothèses :** seuils identiques pour tous les équipements, absence de durée ou d’hystérésis, notifications sur des évènements non actionnables, dépendances non corrélées.

**Démarche :** relier chaque alerte à un impact et à une action, calibrer les seuils avec les données réelles, dédupliquer les alarmes liées à une cause racine et mesurer le taux de faux positifs. Une alerte sans propriétaire ni procédure devient du bruit.


## 16. Plan de mise en production et rollback

Une mise en production doit être traitée comme un changement contrôlé. Avant le changement, sauvegarder la configuration, noter les états de référence et confirmer l’accès hors bande si le changement peut couper l’accès de gestion.

### Avant

- définir le périmètre, le responsable, la fenêtre et l’impact attendu ;
- vérifier les dépendances, la compatibilité logicielle et la capacité ;
- préparer les commandes, les résultats attendus et les commandes de retour arrière ;
- avertir les propriétaires de service et vérifier la disponibilité de l’équipe de support ;
- confirmer la sauvegarde, l’accès de secours et la procédure de restauration.

### Pendant

- appliquer un changement à la fois ;
- vérifier immédiatement interfaces, voisins, routes, VLAN, passerelles et services ;
- consigner l’heure et le résultat des contrôles ;
- arrêter la procédure si un critère de retour arrière est atteint.

### Après

- exécuter les tests fonctionnels et de résilience prévus ;
- vérifier les alertes, journaux, erreurs et compteurs ;
- mettre à jour diagrammes, plan IP, inventaire et procédures ;
- documenter l’écart entre le comportement attendu et le résultat observé.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520"><rect x="1" y="1" width="1098" height="518" rx="18" fill="#0f172a" stroke="#334155" stroke-width="2"/><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">Cycle de conception et de validation d’une architecture</text><line x1="275" y1="142" x2="315" y2="142" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="315.0" y1="142.0" x2="305.6" y2="147.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="315.0" y1="142.0" x2="305.6" y2="136.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="515" y1="142" x2="555" y2="142" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="555.0" y1="142.0" x2="545.6" y2="147.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="555.0" y1="142.0" x2="545.6" y2="136.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="755" y1="142" x2="795" y2="142" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="795.0" y1="142.0" x2="785.6" y2="147.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="795.0" y1="142.0" x2="785.6" y2="136.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="995" y1="142" x2="1030" y2="142" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="1030.0" y1="142.0" x2="1020.6" y2="147.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="1030.0" y1="142.0" x2="1020.6" y2="136.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="1030" y1="142" x2="1030" y2="297" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="1030" y1="297" x2="995" y2="297" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="995.0" y1="297.0" x2="1004.4" y2="291.3" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="995.0" y1="297.0" x2="1004.4" y2="302.7" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="795" y1="297" x2="755" y2="297" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="755.0" y1="297.0" x2="764.4" y2="291.3" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="755.0" y1="297.0" x2="764.4" y2="302.7" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="555" y1="297" x2="515" y2="297" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="515.0" y1="297.0" x2="524.4" y2="291.3" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="515.0" y1="297.0" x2="524.4" y2="302.7" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="315" y1="297" x2="275" y2="297" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="297.0" x2="284.4" y2="291.3" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="275.0" y1="297.0" x2="284.4" y2="302.7" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="75" y1="297" x2="35" y2="297" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="35" y1="297" x2="35" y2="142" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="35" y1="142" x2="75" y2="142" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="75.0" y1="142.0" x2="65.6" y2="147.7" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><line x1="75.0" y1="142.0" x2="65.6" y2="136.3" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><rect x="75" y="105" width="200" height="75" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="175.0" y="148.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">1. Besoins</text><rect x="315" y="105" width="200" height="75" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="415.0" y="148.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">2. Contraintes</text><rect x="555" y="105" width="200" height="75" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="655.0" y="148.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">3. Architecture</text><rect x="795" y="105" width="200" height="75" rx="12" fill="#132238" stroke="#38bdf8" stroke-width="2"/><text x="895.0" y="148.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">4. Plan IP/VLAN</text><rect x="795" y="260" width="200" height="75" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="895.0" y="303.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">5. Securite</text><rect x="555" y="260" width="200" height="75" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="655.0" y="303.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">6. Redondance</text><rect x="315" y="260" width="200" height="75" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="415.0" y="303.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">7. Tests</text><rect x="75" y="260" width="200" height="75" rx="12" fill="#132238" stroke="#4ade80" stroke-width="2"/><text x="175.0" y="303.28" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f8fafc" text-anchor="middle">8. Exploitation</text><text x="550" y="420" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#e2e8f0" text-anchor="middle">Chaque exigence doit etre reliee a une decision, un test et une preuve de validation.</text><text x="550" y="458" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#cbd5e1" text-anchor="middle">Reviser apres changements, incidents et evolution des usages.</text></svg>


## 17. Quiz final corrigé

### Questions

1. Pourquoi le nombre de couches ne suffit-il pas à déterminer la qualité d’une architecture ?
2. Quelle est la différence entre VLAN, sous-réseau IP et zone de sécurité ?
3. Quels sont les risques d’un domaine L2 trop étendu ?
4. Pourquoi une paire de liens ne garantit-elle pas la résilience ?
5. Quand un accès routé peut-il être préférable à un accès L2 ?
6. Quelles vérifications faut-il faire avant d’annoncer un résumé de routes ?
7. Pourquoi une interface up/up ne prouve-t-elle pas la disponibilité d’une application ?
8. Quels risques de conception l’asymétrie des routes peut-elle créer ?
9. Que doit contenir une matrice de flux ?
10. Pourquoi la QoS n’augmente-t-elle pas la capacité physique ?
11. Quels indicateurs complémentaires à l’utilisation d’une interface faut-il surveiller ?
12. Quelles étapes précèdent une bascule WAN fiable ?
13. Pourquoi faut-il protéger le réseau de management ?
14. Que représente une procédure de rollback testable ?
15. Comment transformer « le réseau doit être disponible » en exigence utile ?

### Corrigé

1. Le nombre de couches ne dit rien à lui seul sur la capacité, la segmentation, l’indépendance des pannes et la qualité opérationnelle. La bonne architecture répond aux besoins avec une complexité maîtrisée.
2. Le VLAN est L2, le sous-réseau est un préfixe L3, et la zone de sécurité est une unité de politique de confiance.
3. Une panne ou une erreur peut s’étendre plus loin ; les dépendances STP et trunks se multiplient et le dépannage devient plus complexe.
4. Les liens peuvent partager le même équipement, le même conduit, la même alimentation ou le même opérateur ; il faut tester des pannes réalistes.
5. Lorsqu’on veut des domaines L2 plus petits, des frontières de panne claires et un routage dynamique directement depuis l’accès, si l’équipe sait exploiter ce modèle.
6. Vérifier l’alignement CIDR, les préfixes réellement couverts, l’acheminement de tous les sous-réseaux et les filtres de routes.
7. L’application peut être arrêtée, DNS peut échouer, une ACL peut bloquer le port, ou la route de retour peut être absente.
8. Les pare-feux à état, le NAT ou les applications peuvent dépendre d’un trajet cohérent ; la route retour doit être prise en compte.
9. Source, destination, protocole/port, décision, justification et propriétaire ; éventuellement date d’expiration et journalisation requise.
10. Elle arbitre la congestion et les files mais ne crée aucune capacité de transmission supplémentaire.
11. Erreurs/discards, latence, perte, jitter, files QoS, CPU, mémoire, flux et disponibilité des services.
12. Valider circuit, tunnel, routes aller/retour, politique, DNS et services applicatifs ; définir les critères de bascule et les tester.
13. Parce qu’il permet de changer le réseau ; une compromission de ce plan peut affecter tous les services.
14. Une procédure précise permettant de retrouver un état connu, avec accès de secours, configurations sauvegardées, critères et tests de retour.
15. En fixant un service, une période, un seuil de disponibilité ou de récupération, des exclusions et une méthode de mesure.


## 18. Glossaire intermédiaire

- **Agrégation de liens :** regroupement logique de liens physiques pour capacité et/ou tolérance de panne.
- **Asymétrie de routage :** chemin retour différent du chemin aller.
- **Bastion :** point contrôlé utilisé pour accéder aux interfaces d’administration.
- **Capacité dégradée :** capacité restante après la perte d’une partie de l’infrastructure.
- **Domaine de panne :** ensemble d’éléments susceptibles d’être affectés par un même incident.
- **ECMP :** utilisation de plusieurs prochains sauts de coût égal.
- **FHRP :** mécanisme de redondance de passerelle de premier saut, par exemple HSRP ou VRRP.
- **FIB :** structure utilisée pour le transfert effectif des paquets.
- **Frontière L2/L3 :** endroit où une extension Ethernet se termine et où le routage prend le relais.
- **Hystérésis :** mécanisme qui évite des changements répétés autour d’un seuil.
- **Matrice de flux :** description des communications autorisées ou refusées entre zones.
- **MTU :** taille maximale de paquet/trame prise en charge sur un lien ou chemin, selon le contexte.
- **QoS :** mécanismes de classification, marquage et traitement des files lors de la congestion.
- **Rollback :** retour contrôlé à un état connu après un changement échoué.
- **Résumé de routes :** annonce d’un préfixe couvrant plusieurs routes plus spécifiques.
- **SVI :** interface virtuelle associée à un VLAN sur un commutateur L3.

## 19. Checklist de conception — à conserver

- [ ] Les besoins métier et les niveaux de service sont quantifiés.
- [ ] Le modèle à deux/trois couches ou l’accès routé est justifié.
- [ ] Les domaines L2/L3 et les frontières de sécurité sont documentés.
- [ ] Les VLAN et préfixes ont un propriétaire, une fonction et une politique.
- [ ] Le plan IPv4/IPv6 évite les chevauchements et réserve une marge réaliste.
- [ ] Les résumés de routes sont cohérents avec les préfixes réellement joignables.
- [ ] Les pannes de liens, d’équipements, de chemins et de services ont des tests précis.
- [ ] Les passerelles et protocoles de routage ont des comportements de bascule documentés.
- [ ] Les flux traversant les pare-feux sont justifiés et testés dans les deux sens.
- [ ] La QoS est cohérente sur le chemin et mesurée pendant la congestion.
- [ ] Les métriques de supervision couvrent interfaces, plans de contrôle et services.
- [ ] Les accès de management, secrets, journaux et sauvegardes sont protégés.
- [ ] Les schémas, l’inventaire et les procédures reflètent l’état réellement déployé.
- [ ] Le changement prévoit sauvegarde, accès hors bande, critères de réussite et rollback.


## Conclusion

Une architecture réseau intermédiaire est une conception où chaque décision peut être expliquée : pourquoi cette frontière L2/L3, pourquoi ce plan d’adressage, pourquoi cette redondance, où s’appliquent les règles de sécurité, comment le réseau se comporte en cas de panne et comment l’équipe saura qu’un service est dégradé. La conception n’est complète que lorsque le scénario nominal, le scénario de panne, l’exploitation et les preuves de validation sont documentés ensemble.

**Étape suivante :** `archi-reseau-expert.md`, qui peut approfondir les fabrics de campus et datacenter, les domaines de routage étendus, les services multi-sites, l’automatisation, la résilience avancée et la gouvernance d’architecture.
