# VPN — Niveau Expert

> **Parcours :** Réseaux et cybersécurité  
> **Niveau :** Expert  
> **Public :** Administrateurs réseau, ingénieurs infrastructure, architectes sécurité et techniciens préparant une mise en production  
> **Prérequis :** Adressage IPv4/IPv6, sous-réseaux, routage, NAT, filtrage stateful, DNS, notions de cryptographie, dépannage TCP/IP  
> **Fil conducteur :** concevoir, déployer, sécuriser, observer et dépanner un VPN comme un système réseau complet.


## 1. Ce que l’on doit savoir faire à la fin

À la fin de ce cours, vous devez pouvoir :

- choisir une architecture VPN adaptée à un besoin métier et justifier ce choix ;
- expliquer le trajet d’un paquet à travers le réseau de transport, le tunnel et le réseau de destination ;
- distinguer le plan de contrôle, le plan de données, l’authentification, le chiffrement et les décisions de routage ;
- concevoir un VPN site-à-site et un accès distant avec des règles de moindre privilège ;
- comparer IPsec/IKEv2, WireGuard et OpenVPN sans les traiter comme des solutions interchangeables en toute circonstance ;
- anticiper les problèmes de sous-réseaux qui se chevauchent, de DNS, d’IPv6, de MTU, de NAT et de routage asymétrique ;
- mettre en place une stratégie de supervision, de rotation des clés, de révocation et de reprise après incident ;
- diagnostiquer une panne par couches au lieu de modifier plusieurs paramètres au hasard ;
- documenter une solution VPN et démontrer son fonctionnement par des tests reproductibles.

**Principe d’ingénierie :** un tunnel qui affiche « connecté » n’est pas nécessairement un VPN fonctionnel, sécurisé ou conforme au besoin. Le tunnel peut être établi alors que les routes, les politiques de filtrage, le DNS ou les droits d’accès sont incorrects.

## 2. Mode d’emploi du cours

Le cours alterne quatre approches complémentaires :

1. **Modèles mentaux et schémas textuels** : pour comprendre les flux sans dépendre d’un dessin complexe ou d’une animation.
2. **Conception** : pour traduire une exigence métier en sous-réseaux, routes, identités, règles de sécurité et objectifs de disponibilité.
3. **Laboratoires** : pour manipuler des configurations et observer le comportement réel des paquets.
4. **Diagnostic** : pour passer d’un symptôme à une hypothèse testable, puis à une correction vérifiée.

Les adresses `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` utilisées dans les exemples sont des plages réservées à la documentation. Remplacez-les par les adresses adaptées à votre laboratoire avant tout déploiement réel.


# PARTIE I — RECONSTRUIRE LES FONDATIONS AVANT L’EXPERTISE

## 3. Parcours pratique de remise à niveau : du débutant à l’expert

Ce parcours est volontairement inclus dans le cours avancé : les pannes VPN les plus difficiles proviennent souvent d’un détail élémentaire mal vérifié. Il peut aussi servir de feuille de route à une personne qui découvre le sujet.

### Étape A — Comprendre la connectivité sans VPN

**Objectif :** savoir expliquer pourquoi deux machines peuvent ou ne peuvent pas communiquer.

1. Relever l’adresse IP, le préfixe, la passerelle et le DNS de chaque poste.
2. Vérifier qu’une adresse est dans le bon sous-réseau.
3. Identifier la route qui sera utilisée pour joindre une destination.
4. Vérifier le filtrage sur l’hôte et sur la passerelle.
5. Distinguer un problème de résolution DNS d’un problème de connectivité IP.

Schéma de départ :

```text
[PC-A : 10.10.10.10/24]
          |
          | réseau local 10.10.10.0/24
          v
[Passerelle A : 10.10.10.1]
          |
          v
       [Internet]
          |
          v
[Passerelle B : 10.20.20.1]
          |
          | réseau local 10.20.20.0/24
          v
[Serveur B : 10.20.20.20/24]
```

**Question de contrôle :** sans VPN ni route spécifique, comment la passerelle A sait-elle où envoyer un paquet à destination de `10.20.20.20` ? Réponse attendue : elle applique sa table de routage ; si aucune route plus spécifique n’existe, le paquet suit généralement la route par défaut, mais la passerelle distante ne saura pas nécessairement retourner vers le réseau source.

### Étape B — Comprendre l’encapsulation

Un VPN réseau prend habituellement un paquet intérieur, le protège, puis le transporte dans un paquet extérieur acheminé sur le réseau existant.

```text
PAQUET INTÉRIEUR (avant encapsulation)
+--------------------------------------------------+
| IP source : 10.10.10.10                          |
| IP destination : 10.20.20.20                     |
| Données applicatives                             |
+--------------------------------------------------+
                          |
                          | encapsulation + protection
                          v
PAQUET EXTÉRIEUR (transport sur Internet)
+--------------------------------------------------+
| IP source publique : 198.51.100.10                |
| IP destination publique : 203.0.113.20            |
| UDP / protocole de transport du VPN               |
| En-tête VPN + paquet intérieur chiffré            |
+--------------------------------------------------+
```

L’équipement de transit voit les adresses extérieures nécessaires à l’acheminement. Il ne doit pas pouvoir lire le contenu intérieur protégé, mais il peut encore observer des métadonnées comme les adresses de transport, les tailles et les rythmes de paquets.

### Étape C — Monter un tunnel dans un laboratoire isolé

1. Créer deux hôtes Linux ou deux machines virtuelles.
2. Attribuer aux hôtes des adresses de réseau différentes.
3. Générer les clés ou certificats nécessaires.
4. Établir un tunnel entre les deux extrémités.
5. Vérifier le handshake ou l’état de la négociation.
6. Vérifier les routes et les règles de pare-feu.
7. Tester un flux applicatif réel, pas seulement un ping.
8. Couper puis rétablir le tunnel afin d’observer la reprise.

### Étape D — Passer d’un tunnel fonctionnel à une architecture maîtrisée

Ajouter ensuite, une fonction à la fois :

- une route vers un sous-réseau distant ;
- une politique qui limite les réseaux accessibles ;
- une résolution DNS prévue pour les noms internes ;
- un test IPv6 ;
- une mesure de latence et de débit ;
- une rotation contrôlée de clé ou de certificat ;
- une surveillance d’indisponibilité et une procédure de retour arrière.

### Étape E — Démontrer la maîtrise

Vous devez pouvoir expliquer, sans vous appuyer uniquement sur l’interface graphique :

- quelle route prend le paquet ;
- quelle identité est authentifiée ;
- quelle politique autorise le paquet ;
- quelle adresse est visible sur le réseau de transport ;
- quels journaux ou compteurs prouvent le passage du trafic ;
- comment révoquer l’accès d’un client sans couper tous les autres.


## 4. Vocabulaire d’architecture

| Terme | Sens opérationnel |
|---|---|
| **Underlay** | Réseau IP existant qui transporte les paquets extérieurs du VPN : Internet, WAN ou réseau opérateur. |
| **Overlay** | Réseau logique construit au-dessus de l’underlay, avec ses adresses, routes et politiques. |
| **Pair / peer** | Extrémité cryptographique d’un tunnel ou d’une relation VPN. Le sens précis dépend du protocole. |
| **Plan de contrôle** | Négociation, authentification, gestion des clés, établissement et renouvellement des associations de sécurité. |
| **Plan de données** | Transport des paquets utilisateur protégés à travers le tunnel. |
| **Route** | Décision indiquant par quelle interface ou prochaine étape envoyer le paquet. Une route n’accorde pas à elle seule un droit d’accès. |
| **Politique de sécurité** | Règles déterminant quelles identités et quels flux sont autorisés, rejetés ou protégés. |
| **SA (Security Association)** | État de sécurité utilisé notamment par IPsec ; les SA de données sont directionnelles. |
| **PFS** | *Perfect Forward Secrecy* : une compromission ultérieure d’une clé à long terme ne doit pas permettre de déduire les clés de session anciennes, sous les hypothèses du protocole et de la configuration. |
| **Split tunneling** | Une partie du trafic passe par le VPN ; une autre passe directement par le réseau local ou Internet. |
| **Full tunneling** | Le VPN est utilisé pour l’ensemble du trafic routable prévu par la politique, généralement avec une route par défaut et un traitement cohérent d’IPv6 et du DNS. |
| **NAT-T** | Encapsulation d’IPsec dans UDP afin de traverser certains mécanismes NAT, souvent sur UDP 4500. |

