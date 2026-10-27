### 5.5 Découverte réseau et découverte de bas niveau

La découverte réseau identifie des hôtes ou des services dans un périmètre configuré. La découverte de bas niveau (LLD) détecte des entités d'un hôte, par exemple interfaces, systèmes de fichiers ou objets SNMP, puis utilise des prototypes pour créer les items, triggers ou graphes correspondants. Cette automatisation doit être filtrée : un commutateur peut exposer des interfaces internes, virtuelles ou inutilisées qui ne méritent pas chacune une alerte.

Tester la découverte sur un équipement pilote, examiner les objets générés et contrôler le volume de données avant de la généraliser. Une interface renommée ou supprimée peut laisser des objets historiques ou des graphes obsolètes ; les règles de conservation et de suppression doivent être explicites.

### 5.6 Prétraitement et items dépendants

Le prétraitement transforme ou valide une valeur avant son usage. Il peut convertir des unités, extraire un champ d'un JSON, appliquer une opération arithmétique ou rejeter une valeur invalide. Un item dépendant réutilise une valeur maître déjà collectée afin de produire plusieurs métriques sans répéter la même interrogation coûteuse.

Cette optimisation peut réduire le nombre de requêtes, mais introduit des dépendances : si le format de la réponse source change, plusieurs mesures dérivées peuvent échouer ensemble. Documenter la structure attendue et les erreurs de prétraitement.

### 5.7 Historique, tendances et rétention

L'historique conserve les valeurs individuelles selon la politique définie. Les tendances conservent des agrégats temporels pour les données numériques supportées, tels que minimum, moyenne, maximum et nombre d'échantillons. Elles permettent de visualiser des périodes longues sans conserver toutes les valeurs brutes indéfiniment. Les chaînes et journaux n'ont pas les mêmes propriétés d'agrégation que les métriques numériques.

La rétention influence le coût, l'espace disque et la profondeur d'analyse. Conserver chaque valeur toutes les quelques secondes pendant des années peut faire croître la base rapidement. Supprimer trop tôt les données rend difficile l'explication d'une saturation lente ou d'une panne rare. La politique doit correspondre à l'objectif de dépannage, aux besoins de capacité et aux exigences de conservation. Mesurer la croissance de base sur un pilote plutôt que se fier seulement à une estimation.