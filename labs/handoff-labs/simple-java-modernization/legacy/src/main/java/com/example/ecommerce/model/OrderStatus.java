package com.example.ecommerce.model;

/**
 * Legacy OrderStatus enum (Java 8)
 * 
 * This can be modernized to a sealed interface with records in Java 17
 * to provide more type safety and pattern matching capabilities.
 */
public enum OrderStatus {
    PENDING("Order is pending"),
    CONFIRMED("Order has been confirmed"),
    PROCESSING("Order is being processed"),
    SHIPPED("Order has been shipped"),
    DELIVERED("Order has been delivered"),
    CANCELLED("Order has been cancelled"),
    REFUNDED("Order has been refunded");

    private final String description;

    OrderStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    public boolean isActive() {
        return this == PENDING || this == CONFIRMED || this == PROCESSING || this == SHIPPED;
    }

    public boolean isCompleted() {
        return this == DELIVERED || this == CANCELLED || this == REFUNDED;
    }

    public boolean canTransitionTo(OrderStatus newStatus) {
        switch (this) {
            case PENDING:
                return newStatus == CONFIRMED || newStatus == CANCELLED;
            case CONFIRMED:
                return newStatus == PROCESSING || newStatus == CANCELLED;
            case PROCESSING:
                return newStatus == SHIPPED || newStatus == CANCELLED;
            case SHIPPED:
                return newStatus == DELIVERED;
            case DELIVERED:
                return newStatus == REFUNDED;
            case CANCELLED:
            case REFUNDED:
                return false;
            default:
                return false;
        }
    }
}

// Made with Bob