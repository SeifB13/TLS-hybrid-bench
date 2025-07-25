#!/bin/bash
# Script de vérification de l'installation TLS-hybrid-bench
# Usage: ./verify_installation.sh
# Auteur: SeifB13

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Configuration
INSTALL_PREFIX="$HOME/ossl-3.5"
OQS_PREFIX="$HOME/oqs"
PYTHON_ENV="$HOME/pqc-bench-env"

echo "=========================================="
echo "  Vérification Installation TLS-hybrid-bench"
echo "=========================================="

# Test 1: Fichiers OpenSSL
info "1. Vérification des fichiers OpenSSL..."
if [[ -x "$INSTALL_PREFIX/bin/openssl" ]]; then
    success "Exécutable OpenSSL trouvé"
    version=$("$INSTALL_PREFIX/bin/openssl" version)
    info "   Version: $version"
else
    error "Exécutable OpenSSL manquant: $INSTALL_PREFIX/bin/openssl"
    exit 1
fi

# Test 2: Bibliothèques liboqs
info "2. Vérification de liboqs..."
if [[ -f "$OQS_PREFIX/lib/liboqs.so" ]]; then
    success "Bibliothèque liboqs trouvée"
else
    error "Bibliothèque liboqs manquante: $OQS_PREFIX/lib/liboqs.so"
    exit 1
fi

# Test 3: OQS Provider
info "3. Vérification d'OQS Provider..."
if [[ -f "$INSTALL_PREFIX/lib64/ossl-modules/oqsprovider.so" ]]; then
    success "OQS Provider trouvé"
else
    error "OQS Provider manquant: $INSTALL_PREFIX/lib64/ossl-modules/oqsprovider.so"
    exit 1
fi

# Test 4: Configuration OpenSSL
info "4. Vérification de la configuration..."
if [[ -f "$INSTALL_PREFIX/ssl/openssl.cnf" ]]; then
    success "Fichier de configuration trouvé"
    if grep -q "oqsprovider" "$INSTALL_PREFIX/ssl/openssl.cnf"; then
        success "OQS Provider configuré"
    else
        error "OQS Provider non configuré dans openssl.cnf"
        exit 1
    fi
else
    error "Fichier de configuration manquant"
    exit 1
fi

# Test 5: Variables d'environnement
info "5. Test de l'environnement..."
export LD_LIBRARY_PATH="$INSTALL_PREFIX/lib64:$LD_LIBRARY_PATH"
export OPENSSL_MODULES="$INSTALL_PREFIX/lib64/ossl-modules"
export OPENSSL_CONF="$INSTALL_PREFIX/ssl/openssl.cnf"
export PATH="$INSTALL_PREFIX/bin:$PATH"

# Test 6: Providers chargés
info "6. Test des providers..."
if openssl list -providers | grep -q "oqsprovider"; then
    success "OQS Provider chargé avec succès"
    openssl list -providers | while read line; do
        info "   $line"
    done
else
    error "OQS Provider non chargé"
    info "Debug: Tentative de chargement manuel..."
    openssl list -providers -provider oqsprovider 2>&1 | head -5
    exit 1
fi

# Test 7: Algorithmes post-quantiques
info "7. Test des algorithmes ML-KEM..."
if openssl list -kem-algorithms | grep -q "ML-KEM"; then
    success "Algorithmes ML-KEM disponibles"
    openssl list -kem-algorithms | grep "ML-KEM" | while read line; do
        info "   $line"
    done
else
    error "Algorithmes ML-KEM non disponibles"
    exit 1
fi

# Test 8: Groupes hybrides TLS
info "8. Test des groupes TLS hybrides..."
if openssl list -groups | grep -i "mlkem" | head -1 >/dev/null; then
    success "Groupes hybrides disponibles"
    openssl list -groups | grep -i "mlkem" | while read line; do
        info "   $line"
    done
else
    error "Groupes hybrides non disponibles"
    exit 1
fi

# Test 9: Environnement Python
info "9. Test de l'environnement Python..."
if [[ -d "$PYTHON_ENV" ]]; then
    success "Environnement Python trouvé"
    source "$PYTHON_ENV/bin/activate"
    
    # Test des imports
    if python -c "import pandas, matplotlib, seaborn, numpy, tqdm" 2>/dev/null; then
        success "Dépendances Python OK"
    else
        error "Dépendances Python manquantes"
        info "Réinstallation recommandée: pip install pandas matplotlib seaborn numpy tqdm"
    fi
    
    deactivate
else
    error "Environnement Python manquant: $PYTHON_ENV"
    exit 1
fi

# Test 10: Scripts d'activation
info "10. Test des scripts d'activation..."
if [[ -x "$HOME/activate_oqs_env.sh" ]]; then
    success "Script OpenSSL disponible: ~/activate_oqs_env.sh"
else
    warning "Script d'activation OpenSSL manquant"
fi

if [[ -x "$HOME/activate_python_env.sh" ]]; then
    success "Script Python disponible: ~/activate_python_env.sh"
else
    warning "Script d'activation Python manquant"
fi

# Test 11: Certificats de test
info "11. Test des certificats..."
CERT_DIR="$HOME/Memoire_M2/tls-test"
if [[ -f "$CERT_DIR/server.crt" && -f "$CERT_DIR/server.key" ]]; then
    success "Certificats de test présents"
    
    # Validation du certificat
    if openssl x509 -in "$CERT_DIR/server.crt" -noout -text | grep -q "localhost"; then
        success "Certificat valide pour localhost"
    else
        warning "Certificat invalide ou mal configuré"
    fi
else
    warning "Certificats de test manquants dans $CERT_DIR"
    info "Générez-les avec: openssl req -x509 -new -nodes -days 30 -newkey rsa:3072 -keyout server.key -out server.crt -subj '/CN=localhost'"
fi

# Test 12: Connectivité (si serveur actif)
info "12. Test de connectivité (optionnel)..."
if nc -z localhost 4433 2>/dev/null; then
    info "Serveur TLS détecté sur le port 4433"
    
    # Test connexion hybride
    if timeout 3 openssl s_client -connect localhost:4433 -groups X25519MLKEM768 -brief >/dev/null 2>&1; then
        success "Connexion hybride TLS réussie"
    else
        warning "Connexion hybride échouée (serveur peut être occupé)"
    fi
else
    info "Pas de serveur TLS actif (normal si non démarré)"
fi

echo ""
echo "=========================================="
echo "   RÉSULTAT DE LA VÉRIFICATION"
echo "=========================================="

# Résumé des composants
echo "📦 Composants installés:"
echo "   • OpenSSL: $($INSTALL_PREFIX/bin/openssl version)"
echo "   • liboqs: $(ls -la $OQS_PREFIX/lib/liboqs.so 2>/dev/null | awk '{print $5}' | numfmt --to=iec)B"
echo "   • OQS Provider: Chargé avec succès"
echo "   • Python: $(python3 --version 2>/dev/null || echo 'Non détecté')"

echo ""
echo "🚀 Prêt pour les benchmarks TLS hybrides !"
echo ""
echo "Commandes de démarrage rapide:"
echo "   source ~/activate_oqs_env.sh && source ~/activate_python_env.sh"
echo "   python src/tls_benchmark/measure_tls.py --iterations 100"
echo ""

success "Vérification complète terminée avec succès !"
