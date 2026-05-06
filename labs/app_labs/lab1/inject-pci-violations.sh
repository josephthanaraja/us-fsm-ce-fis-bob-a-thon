#!/bin/bash
# inject-pci-violations.sh
# Injects simple PCI coding standard violations into OrderService.java for lab practice
# Each violation is easy to identify and fix

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

main() {
    print_header "🔧 PCI Violations Injector"
    
    echo "This script will inject 6 simple PCI coding standard violations into OrderService.java"
    echo "Each violation corresponds to one PCI rule and is easy to fix."
    echo ""
    
    # Check if file exists
    if [ ! -f "$SERVICE_FILE" ]; then
        print_error "OrderService.java not found at: $SERVICE_FILE"
        exit 1
    fi
    
    # Create backup
    echo "📋 Creating backup..."
    cp "$SERVICE_FILE" "$BACKUP_FILE"
    print_success "Backup created: $BACKUP_FILE"
    
    echo ""
    echo "💉 Injecting PCI violations..."
    echo ""
    
    # Read the original file
    ORIGINAL_CONTENT=$(cat "$SERVICE_FILE")
    
    # Create new content with violations
    cat > "$SERVICE_FILE" << 'EOF'
package com.example.orders.service;

import com.example.orders.model.Order;
import com.example.orders.repository.OrderRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Random;

@Service
public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);
    
    // PCI-02 VIOLATION: Hardcoded API key (easy to fix - move to environment variable)
    private static final String API_KEY = "sk_test_1234567890";

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public List<Order> getAllOrders() {
        logger.info("Fetching all orders");
        return orderRepository.findAll();
    }

    public Optional<Order> getOrderById(Long id) {
        logger.info("Fetching order with id: {}", id);
        return orderRepository.findById(id);
    }

    public List<Order> getOrdersByStatus(String status) {
        return orderRepository.findByStatus(status);
    }

    public Order createOrder(Order order) {
        if (order.getStatus() == null) {
            order.setStatus("PENDING");
        }
        
        // PCI-01 VIOLATION: Using System.out (easy to fix - use logger instead)
        System.out.println("Creating order for customer: " + order.getCustomerName());
        
        return orderRepository.save(order);
    }

    public Order updateOrderStatus(Long id, String status) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Order not found: " + id));

        validateStatusTransition(order.getStatus(), status);
        order.setStatus(status);
        logger.info("Updated order {} status to {}", id, status);
        return orderRepository.save(order);
    }

    public void deleteOrder(Long id) {
        logger.info("Deleting order with id: {}", id);
        orderRepository.deleteById(id);
    }

    private void validateStatusTransition(String currentStatus, String newStatus) {
        // Allow all transitions
    }
    
    // PCI-06 VIOLATION: Unresolved TODO (easy to fix - implement or remove)
    // TODO: Add order validation logic
    
    public String generateOrderConfirmation(Long orderId) {
        try {
            Order order = orderRepository.findById(orderId)
                    .orElseThrow(() -> new RuntimeException("Order not found"));
            
            // PCI-05 VIOLATION: Using weak Random (easy to fix - use SecureRandom)
            Random random = new Random();
            int confirmationCode = random.nextInt(999999);
            
            return "Order #" + orderId + " - Confirmation: " + confirmationCode;
        } catch (Exception e) {
            // PCI-04 VIOLATION: Using printStackTrace (easy to fix - use logger.error)
            e.printStackTrace();
            return "Error generating confirmation";
        }
    }
    
    public void connectToExternalService() {
        // PCI-03 VIOLATION: Hardcoded IP address (easy to fix - use configuration)
        String serviceUrl = "http://192.168.1.100:8080/api";
        logger.info("Connecting to external service at: {}", serviceUrl);
    }
}
EOF
    
    print_success "PCI-01: System.out.println() injected (line 47)"
    print_success "PCI-02: Hardcoded API key injected (line 18)"
    print_success "PCI-03: Hardcoded IP address injected (line 92)"
    print_success "PCI-04: printStackTrace() injected (line 84)"
    print_success "PCI-05: Weak Random injected (line 80)"
    print_success "PCI-06: Unresolved TODO injected (line 70)"
    
    echo ""
    print_header "✅ Injection Complete"
    echo ""
    echo "📊 Summary:"
    echo "   File modified: $SERVICE_FILE"
    echo "   Backup saved: $BACKUP_FILE"
    echo "   Violations injected: 6 (one for each PCI rule)"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Open OrderService.java in your editor"
    echo "   2. Check Bob Findings to see the violations"
    echo "   3. Use Code Reviewer mode to analyze"
    echo "   4. Fix each violation following the lab guide"
    echo ""
    echo "🔄 To restore original code:"
    echo "   ./labs/app_labs/lab1/restore-pci-violations.sh"
    echo ""
    print_success "Ready for lab! 🎉"
}

main "$@"

# Made with Bob
