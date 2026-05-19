# Spring Boot Testing Guide

Specific guidance for testing Spring Boot components in the order-service application.

## Controller Testing with @WebMvcTest

`@WebMvcTest` is a Spring Boot test slice annotation that loads only the web layer.

### Key Characteristics

- Loads only the specified controller and web layer components
- Does NOT load services, repositories, or other beans
- Automatically configures MockMvc
- Requires @MockBean for service dependencies

### Example Structure

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    
    @Autowired
    private MockMvc mockMvc;  // Automatically configured
    
    @MockBean
    private OrderService orderService;  // Mock the service dependency
    
    @Autowired
    private ObjectMapper objectMapper;  // For JSON serialization
    
    @Test
    void endpoint_scenario_expectedResult() throws Exception {
        // Test implementation
    }
}
```

## Service Testing with @ExtendWith(MockitoExtension.class)

Service layer tests use pure Mockito without Spring context.

### Key Characteristics

- No Spring context loaded (faster tests)
- Use @Mock for dependencies
- Use @InjectMocks for the service under test
- Manual test fixture setup in @BeforeEach

### Example Structure

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    
    @Mock
    private OrderRepository orderRepository;  // Mock the repository
    
    @InjectMocks
    private OrderService orderService;  // Service under test
    
    private Order testOrder;
    
    @BeforeEach
    void setUp() {
        // Initialize test fixtures
        testOrder = new Order();
        testOrder.setId(1L);
        testOrder.setCustomerName("John Doe");
        testOrder.setProduct("Widget");
        testOrder.setAmount(new BigDecimal("29.99"));
        testOrder.setStatus("PENDING");
    }
    
    @Test
    void method_scenario_expectedResult() {
        // Test implementation
    }
}
```

## MockMvc Testing Patterns

### GET Requests

```java
// Successful GET
mockMvc.perform(get("/api/orders/1"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.id").value(1))
        .andExpect(jsonPath("$.customerName").value("John"));

// Not Found
mockMvc.perform(get("/api/orders/999"))
        .andExpect(status().isNotFound());

// List Response
mockMvc.perform(get("/api/orders"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$[0].customerName").value("John"))
        .andExpect(jsonPath("$").isArray());
```

### POST Requests

```java
Order order = new Order();
order.setCustomerName("Bob");
order.setProduct("Thing");
order.setAmount(new BigDecimal("19.99"));

mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(order)))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.customerName").value("Bob"));
```

### PUT Requests

```java
mockMvc.perform(put("/api/orders/1/status")
                .contentType(MediaType.APPLICATION_JSON)
                .content("\"CONFIRMED\""))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.status").value("CONFIRMED"));
```

### DELETE Requests

```java
mockMvc.perform(delete("/api/orders/1"))
        .andExpect(status().isNoContent());
```

### Validation Testing

```java
@Test
void createOrder_missingFields_returns400() throws Exception {
    Order order = new Order();
    // Missing required fields
    
    mockMvc.perform(post("/api/orders")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(order)))
            .andExpect(status().isBadRequest());
}
```

## Repository Mocking Patterns

### Common Repository Operations

```java
// findById
when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
when(orderRepository.findById(999L)).thenReturn(Optional.empty());

// findAll
when(orderRepository.findAll()).thenReturn(Arrays.asList(testOrder));
when(orderRepository.findAll()).thenReturn(Collections.emptyList());

// save
when(orderRepository.save(any(Order.class))).thenReturn(testOrder);
when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));

// delete (void method - no when() needed)
// Just verify it was called
verify(orderRepository).deleteById(1L);

// existsById
when(orderRepository.existsById(1L)).thenReturn(true);
when(orderRepository.existsById(999L)).thenReturn(false);
```

### Argument Matchers

```java
// Any instance of a class
when(orderRepository.save(any(Order.class))).thenReturn(testOrder);

// Specific value
when(orderRepository.findById(eq(1L))).thenReturn(Optional.of(testOrder));

// Argument captor for verification
ArgumentCaptor<Order> orderCaptor = ArgumentCaptor.forClass(Order.class);
verify(orderRepository).save(orderCaptor.capture());
assertThat(orderCaptor.getValue().getStatus()).isEqualTo("PENDING");
```