## 5. Choisir le type de VPN à partir du besoin

Ne choisissez pas un protocole avant de savoir qui communique, depuis où, vers quoi et avec quelles contraintes.

### Principaux scénarios

**VPN site-à-site** — relie des réseaux derrière deux passerelles : siège, agence, datacenter, cloud ou environnement de secours.

```text
LAN du siège                                      LAN de l'agence
10.10.10.0/24                                     10.20.20.0/24
      |                                                 |
[Passerelle A] == tunnel chiffré sur l'underlay == [Passerelle B]
      |                                                 |
 utilisateurs/serveurs                         utilisateurs/serveurs
```

**VPN d’accès distant** — relie un appareil utilisateur à une passerelle, avec une identité et des droits propres à cet utilisateur ou à cet appareil.

```text
[Portable géré] -- réseau non fiable -- [Concentrateur VPN]
                                              |
                              +---------------+---------------+
                              |               |               |
                         [DNS interne]   [Applications]   [Bastion]
```

**VPN hôte-à-hôte** — protège la communication entre deux serveurs ou deux systèmes précis. Le modèle peut être très ciblé, mais exige une bonne gestion des identités, des routes et des mises à jour.

**Architecture en étoile (hub-and-spoke)** — les sites communiquent au travers d’un ou plusieurs hubs. Elle simplifie souvent le contrôle central, mais peut créer une dépendance et un goulot d’étranglement.

**Maillage (mesh)** — des sites ou hôtes établissent des tunnels entre eux. Le nombre de relations possibles augmente rapidement avec le nombre de pairs ; la distribution des clés, la supervision et les changements de topologie deviennent plus complexes.

### Full tunnel ou split tunnel ?

| Critère | Full tunnel | Split tunnel |
|---|---|---|
| Contrôle du trafic Internet | Plus centralisé si la passerelle inspecte effectivement ce trafic | Le trafic direct dépend aussi du réseau local et de sa sécurité |
| Charge de la passerelle | Peut être élevée : Internet, applications et accès privés traversent le VPN | Habituellement plus faible |
| Accès aux ressources internes | Centralisé par la politique VPN | Dépend des routes et exceptions définies |
| Risques de contournement | Moins de chemins directs si IPv4, IPv6, DNS et règles sont cohérents | Davantage de chemins à documenter et à contrôler |
| Cas d’emploi courant | Environnement réglementé, poste administré, inspection centrale nécessaire | Besoin de conserver un accès local ou de limiter le trafic distant |

Le split tunneling n’est pas automatiquement mauvais et le full tunneling n’est pas automatiquement sûr. Le choix doit résulter d’une analyse des risques, de la posture des terminaux, de la bande passante, des applications et des exigences de supervision.


# PARTIE II — CE QUI SE PASSE DANS LE TUNNEL

## 6. Encapsulation, chiffrement et authentification : ne pas confondre

Un VPN d’entreprise doit généralement réunir plusieurs propriétés distinctes :

- **Confidentialité :** empêcher un observateur non autorisé de lire le contenu protégé.
- **Intégrité et authentification des données :** détecter une altération et vérifier que le paquet provient d’une source possédant les secrets ou clés attendus.
- **Authentification du pair :** établir que l’extrémité distante correspond à l’identité prévue.
- **Protection contre le rejeu :** rejeter, dans les limites prévues par le protocole, des paquets protégés déjà observés.
- **Contrôle d’accès :** limiter les réseaux, hôtes, services et actions accessibles après établissement du tunnel.
- **Disponibilité :** conserver le service malgré une panne, une perte de connectivité ou un renouvellement de clés.

Le chiffrement ne remplace pas le contrôle d’accès. Un utilisateur correctement authentifié ne doit pas obtenir automatiquement l’accès à toutes les machines du réseau.

### Séquence logique d’un flux

```text
1. L'application produit un paquet intérieur
                    |
                    v
2. La table de routage choisit l'interface VPN
                    |
                    v
3. La politique du VPN vérifie le pair / le sélecteur / la destination
                    |
                    v
4. Le protocole protège le paquet (chiffrement + intégrité, selon le protocole)
                    |
                    v
5. L'encapsulation crée un paquet extérieur
                    |
                    v
6. L'underlay achemine le paquet extérieur vers le pair
                    |
                    v
7. Le pair vérifie, déchiffre et désencapsule
                    |
                    v
8. Le routage et le pare-feu locaux traitent le paquet intérieur
                    |
                    v
9. Le serveur ou le poste destinataire reçoit le flux
```

Chaque étape est une zone de panne possible. Un handshake réussi valide certaines étapes de négociation et d’authentification, mais ne démontre pas l’existence d’une route retour ni l’autorisation d’un service applicatif.

## 7. Deux niveaux d’adressage à suivre

Dans un VPN routé, il peut exister des adresses intérieures et extérieures différentes.

```text
Paquet intérieur :
  source      = 10.10.10.15
  destination = 10.20.20.45

Paquet de transport :
  source      = 198.51.100.10
  destination = 203.0.113.20
  protocole   = dépend du VPN et de la configuration
```

Ne concluez pas que le trafic intérieur est impossible parce que ses adresses RFC1918 ne sont pas routables sur Internet. C’est justement l’underlay qui achemine le paquet extérieur. À l’inverse, si le tunnel doit rejoindre un réseau privé, il faut toujours que la route retour et les règles de filtrage existent du côté distant.

## 8. MTU, surcharge et fragmentation

L’ajout d’en-têtes de transport, de VPN, d’authentification et parfois de padding réduit la taille maximale du paquet intérieur qui passe sans fragmentation ou perte. La surcharge exacte dépend du protocole, du mode, des algorithmes, d’IPv4 ou d’IPv6, du chemin et des encapsulations supplémentaires.

### Pourquoi le symptôme peut être trompeur

```text
Petits paquets (DNS, ping court)  ---> passent
Gros paquets (HTTPS, transfert)   ---> ralentissent ou échouent
Handshake VPN                      ---> reste établi
```

Ce motif peut indiquer un problème de MTU, de PMTUD, de filtrage ICMP nécessaire à la découverte de MTU, ou de MSS TCP. Il ne prouve pas à lui seul que la MTU est en cause : il faut mesurer et confirmer.

**Méthode pratique :**

1. confirmer la connectivité avec de petits paquets ;
2. augmenter progressivement la taille des paquets de test en empêchant la fragmentation lorsque l’outil le permet ;
3. vérifier les compteurs de fragmentation, de rejet et d’erreur sur les interfaces ;
4. vérifier si les messages ICMP utiles à PMTUD traversent les pare-feu ;
5. mesurer une MTU compatible avec le chemin ;
6. tester une correction ciblée, par exemple MTU de l’interface tunnel ou MSS clamping lorsque c’est justifié ;
7. vérifier à nouveau les flux TCP, UDP, IPv4 et IPv6 concernés.

Une valeur de MTU de `1420` est couramment utilisée comme point de départ dans certains déploiements WireGuard sur Ethernet, mais **ce n’est pas une valeur universelle**. Elle doit être validée sur le chemin réel. Évitez les modifications globales du MSS ou de la MTU sans mesure, car elles peuvent cacher le problème ou dégrader d’autres flux.


# PARTIE III — IPsec ET IKEv2

## 9. Architecture IPsec

IPsec est une architecture de sécurité au niveau IP. Il ne désigne pas un seul algorithme ni une unique configuration : il regroupe des protocoles, des associations de sécurité et des politiques qui doivent être négociées de manière compatible.

### ESP et AH

- **ESP (Encapsulating Security Payload)** est le mécanisme le plus couramment utilisé pour protéger le trafic IPsec. Selon le profil choisi, il fournit chiffrement, intégrité et authentification des données, avec protection contre le rejeu.
- **AH (Authentication Header)** fournit l’authentification et l’intégrité de certains champs IP, mais ne chiffre pas le contenu. Sa compatibilité avec les transformations d’adresse par NAT est limitée ; ESP avec NAT-T est donc plus fréquent dans les déploiements modernes.

