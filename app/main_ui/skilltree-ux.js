
    /* Skill Tree — fiabilisation et extensions UX, sans modifier les contrats API existants. */
    (function () {
      const baseFactory = window.skilltree;
      if (typeof baseFactory !== 'function') return;

      const BUILTIN_TOPO_CHALLENGES = [
        { id: 'builtin-office-lan', title: 'Réseau de bureau', level: 'debutant', levelLabel: '🌱 Débutant', minutes: 5,
          description: 'Construis un LAN simple : un routeur vers un switch, puis deux PC sur le switch. Objectif : comprendre le chemin d’accès et la topologie physique.',
          timeLimit: 300, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'switch' }, { type: 'pc', peer: 'switch' }],
          expected: { nodes: { router: 1, switch: 1, pc: 2 }, connections: [{ from: 'router', to: 'switch' }, { from: 'switch', to: 'pc' }, { from: 'switch', to: 'pc' }] } },
        { id: 'builtin-service-lan', title: 'LAN avec serveur', level: 'debutant', levelLabel: '🌱 Débutant', minutes: 6,
          description: 'Relie un poste et un serveur au même switch, puis relie le switch au routeur de sortie.',
          timeLimit: 360, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'switch' }, { type: 'pc', peer: 'switch' }, { type: 'server', peer: 'switch' }],
          expected: { nodes: { router: 1, switch: 1, pc: 1, server: 1 }, connections: [{ from: 'router', to: 'switch' }, { from: 'switch', to: 'pc' }, { from: 'switch', to: 'server' }] } },
        { id: 'builtin-intervlan', title: 'Routage inter-VLAN', level: 'intermediaire', levelLabel: '🚀 Intermédiaire', minutes: 8,
          description: 'Modélise un routeur-on-a-stick : un routeur rejoint un switch et deux postes représentent deux VLAN distincts. La validation contrôle la structure ; les VLAN et le trunk doivent être configurés dans le lab CLI.',
          timeLimit: 480, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'switch' }, { type: 'pc', peer: 'switch' }, { type: 'server', peer: 'switch' }],
          expected: { nodes: { router: 1, switch: 1, pc: 2, server: 1 }, connections: [{ from: 'router', to: 'switch' }, { from: 'switch', to: 'pc' }, { from: 'switch', to: 'pc' }, { from: 'switch', to: 'server' }] } },
        { id: 'builtin-dmz', title: 'DMZ segmentée', level: 'intermediaire', levelLabel: '🚀 Intermédiaire', minutes: 10,
          description: 'Place le pare-feu entre le routeur externe et le réseau interne ; le switch dessert un serveur et un poste interne.',
          timeLimit: 600, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'firewall' }, { type: 'firewall', peer: 'switch' }, { type: 'server', peer: 'switch' }, { type: 'pc', peer: 'switch' }],
          expected: { nodes: { router: 1, firewall: 1, switch: 1, server: 1, pc: 1 }, connections: [{ from: 'router', to: 'firewall' }, { from: 'firewall', to: 'switch' }, { from: 'switch', to: 'server' }, { from: 'switch', to: 'pc' }] } },
        { id: 'builtin-wifi-access', title: 'Réseau Wi-Fi d’entreprise', level: 'intermediaire', levelLabel: '🚀 Intermédiaire', minutes: 8,
          description: 'Relie le routeur au switch, le point d’accès au switch, le client Wi-Fi au point d’accès (liaison logique d’association) et le serveur au switch. Ce défi vérifie les connexions représentées, pas la configuration radio.',
          timeLimit: 480, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'switch' }, { type: 'wifi', peer: 'switch' }, { type: 'laptop', peer: 'wifi' }, { type: 'server', peer: 'switch' }],
          expected: { nodes: { router: 1, switch: 1, wifi: 1, laptop: 1, server: 1 }, connections: [{ from: 'router', to: 'switch' }, { from: 'switch', to: 'wifi' }, { from: 'wifi', to: 'laptop' }, { from: 'switch', to: 'server' }] } },
        { id: 'builtin-spine-leaf', title: 'Fabric Spine/Leaf redondante', level: 'expert', levelLabel: '🔥 Expert', minutes: 12,
          description: 'Construis une fabric à deux Spine et deux Leaf. Chaque Leaf doit être connecté aux deux Spine : quatre liaisons au total, sans liaison Leaf–Leaf ni Spine–Spine.',
          timeLimit: 720, minScore: 100, requireCompleteBipartite: ['spine', 'leaf'],
          expected: { nodes: { spine: 2, leaf: 2 }, connections: [{ from: 'spine', to: 'leaf' }, { from: 'spine', to: 'leaf' }, { from: 'spine', to: 'leaf' }, { from: 'spine', to: 'leaf' }] } },
        { id: 'builtin-edge-ha', title: 'Périmètre haute disponibilité', level: 'expert', levelLabel: '🔥 Expert', minutes: 12,
          description: 'Représente une sortie redondante : deux routeurs, deux pare-feu, un switch et un serveur. Chaque routeur rejoint un pare-feu, les deux pare-feu rejoignent le switch et le switch rejoint le serveur.',
          timeLimit: 720, minScore: 100,
          requireTypeCoverage: [{ type: 'router', peer: 'firewall' }, { type: 'firewall', peer: 'switch' }, { type: 'server', peer: 'switch' }],
          expected: { nodes: { router: 2, firewall: 2, switch: 1, server: 1 }, connections: [{ from: 'router', to: 'firewall' }, { from: 'router', to: 'firewall' }, { from: 'firewall', to: 'switch' }, { from: 'firewall', to: 'switch' }, { from: 'switch', to: 'server' }] } }
      ];

      const BUILTIN_CHALLENGE_BRIEFS = {
        "builtin-office-lan": {
          "context": "Un nouveau poste doit rejoindre un bureau et communiquer avec les autres réseaux. Avant de configurer les adresses, vérifie que son chemin physique vers la passerelle est cohérent.",
          "objectives": [
            "Distinguer la distribution locale de la sortie réseau.",
            "Construire un chemin simple vers la passerelle."
          ],
          "concepts": [
            {
              "term": "Switch",
              "explanation": "Relie les hôtes d’un même LAN."
            },
            {
              "term": "Routeur",
              "explanation": "Permet de joindre d’autres réseaux IP."
            },
            {
              "term": "Passerelle par défaut",
              "explanation": "Point de sortie d’un hôte vers un réseau distant."
            }
          ],
          "mission_steps": [
            "Place un routeur, un switch et deux PC.",
            "Relie la passerelle au switch.",
            "Raccorde les deux PC au switch.",
            "Vérifie les connexions."
          ],
          "success_criteria": [
            "Les deux PC sont connectés au switch.",
            "Le routeur est relié au switch.",
            "Aucun équipement requis n’est isolé."
          ],
          "hints": [
            "Le switch distribue la connectivité locale.",
            "La passerelle se raccorde au LAN via le switch."
          ],
          "evaluation_scope": "Exercice local de topologie uniquement : pas de progression serveur ni de validation d’adressage IP.",
          "debrief": "Une fois les liens corrects, configure le plan IP, la passerelle des PC et teste la connectivité."
        },
        "builtin-service-lan": {
          "context": "Un bureau utilise un poste client et un serveur interne. Les deux appareils doivent rejoindre le même réseau local tout en conservant un chemin vers la sortie réseau.",
          "objectives": [
            "Distinguer le rôle client du rôle serveur.",
            "Raccorder les hôtes et la passerelle à l’infrastructure locale."
          ],
          "concepts": [
            {
              "term": "Client",
              "explanation": "Consomme un service réseau."
            },
            {
              "term": "Serveur",
              "explanation": "Héberge un service qui doit être joignable depuis les zones autorisées."
            },
            {
              "term": "LAN",
              "explanation": "Réseau local des terminaux et de leur distribution."
            }
          ],
          "mission_steps": [
            "Place routeur et switch.",
            "Relie le switch au routeur.",
            "Ajoute le client et le serveur au switch.",
            "Vérifie les trois liaisons."
          ],
          "success_criteria": [
            "Le routeur et le switch sont reliés.",
            "Le client et le serveur sont chacun reliés au switch."
          ],
          "hints": [
            "Le switch est le point de distribution du LAN.",
            "Un serveur posé dans le canevas mais isolé ne rend aucun service."
          ],
          "evaluation_scope": "L’exercice vérifie les liaisons dessinées, pas DNS, HTTP, les adresses ni le filtrage.",
          "debrief": "La topologie ne prouve pas qu’un service fonctionne. Vérifie ensuite l’adresse du serveur, le service actif et les règles d’accès."
        },
        "builtin-intervlan": {
          "context": "Deux équipes doivent rester séparées logiquement tout en partageant l’infrastructure physique. Tu représentes la structure de routage inter-VLAN avant de configurer les VLAN et le trunk.",
          "objectives": [
            "Comprendre le rôle du routeur entre VLAN.",
            "Préparer un schéma que tu configureras ensuite dans le lab CLI."
          ],
          "concepts": [
            {
              "term": "VLAN",
              "explanation": "Sépare logiquement les domaines de broadcast."
            },
            {
              "term": "Trunk 802.1Q",
              "explanation": "Transporte plusieurs VLAN sur une liaison balisée."
            },
            {
              "term": "Router-on-a-stick",
              "explanation": "Utilise les sous-interfaces d’un routeur sur un trunk pour router entre VLAN."
            }
          ],
          "mission_steps": [
            "Place routeur, switch, deux PC et serveur.",
            "Relie le routeur au switch.",
            "Raccorde les terminaux au switch.",
            "Dans le lab CLI, configure VLAN, trunk et sous-interfaces."
          ],
          "success_criteria": [
            "Le routeur est relié au switch.",
            "Les deux PC et le serveur sont raccordés au switch.",
            "Tu sais quelles configurations restent à vérifier dans le lab."
          ],
          "hints": [
            "Les deux PC représentent des zones logiques distinctes.",
            "Le schéma n’affiche pas encore les identifiants VLAN."
          ],
          "evaluation_scope": "La vérification locale contrôle la structure, pas les VLAN, le trunk ou les sous-interfaces.",
          "debrief": "Il faut vérifier l’appartenance aux VLAN, les modes d’accès/trunk, les sous-interfaces et les passerelles des hôtes."
        },
        "builtin-dmz": {
          "context": "Un service doit être accessible depuis l’extérieur sans exposer directement le réseau des employés. La DMZ fournit une zone intermédiaire et des contrôles de flux propres.",
          "objectives": [
            "Expliquer le rôle d’une DMZ.",
            "Placer le filtrage sur le chemin vers le réseau interne."
          ],
          "concepts": [
            {
              "term": "DMZ",
              "explanation": "Zone intermédiaire pour les services publiés."
            },
            {
              "term": "Moindre privilège",
              "explanation": "N’autoriser que les communications nécessaires."
            },
            {
              "term": "Filtrage par zone",
              "explanation": "Les flux entre extérieur, DMZ et LAN doivent être contrôlés."
            }
          ],
          "mission_steps": [
            "Construis le chemin depuis le routeur externe vers le pare-feu.",
            "Place le switch réseau local derrière la frontière de sécurité.",
            "Raccorde le serveur et le poste au switch.",
            "Identifie les flux à autoriser dans un vrai lab de sécurité."
          ],
          "success_criteria": [
            "Le routeur rejoint le pare-feu avant le LAN.",
            "Le switch est relié au pare-feu.",
            "Le serveur et le PC sont connectés au switch."
          ],
          "hints": [
            "Une DMZ n’est pas simplement un serveur près d’un pare-feu.",
            "Réfléchis aux flux qui doivent être accessibles depuis Internet."
          ],
          "evaluation_scope": "La topologie locale ne valide pas les règles firewall ni l’isolation réelle de la DMZ.",
          "debrief": "Traduis le schéma en interfaces, zones et règles restrictives, puis vérifie les flux autorisés et interdits."
        },
        "builtin-wifi-access": {
          "context": "Une salle de réunion doit disposer du Wi-Fi sans raccorder les clients mobiles directement au réseau câblé. Tu représentes le point d’accès et le chemin vers l’infrastructure.",
          "objectives": [
            "Distinguer point d’accès et client Wi-Fi.",
            "Comprendre les limites d’un schéma par rapport à une configuration radio réelle."
          ],
          "concepts": [
            {
              "term": "Point d’accès",
              "explanation": "Fait le pont entre les clients sans fil et le réseau filaire."
            },
            {
              "term": "SSID et sécurité radio",
              "explanation": "Le SSID identifie le réseau ; WPA2/WPA3 protègent son accès."
            },
            {
              "term": "VLAN du SSID",
              "explanation": "Le VLAN associé au SSID détermine vers quelle zone réseau le trafic est envoyé."
            }
          ],
          "mission_steps": [
            "Place routeur, switch et point d’accès.",
            "Raccorde l’AP au switch.",
            "Représente l’association du portable à l’AP.",
            "Ajoute le serveur et réfléchis au SSID et au VLAN à configurer ensuite."
          ],
          "success_criteria": [
            "Le routeur et l’AP rejoignent le réseau de distribution.",
            "Le portable est lié au point d’accès.",
            "Le serveur est raccordé au LAN."
          ],
          "hints": [
            "Le lien portable–AP est une association logique, pas un câble.",
            "Le point d’accès doit lui-même rejoindre le réseau qui transporte les clients."
          ],
          "evaluation_scope": "La topologie ne simule pas les ondes, l’authentification, le chiffrement ni le roaming.",
          "debrief": "Vérifie SSID, protection radio, plan RF, VLAN et configuration du port filaire de l’AP dans le lab réel."
        },
        "builtin-spine-leaf": {
          "context": "Tu conçois une petite fabric de datacenter : les serveurs sont raccordés aux Leaf et les Spine assurent le transit. L’objectif est que chaque Leaf dispose de plusieurs chemins vers le cœur de la fabric.",
          "objectives": [
            "Distinguer les rôles Spine et Leaf.",
            "Construire les quatre liaisons croisées."
          ],
          "concepts": [
            {
              "term": "Leaf",
              "explanation": "Point de raccordement des serveurs."
            },
            {
              "term": "Spine",
              "explanation": "Couche de transit qui relie les Leaf."
            },
            {
              "term": "ECMP",
              "explanation": "Permet d’utiliser plusieurs chemins de coût égal si le routage est configuré ainsi."
            }
          ],
          "mission_steps": [
            "Place deux Spine et deux Leaf en deux rangées.",
            "Relie chaque Spine à chaque Leaf.",
            "Vérifie toutes les paires possibles.",
            "Dans un vrai déploiement, teste le routage et les pannes."
          ],
          "success_criteria": [
            "Toutes les paires Spine–Leaf sont connectées.",
            "Aucun Spine ou Leaf n’est isolé.",
            "Aucun lien non attendu ne remplace une paire requise."
          ],
          "hints": [
            "Énumère les deux voisins Leaf de chaque Spine.",
            "Il faut obtenir les quatre combinaisons possibles."
          ],
          "evaluation_scope": "Exercice local sans validation serveur ; il ne teste pas BGP/OSPF ou ECMP.",
          "debrief": "La connectivité croisée fournit des chemins disponibles, mais la disponibilité réelle dépend du routage et du comportement à la panne."
        },
        "builtin-edge-ha": {
          "context": "Une entreprise veut réduire l’impact d’une panne de la périphérie réseau. Tu représentes une sortie avec deux routeurs et deux pare-feu avant de travailler les mécanismes de haute disponibilité.",
          "objectives": [
            "Identifier les composants redondants de la périphérie.",
            "Distinguer des équipements dupliqués d’une haute disponibilité configurée."
          ],
          "concepts": [
            {
              "term": "Redondance",
              "explanation": "Fournit des alternatives quand un composant tombe en panne."
            },
            {
              "term": "Paire HA de pare-feu",
              "explanation": "Exige un mécanisme de basculement et souvent une synchronisation d’état."
            },
            {
              "term": "Domaine de défaillance",
              "explanation": "Des équipements distincts peuvent partager une même dépendance critique."
            }
          ],
          "mission_steps": [
            "Place les deux routeurs et les deux pare-feu.",
            "Raccorde les routeurs à la périphérie de sécurité.",
            "Relie les pare-feu au switch interne.",
            "Connecte le serveur puis identifie les contrôles HA à réaliser ensuite."
          ],
          "success_criteria": [
            "Les routeurs rejoignent la périphérie attendue.",
            "Les deux pare-feu sont représentés et raccordés.",
            "Le switch et le serveur sont connectés au LAN."
          ],
          "hints": [
            "Vérifie chaque routeur et pare-feu individuellement.",
            "Un doublon visuel n’active pas le mécanisme HA."
          ],
          "evaluation_scope": "Exercice local structurel ; aucune vérification serveur du parcours, ni test de heartbeat, de synchronisation ou de failover.",
          "debrief": "Il faut ensuite configurer le mode HA, les liens de contrôle, les routes de retour et des scénarios de panne pour vérifier le comportement réel."
        }
      };

      window.skilltree = function () {
        const app = baseFactory();
        app.topoPortCount = 8;
        app.topoSelectionTick = 0;
        app.examPaused = false;
        app.examInitialTime = 0;
        app._topologyEnhanceBound = false;

        Object.defineProperty(app, 'selectedTopoNode', {
          configurable: true, enumerable: true,
          get() {
            this.topoSelectionTick; // dépendance de réactivité Alpine
            const ed = this.topologyEditor;
            const rawId = ed && ed.node_selected && ed.node_selected.id ? String(ed.node_selected.id) : '';
            const id = rawId.replace(/^node-/, '');
            if (!id) return null;
            const n = this.topoData()[id];
            if (!n) return null;
            return { id, label: (n.data && n.data.label) || n.name || ('Équipement ' + id), inputs: Object.keys(n.inputs || {}).length, outputs: Object.keys(n.outputs || {}).length };
          }
        });
        app.challengeQuery = '';
        app.challengeLevelFilter = 'all';
        app.challengeStateFilter = 'all';
        Object.defineProperty(app, 'challengeNodes', {
          configurable: true, enumerable: true,
          get() {
            const fallbackLevels = {
              'challenge-osi': 'debutant',
              'challenge-small-business': 'debutant',
              'challenge-datacenter': 'intermediaire',
              'challenge-hybrid-cloud': 'intermediaire',
              'challenge-spine-leaf': 'expert',
              'challenge-backbone-segment-routing': 'expert',
              'challenge-fabric-aci-multi-tenant': 'expert',
              'challenge-vpn-inter-sites': 'intermediaire',
              'challenge-dual-isp-ha': 'expert',
              'challenge-it-ot-segmentation': 'expert'
            };
            const remote = (this.nodes || []).filter(n => n.type === 'architecture' || /^challenge-/.test(n.id))
              .map(n => {
                const lvl = this.levelOf(n) || fallbackLevels[n.id] || null;
                const meta = this.levelMeta(lvl) || {};
                return { ...n, builtin: false, level: lvl, levelLabel: (meta.icon || '📘') + ' ' + (meta.label || 'Défi guidé'), minutes: null };
              });
            return [...remote, ...BUILTIN_TOPO_CHALLENGES.map(c => ({ ...c, builtin: true }))];
          }
        });
        app.challengeState = function (c) {
          if (c.builtin) return (this.challengesDone || []).includes(c.id) ? 'validated' : 'available';
          return c.status || 'available';
        };
        app.challengeStatusLabel = function (c) {
          const state = this.challengeState(c);
          if (c.builtin) return state === 'validated'
            ? '✅ Réussi dans le navigateur · rejouable, sans validation du parcours'
            : '🧩 Entraînement libre · ne valide pas le cours du parcours';
          if (state === 'locked') return '🔒 Prérequis à valider avant de commencer';
          if (state === 'validated') return '✅ Validé dans le parcours · rejouable';
          if (state === 'in_progress') return '↻ Tentative enregistrée · à poursuivre';
          return c.description || 'Défi prêt à relever';
        };
        Object.defineProperty(app, 'filteredChallengeNodes', {
          configurable: true, enumerable: true,
          get() {
            const query = this.norm((this.challengeQuery || '').trim());
            return this.challengeNodes.filter(c => {
              const hay = this.norm([c.id, c.title, c.description, c.category, c.levelLabel].join(' '));
              if (query && !hay.includes(query)) return false;
              if (this.challengeLevelFilter !== 'all' && c.level !== this.challengeLevelFilter) return false;
              if (this.challengeStateFilter !== 'all' && this.challengeState(c) !== this.challengeStateFilter) return false;
              return true;
            });
          }
        });
        Object.defineProperty(app, 'challengeProgress', {
          configurable: true, enumerable: true,
          get() {
            const list = this.challengeNodes;
            return {
              total: list.length,
              completed: list.filter(c => this.challengeState(c) === 'validated').length,
              inProgress: list.filter(c => this.challengeState(c) === 'in_progress').length,
              locked: list.filter(c => this.challengeState(c) === 'locked').length
            };
          }
        });

        // Lecteur : les SVG conservent leurs couleurs sémantiques, tandis que les textes HTML suivent la palette.
        app.fixLessonContrast = function () {
          const root = document.querySelector('.lesson-prose');
          if (!root) return;
          // Les couleurs SVG ont été choisies pour les fonds internes de leurs boîtes : les recalculer en fonction
          // du fond HTML parent provoquait du texte sombre sur des nœuds sombres (et inversement).
          root.querySelectorAll('svg').forEach(svg => {
            svg.style.maxWidth = '100%';
            if (!svg.hasAttribute('preserveAspectRatio')) svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            if (!svg.hasAttribute('role')) svg.setAttribute('role', 'img');
          });
        };

        // Thèmes : rafraîchir l’interface du cours et les graphiques Chart.js.
        const originalSetTheme = app.setTheme;
        app.setTheme = function (id) {
          originalSetTheme.call(this, id);
          this.$nextTick(() => { this.fixLessonContrast(); if (this.tab === 'stats') this.renderSpiderChart(); });
        };

        // Radar : un seul graphique actif, axes lisibles et infobulle limitée au point survolé.
        app.renderSpiderChart = async function () {
          const canvas = document.getElementById('spiderChart');
          if (!canvas) return;
          if (!window.Chart) {
            try { await window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/chart.js', 'Chart'); }
            catch (error) { console.warn('Chart.js indisponible.', error); return; }
          }
          if (!canvas.isConnected || !window.Chart) return;
          const existing = window.Chart.getChart ? window.Chart.getChart(canvas) : window.spider;
          if (existing) existing.destroy();
          window.spider = null;
          if (!this.stats || !Array.isArray(this.stats.categories) || !this.radarHasPositiveRate()) return;

          const byName = new Map();
          this.stats.categories.forEach(c => {
            const name = String(c?.name || c?.category || '').trim();
            if (name && !byName.has(name)) byName.set(name, { ...c, name });
          });
          const categories = [...byName.values()].slice(0, 18);
          if (!categories.length) return;
          const styles = getComputedStyle(document.documentElement);
          const rgb = name => {
            const parts = styles.getPropertyValue(name).trim().split(/\s+/).map(Number);
            return parts.length === 3 && parts.every(Number.isFinite) ? parts.join(',') : '128,128,128';
          };
          const accent = `rgb(${rgb('--cyan-400')})`;
          const accentFill = `rgba(${rgb('--cyan-400')}, .18)`;
          const grid = `rgba(${rgb('--w')}, .13)`;
          const labelColor = `rgb(${rgb('--z-200')})`;
          const tickColor = `rgb(${rgb('--z-400')})`;
          const labels = categories.map(c => c.name);
          const values = categories.map(c => Math.max(0, Math.min(100, Number(c.success_rate) || 0)));
          this.radarSelectedDomain = null;
          window.spider = new Chart(canvas, {
            type: 'radar',
            data: { labels, datasets: [{
              label: 'Taux de réussite', data: values, fill: true,
              backgroundColor: accentFill, borderColor: accent,
              pointBackgroundColor: `rgb(${rgb('--emerald-400')})`,
              pointBorderColor: styles.getPropertyValue('--s1').trim() || '#ffffff',
              pointHoverBackgroundColor: accent, pointHoverBorderColor: `rgb(${rgb('--z-50')})`,
              borderWidth: 2.5,
              pointRadius: ctx => (Number(ctx.raw) > 0 ? 3.5 : 0),
              pointHitRadius: ctx => (Number(ctx.raw) > 0 ? 8 : 0),
              pointHoverRadius: 6
            }] },
            options: {
              responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
              interaction: { intersect: true, mode: 'nearest' },
              layout: { padding: { top: 22, right: 28, bottom: 22, left: 28 } },
              plugins: {
                legend: { display: false },
                tooltip: {
                  enabled: true, intersect: true, mode: 'nearest',
                  callbacks: {
                    title: items => items.length ? labels[items[0].dataIndex] : '',
                    label: ctx => `Réussite : ${Math.round(Number(ctx.parsed.r) || 0)}%`
                  }
                }
              },
              onClick: (event, elements) => {
                if (!elements || !elements.length) return;
                const index = elements[0].index;
                this.radarSelectedDomain = { name: labels[index], rate: Math.round(values[index]), category: categories[index] };
              },
              scales: { r: {
                min: 0, max: 100, beginAtZero: true,
                angleLines: { color: grid, lineWidth: 1 }, grid: { color: grid, circular: true },
                ticks: { display: true, stepSize: 20, color: tickColor, backdropColor: 'transparent', showLabelBackdrop: false, font: { size: 10 } },
                pointLabels: {
                  color: labelColor, padding: 11,
                  font: { size: 10, weight: '600' },
                  callback(label) {
                    const words = String(label).split(/\s+/);
                    const lines = []; let line = '';
                    words.forEach(word => {
                      const next = line ? `${line} ${word}` : word;
                      if (next.length > 19 && line) { lines.push(line); line = word; }
                      else line = next;
                    });
                    if (line) lines.push(line);
                    return lines;
                  }
                }
              } }
            }
          });
        };

        // Drawflow: dimensions d’icônes corrigées, ports réglables à l’ajout et sur un nœud existant.
        const originalInitTopology = app.initTopology.bind(app);
        app.initTopology = async function () {
          await originalInitTopology();
          const ed = this.topologyEditor;
          if (!ed || this._topologyEnhanceBound) return;
          this._topologyEnhanceBound = true;
          // Les imports de topologies peuvent déjà contenir des équipements avec beaucoup de ports.
          Object.entries(this.topoData()).forEach(([id, node]) => {
            const portCount = Math.max(Object.keys(node.inputs || {}).length, Object.keys(node.outputs || {}).length, 1);
            const element = document.getElementById(`node-${id}`);
            if (element) element.style.minHeight = `${Math.max(76, portCount * 22)}px`;
          });
          const changed = () => { this.topoSelectionTick++; };
          try { ed.on('nodeSelected', changed); ed.on('nodeUnselected', changed); } catch (_) { /* version Drawflow sans événement */ }
        };

        app.addDevice = function (type) {
          const ed = this.topologyEditor;
          if (!ed) { this.notify('Ouvre un défi pour initialiser le canevas.'); return; }
          const d = this.devices.find(x => x.type === type);
          if (!d) return;
          const ports = Math.min(48, Math.max(1, Math.round(Number(this.topoPortCount) || 1)));
          this.topoPortCount = ports;
          this.topoTypeCounter[type] = (this.topoTypeCounter[type] || 0) + 1;
          const label = `${d.label} ${this.topoTypeCounter[type]}`;
          const n = Object.keys(this.topoData()).length;
          const canvas = ed.precanvas;
          const columns = Math.max(1, Math.floor((canvas.clientWidth - 100) / 230));
          const x = 48 + (n % columns) * 225;
          const y = 36 + Math.floor(n / columns) * Math.max(180, ports * 23);
          const html = `<div class="topo-node"><span class="topo-icon">${d.icon}</span><span class="topo-copy"><span class="topo-label">${label}</span><span class="topo-sub">${d.hint} · ${ports} ports</span></span></div>`;
          ed.addNode(type, ports, ports, x, y, type, { label, portCount: ports }, html, false);
          const createdData = this.topoData();
          const createdId = Object.keys(createdData).sort((a, b) => Number(a) - Number(b)).pop();
          const createdElement = createdId ? document.getElementById(`node-${createdId}`) : null;
          if (createdElement) createdElement.style.minHeight = `${Math.max(76, ports * 22)}px`;
          this.refreshTopo();
          this.topoSelectionTick++;
        };

        app.applySelectedPorts = function () {
          const ed = this.topologyEditor;
          const selected = this.selectedTopoNode;
          if (!ed || !selected) { this.notify('Sélectionne d’abord un équipement sur le canevas.'); return; }
          if (typeof ed.addNodeInput !== 'function' || typeof ed.addNodeOutput !== 'function' || typeof ed.removeNodeInput !== 'function' || typeof ed.removeNodeOutput !== 'function') {
            this.notify('Cette version de Drawflow ne permet pas de modifier les ports existants. Recharge la bibliothèque Drawflow.'); return;
          }
          const count = Math.min(48, Math.max(1, Math.round(Number(this.topoPortCount) || 1)));
          this.topoPortCount = count;
          const data = this.topoData();
          const node = data[selected.id];
          if (!node) { this.notify('L’équipement sélectionné n’a pas été retrouvé.'); return; }
          const oldIn = Object.keys(node.inputs || {}).length;
          const oldOut = Object.keys(node.outputs || {}).length;
          let connectedToRemove = 0;
          for (let i = count + 1; i <= oldIn; i++) connectedToRemove += (node.inputs[`input_${i}`]?.connections || []).length;
          for (let i = count + 1; i <= oldOut; i++) connectedToRemove += (node.outputs[`output_${i}`]?.connections || []).length;
          if (connectedToRemove && !window.confirm(`Les ports supprimés portent ${connectedToRemove} connexion(s). Continuer et retirer ces ports ?`)) return;
          try {
            for (let i = oldIn; i > count; i--) ed.removeNodeInput(selected.id, `input_${i}`);
            let currentIn = Object.keys(this.topoData()[selected.id]?.inputs || {}).length;
            while (currentIn < count) { ed.addNodeInput(selected.id); currentIn = Object.keys(this.topoData()[selected.id]?.inputs || {}).length; }
            for (let i = oldOut; i > count; i--) ed.removeNodeOutput(selected.id, `output_${i}`);
            let currentOut = Object.keys(this.topoData()[selected.id]?.outputs || {}).length;
            while (currentOut < count) { ed.addNodeOutput(selected.id); currentOut = Object.keys(this.topoData()[selected.id]?.outputs || {}).length; }
            const refreshed = this.topoData()[selected.id];
            if (refreshed && refreshed.data) refreshed.data.portCount = count;
            const dom = document.getElementById(`node-${selected.id}`);
            if (dom) dom.style.minHeight = `${Math.max(76, count * 22)}px`;
            const sub = dom && dom.querySelector('.topo-sub');
            if (sub) sub.textContent = `${(refreshed && refreshed.name || 'Équipement').toUpperCase()} · ${count} entrées/sorties`;
            this.refreshTopo(); this.topoSelectionTick++;
            this.notify(`Ports mis à jour : ${count} entrée(s) et ${count} sortie(s).`);
          } catch (e) {
            console.error('Mise à jour des ports', e);
            this.notify('Impossible de modifier les ports : vérifie la version de Drawflow.');
          }
        };

        const originalStartChallenge = app.startChallenge.bind(app);
        const originalClearTopology = app.clearTopology.bind(app);
        app.clearTopology = function (force = false) {
          const count = Object.keys(this.topoData()).length;
          if (count && !force && !this._allowChallengeClear && !window.confirm(`Effacer cette topologie et ses ${count} équipement(s) ? Pense à sauvegarder avant de continuer.`)) return false;
          originalClearTopology();
          this.challengeResult = null;
          return true;
        };
        const readSavedState = (key, fallback) => {
          try {
            const raw = localStorage.getItem('st:' + key);
            return raw === null ? fallback : JSON.parse(raw);
          } catch (_) {
            return fallback;
          }
        };
        app.exportData = function () {
          const localData = {};
          const allowedPrefixes = ['skilltree-', 'st:'];
          try {
            for (let i = 0; i < localStorage.length; i += 1) {
              const key = localStorage.key(i);
              if (!key || !allowedPrefixes.some(prefix => key.startsWith(prefix))) continue;
              const raw = localStorage.getItem(key);
              try { localData[key] = JSON.parse(raw); } catch (_) { localData[key] = raw; }
            }
          } catch (_) { }
          const snapshot = {
            app: 'Skill-Tree',
            schema_version: 2,
            exported_at: new Date().toISOString(),
            profile: { name: app.userName, theme: app.activeThemeId || document.documentElement.dataset.theme || app.theme, current_level: app.userStats?.current_level ?? null },
            progress: { total: app.total, validated: app.validated, nodes: (app.nodes || []).map(n => ({ id: n.id, title: n.title, status: n.status, category: n.category, level: app.levelOf(n), module: app.moduleOf(n) })) },
            statistics: app.stats || null,
            exam_history: app.examHistory || readSavedState('exam-history', []),
            completed_challenges: app.challengesDone || readSavedState('challenges-done', []),
            completed_labs: app.labsDone || readSavedState('labs-done', []),
            diagnostics: app.diagDoneMap || readSavedState('diag-done', {}),
            preferences: {
              theme: app.activeThemeId || document.documentElement.dataset.theme || app.theme,
              sidebar_collapsed: !!app.sidebarCollapsed,
              focus_mode: !!app.focusMode,
              font_size: Number(app.fontSize) || 17,
              reading_width: app.readingWidth === 'wide' ? 'wide' : 'comfortable',
              compact_ui: !!app.compactUi,
              reduce_motion: !!app.reduceMotion
            },
            local_data: localData,
            topology_draft: readSavedState('topology-draft', null)
          };
          const name = `skilltree-sauvegarde-${new Date().toISOString().slice(0,10)}.json`;
          // Le factory d'interface est la source stable des données : ne pas dépendre
          // du this implicite d'une expression Alpine, qui peut être window.
          app.saveFile(name, new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json;charset=utf-8' }));
          app.notify('Sauvegarde JSON téléchargée. Conserve-la dans un emplacement sûr.');
          return snapshot;
        };
        app._allowChallengeClear = false;
        app.startChallenge = async function (id) {
          const local = BUILTIN_TOPO_CHALLENGES.find(c => c.id === id);
          const count = Object.keys(this.topoData()).length;
          if (count && !window.confirm(`Démarrer ce défi effacera les ${count} équipement(s) du défi précédent. Continuer ?`)) return;
          if (local) {
            this._allowChallengeClear = true;
            try { originalClearTopology(); }
            finally { this._allowChallengeClear = false; }
            this.challenge = { ...local, brief: BUILTIN_CHALLENGE_BRIEFS[id] || {}, expected: local.expected, minScore: local.minScore || 100, builtin: true };
            this.challengeResult = null;
            this.challengeLeft = local.timeLimit || 300;
            clearInterval(this.challengeTimer);
            this.challengeTimer = setInterval(() => {
              if (!this.challenge || this.challengeResult) { clearInterval(this.challengeTimer); return; }
              this.challengeLeft = Math.max(0, this.challengeLeft - 1);
              if (this.challengeLeft <= 0) this.checkChallenge(true);
            }, 1000);

            // Le canevas doit être visible avant d'initialiser Drawflow : sinon ses dimensions sont nulles.
            await this.$nextTick();
            await this.initTopology();
            this.notify(`Défi lancé : ${local.title}`);
            return;
          }
          // Le défi distant consomme la même API qu'avant ; on évite un deuxième prompt lors de son effacement.
          this._allowChallengeClear = true;
          try { await originalStartChallenge(id); }
          finally { this._allowChallengeClear = false; }
          if (this.challenge) {
            // Les défis serveur n'affichent le canevas qu'après le chargement de leur consigne.
            await this.$nextTick();
            await this.initTopology();
          }
        };

        // Les défis vérifient les comptes, la couverture de chaque équipement et les fabrics full-mesh.
        const originalCheckChallenge = app.checkChallenge.bind(app);
        app.checkChallenge = async function (timeout) {
          const ch = this.challenge;
          if (!ch || this.challengeSubmissionBusy) return;
          const graph = this.topoData();
          const architectBadgeWasUnlocked = this.badges.some(badge => badge.id === 'topo' && badge.ok);
          const seenBadgesBeforeRefresh = LS.get('badges-seen', null);

          // Défis du catalogue : le serveur calcule score, réussite et progression.
          // On n'envoie jamais le score annoncé par le navigateur.
          if (!ch.builtin) {
            clearInterval(this.challengeTimer);
            this.challengeSubmissionBusy = true;
            this.challengeResult = {
              score: null, passed: false, timeout: !!timeout, pending: true, error: '',
              missingNodes: [], extraNodes: [], missingLinks: [], extraLinks: [],
            };
            try {
              const response = await fetch(`/api/node/${encodeURIComponent(ch.id)}/challenge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topology: graph, timeout: !!timeout }),
              });
              const responseText = await response.text();
              let result;
              try { result = JSON.parse(responseText); }
              catch (_) { throw new Error(responseText || `Erreur ${response.status}`); }
              if (!response.ok) throw new Error(result.detail || responseText || `Erreur ${response.status}`);

              this.challengeResult = {
                score: Number(result.score) || 0,
                passed: !!result.passed,
                timeout: !!result.timeout,
                missingNodes: result.missing_nodes || [],
                extraNodes: result.extra_nodes || [],
                missingLinks: result.missing_links || [],
                extraLinks: result.extra_links || [],
                pending: false,
                error: '',
                validated: !!result.validated,
                attemptRecorded: !!result.attempt_recorded,
                xpGained: Number(result.xp_gained) || 0,
                coinsGained: Number(result.coins_gained) || 0,
                badgesUnlocked: result.badges_unlocked || [],
              };
              // Un défi serveur réussi doit aussi alimenter le compteur de défis local,
              // utilisé par le système de badges du dashboard.
              if (result.passed && !this.challengesDone.includes(ch.id)) {
                this.challengesDone = [...this.challengesDone, ch.id];
                LS.set('challenges-done', this.challengesDone);
              }
              await this.refreshAll();
              // refreshAll() peut déjà déclencher la célébration de badge via checkRewards().
              // N'afficher qu'une seule salve de confettis pour ce résultat.
              const refreshAlreadyCelebrated = Array.isArray(seenBadgesBeforeRefresh)
                && this.badges.some(badge => badge.ok && !seenBadgesBeforeRefresh.includes(badge.id));
              const architectBadgeSuffix = !architectBadgeWasUnlocked && result.passed
                ? ' 🧩 Badge « Architecte » débloqué.'
                : '';

              const rewardParts = [];
              if (Number(result.xp_gained) > 0) rewardParts.push(`+${Number(result.xp_gained)} XP`);
              if (Number(result.coins_gained) > 0) rewardParts.push(`+${Number(result.coins_gained)} pièces`);
              (Array.isArray(result.badges_unlocked) ? result.badges_unlocked : []).forEach(badge => {
                const label = typeof badge === 'string' ? badge : (badge.nom || badge.id || badge.name || 'Badge');
                rewardParts.push(`Badge : ${label}`);
              });
              const rewardSuffix = rewardParts.length ? ` Récompenses : ${rewardParts.join(' · ')}.` : '';

              if (result.passed && result.validated && result.attempt_recorded) {
                if (!refreshAlreadyCelebrated) this.celebrate();
                this.notify(`Défi validé et progression enregistrée : ${result.score} %.${architectBadgeSuffix}${rewardSuffix}`);
              } else if (result.passed && result.attempt_recorded) {
                this.notify(`Défi réussi (${result.score} %) : les autres exigences restent à valider.${architectBadgeSuffix}${rewardSuffix}`);
              } else if (!result.passed && result.attempt_recorded) {
                this.notify(`Tentative enregistrée : ${result.score} %. Corrige la topologie puis réessaie.`);
              } else if (result.passed && result.validated) {
                this.notify(`Ce défi est déjà validé dans ton parcours.${architectBadgeSuffix}`);
              }
            } catch (error) {
              this.challengeResult = {
                score: null, passed: false, timeout: !!timeout, pending: false,
                error: `La vérification serveur n'a pas pu être enregistrée : ${error.message}`,
                missingNodes: [], extraNodes: [], missingLinks: [], extraLinks: [],
              };
              this.notify('Défi non enregistré : vérifie la connexion puis réessaie.');
            } finally {
              this.challengeSubmissionBusy = false;
            }
            return;
          }

          // Défis intégrés : exercice local sans effet sur la progression serveur.
          const linked = (idA, nodeA, idB, nodeB) => {
            const fromA = Object.values(nodeA.outputs || {}).some(o => (o.connections || []).some(c => String(c.node) === String(idB)));
            const fromB = Object.values(nodeB.outputs || {}).some(o => (o.connections || []).some(c => String(c.node) === String(idA)));
            return fromA || fromB;
          };
          const missing = [];
          for (const rule of (ch.requireTypeCoverage || [])) {
            const required = Object.entries(graph).filter(([, n]) => n.name === rule.type);
            const peers = Object.entries(graph).filter(([, n]) => n.name === rule.peer);
            for (const [id, node] of required) {
              if (!peers.some(([peerId, peerNode]) => linked(id, node, peerId, peerNode))) {
                missing.push(`${(node.data && node.data.label) || rule.type} doit être relié à ${(rule.peer || 'un équipement requis')}`);
              }
            }
          }
          const rule = ch.requireCompleteBipartite;
          if (Array.isArray(rule) && rule.length === 2) {
            const [typeA, typeB] = rule;
            const aNodes = Object.entries(graph).filter(([, n]) => n.name === typeA);
            const bNodes = Object.entries(graph).filter(([, n]) => n.name === typeB);
            aNodes.forEach(([idA, nodeA]) => bNodes.forEach(([idB, nodeB]) => {
              if (!linked(idA, nodeA, idB, nodeB)) missing.push(`Lien Spine/Leaf manquant : ${(nodeA.data && nodeA.data.label) || typeA} ↔ ${(nodeB.data && nodeB.data.label) || typeB}`);
            }));
          }
          const priorMin = ch.minScore;
          if (missing.length) ch.minScore = 101;
          originalCheckChallenge(timeout);
          ch.minScore = priorMin;
          if (missing.length && this.challengeResult) {
            this.challengeResult.score = Math.min(Number(this.challengeResult.score) || 0, 95);
            this.challengeResult.passed = false;
            this.challengeResult.missingLinks = [...(this.challengeResult.missingLinks || []), ...missing];
          }
        };

        // Examen : pause explicite, minuteur figé, et durée mesurée hors périodes de pause.
        // Ne pas lier ces méthodes à l'objet brut créé avant Alpine : les mutations
        // doivent être appliquées au proxy réactif reçu via `this`, sinon l'API répond
        // mais x-if conserve le formulaire et n'affiche jamais les questions.
        const originalLaunchExam = app.launchExam;
        const originalResetExam = app.resetExam;
        app.launchExam = async function (cfg) {
          this.examPaused = false;
          this.examInitialTime = Number(cfg.minutes || 30) * 60;
          await originalLaunchExam.call(this, cfg);
          if (this.exam && !this.examResult) {
            this.examInitialTime = this.examLeft || this.examInitialTime;
            this.examPaused = false;
          }
        };
        app.startExamTimer = function () {
          this.stopExamTimer();
          if (!this.exam || this.examPaused || this.examResult) return;
          this.examTimerId = setInterval(() => {
            if (this.examPaused || !this.exam || this.examResult) return;
            this.examLeft = Math.max(0, this.examLeft - 1);
            if (this.examLeft <= 0) this.submitExam(true);
          }, 1000);
        };
        app.pauseExam = async function () {
          if (!this.exam || !this.exam.id || this.examResult || this.examPaused || this.examBusy) return;
          this.examBusy = true;
          try {
            const r = await fetch('/api/exam/pause', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: this.exam.id }) });
            const text = await r.text(); let data; try { data = JSON.parse(text); } catch (_) { data = { detail: text }; }
            if (!r.ok) throw new Error(data.detail || text || ('HTTP ' + r.status));
            this.examPaused = true;
            this.stopExamTimer();
            this.notify('Examen mis en pause. Le serveur prolonge aussi l’échéance.');
          } catch (error) {
            this.examErr = 'Impossible de mettre l’examen en pause : ' + (error.message || 'erreur réseau') + '. Réessaie.';
            this.notify(this.examErr);
          } finally { this.examBusy = false; }
        };
        app.resumeExam = async function () {
          if (!this.exam || !this.exam.id || this.examResult || !this.examPaused || this.examBusy) return;
          this.examBusy = true;
          try {
            const r = await fetch('/api/exam/resume', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: this.exam.id }) });
            const text = await r.text(); let data; try { data = JSON.parse(text); } catch (_) { data = { detail: text }; }
            if (!r.ok) throw new Error(data.detail || text || ('HTTP ' + r.status));
            this.examPaused = false;
            this.examErr = '';
            this.startExamTimer();
            this.notify('Examen repris.');
          } catch (error) {
            this.examErr = 'Impossible de reprendre l’examen : ' + (error.message || 'erreur réseau') + '. Réessaie.';
            this.notify(this.examErr);
          } finally { this.examBusy = false; }
        };
        // Cette surcharge est celle réellement appelée par l'interface : garder le même contrat strict
        // que submitExam(auto) plus haut évite qu'une ancienne implémentation accepte une note incomplète.
        app.submitExam = async function (auto) {
          if (!this.exam || !this.exam.id || this.examResult || this.examBusy) return;
          this.examBusy = true;
          this.stopExamTimer();
          this.examConfirm = false;
          this.examErr = '';
          const clientDuration = Math.max(0, (Number(this.examInitialTime) || Number(this.examLeft) || 0) - Number(this.examLeft || 0));
          let res;

          try {
            const response = await fetch('/api/exam/submit', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: this.exam.id, answers: this.examAnswers })
            });
            const raw = await response.text();
            try {
              res = raw ? JSON.parse(raw) : {};
            } catch (_) {
              throw new Error('Le serveur a renvoyé une réponse illisible.');
            }
            if (!response.ok) {
              throw new Error(res.detail || res.message || raw || ('HTTP ' + response.status));
            }
            if (
              !res
              || res.success !== true
              || typeof res.score !== 'number'
              || !Number.isFinite(res.score)
              || res.score < 0
              || res.score > 100
              || typeof res.passed !== 'boolean'
            ) {
              throw new Error('Le serveur n’a pas renvoyé un résultat de correction valide.');
            }
          } catch (error) {
            this.examErr = 'L’examen n’a pas été enregistré : '
              + (error.message || 'erreur réseau')
              + '. Tes réponses sont conservées à l’écran ; réessaie de terminer.';
            this.notify(this.examErr);
            this.examBusy = false;
            if (!auto && Number(this.examLeft) > 0 && !this.examPaused) this.startExamTimer();
            return;
          }

          const score = Math.round(res.score);
          const passed = res.passed;
          const correct = Number(res.correct) || 0;
          const total = Number(res.total) || this.exam.questions.length;
          const duration = res.duration !== undefined
            ? Math.max(0, Number(res.duration) || 0)
            : clientDuration;
          const timedOut = !!auto || !!res.time_expired;

          this.examErr = '';
          this.examResult = { ...res, score, passed, auto: timedOut, duration, correct, total };
          this.examHistory = [{
            id: Date.now(),
            date: new Date().toISOString(),
            module: this.exam.cfg.module,
            levels: this.exam.cfg.levels,
            score,
            passed,
            correct,
            total,
            duration
          }, ...this.examHistory].slice(0, 50);
          LS.set('exam-history', this.examHistory);
          this.examBusy = false;
          if (passed) this.celebrate();

          try {
            await this.refreshAll();
          } catch (_) {
            // La correction est déjà enregistrée ; une erreur secondaire de rafraîchissement ne l'annule pas.
            this.notify('Examen enregistré ; certaines données du tableau de bord n’ont pas pu être actualisées.');
          }
        };
        app.resetExam = function () {
          this.stopExamTimer(); this.exam = null; this.examResult = null; this.examConfirm = false;
          this.examPaused = false; this.examInitialTime = 0; this.examAnswers = []; this.examFlags = {}; this.examLeft = 0;
          originalResetExam.call(this);
        };

        // Labs : erreur réseau lisible au lieu d’une promesse rejetée silencieuse.
        app.runLabCommand = async function () {
          if (!this.labId || this.labBusy || !this.labCommand.trim()) return;
          const cmd = this.labCommand.trim(); this.labCommand = '';
          this.labOutput.push({ text: `$ ${cmd}` });
          this.labBusy = true;
          try {
            const r = await fetch('/api/lab/exec', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lab_id: this.labId, command: cmd }) });
            const text = await r.text();
            let data; try { data = JSON.parse(text); } catch (_) { data = { stdout: text }; }
            if (!r.ok) throw new Error(data.detail || data.stderr || text || `Erreur HTTP ${r.status}`);
            const output = data.stdout || data.stderr || data.output || '(commande exécutée sans sortie)';
            this.labOutput.push({ text: String(output) });
          } catch (e) { this.labOutput.push({ text: `ERREUR : ${e.message}` }); }
          finally { this.labBusy = false; this.$nextTick(() => { const el = this.$refs.labConsole; if (el) el.scrollTop = el.scrollHeight; }); }
        };

        // Sauvegarde locale d’abord, puis serveur ; un HTTP 500 ne sera plus présenté comme une réussite.
        app.saveTopology = async function () {
          if (!this.topologyEditor) { this.notify('Le canevas n’est pas initialisé.'); return; }
          const data = this.topologyEditor.export();
          try { localStorage.setItem('skilltree-topology-draft', JSON.stringify(data)); } catch (_) { }
          try { LS.set('topology-draft', data); } catch (_) { }
          try {
            const r = await fetch('/api/topology', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            this.notify('Topologie sauvegardée localement et sur le serveur.');
          } catch (e) { this.notify('Topologie gardée en local ; serveur indisponible ou refus de sauvegarde.'); }
        };
        app.loadTopology = async function () {
          if (!this.topologyEditor) return;
          try {
            const r = await fetch('/api/topology');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const d = await r.json();
            if (!d || !d.drawflow) throw new Error('format de topologie invalide');
            this.topologyEditor.import(d); this.refreshTopo(); this.topoSelectionTick++;
            this.notify('Topologie chargée depuis le serveur.');
          } catch (e) {
            const local = LS.get('topology-draft', null);
            if (local && local.drawflow) { try { this.topologyEditor.import(local); this.refreshTopo(); this.notify('Topologie locale chargée (serveur indisponible).'); return; } catch (_) { } }
            this.notify('Chargement impossible : ' + e.message);
          }
        };

        return app;
      };
    })();
  