package com.example.ecommerce.service;

import com.example.ecommerce.model.Payment;
import com.example.ecommerce.model.CreditCardPayment;
import com.example.ecommerce.model.PayPalPayment;
import com.example.ecommerce.model.BankTransferPayment;
import java.math.BigDecimal;

/**
 * Legacy Java 8 Payment Service
 * This class demonstrates traditional instanceof checks and if-else chains
 * that can be modernized with Java 17 pattern matching and switch expressions.
 */
public class PaymentService {
    
    /**
     * Calculate processing fee based on payment type
     * Legacy implementation using instanceof and if-else
     */
    public BigDecimal calculateFee(Payment payment) {
        if (payment instanceof CreditCardPayment) {
            CreditCardPayment cc = (CreditCardPayment) payment;
            return cc.getAmount().multiply(new BigDecimal("0.029"));
        } else if (payment instanceof PayPalPayment) {
            PayPalPayment pp = (PayPalPayment) payment;
            return pp.getAmount().multiply(new BigDecimal("0.034"));
        } else if (payment instanceof BankTransferPayment) {
            return BigDecimal.ZERO;
        } else {
            throw new IllegalArgumentException("Unknown payment type");
        }
    }
    
    /**
     * Process payment with legacy error handling
     */
    public String processPayment(Payment payment) {
        if (payment == null) {
            throw new IllegalArgumentException("Payment cannot be null");
        }
        
        BigDecimal fee = calculateFee(payment);
        BigDecimal total = payment.getAmount().add(fee);
        
        String paymentType = "";
        if (payment instanceof CreditCardPayment) {
            paymentType = "Credit Card";
        } else if (payment instanceof PayPalPayment) {
            paymentType = "PayPal";
        } else if (payment instanceof BankTransferPayment) {
            paymentType = "Bank Transfer";
        }
        
        return String.format("Processing %s payment of %s (fee: %s, total: %s)", 
            paymentType, payment.getAmount(), fee, total);
    }
    
    /**
     * Validate payment with verbose null checks
     */
    public boolean validatePayment(Payment payment) {
        if (payment == null) {
            return false;
        }
        
        if (payment.getAmount() == null) {
            return false;
        }
        
        if (payment.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            return false;
        }
        
        if (payment instanceof CreditCardPayment) {
            CreditCardPayment cc = (CreditCardPayment) payment;
            if (cc.getCardNumber() == null || cc.getCardNumber().isEmpty()) {
                return false;
            }
            if (cc.getCvv() == null || cc.getCvv().isEmpty()) {
                return false;
            }
        } else if (payment instanceof PayPalPayment) {
            PayPalPayment pp = (PayPalPayment) payment;
            if (pp.getEmail() == null || pp.getEmail().isEmpty()) {
                return false;
            }
        }
        
        return true;
    }
}