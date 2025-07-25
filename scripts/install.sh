#!/bin/bash
# Installation automatique d'OpenSSL 3.5 + OQS Provider
# Usage: ./install.sh
# Auteur: SeifB13
# Date: Juillet 2025

set -e  # Arrêt sur erreur

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
WORK_DIR="$HOME/Memoire_M2"
INSTALL_PREFIX="$HOME/ossl-3.5"
OQS_PREFIX="$HOME/oqs"
PYTHON_ENV="$HOME/pqc-bench-env"

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis système..."
    
    # Vérification OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        error "Ce script nécessite Ubuntu/Debian Linux ou WSL2"
        exit 1
    fi
    
    # Vérification des outils
    local tools=("git" "cmake" "ninja" "gcc" "python3" "pip3")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "Outil manquant: $tool"
            echo "Exécutez: sudo apt install build-essential git cmake ninja-build python3-pip"
            exit 1
        fi
    done
    
    # Vérification espace disque (2GB minimum)
    local available=$(df "$HOME" | awk 'NR==2 {print $4}')
    if [[ $available -lt 2097152 ]]; then
        warning "Espace disque faible (< 2GB). L'installation peut échouer."
    fi
    
    success "Prérequis validés"
}

# Installation d'OpenSSL 3.5
install_openssl() {
    log "Installation d'OpenSSL 3.5.0..."
    
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Nettoyage si installation précédente
    if [[ -d "$INSTALL_PREFIX" ]]; then
        warning "Installation OpenSSL existante détectée. Suppression..."
        rm -rf "$INSTALL_PREFIX"
    fi
    
    if [[ -d "openssl" ]]; then
        rm -rf openssl
    fi
    
    # Clonage et compilation
    log "Clonage d'OpenSSL 3.5.0..."
    git clone --branch openssl-3.5.0 --depth 1 https://github.com/openssl/openssl.git
    cd openssl
    
    log "Configuration d'OpenSSL avec support FIPS..."
    ./Configure enable-fips --prefix="$INSTALL_PREFIX"
    
    log "Compilation d'OpenSSL (cela peut prendre 5-10 minutes)..."
    make -j$(nproc)
    
    log "Installation d'OpenSSL..."
    make install_sw
    
    # Vérification
    if [[ -x "$INSTALL_PREFIX/bin/openssl" ]]; then
        local version=$("$INSTALL_PREFIX/bin/openssl" version)
        success "OpenSSL installé: $version"
    else
        error "Échec de l'installation d'OpenSSL"
        exit 1
    fi
}

# Installation de liboqs
install_liboqs() {
    log "Installation de liboqs (Open Quantum Safe)..."
    
    cd "$WORK_DIR"
    
    # Nettoyage si installation précédente
    if [[ -d "$OQS_PREFIX" ]]; then
        warning "Installation liboqs existante détectée. Suppression..."
        rm -rf "$OQS_PREFIX"
    fi
    
    if [[ -d "liboqs" ]]; then
        rm -rf liboqs
    fi
    
    # Clonage et compilation
    log "Clonage de liboqs..."
    git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
    cd liboqs
    
    mkdir build && cd build
    
    log "Configuration de liboqs avec ML-KEM activé..."
    cmake -GNinja \
        -DCMAKE_INSTALL_PREFIX="$OQS_PREFIX" \
        -DCMAKE_BUILD_TYPE=Release \
        -DOQS_ENABLE_KEM_MLKEM=ON \
        -DOQS_ENABLE_SIG_DILITHIUM=ON \
        -DOQS_ENABLE_SIG_FALCON=ON \
        -DOQS_ENABLE_SIG_SPHINCS=ON \
        ..
    
    log "Compilation de liboqs..."
    ninja
    
    log "Installation de liboqs..."
    ninja install
    
    # Vérification
    if [[ -f "$OQS_PREFIX/lib/liboqs.so" ]]; then
        success "liboqs installé dans $OQS_PREFIX"
    else
        error "Échec de l'installation de liboqs"
        exit 1
    fi
}