Ne retenez pas « IPsec = chiffrement » comme définition complète. Il faut connaître le mode, les sélecteurs, les algorithmes négociés, les clés et les politiques réellement appliquées.

### Mode transport et mode tunnel

```text
MODE TRANSPORT
+------------------+---------------------------+
| En-tête IP hôte  | ESP | données protégées    |
+------------------+---------------------------+
      L'en-tête IP d'origine est conservé en grande partie.
      Usage fréquent : protection entre deux hôtes.

MODE TUNNEL
+--------------------+--------------------------+
| Nouvel en-tête IP  | ESP | paquet IP intérieur  |
+--------------------+--------------------------+
      Le paquet IP intérieur est encapsulé.
      Usage fréquent : passerelle-à-passerelle ou accès distant.
```

La représentation est conceptuelle : les champs exacts et leur ordre varient selon le protocole, le mode et les transformations choisies.

## 10. Rôle d’IKEv2

IKEv2 négocie l’authentification des pairs, établit des secrets partagés dérivés de l’échange de clés, choisit les algorithmes compatibles et crée ou renouvelle les associations de sécurité utilisées par IPsec. L’échange initial établit l’association IKE ; des échanges ultérieurs établissent les associations de sécurité pour les données et peuvent les renouveler.

### Cycle simplifié

```text
Pair A                                          Pair B
  |                                                |
  |---- propositions, échange de clés, nonce ----->|
  |<--- choix, échange de clés, nonce -------------|
  |                                                |
  |<---- authentification / création de l'IKE SA -->|
  |                                                |
  |<---- création des Child SAs pour les données -->|
  |                                                |
  |========== trafic IPsec protégé ================|
  |                                                |
  |<------ renouvellement / suppression des SA ---->|
```

Les messages affichés sont regroupés pour illustrer le déroulement logique ; ce schéma n’est pas une trace paquet par paquet de la machine d’état IKEv2.

### Éléments à maîtriser

- **IKE SA :** protège les échanges de contrôle IKE entre les pairs.
- **Child SA :** association utilisée pour protéger le trafic, le plus souvent par ESP.
- **Propositions cryptographiques :** combinaisons d’algorithmes acceptées par les deux extrémités.
- **Authentification :** certificats, clé prépartagée ou mécanisme pris en charge par l’implémentation et le profil retenu.
- **Sélecteurs de trafic :** réseaux, adresses ou autres critères indiquant quels flux sont couverts par les SA.
- **Durées de vie et rekeying :** renouvellement des clés et des associations pour limiter l’exposition et maintenir le service.
- **Détection de pair inactif :** mécanismes permettant de détecter un état devenu inutilisable et de déclencher une reprise.
- **NAT-T :** encapsulation UDP d’ESP lorsque la traversée de NAT l’exige.

## 11. Concevoir les propositions IPsec

Une configuration robuste doit définir explicitement des profils compatibles et maintenables. Les choix précis dépendent des équipements, des exigences réglementaires, des performances attendues et des recommandations cryptographiques applicables à l’organisation.

À vérifier dans la documentation de la plateforme et dans la politique de sécurité :

- versions de protocole acceptées ;
- algorithmes de chiffrement et d’intégrité approuvés ;
- groupe(s) d’échange de clés jugés appropriés ;
- utilisation de PFS lors de la création ou du renouvellement des SA de données, selon le profil ;
- mode d’authentification et règles de validation des certificats ;
- durées de vie, renouvellement et temporisations ;
- traitement des sélecteurs et des réseaux distants ;
- comportement lorsque le pair devient injoignable ;
- journalisation et alertes sur les échecs de négociation.

Évitez de reprendre aveuglément un exemple ancien trouvé sur un forum. Un équipement peut continuer à accepter des algorithmes obsolètes pour des raisons de compatibilité, sans que cela signifie qu’ils soient adaptés à une nouvelle architecture. Pour IPsec/IKE, utilisez les recommandations actuelles du constructeur et des référentiels de sécurité reconnus ; NIST SP 800-77 Rev. 1 est une référence utile pour la conception et l’exploitation d’IPsec.

## 12. IPsec : panne de négociation ou panne de données ?

| Symptôme | Hypothèses à tester | Vérifications utiles |
|---|---|---|
| Aucun échange IKE visible | Mauvaise IP de pair, mauvais chemin, UDP bloqué, mauvais port, NAT ou équipement intermédiaire | Capturer sur l’interface extérieure, vérifier le pare-feu et l’adresse cible |
| Échange IKE démarre puis échoue | Propositions incompatibles, identité incorrecte, certificat ou clé prépartagée invalide, horloge/certificat | Journaux IKE détaillés, dates de validité, identité attendue et algorithmes autorisés |
| IKE SA établie, aucune Child SA utile | Sélecteurs incompatibles, absence de sous-réseaux correspondants, politique incohérente | Comparer les sélecteurs locaux/distants et l’état des SA de données |
| SA présente, aucun trafic | Route absente, filtrage, route retour manquante, mauvaise politique, NAT inattendu | Table de routage, règles de pare-feu, compteurs ESP et capture côté LAN |
| Trafic dans un seul sens | Routage asymétrique, politique différente, filtrage retour, SA unidirectionnelle incomplète | Capturer aux deux extrémités, inspecter les routes et les compteurs dans chaque direction |
| Coupures après une période | Rekeying, perte de connectivité, durée de vie incohérente, état NAT, DPD | Journaux autour de l’heure exacte, état IKE/Child SA avant et après la coupure |


# PARTIE IV — WIREGUARD ET OPENVPN

## 13. WireGuard : simplicité du plan cryptographique, rigueur de l’exploitation

WireGuard est un VPN moderne transporté sur UDP, fondé sur des paires de clés publiques/privées et une liste de pairs autorisés. Son protocole utilise notamment une construction issue de Noise, Curve25519 pour l’échange de clés, ChaCha20-Poly1305 pour la protection des données et BLAKE2s pour les fonctions de hachage. Vérifiez toujours les choix et capacités de la version réellement déployée dans la documentation officielle.

### Principes opérationnels

- Chaque pair possède une clé privée qu’il doit protéger et une clé publique distribuée aux pairs qui doivent le reconnaître.
- Les clés publiques des pairs jouent un rôle central dans l’authentification cryptographique.
- `AllowedIPs` sert à la fois à associer des préfixes à un pair et, sur réception, à vérifier les adresses source autorisées pour ce pair. Ce n’est donc pas seulement une déclaration descriptive de réseau.
- L’interface crée un réseau logique ; les routes effectives dépendent aussi de l’outil de configuration et du système.
- Le protocole s’occupe du renouvellement des clés de session ; l’administrateur doit, lui, gérer l’inventaire des pairs, la distribution, la révocation et la rotation des clés à long terme.
- WireGuard ne fournit pas à lui seul un système complet de gestion du cycle de vie des utilisateurs, de contrôle de posture ou de distribution d’identité d’entreprise. Ces fonctions doivent être intégrées dans l’architecture qui l’entoure si elles sont nécessaires.

### Schéma de relation entre pairs

```text
             [Contrôle d'accès / inventaire des clés]
                           |
                  distribue les clés publiques
                  et gère les révocations
                    /                 \
                   v                   v
        [Pair A : clé A]           [Pair B : clé B]
               |                         |
               +===== WireGuard / UDP ===+
               |                         |
        préfixes autorisés         préfixes autorisés
        10.10.10.0/24              10.20.20.0/24
```

Le plan de gestion représenté ici n’est pas nécessairement un composant intégré au protocole. Il peut s’agir d’une procédure, d’un gestionnaire de configuration ou d’une plateforme externe.

## 14. Laboratoire WireGuard : relier deux LAN

### 14.1 Topologie cible

