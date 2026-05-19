# Java Unit Test Conventions

This document outlines the testing conventions used in this Spring Boot order-service application.

## Test Framework Stack

- **JUnit 5**: Test framework
- **Mockito**: Mocking framework
- **AssertJ**: Fluent assertion library
- **Spring Boot Test**: Spring testing utilities

## Naming Conventions

Test methods follow the pattern: `methodName_scenario_expectedResult`

Examples:
- `getAllOrders_returnsAllOrders()`
- `getOrderById_existingId_returnsOrder()`
- `getOrderById_nonExistingId_returnsEmpty()`
- `updateOrderStatus_invalidTransition_throwsException()`

## Test Class Structure

### Service Layer Tests

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    
    @Mock
    private OrderRepository orderRepository;
    
    @InjectMocks
    private OrderService orderService;
    
    private Order testOrder;
    
    @BeforeEach
    void setUp() {
        // Initialize test fixtures
        testOrder = new Order();
        testOrder.setId(1L);
        testOrder.setCustomerName("John Doe");
        // ... set other fields
    }
    
    @Test
    void methodName_scenario_expectedResult() {
        // Arrange
        when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        
        // Act
        Optional<Order> result = orderService.getOrderById(1L);
        
        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getCustomerName()).isEqualTo("John Doe");
    }
}
```

### Controller Layer Tests

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private OrderService orderService;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    void methodName_scenario_expectedResult() throws Exception {
        // Arrange
        Order order = new Order();
        order.setId(1L);
        order.setCustomerName("John");
        when(orderService.getOrderById(1L)).thenReturn(Optional.of(order));
        
        // Act & Assert
        mockMvc.perform(get("/api/orders/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerName").value("John"));
    }
}
```

## Assertion Patterns

### AssertJ Assertions (Preferred)

```java
// Collections
assertThat(orders).hasSize(1);
assertThat(orders).isEmpty();
assertThat(orders).isNotEmpty();

// Optionals
assertThat(result).isPresent();
assertThat(result).isEmpty();

// Objects
assertThat(order.getCustomerName()).isEqualTo("John Doe");
assertThat(order.getStatus()).isEqualTo("PENDING");

// Exceptions
assertThatThrownBy(() -> orderService.updateOrderStatus(1L, "INVALID"))
    .isInstanceOf(IllegalStateException.class)
    .hasMessageContaining("Cannot transition");
```

## Mocking Patterns

### Service Layer Mocking

```java
// Mock repository responses
when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
when(orderRepository.findAll()).thenReturn(Arrays.asList(testOrder));
when(orderRepository.save(any(Order.class))).thenReturn(testOrder);

// Verify interactions
verify(orderRepository).deleteById(1L);
verify(orderRepository).save(any(Order.class));
```

### Controller Layer Mocking

```java
// Mock service responses
when(orderService.getAllOrders()).thenReturn(Arrays.asList(order));
when(orderService.getOrderById(1L)).thenReturn(Optional.of(order));
when(orderService.createOrder(any(Order.class))).thenReturn(order);
```

## Test Fixture Setup

Use `@BeforeEach` to initialize common test data:

```java
private Order testOrder;

@BeforeEach
void setUp() {
    testOrder = new Order();
    testOrder.setId(1L);
    testOrder.setCustomerName("John Doe");
    testOrder.setProduct("Widget");
    testOrder.setAmount(new BigDecimal("29.99"));
    testOrder.setStatus("PENDING");
}
```

## Test Coverage Guidelines

For each method, test:
1. **Happy path**: Normal successful execution
2. **Edge cases**: Boundary conditions, empty inputs, null values
3. **Error cases**: Invalid inputs, exceptions, constraint violations
4. **State transitions**: For stateful operations (e.g., order status changes)

Example coverage for `getOrderById`:
- `getOrderById_existingId_returnsOrder()` - happy path
- `getOrderById_nonExistingId_returnsEmpty()` - edge case