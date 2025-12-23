# Interface Chat Style

## Vue d'ensemble
Cette nouvelle interface transforme l'expérience de recherche en une conversation naturelle avec Tchaller, similaire à l'interaction avec ChatGPT, plutôt que d'afficher des résultats mécaniques.

## Caractéristiques principales

### 1. Conversation naturelle
- **Messages en bulles** : Les échanges sont présentés dans des bulles de conversation distinctes
- **Typing indicator** : Animation de saisie pour une expérience plus réaliste
- **Avatar personnalisé** : Icônes distinctes pour l'utilisateur et Tchaller

### 2. Structure de conversation
1. **Message d'accueil** : Présentation chaleureuse de Tchaller
2. **Messages utilisateur** : Alignés à droite avec fond orange
3. **Réponses de Tchaller** : Alignées à gauche avec fond gris clair
4. **Suggestions rapides** : Chips cliquables pour les recherches courantes

### 3. Réponse conversationnelle
- **Texte naturel** : La réponse générée par l'IA est affichée en premier comme dans une conversation
- **Cartes d'activités** : Les détails techniques sont présentés sous forme de cartes intégrées dans le message de Tchaller

## Avantages par rapport à l'ancienne interface

### Ancienne interface (mécanique)
- Résultats structurés en cartes séparées
- Pas de contexte conversationnel
- Interface plus formelle et moins engageante

### Nouvelle interface (chat style)
- **Expérience immersive** : Conversation fluide avec Tchaller
- **Engagement accru** : L'utilisateur se sent plus connecté à l'assistant
- **Hiérarchie d'information** : Réponse naturelle en premier, détails techniques en support
- **Accessibilité** : Interface tactile intuitive avec suggestions rapides

## Fonctionnalités techniques

### Auto-redimensionnement du champ de saisie
Le textarea s'adapte automatiquement à la longueur du message, jusqu'à 150px de hauteur.

### Navigation au clavier
- **Enter** : Envoyer le message
- **Shift + Enter** : Saut de ligne
- **Clic sur les chips** : Insertion automatique du prompt

### Design responsive
- Adapté aux mobiles et tablettes
- Bulles de conversation qui s'ajustent à la taille de l'écran
- Layout optimisé pour le tactile

## Personnalisation

### Couleurs et branding
- **Orange (#ff5b2e)** : Couleur principale pour l'identité Tchaller
- **Dégradés subtils** : Pour un effet moderne et professionnel
- **Contraste accessible** : Respect des normes d'accessibilité

### Animations
- **Fade-in** : Apparition progressive des messages
- **Bounce** : Animation des points de saisie
- **Transitions** : Effets de survol sur les boutons

## Intégration backend

L'interface utilise le même endpoint API :
```
POST https://tchallerback.onrender.com/api/v1/search/
```

Mais présente les données différemment :
1. Le champ `response` est affiché comme message principal
2. Les `activities` sont intégrées comme cartes dans le message de Tchaller.

## Exemple d'interaction

**Utilisateur** : "Trouve-moi une pharmacie ouverte maintenant"

**Tchaller** :
```
Parfait ! J'ai trouvé 3 pharmacies qui correspondent à ta recherche :

**Pharmacie Centrale**
à 780m (Santé) - ✅ OUVERT - ⭐ 4.6/5 (163 avis) - €€
📞 +2250794520607, 💬 +2250794520607

Veux-tu voir les 2 autres options ?
```

[Suivi des cartes détaillées des pharmacies]

Cette approche transforme l'expérience de recherche en une conversation naturelle avec un assistant IA, tout en conservant l'accès aux informations techniques détaillées.