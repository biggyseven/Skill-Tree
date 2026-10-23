# Haute Disponibilité : Les Fondations

**Niveau :** Administrateur Réseau Junior

La haute disponibilité (HA) est une propriété **architecturale** d’un réseau. Elle ne se résume pas à acheter deux équipements, mais vise à garantir la continuité de service malgré une panne matérielle, logicielle ou humaine. C'est l'art de s'assurer que si une pièce du puzzle disparaît, le réseau continue de fonctionner.

> **Analogie** : Une porte d’entrée unique peut être parfaite. Mais si elle est bloquée, tout le monde reste dehors. Une deuxième porte, avec une signalisation claire et des clés testées, évite que la panne devienne un arrêt total.


## 1. Le problème de la passerelle unique

Dans un réseau classique, tous les ordinateurs (PC, serveurs) ont une **passerelle par défaut** (souvent l'adresse IP du routeur, comme 192.168.1.1). C'est par cette adresse que tout le trafic sort vers Internet.

Si ce routeur tombe en panne, tous les PCs perdent leur connexion Internet, même si le reste du réseau local fonctionne.

## 2. La solution : La redondance

La redondance consiste à doubler les éléments critiques :
- **Alimentation** (deux prises, onduleurs).
- **Câbles** (deux fibres au lieu d'une).
- **Équipements** (deux switches, deux routeurs).

Le but n'est pas d'empêcher la panne, mais de **limiter son impact** et de permettre un retour rapide à la normale.

## 3. Les protocoles de passerelle (FHRP)

Pour que les ordinateurs ne s'aperçoivent de rien si le routeur principal tombe, on utilise une **IP virtuelle**. 
Deux routeurs (R1 et R2) se partagent cette adresse IP. Les PCs utilisent cette IP virtuelle comme passerelle.
- **R1** est le routeur actif (il répond).
- **R2** est en veille (il écoute).

Si R1 tombe, R2 prend le relais **instantanément**. Le PC n'a pas changé de passerelle, il n'a rien vu.

```text
              Réseau local (Postes clients)
                        |
              Passerelle virtuelle 192.168.10.1 (VIP)
                       /             \
          R1 (Actif)                R2 (En veille)
          192.168.10.2             192.168.10.3