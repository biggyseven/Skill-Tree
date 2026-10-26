# IDS/IPS et détection d'intrusion

> **Mise en contexte**
>
> Une entreprise possède un pare-feu, des VLAN, un VPN et des postes protégés. Pourtant, un appareil compromis peut utiliser une connexion autorisée pour communiquer avec une infrastructure inconnue, un poste peut sonder les services internes et une application peut recevoir des requêtes malveillantes. Les contrôles préventifs réduisent les possibilités, mais ils ne détectent pas nécessairement toutes les tentatives. L'organisation doit aussi observer le réseau et les systèmes, repérer les signaux pertinents, les analyser puis décider si une alerte demande une réponse.
>
> Un IDS (*Intrusion Detection System*) recherche des signes d'activité suspecte et génère des alertes. Un IPS (*Intrusion Prevention System*) peut en plus interrompre un trafic lorsqu'il est intégré au chemin de transmission et configuré pour bloquer. Le résultat dépend du placement des capteurs, de la visibilité, des règles, des faux positifs, de la capacité et du travail d'investigation. Ce cours relie les concepts à des architectures concrètes, avec de nombreux schémas, exemples, travaux pratiques et exercices corrigés.

## 1. Objectifs pédagogiques et prérequis

À la fin du cours, tu dois savoir différencier IDS et IPS, reconnaître les types de capteurs, comparer les signatures et la détection comportementale, déterminer où placer un capteur, comprendre les limites d'un port miroir, interpréter les champs d'une alerte, distinguer faux positif et faux négatif, ajuster une règle sans créer une brèche, expliquer les modes passif et inline, comprendre les limites liées au chiffrement, intégrer les événements à une chaîne de supervision et organiser la réponse à une alerte.

Les prérequis sont les bases TCP/IP, les ports et protocoles, les VLAN, le routage, les pare-feu, les journaux et les principes de réponse à incident. Les exemples de trafic et les règles de test sont inoffensifs et doivent être employés dans un laboratoire autorisé. Ne réalise jamais un scan, une capture ou un test de blocage sur un réseau tiers sans autorisation explicite.

## 2. IDS, IPS et systèmes de détection/prévention

Un IDS surveille des paquets, des métadonnées ou des événements système puis recherche des signes d'incident. Il peut utiliser des règles déterministes, des signatures connues, des anomalies de protocole et des modèles de comportement. Lorsqu'un événement correspond aux critères, le capteur produit une alerte, un journal ou une donnée utile à l'investigation. Dans son mode passif classique, il n'est pas placé sur le chemin où transite le paquet original.

Un IPS dispose d'une capacité de prévention. En mode inline, le trafic traverse le moteur d'inspection, qui peut transmettre, abandonner ou rejeter des paquets selon les règles et le mode configuré. Cela permet de bloquer certaines tentatives avant qu'elles atteignent le service cible. En contrepartie, l'IPS devient une dépendance de disponibilité : une mauvaise règle, une saturation, un défaut logiciel ou une politique trop agressive peut interrompre du trafic légitime.

**Schéma pédagogique — IDS passif et IPS en ligne**

~~~text
IDS passif avec copie du trafic
[Client] ---> [Switch / routeur] --------------------> [Serveur]
                     |
                     +---- copie du flux -----------> [IDS] ---> [Alerte]

IPS inline
[Client] ---> [Capteur IPS / moteur de décision] ---> [Serveur]
                         |
                         +-- trafic permis : transmettre
                         +-- trafic interdit : bloquer selon politique
~~~

Un produit peut proposer plusieurs modes, et la présence d'une fonction dans l'interface ne veut pas dire qu'elle est active. Une règle de blocage sur un capteur en miroir ne supprime pas spontanément les paquets sur le lien observé. Elle n'a un effet de prévention que si l'architecture fournit une action de blocage et si celle-ci est réellement configurée. La syntaxe, les actions et les modes de fonctionnement varient selon le moteur et sa version.

Une alerte n'est pas une preuve de compromission. Elle signifie qu'un motif, un comportement ou une anomalie correspond aux critères d'une règle. Une sonde de vulnérabilité autorisée peut produire les mêmes signaux qu'une reconnaissance non autorisée ; une application légitime peut contenir une séquence qui ressemble à une tentative d'exploitation. L'analyse doit rapprocher le signal du contexte : origine, cible, heure, processus, activité prévue, impact et autres événements.

## 3. Les principales familles de capteurs

Un NIDS (*Network IDS*) analyse le trafic d'un segment ou d'un point réseau. Il peut détecter des scans, des protocoles inattendus, des tentatives d'exploitation connues ou des communications entre hôtes. Sa visibilité dépend du point de capture, du routage, du chiffrement, de la capacité à reconstituer les conversations et de l'absence de pertes de capture.

Un HIDS (*Host IDS*) surveille un hôte : journaux système, changements de fichiers, processus, configuration, connexions locales ou autres événements disponibles. Il peut voir des faits qui ne sont plus visibles sur le réseau, par exemple ce qui se passe après déchiffrement ou dans un processus. Il ne fournit pas automatiquement la vue globale des communications.

Un système de détection sans fil observe les réseaux radio, les points d'accès non autorisés et certaines anomalies Wi-Fi. Les systèmes NDR (*Network Detection and Response*) associent souvent métadonnées réseau, détection comportementale et fonctions d'investigation. Les EDR se concentrent sur les endpoints ; le SIEM centralise et corrèle des événements issus de plusieurs sources. Ces catégories se chevauchent parfois commercialement, mais leur visibilité et leur rôle technique restent distincts.

**Schéma pédagogique — compléter les vues**

