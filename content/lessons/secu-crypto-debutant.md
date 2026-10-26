# Cryptographie

> **Encadré de mise en contexte**
>
> Une plateforme de formation doit protéger les comptes, transmettre des données privées, vérifier les fichiers de mise à jour et éviter qu'un vol de base de données révèle immédiatement les mots de passe. Ces besoins sont différents. Le chiffrement rend les données illisibles sans la clé appropriée ; le hachage calcule une empreinte ; une signature numérique contribue à vérifier l'intégrité et l'origine cryptographique ; le stockage des mots de passe repose sur des mécanismes spécialisés.
>
> Ce cours introduit la cryptographie par ses usages, ses limites et ses erreurs courantes. L'objectif est de comprendre quel mécanisme correspond à quel problème, sans inventer d'algorithmes ni improviser la gestion des clés.

## 1. Qu'est-ce que la cryptographie ?

La cryptographie utilise des méthodes mathématiques et informatiques pour protéger les informations et fournir certains services de sécurité. Elle intervient dans HTTPS, les applications bancaires, les réseaux privés virtuels, le chiffrement des disques, les sauvegardes et les signatures de logiciels.

Elle peut contribuer à la confidentialité, à l'intégrité et à l'authenticité selon le mécanisme. Elle ne remplace pas les permissions, la supervision ou les procédures de récupération. Une donnée chiffrée peut rester exposée si l'application la déchiffre pour un utilisateur qui ne devrait pas la recevoir. Une clé perdue peut rendre les données irrécupérables. Un fichier signé n'est pas automatiquement confidentiel.

La sécurité ne doit pas reposer sur le secret du nom de l'algorithme. Les mécanismes modernes sont étudiés publiquement ; la clé et la manière dont le mécanisme est appliqué jouent un rôle essentiel. Il faut privilégier des algorithmes reconnus, des bibliothèques maintenues et des protocoles conçus pour le besoin réel.

## 2. Vocabulaire fondamental

Le **texte en clair** désigne le contenu sous sa forme exploitable avant chiffrement. Il peut s'agir d'un texte, d'une image, d'un fichier ou d'une base de données.

Le **texte chiffré** est le résultat d'une opération de chiffrement. Il nécessite les éléments appropriés pour retrouver le contenu. Un **algorithme cryptographique** définit les règles de l'opération ; une **clé cryptographique** est une donnée utilisée par le mécanisme.

Le **chiffrement** transforme les données et le **déchiffrement** permet à un destinataire autorisé de retrouver le contenu avec la clé appropriée. Le **hachage** produit une empreinte de taille déterminée. La **signature numérique** permet de vérifier une signature associée à un contenu. Le **certificat numérique** associe une clé publique à une identité ou un nom selon des règles de confiance.

Ces termes ne sont pas interchangeables. Il faut définir l'objectif avant de choisir le mécanisme.

## 3. Encodage, obfuscation et chiffrement

L'encodage transforme des données pour les représenter dans un format donné. Base64 permet de représenter certaines données binaires sous forme de caractères. Il ne protège pas la confidentialité : toute personne connaissant Base64 peut décoder la valeur sans secret.

L'obfuscation cherche à rendre un programme ou un contenu moins immédiatement lisible. Elle peut compliquer une analyse superficielle, mais ne fournit pas à elle seule les garanties d'une construction cryptographique reconnue.

Le chiffrement utilise un algorithme et une clé pour protéger le contenu. Il doit être utilisé avec une gestion sûre des clés, des paramètres adaptés et des contrôles d'accès cohérents. Il ne faut jamais protéger un mot de passe en le plaçant simplement en Base64, en changeant son nom ou en le transformant à l'aide d'une substitution inventée.

## 4. Chiffrement symétrique

Le chiffrement symétrique utilise un secret commun pour chiffrer et déchiffrer. Il est généralement efficace pour traiter de grandes quantités de données et sert notamment à protéger les fichiers, les disques et les données de session.

Alice peut chiffrer un document avec une clé secrète, transmettre le texte chiffré à Bob, puis Bob utilise la même clé pour retrouver le contenu. La difficulté consiste à faire parvenir la clé à Bob de manière sûre. Si la clé est envoyée par le même canal non protégé que le document, un tiers peut obtenir les deux éléments.