# Installation d'OQS Provider
install_oqs_provider() {
    log "Installation d'OQS Provider..."
    
    cd "$WORK_DIR"
    
    if [[ -d "oqs-provider" ]]; then
        rm -rf oqs-provider
    fi
    
    # Clonage et compilation
    log "Clonage d'OQS Provider..."
    git clone --depth 1 https://github.com/open-quantum-safe/oqs-provider.git
    cd oqs-provider
    
    mkdir build && cd build
    
    log "Configuration d'OQS Provider..."
    cmake -GNinja \
        -DOPENSSL_ROOT_DIR="$INSTALL_PREFIX" \
        -DOPENSSL_LIBRARIES="$INSTALL_PREFIX/lib64" \
        -DCMAKE_PREFIX_PATH="$OQS_PREFIX" \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
        ..
    
    log "Compilation d'OQS Provider..."
    ninja
    
    log "Installation d'OQS Provider..."
    ninja install
    
    # Vérification
    if [[ -f "$INSTALL_PREFIX/lib64/ossl-modules/oqsprovider.so" ]]; then
        success "OQS Provider installé"
    else
        error "Échec de l'installation d'OQS Provider"
        exit 1
    fi
}

# Configuration d'OpenSSL
configure_openssl() {
    log "Configuration d'OpenSSL pour OQS Provider..."
    
    local config_file="$INSTALL_PREFIX/ssl/openssl.cnf"
    
    # Création du répertoire de configuration
    mkdir -p "$(dirname "$config_file")"
    
    # Génération du fichier de configuration
    cat > "$config_file" <<EOF
openssl_conf = openssl_init

[openssl_init]
providers = provider_sect

[provider_sect]
base = base_sect
default = default_sect
oqsprovider = oqs_sect

[base_sect]
activate = 1

[default_sect]
activate = 1

[oqs_sect]
activate = 1
module = $INSTALL_PREFIX/lib64/ossl-modules/oqsprovider.so
EOF
    
    success "Configuration OpenSSL créée: $config_file"
}

# Configuration de l'environnement
setup_environment() {
    log "Configuration de l'environnement..."
    
    local activate_script="$HOME/activate_oqs_env.sh"
    
    cat > "$activate_script" <<EOF
#!/bin/bash
# Configuration automatique de l'environnement OpenSSL + OQS
# Généré par le script d'installation TLS-hybrid-bench

export LD_LIBRARY_PATH="$INSTALL_PREFIX/lib64:\$LD_LIBRARY_PATH"
export OPENSSL_MODULES="$INSTALL_PREFIX/lib64/ossl-modules"
export OPENSSL_CONF="$INSTALL_PREFIX/ssl/openssl.cnf"
export PATH="$INSTALL_PREFIX/bin:\$PATH"

echo "✅ Environnement OpenSSL + OQS activé"
echo "OpenSSL: \$($INSTALL_PREFIX/bin/openssl version)"
echo "Providers: \$($INSTALL_PREFIX/bin/openssl list -providers -provider oqsprovider 2>/dev/null | wc -l) chargés"
EOF
    
    chmod +x "$activate_script"
    success "Script d'activation créé: $activate_script"
    
    # Ajout au .bashrc si souhaité
    if [[ ! -f "$HOME/.bashrc" ]] || ! grep -q "activate_oqs_env.sh" "$HOME/.bashrc"; then
        echo "# Auto-activation OpenSSL + OQS (TLS-hybrid-bench)" >> "$HOME/.bashrc"
        echo "# source ~/activate_oqs_env.sh" >> "$HOME/.bashrc"
        log "Ligne ajoutée à ~/.bashrc (commentée). Décommentez pour activation automatique."
    fi
}

