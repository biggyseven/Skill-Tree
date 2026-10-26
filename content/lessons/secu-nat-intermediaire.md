# NAT et sécurité du périmètre

## Introduction

La traduction d’adresses réseau (NAT) modifie les adresses IP, et parfois les ports, lorsqu’un paquet traverse une frontière. Elle permet notamment à plusieurs hôtes privés de partager une adresse publique ou à un service interne d’être publié.

Le NAT statique établit une correspondance fixe, le NAT dynamique utilise un pool et PAT différencie les sessions au moyen des ports. Une publication entrante expose un service précis : elle doit donc viser la destination et les ports nécessaires, et non ouvrir largement le réseau interne.

Le NAT n’est pas un mécanisme de sécurité complet. Il doit être associé à un filtrage explicite, au durcissement des services, à une journalisation exploitable et à une révision des redirections pour réduire la surface d’attaque.

## Concepts clés

- **NAT statique** : correspondance stable entre adresses.
- **NAT dynamique** : allocation depuis un pool.
- **PAT / overload** : partage d’une adresse grâce aux ports.
- **Publication** : exposition ciblée d’un service.

## Méthode pratique

1. Recense les flux sortants et les services réellement publiés.
2. Associe la traduction à des règles de filtrage adaptées.
3. Vérifie le chemin retour et les traductions actives.
4. Retire les redirections inutilisées et trace les changements.

## À retenir

Masquer une adresse privée ne remplace ni le filtrage ni le durcissement du service.
