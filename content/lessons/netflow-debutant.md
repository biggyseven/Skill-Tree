# IP SLA & NetFlow — Niveau Débutant

**Fichier :** `netflow-debutant.md`  
**Parcours :** Réseaux Cisco — Débutant  
**Prérequis :** adressage IPv4, passerelle par défaut, routage statique, notions de ping et de ports TCP/UDP.  
**Environnement visé :** Cisco IOS / IOS XE, avec des variantes selon le modèle et la version. Les exemples d’export NetFlow utilisent Flexible NetFlow lorsqu’il est disponible.

> **Objectif du cours** — Savoir mesurer la disponibilité et les performances d’un chemin réseau avec IP SLA, observer les conversations IP avec NetFlow, puis utiliser ces deux sources d’information pour diagnostiquer un problème simple. IP SLA et NetFlow sont complémentaires, mais ne mesurent pas la même chose.

## Plan du cours

1. Observer un réseau : disponibilité, performance et trafic
2. Comprendre IP SLA
3. Configurer une opération ICMP Echo
4. Relier IP SLA au suivi d’une route
5. Comprendre NetFlow et la notion de flux
6. Découvrir Flexible NetFlow : record, monitor, exporter, collector
7. Configurer une collecte NetFlow simple
8. Lire les résultats et dépanner
9. Laboratoire guidé et exercices corrigés
10. Quiz final et fiche de révision


## 1. Pourquoi mesurer et observer le réseau ?

Un réseau peut sembler « en panne » pour plusieurs raisons différentes. Une interface peut être administrativement désactivée, un lien peut être coupé, la route peut manquer, une ACL peut bloquer le trafic, ou un serveur peut être accessible au niveau IP mais ne plus fournir le service attendu. À l’inverse, un réseau peut rester joignable tout en étant lent ou saturé.

Trois questions doivent être séparées :

- **Disponibilité :** est-ce que la cible répond à la sonde choisie ?
- **Performance :** combien de temps prend l’aller-retour ? Y a-t-il de la gigue ou des pertes ?
- **Utilisation :** quelles conversations échangent du trafic, et combien de paquets ou d’octets représentent-elles ?

IP SLA répond surtout aux deux premières questions. NetFlow aide à répondre à la troisième. Aucun des deux ne remplace à lui seul une capture de paquets, les journaux, les compteurs d’interface ou les tests applicatifs.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="diag1-title diag1-desc">
  <title id="diag1-title">Trois angles complémentaires pour comprendre un incident</title>
  <desc id="diag1-desc">IP SLA mesure la réponse et les délais, NetFlow décrit les conversations et le volume, les outils de diagnostic complètent l'analyse.</desc>
  <defs><linearGradient id="d1bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101b2d"/><stop offset="1" stop-color="#08111e"/></linearGradient><marker id="d1arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#83a4c7"/></marker></defs>
  <rect x="1" y="1" width="958" height="348" rx="20" fill="url(#d1bg)" stroke="#29415d"/>
  <text x="480" y="36" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Trois angles pour diagnostiquer un incident</text>
  <rect x="42" y="78" width="262" height="172" rx="15" fill="#142c3b" stroke="#38bdf8" stroke-width="2"/>
  <circle cx="75" cy="111" r="15" fill="#38bdf8"/><text x="75" y="117" text-anchor="middle" fill="#072033" font-size="18" font-weight="700">1</text>
  <text x="173" y="116" text-anchor="middle" fill="#eaf8ff" font-size="21" font-weight="700">IP SLA</text>
  <text x="173" y="150" text-anchor="middle" fill="#c9e7f5" font-size="15">La cible répond-elle ?</text>
  <text x="173" y="174" text-anchor="middle" fill="#c9e7f5" font-size="15">Combien de millisecondes ?</text>
  <text x="173" y="211" text-anchor="middle" fill="#38bdf8" font-size="13">Disponibilité · délai · gigue</text>
  <rect x="349" y="78" width="262" height="172" rx="15" fill="#182d25" stroke="#4ade80" stroke-width="2"/>
  <circle cx="382" cy="111" r="15" fill="#4ade80"/><text x="382" y="117" text-anchor="middle" fill="#092513" font-size="18" font-weight="700">2</text>
  <text x="480" y="116" text-anchor="middle" fill="#edfff2" font-size="21" font-weight="700">NetFlow</text>
  <text x="480" y="150" text-anchor="middle" fill="#d3f6dc" font-size="15">Qui parle avec qui ?</text>
  <text x="480" y="174" text-anchor="middle" fill="#d3f6dc" font-size="15">Combien de trafic ?</text>
  <text x="480" y="211" text-anchor="middle" fill="#4ade80" font-size="13">Flux · paquets · octets</text>
  <rect x="656" y="78" width="262" height="172" rx="15" fill="#30251a" stroke="#fbbf24" stroke-width="2"/>
  <circle cx="689" cy="111" r="15" fill="#fbbf24"/><text x="689" y="117" text-anchor="middle" fill="#2c1c00" font-size="18" font-weight="700">3</text>
  <text x="787" y="116" text-anchor="middle" fill="#fff7e4" font-size="21" font-weight="700">Diagnostic</text>
  <text x="787" y="150" text-anchor="middle" fill="#fce8bd" font-size="15">Routes, ACL, interface ?</text>
  <text x="787" y="174" text-anchor="middle" fill="#fce8bd" font-size="15">Application et journaux ?</text>
  <text x="787" y="211" text-anchor="middle" fill="#fbbf24" font-size="13">Contexte · hypothèse · preuve</text>
  <path d="M304 164 H338" stroke="#83a4c7" stroke-width="2" marker-end="url(#d1arr)"/><path d="M611 164 H645" stroke="#83a4c7" stroke-width="2" marker-end="url(#d1arr)"/>
  <text x="480" y="290" text-anchor="middle" fill="#e2eaf4" font-size="16" font-weight="600">Une mesure isolée ne suffit pas : recouper les indices.</text>
  <text x="480" y="318" text-anchor="middle" fill="#98abc2" font-size="13">Exemple : ping réussi + latence élevée + hausse du trafic sur une interface.</text>
</svg>

### Exemple de raisonnement

Un utilisateur signale que l’accès à une application est lent.

1. IP SLA montre que les sondes ICMP répondent, mais que le délai passe de 12 ms à 180 ms.
2. NetFlow montre une forte hausse des octets d’un flux entre deux sous-réseaux.
3. Les compteurs d’interface et les journaux aident à confirmer si le lien est congestionné ou si le serveur ralentit.

Cette corrélation oriente l’enquête, mais elle ne prouve pas à elle seule que le flux observé est la cause de la lenteur.

## 2. IP SLA : mesurer activement un chemin

**IP SLA** (IP Service Level Agreements) est une fonction de mesure active disponible sur de nombreuses plateformes Cisco. Un équipement source exécute une opération vers une destination et enregistre des statistiques. Le type de sonde détermine ce qui est réellement testé.

### 2.1 Opérations courantes

| Opération | Ce qu’elle observe | Limite principale |
|---|---|---|
| ICMP Echo | Réponse ICMP et temps aller-retour estimé | Un ping réussi ne prouve pas que l’application fonctionne. |
| UDP Jitter | Délai, variation de délai et pertes sur des échanges UDP | Nécessite généralement un répondant IP SLA compatible côté destination. |
| TCP Connect | Temps nécessaire pour établir une connexion TCP | Dépend du port ciblé et de ce que le serveur accepte. |
| DNS | Temps et résultat d’une résolution DNS | La syntaxe et les options dépendent de la plateforme. |
| HTTP / opérations applicatives prises en charge | Réponse d’un service ciblé | Le type exact et les prérequis dépendent de la version IOS/IOS XE. |

Pour débuter, ICMP Echo est le plus simple : le routeur envoie une requête à l’adresse cible, puis mesure le temps de réponse si une réponse revient. Le routeur ne mesure pas une « vitesse Internet » universelle ; il mesure un chemin, depuis un point précis, vers une cible précise, avec une méthode précise.

