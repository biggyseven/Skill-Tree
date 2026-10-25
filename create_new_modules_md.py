import os

LESSON_DIR = "content/lessons"
os.makedirs(LESSON_DIR, exist_ok=True)

# Liste des nouveaux cours à créer (ID et Titre)
courses = [
    # --- MODULE RÉSEAU MANQUANTS ---
    ("isis-debutant", "IS-IS - Débutant"),
    ("isis-intermediaire", "IS-IS - Intermédiaire"),
    ("isis-expert", "IS-IS - Expert"),
    ("netflow-debutant", "IP SLA & NetFlow - Débutant"),
    ("netflow-intermediaire", "IP SLA & NetFlow - Intermédiaire"),
    ("netflow-expert", "IP SLA & NetFlow - Expert"),
    ("archi-reseau-debutant", "Architecture Réseau - Débutant"),
    ("archi-reseau-intermediaire", "Architecture Réseau - Intermédiaire"),
    ("archi-reseau-expert", "Architecture Réseau - Expert"),
    ("sd-access-debutant", "Cisco SD-Access - Débutant"),
    ("sd-access-intermediaire", "Cisco SD-Access - Intermédiaire"),
    ("sd-access-expert", "Cisco SD-Access - Expert"),

    # --- MODULE ADMINISTRATION SYSTÈME (LINUX/WINDOWS) ---
    ("linux-debutant", "Introduction à Linux et au shell"),
    ("linux-intermediaire", "Administration Linux Avancée"),
    ("linux-expert", "Linux Expert (Performance et Kernel)"),
    ("storage-debutant", "Système de fichiers et permissions"),
    ("storage-intermediaire", "Stockage : LVM et RAID"),
    ("storage-expert", "Stockage Réseau (NAS/SAN)"),
    ("users-debutant", "Utilisateurs et groupes"),
    ("users-intermediaire", "Authentification centralisée (LDAP/AD)"),
    ("users-expert", "Kerberos et PKI"),
    ("process-debutant", "Processus et services (systemd)"),
    ("process-intermediaire", "Gestion avancée des services"),
    ("process-expert", "Optimisation des performances"),
    ("packages-debutant", "Paquets et mises à jour"),
    ("packages-intermediaire", "Gestion de parc et patch management"),
    ("packages-expert", "Durcissement CIS et audit"),
    ("scripting-debutant", "Scripting Bash"),
    ("scripting-intermediaire", "Automatisation avec Ansible"),
    ("scripting-expert", "Ansible Avancé et AWX"),
    ("reseau-linux-debutant", "Réseau sous Linux (netplan, nmcli)"),
    ("reseau-linux-intermediaire", "Filtrage et NAT (nftables/iptables)"),
    ("reseau-linux-expert", "Réseau avancé sous Linux (VLAN, Bonds, Bridges)"),
    ("web-server-debutant", "Serveurs Web (Nginx/Apache)"),
    ("web-server-intermediaire", "Reverse Proxy et Load Balancing"),
    ("web-server-expert", "Haute Performance Web"),
    ("db-debutant", "Bases de données (SQL)"),
    ("db-intermediaire", "Administration de bases de données"),
    ("db-expert", "Haute Disponibilité BDD"),
    ("windows-server-debutant", "Windows Server : bases et Active Directory"),
    ("windows-server-intermediaire", "GPO et gestion de parc Windows"),
    ("windows-server-expert", "Windows Server Expert (Failover, Hyper-V)"),
    ("ha-sys-debutant", "Haute disponibilité (Keepalived, Pacemaker)"),
    ("ha-sys-intermediaire", "Clusters Linux Avancés"),
    ("ha-sys-expert", "DRP et PRA (Reprise d'activité)"),
    ("virt-debutant", "Virtualisation (KVM, Proxmox, VMware)"),
    ("virt-intermediaire", "Gestion avancée de l'hyperviseur"),
    ("virt-expert", "Cloud Privé et Infogérance"),
    ("monitoring-debutant", "Journaux et supervision"),
    ("monitoring-intermediaire", "Supervision avec Prometheus et Grafana"),
    ("monitoring-expert", "Observabilité avancée (Tracing, Logs)"),
    ("backup-debutant", "Sauvegarde et restauration"),
    ("backup-intermediaire", "Solutions de sauvegarde d'entreprise"),
    ("backup-expert", "Tests de restauration et PRA"),

    # --- MODULE DEVOPS ---
    ("cicd-debutant", "Principes DevOps et cycle CI/CD"),
    ("cicd-intermediaire", "CI/CD avec GitHub Actions et GitLab CI"),
    ("cicd-expert", "GitOps et ArgoCD"),
    ("git-debutant", "Git et gestion de versions"),
    ("git-intermediaire", "Git Avancé"),
    ("git-expert", "Stratégies de branching"),
    ("docker-debutant", "Docker : images et conteneurs"),
    ("docker-intermediaire", "Docker Compose et registres"),
    ("docker-expert", "Sécurité des conteneurs"),
    ("k8s-debutant", "Kubernetes : les bases"),
    ("k8s-intermediaire", "Kubernetes : réseau et stockage"),
    ("k8s-expert", "Kubernetes avancé et Sécurité"),
    ("iac-intermediaire", "Infrastructure as Code avec Terraform"),
    ("iac-expert", "IaC à grande échelle"),
    ("observability-intermediaire", "Observabilité : Prometheus et Grafana"),
    ("observability-expert", "SRE : SLI, SLO et gestion des incidents"),
    ("devsecops-expert", "DevSecOps"),
    ("mesh-expert", "Service Mesh (Istio, Linkerd)")
]

print("✨ Création des fichiers de cours pour les nouveaux modules...\n")
created_count = 0

for node_id, title in courses:
    # On nettoie l'ID pour être sûr (au cas où il y aurait un "-md" dans la liste)
    clean_id = node_id.replace("-md", "")
    filepath = os.path.join(LESSON_DIR, f"{clean_id}.md")
    
    # Si le fichier n'existe pas, on le crée avec un contenu temporaire
    if not os.path.exists(filepath):
        content = f"""---
node_id: {clean_id}
title: {title}
---

# {title}

> **Note** : Ce cours est en cours de rédaction. Utilisez ChatGPT ou Gemini pour générer le contenu complet !
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 Créé : {clean_id}.md")
        created_count += 1

print(f"\n✅ Terminé ! {created_count} fichiers ont été créés avec succès.")
print("Tu n'as plus qu'à coller le texte généré par l'IA dedans !")