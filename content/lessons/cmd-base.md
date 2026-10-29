# Configuration de base (Hostname, SSH, Mots de passe, NTP)

> **Contexte d'utilisation :** fiche de démarrage pour un switch ou un routeur Cisco IOS / IOS XE en lab ou en environnement d'exploitation. Les syntaxes peuvent varier selon la plateforme et la version. Appliquer les changements en console ou avec un accès de secours disponible.

## 1. Séquence minimale recommandée

~~~~text
enable
configure terminal
hostname SW-ACC-01
no ip domain-lookup
enable secret <SECRET-FORT>
service password-encryption
ip domain-name entreprise.example
username admin privilege 15 secret <SECRET-FORT>
crypto key generate rsa modulus 2048
ip ssh version 2
line console 0
 logging synchronous
 exec-timeout 10 0
line vty 0 4
 login local
 transport input ssh
 exec-timeout 10 0
end
copy running-config startup-config
~~~~

Remplace les noms et secrets par les valeurs de l'organisation. Ne colle jamais un mot de passe réel dans un ticket, un dépôt Git, une capture d'écran ou une fiche de lab publique. Si la plateforme demande de choisir une taille de clé après la commande RSA, sélectionner au minimum 2048 bits lorsque c'est compatible avec la politique et la version.

## 2. Commandes utiles

| Commande | Rôle | Point de vigilance |
|---|---|---|
| hostname SW-ACC-01 | Définit l'identité CLI | Choisir une convention unique, documentée |
| no ip domain-lookup | Évite une résolution DNS involontaire des commandes mal tapées | Désactive cette fonction sur l'équipement, pas les clients |
| enable secret ... | Protège le mode privilégié avec un secret haché selon la plateforme | Préférer à enable password |
| service password-encryption | Masque certains mots de passe de configuration en clair | Obfuscation faible : ce n'est pas un chiffrement robuste |
| username admin privilege 15 secret ... | Crée un compte local privilégié | Limiter le privilège si l'usage ne nécessite pas 15 |
| ip domain-name domaine | Définit le domaine utilisé notamment pour les clés SSH | Requis avant la génération de clés sur de nombreuses versions |
| crypto key generate rsa modulus 2048 | Génère des clés RSA pour SSH | Les options exactes peuvent varier |
| ip ssh version 2 | Force SSHv2 lorsque pris en charge | Éviter Telnet pour l'administration |
| login local | Utilise la base locale sur la ligne concernée | Vérifier qu'un compte fonctionne avant de fermer la session courante |
| transport input ssh | Autorise SSH sur les lignes VTY | Peut couper les accès Telnet existants |
| exec-timeout 10 0 | Ferme une session inactive après 10 minutes | Ajuster aux procédures d'exploitation |
| copy running-config startup-config | Sauvegarde la configuration active au démarrage | Ne pas sauvegarder une configuration non validée |

## 3. Accès SSH : bonnes pratiques

1. Configurer un hostname et un domaine cohérents.
2. Créer et tester un compte local ou l'intégration AAA approuvée.
3. Générer les clés et activer SSHv2.
4. Sur les lignes VTY, limiter le transport à SSH, sélectionner l'authentification, définir un délai d'inactivité.
5. Si une ACL de gestion est prévue, l'appliquer après vérification de l'adresse source autorisée et en conservant une voie de secours.
6. Ouvrir une **nouvelle** session SSH pour valider le résultat avant de fermer la console ou la session de travail.

Pour restreindre les sources d'administration, une ACL standard peut être liée aux VTY avec access-class. Contrôler la syntaxe adaptée à l'IOS visé et éviter de déployer une liste qui ne permet plus à l'équipe réseau de revenir sur l'équipement.

## 4. Heure et NTP

~~~~text
configure terminal
clock timezone WAT 1 0
ntp server 192.0.2.20
end
show clock detail
show ntp status
show ntp associations
~~~~

- clock timezone définit le fuseau affiché ; il ne synchronise pas l'horloge.
- ntp server déclare un serveur NTP. L'adresse d'exemple 192.0.2.20 est réservée à la documentation : la remplacer.
- show ntp status indique si l'équipement est synchronisé.
- show ntp associations permet de voir les pairs et leur état.
- Un équipement juste démarré peut prendre du temps avant de se synchroniser. Vérifier l'ACL, le routage, la résolution DNS éventuelle et la source NTP autorisée.
- Certaines versions prennent aussi en charge l'authentification NTP. Ne pas activer une clé sans avoir configuré et validé la même politique sur la source.

Une heure fiable améliore la corrélation des journaux, le dépannage et la chronologie d'incident. Elle ne remplace pas les horodatages et la centralisation des logs.

## 5. Contrôles après configuration

~~~~text
show running-config
show startup-config
show ip ssh
show users
show line
show clock detail
show ntp status
show logging
~~~~

| Si tu observes… | Vérifie d'abord… |
|---|---|
| SSH refuse la connexion | IP de gestion, routage, ACL, clé RSA, transport VTY, compte et secret |
| Le login s'ouvre puis se ferme | Authentification locale, niveau de privilège, exec-timeout, méthode AAA |
| L'heure dérive | Statut NTP, reachability, source, fuseau et éventuel filtrage UDP/123 |
| Le changement disparaît après reboot | Sauvegarde running-config vers startup-config |
| Les commandes tapées lancent une résolution DNS | no ip domain-lookup et les erreurs de saisie |

## 6. Arbre de décision avant de quitter l'équipement

~~~~text
La configuration est-elle correcte ?
├─ Non → rester en console, corriger, relancer les show
└─ Oui
   ├─ SSH testé dans une nouvelle session ?
   │  ├─ Non → tester avant de fermer la session actuelle
   │  └─ Oui → vérifier privilèges et accès de secours
   ├─ Heure synchronisée et journaux lisibles ?
   │  └─ Non → diagnostiquer NTP / fuseau / accès aux logs
   └─ Configuration relue et validée ?
      ├─ Non → ne pas sauvegarder à l'aveugle
      └─ Oui → copy running-config startup-config
~~~~

**Règle d'or :** conserver un accès de secours, changer une famille de paramètres à la fois, relire la configuration et tester le chemin d'administration depuis le réseau réellement utilisé.