### 2.2 Le cycle d’une sonde ICMP Echo

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="diag2-title diag2-desc">
  <title id="diag2-title">Cycle d'une sonde IP SLA ICMP Echo</title>
  <desc id="diag2-desc">Le routeur source envoie une requête ICMP Echo, la cible répond avec Echo Reply, puis la mesure et son statut sont enregistrés localement.</desc>
  <defs><linearGradient id="d2bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111c30"/><stop offset="1" stop-color="#080f1c"/></linearGradient><marker id="d2blue" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#38bdf8"/></marker><marker id="d2green" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#4ade80"/></marker></defs>
  <rect x="1" y="1" width="958" height="388" rx="20" fill="url(#d2bg)" stroke="#29415d"/>
  <text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Cycle d’une opération ICMP Echo</text>
  <rect x="42" y="80" width="220" height="110" rx="14" fill="#152c43" stroke="#38bdf8" stroke-width="2"/><text x="152" y="112" text-anchor="middle" fill="#eaf8ff" font-size="18" font-weight="700">Routeur source</text><text x="152" y="138" text-anchor="middle" fill="#c7e7f8" font-size="14">IP SLA operation 10</text><text x="152" y="162" text-anchor="middle" fill="#7dd3fc" font-size="14">Déclenche la sonde</text>
  <rect x="365" y="80" width="230" height="110" rx="14" fill="#18263a" stroke="#8195b2" stroke-width="2"/><text x="480" y="112" text-anchor="middle" fill="#eff5ff" font-size="18" font-weight="700">Réseau IP</text><text x="480" y="138" text-anchor="middle" fill="#c3d0e1" font-size="14">Routes · ACL · liens</text><text x="480" y="162" text-anchor="middle" fill="#a6bad2" font-size="14">Chemin aller / retour</text>
  <rect x="698" y="80" width="220" height="110" rx="14" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="808" y="112" text-anchor="middle" fill="#edfff2" font-size="18" font-weight="700">Cible</text><text x="808" y="138" text-anchor="middle" fill="#d1fae0" font-size="14">192.0.2.10</text><text x="808" y="162" text-anchor="middle" fill="#86efac" font-size="14">Répond si autorisé</text>
  <path d="M262 112 H355" stroke="#38bdf8" stroke-width="3" marker-end="url(#d2blue)"/><text x="309" y="99" text-anchor="middle" fill="#7dd3fc" font-size="13">Echo Request</text>
  <path d="M595 112 H688" stroke="#38bdf8" stroke-width="3" marker-end="url(#d2blue)"/><text x="642" y="99" text-anchor="middle" fill="#7dd3fc" font-size="13">ICMP</text>
  <path d="M698 165 H605" stroke="#4ade80" stroke-width="3" marker-end="url(#d2green)"/><text x="650" y="184" text-anchor="middle" fill="#86efac" font-size="13">Echo Reply</text>
  <path d="M365 165 H272" stroke="#4ade80" stroke-width="3" marker-end="url(#d2green)"/>
  <rect x="80" y="236" width="800" height="105" rx="14" fill="#111f31" stroke="#405773"/><text x="480" y="264" text-anchor="middle" fill="#f1f6ff" font-size="18" font-weight="700">Résultat enregistré sur le routeur source</text>
  <rect x="111" y="282" width="208" height="39" rx="8" fill="#153047" stroke="#38bdf8"/><text x="215" y="307" text-anchor="middle" fill="#d9f4ff" font-size="15">Succès / échec</text>
  <rect x="376" y="282" width="208" height="39" rx="8" fill="#173125" stroke="#4ade80"/><text x="480" y="307" text-anchor="middle" fill="#d1fae0" font-size="15">Temps aller-retour</text>
  <rect x="641" y="282" width="208" height="39" rx="8" fill="#30251a" stroke="#fbbf24"/><text x="745" y="307" text-anchor="middle" fill="#fff0c2" font-size="15">Historique / seuils</text>
  <text x="480" y="367" text-anchor="middle" fill="#9fb1c9" font-size="13">La sonde vérifie la réponse ICMP ; elle ne valide pas à elle seule le service applicatif.</text>
</svg>

### 2.3 Notions à distinguer

- **Fréquence (`frequency`)** : intervalle auquel l’opération est répétée, selon les contraintes de la plateforme.
- **Timeout** : délai maximal d’attente d’une réponse avant de considérer la tentative comme expirée.
- **RTT (Round-Trip Time)** : temps entre l’envoi de la sonde et la réception de la réponse.
- **Perte** : absence de réponse attendue. Elle peut être liée à la connectivité, au filtrage, à la charge ou à la politique ICMP de la cible.
- **Source de la sonde** : interface ou adresse source employée. Elle influence le chemin pris et la validité du test.
- **Seuil (threshold)** : valeur utilisée pour interpréter la mesure ou déclencher une action, selon les fonctions prises en charge.

Un délai de 0 ms affiché ou une valeur manquante ne signifie pas forcément que le réseau est instantané : interprète le résultat à l’aide de l’état de l’opération et de l’historique. Les mesures sont également influencées par le moment du test et la charge du routeur.

## 3. Configurer IP SLA ICMP Echo

### 3.1 Topologie d’exemple

On veut vérifier depuis R1 que la cible de test `192.0.2.10` répond. Les adresses de documentation utilisées ici sont des exemples réservés à la documentation ; remplace-les dans ton laboratoire par le plan d’adressage réel.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 330" role="img" aria-labelledby="diag3-title diag3-desc">
  <title id="diag3-title">Topologie de base pour IP SLA</title>
  <desc id="diag3-desc">R1 envoie une sonde via un routeur intermédiaire vers un serveur de test; les adresses servent d'exemple documentaire.</desc>
  <defs><linearGradient id="d3bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2c"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d3arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8aa4c3"/></marker></defs>
  <rect x="1" y="1" width="958" height="328" rx="20" fill="url(#d3bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Topologie de mesure</text>
  <rect x="50" y="98" width="210" height="112" rx="14" fill="#152c43" stroke="#38bdf8" stroke-width="2"/><text x="155" y="130" text-anchor="middle" fill="#eaf8ff" font-size="21" font-weight="700">R1</text><text x="155" y="157" text-anchor="middle" fill="#bae6fd" font-size="15">Source IP SLA</text><text x="155" y="183" text-anchor="middle" fill="#7dd3fc" font-size="14">192.0.2.1 (exemple)</text>
  <rect x="375" y="98" width="210" height="112" rx="14" fill="#202c3e" stroke="#8aa4c3" stroke-width="2"/><text x="480" y="130" text-anchor="middle" fill="#eef5ff" font-size="21" font-weight="700">Réseau</text><text x="480" y="157" text-anchor="middle" fill="#cbd5e1" font-size="15">Routage + ACL</text><text x="480" y="183" text-anchor="middle" fill="#a8bdd6" font-size="14">Chemin aller et retour</text>
  <rect x="700" y="98" width="210" height="112" rx="14" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="805" y="130" text-anchor="middle" fill="#edfff2" font-size="21" font-weight="700">Cible de test</text><text x="805" y="157" text-anchor="middle" fill="#d1fae0" font-size="15">192.0.2.10</text><text x="805" y="183" text-anchor="middle" fill="#86efac" font-size="14">ICMP autorisé</text>
  <path d="M260 154 H365" stroke="#38bdf8" stroke-width="3" marker-end="url(#d3arr)"/><path d="M585 154 H690" stroke="#38bdf8" stroke-width="3" marker-end="url(#d3arr)"/>
  <text x="480" y="246" text-anchor="middle" fill="#e2eaf4" font-size="16" font-weight="600">Choisir une cible pertinente</text><text x="480" y="272" text-anchor="middle" fill="#9fb1c9" font-size="14">Une cible proche teste surtout l'accès local ; une cible distante teste davantage de segments.</text><text x="480" y="296" text-anchor="middle" fill="#fbbf24" font-size="13">Le ping peut être filtré même si un service applicatif reste disponible.</text>
</svg>

### 3.2 Exemple de configuration

> **À adapter :** la syntaxe et les fonctions disponibles varient selon IOS/IOS XE, le matériel et les licences. Vérifie la CLI avec `?` et la documentation de la version avant d’utiliser cet exemple en production.

```text
R1# configure terminal
R1(config)# ip sla 10
R1(config-ip-sla)# icmp-echo 192.0.2.10 source-interface GigabitEthernet0/0
R1(config-ip-sla-echo)# timeout 1000
R1(config-ip-sla-echo)# frequency 10
R1(config-ip-sla-echo)# exit
R1(config)# ip sla schedule 10 life forever start-time now
R1(config)# end
```

**Lecture de la configuration :**

- `ip sla 10` crée l’opération numéro 10.
- `icmp-echo 192.0.2.10` définit la cible de la sonde.
- `source-interface GigabitEthernet0/0` choisit une interface source ; l’interface doit exister et convenir au chemin testé.
- `timeout 1000` indique un délai maximal de 1 000 ms dans les versions qui prennent en charge cette forme de commande.
- `frequency 10` demande une nouvelle mesure toutes les 10 secondes. La relation entre fréquence, timeout et charge doit être vérifiée sur la plateforme.
- `ip sla schedule ... start-time now` démarre l’opération et la laisse fonctionner tant qu’elle n’est pas arrêtée ou supprimée.

