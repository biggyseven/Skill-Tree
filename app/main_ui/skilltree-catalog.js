
    /* ====================== Skill Tree v3 : modules, recherche, examens, labs, récompenses ====================== */
    const PASS_SCORE = 80;

    const LEVELS = [
      { id: 'debutant', label: 'Débutant', icon: '🌱' },
      { id: 'intermediaire', label: 'Intermédiaire', icon: '🚀' },
      { id: 'expert', label: 'Expert', icon: '🔥' },
    ];

        const MODULES = [
      { id: 'admin-reseaux', label: 'Administration Réseaux', short: 'Réseaux', icon: '🌐', roadmap: {} },
      { id: 'admin-systeme', label: 'Administration Système', short: 'Système', icon: '🖥️', roadmap: {
        debutant: ['Introduction à Linux et au shell', 'Système de fichiers et permissions', 'Utilisateurs et groupes', 'Processus et services (systemd)', 'Paquets et mises à jour', 'Windows Server : bases et Active Directory'],
        intermediaire: ['Scripting Bash', 'Réseau sous Linux (netplan, nftables)', 'Stockage : LVM et RAID', 'Active Directory et GPO', 'SSH et sécurisation du serveur', 'Journaux et supervision', 'Sauvegarde et restauration'],
        expert: ['Haute disponibilité (Keepalived, Pacemaker)', 'Virtualisation (KVM, Proxmox, VMware)', 'Durcissement CIS et audit', 'Optimisation des performances', 'Automatisation avec Ansible', 'LDAP, Kerberos et PKI'] } },
      { id: 'devops', label: 'DevOps', short: 'DevOps', icon: '⚙️', roadmap: {
        debutant: ['Principes DevOps et cycle CI/CD', 'Git et gestion de versions', 'Linux pour DevOps', 'YAML, JSON et formats de configuration', 'Docker : images et conteneurs', 'Introduction au cloud'],
        intermediaire: ['Docker Compose et registres', 'CI/CD avec GitHub Actions et GitLab CI', 'Infrastructure as Code avec Terraform', 'Configuration avec Ansible', 'Observabilité : Prometheus et Grafana', 'Kubernetes : les bases'],
        expert: ['Kubernetes avancé : réseau et sécurité', 'GitOps avec ArgoCD', 'IaC à grande échelle', 'SRE : SLI, SLO et gestion des incidents', 'DevSecOps', 'Service mesh'] } },
      { id: 'cloud', label: 'Cloud Computing', short: 'Cloud', icon: '☁️', roadmap: {} },
      { id: 'data', label: 'Data & Bases de données', short: 'Data', icon: '📊', roadmap: {
        debutant: [
          'Concepts des bases de données relationnelles',
          'Requêtes SQL de base (SELECT, INSERT)',
          'Modélisation et diagrammes (MCD/MLD)',
          'Jointures et agrégations SQL',
          'Normalisation (1NF, 2NF, 3NF)',
          'Travaux pratiques (MySQL/PostgreSQL)'
        ],
        intermediaire: [
          'Rôle du DBA et architecture SGBD',
          'Sous-requêtes, CTE et procédures stockées',
          'Indexation et plans d’exécution',
          'Backup, PITR et restauration',
          'Introduction à MongoDB et Redis',
          'Entrepôt de données et ETL'
        ],
        expert: [
          'Architecture Hadoop et Spark',
          'Kafka et traitement en temps réel',
          'Data Lakes et Lakehouse',
          'Chiffrement, RGPD et contrôle d’accès',
          'Qualité, lignage et gouvernance',
          'Pipelines de données complexes'
        ]
      } },
      { id: 'aiops', label: 'AIOps & Intelligence Artificielle', short: 'AIOps', icon: '🤖', roadmap: {
        debutant: [
          "Qu'est-ce que l'AIOps ?",
          "IA, Machine Learning, Deep Learning",
          "Automatisation avec Python et Bash",
          "Automatiser via Slack/Teams (ChatOps)",
          "Intent-Based Networking (IBN)",
          "Outils (Ansible, Nornir)"
        ],
        intermediaire: [
          "ML pour la supervision réseau",
          "Détection d'anomalies (Z-score, clustering)",
          "Pipelines CI/CD pour le réseau",
          "Introduction aux LLMs pour l'administration réseau",
          "Streaming Telemetry (gNMI, gRPC)",
          "Jumeaux numériques réseau"
        ],
        expert: [
          "IA générative pour le diagnostic d'incidents",
          "Réseaux auto-cicatrisants",
          "Maintenance prédictive par IA",
          "Corrélation d'événements et RCA automatisée",
          "MLOps pour l'infrastructure",
          "Éthique de l'IA et biais algorithmiques"
        ]
      } },
      { id: 'gestion-projet-it', label: 'Gestion de Projet IT', short: 'Projet IT', icon: '📋', roadmap: {
        debutant: [
          "Introduction à la gestion de projet IT",
          "Phases d'un projet (Initiation, Planification)",
          "Rôles (Chef de projet, MOA, MOE)",
          "Outils de gestion (Jira, Trello, MS Project)",
          "Notions de Gantt et PERT",
          "Estimation des coûts et budget"
        ],
        intermediaire: [
          "Manifeste Agile et framework Scrum",
          "Rôle du Scrum Master et cérémonies",
          "Fondamentaux du PMI et de la certification PMP",
          "Méthodologie PRINCE2",
          "Identification et mitigation des risques",
          "Assurance qualité et tests de recette"
        ],
        expert: [
          "Direction de programme et portefeuille",
          "Conduite du changement IT",
          "Méthodologies hybrides Agile/Waterfall",
          "Leadership et gestion des parties prenantes",
          "Intégration ITSM et stratégie",
          "Audit de projet et capitalisation"
        ]
      } },
      { id: 'telecom', label: 'Opérateurs & Télécoms', short: 'Télécoms', icon: '📡', roadmap: {} },
      { id: 'voix', label: 'Voix & Collaboration', short: 'Voix', icon: '📞', roadmap: {} },
      { id: 'ot', label: 'Réseaux Industriels (OT)', short: 'OT', icon: '🏭', roadmap: {} },
      { id: 'cybersecurite', label: 'Cybersécurité', short: 'Cybersécurité', icon: '🛡️', roadmap: {
        debutant: ['Triade CIA', 'Panorama des menaces', 'Cryptographie', 'Hachage', 'Authentification', 'Endpoint Security', 'Wi-Fi', 'Introduction Pare-feu'],
        intermediaire: ['ACL Avancées', 'NAT & Périmètre', 'VPN & IPsec', 'Sécurité L2', 'Pare-feu NGFW', 'IDS/IPS', 'Segmentation', 'Sécurité Linux', 'Active Directory', 'SIEM', 'Services Réseau', 'Sécurité Web'],
        expert: ['Zero Trust', 'Cloud Security', 'K8s Security', 'DevSecOps', 'IAM Avancé', 'Pentest', 'Analyse Malwares', 'Forensique', 'DFIR', 'Gouvernance', 'Routing Secu', 'Vulnérabilités', 'Supply Chain', 'OT/ICS', 'Red Team', 'Threat Hunting'] } },
      { id: 'maintenance', label: 'Maintenance & Reporting', short: 'Maintenance', icon: '🔧', roadmap: {
        debutant: ['Fondamentaux', 'Outils diagnostic', 'Hardware', 'OS', 'Helpdesk', 'Communication', 'Documentation', 'Sécurité base'],
        intermediaire: ['Monitoring', 'Sauvegarde', 'Préventive', 'Gestion parc', 'Procédures', 'Escalade', 'ITIL', 'RCA', 'SLA', 'Reporting incident', 'Reporting mensuel', 'Automatisation'],
        expert: ['Prédictive', 'Audits', 'KPI', 'Capitalisation', 'Gestion crise', "Appels d'offres", 'Fournisseurs', 'Management', 'Budget', 'Transformation', 'Stratégie', 'RETEX']
      } },
      { id: 'supervision', label: 'Supervision & Monitoring', short: 'Supervision', icon: '📈', roadmap: {
        debutant: ['Fondamentaux monitoring', 'SNMP', 'Syslog', 'Surveillance ICMP', 'Métriques/Logs/Traces', 'Alerting'],
        intermediaire: ['Zabbix', 'Nagios/Centreon', 'Prometheus', 'Grafana', 'NetFlow/sFlow', 'Stack ELK', 'Loki', 'APM', 'Monitoring synthétique'],
        expert: ['SRE', 'SLI/SLO/SLA', 'Observabilité', 'Tracing distribué', 'OpenTelemetry', 'IAOps Monitoring', 'On-call & Runbooks', 'FinOps Monitoring', 'HA Monitoring']
      } },
    ];

    /* Niveau par défaut des cours qui n'ont pas "level" ni de mot-clé dans leur titre. À ajuster librement. */
    const LEVEL_MAP = {
      'intro-reseau': 'debutant', 'materiel-reseau': 'debutant', 'adressage-debutant': 'debutant', 'cabling': 'debutant', 'equipment': 'debutant',
      'osi': 'debutant', 'tcp-udp': 'debutant', 'ethernet': 'debutant', 'vlan': 'debutant', 'stp': 'debutant', 'wifi': 'debutant', 'ipv4': 'debutant',
      'arp': 'debutant', 'dhcp-dns': 'debutant', 'poe': 'debutant',
      'ipv6': 'intermediaire', 'nat': 'intermediaire', 'routing': 'intermediaire', 'ha': 'intermediaire', 'ospf': 'intermediaire', 'bgp': 'intermediaire',
      'dns-advanced': 'intermediaire', 'ntp-syslog': 'intermediaire', 'acl': 'intermediaire', 'firewall': 'intermediaire', 'vpn': 'intermediaire',
      'aaa': 'intermediaire', 'troubleshooting': 'intermediaire', 'cloud': 'intermediaire', 'automation': 'intermediaire', 'mpls': 'intermediaire',
      'qos': 'intermediaire', 'sdwan': 'intermediaire', 'sd-wan': 'intermediaire', 'ansible': 'intermediaire', 'etherchannel': 'intermediaire',
      'vtp': 'intermediaire', 'eigrp': 'intermediaire', 'pbr': 'intermediaire', 'ipsec': 'intermediaire', 'radius': 'intermediaire',
      'netmiko': 'intermediaire', 'restconf': 'intermediaire', 'aws-vpc': 'intermediaire', 'azure-vnet': 'intermediaire', 'wireguard': 'intermediaire',
      'pki': 'intermediaire', 'wireshark': 'intermediaire', 'terraform': 'intermediaire', 'multicast': 'intermediaire', 'vrf': 'intermediaire',
      'layer2-security': 'intermediaire', 'ids-ips': 'intermediaire', 'napalm': 'intermediaire', 'cicd-network': 'intermediaire',
      'itil-rca': 'intermediaire', 'mtu-pmtud': 'intermediaire',
      'ospf-advanced': 'expert', 'bgp-advanced': 'expert', 'qos-advanced': 'expert', 'vxlan': 'expert', 'spine-leaf': 'expert', 'sd-access': 'expert',
      'zero-trust': 'expert', 'zero-trust-architecture': 'expert', 'ddos-mitigation': 'expert', 'netconf-yang': 'expert', 'wireshark-advanced': 'expert',
      'segment-routing': 'expert', 'evpn': 'expert', 'cisco-aci': 'expert',
    };

    const NAV_ITEMS = [
      { id: 'tree', label: 'Tableau de bord', title: 'Tableau de bord', svg: '<rect x="3" y="3" width="7" height="7" rx="2"></rect><rect x="14" y="3" width="7" height="7" rx="2"></rect><rect x="3" y="14" width="7" height="7" rx="2"></rect><rect x="14" y="14" width="7" height="7" rx="2"></rect>' },
      { id: 'labs', label: 'Labs', title: 'Labs pratiques', svg: '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"></path><path d="M7.5 15h9"></path>' },
      { id: 'war', label: 'War Room', title: 'War Room — File d’attente NOC', svg: '<path d="M12 3a6 6 0 0 0-6 6v4l-2 3h16l-2-3V9a6 6 0 0 0-6-6Z"></path><path d="M9 20h6M12 1v2M3.5 5.5 5 7M20.5 5.5 19 7"></path>' },
      { id: 'exam', label: 'Examens', title: "Centre d'évaluation", svg: '<rect x="5" y="4" width="14" height="17" rx="2"></rect><path d="M9 4V3h6v1M9 9h6M9 13h6M9 17h3"></path>' },
      { id: 'challenges', label: 'Défis', title: "Défis d'architecture", svg: '<circle cx="12" cy="12" r="9"></circle><circle cx="12" cy="12" r="5"></circle><circle cx="12" cy="12" r="1"></circle>' },
      { id: 'diagnostic', label: 'Diagnostic', title: 'Diagnostic Interactif', svg: '<circle cx="5" cy="5" r="2"></circle><circle cx="19" cy="12" r="2"></circle><circle cx="5" cy="19" r="2"></circle><path d="M7 5h4a3 3 0 0 1 3 3v1a3 3 0 0 0 3 3M7 19h4a3 3 0 0 0 3-3v-1a3 3 0 0 1 3-3"></path>' },
      { id: 'memo', label: 'Révisions', title: 'Révisions espacées', svg: '<rect x="4" y="6" width="13" height="15" rx="2"></rect><path d="M8 3h9a3 3 0 0 1 3 3v11"></path>' },
      { id: 'stats', label: 'Radar', title: 'Radar de compétences', svg: '<path d="M4 19V9M10 19V5M16 19v-7M22 19V3"></path>' },
      { id: 'rewards', label: 'Récompenses', title: 'Récompenses et diplômes', svg: '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z"></path><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"></path>' },
    ];

    /* Scénarios de diagnostic intégrés (même format que ceux du serveur : steps + start). good = bonne décision. */
    const DIAG_BUILTIN = {
      'wifi-lent': { title: 'Wi-Fi lent à l’étage', level: 'debutant', domain: 'network', desc: 'Les utilisateurs d’un étage se plaignent d’un Wi-Fi lent depuis ce matin.', start: 'a',
        steps: {
          a: { competency: 'Mesure Wi-Fi', situation: 'Depuis ce matin, les utilisateurs du 2e étage trouvent le Wi-Fi très lent. Les autres étages vont bien. Que fais-tu en premier ?', choices: [
            { id: 'a1', label: 'Redémarrer tous les points d’accès de l’immeuble', next: 'bad1', good: false, feedback: 'Action lourde, non ciblée : tu coupes aussi les étages qui fonctionnent.' },
            { id: 'a2', label: 'Mesurer signal, canal et utilisation du canal sur les AP de l’étage', next: 'b', good: true, feedback: 'Bonne méthode : on mesure avant d’agir.' },
            { id: 'a3', label: 'Changer le mot de passe du Wi-Fi', next: 'bad1', good: false, feedback: 'Le mot de passe n’a aucun rapport avec la lenteur.' } ] },
          b: { competency: 'Capacité radio', situation: 'Mesures : RSSI correct (-62 dBm), mais utilisation du canal à 85 %. 60 clients sont connectés en 2,4 GHz, canal 6, canaux de 40 MHz.', choices: [
            { id: 'b1', label: 'Pousser les clients en 5 GHz, canaux de 20 MHz bien répartis', next: 'ok', good: true, feedback: 'Le canal est saturé : il faut répartir la charge.' },
            { id: 'b2', label: 'Augmenter la puissance d’émission des AP', next: 'bad2', good: false, feedback: 'Plus de puissance n’augmente pas la capacité, et brouille les AP voisins.' },
            { id: 'b3', label: 'Désactiver le chiffrement pour alléger le trafic', next: 'bad2', good: false, feedback: 'Dangereux et sans effet notable sur la saturation.' } ] },
          ok: { situation: 'Après la répartition en 5 GHz, l’utilisation du canal tombe à 35 % et les plaintes cessent.', conclusion: { outcome: 'success', title: 'Problème résolu', text: 'Cause : saturation du canal 2,4 GHz. Leçon : mesurer d’abord (signal, canal, utilisation), puis répartir les clients.' } },
          bad1: { competency: 'Démarche de dépannage', situation: 'Rien ne change : le problème revient quelques minutes plus tard.', choices: [ { id: 'r1', label: 'Reprendre avec une mesure du canal', next: 'b', good: true, feedback: 'Bon réflexe : retour à la mesure.' } ] },
          bad2: { competency: 'Conception radio', situation: 'Le Wi-Fi est encore plus instable : les AP voisins se perturbent mutuellement.', choices: [ { id: 'r2', label: 'Revenir à la répartition 5 GHz et canaux de 20 MHz', next: 'ok', good: true, feedback: 'Bonne correction.' } ] },
        } },
      'vlan-hote': { title: 'Hôte injoignable dans un VLAN', level: 'intermediaire', domain: 'network', desc: 'Un PC du VLAN 20 ne joint pas sa passerelle.', start: 'a',
        steps: {
          a: { competency: 'Configuration IP', situation: 'Un PC du VLAN 20 (10.20.0.0/24) ne ping pas sa passerelle 10.20.0.1. Premier réflexe ?', choices: [
            { id: 'a1', label: 'Vérifier l’adresse IP, le masque et la passerelle du PC', next: 'b', good: true, feedback: 'On commence toujours par la configuration locale.' },
            { id: 'a2', label: 'Redémarrer le switch', next: 'bad', good: false, feedback: 'Impact énorme sur tous les utilisateurs, sans diagnostic.' },
            { id: 'a3', label: 'Remplacer le câble sans rien vérifier', next: 'bad', good: false, feedback: 'Possible, mais ce n’est pas la première étape.' } ] },
          b: { competency: 'Segmentation VLAN', situation: 'Le PC a 10.20.0.50/24, passerelle 10.20.0.1 : correct. Le voyant du port est vert. Que vérifies-tu sur le switch ?', choices: [
            { id: 'b1', label: 'show vlan brief : le port est-il dans le bon VLAN ?', next: 'c', good: true, feedback: 'Excellent : un port d’accès dans le mauvais VLAN est une cause classique.' },
            { id: 'b2', label: 'show ip route', next: 'bad', good: false, feedback: 'Le switch d’accès ne route pas ici : ce n’est pas utile pour ce symptôme.' } ] },
          c: { competency: 'Segmentation VLAN', situation: 'Le port Fa0/7 apparaît dans le VLAN 1 (par défaut). Le trunk vers le routeur transporte bien le VLAN 20.', choices: [
            { id: 'c1', label: 'interface Fa0/7 : switchport mode access + switchport access vlan 20', next: 'ok', good: true, feedback: 'Correction ciblée.' },
            { id: 'c2', label: 'Ajouter le VLAN 1 au trunk', next: 'bad', good: false, feedback: 'Ça ne règle pas l’appartenance du port au bon VLAN.' } ] },
          ok: { situation: 'Le ping vers 10.20.0.1 répond.', conclusion: { outcome: 'success', title: 'Problème résolu', text: 'Cause : port d’accès resté dans le VLAN 1. Vérifie toujours le VLAN du port avec show vlan brief.' } },
          bad: { competency: 'Démarche de dépannage', situation: 'Aucune amélioration. Tu perds du temps.', choices: [ { id: 'r', label: 'Reprendre au diagnostic ciblé (IP puis VLAN du port)', next: 'a', good: true, feedback: 'Bon réflexe : on reprend la méthode.' } ] },
        } },
      'etherchannel-suspendu': { title: 'EtherChannel suspendu (s)', level: 'intermediaire', domain: 'network', desc: 'Un port est suspendu dans un Port-channel.', start: 'a',
        steps: {
          a: { competency: 'Lecture EtherChannel', situation: 'show etherchannel summary affiche Po1(SU) avec Gi0/1(P) mais Gi0/2(s). Que signifie (s) ?', choices: [
            { id: 'a1', label: 'Le port est suspendu : sa configuration n’est pas compatible avec le groupe', next: 'b', good: true, feedback: 'Exact : (s) signale une incompatibilité.' },
            { id: 'a2', label: 'Le câble est coupé', next: 'bad', good: false, feedback: 'Un câble coupé donnerait (D) down.' } ] },
          b: { competency: 'Cohérence de configuration', situation: 'Que compares-tu entre Gi0/1 et Gi0/2 ?', choices: [
            { id: 'b1', label: 'Vitesse, duplex, mode trunk/access, VLAN autorisés et natif', next: 'c', good: true, feedback: 'La liste correcte des paramètres à aligner.' },
            { id: 'b2', label: 'Seulement la description du port', next: 'bad', good: false, feedback: 'La description n’a aucune influence sur la formation du groupe.' } ] },
          c: { competency: 'Cohérence de configuration', situation: 'Gi0/2 autorise les VLAN 10,20,30 alors que Gi0/1 et Po1 autorisent 10,20. Que fais-tu ?', choices: [
            { id: 'c1', label: 'Aligner Gi0/2 sur le Port-channel : switchport trunk allowed vlan 10,20', next: 'ok', good: true, feedback: 'Bonne correction, faite sur l’interface membre.' },
            { id: 'c2', label: 'Supprimer le Port-channel et le recréer sans vérifier', next: 'bad', good: false, feedback: 'Inutile : l’incompatibilité resterait.' } ] },
          ok: { situation: 'Gi0/2 passe en (P) et le groupe affiche Po1(SU) avec deux ports regroupés.', conclusion: { outcome: 'success', title: 'Problème résolu', text: 'Cause : VLAN autorisés différents sur un port membre. Tous les ports membres doivent être identiques.' } },
          bad: { competency: 'Démarche de dépannage', situation: 'Le symptôme persiste.', choices: [ { id: 'r', label: 'Reprendre par la comparaison des paramètres des ports', next: 'b', good: true, feedback: 'Bon réflexe.' } ] },
        } },
      'linux-service-down': { title: 'Service web Linux indisponible', level: 'debutant', domain: 'linux', desc: 'Un service web retourne une erreur après une modification de configuration.', start: 'a',
        steps: {
          a: { competency: 'Services Linux', situation: 'Après un changement, le site interne renvoie une erreur 503. Quelle est la première vérification ?', choices: [
            { id: 'a-status', label: 'Consulter systemctl status nginx --no-pager et vérifier le service', next: 'b', good: true, feedback: 'Oui : vérifie le service et son état avant de redémarrer ou modifier quoi que ce soit.' },
            { id: 'a-reboot', label: 'Redémarrer immédiatement tout le serveur', next: 'bad', good: false, feedback: 'Un redémarrage peut interrompre d’autres services et effacer des indices utiles.' } ] },
          b: { competency: 'Journaux Linux', situation: 'Le service est en échec et signale une erreur de configuration. Quelle vérification apporte la preuve la plus utile ?', choices: [
            { id: 'b-journal', label: 'Lire journalctl -u nginx --since "10 minutes ago" et repérer l’erreur', next: 'c', good: true, feedback: 'Exact : les journaux du service donnent l’heure et le détail de l’échec.' },
            { id: 'b-delete', label: 'Supprimer les journaux puis relancer le service', next: 'bad', good: false, feedback: 'Ne détruis pas les traces : elles permettent d’identifier la cause et de vérifier la correction.' } ] },
          c: { competency: 'Configuration de service Linux', situation: 'Le journal indique une directive inconnue dans nginx.conf. Quelle action est la plus sûre ?', choices: [
            { id: 'c-test', label: 'Exécuter nginx -t, corriger uniquement la directive fautive, puis recharger le service', next: 'ok', good: true, feedback: 'Bonne méthode : valide la syntaxe avant le rechargement et limite le changement à la cause identifiée.' },
            { id: 'c-perms', label: 'Appliquer chmod -R 777 à /etc/nginx', next: 'bad', good: false, feedback: 'Cela élargit dangereusement les permissions et ne corrige pas une directive invalide.' } ] },
          ok: { situation: 'Le test de configuration réussit, le service est rechargé et le site répond de nouveau.', conclusion: { outcome: 'success', title: 'Service rétabli', text: 'La cause était une directive de configuration invalide. Vérifie l’état, lis les journaux, teste la configuration, corrige le minimum nécessaire puis contrôle le service.' } },
          bad: { competency: 'Démarche de dépannage', situation: 'Le problème persiste. Reprends une démarche progressive.', choices: [
            { id: 'retry', label: 'Revenir au statut du service puis suivre les journaux', next: 'a', good: true, feedback: 'Bon réflexe : repars des observations plutôt que d’empiler des changements.' } ] }
        } },
      'security-suspicious-login': { title: 'Connexion suspecte sur un serveur', level: 'debutant', domain: 'security', desc: 'Des échecs SSH sont suivis d’une connexion réussie depuis une adresse inconnue.', start: 'a',
        steps: {
          a: { competency: 'Réponse à incident', situation: 'Les journaux montrent plusieurs échecs SSH, puis une connexion réussie depuis une adresse inhabituelle. Que fais-tu d’abord ?', choices: [
            { id: 'a-preserve', label: 'Préserver les journaux, noter l’heure et l’adresse source, puis appliquer la procédure de signalement', next: 'b', good: true, feedback: 'Exact : préserve les preuves et traite l’événement avec une réponse proportionnée.' },
            { id: 'a-delete', label: 'Effacer les journaux afin de supprimer les traces de l’activité suspecte', next: 'bad', good: false, feedback: 'Ne supprime pas les éléments de preuve : cela empêche de comprendre et d’investiguer l’incident.' } ] },
          b: { competency: 'Analyse des journaux de sécurité', situation: 'La connexion inconnue a exécuté une commande avec sudo. Quelle vérification priorises-tu ?', choices: [
            { id: 'b-correlate', label: 'Corréler l’utilisateur, l’adresse source, l’heure, les sessions et les commandes privilégiées', next: 'c', good: true, feedback: 'Oui : la chronologie aide à estimer le périmètre et les actions réellement exécutées.' },
            { id: 'b-blind-block', label: 'Bloquer toutes les adresses IP externes sans examiner les éléments', next: 'bad', good: false, feedback: 'Une mesure trop large peut interrompre des services légitimes et ne clarifie pas le périmètre.' } ] },
          c: { competency: 'Contrôle d’accès et identité', situation: 'L’équipe confirme que le compte a été compromis. Quelle remédiation est la plus adaptée ?', choices: [
            { id: 'c-contain', label: 'Révoquer les sessions, réinitialiser le secret via la procédure approuvée, renforcer l’authentification et poursuivre la surveillance', next: 'ok', good: true, feedback: 'Correct : limite l’accès compromis, garde les traces et vérifie la persistance avant de clôturer l’incident.' },
            { id: 'c-audit', label: 'Désactiver l’audit SSH pour éviter les alertes', next: 'bad', good: false, feedback: 'Désactiver l’audit masque les événements et rend les prochaines tentatives plus difficiles à détecter.' } ] },
          ok: { situation: 'Les sessions suspectes sont révoquées, le compte est sécurisé et les journaux sont conservés pour l’investigation.', conclusion: { outcome: 'success', title: 'Incident contenu', text: 'La bonne réponse combine préservation des preuves, analyse de la chronologie, confinement du compte et surveillance. Une alerte doit être vérifiée sans effacer les traces ni désactiver les contrôles.' } },
          bad: { competency: 'Démarche de dépannage', situation: 'La réponse choisie laisse le périmètre incertain. Reprends l’analyse à partir des preuves.', choices: [
            { id: 'retry', label: 'Conserver les traces et vérifier la chronologie des connexions', next: 'a', good: true, feedback: 'Bon réflexe : établis les faits avant d’élargir les mesures de confinement.' } ] }
        } },
      'cloud-instance-unreachable': { title: 'Instance cloud inaccessible', level: 'intermediaire', domain: 'cloud', desc: 'Une instance fonctionne mais la connexion d’administration échoue après un changement réseau.', start: 'a',
        steps: {
          a: { competency: 'Diagnostic cloud réseau', situation: 'Une instance EC2 est en état running, mais SSH expire. Quelle vérification est la plus utile avant de modifier les règles ?', choices: [
            { id: 'a-scope', label: 'Contrôler les vérifications d’état, le groupe de sécurité, les ACL réseau et la table de routage', next: 'b', good: true, feedback: 'Exact : vérifie chaque couche et le chemin de retour avant de modifier l’architecture.' },
            { id: 'a-open', label: 'Autoriser immédiatement SSH depuis 0.0.0.0/0', next: 'bad', good: false, feedback: 'N’expose pas l’administration à toutes les adresses : identifie d’abord la source et le contrôle bloquant.' } ] },
          b: { competency: 'Règles de sécurité cloud', situation: 'Le groupe de sécurité autorise SSH uniquement depuis l’ancienne adresse IP du poste d’administration. Que fais-tu ?', choices: [
            { id: 'b-cidr', label: 'Mettre à jour la règle avec le CIDR d’administration approuvé et le port nécessaire uniquement', next: 'c', good: true, feedback: 'Bonne correction : conserve un accès source restreint et documenté.' },
            { id: 'b-wide', label: 'Autoriser tous les ports depuis Internet pour dépanner plus vite', next: 'bad', good: false, feedback: 'Une ouverture globale augmente fortement l’exposition sans isoler les règles réellement nécessaires.' } ] },
          c: { competency: 'Connectivité cloud privée', situation: 'La règle est correcte mais l’instance n’a pas d’adresse publique et se trouve dans un sous-réseau privé. Comment l’administrer ?', choices: [
            { id: 'c-private', label: 'Utiliser le bastion, le VPN ou le service d’accès géré approuvé et vérifier les routes associées', next: 'ok', good: true, feedback: 'Exact : un sous-réseau privé s’administre par le chemin prévu, sans exposition improvisée.' },
            { id: 'c-public', label: 'Attribuer une adresse publique sans vérifier la politique réseau', next: 'bad', good: false, feedback: 'N’ajoute pas d’exposition publique sans validation de l’architecture et de la politique de sécurité.' } ] },
          ok: { situation: 'Le chemin d’administration autorisé est restauré, tout en gardant les sources d’accès restreintes.', conclusion: { outcome: 'success', title: 'Accès cloud rétabli', text: 'Une connexion distante dépend du routage, des contrôles réseau et du chemin d’administration choisi. Vérifie ces éléments par couche et garde les accès d’administration au périmètre minimal nécessaire.' } },
          bad: { competency: 'Démarche de dépannage', situation: 'L’accès n’est pas encore rétabli. Reprends les vérifications par couche.', choices: [
            { id: 'retry', label: 'Comparer l’état de l’instance, les règles d’accès et le chemin réseau', next: 'a', good: true, feedback: 'Bon réflexe : identifie la couche en cause avant d’appliquer une correction ciblée.' } ] }
        } },
    };

    const DIAG_REMEDIATION = {
      "Triage initial": { competency:"Triage initial", prompt:"Le problème touche un seul poste. Quelle vérification limite le risque avant de modifier le réseau ?", hint:"Compare avec un poste fonctionnel et vérifie la configuration locale.", choices:[
        {label:"Comparer le lien, l'adresse IP, le masque et la passerelle",good:true,feedback:"Exact : délimite le problème et recueille des indices avant d'agir."},
        {label:"Redémarrer immédiatement le commutateur principal",good:false,feedback:"Cela peut interrompre des utilisateurs sans isoler la cause."}
      ]},
      "Connectivité locale et ARP": { competency:"Connectivité locale et ARP", prompt:"Sur un LAN IPv4, que permet principalement ARP ?", hint:"ARP intervient entre l'adresse IP d'un voisin et son adresse de couche 2.", choices:[
        {label:"Associer l'adresse IPv4 voisine à une adresse MAC",good:true,feedback:"Correct : cette association permet de construire la trame Ethernet."},
        {label:"Traduire un nom de domaine en adresse IP",good:false,feedback:"C'est le rôle de la résolution DNS."}
      ]},
      "Lecture de la configuration IP": { competency:"Lecture de la configuration IP", prompt:"Quelle commande Linux affiche les adresses IP des interfaces ?", hint:"Utilise la commande ip avec le sous-commande addr.", choices:[
        {label:"ip addr",good:true,feedback:"Correct : ip addr (ou ip a) affiche la configuration IP des interfaces."},
        {label:"nslookup",good:false,feedback:"nslookup interroge le DNS, pas la configuration des interfaces."}
      ]},
      "Configuration IP": { competency:"Configuration IP", prompt:"Un poste ne joint pas sa passerelle. Que vérifies-tu d'abord localement ?", hint:"Le masque définit le sous-réseau auquel l'adresse appartient.", choices:[
        {label:"Adresse IP, masque/préfixe et passerelle",good:true,feedback:"Exact : une erreur sur l'une de ces valeurs peut couper la connectivité."},
        {label:"Le cache du navigateur uniquement",good:false,feedback:"Le navigateur n'explique pas l'échec vers une passerelle IP."}
      ]},
      "DHCP et adressage": { competency:"DHCP et adressage", prompt:"Que suggère généralement une adresse IPv4 169.254.x.x dans ce scénario ?", hint:"C'est une plage link-local que le système peut s'attribuer en l'absence de bail DHCP utilisable.", choices:[
        {label:"Le poste n'a probablement pas obtenu de bail DHCP valide",good:true,feedback:"Oui : vérifie DHCP, le VLAN et le relais éventuel."},
        {label:"Le serveur DNS est forcément en panne",good:false,feedback:"Une adresse link-local pointe d'abord vers un problème d'adressage."}
      ]},
      "Rétablissement contrôlé": { competency:"Rétablissement contrôlé", prompt:"Avant d'utiliser temporairement une IP statique, quelle précaution est indispensable ?", hint:"Il faut éviter tout conflit d'adresse et respecter les procédures du réseau.", choices:[
        {label:"Vérifier l'autorisation, l'adresse libre, le masque et la passerelle",good:true,feedback:"Correct : évite les doublons et rétablis DHCP après la réparation."},
        {label:"Choisir une adresse au hasard dans le sous-réseau",good:false,feedback:"Une adresse déjà utilisée peut aggraver l'incident."}
      ]},
      "Mesure Wi-Fi": { competency:"Mesure Wi-Fi", prompt:"Le Wi-Fi est lent sur un étage. Que mesures-tu d'abord ?", hint:"La qualité du signal et l'occupation du canal sont deux indicateurs différents.", choices:[
        {label:"RSSI/SNR, occupation des canaux et répartition des clients",good:true,feedback:"Bonne démarche : distingue couverture faible et congestion radio."},
        {label:"Redémarrer tous les points d'accès sans mesurer",good:false,feedback:"Tu interromps potentiellement les zones saines sans trouver la cause."}
      ]},
      "Capacité radio": { competency:"Capacité radio", prompt:"Le signal est bon, mais l'occupation du canal atteint 85 %. Quelle hypothèse est prioritaire ?", hint:"Un signal fort ne signifie pas que le temps d'antenne est libre.", choices:[
        {label:"Congestion ou contention du canal",good:true,feedback:"Oui : examine la densité, les largeurs de canal et la répartition des fréquences."},
        {label:"Désactiver le chiffrement",good:false,feedback:"Désactiver la sécurité ne corrige pas la contention radio."}
      ]},
      "Démarche de dépannage": { competency:"Démarche de dépannage", prompt:"Quelle séquence limite le mieux les interventions inutiles ?", hint:"Recueille des faits avant de changer la configuration.", choices:[
        {label:"Définir le périmètre, mesurer, formuler une hypothèse, tester puis corriger",good:true,feedback:"Exact : la méthode est vérifiable et limite les effets de bord."},
        {label:"Modifier plusieurs paramètres à la fois",good:false,feedback:"Tu ne sauras pas quelle modification a été utile et risques une autre panne."}
      ]},
      "Conception radio": { competency:"Conception radio", prompt:"Dans un Wi-Fi dense, quel réglage peut améliorer la réutilisation des canaux ?", hint:"Une largeur plus importante consomme davantage de spectre contigu.", choices:[
        {label:"Planifier les canaux et choisir une largeur adaptée à la densité",good:true,feedback:"Oui : adapte canaux et largeurs aux mesures du site."},
        {label:"Augmenter systématiquement la puissance",good:false,feedback:"Une puissance excessive peut accroître les interférences."}
      ]},
      "Segmentation VLAN": { competency:"Segmentation VLAN", prompt:"Le poste attend le VLAN 20, mais son port d'accès est dans le VLAN 1. Quelle correction cible la cause ?", hint:"Le VLAN du port d'accès doit correspondre au segment attendu.", choices:[
        {label:"Affecter le port au VLAN 20 après vérification",good:true,feedback:"Exact : vérifie aussi l'existence du VLAN et les trunks nécessaires."},
        {label:"Ajouter le VLAN 1 partout sans vérifier le port",good:false,feedback:"Cela ne corrige pas l'appartenance du port d'accès."}
      ]},
      "Lecture EtherChannel": { competency:"Lecture EtherChannel", prompt:"Un port EtherChannel est marqué « (s) ». Quelle est l'interprétation probable ?", hint:"Le « s » signale un port suspendu.", choices:[
        {label:"Le port est suspendu, probablement pour incompatibilité de configuration",good:true,feedback:"Correct : compare paramètres du membre et du Port-channel."},
        {label:"Le port est élu racine STP",good:false,feedback:"L'état « (s) » n'indique pas une élection STP."}
      ]},
      "Cohérence de configuration": { competency:"Cohérence de configuration", prompt:"Deux membres d'un EtherChannel autorisent des VLAN différents. Quelle démarche est la plus sûre ?", hint:"Compare les paramètres effectifs avant de modifier la configuration.", choices:[
        {label:"Aligner la configuration divergente puis vérifier l'état du groupe",good:true,feedback:"Correct : corrige la différence ciblée puis vérifie que le port rejoint le groupe."},
        {label:"Supprimer et recréer le groupe sans comparaison",good:false,feedback:"La cause peut persister et l'opération peut interrompre le trafic."}
      ]},
      "Services Linux": { competency:"Services Linux", prompt:"Un service Linux vient d’échouer. Quelle commande indique son état ?", hint:"Commence par l’unité systemd avant de redémarrer toute la machine.", choices:[
        {label:"systemctl status nginx --no-pager",good:true,feedback:"Correct : vérifie l’état du service et le message de la dernière transition."},
        {label:"chmod -R 777 /etc/nginx",good:false,feedback:"Élargir les permissions ne donne pas le statut du service et peut compromettre sa sécurité."}
      ]},
      "Journaux Linux": { competency:"Journaux Linux", prompt:"Où rechercher les messages récents d’un service systemd précis ?", hint:"Utilise le journal système et filtre par unité.", choices:[
        {label:"journalctl -u nginx --since \"10 minutes ago\"",good:true,feedback:"Exact : le filtre par unité et par période aide à relier l’erreur au changement."},
        {label:"Supprimer /var/log et redémarrer",good:false,feedback:"Cela détruit les indices au lieu de les analyser."}
      ]},
      "Configuration de service Linux": { competency:"Configuration de service Linux", prompt:"Avant de recharger Nginx après une correction, que faut-il faire ?", hint:"Nginx dispose d’un contrôle de syntaxe dédié.", choices:[
        {label:"nginx -t, corriger l’erreur signalée, puis recharger le service",good:true,feedback:"Oui : valide d’abord la configuration puis applique une correction limitée."},
        {label:"Appliquer des permissions 777 à tout /etc/nginx",good:false,feedback:"Cela ne corrige pas une directive invalide et ouvre inutilement les fichiers."}
      ]},
      "Réponse à incident": { competency:"Réponse à incident", prompt:"Une connexion suspecte est détectée. Quel premier geste protège l’investigation ?", hint:"Conserve les traces et établis une chronologie avant de modifier le système.", choices:[
        {label:"Préserver les journaux, noter les indicateurs et suivre la procédure de signalement",good:true,feedback:"Exact : la conservation des preuves aide à qualifier et à traiter l’incident."},
        {label:"Effacer les traces et désactiver l’audit",good:false,feedback:"Cela empêche d’investiguer l’incident et réduit la visibilité sur de nouvelles activités."}
      ]},
      "Analyse des journaux de sécurité": { competency:"Analyse des journaux de sécurité", prompt:"Quels éléments aident le plus à qualifier une connexion suspecte ?", hint:"Cherche une chronologie entre l’utilisateur, la source et les actions exécutées.", choices:[
        {label:"Corréler utilisateur, adresse source, heure, sessions et actions privilégiées",good:true,feedback:"Exact : la corrélation aide à estimer le périmètre réel de l’activité."},
        {label:"Se baser uniquement sur le nombre d’échecs sans examiner la connexion réussie",good:false,feedback:"La connexion réussie et les actions associées sont essentielles à l’évaluation."}
      ]},
      "Contrôle d’accès et identité": { competency:"Contrôle d’accès et identité", prompt:"Un compte est confirmé compromis. Quelle mesure est la plus adaptée ?", hint:"Révoque l’accès compromis, sécurise le compte et conserve les traces.", choices:[
        {label:"Révoquer les sessions, changer les secrets via la procédure approuvée et renforcer l’authentification",good:true,feedback:"Correct : combine confinement du compte et protection durable sans supprimer les preuves."},
        {label:"Désactiver les journaux d’authentification pour éviter les alertes",good:false,feedback:"Cela masque l’activité au lieu de sécuriser le compte."}
      ]},
      "Diagnostic cloud réseau": { competency:"Diagnostic cloud réseau", prompt:"Une instance cloud est en marche mais inaccessible. Que vérifies-tu avant de changer les règles ?", hint:"L’accès dépend des vérifications d’état, du filtrage et du chemin réseau.", choices:[
        {label:"État de l’instance, groupes de sécurité, ACL réseau et tables de routage",good:true,feedback:"Exact : vérifie le chemin et les contrôles par couche."},
        {label:"Autoriser tous les ports depuis toutes les adresses",good:false,feedback:"Une ouverture globale ne localise pas la cause et expose l’instance."}
      ]},
      "Règles de sécurité cloud": { competency:"Règles de sécurité cloud", prompt:"Un groupe de sécurité n’autorise plus l’adresse IP actuelle de l’administrateur. Quelle correction convient ?", hint:"Garde le port et les sources à la portée minimale nécessaire.", choices:[
        {label:"Mettre à jour la source avec le CIDR d’administration approuvé",good:true,feedback:"Correct : rétablis le besoin d’accès sans exposer le service à Internet entier."},
        {label:"Autoriser 0.0.0.0/0 sur tous les ports",good:false,feedback:"Cette règle est trop large et augmente fortement la surface d’exposition."}
      ]},
      "Connectivité cloud privée": { competency:"Connectivité cloud privée", prompt:"Une instance privée doit être administrée. Quel accès privilégier ?", hint:"Utilise le chemin d’administration défini par l’architecture et la politique cloud.", choices:[
        {label:"VPN, bastion ou accès géré approuvé, avec routes vérifiées",good:true,feedback:"Oui : un chemin privé approuvé évite d’exposer directement l’instance."},
        {label:"Ajouter une adresse publique sans vérification de politique",good:false,feedback:"L’exposition publique doit respecter l’architecture et la politique de sécurité."}
      ]},
    };
    const DIAG_LEARNING_PATHS = {
      "Triage initial": {courseIds:["intro-reseau-debutant","materiel-reseau-debutant"],labIds:[]},
      "Connectivité locale et ARP": {courseIds:["arp-debutant","ethernet-debutant"],labIds:["lab_netns"]},
      "Lecture de la configuration IP": {courseIds:["ipv4-debutant","adressage-debutant"],labIds:["lab_netns"]},
      "Configuration IP": {courseIds:["ipv4-debutant","adressage-debutant"],labIds:["lab_netns"]},
      "DHCP et adressage": {courseIds:["dhcp-dns-debutant","adressage-debutant"],labIds:[]},
      "Rétablissement contrôlé": {courseIds:["adressage-intermediaire","ipv4-debutant"],labIds:["lab_netns"]},
      "Mesure Wi-Fi": {courseIds:["wifi-debutant"],labIds:[]},
      "Capacité radio": {courseIds:["wifi-intermediaire","wifi-debutant"],labIds:[]},
      "Démarche de dépannage": {courseIds:["osi-debutant","osi-intermediaire"],labIds:["lab_tshoot_route"]},
      "Conception radio": {courseIds:["wifi-intermediaire","wifi-expert"],labIds:[]},
      "Segmentation VLAN": {courseIds:["vlan-debutant","vlan-intermediaire"],labIds:["lab_troubleshoot_vlan"]},
      "Lecture EtherChannel": {courseIds:["etherchannel-debutant","etherchannel-intermediaire"],labIds:[]},
      "Cohérence de configuration": {courseIds:["etherchannel-intermediaire","ethernet-intermediaire"],labIds:[]},
      "Services Linux": {courseIds:["linux-debutant","process-debutant","linux-intermediaire"],labIds:[]},
      "Journaux Linux": {courseIds:["monitoring-debutant","monitoring-intermediaire","linux-intermediaire","linux-debutant"],labIds:[]},
      "Configuration de service Linux": {courseIds:["linux-debutant","process-debutant","linux-intermediaire"],labIds:[]},
      "Réponse à incident": {courseIds:["firewall-debutant","acl-debutant","routing-debutant","ipv4-debutant"],labIds:[]},
      "Analyse des journaux de sécurité": {courseIds:["firewall-debutant","acl-debutant","routing-debutant","ipv4-debutant","linux-debutant"],labIds:[]},
      "Contrôle d’accès et identité": {courseIds:["aaa-debutant","acl-debutant","routing-debutant","ipv4-debutant"],labIds:[]},
      "Diagnostic cloud réseau": {courseIds:["cloud-debutant","aws-vpc-debutant","aws-vpc-intermediaire"],labIds:[]},
      "Règles de sécurité cloud": {courseIds:["cloud-debutant","aws-vpc-debutant","azure-vnet-debutant"],labIds:[]},
      "Connectivité cloud privée": {courseIds:["cloud-debutant","aws-vpc-debutant","aws-vpc-intermediaire"],labIds:[]}
    };

    function skilltreeExt() {
      const LS = {
        get(k, d) { try { const v = localStorage.getItem('st:' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
        set(k, v) { try { localStorage.setItem('st:' + k, JSON.stringify(v)); } catch (e) { } },
      };
      const H = { 'Content-Type': 'application/json' };
      const INTERVALS = [0, 1, 2, 4, 8, 16];

      return {
        // ---------- état commun ----------
        navItems: NAV_ITEMS, modules: MODULES, levels: LEVELS,
        warTickets: [], warFilter: 'all', warTab: 'inbox', warLoading: false, warError: '', warNotice: '', _warTicketTimer: null,
        warOpenTicketCount: 0, _warOpenCountTimer: null,
        warBadges: [], warBadgesLoading: false, warBadgesError: '',
        warWeeklyReport: null, warWeeklyLoading: false, warWeeklyError: '',
        warStressBusy: false, warStressMission: null, warStressNotice: '', _warStressPollTimer: null,
        warStats: { mttr_minutes: 0, sla_compliance_pct: 0, total_resolved: 0, total_failed: 0, incidents_today: 0, recent_resolved: [] }, warLiveLoading: false, warStatsError: '',
        warArchive: [], warArchiveLoading: false, warArchiveError: '', warReplayBusy: null,
        warScenarios: [], warScenariosLoading: false, warScenarioError: '', warScenarioNotice: '', warScenarioFilter: 'all', warScenarioSearch: '',
        warRandomBusy: false, warScenarioOptions: null, createScenarioOpen: false, createScenarioBusy: false,
        createScenarioError: '', createScenarioSuccess: '', createScenarioSavedId: '',
        createScenario: { name: '', type: 'incident', severity: 'normal', topology: 'lan_simple', fault_id: 'port_shutdown', target_device: 'SW1', target_port: 'Fa0/7', sla_minutes: 30 },
        sidebarContextMenu: { open: false, x: 8, y: 8, id: '', label: '' },
        moduleFilter: 'all',
        submoduleFilter: null,
        moduleNextCourseId: null,
        moduleOverrides: LS.get('module-overrides', {}), levelOverrides: LS.get('level-overrides', {}),
        toast: { show: false, text: '' },

        norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); },
        notify(text) { this.toast = { show: true, text }; clearTimeout(this._toastT); this._toastT = setTimeout(() => { this.toast.show = false; }, 4200); },
        celebrate() {
          window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js', 'confetti')
            .then(() => { if (typeof window.confetti === 'function') window.confetti({ particleCount: 140, spread: 75, origin: { y: 0.65 } }); })
            .catch(error => console.debug('Confettis indisponibles.', error));
        },
        saveFile(name, blob) {
          if (!(blob instanceof Blob)) throw new TypeError('Le fichier à télécharger doit être un Blob.');
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = String(name || 'skilltree-export');
          a.setAttribute('aria-hidden', 'true');
          a.tabIndex = -1;
          // L’ancre doit rester activable : hidden/display:none peut faire échouer
          // certains chemins de téléchargement du navigateur.
          Object.assign(a.style, {
            position: 'fixed',
            left: '-10000px',
            top: '0',
            width: '1px',
            height: '1px',
            opacity: '0',
            pointerEvents: 'none'
          });
          document.body.appendChild(a);
          a.click();
          // Laisser le navigateur amorcer le téléchargement avant de retirer le lien.
          window.setTimeout(() => {
            a.remove();
            URL.revokeObjectURL(url);
          }, 1200);
        },
        fmtClock(sec) { const s = Math.max(0, sec | 0); return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0'); },

        // ---------- modules et niveaux ----------
        newTabUrl(kind, id) {
          const paramsByKind = { tab: 'openTab', module: 'openModule', course: 'openCourse' };
          const param = paramsByKind[kind];
          if (!param || id === null || id === undefined || String(id) === '') return '/';
          const params = new URLSearchParams();
          params.set(param, String(id));
          return '/?' + params.toString();
        },
        openSidebarContextMenu(event, id, label) {
          const menuWidth = 250;
          const menuHeight = 52;
          const maxX = Math.max(8, window.innerWidth - menuWidth - 8);
          const maxY = Math.max(8, window.innerHeight - menuHeight - 8);
          const clientX = Number(event?.clientX) || 8;
          const clientY = Number(event?.clientY) || 8;
          this.sidebarContextMenu = {
            open: true,
            x: Math.max(8, Math.min(clientX, maxX)),
            y: Math.max(8, Math.min(clientY, maxY)),
            id: String(id || ''),
            label: String(label || 'Navigation')
          };
        },
        closeSidebarContextMenu() {
          if (this.sidebarContextMenu?.open) {
            this.sidebarContextMenu = { ...this.sidebarContextMenu, open: false };
          }
        },
        closeSidebarContextMenuOnOutside(event) {
          if (!this.sidebarContextMenu?.open) return;
          if (event?.target?.closest?.('[data-sidebar-context-menu]')) return;
          this.closeSidebarContextMenu();
        },
        moduleMeta(id) { return this.modules.find(m => m.id === id) || { id: 'all', label: 'Tous les modules', short: 'Tous', icon: '🧭', roadmap: {} }; },
        levelMeta(id) { return this.levels.find(l => l.id === id) || null; },
                moduleOf(n) {
          const id = String(n.id || '');
          if (id.startsWith('maint-')) return 'maintenance';

          // Les modules nouvellement ajoutés au catalogue sont canoniques :
          // ne pas laisser d'anciennes affectations locales les masquer.
          const raw = String(n.module || '').trim();
          if (id.startsWith('sup-') || raw === 'Supervision & Monitoring') return 'supervision';
          if (raw === 'AIOps & Intelligence Artificielle' || raw.toLowerCase().startsWith('aiops')) return 'aiops';
          if (raw.toLowerCase() === 'gestion de projet it' || id.startsWith('proj-')) return 'gestion-projet-it';

          // Les affectations manuelles restent disponibles pour les autres cours.
          const o = this.moduleOverrides[n.id]; if (o) return o;

          // 1. D'abord, on vérifie le champ "module" exact.
          if (raw === 'Data & Bases de données' || raw.toLowerCase().startsWith('data')) return 'data';
          if (raw === 'Cybersécurité') return 'cybersecurite';
          
          if (raw === 'Réseaux Industriels (OT)') return 'ot';
          if (raw === 'Cloud Computing') return 'cloud';
          if (raw === 'Opérateurs & Télécoms') return 'telecom';
          if (raw === 'Voix & Collaboration') return 'voix';
          if (raw === 'Administration Système') return 'admin-systeme';
          if (raw === 'DevOps') return 'devops';
          if (raw === 'Administration Réseaux') return 'admin-reseaux';

          // 2. Ensuite, on vérifie l'ID du cours (au cas où le champ module serait absent).
          if (id.startsWith('data-')) return 'data';
          if (id.startsWith('aiops-')) return 'aiops';
          if (id.startsWith('proj-')) return 'gestion-projet-it';
          if (id.startsWith('secu-')) return 'cybersecurite';
          if (id.startsWith('ot-')) return 'ot';
          if (id.startsWith('cloud-aws') || id.startsWith('cloud-azure') || id.startsWith('cloud-gcp') || id.startsWith('cloud-serverless')) return 'cloud';
          if (id.startsWith('telecom-')) return 'telecom';
          if (id.startsWith('voice-')) return 'voix';
          
          // 3. Pour l'Admin Sys et le DevOps, on garde nos anciennes règles basées sur l'ID.
          if (/^(sys|sysadmin|linux|win|storage|users|process|packages|scripting|reseau-linux|web-server|db|ha-sys|virt|monitoring|backup)-/.test(id)) return 'admin-systeme';
          if (/^(devops|k8s|docker|git|iac|observability|devsecops|mesh)-/.test(id)) return 'devops';

          // 4. On garde les anciens cours AWS/Azure dans "Administration Réseaux" (car ce sont des cours de réseau cloud).
          if (id.startsWith('aws-vpc') || id.startsWith('azure-vnet')) return 'admin-reseaux';

          // 5. Par défaut, tout le reste est du Réseau.
          return 'admin-reseaux';
        },
        levelOf(n) {
          const o = this.levelOverrides[n.id]; if (o) return o;
          const probe = this.norm(n.level) || this.norm(n.id + ' ' + n.title);
          if (/(^|[^a-z])expert/.test(probe)) return 'expert';
          if (/intermediaire|intermediate/.test(probe)) return 'intermediaire';
          if (/debutant|beginner/.test(probe)) return 'debutant';
          return LEVEL_MAP[n.id] || null;
        },
        levelLabel(n) { const l = this.levelMeta(this.levelOf(n)); return l ? l.icon + ' ' + l.label : 'Non classé'; },
        nodesIn(mod, lvl) { return this.nodes.filter(n => (!mod || mod === 'all' || this.moduleOf(n) === mod) && (!lvl || this.levelOf(n) === lvl)); },
        moduleLevelStats(mod, lvl) { const l = this.nodesIn(mod, lvl); const v = l.filter(n => n.status === 'validated').length; return { total: l.length, validated: v, pct: l.length ? Math.round(100 * v / l.length) : 0 }; },
        get moduleCards() {
          const mk = (id, label, icon) => { const l = this.nodesIn(id); const v = l.filter(n => n.status === 'validated').length; return { id, label, icon, total: l.length, validated: v, pct: l.length ? Math.round(100 * v / l.length) : 0 }; };
          return [mk('all', 'Tous les modules', '🧭'), ...this.modules.map(m => mk(m.id, m.label, m.icon))];
        },
        setModule(id) {
          this.moduleFilter = id;
          this.treeFilter = 'all';
          this.submoduleFilter = null;
          const firstCourse = id === 'all' ? null : this.orderedModuleLessons(id)[0];
          this.moduleNextCourseId = firstCourse && firstCourse.id ? firstCourse.id : null;
        },
        openLearningStep() {
          const node = this.resumeNode;
          if (!node) return;
          this.moduleNextCourseId = null;
          return this.show(node.id);
        },
        get submodules() {
          const grouped = new Map();
          this.nodes
            .filter(n => this.moduleFilter !== 'all' && this.moduleOf(n) === this.moduleFilter)
            .forEach(n => {
              const name = n.category || 'Sans catégorie';
              if (!grouped.has(name)) grouped.set(name, []);
              grouped.get(name).push(n);
            });

          return [...grouped.entries()].map(([name, items]) => {
            const total = items.length;
            const validated = items.filter(n => n.status === 'validated').length;
            return {
              name,
              icon: this.categoryIcon(name),
              total,
              validated,
              progress: total ? Math.round(100 * validated / total) : 0
            };
          });
        },
        get showSubmoduleOverview() {
          return this.moduleFilter !== 'all'
            && this.treeFilter === 'all'
            && this.submoduleFilter === null
            && this.submodules.length > 1;
        },
        get showCourseTree() {
          return !this.showSubmoduleOverview;
        },
        selectSubmodule(categoryName) {
          this.submoduleFilter = categoryName;
        },
        returnToSubmodules() {
          this.submoduleFilter = null;
        },
        categoryIcon(name) {
          const icons = {
            'Fondamentaux': '🧱',
            'Couche 2': '🔌',
            'Couche 3': '🌐',
            'Routage': '🧭',
            'Routage Avancé': '🚀',
            'Services': '⚙️',
            'Sécurité': '🛡️',
            'Exploitation': '🛠️',
            'Cloud & Auto': '☁️',
            'Labs': '🧪',
            'Défis': '🎯'
          };
          return icons[name] || '📚';
        },
        get categories() {
          const map = { beginner: 'debutant', intermediaire: 'intermediaire', expert: 'expert' };
          const grouped = new Map();
          this.nodes.filter(n => {
            const moduleMatches = this.moduleFilter === 'all' || this.moduleOf(n) === this.moduleFilter;
            const levelMatches = this.treeFilter === 'all'
              || (this.treeFilter === 'favorites' ? this.isFavorite(n.id) : this.levelOf(n) === map[this.treeFilter]);
            const category = n.category || 'Sans catégorie';
            const submoduleMatches = this.submoduleFilter === null || category === this.submoduleFilter;
            return moduleMatches && levelMatches && submoduleMatches;
          }).forEach(n => {
            const name = n.category || 'Sans catégorie';
            if (!grouped.has(name)) grouped.set(name, []);
            grouped.get(name).push(n);
          });
          return [...grouped.entries()].map(([name, items]) => ({
            name,
            items,
            validated: items.filter(n => n.status === 'validated').length
          }));
        },

        // ---------- gestionnaire de modules / migration ----------
        modMgrOpen: false, modMgrQuery: '',
        get modMgrNodes() { const q = this.norm(this.modMgrQuery); return this.nodes.filter(n => !q || this.norm(n.id + ' ' + n.title + ' ' + n.category).includes(q)); },
        setNodeModule(id, m) { this.moduleOverrides = { ...this.moduleOverrides, [id]: m }; LS.set('module-overrides', this.moduleOverrides); },
        setNodeLevel(id, l) { const o = { ...this.levelOverrides }; if (l) o[id] = l; else delete o[id]; this.levelOverrides = o; LS.set('level-overrides', o); },
        bulkModule(m) { const o = { ...this.moduleOverrides }; this.modMgrNodes.forEach(n => { o[n.id] = m; }); this.moduleOverrides = o; LS.set('module-overrides', o); this.notify(`${this.modMgrNodes.length} cours assignés à ${this.moduleMeta(m).label}`); },
        resetMapping() { this.moduleOverrides = {}; this.levelOverrides = {}; LS.set('module-overrides', {}); LS.set('level-overrides', {}); this.notify('Affectations réinitialisées'); },
        exportMapping() {
          const nodes = {}; this.nodes.forEach(n => { nodes[n.id] = { module: this.moduleOf(n), level: this.levelOf(n) }; });
          this.saveFile('modules-mapping.json', new Blob([JSON.stringify({ version: 1, nodes }, null, 2)], { type: 'application/json' }));
          this.notify('Fichier modules-mapping.json exporté (voir migrate_modules.py)');
        },

        // ---------- recherche ----------
        mobileActionsOpen: false, searchQuery: '', searchOpen: false, mobileSearchOpen: false, searchActive: 0, searchContent: false, searchIdx: null, searchBusy: false, searchDone: 0,
        get searchResults() {
          const q = this.norm(this.searchQuery.trim()); if (q.length < 2) return [];
          const toks = q.split(/\s+/); const out = [];
          this.nodes.forEach(n => {
            const hay = this.norm([n.id, n.title, n.category, this.moduleMeta(this.moduleOf(n)).label, (this.levelMeta(this.levelOf(n)) || {}).label].join(' '));
            if (toks.every(t => hay.includes(t))) out.push({ node: n, score: 1 + (this.norm(n.title).includes(q) ? 3 : 0) + (this.norm(n.id).includes(q) ? 2 : 0), snippet: '' });
          });
          if (this.searchContent && this.searchIdx) {
            this.nodes.forEach(n => {
              const e = this.searchIdx[n.id]; if (!e || out.some(o => o.node.id === n.id)) return;
              const i = e.norm.indexOf(q); if (i < 0) return;
              out.push({ node: n, score: 0.5, snippet: '…' + e.raw.slice(Math.max(0, i - 40), i + q.length + 70).replace(/\s+/g, ' ').trim() + '…' });
            });
          }
          return out.sort((a, b) => b.score - a.score).slice(0, 12);
        },
        async toggleContentSearch() {
          if (!this.searchContent || this.searchIdx || this.searchBusy) return;
          this.searchBusy = true; this.searchDone = 0; const idx = {}; const todo = [...this.nodes]; let i = 0;
          const worker = async () => { while (i < todo.length) { const n = todo[i++]; try { const r = await fetch(`/api/node/${n.id}/lesson`); if (r.ok) { const raw = await r.text(); idx[n.id] = { raw, norm: this.norm(raw) }; } } catch (e) { } this.searchDone++; } };
          await Promise.all([worker(), worker(), worker(), worker(), worker()]);
          this.searchIdx = idx; this.searchBusy = false;
        },
        openMobileSearch() {
          this.mobileActionsOpen = false;
          this.mobileSearchOpen = true; this.searchOpen = true;
          this.$nextTick(() => this.$refs.mobileSearchBox?.focus());
        },
        closeMobileSearch() {
          this.mobileSearchOpen = false; this.searchOpen = false;
        },
        openSearchResult(r) { if (!r) return; this.searchOpen = false; this.mobileSearchOpen = false; this.searchQuery = ''; this.show(r.node.id); },
        onGlobalKey(e) {
          const t = e.target; const typing = t && (/^(input|textarea|select)$/i.test(t.tagName) || t.isContentEditable);
          if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) {
            e.preventDefault();
            if (window.matchMedia('(max-width: 1023px)').matches) { this.openMobileSearch(); }
            else { const b = this.$refs.searchBox; if (b) { b.focus(); this.searchOpen = true; } }
            return;
          }
          if (typing || this.open) return;
          if (this.tab === 'memo' && this.currentFlashcard) {
            if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); this.flipFlashcard(); }
            else if (e.key === 'ArrowRight') this.markFlashcard(true);
            else if (e.key === 'ArrowLeft') this.markFlashcard(false);
          }
        },

        // ---------- examens ----------
        examCfg: { module: 'admin-reseaux', levels: ['debutant'], count: 20, minutes: 30 },
        examHistory: LS.get('exam-history', []), examIdx: 0, examFlags: {}, examLeft: 0, examTimerId: null, examConfirm: false, examErr: '', examStarted: 0,
        examBest(mod, lvls) { const key = [...lvls].sort().join('+'); const l = this.examHistory.filter(e => e.module === mod && [...e.levels].sort().join('+') === key); return l.length ? Math.max(...l.map(e => e.score)) : null; },
        examBestLabel(mod, lvls) { const b = this.examBest(mod, lvls); return b === null ? 'Jamais passé' : 'Meilleur score : ' + b + ' %'; },
        toggleCfgLevel(id) {
          if (id === 'all') {
            this.examCfg.levels = this.examCfg.levels.includes('all') ? ['debutant'] : ['all'];
            return;
          }
          if (this.examCfg.levels.includes('all')) {
            this.examCfg.levels = [id];
            return;
          }
          const l = this.examCfg.levels;
          this.examCfg.levels = l.includes(id) ? l.filter(x => x !== id) : [...l, id];
        },
        randomExamPresets: [
          { icon: '⚡', label: 'Express',   sub: '50 questions · 45 min · aléatoire',  cfg: { module: 'all', levels: ['all'], count: 50,  minutes: 45 } },
          { icon: '🚀', label: 'Complet',   sub: '100 questions · 90 min · aléatoire', cfg: { module: 'all', levels: ['all'], count: 100, minutes: 90 } },
          { icon: '🔥', label: 'Marathon',  sub: '200 questions · 3 h · aléatoire',    cfg: { module: 'all', levels: ['all'], count: 200, minutes: 180 } },
          { icon: '🏆', label: 'Ultime',    sub: '500 questions · 8 h · aléatoire',    cfg: { module: 'all', levels: ['all'], count: 500, minutes: 480 } },
        ],
        get examClock() { return this.fmtClock(this.examLeft); },
        get examAnswered() { return this.examAnswers.filter(a => a !== null && a !== '' && a !== undefined).length; },
        get examBreakdown() {
          if (!this.exam || !this.examResult || !this.examResult.details) return [];
          const g = {}; this.exam.questions.forEach((q, i) => { const l = this.norm(q.level || ''); if (!l) return; g[l] = g[l] || { ok: 0, total: 0 }; g[l].total++; if (this.examResult.details[i] && this.examResult.details[i].correct) g[l].ok++; });
          return Object.entries(g).map(([id, v]) => ({ id, label: (this.levelMeta(id) || { label: id }).label, ...v, pct: Math.round(100 * v.ok / v.total) }));
        },
        get examWrong() {
          if (!this.exam || !this.examResult || !this.examResult.details) return [];
          return this.exam.questions.map((q, i) => ({ q, i, d: this.examResult.details[i] })).filter(x => x.d && x.d.correct === false);
        },
        async launchExam(cfg) {
          if (this.examBusy) return;
          this.examBusy = true;
          this.examErr = '';
          try {
            if (!cfg || !Array.isArray(cfg.levels) || cfg.levels.length === 0) {
              throw new Error('Choisis au moins un niveau pour lancer cet examen.');
            }
            const moduleId = String(cfg.module || 'all');
            const selectedLevels = cfg.levels.map(level => String(level));
            const count = Number(cfg.count || 20);
            const minutes = Number(cfg.minutes || 30);
            if (!Number.isInteger(count) || count < 1 || count > 500) {
              throw new Error('Le nombre de questions doit être compris entre 1 et 500.');
            }
            if (!Number.isFinite(minutes) || minutes < 1 || minutes > 480) {
              throw new Error('La durée doit être comprise entre 1 minute et 8 heures.');
            }

            const allModules = moduleId === 'all';
            const allLevels = selectedLevels.includes('all');
            const scope = this.nodes.filter(n =>
              (allModules || this.moduleOf(n) === moduleId) &&
              (allLevels || selectedLevels.includes(this.levelOf(n)))
            );
            if (!scope.length) {
              throw new Error('Aucun cours disponible pour le module et les niveaux sélectionnés.');
            }

            let pool = scope;
            if (allModules || allLevels) {
              pool = [...scope];
              for (let i = pool.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [pool[i], pool[j]] = [pool[j], pool[i]];
              }
            }
            const levelsBody = allLevels ? ['debutant', 'intermediaire', 'expert'] : selectedLevels;
            const body = {
              ...(allModules ? {} : { module: moduleId, node_ids: pool.map(n => n.id) }),
              levels: levelsBody,
              count,
              time_limit: minutes * 60
            };

            let response = await fetch('/api/exam/build', {
              method: 'POST',
              headers: H,
              body: JSON.stringify(body)
            });
            if (response.status === 404 || response.status === 405) {
              const categories = {};
              scope.forEach(n => {
                categories[n.category] = (categories[n.category] || 0) + 1;
              });
              const category = Object.keys(categories).sort((a, b) => categories[b] - categories[a])[0];
              if (!category) throw new Error('Impossible de déterminer la catégorie de cet examen.');
              response = await fetch('/api/exam/start', {
                method: 'POST',
                headers: H,
                body: JSON.stringify({ ...body, category })
              });
            }
            if (!response.ok) {
              const responseText = await response.text();
              let message = responseText;
              try {
                const errorPayload = JSON.parse(responseText);
                message = errorPayload.detail || errorPayload.message || errorPayload.error || responseText;
              } catch (_) { /* Le serveur peut aussi renvoyer un texte brut. */ }
              throw new Error(message || ('Erreur HTTP ' + response.status));
            }

            const data = await response.json();
            const rawQuestions = Array.isArray(data.questions) ? data.questions : [];
            const questions = rawQuestions.filter(question =>
              !/question temporaire|réponse provisoire|option temporaire/i.test(String(question.prompt || ''))
            );
            if (!questions.length) {
              throw new Error('Aucune question exploitable pour ce périmètre. Vérifie les banques de quiz et d’examen.');
            }
            const selectedQuestions = questions.length > count ? questions.slice(0, count) : questions;
            if (selectedQuestions.length < count) {
              this.notify('Seulement ' + selectedQuestions.length + ' questions disponibles (demandé : ' + count + ').');
            }

            this.exam = {
              ...data,
              questions: selectedQuestions,
              cfg: { module: moduleId, levels: [...selectedLevels], count, minutes },
              category: allModules ? '🎲 Aléatoire · Tous modules' : (data.category || this.moduleMeta(moduleId).label)
            };
            this.examAnswers = selectedQuestions.map(() => null);
            this.examFlags = {};
            this.examIdx = 0;
            this.examResult = null;
            this.examConfirm = false;
            this.examLeft = Number(data.time_limit) || minutes * 60;
            this.examStarted = Date.now();
            this.startExamTimer();
          } catch (error) {
            this.examErr = error && error.message ? error.message : 'Impossible de démarrer cet examen. Réessaie.';
            if (typeof this.notify === 'function') this.notify(this.examErr);
          } finally {
            this.examBusy = false;
          }
        },
        startExamTimer() { this.stopExamTimer(); this.examTimerId = setInterval(() => { this.examLeft--; if (this.examLeft <= 0) this.submitExam(true); }, 1000); },
        stopExamTimer() { if (this.examTimerId) { clearInterval(this.examTimerId); this.examTimerId = null; } },
        gradeLocally() {
          const qs = this.exam.questions; if (!qs.every(q => typeof q.answer === 'number')) return null;
          const details = qs.map((q, i) => ({ correct: this.examAnswers[i] === q.answer, answer: q.answer, explanation: q.explanation || '' }));
          const correct = details.filter(d => d.correct).length;
          return { score: Math.round(100 * correct / qs.length), correct, total: qs.length, details };
        },
        async submitExam(auto) {
          if (!this.exam || this.examResult || this.examBusy) return;
          this.examBusy = true;
          this.stopExamTimer();
          this.examConfirm = false;
          this.examErr = '';
          const clientDuration = Math.max(0, Math.round((Date.now() - this.examStarted) / 1000));
          let result;

          try {
            const response = await fetch('/api/exam/submit', {
              method: 'POST',
              headers: H,
              body: JSON.stringify({ session_id: this.exam.id, answers: this.examAnswers })
            });
            const raw = await response.text();
            try {
              result = raw ? JSON.parse(raw) : {};
            } catch (_) {
              throw new Error('Le serveur a renvoyé une réponse illisible.');
            }
            if (!response.ok) {
              throw new Error(result.detail || result.message || ('Erreur HTTP ' + response.status));
            }
            if (
              !result
              || result.success !== true
              || typeof result.score !== 'number'
              || !Number.isFinite(result.score)
              || result.score < 0
              || result.score > 100
              || typeof result.passed !== 'boolean'
            ) {
              throw new Error('Le serveur n’a pas renvoyé un résultat de correction valide.');
            }
          } catch (error) {
            this.examErr = 'Impossible de corriger l’examen côté serveur : '
              + (error.message || 'erreur réseau')
              + '. Les réponses sont conservées ; réessaie sans quitter cet écran.';
            if (!auto && this.examLeft > 0 && !this.examResult) this.startExamTimer();
            this.examBusy = false;
            return;
          }

          const score = Math.max(0, Math.min(100, Math.round(result.score)));
          const duration = Number.isFinite(Number(result.duration))
            ? Math.max(0, Math.round(Number(result.duration)))
            : clientDuration;
          const passed = result.passed;

          this.examResult = { ...result, score, passed, auto: !!auto, duration };
          this.examHistory = [{
            id: Date.now(),
            date: new Date().toISOString(),
            module: this.exam.cfg.module,
            levels: this.exam.cfg.levels,
            score,
            passed,
            correct: result.correct,
            total: result.total,
            duration
          }, ...this.examHistory].slice(0, 50);
          LS.set('exam-history', this.examHistory);
          this.examBusy = false;
          if (passed) this.celebrate();

          try {
            await this.refreshAll();
          } catch (_) {
            // La note est déjà enregistrée côté serveur : un rafraîchissement secondaire ne l'annule pas.
            this.notify('Examen enregistré ; certaines données du tableau de bord n’ont pas pu être actualisées.');
          }
        },
        resetExam() { this.stopExamTimer(); this.exam = null; this.examResult = null; this.examConfirm = false; },

        // ---------- labs ----------
        labIndex: {}, labIndexBusy: false, labIndexDone: 0, labCatalogLoaded: false, labCatalog: [], labIndexTask: null, labFilter: { module: 'all', level: 'all' },
        labWorkspaceFallbackId: null,
        labsDone: LS.get('labs-done', []), labSteps: LS.get('lab-steps', {}), labHints: {},
        get labNodes() {
          const catalogById = new Map((this.labCatalog || []).map(lab => [String(lab.id), lab]));
          const courseById = new Map(this.nodes.map(node => [String(node.id), node]));
          const ids = new Set([
            ...this.nodes
              .filter(node => this.labIndex[node.id] || catalogById.has(String(node.id)))
              .map(node => String(node.id)),
            ...this.labCatalog
              .filter(lab => !courseById.has(String(lab.id)))
              .map(lab => String(lab.id)),
          ]);

          return [...ids].map(id => {
            const course = courseById.get(id);
            const catalog = catalogById.get(id);
            const node = course ? { ...course } : {
              id,
              title: String(catalog?.title || id),
              module: String(catalog?.module || ''),
              level: String(catalog?.level || ''),
              category: '',
            };
            if (!node.module && catalog?.module) node.module = String(catalog.module);
            if (!node.level && catalog?.level) node.level = String(catalog.level);
            return node;
          }).filter(node =>
            this.labIndex[node.id] &&
            (this.labFilter.module === 'all' || this.moduleOf(node) === this.labFilter.module) &&
            (this.labFilter.level === 'all' || this.levelOf(node) === this.labFilter.level)
          );
        },
        async loadLabIndex() {
          // Le catalogue v2 pilote l'affichage initial; l'index historique se remplit en parallèle.
          // Une tâche unique empêche de relancer des centaines de requêtes lors d'un aller-retour d'onglet.
          if (this.labIndexTask) return;
          // Les métadonnées de l'arbre donnent déjà les exigences de chaque cours.
          // Ne demande le détail qu'aux cours qui ont réellement un lab historique.
          // Le catalogue v2 séparé couvre les scénarios v2 optionnels et les cours absents de SQLite.
          const todo = this.nodes.filter(n => {
            if (n.id in this.labIndex) return false;
            if (!Array.isArray(n.requirements_detail)) return true;
            return n.requirements_detail.some(requirement => requirement?.kind === 'lab');
          });
          const needsCatalog = !this.labCatalogLoaded;
          if (!todo.length && !needsCatalog) return;

          this.labIndexBusy = needsCatalog;
          this.labIndexDone = 0;
          let i = 0;
          const worker = async () => {
            while (i < todo.length) {
              const n = todo[i++];
              try {
                const r = await fetch(`/api/node/${encodeURIComponent(n.id)}`);
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                const d = await r.json();
                const legacyLab = d.lab || null;
                const current = this.labIndex[n.id];
                // Un résultat tardif du chargement historique ne doit pas effacer un lab v2.
                this.labIndex[n.id] = current?.kind === 'workspace-v2'
                  ? { ...(legacyLab && typeof legacyLab === 'object' ? legacyLab : {}), ...current }
                  : legacyLab;
              } catch (e) {
                if (this.labIndex[n.id]?.kind !== 'workspace-v2') delete this.labIndex[n.id];
                console.warn(`Impossible de charger l’index du lab ${n.id}; une nouvelle tentative sera faite au prochain accès.`, e);
              }
              this.labIndexDone++;
            }
          };

          const loadCatalog = async () => {
            if (this.labCatalogLoaded) return;
            try {
              const response = await fetch('/api/lab/v2');
              if (!response.ok) throw new Error(`HTTP ${response.status}`);
              const catalog = await response.json();
              if (!Array.isArray(catalog)) throw new Error('Format de catalogue invalide');
              this.labCatalog = catalog.filter(lab => lab && typeof lab.id === 'string' && lab.id.trim());
              for (const lab of this.labCatalog) {
                const id = String(lab.id);
                const current = this.labIndex[id] && typeof this.labIndex[id] === 'object'
                  ? this.labIndex[id]
                  : {};
                this.labIndex[id] = {
                  ...current,
                  kind: 'workspace-v2',
                  duration: Number(lab.duration_min ?? current.duration) || null,
                  difficulty: String(lab.difficulty || current.difficulty || ''),
                  schema_version: Number(lab.schema_version || 2),
                };
              }
              this.labCatalogLoaded = true;
            } catch (e) {
              // Ne pas mémoriser un échec : le prochain accès à Labs réessaiera.
              console.warn('Impossible de charger le catalogue Lab Workspace v2; une nouvelle tentative sera faite au prochain accès.', e);
            } finally {
              // L'interface peut afficher les cartes v2 dès que le catalogue a répondu.
              this.labIndexBusy = false;
            }
          };

          const catalogTask = loadCatalog();
          const legacyTask = Promise.all([worker(), worker(), worker(), worker(), worker()]);
          this.labIndexTask = Promise.allSettled([catalogTask, legacyTask]).finally(() => {
            this.labIndexTask = null;
            this.labIndexBusy = false;
          });

          // Ne bloque pas l'ouverture de Labs sur toutes les requêtes de détail historiques.
          await catalogTask;
        },
        hasVisualLab(id) {
          const nodeId = String(id || '');
          if (!nodeId) return false;
          return this.labIndex[nodeId]?.kind === 'workspace-v2' ||
            (Array.isArray(this.labCatalog) && this.labCatalog.some(lab => String(lab?.id || '') === nodeId));
        },
        async openVisualLab() {
          const nodeId = String(this.detail?.id || '');
          if (!nodeId) return;

          // Ouvrir la fenêtre de façon synchrone dans le clic utilisateur, puis vérifier le scénario.
          const labWindow = window.open('about:blank', '_blank');
          if (!labWindow) {
            this.notify("Autorise les fenêtres contextuelles pour ouvrir le laboratoire dans un nouvel onglet.");
            return;
          }

          this.labWorkspaceFallbackId = null;
          try {
            const response = await fetch(`/api/lab/v2/${encodeURIComponent(nodeId)}`);
            const payload = await response.json().catch(() => ({}));
            const topologyNodes = payload?.definition?.initial_topology?.nodes;
            if (
              !response.ok ||
              payload.sandbox === true ||
              !Array.isArray(topologyNodes) ||
              topologyNodes.length === 0
            ) {
              labWindow.close();
              this.labWorkspaceFallbackId = nodeId;
              this.notify(
                response.ok
                  ? "Ce laboratoire ne possède pas encore de scénario visuel v2. Il reste disponible dans le mode classique."
                  : "Le scénario Lab Workspace n’est pas disponible pour le moment. Le mode classique reste accessible."
              );
              return;
            }
            labWindow.location.replace(`/lab.html?id=${encodeURIComponent(nodeId)}`);
          } catch (error) {
            if (!labWindow.closed) labWindow.close();
            this.labWorkspaceFallbackId = nodeId;
            this.notify("Impossible de joindre le Lab Workspace. Le laboratoire reste dans le mode classique.");
          }
        },
        async openLab(id, openInNewTab = false) {
          const nodeId = String(id || '');
          if (!nodeId) return;

          // Préouvrir l'onglet pendant le clic utilisateur pour éviter le blocage popup.
          const labWindow = openInNewTab ? window.open('about:blank', '_blank') : null;
          if (openInNewTab && !labWindow) {
            this.notify("Autorise les fenêtres contextuelles pour ouvrir le laboratoire dans un nouvel onglet.");
            return;
          }
          const navigate = url => {
            if (openInNewTab) {
              if (labWindow && !labWindow.closed) labWindow.location.replace(url);
              else this.notify("La fenêtre du laboratoire a été fermée avant l'ouverture.");
            } else {
              window.location.assign(url);
            }
          };

          // Le nouveau workspace React Flow est prioritaire quand une définition v2 existe.
          // Les nœuds historiques sans définition v2 conservent leur lecteur classique.
          try {
            const response = await fetch(`/api/lab/v2/${encodeURIComponent(nodeId)}`);
            if (response.ok) {
              const labPayload = await response.json();
              // Un bac à sable générique ne remplace pas une consigne legacy déjà disponible.
              // Le workspace v2 n'est prioritaire que lorsqu'une vraie définition de lab existe.
              const topologyNodes = labPayload.definition?.initial_topology?.nodes;
              if (
                !labPayload.sandbox &&
                Array.isArray(topologyNodes) &&
                topologyNodes.length > 0
              ) {
                this.labWorkspaceFallbackId = null;
                navigate(`/lab.html?id=${encodeURIComponent(nodeId)}`);
                return;
              }
            } else if (response.status !== 404) {
              this.notify('Le Lab Workspace est indisponible ; ouverture du laboratoire classique.');
            }
          } catch (error) {
            this.notify('Le Lab Workspace ne répond pas ; ouverture du laboratoire classique.');
          }

          // Un lab historique reste ouvrable dans un nouvel onglet : la page racine
          // réessaie avec openLabInTab=false puis affiche son onglet classique si besoin.
          if (openInNewTab && labWindow && !labWindow.closed) {
            labWindow.location.replace('/?openLab=' + encodeURIComponent(nodeId));
            return;
          }
          await this.show(nodeId);
          this.modalTab = 'lab';
          // Le repli classique est un choix de compatibilité, pas une panne v2.
          this.labWorkspaceFallbackId = null;
        },
        isLabDone(id) { return this.labsDone.includes(id); },
        stepDone(i) { return !!(this.detail && this.labSteps[this.detail.id + ':' + i]); },
        toggleStep(i) { const k = this.detail.id + ':' + i; const o = { ...this.labSteps }; if (o[k]) delete o[k]; else o[k] = 1; this.labSteps = o; LS.set('lab-steps', o); },
        onLabValidated(data) {
          // Un bac à sable peut répondre à son contrôle technique, mais ne valide
          // ni le cours ni le compteur local de labs réussis.
          if (!data || !data.passed || data.sandbox === true || data.stale === true || data.attempt_recorded === false) return;
          // Le résultat d'un onglet séparé doit rester associé au lab lancé,
          // même si l'utilisateur ouvre ensuite un autre cours dans le dashboard.
          const nodeId = String(data.lab_id || (this.detail && this.detail.id) || '');
          if (!nodeId || this.labsDone.includes(nodeId)) return;
          this.labsDone = [...this.labsDone, nodeId];
          LS.set('labs-done', this.labsDone);
          const xp = Number(data.xp_gained ?? data.xpGained ?? data.xp_earned ?? data.xp_reward) || 0;
          this.notify('✅ Lab validé : ' + (data.title || nodeId) + (xp > 0 ? ' · +' + xp + ' XP' : ''));
          this.celebrate();
          this.checkRewards();
        },

        // ---------- récompenses et diplômes ----------
        issuedDiplomas: [], certificationExams: [], diplomaView: null, diplomasError: '', challengesDone: LS.get('challenges-done', []), diagDoneMap: LS.get('diag-done', {}),
        async loadDiplomas() {
          try {
            const response = await fetch('/api/certificates', { headers: H });
            if (!response.ok) throw new Error('HTTP ' + response.status);
            const payload = await response.json();
            this.issuedDiplomas = Array.isArray(payload.items) ? payload.items : [];
            this.certificationExams = Array.isArray(payload.exams) ? payload.exams : [];
            this.diplomasError = '';
          } catch (error) {
            // Conserve les données serveur déjà chargées lors d'une erreur réseau temporaire.
            this.diplomasError = 'Les diplômes ne peuvent pas être chargés depuis le serveur.';
          }
        },
        diplomaStatus(mod, lvl) {
          const s = this.moduleLevelStats(mod, lvl);
          const moduleLabel = (this.moduleMeta(mod) || { label: mod }).label;
          const scopeIds = this.nodesIn(mod, lvl).map(node => String(node.id)).sort();
          const issued = this.issuedDiplomas.find(d => d.module === mod && d.level === lvl);
          if (issued) return { state: 'issued', ...s, issued, best: issued.score, examSessionId: issued.exam_session_id };
          if (!s.total) return { state: 'empty', ...s };
          if (s.validated < s.total) return { state: 'learning', ...s };
          const matching = this.certificationExams.filter(exam => {
            if (exam.module_label !== moduleLabel || exam.level !== lvl || !Array.isArray(exam.scope_node_ids)) return false;
            const savedScope = exam.scope_node_ids.map(String).sort();
            return savedScope.length === scopeIds.length && savedScope.every((id, index) => id === scopeIds[index]);
          });
          const best = matching.length ? Math.max(...matching.map(exam => Number(exam.score) || 0)) : null;
          const passing = matching
            .filter(exam => exam.passed && Number(exam.score) >= PASS_SCORE && exam.session_id)
            .sort((a, b) => Number(b.submitted_at || 0) - Number(a.submitted_at || 0))[0];
          if (!passing) return { state: 'exam', ...s, best };
          return { state: 'ready', ...s, best: Number(passing.score), examSessionId: passing.session_id };
        },
        async startDiplomaExam(mod, lvl) {
          const state = this.diplomaStatus(mod, lvl);
          if (state.state !== 'exam') return;
          const moduleLabel = (this.moduleMeta(mod) || { label: mod }).label;
          this.examBusy = true;
          this.examErr = '';
          try {
            const response = await fetch('/api/certificate/exam/start', {
              method: 'POST', headers: H,
              body: JSON.stringify({ module: moduleLabel, module_id: mod, level: lvl })
            });
            const raw = await response.text();
            let data;
            try { data = raw ? JSON.parse(raw) : {}; } catch (_) { data = { detail: raw }; }
            if (!response.ok) throw new Error(data.detail || ('HTTP ' + response.status));
            const questions = Array.isArray(data.questions) ? data.questions : [];
            if (!questions.length) throw new Error('Aucune question disponible pour cet examen de diplôme.');
            this.exam = {
              ...data,
              questions,
              cfg: { module: mod, levels: [lvl], count: questions.length, minutes: Math.ceil((Number(data.time_limit) || 1800) / 60) },
              category: data.category || ('Diplôme · ' + moduleLabel)
            };
            this.examAnswers = questions.map(() => null);
            this.examFlags = {};
            this.examIdx = 0;
            this.examResult = null;
            this.examConfirm = false;
            this.examLeft = Number(data.time_limit) || 1800;
            this.examInitialTime = this.examLeft;
            this.examStarted = Date.now();
            this.examPaused = false;
            this.tab = 'exam';
            this.startExamTimer();
          } catch (error) {
            this.examErr = error.message || 'Impossible de démarrer l’examen officiel.';
            this.notify(this.examErr);
          } finally {
            this.examBusy = false;
          }
        },
        async issueDiploma(mod, lvl) {
          const st = this.diplomaStatus(mod, lvl);
          if (st.state !== 'ready' || !st.examSessionId) return;
          const moduleLabel = (this.moduleMeta(mod) || { label: mod }).label;
          try {
            const response = await fetch('/api/certificate/issue', {
              method: 'POST', headers: H,
              body: JSON.stringify({
                module: moduleLabel,
                module_id: mod,
                level: lvl,
                exam_session_id: st.examSessionId,
                name: this.userName
              })
            });
            const raw = await response.text();
            let data;
            try { data = raw ? JSON.parse(raw) : {}; } catch (_) { data = { detail: raw }; }
            if (!response.ok || !data.certificate) throw new Error(data.detail || ('HTTP ' + response.status));
            this.diplomaView = data.certificate;
            await this.loadDiplomas();
            this.celebrate();
            this.checkRewards();
          } catch (error) {
            this.notify('Le diplôme n’a pas pu être délivré : ' + (error.message || 'erreur serveur'));
          }
        },
        viewDiploma(mod, lvl) {
          const d = this.issuedDiplomas.find(x => x.module === mod && x.level === lvl);
          if (d) this.diplomaView = d;
        },
        fmtDate(iso) { try { return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return iso; } },
        async downloadDiploma() {
          if (!this.diplomaView || !this.diplomaView.number) { this.notify('Ce diplôme ne possède pas de numéro serveur.'); return; }
          try {
            const response = await fetch('/api/certificate?number=' + encodeURIComponent(this.diplomaView.number), { headers: H });
            if (!response.ok) throw new Error('HTTP ' + response.status);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'diplome-' + this.diplomaView.number + '.pdf';
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
          } catch (error) {
            this.notify('Téléchargement du PDF impossible : ' + (error.message || 'erreur serveur'));
          }
        },
        printDiploma() { window.print(); },
        get badges() {
          const done = this.validated; const passed = this.examHistory.filter(e => e.passed); const best = this.examHistory.reduce((m, e) => Math.max(m, e.score || 0), 0);
          const modulesDone = this.modules.filter(m => { const l = this.nodesIn(m.id); return l.length && l.every(n => n.status === 'validated'); }).length;
          const b = (id, icon, name, desc, ok) => ({ id, icon, name, desc, ok });
          return [
            b('first', '🚀', 'Premier pas', 'Valider un premier cours', done >= 1), b('five', '📚', 'Studieux', 'Valider 5 cours', done >= 5),
            b('ten', '🎯', 'Assidu', 'Valider 10 cours', done >= 10), b('twentyfive', '⭐', 'Expert en herbe', 'Valider 25 cours', done >= 25), b('fifty', '👑', 'Érudit', 'Valider 50 cours', done >= 50),
            b('exam1', '📝', 'Premier examen', 'Réussir un examen', passed.length >= 1), b('exam5', '🧠', 'Persévérant', 'Réussir 5 examens', passed.length >= 5),
            b('perfect', '💯', 'Sans faute', 'Obtenir 100 % à un examen', best >= 100),
            b('lab1', '🧪', 'Mains dans le réseau', 'Réussir un lab', this.labsDone.length >= 1), b('lab5', '🛠️', 'Technicien', 'Réussir 5 labs', this.labsDone.length >= 5),
            b('streak7', '🔥', 'Une semaine', '7 jours consécutifs', this.streakDays >= 7), b('streak30', '🌋', 'Un mois', '30 jours consécutifs', this.streakDays >= 30),
            b('topo', '🧩', 'Architecte', "Réussir un défi d'architecture", this.challengesDone.length >= 1),
            b('diag', '🩺', 'Dépanneur', 'Terminer un diagnostic avec 80 % d’efficacité', Object.values(this.diagDoneMap).some(v => v >= 80)),
            b('diploma1', '🎓', 'Diplômé', 'Obtenir un diplôme', this.issuedDiplomas.length >= 1), b('diploma3', '🏅', 'Triple diplômé', 'Obtenir 3 diplômes', this.issuedDiplomas.length >= 3),
            b('module', '🏆', 'Maître de module', 'Terminer un module complet', modulesDone >= 1),
          ];
        },
        checkRewards() {
          if (!this.nodes.length) return;
          const ok = this.badges.filter(b => b.ok).map(b => b.id); const seen = LS.get('badges-seen', null);
          if (seen === null) { LS.set('badges-seen', ok); return; }
          const fresh = ok.filter(id => !seen.includes(id)); if (!fresh.length) return;
          LS.set('badges-seen', [...seen, ...fresh]); const b = this.badges.find(x => x.id === fresh[0]);
          this.notify(`${b.icon} Badge débloqué : ${b.name}` + (fresh.length > 1 ? ` (+${fresh.length - 1})` : '')); this.celebrate();
        },

        // ---------- topologie ----------
        devices: [
          { type: 'router', label: 'Routeur', hint: 'L3', icon: TOPO_ICONS.router }, { type: 'switch', label: 'Switch', hint: 'L2', icon: TOPO_ICONS.switch },
          { type: 'firewall', label: 'Firewall', hint: 'Sécurité', icon: TOPO_ICONS.firewall }, { type: 'server', label: 'Serveur', hint: 'Services', icon: TOPO_ICONS.server },
          { type: 'pc', label: 'PC', hint: 'Terminal', icon: TOPO_ICONS.pc }, { type: 'laptop', label: 'Portable', hint: 'Client', icon: TOPO_ICONS.laptop },
          { type: 'wifi', label: 'Point d’accès', hint: 'Wi-Fi', icon: TOPO_ICONS.wifi }, { type: 'cloud', label: 'Cloud', hint: 'Externe', icon: TOPO_ICONS.cloud },
          { type: 'spine', label: 'Spine', hint: 'Fabric', icon: TOPO_ICONS.spine }, { type: 'leaf', label: 'Leaf', hint: 'Fabric', icon: TOPO_ICONS.leaf },
          { type: 'apic', label: 'Contrôleur APIC', hint: 'Control plane', icon: TOPO_ICONS.apic },
          { type: 'plc', label: 'Automate industriel', hint: 'OT', icon: TOPO_ICONS.plc },
        ],
        topoCounts: { nodes: 0, links: 0 }, topoTypeCounter: {}, challenge: null, challengeLeft: 0, challengeTimer: null, challengeResult: null, challengeSubmissionBusy: false,
        get challengeNodes() { return this.nodes.filter(n => n.type === 'architecture' || /^challenge-/.test(n.id)); },
        get expectedSummary() {
          if (!this.challenge) return '';
          // Pour les défis serveur, le navigateur reçoit uniquement un résumé,
          // jamais la correction complète des connexions attendues.
          const e = this.challenge.expectedSummary || this.challenge.expected || {};
          const nodes = Object.entries(e.nodes || {}).map(([k, v]) => `${v} ${k}`).join(' · ');
          const connectionCount = Array.isArray(e.connections)
            ? e.connections.length
            : Math.max(0, Number(e.connections) || 0);
          return `${nodes || 'Topologie à construire'} — ${connectionCount} liens`;
        },
        async initTopology() {
          if (this.topologyReady) return;
          if (!this.$refs.canvas) return;
          try {
            await Promise.all([
              window.skillTreeLoadScript('https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.js', 'Drawflow'),
              window.skillTreeLoadStyle('https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.css'),
            ]);
          } catch (error) {
            console.warn('Drawflow indisponible.', error);
            this.notify('Impossible de charger l’éditeur de topologie. Réessaie.');
            return;
          }
          const el = this.$refs.canvas;
          if (!el || this.topologyReady || typeof window.Drawflow !== 'function') return;
          const ed = new window.Drawflow(el); ed.reroute = true; ed.start();
          ['nodeCreated', 'nodeRemoved', 'connectionCreated', 'connectionRemoved', 'nodeMoved'].forEach(ev => ed.on(ev, () => this.refreshTopo()));
          this.topologyEditor = ed; this.topologyReady = true;
          // Les topologies libres ne sont plus restaurées : ce canevas est réservé aux défis,
          // qui doivent toujours commencer avec une configuration vierge.
          this.refreshTopo(false);
        },
        topoData() { try { return this.topologyEditor.export().drawflow.Home.data || {}; } catch (e) { return {}; } },
        refreshTopo(save = true) {
          const d = this.topoData(); let links = 0; Object.values(d).forEach(n => Object.values(n.outputs || {}).forEach(o => { links += (o.connections || []).length; }));
          this.topoCounts = { nodes: Object.keys(d).length, links };
          if (save) { try { LS.set('topology-draft', this.topologyEditor.export()); } catch (e) { } }
        },
        addDevice(type) {
          const ed = this.topologyEditor; if (!ed) return; const d = this.devices.find(x => x.type === type);
          this.topoTypeCounter[type] = (this.topoTypeCounter[type] || 0) + 1; const label = `${d.label} ${this.topoTypeCounter[type]}`;
          const n = Object.keys(this.topoData()).length; const x = 70 + (n % 6) * 150, y = 60 + Math.floor(n / 6) * 130;
          const html = `<div class="topo-node"><span class="topo-icon">${d.icon}</span><span><span class="topo-label">${label}</span><span class="topo-sub">${d.hint}</span></span></div>`;
          ed.addNode(type, 3, 3, x, y, type, { label }, html, false);
        },
        removeSelected() { const ed = this.topologyEditor; if (ed && ed.node_selected && ed.node_selected.id) ed.removeNodeId(ed.node_selected.id); },
        clearTopology() { if (!this.topologyEditor) return; this.topologyEditor.clear(); this.topoTypeCounter = {}; this.refreshTopo(); },
        async saveTopology() {
          const data = this.topologyEditor.export(); LS.set('topology-draft', data);
          try { await fetch('/api/topology', { method: 'POST', headers: H, body: JSON.stringify(data) }); this.notify('Topologie sauvegardée'); } catch (e) { this.notify('Sauvegardée localement (serveur injoignable)'); }
        },
        async loadTopology() {
          try { const r = await fetch('/api/topology'); const d = await r.json(); if (d && d.drawflow) { this.topologyEditor.import(d); this.refreshTopo(); this.notify('Topologie chargée'); } else this.notify('Aucune topologie sur le serveur'); } catch (e) { this.notify('Chargement impossible'); }
        },
        async exportTopologyPng() {
          const el = document.getElementById('drawflow');
          if (!el) return;
          try { await window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js', 'html2canvas'); }
          catch (error) { console.warn('html2canvas indisponible.', error); this.notify('L’export PNG est indisponible pour le moment.'); return; }
          if (typeof window.html2canvas !== 'function') return;
          const canvas = await window.html2canvas(el, { backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--s0').trim() });
          canvas.toBlob(blob => this.saveFile('topologie.png', blob), 'image/png');
        },
        topoSnapshot() {
          const d = this.topoData(); const nodes = {}, links = {};
          Object.values(d).forEach(n => { nodes[n.name] = (nodes[n.name] || 0) + 1; Object.values(n.outputs || {}).forEach(o => (o.connections || []).forEach(c => { const t = d[c.node]; if (!t) return; const k = [n.name, t.name].sort().join('|'); links[k] = (links[k] || 0) + 1; })); });
          return { nodes, links };
        },
        async startChallenge(id) {
          try {
            const response = await fetch(`/api/node/${encodeURIComponent(String(id))}`);
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || `Erreur HTTP ${response.status}`);
            const challenge = data.challenge || {};
            if (!challenge.expected_summary) throw new Error('résumé du défi indisponible');

            // On ne détruit le canevas qu'après avoir confirmé que le scénario existe côté serveur.
            this.clearTopology();
            const requirement = (data.requirements || []).find(item => item.kind === 'manual') || {};
            this.challenge = {
              id: data.id || String(id),
              title: data.title,
              description: data.description,
              expectedSummary: challenge.expected_summary,
              minScore: requirement.min_score || 100,
              brief: challenge.brief || {},
              builtin: false,
            };
            this.challengeResult = null;
            const timeLimit = Number(challenge.time_limit);
            this.challengeLeft = Number.isFinite(timeLimit) && timeLimit > 0 ? Math.floor(timeLimit) : 300;
            clearInterval(this.challengeTimer);
            this.challengeTimer = setInterval(() => {
              if (!this.challenge || this.challengeResult) {
                clearInterval(this.challengeTimer);
                return;
              }
              this.challengeLeft = Math.max(0, this.challengeLeft - 1);
              if (this.challengeLeft === 0) this.checkChallenge(true);
            }, 1000);
          } catch (error) {
            this.notify('Défi indisponible : ' + error.message);
          }
        },
        endChallenge() { if (this.challengeSubmissionBusy) { this.notify('La vérification du défi est en cours. Attends son résultat avant de quitter.'); return; } clearInterval(this.challengeTimer); this.challenge = null; this.challengeResult = null; },
        checkChallenge(timeout) {
          if (!this.challenge) return; clearInterval(this.challengeTimer);
          const exp = this.challenge.expected; const expLinks = {}; (exp.connections || []).forEach(c => { const k = [c.from, c.to].sort().join('|'); expLinks[k] = (expLinks[k] || 0) + 1; });
          const have = this.topoSnapshot();
          const cmp = (h, e) => { const keys = new Set([...Object.keys(h), ...Object.keys(e)]); let match = 0, sh = 0, se = 0; const missing = [], extra = []; keys.forEach(k => { const a = h[k] || 0, b = e[k] || 0; match += Math.min(a, b); sh += a; se += b; if (a < b) missing.push(`${b - a} × ${k.replace('|', ' ↔ ')}`); if (a > b) extra.push(`${a - b} × ${k.replace('|', ' ↔ ')}`); }); return { ratio: Math.max(sh, se) ? match / Math.max(sh, se) : 1, missing, extra }; };
          const n = cmp(have.nodes, exp.nodes || {}), l = cmp(have.links, expLinks);
          const score = Math.round(100 * (0.5 * n.ratio + 0.5 * l.ratio)); const passed = !timeout && score >= this.challenge.minScore;
          this.challengeResult = { score, passed, timeout: !!timeout, missingNodes: n.missing, extraNodes: n.extra, missingLinks: l.missing, extraLinks: l.extra };
          if (passed && !this.challengesDone.includes(this.challenge.id)) { this.challengesDone = [...this.challengesDone, this.challenge.id]; LS.set('challenges-done', this.challengesDone); this.celebrate(); this.checkRewards(); }
        },

        // ---------- diagnostic ----------
        diagList: [], diagId: null, diagData: null, diagKey: null, diagTrail: [],
        diagRunStartedAt: 0, diagCommandInput: '', diagCommandFeedback: '',
        diagAdaptiveQuestion: null, diagAdaptiveResumeKey: null, diagAdaptiveNextKey: null,
        diagAdaptiveAttempts: 0, diagAdaptiveFeedback: '',
        diagProgressMap: LS.get('diag-progress', {}) || {}, diagResultsMap: LS.get('diag-results', {}) || {},
        async loadDiagnostic() {
          if (this.diagList.length) return;
          this.diagList = [{ id: 'network_down', title: 'Poste sans accès au réseau', level: 'debutant', domain: 'network', desc: 'Identifie une panne d’adressage et choisis un rétablissement sûr.' },
            ...Object.entries(DIAG_BUILTIN).map(([id, d]) => ({ id, title: d.title, level: d.level, domain: d.domain || 'network', desc: d.desc }))];
        },
        async openDiag(id) {
          let data = DIAG_BUILTIN[id];
          if (!data) { try { const r = await fetch(`/api/diagnostics/${id}`); if (!r.ok) throw new Error(); data = await r.json(); } catch (e) { this.notify('Scénario indisponible'); return; } }
          const progressMap = this.diagProgressMap && typeof this.diagProgressMap === 'object' && !Array.isArray(this.diagProgressMap)
            ? this.diagProgressMap : {};
          const saved = progressMap[id];
          const steps = data.steps || {};
          const validTrail = saved && Array.isArray(saved.trail) && saved.trail.every(item =>
            item && typeof item === 'object' && typeof item.key === 'string' && !!steps[item.key] &&
            (item.good === undefined || typeof item.good === 'boolean'));
          const validAdaptiveQuestion = !saved || !saved.adaptiveQuestion || (
            typeof saved.adaptiveQuestion.prompt === 'string' &&
            Array.isArray(saved.adaptiveQuestion.choices) && saved.adaptiveQuestion.choices.length > 0 &&
            saved.adaptiveQuestion.choices.every(choice => choice && typeof choice.label === 'string' && typeof choice.good === 'boolean'));
          const validAdaptiveKeys = !saved || (
            (!saved.adaptiveResumeKey || !!steps[saved.adaptiveResumeKey]) &&
            (!saved.adaptiveNextKey || !!steps[saved.adaptiveNextKey]));
          const canResume = !!(saved && steps[saved.stepKey] && validTrail && validAdaptiveQuestion && validAdaptiveKeys);
          this.diagProgressMap = progressMap;
          if (saved && !canResume) {
            const cleanedProgress = { ...progressMap };
            delete cleanedProgress[id];
            this.diagProgressMap = cleanedProgress;
            LS.set('diag-progress', cleanedProgress);
          }
          this.diagId = id;
          this.diagData = data;
          this.diagKey = canResume ? saved.stepKey : data.start;
          this.diagTrail = canResume ? saved.trail : [];
          this.diagRunStartedAt = canResume && Number.isFinite(Number(saved.startedAt)) ? Number(saved.startedAt) : Date.now();
          this.diagAdaptiveQuestion = canResume ? (saved.adaptiveQuestion || null) : null;
          this.diagAdaptiveResumeKey = canResume ? (saved.adaptiveResumeKey || null) : null;
          this.diagAdaptiveNextKey = canResume ? (saved.adaptiveNextKey || null) : null;
          this.diagAdaptiveAttempts = canResume ? (Number(saved.adaptiveAttempts) || 0) : 0;
          this.diagAdaptiveFeedback = canResume ? (saved.adaptiveFeedback || '') : '';
          this.diagCommandInput = '';
          this.diagCommandFeedback = '';
          if (!canResume) this.diagSaveProgress();
        },
        get diagStep() { return this.diagData && this.diagData.steps ? this.diagData.steps[this.diagKey] || null : null; },
        get diagFinished() { return !!this.diagStep && !(this.diagStep.choices && this.diagStep.choices.length) && !this.diagStep.command; },
        get diagEfficiency() { const r = this.diagTrail.filter(x => x.good === true || x.good === false); return r.length ? Math.round(100 * r.filter(x => x.good === true).length / r.length) : null; },
        diagCorrectCount() { return this.diagTrail.filter(x => x.good === true).length; },
        diagScoredCount() { return this.diagTrail.filter(x => x.good === true || x.good === false).length; },
        diagElapsedSeconds() { return this.diagRunStartedAt ? Math.max(0, Math.floor((Date.now() - this.diagRunStartedAt) / 1000)) : 0; },
        diagElapsedLabel() { const s = this.diagElapsedSeconds(); return s >= 60 ? `${Math.floor(s / 60)} min ${s % 60}s` : `${s}s`; },
        diagFinalOutcome() { return (this.diagStep && this.diagStep.conclusion && this.diagStep.conclusion.outcome) || (this.diagStep && this.diagStep.outcome) || null; },
        diagCompetencySummary() {
          const groups = new Map();
          this.diagTrail.forEach(item => {
            if (item.good !== true && item.good !== false) return;
            const name = item.competency || 'Méthode de dépannage';
            const group = groups.get(name) || { name, total: 0, correct: 0 };
            group.total += 1;
            if (item.good === true) group.correct += 1;
            groups.set(name, group);
          });
          return [...groups.values()].map(item => ({ ...item, rate: Math.round(100 * item.correct / item.total) }))
            .sort((a, b) => a.rate - b.rate || a.name.localeCompare(b.name, 'fr'));
        },
        diagCompetencyToReview() { return this.diagCompetencySummary().filter(item => item.rate < 80).map(item => item.name); },
        diagLearningRecommendations() {
          const courses = new Map();
          const labs = new Map();
          const weak = this.diagCompetencySummary().filter(item => item.rate < 80)
            .sort((a, b) => a.rate - b.rate || a.name.localeCompare(b.name, 'fr'));
          weak.forEach(item => {
            const path = DIAG_LEARNING_PATHS[item.name];
            if (!path) return;
            const candidates = (path.courseIds || []).map(id => this.nodes.find(node => String(node.id) === id)).filter(Boolean);
            const course = candidates.find(node => node.status !== 'validated' && node.status !== 'locked');
            if (course && !courses.has(course.id)) {
              const isPrimaryTarget = String(course.id) === String((path.courseIds || [])[0]);
              courses.set(course.id, { node: course, competency: item.name, rate: item.rate,
                reason: !isPrimaryTarget
                  ? 'Prérequis à valider pour débloquer le parcours ciblé.'
                  : (item.rate < 50 ? 'Reprendre les fondamentaux avant de progresser.' : 'Consolider cette notion avant de poursuivre.') });
            }
            (path.labIds || []).forEach(id => {
              const node = this.nodes.find(candidate => String(candidate.id) === id);
              if (!node || node.status === 'validated' || node.status === 'locked' || this.isLabDone(node.id) || labs.has(node.id)) return;
              labs.set(node.id, { node, competency: item.name, rate: item.rate });
            });
          });
          return { courses: [...courses.values()].slice(0, 3), labs: [...labs.values()].slice(0, 2) };
        },
        async diagOpenCourse(nodeId) {
          if (!nodeId) return;
          await this.setTab('tree');
          await this.show(nodeId);
        },
        async diagStartGuidedReview(nodeId) {
          if (!nodeId) return;
          await this.loadFlashcards();
          const hasCards = this.flashcards.some(card => String(card.node_id) === String(nodeId));
          if (!hasCards) {
            this.notify('Aucune carte de révision n’est disponible pour ce cours. Je l’ouvre pour que tu puisses le reprendre.');
            await this.setTab('tree');
            await this.show(nodeId);
            return;
          }
          this.reviewNodeId = String(nodeId);
          this.reviewDaysSince = null;
          await this.setTab('memo');
        },
        async diagOpenLab(nodeId) {
          if (!nodeId) return;
          await this.openLab(nodeId);
        },
        diagLevelRank(level) {
          const normalized = this.norm(level || '').replace(/\s+/g, '');
          return ({ debutant: 0, intermediaire: 1, expert: 2 })[normalized] ?? -1;
        },
        diagLevelLabel(level) {
          const normalized = this.norm(level || '').replace(/\s+/g, '');
          return ({ debutant: 'Débutant', intermediaire: 'Intermédiaire', expert: 'Expert' })[normalized] || 'niveau inconnu';
        },
        diagDomainLabel(domain) {
          return ({ network: 'réseaux', linux: 'systèmes Linux', security: 'cybersécurité', cloud: 'cloud' })[domain] || 'domaine général';
        },
        diagNextScenarioRecommendation() {
          if (!this.diagFinished || this.diagFinalOutcome() !== 'success' || this.diagEfficiency === null) return null;
          const score = this.diagEfficiency;
          const currentId = this.diagId;
          const current = this.diagList.find(item => item.id === currentId) || {
            id: currentId,
            title: this.diagData && this.diagData.title,
            level: this.diagData && this.diagData.level,
            domain: (this.diagData && this.diagData.domain) || 'network'
          };
          if (score < 60) {
            return { id: currentId, title: this.diagData.title, replay: true, reason: 'Ton efficacité reste inférieure à 60 %. Rejoue ce scénario après avoir travaillé les compétences recommandées.' };
          }

          const currentRank = this.diagLevelRank(current.level || (this.diagData && this.diagData.level));
          if (currentRank < 0) return null;
          const currentDomain = current.domain || 'network';
          const completed = this.diagDoneMap || {};
          const isCompleted = item => Object.prototype.hasOwnProperty.call(completed, item.id);
          const scenarios = this.diagList.filter(item => item.id !== currentId && this.diagLevelRank(item.level) >= 0);
          const sameLevel = scenarios.filter(item => this.diagLevelRank(item.level) === currentRank);
          const higherLevel = scenarios.filter(item => this.diagLevelRank(item.level) > currentRank);
          const preferSameDomain = items => [...items].sort((a, b) => {
            const sameDomainA = (a.domain || 'network') === currentDomain ? 1 : 0;
            const sameDomainB = (b.domain || 'network') === currentDomain ? 1 : 0;
            if (sameDomainA !== sameDomainB) return sameDomainB - sameDomainA;
            return 0; // Preserve the curriculum's declared scenario order.
          });

          if (score < 80) {
            // Pour une efficacité moyenne, ne pas revenir vers un scénario déjà terminé :
            // on préfère un scénario inédit du même niveau, même s’il faut changer de domaine.
            const unplayedPeers = preferSameDomain(sameLevel.filter(item => !isCompleted(item)));
            const target = unplayedPeers[0];
            if (!target) return null;
            const targetDomain = target.domain || 'network';
            const reason = targetDomain === currentDomain
              ? `Ton efficacité est de ${score} %. Continue avec un scénario inédit de niveau ${this.diagLevelLabel(target.level)} dans le domaine ${this.diagDomainLabel(targetDomain)}.`
              : `Ton efficacité est de ${score} %. Les scénarios inédits de niveau ${this.diagLevelLabel(current.level)} dans ${this.diagDomainLabel(currentDomain)} sont épuisés ; élargis le diagnostic au domaine ${this.diagDomainLabel(targetDomain)} au même niveau.`;
            return { id: target.id, title: target.title, replay: false, reason };
          }

          // Au-dessus du seuil, chercher d’abord un scénario inédit au prochain niveau ;
          // un scénario terminé ne doit jamais être repris automatiquement.
          const unplayedHigher = higherLevel.filter(item => !isCompleted(item)).sort((a, b) => {
            const rankA = this.diagLevelRank(a.level);
            const rankB = this.diagLevelRank(b.level);
            if (rankA !== rankB) return rankA - rankB;
            const sameDomainA = (a.domain || 'network') === currentDomain ? 1 : 0;
            const sameDomainB = (b.domain || 'network') === currentDomain ? 1 : 0;
            if (sameDomainA !== sameDomainB) return sameDomainB - sameDomainA;
            return 0; // Preserve the curriculum's declared scenario order.
          });
          const nextLevel = unplayedHigher[0];
          if (nextLevel) {
            const targetDomain = nextLevel.domain || 'network';
            const reason = targetDomain === currentDomain
              ? `Ton efficacité atteint au moins 80 %. Passe au niveau ${this.diagLevelLabel(nextLevel.level)} dans le domaine ${this.diagDomainLabel(targetDomain)}.`
              : `Ton efficacité atteint au moins 80 %. Aucun scénario inédit de niveau supérieur n’est disponible dans ${this.diagDomainLabel(currentDomain)} ; poursuis au niveau ${this.diagLevelLabel(nextLevel.level)} dans le domaine ${this.diagDomainLabel(targetDomain)} pour élargir ton parcours.`;
            return { id: nextLevel.id, title: nextLevel.title, replay: false, reason };
          }

          // Si le niveau supérieur a déjà été exploré, achever d’abord les scénarios inédits
          // du niveau actuel. Si tout a été joué, ne pas tourner en boucle : afficher la fin du parcours.
          const unplayedPeers = preferSameDomain(sameLevel.filter(item => !isCompleted(item)));
          const unplayedPeer = unplayedPeers[0];
          if (!unplayedPeer) return null;
          const targetDomain = unplayedPeer.domain || 'network';
          const reason = targetDomain === currentDomain
            ? `Ton efficacité atteint au moins 80 %. Aucun scénario inédit de niveau supérieur n’est disponible ; explore un autre scénario de niveau ${this.diagLevelLabel(unplayedPeer.level)} dans ${this.diagDomainLabel(targetDomain)}.`
            : `Ton efficacité atteint au moins 80 %. Aucun niveau supérieur inédit n’est disponible ; explore un scénario de niveau ${this.diagLevelLabel(unplayedPeer.level)} dans le domaine ${this.diagDomainLabel(targetDomain)}.`;
          return { id: unplayedPeer.id, title: unplayedPeer.title, replay: false, reason };
        },
        async diagStartNextScenario() {
          const next = this.diagNextScenarioRecommendation();
          if (!next) return;
          if (next.replay) this.diagReset();
          else await this.openDiag(next.id);
        },
        diagSaveProgress() {
          if (!this.diagId || !this.diagData || this.diagFinished) return;
          const progress = {
            stepKey: this.diagKey,
            trail: this.diagTrail,
            startedAt: this.diagRunStartedAt || Date.now(),
            adaptiveQuestion: this.diagAdaptiveQuestion,
            adaptiveResumeKey: this.diagAdaptiveResumeKey,
            adaptiveNextKey: this.diagAdaptiveNextKey,
            adaptiveAttempts: this.diagAdaptiveAttempts,
            adaptiveFeedback: this.diagAdaptiveFeedback,
            updatedAt: new Date().toISOString()
          };
          this.diagProgressMap = { ...this.diagProgressMap, [this.diagId]: progress };
          LS.set('diag-progress', this.diagProgressMap);
        },
        diagCompleteRun() {
          if (!this.diagId) return;
          const id = this.diagId;
          const score = this.diagEfficiency;
          const elapsedSeconds = this.diagElapsedSeconds();
          const result = {
            score,
            correctAnswers: this.diagCorrectCount(),
            decisions: this.diagScoredCount(),
            elapsedSeconds,
            completedAt: new Date().toISOString(),
            outcome: this.diagFinalOutcome(),
            competencies: this.diagCompetencySummary()
          };
          if (score !== null) {
            const best = { ...this.diagDoneMap };
            best[id] = Math.max(Number(best[id]) || 0, score);
            this.diagDoneMap = best;
            LS.set('diag-done', best);
          }
          this.diagResultsMap = { ...this.diagResultsMap, [id]: result };
          LS.set('diag-results', this.diagResultsMap);
          const progress = { ...this.diagProgressMap };
          delete progress[id];
          this.diagProgressMap = progress;
          LS.set('diag-progress', progress);
          this.checkRewards();
        },
        diagChoose(c) {
          const step = this.diagStep;
          const stepKey = this.diagKey;
          const competency = c.competency || (step && step.competency) || (this.diagData && this.diagData.competency) || 'Démarche de dépannage';
          this.diagTrail = [...this.diagTrail, {
            key: stepKey, situation: step ? step.situation : '',
            label: c.label, good: c.good, feedback: c.feedback, competency, decisionType: 'scenario'
          }];
          this.diagCommandInput = '';
          this.diagCommandFeedback = '';
          if (c.good === false && DIAG_REMEDIATION[competency]) {
            this.diagAdaptiveQuestion = DIAG_REMEDIATION[competency];
            this.diagAdaptiveResumeKey = stepKey;
            this.diagAdaptiveNextKey = c.next;
            this.diagAdaptiveAttempts = 0;
            this.diagAdaptiveFeedback = c.feedback || 'Revois l’indice puis réponds à la question de consolidation.';
            this.diagSaveProgress();
            return;
          }
          this.diagKey = c.next;
          if (this.diagFinished) this.diagCompleteRun();
          else this.diagSaveProgress();
        },
        diagChooseAdaptive(choice) {
          const question = this.diagAdaptiveQuestion;
          if (!question || !choice) return;
          this.diagAdaptiveAttempts += 1;
          this.diagTrail = [...this.diagTrail, {
            key: this.diagAdaptiveResumeKey || this.diagKey,
            situation: question.prompt, label: choice.label, good: choice.good === true,
            feedback: choice.feedback || '', competency: question.competency || 'Démarche de dépannage',
            decisionType: 'consolidation'
          }];
          if (choice.good === true) {
            this.diagKey = this.diagAdaptiveResumeKey || this.diagKey;
            this.diagAdaptiveQuestion = null;
            this.diagAdaptiveResumeKey = null;
            this.diagAdaptiveNextKey = null;
            this.diagAdaptiveAttempts = 0;
            this.diagAdaptiveFeedback = '';
            this.diagSaveProgress();
            return;
          }
          this.diagAdaptiveFeedback = (choice.feedback || 'Pas encore. Essaie de nouveau.') + ' Indice : ' + (question.hint || 'Reprends les éléments essentiels de la situation.');
          this.diagSaveProgress();
        },
        diagRetryAdaptive() {
          if (!this.diagAdaptiveQuestion) return;
          this.diagAdaptiveFeedback = this.diagAdaptiveQuestion.hint || 'Relis la situation puis essaie à nouveau.';
        },
        diagContinueAfterSupport() {
          if (!this.diagAdaptiveQuestion) return;
          this.diagKey = this.diagAdaptiveNextKey || this.diagAdaptiveResumeKey || this.diagKey;
          this.diagAdaptiveQuestion = null;
          this.diagAdaptiveResumeKey = null;
          this.diagAdaptiveNextKey = null;
          this.diagAdaptiveAttempts = 0;
          this.diagAdaptiveFeedback = '';
          if (this.diagFinished) this.diagCompleteRun();
          else this.diagSaveProgress();
        },
        diagSubmitCommand() {
          const step = this.diagStep;
          const answer = String(this.diagCommandInput || '').trim();
          if (!step || !step.command || !answer) return;
          let correct = false;
          try { correct = new RegExp(step.command.regex || '^(?!x)x$', 'i').test(answer); } catch (e) {
            this.diagCommandFeedback = 'Le contrôle de cette commande est mal configuré. Reviens aux scénarios et réessaie plus tard.';
            return;
          }
          this.diagChoose({
            label: `Commande saisie : ${answer}`,
            next: correct ? step.next : this.diagKey,
            good: correct,
            feedback: correct ? 'Bonne commande : la vérification peut continuer.' : 'La commande ne correspond pas à la consigne. Il faut afficher la configuration IP avant de poursuivre.',
            commandFeedback: correct ? '' : 'Commande incorrecte. Relis la consigne puis réessaie ; cette tentative apparaîtra dans le bilan.'
          });
        },
        diagBack() {
          if (!this.diagTrail.length || this.diagFinished || this.diagAdaptiveQuestion) return;
          const t = this.diagTrail[this.diagTrail.length - 1];
          this.diagTrail = this.diagTrail.slice(0, -1);
          this.diagKey = t.key;
          this.diagCommandInput = '';
          this.diagCommandFeedback = '';
          this.diagSaveProgress();
        },
        diagReset() {
          if (!this.diagData || !this.diagId) return;
          this.diagKey = this.diagData.start;
          this.diagTrail = [];
          this.diagRunStartedAt = Date.now();
          this.diagCommandInput = '';
          this.diagCommandFeedback = '';
          this.diagAdaptiveQuestion = null;
          this.diagAdaptiveResumeKey = null;
          this.diagAdaptiveNextKey = null;
          this.diagAdaptiveAttempts = 0;
          this.diagAdaptiveFeedback = '';
          this.diagSaveProgress();
        },
        diagClose() {
          if (this.diagData && !this.diagFinished) this.diagSaveProgress();
          this.diagId = null;
          this.diagData = null;
          this.diagTrail = [];
          this.diagKey = null;
          this.diagRunStartedAt = 0;
          this.diagCommandInput = '';
          this.diagCommandFeedback = '';
          this.diagAdaptiveQuestion = null;
          this.diagAdaptiveResumeKey = null;
          this.diagAdaptiveNextKey = null;
          this.diagAdaptiveAttempts = 0;
          this.diagAdaptiveFeedback = '';
        },

        // ---------- mémo (révision espacée de Leitner) ----------
        cardFilter: { module: 'all', level: 'all', mode: 'due' }, reviewNodeId: null, reviewDaysSince: null, cardLoadError: null, flashcardsLoaded: false, flashcardDeckSignature: '', cardBoxes: LS.get('card-boxes', {}), cardSession: { known: 0, unknown: 0, total: 0 },
        cardKey(c) { return c.id || `${c.node_id || ''}|${c.front}`; },
        async loadFlashcards(force = false) {
          if (this.flashcardsLoaded && !force && !this.cardLoadError) {
            if (this.flashcardDeckSignature !== this.cardDeckSignature()) this.buildDeck();
            return;
          }
          this.flashcardsLoading = true;
          this.cardLoadError = null;
          try {
            const r = await fetch('/api/flashcards');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const d = await r.json();
            if (!d || !Array.isArray(d.cards)) {
              throw new Error('Réponse de cartes invalide.');
            }
            this.flashcards = d.cards;
            this.flashcardsLoaded = true;
          } catch (e) {
            this.cardLoadError = 'Les cartes de révision ne peuvent pas être chargées. Vérifie la connexion puis réessaie.';
            console.error('loadFlashcards', e);
          } finally {
            this.flashcardsLoading = false;
            this.buildDeck();
          }
        },
        cardDeckSignature() {
          return JSON.stringify({
            reviewNodeId: this.reviewNodeId == null ? null : String(this.reviewNodeId),
            reviewDaysSince: this.reviewDaysSince == null ? null : Number(this.reviewDaysSince),
            cardFilter: this.cardFilter,
          });
        },
        buildDeck() {
          const signature = this.cardDeckSignature();
          const now = Date.now(); const f = this.cardFilter;
          let cards = this.flashcards.filter(c => {
            if (this.reviewNodeId !== null && this.reviewNodeId !== undefined) {
              return String(c.node_id) === String(this.reviewNodeId);
            }
            const n = this.nodes.find(x => String(x.id) === String(c.node_id));
            if (!n) return f.module === 'all' && f.level === 'all';
            return (f.module === 'all' || this.moduleOf(n) === f.module) && (f.level === 'all' || this.levelOf(n) === f.level);
          });
          // Une révision conseillée par le serveur doit pouvoir revoir toutes les cartes du cours,
          // même si certaines cartes ne sont pas encore dues selon la boîte de Leitner.
          if (!this.reviewNodeId && f.mode === 'due') cards = cards.filter(c => { const b = this.cardBoxes[this.cardKey(c)]; return !b || b.due <= now; });
          for (let i = cards.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [cards[i], cards[j]] = [cards[j], cards[i]]; }
          this.flashcardQueue = cards; this.flashcardFlipped = false; this.cardSession = { known: 0, unknown: 0, total: cards.length };
          this.flashcardDeckSignature = signature;
        },
        clearGuidedReview() {
          this.reviewNodeId = null;
          this.reviewDaysSince = null;
          this.cardFilter = { ...this.cardFilter, module: 'all', level: 'all', mode: 'due' };
          this.buildDeck();
        },
        async openGuidedReviewLesson() {
          const nodeId = this.reviewNodeId;
          if (!nodeId) return;
          this.reviewNodeId = null;
          this.reviewDaysSince = null;
          await this.setTab('tree');
          await this.show(nodeId);
        },
        markFlashcard(known) {
          const c = this.flashcardQueue.shift(); if (!c) return; this.flashcardFlipped = false;
          const k = this.cardKey(c); const b = { ...(this.cardBoxes[k] || { box: 0, due: 0 }) };
          b.box = known ? Math.min(b.box + 1, 5) : 1; b.due = Date.now() + (known ? INTERVALS[b.box] : 0) * 86400000;
          this.cardBoxes = { ...this.cardBoxes, [k]: b }; LS.set('card-boxes', this.cardBoxes);
          if (known) this.cardSession.known++; else { this.cardSession.unknown++; this.flashcardQueue.splice(Math.min(4, this.flashcardQueue.length), 0, c); }
        },
        get cardStats() {
          const now = Date.now(); let nw = 0, due = 0, mastered = 0;
          this.flashcards.forEach(c => { const b = this.cardBoxes[this.cardKey(c)]; if (!b) { nw++; due++; } else { if (b.box >= 4) mastered++; if (b.due <= now) due++; } });
          return { total: this.flashcards.length, nw, due, mastered };
        },
        cardNodeTitle(c) { const n = this.nodes.find(x => x.id === c.node_id); return n ? n.title : ''; },
        resetBoxes() { this.cardBoxes = {}; LS.set('card-boxes', {}); this.buildDeck(); },
      };
    }
  