# Optimisation de la satisfaction support : interpréter CSAT et NPS avec méthode

> **Mise en contexte**
>
> La satisfaction ne se décrète pas à partir d'un score vert. Un utilisateur peut apprécier la politesse d'un agent tout en restant bloqué dans son travail ; un autre peut être mécontent du délai alors que l'équipe a respecté un engagement réaliste. Au niveau expert, il faut combiner les enquêtes, les retours qualitatifs, les données opérationnelles et l'analyse du parcours pour comprendre ce qui influence l'expérience, puis mesurer si les actions corrigent réellement les irritants.

## 1. Clarifier ce que l'on mesure

La satisfaction client (CSAT) mesure généralement une appréciation liée à une interaction ou à un résultat, à l'aide d'une question et d'une échelle définies. Le Net Promoter Score (NPS) mesure la propension déclarée à recommander une organisation, un service ou un produit, souvent sur une échelle de 0 à 10. Les deux approches ne mesurent pas exactement la même chose et ne doivent pas être utilisées comme des synonymes.

Le CSAT peut être pertinent après la résolution d'un ticket : « Dans quelle mesure êtes-vous satisfait de l'aide reçue ? » Il faut décider si le score représente l'interaction avec l'agent, la résolution du problème ou le parcours entier. Le NPS porte davantage sur une relation plus large ; une question NPS posée après chaque ticket peut être mal adaptée, car l'utilisateur évalue alors des éléments qu'il ne peut pas distinguer.

La satisfaction, l'effort perçu, la résolution au premier contact, le délai et la fidélité déclarée sont des dimensions complémentaires. Une bonne expérience suppose souvent que la demande soit résolue, que l'utilisateur comprenne ce qui s'est passé et sache quoi faire ensuite. Le choix des questions doit découler de la décision que vous souhaitez prendre.

## 2. Calculer et interpréter CSAT et NPS

Pour un CSAT calculé comme le pourcentage de réponses positives, la formule doit préciser quelles catégories de l'échelle sont considérées comme positives :

~~~text
CSAT positif (%) = nombre de réponses définies comme positives / nombre de réponses valides × 100
~~~

Il existe plusieurs façons de calculer et présenter le CSAT. Certaines organisations publient la moyenne d'une échelle ; d'autres publient la part des réponses dans les catégories supérieures. Il faut annoncer la méthode et ne pas comparer deux chiffres calculés différemment.

Dans une enquête NPS sur une échelle de 0 à 10, les réponses sont généralement classées en promoteurs (9-10), passifs (7-8) et détracteurs (0-6). Le score est la part de promoteurs moins la part de détracteurs, exprimée en points, et peut donc aller de -100 à +100. Les passifs sont inclus dans le total des réponses mais ne s'ajoutent ni à la part des promoteurs ni à celle des détracteurs.

~~~text
NPS = % promoteurs - % détracteurs
~~~

Ne présentez pas un NPS comme un pourcentage de clients satisfaits. Ce serait une interprétation incorrecte. De même, une différence de quelques points n'est pas nécessairement significative, surtout si le volume de réponses est faible ou si la population répondante a changé.

## 3. Concevoir une enquête utile

Une enquête commence par une question précise, un public défini, un moment approprié et une décision attendue. Une question qui demande simultanément si le délai, la compétence, l'accueil et le résultat étaient satisfaisants mélange plusieurs dimensions. Un score global peut être conservé pour un suivi, mais il doit être complété par des questions ciblées ou des commentaires permettant d'identifier les causes.

Gardez le questionnaire court. Utilisez une échelle compréhensible, des libellés équilibrés et une option « non applicable » lorsque nécessaire. Évitez les formulations qui suggèrent la réponse attendue et les questions doubles. Précisez la période de référence et ne sollicitez pas plusieurs fois la même personne sans raison.

Le moment d'envoi influence les réponses. Une enquête immédiate peut recueillir le ressenti sur l'agent, mais être trop rapide pour savoir si le problème est réellement résolu. Une enquête trop tardive peut être affectée par des événements ultérieurs. Le moment doit correspondre à la dimension mesurée et rester cohérent dans le temps.

~~~mermaid
flowchart TD
    A[Décision à éclairer] --> B[Choisir la dimension mesurée]
    B --> C[Définir public et moment]
    C --> D[Écrire et tester la question]
    D --> E[Collecter les réponses]
    E --> F[Contrôler biais et volume]
    F --> G[Analyser les causes]
    G --> H[Action et mesure de suivi]
~~~

## 4. Comprendre les biais et les limites