AES, l'Advanced Encryption Standard, est un algorithme symétrique normalisé par le NIST. Il utilise des blocs de 128 bits et accepte des clés de 128, 192 ou 256 bits. Les noms AES-128 et AES-256 décrivent la taille de la clé. La sécurité dépend aussi du mode, des paramètres, de la qualité de la clé et de sa gestion. Référence : NIST FIPS 197, https://csrc.nist.gov/pubs/fips/197/final.

Il ne faut pas inventer son propre algorithme. Une substitution de lettres ou une combinaison improvisée peut sembler difficile à lire mais se casse souvent facilement. Les mécanismes reconnus bénéficient d'une analyse publique beaucoup plus approfondie.

## 5. Modes de chiffrement et authenticité

Un algorithme par blocs doit être utilisé dans un mode adapté au contenu. Les modes ont des propriétés différentes. Certains apportent principalement de la confidentialité sans garantir l'intégrité ou l'authenticité.

AES-GCM est un mode de chiffrement authentifié. Il permet au destinataire de détecter certaines modifications du contenu et des paramètres associés. La sécurité exige une utilisation correcte, notamment le respect des règles de génération et de non-réutilisation du nonce avec une même clé.

Un nonce est une valeur utilisée une fois dans un contexte défini par le mécanisme ; il n'est pas nécessairement secret. Il faut suivre les exigences du mode et laisser la bibliothèque gérer les paramètres lorsque cela est possible. Le mode ECB ne convient pas au chiffrement général de données sensibles, car il peut révéler certaines structures répétitives.

Évite de combiner toi-même des primitives si tu ne maîtrises pas précisément les garanties qu'elles fournissent. Une bibliothèque reconnue et une construction documentée sont préférables à une solution artisanale.

## 6. Cryptographie asymétrique

La cryptographie asymétrique utilise une paire de clés associées : une clé publique et une clé privée. La clé publique peut être communiquée, alors que la clé privée doit rester protégée.

Selon l'algorithme, les mécanismes asymétriques peuvent servir au chiffrement, à l'établissement de secrets ou aux signatures numériques. Ces usages ne sont pas tous interchangeables. RSA et certaines constructions à courbes elliptiques sont des familles connues ; le choix des algorithmes et paramètres doit suivre les recommandations actuelles et les exigences du système.

La clé publique doit être reliée à la bonne identité. Si Alice reçoit une clé publique appartenant à un imposteur qui prétend être Bob, elle risque de protéger son message pour la mauvaise personne. Le mécanisme cryptographique peut fonctionner correctement tout en protégeant le message pour un attaquant.

La clé privée n'est pas le mot de passe du compte. Elle peut être stockée dans un fichier ou un composant matériel et être protégée par un autre mécanisme. Si elle est compromise, il peut être nécessaire de la révoquer ou de la remplacer selon son usage.

## 7. Chiffrement hybride et HTTPS

Le chiffrement symétrique est efficace pour de grands volumes de données, tandis que les mécanismes asymétriques aident à l'établissement de clés et à certains contrôles d'identité. Les systèmes modernes combinent souvent ces familles.

Dans une architecture hybride, les participants établissent ou protègent un secret de session, dérivent une clé symétrique et utilisent ensuite un mécanisme adapté pour protéger les données. Les protocoles réels comportent des négociations, des vérifications d'identité et des protections supplémentaires.

HTTPS utilise TLS pour protéger les communications entre un navigateur et un serveur. Une connexion correctement configurée contribue à la confidentialité et à l'intégrité des échanges en transit. Le navigateur vérifie le certificat du serveur selon une chaîne de confiance et le nom demandé.

La présence d'un cadenas ne garantit pas que le site est honnête ou exempt de vulnérabilités. Un site frauduleux peut obtenir un certificat valide pour son propre domaine. Il faut donc vérifier le nom du domaine et la légitimité du service, surtout avant de saisir des identifiants.

## 8. Hachage et empreintes

Une fonction de hachage transforme des données de taille variable en une empreinte de taille déterminée. SHA-256 produit une empreinte de 256 bits. La fonction est conçue pour rendre difficiles certaines opérations, notamment la recherche d'un contenu correspondant à une empreinte ou la recherche d'une collision utile.

Une empreinte permet de comparer des contenus. Si un fichier change, son empreinte devrait généralement changer. Cependant, le hachage seul n'empêche pas une modification et n'authentifie pas automatiquement l'auteur.

Sous Windows PowerShell :

~~~powershell
Get-FileHash .\document.txt -Algorithm SHA256
~~~