```text
LAN A : 10.10.10.0/24                         LAN B : 10.20.20.0/24
PC-A : 10.10.10.10                            PC-B : 10.20.20.20
          |                                             |
    [GW-A / wg0] ===== tunnel WireGuard ===== [GW-B / wg0]
    LAN : .1                                      LAN : .1
    WG  : 10.255.0.1/30                           WG  : 10.255.0.2/30
    WAN : 198.51.100.10                            WAN : 203.0.113.20
```

Les adresses WAN sont des exemples documentaires. Dans un laboratoire réel, les deux passerelles doivent pouvoir s’atteindre par l’underlay. Si l’une des extrémités est derrière un NAT, il faut adapter l’endpoint, les règles de transfert et, lorsque nécessaire, le keepalive.

### 14.2 Générer les clés

Sur chaque passerelle, avec WireGuard installé :

```bash
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

- Gardez `privatekey` local à l’équipement et protégez-le avec des permissions restrictives.
- Échangez la **clé publique**, jamais la clé privée.
- Évitez d’inclure des clés privées dans un dépôt Git, une capture d’écran, une commande copiée dans un ticket ou un journal.
- Les noms de fichiers et commandes exacts peuvent dépendre de la distribution et de l’outil d’administration utilisé.

### 14.3 Configuration indicative de GW-A

Créez `/etc/wireguard/wg0.conf` sur GW-A, puis remplacez les champs entre chevrons par les valeurs réelles du laboratoire.

```ini
[Interface]
Address = 10.255.0.1/30
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_DE_GW_A>

[Peer]
PublicKey = <CLE_PUBLIQUE_DE_GW_B>
Endpoint = 203.0.113.20:51820
AllowedIPs = 10.255.0.2/32, 10.20.20.0/24
```

### 14.4 Configuration indicative de GW-B

```ini
[Interface]
Address = 10.255.0.2/30
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_DE_GW_B>

[Peer]
PublicKey = <CLE_PUBLIQUE_DE_GW_A>
Endpoint = 198.51.100.10:51820
AllowedIPs = 10.255.0.1/32, 10.10.10.0/24
```

**Lecture des `AllowedIPs` :** GW-A envoie au pair B les paquets destinés au réseau B et accepte de ce pair les sources correspondant aux préfixes déclarés. La configuration de GW-B fait l’inverse. Ajouter `0.0.0.0/0` ou `::/0` change fortement le périmètre du routage et ne doit pas être fait pour un simple site-à-site sans besoin explicite.

### 14.5 Activer le routage et le filtrage

Sur les deux passerelles, vérifiez les points suivants avant les tests :

1. Le noyau autorise le transfert IPv4, par exemple via `net.ipv4.ip_forward=1` lorsque ce réglage est applicable.
2. Les règles de pare-feu autorisent le trafic de transfert entre `wg0` et les interfaces LAN, uniquement pour les flux nécessaires.
3. Le pare-feu de l’underlay autorise le trafic UDP WireGuard sur le port configuré vers la passerelle concernée.
4. Les postes des LAN savent retourner vers le réseau distant, soit parce que la passerelle VPN est leur routeur par défaut, soit grâce à une route spécifique.
5. Aucune règle NAT superflue ne masque les adresses sources entre les deux LAN. Pour une interconnexion routée normale, privilégiez des routes explicites plutôt qu’un NAT utilisé uniquement pour contourner un oubli de routage.
6. Les sous-réseaux locaux et distants ne se chevauchent pas.

Commandes Linux à adapter à l’environnement :

```bash
# Charger l'interface (selon le paquet et la distribution)
sudo wg-quick up wg0

# Examiner les paramètres et le dernier handshake
sudo wg show

# Examiner les routes
ip route
ip route get 10.20.20.20

# Examiner les adresses et l'état de l'interface
ip address show wg0
```

La syntaxe et les outils d’activation peuvent varier. Ne réactivez pas aveuglément une interface déjà gérée par NetworkManager, systemd-networkd ou une plateforme d’orchestration.

### 14.6 Vérifier dans le bon ordre

```text
[1] GW-A joint-il l'endpoint public de GW-B ?
       |
       v
[2] Des paquets UDP WireGuard atteignent-ils GW-B ?
       |
       v
[3] Le handshake apparaît-il dans wg show ?
       |
       v
[4] La route vers 10.20.20.0/24 passe-t-elle par wg0 ?
       |
       v
[5] Les compteurs de transfert progressent-ils dans les deux sens ?
       |
       v
[6] GW-B a-t-il une route retour vers 10.10.10.0/24 ?
       |
       v
[7] Le pare-feu autorise-t-il le flux de bout en bout ?
       |
       v
[8] Une application réelle fonctionne-t-elle ?
```

Ne considérez pas le test terminé tant qu’un flux initié depuis chaque LAN a été vérifié selon la politique attendue. Un ping peut être bloqué sans que le tunnel soit en panne ; inversement, un ping réussi ne démontre pas que les applications et règles exigées fonctionnent.

### 14.7 Cas de client derrière NAT

Un pair situé derrière un NAT peut perdre l’état de traduction lorsqu’il reste inactif. `PersistentKeepalive` permet, lorsque c’est nécessaire, d’envoyer périodiquement un paquet pour maintenir le mapping NAT actif. Une valeur de `25` secondes est souvent utilisée comme point de départ pour un pair derrière NAT, mais elle doit être justifiée par le comportement réel du réseau et les contraintes de consommation ou de politique. Elle n’est pas nécessaire sur tous les pairs.

## 15. OpenVPN : flexibilité, PKI et transport

OpenVPN utilise TLS pour la négociation et l’authentification selon le profil configuré, puis transporte le trafic VPN dans un canal de données protégé. Il peut utiliser TCP ou UDP et des interfaces virtuelles de type TUN ou TAP selon le besoin et le mode.

- **TUN** sert typiquement au transport de paquets IP routés.
- **TAP** fonctionne au niveau Ethernet et peut transporter des trames de couche 2 ; il n’est pas requis pour la majorité des architectures routées modernes.
- **UDP** est souvent privilégié pour le transport VPN général, car le transport retransmettant les pertes est généralement géré par les applications qui en ont besoin.
- **TCP** peut être utile dans des environnements particuliers, mais encapsuler des flux TCP à l’intérieur d’une session TCP peut provoquer des effets de performance liés aux retransmissions et au contrôle de congestion imbriqués (*TCP-over-TCP*).
- Les certificats doivent être correctement validés : identité attendue, chaîne de confiance, période de validité, révocation et protection des clés privées.
- Il faut éviter les compatibilités anciennes ou les paramètres qui réintroduisent des mécanismes obsolètes ; les valeurs recommandées évoluent avec les versions.

### Exemple de chemin OpenVPN routé

```text
[Client OpenVPN]
      |
      | tunnel IP virtuel (TUN)
      v
[Canal de données OpenVPN protégé]
      |
      v
[Serveur OpenVPN]
      |
      +---- route + filtrage ----> [Réseau applicatif interne]