~~~text
                        [SIEM / console centrale]
                         ^          ^          ^
                         |          |          |
                      [NIDS]    [HIDS / EDR]  [WIDS]
                         ^          ^          ^
                         |          |          |
                   [trafic réseau] [endpoint] [radio Wi-Fi]
                         |          |          |
                      [Switch]   [Serveur]   [Points d'acces]
                          \          |          /
                           +---- reseau --------+
~~~

Un NIDS peut voir que le serveur échange avec une adresse inconnue sans savoir quel processus a créé le trafic. Un HIDS peut révéler le processus, mais manquer le balayage initial du réseau. La corrélation ajoute le contexte ; elle exige toutefois des horloges cohérentes, des identifiants stables et une collecte correctement configurée.

## 4. Choisir l'emplacement des capteurs

Le placement découle des questions que l'organisation veut résoudre. Un capteur à la bordure Internet observe les flux qui passent par cette frontière. Il peut détecter certaines tentatives entrantes, des connexions sortantes inhabituelles et du trafic vers les services publiés. Il ne voit pas nécessairement les communications entre deux serveurs si celles-ci restent sur un segment interne ou passent par le routage de distribution.

Un capteur placé à proximité d'un réseau sensible permet d'observer des flux internes précis. Un capteur dans une DMZ peut suivre les connexions aux services exposés, mais doit aussi couvrir les sorties de cette DMZ lorsque le besoin de sécurité l'exige. Dans un centre de données, plusieurs capteurs ou sources de télémétrie peuvent être nécessaires pour éviter les angles morts.

**Schéma pédagogique — observation nord-sud et est-ouest**

~~~text
                     [Internet]
                         |
                   [Pare-feu bordure]
                         |
                   (Capteur A)
                         |
                  [Distribution L3]
                  /       |        \
                 v        v         v
            [VLAN users] [Serveurs] [DMZ]
                |           |         |
           (Capteur B) (Capteur C)  (Capteur D)

A : trafic qui traverse la bordure.
B/C/D : flux internes spécifiques selon le routage et le placement.
~~~

Avant de choisir une interface, dessine les chemins des flux, les VLAN, les liens agrégés, les routes de secours, les VPN et les tunnels. Vérifie si le trafic retour emprunte un autre chemin, si le chiffrement empêche l'inspection du contenu et si le capteur reçoit effectivement les paquets. La topologie logique ne garantit pas automatiquement la visibilité réelle.

Dans un réseau OT/ICS, médical ou critique, privilégie souvent une première phase d'observation passive. Toute insertion inline doit être précédée d'un test de compatibilité, d'une analyse de risque, d'un plan de retour arrière et de l'accord des responsables métier. Les erreurs de blocage peuvent interrompre une production et avoir des impacts physiques.

## 5. SPAN, TAP et perte de visibilité

Un port miroir (SPAN sur les plateformes qui emploient ce terme) copie des paquets depuis une ou plusieurs interfaces ou VLAN vers un port de surveillance. Le capteur observe une copie sans être dans le chemin de transmission. C'est pratique pour démarrer un IDS passif, mais le débit agrégé de plusieurs sources peut dépasser la capacité du port de destination ou du moteur de capture.

Un TAP fournit une copie de trafic sur une liaison physique selon les caractéristiques du matériel. Il peut apporter une visibilité utile sur une liaison précise, mais nécessite du matériel, une installation et une conception appropriée. Aucun TAP ou SPAN ne garantit à lui seul la couverture de tous les chemins.

**Schéma pédagogique — surcharge du port miroir**

~~~text
Lien A : 6 Gbit/s ----\
Lien B : 5 Gbit/s -----+--> [SPAN] --> port miroir 10 Gbit/s --> [IDS]
Lien C : 4 Gbit/s ----/                         |
                                           pertes possibles
                                   si le débit copié dépasse
                                     la capacité de sortie
~~~

Lorsque les sources produisent davantage de trafic que le port miroir ne peut transmettre, des paquets peuvent être perdus. Le moteur risque de manquer des segments ou de reconstruire incorrectement un flux TCP. Mesure les compteurs de capture, la charge CPU, la saturation des interfaces, les files d'attente et les pertes. Réduis les sources miroitées selon l'objectif ou répartis la capture sur plusieurs capteurs.

L'absence d'alerte n'est interprétable que si le capteur a reçu le trafic pertinent, que les règles sont actives et que le protocole était visible. Surveille la santé des capteurs : service arrêté, disque plein, ingestion retardée, paquets perdus, règles non chargées et mises à jour échouées doivent générer des événements opérationnels.

## 6. Méthodes de détection

La détection par signatures recherche des motifs définis : séquences, champs de protocole, contenus, combinaisons de conditions ou enchaînements de paquets. Elle est efficace pour des comportements connus et bien caractérisés. Sa couverture dépend de la qualité des règles, de leur mise à jour, de la visibilité du trafic et des capacités de décodage du moteur.

La détection par anomalies compare l'activité à une ligne de base ou à des contraintes de protocole. Elle peut signaler un comportement nouveau, mais le trafic qui change de manière légitime peut produire beaucoup de faux positifs. La détection comportementale examine plutôt des séries d'événements : balayage de destinations, volume sortant inhabituel, connexions rares entre zones ou séquence d'actions qui ne correspond pas à l'usage attendu.

**Schéma pédagogique — chaîne des méthodes de détection**

~~~text
Trafic / evenements / metadonnees
                 |
                 v
           [Normalisation]
                 |
         +-------+---------+
         |       |         |
         v       v         v
    [Signatures][Anomalies][Comportement]
         |       |         |
         +-------+---------+
                 |
                 v
          [Alerte candidate]
                 |
                 v
       [Contexte + priorite + triage]
~~~

Les systèmes combinent souvent plusieurs approches. Une signature peut détecter un motif connu, la détection comportementale peut montrer qu'une source a touché beaucoup de ports, et l'EDR peut donner le nom du processus à l'origine du trafic. Aucun signal ne prouve à lui seul que l'attaque a réussi ; il faut distinguer tentative, blocage, activité suspecte et compromission confirmée.

## 7. Signatures, règles et actions

Une règle décrit un motif à détecter et l'action associée. Selon le moteur, elle peut inclure une action, un protocole, source et destination, ports, direction, conditions de correspondance, identifiant, message et classification. Les syntaxes et priorités diffèrent entre Snort, Suricata et les solutions commerciales. Utilise toujours la documentation de la version installée.

**Schéma pédagogique — anatomie conceptuelle d'une règle**

~~~text
[Action] [protocole] [source:port] [direction] [destination:port]
             |
             v
        [Conditions de correspondance]
   contenu / etat / protocole decode / sequence
             |
             v
      [Identifiant + message + classification]
             |
             v
      [Evenement et action prevue]
~~~

Une action d'alerte génère un événement sans nécessairement bloquer le paquet. Une action drop, block ou reject peut avoir une signification précise selon le moteur et le mode. Par exemple, Suricata distingue le mode IDS passif du mode IPS inline ; les effets d'une action dans une analyse hors ligne de capture ne bloquent pas le réseau en direct.

Exemple pédagogique d'une règle Suricata inoffensive : elle génère une alerte pour une requête HTTP de laboratoire dirigée vers un chemin de test que l'apprenant contrôle. Elle ne cherche pas à exploiter une vulnérabilité.

~~~text
alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"FORMATION IDS marqueur de test"; flow:established,to_server; http.uri; content:"/training-ids-test"; sid:1000001; rev:1;)
~~~

Cet exemple illustre une alerte de test, pas une signature complète de protection contre les attaques Web. Les variables réseau et le décodage doivent correspondre à la version installée. Vérifie la syntaxe, teste sur un flux contrôlé et utilise le mode d'alerte avant de considérer une action de blocage.

## 8. Lire et prioriser une alerte

Une alerte utile fournit le moment, la source, la cible, les ports, le protocole, la règle, le capteur, le message, l'action et des données de contexte. Les champs réels dépendent de l'outil et de sa configuration. La gravité attribuée par la signature ne suffit pas à estimer l'impact : la criticité du serveur, l'exposition, la répétition, la confiance et le contexte métier comptent aussi.

**Schéma pédagogique — cycle de vie d'une alerte**

~~~text
[Evenement detecte]
        |
        v
[Dedoublonner / enrichir]
        |
        v
[Prioriser: severite + cible + contexte]
        |
        v
[Analyste verifie les faits]
        |
   +----+------------------+
   |                       |
   v                       v
Activite legitime      Incident probable
   |                       |
   v                       v
Ajuster/documenter     Confinement coordonne
                           |
                           v
                    Remediation / reprise
                           |
                           v
                    Lecon apprise / regle
~~~

Un grand nombre d'alertes peut correspondre à un scanner de conformité autorisé ou à une boucle de détection répétée. Une alerte de faible gravité peut être importante si elle touche un actif critique ou s'accompagne d'autres événements. Distingue la sévérité de la règle, la confiance dans le signal, l'impact potentiel et l'urgence opérationnelle.