# Installation de l'environnement Python
setup_python_environment() {
    log "Configuration de l'environnement Python..."
    
    # Création de l'environnement virtuel
    if [[ -d "$PYTHON_ENV" ]]; then
        warning "Environnement Python existant. Suppression..."
        rm -rf "$PYTHON_ENV"
    fi
    
    python3 -m venv "$PYTHON_ENV"
    source "$PYTHON_ENV/bin/activate"
    
    # Mise à jour de pip
    pip install --upgrade pip
    
    # Installation des dépendances
    log "Installation des dépendances Python..."
    pip install \
        pandas \
        matplotlib \
        seaborn \
        numpy \
        click \
        tqdm \
        jinja2
    
    success "Environnement Python configuré: $PYTHON_ENV"
    
    # Script d'activation Python
    local python_activate="$HOME/activate_python_env.sh"
    cat > "$python_activate" <<EOF
#!/bin/bash
# Activation de l'environnement Python pour TLS-hybrid-bench
source "$PYTHON_ENV/bin/activate"
echo "✅ Environnement Python activé: $PYTHON_ENV"
EOF
    
    chmod +x "$python_activate"
    log "Script Python créé: $python_activate"
}

# Tests de validation
run_validation_tests() {
    log "Exécution des tests de validation..."
    
    # Chargement de l'environnement
    export LD_LIBRARY_PATH="$INSTALL_PREFIX/lib64:$LD_LIBRARY_PATH"
    export OPENSSL_MODULES="$INSTALL_PREFIX/lib64/ossl-modules"
    export OPENSSL_CONF="$INSTALL_PREFIX/ssl/openssl.cnf"
    export PATH="$INSTALL_PREFIX/bin:$PATH"
    
    local openssl="$INSTALL_PREFIX/bin/openssl"
    
    # Test 1: Version OpenSSL
    log "Test 1: Version OpenSSL"
    local version=$("$openssl" version)
    if [[ "$version" == *"3.5.0"* ]]; then
        success "✓ OpenSSL 3.5.0 détecté"
    else
        error "✗ Version OpenSSL incorrecte: $version"
        return 1
    fi
    
    # Test 2: Providers disponibles
    log "Test 2: Providers OpenSSL"
    if "$openssl" list -providers | grep -q "oqsprovider"; then
        success "✓ OQS Provider chargé"
    else
        error "✗ OQS Provider non disponible"
        return 1
    fi
    
    # Test 3: Algorithmes post-quantiques
    log "Test 3: Algorithmes ML-KEM"
    if "$openssl" list -kem-algorithms | grep -q "ML-KEM-768"; then
        success "✓ ML-KEM-768 disponible"
    else
        error "✗ ML-KEM-768 non disponible"
        return 1
    fi
    
    # Test 4: Groupes hybrides
    log "Test 4: Groupes hybrides TLS"
    if "$openssl" list -groups | grep -q "X25519MLKEM768"; then
        success "✓ Groupe hybride X25519MLKEM768 disponible"
    else
        error "✗ Groupe hybride non disponible"
        return 1
    fi
    
    # Test 5: Environnement Python
    log "Test 5: Environnement Python"
    source "$PYTHON_ENV/bin/activate"
    if python -c "import pandas, matplotlib, seaborn, numpy" 2>/dev/null; then
        success "✓ Dépendances Python disponibles"
    else
        error "✗ Dépendances Python manquantes"
        return 1
    fi
    
    success "Tous les tests de validation réussis !"
}