Sous Linux :

~~~bash
sha256sum document.txt
~~~

Pour vérifier un téléchargement, compare l'empreinte calculée à une référence obtenue par un canal fiable. Si un attaquant peut remplacer le fichier et la référence ensemble, la vérification est insuffisante. Une signature numérique peut apporter une garantie différente si la clé publique est elle-même digne de confiance.

## 9. Stockage sécurisé des mots de passe

Une application ne doit généralement pas conserver les mots de passe en clair. Si un attaquant vole la base, les secrets ne devraient pas être directement utilisables.

Le stockage des mots de passe utilise des fonctions spécialisées, par exemple Argon2id, scrypt, bcrypt ou PBKDF2, selon les bibliothèques et recommandations actuelles. Ces méthodes sont conçues pour rendre les essais de mots de passe candidats plus coûteux que des fonctions de hachage très rapides.

Un **sel**, ou salt, est une valeur associée au traitement d'un mot de passe. Il n'est pas nécessairement secret. Il aide notamment à empêcher que deux comptes ayant le même mot de passe produisent systématiquement la même valeur dans le même schéma de stockage et réduit l'intérêt de certaines tables précomputées.

SHA-256 seul n'est pas le mécanisme recommandé pour stocker les mots de passe : il est conçu pour être rapide. Il faut utiliser une bibliothèque reconnue et respecter ses recommandations. Voir l'OWASP Password Storage Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html.

## 10. Signatures numériques

Une signature numérique utilise un mécanisme cryptographique pour permettre la vérification d'une signature associée à un contenu. Le signataire utilise une clé privée ; le destinataire utilise la clé publique correspondante.

La signature peut aider à détecter une modification du contenu et à vérifier que la signature correspond à la clé privée associée. Elle ne prouve pas automatiquement que le document est vrai ou raisonnable et ne garantit pas la confidentialité. Un fichier signé mais non chiffré peut toujours être lu par toute personne qui y a accès.

Il faut vérifier que la clé publique appartient à la personne ou à l'organisation attendue. Une signature vérifiée avec une clé fournie par un attaquant établit une relation cryptographique avec cette clé, pas nécessairement l'identité revendiquée.

Référence : NIST FIPS 186-5, Digital Signature Standard, https://csrc.nist.gov/pubs/fips/186-5/final.

## 11. Certificats et autorités de certification

Un certificat numérique associe une clé publique à un nom ou à une identité selon un processus de confiance. Dans le Web, un certificat TLS aide le navigateur à vérifier que la clé publique présentée est associée au nom de serveur visité.

Une autorité de certification émet ou signe des certificats. Le client vérifie que la chaîne mène à une autorité de confiance, que le nom attendu correspond et que les règles de validation pertinentes sont respectées.

Un certificat expiré, révoqué ou associé à un autre nom peut déclencher un avertissement. Il ne faut pas ignorer l'avertissement sans comprendre sa cause. Un certificat public peut être distribué ; la clé privée associée doit rester protégée.

## 12. Gestion des clés

La sécurité cryptographique dépend de la génération, du stockage, de la distribution, de l'accès, de la rotation et de la destruction contrôlée des clés.

Les clés doivent être générées avec des mécanismes cryptographiquement sûrs, pas à partir d'un nom, d'une date ou d'une phrase prévisible. Les clés ne doivent pas être intégrées au code source, aux journaux ou à des dépôts partagés. Il faut limiter les accès et documenter les usages.

Une clé perdue peut rendre des données irrécupérables. Il faut donc prévoir une stratégie de récupération lorsque le besoin le justifie, tout en protégeant la procédure de secours. La sauvegarde d'un fichier chiffré n'est pas suffisante si la clé nécessaire au déchiffrement est définitivement perdue.

Le NIST fournit des recommandations dans la série SP 800-57 : https://csrc.nist.gov/Projects/Key-Management/Key-Management-Guidelines.

## 13. Aléatoire et évolution des algorithmes

Les clés, nonces et jetons nécessitent parfois des valeurs imprévisibles. Une valeur construite à partir de l'heure, du nom de l'utilisateur ou d'un compteur simple peut être devinée. Il faut utiliser les générateurs cryptographiquement sûrs du système ou de bibliothèques reconnues.