Les alertes devraient être regroupées selon un contexte utile : source, cible, règle, fenêtre temporelle, session et identités connues. La déduplication doit réduire le bruit sans effacer les détails utiles. Les événements originaux doivent rester accessibles selon la politique de rétention afin de soutenir les enquêtes et audits.

## 9. Faux positifs et faux négatifs

Un faux positif est un événement légitime signalé ou bloqué à tort. Un faux négatif est une activité malveillante non détectée. Un réglage sérieux ne consiste pas à désactiver de nombreuses signatures pour réduire le volume ni à bloquer tout ce qui paraît inhabituel. Il faut confirmer le contexte et ajuster la détection de manière contrôlée.

**Schéma pédagogique — confirmer puis régler**

~~~text
Alerte
  |
  v
[Examiner la regle, le flux et le contexte]
  |
  +--> comportement malveillant ? --> conserver / repondre
  |
  +--> trafic legitime ?
              |
              v
     [Reproduire et confirmer]
              |
              v
[Exception minimale / seuil / action / conditions]
              |
              v
[Test positif + test negatif + revue]
              |
              v
            Deployer
~~~

Les modes observation et prévention doivent être distingués. L'alerte seule peut servir à établir une baseline et à étudier les faux positifs. Le blocage doit être activé après validation, en particulier pour des applications critiques. Certains produits permettent de passer une signature de drop à alert sans rendre toute la politique inactive. Les fonctions exactes sont spécifiques au fournisseur.

Une exception trop générale crée un angle mort. Si une sauvegarde légitime déclenche une signature, exclure tout le serveur peut permettre à d'autres flux de contourner la détection. Cherche l'ajustement le plus étroit compatible avec les preuves : signature, protocole, direction, source, destination ou période, selon les possibilités du moteur.

## 10. TLS et limites de visibilité

Sur une session HTTPS, un capteur passif voit les adresses, les ports, les tailles, les rythmes et certaines métadonnées accessibles, mais pas nécessairement la charge utile en clair. Les capacités de classification et de détection dépendent du protocole, des métadonnées disponibles, du point d'observation et de la prise en charge par le moteur.

**Schéma pédagogique — compléter la visibilité d'un trafic chiffré**

~~~text
[Client] ======= session TLS chiffree ======= [Serveur]
   |                                             |
   v                                             v
[EDR / processus]                         [Logs applicatifs]
       \                                       /
        +------ [IDS reseau: metadonnees] -----+
                          |
                          v
                [Correlation multi-sources]
~~~

L'utilisation de TLS n'annule pas toute utilité de l'IDS. L'analyse des destinations, de la fréquence, des comportements et de certains éléments de protocole peut apporter des signaux. Mais il ne faut jamais prétendre que le capteur peut lire tout le contenu chiffré s'il ne dispose pas d'une inspection autorisée et compatible.

L'inspection TLS intermédiaire pose des questions de confiance, de certificats, de sécurité des clés, de confidentialité, de compatibilité et de performance. Elle demande une décision explicite et une méthode de déploiement adaptée ; ce n'est pas une option à activer sans analyse. Les endpoints, DNS, journaux serveur, identité et autres contrôles doivent compléter les angles morts.

## 11. Baseline et détection comportementale

Une baseline décrit le fonctionnement attendu : destinations, services, volumes, horaires, identités, types de flux et relations entre zones. Elle doit couvrir des périodes représentatives et être actualisée après des changements. Une baseline trop courte peut classer un usage légitime comme anormal ; une baseline contaminée par une activité malveillante peut normaliser un comportement dangereux.

Des signaux possibles incluent un nombre inhabituel de destinations, des ports contactés, un volume sortant exceptionnel, des échecs d'authentification répétés, des requêtes DNS atypiques, de nouvelles communications latérales ou une activité en dehors des horaires attendus. Les seuils doivent être adaptés aux actifs et aux capacités de l'organisation.

**Schéma pédagogique — déviation comportementale**

~~~text
[Baseline validee: destinations / volume / horaires]
                         |
                         v
                  [Valeur observee]
                         |
                +--------+---------+
                |                  |
                v                  v
         Dans la normale     Ecart significatif
                |                  |
                v                  v
          Suivi courant      Enrichir / alerter
                                   |
                                   v
                         Verifier changement,
                         maintenance, panne
                         ou comportement hostile
~~~

Une anomalie est une hypothèse, pas une conclusion. Les sauvegardes, déploiements et tests approuvés peuvent produire des pics. Il faut tenir compte des changements et éviter qu'une liste d'exceptions permanente ne masque des événements réellement dangereux.

## 12. Suricata en laboratoire : vérifier une détection

Suricata peut analyser des captures ou du trafic en direct, produire des alertes et, selon le mode et la configuration, être utilisé pour la prévention inline. Les étapes diffèrent selon le système, la version et les paquets installés. Commence par vérifier la version, la configuration et le jeu de règles approuvé.

Une commande de validation de configuration fréquemment disponible est :

~~~text
suricata -T -c /etc/suricata/suricata.yaml
~~~

Le chemin de configuration peut être différent. Cette vérification ne confirme pas que le capteur reçoit le trafic voulu ni que la règle détecte le test. La capture, les interfaces, le chargement de règles et les journaux doivent être contrôlés séparément.

**Schéma pédagogique — laboratoire déterministe**

~~~text
[Client de test] ---> [Serveur HTTP contrôlé]
       |                       ^
       | requête au chemin     |
       v                       |
[Capture / interface] ---> [Suricata en IDS]
                                |
                                v
                         [eve.json / alertes]
                                |
                                v
                         [Verification humaine]

Ne teste pas le blocage inline sur un réseau de production.
~~~

Pour vérifier un scénario, envoie une requête inoffensive vers un chemin précis que tu contrôles. Observe si le capteur reçoit le trafic, si la règle est chargée et si l'événement apparaît dans le journal. Répète avec une requête différente pour vérifier la condition de correspondance. Ne télécharge pas et ne lance pas d'exploit réel uniquement pour démontrer que l'IDS fonctionne.

## 13. Journaux et corrélation SIEM

Un journal JSON tel que eve.json peut contenir des alertes, flux, événements DNS, HTTP, TLS et statistiques selon la configuration. Pour un événement, examine l'horodatage, le type, le capteur, les adresses, les ports, le protocole, l'action et la règle. Les champs exacts dépendent de la version et de la configuration.

Exemple purement illustratif d'un événement de test :

~~~json
{
  "timestamp": "2026-10-26T12:00:00.000000+0000",
  "event_type": "alert",
  "src_ip": "192.0.2.25",
  "src_port": 53120,
  "dest_ip": "198.51.100.40",
  "dest_port": 80,
  "proto": "TCP",
  "alert": {
    "signature": "FORMATION IDS marqueur de test",
    "category": "Test de laboratoire",
    "severity": 3,
    "action": "allowed"
  }
}
~~~

Les valeurs et la forme sont fictives ; l'action et la structure réelles varient selon le moteur. Dans un IDS passif, une valeur indiquant que le trafic a continué ne signifie pas que le capteur a pris une décision de pare-feu. Il a seulement observé le flux et produit une alerte.

**Schéma pédagogique — corrélation multi-sources**

~~~text
[NIDS/IPS] [EDR] [DNS] [Pare-feu] [Identite]
    \        |     |       |         /
     +-------+-----+-------+--------+
                    |
                    v
             [Collecteur / SIEM]
                    |
                    v
         [Normalisation + correlation]
                    |
                    v
          [Investigation / priorite]
                    |
                    v
              [Reponse suivie]