Le biais de non-réponse est important : les personnes très satisfaites ou très mécontentes peuvent répondre plus souvent que les autres. Le canal de collecte, la langue, l'horaire, la complexité du ticket et le type de demande peuvent également influencer la participation. Le score des répondants ne représente pas automatiquement l'ensemble des utilisateurs.

Publiez le nombre de réponses, le taux de réponse lorsqu'il peut être calculé et la population interrogée. Comparez les groupes avec prudence, surtout quand certains groupes ont peu de réponses. Pour de petits effectifs, évitez des classements qui permettraient d'identifier indirectement une personne.

Le score peut évoluer parce que la composition des répondants change, et non parce que le service s'améliore ou se dégrade. Segmentez par type de demande, canal, région et issue, mais conservez assez de volume pour interpréter les résultats. Documentez les changements d'enquête, d'échelle ou de moment : une série historique n'est comparable que si les conditions de mesure le permettent.

Ne demandez pas au support d'augmenter le score par pression sur les utilisateurs, en filtrant les destinataires ou en les incitant à modifier leur réponse. La mesure doit refléter l'expérience, pas devenir un objectif qui encourage la manipulation.

## 5. Relier le ressenti aux données opérationnelles

Un score faible décrit une expérience ; il n'explique pas automatiquement pourquoi elle s'est produite. Croisez les retours avec les délais, les transferts, la réouverture, la résolution au premier contact, la qualité des communications et le type de demande. Un même score peut cacher plusieurs causes : absence de mise à jour, problème qui revient, procédure compliquée, manque de clarté ou délai imposé par une dépendance externe.

~~~mermaid
flowchart LR
    A[Score et commentaire] --> D[Analyse du parcours]
    B[Délais et transferts] --> D
    C[Réouverture et résultat] --> D
    D --> E[Hypothèses de cause]
    E --> F[Échantillon de tickets et entretiens]
    F --> G[Action ciblée]
    G --> H[Mesure avant/après]
~~~

Analysez les commentaires avec un codage cohérent : délai, qualité de solution, communication, effort utilisateur, outil, accès, transfert ou autre cause. Lisez régulièrement un échantillon brut, car une classification automatique peut manquer le sarcasme, le contexte et le problème métier. Gardez l'incertitude visible lorsqu'un commentaire ne permet pas de conclure.

Identifiez les moments de vérité du parcours : ouverture du ticket, premier retour, transfert, annonce d'un retard, résolution et réouverture. La qualité de la communication lors d'un retard peut améliorer la compréhension sans remplacer le besoin de corriger la cause du délai.

