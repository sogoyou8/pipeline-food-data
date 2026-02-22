# 🎨 Choix UX/UI — Food Data Dashboard

## 1. Architecture de l'interface

### Pourquoi une Single Page avec deux sections ?

Le dashboard est construit autour de **deux vues principales** accessibles via la navbar sticky :

| Vue | Rôle |
|-----|------|
| **Statistiques** | Vue d'ensemble macro → l'utilisateur comprend le jeu de données en un coup d'œil |
| **Produits** | Exploration détaillée → l'utilisateur recherche, filtre et inspecte un produit |

**Justification** : On suit le pattern **Overview → Detail** (aussi appelé "drill-down"). L'utilisateur commence par le global (combien de produits, quelle distribution) puis descend au niveau unitaire. C'est le pattern standard des dashboards data (Metabase, Looker, etc.).

---

## 2. Layout et hiérarchie visuelle

### Navbar sticky

- **Position fixe en haut** : l'utilisateur peut toujours naviguer entre les sections sans scroller
- **Backdrop-filter blur** : effet de transparence moderne qui laisse deviner le contenu derrière, signalant que la page scrolle "en dessous"
- **Logo + titre à gauche, liens à droite** : convention web universelle (loi de Jakob Nielsen)

### Hero banner

- **Gradient vert** : couleur associée à l'alimentaire et la santé, cohérente avec le sujet
- **Chiffre dynamique** : le compteur animé de produits attire l'attention et donne une première donnée quantitative
- **Minimaliste** : juste un titre + sous-titre, pas de surcharge

### KPI Cards (4 cartes)

- **Icônes emoji** : reconnaissance instantanée sans avoir à lire le label
- **Chiffre très gros, label petit** : hiérarchie typographique → l'œil capte d'abord la valeur
- **Animation au chargement** : les chiffres "comptent" de 0 à la valeur finale → donne une sensation de dynamisme et de données vivantes
- **4 cartes** : rule of 4 en UX → au-delà de 5, la mémoire de travail sature (loi de Miller)

---

## 3. Graphiques et visualisations

### Distribution Nutriscore (barres verticales)

- **Couleurs officielles Nutriscore** (A=vert foncé → E=rouge) : pas besoin de légende, les utilisateurs français reconnaissent immédiatement
- **Barres avec hauteur proportionnelle** : comparaison visuelle instantanée
- **Labels ronds colorés** sous les barres : rappellent le vrai logo Nutriscore
- **Compteur au-dessus** : valeur exacte sans hover (accessible)

**Pourquoi pas un camembert ?** Les camemberts sont mauvais pour comparer des valeurs proches (Cleveland & McGill, 1984). Les barres permettent une comparaison bien plus précise.

### Top Marques / Catégories (barres horizontales)

- **Barres horizontales** : mieux adaptées aux labels texte longs (les noms de marques)
- **Numéro de position** visible : classement clair
- **Gradient sur les barres** : donne de la profondeur sans ajouter d'information inutile
- **Scroll interne** limité à 10 items : évite de noyer l'utilisateur

---

## 4. Système de filtres

### Pourquoi ces 5 filtres ?

| Filtre | Type d'input | Justification |
|--------|-------------|---------------|
| **Recherche texte** | Input texte + icône | Le filtre le plus naturel, premier réflexe utilisateur |
| **Nutriscore** | Chips/boutons | Valeurs discrètes (A-E) → sélection binaire, pas besoin d'un dropdown |
| **Marque** | Input texte | Trop de marques pour un select → recherche libre |
| **Catégorie** | Input texte | Même raison |
| **Qualité minimum** | Range slider | Valeur continue 0-100 → le slider est l'input le plus intuitif |

### Choix UX des filtres

- **Debounce 400ms** sur les inputs texte : évite de spammer l'API à chaque frappe
- **Application immédiate** (pas de bouton "Rechercher") : feedback instantané, l'utilisateur voit les résultats se mettre à jour en temps réel
- **Chips Nutriscore** au lieu d'un select : plus visuel, un seul clic, état actif clairement visible par la couleur
- **Bouton Reset visible** : l'utilisateur peut toujours revenir à l'état initial
- **Compteur de résultats** mis à jour : feedback immédiat sur l'impact du filtre

---

## 5. Liste des produits

### Cards (vue grille)

