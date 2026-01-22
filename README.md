# PoE2 Trade Analyzer
Outil d’analyse et de comparaison des devises sur Path of Exile 2.
Il permet de détecter automatiquement des opportunités d’arbitrage entre Chaos / Divine / Exalted à partir des données de trade.

## Fonctionnalités
### Overview
Vue globale de l’état du marché :
- Affichage de toutes les devises principales
- Taux de change croisés (Chaos ⇄ Divine ⇄ Exalted)
- Volumes de trade
- Données de liquidité
- Accès direct au détail d’une devise

Objectif :
- Comprendre rapidement quelles devises sont liquides, chères ou sous-valorisées.

### Opportunities Scanner
Scanner automatique d’opportunités d’arbitrage.
Pour chaque devise, l’outil :
Compare les taux de change entre :
- Chaos ⇄ Divine
- Chaos ⇄ Exalted
- Divine ⇄ Exalted

Applique :
- Slippage d’achat
- Slippage de vente
- Filtres de liquidité
- Filtres de profit

Calcule :
- Profit %
- Profit par unité
- Volume exploitable
- Score de priorité

Résultat :
- Une liste triée d’opportunités réellement exploitables.

#### Logique de scoring
Chaque opportunité reçoit un score basé sur :
Score = Profit % × √(liquidité) × SpreadFactor + Bonus(profit valeur)
- Plus le profit % est élevé → score ↑
- Plus la liquidité est forte → score ↑
- Plus le spread est faible → score ↑
- Plus le profit réel par unité est élevé → score ↑

Cela évite de favoriser :
- des trades très profitables mais impossibles à exécuter
- ou des trades liquides mais non rentables

## Stack technique
- Python
- Streamlit
- JSON (données de marché)