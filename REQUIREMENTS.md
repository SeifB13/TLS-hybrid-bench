# Exigences Système - Requirements

## 🖥️ Système d'exploitation

### Pris en charge
- **Ubuntu 22.04 LTS** ou supérieur (recommandé)
- **Debian 11** ou supérieur
- **WSL2** sous Windows 10/11 avec distribution Ubuntu

### Non pris en charge actuellement
- macOS (support prévu v2.0)
- Windows natif (support prévu v2.0)  
- Conteneurs Alpine Linux (bibliothèques manquantes)

## 🔧 Prérequis matériels

### Configuration minimale
- **CPU**: 2 cœurs x86_64
- **RAM**: 4 Go disponibles
- **Stockage**: 3 Go libres
- **Réseau**: Connexion internet pour téléchargements

### Configuration recommandée
- **CPU**: 4+ cœurs avec support AVX2
- **RAM**: 8 Go disponibles
- **Stockage**: 5 Go libres (SSD recommandé)
- **Réseau**: Connexion haut débit (compilations)

## 📦 Dépendances système

### Compilateurs et outils de build
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  build-essential \
  cmake \
  ninja-build \
  git \
  pkg-config \
  libssl-dev
```

### Python et environnement
- **Python**: 3.10 ou supérieur
- **pip**: Version récente
- **venv**: Module d'environnements virtuels

```bash
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev
```

### Outils additionnels
```bash
sudo apt install -y \
  wget \
  curl \
  netcat \
  jq
```

## 🐍 Dépendances Python

### Analyse de données
- `pandas >= 1.5.0` - Manipulation de données
- `numpy >= 1.21.0` - Calculs numériques
- `scipy >= 1.9.0` - Tests statistiques

### Visualisation
- `matplotlib >= 3.5.0` - Graphiques de base
- `seaborn >= 0.11.0` - Visualisations statistiques

### Interface utilisateur
- `tqdm >= 4.60.0` - Barres de progression
- `click >= 8.0.0` - Interface en ligne de commande

### Utilitaires
- `jinja2 >= 3.0.0` - Génération de templates
- `pyyaml >= 6.0` - Configuration YAML

## 🔒 Composants cryptographiques

### OpenSSL 3.5.0
- **Source**: Compilation depuis les sources GitHub
- **Configuration**: `enable-fips` pour la conformité
- **Installation**: `~/ossl-3.5/` (utilisateur)

### liboqs (Open Quantum Safe)
- **Version**: Dernière stable depuis GitHub
- **Algorithmes**: ML-KEM, Dilithium, Falcon, SPHINCS+
- **Configuration optimisée**: AVX2/AVX512 si disponible

### OQS Provider
- **Type**: Module dynamique OpenSSL
- **Intégration**: Chargement automatique via `openssl.cnf`
- **Validation**: Tests de connectivité TLS

## 🌐 Connectivité réseau

### Ports requis
- **4433/tcp**: Serveur TLS de test (localhost uniquement)
- **80/443**: Téléchargements HTTPS (sortant)
- **22**: Git SSH (optionnel)

### Accès internet requis pour
- Clonage des dépôts Git (OpenSSL, liboqs, oqs-provider)
- Téléchargement des paquets système
- Installation des modules Python

## 💾 Espace disque détaillé

### Répartition par composant
```
~/Memoire_M2/                    (~1.5 Go)
├── openssl/                     (200 Mo sources + build)
├── liboqs/                      (150 Mo sources + build)  
├── oqs-provider/                (50 Mo sources + build)
└── tls-test/                    (5 Mo certificats)

~/ossl-3.5/                      (~800 Mo)
├── bin/                         (50 Mo exécutables)
├── lib64/                       (600 Mo bibliothèques)
└── include/                     (150 Mo headers)

~/oqs/                           (~300 Mo)
├── lib/                         (200 Mo bibliothèques)
├── include/                     (50 Mo headers)
└── bin/                         (50 Mo utilitaires)

~/pqc-bench-env/                 (~200 Mo)
└── (environnement Python virtuel)

TOTAL APPROXIMATIF: 2.8 Go
```

## 🧪 Validation des prérequis

### Script de vérification automatique
```bash
# Test des prérequis avant installation
curl -sSL https://raw.githubusercontent.com/SeifB13/TLS-hybrid-bench/main/scripts/check_requirements.sh | bash
```

### Vérifications manuelles

#### Test compilateur
```bash
gcc --version | head -1
# Attendu: gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0

cmake --version | head -1
# Attendu: cmake version 3.22.1 ou supérieur
```

#### Test Python
```bash
python3 --version
# Attendu: Python 3.10.x ou supérieur

python3 -c "import venv, ssl; print('Python OK')"
# Attendu: Python OK
```

#### Test connectivité
```bash
# Test accès GitHub
curl -Is https://github.com | head -1
# Attendu: HTTP/2 200

# Test résolution DNS
nslookup github.com
# Doit résoudre sans erreur
```

## ⚠️ Limitations connues

### Environnements non supportés
- **Docker Alpine**: Bibliothèques glibc manquantes
- **WSL1**: Problèmes de performances et compatibilité
- **Systèmes 32-bit**: Non supporté par liboqs
- **ARM**: Support expérimental uniquement

### Contraintes mémoire
- **Compilation liboqs**: Pics à 2+ Go RAM
- **Tests intensifs**: 500+ Mo par processus Python
- **Serveurs virtuels**: Éviter overcommit mémoire

### Versions obsolètes
- **Ubuntu < 20.04**: Compilateurs trop anciens
- **Python < 3.8**: Syntaxe moderne non supportée
- **OpenSSL < 3.0**: API incompatibles

## 🔧 Résolution de problèmes courants

### Erreur: "cmake not found"
```bash
# Ubuntu/Debian
sudo apt install cmake

# Si version trop ancienne
sudo snap install cmake --classic
```

### Erreur: "ninja not found" 
```bash
sudo apt install ninja-build
# Note: le paquet s'appelle ninja-build, pas ninja
```

### Erreur: "Python.h not found"
```bash
sudo apt install python3-dev
```

### Erreur: "No space left on device"
```bash
# Nettoyage des caches
sudo apt clean
sudo apt autoclean

# Vérification espace
df -h $HOME
```

### Erreur: "Permission denied" WSL2
```bash
# Réinitialisation des permissions
sudo chmod -R 755 ~/Memoire_M2
```

## 📋 Checklist de validation

Avant de lancer l'installation, vérifiez :

- [ ] Système Ubuntu 22.04+ ou WSL2 configuré
- [ ] 4+ Go RAM disponibles  
- [ ] 3+ Go stockage libre
- [ ] Connexion internet stable
- [ ] Droits utilisateur suffisants (pas de root requis)
- [ ] `build-essential cmake ninja-build git` installés
- [ ] `python3 python3-pip python3-venv` installés
- [ ] Accès en écriture à `$HOME`
- [ ] Ports 4433 disponible pour tests
- [ ] Pas d'autre OpenSSL système en conflit

Une fois ces prérequis validés, l'installation automatique devrait se dérouler sans problème.