- **Barre latérale colorée** (4px à gauche) : indique le Nutriscore par couleur, visible même en scannant rapidement la page (pre-attentive processing)
- **Badge Nutriscore rond** en haut à droite : rappel visuel compact
- **Barre de progression qualité** : plus parlant qu'un simple chiffre, perception proportionnelle
- **Tags catégorie/allergène** : limités à 2 pour ne pas encombrer la carte
- **Hover avec élévation** : feedback tactile, indique que la carte est cliquable
- **Troncature du titre à 2 lignes** : uniformité visuelle des cartes

### Vue liste (alternative)

- **Option grille/liste** : les utilisateurs ont des préférences différentes. La vue liste est meilleure pour scanner rapidement beaucoup d'items, la grille pour un aperçu visuel.

### Pourquoi pas de tableau ?

Un tableau est adapté aux données tabulaires denses (Excel, admin). Ici, chaque produit a des données hétérogènes (tags, score visuel, badge). Les **cards** permettent plus de richesse visuelle par item.

---

## 6. Pagination

- **Numéros de pages avec ellipses** : l'utilisateur sait où il est et combien de pages existent
- **Page courante mise en évidence** (fond vert) : repère visuel immédiat
- **Scroll automatique** vers le haut de la section au changement de page
- **Boutons Précédent/Suivant** désactivés aux extrémités : prévention d'erreur (principe de Norman)
- **Masquage des numéros sur mobile** : seuls Précédent/Suivant restent, les numéros prennent trop de place

---

## 7. Modal de détail

### Pourquoi une modale plutôt qu'une nouvelle page ?

- **Contexte conservé** : l'utilisateur ne perd pas sa position dans la liste ni ses filtres
- **Fermeture rapide** : clic overlay, bouton ✕, ou touche Escape
- **Animation d'entrée** : scale + fade → transition douce qui donne une sensation de fluidité

### Organisation du détail

- **Header** : Nutriscore (gros badge carré) + nom + marque + code-barres → identification immédiate
- **Grille 2 colonnes** : Score qualité | Catégories en haut, Nutriments (pleine largeur) en dessous
- **Score qualité avec cercle coloré** + explication textuelle : le chiffre seul ne suffit pas, on explique ce qu'il signifie
- **Nutriments en tableau** avec mini-barres : comparaison visuelle des valeurs entre nutriments
- **Allergènes en rouge** : convention couleur danger/alerte → l'utilisateur identifie immédiatement un risque

---

## 8. Choix de couleurs

| Usage | Couleur | Raison |
|-------|---------|--------|
| Primaire | Vert foncé `#2d6a4f` | Alimentaire, santé, naturel |
| Accent | Vert clair `#52b788` | Fraîcheur, actions positives |
| Catégories | Bleu `#e3f2fd` | Neutre, informatif |
| Allergènes | Rouge `#fce4ec` | Danger, attention |
| Fond | Gris très clair `#f8f9fa` | Contraste doux avec les cartes blanches |

### Accessibilité

- Contraste texte/fond > 4.5:1 (WCAG AA)
- Les couleurs Nutriscore ne sont jamais le seul vecteur d'information (toujours accompagnées de la lettre)
- Focus visible sur les éléments interactifs

---

## 9. Responsive Design

| Breakpoint | Adaptation |
|------------|-----------|
| > 1024px | Grille 3 colonnes, charts côte à côte |
| 768-1024px | Grille 2 colonnes, charts empilés |
| < 768px | 1 colonne, filtres empilés, pagination simplifiée |
| < 480px | KPI en 1 colonne, meta empilés |

**Approche Mobile-First** dans le CSS : les styles de base sont pour mobile, les media queries ajoutent de la complexité pour les grands écrans.

---

## 10. Performance perçue

| Technique | Effet |
|-----------|-------|
| Animation des KPI | L'utilisateur sent que les données "arrivent" |
| Spinner de chargement | Feedback que quelque chose se passe |
| Debounce sur les filtres | Pas de lag pendant la frappe |
| Scroll smooth au changement de page | Transition fluide |
| Pagination serveur (20 items) | Temps de réponse < 200ms |

---

## Résumé des principes UX appliqués

1. **Overview → Detail** (Shneiderman) : stats globales → liste → détail
2. **Loi de Miller** : max 4-5 éléments par groupe
3. **Loi de Fitts** : boutons de taille suffisante, zones de clic généreuses
4. **Feedback immédiat** : chaque action a une réponse visuelle
5. **Prévention d'erreur** (Norman) : boutons désactivés, reset visible
6. **Reconnaissance plutôt que rappel** : icônes, couleurs Nutriscore connues
7. **Consistance** : mêmes couleurs, mêmes rayons, mêmes espacements partout