~~~

Le SIEM doit être surveillé comme un service : délais d'ingestion, files d'attente, perte de données, horloges, accès et stockage. Une alerte qui n'atteint pas les analystes n'est pas utile. Centralise les événements pertinents, conserve les détails nécessaires, protège les données sensibles et vérifie régulièrement le pipeline de collecte.

## 14. Réponse à une alerte

Commence par préserver les faits : règle, horodatage, source, cible, flux, action et changement récent. Vérifie si l'activité était prévue et autorisée. Recherche des signaux associés dans les journaux du pare-feu, du DNS, de l'endpoint et du service cible. La question principale est de déterminer si le capteur a observé une tentative, un trafic bloqué, une activité suspecte ou une compromission confirmée.

Si une réponse est nécessaire, choisis une action proportionnée : bloquer un flux précis, isoler un endpoint, révoquer une session, faire analyser le serveur ou escalader vers l'équipe de réponse à incident. Évalue l'impact opérationnel et conserve les preuves avant les manipulations qui pourraient détruire les données utiles. Les actions automatiques doivent suivre une politique testée, avec des garde-fous et une procédure d'exception.

## 15. IPS inline, tolérance aux pannes et disponibilité

Un IPS en ligne est une étape du chemin de données. Il peut bloquer les flux malveillants, mais rend l'architecture dépendante du moteur et de ses ressources. Il faut évaluer le débit, les nouvelles connexions par seconde, la latence, le réassemblage, la charge, la mise à jour des règles et le comportement de panne.

**Schéma pédagogique — panne de capteur inline**

~~~text
Lien reseau ---> [IPS inline] ---> Destination
                      |
                 panne moteur
                      |
             +--------+--------+
             |                 |
             v                 v
         Fail-open          Fail-closed
     trafic continue,     trafic bloque selon
     inspection absente   la conception

Choisir après analyse du risque et test de reprise.
~~~

Fail-open privilégie la continuité en laissant passer le trafic si le contrôle échoue, mais les paquets ne bénéficient plus de la même inspection. Fail-closed privilégie le contrôle, mais peut interrompre une activité légitime. Aucun choix n'est universel. La décision dépend de la criticité de l'actif, des contrôles compensatoires, de la redondance et des objectifs de disponibilité.

Ne déploie pas la prévention en ligne dans un environnement critique sans tester les règles, les faux positifs, la panne du moteur, la redondance et le retour arrière. Un capteur en miroir n'est pas équivalent à un IPS inline. Une action de blocage dans une règle ne prouve pas que la topologie permet d'arrêter le trafic réellement observé.

## 16. Cycle de vie des règles

Les règles évoluent avec les vulnérabilités, les protocoles, les applications et les moteurs d'inspection. Une mise à jour peut améliorer la couverture ou modifier les résultats, parfois avec de nouveaux faux positifs. Documente l'origine, la version, le propriétaire, les exceptions, l'action et le but de chaque règle locale.

**Schéma pédagogique — cycle de mise à jour**

~~~text
[Regles approuvees / source fiable]
                  |
                  v
       [Verifier version et origine]
                  |
                  v
        [Tester configuration / rules]
                  |
                  v
       [Mesurer faux positifs / charge]
                  |
                  v
             [Pilote]
                  |
                  v
       [Surveiller et revenir arriere]
                  |
                  v
       [Deploiement general / revue]
~~~

Évite de modifier directement les fichiers de règles fournis si le gestionnaire de mise à jour écrase ces changements. Utilise les mécanismes prévus par le produit, conserve un identifiant local non conflictuel et teste sur des captures connues. Une signature trop large génère des faux positifs ; une signature trop étroite peut manquer des variantes. Les changements doivent être relus, validés et observés après déploiement.

## 17. Performances et santé du capteur

La performance dépend du débit, des tailles de paquets, du nombre de sessions, du nombre de règles, du réassemblage des flux, des protocoles, du journalisation et de la capacité de stockage. Une fiche technique de débit nominal ne garantit pas le même résultat avec la totalité des fonctions activées.

Surveille les pertes de paquets, le débit capturé, le CPU, la mémoire, les files d'attente, les retards d'analyse, le nombre de sessions et l'espace disque. Une saturation peut provoquer des faux négatifs, tandis qu'une collecte saturée peut laisser les alertes sans traitement. Répartis les sources de capture ou augmente la capacité selon les objectifs, en documentant la couverture perdue lors de toute réduction.

## 18. Surveillance des réseaux OT/ICS

Les environnements industriels ont souvent des communications répétitives et des contraintes fortes de disponibilité. Une détection passive permet d'établir ce qui est normal : quels postes parlent aux automates, quelles applications utilisent les protocoles prévus et à quelles heures les échanges sont attendus.

**Schéma pédagogique — surveillance OT**

~~~text
[Poste operateur HMI] ------> [PLC / automate]
          |                         |
          v                         v
       [Zone controle] -------- [Equipement terrain]
          |
          v
   [Capteur passif IDS OT]
          |
          v
     [Analyse et alerte]
~~~

Une nouvelle destination, un protocole inattendu ou une communication hors horaire peut justifier une investigation, mais les tests doivent être approuvés. Ne passe pas un capteur en mode blocage sur des automates de production sans analyse de risque, validation par le responsable industriel et procédure de restauration. La disponibilité et la sûreté sont des exigences de premier plan.

## 19. Durcissement du capteur et intégrité de collecte

Le capteur doit lui-même être protégé : comptes individuels, accès administratif restreint, mises à jour contrôlées, synchronisation horaire, sauvegarde de configuration et stockage protégé des journaux et captures. Les PCAP peuvent contenir des données sensibles ; leur accès et leur conservation doivent suivre la politique de l'organisation.

Vérifie les services ouverts, les interfaces d'administration, le système et le moteur, les permissions de fichiers, les sources de règles et les intégrations SIEM. Prévois un accès de secours lorsque le capteur en ligne peut interrompre le chemin de gestion. Teste la récupération et le retour à une configuration connue avant un changement majeur.

## 20. Méthode de dépannage d'une absence d'alerte

1. Confirme que le trafic de test passe par le point observé.
2. Vérifie l'état du capteur, l'interface de capture et les pertes.
3. Confirme que les règles attendues sont chargées et actives.
4. Vérifie que le protocole et les champs sont visibles au moteur.
5. Contrôle les journaux, filtres de consultation et files de collecte.
6. Reproduis avec un marqueur inoffensif et connu.
7. Compare les résultats d'une capture source et ceux du moteur.
8. Vérifie les versions du moteur, les règles et leurs actions.
9. Change un élément à la fois et consigne les résultats.
10. Reteste la détection et l'absence d'impact sur le trafic légitime.

Une absence d'alerte peut venir d'une capture invisible, de paquets perdus, d'une règle non chargée, d'un filtre de journal ou d'un protocole chiffré. Il faut isoler ces possibilités au lieu de conclure directement que le système n'a détecté aucune menace.

## 21. Travaux pratiques guidés

### TP 1 — Générer une alerte de test Suricata

Utilise une machine client et un serveur HTTP de laboratoire que tu contrôles. Ajoute la règle d'alerte de marqueur présentée dans ce cours, vérifie la configuration et assure-toi que le capteur voit le trafic du laboratoire.

