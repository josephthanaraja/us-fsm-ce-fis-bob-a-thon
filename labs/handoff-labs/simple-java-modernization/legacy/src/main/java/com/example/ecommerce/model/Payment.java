package com.example.ecommerce.model;

import java.math.BigDecimal;

/**
 * Legacy Payment hierarchy (Java 8)
 * 
 * Issues:
 * - Open hierarchy (any class can extend)
 * - Verbose instanceof checks required
 * - No exhaustiveness checking
 */
public abstract class Payment {
    protected BigDecimal amount;
    protected PaymentStatus status;

    public Payment(BigDecimal amount) {
        this.amount = amount;
        this.status = PaymentStatus.PENDING;
    }

    public abstract String getPaymentMethod();
    
    public BigDecimal getAmount() {
        return amount;
    }

    public PaymentStatus getStatus() {
        return status;
    }

    public void setStatus(PaymentStatus status) {
        this.status = status;
    }
}

public class CreditCardPayment extends Payment {
    private String cardNumber;
    private String cvv;
    private String expiryDate;

    public CreditCardPayment(BigDecimal amount, String cardNumber, String cvv, String expiryDate) {
        super(amount);
        this.cardNumber = cardNumber;
        this.cvv = cvv;
        this.expiryDate = expiryDate;
    }

    @Override
    public String getPaymentMethod() {
        return "Credit Card";
    }

    public String getCardNumber() {
        return cardNumber;
    }

    public String getCvv() {
        return cvv;
    }

    public String getExpiryDate() {
        return expiryDate;
    }
}

public class PayPalPayment extends Payment {
    private String email;

    public PayPalPayment(BigDecimal amount, String email) {
        super(amount);
        this.email = email;
    }

    @Override
    public String getPaymentMethod() {
        return "PayPal";
    }

    public String getEmail() {
        return email;
    }
}

public class BankTransferPayment extends Payment {
    private String accountNumber;
    private String routingNumber;

    public BankTransferPayment(BigDecimal amount, String accountNumber, String routingNumber) {
        super(amount);
        this.accountNumber = accountNumber;
        this.routingNumber = routingNumber;
    }

    @Override
    public String getPaymentMethod() {
        return "Bank Transfer";
    }

    public String getAccountNumber() {
        return accountNumber;
    }

    public String getRoutingNumber() {
        return routingNumber;
    }
}

enum PaymentStatus {
    PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED
}

// Made with Bob
