#!/bin/bash
# restore-pci-violations.sh
# Restores OrderService.java to its original state before PCI violations were injected

set -e

SERVICE_FILE="order-service/src/main/java/com/example/orders/service/OrderService.java"
BACKUP_FILE="${SERVICE_FILE}.backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

main() {
    print_header "🔄 PCI Violations Restore"
    
    echo "This script will restore OrderService.java to its original state"
    echo ""
    
    # Check if backup exists
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        echo ""
        echo "This means either:"
        echo "  1. Violations were never injected"
        echo "  2. Backup was already restored and deleted"
        echo ""
        exit 1
    fi
    
    # Restore from backup
    echo "📋 Restoring from backup..."
    cp "$BACKUP_FILE" "$SERVICE_FILE"
    print_success "File restored: $SERVICE_FILE"
    
    # Remove backup
    echo ""
    echo "🗑️  Removing backup file..."
    rm "$BACKUP_FILE"
    print_success "Backup removed: $BACKUP_FILE"
    
    echo ""
    print_header "✅ Restore Complete"
    echo ""
    echo "📊 Summary:"
    echo "   OrderService.java has been restored to its original state"
    echo "   All PCI violations have been removed"
    echo "   Backup file has been cleaned up"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Verify the file is clean"
    echo "   2. Check Bob Findings (should show no issues)"
    echo "   3. Run: mvn checkstyle:check (should pass)"
    echo ""
    print_success "Code restored! 🎉"
}

main "$@"

# Made with Bob
