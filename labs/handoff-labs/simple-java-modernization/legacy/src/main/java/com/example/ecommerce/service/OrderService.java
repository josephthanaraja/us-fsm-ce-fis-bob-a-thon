package com.example.ecommerce.service;

import com.example.ecommerce.model.Order;
import com.example.ecommerce.model.OrderStatus;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Legacy OrderService (Java 8)
 * 
 * Issues:
 * - Uses legacy Date API
 * - Verbose stream operations with Collectors.toList()
 * - Traditional null checks
 * - No Optional usage
 */
public class OrderService {
    private List<Order> orders;

    public OrderService() {
        this.orders = new ArrayList<>();
    }

    /**
     * Find high value orders (legacy implementation)
     * Can be modernized with .toList() in Java 17
     */
    public List<Order> findHighValueOrders(List<Order> orders) {
        return orders.stream()
            .filter(order -> order.getTotal().compareTo(new BigDecimal("1000")) > 0)
            .collect(Collectors.toList());
    }

    /**
     * Find orders by status (legacy implementation)
     */
    public List<Order> findOrdersByStatus(OrderStatus status) {
        return orders.stream()
            .filter(order -> order.getStatus() == status)
            .collect(Collectors.toList());
    }

    /**
     * Find overdue orders (legacy implementation with Date API)
     */
    public List<Order> findOverdueOrders() {
        return orders.stream()
            .filter(Order::isOverdue)
            .collect(Collectors.toList());
    }

    /**
     * Calculate total revenue (legacy implementation)
     */
    public BigDecimal calculateTotalRevenue() {
        return orders.stream()
            .filter(order -> order.getStatus() == OrderStatus.DELIVERED)
            .map(Order::getTotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    /**
     * Find orders by customer (legacy implementation with null check)
     */
    public List<Order> findOrdersByCustomer(String customerId) {
        if (customerId == null || customerId.isEmpty()) {
            return new ArrayList<>();
        }
        
        return orders.stream()
            .filter(order -> customerId.equals(order.getCustomerId()))
            .collect(Collectors.toList());
    }

    /**
     * Find order by ID (legacy implementation - returns null)
     * Should return Optional in modern Java
     */
    public Order findById(String orderId) {
        if (orderId == null) {
            return null;
        }
        
        for (Order order : orders) {
            if (orderId.equals(order.getId())) {
                return order;
            }
        }
        return null;
    }

    /**
     * Create new order (legacy implementation)
     */
    public Order createOrder(String customerId, Date deliveryDate) {
        String orderId = generateOrderId();
        Order order = new Order(orderId, customerId, new Date(), deliveryDate);
        orders.add(order);
        return order;
    }

    /**
     * Update order status (legacy implementation with verbose checks)
     */
    public boolean updateOrderStatus(String orderId, OrderStatus newStatus) {
        Order order = findById(orderId);
        if (order == null) {
            return false;
        }
        
        if (!order.getStatus().canTransitionTo(newStatus)) {
            return false;
        }
        
        order.setStatus(newStatus);
        return true;
    }

    /**
     * Cancel order (legacy implementation)
     */
    public boolean cancelOrder(String orderId) {
        Order order = findById(orderId);
        if (order == null) {
            return false;
        }
        
        if (order.getStatus() == OrderStatus.DELIVERED || 
            order.getStatus() == OrderStatus.CANCELLED) {
            return false;
        }
        
        order.setStatus(OrderStatus.CANCELLED);
        return true;
    }

    /**
     * Get orders in date range (legacy Date API)
     */
    public List<Order> getOrdersInDateRange(Date startDate, Date endDate) {
        if (startDate == null || endDate == null) {
            return new ArrayList<>();
        }
        
        return orders.stream()
            .filter(order -> {
                Date orderDate = order.getOrderDate();
                return !orderDate.before(startDate) && !orderDate.after(endDate);
            })
            .collect(Collectors.toList());
    }

    /**
     * Get order statistics (legacy implementation)
     */
    public OrderStatistics getStatistics() {
        int totalOrders = orders.size();
        int activeOrders = (int) orders.stream()
            .filter(order -> order.getStatus().isActive())
            .count();
        int completedOrders = (int) orders.stream()
            .filter(order -> order.getStatus().isCompleted())
            .count();
        BigDecimal totalRevenue = calculateTotalRevenue();
        
        return new OrderStatistics(totalOrders, activeOrders, completedOrders, totalRevenue);
    }

    private String generateOrderId() {
        return "ORD-" + System.currentTimeMillis();
    }

    public List<Order> getAllOrders() {
        return new ArrayList<>(orders);
    }
}

class OrderStatistics {
    private final int totalOrders;
    private final int activeOrders;
    private final int completedOrders;
    private final BigDecimal totalRevenue;

    public OrderStatistics(int totalOrders, int activeOrders, int completedOrders, BigDecimal totalRevenue) {
        this.totalOrders = totalOrders;
        this.activeOrders = activeOrders;
        this.completedOrders = completedOrders;
        this.totalRevenue = totalRevenue;
    }

    public int getTotalOrders() {
        return totalOrders;
    }

    public int getActiveOrders() {
        return activeOrders;
    }

    public int getCompletedOrders() {
        return completedOrders;
    }

    public BigDecimal getTotalRevenue() {
        return totalRevenue;
    }

    @Override
    public String toString() {
        return "OrderStatistics{" +
                "totalOrders=" + totalOrders +
                ", activeOrders=" + activeOrders +
                ", completedOrders=" + completedOrders +
                ", totalRevenue=" + totalRevenue +
                '}';
    }
}

// Made with Bob