## Testing Business Logic

### State Transitions

```java
@Test
void updateOrderStatus_validTransition_succeeds() {
    // Arrange
    testOrder.setStatus("PENDING");
    when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
    when(orderRepository.save(any(Order.class))).thenReturn(testOrder);
    
    // Act
    Order updated = orderService.updateOrderStatus(1L, "CONFIRMED");
    
    // Assert
    assertThat(updated.getStatus()).isEqualTo("CONFIRMED");
}

@Test
void updateOrderStatus_invalidTransition_throwsException() {
    // Arrange
    testOrder.setStatus("PENDING");
    when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
    
    // Act & Assert
    assertThatThrownBy(() -> orderService.updateOrderStatus(1L, "DELIVERED"))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("Cannot transition from PENDING to DELIVERED");
}
```

### Default Values

```java
@Test
void createOrder_setsDefaultStatus() {
    // Arrange
    Order newOrder = new Order();
    newOrder.setCustomerName("Jane");
    newOrder.setProduct("Gadget");
    newOrder.setAmount(new BigDecimal("49.99"));
    // Note: status not set
    
    when(orderRepository.save(any(Order.class))).thenReturn(newOrder);
    
    // Act
    Order created = orderService.createOrder(newOrder);
    
    // Assert
    assertThat(created.getStatus()).isEqualTo("PENDING");
}
```

### Null Safety

```java
@Test
void getOrderById_nullId_throwsException() {
    assertThatThrownBy(() -> orderService.getOrderById(null))
            .isInstanceOf(IllegalArgumentException.class);
}
```

## Test Data Management

### Using @BeforeEach for Common Setup

```java
private Order testOrder;
private Order anotherOrder;

@BeforeEach
void setUp() {
    testOrder = new Order();
    testOrder.setId(1L);
    testOrder.setCustomerName("John Doe");
    testOrder.setProduct("Widget");
    testOrder.setAmount(new BigDecimal("29.99"));
    testOrder.setStatus("PENDING");
    
    anotherOrder = new Order();
    anotherOrder.setId(2L);
    anotherOrder.setCustomerName("Jane Smith");
    anotherOrder.setProduct("Gadget");
    anotherOrder.setAmount(new BigDecimal("49.99"));
    anotherOrder.setStatus("CONFIRMED");
}
```

### Test-Specific Data

```java
@Test
void specificScenario_needsSpecialData() {
    // Create test-specific data inline
    Order specialOrder = new Order();
    specialOrder.setStatus("CANCELLED");
    specialOrder.setAmount(BigDecimal.ZERO);
    
    // Test with special data
}
```

## Common Pitfalls to Avoid

### ❌ Don't: Mix Spring and Mockito annotations incorrectly

```java
// WRONG - mixing @Mock with @WebMvcTest
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Mock  // ❌ Should be @MockBean
    private OrderService orderService;
}
```

### ✅ Do: Use correct annotations for each test type

```java
// Controller tests use @MockBean
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @MockBean  // ✅ Correct
    private OrderService orderService;
}

// Service tests use @Mock
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock  // ✅ Correct
    private OrderRepository orderRepository;
}
```

### ❌ Don't: Forget to mock repository responses

```java
@Test
void getOrderById_returnsOrder() {
    // ❌ No when() setup - will return null
    Optional<Order> result = orderService.getOrderById(1L);
    assertThat(result).isPresent();  // Will fail!
}
```

### ✅ Do: Always set up mock behavior

```java
@Test
void getOrderById_returnsOrder() {
    // ✅ Mock the repository response
    when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
    
    Optional<Order> result = orderService.getOrderById(1L);
    assertThat(result).isPresent();
}
```

### ❌ Don't: Use JUnit assertions when AssertJ is available

```java
// ❌ Old JUnit style
assertEquals("John", order.getCustomerName());
assertTrue(result.isPresent());
```

### ✅ Do: Use AssertJ fluent assertions

```java
// ✅ AssertJ style (matches repo conventions)
assertThat(order.getCustomerName()).isEqualTo("John");
assertThat(result).isPresent();