```

Une configuration OpenVPN opérationnelle dépend de plusieurs fichiers et directives : certificat/clé du serveur, certificat/clé du client si l’authentification par certificat est retenue, autorité de certification, paramètres TLS, paramètres de canal de données, pool d’adresses, routes distribuées, DNS et règles de pare-feu. Les paramètres exacts doivent être adaptés à la version et au modèle d’authentification de la plateforme.

## 16. Comparaison : IPsec/IKEv2, WireGuard et OpenVPN

| Critère | IPsec / IKEv2 | WireGuard | OpenVPN |
|---|---|---|---|
| Approche | Architecture IP standardisée, négociation IKE et ESP | Protocole VPN compact sur UDP basé sur des pairs cryptographiques | Solution VPN flexible avec TLS et canal de données dédié |
| Usage fréquent | Site-à-site, équipements d’entreprise, mobilité selon les clients | Site-à-site et accès distant, notamment quand l’écosystème le prend en charge | Accès distant et interconnexion lorsque flexibilité et compatibilité sont importantes |
| Gestion d’identité | Certificats, clés prépartagées ou mécanismes compatibles avec le profil | Clés publiques des pairs ; gestion utilisateur et cycle de vie souvent à intégrer séparément | Certificats et autres mécanismes selon le serveur et la configuration |
| Interopérabilité | Large mais la compatibilité des propositions et comportements doit être testée | Très bonne entre implémentations compatibles, mais intégration à l’outillage existant à vérifier | Large avec ses clients et profils, mais les paramètres et versions doivent être alignés |
| Transport | ESP, souvent UDP 4500 avec NAT-T ; IKE généralement sur UDP 500/4500 | UDP | UDP ou TCP |
| Complexité dominante | Négociation, propositions, SA, sélecteurs, NAT-T et compatibilité interconstructeurs | Inventaire/distribution des clés, `AllowedIPs`, routage et intégration de gestion | PKI, fichiers de configuration, options TLS/data-channel, pool, routes et compatibilité |
| Attention particulière | Un tunnel établi peut n’autoriser aucun flux utile si les sélecteurs ou routes sont incohérents | `AllowedIPs` a des implications de routage et d’authentification de source | Ne pas reprendre d’anciens paramètres ou des options de compatibilité qui abaissent la sécurité |

Il n’existe pas de gagnant universel. Le choix dépend de l’architecture, des clients supportés, du système de gestion des identités, de l’interopérabilité des équipements, des contraintes de conformité, de la performance et de la capacité de l’équipe à maintenir le système.


# PARTIE V — ROUTAGE, DNS ET POLITIQUES D’ACCÈS

## 17. Le routage décide du chemin, pas du droit d’accès

Pour qu’un paquet atteigne un serveur distant, il faut plusieurs conditions simultanées :

1. une route utilisable vers la destination ;
2. un tunnel et un pair en état d’acheminer le trafic ;
3. une politique VPN qui couvre le flux ;
4. un pare-feu qui autorise le flux dans le sens nécessaire ;
5. une route retour vers la source ;
6. un service qui écoute sur l’adresse et le port attendus.

### Exemple de table de routage logique

```text
Destination           Prochaine étape / interface
10.10.10.0/24         LAN local
10.20.20.0/24         interface VPN (wg0 ou interface équivalente)
0.0.0.0/0             passerelle Internet par défaut
```

Ce tableau est un exemple conceptuel ; les routes les plus spécifiques l’emportent habituellement sur les routes moins spécifiques. Le routage par politique, les règles de marquage, plusieurs tables, les namespaces ou les routes imposées par un client peuvent changer la décision finale. Utilisez un outil comme `ip route get <adresse>` sur Linux pour examiner la décision effective du noyau dans le contexte courant.

## 18. Sous-réseaux qui se chevauchent

Le chevauchement est un problème d’architecture, pas uniquement un problème de tunnel.

Exemple : le siège et une agence utilisent tous deux `192.168.1.0/24`. Un poste du siège veut joindre `192.168.1.50`. La table de routage locale considère normalement cette destination comme locale : le paquet ne part donc pas spontanément vers l’agence.

```text
SIÈGE                                      AGENCE
192.168.1.0/24                             192.168.1.0/24
PC : 192.168.1.20                          Serveur : 192.168.1.50
       |                                          |
       +------ tunnel VPN entre passerelles ------+

Le même préfixe désigne deux réseaux différents : le routage est ambigu.
```

**Solutions par ordre de préférence selon le contexte :**

- renuméroter l’un des réseaux avec un plan d’adressage géré ;
- utiliser une translation d’adresses documentée et strictement limitée si la renumérotation est impossible ;
- concevoir une architecture d’accès par proxy ou bastion lorsqu’un accès applicatif contrôlé est plus approprié qu’un routage complet.

Le NAT de contournement a des coûts : diagnostic plus difficile, journalisation moins directe, règles supplémentaires et comportement inattendu pour certains protocoles. Documentez les adresses traduites et les limites du modèle.

## 19. Split tunnel, full tunnel et routes IPv6

Un profil full tunnel doit être vérifié sur l’ensemble de la pile réseau. Il ne suffit pas d’envoyer la route IPv4 `0.0.0.0/0` vers le tunnel si le système possède aussi une connectivité IPv6 utilisable qui continue à sortir directement.

Checklist d’un profil full tunnel :

- route IPv4 par défaut prévue dans le VPN ;
- route IPv6 par défaut ou politique IPv6 cohérente ;
- accès à l’endpoint VPN conservé par une route de transport qui évite de faire boucler le tunnel sur lui-même ;
- DNS prévu dans le profil ;
- règles de fuite ou *kill switch* adaptées au système, notamment en cas de coupure du tunnel ;
- gestion des réseaux locaux explicitement décidée ;
- tests d’adresse de sortie IPv4 et IPv6, de DNS et de reconnexion ;
- comportement documenté lorsqu’un réseau Wi-Fi, une interface Ethernet ou un partage mobile change.

Dans certains clients, la route vers le serveur VPN doit rester accessible par l’underlay, même lorsque le reste du trafic est envoyé dans le tunnel. Une mauvaise route peut faire perdre le serveur et empêcher le tunnel de se rétablir.

## 20. DNS : le tunnel peut fonctionner alors que les noms échouent

Exemples typiques :

- les adresses IP internes répondent, mais `app.intra.example` ne se résout pas ;
- les noms publics se résolvent, mais les noms privés échouent ;
- le DNS privé ne répond que depuis certains sous-réseaux ;
- le suffixe de recherche manque ;
- le poste conserve un serveur DNS du réseau local ;
- plusieurs interfaces publient des serveurs DNS concurrents ;
- une reconnexion du VPN ne restaure pas la configuration DNS attendue.

### Diagnostic DNS

```text
Nom applicatif échoue
       |
       +--> Le service est-il joignable par IP ?
       |         |
       |         +--> NON : vérifier route, filtre, service et retour
       |         |
       |         +--> OUI : continuer
       |
       +--> Quel serveur DNS le poste interroge-t-il réellement ?
       |
       +--> Le serveur DNS est-il joignable via le VPN ?
       |
       +--> Le serveur connaît-il la zone et le nom demandé ?
       |
       +--> Le suffixe de recherche et les politiques par domaine sont-ils corrects ?