Les algorithmes évoluent avec les capacités de calcul et les connaissances des attaquants. La cryptographie post-quantique étudie des mécanismes conçus pour résister à certaines attaques de futurs ordinateurs quantiques. Le NIST a publié FIPS 203 pour ML-KEM, un mécanisme d'encapsulation de clé destiné à établir un secret partagé ; il ne remplace pas directement un chiffrement de fichier tel qu'AES. Référence : https://csrc.nist.gov/pubs/fips/203/final.

Pour un débutant, l'essentiel est de suivre des recommandations actuelles, maintenir les bibliothèques et prévoir une migration lorsque les standards évoluent, plutôt que de figer un mécanisme sans tenir compte de la durée de protection requise.

## 14. TP : chiffrement authentifié avec Python

Utilise un environnement local que tu contrôles. Installe la bibliothèque :

~~~bash
python -m pip install cryptography
~~~

Le programme suivant chiffre et déchiffre un message de démonstration en mémoire :

~~~python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
cipher = AESGCM(key)
nonce = os.urandom(12)
message = b"Document confidentiel de demonstration"
associated_data = b"cours-cybersecurite-v1"

ciphertext = cipher.encrypt(nonce, message, associated_data)
recovered = cipher.decrypt(nonce, ciphertext, associated_data)

assert recovered == message
print("Verification : OK")
print("Donnees chiffrees :", ciphertext.hex())
~~~

La bibliothèque génère une clé et le programme génère un nonce. AES-GCM chiffre les données et fournit une vérification d'authenticité. Ce programme est une démonstration, pas un système de stockage prêt pour la production : la clé est perdue à la fin de l'exécution, car aucun mécanisme de gestion des clés n'est prévu.

Pour une application réelle, il faut concevoir la protection et la récupération de la clé, le format de stockage et les procédures de rotation. Une expérience contrôlée peut modifier un octet du texte chiffré et vérifier que le déchiffrement échoue. N'accepte jamais des données qui n'ont pas passé la validation d'authenticité.

## 15. TP : comparer des empreintes

Avec Python :

~~~python
import hashlib

message = b"Premier message de test"
print(hashlib.sha256(message).hexdigest())

message = b"Message de test modifie"
print(hashlib.sha256(message).hexdigest())
~~~

Les deux empreintes devraient différer. Cette expérience montre que l'empreinte dépend du contenu. Elle ne prouve pas l'identité de l'auteur, la confidentialité du fichier ni la fiabilité d'une référence placée au même endroit que le fichier.

## 16. Étude de cas : NovaLearn

NovaLearn conserve les informations personnelles, gère les comptes et distribue des fichiers de mise à jour. Pour les communications, le service doit utiliser TLS configuré correctement et protéger la clé privée du serveur. Pour les données stockées, il faut déterminer lesquelles nécessitent un chiffrement au repos et contrôler les permissions. Les mots de passe doivent utiliser une fonction spécialisée.

Pour vérifier les fichiers de mise à jour, le système peut vérifier une signature liée à une clé publique de confiance. Une empreinte peut être utile si la référence provient d'un canal fiable. Les clés doivent être documentées, protégées et remplaçables. Les procédures de récupération doivent être testées.

Cette stratégie reste incomplète sans contrôle d'accès, journalisation, sauvegardes et processus d'incident. La cryptographie s'intègre dans une architecture de sécurité ; elle ne remplace pas les autres contrôles.

## 17. Exercices corrigés

**Exercice 1.** Base64 est-il du chiffrement ?

**Correction :** non, c'est un encodage réversible sans clé secrète.

**Exercice 2.** Dans une paire asymétrique, quelle clé doit rester secrète ?

**Correction :** la clé privée. La clé publique peut être diffusée, mais son association à l'identité attendue doit être vérifiée.

**Exercice 3.** Pourquoi SHA-256 seul n'est-il pas recommandé pour les mots de passe ?

**Correction :** il est rapide et facilite les essais massifs. Le stockage des mots de passe doit employer une fonction spécialisée.

**Exercice 4.** Un fichier signé est-il forcément confidentiel ?

**Correction :** non, la signature aide à vérifier l'intégrité et l'origine cryptographique mais ne cache pas le contenu.

**Exercice 5.** Que faire si une clé privée est compromise ?

**Correction :** évaluer son rôle, la révoquer ou la remplacer selon le mécanisme, examiner les traces et actualiser les systèmes concernés.

**Exercice 6.** Une empreinte vient de la même source inconnue que le fichier. Le fichier est-il garanti authentique ?

