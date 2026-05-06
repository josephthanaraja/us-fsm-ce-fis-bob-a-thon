#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# Vulnerability Injection Script - New SecurityService.java
# 
# Creates a new SecurityService.java file with 6 common security
# vulnerabilities to demonstrate AI-driven security detection in CI/CD.
#
# Usage:
#   ./pipeline/inject_vulnerabilities_new_file.sh
#
# To remove:
#   ./pipeline/restore_vulnerabilities.sh
# ═══════════════════════════════════════════════════════════════════

set -e

TARGET_DIR="order-service/src/main/java/com/example/orders/service"
TARGET_FILE="$TARGET_DIR/SecurityService.java"

echo "🔧 Injecting vulnerabilities into new SecurityService.java..."
echo ""

# Check if file already exists
if [ -f "$TARGET_FILE" ]; then
    echo "⚠️  SecurityService.java already exists!"
    echo "    Run ./pipeline/restore_vulnerabilities.sh first to clean up."
    exit 1
fi

# Create the vulnerable SecurityService.java
cat << 'EOF' > "$TARGET_FILE"
package com.example.orders.service;

import com.example.orders.model.Order;
import org.springframework.stereotype.Service;
import java.sql.Connection;
import java.sql.Statement;
import java.sql.ResultSet;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * SecurityService - INTENTIONALLY VULNERABLE for security testing demo
 * 
 * This service contains 6 common security vulnerabilities:
 * 1. SQL Injection (CWE-89)
 * 2. Hardcoded Credentials (CWE-798)
 * 3. Weak Cryptography - MD5 (CWE-327)
 * 4. Insecure Logging (CWE-532)
 * 5. Weak Random Number Generation (CWE-330)
 * 6. Exception Information Exposure (CWE-209)
 */
@Service
public class SecurityService {

    // VULNERABILITY 2: Hardcoded Credentials (CWE-798)
    // PCI Checkstyle: PCI-02-NoHardcodedSecrets
    // SonarQube: java:S2068
    private static final String DB_PASSWORD = "prod_password_2024!";
    private static final String API_KEY = "sk-1234567890abcdef";
    private static final String BACKUP_DB_URL = "jdbc:postgresql://10.0.1.50:5432/orders";

    /**
     * VULNERABILITY 1: SQL Injection (CWE-89)
     * Concatenates user input directly into SQL query
     * SonarQube: java:S2077
     * PCI DSS: 6.5.1 (Injection flaws)
     */
    public List<Order> searchOrdersByCustomer(String customerName, Connection conn) throws Exception {
        Statement stmt = conn.createStatement();
        // Vulnerable: Direct string concatenation in SQL
        String sql = "SELECT * FROM orders WHERE customer_name = '" + customerName + "'";
        ResultSet rs = stmt.executeQuery(sql);
        
        List<Order> orders = new ArrayList<>();
        while (rs.next()) {
            Order order = new Order();
            order.setId(rs.getLong("id"));
            order.setCustomerName(rs.getString("customer_name"));
            order.setProduct(rs.getString("product"));
            orders.add(order);
        }
        return orders;
    }

    /**
     * VULNERABILITY 3: Weak Cryptography - MD5 (CWE-327)
     * Uses MD5 for password hashing (cryptographically broken)
     * SonarQube: java:S4790
     * PCI DSS: 4.1 (Strong cryptography required)
     */
    public String hashPassword(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        md.update(password.getBytes());
        byte[] digest = md.digest();
        
        StringBuilder hexString = new StringBuilder();
        for (byte b : digest) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }

    /**
     * VULNERABILITY 4: Insecure Logging (CWE-532)
     * Logs sensitive data to stdout (may contain PII/cardholder data)
     * PCI Checkstyle: PCI-01-NoSystemOut
     * PCI DSS: 3.4 (Render PAN unreadable)
     */
    public void logOrderDetails(Order order) {
        // Vulnerable: Using System.out instead of logger
        System.out.println("Processing order: " + order.getId() + 
                          " for customer: " + order.getCustomerName() +
                          " amount: $" + order.getAmount());
        System.out.println("Payment processed with API key: " + API_KEY);
    }

    /**
     * VULNERABILITY 5: Weak Random Number Generation (CWE-330)
     * Uses java.util.Random for security-sensitive tokens
     * PCI Checkstyle: PCI-05-NoWeakRandom
     * SonarQube: java:S2245
     * PCI DSS: 6.5.3 (Insecure cryptographic storage)
     */
    public String generateSessionToken() {
        Random random = new Random();
        long token = random.nextLong();
        return String.valueOf(Math.abs(token));
    }

    /**
     * VULNERABILITY 6: Exception Information Exposure (CWE-209)
     * Prints stack traces that may leak sensitive information
     * PCI Checkstyle: PCI-04-NoStackTrace
     * SonarQube: java:S1148
     * PCI DSS: 6.5.5 (Improper error handling)
     */
    public void processPayment(Order order) {
        try {
            // Simulate payment processing
            if (order.getAmount().doubleValue() > 10000) {
                throw new RuntimeException("Payment amount exceeds limit");
            }
            
            // Connect to payment gateway using hardcoded credentials
            String connectionString = "https://payment-gateway.example.com?apikey=" + API_KEY;
            System.out.println("Connecting to: " + connectionString);
            
        } catch (Exception e) {
            // Vulnerable: printStackTrace exposes internal details
            e.printStackTrace();
            System.err.println("Payment failed for order: " + order.getId());
        }
    }

    /**
     * Additional method demonstrating multiple vulnerabilities combined
     */
    public String authenticateUser(String username, String password, Connection conn) throws Exception {
        // SQL Injection vulnerability
        String sql = "SELECT * FROM users WHERE username = '" + username + 
                    "' AND password = '" + hashPassword(password) + "'";
        
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(sql);
        
        if (rs.next()) {
            // Weak random for session token
            String sessionToken = generateSessionToken();
            
            // Insecure logging
            System.out.println("User " + username + " authenticated with token: " + sessionToken);
            
            return sessionToken;
        }
        
        return null;
    }
}
EOF

echo "✅ Vulnerabilities injected successfully!"
echo ""
echo "📍 File created: $TARGET_FILE"
echo ""
echo "🔍 Injected vulnerabilities:"
echo "   1. SQL Injection (searchOrdersByCustomer, authenticateUser)"
echo "   2. Hardcoded credentials (DB_PASSWORD, API_KEY, BACKUP_DB_URL)"
echo "   3. Weak cryptography (MD5 hashing in hashPassword)"
echo "   4. Insecure logging (System.out.println with sensitive data)"
echo "   5. Weak random (java.util.Random in generateSessionToken)"
echo "   6. Stack trace exposure (printStackTrace in processPayment)"
echo ""
echo "🧪 Test detection:"
echo "   PCI Checkstyle: cd order-service && mvn checkstyle:check -Dcheckstyle.config.location=../pipeline/pci-checkstyle.xml"
echo "   Compile check:  cd order-service && mvn compile"
echo ""
echo "🧹 To remove: ./pipeline/restore_vulnerabilities.sh"

# Made with Bob