Dans certaines versions, le mode CLI après `icmp-echo` est le mode de configuration IP SLA Echo ; le prompt peut donc changer avant de saisir `timeout` et `frequency`. Suis les modes de configuration indiqués par l’équipement.

### 3.3 Vérifier l’opération

```text
show ip sla configuration
show ip sla statistics
show ip sla summary
```

Toutes ces commandes ne sont pas forcément disponibles sous la même forme sur chaque plate-forme. Le résultat doit notamment permettre d’identifier l’opération, son état, le dernier résultat, le RTT et l’historique lorsque celui-ci est pris en charge.

Si la sonde échoue, vérifie d’abord l’adresse cible, la source sélectionnée, la route utilisée, les ACL et le comportement ICMP de la cible. Ne conclus pas immédiatement à une panne physique.

## 4. Utiliser IP SLA pour suivre une route

IP SLA peut alimenter un objet de suivi (`track`). Une route statique principale peut être associée à cet objet : si la condition de suivi devient indisponible, la route suivie peut être retirée de la table de routage, ce qui permet à une route de secours de devenir préférable.

**Attention :** cela n’est pas une bascule universelle ni instantanée. Le résultat dépend du choix de la cible, du timeout, de la fréquence, des temporisations de suivi, de la route de retour et du support du mécanisme par la version IOS/IOS XE.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-labelledby="diag4-title diag4-desc">
  <title id="diag4-title">Chaîne IP SLA, track et bascule de route</title>
  <desc id="diag4-desc">La sonde IP SLA fournit un état à l'objet track. Quand le suivi du prochain saut principal passe de up à down, la route statique principale peut être retirée et une route de secours peut être utilisée.</desc>
  <defs><linearGradient id="d4bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#08111e"/></linearGradient><marker id="d4arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="408" rx="20" fill="url(#d4bg)" stroke="#29415d"/><text x="480" y="34" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">De la mesure à la décision de routage</text>
  <rect x="38" y="79" width="202" height="96" rx="13" fill="#152c43" stroke="#38bdf8" stroke-width="2"/><text x="139" y="111" text-anchor="middle" fill="#eaf8ff" font-size="18" font-weight="700">IP SLA 10</text><text x="139" y="138" text-anchor="middle" fill="#bae6fd" font-size="14">Sonde de la cible</text><text x="139" y="158" text-anchor="middle" fill="#7dd3fc" font-size="12">Succès / échec</text>
  <rect x="285" y="79" width="202" height="96" rx="13" fill="#202a3b" stroke="#a5b4fc" stroke-width="2"/><text x="386" y="111" text-anchor="middle" fill="#eef2ff" font-size="18" font-weight="700">track 10</text><text x="386" y="138" text-anchor="middle" fill="#dbe3ff" font-size="14">Convertit le résultat</text><text x="386" y="158" text-anchor="middle" fill="#a5b4fc" font-size="12">État suivi</text>
  <rect x="532" y="79" width="390" height="96" rx="13" fill="#182b22" stroke="#4ade80" stroke-width="2"/><text x="727" y="111" text-anchor="middle" fill="#edfff2" font-size="18" font-weight="700">Table de routage</text><text x="727" y="138" text-anchor="middle" fill="#d1fae0" font-size="14">Route principale suivie / route de secours</text><text x="727" y="158" text-anchor="middle" fill="#86efac" font-size="12">Décision fondée sur l’état + les préférences de route</text>
  <path d="M240 127 H275" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d4arr)"/><path d="M487 127 H522" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d4arr)"/>
  <rect x="64" y="226" width="382" height="126" rx="13" fill="#142f25" stroke="#4ade80"/><text x="255" y="254" text-anchor="middle" fill="#d1fae0" font-size="18" font-weight="700">Scénario A · Sonde OK</text><text x="255" y="283" text-anchor="middle" fill="#d1fae0" font-size="15">track = up</text><text x="255" y="308" text-anchor="middle" fill="#b7f7c9" font-size="14">La route principale reste candidate</text><text x="255" y="331" text-anchor="middle" fill="#86efac" font-size="12">Sous réserve de la table de routage réelle</text>
  <rect x="514" y="226" width="382" height="126" rx="13" fill="#35251d" stroke="#fb923c"/><text x="705" y="254" text-anchor="middle" fill="#ffedd5" font-size="18" font-weight="700">Scénario B · Sonde échoue</text><text x="705" y="283" text-anchor="middle" fill="#ffedd5" font-size="15">track = down</text><text x="705" y="308" text-anchor="middle" fill="#fed7aa" font-size="14">La route suivie peut être retirée</text><text x="705" y="331" text-anchor="middle" fill="#fdba74" font-size="12">La route de secours peut alors être retenue</text>
  <text x="480" y="385" text-anchor="middle" fill="#9fb1c9" font-size="13">Le mécanisme doit surveiller une cible qui reflète réellement la santé du chemin à protéger.</text>
</svg>

### 4.1 Exemple IP SLA + track + routes statiques

Exemple de principe sur R1. Le prochain saut principal et le prochain saut de secours sont illustratifs ; assure-toi que les deux chemins sont routables et que la sonde ne peut pas continuer à réussir via un chemin qui ne représente pas celui que tu veux contrôler.

```text
R1(config)# ip sla 10
R1(config-ip-sla)# icmp-echo 192.0.2.10 source-interface GigabitEthernet0/0
R1(config-ip-sla-echo)# timeout 1000
R1(config-ip-sla-echo)# frequency 10
R1(config)# ip sla schedule 10 life forever start-time now
R1(config)# track 10 ip sla 10 reachability
R1(config)# ip route 0.0.0.0 0.0.0.0 198.51.100.1 track 10
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1 200
```

Ici, la route de secours utilise une distance administrative plus élevée à titre d’illustration. Les distances, adresses et capacités doivent être ajustées à la topologie réelle. Une seule route par défaut n’est pas automatiquement suffisante pour garantir une bonne bascule : la sonde doit être liée à la disponibilité de la destination pertinente et le trafic doit pouvoir revenir par le chemin attendu.

**Vérification :** consulte la sortie de `show track`, `show ip sla statistics` et `show ip route`. Sur certaines versions, la syntaxe ou les sous-commandes de suivi peuvent différer. Teste les scénarios de succès et de panne dans un environnement contrôlé avant de modifier un routeur en production.

## 5. NetFlow : observer les conversations IP

**NetFlow** est un mécanisme d’observation du trafic. Un équipement identifie des paquets appartenant à un même flux selon des champs de clé, maintient des compteurs, puis fournit des enregistrements à un outil collecteur. Le but est de comprendre les conversations et leur volume, pas de lire intégralement le contenu applicatif.

### 5.1 Qu’est-ce qu’un flux ?

Une définition classique de flux IPv4 s’appuie sur le « cinq-tuple » :

1. Adresse IP source
2. Adresse IP destination
3. Protocole IP (TCP, UDP, ICMP, etc.)
4. Port source, lorsqu’il existe
5. Port destination, lorsqu’il existe