**Correction :** non, la référence doit provenir d'un canal fiable ou la signature doit être vérifiée avec une clé de confiance.

## 18. Défi final : concevoir une stratégie cryptographique

NovaLearn doit protéger les données personnelles, sécuriser les communications, stocker correctement les mots de passe, vérifier les mises à jour et pouvoir récupérer les données après un incident.

Le plan doit préciser, pour chaque besoin, l'objectif, le mécanisme choisi, la gestion de la clé ou de la référence de confiance, les limites et le test de vérification.

**Correction indicative.** Les données en transit sont protégées avec TLS correctement configuré. Les données stockées peuvent nécessiter un chiffrement au repos et des clés gérées séparément. Les mots de passe utilisent une fonction spécialisée. Les mises à jour sont vérifiées par signature ou par empreinte de source fiable. Les clés sont générées par des mécanismes sûrs, protégées, documentées et remplaçables. La récupération est testée pour éviter une perte définitive.

Les vérifications doivent être périodiques. Une configuration correcte aujourd'hui peut devenir insuffisante lorsque les recommandations, bibliothèques ou menaces évoluent.

## 19. Glossaire et ressources

**AES :** algorithme de chiffrement symétrique normalisé.  
**Certificat :** document numérique associant une clé publique à un nom ou une identité selon des règles de confiance.  
**Chiffrement :** protection du contenu en le rendant illisible sans les éléments nécessaires.  
**Clé privée :** partie secrète d'une paire de clés asymétriques.  
**Clé publique :** partie partageable d'une paire asymétrique, dont l'identité doit être vérifiée.  
**Encodage :** représentation des données dans un format, sans confidentialité automatique.  
**Hachage :** calcul d'une empreinte de longueur déterminée.  
**Nonce :** valeur utilisée selon les exigences d'un mécanisme cryptographique.  
**Signature numérique :** signature vérifiable associée à un contenu.  
**TLS :** protocole permettant de protéger les communications.  
**Chiffrement authentifié :** construction associant confidentialité et vérification d'authenticité.  
**Sel :** valeur associée au traitement des mots de passe pour limiter certains types d'attaques.

Ressources : NIST AES FIPS 197, https://csrc.nist.gov/pubs/fips/197/final ; NIST Digital Signature Standard, https://csrc.nist.gov/pubs/fips/186-5/final ; NIST Key Management, https://csrc.nist.gov/Projects/Key-Management/Key-Management-Guidelines ; OWASP Cryptographic Storage Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html ; OWASP Password Storage Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

## 20. Dossiers pratiques d'application

### Cas 1 — Transmission d'un document confidentiel

**Situation.** Une entreprise doit envoyer un contrat à son partenaire et limiter sa lecture aux destinataires autorisés.

**Analyse cryptographique.** Le chiffrement peut contribuer à la confidentialité, mais l'identité du destinataire et la distribution de la clé sont aussi critiques. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Employer un mécanisme reconnu, vérifier le destinataire et transmettre ou mettre à disposition la clé par un canal adapté et séparé. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Tester l'ouverture par un destinataire autorisé et confirmer que le fichier reste inaccessible dans les conditions prévues sans la clé requise. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** La clé est aussi importante que l'algorithme. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 2 — Référence de hachage non fiable

**Situation.** Un utilisateur télécharge un programme et son empreinte SHA-256 depuis une page inconnue.

**Analyse cryptographique.** Si la source est compromise, le programme et la référence peuvent être remplacés ensemble. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Obtenir une référence de confiance ou vérifier une signature associée à une clé publique authentifiée. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Faire vérifier le fichier par la procédure officielle et consigner la provenance de la référence. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** Une empreinte seule n'authentifie pas sa source. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 3 — Mots de passe conservés en clair

**Situation.** Une base de comptes contient directement les mots de passe des utilisateurs.

**Analyse cryptographique.** Le vol de la base exposerait immédiatement les secrets, dont certains peuvent être réutilisés sur d'autres services. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Remplacer le stockage en clair par une fonction spécialisée, revoir les accès à la base et traiter la fuite si elle s'est produite. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Tester que l'application vérifie les mots de passe sans conserver les secrets récupérables et qu'aucun secret n'apparaît dans les journaux. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** La vérification d'un mot de passe n'exige généralement pas sa récupération en clair. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 4 — Clé privée copiée dans un dépôt

**Situation.** Un développeur commite une clé privée dans un dépôt partagé.