**Travail demandé :** envoie une requête vers le chemin de test, relève l'alerte puis envoie une requête vers un autre chemin. Compare les journaux et identifie les champs disponibles : heure, source, destination, règle, action et message.

**Correction attendue :** le marqueur déclenche l'événement défini ; la requête différente ne doit pas correspondre à cette condition de la même manière. Si aucune alerte n'apparaît, vérifie l'interface, les règles chargées, la visibilité du protocole et la configuration de journalisation avant toute modification.

### TP 2 — Cartographier un placement IDS

Le réseau comprend un pare-feu, trois VLAN internes, une DMZ et un VPN. Le trafic entre deux serveurs internes ne traverse pas le pare-feu de bordure.

**Travail demandé :** dessine les chemins, choisis les points d'observation, indique les limites d'un SPAN qui copie plusieurs liens, et propose des métriques pour détecter les pertes de capture.

**Correction attendue :** le capteur de bordure observe les flux qui traversent la bordure mais pas tous les mouvements latéraux. Il faut un point d'observation sur les chemins internes pertinents ou une autre source de télémétrie. Mesure les pertes, le débit agrégé, la charge et les sessions vues, puis teste la visibilité avec un flux connu.

### TP 3 — Décider d'une exception IPS

Une sauvegarde autorisée déclenche une signature et la politique en ligne bloque la session.

**Travail demandé :** confirme la fenêtre de sauvegarde, le système source, la destination, l'identifiant de règle et le contexte du trafic. Propose un réglage minimal puis définis les tests de non-régression.

**Correction attendue :** établis d'abord le caractère légitime de l'activité. Si le faux positif est confirmé, limite l'exception à la signature et au flux nécessaire selon les capacités du moteur, donne-lui un propriétaire et une date de revue, puis teste qu'une activité non autorisée conserve la capacité d'être détectée.

## 22. Exercices corrigés

### Exercice 1 — IDS ou IPS

Un capteur reçoit une copie SPAN, crée une alerte et n'interrompt pas le flux. Est-ce un comportement anormal ?

**Correction :** non. Le capteur fonctionne en mode passif. Il observe et journalise sans agir sur les paquets originaux. Pour prévenir, il faut un IPS en ligne ou un mécanisme d'action explicitement conçu et contrôlé.

### Exercice 2 — Faux positif

Une signature IPS bloque une application métier.

**Correction :** examine le flux, le contexte, l'identifiant de signature et les preuves. Reproduis en laboratoire, confirme le faux positif et ajuste le minimum nécessaire. N'éteins pas toute la prévention pour une seule règle.

### Exercice 3 — Aucune alerte ne remonte au SIEM

Que faut-il vérifier ?

**Correction :** capteur, interface, capture, règles actives, paramètres de journalisation, connecteur, files d'attente, horloges et filtres côté SIEM. L'absence d'événement visible peut venir de la collecte et non de l'absence de détection.

### Exercice 4 — Scan approuvé

Un scanner de conformité déclenche beaucoup de signatures.

**Correction :** vérifie l'identité du scanner, les cibles, les horaires et l'approbation. Documente le périmètre autorisé et surveille les écarts. Ne crée pas d'exclusion globale pour toute l'organisation.

### Exercice 5 — TLS

Pourquoi un NIDS peut-il ne pas inspecter la charge utile d'une session HTTPS ?

**Correction :** la charge utile est chiffrée. Le capteur peut toujours utiliser certaines métadonnées et comportements, tandis que l'EDR, le DNS et les logs du serveur fournissent une autre visibilité. Le déchiffrement éventuel demande une décision explicite et compatible.

### Exercice 6 — Capture avec pertes

Pourquoi les pertes SPAN sont-elles problématiques ?

**Correction :** l'IDS ne peut pas inspecter les paquets qu'il ne reçoit pas et peut reconstituer incorrectement un flux. Mesure la charge agrégée et la capacité du port miroir puis répartis la capture ou adapte l'architecture.

### Exercice 7 — Anomalie de volume sortant

Un serveur envoie beaucoup plus de données que d'habitude.

**Correction :** compare la baseline, les sauvegardes, les changements, la destination et les journaux du serveur. Le volume peut indiquer une tâche légitime ou une exfiltration ; il faut corréler et vérifier les faits.

### Exercice 8 — Une signature change après mise à jour

Comment sécuriser le changement ?

**Correction :** vérifie les notes et versions, observe les événements affectés, valide les règles sensibles sur un pilote et garde un retour arrière. Ne désactive pas les mises à jour en permanence pour conserver l'ancien résultat.

### Exercice 9 — L'IPS tombe

Quelles décisions doivent avoir été prises avant la mise en production ?

**Correction :** fail-open ou fail-closed, impact métier, redondance, capacité, accès hors bande, procédure de reprise et surveillance. Le choix dépend de la criticité et des contrôles compensatoires.

### Exercice 10 — Sévérité élevée

Une alerte de gravité élevée signifie-t-elle que le système est compromis ?

**Correction :** non. La sévérité reflète la règle ou la classification, pas nécessairement une réussite d'exploitation. Vérifie la cible, les actions du capteur, les logs endpoint et serveur, puis classe l'événement selon les preuves.

### Exercice 11 — Mouvement latéral invisible

Les scans entre deux VLAN ne sont pas détectés par le capteur de bordure.

**Correction :** le trafic peut ne pas traverser cette frontière. Cartographie le chemin réel et place des capteurs ou une télémétrie adaptée sur les flux prioritaires. Teste la visibilité avec un trafic autorisé et connu.

### Exercice 12 — Trop d'alertes

Comment réduire la fatigue des analystes ?

**Correction :** déduplique les événements, enrichis par l'identité et l'inventaire, regroupe par source/cible/règle et confirme les faux positifs. Ne supprime pas une famille entière de règles seulement parce qu'elle génère beaucoup d'événements.

## 23. Défi final — déployer un IDS/IPS avec contrôle progressif

### Contexte

L'entreprise dispose d'une DMZ Web, d'un réseau utilisateurs, de serveurs critiques, d'un accès VPN, de sauvegardes nocturnes et de scans de conformité autorisés. Elle veut améliorer la détection sans interrompre son activité.

### Correction détaillée

**Étape 1 — Fixer les objectifs.** Définis les actifs et les questions de détection : flux vers la DMZ, accès aux serveurs, trafic sortant anormal, identité à l'origine des événements et signaux endpoint complémentaires.

**Étape 2 — Cartographier les chemins.** Identifie les routes, VLAN, points de capture, SPAN/TAP, tunnels et chemins asymétriques. Évalue les pertes possibles et valide la réception avec un flux de test.

**Étape 3 — Déployer passivement.** Charge un corpus approuvé, vérifie la configuration et les journaux, puis observe les alertes. Mesure le volume, les faux positifs et les ressources avant tout blocage automatique.

**Étape 4 — Construire la baseline.** Documente applications, destinations, horaires, sauvegardes, scans autorisés et changements. Toute exception possède un motif, un propriétaire et une date de revue.

**Étape 5 — Centraliser et corréler.** Configure les événements pertinents dans le SIEM, vérifie les horloges, surveille les pertes de collecte et enrichis les alertes avec les actifs et les identités.

**Étape 6 — Valider la prévention.** Dans un laboratoire ou pilote isolé, vérifie les règles de blocage, les faux positifs, le comportement en panne, la performance et la capacité de rollback. Étends progressivement aux flux pour lesquels l'interruption est acceptable.