```

La façon d’afficher et de modifier les DNS dépend du système d’exploitation et du client VPN. Vérifiez la configuration réellement appliquée par le système après connexion, après déconnexion et après reconnexion.

## 21. Pare-feu et moindre privilège

Une architecture VPN ne devrait pas rendre tout un LAN accessible à tout utilisateur distant simplement parce qu’il est connecté.

### Exemple de matrice d’accès

| Origine | Destination | Service | Décision de départ |
|---|---|---|---|
| Groupe support | Bastion d’administration | SSH/RDP selon la plateforme | Autoriser, journaliser, MFA si applicable |
| Utilisateur métier | Application métier | HTTPS | Autoriser uniquement vers l’application nécessaire |
| Utilisateur métier | Réseau d’administration | Tous services | Refuser par défaut |
| Client VPN | Réseau de gestion des hyperviseurs | Tous services | Refuser sauf rôle explicitement autorisé |
| Pair site-à-site | Sous-réseau applicatif distant | Services documentés | Autoriser les flux nécessaires uniquement |

Une adresse source issue du pool VPN n’est pas une identité suffisante. Selon le risque, reliez la décision d’accès au compte, au certificat ou à la clé, au rôle, à l’état du terminal, à la destination et au service. Un VPN peut fournir une connectivité réseau privée sans fournir à lui seul un modèle complet de contrôle d’accès applicatif.


# PARTIE VI — SÉCURISER L’EXPLOITATION

## 22. Modèle de menace : que protège le VPN et que ne protège-t-il pas ?

Un VPN peut protéger les paquets pendant leur transport entre des pairs correctement authentifiés. Il ne protège pas automatiquement :

- un poste compromis avant le chiffrement ou après le déchiffrement ;
- des identifiants volés ou une session applicative déjà détournée ;
- un serveur interne vulnérable accessible derrière le tunnel ;
- des données copiées ou enregistrées après leur arrivée ;
- un administrateur autorisé qui dispose de privilèges excessifs ;
- des métadonnées de trafic visibles sur l’underlay ;
- une mauvaise configuration de routage, de DNS ou de pare-feu ;
- une interruption volontaire ou accidentelle de connectivité.

Le VPN est un contrôle dans une défense en profondeur. Il doit être combiné à des mises à jour, au durcissement des systèmes, à la gestion des identités, à la segmentation et à la supervision.

## 23. Identités, clés, certificats et révocation

### Pour les certificats

- établir une autorité de certification (CA) et une politique d’émission contrôlées ;
- protéger les clés privées de la CA plus strictement que les certificats des clients ;
- distinguer les certificats de serveur, d’utilisateur, de machine et d’administration selon le besoin ;
- vérifier le nom ou l’identité attendue du serveur côté client ;
- vérifier les dates de validité, la chaîne de confiance et les mécanismes de révocation disponibles ;
- prévoir le renouvellement avant expiration et surveiller les certificats proches de leur fin de validité ;
- définir une procédure de compromission : révoquer, remplacer, désactiver le pair, vérifier les journaux, puis confirmer que l’ancien accès ne fonctionne plus.

### Pour les clés WireGuard

- tenir un inventaire reliant chaque clé publique à un équipement, un propriétaire, une fonction et une date d’émission ;
- protéger les clés privées par les permissions, les mécanismes de stockage et les contrôles d’accès disponibles ;
- retirer la clé publique d’un pair autorisé lorsqu’il doit perdre l’accès ;
- remplacer une clé compromise et vérifier la suppression de l’ancienne autorisation partout où elle est distribuée ;
- ne pas confondre le renouvellement périodique des clés de session avec la rotation des clés d’identité à long terme.

### Authentification multifacteur

Pour l’accès distant utilisateur, l’authentification multifacteur peut réduire le risque lié à un mot de passe volé, à condition qu’elle soit réellement intégrée au flux d’authentification et qu’elle ne soit pas contournable par un ancien portail ou un chemin alternatif. Un certificat de machine, une clé de pair et une authentification utilisateur ne sont pas des concepts identiques : associez-les selon le modèle de menace.

## 24. Journalisation et supervision

Superviser le tunnel ne signifie pas seulement surveiller le ping de l’endpoint.

### Indicateurs utiles

- disponibilité et dernier établissement réussi ;
- dernier handshake ou âge des SA ;
- échecs d’authentification et de négociation ;
- nombre de pairs actifs et évolution du nombre de clients ;
- compteurs d’octets et paquets entrants/sortants ;
- pertes, latence et débit des flux utiles ;
- expiration prochaine de certificat ;
- changements de configuration, de clés, de routes ou de politiques ;
- charge CPU, mémoire, interfaces et liens WAN ;
- taux d’échec des applications accessibles à travers le tunnel.

### Alertes à prioriser

1. tunnel critique indisponible au-delà du seuil convenu ;
2. échec répété d’authentification ou comportement inhabituel ;
3. certificat proche d’expirer ou clé compromise ;
4. hausse anormale des pairs, du trafic ou des erreurs ;
5. écart de configuration entre les deux extrémités ;
6. tunnel déclaré actif mais application métier indisponible.

Ne stockez pas de secrets ou de données utilisateur excessives dans les journaux. Les journaux doivent être protégés, horodatés de manière cohérente, conservés selon une politique définie et accessibles aux seuls rôles qui en ont besoin.

## 25. Disponibilité, redondance et reprise

Un VPN réellement critique doit traiter les pannes de WAN, de passerelle, de processus, de clés, de DNS et de routage.

```text
                   +--------------------+
                   | Clients / sites     |
                   +---------+----------+
                             |
                    routes / politiques
                             |
                +------------+------------+
                |                         |
           [VPN Gateway A]           [VPN Gateway B]
                |                         |
                +------------+------------+
                             |
                  Réseau interne segmenté
```

Ce schéma ne définit pas un mécanisme de haute disponibilité : il représente deux chemins potentiels. En production, il faut choisir et tester le mode exact, par exemple redondance de passerelle, bascule de route, cluster d’équipements, deux tunnels ou reprise sur un second site.

À documenter et tester :

- mode de détection de panne et temporisation ;
- convergence du routage et risque de route asymétrique ;
- disponibilité des deux endpoints depuis les sites distants ;
- synchronisation ou distribution des clés et certificats ;
- capacité de la seconde passerelle à supporter la charge ;
- comportement des sessions applicatives lors de la bascule ;
- tests de retour à la passerelle primaire ;
- procédure de changement de clé ou de certificat sur les deux chemins.

La disponibilité du tunnel ne garantit pas la continuité des sessions TCP. Une bascule peut conserver la route mais changer l’adresse source, l’état NAT ou l’association de sécurité ; l’application peut alors devoir se reconnecter.

## 26. Performance et capacité

Le débit réel peut être limité par :

- le débit WAN disponible dans chaque sens ;
- la capacité CPU à chiffrer et vérifier les paquets ;
- le nombre de paquets par seconde, pas seulement le débit en bits/s ;
- les capacités cryptographiques de la plateforme ;
- la MTU, la fragmentation et les retransmissions ;
- le nombre de tunnels, de pairs, de routes et de politiques ;
- la journalisation, l’inspection, l’antivirus ou les autres fonctions de sécurité ;
- la latence et les pertes sur l’underlay.

Pour dimensionner, mesurez des scénarios réalistes : plusieurs utilisateurs simultanés, plusieurs flux par utilisateur, transferts de fichiers, applications interactives et pics de charge. Distinguez le débit d’un seul flux du débit agrégé. Comparez les résultats avant et après tunnel dans les mêmes conditions.


# PARTIE VII — MÉTHODE DE DÉPANNAGE EXPERTE

## 27. Règle de diagnostic : ne modifier qu’une variable à la fois

Pour chaque incident :

1. écrire le symptôme exact et l’heure de début ;
2. définir le périmètre : un utilisateur, un site, une destination, un protocole ou tous les flux ;
3. identifier ce qui fonctionne encore ;
4. proposer une hypothèse et le test qui peut la confirmer ou l’infirmer ;
5. collecter les preuves avant de modifier la configuration ;
6. effectuer une modification réversible ;
7. rejouer les tests et comparer les résultats ;
8. documenter la cause racine et la prévention.

Évitez le dépannage par « redémarrer tout », qui peut effacer les indices ou aggraver une panne étendue. Un redémarrage peut être une action de rétablissement valide, mais il ne remplace pas le diagnostic.

## 28. Matrice symptôme → test

| Symptôme | Causes plausibles | Test discriminant |
|---|---|---|
| Pas de handshake | Endpoint incorrect, port filtré, clé/identité incorrecte, service non à l’écoute | Capturer l’underlay, vérifier l’endpoint, les règles et les journaux du protocole |
| Handshake présent, aucun paquet utile | Mauvais `AllowedIPs` ou sélecteurs, route absente, pare-feu, forwarding désactivé | Vérifier route effective, compteur de trafic, règle de transfert et route retour |
| Un seul sens fonctionne | Route retour absente, filtrage stateful, NAT inattendu, asymétrie | Capture aux deux côtés et comparaison des routes dans les deux sens |
| Les pings fonctionnent, l’application échoue | Port fermé, ACL applicative, DNS, MTU, certificat applicatif ou proxy | Tester le port et le service, résoudre le nom séparément, mesurer la MTU |
| Les petits paquets passent mais pas les gros | MTU/PMTUD, fragmentation filtrée, MSS inadapté | Tests de taille, compteurs et capture ICMP/fragmentation |
| Connexion instable en mobilité | Changement d’adresse, NAT, roaming, Wi-Fi qui change, temporisations | Comparer les horaires des changements d’interface, des handshakes et des pertes |
| Certains sites ne sont pas accessibles | Route manquante, chevauchement de sous-réseau, sélecteur incomplet | Comparer plan d’adressage, route choisie et préfixes déclarés |
| Les IP fonctionnent mais les noms échouent | DNS absent, mauvaise zone, suffixe ou résolution par mauvaise interface | Interroger explicitement le DNS prévu et comparer la réponse |
| VPN connecté mais Internet ne passe plus | Route par défaut, DNS, NAT de sortie ou filtrage du full tunnel | Examiner routes IPv4/IPv6, DNS et sortie Internet depuis la passerelle VPN |
| Fuite hors tunnel | Route IPv6 ou DNS non gérée, kill switch incomplet, exception non voulue | Test IPv4/IPv6/DNS avant, pendant, après déconnexion et après reconnexion |
| Panne périodique | Expiration de certificat, rekey, NAT timeout, rotation ou tâche de maintenance | Corréler la panne avec les journaux et changements d’état horodatés |

## 29. Outils et preuves à collecter

Les commandes varient selon l’OS, la distribution et le client. La liste ci-dessous est une boîte à outils, pas une séquence à exécuter intégralement sur tous les systèmes.

### Linux : routes et interfaces

```bash
ip address
ip route
ip route get 10.20.20.20
ip rule
ip -s link
```

### WireGuard

```bash
sudo wg show
sudo wg show wg0
```

Inspectez notamment la clé publique du pair, le dernier handshake et les compteurs reçus/envoyés. Masquez les informations sensibles dans les captures partagées et ne publiez jamais de clé privée.

### Écoute et capture

```bash
# Vérifier les sockets UDP, selon les outils disponibles
sudo ss -lunp