Le protocole IP et les ports dépendent du paquet. ICMP, par exemple, n’utilise pas des ports TCP/UDP ; la présence de ces champs dans un enregistrement dépend donc du type de trafic et de la configuration du record. Une implémentation peut inclure d’autres clés, comme les interfaces d’entrée/sortie, le sens du flux, le VLAN, les adresses IPv6 ou des informations de couche 2.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-labelledby="diag5-title diag5-desc">
  <title id="diag5-title">Les cinq champs classiques d'un flux IP</title>
  <desc id="diag5-desc">Un flux est caractérisé classiquement par l'adresse IP source, l'adresse IP destination, le protocole, le port source et le port destination.</desc>
  <defs><linearGradient id="d5bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient></defs>
  <rect x="1" y="1" width="958" height="408" rx="20" fill="url(#d5bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Le cinq-tuple d’un flux IP classique</text>
  <rect x="42" y="83" width="262" height="112" rx="13" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="173" y="114" text-anchor="middle" fill="#eaf8ff" font-size="17" font-weight="700">1 · IP source</text><text x="173" y="146" text-anchor="middle" fill="#bae6fd" font-size="17">10.10.10.25</text><text x="173" y="172" text-anchor="middle" fill="#7dd3fc" font-size="13">Qui envoie ?</text>
  <rect x="349" y="83" width="262" height="112" rx="13" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="480" y="114" text-anchor="middle" fill="#eaf8ff" font-size="17" font-weight="700">2 · IP destination</text><text x="480" y="146" text-anchor="middle" fill="#bae6fd" font-size="17">203.0.113.8</text><text x="480" y="172" text-anchor="middle" fill="#7dd3fc" font-size="13">Qui reçoit ?</text>
  <rect x="656" y="83" width="262" height="112" rx="13" fill="#22263c" stroke="#a5b4fc" stroke-width="2"/><text x="787" y="114" text-anchor="middle" fill="#eef2ff" font-size="17" font-weight="700">3 · Protocole IP</text><text x="787" y="146" text-anchor="middle" fill="#dbe3ff" font-size="17">TCP · UDP · ICMP</text><text x="787" y="172" text-anchor="middle" fill="#c7d2fe" font-size="13">Quel type de transport ?</text>
  <rect x="177" y="231" width="262" height="112" rx="13" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="308" y="262" text-anchor="middle" fill="#edfff2" font-size="17" font-weight="700">4 · Port source</text><text x="308" y="294" text-anchor="middle" fill="#d1fae0" font-size="17">51514 (exemple TCP)</text><text x="308" y="320" text-anchor="middle" fill="#86efac" font-size="13">Côté émetteur</text>
  <rect x="521" y="231" width="262" height="112" rx="13" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="652" y="262" text-anchor="middle" fill="#edfff2" font-size="17" font-weight="700">5 · Port destination</text><text x="652" y="294" text-anchor="middle" fill="#d1fae0" font-size="17">443 (HTTPS, exemple)</text><text x="652" y="320" text-anchor="middle" fill="#86efac" font-size="13">Côté service</text>
  <text x="480" y="376" text-anchor="middle" fill="#e2eaf4" font-size="15" font-weight="600">Une combinaison de clés distingue un flux d’un autre.</text><text x="480" y="396" text-anchor="middle" fill="#9fb1c9" font-size="12">Les ports ne s’appliquent pas à toutes les familles de paquets ; le record peut utiliser d’autres clés.</text>
</svg>

### 5.2 Ce que NetFlow peut et ne peut pas dire

NetFlow peut fournir, suivant le record et la plateforme, des adresses, ports, protocole, interfaces, nombre de paquets, nombre d’octets et des timestamps. Ces informations permettent de repérer des « top talkers », des changements de volume, des flux inhabituels ou les applications réseau probables à partir de leurs ports et métadonnées.

NetFlow ne doit pas être confondu avec :

- **Une capture de paquets (PCAP)**, qui peut conserver des paquets individuels et éventuellement une partie de leur charge utile.
- **Un journal applicatif**, qui peut contenir des codes d’erreur ou le contexte d’une transaction.
- **Un IDS/IPS**, qui analyse des signatures ou des comportements selon une politique de sécurité.
- **Un test de performance actif**, comme IP SLA, qui génère volontairement des sondes et en mesure les résultats.

La visibilité dépend de l’endroit où l’on applique NetFlow, du sens d’observation (`input` ou `output`), du record choisi, de l’échantillonnage et des délais d’export. Le même trafic peut être observé sur plusieurs interfaces ; il faut éviter de sommer des observations doublées sans comprendre le point de mesure.

## 6. Flexible NetFlow : les composants

Les configurations récentes de type **Flexible NetFlow (FNF)** séparent plusieurs rôles. Cette séparation rend la collecte personnalisable, mais impose de construire et de relier les objets dans le bon ordre.

- **Flow record :** décrit les clés utilisées pour identifier le flux et les champs additionnels collectés.
- **Flow monitor :** associe un record à un cache et éventuellement à un exporter. Il est ensuite appliqué à une interface.
- **Flow exporter :** décrit l’adresse du collecteur, l’adresse source d’export, le transport et le format de sortie disponibles.
- **Collector :** logiciel ou appliance qui reçoit les enregistrements, les interprète et les rend consultables.
- **Flow sampler (optionnel) :** permet de ne traiter qu’un sous-ensemble des paquets, selon le mécanisme de la plate-forme, pour diminuer la charge.

Le record répond à « quelles informations ? », le monitor à « comment garder les statistiques ? », l’exporter à « où et comment envoyer ? », et le collector à « où analyser les résultats ? ».

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 460" role="img" aria-labelledby="diag6-title diag6-desc">
  <title id="diag6-title">Chaîne Flexible NetFlow de l'interface au collecteur</title>
  <desc id="diag6-desc">Les paquets arrivent sur une interface surveillée; le flow monitor combine record et cache, puis le flow exporter transmet les enregistrements au collecteur.</desc>
  <defs><linearGradient id="d6bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d6arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="458" rx="20" fill="url(#d6bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Flexible NetFlow : construction et circulation</text>
  <rect x="36" y="95" width="172" height="113" rx="12" fill="#202a3b" stroke="#8aa4c3" stroke-width="2"/><text x="122" y="125" text-anchor="middle" fill="#eff5ff" font-size="17" font-weight="700">Interface</text><text x="122" y="151" text-anchor="middle" fill="#cbd5e1" font-size="14">Input / output</text><text x="122" y="177" text-anchor="middle" fill="#9fb1c9" font-size="12">Paquets observés</text>
  <rect x="260" y="72" width="190" height="75" rx="11" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="355" y="100" text-anchor="middle" fill="#eaf8ff" font-size="17" font-weight="700">Flow record</text><text x="355" y="124" text-anchor="middle" fill="#bae6fd" font-size="13">Clés + champs collectés</text>
  <rect x="260" y="169" width="190" height="75" rx="11" fill="#1d2b3e" stroke="#a5b4fc" stroke-width="2"/><text x="355" y="197" text-anchor="middle" fill="#eef2ff" font-size="17" font-weight="700">Flow monitor</text><text x="355" y="221" text-anchor="middle" fill="#dbe3ff" font-size="13">Record + cache</text>
  <rect x="509" y="119" width="190" height="113" rx="12" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="604" y="151" text-anchor="middle" fill="#edfff2" font-size="17" font-weight="700">Flow exporter</text><text x="604" y="178" text-anchor="middle" fill="#d1fae0" font-size="14">Destination + source</text><text x="604" y="201" text-anchor="middle" fill="#86efac" font-size="13">UDP / format supporté</text>
  <rect x="755" y="119" width="170" height="113" rx="12" fill="#30251a" stroke="#fbbf24" stroke-width="2"/><text x="840" y="151" text-anchor="middle" fill="#fff7e4" font-size="17" font-weight="700">Collector</text><text x="840" y="178" text-anchor="middle" fill="#fce8bd" font-size="14">Réception</text><text x="840" y="201" text-anchor="middle" fill="#fbbf24" font-size="13">Analyse / rapports</text>
  <path d="M208 150 H250" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d6arr)"/><path d="M355 147 V159" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d6arr)"/><path d="M450 206 H482 V177 H499" stroke="#9bb2ce" stroke-width="2.5" fill="none" marker-end="url(#d6arr)"/><path d="M699 176 H745" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d6arr)"/>
  <rect x="85" y="294" width="790" height="105" rx="13" fill="#0e1b2b" stroke="#405773"/><text x="480" y="322" text-anchor="middle" fill="#f1f6ff" font-size="17" font-weight="700">À retenir : les objets doivent être reliés explicitement</text>
  <text x="480" y="351" text-anchor="middle" fill="#c6d4e5" font-size="14">Record → Monitor ; Exporter → Monitor ; Monitor → interface ; Collector → reçoit l’export.</text><text x="480" y="376" text-anchor="middle" fill="#9fb1c9" font-size="13">Un monitor sans application sur interface ne fournit pas la visibilité attendue sur ce trafic.</text>
  <text x="480" y="430" text-anchor="middle" fill="#8fa5c0" font-size="13">Les commandes et formats possibles varient selon IOS/IOS XE, modèle et version.</text>
</svg>

### 6.1 NetFlow v5, v9 et IPFIX : idée générale

- **NetFlow v5** est un format historique simple, avec une structure de champs plus figée, souvent associé au NetFlow traditionnel IPv4.
- **NetFlow v9** utilise des templates décrivant les champs exportés, ce qui permet une structure plus flexible.
- **IPFIX** est un protocole standardisé pour l’export d’informations de flux, inspiré du modèle à templates.

La compatibilité précise dépend du matériel, du logiciel et du collecteur. Le fait qu’un équipement sache générer un format ne garantit pas qu’un collecteur particulier le prenne en charge correctement : vérifie le format configuré des deux côtés.