**Étape 7 — Préparer la réponse.** Définis les responsabilités, l'escalade, les actions de confinement, la conservation des preuves et les critères pour passer d'une alerte à un incident confirmé.

**Étape 8 — Mesurer et améliorer.** Suit la couverture, les pertes de paquets, le délai de traitement, les exceptions, les fausses alertes et les incidents. Ajuste la baseline après chaque changement important.

Le défi est réussi lorsque la couverture est démontrée, les règles sont à jour, les alertes sont utiles, l'IPS ne bloque pas les services métier de façon imprévue et l'équipe peut justifier chaque exception.

## 24. Checklist de validation

- Les objectifs et actifs surveillés sont identifiés.
- Les capteurs ont un propriétaire, une version et une couverture documentés.
- Les points de capture couvrent les chemins réseau attendus.
- Les pertes, files d'attente, CPU, disque et santé du service sont surveillés.
- Les règles viennent de sources approuvées et leur mise à jour est contrôlée.
- Les alertes contiennent assez de contexte pour investiguer.
- Les faux positifs ont une procédure de confirmation et de revue.
- Les actions de blocage ont été validées avant la production.
- Le mode de panne de l'IPS et le rollback sont documentés.
- Le SIEM reçoit les événements et les horloges sont cohérentes.
- Les limites de visibilité TLS sont explicitement connues.
- Les tests et maintenances autorisés sont documentés.
- Les journaux, captures et configurations sont protégés.
- Les responsabilités de réponse sont claires.
- Des tests inoffensifs prouvent qu'une règle attendue déclenche correctement.

## 25. Glossaire

**IDS :** système qui surveille des événements et signale des signes possibles d'incident.

**IPS :** système capable de bloquer certaines communications lorsqu'il est déployé et configuré pour la prévention.

**IDPS :** système ou architecture associant détection et prévention.

**NIDS/NIPS :** système de détection ou de prévention fondé sur le trafic réseau.

**HIDS :** capteur logiciel qui surveille un hôte.

**NDR :** détection et réponse réseau souvent centrées sur les flux et les comportements.

**Signature :** règle qui reconnaît un motif ou une séquence.

**Faux positif :** activité légitime signalée ou bloquée à tort.

**Faux négatif :** activité malveillante qui n'est pas détectée.

**SPAN :** mécanisme de copie de trafic vers un port de surveillance.

**TAP :** équipement qui fournit une copie du trafic d'une liaison.

**Baseline :** référence décrivant le comportement attendu.

**SIEM :** système de collecte et de corrélation des événements de sécurité.

**Fail-open :** le trafic continue lorsque le contrôle tombe en panne, selon le design.

**Fail-closed :** le trafic est interrompu ou bloqué lorsque le contrôle tombe en panne.

**IPS inline :** moteur inséré dans le chemin de transmission, capable d'agir sur les paquets selon sa politique.

## 26. Références officielles

- NIST SP 800-94, Guide to Intrusion Detection and Prevention Systems (IDPS) : https://csrc.nist.gov/pubs/sp/800/94/final. NIST précise que le projet de révision de 2012 n'est pas devenu une publication finale.
- Suricata, concept du mode IPS : https://docs.suricata.io/en/latest/ips/ips-concept.html
- Suricata, format des règles : https://docs.suricata.io/en/suricata-8.0.3/rules/intro.html
- Snort 3, structure des règles : https://docs.snort.org/rules/
- Snort 3, journalisation JSON : https://docs.snort.org/start/alert_logging
- Cisco Secure Firewall, gestion des politiques d'intrusion : https://www.cisco.com/c/en/us/td/docs/security/firepower/770/fdm/fptd-fdm-config-guide-770/fptd-fdm-intrusion.html

Les commandes, actions de règles et options de prévention varient selon le moteur et la version installée. Consulte la documentation qui correspond à l'environnement réel. Déploie les règles de blocage en laboratoire puis sur un périmètre pilote validé avant toute mise en production.

Fin du cours.

## 27. Cas pratiques supplémentaires — 30 diagnostics

### Cas de dépannage 1 — Le capteur ne génère aucune alerte

**Analyse.** Le trafic peut ne pas passer par l'interface observée, la règle ne pas être chargée ou le protocole être invisible. Vérifie d'abord l'interface, les compteurs de capture et les pertes, puis la règle active et le journal de sortie. Reproduis avec un marqueur inoffensif contrôlé. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne conclus pas à l'absence de menace avant d'avoir prouvé que le capteur voit le flux. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 2 — Des alertes disparaissent avant d'atteindre le SIEM

**Analyse.** Le connecteur ou la file de collecte peut être saturé, arrêté ou filtrer les événements. Compare le volume généré au volume reçu, les horodatages, les erreurs de transport, la file d'attente et l'espace disque. Vérifie le pipeline avec un événement de test. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne réduis pas la journalisation sans comprendre les pertes. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 3 — Un scan de conformité produit de nombreuses alertes

**Analyse.** Le scanner peut produire un trafic similaire à une reconnaissance non autorisée. Confirme son adresse, son propriétaire, les cibles et la fenêtre approuvée. Compare le périmètre observé à l'autorisation officielle et documente les écarts. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne mets pas le réseau entier en exclusion pour réduire les alertes du scanner. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 4 — Un vrai positif est classé comme faux positif

**Analyse.** Le contexte a pu être incomplet ou l'analyste a supposé qu'une source connue était toujours fiable. Reconstitue la chronologie, les sessions, l'identité, l'action appliquée et les logs endpoint et serveur. Revois l'exception et les critères de triage. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne traite pas une source connue comme automatiquement légitime. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 5 — Le port SPAN montre moins de trafic que le lien source

**Analyse.** Le débit agrégé peut dépasser le débit du port miroir ou les files de capture peuvent perdre des paquets. Mesure les débits, compteurs d'interface, pertes et files d'attente. Réduis les sources non pertinentes ou répartis la capture selon la couverture recherchée. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne considère pas un flux partiellement capturé comme une preuve exhaustive. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 6 — L'IDS ne détecte pas le contenu d'une session HTTPS

**Analyse.** La charge utile est chiffrée et le point de capture n'a pas accès au texte en clair. Utilise la télémétrie d'endpoint, les métadonnées, DNS et les journaux serveur. Évalue l'inspection TLS seulement si elle est légale, compatible et approuvée. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne prétends pas que l'IDS passif peut lire le contenu TLS chiffré. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 7 — Une signature IPS bloque une application légitime

**Analyse.** Une règle peut être trop large ou un changement applicatif peut déclencher un faux positif. Récupère le SID ou identifiant, le flux et l'action. Reproduis en laboratoire, confirme le besoin puis applique une exception précise et surveillée. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne désactive pas toute la politique IPS pour une règle. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 8 — Le blocage IPS n'a aucun effet

**Analyse.** Le capteur peut être passif, la règle en mode alerte ou le trafic contourner le capteur inline. Vérifie la topologie, l'action de règle, le mode du moteur et les compteurs de blocage. Teste uniquement dans un laboratoire autorisé. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne déduis pas d'une action configurée que le trafic réel est forcément bloqué. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 9 — Le capteur se sature lors d'un pic de trafic