# Capture indicative ; adapter l'interface et le filtre
sudo tcpdump -ni <interface_wan> udp port 51820
sudo tcpdump -ni <interface_lan> host 10.20.20.20
```

Pour IPsec, ajoutez des captures adaptées à IKE et ESP/NAT-T, puis examinez les journaux natifs de la plateforme. Le trafic ESP peut ne pas apparaître comme un simple flux UDP si NAT-T n’est pas utilisé.

### Tests applicatifs

- vérifier une résolution DNS ;
- tester la connexion au port TCP ou UDP réellement utilisé ;
- effectuer une requête HTTP(S) vers le service attendu ;
- comparer un test depuis le LAN local et depuis le VPN ;
- tester le sens retour ;
- répéter après reconnexion ou bascule.

Une capture peut révéler des adresses privées, noms internes, identifiants ou métadonnées sensibles. Limitez le périmètre, protégez les fichiers de capture et effacez-les selon la politique de l’organisation.

## 30. Arbre de décision général

```text
Le VPN est-il établi ?
 |
 +-- NON --> L'endpoint est-il joignable depuis l'underlay ?
 |              |
 |              +-- NON --> routes WAN / DNS public / NAT / pare-feu
 |              |
 |              +-- OUI --> authentification / certificats / clés /
 |                           propositions / port / version / logs
 |
 +-- OUI --> La route vers la destination utilise-t-elle le VPN ?
                |
                +-- NON --> route / AllowedIPs / sélecteurs / table de routage
                |
                +-- OUI --> Les compteurs et captures montrent-ils le trafic ?
                               |
                               +-- NON --> pare-feu local / interface / application
                               |
                               +-- OUI --> Le retour est-il routé et autorisé ?
                                              |
                                              +-- NON --> route retour / ACL / NAT
                                              |
                                              +-- OUI --> DNS / MTU / service / politique
