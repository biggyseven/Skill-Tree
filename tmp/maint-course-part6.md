## 7. SNMP : supervision des routeurs et commutateurs

### 7.1 SNMP, MIB et OID

SNMP permet à une station de gestion d'interroger des objets exposés par les équipements. Les données disponibles dépendent des OID, de la MIB, du firmware et des permissions. Deux familles d'équipements peuvent exposer des champs différents ou des limites d'implémentation différentes.

SNMPv1 et SNMPv2c reposent couramment sur des communautés et ne fournissent pas la confidentialité moderne attendue. SNMPv3 propose des niveaux de sécurité avec authentification et confidentialité lorsqu'ils sont configurés correctement. Limiter les sources autorisées, employer des droits de lecture, protéger les identifiants et éviter d'activer l'écriture uniquement pour faciliter la collecte.

Un OID identifie un objet dans une hiérarchie. Les compteurs d'interfaces permettent de mesurer le trafic. Les OID propriétaires peuvent donner d'autres informations, comme température, alimentation, état de module ou alarmes du constructeur. Il faut vérifier la MIB et la référence de l'équipement plutôt que supposer que chaque modèle expose les mêmes données.

### 7.2 Compteur brut et débit calculé

Un compteur d'octets représente un volume accumulé à un moment donné, pas le débit instantané. Le débit se calcule à partir de la différence entre deux lectures séparées par une durée connue. La différence est divisée par le temps écoulé puis multipliée par huit pour passer d'octets par seconde à bits par seconde.

~~~mermaid
flowchart LR
  A[Compteur à t1] --> C[Calcul différence]
  B[Compteur à t2] --> C
  D[Durée entre lectures] --> E[Octets par seconde]
  C --> E
  E --> F[Conversion en bits]
  F --> G[Débit calculé]
~~~

Les redémarrages, débordements de compteur, changements d'interface et données manquantes peuvent créer des pointes artificielles. Utiliser les compteurs adaptés à la vitesse de l'interface et traiter les valeurs incohérentes. La supervision doit aussi connaître la vitesse nominale réelle : un calcul fondé sur une capacité erronée produit un pourcentage trompeur.

Sur une interface importante, surveiller l'état administratif, l'état opérationnel, les trafics entrant et sortant ainsi que les erreurs et discards disponibles. Une utilisation élevée pendant une seconde ne signifie pas nécessairement une saturation persistante. Rapprocher débit, perte, latence, files d'attente, horaires et rôle de la liaison.

### 7.3 Vérifier SNMP depuis le point de collecte

Avant de configurer des centaines d'équipements, tester une cible pilote avec les utilitaires disponibles dans le réseau d'administration. Vérifier d'abord l'accessibilité IP, puis la version SNMP, l'accès UDP 161, l'utilisateur ou la communauté, le niveau de sécurité et l'OID demandé. Utiliser les mécanismes approuvés de fourniture des secrets plutôt que de les écrire dans un historique shell ou un fichier partagé.

Si un contrôle échoue, avancer par couches : connectivité IP, routage, filtrage, version SNMP, utilisateur, niveau de sécurité, secrets, vue de lecture, OID et prise en charge de la MIB. Un échec d'authentification ne justifie pas d'ouvrir SNMP en lecture/écriture ni de permettre toutes les sources.

### 7.4 Polling et traps SNMP

Le polling interroge périodiquement l'équipement pour connaître son état courant et lire ses compteurs. Une trap est un message émis par l'équipement lors d'un événement configuré. Une trap peut arriver rapidement après une panne d'interface ; le polling permet ensuite de confirmer si la condition persiste et d'obtenir des données de tendance.

~~~mermaid
flowchart TD
  A[Équipement réseau] --> B[Polling périodique]
  B --> C[État et compteurs actuels]
  A --> D[Trap sur événement]
  D --> E[Récepteur de traps]
  C --> F[Corrélation]
  E --> F
  F --> G[Incident documenté]
~~~

La réception des traps n'est pas automatique. Il faut un récepteur configuré, la bonne route, un format de message adapté et une intégration vers Zabbix ou Nagios. Une trap perdue ne signifie pas que l'événement n'a pas eu lieu ; une trap reçue ne confirme pas non plus que la panne est encore présente. Les deux mécanismes se complètent.