## 7. Configurer Flexible NetFlow : exemple de laboratoire

### 7.1 Préparer la collecte

On suppose :

- Routeur d’observation : `R1`
- Interface étudiée : `GigabitEthernet0/1`
- Adresse source des exports : Loopback0
- Collecteur NetFlow : `192.0.2.50`
- Port UDP du collecteur : `2055` dans cet exemple

Les valeurs d’adresses et de ports sont illustratives. Le collecteur doit être joignable depuis l’adresse source d’export, et les ACL intermédiaires doivent permettre le transport utilisé. Le port UDP 2055 est courant mais pas universel : configure le même port côté routeur et côté collecteur.

### 7.2 Construire record, exporter et monitor

L’exemple suivant illustre une configuration Flexible NetFlow de style IOS XE. **Il n’est pas universel** : certains appareils utilisent un ensemble de commandes ou de champs différent. Vérifie d’abord `show version`, la documentation de la plate-forme et l’aide CLI (`?`).

```text
R1# configure terminal
!
flow record IPV4-BASIC-RECORD
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 collect counter packets long
 collect counter bytes long
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
flow exporter NF-EXPORTER
 destination 192.0.2.50
 source Loopback0
 transport udp 2055
 export-protocol netflow-v9
!
flow monitor IPV4-BASIC-MONITOR
 record IPV4-BASIC-RECORD
 exporter NF-EXPORTER
 cache timeout active 60
 cache timeout inactive 15
!
interface GigabitEthernet0/1
 ip flow monitor IPV4-BASIC-MONITOR input
!
end
```

**Points à vérifier avant application :**

- Le modèle prend-il en charge les commandes `flow record`, `flow exporter` et `flow monitor` ?
- La forme exacte de `export-protocol` est-elle disponible pour ce logiciel ?
- Le nom d’interface est-il correct ?
- Loopback0 existe-t-elle et est-elle routable depuis le collecteur ?
- Le collecteur reçoit-il le même format et le même port ?
- Le record sélectionne-t-il les champs nécessaires à l’usage voulu ?

Ne copie pas ce bloc aveuglément en production. Si l’équipement fonctionne avec le NetFlow traditionnel, la syntaxe peut être complètement différente. N’essaie pas de mélanger les syntaxes de deux familles de configuration sans vérifier la documentation du modèle.

### 7.3 Sens d’observation : input et output

L’application `input` observe le trafic lorsqu’il entre dans l’interface surveillée. L’application `output`, si elle est prise en charge, observe le trafic à la sortie de cette interface. Le choix dépend de la question à résoudre.

