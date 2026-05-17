package com.example.ecommerce.model;

import java.math.BigDecimal;
import java.util.Objects;

/**
 * Legacy Product class (Java 8)
 * 
 * This is a traditional POJO with lots of boilerplate code.
 * Issues:
 * - Verbose getter/setter methods
 * - Manual equals/hashCode implementation
 * - Mutable by default
 * - No built-in validation
 */
public class Product {
    private final String id;
    private final String name;
    private final BigDecimal price;
    private final String category;
    private final String description;
    private final int stockQuantity;

    public Product(String id, String name, BigDecimal price, String category, 
                   String description, int stockQuantity) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.category = category;
        this.description = description;
        this.stockQuantity = stockQuantity;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public String getCategory() {
        return category;
    }

    public String getDescription() {
        return description;
    }

    public int getStockQuantity() {
        return stockQuantity;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return stockQuantity == product.stockQuantity &&
                Objects.equals(id, product.id) &&
                Objects.equals(name, product.name) &&
                Objects.equals(price, product.price) &&
                Objects.equals(category, product.category) &&
                Objects.equals(description, product.description);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, price, category, description, stockQuantity);
    }

    @Override
    public String toString() {
        return "Product{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", price=" + price +
                ", category='" + category + '\'' +
                ", description='" + description + '\'' +
                ", stockQuantity=" + stockQuantity +
                '}';
    }
}

// Made with Bob
