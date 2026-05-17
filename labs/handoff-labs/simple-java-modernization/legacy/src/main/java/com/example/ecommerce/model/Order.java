package com.example.ecommerce.model;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Objects;

/**
 * Legacy Order class (Java 8)
 * 
 * Issues:
 * - Uses legacy Date API
 * - Mutable collections
 * - Verbose null checks
 * - Traditional POJO boilerplate
 */
public class Order {
    private final String id;
    private final String customerId;
    private final List<OrderItem> items;
    private final Date orderDate;
    private final Date deliveryDate;
    private OrderStatus status;
    private BigDecimal total;

    public Order(String id, String customerId, Date orderDate, Date deliveryDate) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>();
        this.orderDate = orderDate;
        this.deliveryDate = deliveryDate;
        this.status = OrderStatus.PENDING;
        this.total = BigDecimal.ZERO;
    }

    public void addItem(OrderItem item) {
        if (item != null) {
            items.add(item);
            recalculateTotal();
        }
    }

    public void removeItem(OrderItem item) {
        if (item != null) {
            items.remove(item);
            recalculateTotal();
        }
    }

    private void recalculateTotal() {
        total = BigDecimal.ZERO;
        for (OrderItem item : items) {
            total = total.add(item.getSubtotal());
        }
    }

    public boolean isOverdue() {
        if (deliveryDate == null) {
            return false;
        }
        Date now = new Date();
        return deliveryDate.before(now) && status != OrderStatus.DELIVERED;
    }

    public String getId() {
        return id;
    }

    public String getCustomerId() {
        return customerId;
    }

    public List<OrderItem> getItems() {
        return new ArrayList<>(items);
    }

    public Date getOrderDate() {
        return orderDate;
    }

    public Date getDeliveryDate() {
        return deliveryDate;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public void setStatus(OrderStatus status) {
        this.status = status;
    }

    public BigDecimal getTotal() {
        return total;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Order order = (Order) o;
        return Objects.equals(id, order.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "Order{" +
                "id='" + id + '\'' +
                ", customerId='" + customerId + '\'' +
                ", items=" + items.size() +
                ", orderDate=" + orderDate +
                ", deliveryDate=" + deliveryDate +
                ", status=" + status +
                ", total=" + total +
                '}';
    }
}

class OrderItem {
    private final String productId;
    private final String productName;
    private final int quantity;
    private final BigDecimal unitPrice;

    public OrderItem(String productId, String productName, int quantity, BigDecimal unitPrice) {
        this.productId = productId;
        this.productName = productName;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public BigDecimal getSubtotal() {
        return unitPrice.multiply(new BigDecimal(quantity));
    }

    public String getProductId() {
        return productId;
    }

    public String getProductName() {
        return productName;
    }

    public int getQuantity() {
        return quantity;
    }

    public BigDecimal getUnitPrice() {
        return unitPrice;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        OrderItem orderItem = (OrderItem) o;
        return quantity == orderItem.quantity &&
                Objects.equals(productId, orderItem.productId) &&
                Objects.equals(productName, orderItem.productName) &&
                Objects.equals(unitPrice, orderItem.unitPrice);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productId, productName, quantity, unitPrice);
    }
}

// Made with Bob