~~~mermaid
flowchart TD
    A[Retour utilisateur] --> B[Accuser réception et qualifier]
    B --> C[Analyser les faits]
    C --> D{Action nécessaire ?}
    D -->|Individuelle| E[Réponse et suivi du dossier]
    D -->|Structurelle| F[Action d'amélioration]
    E --> G[Confirmer la suite]
    F --> H[Mesurer l'effet]
    G --> I[Informer et capitaliser]
    H --> I
~~~

## 6. Fermer la boucle avec les utilisateurs

« Fermer la boucle » signifie que le retour recueilli provoque une analyse et, lorsque c'est pertinent, une réponse ou une action. Une équipe doit distinguer le suivi individuel d'un retour et les améliorations structurelles à l'échelle du service.

Pour un utilisateur insatisfait, vérifiez les faits, reconnaissez l'impact, expliquez les actions réalistes et donnez un point de contact. Ne promettez pas une correction qui dépend d'une autre équipe sans accord. Le suivi individuel ne doit pas révéler les détails confidentiels d'un autre dossier.

À l'échelle collective, publiez des améliorations concrètes : formulaire simplifié, procédure corrigée, notification plus claire ou délai mieux annoncé. Expliquez ce qui a été retenu et ce qui ne peut pas être modifié, avec une raison compréhensible. Cette transparence renforce la confiance et incite les personnes à fournir des retours utiles.

## 7. Segmenter sans punir ni masquer

Comparer des agents par CSAT peut être trompeur. Certains reçoivent les demandes les plus difficiles, les utilisateurs en colère ou les cas qui nécessitent plusieurs équipes. Le score peut aussi être influencé par des facteurs hors du contrôle de l'agent. L'analyse doit se concentrer sur les conditions de service et sur les pratiques modifiables, avec des échantillons suffisants.

Les segments sont utiles pour chercher des motifs, mais trop de découpages peuvent produire des conclusions instables. Définissez à l'avance les dimensions pertinentes et évitez de sélectionner uniquement le segment qui confirme une hypothèse. Lorsque la taille d'un groupe est faible, agrégerez les résultats ou indiquez qu'aucune conclusion robuste n'est possible.

## 8. Construire un plan d'amélioration expérimental

Pour chaque action, formulez une hypothèse et une mesure de garde-fou. Exemple : « Si nous donnons une prochaine heure de mise à jour au lieu d'un message générique, la satisfaction sur la communication augmentera sans augmenter le volume de relances. » Mesurez une référence, testez sur une population limitée et documentez les autres changements qui pourraient influencer les résultats.

N'interprétez pas une amélioration avant/après comme une preuve absolue de causalité. Le volume, la saison, une mise à jour logicielle ou la composition des tickets ont pu changer. Examinez un échantillon de commentaires, les métriques opérationnelles et l'évolution d'un groupe comparable si c'est possible et raisonnable.

~~~mermaid
flowchart TD
    A[Signal d'insatisfaction] --> B[Formuler une hypothèse]
    B --> C[Définir référence et garde-fous]
    C --> D[Test limité]
    D --> E[Comparer scores et résultats]
    E --> F{Bénéfice durable ?}
    F -->|Oui| G[Déployer et documenter]
    F -->|Non| H[Adapter ou arrêter]
    G --> I[Surveiller]
    H --> B
~~~

## 9. Atelier pratique corrigé : score en baisse après une migration

**Situation.** Le CSAT positif passe de 88 % à 79 % après la migration d'un portail. Le volume de réponses a diminué de moitié. Les commentaires parlent de difficulté à retrouver les catégories et de demandes réaffectées.

**Étape 1 — Contrôler la mesure.** Vérifier l'échelle, le moment d'envoi, la population, le nombre de réponses et le taux de participation. S'assurer que les périodes sont comparables.

**Étape 2 — Examiner le parcours.** Comparer les tickets mal catégorisés, les réaffectations, le temps de saisie et les demandes abandonnées avant et après migration. Lire un échantillon de commentaires.

**Étape 3 — Formuler des hypothèses.** La navigation peut être moins claire, les catégories peuvent avoir changé ou le groupe répondant peut avoir évolué. Ne retenir aucune explication sans preuve complémentaire.

**Étape 4 — Tester une action.** Réviser les libellés, proposer des recherches par synonymes et réaliser un test d'usage avec des utilisateurs représentatifs. Garder le questionnaire identique pendant la période pilote.

**Étape 5 — Vérifier.** Suivre la qualité de catégorisation, les réaffectations, les abandons et le CSAT avec son taux de réponse. Généraliser seulement si l'expérience s'améliore sans déplacer les problèmes vers une autre étape.

## 10. Exercices corrigés

**Exercice A.** Le NPS passe de +10 à +25 avec seulement douze réponses dans le second mois. Peut-on annoncer une amélioration générale ?

**Correction.** Présenter la variation comme un signal préliminaire, afficher l'effectif et vérifier le profil des répondants. Un petit échantillon peut fluctuer fortement. Chercher des preuves supplémentaires dans les commentaires et les métriques opérationnelles avant une conclusion générale.

**Exercice B.** Un commentaire dit « agent très agréable, mais j'ai attendu quatre jours sans information ». Quelle action est la plus pertinente ?

**Correction.** Distinguer qualité relationnelle et qualité du parcours. Examiner la cause du délai et la cadence des mises à jour. Le problème peut être une dépendance, une charge ou une règle de communication. Une réponse plus polie ne résoudra pas l'absence d'information.

## 11. Défi final corrigé

**Défi.** Concevez un programme de mesure d'expérience sur 90 jours avec CSAT, NPS ou une mesure d'effort, suivi des retours et trois actions prioritaires.

**Proposition de correction.** Définir une question CSAT après résolution, une enquête relationnelle moins fréquente si le NPS sert à mesurer la relation globale, et un suivi de l'effort pour un parcours ciblé. Documenter la population, le moment, le taux de réponse et les limites. Analyser commentaires et données de tickets, choisir les trois irritants les plus impactants et lancer des pilotes dotés d'une mesure principale et de garde-fous. Réaliser une revue mensuelle, publier les actions prises et conserver la même méthode de mesure autant que possible.

## 12. Checklist de mesure

- La question correspond à une décision et à une dimension claire.
- La formule CSAT ou NPS et l'échelle sont documentées.
- Le volume de réponses, le taux de participation et les limites sont visibles.
- Les biais de non-réponse et les changements de population sont examinés.
- Les scores sont croisés avec les résultats opérationnels et les commentaires.
- Les petits groupes sont protégés contre l'identification indirecte.
- Les retours conduisent à une réponse ou à une action traçable.
- Les pilotes sont évalués avec une référence et des garde-fous.

**À retenir :** mesurer l'expérience n'a de valeur que si la question est adaptée, les biais visibles et les retours transformés en changements mesurables. Un score ne remplace jamais l'analyse du parcours réel.
