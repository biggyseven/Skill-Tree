# MPLS-TP & Métro Ethernet — Débutant

> **Mise en contexte**
> Une entreprise demande à un opérateur de relier le siège et deux agences au moyen de services Ethernet. Le transport doit isoler les clients, surveiller les défauts et prévoir une protection. Il faut distinguer le service vendu au client de la manière dont les paquets circulent dans le réseau opérateur.

## Objectifs d’apprentissage
À la fin du cours, vous saurez distinguer réseau client et réseau opérateur, expliquer une étiquette MPLS et un LSP, différencier UNI/NNI/service/pseudowire et comprendre les objectifs de l’OAM et de la protection.

## Prérequis
Connaître les bases d’Ethernet, les VLAN et les notions de réseau IP. Le cours MPLS débutant est un prérequis utile.

## 1. Du service client au réseau de transport
Un opérateur transporte plusieurs services Ethernet sur une infrastructure commune. Les sites clients utilisent des interfaces de démarcation et des paramètres de service, mais ne voient pas nécessairement les nœuds internes.

    LAN site A — UNI — PE — réseau de transport — PE — UNI — LAN site B
                          LSP / service logique

- **UNI** (User-Network Interface) : démarcation entre le client et l’opérateur.
- **NNI** (Network-Network Interface) : interconnexion entre réseaux ou équipements opérateurs.
- **PE** (Provider Edge) : équipement de bord de l’opérateur.
- **P** : équipement de transport au cœur du réseau.

Le schéma est conceptuel ; le nombre de nœuds et les fonctions exactes dépendent de l’architecture.

## 2. Comprendre MPLS et les labels
MPLS utilise des étiquettes pour identifier le traitement de transfert d’un paquet dans un domaine MPLS. Le label n’est ni une adresse IP ni un identifiant universel de client : sa signification dépend du contexte et du nœud qui le traite.

Un **LSP** (Label Switched Path) est un chemin de transfert associé à des labels. Pour un service bidirectionnel, les directions peuvent être traitées par des chemins distincts selon l’architecture.

MPLS-TP adapte MPLS aux besoins des réseaux de transport. L’exploitation structurée, l’OAM, la protection et un comportement prévisible sont des objectifs de conception. Chaque déploiement n’utilise pas nécessairement le même plan de contrôle ou les mêmes mécanismes ; les capacités dépendent de la solution retenue.

## 3. Le service Ethernet n’est pas le LSP
Le service Ethernet décrit ce que le client doit obtenir : une connectivité entre sites avec des paramètres de bande passante, MTU et QoS convenus. Le transport MPLS-TP fait circuler le trafic dans le réseau opérateur. Selon la conception, un service de couche 2 peut utiliser un pseudowire ou un autre mécanisme de service.

| Élément | Question à laquelle il répond |
|---|---|
| UNI | Où le client remet-il son trafic à l’opérateur ? |
| VLAN / identifiant de service | Comment le trafic est-il classé et séparé ? |
| LSP | Quel chemin de transport à labels est utilisé ? |
| Pseudowire / fonction de service | Comment le service de couche 2 est-il représenté sur le transport ? |
| OAM | Comment détecter certains défauts ? |
| SLA | Quels niveaux de service l’opérateur s’engage-t-il à respecter ? |

Un LSP actif ne garantit pas que le service fonctionne : mauvais VLAN, MTU incohérent ou association de service incorrecte peuvent bloquer le trafic.

## 4. Isolation et paramètres de service
Un réseau partagé doit éviter le mélange des clients. L’isolation peut reposer sur des identifiants de service, des encapsulations et des règles adaptées. Il faut vérifier classification à l’entrée, transport et remise à la sortie.

Une fiche de service devrait décrire :
- identifiant du service et ports UNI concernés ;
- VLAN client et traitement des tags ;
- MTU supporté sur tout le chemin ;
- débit contractuel et classes QoS ;
- surveillance et seuils d’alarme ;
- responsabilités du client et de l’opérateur.

QinQ et les options de remise des trames dépendent de l’offre et des équipements. Confirmer le modèle, la version et le profil de service avant d’appliquer une configuration.

## 5. OAM : observer la continuité
OAM signifie Operations, Administration and Maintenance. Ces mécanismes peuvent surveiller la continuité ou localiser certains défauts. Les fonctions exactes dépendent de la technologie et du niveau surveillé.

Distinguer une interface physique opérationnelle, un chemin de transport déclaré actif et un service de bout en bout conforme. Ces constats ne sont pas équivalents. L’OAM ne remplace pas nécessairement le test fonctionnel du service complet.

## 6. Protection et disponibilité
Un chemin de protection aide à rétablir le trafic après certains défauts. Son délai et son comportement dépendent du mécanisme, de l’architecture et des défaillances. Une protection indiquée dans la configuration n’est pas une preuve : il faut définir un essai autorisé, observer les alarmes et pertes, contrôler le retour au service et conserver les résultats.

Lorsque la diversité physique est exigée, vérifier les points de défaillance communs ; deux chemins logiques peuvent utiliser la même infrastructure physique.

## 7. TP guidé : fiche d’un service Métro Ethernet
**Situation :** le siège A doit communiquer avec l’agence B au moyen d’un service Ethernet sur un réseau MPLS-TP partagé.

1. Dessiner les LAN, les UNI et les PE ; distinguer la partie client et la partie opérateur.
2. Consigner l’identifiant fictif, le VLAN, le MTU et le débit fournis par le scénario.
3. Représenter le LSP et préciser ce qui n’est pas visible du client.
4. Définir un test fonctionnel de bout en bout et les indicateurs OAM disponibles.
5. Établir les vérifications à réaliser si le LSP est actif mais que le service échoue.
6. Préciser les autorisations nécessaires avant de tester la protection.

**Livrables :** schéma, fiche de service, matrice de responsabilités et procédure de diagnostic.

## Exercices corrigés
**1.** À quoi sert un label MPLS ?  
**Correction :** il guide le traitement et le transfert du paquet selon le contexte MPLS. Il ne remplace pas l’adresse IP et n’identifie pas universellement un client.

**2.** Un LSP est actif mais les sites ne communiquent pas. Que vérifier ?  
**Correction :** classification VLAN/service aux UNI, association au transport, MTU, paramètres aux extrémités et fonctionnement de bout en bout.

**3.** Quelle différence existe entre UNI et NNI ?  
**Correction :** la UNI marque l’interface client-opérateur ; la NNI sert à l’interconnexion entre réseaux ou équipements opérateurs selon l’architecture.

## Défi final corrigé
**Scénario :** une agence perd la connectivité ; la UNI est active et la supervision indique que le transport est disponible.

**Correction attendue :** confirmer l’étendue de l’incident, vérifier VLAN et identifiant de service, MTU et associations aux deux extrémités, examiner les résultats OAM disponibles puis réaliser un test fonctionnel autorisé. Comparer avec un service témoin si possible. Ne modifier qu’un paramètre à la fois, documenter les résultats et escalader au niveau transport si les preuves localisent le défaut dans le LSP ou les équipements opérateur.

## À retenir
MPLS-TP transporte des services ; il ne se confond pas avec eux. La UNI marque la frontière client-opérateur, le LSP porte le transport et l’OAM aide à surveiller certains niveaux. La protection doit être testée selon des critères définis.
