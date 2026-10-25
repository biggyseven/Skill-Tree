# PKI et certificats TLS/SSL — Débutant

**Niveau :** Débutant

La Public Key Infrastructure (PKI), ou infrastructure à clés publiques, permet de lier une identité — par exemple le nom d’un serveur Web — à une clé publique au moyen d’un certificat numérique. Cette liaison est vérifiée par une chaîne de confiance et des règles précises. Dans la pratique, les certificats servent à établir HTTPS, à authentifier des équipements réseau, à sécuriser des API, à protéger des accès VPN et à mettre en place l’authentification mutuelle.

Le terme **SSL** reste courant dans les conversations et dans certains noms d’options, mais SSL est un ancien protocole qui ne doit plus être activé. Les déploiements modernes utilisent TLS. TLS 1.3 est spécifié par la RFC 9846 publiée en juillet 2026, qui remplace la RFC 8446 ; les environnements existants peuvent encore rencontrer TLS 1.2 selon les politiques de compatibilité. Le certificat ne chiffre pas, à lui seul, toute la communication : il participe à l’authentification et à l’établissement du canal TLS, qui utilise ensuite des clés symétriques pour protéger les données. [RFC 9846](https://www.rfc-editor.org/rfc/rfc9846.html)

> **Analogie** : Un certificat est comparable à une carte d’identité signée par une autorité reconnue. La carte relie un nom à une clé publique, et la signature permet de vérifier que l’autorité a approuvé cette liaison. Une carte authentique ne garantit toutefois pas que son porteur est bien la personne recherchée si tu ne compares pas le bon nom.


<style>
.pki-diagram{width:100%;max-width:100%;margin:1.35rem auto 1.8rem;padding:.55rem;border:1px solid #334155;border-radius:16px;background:#090d14;box-sizing:border-box;overflow:hidden;color:#e4e4e7}
.pki-diagram svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}
.pki-diagram svg text{font-family:Inter,ui-sans-serif,system-ui,sans-serif;font-size:13px;fill:#e4e4e7}
.pki-diagram svg .pki-title{font-size:15px;font-weight:700;fill:#f8fafc}
.pki-diagram svg .pki-sub{font-size:11px;fill:#cbd5e1}
.pki-diagram svg .pki-box{fill:#111827;stroke:#64748b;stroke-width:1.5}
.pki-diagram svg .pki-blue{fill:#102a43;stroke:#60a5fa;stroke-width:1.5}
.pki-diagram svg .pki-green{fill:#123126;stroke:#4ade80;stroke-width:1.5}
.pki-diagram svg .pki-amber{fill:#352711;stroke:#fbbf24;stroke-width:1.5}
.pki-diagram svg .pki-red{fill:#3b171b;stroke:#f87171;stroke-width:1.5}
.pki-diagram svg .pki-flow{fill:none;stroke-width:2.5;stroke-linecap:round;stroke-dasharray:6 9;animation:pkiFlow 1.35s linear infinite}
.pki-diagram svg .pki-flow-blue{stroke:#60a5fa}
.pki-diagram svg .pki-flow-green{stroke:#4ade80}
.pki-diagram svg .pki-flow-amber{stroke:#fbbf24}
.pki-diagram svg .pki-flow-red{stroke:#f87171}
.pki-diagram svg .pki-dot{animation:pkiPulse 1.8s ease-in-out infinite}
.pki-diagram svg .pki-dot-delay{animation-delay:.65s}
.pki-diagram svg .pki-flow-slow{animation-duration:2.1s}
@keyframes pkiFlow{to{stroke-dashoffset:-30}}
@keyframes pkiPulse{0%,100%{opacity:.35}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.pki-diagram svg *, .pki-diagram svg *::before,.pki-diagram svg *::after{animation:none!important;transition:none!important}}
@media(max-width:640px){.pki-diagram{padding:.25rem;border-radius:10px}.pki-diagram svg text{font-size:12px}}
</style>

## 1. Pourquoi les certificats sont nécessaires

Quand un navigateur ouvre `https://exemple.test`, il doit répondre à plusieurs questions :

1. Est-ce que le serveur peut prouver qu’il détient la clé privée correspondant à une clé publique certifiée ?
2. Le certificat a-t-il été signé par une autorité de certification reconnue par le navigateur ou le système ?
3. Le nom demandé correspond-il à un nom présent dans le certificat ?
4. Le certificat est-il dans sa période de validité et acceptable selon les règles cryptographiques locales ?
5. Existe-t-il une information de révocation pertinente et accessible, lorsque l’application exige cette vérification ?

Le cadenas du navigateur ne signifie pas « ce site est honnête » ou « ce site ne peut pas être malveillant ». Il signifie principalement que la connexion répond aux contrôles TLS que le navigateur applique : identité attendue, chaîne de confiance et protection cryptographique du canal. Un site frauduleux peut aussi posséder un certificat valide pour son propre nom de domaine.

## 2. Les éléments de base d’une PKI

Une PKI regroupe les rôles, les procédures, les logiciels et les politiques utilisés pour gérer des clés et des certificats. Les rôles les plus courants sont :

| Élément | Fonction | Exemple |
|---|---|---|
| Paire de clés | Une clé privée reste secrète ; la clé publique peut être partagée | Clé d’un serveur HTTPS |
| Certificat X.509 | Lie une identité à une clé publique, avec des usages et une période de validité | `www.exemple.com` |
| Autorité de certification (CA/AC) | Signe les certificats selon une politique | CA d’entreprise ou CA publique |
| Autorité d’enregistrement (RA) | Vérifie ou transmet les demandes selon la politique | Équipe IT vérifiant l’identité d’un employé |
| CSR | Demande de signature contenant la clé publique et les attributs demandés | Fichier `.csr` créé sur le serveur |
| Magasin de confiance | Liste de certificats racines ou ancres approuvés | Magasin du système d’exploitation |
| CRL | Liste publiée de certificats révoqués | Liste émise par une CA |
| OCSP | Protocole permettant de demander le statut d’un certificat | Réponse « good », « revoked » ou « unknown » |
| Horloge fiable | Permet de contrôler `notBefore` et `notAfter` | NTP correctement configuré |

La **clé privée** doit rester sous contrôle de son propriétaire. Elle n’est normalement jamais envoyée à l’autorité de certification. La demande de signature (CSR) transmet la clé publique et des informations de demande ; la CA signe ensuite un certificat qui contient la clé publique et les identités approuvées.

> **Piège :** Un certificat public n’est pas un secret. En revanche, sa clé privée l’est. Envoyer une clé privée à un fournisseur par courrier électronique ou la commettre dans Git compromet potentiellement l’identité protégée par cette clé.

### Schéma 1 — Chaîne de confiance

<div class="pki-diagram"><svg viewBox="0 0 760 350" role="img" aria-label="Chaîne de confiance : la racine signe l’autorité intermédiaire, qui signe le certificat du serveur, puis le client valide la chaîne."><rect x="8" y="8" width="744" height="334" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Chaîne de confiance d’un certificat TLS</text><rect class="pki-green" x="28" y="62" width="205" height="66" rx="10"/><text x="130" y="87" text-anchor="middle" class="pki-title">CA racine</text><text x="130" y="108" text-anchor="middle" class="pki-sub">Ancre de confiance locale</text><rect class="pki-blue" x="278" y="62" width="205" height="66" rx="10"/><text x="380" y="87" text-anchor="middle" class="pki-title">CA intermédiaire</text><text x="380" y="108" text-anchor="middle" class="pki-sub">Certificat signé par la racine</text><rect class="pki-amber" x="528" y="62" width="205" height="66" rx="10"/><text x="630" y="87" text-anchor="middle" class="pki-title">Certificat serveur</text><text x="630" y="108" text-anchor="middle" class="pki-sub">Nom : www.exemple.test</text><path class="pki-flow pki-flow-green" d="M233 95 H270"/><path class="pki-flow pki-flow-blue" d="M483 95 H520"/><text x="252" y="148" text-anchor="middle" class="pki-sub">signe</text><text x="505" y="148" text-anchor="middle" class="pki-sub">signe</text><rect class="pki-box" x="110" y="200" width="540" height="88" rx="12"/><text x="380" y="225" text-anchor="middle" class="pki-title">Le client valide la chaîne</text><text x="380" y="247" text-anchor="middle" class="pki-sub">Signatures • dates • nom demandé • usages de clé</text><text x="380" y="267" text-anchor="middle" class="pki-sub">Racine présente dans le magasin de confiance</text><path class="pki-flow pki-flow-amber" d="M630 128 V170 H630 V192"/><path class="pki-flow pki-flow-green" d="M130 128 V170 H130 V192"/><circle class="pki-dot" cx="251" cy="95" r="4" fill="#4ade80"/><circle class="pki-dot pki-dot-delay" cx="501" cy="95" r="4" fill="#60a5fa"/><text x="380" y="319" text-anchor="middle" class="pki-sub">Une chaîne valide ne remplace pas la vérification du nom demandé.</text></svg></div>

La racine est généralement auto-signée et distribuée par un canal de confiance ; elle n’est pas approuvée simplement parce que son certificat s’auto-signe. Le magasin de confiance est ce qui fait du certificat racine une ancre. Les certificats intermédiaires permettent de limiter l’exposition de la racine et de déléguer l’émission. Le serveur transmet habituellement son certificat et les intermédiaires nécessaires ; il n’est généralement pas censé transmettre la racine comme preuve de confiance.

## 3. Anatomie d’un certificat X.509

Un certificat X.509 contient plusieurs champs. Les noms exacts peuvent varier selon l’outil d’inspection, mais les fonctions restent comparables.

| Champ / extension | Utilité | Ce qu’il faut vérifier |
|---|---|---|
| Subject | Identité du sujet, souvent moins déterminante pour le nom DNS moderne | Les attributs de sujet utiles à la politique |
| Subject Public Key Info | Algorithme et clé publique | Taille/type acceptable et compatibilité |
| Issuer | Autorité émettrice | Cohérence avec l’émetteur dans la chaîne |
| Serial Number | Numéro unique dans le contexte de l’émetteur | Utile pour OCSP/CRL et l’inventaire |
| Not Before / Not After | Début et fin de validité | Horloge du client, renouvellement |
| Signature Algorithm | Algorithme de signature du certificat | Algorithme permis par la politique |
| Subject Alternative Name (SAN) | DNS, IP ou autres identités | Présence du nom exact demandé |
| Basic Constraints | Indique si un certificat peut agir comme CA | `CA:TRUE` réservé aux CA selon la politique |
| Key Usage | Usages cryptographiques permis | Usages adaptés à la clé |
| Extended Key Usage (EKU) | Usage applicatif, par exemple serveur TLS | `serverAuth` ou `clientAuth` si requis |
| Authority Key Identifier / Subject Key Identifier | Aide à relier les certificats d’une chaîne | Correspondance entre émetteur et sujet |
| AIA / CRL Distribution Points | Indications sur certificats CA ou statut | Accès réseau et politique de validation |

### SAN plutôt que Common Name

Pour une identité de serveur TLS, les règles modernes de vérification de nom utilisent les identifiants de l’extension **Subject Alternative Name (SAN)**, notamment `dNSName` pour un nom DNS ou `iPAddress` pour une adresse IP. Il ne faut pas compter sur un nom DNS uniquement placé dans le champ Common Name (CN). La RFC 9525 décrit ces règles d’identité de service. [RFC 9525](https://www.rfc-editor.org/rfc/rfc9525.html)

Par exemple, pour visiter `https://vpn.exemple.test`, le client doit trouver une entrée SAN appropriée pour `vpn.exemple.test`. Un certificat pour `www.exemple.test` ne devient pas valide pour `vpn.exemple.test` juste parce que les deux sites sont administrés par la même entreprise.

Un certificat wildcard comme `*.exemple.test` peut couvrir `vpn.exemple.test` selon les règles de correspondance, mais il ne couvre normalement pas `exemple.test` ni `api.dev.exemple.test`. Les règles exactes doivent être vérifiées avec l’application et la politique d’identité.

### Schéma 2 — Les champs du certificat

<div class="pki-diagram"><svg viewBox="0 0 760 370" role="img" aria-label="Carte explicative des champs d’un certificat X.509 : identité SAN, clé publique, émetteur, validité, usages et signature."><rect x="8" y="8" width="744" height="354" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Lecture visuelle d’un certificat X.509</text><rect class="pki-blue" x="28" y="58" width="330" height="74" rx="10"/><text x="45" y="82" class="pki-title">Identité — Subject Alternative Name</text><text x="45" y="104" class="pki-sub">DNS: www.exemple.test</text><text x="45" y="120" class="pki-sub">IP: 192.0.2.20 (si nécessaire)</text><rect class="pki-green" x="390" y="58" width="342" height="74" rx="10"/><text x="408" y="82" class="pki-title">Clé publique</text><text x="408" y="104" class="pki-sub">Algorithme + paramètres + clé</text><text x="408" y="120" class="pki-sub">La clé privée reste sur le serveur</text><rect class="pki-box" x="28" y="155" width="330" height="75" rx="10"/><text x="45" y="180" class="pki-title">Émetteur et numéro de série</text><text x="45" y="202" class="pki-sub">CA émettrice • référence pour révocation</text><text x="45" y="218" class="pki-sub">La chaîne relie chaque signature à son émetteur</text><rect class="pki-amber" x="390" y="155" width="342" height="75" rx="10"/><text x="408" y="180" class="pki-title">Validité temporelle</text><text x="408" y="202" class="pki-sub">Not Before • Not After</text><text x="408" y="218" class="pki-sub">Contrôlée avec l’horloge du client</text><rect class="pki-red" x="28" y="253" width="330" height="75" rx="10"/><text x="45" y="278" class="pki-title">Usages et contraintes</text><text x="45" y="300" class="pki-sub">Key Usage • EKU • Basic Constraints</text><text x="45" y="316" class="pki-sub">Le certificat ne doit être utilisé que dans son rôle</text><rect class="pki-box" x="390" y="253" width="342" height="75" rx="10"/><text x="408" y="278" class="pki-title">Signature de la CA</text><text x="408" y="300" class="pki-sub">Détecte une modification non autorisée</text><text x="408" y="316" class="pki-sub">À vérifier avec la clé publique de l’émetteur</text><path class="pki-flow pki-flow-blue" d="M358 94 H382"/><path class="pki-flow pki-flow-green" d="M561 132 V147"/><path class="pki-flow pki-flow-amber" d="M358 192 H382"/><circle class="pki-dot" cx="370" cy="94" r="3.5" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="561" cy="141" r="3.5" fill="#4ade80"/></svg></div>

## 4. Certificat, clé publique et clé privée : ne pas les confondre

Une clé publique peut être intégrée dans un certificat et communiquée à d’autres systèmes. La clé privée correspondante prouve le contrôle de cette identité lors des opérations cryptographiques, selon le protocole et l’algorithme utilisés. Le serveur doit protéger la clé privée contre la lecture, l’exfiltration et l’utilisation non autorisée.

Un certificat n’est pas une clé privée chiffrée. C’est un objet signé. Un fichier `server.crt` ou `server.pem` contient souvent le certificat public ; un fichier `server.key` contient la clé privée et exige une protection stricte. L’extension du fichier ne suffit toutefois pas à prouver ce qu’il contient : inspecte le format et les permissions.

Le certificat ne chiffre pas tout le trafic applicatif à lui seul. Pendant TLS, les clés et paramètres du canal sont établis selon le protocole. Ensuite, des algorithmes symétriques protègent les données. La signature numérique du certificat permet de vérifier qu’une CA a lié l’identité à la clé publique, et la preuve de possession permet au serveur de montrer qu’il détient la clé privée correspondante.

> **Astuce :** Sépare les chemins et les droits du certificat public et de la clé privée. Le certificat peut souvent être lisible par le processus Web et les outils de supervision ; la clé privée ne doit être accessible qu’au compte ou au composant qui en a réellement besoin.

## 5. Le rôle d’une autorité de certification

La CA applique une politique : qui peut demander quel type de certificat, quelles preuves sont exigées, quels algorithmes et durées sont acceptés, comment les numéros de série sont alloués et comment les certificats sont révoqués. Une CA publique vérifie notamment le contrôle d’un nom de domaine pour des certificats TLS validés par domaine. Une CA privée d’entreprise peut émettre des certificats pour des serveurs internes, des utilisateurs ou des appareils gérés.

Une CA racine doit être protégée particulièrement soigneusement. Dans une architecture d’entreprise, la racine peut être conservée hors ligne et n’être utilisée que pour signer les CA intermédiaires. Une CA intermédiaire en ligne émet les certificats opérationnels. Cette organisation réduit le risque qu’une compromission d’un serveur d’émission permette de signer directement tout type de certificat racine.

### Schéma 3 — Cycle d’émission d’un certificat

<div class="pki-diagram"><svg viewBox="0 0 760 400" role="img" aria-label="Cycle d’émission : le serveur crée une paire de clés et une CSR, l’autorité vérifie la demande, signe puis renvoie le certificat au serveur."><rect x="8" y="8" width="744" height="384" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">De la génération de clé à l’installation</text><rect class="pki-blue" x="28" y="68" width="205" height="75" rx="10"/><text x="130" y="93" text-anchor="middle" class="pki-title">1. Serveur</text><text x="130" y="114" text-anchor="middle" class="pki-sub">Génère la paire de clés</text><text x="130" y="130" text-anchor="middle" class="pki-sub">Privée conservée localement</text><rect class="pki-amber" x="278" y="68" width="205" height="75" rx="10"/><text x="380" y="93" text-anchor="middle" class="pki-title">2. CSR</text><text x="380" y="114" text-anchor="middle" class="pki-sub">Clé publique + noms demandés</text><text x="380" y="130" text-anchor="middle" class="pki-sub">Aucune clé privée dedans</text><rect class="pki-green" x="528" y="68" width="205" height="75" rx="10"/><text x="630" y="93" text-anchor="middle" class="pki-title">3. Autorité</text><text x="630" y="114" text-anchor="middle" class="pki-sub">Vérifie la demande</text><text x="630" y="130" text-anchor="middle" class="pki-sub">Applique sa politique</text><path class="pki-flow pki-flow-blue" d="M233 106 H270"/><path class="pki-flow pki-flow-amber" d="M483 106 H520"/><text x="250" y="162" text-anchor="middle" class="pki-sub">CSR</text><text x="504" y="162" text-anchor="middle" class="pki-sub">validation</text><rect class="pki-green" x="528" y="213" width="205" height="73" rx="10"/><text x="630" y="238" text-anchor="middle" class="pki-title">4. Signature</text><text x="630" y="259" text-anchor="middle" class="pki-sub">Certificat X.509 émis</text><text x="630" y="275" text-anchor="middle" class="pki-sub">Clé publique + identité</text><rect class="pki-blue" x="278" y="213" width="205" height="73" rx="10"/><text x="380" y="238" text-anchor="middle" class="pki-title">5. Installation</text><text x="380" y="259" text-anchor="middle" class="pki-sub">Certificat + intermédiaires</text><text x="380" y="275" text-anchor="middle" class="pki-sub">Référence de clé privée</text><rect class="pki-box" x="28" y="213" width="205" height="73" rx="10"/><text x="130" y="238" text-anchor="middle" class="pki-title">6. Test TLS</text><text x="130" y="259" text-anchor="middle" class="pki-sub">Nom • dates • chaîne</text><text x="130" y="275" text-anchor="middle" class="pki-sub">Service présenté en HTTPS</text><path class="pki-flow pki-flow-green" d="M630 143 V205"/><path class="pki-flow pki-flow-blue" d="M528 249 H490"/><path class="pki-flow pki-flow-green" d="M278 249 H240"/><text x="380" y="326" text-anchor="middle" class="pki-sub">Le fichier de clé privée n’est jamais envoyé à la CA.</text><text x="380" y="347" text-anchor="middle" class="pki-sub">La procédure d’émission, de renouvellement et de révocation doit être documentée.</text><circle class="pki-dot" cx="251" cy="106" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="504" cy="106" r="4" fill="#fbbf24"/><circle class="pki-dot" cx="509" cy="249" r="4" fill="#4ade80"/></svg></div>

## 6. CSR : demander un certificat sans partager le secret

Une **Certificate Signing Request** (CSR), généralement au format PKCS#10, contient la clé publique, un sujet et éventuellement des extensions demandées. La CA vérifie la preuve de contrôle des identités ainsi que la politique d’émission avant de créer le certificat. Les extensions demandées par la CSR ne sont pas automatiquement acceptées : la CA peut les remplacer ou les limiter.

Dans un environnement Web moderne, il faut notamment s’assurer que les DNS attendus sont présents dans SAN. La liste des noms doit être délibérée : un certificat multi-SAN couvre plusieurs identités, mais élargit aussi l’impact potentiel de la compromission de sa clé privée.

## 7. Comment TLS utilise le certificat

À haut niveau, lors d’une connexion HTTPS, le client annonce les versions et capacités qu’il prend en charge. Le serveur choisit des paramètres compatibles et fournit les éléments d’authentification prévus par la version TLS. Le client vérifie le certificat et prouve que la chaîne remonte à une ancre de confiance, que le nom demandé correspond à SAN, que la validité temporelle est correcte et que les usages/algorithmes sont acceptables. La négociation de clés produit ensuite les clés de trafic. Une fois le handshake terminé, les données applicatives circulent dans des enregistrements TLS protégés.

TLS 1.3 et TLS 1.2 n’utilisent pas exactement les mêmes messages et mécanismes. Un diagramme pédagogique qui simplifie les étapes ne doit donc pas être utilisé comme trace exacte de tous les paquets. La version TLS réellement négociée dépend de ce que prennent en charge client, serveur et politique de sécurité.

### Schéma 4 — Handshake TLS et validation de l’identité

<div class="pki-diagram"><svg viewBox="0 0 760 430" role="img" aria-label="Séquence TLS simplifiée : ClientHello, choix du serveur, certificat et preuve de possession, validation côté client, clés de trafic puis données chiffrées."><rect x="8" y="8" width="744" height="414" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Établissement d’une connexion TLS</text><rect class="pki-blue" x="45" y="54" width="230" height="52" rx="9"/><text x="160" y="76" text-anchor="middle" class="pki-title">Client / navigateur</text><text x="160" y="93" text-anchor="middle" class="pki-sub">Vérifie le nom attendu</text><rect class="pki-green" x="485" y="54" width="230" height="52" rx="9"/><text x="600" y="76" text-anchor="middle" class="pki-title">Serveur TLS</text><text x="600" y="93" text-anchor="middle" class="pki-sub">Possède la clé privée</text><path class="pki-flow pki-flow-blue" d="M160 106 V133 H600 V106"/><text x="380" y="126" text-anchor="middle" class="pki-sub">ClientHello → paramètres négociés</text><path class="pki-flow pki-flow-green" d="M600 106 V166 H160 V106" style="stroke-dashoffset:0"/><text x="380" y="158" text-anchor="middle" class="pki-sub">ServerHello + paramètres TLS</text><rect class="pki-amber" x="65" y="184" width="270" height="77" rx="10"/><text x="200" y="208" text-anchor="middle" class="pki-title">Vérification côté client</text><text x="200" y="230" text-anchor="middle" class="pki-sub">Chaîne • dates • SAN • usages</text><text x="200" y="247" text-anchor="middle" class="pki-sub">Ancres de confiance locales</text><rect class="pki-box" x="425" y="184" width="270" height="77" rx="10"/><text x="560" y="208" text-anchor="middle" class="pki-title">Certificat + preuve de possession</text><text x="560" y="230" text-anchor="middle" class="pki-sub">Clé publique et identité certifiées</text><text x="560" y="247" text-anchor="middle" class="pki-sub">Signature vérifiée par le client</text><path class="pki-flow pki-flow-amber" d="M425 222 H344"/><path class="pki-flow pki-flow-blue" d="M200 261 V286 H560 V261"/><text x="380" y="281" text-anchor="middle" class="pki-sub">Accord sur les clés du canal</text><rect class="pki-green" x="180" y="306" width="400" height="66" rx="10"/><text x="380" y="331" text-anchor="middle" class="pki-title">Canal TLS protégé établi</text><text x="380" y="352" text-anchor="middle" class="pki-sub">Confidentialité • intégrité • authentification du serveur</text><path class="pki-flow pki-flow-green" d="M560 261 V291 H580 V306"/><circle class="pki-dot" cx="380" cy="126" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="380" cy="158" r="4" fill="#4ade80"/><text x="380" y="397" text-anchor="middle" class="pki-sub">Le certificat aide à authentifier l’identité ; il ne chiffre pas seul les données applicatives.</text></svg></div>

Une validation réussie donne au client de bonnes raisons de croire qu’il communique avec le serveur correspondant à l’identité demandée et que le canal TLS est protégé. Si le certificat est expiré, auto-signé non approuvé, émis pour un autre nom ou relié à une chaîne non approuvée, le client doit généralement refuser la connexion ou afficher une erreur selon sa politique.

> **Danger :** Ne désactive pas la vérification des certificats pour « faire fonctionner » une application. Des options comme `curl -k`, `--insecure` ou la désactivation de `verify=True` servent seulement à diagnostiquer temporairement un problème dans un environnement contrôlé ; elles suppriment un contrôle de sécurité essentiel.

## 8. Certificats serveur et certificats client

Le cas le plus courant est l’authentification du serveur : un navigateur vérifie `www.exemple.com`. Avec **l’authentification TLS mutuelle** (mTLS), le serveur demande aussi au client un certificat et valide l’identité présentée. Le mTLS peut être utilisé pour des API internes, des communications entre services, des équipements d’administration ou des systèmes industriels.

| Fonction | Certificat serveur | Certificat client |
|---|---|---|
| Qui le présente ? | Serveur | Client lorsque le serveur le demande |
| Qui vérifie ? | Client | Serveur |
| Identité fréquente | Nom DNS du service | Identité machine, service ou utilisateur |
| Usage typique | HTTPS | API mTLS, accès machine-à-machine |
| Erreur courante | SAN ou chaîne incorrecte | CA client absente, EKU ou politique d’identité inadaptée |

Le certificat client ne doit pas être confondu avec une simple connexion nécessitant un nom d’utilisateur et un mot de passe. Le certificat est un moyen d’authentifier une clé et une identité selon une politique ; l’application doit encore associer cette identité à des droits précis.

### Schéma 5 — TLS simple et TLS mutuel

<div class="pki-diagram"><svg viewBox="0 0 760 330" role="img" aria-label="Comparaison entre TLS ordinaire, où le client valide le serveur, et mTLS, où serveur et client présentent chacun un certificat."><rect x="8" y="8" width="744" height="314" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Authentification du serveur et authentification mutuelle</text><rect class="pki-blue" x="30" y="60" width="210" height="58" rx="9"/><text x="135" y="84" text-anchor="middle" class="pki-title">TLS classique</text><text x="135" y="102" text-anchor="middle" class="pki-sub">Le client valide le serveur</text><rect class="pki-green" x="520" y="60" width="210" height="58" rx="9"/><text x="625" y="84" text-anchor="middle" class="pki-title">mTLS</text><text x="625" y="102" text-anchor="middle" class="pki-sub">Les deux côtés s’authentifient</text><rect class="pki-box" x="30" y="151" width="210" height="112" rx="10"/><text x="135" y="177" text-anchor="middle" class="pki-title">Client</text><text x="135" y="199" text-anchor="middle" class="pki-sub">Valide la chaîne</text><text x="135" y="217" text-anchor="middle" class="pki-sub">et le nom du serveur</text><text x="135" y="244" text-anchor="middle" class="pki-sub">Aucun certificat client exigé</text><rect class="pki-box" x="520" y="151" width="210" height="112" rx="10"/><text x="625" y="177" text-anchor="middle" class="pki-title">Serveur</text><text x="625" y="199" text-anchor="middle" class="pki-sub">Valide le certificat client</text><text x="625" y="217" text-anchor="middle" class="pki-sub">selon la CA et la politique</text><text x="625" y="244" text-anchor="middle" class="pki-sub">Associe l’identité aux droits</text><path class="pki-flow pki-flow-blue" d="M240 190 H510"/><path class="pki-flow pki-flow-green" d="M510 218 H240"/><text x="375" y="180" text-anchor="middle" class="pki-sub">certificat serveur</text><text x="375" y="238" text-anchor="middle" class="pki-sub">certificat client en mTLS</text><circle class="pki-dot" cx="375" cy="190" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="375" cy="218" r="4" fill="#4ade80"/><text x="380" y="295" text-anchor="middle" class="pki-sub">mTLS renforce l’authentification mais exige une gestion du cycle de vie des certificats clients.</text></svg></div>

## 9. Durée de validité, renouvellement et révocation

Un certificat ne doit pas être utilisé indéfiniment. Il possède une date de début et une date de fin de validité. Les certificats de serveur modernes sont souvent de durée relativement courte par rapport aux certificats de CA, ce qui réduit la durée d’exposition en cas de problème et pousse à automatiser le renouvellement.

Trois opérations sont à distinguer :

- **Renouvellement** : obtenir un nouveau certificat avant expiration, en conservant ou en remplaçant la paire de clés selon la politique.
- **Révocation** : déclarer qu’un certificat ne doit plus être accepté avant sa date de fin, par exemple après compromission de la clé privée ou erreur d’émission.
- **Expiration** : la période de validité est terminée ; le certificat n’est plus acceptable au-delà de cette période même s’il n’est pas révoqué.

Une CRL (Certificate Revocation List) est une liste signée publiée par l’émetteur. OCSP permet à un client ou à un composant de demander le statut d’un certificat, mais sa disponibilité, le comportement en cas d’échec et les caches dépendent du logiciel et de la politique. La vérification de révocation n’est pas appliquée de manière uniforme par tous les clients TLS. Il faut donc connaître le comportement réel de l’application, au lieu de supposer que la mention OCSP dans un certificat garantit un contrôle parfait dans toutes les connexions. [RFC 6960 / OCSP](https://www.rfc-editor.org/rfc/rfc6960.html)

### Schéma 6 — Cycle de vie du certificat

<div class="pki-diagram"><svg viewBox="0 0 760 360" role="img" aria-label="Cycle de vie : demande, émission, déploiement, surveillance et renouvellement ; incident peut mener à la révocation."><rect x="8" y="8" width="744" height="344" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Cycle de vie et supervision</text><rect class="pki-blue" x="28" y="72" width="155" height="67" rx="10"/><text x="105" y="98" text-anchor="middle" class="pki-title">Demande</text><text x="105" y="119" text-anchor="middle" class="pki-sub">CSR / identité</text><rect class="pki-green" x="213" y="72" width="155" height="67" rx="10"/><text x="290" y="98" text-anchor="middle" class="pki-title">Émission</text><text x="290" y="119" text-anchor="middle" class="pki-sub">CA / signature</text><rect class="pki-blue" x="398" y="72" width="155" height="67" rx="10"/><text x="475" y="98" text-anchor="middle" class="pki-title">Déploiement</text><text x="475" y="119" text-anchor="middle" class="pki-sub">Service / chaîne</text><rect class="pki-amber" x="583" y="72" width="149" height="67" rx="10"/><text x="657" y="98" text-anchor="middle" class="pki-title">Supervision</text><text x="657" y="119" text-anchor="middle" class="pki-sub">Expiration / statut</text><path class="pki-flow pki-flow-blue" d="M183 105 H205"/><path class="pki-flow pki-flow-green" d="M368 105 H390"/><path class="pki-flow pki-flow-amber" d="M553 105 H575"/><path class="pki-flow pki-flow-green pki-flow-slow" d="M657 139 V190 H475 V147"/><text x="566" y="181" text-anchor="middle" class="pki-sub">renouveler avant expiration</text><rect class="pki-red" x="218" y="226" width="320" height="67" rx="10"/><text x="378" y="251" text-anchor="middle" class="pki-title">Incident ou compromission</text><text x="378" y="273" text-anchor="middle" class="pki-sub">Révoquer • remplacer la clé • enquêter</text><path class="pki-flow pki-flow-red" d="M475 139 V207 H538 V240"/><path class="pki-flow pki-flow-red" d="M378 226 V199 H290 V147"/><text x="380" y="323" text-anchor="middle" class="pki-sub">Inventaire, alertes et automatisation évitent les interruptions inattendues.</text><circle class="pki-dot" cx="196" cy="105" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="379" cy="105" r="4" fill="#4ade80"/><circle class="pki-dot" cx="565" cy="105" r="4" fill="#fbbf24"/></svg></div>

Les erreurs de certificat dues à l’expiration sont fréquemment des erreurs d’exploitation plutôt que des défaillances cryptographiques. Une gestion saine exige un inventaire : nom DNS, propriétaire, CA, échéance, emplacement de la clé, service qui l’utilise et procédure de renouvellement.

> **Piège :** Le renouvellement n’est pas terminé lorsque la CA délivre le nouveau certificat. Il faut aussi l’installer, présenter la chaîne correcte, vérifier le nom, tester la négociation TLS et confirmer que le service ne présente plus l’ancien certificat.

## 10. Formats de fichiers de certificats

Les outils utilisent différents encodages et conteneurs. Les extensions de fichiers sont des conventions, pas une preuve absolue du contenu.

| Format | Aspect courant | Contenu / usage |
|---|---|---|
| PEM | Texte avec `-----BEGIN CERTIFICATE-----` | Certificat ou clé encodé en Base64 avec délimiteurs |
| DER | Binaire | Encodage ASN.1 binaire d’un certificat ou d’une clé |
| PKCS#12 (`.p12`, `.pfx`) | Conteneur souvent protégé par mot de passe | Peut réunir certificat, chaîne et clé privée |
| CSR (`.csr`, `.req`) | PEM ou DER | Demande de signature ; contient normalement la clé publique, pas la clé privée |
| Chaîne (`chain.pem`, `fullchain.pem`) | Plusieurs blocs PEM | Certificat serveur suivi des intermédiaires selon l’outil |
| Clé privée (`.key`) | PEM ou autre format | Matériel secret : protection stricte requise |

Ne partage pas le mot de passe d’un conteneur PKCS#12 avec son fichier si ce n’est pas nécessaire. Évite de déposer une clé privée non chiffrée dans un répertoire web, un dépôt Git ou une sauvegarde accessible à des personnes non autorisées.

## 11. Créer une CA locale de laboratoire

Pour apprendre, tu peux créer une petite CA locale dans une machine de laboratoire. Elle ne sera pas automatiquement reconnue par les navigateurs ou les autres appareils. Il faudra installer le certificat racine dans le magasin de confiance des clients concernés, uniquement si tu contrôles cet environnement et que tu comprends l’impact de cette confiance.

L’exemple suivant sert à un **laboratoire isolé**. Il crée une CA de test, puis une clé et une CSR serveur. Les chemins et les durées sont à adapter. Pour une PKI de production, ne réutilise pas ces commandes telles quelles sans concevoir le stockage de clés, les politiques d’émission, les sauvegardes, les journaux et la révocation.

```bash
# 1) Répertoire de laboratoire
mkdir -p ~/pki-lab/{ca,server}
chmod 700 ~/pki-lab
cd ~/pki-lab

# 2) Clé privée de CA de laboratoire : protège ce fichier
openssl genpkey -algorithm RSA \
  -pkeyopt rsa_keygen_bits:3072 \
  -out ca/ca.key
chmod 600 ca/ca.key

# 3) Certificat racine auto-signé pour le labo (5 ans ici, exemple seulement)
openssl req -x509 -new -sha256 \
  -key ca/ca.key \
  -out ca/ca.crt \
  -days 1825 \
  -subj "/CN=SkillTree Lab Root CA"

# 4) Clé privée du serveur
openssl genpkey -algorithm RSA \
  -pkeyopt rsa_keygen_bits:2048 \
  -out server/server.key
chmod 600 server/server.key

# 5) CSR : inclure le nom attendu dans les extensions de demande
openssl req -new -sha256 \
  -key server/server.key \
  -out server/server.csr \
  -subj "/CN=web.lab.test"
```

La CSR ne comprend pas automatiquement toutes les extensions nécessaires à l’usage TLS. Une CA doit imposer une politique pour SAN, Basic Constraints, Key Usage et Extended Key Usage. Pour l’exercice suivant, tu peux d’abord inspecter les objets :

```bash
openssl x509 -in ca/ca.crt -noout -subject -issuer -dates -fingerprint -sha256
openssl req -in server/server.csr -noout -subject -text
openssl pkey -in server/server.key -check -noout
```

**Ne présente pas une CA racine de laboratoire comme une CA publique.** Le but est d’apprendre le format et les contrôles, pas de produire un certificat publiquement approuvé.

## 12. Obtenir et gérer un certificat public

Pour un service accessible publiquement, une CA de confiance publique peut délivrer un certificat à la suite d’une validation des noms. ACME automatise une grande partie de la demande, de la preuve de contrôle de domaine et du renouvellement. Le protocole ACME est spécifié par la RFC 8555. [RFC 8555](https://www.rfc-editor.org/rfc/rfc8555.html)

Les principales méthodes de validation sont :

- **HTTP-01** : l’autorité vérifie une réponse disponible à une URL spécifique du domaine. Il faut que le chemin et le serveur Web soient accessibles comme prévu.
- **DNS-01** : le demandeur publie un enregistrement TXT. Cette méthode convient notamment aux certificats wildcard et aux infrastructures où le service n’est pas directement accessible sur HTTP.
- **TLS-ALPN-01** : validation via une négociation TLS spécifique, si le client et l’autorité la prennent en charge.

Le choix dépend de l’architecture DNS, du pare-feu, de la disponibilité du port nécessaire, du contrôle des API DNS et des besoins d’automatisation. Protéger les identifiants d’API DNS est particulièrement important : une fuite peut permettre de modifier les enregistrements ou d’émettre des certificats pour des domaines gérés par ce compte.

### Schéma 7 — Émission automatisée avec ACME

<div class="pki-diagram"><svg viewBox="0 0 760 335" role="img" aria-label="Client ACME crée une clé et demande un certificat ; CA valide le contrôle du domaine par HTTP ou DNS puis émet le certificat qui est déployé."><rect x="8" y="8" width="744" height="319" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Automatisation ACME : validation avant émission</text><rect class="pki-blue" x="26" y="67" width="200" height="70" rx="10"/><text x="126" y="93" text-anchor="middle" class="pki-title">Client ACME</text><text x="126" y="114" text-anchor="middle" class="pki-sub">Clé • CSR • demande</text><rect class="pki-amber" x="280" y="67" width="200" height="70" rx="10"/><text x="380" y="93" text-anchor="middle" class="pki-title">Validation de domaine</text><text x="380" y="114" text-anchor="middle" class="pki-sub">HTTP-01 / DNS-01</text><rect class="pki-green" x="534" y="67" width="200" height="70" rx="10"/><text x="634" y="93" text-anchor="middle" class="pki-title">Autorité de certification</text><text x="634" y="114" text-anchor="middle" class="pki-sub">Émet après validation</text><path class="pki-flow pki-flow-blue" d="M226 102 H272"/><path class="pki-flow pki-flow-amber" d="M480 102 H526"/><text x="249" y="154" text-anchor="middle" class="pki-sub">demande</text><text x="503" y="154" text-anchor="middle" class="pki-sub">preuve acceptée</text><rect class="pki-box" x="280" y="205" width="200" height="65" rx="10"/><text x="380" y="230" text-anchor="middle" class="pki-title">Installation</text><text x="380" y="251" text-anchor="middle" class="pki-sub">Certificat + chaîne</text><path class="pki-flow pki-flow-green" d="M634 137 V187 H480 V213"/><path class="pki-flow pki-flow-blue" d="M280 237 H226 V180 H126 V145"/><text x="126" y="204" text-anchor="middle" class="pki-sub">Renouvellement automatisé</text><text x="380" y="301" text-anchor="middle" class="pki-sub">Une tâche périodique doit confirmer le succès du renouvellement, pas seulement son lancement.</text><circle class="pki-dot" cx="249" cy="102" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="503" cy="102" r="4" fill="#fbbf24"/><circle class="pki-dot" cx="557" cy="187" r="4" fill="#4ade80"/></svg></div>

L’automatisation doit inclure une notification d’échec, une supervision des dates et un test post-déploiement. La bonne mesure opérationnelle est « le nouveau certificat est installé et présenté par le service », pas uniquement « la commande ACME a été exécutée ».

## 13. Vérifier un certificat et un service HTTPS

Avant de modifier un certificat en production, inspecte le certificat actuel, le nom présenté par le service, la chaîne intermédiaire et les dates. Les commandes suivantes sont destinées au diagnostic ; certaines options peuvent varier selon la version OpenSSL.

```bash
# Lister le sujet, l'émetteur, les dates et le SAN d'un certificat PEM
openssl x509 -in server.crt -noout \
  -subject -issuer -dates -ext subjectAltName

# Afficher les usages et contraintes disponibles
openssl x509 -in server.crt -noout -text

# Vérifier une chaîne locale avec la racine et les intermédiaires appropriés
openssl verify -CAfile root-ca.pem \
  -untrusted intermediates.pem server.crt
```

Pour observer ce que présente un service, tu peux utiliser :

```bash
# Demander l'identité attendue et récupérer le certificat présenté
openssl s_client -connect www.exemple.com:443 \
  -servername www.exemple.com -showcerts </dev/null

# Faire une requête HTTPS en conservant la validation standard
curl -v https://www.exemple.com/
```

La sortie de `openssl s_client` montre les éléments reçus par l’outil et les informations de négociation. Elle ne remplace pas une validation par l’application réelle : le magasin de confiance, les contraintes propres au logiciel, les proxies et la configuration du client peuvent différer. L’option `-servername` envoie le SNI attendu ; sans SNI, un serveur hébergeant plusieurs sites peut présenter un autre certificat.

## 14. Diagnostiquer les erreurs fréquentes

| Symptôme | Causes fréquentes | Vérifications initiales |
|---|---|---|
| `certificate has expired` | Certificat expiré, horloge incorrecte, mauvais nœud derrière un répartiteur | Contrôler `notAfter`, NTP, tous les backends |
| `hostname mismatch` | SAN absent ou incorrect, SNI absent, mauvais certificat par défaut | Vérifier SAN et nom réellement demandé |
| `unable to get local issuer certificate` | Intermédiaire manquant ou magasin de confiance incomplet | Contrôler la chaîne transmise et le magasin du client |
| `self signed certificate` | Certificat non approuvé ou chaîne privée absente | Installer l’ancre privée via une procédure approuvée |
| `certificate revoked` | Statut de révocation confirmé | Suspendre l’usage, investiguer et réémettre |
| `wrong key` ou clé non correspondante | Certificat et clé provenant de demandes différentes | Comparer les clés publiques dérivées et retrouver l’association correcte |
| `unsupported certificate` | Type de certificat, algorithme, usage ou politique non accepté | Examiner la version TLS et la politique cryptographique |
| Fonctionne sur une machine mais pas une autre | Magasins de confiance, heure, proxy TLS, version logicielle différents | Comparer environnements, journaux et chaîne reçue |
| Échec après renouvellement | Mauvais chemin, reload non effectué, intermédiaire oublié | Contrôler le processus qui sert TLS et retester chaque endpoint |

### Arbre de dépannage

<div class="pki-diagram"><svg viewBox="0 0 760 440" role="img" aria-label="Arbre de dépannage TLS : vérifier l’heure, le nom SAN, la chaîne de confiance et les dates, puis usages et négociation TLS."><rect x="8" y="8" width="744" height="424" rx="14" fill="#090d14" stroke="#334155"/><text x="28" y="35" class="pki-title">Arbre de diagnostic d’un certificat TLS</text><rect class="pki-blue" x="225" y="55" width="310" height="53" rx="10"/><text x="380" y="77" text-anchor="middle" class="pki-title">Connexion TLS échoue</text><text x="380" y="95" text-anchor="middle" class="pki-sub">Collecter erreur + certificat présenté</text><path class="pki-flow pki-flow-blue" d="M380 108 V133"/><rect class="pki-box" x="230" y="135" width="300" height="50" rx="9"/><text x="380" y="156" text-anchor="middle" class="pki-title">L’horloge est-elle correcte ?</text><text x="380" y="173" text-anchor="middle" class="pki-sub">NTP • Not Before • Not After</text><path class="pki-flow pki-flow-red" d="M230 160 H95 V211"/><text x="119" y="151" class="pki-sub">Non</text><rect class="pki-red" x="25" y="213" width="140" height="54" rx="9"/><text x="95" y="235" text-anchor="middle" class="pki-title">Corriger l’heure</text><text x="95" y="253" text-anchor="middle" class="pki-sub">ou renouveler</text><path class="pki-flow pki-flow-green" d="M380 185 V207"/><text x="394" y="201" class="pki-sub">Oui</text><rect class="pki-box" x="230" y="209" width="300" height="55" rx="9"/><text x="380" y="231" text-anchor="middle" class="pki-title">Le SAN correspond-il au nom ?</text><text x="380" y="250" text-anchor="middle" class="pki-sub">SNI • DNS • IP demandée</text><path class="pki-flow pki-flow-red" d="M530 235 H660 V290"/><text x="577" y="226" class="pki-sub">Non</text><rect class="pki-red" x="580" y="292" width="150" height="55" rx="9"/><text x="655" y="314" text-anchor="middle" class="pki-title">Corriger SAN/SNI</text><text x="655" y="333" text-anchor="middle" class="pki-sub">ou routage du nom</text><path class="pki-flow pki-flow-green" d="M380 264 V285"/><text x="394" y="280" class="pki-sub">Oui</text><rect class="pki-box" x="230" y="287" width="300" height="55" rx="9"/><text x="380" y="309" text-anchor="middle" class="pki-title">La chaîne est-elle approuvée ?</text><text x="380" y="328" text-anchor="middle" class="pki-sub">Intermédiaires • magasin de confiance</text><path class="pki-flow pki-flow-red" d="M230 315 H95 V348"/><rect class="pki-red" x="25" y="350" width="140" height="52" rx="9"/><text x="95" y="372" text-anchor="middle" class="pki-title">Réparer la chaîne</text><text x="95" y="389" text-anchor="middle" class="pki-sub">ou confiance</text><path class="pki-flow pki-flow-green" d="M380 342 V365"/><rect class="pki-green" x="230" y="367" width="300" height="42" rx="9"/><text x="380" y="393" text-anchor="middle" class="pki-title">Vérifier usages, algorithmes et version TLS</text><circle class="pki-dot" cx="380" cy="121" r="4" fill="#60a5fa"/><circle class="pki-dot pki-dot-delay" cx="380" cy="198" r="4" fill="#4ade80"/><circle class="pki-dot" cx="380" cy="276" r="4" fill="#4ade80"/></svg></div>

La méthode recommandée consiste à identifier le premier contrôle qui échoue. Il est inutile de renouveler le certificat si la cause est une horloge incorrecte ou un SNI manquant. Inversement, un certificat renouvelé ne corrigera pas un intermédiaire oublié ou un service qui continue à servir une ancienne configuration.

> **Astuce :** Compare le certificat vu à travers le répartiteur de charge à celui de chaque serveur en amont. Un renouvellement réussi sur un seul nœud peut laisser une partie des utilisateurs exposée à l’ancien certificat.

## 15. Sécuriser les clés privées et la chaîne de confiance

La plupart des incidents importants de PKI ne proviennent pas d’une faiblesse mathématique de l’algorithme : ils sont dus à la fuite d’une clé, à une mauvaise attribution de nom, à une CA trop puissante, à des permissions excessives, à une expiration ignorée ou à une validation désactivée.

Bonnes pratiques de base :

- protéger les clés privées par les permissions du système, un secret manager ou un HSM lorsque le niveau de risque le justifie ;
- séparer les rôles d’émission et de validation, et limiter les noms/usages qu’une CA peut signer ;
- conserver des inventaires et surveiller les échéances, avec des alertes avant expiration ;
- documenter la procédure de remplacement et de révocation d’une clé compromise ;
- minimiser les exports de clés et ne jamais journaliser les secrets ;
- utiliser TLS moderne et désactiver SSL et les versions TLS obsolètes selon la politique de sécurité ;
- ne jamais ajouter une CA inconnue à un magasin de confiance pour contourner une erreur ;
- tester les renouvellements et rotations sur un environnement de préproduction ;
- garder des sauvegardes protégées de la configuration et prévoir comment reconstruire une CA si nécessaire.

Une clé exportée doit être considérée comme un actif sensible. Si une clé privée serveur est compromise, révoquer le certificat peut être nécessaire, mais la réponse doit aussi supprimer ou isoler les copies de clé, identifier les systèmes qui l’utilisent et émettre un remplacement avec une nouvelle paire de clés lorsque la politique le recommande.

## 16. Laboratoire guidé : vérifier le certificat d’un site

**Objectif :** savoir retrouver l’identité, l’émetteur, les dates, la chaîne et la version TLS d’un service sans désactiver la validation.

### Étape A — Vérifier le certificat présenté

```bash
openssl s_client -connect www.example.com:443 \
  -servername www.example.com -showcerts </dev/null
```

Remplace `www.example.com` par un nom que tu es autorisé à tester. Observe :
- la version et la suite cryptographique négociées ;
- le certificat serveur et les éventuels intermédiaires transmis ;
- le résultat de la vérification de la chaîne ;
- les alertes ou erreurs éventuelles.

Les sorties exactes varient selon les versions OpenSSL et les bibliothèques du système.

### Étape B — Inspecter le SAN et les dates

Enregistre uniquement le certificat public dans un fichier au format PEM si nécessaire, puis exécute :

```bash
openssl x509 -in server.crt -noout \
  -subject -issuer -dates -ext subjectAltName
```

Réponds aux questions suivantes :
1. Le nom d’hôte testé figure-t-il dans SAN ?
2. Le certificat est-il actuellement dans sa période de validité ?
3. Quel est l’émetteur ?
4. Le serveur a-t-il transmis les certificats intermédiaires utiles ?
5. Le client possède-t-il l’ancre de confiance qui permet de valider la chaîne ?

### Étape C — Tester la validation applicative

```bash
curl -v https://www.example.com/
```

Ne rajoute pas `-k` ou `--insecure`. Si la commande échoue, relève l’erreur puis formule une hypothèse. Les causes possibles incluent une date erronée, un SAN incompatible, une chaîne incomplète, un proxy intermédiaire ou une politique locale.

### Étape D — Rédiger une conclusion

La conclusion doit séparer les faits observés des hypothèses. Exemple : « Le certificat présenté contient `www.example.com` dans SAN et n’est pas expiré ; la validation échoue car le client ne trouve pas l’émetteur intermédiaire ». Ce diagnostic est plus utile que « HTTPS ne marche pas ».

## 17. Questions de révision avec corrigés

**1. Quelle est la différence entre une clé privée et un certificat ?**  
La clé privée est le secret utilisé par le propriétaire pour prouver le contrôle d’une clé ou réaliser des opérations cryptographiques. Le certificat est un objet public signé qui lie une clé publique à une identité et à des usages.

**2. Pourquoi faut-il vérifier SAN ?**  
Parce que la connexion doit authentifier le nom de service réellement demandé. Une chaîne signée valide ne suffit pas si le certificat désigne un autre serveur.

**3. Une CA auto-signée est-elle automatiquement approuvée ?**  
Non. L’approbation vient de son installation comme ancre de confiance par une procédure fiable, pas du fait qu’elle s’auto-signe.

**4. Que se passe-t-il si un certificat expire ?**  
Les clients qui appliquent la validation habituelle rejettent la connexion ou avertissent l’utilisateur. Le renouvellement et le rechargement du service doivent être planifiés avant l’échéance.

**5. À quoi sert une CSR ?**  
À demander un certificat. Elle transmet une clé publique et des attributs demandés ; elle ne doit pas contenir la clé privée correspondante.

**6. À quoi sert mTLS ?**  
À authentifier le client par certificat en plus de l’authentification du serveur, pour les usages où le service doit vérifier l’identité cryptographique de son client.

**7. Quelle différence entre CRL et OCSP ?**  
Une CRL est une liste de certificats révoqués publiée par une CA. OCSP est un protocole de demande du statut d’un certificat. Leur utilisation effective dépend de la politique et du client.

**8. Pourquoi SSL doit-il être désactivé ?**  
SSL est obsolète. Les systèmes modernes doivent utiliser des versions TLS acceptées par leur politique de sécurité et leurs contraintes de compatibilité.

**9. Pourquoi ne pas désactiver la validation pour corriger une erreur ?**  
Parce que cela supprime la vérification de l’identité, facilitant les attaques de l’homme du milieu. Il faut réparer la cause réelle.

**10. Que faut-il vérifier après un renouvellement ?**  
Le certificat est installé, la chaîne intermédiaire est correcte, le nom demandé correspond à SAN, le service a rechargé sa configuration et tous les nœuds présentent le nouveau certificat.

## Points à retenir

- Une PKI organise la confiance entre identités, clés publiques, autorités de certification et clients qui valident les certificats.
- La clé privée doit rester secrète ; le certificat et la CSR peuvent être transmis selon le processus.
- Un client doit vérifier la chaîne, la période de validité, le nom dans SAN, les usages et les paramètres cryptographiques.
- TLS assure le canal sécurisé ; le certificat participe à l’authentification mais n’est pas à lui seul le mécanisme de chiffrement des données.
- Les certificats doivent être inventoriés, renouvelés, contrôlés et révoqués selon une procédure.
- L’automatisation ACME aide à gérer le cycle de vie, mais doit être accompagnée de supervision et de tests après déploiement.
- Ne désactive jamais la validation TLS comme solution permanente.

## Références techniques

1. **RFC 5280** — Internet X.509 Public Key Infrastructure Certificate and CRL Profile. https://www.rfc-editor.org/rfc/rfc5280.html
2. **RFC 9846** — The Transport Layer Security (TLS) Protocol Version 1.3 (juillet 2026). https://www.rfc-editor.org/rfc/rfc9846.html
3. **RFC 9525** — Service Identity in TLS. https://www.rfc-editor.org/rfc/rfc9525.html
4. **RFC 6960** — Online Certificate Status Protocol (OCSP), à lire avec ses mises à jour référencées par l’IETF. https://www.rfc-editor.org/rfc/rfc6960.html
5. **RFC 8555** — Automatic Certificate Management Environment (ACME). https://www.rfc-editor.org/rfc/rfc8555.html
6. **OpenSSL Documentation** — commandes `req`, `x509`, `verify` et `s_client`. https://docs.openssl.org/
7. **Let’s Encrypt Documentation** — automatisation de certificats et validation de domaine. https://letsencrypt.org/docs/