```

Cet arbre est un guide de triage : plusieurs causes peuvent coexister. Les symptômes doivent toujours être confrontés à des observations du système réel.


# PARTIE VIII — LABORATOIRES D’EXPERTISE

## 31. Laboratoire 1 — VPN site-à-site sécurisé

**Objectif :** déployer ou simuler l’interconnexion de deux sous-réseaux non chevauchants.

**Contexte :** siège `10.10.10.0/24`, agence `10.20.20.0/24`, deux passerelles, underlay IP entre les passerelles.

**Travail demandé :**

1. dessiner la topologie et attribuer les adresses ;
2. définir les préfixes autorisés ;
3. choisir IPsec/IKEv2 ou WireGuard et justifier ce choix ;
4. configurer le tunnel et les routes ;
5. limiter les flux au besoin métier ;
6. vérifier les routes aller/retour ;
7. vérifier les logs et compteurs ;
8. simuler la perte du tunnel et documenter la reprise.

**Critères de réussite :** un hôte autorisé de chaque LAN peut joindre le service cible ; un flux non autorisé est bloqué ; la cause d’une panne simulée peut être identifiée grâce aux journaux et tests.

## 32. Laboratoire 2 — Accès distant avec droits limités

**Objectif :** concevoir un accès distant qui n’ouvre pas tout le réseau interne.

**Environnement :** un client, une passerelle VPN, un DNS interne, une application métier et un réseau d’administration séparé.

**Travail demandé :**

1. distinguer l’identité utilisateur et l’identité machine si les deux sont requises ;
2. choisir le mécanisme d’authentification ;
3. définir le pool d’adresses VPN ;
4. distribuer les routes strictement nécessaires ;
5. distribuer le DNS interne et les suffixes utiles ;
6. autoriser uniquement les services métier prévus ;
7. prouver que le réseau d’administration reste inaccessible à l’utilisateur ordinaire ;
8. révoquer un compte, certificat ou pair de test et vérifier que l’accès est effectivement coupé.

**Livrable :** matrice d’accès, diagramme textuel, configuration expurgée de secrets, résultats des tests avant/après révocation.

## 33. Laboratoire 3 — Full tunnel, split tunnel et fuite

**Objectif :** prouver le chemin suivi par IPv4, IPv6 et DNS.

**Travail demandé :**

1. établir un profil split tunnel vers un sous-réseau privé ;
2. comparer une destination interne et une destination Internet ;
3. passer à un profil full tunnel dans un environnement contrôlé ;
4. tester la route IPv4 par défaut ;
5. tester le chemin IPv6 ;
6. confirmer le serveur DNS utilisé ;
7. simuler une coupure du tunnel et vérifier le comportement prévu ;
8. écrire une procédure de test reproductible.

**Attention :** un test de fuite doit être réalisé sur un environnement et un terminal dont vous êtes autorisé à vérifier la configuration. Évitez de modifier globalement la connectivité d’un poste de production.

## 34. Laboratoire 4 — Diagnostic MTU

**Objectif :** reconnaître un tunnel établi qui perd les grands paquets.

**Scénario :** petits échanges fonctionnels, transfert de fichier instable.

**Travail demandé :**

1. reproduire le problème avec une destination contrôlée ;
2. mesurer les tailles de paquets qui passent ;
3. observer les compteurs et messages ICMP disponibles ;
4. comparer le comportement sur tunnel et hors tunnel ;
5. modifier un seul paramètre à la fois ;
6. confirmer la correction sur plusieurs flux et après reconnexion ;
7. expliquer pourquoi l’ajustement choisi est approprié au chemin.

## 35. Laboratoire 5 — Haute disponibilité et rotation

**Objectif :** valider l’exploitation au-delà du cas nominal.

**Travail demandé :**

- simuler une panne de l’endpoint principal ;
- mesurer le délai de détection et de reprise ;
- vérifier les routes retour pendant la convergence ;
- renouveler une clé ou un certificat selon la procédure prévue ;
- retirer un pair et vérifier qu’il ne peut plus établir le tunnel ;
- confirmer que les journaux permettent de reconstituer la chronologie ;
- documenter les conséquences sur les sessions applicatives.


# PARTIE IX — ÉVALUATION ET SYNTHÈSE

## 36. Questions de vérification

Répondez sans relire le cours, puis vérifiez vos réponses.

1. Pourquoi un handshake VPN réussi ne prouve-t-il pas qu’un serveur distant est accessible ?
2. Quelle est la différence entre une route et une règle de pare-feu ?
3. Pourquoi le réseau de transport utilise-t-il des adresses différentes de celles du paquet intérieur ?
4. Dans IPsec, à quoi servent IKE SA et Child SA ?
5. Pourquoi ESP est-il généralement plus pertinent qu’AH lorsque NAT est présent ?
6. Que représente `AllowedIPs` dans WireGuard au-delà de la sélection de route ?
7. Pourquoi ne faut-il pas envoyer un préfixe `0.0.0.0/0` à tous les pairs sans réfléchir au besoin ?
8. Quel symptôme peut faire suspecter un problème de MTU et quelles autres causes faut-il éliminer ?
9. Pourquoi un full tunnel doit-il traiter IPv4, IPv6 et DNS de manière cohérente ?
10. Quelles données faut-il inventorier pour pouvoir révoquer rapidement un accès ?
11. Pourquoi un chevauchement entre deux sous-réseaux rend-il le routage ambigu ?
12. Quelle différence existe entre renouveler des clés de session et faire tourner une clé d’identité ?
13. Quels tests démontrent qu’une politique de moindre privilège fonctionne réellement ?
14. Quelles preuves collecter avant de redémarrer un tunnel en panne ?
15. Pourquoi un tunnel redondant n’assure-t-il pas nécessairement la continuité des sessions applicatives ?

## 37. Corrigé synthétique

1. Le handshake valide l’établissement cryptographique, pas les routes, les règles de transfert, le retour, le DNS ni le service applicatif.
2. La route décide du chemin ; le pare-feu autorise ou bloque un flux selon les règles en place.
3. Le paquet intérieur porte les adresses logiques des systèmes communicants ; le paquet extérieur porte les adresses utilisées par l’underlay pour acheminer le tunnel.
4. L’IKE SA protège les échanges IKE ; les Child SAs protègent le trafic de données IPsec.
5. AH authentifie certains champs IP qui peuvent être modifiés par NAT ; cette modification complique son fonctionnement. ESP avec NAT-T est plus répandu.
6. `AllowedIPs` associe les préfixes aux pairs pour l’envoi et contraint les adresses source attendues des paquets reçus du pair.
7. Cela peut détourner tout le trafic, exposer le poste à des erreurs de route, surcharger la passerelle ou provoquer une coupure si le chemin vers l’endpoint n’est pas préservé.
8. Les petits paquets passent et les gros échouent ou se bloquent. Il faut tester MTU/PMTUD mais aussi filtrage ICMP, service, pertes et autres causes réseau.
9. Sinon une famille d’adresses ou les requêtes DNS peuvent sortir par le chemin local alors que l’autre trafic passe dans le tunnel.
10. Identité ou propriétaire, pair/équipement, clé publique ou certificat, droits accordés, expiration, emplacement de configuration et procédure de révocation.
11. La destination peut sembler directement connectée localement, donc le trafic ne suit pas le tunnel attendu ; une renumérotation ou une translation contrôlée peut être nécessaire.
12. Le renouvellement des clés de session protège le trafic courant et limite la durée d’utilisation d’une clé ; la rotation d’identité change le secret ou certificat qui identifie à long terme le pair.
13. Un flux requis passe, un flux non autorisé échoue, les journaux reflètent le résultat et la révocation bloque réellement le pair concerné.
14. Symptôme précis, heure, périmètre, routes, état du tunnel, journaux, compteurs, captures limitées et tests de flux.
15. La bascule peut modifier l’adresse source ou l’état réseau, et les sessions applicatives ont leur propre état et leurs propres temporisations.

## 38. Projet de synthèse : rédiger un dossier de conception VPN

Rédigez un dossier qui comporte au minimum :

1. **Besoin métier** — utilisateurs, applications, sites, contraintes et objectifs de disponibilité.
2. **Modèle de menace** — réseaux non fiables, terminaux, identité, données et risques résiduels.
3. **Architecture** — schémas textuels, points de terminaison, underlay, overlay et zones de sécurité.
4. **Plan d’adressage** — pools, sous-réseaux, routes, absence de chevauchement et traitement d’IPv6.
5. **Choix du protocole** — comparaison documentée des options retenues et rejetées.
6. **Authentification et clés** — génération, stockage, rotation, révocation et responsabilité opérationnelle.
7. **Politiques d’accès** — matrice origine/destination/service, accès refusés et journalisation.
8. **DNS et routage** — split/full tunnel, routes de secours et comportement de reconnexion.
9. **Performance** — capacité, MTU, latence, débit attendu et seuils d’alerte.
10. **Exploitation** — supervision, sauvegardes, changements, procédures de panne et reprise.
11. **Tests de recette** — connectivité, autorisations, refus, DNS, IPv6, MTU, rotation et bascule.
12. **Risques résiduels** — limites du VPN, contrôles complémentaires et plan d’amélioration.

Le dossier doit permettre à une autre personne qualifiée de reconstruire le laboratoire, de comprendre les décisions prises et de diagnostiquer une panne sans dépendre de la mémoire de l’auteur.


# GLOSSAIRE

- **ACL :** liste de contrôle d’accès déterminant les flux autorisés ou refusés.
- **CA :** autorité de certification qui émet et valide les certificats selon une politique.
- **Child SA :** association IPsec utilisée pour la protection du trafic de données.
- **ESP :** protocole IPsec assurant la protection des paquets selon les algorithmes et le mode retenus.
- **Full tunnel :** politique où tout le trafic visé est dirigé vers le VPN.
- **Handshake :** échange initial ou renouvelé permettant d’établir des clés ou un état de sécurité.
- **IKEv2 :** protocole de négociation et de gestion des associations de sécurité IPsec.
- **IPsec :** architecture de sécurité au niveau IP.
- **MTU :** taille maximale d’un paquet ou d’une unité de transmission sur une interface, selon le contexte.
- **NAT-T :** transport d’ESP dans UDP pour faciliter la traversée de NAT.
- **Overlay :** réseau logique construit sur un réseau de transport.
- **PFS :** propriété de sécurité visant à préserver les clés de session passées si une clé à long terme est compromise ultérieurement, selon le protocole et le profil.
- **PMTUD :** découverte de la MTU du chemin.
- **SA :** association de sécurité qui définit notamment les paramètres de protection d’un trafic.
- **Split tunnel :** séparation entre le trafic envoyé dans le VPN et celui qui suit un autre chemin.
- **TAP :** interface virtuelle de couche Ethernet.
- **TUN :** interface virtuelle de couche IP.
- **Underlay :** réseau existant qui transporte les paquets extérieurs du tunnel.
- **VPN :** réseau privé virtuel permettant de créer une connectivité logique protégée au-dessus d’un réseau existant.


# RÉFÉRENCES TECHNIQUES

Les références ci-dessous sont des sources de départ pour approfondir le protocole et actualiser les choix opérationnels. Les paramètres de sécurité doivent être validés au moment du déploiement, dans la version exacte du logiciel ou du matériel concerné.

1. **NIST — Guide to IPsec VPNs, SP 800-77 Rev. 1** : guide de conception et d’exploitation d’IPsec.  
   https://csrc.nist.gov/pubs/sp/800/77/r1/final
2. **IETF — RFC 4301, Security Architecture for the Internet Protocol** : architecture de sécurité IPsec.  
   https://www.rfc-editor.org/rfc/rfc4301.html
3. **IETF — RFC 7296, Internet Key Exchange Protocol Version 2 (IKEv2)** : spécification IKEv2, mise à jour par plusieurs RFC ultérieures.  
   https://www.rfc-editor.org/rfc/rfc7296.html
4. **WireGuard — Protocol & Cryptography** : description officielle des primitives et du protocole.  
   https://www.wireguard.com/protocol/
5. **OpenVPN — Manuel de référence 2.6** : options et comportement d’OpenVPN selon la version.  
   https://openvpn.net/community-docs/community-articles/openvpn-2-6-manual.html


## Check-list finale avant mise en production

- [ ] Besoin métier, périmètre et modèle de menace documentés.
- [ ] Plan d’adressage sans chevauchement ou stratégie de traduction explicitement validée.
- [ ] Choix du protocole justifié par l’interopérabilité, la sécurité et l’exploitation.
- [ ] Clés/certificats générés, protégés, inventoriés et révocables.
- [ ] Authentification et droits associés aux rôles réels.
- [ ] Routes aller et retour vérifiées.
- [ ] Règles de pare-feu limitées aux services nécessaires.
- [ ] DNS interne, IPv4, IPv6 et comportement full/split tunnel testés.
- [ ] MTU et flux applicatifs représentatifs testés.
- [ ] Journaux, alertes, sauvegardes et procédure de retour arrière en place.
- [ ] Scénarios de perte de tunnel, de rotation et de bascule exécutés.
- [ ] Secrets absents des dépôts, tickets, captures d’écran et fichiers de journalisation.

**Règle d’or :** la réussite d’un VPN se mesure à la connectivité requise, aux accès interdits, à la sécurité des identités, à la capacité de diagnostiquer les incidents et à la qualité de la reprise — pas au seul voyant « connecté ».
