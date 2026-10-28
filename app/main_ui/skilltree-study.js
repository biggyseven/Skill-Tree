
    /* Fusionne le noyau (skilltreeBase) et l'extension v3 (skilltreeExt) : l'extension remplace les méthodes de même nom. */
    function rgbOf(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim().split(/\s+/).join(','); }
    function skilltreeStudySession() {
      const storageKey = 'skilltree-study-session-v1';
      const goals = [15, 25, 45, 60];
      const todayKey = () => {
        const now = new Date();
        return String(now.getFullYear()) + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
      };
      return {
        goals,
        targetMinutes: 25,
        elapsedSeconds: 0,
        running: false,
        _interval: null,
        _onVisibilityChange: null,
        _onPageHide: null,
        init() {
          let saved = null;
          try { saved = JSON.parse(localStorage.getItem(storageKey) || 'null'); } catch (_) { }
          const target = Number(saved && saved.targetMinutes);
          if (goals.includes(target)) this.targetMinutes = target;
          if (saved && saved.date === todayKey()) {
            this.elapsedSeconds = Math.max(0, Math.floor(Number(saved.elapsedSeconds) || 0));
          }
          // Ne jamais compter le temps passé hors de l'application après un rechargement.
          this.running = false;
          this._onVisibilityChange = () => { if (document.hidden) this.pause(); };
          this._onPageHide = () => this.pause();
          document.addEventListener('visibilitychange', this._onVisibilityChange);
          window.addEventListener('pagehide', this._onPageHide);
          this._interval = window.setInterval(() => {
            if (!this.running) return;
            this.elapsedSeconds += 1;
            if (this.goalReached) {
              this.running = false;
              this.persist();
              return;
            }
            if (this.elapsedSeconds % 5 === 0) this.persist();
          }, 1000);
          this.persist();
        },
        destroy() {
          if (this._interval !== null) window.clearInterval(this._interval);
          if (this._onVisibilityChange) document.removeEventListener('visibilitychange', this._onVisibilityChange);
          if (this._onPageHide) window.removeEventListener('pagehide', this._onPageHide);
          this.running = false;
          this.persist();
        },
        get goalReached() { return this.elapsedSeconds >= this.targetMinutes * 60; },
        get progressPercent() {
          return Math.min(100, Math.round((this.elapsedSeconds / (this.targetMinutes * 60)) * 100));
        },
        get statusLabel() {
          if (this.goalReached) return 'Objectif atteint — bravo !';
          if (this.running) return 'Session en cours';
          return this.elapsedSeconds > 0 ? 'Session en pause · tu peux reprendre quand tu veux' : 'Choisis une durée et lance ta session';
        },
        elapsedLabel() {
          const seconds = Math.max(0, Math.floor(this.elapsedSeconds));
          const hours = Math.floor(seconds / 3600);
          const minutes = Math.floor((seconds % 3600) / 60);
          const rest = seconds % 60;
          return hours
            ? String(hours) + ' h ' + String(minutes).padStart(2, '0') + ' min'
            : String(minutes).padStart(2, '0') + ':' + String(rest).padStart(2, '0');
        },
        setTarget(minutes) {
          const value = Number(minutes);
          if (!goals.includes(value)) return;
          this.targetMinutes = value;
          if (this.goalReached) this.running = false;
          this.persist();
        },
        toggle() {
          if (this.goalReached) return;
          this.running = !this.running;
          this.persist();
        },
        pause() {
          if (!this.running) return;
          this.running = false;
          this.persist();
        },
        reset() {
          this.running = false;
          this.elapsedSeconds = 0;
          this.persist();
        },
        persist() {
          try {
            localStorage.setItem(storageKey, JSON.stringify({
              date: todayKey(),
              targetMinutes: this.targetMinutes,
              elapsedSeconds: this.elapsedSeconds,
              running: this.running,
            }));
          } catch (_) { }
        },
      };
    }

    function skilltreeTheme() {
      const TONE = { cyan: 'bg-cyan-500/10 text-cyan-400', emerald: 'bg-emerald-500/10 text-emerald-400', fuchsia: 'bg-fuchsia-500/10 text-fuchsia-400', orange: 'bg-orange-500/10 text-orange-400' };
      return {
        themes: window.THEMES, themeMenuOpen: false, theme: document.documentElement.dataset.theme || 'graphite', activeThemeId: document.documentElement.dataset.theme || 'graphite',
        liveEvents: (() => {
          try {
            const saved = JSON.parse(localStorage.getItem('skilltree-notifications-v1') || '[]');
            return Array.isArray(saved) ? saved.filter(n => n && typeof n === 'object').slice(0, 30) : [];
          } catch (_) { return []; }
        })(),
        radarSelectedDomain: null,
        syncTheme() {
          const root = document.documentElement;
          const applied = root.dataset.theme;
          const stored = (() => { try { return localStorage.getItem('skilltree-theme2'); } catch (_) { return null; } })();
          // activeThemeId est la source réactive unique pendant la session ; stockage et DOM sont synchronisés avec elle.
          const fallback = this.themes.some(x => x.id === applied) ? applied : 'graphite';
          const id = this.themes.some(x => x.id === this.activeThemeId)
            ? this.activeThemeId
            : (this.themes.some(x => x.id === stored) ? stored : fallback);
          const selected = this.themes.find(x => x.id === id);
          if (!selected) return;
          this.activeThemeId = id;
          this.theme = id;
          root.dataset.theme = id;
          root.classList.toggle('dark', selected.kind === 'dark');
          root.classList.toggle('light', selected.kind === 'light');
          root.style.colorScheme = selected.kind;
          try { if (stored !== id) localStorage.setItem('skilltree-theme2', id); } catch (_) { }
        },
        themeIsActive(id) { return this.activeThemeId === id; },
        closeModalsOnOutside(event) {
          const target = event && event.target;
          if (!target || !target.closest) return;
          // Un clic dans le contenu ne doit pas interrompre les actions du formulaire ou de la modale.
          if (target.closest('[role="dialog"][aria-modal="true"], [data-modal-content]')) return;
          if (this.open) this.close();
          if (this.mobileSearchOpen) this.closeMobileSearch();
          if (this.shopOpen) this.shopOpen = false;
          if (this.diplomaView) this.diplomaView = null;
          if (this.modMgrOpen) this.modMgrOpen = false;
        },
        closeThemeOnOutside(event) {
          const target = event && event.target;
          if (!target || !target.closest || !target.closest('[data-theme-picker]')) this.themeMenuOpen = false;
        },
        radarHasData() {
          const categories = Array.isArray(this.stats?.categories) ? this.stats.categories : [];
          if (!categories.length) return false;
          const totalAttempts = Number(this.stats?.totals?.attempts);
          if (Number.isFinite(totalAttempts) && totalAttempts > 0) return true;
          return categories.some(c => Number(c?.attempts ?? c?.total_attempts ?? c?.questions_answered ?? 0) > 0 || Number(c?.success_rate) > 0);
        },
        radarHasPositiveRate() {
          return Array.isArray(this.stats?.categories) && this.stats.categories.some(c => Number(c?.success_rate) > 0);
        },
        setTheme(id) {
          const m = this.themes.find(x => x.id === id);
          if (!m) return;
          const r = document.documentElement;
          // Mettre à jour l'état Alpine avant le DOM évite une coche qui reste sur l'ancien thème.
          this.activeThemeId = id;
          this.theme = id;
          r.dataset.theme = id;
          r.classList.toggle('dark', m.kind === 'dark');
          r.classList.toggle('light', m.kind === 'light');
          r.style.colorScheme = m.kind;
          try { localStorage.setItem('skilltree-theme2', id); } catch (_) { }
          // Le sélecteur reste ouvert pour que la coche confirme immédiatement le choix.
          if (this.stats && this.tab === 'stats') this.$nextTick(() => this.renderSpiderChart());
        },
        toggleTheme() { const k = (this.themes.find(x => x.id === this.theme) || {}).kind; this.setTheme(k === 'dark' ? 'lumiere' : 'graphite'); },
        /* Parcours : fenêtre de 5 cours autour de l'étape en cours, calculée depuis /api/tree */
        get lastOpenedNode() {
          return this.lastOpenedNodeId ? (this.nodes.find(n => String(n.id) === String(this.lastOpenedNodeId)) || null) : null;
        },
        get resumableLastNode() {
          const node = this.lastOpenedNode;
          return node && node.status !== 'locked' ? node : null;
        },
        get moduleNextCourse() {
          if (this.moduleNextCourseId === null || this.moduleNextCourseId === undefined) return null;
          return this.nodes.find(node => String(node.id) === String(this.moduleNextCourseId)) || null;
        },
        get resumeNode() {
          return this.moduleNextCourse
            || this.resumableLastNode
            || this.parcours.cur
            || this.nodes.find(n => n.status === 'in_progress')
            || this.nodes.find(n => n.status === 'available')
            || this.nodes.find(n => n.status === 'validated')
            || null;
        },
        get allNodesValidated() {
          return this.nodes.length > 0 && this.nodes.every(node => node.status === 'validated');
        },
        get resumeBadge() {
          if (this.treeError && !this.nodes.length) return 'Parcours indisponible';
          if (!this.nodes.length) return this.loading ? 'Chargement du parcours' : 'Aucun cours disponible';
          if (this.moduleNextCourse) return 'Module sélectionné';
          if (this.resumableLastNode) return 'Reprise disponible';
          if (this.resumeNode?.status === 'in_progress') return 'Activité à reprendre';
          if (this.allNodesValidated) return 'Parcours terminé';
          return this.resumeNode ? 'Prêt à continuer' : 'À explorer';
        },
        get resumeEyebrow() {
          if (this.treeError && !this.nodes.length) return 'Parcours indisponible';
          if (!this.nodes.length) return this.loading ? 'Chargement en cours' : 'Aucun cours disponible';
          if (this.moduleNextCourse) return 'Prochaine étape du module';
          if (this.resumableLastNode) return 'Reprendre ta dernière leçon';
          if (this.resumeNode?.status === 'in_progress') return 'Reprendre une activité';
          if (this.allNodesValidated) return 'Révision recommandée';
          return 'Ta prochaine étape';
        },
        get resumeDescription() {
          if (this.treeError && !this.nodes.length) return 'Le parcours n’a pas pu être chargé. Réessaie depuis le message affiché en haut du tableau de bord.';
          if (!this.nodes.length) return this.loading ? 'Récupération des étapes du parcours…' : 'Le serveur ne fournit actuellement aucun cours dans le parcours.';
          if (this.moduleNextCourse) return 'Tu as sélectionné le module ' + this.moduleMeta(this.moduleOf(this.moduleNextCourse)).label + '. Commence par ce premier cours quand tu es prêt.';
          if (this.resumableLastNode) return 'Retrouve le cours où tu t’es arrêté et poursuis ta lecture sans devoir le rechercher.';
          if (this.resumeNode?.status === 'in_progress') return 'Une activité est déjà commencée : reprends-la pour poursuivre ta progression.';
          if (this.allNodesValidated) return 'Tu as validé tout le parcours disponible. Choisis une leçon pour réviser et consolider tes acquis.';
          if (this.resumeNode) return 'Poursuis le parcours conseillé, étape après étape.';
          if (this.nodes.length) return 'Aucune étape accessible pour le moment. Vérifie les prérequis des cours.';
          return 'Choisis un cours pour commencer à construire tes compétences réseau.';
        },
        get resumeButtonLabel() {
          if (this.treeError && !this.nodes.length) return 'Parcours indisponible';
          if (!this.nodes.length) return this.loading ? 'Chargement…' : 'Aucun cours disponible';
          if (this.moduleNextCourse) {
            if (this.moduleNextCourse.status === 'locked') return 'Voir les prérequis';
            if (this.moduleNextCourse.status === 'in_progress') return 'Reprendre cette leçon';
            if (this.moduleNextCourse.status === 'validated') return 'Revoir ce cours';
            return 'Commencer ce cours';
          }
          if (this.resumableLastNode) return this.lastLessonProgress >= 100 ? 'Revoir cette leçon' : 'Reprendre la lecture';
          if (this.resumeNode?.status === 'in_progress') return 'Reprendre cette activité';
          if (this.resumeNode?.status === 'validated') return 'Réviser cette leçon';
          if (this.resumeNode) return 'Commencer la prochaine étape';
          return 'Aucune étape accessible';
        },
        get nextLessonNode() {
          // Distinguer la reprise de la dernière leçon de la prochaine étape conseillée.
          // Ne rien afficher si la dernière leçon est elle-même l'étape courante.
          if (!this.resumableLastNode) return null;
          const next = this.parcours.cur;
          if (!next || String(next.id) === String(this.resumableLastNode.id) || next.status === 'locked') return null;
          return next;
        },
        get parcours() {
          const pool = this.nodesIn(this.moduleFilter);
          const total = pool.length;
          const done = pool.filter(n => n.status === 'validated').length;
          const finished = total > 0 && done === total;
          // Une action "challenge" peut aussi être une nouveauté disponible :
          // seule une tentative déjà en cours doit remplacer l'étape courante du parcours.
          const activePlanAction = (this.dailyPlan || []).find(action =>
            action.status === 'in_progress' &&
            ['continue', 'lab', 'challenge'].includes(action.action) &&
            pool.some(node => String(node.id) === String(action.node_id))
          );
          let ci = activePlanAction
            ? pool.findIndex(node => String(node.id) === String(activePlanAction.node_id))
            : -1;
          if (ci < 0) ci = pool.findIndex(node => node.status === 'in_progress');
          if (ci < 0) ci = pool.findIndex(node => node.status === 'available');
          if (ci < 0 && finished) ci = total - 1;

          const activeIndex = Math.max(0, ci);
          const start = Math.max(0, Math.min(activeIndex - 2, total - 5));
          const steps = pool.slice(start, start + 5).map((node, i) => ({
            id: node.id,
            title: node.title,
            status: node.status,
            cur: !finished && ci >= 0 && start + i === ci,
          }));
          const pos = steps.findIndex(step => step.cur);
          return {
            steps,
            total,
            done,
            finished,
            cur: ci >= 0 && !finished ? pool[ci] : null,
            fill: finished ? 1 : (steps.length > 1 && pos >= 0 ? pos / (steps.length - 1) : 0),
          };
        },
        get planActions() {
          // Le résumé de reprise et le graphe montrent déjà leur activité cible.
          // Le plan du jour propose des actions complémentaires plutôt que de dupliquer ces nœuds.
          const visibleNodeIds = [
            this.resumeNode?.id,
            this.parcours.cur?.id,
          ].filter(id => id !== null && id !== undefined).map(String);
          if (this.dailyPlan.length) {
            return this.dailyPlan.filter(action => !visibleNodeIds.includes(String(action.node_id)));
          }
          return this.nodes
            .filter(n => n.status === 'available' && !visibleNodeIds.includes(String(n.id)))
            .slice(0, 3)
            .map(n => ({ node_id: n.id, label: n.title, reason: n.category || '', action: 'start' }));
        },
        get planEmptyMessage() {
          if (this.dashboardDataErrors.dailyPlan && !this.dailyPlan.length) return 'Le plan du serveur est indisponible. Les suggestions locales éventuelles sont déduites du parcours chargé.';
          if (this.treeError && !this.nodes.length) return 'Le parcours ne peut pas être affiché. Réessaie avec le bouton ci-dessus.';
          if (!this.nodes.length) return this.loading ? 'Préparation de ta session…' : 'Aucun cours disponible pour le moment.';
          if (this.nodes.every(n => n.status === 'validated')) return '🎉 Tu as validé tout le parcours actuellement disponible. Reprends une leçon pour réviser ou explore les modules pour approfondir.';
          const visibleNodeIds = [this.resumeNode?.id, this.parcours.cur?.id]
            .filter(id => id !== null && id !== undefined).map(String);
          if (this.dailyPlan.length && this.dailyPlan.every(action => visibleNodeIds.includes(String(action.node_id)))) {
            return 'Les priorités du jour sont déjà mises en évidence dans les cartes de reprise et du parcours. Explore un autre module pour varier ta session.';
          }
          if (!this.dailyPlan.length && this.nodes.some(n => n.status === 'available' && visibleNodeIds.includes(String(n.id)))) {
            return 'La prochaine étape est déjà mise en évidence dans les cartes ci-dessus. Explore un autre module pour varier ta session.';
          }
          return 'Aucune action recommandée pour le moment. Consulte les prérequis des cours ou explore un module.';
        },
        get notifications() {
          return this.liveEvents.slice(0, 30).map(n => ({
            ...n,
            read: n.read === true,
            cls: TONE[n.tone] || TONE.cyan,
          }));
        },
        get unreadNotificationCount() {
          return this.liveEvents.filter(n => n.read !== true).length;
        },
        persistNotifications() {
          this.liveEvents = this.liveEvents.slice(0, 30);
          try { localStorage.setItem('skilltree-notifications-v1', JSON.stringify(this.liveEvents)); } catch (_) { }
        },
        addNotification(event) {
          if (!event || !event.title) return;
          const id = String(event.id || (Date.now() + '-' + Math.random().toString(36).slice(2, 9)));
          if (this.liveEvents.some(n => String(n.id) === id)) return;
          const notification = {
            icon: '🔔', tone: 'cyan', sub: '', node: null,
            ...event,
            id,
            createdAt: event.createdAt || new Date().toISOString(),
            read: false,
          };
          this.liveEvents = [notification, ...this.liveEvents.filter(n => String(n.id) !== id)].slice(0, 30);
          this.persistNotifications();
        },
        markNotificationRead(id) {
          if (!this.liveEvents.some(n => String(n.id) === String(id) && n.read !== true)) return;
          this.liveEvents = this.liveEvents.map(n => String(n.id) === String(id) ? { ...n, read: true } : n);
          this.persistNotifications();
        },
        markAllNotificationsRead() {
          if (!this.unreadNotificationCount) return;
          this.liveEvents = this.liveEvents.map(n => ({ ...n, read: true }));
          this.persistNotifications();
        },
        openNotification(notification) {
          if (!notification) return;
          this.markNotificationRead(notification.id);
          this.notificationsOpen = false;
          if (notification.node && this.nodes.some(n => String(n.id) === String(notification.node))) {
            this.show(notification.node);
          }
        },
        notificationTime(value) {
          try {
            const date = new Date(value);
            if (!Number.isFinite(date.getTime())) return '';
            return date.toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
          } catch (_) { return ''; }
        },
        startSync() {
          if (this._sync) return; const go = () => { if (!document.hidden && !this.open) this.refreshAll(); };
          this._sync = setInterval(go, 45000); document.addEventListener('visibilitychange', go);
        },
      };
    }
    function skilltree() {
      const base = skilltreeBase();
      Object.defineProperties(base, Object.getOwnPropertyDescriptors(skilltreeExt()));
      Object.defineProperties(base, Object.getOwnPropertyDescriptors(skilltreeTheme()));
      const origLoad = base.loadTree, origInit = base.init;
      const origLoadStreak = base.loadStreak;
      const origCheckRewards = base.checkRewards;
      const nodeSnapshotKey = 'skilltree-node-snapshot-v1';
      const streakSnapshotKey = 'skilltree-streak-snapshot-v1';
      const readNodeSnapshot = () => {
        try {
          const saved = JSON.parse(localStorage.getItem(nodeSnapshotKey) || 'null');
          return saved && saved.nodes && typeof saved.nodes === 'object' ? saved.nodes : null;
        } catch (_) { return null; }
      };
      const saveNodeSnapshot = (nodes) => {
        const snapshot = {};
        nodes.forEach(n => { snapshot[String(n.id)] = { title: n.title, status: n.status, module: n.module }; });
        try { localStorage.setItem(nodeSnapshotKey, JSON.stringify({ nodes: snapshot })); } catch (_) { }
      };
      base.loadTree = async function () {
        const savedBefore = readNodeSnapshot();
        const previousInMemory = new Map((this.nodes || []).map(n => [String(n.id), { title: n.title, status: n.status, module: n.module }]));
        await origLoad.call(this);
        if (this.treeError || !Array.isArray(this.nodes)) return;

        // Le snapshot local permet de détecter les ajouts/modifications même après fermeture ou rechargement de la page.
        const previous = savedBefore || (previousInMemory.size ? Object.fromEntries(previousInMemory) : null);
        if (previous) {
          const added = this.nodes.filter(n => !Object.prototype.hasOwnProperty.call(previous, String(n.id)));
          if (added.length) {
            const titles = added.slice(0, 3).map(n => n.title).join(', ');
            const extra = added.length > 3 ? ' et ' + (added.length - 3) + ' autre(s)' : '';
            this.addNotification({
              id: 'courses-added:' + added.map(n => String(n.id)).sort().join('|'),
              icon: '🆕', tone: 'cyan',
              title: added.length + ' nouveau' + (added.length > 1 ? 'x' : '') + ' cours disponible' + (added.length > 1 ? 's' : ''),
              sub: titles + extra,
              node: added[0].id,
            });
          }
          this.nodes.forEach(n => {
            const old = previous[String(n.id)];
            if (!old) return;
            if (old.status === 'locked' && n.status === 'available') {
              this.addNotification({
                id: 'course-unlocked:' + String(n.id),
                icon: '🔓', tone: 'fuchsia', title: 'Cours débloqué', sub: n.title, node: n.id,
              });
            } else if (old.status !== 'validated' && n.status === 'validated') {
              this.addNotification({
                id: 'course-validated:' + String(n.id),
                icon: '✅', tone: 'emerald', title: 'Cours validé', sub: n.title, node: n.id,
              });
            }
          });
        }
        saveNodeSnapshot(this.nodes);
      };

      if (typeof origLoadStreak === 'function') {
        base.loadStreak = async function () {
          let previous = null;
          try {
            const stored = localStorage.getItem(streakSnapshotKey);
            if (stored !== null && Number.isInteger(Number(stored)) && Number(stored) >= 0) previous = Number(stored);
          } catch (_) { }
          await origLoadStreak.call(this);
          if (this.dashboardDataErrors?.streak || !Number.isInteger(this.streakDays) || this.streakDays < 0) return;
          const current = this.streakDays;
          if (previous !== null && current > previous) {
            const milestones = [3, 7, 14, 30, 50, 100];
            const milestone = milestones.filter(day => previous < day && current >= day).pop();
            this.addNotification({
              id: milestone ? 'streak-milestone:' + milestone : 'streak-days:' + current,
              icon: '🔥', tone: 'orange',
              title: milestone ? 'Série de ' + milestone + ' jours atteinte !' : 'Série quotidienne prolongée',
              sub: 'Tu as étudié ' + current + ' jours consécutifs.',
            });
          }
          try { localStorage.setItem(streakSnapshotKey, String(current)); } catch (_) { }
        };
      }

      if (typeof origCheckRewards === 'function') {
        base.checkRewards = function (...args) {
          let previouslySeen = null;
          try {
            const raw = localStorage.getItem('st:badges-seen');
            previouslySeen = raw ? JSON.parse(raw) : null;
          } catch (_) { }
          const newlyUnlocked = Array.isArray(previouslySeen) && this.nodes.length
            ? this.badges.filter(b => b.ok && !previouslySeen.includes(b.id))
            : [];
          const result = origCheckRewards.apply(this, args);
          newlyUnlocked.forEach(b => this.addNotification({
            id: 'badge-unlocked:' + b.id,
            icon: b.icon || '🏅', tone: 'orange',
            title: 'Badge débloqué : ' + b.name, sub: b.desc,
          }));
          return result;
        };
      }
      base.init = async function () { this.syncTheme?.(); await origInit.call(this); this.syncTheme?.(); this.startSync(); };
      return base;
    }
  