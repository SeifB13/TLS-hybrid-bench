# TLS Hybrid Bench - Post-Quantum Cryptography Benchmarking Suite

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Banc d'essai pour l'évaluation des performances TLS 1.3 hybride avec cryptographie post-quantique**
> 
> Développé dans le cadre d'un projet de recherche sur la cybersécurité à l'ère quantique (2025)

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture technique](#architecture-technique)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Analyse CARI](#analyse-cari)
- [Résultats](#résultats)
- [Documentation](#documentation)
- [Citation](#citation)
- [Licence](#licence)

## 🎯 Vue d'ensemble

Ce projet fournit un environnement reproductible pour évaluer l'impact des algorithmes post-quantiques hybrides sur les performances TLS 1.3. Il inclut :

- **Banc d'essai TLS** : Mesure de latence pour handshakes classiques vs hybrides
- **Indice CARI** : Crypto-Agility Readiness Index pour évaluer la maturité organisationnelle
- **Scripts d'analyse** : Génération automatique de graphiques et statistiques
- **Documentation complète** : Protocoles de reproduction et guides d'installation

### 🔬 Objectifs scientifiques

- Quantifier l'impact performance des algorithmes ML-KEM-768 dans TLS 1.3
- Développer un indice de maturité pour la transition post-quantique
- Fournir des outils reproductibles pour la recherche en cybersécurité quantique

## 🏗️ Architecture technique

### Composants principaux

```
TLS-hybrid-bench/
├── src/                    # Scripts de mesure et d'analyse
│   ├── tls_benchmark/      # Benchmarks TLS 1.3
│   ├── cari_analysis/      # Calcul de l'indice CARI
│   └── utils/              # Utilitaires communs
├── data/                   # Jeux de données
│   ├── input/              # Données d'entrée
│   └── output/             # Résultats générés
├── results/                # Figures et rapports
│   ├── figures/            # Graphiques vectoriels (PDF)
│   └── reports/            # Analyses détaillées
└── scripts/                # Scripts d'installation et utilitaires
```

### Stack technologique

- **OpenSSL 3.5** + **OQS Provider 0.9.0** (cryptographie post-quantique)
- **Python 3.10+** (analyse de données)
- **Pandas**, **Matplotlib**, **Seaborn** (visualisation)
- **Ubuntu 22.04+ / WSL2** (environnement recommandé)

## 🚀 Installation

### Prérequis système

```bash
# Ubuntu 22.04+ ou WSL2
sudo apt update && sudo apt install -y \
  build-essential git ninja-build cmake \
  libssl-dev pkg-config python3-pip python3-venv
```

### Installation automatique

```bash
# Cloner le dépôt
git clone https://github.com/SeifB13/TLS-hybrid-bench.git
cd TLS-hybrid-bench

# Exécuter le script d'installation
chmod +x scripts/install.sh
./scripts/install.sh
```

### Vérification

```bash
# Activer l'environnement
source scripts/activate_env.sh

# Vérifier l'installation
./scripts/verify_installation.sh
```

## 📊 Utilisation

### 1. Benchmark TLS 1.3

```bash
# Terminal 1 : Lancer le serveur TLS
./scripts/start_tls_server.sh

# Terminal 2 : Exécuter les mesures
python src/tls_benchmark/measure_tls.py --iterations 1000
```

### 2. Analyse CARI

```bash
# Calculer l'indice CARI
python src/cari_analysis/compute_cari.py

# Générer les radars
python src/cari_analysis/generate_radars.py
```

### 3. Génération des rapports

```bash
# Rapport complet
python src/utils/generate_report.py --format pdf
```

## 📈 Analyse CARI

Le **Crypto-Agility Readiness Index (CARI)** évalue la maturité organisationnelle selon 10 critères :

| Critère | Poids | Description |
|---------|-------|-------------|
| Manque de normes | 12% | Absence de standards d'hybridation |
| Hybridation non standardisée | 10% | Protocoles propriétaires |
| Bibliothèques de référence | 10% | Manque d'implémentations certifiées |
| Référentiels obsolètes | 8% | Documentation non mise à jour |
| Équipements matériels | 8% | HSM non compatibles PQC |
| Performance signatures | 5% | Impact sur les temps de traitement |
| Plan de transition | 15% | Absence de feuille de route |
| Certification bibliothèques | 12% | Validation sécuritaire |
| Sensibilisation | 10% | Formation des équipes |
| Coût compétences | 10% | Investissement en formation |

### Profils évalués

- **Spécialistes** (CARI: 100%) : Éditeurs de bibliothèques cryptographiques
- **Sensibilisés** (CARI: 83.8%) : Organisations ayant initié la démarche  
- **Non sensibilisés** (CARI: 67.6%) : Entreprises sans préparation PQC

## 📋 Résultats

### Performance TLS 1.3 Hybride

Mesures sur 1000 handshakes :
- **Classique (X25519)** : 76.6 ms (moyenne)
- **Hybride (X25519+ML-KEM-768)** : 71.3 ms (moyenne)
- **Impact** : -6.9% (non significatif statistiquement)

### Conclusions

✅ **Faisabilité technique confirmée**  
✅ **Pas de dégradation performance notable**  
✅ **Compatible infrastructures existantes**  

## 📚 Documentation

- [Installation détaillée](docs/protocol/INSTALLATION.md)
- [Protocole expérimental](docs/protocol/EXPERIMENTAL_PROTOCOL.md)
- [Méthodologie CARI](docs/protocol/CARI_METHODOLOGY.md)
- [Reproduction des résultats](docs/protocol/REPRODUCTION.md)

## 🔬 Citation

```bibtex
@misc{seifb13_2025_quantum,
  title={Cybersécurité à l'ère quantique : défis et stratégies d'adaptation pour les entreprises},
  author={SeifB13},
  year={2025},
  type={Projet de recherche},
  url={https://github.com/SeifB13/TLS-hybrid-bench}
}
```

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour les détails.

---

**Auteur** : SeifB13  
**Date** : Juillet 2025