# Génération du certificat de test
generate_test_certificate() {
    log "Génération du certificat de test..."
    
    local cert_dir="$WORK_DIR/tls-test"
    mkdir -p "$cert_dir"
    
    # Chargement de l'environnement
    export LD_LIBRARY_PATH="$INSTALL_PREFIX/lib64:$LD_LIBRARY_PATH"
    export OPENSSL_MODULES="$INSTALL_PREFIX/lib64/ossl-modules"
    export OPENSSL_CONF="$INSTALL_PREFIX/ssl/openssl.cnf"
    
    local openssl="$INSTALL_PREFIX/bin/openssl"
    
    # Génération clé + certificat RSA 3072
    "$openssl" req -x509 -new -nodes -days 30 \
        -newkey rsa:3072 \
        -keyout "$cert_dir/server.key" \
        -out "$cert_dir/server.crt" \
        -subj "/CN=localhost/O=TLS-Hybrid-Bench/C=FR" \
        2>/dev/null
    
    if [[ -f "$cert_dir/server.crt" && -f "$cert_dir/server.key" ]]; then
        success "Certificat de test généré: $cert_dir/"
        
        # Script de lancement du serveur
        cat > "$cert_dir/start_server.sh" <<EOF
#!/bin/bash
# Script de lancement du serveur TLS pour les tests
source "$HOME/activate_oqs_env.sh"

echo "Démarrage du serveur TLS hybride sur le port 4433..."
echo "Groupes supportés: X25519, X25519MLKEM768"
echo "Arrêt: Ctrl+C"
echo ""

$openssl s_server \\
    -cert "$cert_dir/server.crt" \\
    -key "$cert_dir/server.key" \\
    -groups X25519:X25519MLKEM768 \\
    -tls1_3 \\
    -accept 4433
EOF
        chmod +x "$cert_dir/start_server.sh"
        log "Script serveur créé: $cert_dir/start_server.sh"
    else
        error "Échec de génération du certificat"
        return 1
    fi
}

# Nettoyage en cas d'erreur
cleanup_on_error() {
    error "Erreur détectée. Nettoyage en cours..."
    
    # Suppression des répertoires partiels
    [[ -d "$WORK_DIR/openssl" ]] && rm -rf "$WORK_DIR/openssl"
    [[ -d "$WORK_DIR/liboqs" ]] && rm -rf "$WORK_DIR/liboqs"
    [[ -d "$WORK_DIR/oqs-provider" ]] && rm -rf "$WORK_DIR/oqs-provider"
    
    warning "Nettoyage terminé. Relancez le script pour recommencer."
}

# Affichage du résumé final
print_summary() {
    echo ""
    echo "=========================================="
    echo "   INSTALLATION TERMINÉE AVEC SUCCÈS"  
    echo "=========================================="
    echo ""
    echo "📦 Composants installés:"
    echo "   • OpenSSL 3.5.0 + FIPS: $INSTALL_PREFIX"
    echo "   • liboqs: $OQS_PREFIX"
    echo "   • OQS Provider: $INSTALL_PREFIX/lib64/ossl-modules/"
    echo "   • Environnement Python: $PYTHON_ENV"
    echo ""
    echo "🚀 Pour commencer:"
    echo "   1. Charger l'environnement:"
    echo "      source ~/activate_oqs_env.sh"
    echo ""
    echo "   2. Activer Python:"
    echo "      source ~/activate_python_env.sh"
    echo ""
    echo "   3. Lancer le serveur de test:"
    echo "      $WORK_DIR/tls-test/start_server.sh"
    echo ""
    echo "   4. Tester la connexion (autre terminal):"
    echo "      openssl s_client -connect localhost:4433 -groups X25519MLKEM768 -brief"
    echo ""
    echo "📚 Documentation complète:"
    echo "   docs/protocol/INSTALLATION.md"
    echo ""
    success "Installation complète ! Bon benchmark ! 🔒"
}

# Fonction principale
main() {
    echo "========================================"
    echo "  TLS Hybrid Bench - Installation"
    echo "  OpenSSL 3.5 + OQS Provider"
    echo "========================================"
    echo ""
    
    # Configuration du trap pour nettoyage en cas d'erreur
    trap cleanup_on_error ERR
    
    check_prerequisites
    install_openssl
    install_liboqs
    install_oqs_provider
    configure_openssl
    setup_environment
    setup_python_environment
    generate_test_certificate
    run_validation_tests
    
    print_summary
}

# Exécution si script appelé directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
