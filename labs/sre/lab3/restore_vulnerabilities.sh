#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# Vulnerability Restoration Script
# 
# Removes injected vulnerabilities and restores original code.
# Works with both injection approaches.
#
# Usage:
#   ./pipeline/restore_vulnerabilities.sh
# ═══════════════════════════════════════════════════════════════════

set -e

SECURITY_SERVICE="order-service/src/main/java/com/example/orders/service/SecurityService.java"
ORDER_SERVICE="order-service/src/main/java/com/example/orders/service/OrderService.java"
ORDER_SERVICE_BACKUP="$ORDER_SERVICE.backup"

CLEANED=0

echo "🧹 Restoring original code and removing vulnerabilities..."
echo ""

# Remove SecurityService.java if it exists (Approach 1)
if [ -f "$SECURITY_SERVICE" ]; then
    echo "🗑️  Removing SecurityService.java..."
    rm "$SECURITY_SERVICE"
    echo "   ✅ Deleted: $SECURITY_SERVICE"
    CLEANED=1
fi

# Restore OrderService.java from backup if it exists (Approach 2)
if [ -f "$ORDER_SERVICE_BACKUP" ]; then
    echo "♻️  Restoring OrderService.java from backup..."
    mv "$ORDER_SERVICE_BACKUP" "$ORDER_SERVICE"
    echo "   ✅ Restored: $ORDER_SERVICE"
    CLEANED=1
fi

if [ $CLEANED -eq 0 ]; then
    echo "ℹ️  No vulnerabilities found to clean up."
    echo "   The codebase appears to be in its original state."
else
    echo ""
    echo "✅ Cleanup complete! Original code restored."
    echo ""
    echo "🧪 Verify restoration:"
    echo "   cd order-service && mvn compile"
    echo "   cd order-service && mvn test"
fi

echo ""

# Made with Bob
