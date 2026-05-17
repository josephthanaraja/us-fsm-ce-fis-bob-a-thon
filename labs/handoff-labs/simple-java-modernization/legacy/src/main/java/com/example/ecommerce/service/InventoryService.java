package com.example.ecommerce.service;

import com.example.ecommerce.model.Product;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Legacy InventoryService (Java 8)
 * 
 * Issues:
 * - Verbose null checks
 * - No Optional usage
 * - Traditional exception handling
 * - Mutable state management
 */
public class InventoryService {
    private Map<String, Integer> inventory;
    private Map<String, Product> products;

    public InventoryService() {
        this.inventory = new HashMap<>();
        this.products = new HashMap<>();
    }

    /**
     * Add product to inventory (legacy implementation)
     */
    public void addProduct(Product product, int quantity) {
        if (product == null) {
            throw new IllegalArgumentException("Product cannot be null");
        }
        if (quantity < 0) {
            throw new IllegalArgumentException("Quantity cannot be negative");
        }
        
        products.put(product.getId(), product);
        inventory.put(product.getId(), quantity);
    }

    /**
     * Update stock quantity (legacy implementation)
     */
    public boolean updateStock(String productId, int quantity) {
        if (productId == null || productId.isEmpty()) {
            return false;
        }
        
        if (!inventory.containsKey(productId)) {
            return false;
        }
        
        if (quantity < 0) {
            return false;
        }
        
        inventory.put(productId, quantity);
        return true;
    }

    /**
     * Check if product is in stock (legacy implementation)
     */
    public boolean isInStock(String productId) {
        if (productId == null) {
            return false;
        }
        
        Integer quantity = inventory.get(productId);
        return quantity != null && quantity > 0;
    }

    /**
     * Get stock quantity (legacy implementation - returns -1 for not found)
     * Should return Optional in modern Java
     */
    public int getStockQuantity(String productId) {
        if (productId == null) {
            return -1;
        }
        
        Integer quantity = inventory.get(productId);
        return quantity != null ? quantity : -1;
    }

    /**
     * Reserve stock for order (legacy implementation)
     */
    public boolean reserveStock(String productId, int quantity) {
        if (productId == null || quantity <= 0) {
            return false;
        }
        
        Integer currentStock = inventory.get(productId);
        if (currentStock == null || currentStock < quantity) {
            return false;
        }
        
        inventory.put(productId, currentStock - quantity);
        return true;
    }

    /**
     * Release reserved stock (legacy implementation)
     */
    public boolean releaseStock(String productId, int quantity) {
        if (productId == null || quantity <= 0) {
            return false;
        }
        
        Integer currentStock = inventory.get(productId);
        if (currentStock == null) {
            return false;
        }
        
        inventory.put(productId, currentStock + quantity);
        return true;
    }

    /**
     * Find low stock products (legacy implementation)
     */
    public List<Product> findLowStockProducts(int threshold) {
        return inventory.entrySet().stream()
            .filter(entry -> entry.getValue() < threshold)
            .map(entry -> products.get(entry.getKey()))
            .filter(product -> product != null)
            .collect(Collectors.toList());
    }

    /**
     * Find out of stock products (legacy implementation)
     */
    public List<Product> findOutOfStockProducts() {
        return inventory.entrySet().stream()
            .filter(entry -> entry.getValue() == 0)
            .map(entry -> products.get(entry.getKey()))
            .filter(product -> product != null)
            .collect(Collectors.toList());
    }

    /**
     * Get total inventory value (legacy implementation)
     */
    public java.math.BigDecimal getTotalInventoryValue() {
        return inventory.entrySet().stream()
            .map(entry -> {
                Product product = products.get(entry.getKey());
                if (product == null) {
                    return java.math.BigDecimal.ZERO;
                }
                return product.getPrice().multiply(new java.math.BigDecimal(entry.getValue()));
            })
            .reduce(java.math.BigDecimal.ZERO, java.math.BigDecimal::add);
    }

    /**
     * Check stock availability for multiple products (legacy implementation)
     */
    public boolean checkAvailability(Map<String, Integer> requiredItems) {
        if (requiredItems == null || requiredItems.isEmpty()) {
            return false;
        }
        
        for (Map.Entry<String, Integer> entry : requiredItems.entrySet()) {
            String productId = entry.getKey();
            Integer required = entry.getValue();
            
            if (productId == null || required == null || required <= 0) {
                return false;
            }
            
            Integer available = inventory.get(productId);
            if (available == null || available < required) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Get inventory summary (legacy implementation)
     */
    public InventorySummary getSummary() {
        int totalProducts = products.size();
        int inStockProducts = (int) inventory.values().stream()
            .filter(qty -> qty > 0)
            .count();
        int outOfStockProducts = (int) inventory.values().stream()
            .filter(qty -> qty == 0)
            .count();
        java.math.BigDecimal totalValue = getTotalInventoryValue();
        
        return new InventorySummary(totalProducts, inStockProducts, outOfStockProducts, totalValue);
    }

    /**
     * Get product by ID (legacy implementation - returns null)
     */
    public Product getProduct(String productId) {
        if (productId == null) {
            return null;
        }
        return products.get(productId);
    }

    public Map<String, Integer> getInventory() {
        return new HashMap<>(inventory);
    }
}

class InventorySummary {
    private final int totalProducts;
    private final int inStockProducts;
    private final int outOfStockProducts;
    private final java.math.BigDecimal totalValue;

    public InventorySummary(int totalProducts, int inStockProducts, 
                           int outOfStockProducts, java.math.BigDecimal totalValue) {
        this.totalProducts = totalProducts;
        this.inStockProducts = inStockProducts;
        this.outOfStockProducts = outOfStockProducts;
        this.totalValue = totalValue;
    }

    public int getTotalProducts() {
        return totalProducts;
    }

    public int getInStockProducts() {
        return inStockProducts;
    }

    public int getOutOfStockProducts() {
        return outOfStockProducts;
    }

    public java.math.BigDecimal getTotalValue() {
        return totalValue;
    }

    @Override
    public String toString() {
        return "InventorySummary{" +
                "totalProducts=" + totalProducts +
                ", inStockProducts=" + inStockProducts +
                ", outOfStockProducts=" + outOfStockProducts +
                ", totalValue=" + totalValue +
                '}';
    }
}

// Made with Bob