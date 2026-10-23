# Authentification centralisée avec RADIUS — Intermédiaire

**Niveau :** INTERMÉDIAIRE

Ce cours poursuit le niveau Débutant : les rôles du client RADIUS/NAS, les messages Access-Request/Accept/Reject/Challenge et les bases d’AAA sont supposés connus. L’objectif est maintenant de concevoir, configurer et dépanner une authentification centralisée dans un réseau réaliste, avec des politiques cohérentes, plusieurs serveurs, du 802.1X, de l’accounting et des contrôles de sécurité.

À la fin du cours, vous devrez pouvoir suivre une authentification de bout en bout, déterminer quel composant prend chaque décision, distinguer un problème EAP d’un refus RADIUS, mesurer l’effet d’un timeout, et proposer un changement réversible sans verrouiller les administrateurs hors des équipements.

> **Analogie** : RADIUS ressemble à un poste de contrôle central. Le NAS vérifie le badge et transmet la demande ; le serveur vérifie l’identité et la politique, puis renvoie une décision accompagnée d’attributs. Le poste de contrôle ne remplace toutefois pas le NAS : c’est l’équipement d’accès qui applique le résultat.

<style>.radius-visual{width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.radius-visual *{box-sizing:border-box}.radius-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px;overflow:visible}.radius-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.radius-visual svg .small{font-size:12px;fill:#a1a1aa}.radius-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.radius-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:radiusFlow 1.25s linear infinite}.radius-visual svg .flow-blue{stroke:#60a5fa}.radius-visual svg .flow-green{stroke:#4ade80}.radius-visual svg .flow-amber{stroke:#fbbf24}.radius-visual svg .flow-red{stroke:#fb7185}.radius-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.radius-visual svg .radius-int-flow,.radius-visual svg .radius-int-decision-flow,.radius-visual svg .radius-int-eap-flow,.radius-visual svg .radius-int-acct-flow,.radius-visual svg .radius-int-diag-flow,.radius-visual svg .radius-int-failover-flow{stroke-dasharray:7 7;stroke-linecap:round;animation:radiusFlow 1.25s linear infinite}.radius-visual svg .radius-int-packet{animation:radiusPulse 1.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.radius-visual svg .radius-int-packet-delay{animation-delay:.45s}.radius-visual svg .radius-int-soft{animation:radiusPulse 2.1s ease-in-out infinite}.radius-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7}.radius-visual__note{color:#94a3b8;font-size:.8rem;line-height:1.65;margin:.5rem .35rem .2rem}@keyframes radiusFlow{to{stroke-dashoffset:-32}}@keyframes radiusPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(max-width:700px){.radius-visual{padding:8px}.radius-visual svg text{font-size:17px}.radius-visual svg .small{font-size:14px}.radius-visual svg .title{font-size:19px}}@media(prefers-reduced-motion:reduce){.radius-visual svg .flow,.radius-visual svg .radius-int-flow,.radius-visual svg .radius-int-decision-flow,.radius-visual svg .radius-int-eap-flow,.radius-visual svg .radius-int-acct-flow,.radius-visual svg .radius-int-diag-flow,.radius-visual svg .radius-int-failover-flow,.radius-visual svg .radius-int-packet,.radius-visual svg .radius-int-soft{animation:none!important}.radius-visual{scroll-behavior:auto!important}}</style>

---

## 1. La théorie et les algorithmes

### 1.1 Architecture et responsabilités

RADIUS sépare le point d’accès au réseau de la décision d’authentification. Le client RADIUS — souvent appelé **NAS** (*Network Access Server*) — est un switch, un contrôleur Wi-Fi, un concentrateur VPN ou un équipement d’accès. Il échange avec un serveur RADIUS sur UDP/1812 pour l’authentification et UDP/1813 pour l’accounting dans les déploiements courants. Ces ports sont conventionnels : une configuration peut les changer, il faut donc vérifier la configuration réelle.

Le serveur peut consulter une base locale, un annuaire ou un fournisseur d’identité. Il applique une politique qui associe identité, groupe, type d’accès, heure, posture du poste, emplacement et méthode EAP. Le serveur répond ; le NAS traduit cette réponse en état de port, VLAN, ACL, rôle, profil VPN ou autorisation de session, selon les capacités du constructeur.

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 330" role="img" aria-labelledby="radius-int-arch-title radius-int-arch-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-arch-title">Architecture RADIUS centralisée</title><desc id="radius-int-arch-desc">Le terminal échange avec le NAS. Le NAS relaie la requête au serveur RADIUS, qui consulte la source d'identité et renvoie une décision. Les journaux d'accounting enregistrent le cycle de session.</desc>
<rect x="1" y="1" width="958" height="328" rx="14" fill="#090d14" stroke="#3f3f46"/>
<text x="28" y="30" fill="#f4f4f5" font-size="18" font-weight="700">Architecture de décision centralisée</text>
<rect x="24" y="78" width="174" height="142" rx="12" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="111" y="108" text-anchor="middle" fill="#eff6ff" font-size="15" font-weight="700">Poste client</text><text x="111" y="134" text-anchor="middle" fill="#bfdbfe" font-size="13">Supplicant / VPN</text><text x="111" y="170" text-anchor="middle" fill="#cbd5e1" font-size="12">Identité et méthode</text><text x="111" y="190" text-anchor="middle" fill="#cbd5e1" font-size="12">EAP si applicable</text>
<rect x="258" y="78" width="174" height="142" rx="12" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="345" y="108" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">NAS / équipement</text><text x="345" y="134" text-anchor="middle" fill="#bbf7d0" font-size="13">Switch, AP, VPN</text><text x="345" y="170" text-anchor="middle" fill="#d1fae5" font-size="12">Applique le résultat</text><text x="345" y="190" text-anchor="middle" fill="#d1fae5" font-size="12">et ouvre la session</text>
<rect x="493" y="78" width="190" height="142" rx="12" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="588" y="108" text-anchor="middle" fill="#eff6ff" font-size="15" font-weight="700">Serveur RADIUS</text><text x="588" y="134" text-anchor="middle" fill="#bfdbfe" font-size="13">Politique AAA</text><text x="588" y="170" text-anchor="middle" fill="#cbd5e1" font-size="12">Vérifie identité</text><text x="588" y="190" text-anchor="middle" fill="#cbd5e1" font-size="12">et règles d’accès</text>
<rect x="744" y="54" width="190" height="88" rx="10" fill="#2b2110" stroke="#fbbf24" stroke-width="1.5"/><text x="839" y="81" text-anchor="middle" fill="#fef3c7" font-size="14" font-weight="700">Source d’identité</text><text x="839" y="104" text-anchor="middle" fill="#fde68a" font-size="12">Annuaire / base locale</text><text x="839" y="122" text-anchor="middle" fill="#fde68a" font-size="12">Groupes et attributs</text>
<rect x="744" y="163" width="190" height="88" rx="10" fill="#172033" stroke="#94a3b8" stroke-width="1.5"/><text x="839" y="190" text-anchor="middle" fill="#f1f5f9" font-size="14" font-weight="700">Accounting / SIEM</text><text x="839" y="213" text-anchor="middle" fill="#cbd5e1" font-size="12">Début, mises à jour, fin</text><text x="839" y="231" text-anchor="middle" fill="#cbd5e1" font-size="12">et corrélation</text>
<path d="M198 136 H258" fill="none" stroke="#4ade80" stroke-width="3"/><polygon points="258,136 247,130 247,142" fill="#4ade80"/><circle class="radius-int-packet" cx="225" cy="136" r="5" fill="#4ade80"/><text x="228" y="122" text-anchor="middle" fill="#86efac" font-size="11">EAP / accès</text>
<path class="radius-int-flow" d="M432 136 H493" fill="none" stroke="#60a5fa" stroke-width="3"/><polygon points="493,136 482,130 482,142" fill="#60a5fa"/><circle class="radius-int-packet" cx="461" cy="136" r="5" fill="#60a5fa"/><text x="462" y="122" text-anchor="middle" fill="#93c5fd" font-size="11">RADIUS</text>
<path d="M683 103 H714 V98 H744" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="744,98 734,92 734,104" fill="#fbbf24"/><text x="711" y="84" text-anchor="middle" fill="#fde68a" font-size="10">Identité</text>
<path d="M683 190 H714 V207 H744" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="744,207 734,201 734,213" fill="#4ade80"/><text x="713" y="180" text-anchor="middle" fill="#86efac" font-size="10">Événements</text>
<path d="M588 220 V276 H345 V220" fill="none" stroke="#a78bfa" stroke-width="2" stroke-dasharray="6 5"/><polygon points="345,220 339,230 351,230" fill="#a78bfa"/><text x="466" y="269" text-anchor="middle" fill="#c4b5fd" font-size="11">Résultat RADIUS : décision + attributs</text>
<text x="28" y="309" fill="#a1a1aa" font-size="12">Le serveur décide selon la politique ; le NAS applique le résultat à la session.</text>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Les lignes animées montrent les échanges, mais pas le détail de chaque paquet. Les rôles restent distincts : authentification centrale et application locale de la décision.</p></div>

> **Piège :** un serveur qui renvoie `Access-Accept` n’assure pas, à lui seul, que le poste obtient le bon VLAN ou la bonne ACL. Le NAS doit comprendre et appliquer les attributs retournés ; sa configuration peut aussi contenir une politique locale prioritaire.

### 1.2 Messages et machine à états

Le dialogue ne se réduit pas à « accepté » ou « refusé ». Le NAS envoie un `Access-Request`. Le serveur peut répondre par `Access-Accept`, `Access-Reject` ou `Access-Challenge`. Le challenge sert à poursuivre un échange, par exemple une étape EAP ou une autre méthode de vérification. Le NAS peut ensuite envoyer une nouvelle requête associée au processus.

Un timeout n’est pas un rejet : il signifie que le NAS n’a pas obtenu de réponse exploitable dans le délai prévu. Les causes possibles comprennent la perte réseau, un secret partagé incorrect, une ACL qui bloque UDP, une surcharge serveur ou une réponse que le client ne peut pas valider. Il faut conserver cette distinction dans les journaux et le dépannage.

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 310" role="img" aria-labelledby="radius-int-msg-title radius-int-msg-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-msg-title">Cycle des messages RADIUS</title><desc id="radius-int-msg-desc">Le NAS envoie Access-Request. Le serveur peut répondre Accept, Reject ou Challenge. Un Challenge conduit à une nouvelle étape et pas à une décision finale immédiate.</desc>
<rect x="1" y="1" width="958" height="308" rx="14" fill="#090d14" stroke="#3f3f46"/><text x="26" y="29" fill="#f4f4f5" font-size="18" font-weight="700">Cycle de décision et branches de réponse</text>
<rect x="44" y="56" width="184" height="62" rx="10" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="136" y="81" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">NAS / client RADIUS</text><text x="136" y="101" text-anchor="middle" fill="#bbf7d0" font-size="12">Envoie la demande</text>
<rect x="733" y="56" width="184" height="62" rx="10" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="825" y="81" text-anchor="middle" fill="#eff6ff" font-size="15" font-weight="700">Serveur RADIUS</text><text x="825" y="101" text-anchor="middle" fill="#bfdbfe" font-size="12">Évalue la politique</text>
<path class="radius-int-decision-flow" d="M228 74 H733" fill="none" stroke="#60a5fa" stroke-width="3"/><polygon points="733,74 721,67 721,81" fill="#60a5fa"/><text x="480" y="63" text-anchor="middle" fill="#93c5fd" font-size="13" font-weight="700">Access-Request</text>
<path d="M825 118 V148 H154 V185" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="154,185 147,173 161,173" fill="#4ade80"/><rect x="37" y="185" width="235" height="60" rx="10" fill="#102a23" stroke="#4ade80"/><text x="154" y="210" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">Access-Accept</text><text x="154" y="229" text-anchor="middle" fill="#bbf7d0" font-size="12">Autoriser et appliquer les attributs</text>
<path d="M825 118 V185" fill="none" stroke="#fb7185" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="825,185 818,173 832,173" fill="#fb7185"/><rect x="700" y="185" width="235" height="60" rx="10" fill="#321821" stroke="#fb7185"/><text x="817" y="210" text-anchor="middle" fill="#ffe4e6" font-size="15" font-weight="700">Access-Reject</text><text x="817" y="229" text-anchor="middle" fill="#fecdd3" font-size="12">Refus explicite de la demande</text>
<path d="M825 118 V145 H480 V185" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="480,185 473,173 487,173" fill="#fbbf24"/><rect x="362" y="185" width="235" height="60" rx="10" fill="#30240d" stroke="#fbbf24"/><text x="480" y="210" text-anchor="middle" fill="#fef3c7" font-size="15" font-weight="700">Access-Challenge</text><text x="480" y="229" text-anchor="middle" fill="#fde68a" font-size="12">Continuer le dialogue</text>
<path d="M480 245 V270 H136 V118" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="5 6"/><polygon points="136,118 130,130 142,130" fill="#fbbf24"/><text x="480" y="291" text-anchor="middle" fill="#fde68a" font-size="12">Réponse/challenge supplémentaire : une nouvelle étape peut être nécessaire</text>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Un `Access-Challenge` indique qu’un dialogue doit continuer. Le résultat final dépend de la suite de l’échange et de la méthode utilisée.</p></div>

> **Astuce :** pour trier un incident, notez séparément le nombre d’`Access-Accept`, d’`Access-Reject`, de timeouts et de challenges. Une hausse des refus suggère d’examiner la politique ou l’identité ; une hausse des timeouts pointe d’abord vers le transport, le serveur, le secret ou les délais.

### 1.3 Attributs RADIUS et application sur le NAS

Les attributs sont des couples de type et de valeur transportés dans les paquets. Ils décrivent notamment l’identité, l’adresse du NAS, le type de service demandé, les paramètres de session et les attributs de contrôle d’accès. Les attributs standards sont définis par les RFC ; les attributs propriétaires (VSA) dépendent du constructeur et de sa documentation.

Pour l’accès filaire ou Wi-Fi, les attributs peuvent déterminer un VLAN dynamique, un filtre, une ACL ou un rôle. Pour un VPN, ils peuvent influencer l’adresse attribuée, des routes ou les paramètres de session. Il ne faut pas supposer qu’un attribut est supporté parce qu’il existe dans une RFC ou parce qu’un autre modèle de switch l’applique : il faut confirmer la prise en charge de la plateforme, de la version logicielle et du contexte de service.

| Besoin | Ce qui est décidé centralement | Ce qui doit être vérifié sur le NAS |
|---|---|---|
| VLAN dynamique | valeur d’attribut conforme à la méthode supportée | VLAN présent, port autorisé, mapping correct |
| ACL ou filtre | nom/identifiant de filtre reconnu | ACL installée, sens d’application, ordre des règles |
| Session VPN | profil et attributs spécifiques | compatibilité client, routes, DNS et MTU |
| Durée d’accès | durée ou paramètres de session | comportement lorsque la session expire |
| Accounting | identifiant et informations de session | envoi des événements début/intermédiaire/fin |

### 1.4 Accounting, CoA et Disconnect

L’accounting suit le cycle d’une session. Un événement `Accounting-Start` signale généralement son commencement, `Interim-Update` fournit périodiquement des compteurs ou un état, et `Accounting-Stop` clôt la session. Les attributs exacts et la fréquence dépendent du NAS. Les événements peuvent être perdus pendant une coupure ; certains équipements réessaient l’envoi ou conservent temporairement les paquets comptables.

Le **Change of Authorization (CoA)** et le **Disconnect** permettent à un serveur de gestion de demander un changement ou la terminaison d’une session existante lorsque le NAS supporte ces mécanismes. Le CoA peut être utile après une modification de posture, de groupe ou de politique. Il doit être protégé par l’authentification du pair, filtré sur les bonnes adresses et tracé : une source non autorisée ne doit pas pouvoir révoquer les sessions d’utilisateurs.

### 1.5 RADIUS avec 802.1X et EAP

802.1X décrit le contrôle d’accès au port ; EAP transporte la méthode d’authentification ; RADIUS véhicule les messages entre l’équipement d’accès et le serveur. Le poste (supplicant) communique avec le switch ou l’AP au moyen d’EAPOL, puis le NAS encapsule les messages EAP dans des échanges RADIUS vers le serveur. Le NAS maintient le contrôle du port et applique le résultat fourni.

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 292" role="img" aria-labelledby="radius-int-eap-title radius-int-eap-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-eap-title">Échanges 802.1X, EAP et RADIUS</title><desc id="radius-int-eap-desc">Le poste envoie EAPOL au switch. Le switch relaie EAP dans RADIUS vers le serveur, reçoit le résultat et ouvre ou maintient le port selon la politique.</desc>
<rect x="1" y="1" width="958" height="290" rx="14" fill="#090d14" stroke="#3f3f46"/><text x="24" y="29" fill="#f4f4f5" font-size="18" font-weight="700">Qui parle à qui pendant 802.1X ?</text>
<rect x="30" y="62" width="235" height="90" rx="11" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="147" y="89" text-anchor="middle" fill="#eff6ff" font-size="15" font-weight="700">Supplicant</text><text x="147" y="112" text-anchor="middle" fill="#bfdbfe" font-size="13">Ordinateur / téléphone</text><text x="147" y="133" text-anchor="middle" fill="#cbd5e1" font-size="12">EAPOL vers le NAS</text>
<rect x="360" y="62" width="235" height="90" rx="11" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="477" y="89" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">Authentificateur / NAS</text><text x="477" y="112" text-anchor="middle" fill="#bbf7d0" font-size="13">Switch ou AP</text><text x="477" y="133" text-anchor="middle" fill="#d1fae5" font-size="12">Contrôle le port</text>
<rect x="690" y="62" width="235" height="90" rx="11" fill="#111827" stroke="#a78bfa" stroke-width="1.5"/><text x="807" y="89" text-anchor="middle" fill="#ede9fe" font-size="15" font-weight="700">Serveur RADIUS</text><text x="807" y="112" text-anchor="middle" fill="#ddd6fe" font-size="13">Méthode EAP / identité</text><text x="807" y="133" text-anchor="middle" fill="#ddd6fe" font-size="12">Applique la politique</text>
<path class="radius-int-eap-flow" d="M265 91 H360" fill="none" stroke="#60a5fa" stroke-width="3"/><polygon points="360,91 348,84 348,98" fill="#60a5fa"/><text x="312" y="79" text-anchor="middle" fill="#93c5fd" font-size="12">EAPOL</text>
<path class="radius-int-eap-flow" d="M595 91 H690" fill="none" stroke="#4ade80" stroke-width="3"/><polygon points="690,91 678,84 678,98" fill="#4ade80"/><text x="642" y="79" text-anchor="middle" fill="#86efac" font-size="12">RADIUS / EAP</text>
<path d="M690 132 H595" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6 5"/><polygon points="595,132 607,125 607,139" fill="#fbbf24"/><text x="642" y="150" text-anchor="middle" fill="#fde68a" font-size="11">Accept / Reject / Challenge</text>
<rect x="58" y="190" width="844" height="70" rx="10" fill="#111827" stroke="#52525b"/><text x="480" y="216" text-anchor="middle" fill="#f4f4f5" font-size="14" font-weight="700">Le NAS applique le résultat</text><text x="480" y="239" text-anchor="middle" fill="#cbd5e1" font-size="12">Port contrôlé, VLAN, rôle ou filtre — selon la configuration et les capacités du matériel</text>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Le poste ne contacte pas forcément directement le serveur RADIUS. Le NAS relaye l’authentification et demeure responsable de l’application locale de la politique.</p></div>

Le choix EAP est déterminant. EAP-TLS utilise des certificats côté client et serveur et nécessite une PKI correctement gérée. PEAP et EAP-TTLS reposent sur un tunnel TLS, mais leurs exigences de configuration diffèrent. Il faut valider le certificat du serveur côté client : accepter automatiquement n’importe quel certificat peut permettre une attaque de type faux serveur d’authentification.

> **Danger :** ne désactivez pas la validation du certificat serveur pour « faire fonctionner le Wi-Fi ». Cela peut rendre possible la collecte d’identifiants par un point d’accès malveillant. Distribuez plutôt la bonne autorité de certification et configurez explicitement les noms de serveurs attendus.

### 1.6 Transport et sécurité du protocole

RADIUS classique repose couramment sur UDP. Il utilise un secret partagé entre chaque client/NAS déclaré et le serveur. Le secret sert notamment à l’authentification de certains échanges et à la protection de certains attributs, mais **ne chiffre pas l’ensemble du paquet** et ne doit pas être présenté comme un chiffrement général du transport.

Pour réduire les risques : restreignez les clients autorisés, choisissez un secret aléatoire et unique par NAS lorsque c’est pris en charge, protégez la configuration, limitez les échanges par ACL et utilisez une protection de transport prise en charge lorsque l’architecture le permet. RADIUS/TLS ou RADIUS/DTLS peuvent améliorer la protection du transport si les équipements et le serveur les prennent correctement en charge. Ne supposez pas qu’un NAS plus ancien comprend automatiquement ces profils.

### 1.7 Calculs simples pour dimensionner le service

Une authentification en plusieurs étapes peut occasionner plusieurs échanges RADIUS. Une estimation de charge doit donc s’appuyer sur les échanges mesurés, pas uniquement sur le nombre de clients connectés. Si 300 appareils se reconnectent dans une minute et qu’un processus moyen génère quatre requêtes, la charge moyenne sur cette minute est :

\[
\text{requêtes/s moyennes} = \frac{300 \times 4}{60} = 20
\]

Cette moyenne masque les pointes. Un redémarrage de switch, une panne Wi-Fi ou l’expiration simultanée de sessions peuvent faire croître les demandes sur quelques secondes. Mesurez les taux de requêtes, le temps de réponse, les timeouts, les files de travail et la latence de la source d’identité.

| Indicateur | Ce qu’il révèle | À corréler avec |
|---|---|---|
| taux Access-Request | charge reçue | connexions/déconnexions, événements de port |
| taux Access-Reject | refus de politique ou d’identité | méthode EAP, groupes, certificats |
| timeout NAS | absence de réponse exploitable | UDP, ACL, secret, surcharge, délais |
| temps de réponse serveur | latence de décision | base d’identité, CPU, disque, réseau |
| sessions sans Stop | accounting incomplet ou interruption | reboot NAS, perte de paquet, durée de session |

---

## 2. Configuration et pratique

Les commandes qui suivent sont des modèles d’apprentissage. Les noms d’interfaces, la syntaxe des commandes et les méthodes acceptées changent selon la famille Cisco et la version IOS/IOS XE. Réalisez les premiers essais dans un laboratoire. Avant de modifier AAA sur un routeur distant, vérifiez la console ou un accès de secours et préparez un retour arrière.

### 2.1 Préparer un plan de déploiement

Exemple d’environnement de laboratoire :

| Élément | Valeur d’exemple | Rôle |
|---|---|---|
| Switch d’accès | `192.0.2.10` | client/NAS RADIUS |
| Serveur primaire | `192.0.2.20` | décision AAA |
| Serveur secondaire | `192.0.2.21` | continuité de service |
| VLAN de gestion | `192.0.2.0/24` | transport d’administration |
| Secret du laboratoire | valeur fournie hors du cours | partagé entre NAS et serveur |

Les adresses `192.0.2.0/24` sont réservées à la documentation et ne doivent pas être reprises telles quelles dans un réseau opérationnel. Générez un secret suffisamment long, stockez-le dans un gestionnaire de secrets et assurez-vous qu’il correspond de part et d’autre.

### 2.2 Vérifier la connectivité avant AAA

Sur l’équipement d’accès, vérifiez l’adresse source utilisée pour contacter le serveur, le routage et la connectivité IP. L’adresse du NAS déclarée sur le serveur doit correspondre à l’adresse source reçue ; sinon le serveur peut ignorer la requête ou la considérer comme un client inconnu.

```text
show ip interface brief
show ip route
show running-config | include source-interface
ping 192.0.2.20 source Vlan99
show logging
```

Toutes les commandes ne sont pas prises en charge sur chaque modèle. Si le `ping` est filtré, cela ne prouve pas à lui seul que UDP/1812 est bloqué ou autorisé : la politique réseau peut traiter ICMP et RADIUS différemment.

### 2.3 Configurer un client RADIUS sur Cisco IOS/IOS XE

Exemple indicatif pour un commutateur prenant en charge la syntaxe `radius server`. La clé affichée est un marqueur : remplacez-la par un secret réel hors du document.

```text
configure terminal
!
radius server RAD-PRIMARY
 address ipv4 192.0.2.20 auth-port 1812 acct-port 1813
 key <SECRET_PARTAGE_LAB>
!
radius server RAD-SECONDARY
 address ipv4 192.0.2.21 auth-port 1812 acct-port 1813
 key <SECRET_PARTAGE_LAB_SECONDARY>
!
aaa new-model
!
aaa group server radius RAD-GROUP
 server name RAD-PRIMARY
 server name RAD-SECONDARY
!
end
```

Selon la plateforme, le secret de chaque serveur peut être géré dans un coffre ou un mécanisme différent. Ne copiez pas littéralement les chevrons `<...>` dans un terminal : ils indiquent une valeur à substituer. Pour certains IOS plus anciens, la configuration utilise d’autres commandes comme `radius-server host`; consultez l’aide de la version installée.

### 2.4 Activer une méthode d’authentification avec filet de sécurité

La présence de `aaa new-model` seule ne déploie pas une politique complète. Définissez des méthodes explicites et comprenez l’ordre des méthodes. Si une méthode renvoie un refus explicite, le comportement peut différer d’une absence de réponse. Le mot-clé `local` n’est pas une garantie universelle de secours après chaque refus RADIUS : il dépend de la logique AAA et des résultats de la méthode précédente.

Avant d’appliquer AAA à l’accès distant :

1. créez et testez un compte local privilégié de secours selon la politique de l’organisation ;
2. testez une session console ou un canal hors bande ;
3. vérifiez la prise en charge de l’ordre des méthodes et les résultats de refus/timeouts sur la version exacte ;
4. gardez une session d’administration existante ouverte pendant le test ;
5. ne sauvegardez le changement qu’après validation d’une nouvelle connexion ;
6. préparez une procédure de retour arrière.

Exemple de base à adapter et à tester :

```text
configure terminal
username secours privilege 15 secret <SECRET_LOCAL_UNIQUE>
aaa authentication login ADMIN group RAD-GROUP local
line vty 0 4
 login authentication ADMIN
 transport input ssh
end
```

Cette syntaxe n’est pas un modèle universel. Certaines plateformes exigent une liste `default` ou des commandes supplémentaires pour les lignes VTY, la méthode EXEC, l’autorisation des commandes et l’accounting. Le but de l’exemple est de montrer la séparation entre la définition des serveurs et la méthode appliquée aux lignes d’accès.

> **Piège :** ne testez jamais pour la première fois une nouvelle liste AAA sur un équipement distant sans chemin de secours. Une erreur de liste, de source RADIUS ou de secret peut transformer une configuration fonctionnelle en verrouillage administratif.

### 2.5 Exemple FreeRADIUS : déclaration d’un NAS

Sur un serveur de laboratoire FreeRADIUS, déclarez chaque équipement d’accès explicitement dans la configuration des clients. L’emplacement et le nom exacts du fichier varient selon la distribution ; on retrouve souvent `clients.conf` ou un répertoire de fragments chargé par le service.

Exemple conceptuel :

```text
client switch-lab {
    ipaddr = 192.0.2.10
    secret = <SECRET_PARTAGE_LAB>
    shortname = switch-lab
}
```

Évitez les plages d’adresses trop larges et les secrets partagés entre tous les équipements. Une déclaration inconnue peut être ignorée, ce qui se manifeste côté NAS par un timeout plutôt que par un `Access-Reject`. Vérifiez les journaux du serveur dans un environnement de test et protégez-les : ils peuvent contenir des identifiants réseau, des adresses et des détails d’infrastructure.

Commandes de vérification courantes sur un système Linux, à adapter à la distribution :

```bash
sudo freeradius -XC
sudo systemctl status freeradius
sudo journalctl -u freeradius --since "10 minutes ago"
```

Le mode diagnostic au premier plan peut afficher des données sensibles. N’enregistrez pas les sorties complètes dans un ticket public et arrêtez le mode verbeux après le laboratoire.

### 2.6 Accounting : suivre le cycle de session

L’accounting doit être activé sur le NAS et configuré sur le serveur. Vérifiez au minimum que les événements de démarrage et d’arrêt arrivent, que l’identifiant de session est stable pour une même session et que la collecte interprète correctement les compteurs. Certains NAS envoient des mises à jour périodiques ; un intervalle très court produit davantage d’événements sans forcément apporter plus de valeur.

Schéma d’une session comptabilisée :

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 260" role="img" aria-labelledby="radius-int-acct-title radius-int-acct-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-acct-title">Cycle d'accounting RADIUS</title><desc id="radius-int-acct-desc">Un début de session, des mises à jour intermédiaires, puis un événement d'arrêt convergent vers les journaux d'accounting.</desc>
<rect x="1" y="1" width="958" height="258" rx="14" fill="#090d14" stroke="#3f3f46"/><text x="24" y="29" fill="#f4f4f5" font-size="18" font-weight="700">Traçabilité d’une session</text>
<rect x="30" y="80" width="190" height="78" rx="11" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="125" y="110" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">NAS / session</text><text x="125" y="133" text-anchor="middle" fill="#bbf7d0" font-size="12">Début → activité → fin</text>
<rect x="335" y="54" width="260" height="50" rx="9" fill="#102a23" stroke="#4ade80"/><text x="465" y="84" text-anchor="middle" fill="#dcfce7" font-size="14" font-weight="700">Accounting-Start</text>
<rect x="335" y="116" width="260" height="50" rx="9" fill="#111f37" stroke="#60a5fa"/><text x="465" y="146" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">Interim-Update</text>
<rect x="335" y="178" width="260" height="50" rx="9" fill="#321821" stroke="#fb7185"/><text x="465" y="208" text-anchor="middle" fill="#ffe4e6" font-size="14" font-weight="700">Accounting-Stop</text>
<rect x="710" y="91" width="220" height="100" rx="11" fill="#172033" stroke="#94a3b8" stroke-width="1.5"/><text x="820" y="121" text-anchor="middle" fill="#f1f5f9" font-size="15" font-weight="700">Stockage / SIEM</text><text x="820" y="145" text-anchor="middle" fill="#cbd5e1" font-size="12">Session-Id, temps,</text><text x="820" y="163" text-anchor="middle" fill="#cbd5e1" font-size="12">octets et durée</text>
<path d="M220 119 H274 V79 H335 M274 119 H335 M274 119 V203 H335" fill="none" stroke="#60a5fa" stroke-width="2.2"/><path class="radius-int-acct-flow" d="M595 79 H710 M595 141 H710 M595 203 H710" fill="none" stroke="#a78bfa" stroke-width="2.6"/><polygon points="710,79 699,73 699,85" fill="#a78bfa"/><polygon points="710,141 699,135 699,147" fill="#a78bfa"/><polygon points="710,203 699,197 699,209" fill="#a78bfa"/><text x="480" y="244" text-anchor="middle" fill="#a1a1aa" font-size="11">L’accounting complète les traces d’autorisation ; il ne remplace pas la décision d’accès.</text>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Les événements peuvent être perdus ou retardés lors d’une panne. Vérifiez la corrélation entre les journaux du NAS et ceux du serveur avant de conclure qu’une session n’a jamais existé.</p></div>

### 2.7 Tests fonctionnels après configuration

Utilisez une matrice courte et reproductible. Elle permet de distinguer un défaut de protocole d’un problème de politique ou d’application locale.

| Cas | Résultat attendu | Preuve à collecter |
|---|---|---|
| Identifiant connu, politique autorisée | Accept, session active | log serveur, session NAS |
| Identifiant valide mais groupe interdit | Reject | règle ayant refusé, groupe résolu |
| Serveur primaire inaccessible | bascule selon la politique | délai, serveur secondaire, résultat |
| Secret incorrect en laboratoire | erreur de traitement ou timeout selon implémentation | log serveur/NAS, capture de contrôle |
| VLAN demandé absent du switch | authentification possible mais application incorrecte/échec d’accès | attribut reçu, VLAN opérationnel |
| Accounting activé | Start et Stop visibles | Session-Id et timestamps corrélés |

> **Astuce :** testez aussi le cas de panne. Un système qui accepte un utilisateur en temps normal, mais refuse toute authentification lors d’une courte panne du serveur central, peut avoir un comportement conforme à la politique de sécurité mais inadapté aux besoins de continuité. La politique *fail-open/fail-closed* doit être décidée explicitement, documentée et validée.

---

## 3. Dépannage et sécurité

### 3.1 Algorithme de dépannage : trouver le premier plan en échec

Procédez par couches et évitez de changer plusieurs paramètres en même temps. Commencez par vérifier que le NAS contacte le bon serveur depuis la bonne adresse. Puis contrôlez la réponse RADIUS, la méthode EAP si présente, l’identité et la politique ; enfin, inspectez l’application des attributs et la session sur l’équipement.

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 410" role="img" aria-labelledby="radius-int-diag-title radius-int-diag-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-diag-title">Arbre de dépannage RADIUS</title><desc id="radius-int-diag-desc">Cinq vérifications alignées : source et routage, réponse RADIUS, EAP et certificat, politique et attributs, puis application locale et accounting. Les branches sont reliées sans traverser les libellés.</desc>
<rect x="1" y="1" width="958" height="408" rx="14" fill="#090d14" stroke="#3f3f46"/><text x="480" y="29" text-anchor="middle" fill="#f4f4f5" font-size="18" font-weight="700">Trouver le premier plan en échec</text>
<rect x="235" y="49" width="490" height="54" rx="10" fill="#13283a" stroke="#60a5fa" stroke-width="1.5"/><text x="480" y="72" text-anchor="middle" fill="#eff6ff" font-size="14" font-weight="700">1. Source NAS, routage et UDP/1812–1813</text><text x="480" y="90" text-anchor="middle" fill="#bfdbfe" font-size="11">Le serveur voit-il la requête du bon client ?</text>
<path class="radius-int-diag-flow" d="M480 103 V123" fill="none" stroke="#22d3ee" stroke-width="2.5"/><polygon points="480,125 473,113 487,113" fill="#22d3ee"/>
<rect x="235" y="127" width="490" height="54" rx="10" fill="#19191f" stroke="#71717a" stroke-width="1.5"/><text x="480" y="150" text-anchor="middle" fill="#f4f4f5" font-size="14" font-weight="700">2. Réponse : Accept, Reject, Challenge ou timeout ?</text><text x="480" y="168" text-anchor="middle" fill="#d4d4d8" font-size="11">Séparer refus explicite et absence de réponse</text>
<path class="radius-int-diag-flow" d="M480 181 V201" fill="none" stroke="#22d3ee" stroke-width="2.5"/><polygon points="480,203 473,191 487,191" fill="#22d3ee"/>
<rect x="235" y="205" width="490" height="54" rx="10" fill="#19191f" stroke="#71717a" stroke-width="1.5"/><text x="480" y="228" text-anchor="middle" fill="#f4f4f5" font-size="14" font-weight="700">3. EAP, certificat et identité</text><text x="480" y="246" text-anchor="middle" fill="#d4d4d8" font-size="11">Vérifier la méthode et la chaîne de confiance</text>
<path class="radius-int-diag-flow" d="M480 259 V279" fill="none" stroke="#22d3ee" stroke-width="2.5"/><polygon points="480,281 473,269 487,269" fill="#22d3ee"/>
<rect x="235" y="283" width="490" height="54" rx="10" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="480" y="306" text-anchor="middle" fill="#dcfce7" font-size="14" font-weight="700">4. Politique, groupes et attributs retournés</text><text x="480" y="324" text-anchor="middle" fill="#bbf7d0" font-size="11">Vérifier ce que le serveur a réellement envoyé</text>
<path class="radius-int-diag-flow" d="M480 337 V357" fill="none" stroke="#22d3ee" stroke-width="2.5"/><polygon points="480,359 473,347 487,347" fill="#22d3ee"/>
<rect x="235" y="361" width="490" height="36" rx="9" fill="#30240d" stroke="#fbbf24" stroke-width="1.5"/><text x="480" y="384" text-anchor="middle" fill="#fef3c7" font-size="13" font-weight="700">5. Application NAS, VLAN/ACL, session et accounting</text>
<rect x="24" y="122" width="178" height="72" rx="9" fill="#321821" stroke="#fb7185"/><text x="113" y="147" text-anchor="middle" fill="#ffe4e6" font-size="12" font-weight="700">Timeout</text><text x="113" y="166" text-anchor="middle" fill="#fecdd3" font-size="11">Transport, secret, charge</text><path d="M202 158 H220 V154 H235" fill="none" stroke="#fb7185" stroke-width="2"/><polygon points="235,154 225,148 225,160" fill="#fb7185"/>
<rect x="758" y="198" width="178" height="72" rx="9" fill="#30240d" stroke="#fbbf24"/><text x="847" y="222" text-anchor="middle" fill="#fef3c7" font-size="12" font-weight="700">Refus / EAP</text><text x="847" y="241" text-anchor="middle" fill="#fde68a" font-size="11">Identité, certificat, règle</text><path d="M725 232 H742 V234 H758" fill="none" stroke="#fbbf24" stroke-width="2"/><polygon points="758,234 748,228 748,240" fill="#fbbf24"/>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Suivez les étapes dans l’ordre et arrêtez-vous au premier endroit où la preuve ne correspond plus au comportement attendu. Les deux branches latérales donnent des pistes, pas des conclusions définitives.</p></div>

### 3.2 Cas 1 — le NAS signale un timeout

**Symptôme :** les connexions échouent, mais aucun `Access-Reject` n’apparaît dans les journaux applicatifs. Le NAS indique que le serveur ne répond pas.

Procédure :

1. Confirmez l’adresse et l’interface source utilisées par le NAS.
2. Vérifiez route, ACL et chemin retour entre cette adresse et le serveur.
3. Confirmez que le serveur écoute sur le port et le transport attendus.
4. Vérifiez que l’adresse source du paquet correspond à un client déclaré.
5. Comparez le secret des deux côtés et cherchez des erreurs d’authentification de paquet.
6. Contrôlez la charge CPU, la latence d’annuaire, les files et les délais du serveur.
7. Mesurez le comportement de basculement vers le secondaire.

Une capture peut confirmer si la requête quitte le NAS et si une réponse revient, mais la présence d’un paquet ne garantit pas qu’il est accepté par le service. Limitez la capture au flux nécessaire et protégez le fichier : RADIUS peut révéler des métadonnées sensibles.

### 3.3 Cas 2 — Access-Accept, mais pas d’accès réseau

Dans ce cas, l’authentification centrale a abouti, mais il reste à vérifier l’autorisation appliquée localement. Contrôlez :

- le VLAN ou le rôle réellement affecté à la session ;
- l’existence du VLAN sur le switch et le transport sur les trunks ;
- la présence et le sens d’application de l’ACL ;
- l’adresse IP reçue par DHCP, la passerelle, le DNS et les routes ;
- les attributs standards ou propriétaires, ainsi que leur correspondance exacte ;
- les politiques locales qui peuvent remplacer ou compléter les attributs RADIUS.

Ne corrigez pas le problème en donnant arbitrairement un accès plus large. Comparez la session affectée à une session fonctionnelle du même profil et faites varier un seul paramètre à la fois.

### 3.4 Cas 3 — l’authentification 802.1X échoue après un changement de certificat

Vérifiez d’abord la date et l’heure du client, de l’équipement et du serveur. Une horloge incorrecte peut rendre un certificat invalide. Confirmez ensuite que la chaîne de certification est complète, que le certificat est dans sa période de validité, qu’il correspond à l’identité attendue et que les clients possèdent l’autorité de confiance correcte.

Vérifiez aussi que la méthode EAP côté supplicant correspond à celle autorisée côté serveur. Un serveur peut avoir un certificat valide mais présenter un nom inattendu ; le client doit valider la chaîne et l’identité, pas uniquement accepter qu’un certificat existe. Ne désactivez pas la vérification pour rétablir rapidement le service.

### 3.5 Redondance et stratégie de panne

La configuration de plusieurs serveurs ne suffit pas à prouver la haute disponibilité. Le client NAS doit savoir quand un serveur est indisponible, combien de temps attendre, quand basculer, comment réessayer et quand revenir au serveur préféré. Les temporisations trop longues affectent l’expérience utilisateur ; les temporisations trop courtes peuvent déclarer à tort un serveur sain comme mort lors d’un pic de charge.

<div class="radius-visual" style="width:100%;max-width:100%;min-width:0;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 960 275" role="img" aria-labelledby="radius-int-ha-title radius-int-ha-desc" style="display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px">
<title id="radius-int-ha-title">Basculement RADIUS</title><desc id="radius-int-ha-desc">Le NAS tente le serveur primaire. En cas de timeout, la politique de temporisation déclenche une tentative sur le serveur secondaire. Une réponse doit être confirmée avant de considérer le basculement réussi.</desc>
<rect x="1" y="1" width="958" height="273" rx="14" fill="#090d14" stroke="#3f3f46"/><text x="24" y="29" fill="#f4f4f5" font-size="18" font-weight="700">Basculement : le timeout est une décision opérationnelle</text>
<rect x="32" y="88" width="180" height="84" rx="11" fill="#102a23" stroke="#4ade80" stroke-width="1.5"/><text x="122" y="117" text-anchor="middle" fill="#dcfce7" font-size="15" font-weight="700">NAS</text><text x="122" y="141" text-anchor="middle" fill="#bbf7d0" font-size="12">Demande d’accès</text>
<rect x="354" y="54" width="220" height="72" rx="11" fill="#321821" stroke="#fb7185" stroke-width="1.5"/><text x="464" y="82" text-anchor="middle" fill="#ffe4e6" font-size="15" font-weight="700">Serveur primaire</text><text x="464" y="103" text-anchor="middle" fill="#fecdd3" font-size="12">Pas de réponse / timeout</text>
<rect x="354" y="164" width="220" height="72" rx="11" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="464" y="192" text-anchor="middle" fill="#eff6ff" font-size="15" font-weight="700">Serveur secondaire</text><text x="464" y="213" text-anchor="middle" fill="#bfdbfe" font-size="12">Tentative puis réponse</text>
<rect x="714" y="96" width="214" height="78" rx="11" fill="#172033" stroke="#94a3b8" stroke-width="1.5"/><text x="821" y="123" text-anchor="middle" fill="#f1f5f9" font-size="14" font-weight="700">Validation opérationnelle</text><text x="821" y="145" text-anchor="middle" fill="#cbd5e1" font-size="12">Session, VLAN/ACL, journaux</text>
<path class="radius-int-failover-flow" d="M212 105 H354" fill="none" stroke="#fb7185" stroke-width="3"/><polygon points="354,105 342,98 342,112" fill="#fb7185"/><text x="283" y="93" text-anchor="middle" fill="#fda4af" font-size="11">1 · Primaire</text>
<path class="radius-int-failover-flow" d="M212 153 H292 V200 H354" fill="none" stroke="#60a5fa" stroke-width="3"/><polygon points="354,200 342,193 342,207" fill="#60a5fa"/><text x="284" y="188" text-anchor="middle" fill="#93c5fd" font-size="11">2 · Après timeout</text>
<path d="M574 200 H649 V135 H714" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 6"/><polygon points="714,135 702,128 702,142" fill="#4ade80"/><text x="646" y="123" text-anchor="middle" fill="#86efac" font-size="11">3 · Réponse testée</text>
<text x="480" y="258" text-anchor="middle" fill="#a1a1aa" font-size="12">Mesurer le délai total et les sessions impactées ; ne pas conclure sur la seule présence d’un serveur secondaire.</text>
</svg><p class="radius-visual__caption" style="margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7">Une bascule est réussie lorsque la nouvelle authentification et l’accès réseau fonctionnent, pas seulement lorsque le NAS envoie une requête au secondaire.</p></div>

> **Piège :** un serveur de secours qui utilise une base d’identités ou une politique différente peut répondre rapidement tout en accordant le mauvais accès. Répliquez et contrôlez les politiques, certificats, groupes et secrets de manière sécurisée.

### 3.6 Sécurité opérationnelle

**Secrets et configuration.** Limitez la lecture des configurations, évitez les secrets dans les dépôts de code et dans les scripts de diagnostic. Faites tourner un secret en synchronisant le changement entre NAS et serveur, avec un plan de retour arrière. Ne collez jamais les journaux RADIUS complets dans un ticket ou une conversation publique.

**Filtrage réseau.** N’autorisez les ports RADIUS que depuis les adresses NAS prévues vers les serveurs. Les réponses doivent revenir par le chemin autorisé. Les requêtes CoA/Disconnect doivent être restreintes plus strictement encore, car elles modifient des sessions actives.

**Moindre privilège.** Définissez des politiques séparées pour l’administration des équipements, l’accès filaire, le Wi-Fi invité, les terminaux gérés et les accès VPN. Un refus d’accès invité ne doit pas affecter la gestion de l’équipement. Les comptes de service ne doivent pas disposer de privilèges interactifs inutiles.

**Confidentialité des journaux.** Les attributs RADIUS peuvent contenir des noms d’utilisateur, des adresses, des identifiants de NAS, des durées de session et des informations d’accounting. Appliquez le contrôle d’accès, une durée de conservation documentée et la suppression des champs inutiles.

**Validation des changements.** Utilisez un environnement de test, une fenêtre de maintenance et une matrice de test. Gardez une session d’administration de secours, recueillez les états avant/après, et annulez le changement si les résultats sortent des seuils acceptés.

### 3.7 Étude de cas : les utilisateurs Wi-Fi sont rejetés après une modification de groupe

**Contexte :** les utilisateurs du service Finance se connectaient auparavant au SSID entreprise. Après une mise à jour de l’annuaire, ils reçoivent un refus. Les comptes fonctionnent encore pour d’autres applications.

**Hypothèses à comparer :** le groupe n’est plus résolu comme attendu ; la règle RADIUS utilise un nom de groupe erroné ; les attributs d’identité reçus changent de casse ou de format ; la méthode EAP échoue avant même l’étape de politique ; le NAS applique un cache ou une politique locale différente.

**Méthode :** choisissez un utilisateur de test autorisé et un utilisateur de test non autorisé. Collectez pour une seule tentative horodatée le journal serveur, l’identité canonique et les groupes résolus. Déterminez si le serveur renvoie réellement Reject ou si le NAS expire. Comparez la règle ayant été sélectionnée avec celle d’un utilisateur de référence. Corrigez une condition à la fois et vérifiez que l’utilisateur non autorisé reste refusé.

**Critères de réussite :** le compte autorisé accède au VLAN attendu, l’ACL est appliquée, l’accounting est complet, l’utilisateur non autorisé reste bloqué, et l’ancien comportement peut être restauré si une autre application de politique est touchée.

### 3.8 Étude de cas : le serveur répond Accept mais l’accounting est incomplet

**Symptôme :** l’utilisateur a accès au réseau, mais les rapports de session n’enregistrent que les débuts ou que les mises à jour. Vérifiez la configuration du port accounting, les règles de filtrage UDP/1813, l’horodatage des systèmes, la politique de retry du NAS et la capacité de stockage côté serveur.

Ne concluez pas qu’un `Accounting-Stop` est absent uniquement parce que le tableau de bord ne l’affiche pas. Vérifiez les journaux bruts, les éventuelles déduplications, le `Acct-Session-Id`, les NAS-Port-Id et les horodatages. Si le NAS redémarre ou perd le réseau, il peut ne jamais transmettre l’événement final. Le système de reporting doit pouvoir marquer une session comme incomplète plutôt que d’inventer une heure de fermeture.

### 3.9 Contrôle de changement : déploiement en trois phases

1. **Préparation :** sauvegarder la configuration, exporter la politique serveur, vérifier les certificats, inventorier les NAS et préparer deux comptes de test (autorisé/refusé).
2. **Pilote :** appliquer la nouvelle règle à un équipement ou un petit groupe, suivre les Accept/Reject/timeouts et vérifier les attributs appliqués.
3. **Généralisation :** élargir par lots. Arrêter le déploiement si la latence ou le taux de refus sort des seuils décidés. Après chaque lot, effectuer une nouvelle connexion et confirmer le chemin de secours.

### 3.10 Checklist opérationnelle

- [ ] L’adresse source du NAS est stable et déclarée sur le serveur.
- [ ] Les secrets sont uniques, protégés et identiques des deux côtés.
- [ ] Les routes, ACL et ports de transport sont validés.
- [ ] La politique distingue explicitement Accept, Reject et timeout.
- [ ] Le chemin de secours a été testé pendant une panne simulée.
- [ ] Les attributs reçus sont compris et correctement appliqués par le NAS.
- [ ] Les certificats EAP sont vérifiés par les clients.
- [ ] CoA/Disconnect sont limités à des pairs autorisés.
- [ ] Accounting-Start, Interim-Update et Stop sont corrélés.
- [ ] Les journaux et captures protègent les données d’identité.
- [ ] Les étapes de retour arrière sont documentées et testées.

---

## Points à retenir

- RADIUS centralise l’authentification et la politique, mais le NAS applique les décisions à la session.
- Un `Access-Reject` est une décision explicite ; un timeout est une absence de réponse exploitable. Ils ne se diagnostiquent pas de la même manière.
- Les attributs standards et propriétaires doivent être validés avec la documentation de la plateforme.
- 802.1X contrôle l’accès au port, EAP transporte la méthode, et RADIUS relie le NAS au serveur.
- L’accounting décrit le cycle de session mais peut être incomplet en cas de panne.
- La redondance exige de valider les délais, le comportement de bascule et la cohérence des politiques.
- Ne désactivez pas la validation des certificats EAP et ne modifiez pas AAA à distance sans accès de secours.
- Utilisez une matrice de test, un pilote, des journaux corrélés et un retour arrière documenté pour chaque changement.

## Exercices corrigés

### Exercice 1 — Requête sans réponse

**Question :** le NAS journalise des timeouts. Aucun refus n’apparaît dans la console du serveur. Quelle est la première enquête ?

**Correction :** confirmer l’adresse source réelle du NAS, le client déclaré, le chemin IP et le retour UDP, le port d’écoute, le secret partagé et les journaux de transport. Un timeout n’est pas la preuve que le mot de passe utilisateur est faux.

### Exercice 2 — Accept mais mauvais VLAN

**Question :** le serveur renvoie Accept, mais le poste reçoit une adresse d’un VLAN inattendu. Que faut-il vérifier ?

**Correction :** inspecter les attributs de la réponse, le support des attributs par le NAS, le mapping VLAN local, la présence du VLAN, les trunks, le DHCP et les politiques locales prioritaires. Ne pas ouvrir tout le réseau pour contourner l’erreur.

### Exercice 3 — Port sécurisé après changement de certificat

**Question :** les postes refusent le serveur depuis le renouvellement de certificat. Quelle séquence est sûre ?

**Correction :** contrôler l’heure, le nom du serveur, la période de validité et la chaîne de certification ; vérifier la méthode EAP et l’autorité distribuée aux clients. Ne pas désactiver la validation serveur pour rétablir le service.

### Exercice 4 — Serveur secondaire actif

**Question :** la bascule fonctionne, mais les utilisateurs invités obtiennent désormais l’accès interne. Quel risque est probable ?

**Correction :** divergence de politiques, de groupes ou d’attributs sur le serveur secondaire. Comparer les règles et les données répliquées, valider avec un compte autorisé et un compte interdit, et corriger la cohérence avant de généraliser.

### Exercice 5 — Sessions sans événement Stop

**Question :** les dashboards montrent des sessions sans clôture. Est-ce nécessairement une erreur RADIUS ?

**Correction :** non. Corréler les journaux bruts, les identifiants de session, l’état du NAS, la connectivité accounting, les retries et la logique de reporting. Marquer les sessions comme incomplètes si la preuve de clôture manque.

## Glossaire

| Terme | Définition |
|---|---|
| AAA | Authentication, Authorization, Accounting. |
| NAS | Network Access Server, équipement qui contrôle l’accès et agit comme client RADIUS. |
| EAP | Extensible Authentication Protocol, cadre pour diverses méthodes d’authentification. |
| EAPOL | Transport EAP entre supplicant et équipement d’accès sur un LAN. |
| Access-Request | Requête RADIUS demandant l’évaluation d’une tentative ou d’un échange. |
| Access-Accept | Réponse d’autorisation positive accompagnée éventuellement d’attributs. |
| Access-Reject | Refus explicite de la demande. |
| Access-Challenge | Réponse qui demande de poursuivre l’échange. |
| Accounting | Enregistrements du cycle et des compteurs d’une session. |
| CoA | Change of Authorization, demande de changement sur une session active. |
| VSA | Vendor-Specific Attribute, attribut défini par un constructeur. |
| EAP-TLS | Méthode EAP qui repose sur TLS et des certificats. |
| Secret partagé | Valeur commune au NAS et au serveur, à protéger et gérer par équipement. |
| Fail-closed | En cas d’échec de contrôle, l’accès est refusé. |
| Fail-open | En cas d’échec de contrôle, un accès est permis selon une politique exceptionnelle. |

## Références techniques

- **RFC 2865** — Remote Authentication Dial In User Service (RADIUS), format et messages d’authentification/autorisation.
- **RFC 2866** — RADIUS Accounting.
- **RFC 3579** — RADIUS Support for EAP.
- **RFC 3580** — IEEE 802.1X RADIUS Usage Guidelines.
- **RFC 5176** — Dynamic Authorization Extensions to RADIUS (Disconnect et Change of Authorization).
- **RFC 6614** — Transport Layer Security (TLS) Encryption for RADIUS.
- **RFC 9765** — RADIUS/1.1, profil expérimental à évaluer selon les implémentations et la politique locale.
- **Documentation Cisco IOS/IOS XE** — commandes AAA, serveur RADIUS, 802.1X et attributs spécifiques à la plateforme.
- **Documentation FreeRADIUS** — configuration des clients, politiques, EAP et diagnostic serveur.

Les commandes et les attributs constructeurs doivent être confirmés dans la documentation correspondant exactement au modèle et à la version du logiciel installé.