**Analyse cryptographique.** La valeur peut rester disponible dans l'historique, même après suppression de la ligne. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Considérer la clé comme compromise, la révoquer ou la remplacer, examiner les usages et corriger le stockage des secrets. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Confirmer que l'ancienne clé n'est plus acceptée et vérifier les journaux d'utilisation. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** Effacer la ligne visible ne suffit pas si la clé reste valide. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 5 — Certificat valide pour un domaine frauduleux

**Situation.** Un site frauduleux présente un certificat TLS valide pour son propre domaine.

**Analyse cryptographique.** TLS peut protéger la connexion au domaine présenté sans prouver que ce domaine est celui du service légitime attendu. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Vérifier le nom de domaine, utiliser les liens connus et ne pas saisir de secrets sur une page inattendue. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Examiner le domaine et l'origine de la demande par un canal officiel. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** HTTPS ne garantit pas l'honnêteté du site. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 6 — Nonce réutilisé avec AES-GCM

**Situation.** Une application réutilise le même nonce avec la même clé sur plusieurs messages.

**Analyse cryptographique.** Cette erreur peut compromettre les garanties de sécurité du mode. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Utiliser une bibliothèque et une conception qui respectent les contraintes de nonce et évaluer le remplacement de clé si nécessaire. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Ajouter des tests et une revue de conception, au lieu de gérer manuellement des paramètres fragiles. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** Le choix d'AES ne compense pas une mauvaise utilisation du mode. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 7 — Fichier signé mais non chiffré

**Situation.** Un document possède une signature valide mais circule sans mécanisme de confidentialité.

**Analyse cryptographique.** La signature peut aider à vérifier le contenu, mais toute personne qui obtient le fichier peut le lire. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Ajouter un chiffrement approprié si la confidentialité est nécessaire et traiter séparément la validation de la signature. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Vérifier la signature puis tester que seuls les destinataires autorisés peuvent déchiffrer la version protégée. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** Authenticité et confidentialité sont deux objectifs différents. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 8 — Clé publique d'un imposteur

**Situation.** Un partenaire envoie une clé publique par un canal qui n'a pas été vérifié.

**Analyse cryptographique.** Un message chiffré pour la mauvaise clé peut devenir lisible par l'imposteur. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Vérifier l'empreinte ou le certificat de la clé par un canal fiable avant de l'utiliser. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Faire confirmer la clé par un contact déjà connu et documenter la méthode de vérification. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** La cryptographie ne remplace pas la vérification d'identité. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 9 — Clé de chiffrement perdue

**Situation.** La seule copie de la clé d'archives se trouve sur le poste d'un ancien collaborateur.

**Analyse cryptographique.** La confidentialité peut être maintenue, mais la disponibilité des données pour l'organisation est compromise. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Mettre en place un inventaire, une récupération contrôlée et des responsabilités de garde des clés. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Tester une restauration depuis une copie de secours autorisée et vérifier que l'accès est journalisé. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** La récupération doit être prévue avant la perte. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

### Cas 10 — Algorithme de chiffrement inventé

**Situation.** Une application remplace les lettres par d'autres et affirme que ses documents sont sécurisés.

**Analyse cryptographique.** La transformation est facilement analysable et ne possède pas de garanties reconnues. Il faut identifier le besoin principal : cacher le contenu, vérifier un changement, confirmer une signature, protéger un mot de passe ou gérer une clé. Ces objectifs sont liés mais ne sont pas interchangeables. Vérifie aussi quelles informations sont connues et lesquelles restent à confirmer.

**Mesures.** Remplacer la méthode par une bibliothèque éprouvée et un mécanisme adapté à l'objectif. Utilise une bibliothèque et un protocole reconnus, protège les secrets et documente les conditions de récupération. Toute action de remplacement ou de rotation doit tenir compte des données existantes et des services qui dépendent de la clé concernée.

**Vérification.** Faire relire la conception et vérifier son comportement avec des tests appropriés. Le résultat doit être contrôlé avec un test adapté au besoin. Il faut vérifier le comportement sur les cas normaux et les cas d'échec, et consigner les limites connues. Une opération qui réussit ne prouve pas automatiquement que toute l'architecture est sûre.

**À retenir.** La simplicité d'une méthode artisanale ne constitue pas une preuve de sécurité. La cryptographie n'est efficace que si le mécanisme, la confiance dans les clés et les pratiques d'exploitation sont cohérents.