**Analyse.** Le débit, les sessions, les règles ou la réassemblage peuvent excéder les ressources disponibles. Examine CPU, mémoire, débit, paquets perdus, files et nouvelles connexions. Dimensionne ou répartis la capture après mesure. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne désactive pas arbitrairement les règles les plus protectrices pour faire baisser la charge. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 10 — Une mise à jour change beaucoup le nombre d'alertes

**Analyse.** Les signatures ou le moteur peuvent modifier la classification et les règles correspondantes. Vérifie la version, les notes de version et les identifiants touchés. Compare sur un jeu de captures connu ou un pilote et garde un plan de retour arrière. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne bloque pas définitivement les mises à jour pour conserver un comportement ancien. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 11 — Les alertes n'ont pas d'heure cohérente

**Analyse.** La synchronisation des horloges peut être absente ou incorrecte sur les capteurs et collecteurs. Contrôle NTP, fuseaux, horodatage des événements et délai de collecte. Compare un événement simultané visible dans plusieurs sources. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne reconstitue pas une chronologie de mémoire lorsque les horodatages ne concordent pas. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 12 — Le même incident crée des milliers d'alertes

**Analyse.** Une règle peut générer une alerte par paquet ou par requête sans regroupement de session. Ajoute une déduplication ou un regroupement adapté à la règle et conserve les événements originaux utiles. Surveille les premières et dernières occurrences, les sources et les cibles. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne supprime pas les événements sans garder la piste et les indicateurs nécessaires à l'enquête. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 13 — Un hôte connu commence à contacter de nombreuses destinations

**Analyse.** Une tâche légitime ou une compromission peut produire ce changement comportemental. Compare la baseline, les tâches de maintenance, les processus de l'endpoint, le DNS et les journaux du pare-feu. Détermine si le changement est approuvé avant de bloquer. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne confonds pas une anomalie avec une preuve définitive d'attaque. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 14 — Une alerte élevée n'a aucun effet confirmé sur la cible

**Analyse.** La règle peut détecter une tentative, une activité bloquée ou une séquence qui ressemble à une attaque. Vérifie l'action réelle, les logs serveur, les événements EDR, l'état de vulnérabilité et la chronologie. Classe séparément la tentative, l'exploitation et l'impact. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne déclare pas un incident confirmé sur la seule gravité de la signature. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 15 — Un changement de topologie crée un angle mort

**Analyse.** Le nouveau chemin de trafic peut ne plus traverser le capteur prévu. Compare le schéma avant/après, les routes, les trunks, les liens agrégés et les interfaces miroir. Valide les chemins par un test autorisé et adapte la couverture. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne suppose pas qu'un capteur reste pertinent après un changement de routage. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 16 — Le capteur OT envoie trop d'alertes après un redémarrage d'usine

**Analyse.** Les communications de démarrage ou une nouvelle configuration peuvent différer de la baseline. Vérifie la fenêtre de maintenance, les actifs redémarrés et les protocoles attendus avec les responsables OT. Actualise la baseline après validation du changement. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne passe pas automatiquement en prévention dans un environnement industriel. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 17 — Un port TCP est détecté mais l'application reste inconnue

**Analyse.** La classification peut nécessiter plus de données ou le protocole n'est pas pris en charge. Examine la visibilité, la réassemblage, la version du moteur, les métadonnées et le contexte applicatif. Si besoin, enrichis par logs endpoint ou serveur. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne traite pas un port comme une identité complète de l'application. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 18 — Une règle locale est écrasée à la mise à jour

**Analyse.** Le mécanisme de gestion des règles reconstruit les fichiers de référence. Place la modification dans le mécanisme d'override ou fichier local recommandé, utilise un identifiant approprié et vérifie après mise à jour. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne modifie pas en silence un fichier géré automatiquement. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 19 — Le capteur voit uniquement un sens du trafic

**Analyse.** Le routage asymétrique ou la configuration du miroir peut ne fournir qu'une direction. Vérifie les interfaces source, la direction de capture et les chemins aller/retour. Compare les adresses vues et la couverture du segment. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne dépanne pas le réassemblage d'une session sans confirmer que les deux directions sont capturées. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 20 — Le moteur signale des faux positifs après changement applicatif

**Analyse.** Une nouvelle version peut modifier les requêtes ou protocoles sans que les signatures soient adaptées. Compare les anciennes et nouvelles requêtes, les versions de règles et la fenêtre de déploiement. Teste un ajustement ciblé avec l'équipe applicative. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne crée pas une exclusion globale de toute l'application si une seule signature est en cause. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 21 — La prévention provoque une interruption critique

**Analyse.** La politique de blocage ou le comportement de panne n'a peut-être pas été testé dans le contexte réel. Exécute la procédure d'escalade et de retour arrière, préserve les logs puis évalue la règle responsable et l'impact. Réintroduis la prévention après un pilote adapté. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne réactive pas la même règle en blocage sans preuve que la cause est corrigée. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 22 — Les alertes ne contiennent pas le nom de l'actif

**Analyse.** L'inventaire ou l'enrichissement de contexte est absent ou la résolution des identités est en panne. Vérifie la source du CMDB/actifs, la résolution IP-MAC, les mises à jour et le propriétaire des actifs. Corrèle à partir de l'adresse et de l'horodatage en attendant la correction. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne suppose pas qu'une adresse IP identifie durablement un appareil. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 23 — Un flux est autorisé mais le journal dit 'allowed'

**Analyse.** Le champ d'action peut décrire le résultat du moteur IDS sans exprimer une décision de pare-feu. Consulte la documentation du champ, vérifie le mode passif/inline et les compteurs du dispositif de blocage réel. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne confonds pas action d'alerte et autorisation produite par un pare-feu. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 24 — Des règles personnalisées se chevauchent

**Analyse.** Plusieurs règles peuvent correspondre au même paquet avec des actions différentes selon les priorités de l'engine. Teste sur des captures, examine les priorités et l'ordre effectif, puis dédoublonne et documente les motifs. Ne change pas l'ordre sans vérifier les conséquences. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne suppose pas que l'ordre des fichiers correspond à l'ordre d'évaluation. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 25 — Un capteur n'envoie plus de statistiques

**Analyse.** Le processus peut être actif mais la sortie de statistiques ou le collecteur peut échouer. Vérifie l'état de service, les sorties, l'horloge, les permissions, le réseau de gestion et l'état du SIEM. Teste avec un événement contrôlé. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne considère pas le silence du capteur comme une période sans activité. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 26 — L'analyste ne sait pas qui possède le serveur ciblé

**Analyse.** L'inventaire des actifs ou le lien entre IP et propriétaire est manquant. Enrichis l'alerte avec inventaire, DNS interne, registre IPAM et propriétaire applicatif. Ajoute une action de mise à jour du registre après investigation. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne retarde pas un confinement nécessaire uniquement parce que la fiche d'actif est incomplète ; escalade au responsable opérationnel. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 27 — Une activité de pentest n'était pas annoncée à l'équipe SOC

**Analyse.** Un test autorisé peut générer des alertes authentiques sans contexte partagé. Vérifie l'autorisation, les plages d'origine, la fenêtre et les cibles auprès du responsable. Documente les résultats et améliore le processus de notification des exercices. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne désactive pas les capteurs pour tous les tests futurs. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 28 — La recherche historique ne trouve pas l'événement

