
    const TOPO_ICONS = {
      router: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="13" width="20" height="8" rx="2"></rect><path d="M6 17h.01M9.5 17h.01"></path><path d="M12 9V3M12 3 9 6M12 3l3 3"></path></svg>',
      switch: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="6" width="20" height="12" rx="2"></rect><path d="M6 10h6M6 14h6"></path><path d="M16 10h2M16 14h2"></path></svg>',
      pc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="4" width="18" height="12" rx="2"></rect><path d="M8 20h8M12 16v4"></path></svg>',
      firewall: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="1.5"></rect><path d="M3 10h18M3 15h18M8 5v5M16 10v5M8 15v4"></path></svg>',
      server: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="8" rx="2"></rect><rect x="3" y="13" width="18" height="8" rx="2"></rect><path d="M7 7h.01M7 17h.01M11 7h6M11 17h6"></path></svg>',
      cloud: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 18h10a4 4 0 0 0 .5-7.97A6 6 0 0 0 6.2 8.4 4.8 4.8 0 0 0 7 18Z"></path></svg>',
      vpc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2.5" y="4" width="19" height="16" rx="2" stroke-dasharray="3 2"></rect><path d="M6.5 8.5h4v3h-4zM13.5 12.5h4v3h-4zM10.5 10h3M9 11.5v3M13.5 14h-2.5"></path></svg>',
      subnet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="4" width="18" height="6" rx="1.5"></rect><rect x="3" y="14" width="18" height="6" rx="1.5"></rect><path d="M7 7h10M7 17h10"></path></svg>',
      wifi: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 9a14 14 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15a4.5 4.5 0 0 1 6 0"></path><circle cx="12" cy="19" r="1"></circle></svg>',
      laptop: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="4" width="14" height="12" rx="1.5"></rect><path d="M2.5 20h19l-2-4h-15l-2 4Z"></path></svg>',
      spine: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="4" width="20" height="6" rx="1"></rect><path d="M6 7h.01M10 7h.01"></path><path d="M6 14v6M18 14v6"></path><circle cx="6" cy="14" r="2"></circle><circle cx="18" cy="14" r="2"></circle></svg>',
      leaf: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="10" width="20" height="8" rx="1"></rect><path d="M6 14h.01M10 14h.01"></path><path d="M6 6v4M18 6v4"></path><circle cx="6" cy="6" r="2"></circle><circle cx="18" cy="6" r="2"></circle></svg>',
      apic: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="3" width="16" height="18" rx="2"></rect><circle cx="12" cy="8" r="2"></circle><path d="M8 14h8M8 17h8"></path></svg>',
      plc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="3" width="16" height="18" rx="2"></rect><path d="M8 7h8M8 11h8M8 15h4"></path><circle cx="17" cy="17" r="1"></circle></svg>',
    };

    function skilltreeBase() {
      return {
        socket: null,
        showUpdateToast: false,
        profileMenuOpen: false, profileDraft: '',
        theme: document.documentElement.classList.contains('light') ? 'light' : 'dark',
        focusMode: false, treeFilter: 'all', sidebarCollapsed: false,
        compactUi: false, reduceMotion: false,
        notificationsOpen: false, settingsMenuOpen: false,
        // Résoudre la destination dès la création de l’état Alpine pour éviter un flash du tableau de bord.
        tab: (() => {
          const requested = new URLSearchParams(window.location.search).get('openTab');
          return NAV_ITEMS.some(item => item.id === requested) ? requested : 'tree';
        })(),
        tabHistory: [],
        userName: localStorage.getItem('skilltree-name') || 'Ton Nom',
        lastOpenedNodeId: localStorage.getItem('skilltree-last-node') || '',
        lastOpenedNodeStatus: localStorage.getItem('skilltree-last-status') || '',
        lastLessonProgress: Math.max(0, Math.min(100, Number(localStorage.getItem('skilltree-last-progress') || 0) || 0)),
        favoriteNodeIds: [],
        nodes: [], total: 0, validated: 0, loading: true, treeError: null, streakDays: 0, streakLoaded: false,
        dashboardDataErrors: { userStats: null, streak: null, dailyPlan: null, stats: null },
        userStats: { total_xp: 0, current_level: 1, level_name: 'Débutant', progress_percent: 0, coins: 0 }, userStatsLoaded: false,
        shopOpen: false, shopItems: [], open: false,
        detail: null, detailLoading: false, detailLoadError: null, detailRequestedNodeId: null, _detailRequestId: 0, modalTab: 'lesson', isFullscreen: false,
        learningProgress: null, learningProgressError: '', _learningProgressTimer: null, _learningProgressNodeId: '', _learningProgressBusy: false,
        lessonHtml: '', lessonMissing: false, lessonIsPlaceholder: false,

        // --- Lecteur de cours ---
        fontSize: 17,
        readingWidth: 'comfortable',
        lessonToc: [], activeSection: '', lessonProgress: 0, readingMinutes: 1,
        lessonPositions: {}, startSectionSelection: '__resume__', readingContextMenu: { open: false, x: 0, y: 0, targetId: '', sectionId: '__top__', targetLabel: 'Début du cours' }, readingStartCounter: 0, _lessonHeadingOffsets: [], _lessonHeadingCourseId: '', _lessonHeadingObserver: null, _lessonHeadingRefreshFrame: 0, _mermaidInitialized: false,

        quiz: null, quizAnswers: [], quizResult: null, quizBusy: false,
        exerciseMode: null, exerciseQuestion: null, exerciseAnswer: '', exerciseResult: null, exerciseBusy: false, exerciseError: null, exercisePreferredKind: null,

        labId: null, labBusy: false, labRunning: false, labOutput: [], labCommand: '', labValidation: null, labError: null,

        tutorOpen: false, tutorQuestion: '', tutorMessages: [], tutorBusy: false, tutorSelectedText: '',
        tutorSize: (['compact', 'normal', 'large'].includes(localStorage.getItem('skilltree-tutor-size')) ? localStorage.getItem('skilltree-tutor-size') : 'normal'),
        speechState: 'idle', speechKind: null, speechEngine: null, speechRate: 1, speechQueue: [], speechQueueIndex: 0,
        speechError: null, _speechRunId: 0, _speechAudioUrls: {}, _speechAudioRequests: {}, _speechLoadedIndex: -1, _browserSpeechUtterance: null,
        dailyPlan: [], stats: null, statsLoading: false, statsLoaded: false, flashcards: [], flashcardQueue: [], flashcardsLoading: false, flashcardFlipped: false,

        diagnostic: null, diagnosticStep: null,
        exam: null, examAnswers: [], examResult: null, examBusy: false, examCategory: '',

        devices: [
          { type: 'router', label: 'Routeur', hint: 'L3', icon: TOPO_ICONS.router },
          { type: 'switch', label: 'Switch', hint: 'L2', icon: TOPO_ICONS.switch },
          { type: 'pc', label: 'PC', hint: 'Terminal', icon: TOPO_ICONS.pc },
          { type: 'firewall', label: 'Firewall', hint: 'Sécurité', icon: TOPO_ICONS.firewall },
          { type: 'server', label: 'Serveur', hint: 'Services', icon: TOPO_ICONS.server },
          { type: 'plc', label: 'Automate industriel', hint: 'OT', icon: TOPO_ICONS.plc },
          { type: 'cloud', label: 'Cloud', hint: 'Externe', icon: TOPO_ICONS.cloud },
        ],
        topologyEditor: null, topologyReady: false,

        async init() {
          this.loadLessonPositions();
          this.$watch('modalTab', (value, previous) => {
            const nodeId = String(this._learningProgressNodeId || '');
            if (!nodeId || !this.open) return;
            if ((previous === 'lesson' && value !== 'lesson') || (value === 'lesson' && previous !== 'lesson')) {
              void this.syncLearningProgress(nodeId, { force: true });
            }
          });
          this.loadUiPrefs();
          this.loadFavorites();
          this.loadWarOpenCount();
          if (this._warOpenCountTimer) clearInterval(this._warOpenCountTimer);
          this._warOpenCountTimer = window.setInterval(() => { if (this.tab === 'war') this.loadWarOpenCount(); }, 5000);
          window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            const message = event.data;
            if (message && message.type === 'lab:submit-result' && message.detail) {
              this.onLabValidated(message.detail);
              // Le workspace peut valider un cours dans un autre onglet :
              // synchroniser l'arbre et les recommandations dès le retour du résultat.
              this.refreshAll();
            } else if (message && message.type === 'war-room:ticket-validated') {
              this.notify(message.detail?.message || '✅ Ticket validé. Termine le post-mortem pour le clôturer.');
            } else if (message && message.type === 'war-room:ticket-resolved') {
              const xp = Number(message.detail?.xp_earned) || 0;
              this.notify('🏁 Ticket clôturé.' + (xp > 0 ? ' +' + xp + ' XP gagnés.' : ''));
              this.refreshAll();
            }
          });
          // Lancer les appels de données sans retarder le rendu initial ni la navigation vers la section demandée.
          const refreshTask = this.refreshAll().catch(error => {
            console.error('Chargement initial des données', error);
            return null;
          });
          this.examCategory = this.examCategories[0]?.name || '';
          this.connectWebSocket();
          const requestedUrl = new URL(window.location.href);
          const requestedLabId = requestedUrl.searchParams.get('openLab');
          const requestedCourseId = requestedUrl.searchParams.get('openCourse');
          const requestedModuleId = requestedUrl.searchParams.get('openModule');
          const requestedTabId = requestedUrl.searchParams.get('openTab');
          if (requestedLabId || requestedCourseId || requestedModuleId || requestedTabId) {
            ['openLab', 'openCourse', 'openModule', 'openTab'].forEach(key => requestedUrl.searchParams.delete(key));
            const cleanUrl = requestedUrl.pathname + requestedUrl.search + requestedUrl.hash;
            try { window.history.replaceState(window.history.state, '', cleanUrl); } catch (_) { }
          }

          if (requestedTabId && this.navItems.some(item => item.id === requestedTabId)) {
            // Afficher la section tout de suite ; son contenu peut se charger pendant les autres requêtes.
            const tabTask = this.setTab(requestedTabId, { skipHistory: true, forceLoad: true });
            if (requestedTabId === 'labs') {
              // Le catalogue v2 démarre immédiatement. Une fois l'arbre disponible, compléter les labs historiques.
              Promise.all([refreshTask, tabTask]).then(async () => {
                if (this.tab !== requestedTabId) return;
                if (this.labIndexTask) await this.labIndexTask;
                return this.loadLabIndex();
              }).catch(error => console.error('Chargement différé des Labs', error));
            }
          }

          if (requestedModuleId || requestedCourseId) {
            refreshTask.then(async () => {
              if (requestedModuleId && (requestedModuleId === 'all' || this.modules.some(module => module.id === requestedModuleId))) {
                await this.setTab('tree');
                await this.setModule(requestedModuleId);
              }
              if (requestedCourseId) {
                await this.setTab('tree');
                await this.show(requestedCourseId);
              }
            }).catch(error => console.error('Ouverture du parcours demandé', error));
          }
          if (requestedLabId) {
            // L'API du lab est indépendante du chargement des statistiques du tableau de bord.
            this.openLab(requestedLabId, false);
          }
        },

        // --- Préférences d'affichage du lecteur et préférences générales ---
        loadUiPrefs() {
          try {
            const p = JSON.parse(localStorage.getItem('skilltree-ui') || '{}');
            if (p.fs) this.fontSize = Math.min(22, Math.max(14, Number(p.fs) || 17));
            if (p.readingWidth === 'comfortable' || p.readingWidth === 'wide') this.readingWidth = p.readingWidth;
            this.isFullscreen = !!p.full;
          } catch (_) { }
          try {
            const p = JSON.parse(localStorage.getItem('skilltree-settings-v1') || '{}');
            this.compactUi = p.compactUi === true;
            this.reduceMotion = p.reduceMotion === true;
          } catch (_) {
            this.compactUi = false;
            this.reduceMotion = false;
          }
          this.applySettingsPrefs();
        },
        saveUiPrefs() {
          try { localStorage.setItem('skilltree-ui', JSON.stringify({ fs: this.fontSize, full: this.isFullscreen, readingWidth: this.readingWidth })); } catch (_) { }
        },
        applySettingsPrefs() {
          document.documentElement.classList.toggle('reduce-motion', !!this.reduceMotion);
        },
        saveSettingsPrefs() {
          this.applySettingsPrefs();
          try {
            localStorage.setItem('skilltree-settings-v1', JSON.stringify({
              compactUi: !!this.compactUi,
              reduceMotion: !!this.reduceMotion,
            }));
          } catch (_) { }
        },
        resetDisplayPreferences() {
          this.fontSize = 17;
          this.readingWidth = 'comfortable';
          this.isFullscreen = false;
          this.compactUi = false;
          this.reduceMotion = false;
          this.saveUiPrefs();
          this.saveSettingsPrefs();
          if (typeof this.setTheme === 'function') this.setTheme('graphite');
          this.settingsMenuOpen = false;
          if (typeof this.notify === 'function') this.notify('Préférences d’affichage rétablies.');
        },
        loadLessonPositions() {
          try {
            const stored = JSON.parse(localStorage.getItem('skilltree-lesson-positions') || '{}');
            this.lessonPositions = stored && typeof stored === 'object' && !Array.isArray(stored) ? stored : {};
          } catch (_) {
            this.lessonPositions = {};
          }
        },
        saveLessonPosition(nodeId, position) {
          const key = String(nodeId || '');
          if (!key || !position || typeof position !== 'object') return;
          const previous = this.lessonPositions[key] && typeof this.lessonPositions[key] === 'object'
            ? this.lessonPositions[key]
            : {};
          this.lessonPositions = { ...(this.lessonPositions || {}), [key]: { ...previous, ...position } };
          try {
            localStorage.setItem('skilltree-lesson-positions', JSON.stringify(this.lessonPositions));
          } catch (_) { /* La reprise reste une amélioration facultative du navigateur. */ }
        },
        restoreLessonPosition(container, savedPosition = null) {
          if (!container) return;
          const nodeId = String(this.detail?.id || '');
          const saved = savedPosition || this.lessonPositions[nodeId] || null;
          const goToHeading = (headingId, extraOffset = 0) => {
            if (!headingId) return false;
            const wantedId = String(headingId);
            const heading = Array.from(container.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]'))
              .find(element => element.id === wantedId);
            if (!heading) return false;
            const top = heading.getBoundingClientRect().top - container.getBoundingClientRect().top + container.scrollTop;
            container.scrollTop = Math.max(0, top + Math.max(0, Number(extraOffset) || 0));
            return true;
          };

          if (this.startSectionSelection === '__top__') {
            container.scrollTop = 0;
          } else if (this.startSectionSelection && this.startSectionSelection !== '__resume__') {
            if (!goToHeading(this.startSectionSelection)) {
              this.speechError = 'La section choisie est introuvable. Sélectionne une autre section ou le début du cours.';
              this.notify(this.speechError);
              return;
            }
          } else if (saved && saved.sectionId && goToHeading(saved.sectionId, saved.sectionOffset)) {
            // La section mémorisée reste prioritaire quand la longueur du cours a changé.
          } else if (saved && Number.isFinite(Number(saved.scrollTop))) {
            container.scrollTop = Math.max(0, Number(saved.scrollTop));
          } else {
            const legacyProgress = nodeId === String(this.lastOpenedNodeId || '') ? this.lastLessonProgress : 0;
            const progress = saved && Number.isFinite(Number(saved.progress))
              ? Math.max(0, Math.min(100, Number(saved.progress)))
              : legacyProgress;
            const max = Math.max(0, container.scrollHeight - container.clientHeight);
            container.scrollTop = Math.round(max * progress / 100);
          }
          this.onLessonScroll({ target: container });
        },
        startLessonAtSelection() {
          const container = this.$refs.modalScroll;
          if (!container) return;
          const position = this.lessonPositions[String(this.detail?.id || '')] || null;
          this.restoreLessonPosition(container, position);
        },
        closeReadingContextMenu() {
          if (this.readingContextMenu?.open) this.readingContextMenu = { ...this.readingContextMenu, open: false };
        },
        openReadingContextMenu(event) {
          const article = this.$refs.lessonArticle;
          const source = event.target instanceof Element ? event.target : event.target?.parentElement;
          if (!article || !source || !article.contains(source) || this.modalTab !== 'lesson') {
            this.closeReadingContextMenu();
            return;
          }
          if (source.closest('a, button, input, select, textarea, pre, code, table, svg, video, audio, .lesson-diagram-toolbar, .no-speech')) {
            this.closeReadingContextMenu();
            return;
          }
          const block = source.closest('h1, h2, h3, h4, h5, h6, p, li, blockquote, figcaption, dd, dt');
          if (!block || !article.contains(block)) {
            this.closeReadingContextMenu();
            return;
          }
          event.preventDefault();
          const headingSelector = 'h1, h2, h3, h4, h5, h6';
          const headings = Array.from(article.querySelectorAll(headingSelector)).filter(heading => heading.id);
          const isHeading = /^H[1-6]$/.test(block.tagName);
          const precedingHeading = isHeading
            ? block
            : headings.filter(heading => (heading.compareDocumentPosition(block) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0).pop();
          const sectionId = precedingHeading && precedingHeading.id ? precedingHeading.id : '__top__';

          // Marquer le bloc exact cliqué. Le titre de section reste séparé : il sert à la progression,
          // tandis que le marqueur du bloc détermine le premier texte effectivement prononcé.
          this.readingStartCounter = (Number(this.readingStartCounter) || 0) + 1;
          const targetId = 'reading-start-' + this.readingStartCounter;
          block.setAttribute('data-speech-start-id', targetId);
          const targetLabel = String(block.innerText || block.textContent || '')
            .replace(/\s+/gu, ' ').trim().slice(0, 100) || 'Point sélectionné';
          const panel = article.closest('[role="dialog"]');
          const bounds = panel ? panel.getBoundingClientRect() : { left: 0, top: 0, width: window.innerWidth, height: window.innerHeight };
          const menuWidth = 252;
          const menuHeight = 112;
          const x = Math.max(8, Math.min(event.clientX - bounds.left, bounds.width - menuWidth - 8));
          const y = Math.max(8, Math.min(event.clientY - bounds.top, bounds.height - menuHeight - 8));
          this.readingContextMenu = { open: true, x, y, targetId, sectionId, targetLabel };
        },
        startReadingFromContextMenu() {
          const targetId = this.readingContextMenu?.targetId || '';
          const sectionId = this.readingContextMenu?.sectionId || '__top__';
          this.closeReadingContextMenu();
          if (!this.open || !this.$refs.lessonArticle || !targetId) return;

          const article = this.$refs.lessonArticle;
          const target = Array.from(article.querySelectorAll('[data-speech-start-id]'))
            .find(element => element.getAttribute('data-speech-start-id') === targetId);
          if (!target) {
            this.speechError = 'Le point choisi n’est plus disponible. Sélectionne une autre section.';
            this.notify(this.speechError);
            return;
          }

          this.startSectionSelection = sectionId;
          const container = this.$refs.modalScroll;
          if (container) {
            const top = target.getBoundingClientRect().top - container.getBoundingClientRect().top + container.scrollTop;
            container.scrollTop = Math.max(0, top - 20);
            this.onLessonScroll({ target: container });
          }
          this.startSpeech(this.speechTextFromArticle(targetId), 'lesson');
        },
        changeFontSize(delta) {
          this.fontSize = Math.min(22, Math.max(14, this.fontSize + delta));
          this.saveUiPrefs();
        },
        toggleReadingWidth() {
          this.readingWidth = this.readingWidth === 'wide' ? 'comfortable' : 'wide';
          this.saveUiPrefs();
          this.$nextTick(() => {
            this.fixLessonContrast();
            const scroll = this.$refs.modalScroll;
            if (scroll) this.onLessonScroll({ target: scroll });
          });
        },
        toggleFullscreen() {
          this.isFullscreen = !this.isFullscreen;
          this.saveUiPrefs();
        },
        onEscape() {
          if (this.readingContextMenu?.open) { this.closeReadingContextMenu(); return; }
          if (!this.open) return;
          if (this.isFullscreen) { this.isFullscreen = false; this.saveUiPrefs(); return; }
          this.close();
        },

        connectWebSocket() {
          // On force 127.0.0.1 pour éviter les conflits localhost / 127.0.0.1
          const host = window.location.host.includes('localhost') ? '127.0.0.1:8000' : window.location.host;
          const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
          const wsUrl = `${protocol}//${host}/api/ws`;

          this.socket = new WebSocket(wsUrl);

          this.socket.onmessage = (event) => {
            if (event.data === "update") {
              console.log("🔄 Mise à jour reçue du serveur !");
              this.refreshAll();
              this.showUpdateToast = true;
              setTimeout(() => { this.showUpdateToast = false; }, 4000);
            }
          };

          this.socket.onclose = () => {
            console.log("WebSocket déconnecté. Nouvelle tentative dans 5 secondes...");
            setTimeout(() => this.connectWebSocket(), 5000);
          };
        },
        async refreshAll() {
          const resumeIdBeforeRefresh = String(this.lastOpenedNodeId || '');
          const resumeStatusBeforeRefresh = this.lastOpenedNodeStatus
            || (this.lastOpenedNodeId ? localStorage.getItem('skilltree-last-status') || '' : '');
          await Promise.all([this.loadTree(), this.loadDailyPlan(), this.loadStreak(), this.loadUserStats(), this.loadDiplomas()]);

          // Détecte aussi une validation faite dans un autre onglet, pendant que
          // le tableau de bord était fermé, ou par un mécanisme autre que le quiz.
          if (resumeIdBeforeRefresh && String(this.lastOpenedNodeId || '') === resumeIdBeforeRefresh) {
            const resumeNodeAfterRefresh = this.nodes.find(node => String(node.id) === resumeIdBeforeRefresh);
            if (
              resumeNodeAfterRefresh?.status === 'validated'
              && resumeStatusBeforeRefresh !== 'validated'
              && !this.allNodesValidated
            ) {
              this.clearResumeTargetAfterValidation(resumeIdBeforeRefresh);
            } else if (resumeNodeAfterRefresh) {
              this.lastOpenedNodeStatus = resumeNodeAfterRefresh.status;
              try { localStorage.setItem('skilltree-last-status', resumeNodeAfterRefresh.status); } catch (e) { }
            }
          }

          if (this.checkRewards) this.checkRewards();
          return {
            tree: !this.treeError,
            dailyPlan: !this.dashboardDataErrors.dailyPlan,
            userStats: !this.dashboardDataErrors.userStats,
            streak: !this.dashboardDataErrors.streak,
          };
        },
        async retryDashboardData() {
          await Promise.all([this.refreshAll(), this.loadStats(true)]);
        },

        editProfile() {
          this.profileDraft = this.userName;
          this.notificationsOpen = false; this.settingsMenuOpen = false; this.themeMenuOpen = false;
          this.profileMenuOpen = !this.profileMenuOpen;
        },
        saveProfile() {
          const name = (this.profileDraft || '').trim();
          if (name) {
            this.userName = name;
            try { localStorage.setItem('skilltree-name', name); } catch (e) { }
          }
          this.profileMenuOpen = false;
        },

        exportData() {
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
            schemaVersion: 1,
            exportedAt: new Date().toISOString(),
            preferences: {
              theme: this.activeThemeId || document.documentElement.dataset.theme || 'graphite',
              fontSize: this.fontSize,
              readingWidth: this.readingWidth,
              compactUi: !!this.compactUi,
              reduceMotion: !!this.reduceMotion,
            },
            progress: {
              lastOpenedNodeId: this.lastOpenedNodeId || '',
              lastOpenedNodeStatus: this.lastOpenedNodeStatus || '',
              lastLessonProgress: Number(this.lastLessonProgress) || 0,
            },
            localData,
          };
          const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json;charset=utf-8' });
          const name = 'skilltree-sauvegarde-' + new Date().toISOString().slice(0, 10) + '.json';
          this.saveFile(name, blob);
          if (typeof this.notify === 'function') this.notify('Sauvegarde JSON téléchargée.');
          return snapshot;
        },
        reloadContent() { this.refreshAll(); },
        toggleTheme() { this.theme = this.theme === 'dark' ? 'light' : 'dark'; document.documentElement.classList.toggle('dark', this.theme === 'dark'); },

        goBackTab() {
          const previous = this.tabHistory.pop();
          const target = previous && previous !== this.tab ? previous : 'tree';
          return this.setTab(target, { skipHistory: true });
        },

        async setTab(name, options = {}) {
          const tabChanged = name !== this.tab;
          if (tabChanged) {
            if (!options.skipHistory) {
              if (name === 'tree') {
                this.tabHistory = [];
              } else {
                this.tabHistory.push(this.tab);
                if (this.tabHistory.length > 30) this.tabHistory.shift();
              }
            }
            this.tab = name;
          }
          this.notificationsOpen = false; this.settingsMenuOpen = false; this.profileMenuOpen = false;
          // Un clic sur l’onglet déjà actif ne doit pas interrompre la lecture en cours.
          // forceLoad permet d'initialiser son contenu si l'onglet venait de l'URL.
          if (!tabChanged && !options.forceLoad) return;
          if (tabChanged) {
            this.$nextTick(() => {
              const m = this.$refs.mainScroll;
              if (!m) return;
              if (this.reduceMotion || typeof m.scrollTo !== 'function') m.scrollTop = 0;
              else m.scrollTo({ top: 0, behavior: 'smooth' });
            });
          }
          try {
            if (name === 'stats') await this.loadStats();
            if (name === 'memo') await this.loadFlashcards();
            if (name === 'diagnostic') await this.loadDiagnostic();
            if (name === 'labs') await this.loadLabIndex();
            if (name === 'war') await this.loadTickets();
            if (name === 'rewards') this.checkRewards();
          } catch (e) { console.error('setTab', name, e); }
        },

        openExamCenter() {
          // Le centre est local : forcer son activation même si l'onglet est déjà sélectionné.
          const navigation = this.setTab('exam', { forceLoad: true });
          this.$nextTick(() => {
            if (this.tab !== 'exam') return;
            const section = document.getElementById('exam-center');
            const heading = section && section.querySelector('h2');
            if (heading) {
              heading.setAttribute('tabindex', '-1');
              heading.focus({ preventScroll: true });
            }
          });
          return navigation;
        },

        loadFavorites() {
          try {
            const saved = JSON.parse(localStorage.getItem('skilltree-favorites') || '[]');
            this.favoriteNodeIds = Array.isArray(saved) ? [...new Set(saved.map(String))] : [];
          } catch (e) {
            this.favoriteNodeIds = [];
          }
        },
        isFavorite(nodeId) {
          return !!nodeId && this.favoriteNodeIds.includes(String(nodeId));
        },
        toggleFavorite(nodeId) {
          if (!nodeId) return;
          const id = String(nodeId);
          this.favoriteNodeIds = this.isFavorite(id)
            ? this.favoriteNodeIds.filter(value => value !== id)
            : [...this.favoriteNodeIds, id];
          try { localStorage.setItem('skilltree-favorites', JSON.stringify(this.favoriteNodeIds)); } catch (e) { }
        },
        get favoriteCount() {
          return this.nodes.filter(n => this.isFavorite(n.id)).length;
        },

        async loadTree() {
          const hadNodes = this.nodes.length > 0;
          this.loading = true;
          this.treeError = null;
          try {
            const r = await fetch('/api/tree');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const d = await r.json();
            if (!d || !Array.isArray(d.nodes)) throw new Error('Réponse /api/tree invalide : le tableau nodes est absent.');
            this.nodes = d.nodes;
            this.total = Number.isInteger(d.total) && d.total >= 0 ? d.total : d.nodes.length;
            this.validated = Number.isInteger(d.validated) && d.validated >= 0
              ? d.validated
              : d.nodes.filter(node => node.status === 'validated').length;
          } catch (e) {
            this.treeError = hadNodes
              ? 'Actualisation du parcours impossible. Les données précédentes restent affichées.'
              : "Impossible de charger le parcours. Vérifie que l’API Skill-Tree est disponible, puis réessaie.";
            console.error('loadTree', e);
          } finally {
            this.loading = false;
          }
        },
        async loadUserStats() {
          try {
            const r = await fetch('/api/user-stats');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            if (!data || !Number.isFinite(data.total_xp) || !Number.isFinite(data.coins) || !Number.isFinite(data.current_level)) {
              throw new Error('Réponse de statistiques utilisateur invalide.');
            }
            this.userStats = data;
            this.userStatsLoaded = true;
            this.dashboardDataErrors.userStats = null;
          } catch (e) {
            this.dashboardDataErrors.userStats = 'XP, niveau et pièces : données du compte indisponibles.';
            console.error('loadUserStats', e);
          }
        },
        async loadStreak() {
          try {
            const r = await fetch('/api/streak');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            if (!data || !Number.isInteger(data.days) || data.days < 0) throw new Error('Réponse de série quotidienne invalide.');
            this.streakDays = data.days;
            this.streakLoaded = true;
            this.dashboardDataErrors.streak = null;
          } catch (e) {
            this.dashboardDataErrors.streak = 'Série quotidienne : historique indisponible.';
            console.error('loadStreak', e);
          }
        },
        async loadDailyPlan() {
          try {
            const r = await fetch('/api/daily-plan');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            if (!data || !Array.isArray(data.actions)) throw new Error('Réponse de plan quotidien invalide.');
            this.dailyPlan = data.actions;
            this.dashboardDataErrors.dailyPlan = null;
          } catch (e) {
            this.dashboardDataErrors.dailyPlan = 'Plan quotidien : les recommandations n’ont pas pu être actualisées.';
            console.error('loadDailyPlan', e);
          }
        },
        async loadStats(force = false) {
          if (this.statsLoaded && !force && !this.dashboardDataErrors.stats) {
            this.$nextTick(() => this.renderSpiderChart());
            return;
          }
          this.statsLoading = true;
          try {
            const r = await fetch('/api/stats');
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            if (!data || !data.totals || !Array.isArray(data.categories)) throw new Error('Réponse de statistiques de progression invalide.');
            this.stats = data;
            this.statsLoaded = true;
            this.dashboardDataErrors.stats = null;
          } catch (e) {
            this.dashboardDataErrors.stats = 'Statistiques de progression : données indisponibles.';
            console.error('loadStats', e);
          } finally {
            this.statsLoading = false;
            this.$nextTick(() => this.renderSpiderChart());
          }
        },
        async loadFlashcards() {
          this.flashcardsLoading = true;
          try { const r = await fetch('/api/flashcards'); const d = await r.json(); this.flashcards = d.cards || []; this.flashcardQueue = this.flashcards.slice(); } catch(e) {}
          this.flashcardsLoading = false;
        },
        async loadDiagnostic() {
          try { const r = await fetch('/api/diagnostics/network_down'); this.diagnostic = await r.json(); this.diagnosticStep = this.diagnostic.steps[this.diagnostic.start]; } catch(e){}
        },

        async loadWarOpenCount() {
          try {
            const response = await fetch('/api/tickets/open-count', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => ({}));
            if (response.ok) this.warOpenTicketCount = Math.max(0, Number(payload.count) || 0);
          } catch (_) { /* Le compteur sera retenté au prochain cycle. */ }
        },
        async loadWarBadges() {
          this.warBadgesLoading = true; this.warBadgesError = '';
          try {
            const response = await fetch('/api/tickets/badges', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => []);
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warBadges = Array.isArray(payload) ? payload : [];
          } catch (error) { this.warBadgesError = 'Impossible de charger les badges : ' + error.message; }
          finally { this.warBadgesLoading = false; }
        },
        async loadWarWeeklyReport() {
          this.warWeeklyLoading = true; this.warWeeklyError = '';
          try {
            const response = await fetch('/api/itsm/weekly-report', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warWeeklyReport = payload;
          } catch (error) { this.warWeeklyError = 'Impossible de charger le rapport hebdomadaire : ' + error.message; }
          finally { this.warWeeklyLoading = false; }
        },
        weeklyResolvedHeight(day) {
          const days = this.warWeeklyReport?.daily_breakdown || [];
          const maxCount = Math.max(1, ...days.map(item => Number(item.resolved) || 0));
          const count = Math.max(0, Number(day?.resolved) || 0);
          return count ? Math.max(8, Math.round(count / maxCount * 100)) : 2;
        },
        weeklyTicketHeight(day, metric) {
          const days = this.warWeeklyReport?.daily_breakdown || [];
          const maxCount = Math.max(1, ...days.flatMap(item => [Number(item.opened) || 0, Number(item.resolved) || 0]));
          const count = Math.max(0, Number(day?.[metric]) || 0);
          return count ? Math.max(8, Math.round(count / maxCount * 100)) : 2;
        },
        formatWeeklyDay(value) {
          if (!value) return '—';
          const d = new Date(String(value) + 'T12:00:00Z');
          return Number.isNaN(d.getTime()) ? String(value).slice(5) : d.toLocaleDateString('fr-FR', { weekday: 'short', timeZone: 'UTC' });
        },
        exportWarWeeklyReport() {
          const r = this.warWeeklyReport;
          if (!r) { this.notify('Le rapport hebdomadaire n’est pas encore chargé.'); return; }
          const lines = [
            '# Rapport de performance hebdomadaire — War Room', '',
            '**Période :** ' + r.period_start + ' → ' + r.period_end, '',
            '## Indicateurs', '',
            '- Tickets ouverts : ' + r.tickets_opened,
            '- Tickets résolus : ' + r.tickets_resolved,
            '- Tickets échoués : ' + r.tickets_failed,
            '- MTTR : ' + r.mttr_minutes + ' min',
            '- Conformité SLA : ' + r.sla_compliance_pct + ' %',
            '- Type le plus traité : ' + (r.top_scenario_type || 'Aucun'), '',
            '## Records personnels', '',
            '- Résolution la plus rapide : ' + (r.fastest_ticket_id ? r.fastest_ticket_id + ' — ' + r.fastest_resolution_minutes + ' min' : 'Aucune résolution sur la période'),
            '- Résolution la plus lente : ' + (r.slowest_ticket_id ? r.slowest_ticket_id + ' — ' + r.slowest_resolution_minutes + ' min' : 'Aucune résolution sur la période'),
            '- Meilleur SLA : ' + (r.best_sla ? r.best_sla.ticket_id + ' — marge de ' + r.best_sla.margin_minutes + ' min' : 'Aucun ticket avec SLA respecté'), '',
            '## Détail journalier', '',
            '| Date | Ouverts | Résolus | Échoués |',
            '|---|---:|---:|---:|',
            ...(r.daily_breakdown || []).map(day => '| ' + day.date + ' | ' + day.opened + ' | ' + day.resolved + ' | ' + day.failed + ' |'), ''
          ].join('\n');
          this.saveFile('rapport-war-room-hebdomadaire.md', new Blob([lines], { type: 'text/markdown;charset=utf-8' }));
        },
        async launchWarStressTest() {
          if (this.warStressBusy) return;
          if (this.warStressMission?.status === 'in_progress') {
            this.warStressNotice = 'Un stress test est déjà en cours. Termine les trois tickets actifs avant d’en lancer un autre.';
            return;
          }
          this.warStressBusy = true; this.warStressNotice = ''; this.warError = '';
          try {
            const response = await fetch('/api/tickets/stress-test', {
              method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warStressMission = { ...payload, status: 'in_progress' };
            this.warStressNotice = payload.message || '3 incidents simultanés. Tu as 45 minutes pour tous les résoudre. Bon courage !';
            this.warTab = 'inbox'; this.warFilter = 'all';
            await this.loadTickets();
            if (this._warStressPollTimer) clearInterval(this._warStressPollTimer);
            this._warStressPollTimer = window.setInterval(() => this.refreshWarStressMission(), 15000);
            await this.refreshWarStressMission();
          } catch (error) { this.warStressNotice = 'Impossible de lancer le stress test : ' + error.message; }
          finally { this.warStressBusy = false; }
        },
        async refreshWarStressMission() {
          const mission = this.warStressMission;
          if (!mission?.mission_id) return;
          try {
            const response = await fetch('/api/itsm/stress-test/' + encodeURIComponent(mission.mission_id), { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warStressMission = { ...mission, ...payload };
            if (payload.status === 'succeeded') {
              this.warStressNotice = '🏆 Mission Stress Test réussie : ' + payload.resolved + '/' + payload.total + ' tickets résolus. Bonus XP x2 appliqué aux clôtures faites dans le délai.';
              if (this._warStressPollTimer) clearInterval(this._warStressPollTimer);
              this.loadTickets(); this.loadWarOpenCount();
            } else if (payload.status === 'failed') {
              this.warStressNotice = '❌ Mission Stress Test échouée : ' + payload.resolved + '/' + payload.total + ' tickets résolus dans les 45 minutes.';
              if (this._warStressPollTimer) clearInterval(this._warStressPollTimer);
              this.loadTickets(); this.loadWarOpenCount();
            }
          } catch (error) { this.warStressNotice = 'Suivi du stress test indisponible : ' + error.message; }
        },
        async loadItSMStats() {
          this.warLiveLoading = true; this.warStatsError = '';
          try {
            const response = await fetch('/api/itsm/stats', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warStats = { mttr_minutes: 0, sla_compliance_pct: 0, total_resolved: 0, total_failed: 0, incidents_today: 0, recent_resolved: [], ...payload };
          } catch (error) { this.warStatsError = 'Impossible de charger les KPI ITSM : ' + error.message; }
          finally { this.warLiveLoading = false; }
        },
        async loadWarArchive() {
          this.warArchiveLoading = true; this.warArchiveError = '';
          try {
            const response = await fetch('/api/tickets/archive', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => []);
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warArchive = Array.isArray(payload) ? payload : [];
          } catch (error) { this.warArchiveError = 'Impossible de charger les archives : ' + error.message; }
          finally { this.warArchiveLoading = false; }
          await this.loadWarScenarios();
        },
        async replayWarTicket(ticket) {
          if (!ticket || !ticket.id || this.warReplayBusy) return;
          this.warReplayBusy = ticket.id; this.warArchiveError = '';
          try {
            const response = await fetch('/api/tickets/' + encodeURIComponent(ticket.id) + '/replay', {
              method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warTab = 'inbox';
            await this.loadTickets();
            this.warError = 'Ticket rejoué : ' + payload.new_ticket_id + ' · nouveau délai SLA démarré.';
          } catch (error) { this.warArchiveError = 'Impossible de rejouer le ticket : ' + error.message; }
          finally { this.warReplayBusy = null; }
        },
        async createRandomWarTicket() {
          if (this.warRandomBusy) return;
          const target = window.open('about:blank', '_blank');
          this.warRandomBusy = true; this.warError = ''; this.warNotice = '';
          try {
            const response = await fetch('/api/tickets/random', {
              method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warTab = 'inbox'; this.warFilter = 'all';
            await this.loadTickets();
            const ticketId = payload.ticket_id;
            this.warNotice = 'Ticket surprise créé : ' + ticketId + ' · ' + (payload.scenario?.title || 'scénario aléatoire');
            const url = '/lab.html?ticket=' + encodeURIComponent(ticketId);
            if (target) target.location.href = url;
            else window.location.assign(url);
          } catch (error) {
            this.warError = 'Impossible de créer le ticket surprise : ' + error.message;
            try { if (target) target.close(); } catch (_) {}
          } finally { this.warRandomBusy = false; }
        },
        async loadWarScenarios() {
          this.warScenariosLoading = true; this.warScenarioError = ''; this.warScenarioNotice = '';
          try {
            const response = await fetch('/api/scenarios/list', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => []);
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warScenarios = Array.isArray(payload) ? payload : [];
          } catch (error) { this.warScenarioError = 'Impossible de charger les scénarios : ' + error.message; }
          finally { this.warScenariosLoading = false; }
        },
        filteredWarScenarios() {
          const pilotIds = ['INC-001', 'CHG-001', 'PRB-001'];
          const query = this.norm(this.warScenarioSearch);
          return (this.warScenarios || []).filter(scenario => {
            const id = String(scenario.id || '');
            const isPilot = pilotIds.includes(id);
            const isUser = scenario.is_user_created === true || id.startsWith('USER-') || id.startsWith('RND-');
            const matchesType = this.warScenarioFilter === 'all' ||
              (this.warScenarioFilter === 'pilots' && isPilot) ||
              (this.warScenarioFilter === 'user' && isUser);
            const searchable = this.norm([id, scenario.title, scenario.type].filter(Boolean).join(' '));
            return matchesType && (!query || searchable.includes(query));
          });
        },
        filteredWarArchive() {
          const query = this.norm(this.warScenarioSearch);
          return (this.warArchive || []).filter(ticket => {
            const scenarioId = String(ticket.scenario_id || ticket.id || '');
            const isPilot = ['INC-001', 'CHG-001', 'PRB-001'].includes(scenarioId);
            const isUser = scenarioId.startsWith('USER-') || scenarioId.startsWith('RND-') || String(ticket.id || '').startsWith('RND-');
            const matchesType = this.warScenarioFilter === 'all' ||
              (this.warScenarioFilter === 'pilots' && isPilot) ||
              (this.warScenarioFilter === 'user' && isUser);
            const searchable = this.norm([ticket.id, scenarioId, ticket.title, ticket.scenario_title, ticket.type, ticket.status].filter(Boolean).join(' '));
            return matchesType && (!query || searchable.includes(query));
          });
        },
        async loadScenarioOptions() {
          const response = await fetch('/api/scenarios/options', { credentials: 'same-origin', cache: 'no-store' });
          const payload = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
          this.warScenarioOptions = payload;
          this.updateScenarioTopology();
        },
        scenarioFaultOptions() {
          const options = this.warScenarioOptions;
          const topology = this.createScenario.topology;
          return (options?.faults || []).filter(fault => (fault.topologies || []).includes(topology));
        },
        scenarioTargetOptions() {
          return this.warScenarioOptions?.targets?.[this.createScenario.topology]?.[this.createScenario.fault_id] || [];
        },
        scenarioPortOptions() {
          const target = this.scenarioTargetOptions().find(item => item.id === this.createScenario.target_device);
          return target?.ports || [];
        },
        updateScenarioTopology() {
          const faults = this.scenarioFaultOptions();
          if (!faults.some(fault => fault.id === this.createScenario.fault_id)) this.createScenario.fault_id = faults[0]?.id || '';
          this.updateScenarioFault();
        },
        updateScenarioFault() {
          const targets = this.scenarioTargetOptions();
          if (!targets.some(item => item.id === this.createScenario.target_device)) this.createScenario.target_device = targets[0]?.id || '';
          this.updateScenarioDevice();
        },
        updateScenarioDevice() {
          const ports = this.scenarioPortOptions();
          if (!ports.some(item => item.id === this.createScenario.target_port)) this.createScenario.target_port = ports[0]?.id || '';
          this.createScenarioSavedId = '';
          this.createScenarioSuccess = '';
        },
        async openScenarioCreator() {
          this.createScenarioOpen = true;
          this.createScenarioError = ''; this.createScenarioSuccess = ''; this.createScenarioSavedId = '';
          this.createScenario.name = '';
          try {
            if (!this.warScenarioOptions) await this.loadScenarioOptions();
            else this.updateScenarioTopology();
          } catch (error) { this.createScenarioError = 'Impossible de charger les options : ' + error.message; }
        },
        async saveWarScenario() {
          if (this.createScenarioBusy) return;
          this.createScenarioBusy = true; this.createScenarioError = ''; this.createScenarioSuccess = '';
          try {
            const body = {
              name: this.createScenario.name.trim(), type: this.createScenario.type,
              severity: this.createScenario.severity, topology: this.createScenario.topology,
              fault_id: this.createScenario.fault_id, target_device: this.createScenario.target_device,
              target_port: this.createScenario.target_port, sla_minutes: Number(this.createScenario.sla_minutes)
            };
            const response = await fetch('/api/scenarios/save', {
              method: 'POST', credentials: 'same-origin',
              headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.createScenarioSavedId = payload.scenario_id;
            this.createScenarioSuccess = 'Scénario enregistré : ' + payload.scenario_id;
            this.warTab = 'archive'; this.warScenarioFilter = 'user';
            await this.loadWarArchive();
            await this.loadTickets();
          } catch (error) { this.createScenarioError = 'Impossible d’enregistrer le scénario : ' + error.message; }
          finally { this.createScenarioBusy = false; }
        },
        async exportWarScenario(scenarioId) {
          try {
            const response = await fetch('/api/scenarios/' + encodeURIComponent(scenarioId) + '/export', {
              credentials: 'same-origin', cache: 'no-store'
            });
            const body = await response.text();
            let payload = {};
            try { payload = JSON.parse(body); } catch (_) {}
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            const blob = new Blob([JSON.stringify(payload, null, 2) + '\n'], { type: 'application/json;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url; link.download = scenarioId + '.json'; document.body.appendChild(link); link.click(); link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            if (this.createScenarioOpen) this.createScenarioSuccess = 'Export téléchargé : ' + scenarioId + '.json';
            else this.warScenarioNotice = 'Export téléchargé : ' + scenarioId + '.json';
          } catch (error) {
            const message = 'Impossible d’exporter le scénario : ' + error.message;
            if (this.createScenarioOpen) this.createScenarioError = message; else this.warScenarioError = message;
          }
        },
        async importWarScenario(event) {
          const input = event?.target;
          const file = input?.files?.[0];
          if (!file) return;
          this.warScenarioError = '';
          try {
            const imported = JSON.parse(await file.text());
            if (!imported || !imported.id || !imported.type || !imported.initial_topology ||
                !Array.isArray(imported.initial_topology.nodes) || !imported.resolution_check ||
                !Array.isArray(imported.resolution_check.rules) || !imported.resolution_check.rules.length) {
              throw new Error('Le JSON doit contenir id, type, initial_topology.nodes et resolution_check.rules.');
            }
            const response = await fetch('/api/scenarios/import', {
              method: 'POST', credentials: 'same-origin',
              headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(imported)
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warTab = 'archive'; this.warScenarioFilter = 'user';
            await this.loadWarScenarios(); await this.loadTickets(); await this.loadWarArchive();
            this.warScenarioNotice = 'Scénario importé sous ' + payload.scenario_id + '.';
          } catch (error) { this.warScenarioError = 'Import impossible : ' + error.message; }
          finally { if (input) input.value = ''; }
        },
        async launchWarScenario(scenario) {
          if (!scenario?.id) return;
          const target = window.open('about:blank', '_blank');
          try {
            const response = await fetch('/api/tickets/' + encodeURIComponent(scenario.id) + '/open', {
              method: 'POST', credentials: 'same-origin',
              headers: { 'Content-Type': 'application/json' }, body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            const ticketId = payload.ticket?.id;
            if (!ticketId) throw new Error('Le serveur n’a pas retourné de ticket.');
            this.warTab = 'inbox'; await this.loadTickets();
            const url = '/lab.html?ticket=' + encodeURIComponent(ticketId);
            if (target) target.location.href = url; else window.location.assign(url);
          } catch (error) {
            this.warScenarioError = 'Impossible de lancer ce scénario : ' + error.message;
            try { if (target) target.close(); } catch (_) {}
          }
        },
        formatWarDuration(seconds) {
          if (seconds === null || seconds === undefined || !Number.isFinite(Number(seconds))) return '—';
          const total = Math.max(0, Math.floor(Number(seconds)));
          if (total < 60) return total + ' s';
          const minutes = Math.floor(total / 60), secs = total % 60;
          if (minutes < 60) return minutes + ' min ' + String(secs).padStart(2, '0') + ' s';
          return Math.floor(minutes / 60) + ' h ' + String(minutes % 60).padStart(2, '0') + ' min';
        },

        async resumeWarTicket(ticket) {
          if (!ticket?.id || this.warReplayBusy) return;
          const target = window.open('about:blank', '_blank');
          this.warReplayBusy = ticket.id; this.warError = '';
          try {
            const response = await fetch('/api/tickets/' + encodeURIComponent(ticket.id) + '/resume', {
              method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            await this.loadTickets(); this.loadWarOpenCount();
            this.warNotice = 'Ticket repris : ' + ticket.id + ' · le temps SLA restant a été restauré.';
            const url = '/lab.html?ticket=' + encodeURIComponent(ticket.id);
            if (target) target.location.href = url;
            else window.location.assign(url);
          } catch (error) {
            this.warError = 'Impossible de reprendre le ticket : ' + error.message;
            try { if (target) target.close(); } catch (_) {}
          } finally { this.warReplayBusy = null; }
        },
        async loadTickets() {
          this.warLoading = true; this.warError = '';
          try {
            const response = await fetch('/api/tickets', { credentials: 'same-origin', cache: 'no-store' });
            const payload = await response.json().catch(() => []);
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            this.warTickets = Array.isArray(payload) ? payload : [];
            this.loadWarOpenCount();
            if (this._warTicketTimer) clearInterval(this._warTicketTimer);
            this._warTicketTimer = setInterval(() => {
              this.warTickets.forEach(ticket => {
                if (typeof ticket.sla_left === 'number') ticket.sla_left = Math.max(0, ticket.sla_left - 1);
              });
            }, 1000);
          } catch (error) { this.warError = 'Impossible de charger la file NOC : ' + error.message; }
          finally { this.warLoading = false; }
        },
        get filteredWarTickets() {
          return this.warTickets.filter(ticket => this.warFilter === 'all' || ticket.type === this.warFilter);
        },
        formatWarSla(seconds) {
          if (seconds === null || seconds === undefined) return 'Sans SLA';
          const total = Math.max(0, Number(seconds) || 0);
          if (total === 0) return 'SLA dépassé';
          const h = Math.floor(total / 3600), m = Math.floor((total % 3600) / 60), s = Math.floor(total % 60);
          return h > 0 ? String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0') : String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
        },
        async openWarTicket(ticket) {
          const url = '/lab.html?ticket=' + encodeURIComponent(ticket.id);
          const target = window.open(url, '_blank');
          if (!target) { window.location.assign(url); return; }
          try {
            const response = await fetch('/api/tickets/' + encodeURIComponent(ticket.scenario_id || ticket.id) + '/open', {
              method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', body: '{}'
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
            const finalId = payload.ticket && payload.ticket.id ? payload.ticket.id : ticket.id;
            if (finalId !== ticket.id) target.location.href = '/lab.html?ticket=' + encodeURIComponent(finalId);
          } catch (error) {
            this.warError = 'Impossible d’ouvrir le ticket : ' + error.message;
            try { target.close(); } catch (_) {}
          }
        },


        // ================= LECTEUR DE COURS =================
        // Retire l'en-tête technique des fichiers de cours ("## node_id: ..." puis "title: ...") pour ne pas l'afficher
        stripLessonHeader(md) {
          return md.replace(/^\s*##\s*node_id:[^\n]*\n+(?:title:[^\n]*\n+)?/i, '');
        },

        // Dé-indente les balises HTML (4 espaces ou plus) hors blocs de code : sinon Markdown les prend pour du code
        isLessonPlaceholder(md) {
          const lines = this.stripLessonHeader(String(md || ''))
            .replace(/^\uFEFF/u, '')
            .split(/\r?\n/u)
            .map(line => line.trim())
            .filter(Boolean);
          return lines.length === 2
            && /^#\s+\S/u.test(lines[0])
            && /^\[Contenu de \d+\s+mots à rédiger\]$/iu.test(lines[1]);
        },

        normalizeHtmlBlocks(md) {
          let inFence = false;
          return md.split('\n').map(line => {
            if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; return line; }
            if (!inFence && /^ {4,}<\/?[a-zA-Z][^>]*>/.test(line)) return line.trimStart();
            return line;
          }).join('\n');
        },

        slugify(s) {
          return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);
        },

        // Markdown -> HTML : ids de titres + sommaire, callouts, blocs de code, boîte "À retenir"
        formatMarkdown(mdText) {
          const wrap = document.createElement('div');
          wrap.innerHTML = window.marked.parse(this.normalizeHtmlBlocks(this.stripLessonHeader(mdText)));

          // 1. Titres h2 : id + sommaire
          const toc = [];
          wrap.querySelectorAll('h2').forEach((h, i) => {
            const text = h.textContent.trim();
            h.id = `sec-${i}-${this.slugify(text)}`;
            toc.push({ id: h.id, text });

          });
          this.lessonToc = toc;

          // 2. Blockquotes "**Mot-clé :** ..." -> callouts
          wrap.querySelectorAll('blockquote').forEach(bq => {
            const p = bq.firstElementChild;
            const strong = p && p.firstElementChild;
            if (!p || p.tagName !== 'P' || !strong || strong.tagName !== 'STRONG' || p.firstChild !== strong) return;

            const keyword = strong.textContent.replace(/[:：]\s*$/, '').trim();
            let type = null, icon = '';
            if (/analogie|note|remarque/i.test(keyword)) { type = 'info'; icon = '💡'; }
            else if (/astuce|bonne pratique/i.test(keyword)) { type = 'tip'; icon = '✅'; }
            else if (/piège|piege|danger|attention/i.test(keyword)) { type = 'danger'; icon = '⚠️'; }
            else if (/examen/i.test(keyword)) { type = 'exam'; icon = '🎓'; }
            if (!type) return; // citation normale

            strong.remove();
            if (p.firstChild && p.firstChild.nodeType === 3) p.firstChild.textContent = p.firstChild.textContent.replace(/^[\s:：]+/, '');

            const box = document.createElement('div');
            box.className = `callout callout-${type}`;
            const title = document.createElement('div');
            title.className = 'callout-title';
            title.textContent = `${icon} ${keyword}`;
            const content = document.createElement('div');
            content.className = 'callout-content';
            while (bq.firstChild) content.appendChild(bq.firstChild);
            box.appendChild(title);
            box.appendChild(content);
            bq.replaceWith(box);
          });

          // 3. Blocs de code : en-tête (langue) + bouton Copier (géré par délégation, voir onLessonClick)
          wrap.querySelectorAll('pre').forEach(pre => {
            const code = pre.querySelector('code');
            const m = code && code.className.match(/language-(\S+)/);
            const lang = m ? m[1].toLowerCase() : 'text';
            if (lang === 'mermaid') {
              const diagram = document.createElement('div');
              diagram.className = 'lesson-mermaid';
              const source = document.createElement('pre');
              source.className = 'lesson-mermaid-source';
              source.textContent = code ? code.textContent : pre.textContent;
              diagram.appendChild(source);
              pre.replaceWith(diagram);
              return;
            }
            const box = document.createElement('div');
            box.className = 'code-container';
            const head = document.createElement('div');
            head.className = 'code-header';
            head.innerHTML = '<span class="code-lang"></span><button type="button" class="btn-copy">Copier</button>';
            head.querySelector('.code-lang').textContent = lang;
            pre.replaceWith(box);
            box.appendChild(head);
            box.appendChild(pre);
          });

          // 3bis. Tableaux : conteneur arrondi (défilement seulement si le tableau ne peut pas tenir)
          wrap.querySelectorAll('table').forEach(t => {
            const holder = document.createElement('div');
            holder.className = 'table-wrapper';
            t.parentNode.insertBefore(holder, t);
            holder.appendChild(t);
          });

          // 4. Section "À retenir" mise en valeur
          const recapTitle = [...wrap.querySelectorAll('h2')].find(h => /retenir/i.test(h.textContent));
          if (recapTitle) {
            const box = document.createElement('div');
            box.className = 'lesson-recap';
            recapTitle.parentNode.insertBefore(box, recapTitle);
            let n = recapTitle;
            while (n && !(n !== recapTitle && n.nodeType === 1 && n.tagName === 'H2')) {
              const next = n.nextSibling;
              box.appendChild(n);
              n = next;
            }
          }

          // 5. Figures, SVG, images, Mermaid, schémas ASCII et tableaux reçoivent
          // une légende de lecture et une action d’explication contextualisée.
          this.prepareLessonDiagrams(wrap);

          // 6. Temps de lecture (sur le texte, pas sur le HTML)
          const words = (wrap.textContent || '').split(/\s+/).filter(Boolean).length;
          this.readingMinutes = Math.max(1, Math.ceil(words / 200));

          return wrap.innerHTML;
        },

        prepareLessonDiagrams(wrap) {
          const roots = new Set();
          const isAsciiDiagram = source => {
            const value = String(source || '');
            const lines = value.split(/\r?\n/u);
            if (lines.length < 2) return false;
            const pipeRows = lines.filter(line => (line.match(/[|│]/gu) || []).length >= 2);
            const labelsOnLines = lines.filter(line => /[A-Za-z0-9]/u.test(line)).length;
            const connectorOnlyLines = lines.filter(line => !/[A-Za-z0-9]/u.test(line) && /[|+^v<>_\\/\\-]/u.test(line)).length;
            return /[┌┐└┘├┤┬┴┼─│╭╮╰╯↔↕←→↑↓]/u.test(value)
              || pipeRows.length >= 2
              || (labelsOnLines >= 2 && connectorOnlyLines >= 2)
              || lines.some(line => /[A-Za-z0-9][\w.-]*(?:\s*(?:--+>|-{2,}|==>|->|<->|→|←|↔|—|–)\s*)[A-Za-z0-9]/u.test(line));
          };

          wrap.querySelectorAll('.code-container').forEach(container => {
            const lang = String(container.querySelector('.code-lang')?.textContent || '').toLowerCase();
            const sourceNode = container.querySelector('pre code, pre');
            const source = sourceNode ? sourceNode.textContent : '';
            if (['graphviz', 'dot', 'plantuml', 'puml', 'd2', 'ascii', 'diagram', 'flowchart'].includes(lang) || isAsciiDiagram(source)) {
              roots.add(container);
            }
          });

          wrap.querySelectorAll('figure, .diagram, .lesson-figure, .figure, .lesson-mermaid, .table-wrapper, img, svg').forEach(element => {
            let root = element;
            if (element.matches('img, svg')) {
              root = element.closest('figure, .diagram, .lesson-figure, .figure, .lesson-mermaid, .table-wrapper');
              if (!root) {
                // Ne jamais injecter de HTML à l’intérieur d’un SVG ou d’un paragraphe.
                // Un conteneur sémantique permet aux contrôles de rester valides et accessibles.
                const visualParent = element.parentElement;
                const wrapper = document.createElement('figure');
                wrapper.className = 'lesson-visual-diagram';
                if (visualParent && visualParent.tagName === 'P' && visualParent.parentNode) {
                  visualParent.parentNode.insertBefore(wrapper, visualParent);
                  wrapper.appendChild(element);
                  if (!visualParent.textContent.trim() && !visualParent.querySelector('img, svg, video, audio')) {
                    visualParent.remove();
                  }
                } else if (visualParent && visualParent.parentNode) {
                  visualParent.insertBefore(wrapper, element);
                  wrapper.appendChild(element);
                } else {
                  return;
                }
                root = wrapper;
              }
            }
            roots.add(root);
          });

          let candidates = Array.from(roots).filter(root => root && root.nodeType === 1 && wrap.contains(root));
          candidates = candidates.filter(root => !candidates.some(other => other !== root && other.contains(root)));

          candidates.forEach(root => {
            if (root.classList.contains('lesson-diagram-block')) return;
            root.classList.add('lesson-diagram-block');
            root.setAttribute('data-diagram-root', 'true');

            const sourceNode = root.querySelector('.lesson-mermaid-source, pre code, pre');
            const source = sourceNode ? sourceNode.textContent : '';
            const table = root.querySelector('table');
            const svg = root.querySelector('svg') || (root.matches('svg') ? root : null);
            const image = root.querySelector('img[alt], img[title]') || (root.matches('img') ? root : null);
            const mermaid = root.classList.contains('lesson-mermaid');
            const kind = table ? 'tableau' : (mermaid ? 'diagramme Mermaid' : (svg ? 'schéma SVG' : (image ? 'illustration' : 'schéma textuel')));
            root.dataset.diagramType = kind;

            let explicit = '';
            const caption = root.querySelector('figcaption');
            const svgTitle = root.querySelector('svg title, svg desc') || (root.matches('svg') ? root.querySelector('title, desc') : null);
            const titleNode = root.querySelector('title');
            if (caption) explicit = caption.textContent.trim();
            else if (svgTitle) explicit = svgTitle.textContent.trim();
            else if (image) explicit = String(image.getAttribute('alt') || image.getAttribute('title') || '').trim();
            else explicit = String(root.getAttribute('aria-label') || (titleNode && titleNode.textContent) || '').trim();

            const labels = [];
            const addLabel = value => {
              const clean = String(value || '').replace(/\s+/gu, ' ').trim();
              if (clean && !labels.includes(clean) && labels.length < 10) labels.push(clean);
            };
            root.querySelectorAll('svg text, svg tspan').forEach(node => addLabel(node.textContent));
            if (root.matches('svg')) root.querySelectorAll('text, tspan').forEach(node => addLabel(node.textContent));

            if (source) {
              const mermaidNodes = source.matchAll(/[\w.-]+\s*[\[({]([^\])}]+)[\])}]/gu);
              for (const match of mermaidNodes) addLabel(match[1]);
              if (!labels.length && isAsciiDiagram(source)) {
                source.split(/\r?\n/u).forEach(line => {
                  const cleaned = line.replace(/[┌┐└┘├┤┬┴┼─│╭╮╰╯]/gu, ' ');
                  cleaned.split(/(?:--+>|-{2,}|==>|->|<->|→|←|↔|—|–|[|]+|\s{2,})/u)
                    .forEach(part => addLabel(part.replace(/^[\s\[\](){}]+|[\s\[\](){}]+$/gu, '')));
                });
              }
            }

            const content = root.querySelector('table') ? ''
              : String((root.matches('img') ? (root.getAttribute('alt') || root.getAttribute('title') || '') : '') || '');
            let explanation;
            if (explicit) {
              explanation = 'Description associée : ' + explicit + '. Repère ensuite la légende, les flèches, les connecteurs et les regroupements pour relier cette description aux éléments représentés.';
            } else if (labels.length) {
              explanation = 'Éléments ou libellés visibles : ' + labels.slice(0, 8).join(', ') + '. Commence par repérer ces éléments, puis suis les connecteurs et le sens éventuel des flèches. Le texte autour du dessin précise la signification des relations ; une liaison graphique ne prouve pas, à elle seule, qu’un trafic circule en temps réel.';
            } else if (table) {
              const headers = Array.from(table.querySelectorAll('thead th, tr:first-child th, tr:first-child td')).map(cell => cell.textContent.trim()).filter(Boolean);
              explanation = headers.length
                ? 'Lis les intitulés de colonnes, puis compare les valeurs sur une même ligne. Les colonnes donnent le contexte de chaque valeur : ' + headers.join(', ') + '.'
                : 'Lis le tableau ligne par ligne et compare les valeurs dans une même colonne. Les intitulés et le texte autour du tableau donnent le contexte des données.';
            } else {
              explanation = 'Pour lire cette représentation, identifie d’abord les éléments nommés, la légende et les symboles. Suis les connecteurs et les flèches lorsqu’ils existent, puis vérifie le sens de la relation dans le paragraphe voisin. Les traits, couleurs ou flèches ne suffisent pas, à eux seuls, à prouver un échange réel de données.';
            }
            if (content && !explicit) explanation = explanation + ' Texte alternatif : ' + content + '.';

            const toolbar = document.createElement('div');
            toolbar.className = 'lesson-diagram-toolbar';
            const kindLabel = document.createElement('span');
            kindLabel.className = 'lesson-diagram-kind';
            kindLabel.textContent = 'Lecture guidée · ' + kind;
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn-explain-diagram';
            button.textContent = table ? 'Expliquer ce tableau' : 'Expliquer ce schéma';
            button.setAttribute('aria-label', 'Demander une explication contextualisée pour ce ' + kind);
            toolbar.appendChild(kindLabel);
            toolbar.appendChild(button);
            root.insertBefore(toolbar, root.firstChild);

            const guide = document.createElement('div');
            guide.className = 'lesson-diagram-guide';
            guide.setAttribute('role', 'note');
            const guideTitle = document.createElement('strong');
            guideTitle.textContent = table ? 'Comment lire ce tableau' : 'Comment lire ce schéma';
            const guideText = document.createElement('p');
            guideText.textContent = explanation;
            guide.appendChild(guideTitle);
            guide.appendChild(guideText);
            root.appendChild(guide);
          });
        },

        async renderLessonDiagrams() {
          const root = this.$refs.lessonArticle;
          if (!root) return;
          const mermaidBlocks = Array.from(root.querySelectorAll('.lesson-mermaid'));
          if (!mermaidBlocks.length) return;
          try {
            await window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js', 'mermaid');
          } catch (error) {
            console.warn('Mermaid indisponible ; les diagrammes restent sous forme source.', error);
            return;
          }
          if (!window.mermaid) return;

          if (!this._mermaidInitialized) {
            window.mermaid.initialize({
              startOnLoad: false,
              securityLevel: 'strict',
              theme: document.documentElement.classList.contains('light') ? 'default' : 'dark',
            });
            this._mermaidInitialized = true;
          }

          // Rendre chaque diagramme séparément : un diagramme invalide ne doit pas
          // interrompre le rendu des suivants. Mermaid peut produire un SVG d'erreur
          // sans rejeter la promesse de run(), donc on valide aussi le résultat.
          for (const block of mermaidBlocks) {
            if (block.dataset.renderAttempted === 'true') continue;
            const source = block.querySelector('.lesson-mermaid-source');
            if (!source) {
              if (block.querySelector('.mermaid svg')) block.dataset.renderAttempted = 'true';
              continue;
            }

            const sourceText = source.textContent || '';
            const visual = document.createElement('div');
            visual.className = 'mermaid';
            visual.dataset.originalSource = sourceText;
            visual.textContent = sourceText;
            source.replaceWith(visual);
            block.dataset.renderAttempted = 'true';

            try {
              // Parse before rendering so a malformed block is isolated locally.
              await window.mermaid.parse(sourceText);
              await window.mermaid.run({ nodes: [visual] });
              const svg = visual.querySelector('svg');
              const renderedText = String(svg?.textContent || visual.textContent || '');
              const hasMermaidError = /syntax error in text|no diagram type detected|error while rendering diagram|mermaid version\s+\d/i.test(renderedText);
              if (!svg || hasMermaidError) {
                throw new Error('Mermaid did not produce a valid SVG');
              }
            } catch (error) {
              const panel = document.createElement('div');
              panel.className = 'lesson-mermaid-error-panel';
              panel.setAttribute('role', 'status');
              const message = document.createElement('p');
              message.className = 'lesson-mermaid-error-message';
              message.textContent = 'Ce diagramme n’a pas pu être rendu. Le reste du cours reste disponible ; le code source est conservé ci-dessous pour diagnostic.';
              const fallback = document.createElement('pre');
              fallback.className = 'lesson-mermaid-source';
              fallback.textContent = sourceText;
              panel.appendChild(message);
              panel.appendChild(fallback);
              visual.replaceWith(panel);
              block.dataset.diagramRenderError = 'true';
            }
          }

          // Les diagrammes Mermaid peuvent être très grands. Chaque schéma dispose
          // d'un cadre défilant et de commandes de zoom, sans modifier le contenu du SVG.
          mermaidBlocks.forEach(block => {
            if (block.dataset.zoomReady === 'true') return;
            const visual = block.querySelector('.mermaid');
            const svg = visual?.querySelector('svg');
            const toolbar = block.querySelector('.lesson-diagram-toolbar');
            if (!visual || !svg || !toolbar) return;

            const viewBox = svg.viewBox?.baseVal;
            const attrWidth = Number.parseFloat(svg.getAttribute('width'));
            const attrHeight = Number.parseFloat(svg.getAttribute('height'));
            let baseWidth = viewBox && viewBox.width > 0 ? viewBox.width : attrWidth;
            let baseHeight = viewBox && viewBox.height > 0 ? viewBox.height : attrHeight;
            if (!(baseWidth > 0) || !(baseHeight > 0)) {
              try {
                const box = svg.getBBox();
                if (!(baseWidth > 0)) baseWidth = box.width;
                if (!(baseHeight > 0)) baseHeight = box.height;
              } catch (_) {}
            }
            if (!(baseWidth > 0) || !(baseHeight > 0)) return;

            const viewport = document.createElement('div');
            viewport.className = 'lesson-mermaid-viewport';
            viewport.tabIndex = 0;
            viewport.setAttribute('role', 'region');
            viewport.setAttribute('aria-label', 'Zone de lecture du diagramme ; défilement possible après zoom');
            const stage = document.createElement('div');
            stage.className = 'lesson-mermaid-stage';
            svg.parentNode.insertBefore(viewport, svg);
            viewport.appendChild(stage);
            stage.appendChild(svg);

            const controls = document.createElement('div');
            controls.className = 'lesson-diagram-zoom-controls';
            const level = document.createElement('span');
            level.className = 'lesson-diagram-zoom-level';
            level.setAttribute('aria-live', 'polite');
            level.textContent = '100 %';

            const makeButton = (label, ariaLabel, action) => {
              const button = document.createElement('button');
              button.type = 'button';
              button.className = 'btn-diagram-zoom';
              button.textContent = label;
              button.setAttribute('aria-label', ariaLabel);
              button.title = ariaLabel;
              button.addEventListener('click', action);
              return button;
            };

            let scale = 1;
            const maxFrameHeight = () => Math.max(240, Math.min(720, Math.round(window.innerHeight * 0.66)));
            const applyScale = nextScale => {
              scale = Math.max(0.1, Math.min(4, nextScale));
              const width = Math.max(1, Math.round(baseWidth * scale));
              const height = Math.max(1, Math.round(baseHeight * scale));
              svg.style.setProperty('width', width + 'px', 'important');
              svg.style.setProperty('height', height + 'px', 'important');
              svg.style.setProperty('max-width', 'none', 'important');
              svg.style.setProperty('max-height', 'none', 'important');
              svg.style.setProperty('display', 'block', 'important');
              stage.style.width = width + 'px';
              stage.style.height = height + 'px';
              viewport.style.height = Math.min(height + 18, maxFrameHeight()) + 'px';
              level.textContent = Math.round(scale * 100) + ' %';
              level.setAttribute('aria-label', 'Zoom ' + Math.round(scale * 100) + ' pour cent');
            };

            const fitToFrame = () => {
              const availableWidth = Math.max(180, viewport.clientWidth - 24);
              const scaleToFit = Math.min(1, availableWidth / baseWidth, maxFrameHeight() / baseHeight);
              applyScale(scaleToFit);
              viewport.scrollTop = 0;
              viewport.scrollLeft = 0;
            };

            controls.appendChild(makeButton('−', 'Dézoomer le schéma', () => applyScale(scale / 1.2)));
            controls.appendChild(level);
            controls.appendChild(makeButton('+', 'Zoomer le schéma', () => applyScale(scale * 1.2)));
            controls.appendChild(makeButton('Ajuster', 'Ajuster le schéma au cadre visible', fitToFrame));
            controls.appendChild(makeButton('100 %', 'Afficher le schéma à sa taille de référence', () => {
              applyScale(1);
              viewport.scrollTop = 0;
              viewport.scrollLeft = 0;
            }));
            toolbar.appendChild(controls);
            block.dataset.zoomReady = 'true';
            fitToFrame();
          });
        },

        explainDiagramFromButton(button) {
          const root = button.closest('[data-diagram-root="true"]');
          if (!root || !this.detail?.id) return;
          const visual = root.cloneNode(true);
          visual.querySelectorAll('.lesson-diagram-toolbar, .lesson-diagram-guide, button, .code-header').forEach(element => element.remove());
          const visibleLabels = Array.from(visual.querySelectorAll('svg text, svg tspan, figcaption, img[alt], img[title]'))
            .map(element => element.tagName === 'IMG'
              ? (element.getAttribute('alt') || element.getAttribute('title') || '')
              : element.textContent)
            .map(value => String(value || '').replace(/\s+/gu, ' ').trim())
            .filter(Boolean);
          const sourceText = String(visual.innerText || visual.textContent || '').replace(/\s+/gu, ' ').trim();
          // Mermaid est converti en SVG pour l'affichage : conserver son DSL d'origine
          // pour que le tuteur puisse expliquer les relations nommées, pas seulement les libellés rendus.
          const sourceCode = visual.querySelector('.mermaid[data-original-source]')?.dataset.originalSource
            || visual.querySelector('.lesson-mermaid-source')?.textContent
            || '';
          const kind = String(root.dataset.diagramType || 'schéma');
          const nearbyText = sibling => {
            const values = [];
            let current = sibling;
            while (current && values.length < 2) {
              const textValue = String(current.innerText || current.textContent || '').replace(/\s+/gu, ' ').trim();
              if (textValue && !current.classList?.contains('lesson-diagram-block')) values.push(textValue.slice(0, 500));
              current = sibling === root.previousElementSibling ? current.previousElementSibling : current.nextElementSibling;
            }
            return values.join(' | ');
          };
          const previousContext = nearbyText(root.previousElementSibling);
          const nextContext = nearbyText(root.nextElementSibling);
          this.tutorMessages = [];
          this.tutorSelectedText = [
            'Type de représentation : ' + kind,
            'Contenu source ou visible : ' + (sourceText || '(aucun texte directement visible)'),
            'Code source du diagramme : ' + (sourceCode || '(pas de code source textuel disponible)'),
            'Libellés relevés : ' + (visibleLabels.join(', ') || '(aucun libellé accessible détecté)'),
            'Explication voisine avant le schéma : ' + (previousContext || '(aucune)'),
            'Explication voisine après le schéma : ' + (nextContext || '(aucune)'),
          ].join('\n').slice(0, 3000);
          const question = 'Explique précisément ce ' + kind + ' sélectionné, en français clair et par étapes. Commence par son objectif, nomme les éléments réellement présents, puis explique les relations et les flèches en t’appuyant sur le contexte fourni. Distingue ce que le dessin montre de ce qu’il ne permet pas de conclure. Donne un exemple concret de lecture et termine par une synthèse. N’invente aucune étiquette, connexion, donnée, direction de trafic ou fonction absente du schéma et du cours.';
          return this.askTutorPreset(question);
        },

        // Corrige automatiquement le contraste du texte (HTML et SVG) selon le fond RÉEL de chaque élément :
        // texte pâle sur carte claire -> texte foncé ; texte foncé sur fond sombre -> texte clair.
        // Les couleurs voulues qui sont déjà lisibles (badges rouges, etc.) sont conservées.
        fixLessonContrast() {
          const root = this.$refs.lessonArticle || document.querySelector('.lesson-prose');
          if (!root) return;
          const parse = (str) => {
            const m = /rgba?\(([^)]+)\)/.exec(str || '');
            if (!m) return null;
            const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(parseFloat);
            if (p.length < 3 || p.slice(0, 3).some(isNaN)) return null;
            return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
          };
          const lum = (c) => {
            const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
            return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
          };
          const ratio = (a, b) => {
            const l1 = lum(a), l2 = lum(b);
            return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
          };
          const cache = new Map();
          const bgOf = (el) => {
            if (cache.has(el)) return cache.get(el);
            let bg;
            const c = parse(getComputedStyle(el).backgroundColor);
            if (c && c.a >= 0.5) bg = c;
            else if (el.parentElement) bg = bgOf(el.parentElement);
            else bg = { r: 12, g: 12, b: 12, a: 1 };
            cache.set(el, bg);
            return bg;
          };
          const MIN = 4;
          // Le CSS gère déjà le texte Markdown standard. Ne parcourir que les éléments dont
          // la couleur est personnalisée et les libellés SVG ; les milliers de nœuds <pre>/<code>
          // des cours longs ne doivent pas être examinés un par un.
          root.querySelectorAll('svg text, svg tspan, [style*="color" i], [style*="fill" i]').forEach(el => {
            if (el.closest('pre, .code-container')) return;
            const tag = el.tagName.toLowerCase();
            const isSvgText = tag === 'text' || tag === 'tspan';
            const hasText = isSvgText || [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
            if (!hasText) return;
            const cs = getComputedStyle(el);
            const fg = parse(isSvgText ? cs.fill : cs.color);
            if (!fg) return;
            const bg = bgOf(el);
            if (ratio(fg, bg) >= MIN) return;
            const lightBg = lum(bg) > 0.4;
            const bold = (parseInt(cs.fontWeight, 10) || 400) >= 600 || /^h[1-6]$|^(strong|b|th|summary)$/.test(tag);
            let col;
            if (lightBg) col = tag === 'a' ? '#0369a1' : (bold ? '#0f172a' : '#334155');
            else col = bold ? '#ffffff' : '#ece9ff';
            el.style.setProperty(isSvgText ? 'fill' : 'color', col, 'important');
          });
        },

        onLessonClick(e) {
          const diagramButton = e.target.closest('.btn-explain-diagram');
          if (diagramButton) {
            this.explainDiagramFromButton(diagramButton);
            return;
          }
          const btn = e.target.closest('.btn-copy');
          if (!btn) return;
          const pre = btn.closest('.code-container')?.querySelector('pre');
          if (!pre) return;
          navigator.clipboard.writeText(pre.innerText).then(() => {
            btn.textContent = 'Copié ✓';
            setTimeout(() => { btn.textContent = 'Copier'; }, 1800);
          }).catch(() => { });
        },

        refreshLessonHeadingOffsets() {
          const container = this.$refs.modalScroll;
          const article = this.$refs.lessonArticle;
          const courseId = String(this.detail?.id || '');
          if (!container || !article || !courseId) {
            this._lessonHeadingOffsets = [];
            this._lessonHeadingCourseId = courseId;
            return;
          }

          // Les nouveaux cours peuvent avoir plusieurs centaines de titres.
          // Mesurer leur géométrie une seule fois, hors du gestionnaire de scroll.
          const containerTop = container.getBoundingClientRect().top;
          const scrollTop = container.scrollTop;
          this._lessonHeadingOffsets = Array.from(article.querySelectorAll('h2[id]'))
            .map(heading => ({
              id: heading.id,
              top: heading.getBoundingClientRect().top - containerTop + scrollTop,
            }))
            .sort((a, b) => a.top - b.top);
          this._lessonHeadingCourseId = courseId;
        },
        observeLessonHeadingLayout() {
          if (this._lessonHeadingObserver) {
            this._lessonHeadingObserver.disconnect();
            this._lessonHeadingObserver = null;
          }
          if (this._lessonHeadingRefreshFrame) {
            cancelAnimationFrame(this._lessonHeadingRefreshFrame);
            this._lessonHeadingRefreshFrame = 0;
          }

          const container = this.$refs.modalScroll;
          const article = this.$refs.lessonArticle;
          if (!container || !article || typeof ResizeObserver === 'undefined') return;

          // Recalculer seulement quand le texte se recompose (fenêtre redimensionnée,
          // police ou média qui change de taille), jamais à chaque pixel de défilement.
          this._lessonHeadingObserver = new ResizeObserver(() => {
            if (this._lessonHeadingRefreshFrame) cancelAnimationFrame(this._lessonHeadingRefreshFrame);
            this._lessonHeadingRefreshFrame = requestAnimationFrame(() => {
              this._lessonHeadingRefreshFrame = 0;
              if (this.open && this.$refs.lessonArticle === article) this.refreshLessonHeadingOffsets();
            });
          });
          this._lessonHeadingObserver.observe(container);
          this._lessonHeadingObserver.observe(article);
        },
        resetLessonHeadingOffsets() {
          if (this._lessonHeadingObserver) {
            this._lessonHeadingObserver.disconnect();
            this._lessonHeadingObserver = null;
          }
          if (this._lessonHeadingRefreshFrame) cancelAnimationFrame(this._lessonHeadingRefreshFrame);
          this._lessonHeadingRefreshFrame = 0;
          this._lessonHeadingOffsets = [];
          this._lessonHeadingCourseId = '';
        },
        async syncLearningProgress(nodeId = this.detail?.id, options = {}) {
          const targetId = String(nodeId || '');
          const force = options && options.force === true;
          if (!targetId || !this.open || String(this.detail?.id || '') !== targetId) return null;
          if (!force && (this.modalTab !== 'lesson' || document.hidden)) return null;
          if (this._learningProgressBusy) return null;

          this._learningProgressBusy = true;
          try {
            const response = await fetch('/api/node/' + encodeURIComponent(targetId) + '/learning-progress', {
              method: 'POST',
              credentials: 'same-origin',
              cache: 'no-store',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                progress_percent: Math.max(0, Math.min(100, Number(this.lessonProgress) || 0))
              })
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || ('HTTP ' + response.status));
            if (this.open && String(this.detail?.id || '') === targetId) {
              this.learningProgress = payload;
              this.learningProgressError = '';
            }
            return payload;
          } catch (error) {
            if (this.open && String(this.detail?.id || '') === targetId) {
              this.learningProgressError = 'La progression de lecture ne peut pas être synchronisée. Vérifie la connexion puis réessaie.';
            }
            return null;
          } finally {
            this._learningProgressBusy = false;
          }
        },
        startLearningProgressSync(nodeId) {
          if (this._learningProgressTimer) window.clearInterval(this._learningProgressTimer);
          this._learningProgressTimer = null;
          const targetId = String(nodeId || this.detail?.id || '');
          this._learningProgressNodeId = '';
          this.learningProgress = null;
          this.learningProgressError = '';
          if (!targetId || String(this.detail?.id || '') !== targetId ||
              !this.detail?.requirements?.some(requirement => requirement.kind === 'quiz')) return;

          this._learningProgressNodeId = targetId;
          void this.syncLearningProgress(targetId, { force: true });
          this._learningProgressTimer = window.setInterval(() => {
            if (this._learningProgressNodeId === targetId) void this.syncLearningProgress(targetId);
          }, 15000);
        },
        stopLearningProgressSync(options = {}) {
          const nodeId = String(this._learningProgressNodeId || '');
          if (this._learningProgressTimer) window.clearInterval(this._learningProgressTimer);
          this._learningProgressTimer = null;
          this._learningProgressNodeId = '';
          if (options && options.flush === true && nodeId && this.open &&
              String(this.detail?.id || '') === nodeId) {
            void this.syncLearningProgress(nodeId, { force: true });
          }
        },

        onLessonScroll(e) {
          const el = e.target;
          const max = el.scrollHeight - el.clientHeight;
          this.lessonProgress = max > 0 ? Math.min(100, Math.round((el.scrollTop / max) * 100)) : 0;
          if (this.modalTab !== 'lesson' || !this.detail?.id) return;

          const courseId = String(this.detail.id);
          if (this._lessonHeadingCourseId !== courseId) this.refreshLessonHeadingOffsets();
          const headings = this._lessonHeadingOffsets || [];
          const limit = el.scrollTop + 100;

          // Recherche binaire O(log n), sans getBoundingClientRect() par titre pendant le scroll.
          let low = 0;
          let high = headings.length;
          while (low < high) {
            const mid = (low + high) >> 1;
            if (headings[mid].top <= limit) low = mid + 1;
            else high = mid;
          }
          const activeHeading = headings.length ? headings[Math.max(0, low - 1)] : null;
          this.activeSection = activeHeading?.id || (this.lessonToc[0] ? this.lessonToc[0].id : '');
          const headingTop = activeHeading && activeHeading.id === this.activeSection ? activeHeading.top : 0;

          const currentPosition = this.lessonPositions[courseId] || null;
          const positionChanged = !currentPosition
            || Math.abs(Number(currentPosition.scrollTop || 0) - el.scrollTop) >= 180
            || Math.abs(Number(currentPosition.progress || 0) - this.lessonProgress) >= 3
            || String(currentPosition.sectionId || '') !== String(this.activeSection || '');
          if (positionChanged || this.lessonProgress === 0 || this.lessonProgress === 100) {
            this.saveLessonPosition(courseId, {
              scrollTop: Math.round(el.scrollTop),
              progress: this.lessonProgress,
              sectionId: this.activeSection || '',
              sectionOffset: Math.max(0, Math.round(el.scrollTop - headingTop)),
            });
          }

          if (courseId === String(this.lastOpenedNodeId)) {
            const progress = this.lessonProgress;
            if (progress === 0 || progress === 100 || Math.abs(progress - this.lastLessonProgress) >= 3) {
              this.lastLessonProgress = progress;
              try { localStorage.setItem('skilltree-last-progress', String(progress)); } catch (e) { }
            }
          }
        },

        goToSection(id) {
          this.startSectionSelection = String(id || '__resume__');
          const article = this.$refs.lessonArticle;
          const wantedId = String(id || '');
          const el = article && wantedId
            ? Array.from(article.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]')).find(heading => heading.id === wantedId)
            : null;
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        },

        // La séquence du lecteur est limitée au module du cours ouvert.
        // Le champ order est local au module : plusieurs modules peuvent partager la même valeur.
        get lessonNavigationModule() {
          if (this.detail) return this.moduleOf(this.detail);
          return this.moduleFilter && this.moduleFilter !== 'all' ? this.moduleFilter : null;
        },
        orderedModuleLessons(moduleId) {
          const nodes = Array.isArray(this.nodes) ? this.nodes : [];
          if (!moduleId || moduleId === 'all') return [];
          return nodes
            .filter(node => this.moduleOf(node) === moduleId)
            .map((node, index) => {
              const rawOrder = node.order ?? node.sort_order;
              const order = rawOrder === null || rawOrder === undefined || rawOrder === '' ? Number.NaN : Number(rawOrder);
              const rawCatalogIndex = node.catalog_index;
              const catalogIndex = rawCatalogIndex === null || rawCatalogIndex === undefined || rawCatalogIndex === '' ? Number.NaN : Number(rawCatalogIndex);
              return { node, index, order, catalogIndex };
            })
            .sort((a, b) => {
              const aHasOrder = Number.isFinite(a.order);
              const bHasOrder = Number.isFinite(b.order);
              if (aHasOrder && bHasOrder && a.order !== b.order) return a.order - b.order;
              if (aHasOrder !== bHasOrder) return aHasOrder ? -1 : 1;
              const aHasCatalogIndex = Number.isFinite(a.catalogIndex);
              const bHasCatalogIndex = Number.isFinite(b.catalogIndex);
              if (aHasCatalogIndex && bHasCatalogIndex && a.catalogIndex !== b.catalogIndex) return a.catalogIndex - b.catalogIndex;
              if (aHasCatalogIndex !== bHasCatalogIndex) return aHasCatalogIndex ? -1 : 1;
              return a.index - b.index;
            })
            .map(item => item.node);
        },
        get lessonSequence() {
          const nodes = Array.isArray(this.nodes) ? this.nodes : [];
          const activeModule = this.lessonNavigationModule;
          if (activeModule) return this.orderedModuleLessons(activeModule);

          // Sans module sélectionné, regrouper les cours par ordre des modules, puis par ordre local.
          return nodes
            .map((node, index) => {
              const rawOrder = node.order ?? node.sort_order;
              const order = rawOrder === null || rawOrder === undefined || rawOrder === '' ? Number.NaN : Number(rawOrder);
              const rawCatalogIndex = node.catalog_index;
              const catalogIndex = rawCatalogIndex === null || rawCatalogIndex === undefined || rawCatalogIndex === '' ? Number.NaN : Number(rawCatalogIndex);
              const modulePos = this.modules.findIndex(module => module.id === this.moduleOf(node));
              return { node, index, order, catalogIndex, moduleIndex: modulePos >= 0 ? modulePos : this.modules.length };
            })
            .sort((a, b) => {
              if (a.moduleIndex !== b.moduleIndex) return a.moduleIndex - b.moduleIndex;
              const aHasOrder = Number.isFinite(a.order);
              const bHasOrder = Number.isFinite(b.order);
              if (aHasOrder && bHasOrder && a.order !== b.order) return a.order - b.order;
              if (aHasOrder !== bHasOrder) return aHasOrder ? -1 : 1;
              const aHasCatalogIndex = Number.isFinite(a.catalogIndex);
              const bHasCatalogIndex = Number.isFinite(b.catalogIndex);
              if (aHasCatalogIndex && bHasCatalogIndex && a.catalogIndex !== b.catalogIndex) return a.catalogIndex - b.catalogIndex;
              if (aHasCatalogIndex !== bHasCatalogIndex) return aHasCatalogIndex ? -1 : 1;
              return a.index - b.index;
            })
            .map(item => item.node);
        },
        get lessonCurrentIndex() {
          if (!this.detail) return 0;
          const index = this.lessonSequence.findIndex(node => String(node.id) === String(this.detail.id));
          return index >= 0 ? index + 1 : 0;
        },
        get lessonNeighbors() {
          if (!this.detail) return { prev: null, next: null };
          const sequence = this.lessonSequence;
          const index = sequence.findIndex(node => String(node.id) === String(this.detail.id));
          return {
            prev: index > 0 ? sequence[index - 1] : null,
            next: index >= 0 && index < sequence.length - 1 ? sequence[index + 1] : null,
          };
        },

        async show(nodeId) {
          this.stopLearningProgressSync({ flush: true });
          this.labWorkspaceFallbackId = null;
          const nodeKey = String(nodeId);
          this.moduleNextCourseId = null;
          const requestId = ++this._detailRequestId;
          const resumingSameLesson = nodeKey === String(this.lastOpenedNodeId || '');
          const savedPosition = this.lessonPositions[nodeKey] || null;
          this.resetLessonHeadingOffsets();
          this.lastOpenedNodeId = nodeKey;
          this.lastOpenedNodeStatus = this.nodes.find(node => String(node.id) === nodeKey)?.status || '';
          this.detailRequestedNodeId = nodeKey;
          this.startSectionSelection = '__resume__';
          if (savedPosition && Number.isFinite(Number(savedPosition.progress))) {
            this.lastLessonProgress = Math.max(0, Math.min(100, Number(savedPosition.progress)));
          } else if (!resumingSameLesson) {
            this.lastLessonProgress = 0;
          }
          try {
            localStorage.setItem('skilltree-last-node', nodeKey);
            if (this.lastOpenedNodeStatus) localStorage.setItem('skilltree-last-status', this.lastOpenedNodeStatus);
            else localStorage.removeItem('skilltree-last-status');
            if (!resumingSameLesson) localStorage.removeItem('skilltree-last-progress');
          } catch (e) { }
          this.open = true;
          this.detailLoading = true;
          this.detailLoadError = null;
          this.exerciseBusy = false; this.quizBusy = false; this.exerciseError = null;
          this.stopSpeech();
          this.tutorOpen = false; this.tutorQuestion = ''; this.tutorMessages = []; this.tutorSelectedText = '';
          this.detail = null;
          this.learningProgress = null;
          this.learningProgressError = '';
          this.lessonHtml = '';
          this.lessonMissing = false;
          this.lessonIsPlaceholder = false;
          this.modalTab = 'lesson'; this.quiz = null; this.quizResult = null; this.exerciseMode = null; this.exercisePreferredKind = null;
          this.labRunning = false; this.labValidation = null; this.labOutput = []; this.labError = null;
          this.lessonProgress = 0; this.lessonToc = []; this.activeSection = '';

          try {
            const r = await fetch(`/api/node/${encodeURIComponent(nodeKey)}`);
            if (requestId !== this._detailRequestId) return;
            if (!r.ok) throw new Error(`Impossible de charger le cours (HTTP ${r.status}).`);
            const detail = await r.json();
            if (requestId !== this._detailRequestId) return;
            this.detail = detail;

            const l = await fetch(`/api/node/${encodeURIComponent(nodeKey)}/lesson`);
            if (requestId !== this._detailRequestId) return;
            if (l.ok) {
              const md = await l.text();
              if (requestId !== this._detailRequestId) return;
              if (this.isLessonPlaceholder(md)) {
                this.lessonHtml = '';
                this.lessonIsPlaceholder = true;
                this.lessonToc = [];
                this.readingMinutes = 0;
              } else {
                this.lessonIsPlaceholder = false;
                await Promise.all([
                  window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/marked@15.0.7/marked.min.js', 'marked'),
                  window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js', 'DOMPurify'),
                ]);
                const rawHtml = this.formatMarkdown(md);
                this.lessonHtml = window.DOMPurify.sanitize(rawHtml);
                this.lessonMissing = false;
              }
            }
            else { this.lessonHtml = ''; this.lessonMissing = true; }
          } catch (e) {
            if (requestId === this._detailRequestId) {
              this.detail = null;
              this.lessonHtml = '';
              this.lessonMissing = false;
              this.detailLoadError = e && e.message ? e.message : 'Une erreur inattendue empêche le chargement. Vérifie la connexion puis réessaie.';
              console.error("Erreur chargement", e);
            }
          } finally {
            if (requestId === this._detailRequestId) {
              this.detailLoading = false;
              this.$nextTick(async () => {
                if (requestId !== this._detailRequestId || !this.open || this.detailLoadError) return;
                await this.renderLessonDiagrams();
                if (requestId !== this._detailRequestId || !this.open || this.detailLoadError) return;
                const s = this.$refs.modalScroll;
                this.refreshLessonHeadingOffsets();
                this.observeLessonHeadingLayout();
                if (s) this.restoreLessonPosition(s, this.lessonPositions[String(this.detail?.id || '')] || null);
                this.startLearningProgressSync(String(this.detail?.id || ''));
                this.fixLessonContrast();
              });
            }
          }
        },

        close() {
          if (this.open && this.modalTab === 'lesson' && this.$refs.modalScroll) {
            this.onLessonScroll({ target: this.$refs.modalScroll });
          }
          this.resetLessonHeadingOffsets();
          this._detailRequestId += 1;
          this.stopSpeech();
          this.stopLearningProgressSync({ flush: true });
          this.open = false;
          this.detailLoading = false;
          this.detailLoadError = null;
          this.detailRequestedNodeId = null;
          this.detail = null;
          this.tutorOpen = false;
        },

        canStartExercise() { return this.detail?.requirements?.some(r => ['quiz', 'terminal'].includes(r.kind)) || false; },
        async startExercise() {
          this.quizResult = null; this.exerciseResult = null; this.exerciseAnswer = '';
          const preferredKind = this.exercisePreferredKind;
          this.exercisePreferredKind = null;
          if ((preferredKind === 'terminal' || (!preferredKind && this.detail.terminal)) && this.detail.terminal) {
            this.exerciseMode = 'terminal'; this.exerciseQuestion = this.detail.terminal;
          } else {
            const r = await fetch(`/api/node/${this.detail.id}/quiz`);
            if (!r.ok) {
              this.notify('Impossible de charger le quiz (' + r.status + ').');
              return;
            }
            this.quiz = await r.json();
            this.exerciseMode = 'quiz'; this.quizAnswers = this.quiz.questions.map(q => null);
          }
        },
        clearResumeTargetAfterValidation(nodeId) {
          if (String(this.lastOpenedNodeId || '') !== String(nodeId)) return;
          this.lastOpenedNodeId = '';
          this.lastOpenedNodeStatus = '';
          this.lastLessonProgress = 0;
          try {
            localStorage.removeItem('skilltree-last-node');
            localStorage.removeItem('skilltree-last-status');
            localStorage.removeItem('skilltree-last-progress');
          } catch (e) { }
        },
        advanceResumeTargetAfterValidation(nodeId, requestId) {
          if (requestId !== this._detailRequestId || String(this.detail?.id) !== String(nodeId)) return;
          const node = this.nodes.find(item => String(item.id) === String(nodeId));
          if (!node || node.status !== 'validated' || this.allNodesValidated) return;

          // Une validation termine l'étape en cours : le prochain cours accessible
          // prend le relais. La même règle est appliquée par refreshAll aux labs.
          this.clearResumeTargetAfterValidation(nodeId);
        },
        async submitAnswer() {
          if (this.exerciseBusy || !this.detail?.id) return;
          const nodeId = String(this.detail.id);
          const requestId = this._detailRequestId;
          this.exerciseBusy = true;
          this.exerciseError = null;
          this.exerciseResult = null;
          let result;
          try {
            const response = await fetch(`/api/node/${encodeURIComponent(nodeId)}/submit-answer`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ answer: this.exerciseAnswer })
            });
            const raw = await response.text();
            try { result = raw ? JSON.parse(raw) : {}; }
            catch (_) { throw new Error(response.ok ? 'Le serveur a renvoyé une réponse illisible.' : `Erreur HTTP ${response.status}`); }
            if (!response.ok) throw new Error(result.detail || result.message || `Erreur HTTP ${response.status}`);
          } catch (error) {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) {
              this.exerciseError = `La réponse n’a pas pu être enregistrée : ${error.message || 'erreur réseau'}`;
            }
            if (requestId === this._detailRequestId) this.exerciseBusy = false;
            return;
          }

          if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) this.exerciseResult = result;
          try {
            const refreshed = await this.refreshAll();
            if (result.validated && refreshed.tree) this.advanceResumeTargetAfterValidation(nodeId, requestId);
            if (!refreshed.tree || !refreshed.dailyPlan) throw new Error('Actualisation du parcours incomplète.');
          } catch (error) {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) {
              this.exerciseError = 'Réponse enregistrée, mais la progression n’a pas pu être actualisée. Réessaie d’actualiser le tableau de bord.';
            }
          } finally {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) this.exerciseBusy = false;
          }
        },
        async submitQuiz() {
          if (this.quizBusy || !this.detail?.id) return;
          const nodeId = String(this.detail.id);
          const requestId = this._detailRequestId;
          this.quizBusy = true;
          this.exerciseError = null;
          this.quizResult = null;
          let result;
          try {
            const response = await fetch(`/api/node/${encodeURIComponent(nodeId)}/quiz`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ answers: this.quizAnswers })
            });
            const raw = await response.text();
            try { result = raw ? JSON.parse(raw) : {}; }
            catch (_) { throw new Error(response.ok ? 'Le serveur a renvoyé une réponse illisible.' : `Erreur HTTP ${response.status}`); }
            if (!response.ok) throw new Error(result.detail || result.message || `Erreur HTTP ${response.status}`);
          } catch (error) {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) {
              this.exerciseError = `Le quiz n’a pas pu être enregistré : ${error.message || 'erreur réseau'}`;
            }
            if (requestId === this._detailRequestId) this.quizBusy = false;
            return;
          }

          if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) this.quizResult = result;
          if (result.validated && requestId === this._detailRequestId && String(this.detail?.id) === nodeId) {
            await this.syncLearningProgress(nodeId, { force: true });
          }
          try {
            const refreshed = await this.refreshAll();
            if (result.validated && refreshed.tree) this.advanceResumeTargetAfterValidation(nodeId, requestId);
            if (!refreshed.tree || !refreshed.dailyPlan) throw new Error('Actualisation du parcours incomplète.');
          } catch (error) {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) {
              this.exerciseError = 'Résultat enregistré, mais la progression n’a pas pu être actualisée. Réessaie d’actualiser le tableau de bord.';
            }
          } finally {
            if (requestId === this._detailRequestId && String(this.detail?.id) === nodeId) this.quizBusy = false;
          }
        },

        async startLab() {
          this.labBusy = true;
          this.labError = null;
          this.labOutput = [];
          try {
            const r = await fetch('/api/lab/start', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ node_id: this.detail.id })
            });

            const text = await r.text();
            if (!r.ok) {
              throw new Error(text || `Erreur ${r.status}`);
            }

            const data = JSON.parse(text);

            this.labId = data.lab_id;
            this.labRunning = true;
            this.labOutput.push({ text: `Lab démarré (${data.container_id}).` });
            if(data.setup_logs) this.labOutput.push({ text: data.setup_logs });

          } catch (e) {
            this.labError = e.message;
          } finally {
            this.labBusy = false;
          }
        },
        async runLabCommand() {
          this.labOutput.push({ text: `$ ${this.labCommand}` });
          const cmd = this.labCommand; this.labCommand = '';
          const r = await fetch('/api/lab/exec', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lab_id: this.labId, command: cmd }) });
          const data = await r.json(); this.labOutput.push({ text: data.stdout || data.stderr });
        },
        async validateLab() {
          if (!this.labId || this.labBusy) return;
          this.labBusy = true;
          this.labValidation = null;
          this.labError = null;

          try {
            const r = await fetch('/api/lab/validate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ lab_id: this.labId })
            });

            const text = await r.text();
            if (!r.ok) throw new Error(text || `Erreur ${r.status}`);

            const data = JSON.parse(text);
            this.labValidation = data;
            this.labRunning = false;
            if (this.onLabValidated) this.onLabValidated(data);
            await this.refreshAll();

          } catch (e) {
            this.labError = e.message;
          } finally {
            this.labBusy = false;
          }
        },

        get categories() {
          const g = new Map();

          // 1. On filtre les nœuds selon le bouton cliqué (treeFilter)
          const filteredNodes = this.nodes.filter(n => {
            if (this.treeFilter === 'all') return true;

            const title = n.title.toLowerCase();

            if (this.treeFilter === 'beginner') {
              return title.includes('débutant') || title.includes('debutant');
            }
            if (this.treeFilter === 'intermediaire') {
              return title.includes('intermédiaire') || title.includes('intermediaire');
            }
            if (this.treeFilter === 'expert') {
              return title.includes('expert');
            }
            return true;
          });
          // 2. On regroupe les nœuds filtrés par catégorie
          for (const n of filteredNodes) {
            if (!g.has(n.category)) g.set(n.category, []);
            g.get(n.category).push(n);
          }

          // 3. On renvoie le résultat formaté pour l'affichage
          return [...g.entries()].map(([name, items]) => ({
            name,
            items,
            validated: items.filter(n => n.status === 'validated').length
          }));

        },
                get modulesList() {
          const grouped = new Map();
          for (const node of this.nodes || []) {
            const moduleId = this.moduleOf(node);
            const meta = this.moduleMeta(moduleId);
            const item = grouped.get(moduleId) || {
              id: moduleId,
              name: meta.label || moduleId || 'Module non classé',
              total: 0,
              validated: 0,
              icon: meta.icon || '📚',
            };
            item.total += 1;
            if (node.status === 'validated') item.validated += 1;
            grouped.set(moduleId, item);
          }
          return [...grouped.values()].map(item => ({
            ...item,
            progress: item.total ? Math.round((item.validated / item.total) * 100) : 0,
          }));
        },
        get progress() { return this.total ? Math.round((this.validated / this.total) * 100) : 0; },
        get currentFlashcard() { return this.flashcardQueue[0] || null; },
        get examCategories() { const g = new Map(); for (const n of this.nodes) { if (!g.has(n.category)) g.set(n.category, { name: n.category, nodes: 0 }); g.get(n.category).nodes++; } return [...g.values()]; },

        statusMeta(s) { return { validated: { label: 'Validé', text: 'text-emerald-400', icon: 'bg-emerald-500/10 text-emerald-400' }, in_progress: { label: 'En cours', text: 'text-cyan-300', icon: 'bg-cyan-500/10 text-cyan-300' }, available: { label: 'Disponible', text: 'text-fuchsia-400', icon: 'bg-fuchsia-500/10 text-fuchsia-400' }, locked: { label: 'Verrouillé', text: 'text-zinc-500', icon: 'bg-zinc-800 text-zinc-500' } }[s] || { label: s, text: 'text-zinc-500', icon: 'bg-zinc-800 text-zinc-500' }; },
        cardShell(s) { return { validated: 'bg-emerald-500/20 glow-lime', in_progress: 'bg-cyan-500/20', available: 'bg-fuchsia-500/20 glow-fuchsia', locked: 'bg-white/5' }[s] || 'bg-white/5'; },
        kindLabel(k) { return k === 'quiz' ? 'Exercice' : k; },
        planMeta(action) {
          const type = typeof action === 'string' ? action : action?.action;
          const status = action && typeof action === 'object' ? action.status : null;
          const meta = {
            challenge: status === 'available'
              ? { label: 'Défi à relever', classes: 'text-emerald-300 bg-emerald-500/10' }
              : { label: 'Défi à poursuivre', classes: 'text-cyan-300 bg-cyan-500/10' },
            lab: status === 'available'
              ? { label: 'Lab à lancer', classes: 'text-emerald-300 bg-emerald-500/10' }
              : { label: 'Lab à poursuivre', classes: 'text-orange-300 bg-orange-500/10' },
            continue: { label: 'À reprendre', classes: 'text-violet-300 bg-violet-500/10' },
            review: { label: 'Révision', classes: 'text-amber-300 bg-amber-500/10' },
            start: { label: 'À découvrir', classes: 'text-emerald-300 bg-emerald-500/10' },
          };
          return meta[type] || { label: 'Parcours', classes: 'text-zinc-300 bg-white/5' };
        },
        async openPlanAction(action) {
          if (!action || !action.node_id) return;
          const nodeId = String(action.node_id);
          if (action.action === 'challenge') {
            await this.setTab('challenges');
            
            await this.$nextTick();
            await this.startChallenge(nodeId);
            return;
          }
          if (action.action === 'lab') {
            await this.openLab(nodeId, true);
            return;
          }
          if (action.action === 'review') {
            // Les révisions du plan journalier ouvrent directement les cartes du cours ciblé.
            this.reviewNodeId = nodeId;
            this.reviewDaysSince = Number(action.days_since) || null;
            this.cardFilter = { ...this.cardFilter, module: 'all', level: 'all', mode: 'all' };
            await this.setTab('memo');
            return;
          }
          await this.show(nodeId);
          if (action.action === 'continue' && ['quiz', 'terminal'].includes(action.next_requirement_kind)) {
            this.exercisePreferredKind = action.next_requirement_kind;
            this.modalTab = 'exercise';
          }
        },

        renderSpiderChart() {
          const canvas = document.getElementById('spiderChart');
          if (!canvas || !this.stats || !this.stats.categories) return;
          if (!window.Chart) {
            window.skillTreeLoadScript('https://cdn.jsdelivr.net/npm/chart.js', 'Chart')
              .then(() => {
                if (canvas.isConnected && window.Chart) this.renderSpiderChart();
              })
              .catch(error => console.warn('Chart.js indisponible.', error));
            return;
          }
          if (!canvas.isConnected || !window.Chart) return;
          if (window.spider) window.spider.destroy();
          window.spider = new window.Chart(canvas, { type: 'radar', data: { labels: this.stats.categories.map(c => c.name), datasets: [{ data: this.stats.categories.map(c => c.success_rate || 0), backgroundColor: `rgba(${rgbOf('--fuchsia-500')}, 0.2)`, borderColor: `rgb(${rgbOf('--fuchsia-500')})`, borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: false, scales: { r: { ticks: { display: false }, pointLabels: { color: '#e2e8f0' } } } } });
        },

        async startExam() {
          this.examBusy = true;
          const r = await fetch('/api/exam/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ category: this.examCategory }) });
          this.exam = await r.json(); this.examAnswers = this.exam.questions.map(q => null); this.examResult = null; this.examBusy = false;
        },
        async submitExam() {
          this.examBusy = true;
          const r = await fetch('/api/exam/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: this.exam.id, answers: this.examAnswers }) });
          this.examResult = await r.json(); await this.refreshAll(); this.examBusy = false;
        },
        resetExam() { this.exam = null; this.examResult = null; },

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
          this.topologyEditor = new window.Drawflow(el);
          this.topologyEditor.start();
          this.topologyReady = true;
        },
        addDevice(type) {
          if (!this.topologyEditor) return;
          const device = this.devices.find(d => d.type === type);
          const x = this.topologyEditor.precanvas.clientWidth / 2 - 90; const y = this.topologyEditor.precanvas.clientHeight / 2 - 30;
          const html = `<div class="topo-node"><span class="topo-icon">${device.icon}</span><span><span class="topo-label">${device.label}</span></span></div>`;
          this.topologyEditor.addNode(type, 1, 1, x, y, type, { label: device.label }, html, false);
        },
        zoom(d) { if (d > 0) this.topologyEditor.zoom_in(); else this.topologyEditor.zoom_out(); },
        zoomReset() { if (this.topologyEditor) this.topologyEditor.zoom_reset(); },
        async saveTopology() {
          const data = this.topologyEditor.export();
          await fetch('/api/topology', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
          alert("Topologie sauvegardée !");
        },

        flipFlashcard() { this.flashcardFlipped = !this.flashcardFlipped; },
        markFlashcard(known) { this.flashcardQueue.shift(); this.flashcardFlipped = false; },
        chooseDiagnostic(c) { this.diagnosticStep = this.diagnostic.steps[c.next]; },
        downloadCertificate() { window.location.href = '/api/certificate'; },

        async openShop() {
          this.shopOpen = true;
          try {
            const r = await fetch('/api/shop'); const data = await r.json();
            this.shopItems = data.items; this.userStats.coins = data.coins;
          } catch(e) { console.error(e); }
        },
        async buyItem(id) {
          const r = await fetch('/api/shop/buy', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ item_id: id }) });
          const data = await r.json();
          if(data.success) { this.userStats.coins = data.coins; alert("Acheté !"); }
          else { alert(data.detail || "Erreur"); }
        },
        // --- Lecture vocale serveur et assistant pédagogique ---
        speechSupported() {
          return typeof window !== 'undefined'
            && typeof window.fetch === 'function'
            && typeof window.Audio === 'function';
        },
        lessonSpeechButtonLabel() {
          if (this.speechKind === 'lesson' && this.speechState === 'speaking') return 'Mettre en pause';
          if (this.speechKind === 'lesson' && this.speechState === 'paused') return 'Reprendre la lecture';
          if (this.speechKind === 'lesson' && this.speechState === 'starting') return 'Préparation de l’audio…';
          return 'Écouter le cours';
        },
        speechStatusLabel() {
          if (this.speechState === 'paused') return 'Lecture en pause';
          if (this.speechState === 'starting') return 'Préparation du segment audio…';
          if (this.speechEngine === 'browser') return 'Lecture avec la voix de secours du navigateur';
          if (this.speechKind === 'lesson') return 'Lecture du cours en cours';
          if (this.speechKind === 'tutor') return 'Lecture de la réponse en cours';
          return '';
        },
        cleanSpeechVisualText(value) {
          return String(value || '')
            .replace(/\u00a0/gu, ' ')
            .replace(/<br\s*\/?\s*>/giu, ', ')
            .replace(/&nbsp;/giu, ' ')
            .replace(/\s*→\s*/gu, ' va vers ')
            .replace(/\s*↔\s*/gu, ' échange des données avec ')
            .replace(/\s*←\s*/gu, ' reçoit des données de ')
            .replace(/\s+/gu, ' ')
            .replace(/\s+([,.;:!?])/gu, '$1')
            .trim();
        },
        speechTextFromTabularRows(headers, dataRows, title = 'Tableau de données.') {
          const spoken = [title];
          const headerKey = value => String(value || '')
            .normalize('NFD')
            .replace(/\p{Diacritic}/gu, '')
            .toLocaleLowerCase('fr-FR')
            .replace(/[^a-z0-9]+/gu, ' ')
            .trim();
          const quoted = value => '« ' + value + ' »';
          const fieldPhrase = (header, rawValue) => {
            const value = String(rawValue || '').trim() || 'valeur non renseignée';
            const key = headerKey(header);
            if (/^ports?$|^port reseau$/u.test(key)) return 'le port utilisé est ' + value;
            if (/^(?:usage|utilite)$/u.test(key)) return 'l’usage indiqué est ' + quoted(value);
            if (/^(?:role|fonction)$/u.test(key)) return 'le rôle indiqué est ' + quoted(value);
            if (/^(?:description|definition)$/u.test(key)) return 'la description indique ' + quoted(value);
            if (/^(?:protocole|protocol)$/u.test(key)) return 'le protocole utilisé est ' + quoted(value);
            if (/^version$/u.test(key)) return 'la version est ' + quoted(value);
            if (/^(?:couche|niveau)$/u.test(key)) return 'la couche concernée est ' + quoted(value);
            if (/^(?:adresse|adresse ip|ip)$/u.test(key)) return 'l’adresse indiquée est ' + quoted(value);
            if (/^(?:statut|etat|status)$/u.test(key)) return 'l’état indiqué est ' + quoted(value);
            if (/^(?:avantage|point fort)$/u.test(key)) return 'un avantage est ' + quoted(value);
            if (/^(?:inconvenient|limite|point faible)$/u.test(key)) return 'une limite est ' + quoted(value);
            if (/^(?:commande|cmd)$/u.test(key)) return 'la commande à utiliser est ' + quoted(value);
            if (/^(?:resultat|sortie)$/u.test(key)) return 'le résultat est ' + quoted(value);
            if (header) return 'la valeur pour ' + String(header).toLocaleLowerCase('fr-FR') + ' est ' + quoted(value);
            return 'la valeur est ' + quoted(value);
          };

          if (headers.length > 1) {
            const details = headers.slice(1).map(value => String(value || '').trim()).filter(Boolean);
            spoken.push(details.length
              ? 'Les colonnes présentent un élément de référence, puis ses informations associées : ' + details.join(', ') + '.'
              : 'Les colonnes décrivent un élément de référence et ses informations associées.');
          } else if (headers.length === 1 && headers[0]) {
            spoken.push('La colonne porte sur ' + String(headers[0]).toLocaleLowerCase('fr-FR') + '.');
          }

          const firstHeaderKey = headerKey(headers[0] || '');
          const isStepColumn = /^(?:etape|phase|ordre|sequence|numero|rang|n)$/u.test(firstHeaderKey);
          if (!dataRows.length) {
            spoken.push('Le tableau ne contient aucune ligne de données.');
            return spoken;
          }

          dataRows.forEach((row, rowIndex) => {
            const values = Array.isArray(row) ? row : (row && Array.isArray(row.values) ? row.values : []);
            if (!values.length) return;
            const subject = String(values[0] || '').trim();
            const details = values.slice(1).map((value, index) => fieldPhrase(headers[index + 1] || '', value));

            if (isStepColumn && subject) {
              spoken.push('Étape ' + subject + (details.length ? ' : ' + details.join('; ') : '') + '.');
              return;
            }

            if (headers.length > 1 && subject && details.length) {
              spoken.push('Pour ' + subject + ', ' + details.join('; ') + '.');
              return;
            }

            const fields = values.map((value, columnIndex) => {
              const label = headers[columnIndex] || ('colonne ' + (columnIndex + 1));
              return String(label).toLocaleLowerCase('fr-FR') + ' : ' + (String(value || '').trim() || 'valeur non renseignée');
            });
            spoken.push('Ligne ' + (rowIndex + 1) + ', ' + fields.join('; ') + '.');
          });
          return spoken;
        },
        speechTextFromTable(table) {
          if (!table) return [];
          const cleanCell = cell => {
            const clone = cell.cloneNode(true);
            clone.querySelectorAll('button, script, style, .no-speech, [aria-hidden="true"]').forEach(node => node.remove());
            clone.querySelectorAll('svg').forEach(svg => {
              const label = svg.getAttribute('aria-label')
                || svg.querySelector('title, desc')?.textContent
                || '';
              if (label.trim()) svg.replaceWith(clone.ownerDocument.createTextNode(label.trim()));
              else svg.remove();
            });
            return this.cleanSpeechVisualText(clone.innerText || clone.textContent || '');
          };
          const rows = Array.from(table.querySelectorAll('tr'));
          if (!rows.length) return [];
          const caption = this.cleanSpeechVisualText(table.querySelector('caption')?.textContent || '');
          const firstRow = rows[0];
          const headerRow = table.querySelector('thead tr') || (
            firstRow && Array.from(firstRow.children).length
              && Array.from(firstRow.children).every(cell => cell.tagName === 'TH')
                ? firstRow
                : null
          );
          const headers = headerRow
            ? Array.from(headerRow.children).map(cleanCell)
            : [];
          const dataRows = rows.filter(row => row !== headerRow).map(row => ({
            values: Array.from(row.children).map(cleanCell),
            isRowHeader: row.querySelector('th[scope="row"]') !== null,
          }));
          const title = caption ? 'Tableau : ' + caption + '.' : 'Tableau de données.';
          return this.speechTextFromTabularRows(headers, dataRows, title);
        },
        isSpeechNetworkEquipment(value) {
          const label = this.cleanSpeechVisualText(String(value || ''));
          if (!label) return false;
          const equipmentWords = /\b(?:routeur|router|switch|commutateur|pare[\s-]?feu|firewall|serveur|server|client|ordinateur|computer|poste(?: de travail)?|point d['’ ]?acc[eè]s|access point|borne wi[\s-]?fi|modem|passerelle|gateway|spine|leaf|hub|bridge|nas|imprimante|printer|proxy|load balancer|équilibreur)\b/iu;
          const equipmentId = /^(?:pc|sw|s|r|rt|rtr|fw|ap|srv|gw|h|nas|esx|esxi|spine|leaf)[\s_-]*\d+[a-z]?$/iu;
          const baseLabel = label.replace(/[\s_-]*\d+[a-z]?$/iu, '');
          return equipmentWords.test(baseLabel) || equipmentId.test(label);
        },
        speechNetworkInventory(equipmentLabels, connectionCount) {
          const counts = new Map();
          (Array.isArray(equipmentLabels) ? equipmentLabels : []).forEach(value => {
            const label = this.cleanSpeechVisualText(String(value || ''));
            if (!label) return;
            const key = label.toLocaleLowerCase('fr-FR');
            const current = counts.get(key) || { label, count: 0 };
            current.count += 1;
            counts.set(key, current);
          });
          const equipmentCount = Array.from(counts.values()).reduce((sum, item) => sum + item.count, 0);
          const equipmentList = Array.from(counts.values())
            .map(item => item.count > 1 ? item.label + ' (' + item.count + ')' : item.label)
            .join(', ');
          const linkCount = Math.max(0, Number(connectionCount) || 0);
          const equipmentText = equipmentCount === 1 ? '1 équipement identifiable' : equipmentCount + ' équipements identifiables';
          const linkText = linkCount === 1
            ? '1 liaison directe identifiable entre équipements'
            : linkCount + ' liaisons directes identifiables entre équipements';
          const cableText = linkCount === 1 ? '1 câble physique' : linkCount + ' câbles physiques';
          return 'Inventaire du schéma : ' + equipmentText
            + (equipmentList ? ' (' + equipmentList + ')' : '')
            + ' et ' + linkText + '. Cela représente ' + cableText
            + ' uniquement si chaque liaison est physique ; les liens Wi-Fi et les flux logiques ne sont pas des câbles.';
        },
        speechTextFromAsciiDiagram(source) {
          const raw = String(source || '').replace(/\r\n?/gu, '\n');
          const lines = raw.split('\n').map(line => line.trim()).filter(Boolean);
          if (!lines.length) return [];
          const pipeRows = lines.filter(line => (line.match(/[|│]/gu) || []).length >= 2);
          const arrowLines = lines.filter(line => /(?:--+>|-{2,}|==>|->|<->|→|←|↔|⇒)/u.test(line));
          if (pipeRows.length >= 2 && arrowLines.length < 2) {
            const tabularRows = pipeRows
              .map(line => {
                const cells = line.split(/[|│]/u);
                if (cells.length && !cells[0].trim()) cells.shift();
                if (cells.length && !cells[cells.length - 1].trim()) cells.pop();
                return cells.map(value => this.cleanSpeechVisualText(value.replace(/^[\s+\-=:]+|[\s+\-=:]+$/gu, '')));
              })
              .filter(cells => cells.length >= 2 && !cells.every(value => !value || /^[-:=]+$/u.test(value)));
            if (tabularRows.length >= 2) {
              return this.speechTextFromTabularRows(tabularRows[0], tabularRows.slice(1), 'Tableau textuel.');
            }
          }
          const normalizeSegment = value => this.cleanSpeechVisualText(String(value || '')
            .replace(/[┌┐└┘├┤┬┴┼─━│┃╭╮╰╯╔╗╚╝╠╣╦╩╬║]/gu, ' ')
            .replace(/^[\s|+<>\-=_~.]+|[\s|+<>\-=_~.]+$/gu, '')
            .replace(/[\[\]{}]/gu, ' ')
            .replace(/^[\s|+]+|[\s|+]+$/gu, ''));
          const labelFor = value => normalizeSegment(value)
            .replace(/^(?:client|serveur|routeur|switch|firewall|internet)\s*$/iu, match => match);
          const relationships = [];
          const connectionPairs = [];
          const addConnection = (from, to) => {
            const left = labelFor(from);
            const right = labelFor(to);
            if (!left || !right || left.toLocaleLowerCase('fr-FR') === right.toLocaleLowerCase('fr-FR')) return;
            const key = [left.toLocaleLowerCase('fr-FR'), right.toLocaleLowerCase('fr-FR')].sort().join('::');
            if (!connectionPairs.some(item => item.key === key)) connectionPairs.push({ key, from: left, to: right });
          };
          const labels = [];
          const addLabel = value => {
            const label = labelFor(value);
            if (label && !/^[|+\-_=<>~.\s]+$/u.test(label) && !labels.some(item => item.toLocaleLowerCase('fr-FR') === label.toLocaleLowerCase('fr-FR'))) labels.push(label);
          };
          const connectors = /(\s*(?:<-->|<->|<--|<-|-->>|->>|-->|-\.->|==>|---|--o|--x|->|=>|←|↔|→|⇒|⇢|↑|↓|⇧|⇩)\s*)/gu;
          const isConnectorOnlyLine = line => {
            const value = String(line || '').trim();
            return Boolean(value)
              && /^[|│┃┌┐└┘├┤┬┴┼─━╭╮╰╯╔╗╚╝╠╣╦╩╬║+\-_=<>~.^v↑↓⇧⇩\s]+$/u.test(value)
              && /[|│┃^v↑↓⇧⇩]/u.test(value);
          };
          const hasInlineConnector = line =>
            /(?:<-->|<->|<--|<-|-->>|->>|-->|-\.->|==>|---|--o|--x|->|=>|←|↔|→|⇒|⇢|↑|↓|⇧|⇩)/u.test(line);
          const labelledLines = lines
            .map((line, index) => ({ index, label: normalizeSegment(line) }))
            .filter(item => item.label && !isConnectorOnlyLine(lines[item.index]) && !hasInlineConnector(lines[item.index]));

          // Les schémas ASCII verticaux placent souvent la flèche sur sa propre ligne.
          // Relier les deux libellés voisins, sans transformer « v » ou « | » en éléments du schéma.
          for (let index = 0; index < labelledLines.length - 1; index += 1) {
            const upper = labelledLines[index];
            const lower = labelledLines[index + 1];
            const connectorLines = lines.slice(upper.index + 1, lower.index);
            if (!connectorLines.length || !connectorLines.some(isConnectorOnlyLine)) continue;
            const marks = connectorLines.join(' ');
            const pointsUp = /[\^↑⇧]/u.test(marks);
            const pointsDown = /(?:↓|⇩|(?:^|\s)v(?:\s|$))/u.test(marks);
            let from = upper.label;
            let to = lower.label;
            if (pointsUp && !pointsDown) [from, to] = [lower.label, upper.label];
            addConnection(from, to);
            addLabel(from);
            addLabel(to);
            const relation = pointsUp && !pointsDown
              ? 'Le schéma relie le bloc « ' + from + ' » au bloc « ' + to + ' »'
              : pointsDown && !pointsUp
                ? 'Le schéma relie le bloc « ' + from + ' » au bloc « ' + to + ' »'
                : 'Les blocs « ' + from + ' » et « ' + to + ' » sont reliés verticalement';
            if (!relationships.includes(relation)) relationships.push(relation);
          }

          const relationLine = line => {
            if (!/[<>→←↔⇒⇢↑↓⇧⇩]|--|==|->/u.test(line)) return;
            const pieces = line.split(connectors).filter(Boolean);
            if (pieces.length < 3) return;
            const endpoints = [];
            const arrows = [];
            for (let index = 0; index < pieces.length; index += 1) {
              if (index % 2 === 0) {
                const value = normalizeSegment(pieces[index]);
                if (value) endpoints.push(value);
              } else {
                arrows.push(String(pieces[index] || '').trim());
              }
            }
            if (endpoints.length < 2) return;
            for (let index = 0; index < endpoints.length - 1; index += 1) {
              let from = endpoints[index];
              let to = endpoints[index + 1];
              const arrow = arrows[index] || '->';
              if (/^(?:<--|<-|←|↑|⇧)$/u.test(arrow)) [from, to] = [to, from];
              addConnection(from, to);
              addLabel(from);
              addLabel(to);
              const relation = /^(?:<-->|<->|↔)$/u.test(arrow)
                ? 'Les blocs « ' + from + ' » et « ' + to + ' » sont reliés dans les deux sens'
                : 'Le schéma relie le bloc « ' + from + ' » au bloc « ' + to + ' »';
              if (!relationships.includes(relation)) relationships.push(relation);
            }
          };
          lines.forEach(line => {
            if (isConnectorOnlyLine(line)) return;
            relationLine(line);
            const withoutBorders = line
              .replace(/[┌┐└┘├┤┬┴┼─━│┃╭╮╰╯╔╗╚╝╠╣╦╩╬║]/gu, ' ')
              .replace(/^[\s|+]+|[\s|+]+$/gu, '')
              .replace(/[-=<>~]{2,}/gu, ' ')
              .replace(/\s{2,}/gu, ', ');
            if (withoutBorders && !/^[\s|+\-_=<>~.]*$/u.test(withoutBorders)) {
              withoutBorders.split(/\s*,\s*/u).forEach(addLabel);
            }
          });
          const spoken = [];
          const equipment = labels.filter(label => this.isSpeechNetworkEquipment(label));
          const equipmentConnectionPairs = connectionPairs.filter(pair =>
            this.isSpeechNetworkEquipment(pair.from) && this.isSpeechNetworkEquipment(pair.to)
          );
          if (equipment.length && connectionPairs.length) {
            spoken.push(this.speechNetworkInventory(equipment, equipmentConnectionPairs.length));
          }
          if (relationships.length) spoken.push(relationships.map(value => value + '.').join(' '));
          const unmentioned = labels.filter(label => !relationships.some(relation => relation.toLocaleLowerCase('fr-FR').includes(label.toLocaleLowerCase('fr-FR'))));
          if (unmentioned.length) spoken.push('Autres éléments représentés : ' + unmentioned.join(', ') + '.');
          const connectorOnlyLines = lines.filter(isConnectorOnlyLine).length;
          if (!spoken.length && labels.length && connectorOnlyLines > 0) {
            spoken.push('Schéma textuel. Les éléments sont reliés dans l’ordre suivant : ' + labels.join(', puis ') + '.');
          } else if (!spoken.length && labels.length) {
            spoken.push('Schéma textuel. Les éléments représentés, dans l’ordre visuel, sont : ' + labels.join(', ') + '.');
          }
          if (!spoken.length) spoken.push('Schéma textuel. Le diagramme présente des éléments reliés visuellement ; le texte explicatif qui l’accompagne précise le sens des relations.');
          return spoken;
        },
        speechTextFromMermaidDiagram(source, svg) {
          const raw = String(source || '').replace(/\r\n?/gu, '\n');
          const nodes = new Map();
          const cleanLabel = value => this.cleanSpeechVisualText(String(value || '')
            .replace(/<br\s*\/?\s*>/giu, ', ')
            .replace(/<[^>]*>/gu, ' ')
            .replace(/^['"`]|['"`]$/gu, ''));
          const nodePattern = /(?:^|[\s,])([A-Za-z_][\w.-]*)\s*(?:\[\[([^\]]+)\]\]|\[\(([^)]+)\)\]|\(\(([^)]+)\)\)|\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\})/gu;
          for (const line of raw.split('\n')) {
            if (/^\s*(?:%%|#)/u.test(line)) continue;
            for (const match of line.matchAll(nodePattern)) {
              const label = cleanLabel(match.slice(2).find(Boolean) || '');
              if (label) nodes.set(match[1], label);
            }
            const participant = line.match(/^\s*(?:participant|actor)\s+([A-Za-z_][\w.-]*)\s+as\s+(.+?)\s*$/iu);
            if (participant) nodes.set(participant[1], cleanLabel(participant[2]));
            const dotLabel = line.match(/^\s*([A-Za-z_][\w.-]*)\s*\[\s*label\s*=\s*["']([^"']+)["']/iu);
            if (dotLabel) nodes.set(dotLabel[1], cleanLabel(dotLabel[2]));
          }
          const resolveNode = token => {
            const idMatch = String(token || '').match(/[A-Za-z_][\w.-]*/u);
            if (!idMatch) return '';
            const id = idMatch[0];
            return nodes.get(id) || id.replace(/[-_]+/gu, ' ');
          };
          const relationships = [];
          const connections = [];
          const seen = new Set();
          const addRelation = value => {
            const clean = this.cleanSpeechVisualText(value);
            const key = clean.toLocaleLowerCase('fr-FR');
            if (clean && !seen.has(key)) { seen.add(key); relationships.push(clean); }
          };
          for (const line of raw.split('\n')) {
            if (/^\s*(?:%%|#|flowchart\b|graph\b|sequenceDiagram\b|classDiagram\b|stateDiagram\b|erDiagram\b|journey\b|gantt\b|mindmap\b|subgraph\b|end\s*$|direction\b|participant\b|actor\b|autonumber\b)/iu.test(line)) continue;
            const sequence = line.match(/^\s*([A-Za-z_][\w.-]*)\s*(-{1,}(?:>>|>|x|o)|={1,}>|\.{1,}-{1,}>|<-->|<--|<->)\s*([A-Za-z_][\w.-]*)\s*:\s*(.+?)\s*$/u);
            if (sequence) {
              const from = resolveNode(sequence[1]);
              const to = resolveNode(sequence[3]);
              const message = cleanLabel(sequence[4]);
              addRelation(from + ' envoie ' + (message ? 'le message « ' + message + ' »' : 'un message') + ' à ' + to + '.');
              continue;
            }
            const labelledEdge = line.match(/^\s*([A-Za-z_][\w.-]*)(?:\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}))?\s*(-->|-\.->|==>|---|->|=>|→|⇒)\s*\|([^|]+)\|\s*([A-Za-z_][\w.-]*)/u);
            const dashedLabelEdge = line.match(/^\s*([A-Za-z_][\w.-]*)(?:\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}))?\s+--\s+(.+?)\s+-->\s*([A-Za-z_][\w.-]*)/u);
            const simpleEdge = line.match(/^\s*([A-Za-z_][\w.-]*)(?:\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}))?\s*(<-->|<->|<--|<-|-->|-\.->|==>|---|--o|--x|->|=>|→|←|↔|⇒|⇢)\s*([A-Za-z_][\w.-]*)(?:\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}))?/u);
            const edge = labelledEdge
              ? { from: labelledEdge[1], to: labelledEdge[4], label: cleanLabel(labelledEdge[3]), arrow: labelledEdge[2] }
              : dashedLabelEdge
                ? { from: dashedLabelEdge[1], to: dashedLabelEdge[3], label: cleanLabel(dashedLabelEdge[2]), arrow: '-->' }
                : simpleEdge
                  ? { from: simpleEdge[1], to: simpleEdge[3], label: '', arrow: simpleEdge[2] }
                  : null;
            if (!edge) continue;
            let from = resolveNode(edge.from);
            let to = resolveNode(edge.to);
            if (/^(?:<--|<-|←)$/u.test(edge.arrow)) [from, to] = [to, from];
            connections.push({ fromId: edge.from, toId: edge.to, from, to });
            const relation = /^(?:<-->|<->|↔)$/u.test(edge.arrow)
              ? 'Les blocs « ' + from + ' » et « ' + to + ' » sont reliés dans les deux sens'
              : 'Le schéma relie le bloc « ' + from + ' » au bloc « ' + to + ' »';
            addRelation(relation + (edge.label ? ' en passant par ' + edge.label : '') + '.');
          }

          const svgLabels = [];
          if (svg) {
            const svgTextNodes = Array.from(svg.querySelectorAll('text'));
            const candidates = svgTextNodes.length
              ? svgTextNodes
              : Array.from(svg.querySelectorAll('foreignObject, title, desc, [aria-label]'));
            candidates.forEach(node => {
              const label = cleanLabel(node.textContent || node.getAttribute('aria-label') || '');
              if (label && !svgLabels.some(item => item.toLocaleLowerCase('fr-FR') === label.toLocaleLowerCase('fr-FR'))) svgLabels.push(label);
            });
          }
          const allLabels = [];
          nodes.forEach(value => allLabels.push(value));
          svgLabels.forEach(value => {
            if (!allLabels.some(item => item.toLocaleLowerCase('fr-FR') === value.toLocaleLowerCase('fr-FR'))) allLabels.push(value);
          });
          const spoken = [];
          const equipment = Array.from(nodes.entries())
            .filter(([id, label]) => this.isSpeechNetworkEquipment(label) || this.isSpeechNetworkEquipment(id))
            .map(([, label]) => label);
          const equipmentConnections = connections.filter(connection =>
            (this.isSpeechNetworkEquipment(connection.from) || this.isSpeechNetworkEquipment(connection.fromId))
            && (this.isSpeechNetworkEquipment(connection.to) || this.isSpeechNetworkEquipment(connection.toId))
          );
          if (equipment.length && connections.length) {
            spoken.push(this.speechNetworkInventory(equipment, equipmentConnections.length));
          }
          if (relationships.length) spoken.push(relationships.join(' '));
          const otherLabels = allLabels.filter(label =>
            !relationships.some(relation => relation.toLocaleLowerCase('fr-FR').includes(label.toLocaleLowerCase('fr-FR')))
          );
          if (otherLabels.length) spoken.push(
            (relationships.length ? 'Autres libellés du schéma : ' : 'Les éléments représentés sont : ')
              + otherLabels.join(', ') + '.'
          );
          if (!spoken.length) {
            const guide = '';
            spoken.push(guide || 'Diagramme. Les éléments visuels ne possèdent pas tous un libellé lisible ; consulte aussi la description textuelle du cours.');
          }
          return spoken;
        },
        speechTextFromDiagramRoot(root) {
          if (!root) return [];
          const table = root.querySelector('table') || (root.matches('table') ? root : null);
          if (table) {
            const spokenTable = this.speechTextFromTable(table);
            const figureCaption = this.cleanSpeechVisualText(root.querySelector('figcaption')?.textContent || '');
            const tableCaption = this.cleanSpeechVisualText(table.querySelector('caption')?.textContent || '');
            if (figureCaption && figureCaption.toLocaleLowerCase('fr-FR') !== tableCaption.toLocaleLowerCase('fr-FR')) {
              spokenTable.unshift('Tableau : ' + figureCaption + '.');
            }
            return spokenTable;
          }
          const captionNode = root.querySelector('figcaption');
          const titleNode = root.querySelector('svg title, svg desc, title, desc');
          const image = root.querySelector('img[alt], img[title]') || (root.matches('img') ? root : null);
          const caption = this.cleanSpeechVisualText(
            (captionNode && captionNode.textContent) ||
            (titleNode && titleNode.textContent) ||
            (image && (image.getAttribute('alt') || image.getAttribute('title'))) ||
            root.getAttribute('aria-label') || ''
          );
          const sourceNode = root.querySelector('.lesson-mermaid-source, .mermaid[data-original-source], pre code, pre');
          const source = sourceNode
            ? String(sourceNode.dataset?.originalSource || sourceNode.textContent || '').trim()
            : '';
          const svg = root.querySelector('svg') || (root.matches('svg') ? root : null);
          const lang = this.cleanSpeechVisualText(root.querySelector('.code-lang')?.textContent || '').toLocaleLowerCase('fr-FR');
          const ascii = /(?:ascii|diagram|flowchart|graphviz|dot|plantuml|puml|d2)/u.test(lang)
            || root.dataset.diagramType === 'schéma textuel'
            || /[┌┐└┘├┤┬┴┼─│╭╮╰╯↔↕←→↑↓]/u.test(source)
            || /(?:--+>|-{2,}|==>|->|<->|→|←|↔)/u.test(source)
            || source.split(/\r?\n/u).filter(line => (line.match(/[|│]/gu) || []).length >= 2).length >= 2;
          const spoken = [];
          if (caption) spoken.push((root.dataset.diagramType || 'Schéma') + ' : ' + caption + '.');
          if (source && /(?:flowchart\b|graph\s+(?:TD|TB|BT|RL|LR)|sequenceDiagram\b|classDiagram\b|stateDiagram\b|erDiagram\b)/iu.test(source)) {
            spoken.push(...this.speechTextFromMermaidDiagram(source, svg));
          } else if (source && ascii) {
            spoken.push(...this.speechTextFromAsciiDiagram(source));
          } else if (svg) {
            const textNodes = Array.from(svg.querySelectorAll('text'));
            const candidates = textNodes.length ? textNodes : Array.from(svg.querySelectorAll('foreignObject, title, desc, [aria-label]'));
            const labels = candidates
              .map(node => this.cleanSpeechVisualText(node.textContent || node.getAttribute('aria-label') || ''))
              .filter(Boolean);
            const uniqueLabels = labels.filter((label, index) => labels.findIndex(other => other.toLocaleLowerCase('fr-FR') === label.toLocaleLowerCase('fr-FR')) === index);
            if (uniqueLabels.length) spoken.push('Les éléments visibles du schéma sont : ' + uniqueLabels.join(', ') + '.');
          } else if (!source && !image) {
            // Certains schémas sont de simples blocs HTML (boîtes, colonnes, flèches CSS),
            // sans source ASCII ni SVG. Lire leurs libellés visibles au lieu du guide générique.
            const visualCopy = root.cloneNode(true);
            visualCopy.querySelectorAll('.lesson-diagram-toolbar, .lesson-diagram-guide, .code-header, .lesson-diagram-kind, figcaption, button, script, style, [aria-hidden="true"]').forEach(node => node.remove());
            const visualText = this.cleanSpeechVisualText(visualCopy.innerText || visualCopy.textContent || '');
            if (visualText) spoken.push('Le schéma se lit ainsi : ' + visualText + '.');
          }
          if (image) {
            const alt = this.cleanSpeechVisualText(image.getAttribute('alt') || image.getAttribute('title') || '');
            if (alt && alt.toLocaleLowerCase('fr-FR') !== caption.toLocaleLowerCase('fr-FR')) spoken.push('Description de l’illustration : ' + alt + '.');
          }
          if (spoken.length === 0) {
            const guide = root.querySelector('.lesson-diagram-guide p');
            const guideText = this.cleanSpeechVisualText(guide?.textContent || '');
            spoken.push(guideText || 'Schéma. Le dessin est accompagné de son texte explicatif dans le cours.');
          }
          return spoken;
        },
        speechTextFromArticle(startBlockId = undefined) {
          const article = this.$refs.lessonArticle;
          if (!article) return '';
          const readable = article.cloneNode(true);
          const explicitBlockStart = startBlockId !== undefined && startBlockId !== null;
          const selectedStart = explicitBlockStart ? String(startBlockId) : this.startSectionSelection;
          const requestedStart = explicitBlockStart
            ? ''
            : (selectedStart === '__top__'
              ? ''
              : (selectedStart && selectedStart !== '__resume__' ? selectedStart : this.activeSection));
          let target = null;

          if (explicitBlockStart) {
            target = Array.from(readable.querySelectorAll('[data-speech-start-id]'))
              .find(element => element.getAttribute('data-speech-start-id') === selectedStart) || null;
          } else if (requestedStart) {
            target = Array.from(readable.querySelectorAll('h1, h2, h3, h4, h5, h6'))
              .find(heading => heading.id === requestedStart) || null;
          }

          // Une cible introuvable ne doit JAMAIS déclencher silencieusement une lecture depuis le début.
          if ((explicitBlockStart || requestedStart) && !target) return '';

          if (target) {
            let current = target;
            while (current && current.parentElement) {
              const parent = current.parentElement;
              let sibling = parent.firstChild;
              while (sibling && sibling !== current) {
                const next = sibling.nextSibling;
                sibling.remove();
                sibling = next;
              }
              if (parent === readable) break;
              current = parent;
            }
          }
          // Transformer les représentations visuelles en descriptions orales avant de retirer
          // leur HTML : ne jamais perdre les cellules d’un tableau ou les relations d’un schéma.
          readable.querySelectorAll('.lesson-diagram-block').forEach(root => {
            const spoken = this.speechTextFromDiagramRoot(root);
            if (!spoken.length) return;
            const fragment = readable.ownerDocument.createDocumentFragment();
            spoken.forEach(sentence => {
              const paragraph = readable.ownerDocument.createElement('p');
              paragraph.className = 'speech-visual-description';
              paragraph.textContent = sentence;
              fragment.appendChild(paragraph);
            });
            root.replaceWith(fragment);
          });

          // Filet de sécurité pour les tableaux non enveloppés par les enrichissements visuels.
          readable.querySelectorAll('table').forEach(table => {
            if (table.closest('.lesson-diagram-block')) return;
            const fragment = readable.ownerDocument.createDocumentFragment();
            this.speechTextFromTable(table).forEach(sentence => {
              const paragraph = readable.ownerDocument.createElement('p');
              paragraph.className = 'speech-visual-description';
              paragraph.textContent = sentence;
              fragment.appendChild(paragraph);
            });
            table.replaceWith(fragment);
          });

          readable.querySelectorAll('pre, code, kbd, samp, svg, table, img, button, details, video, audio, script, style, nav, aside, .lesson-toc-panel, .lesson-diagram-toolbar, .lesson-diagram-guide, .code-header, .no-speech, [aria-label*="sommaire" i]').forEach(element => element.remove());

          // Certains cours contiennent leur propre sommaire Markdown. Ne pas le réciter comme un paragraphe :
          // on retire uniquement les listes composées exclusivement de liens internes vers des titres.
          const courseHeadingIds = new Set(Array.from(readable.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(heading => heading.id).filter(Boolean));
          readable.querySelectorAll('ul, ol').forEach(list => {
            const items = Array.from(list.children).filter(item => item.tagName === 'LI');
            if (!items.length) return;
            const isContentsList = items.every(item => {
              const links = Array.from(item.querySelectorAll('a'));
              if (links.length !== 1) return false;
              const href = links[0].getAttribute('href') || '';
              if (!href.startsWith('#')) return false;
              const label = links[0].textContent.trim();
              return courseHeadingIds.has(href.slice(1)) || Array.from(readable.querySelectorAll('h1, h2, h3, h4, h5, h6')).some(heading => heading.textContent.trim() === label);
            });
            if (!isContentsList) return;
            const heading = list.previousElementSibling;
            list.remove();
            if (heading && /^H[1-6]$/.test(heading.tagName) && /^(sommaire|table des matières|table des matieres|plan du cours)$/iu.test(heading.textContent.trim())) heading.remove();
          });

          // Préserver les signes de ponctuation du cours et ne jamais inventer de ponctuation à la fin d'un bloc.
          // Les titres ont une annonce dédiée ; le texte pédagogique garde ses signes d'origine.
          // Une ligne Markdown terminée par un saut forcé (<br>) est une unité de lecture distincte.
          // La séparer en paragraphes évite de lire plusieurs champs de contexte comme une seule phrase.
          readable.querySelectorAll('p').forEach(paragraph => {
            if (!paragraph.querySelector('br')) return;
            const parts = [];
            let part = paragraph.cloneNode(false);
            Array.from(paragraph.childNodes).forEach(node => {
              if (node.nodeType === 1 && node.tagName === 'BR') {
                if (part.textContent.trim()) parts.push(part);
                part = paragraph.cloneNode(false);
              } else {
                part.appendChild(node.cloneNode(true));
              }
            });
            if (part.textContent.trim()) parts.push(part);
            if (parts.length < 2) return;
            parts.forEach(piece => paragraph.parentNode.insertBefore(piece, paragraph));
            paragraph.remove();
          });

          readable.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
            const depth = Number(heading.tagName.slice(1));
            const title = String(heading.innerText || heading.textContent || '')
              .replace(/^\s*\d+(?:\.\d+)*[.)]?\s+/u, '')
              .replace(/[ \t]+/gu, ' ')
              .trim();
            if (!title) return;
            const label = depth === 1 ? 'Titre du cours' : (depth === 2 ? 'Section' : 'Sous-section');
            const spokenHeading = readable.ownerDocument.createElement('p');
            spokenHeading.textContent = label + ' : ' + title.replace(/[.!?…:;]+$/u, '') + '.';
            heading.replaceWith(spokenHeading);
          });

          // Les champs de contexte en gras sont lus comme un libellé puis une valeur,
          // avec une pause entre les deux au lieu d'enchaîner « libellé, valeur, libellé, valeur ».
          readable.querySelectorAll('p').forEach(paragraph => {
            const labelElement = paragraph.firstElementChild;
            if (!labelElement || paragraph.firstChild !== labelElement || !/^(STRONG|B)$/.test(labelElement.tagName)) return;
            const rawLabel = String(labelElement.textContent || '').trim();
            if (!/[:：]\s*$/u.test(rawLabel)) return;
            const label = rawLabel.replace(/[:：]\s*$/u, '').trim();
            let value = String(paragraph.textContent || '').slice(labelElement.textContent.length).trim();
            if (!label || !value) return;

            // À l'oral, les flèches d'un parcours expriment une progression, pas un symbole à lire.
            value = value.replace(/\s*→\s*/gu, ', puis ').replace(/[ \t]+/gu, ' ').trim();
            value = value.replace(/[,:;]+\s*$/u, '').trim();
            value = value.replace(/^([a-zà-ÿ])/u, letter => letter.toLocaleUpperCase('fr-FR'));
            if (!/[.!?…]$/u.test(value)) value += '.';

            const spokenLabel = readable.ownerDocument.createElement('p');
            spokenLabel.textContent = label + '.';
            const spokenValue = readable.ownerDocument.createElement('p');
            spokenValue.textContent = value;
            paragraph.replaceWith(spokenLabel, spokenValue);
          });

          // Les blocs restent séparés : le lecteur vocal peut respecter les pauses entre eux.
          readable.querySelectorAll('p, li, blockquote, figcaption').forEach(block => {
            block.append(readable.ownerDocument.createTextNode('\n\n'));
          });

          return (readable.innerText || readable.textContent || '')
            .replace(/\r\n?/g, '\n')
            // Les flèches insérées dans les phrases ou schémas inline doivent être dites en langage naturel.
            .replace(/\s*(?:<-->|<->|↔)\s*/gu, ' échange des données avec ')
            .replace(/\s*(?:<--|<-)\s*/gu, ' reçoit des données de ')
            .replace(/\s*(?:--+>|==>|=>|->|→|⇒)\s*/gu, ' va vers ')
            .replace(/[ \t]+/g, ' ')
            .replace(/\n[ \t]+/g, '\n')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
        },
        splitSpeechText(text, maxLength = 1800) {
          const normalized = String(text || '')
            .replace(/\r\n?/g, '\n')
            .replace(/[ \t]+/g, ' ')
            .replace(/\n[ \t]+/g, '\n')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
          if (!normalized) return [];

          const paragraphs = normalized.split(/\n{2,}/).map(part => part.replace(/\n+/g, ' ').trim()).filter(Boolean);
          const chunks = [];
          const appendSentence = sentence => {
            const clean = String(sentence || '').replace(/\s+/g, ' ').trim();
            if (!clean) return;

            // Garder la ponctuation : elle indique à la voix où respirer et quelle intonation adopter.
            // Le lecteur TTS n'a pas besoin qu'on supprime le point final pour éviter de le prononcer.
            if (clean.length <= maxLength) {
              chunks.push(clean);
              return;
            }

            // Couper uniquement les phrases exceptionnellement longues, en respectant les mots.
            let part = '';
            for (const word of clean.split(/\s+/)) {
              if (part && (part + ' ' + word).length > maxLength) {
                chunks.push(part);
                part = word;
              } else {
                part = part ? part + ' ' + word : word;
              }
            }
            if (part) chunks.push(part);
          };

          for (const paragraph of paragraphs) {
            let sentences;
            if (typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function') {
              const segmenter = new Intl.Segmenter('fr', { granularity: 'sentence' });
              sentences = Array.from(segmenter.segment(paragraph), item => item.segment.trim()).filter(Boolean);
            } else {
              // Le fallback conserve les points, interrogations, exclamations, points-virgules et deux-points.
              sentences = paragraph.split(/(?<=[.!?…;:])\s+/u).map(item => item.trim()).filter(Boolean);
            }
            // Garder plusieurs phrases voisines dans un même segment audio pour une prosodie
            // plus continue ; ne couper qu’aux limites de paragraphe ou lorsqu’un segment devient long.
            let group = '';
            sentences.forEach(sentence => {
              const candidate = group ? group + ' ' + sentence : sentence;
              if (group && candidate.length > maxLength) {
                appendSentence(group);
                group = sentence;
              } else {
                group = candidate;
              }
            });
            if (group) appendSentence(group);
          }
          return chunks;
        },
        async loadSpeechChunk(index, runId) {
          if (runId !== this._speechRunId) return null;
          if (this._speechAudioUrls[index]) return this._speechAudioUrls[index];
          if (this._speechAudioRequests[index]) return this._speechAudioRequests[index];

          const request = (async () => {
            const response = await fetch('/api/tts', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                text: this.speechQueue[index],
                rate: Math.max(0.8, Math.min(1.6, Number(this.speechRate) || 1)),
              }),
            });
            if (!response.ok) {
              let message = 'Impossible de générer la voix française.';
              try {
                const problem = await response.json();
                if (problem && problem.detail) message = problem.detail;
              } catch (_) { /* réponse d'erreur non JSON */ }
              throw new Error(message);
            }
            const blob = await response.blob();
            if (!blob.size) throw new Error('Le service vocal a renvoyé un segment audio vide.');
            const url = URL.createObjectURL(blob);
            if (runId !== this._speechRunId) {
              URL.revokeObjectURL(url);
              return null;
            }
            this._speechAudioUrls[index] = url;
            return url;
          })();

          this._speechAudioRequests[index] = request;
          try {
            return await request;
          } finally {
            if (this._speechAudioRequests[index] === request) delete this._speechAudioRequests[index];
          }
        },
        prefetchSpeechChunk(index, runId) {
          if (runId !== this._speechRunId || index >= this.speechQueue.length) return;
          this.loadSpeechChunk(index, runId).catch(() => {
            // Le segment sera retenté au moment de le lire, avec un message visible si l'échec persiste.
          });
        },
        async playSpeechChunk(index, runId) {
          if (runId !== this._speechRunId) return;
          if (index >= this.speechQueue.length) {
            this.finishSpeech(runId);
            return;
          }
          this.speechQueueIndex = index;
          this.speechError = null;

          try {
            const url = await this.loadSpeechChunk(index, runId);
            if (runId !== this._speechRunId || !url) return;
            const audio = this.$refs.speechAudio;
            if (!audio) throw new Error('Le lecteur audio du cours est introuvable.');

            audio.onended = () => this.onSpeechAudioEnded(runId, index);
            audio.onerror = () => this.onSpeechAudioError(runId, index);
            if (this._speechLoadedIndex !== index || audio.src !== url) {
              audio.pause();
              audio.src = url;
              audio.load();
              this._speechLoadedIndex = index;
            }
            if (this.speechState === 'paused') return;

            this.speechState = 'starting';
            await audio.play();
            if (runId !== this._speechRunId) return;
            this.speechState = 'speaking';
            this.prefetchSpeechChunk(index + 1, runId);
          } catch (error) {
            if (runId !== this._speechRunId) return;
            const message = error && error.message
              ? error.message
              : 'La lecture audio a échoué. Essaie de relancer la lecture.';
            if (!this.startBrowserSpeechFallback(runId, message)) {
              this.speechError = message;
              this.speechState = 'idle';
              this.speechKind = null;
              this.notify(this.speechError);
            }
          }
        },
        startBrowserSpeechFallback(failedRunId, serverError) {
          if (failedRunId !== this._speechRunId) return false;
          if (typeof window === 'undefined' || !('speechSynthesis' in window) || typeof window.SpeechSynthesisUtterance !== 'function') {
            this.speechError = serverError || 'La synthèse vocale est indisponible sur ce serveur et dans ce navigateur.';
            return false;
          }

          const kind = this.speechKind || 'lesson';
          const remainingText = this.speechQueue.slice(this.speechQueueIndex).join(' ');
          if (!remainingText.trim()) {
            this.speechError = serverError || 'Aucun texte restant à lire.';
            return false;
          }

          this.stopSpeech();
          this.speechEngine = 'browser';
          this.speechKind = kind;
          this.speechQueue = this.splitSpeechText(remainingText, 1000);
          this.speechQueueIndex = 0;
          this.speechState = 'starting';
          this.speechError = null;
          this.notify('La voix en ligne est indisponible : lecture de secours activée dans le navigateur.');
          this.speakNextBrowserChunk(this._speechRunId);
          return true;
        },
        speakNextBrowserChunk(runId) {
          if (runId !== this._speechRunId || this.speechEngine !== 'browser') return;
          if (this.speechQueueIndex >= this.speechQueue.length) {
            this.finishSpeech(runId);
            return;
          }

          const utterance = new window.SpeechSynthesisUtterance(this.speechQueue[this.speechQueueIndex]);
          utterance.lang = 'fr-FR';
          utterance.rate = Math.max(0.8, Math.min(1.6, Number(this.speechRate) || 1));
          const availableVoices = window.speechSynthesis.getVoices ? window.speechSynthesis.getVoices() : [];
          utterance.voice = availableVoices.find(voice => String(voice.lang || '').toLowerCase() === 'fr-fr')
            || availableVoices.find(voice => String(voice.lang || '').toLowerCase().startsWith('fr'))
            || null;
          utterance.onstart = () => {
            if (runId === this._speechRunId) this.speechState = 'speaking';
          };
          utterance.onend = () => {
            if (runId !== this._speechRunId) return;
            this.speechQueueIndex += 1;
            this.speakNextBrowserChunk(runId);
          };
          utterance.onerror = event => {
            if (runId !== this._speechRunId || event.error === 'canceled' || event.error === 'interrupted') return;
            this.speechError = 'La voix de secours du navigateur a échoué. Vérifie qu’une voix française est installée.';
            this.speechState = 'idle';
            this.speechKind = null;
            this.notify(this.speechError);
          };
          this._browserSpeechUtterance = utterance;
          window.speechSynthesis.speak(utterance);
        },
        onSpeechAudioEnded(runId, index) {
          if (runId !== this._speechRunId || index !== this.speechQueueIndex) return;
          if (index + 1 >= this.speechQueue.length) {
            this.finishSpeech(runId);
            return;
          }
          this.playSpeechChunk(index + 1, runId);
        },
        onSpeechAudioError(runId, index) {
          if (runId !== this._speechRunId || index !== this.speechQueueIndex) return;
          const message = 'Le fichier audio n’a pas pu être lu. Essaie de relancer la lecture.';
          if (!this.startBrowserSpeechFallback(runId, message)) {
            this.speechError = message;
            this.speechState = 'idle';
            this.speechKind = null;
            this.notify(this.speechError);
          }
        },
        revokeSpeechAudioUrls() {
          Object.values(this._speechAudioUrls || {}).forEach(url => {
            try { URL.revokeObjectURL(url); } catch (_) { /* URL déjà libérée */ }
          });
          this._speechAudioUrls = {};
          this._speechAudioRequests = {};
          this._speechLoadedIndex = -1;
        },
        finishSpeech(runId) {
          if (runId !== this._speechRunId) return;
          this._speechRunId += 1;
          if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel();
          this._browserSpeechUtterance = null;
          const audio = this.$refs.speechAudio;
          if (audio) {
            audio.onended = null;
            audio.onerror = null;
            audio.pause();
            audio.removeAttribute('src');
            audio.load();
          }
          this.revokeSpeechAudioUrls();
          this.speechState = 'idle';
          this.speechKind = null;
          this.speechEngine = null;
          this.speechQueue = [];
          this.speechQueueIndex = 0;
        },
        startSpeech(text, kind) {
          if (!this.speechSupported()) {
            this.speechError = 'La lecture audio n’est pas prise en charge par ce navigateur.';
            return;
          }
          this.stopSpeech();
          this.speechQueue = this.splitSpeechText(text);
          if (!this.speechQueue.length) {
            this.speechError = 'Aucun texte disponible à partir de ce point. Choisis une autre section ou « Début du cours ».';
            this.notify(this.speechError);
            return;
          }
          this.speechKind = kind;
          this.speechEngine = 'server';
          this.speechState = 'starting';
          this.speechError = null;
          this.speechQueueIndex = 0;
          this.playSpeechChunk(0, this._speechRunId);
        },
        stopSpeech() {
          this._speechRunId += 1;
          if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel();
          this._browserSpeechUtterance = null;
          const audio = this.$refs.speechAudio;
          if (audio) {
            audio.onended = null;
            audio.onerror = null;
            audio.pause();
            audio.removeAttribute('src');
            audio.load();
          }
          this.revokeSpeechAudioUrls();
          this.speechState = 'idle';
          this.speechKind = null;
          this.speechEngine = null;
          this.speechQueue = [];
          this.speechQueueIndex = 0;
          this.speechError = null;
        },
        pauseSpeech() {
          if (!['speaking', 'starting'].includes(this.speechState)) return;
          if (this.speechEngine === 'browser' && typeof window !== 'undefined' && 'speechSynthesis' in window) {
            window.speechSynthesis.pause();
          } else {
            const audio = this.$refs.speechAudio;
            if (audio) audio.pause();
          }
          this.speechState = 'paused';
        },
        async resumeSpeech() {
          if (this.speechState !== 'paused') return;
          const runId = this._speechRunId;
          if (this.speechEngine === 'browser' && typeof window !== 'undefined' && 'speechSynthesis' in window) {
            window.speechSynthesis.resume();
            this.speechState = 'speaking';
            return;
          }
          const audio = this.$refs.speechAudio;
          this.speechState = 'starting';
          if (audio && this._speechLoadedIndex === this.speechQueueIndex && audio.src) {
            try {
              await audio.play();
              if (runId === this._speechRunId) this.speechState = 'speaking';
            } catch (error) {
              if (runId !== this._speechRunId) return;
              this.speechState = 'paused';
              this.speechError = 'Appuie de nouveau sur Reprendre pour autoriser la lecture audio.';
            }
          } else if (!this._speechAudioRequests[this.speechQueueIndex]) {
            this.playSpeechChunk(this.speechQueueIndex, runId);
          }
        },
        changeSpeechRate() {
          if (!this.speechKind || !['speaking', 'starting', 'paused'].includes(this.speechState)) return;
          const kind = this.speechKind;
          const remainingText = this.speechQueue.slice(this.speechQueueIndex).join(' ');
          const wasPaused = this.speechState === 'paused';
          if (this.speechEngine === 'browser') {
            this.stopSpeech();
            this.speechEngine = 'browser';
            this.speechKind = kind;
            this.speechQueue = this.splitSpeechText(remainingText, 1000);
            this.speechQueueIndex = 0;
            this.speechState = 'starting';
            this.speakNextBrowserChunk(this._speechRunId);
            if (wasPaused) this.pauseSpeech();
            return;
          }
          this.startSpeech(remainingText, kind);
          if (wasPaused) this.pauseSpeech();
        },
        toggleLessonSpeech() {
          if (this.speechKind === 'lesson' && ['speaking', 'starting'].includes(this.speechState)) return this.pauseSpeech();
          if (this.speechKind === 'lesson' && this.speechState === 'paused') return this.resumeSpeech();
          this.startSpeech(this.speechTextFromArticle(), 'lesson');
        },
        speakTutorMessage(text) {
          const spoken = String(text || '')
            .replace(/\x60{3}[\s\S]*?\x60{3}/gu, ' ')
            .replace(/^\s{0,3}#{1,6}\s+/gmu, '')
            .replace(/^\s*(?:[-*+]|\d+[.)])\s+/gmu, '')
            .replace(/\*\*(.*?)\*\*/gu, '$1')
            .replace(/\*([^*]+)\*/gu, '$1')
            .replace(/\x60([^\x60]+)\x60/gu, '$1')
            .replace(/\[([^\]]+)\]\([^)]+\)/gu, '$1')
            .replace(/^\s*>\s?/gmu, '')
            .replace(/\n{3,}/gu, '\n\n')
            .trim();
          this.startSpeech(spoken, 'tutor');
        },
        setTutorSize(size) {
          if (!['compact', 'normal', 'large'].includes(size)) return;
          this.tutorSize = size;
          try { localStorage.setItem('skilltree-tutor-size', size); } catch (_) { /* Stockage facultatif. */ }
        },
        openTutor() {
          this.tutorOpen = true;
          this.$nextTick(() => {
            if (this.$refs.tutorMessagesArea) this.$refs.tutorMessagesArea.scrollTop = this.$refs.tutorMessagesArea.scrollHeight;
          });
        },
        askTutorPreset(question) {
          this.tutorOpen = true;
          this.tutorQuestion = question;
          return this.askTutor();
        },
        explainSelectedText() {
          const selected = typeof window !== 'undefined' && window.getSelection ? String(window.getSelection().toString()).trim() : '';
          this.tutorOpen = true;
          if (!selected) {
            this.tutorMessages.push({ role: 'assistant', text: 'Sélectionne d’abord un passage dans le cours, puis clique sur « Expliquer ma sélection ».' });
            this.$nextTick(() => {
              if (this.$refs.tutorMessagesArea) this.$refs.tutorMessagesArea.scrollTop = this.$refs.tutorMessagesArea.scrollHeight;
            });
            return;
          }
          this.tutorSelectedText = selected.slice(0, 1800);
          this.tutorQuestion = 'Explique-moi ce passage avec des mots simples, puis donne un exemple concret si cela aide.';
          return this.askTutor();
        },
        async askTutor() {
          const question = String(this.tutorQuestion || '').trim();
          if (!question || this.tutorBusy || !this.detail?.id) return;
          const selectedText = this.tutorSelectedText;
          const history = this.tutorMessages.slice(-8).map(message => ({
            role: message.role === 'assistant' ? 'assistant' : 'user',
            content: String(message.text || '').slice(0, 3000),
          }));
          this.tutorMessages.push({ role: 'user', text: question });
          this.tutorQuestion = '';
          this.tutorSelectedText = '';
          this.tutorBusy = true;
          this.$nextTick(() => {
            if (this.$refs.tutorMessagesArea) this.$refs.tutorMessagesArea.scrollTop = this.$refs.tutorMessagesArea.scrollHeight;
          });
          try {
            const response = await fetch('/api/tutor', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ node_id: this.detail.id, question, selected_text: selectedText, history })
            });
            const raw = await response.text();
            let data;
            try { data = raw ? JSON.parse(raw) : {}; }
            catch (_) { throw new Error('Le serveur a renvoyé une réponse illisible.'); }
            if (!response.ok) throw new Error(data.detail || data.message || `Erreur HTTP ${response.status}`);
            const answer = String(data.answer || 'Je n’ai pas reçu de réponse exploitable.');
            this.tutorMessages.push({ role: 'assistant', text: answer });
          } catch (error) {
            this.tutorMessages.push({ role: 'assistant', text: error.message || 'Erreur de connexion au tuteur.' });
          } finally {
            this.tutorBusy = false;
            this.$nextTick(() => {
              if (this.$refs.tutorMessagesArea) this.$refs.tutorMessagesArea.scrollTop = this.$refs.tutorMessagesArea.scrollHeight;
            });
          }
        }
      };
    }
  