Exemple : pour observer le trafic entrant d’un LAN vers un routeur, un monitor `input` sur l’interface LAN est souvent un point de départ logique. Pour voir ce que le routeur envoie sur un lien WAN, l’observation en sortie de l’interface WAN peut être utile. Ces vues ne sont pas équivalentes et peuvent compter le même paquet à plusieurs points d’observation.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="diag7-title diag7-desc">
  <title id="diag7-title">Observation NetFlow à l'entrée ou à la sortie d'une interface</title>
  <desc id="diag7-desc">Un routeur entre un LAN et un WAN montre deux points de mesure possibles : input sur l'interface LAN, output sur l'interface WAN. Ils répondent à des questions différentes.</desc>
  <defs><linearGradient id="d7bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d7arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="358" rx="20" fill="url(#d7bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Deux points de mesure possibles</text>
  <rect x="44" y="102" width="180" height="112" rx="13" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="134" y="135" text-anchor="middle" fill="#eaf8ff" font-size="18" font-weight="700">LAN</text><text x="134" y="160" text-anchor="middle" fill="#bae6fd" font-size="14">Clients</text><text x="134" y="184" text-anchor="middle" fill="#7dd3fc" font-size="13">10.10.10.0/24</text>
  <rect x="389" y="92" width="182" height="132" rx="15" fill="#202a3b" stroke="#a5b4fc" stroke-width="2"/><text x="480" y="129" text-anchor="middle" fill="#eff5ff" font-size="20" font-weight="700">Routeur R1</text><text x="480" y="155" text-anchor="middle" fill="#dbe3ff" font-size="14">Routage / ACL</text><rect x="414" y="174" width="132" height="30" rx="7" fill="#282546" stroke="#818cf8"/><text x="480" y="194" text-anchor="middle" fill="#e0e7ff" font-size="12">FNF monitor</text>
  <rect x="736" y="102" width="180" height="112" rx="13" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="826" y="135" text-anchor="middle" fill="#edfff2" font-size="18" font-weight="700">WAN</text><text x="826" y="160" text-anchor="middle" fill="#d1fae0" font-size="14">Réseau distant</text><text x="826" y="184" text-anchor="middle" fill="#86efac" font-size="13">Lien vers fournisseur</text>
  <path d="M224 158 H378" stroke="#38bdf8" stroke-width="3" marker-end="url(#d7arr)"/><path d="M571 158 H725" stroke="#4ade80" stroke-width="3" marker-end="url(#d7arr)"/>
  <rect x="40" y="256" width="420" height="67" rx="11" fill="#142b42" stroke="#38bdf8"/><text x="250" y="282" text-anchor="middle" fill="#eaf8ff" font-size="16" font-weight="700">Input côté LAN</text><text x="250" y="304" text-anchor="middle" fill="#bae6fd" font-size="13">Que reçoit le routeur depuis les clients ?</text>
  <rect x="500" y="256" width="420" height="67" rx="11" fill="#173125" stroke="#4ade80"/><text x="710" y="282" text-anchor="middle" fill="#edfff2" font-size="16" font-weight="700">Output côté WAN</text><text x="710" y="304" text-anchor="middle" fill="#d1fae0" font-size="13">Que transmet le routeur sur le lien distant ?</text>
  <text x="480" y="344" text-anchor="middle" fill="#9fb1c9" font-size="12">Exemple conceptuel : les capacités exactes dépendent du matériel et du logiciel.</text>
</svg>

## 8. Comprendre les compteurs et les délais d’export

Les enregistrements de flux peuvent rester dans un cache sur l’équipement. Certains flux expirent après une période d’inactivité ; d’autres sont exportés périodiquement pendant qu’ils restent actifs. Les valeurs `active` et `inactive` configurées dans l’exemple sont des intervalles à adapter à la plateforme et au collecteur.

Cela implique deux conséquences pratiques :

1. Le collecteur peut ne pas afficher immédiatement un flux nouvellement observé.
2. Un flux long peut être exporté plusieurs fois avec des compteurs ou des intervalles correspondant aux règles d’export, plutôt que comme un unique enregistrement final.

Il faut comprendre le modèle de compteurs du matériel et du collecteur avant de comparer deux rapports. La précision, le comportement des caches, l’échantillonnage et les métadonnées disponibles varient selon les versions.

### 8.1 Échantillonnage

Le **sampling** réduit le nombre de paquets traités pour la collecte en observant une partie du trafic. Cela peut diminuer la charge sur l’équipement et le volume d’export, mais les estimations obtenues ont une incertitude. Selon le mécanisme, les compteurs exportés peuvent être des comptes observés ou des estimations ; ne multiplie pas automatiquement les chiffres par le taux de sampling sans vérifier comment l’appareil et le collecteur traitent cette information.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="diag8-title diag8-desc">
  <title id="diag8-title">Principe de l'échantillonnage NetFlow</title>
  <desc id="diag8-desc">Un grand volume de paquets arrive, un mécanisme de sampling sélectionne certains paquets, et les informations observées contribuent aux statistiques de flux. Le résultat est moins coûteux mais potentiellement estimé.</desc>
  <defs><linearGradient id="d8bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d8arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="348" rx="20" fill="url(#d8bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Échantillonnage : moins de paquets traités, plus d’incertitude</text>
  <rect x="35" y="88" width="240" height="150" rx="13" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="155" y="117" text-anchor="middle" fill="#eaf8ff" font-size="17" font-weight="700">Trafic entrant</text>
  <rect x="55" y="136" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="87" y="136" width="22" height="16" rx="3" fill="#38bdf8" opacity=".8"/><rect x="119" y="136" width="22" height="16" rx="3" fill="#38bdf8" opacity=".9"/><rect x="151" y="136" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="183" y="136" width="22" height="16" rx="3" fill="#38bdf8" opacity=".8"/><rect x="215" y="136" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="55" y="166" width="22" height="16" rx="3" fill="#38bdf8" opacity=".8"/><rect x="87" y="166" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="119" y="166" width="22" height="16" rx="3" fill="#38bdf8" opacity=".9"/><rect x="151" y="166" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="183" y="166" width="22" height="16" rx="3" fill="#38bdf8" opacity=".8"/><rect x="215" y="166" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="55" y="196" width="22" height="16" rx="3" fill="#38bdf8" opacity=".9"/><rect x="87" y="196" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="119" y="196" width="22" height="16" rx="3" fill="#38bdf8" opacity=".8"/><rect x="151" y="196" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="183" y="196" width="22" height="16" rx="3" fill="#38bdf8" opacity=".9"/><rect x="215" y="196" width="22" height="16" rx="3" fill="#38bdf8"/><rect x="55" y="226" width="22" height="8" rx="3" fill="#38bdf8" opacity=".8"/><rect x="87" y="226" width="22" height="8" rx="3" fill="#38bdf8"/><rect x="119" y="226" width="22" height="8" rx="3" fill="#38bdf8" opacity=".9"/><rect x="151" y="226" width="22" height="8" rx="3" fill="#38bdf8"/><rect x="183" y="226" width="22" height="8" rx="3" fill="#38bdf8" opacity=".8"/><rect x="215" y="226" width="22" height="8" rx="3" fill="#38bdf8"/>
  <rect x="355" y="106" width="230" height="112" rx="13" fill="#2a2440" stroke="#a5b4fc" stroke-width="2"/><text x="470" y="138" text-anchor="middle" fill="#eef2ff" font-size="17" font-weight="700">Sampler</text><text x="470" y="166" text-anchor="middle" fill="#dbe3ff" font-size="14">Sélectionne une partie</text><text x="470" y="191" text-anchor="middle" fill="#c7d2fe" font-size="13">Selon la méthode configurée</text>
  <rect x="665" y="88" width="260" height="150" rx="13" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="795" y="117" text-anchor="middle" fill="#edfff2" font-size="17" font-weight="700">Statistiques de flux</text>
  <rect x="700" y="141" width="29" height="20" rx="4" fill="#4ade80"/><rect x="748" y="141" width="29" height="20" rx="4" fill="#4ade80" opacity=".9"/><rect x="796" y="141" width="29" height="20" rx="4" fill="#4ade80"/><rect x="844" y="141" width="29" height="20" rx="4" fill="#4ade80" opacity=".9"/><rect x="700" y="173" width="29" height="20" rx="4" fill="#4ade80"/><rect x="748" y="173" width="29" height="20" rx="4" fill="#4ade80" opacity=".9"/><rect x="796" y="173" width="29" height="20" rx="4" fill="#4ade80"/><rect x="844" y="173" width="29" height="20" rx="4" fill="#4ade80" opacity=".9"/>
  <path d="M275 164 H345" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d8arr)"/><path d="M585 164 H655" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d8arr)"/>
  <text x="480" y="277" text-anchor="middle" fill="#e2eaf4" font-size="16" font-weight="700">Avantage</text><text x="480" y="300" text-anchor="middle" fill="#b7f7c9" font-size="14">Réduction possible du coût de traitement et d’export</text><text x="480" y="324" text-anchor="middle" fill="#fdba74" font-size="14">Limite : la mesure peut devenir une estimation, pas un comptage exhaustif.</text>
</svg>

## 9. IP SLA et NetFlow ensemble

Dans un centre de supervision, IP SLA peut signaler que le délai vers une cible se dégrade. NetFlow peut ensuite aider à identifier les conversations volumineuses sur les interfaces concernées. Les compteurs d’interface, la table de routage, les logs, les tests applicatifs et éventuellement une capture de paquets permettent de confirmer ou d’infirmer les hypothèses.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-labelledby="diag9-title diag9-desc">
  <title id="diag9-title">Corrélation entre IP SLA, NetFlow et diagnostic</title>
  <desc id="diag9-desc">IP SLA fournit les mesures actives, NetFlow fournit les métadonnées de trafic et un analyste corrèle les observations avant de conclure.</desc>
  <defs><linearGradient id="d9bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d9arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="398" rx="20" fill="url(#d9bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Corréler les indicateurs pour enquêter</text>
  <rect x="46" y="80" width="250" height="112" rx="13" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="171" y="113" text-anchor="middle" fill="#eaf8ff" font-size="18" font-weight="700">IP SLA</text><text x="171" y="140" text-anchor="middle" fill="#bae6fd" font-size="14">RTT monte à 180 ms</text><text x="171" y="164" text-anchor="middle" fill="#7dd3fc" font-size="13">Alerte de performance</text>
  <rect x="355" y="80" width="250" height="112" rx="13" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="480" y="113" text-anchor="middle" fill="#edfff2" font-size="18" font-weight="700">NetFlow</text><text x="480" y="140" text-anchor="middle" fill="#d1fae0" font-size="14">Hausse d’un flux volumineux</text><text x="480" y="164" text-anchor="middle" fill="#86efac" font-size="13">Volume + endpoints + ports</text>
  <rect x="664" y="80" width="250" height="112" rx="13" fill="#30251a" stroke="#fbbf24" stroke-width="2"/><text x="789" y="113" text-anchor="middle" fill="#fff7e4" font-size="18" font-weight="700">Vérifications</text><text x="789" y="140" text-anchor="middle" fill="#fce8bd" font-size="14">Interface, routes, logs</text><text x="789" y="164" text-anchor="middle" fill="#fbbf24" font-size="13">Confirmer l’hypothèse</text>
  <path d="M296 136 H345" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d9arr)"/><path d="M605 136 H654" stroke="#9bb2ce" stroke-width="2.5" marker-end="url(#d9arr)"/>
  <rect x="98" y="250" width="764" height="90" rx="13" fill="#0e1b2b" stroke="#405773"/><text x="480" y="279" text-anchor="middle" fill="#f1f6ff" font-size="17" font-weight="700">Règle d’or</text><text x="480" y="306" text-anchor="middle" fill="#c6d4e5" font-size="14">Des indices qui coïncident renforcent une hypothèse, mais ne prouvent pas seuls la causalité.</text><text x="480" y="326" text-anchor="middle" fill="#9fb1c9" font-size="12">Vérifier la portée, le point d’observation, le sens du flux et l’heure de chaque mesure.</text>
  <text x="480" y="374" text-anchor="middle" fill="#8fa5c0" font-size="13">Les horodatages et une base de temps cohérente facilitent la corrélation.</text>
</svg>

### Exemple de tableau de corrélation

| Heure | IP SLA | NetFlow | Interprétation provisoire |
|---|---|---|---|
| 10:00 | RTT 15 ms, sans perte | Volume habituel | Situation de référence |
| 10:05 | RTT 170 ms, sans perte | Hausse d’un flux volumineux | Congestion possible, à confirmer |
| 10:08 | RTT élevé | Compteurs de sortie près du débit du lien | Examiner l’utilisation et les files d’attente |
| 10:12 | RTT normal après fin du flux | Volume revenu à la normale | Corrélation plus forte, pas preuve définitive |

## 10. Méthode de dépannage

### 10.1 IP SLA ne répond pas

1. Vérifie l’état et les paramètres de l’opération avec les commandes `show ip sla ...` disponibles sur la plate-forme.
2. Vérifie l’adresse de destination et la source de la sonde.
3. Confirme la route aller et le chemin retour. Une réponse peut repartir par un autre chemin.
4. Examine les ACL, pare-feu et politiques qui peuvent bloquer ICMP.
5. Teste la cible depuis le même réseau source, puis compare avec un test depuis un autre point.
6. Si IP SLA suit une route, vérifie l’état de l’objet `track` et la table de routage.

Évite d’augmenter immédiatement le timeout ou d’abaisser les seuils : commence par déterminer si l’échec est réel, attendu ou provoqué par une politique de sécurité.

### 10.2 Aucun flux n’apparaît dans le collecteur

1. Vérifie que le monitor est appliqué à la bonne interface et dans le bon sens.
2. Vérifie que le trafic traverse vraiment ce point d’observation.
3. Vérifie que l’exporter a une destination et une source valides.
4. Contrôle la route vers le collecteur et les ACL autorisant le transport UDP.
5. Vérifie que le port, le format d’export et la source déclarés correspondent au collecteur.
6. Consulte les états et compteurs de monitor/exporter si ces commandes sont prises en charge.
7. Vérifie si les entrées de cache attendent leur délai d’export ou si le trafic est échantillonné.

### 10.3 NetFlow indique des volumes surprenants

- Confirme les unités : paquets, octets, débit estimé, ou volume sur une période.
- Vérifie si le rapport concerne une seule direction ou les deux.
- Identifie d’éventuels points d’observation doublés.
- Vérifie les timeouts, la période d’agrégation et le traitement des templates côté collecteur.
- Vérifie le sampling et la façon dont les valeurs exportées sont interprétées.
- Compare aux compteurs d’interface et à des mesures indépendantes.

### 10.4 Arbre de dépannage visuel

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-labelledby="diag10-title diag10-desc">
  <title id="diag10-title">Arbre de diagnostic de premier niveau</title>
  <desc id="diag10-desc">Le diagnostic commence par vérifier si IP SLA reçoit une réponse, puis traite séparément la mesure, le suivi de route et NetFlow qui n'exporte pas.</desc>
  <defs><linearGradient id="d10bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111b2d"/><stop offset="1" stop-color="#07101d"/></linearGradient><marker id="d10arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#9bb2ce"/></marker></defs>
  <rect x="1" y="1" width="958" height="478" rx="20" fill="url(#d10bg)" stroke="#29415d"/><text x="480" y="35" text-anchor="middle" fill="#f4f8ff" font-size="22" font-weight="700">Diagnostic de premier niveau</text>
  <rect x="322" y="62" width="316" height="58" rx="12" fill="#202a3b" stroke="#a5b4fc" stroke-width="2"/><text x="480" y="86" text-anchor="middle" fill="#eff5ff" font-size="17" font-weight="700">Quel est le symptôme ?</text><text x="480" y="106" text-anchor="middle" fill="#c7d2fe" font-size="13">Mesure · route · absence de flux</text>
  <path d="M480 120 V144 H173 V164" fill="none" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/><path d="M480 144 V164" fill="none" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/><path d="M480 144 H787 V164" fill="none" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/>
  <rect x="42" y="164" width="262" height="82" rx="12" fill="#142b42" stroke="#38bdf8" stroke-width="2"/><text x="173" y="191" text-anchor="middle" fill="#eaf8ff" font-size="16" font-weight="700">IP SLA en échec</text><text x="173" y="215" text-anchor="middle" fill="#bae6fd" font-size="13">Cible · source · routes · ACL</text><text x="173" y="233" text-anchor="middle" fill="#7dd3fc" font-size="12">Comparer avec un autre test</text>
  <rect x="349" y="164" width="262" height="82" rx="12" fill="#2b243f" stroke="#a5b4fc" stroke-width="2"/><text x="480" y="191" text-anchor="middle" fill="#eef2ff" font-size="16" font-weight="700">Bascule inattendue</text><text x="480" y="215" text-anchor="middle" fill="#dbe3ff" font-size="13">État track · routes candidates</text><text x="480" y="233" text-anchor="middle" fill="#c7d2fe" font-size="12">Cible de sonde pertinente ?</text>
  <rect x="656" y="164" width="262" height="82" rx="12" fill="#173125" stroke="#4ade80" stroke-width="2"/><text x="787" y="191" text-anchor="middle" fill="#edfff2" font-size="16" font-weight="700">Pas de flux exporté</text><text x="787" y="215" text-anchor="middle" fill="#d1fae0" font-size="13">Monitor · exporter · réseau</text><text x="787" y="233" text-anchor="middle" fill="#86efac" font-size="12">Port + format + collector</text>
  <path d="M173 246 V275" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/><path d="M480 246 V275" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/><path d="M787 246 V275" stroke="#9bb2ce" stroke-width="2" marker-end="url(#d10arr)"/>
  <rect x="42" y="277" width="262" height="100" rx="12" fill="#0e1b2b" stroke="#405773"/><text x="173" y="304" text-anchor="middle" fill="#f1f6ff" font-size="15" font-weight="700">Valider la couche réseau</text><text x="173" y="328" text-anchor="middle" fill="#c6d4e5" font-size="13">Ping source-cible, table IP,</text><text x="173" y="349" text-anchor="middle" fill="#c6d4e5" font-size="13">ACL et chemin retour</text>
  <rect x="349" y="277" width="262" height="100" rx="12" fill="#0e1b2b" stroke="#405773"/><text x="480" y="304" text-anchor="middle" fill="#f1f6ff" font-size="15" font-weight="700">Valider la décision</text><text x="480" y="328" text-anchor="middle" fill="#c6d4e5" font-size="13">État du track, distance,</text><text x="480" y="349" text-anchor="middle" fill="#c6d4e5" font-size="13">présence de la route active</text>
  <rect x="656" y="277" width="262" height="100" rx="12" fill="#0e1b2b" stroke="#405773"/><text x="787" y="304" text-anchor="middle" fill="#f1f6ff" font-size="15" font-weight="700">Valider l’export</text><text x="787" y="328" text-anchor="middle" fill="#c6d4e5" font-size="13">Compteurs, source, UDP,</text><text x="787" y="349" text-anchor="middle" fill="#c6d4e5" font-size="13">format et parsing collector</text>
  <text x="480" y="420" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">Ne change qu’un paramètre à la fois.</text><text x="480" y="445" text-anchor="middle" fill="#9fb1c9" font-size="13">Note l’heure, la configuration, le résultat initial et le résultat après chaque modification.</text><text x="480" y="465" text-anchor="middle" fill="#8fa5c0" font-size="12">Sur les équipements de production, suis la procédure de changement et prévois un retour arrière.</text>
</svg>

## 11. Laboratoire guidé : mesurer puis observer

### Objectifs

À la fin du laboratoire, tu dois être capable de :

- démarrer une opération IP SLA ICMP Echo et interpréter son résultat ;
- suivre l’état d’une sonde avec un objet `track` si la plate-forme le permet ;
- créer la chaîne Flexible NetFlow si elle est disponible ;
- vérifier le point de mesure, l’export et l’arrivée des données au collecteur ;
- documenter ce qui a été prouvé, ce qui reste hypothétique et les limites du test.

### Étape A — Documenter la topologie

Avant la configuration, note la version IOS/IOS XE, les interfaces, les adresses IP, le prochain saut, l’adresse source d’export et le collecteur. Confirme que les adresses de test sont bien prévues pour le laboratoire. Utilise une maquette ou un créneau de maintenance pour éviter tout impact involontaire.

### Étape B — Activer IP SLA

1. Configure une sonde ICMP Echo vers une cible qui répond volontairement.
2. Démarre l’opération.
3. Consulte les commandes `show ip sla` disponibles et note l’état, le RTT et les pertes éventuelles.
4. Compare le résultat à un ping lancé depuis la même source quand cela est possible.
5. Si l’environnement de test s’y prête, désactive temporairement un chemin de test contrôlé ou filtre la réponse ICMP pour observer le comportement d’échec. Rétablis ensuite la configuration initiale.

**Résultat attendu :** tu sais distinguer « l’opération est configurée », « l’opération est en cours » et « la destination a répondu à la dernière sonde ».

### Étape C — Ajouter le suivi de route (facultatif)

1. Vérifie que l’opération IP SLA est stable.
2. Configure l’objet `track` et la route suivie dans un environnement adapté.
3. Ajoute une route de secours avec une préférence moins forte, selon le plan de routage de la maquette.
4. Confirme la présence de la route principale puis provoque uniquement une panne de test prévue.
5. Vérifie l’état du track et la table de routage, puis rétablis le chemin.

N’effectue pas de manipulation de lien ou de route sur un réseau de production sans autorisation, fenêtre de changement et plan de retour arrière.

### Étape D — Activer NetFlow

1. Confirme que la plate-forme prend en charge Flexible NetFlow et la syntaxe utilisée.
2. Crée un record comprenant les adresses source/destination, le protocole, les ports disponibles et les compteurs utiles.
3. Crée un exporter dirigé vers le collecteur ; utilise un port et un format acceptés de part et d’autre.
4. Crée un monitor qui référence le record et l’exporter.
5. Applique le monitor sur l’interface où passe le trafic à observer.
6. Génère quelques conversations de test, attends le délai d’export et inspecte le collecteur.
7. Compare l’observation avec les compteurs d’interface et note le sens de mesure.

**Résultat attendu :** tu peux identifier un flux par ses clés et lire les paquets/octets exportés, tout en précisant le point d’observation et les limites de mesure.

### Fiche d’observation à remplir

| Élément | Valeur observée | Interprétation |
|---|---|---|
| Cible IP SLA | À remplir | La cible représente-t-elle le service à surveiller ? |
| RTT habituel | À remplir | Référence du laboratoire |
| RTT lors du test | À remplir | Variation constatée |
| État du track | À remplir | Up/down/inconnu selon la plate-forme |
| Interface NetFlow | À remplir | Point et sens de mesure |
| Format/port d’export | À remplir | Doit correspondre au collecteur |
| Flux le plus volumineux | À remplir | Source, destination, protocole et volume |
| Limites de la mesure | À remplir | Sampling, direction, filtre, cible ICMP, etc. |

## 12. Exercices corrigés

### Exercice 1 — Ping réussi, application inaccessible

**Situation :** IP SLA ICMP Echo répond avec un RTT normal, mais les utilisateurs ne peuvent pas ouvrir une application web.

**Correction :** le résultat prouve seulement qu’une réponse ICMP a été reçue par le chemin de la sonde. Vérifie le port TCP du service, l’écoute du serveur, le DNS, les ACL/pare-feu, le certificat et les journaux applicatifs. Si la plateforme prend en charge une opération adaptée au service, elle peut compléter le diagnostic.

### Exercice 2 — IP SLA échoue, mais la route reste en place

**Situation :** la sonde n’obtient plus de réponse, mais la route statique principale semble toujours présente.

**Correction :** vérifie que l’objet `track` référence la bonne opération, que la route est bien liée au track, que les délais de détection/transition sont écoulés et que tu inspectes la bonne table ou la bonne VRF. Vérifie également si la syntaxe est prise en charge. L’échec d’une sonde seule ne retire aucune route si aucun mécanisme de suivi n’a été configuré.

### Exercice 3 — Le collecteur n’affiche pas le flux créé à l’instant

**Situation :** tu génères du trafic, mais le collecteur ne le montre pas immédiatement.

**Correction :** contrôle la chaîne interface → monitor → exporter → collector, le cache et les délais de timeout/export, les ACL, le port UDP, l’adresse source et le format/templates. Vérifie aussi que tu regardes le bon intervalle et la bonne interface.

### Exercice 4 — Les octets du collecteur sont plus faibles que les compteurs de l’interface

**Situation :** NetFlow affiche un volume bien inférieur à celui du compteur d’interface.

**Correction :** ce n’est pas automatiquement une erreur. Vérifie si le monitor observe la même direction et le même trafic, si l’ensemble de clés limite la visibilité, si le sampling est activé, si les périodes de mesure concordent et si le collecteur interprète correctement les compteurs exportés. Les compteurs d’interface comprennent généralement plus de trafic que les seuls flux sélectionnés par un record ou une politique d’observation spécifique.

### Exercice 5 — Deux rapports affichent la même conversation

**Situation :** un même couple source/destination apparaît dans des rapports de deux interfaces.

**Correction :** le trafic peut être observé en entrée sur un équipement puis en sortie sur un autre, ou encore dans les deux sens. Compare les interfaces, le sens d’application, les clés de flux et les plages horaires avant de totaliser les valeurs. Deux observations ne signifient pas nécessairement deux fois plus de trafic applicatif.

## 13. Quiz final

**1. Quel est l’objectif principal d’IP SLA ?**  
A. Déchiffrer le contenu des paquets  
B. Mesurer activement la réponse et certaines performances d’un chemin ou service  
C. Stocker tous les paquets dans un PCAP  
D. Remplacer automatiquement tous les protocoles de routage

**2. Que représente généralement le RTT ?**  
A. Le temps aller-retour d’une sonde  
B. Le nombre de routes présentes  
C. Le débit maximal du lien  
D. Le nombre de flux NetFlow actifs

**3. Une sonde ICMP Echo réussie prouve-t-elle que HTTP fonctionne ?**  
A. Oui, toujours  
B. Non, car ICMP et HTTP testent des fonctions différentes  
C. Seulement avec NetFlow v9  
D. Seulement si l’interface est en duplex intégral

**4. Quel mécanisme peut exploiter le résultat d’IP SLA pour influencer une route statique ?**  
A. Un objet `track` associé à la route  
B. Un record NetFlow  
C. Le port UDP 2055  
D. Une entrée DNS

**5. Quel ensemble correspond au cinq-tuple classique ?**  
A. MAC source, VLAN, MTU, TTL, DSCP  
B. IP source, IP destination, protocole, port source, port destination  
C. DNS, HTTP, TLS, DHCP, ARP  
D. Interface d’entrée, nom du routeur, heure, modèle et version

**6. Quel objet définit les clés et champs collectés dans Flexible NetFlow ?**  
A. Flow record  
B. Flow exporter  
C. Flow monitor uniquement  
D. Collecteur seulement

**7. À quoi sert le flow exporter ?**  
A. À calculer les routes OSPF  
B. À définir la destination et les paramètres d’export des enregistrements  
C. À créer les adresses IP des clients  
D. À remplacer le cache du monitor

**8. Que faut-il vérifier si aucun flux n’arrive au collecteur ?**  
A. Uniquement la couleur de la LED du routeur  
B. Seulement l’adresse IP source de l’application  
C. Monitor appliqué, exporter, routage vers le collecteur, ACL/UDP, format et configuration du collecteur  
D. Seulement la passerelle par défaut du PC d’administration

**9. Que change généralement le sampling ?**  
A. Il peut réduire le coût de traitement en n’observant qu’une partie des paquets, au prix d’une estimation moins exhaustive  
B. Il garantit une capture intégrale  
C. Il rend IP SLA inutile  
D. Il garantit que tous les compteurs sont exacts à 100 %

**10. Quelle est la meilleure façon d’enquêter sur une hausse de latence ?**  
A. Conclure à la congestion dès le premier RTT élevé  
B. Corréler IP SLA, NetFlow, compteurs d’interface, routes et journaux  
C. Désactiver toutes les ACL  
D. Changer plusieurs paramètres en même temps

### Corrigé

| Question | Réponse | Justification |
|---|---|---|
| 1 | B | IP SLA exécute des mesures actives selon un type d’opération. |
| 2 | A | Le RTT correspond au délai aller-retour de la sonde. |
| 3 | B | La réponse ICMP ne valide pas la connexion ou le fonctionnement HTTP. |
| 4 | A | Un objet de suivi peut lier l’état de l’opération à une route prise en charge. |
| 5 | B | C’est la définition classique du cinq-tuple IPv4/TCP-UDP. |
| 6 | A | Le record définit les clés et champs collectés. |
| 7 | B | L’exporter décrit où et comment envoyer les enregistrements. |
| 8 | C | Il faut valider toute la chaîne de visibilité et d’export. |
| 9 | A | L’échantillonnage peut réduire la charge mais modifie la complétude de la mesure. |
| 10 | B | La corrélation permet une enquête plus solide qu’un indicateur isolé. |

## 14. Fiche de révision

### IP SLA

- **À quoi ça sert ?** Mesurer activement la disponibilité et certaines performances.
- **Par quoi commencer ?** Une opération ICMP Echo simple vers une cible bien choisie.
- **Que vérifier ?** Source, destination, fréquence, timeout, route, ACL, statistiques et état de l’opération.
- **Comment lier à une route ?** Utiliser le mécanisme de suivi pris en charge par la plateforme et tester la bascule hors production.
- **Limite ?** Une réponse ICMP n’atteste pas que l’application est fonctionnelle.

### NetFlow / Flexible NetFlow

- **À quoi ça sert ?** Observer des conversations, volumes et métadonnées de trafic.
- **Record ?** Définition des clés et champs collectés.
- **Monitor ?** Associe record, cache et éventuellement exporter.
- **Exporter ?** Destination, source, protocole/format exporté.
- **Collector ?** Réception, parsing et visualisation.
- **À vérifier ?** Interface, direction, cache/timeouts, sampling, port, format, route vers le collecteur.
- **Limite ?** Ce n’est pas une capture complète des paquets ni une preuve automatique de causalité.

### Méthode de diagnostic

1. Formule une hypothèse avant de modifier la configuration.
2. Enregistre l’heure et la valeur initiale.
3. Vérifie le bon point de mesure et la direction.
4. Croise au moins deux sources indépendantes si possible.
5. Change un seul élément à la fois, puis mesure à nouveau.
6. Documente la conclusion, les preuves et les limites restantes.

## 15. Références techniques

Consulte la documentation correspondant au modèle et à la version logicielle de l’équipement. Les références ci-dessous sont des points de départ Cisco pour vérifier la syntaxe et les prérequis ; elles ne remplacent pas le guide de la version effectivement déployée.

- Cisco IOS XE 17.x — [Configuration des opérations IP SLA ICMP Echo](https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-addressing/b-ip-addressing/m_sla_icmp_echo.html)
- Cisco — [Flexible NetFlow Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/fnf-avc/flexible-netflow-configuration-guide.html)


**Fin du cours — IP SLA & NetFlow, Niveau Débutant.**