**Analyse.** La rétention, les filtres de requête, les indices ou le retard d'ingestion peuvent masquer l'événement. Vérifie l'intervalle, les fuseaux, les filtres, les index et les systèmes sources. Confirme l'existence de l'événement côté capteur et les règles de rétention. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne conclus pas qu'un événement n'existe pas sans vérifier la chaîne de collecte. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 29 — Un comportement nouveau est intégré à la baseline sans enquête

**Analyse.** Une anomalie persistante peut avoir été acceptée trop tôt et devenir invisible. Reviens sur les événements initiaux, identifie la première occurrence et recoupe les changements et les identités. Valide la source et documente la justification avant ajustement de référence. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne laisse pas la baseline normaliser une activité que personne n'a expliquée. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 30 — La règle de blocage arrête un trafic de test mais laisse passer d'autres variantes

**Analyse.** La condition peut être trop spécifique à un seul motif ou format. Utilise plusieurs tests représentatifs et captures contrôlées, analyse ce que la règle détecte réellement et combine des contrôles complémentaires adaptés. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne déduis pas une couverture générale à partir d'un seul cas de test. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

### Cas de dépannage 31 — Une exception a été créée sans date de revue

**Analyse.** L'exception peut survivre à son besoin initial et devenir un angle mort permanent. Attribue un responsable, une justification, un périmètre et une date de révision. Supprime-la lorsque le besoin disparaît et teste la politique après le retrait. Note l'heure, le capteur, le flux, la règle, les pertes de capture et les changements récents. Vérifie les preuves dans les systèmes sources avant d'agir.

**Erreur à éviter.** Ne laisse pas les exceptions de sécurité sans expiration ni contrôle périodique. Une correction est terminée lorsque le test normal réussit, que le scénario suspect est correctement traité et que les événements arrivent à la collecte prévue.

## 28. Défi final — déployer un IDS/IPS de manière graduelle

### Contexte

Une organisation possède un pare-feu périmétrique, une DMZ Web, un réseau utilisateur, des serveurs critiques, un accès VPN et des sauvegardes nocturnes. Les scans de conformité sont autorisés lors de fenêtres définies. Le but est d'améliorer la détection et de prévenir certaines attaques sans perturber le service.

### Correction détaillée

**Étape 1 — Fixer les objectifs.** Identifie les actifs prioritaires et les questions auxquelles les capteurs doivent répondre : flux vers la DMZ, accès aux serveurs critiques, comportement sortant anormal, identité à l'origine d'un événement et signaux endpoint complémentaires.

**Étape 2 — Cartographier les chemins.** Documente les routes, VLAN, points de capture, SPAN/TAP, tunnels et chemins asymétriques. Évalue la capacité et les pertes possibles. Valide la réception avec un trafic de test contrôlé.

**Étape 3 — Déployer passivement.** Charge un jeu de règles approuvé, vérifie la configuration, puis observe les alertes. Mesure le volume, les faux positifs, la charge et les angles morts avant d'envisager un blocage automatique.

**Étape 4 — Construire une baseline.** Documente les applications, destinations, horaires, sauvegardes, scans approuvés et changements planifiés. Chaque exception a une justification, un responsable et une date de revue.

**Étape 5 — Centraliser les événements.** Configure l'envoi au SIEM, synchronise les horloges, surveille les pertes de collecte et enrichis les événements avec les actifs et les identités. Vérifie périodiquement que le pipeline fonctionne de bout en bout.

**Étape 6 — Trier et répondre.** Distingue activité autorisée, faux positif, tentative détectée, trafic bloqué et compromission confirmée. La réponse doit s'appuyer sur les preuves et suivre une procédure de confinement.

**Étape 7 — Valider la prévention.** Dans un laboratoire puis un périmètre pilote, teste les actions drop/reject supportées, les faux positifs, la charge, la redondance, le comportement en panne et le rollback. N'insère pas directement un moteur IPS non validé dans un chemin critique.

**Étape 8 — Maintenir et mesurer.** Suis la couverture, les pertes de paquets, le temps de traitement, la qualité des alertes, les exceptions et les mises à jour. Revois la baseline après chaque changement majeur.

Le défi est réussi quand la couverture des capteurs est démontrée, les règles sont maintenues, les événements arrivent à l'équipe responsable, les exceptions sont justifiées et l'IPS ne perturbe pas les flux métier de façon imprévue.

## 29. Checklist de validation

- Les objectifs de détection et les actifs prioritaires sont définis.
- Chaque capteur a un propriétaire, une version et une couverture documentée.
- Les points de capture correspondent aux chemins réseau réels.
- La perte de paquets, le débit, les files, le CPU et le stockage sont surveillés.
- Les sources de règles sont approuvées et les mises à jour contrôlées.
- Les alertes comprennent les champs utiles à l'investigation.
- Les faux positifs ont une procédure de confirmation et de revue.
- Les règles de blocage sont validées avant le déploiement.
- Le mode de panne de l'IPS et le rollback sont documentés.
- Le SIEM reçoit les événements et les horloges sont cohérentes.
- Les limites de visibilité TLS sont explicites.
- Les scans autorisés et les maintenances sont documentés.
- Les journaux, PCAP et configurations sont protégés.
- Les responsables de réponse et l'escalade sont connus.
- Les tests inoffensifs déclenchent les alertes attendues sans effet inattendu.

## 30. Glossaire

**IDS :** système qui surveille des événements et signale des signes possibles d'incident.

**IPS :** système capable de bloquer certaines communications lorsqu'il est déployé et configuré pour la prévention.

**NIDS/NIPS :** détection ou prévention à partir du trafic réseau.

**HIDS :** capteur logiciel qui observe un hôte.

**NDR :** détection et réponse réseau reposant souvent sur les flux et le comportement.

**Signature :** règle décrivant un motif à détecter.

**Faux positif :** activité légitime signalée ou bloquée à tort.

**Faux négatif :** activité malveillante qui échappe à la détection.

**SPAN :** mécanisme de copie de trafic vers un port de surveillance.

**TAP :** dispositif qui fournit une copie de trafic sur une liaison.

**Baseline :** référence décrivant le comportement attendu.

**SIEM :** plateforme de collecte et de corrélation d'événements de sécurité.

**Fail-open :** le trafic continue si le contrôle échoue, selon le design.

**Fail-closed :** le trafic est interrompu ou bloqué si le contrôle échoue.

**IPS inline :** moteur placé dans le chemin de transmission, capable d'agir sur les paquets.

## 31. Références officielles

- NIST SP 800-94, Guide to Intrusion Detection and Prevention Systems (IDPS) : https://csrc.nist.gov/pubs/sp/800/94/final. NIST signale que le projet de révision de 2012 n'est pas devenu une publication finale.
- Suricata, concept du mode IPS : https://docs.suricata.io/en/latest/ips/ips-concept.html
- Suricata, format des règles : https://docs.suricata.io/en/suricata-8.0.3/rules/intro.html
- Snort 3, structure des règles : https://docs.snort.org/rules/
- Snort 3, journalisation JSON : https://docs.snort.org/start/alert_logging
- Cisco Secure Firewall, gestion des politiques d'intrusion : https://www.cisco.com/c/en/us/td/docs/security/firepower/770/fdm/fptd-fdm-config-guide-770/fptd-fdm-intrusion.html

Les règles, actions et options de prévention varient selon le moteur et la version. Consulte la documentation correspondant au logiciel installé. Déploie les règles de blocage dans un laboratoire puis sur un périmètre pilote validé avant toute mise en production.

Fin du cours.