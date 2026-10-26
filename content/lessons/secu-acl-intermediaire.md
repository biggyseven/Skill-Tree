# ACL et filtrage avancé

## Introduction

Une liste de contrôle d’accès (ACL) définit les paquets autorisés ou refusés en fonction des adresses, des protocoles et parfois des ports. Au niveau intermédiaire, il faut traduire une politique de sécurité en règles précises et savoir où les placer.

Les règles sont évaluées de haut en bas et la première correspondance décide de l’action. Lorsqu’aucune règle ne correspond, une interdiction implicite s’applique généralement ; une règle trop large placée trop tôt peut neutraliser les suivantes.

Une ACL fiable tient compte de la source, de la destination, du sens du trafic et de l’interface. Les tests des flux autorisés et refusés, les compteurs et les journaux permettent de confirmer le résultat sans couper un service par erreur.

## Concepts clés

- **ACL standard** : filtre principalement sur la source.
- **ACL étendue** : contrôle source, destination, protocole et éventuellement ports.
- **Ordre** : première règle correspondante appliquée ; refus implicite si aucune ne correspond.
- **Direction** : `in` à l’entrée d’une interface, `out` à sa sortie.

## Méthode pratique

1. Établis une matrice source / destination / service / décision.
2. Place les refus précis avant les autorisations plus larges.
3. Applique l’ACL sur la bonne interface et dans le bon sens.
4. Teste un flux bloqué et plusieurs flux permis, puis relis `show running-config`.

## À retenir

Une syntaxe valide ne suffit pas : il faut tester la politique complète et documenter chaque exception.
