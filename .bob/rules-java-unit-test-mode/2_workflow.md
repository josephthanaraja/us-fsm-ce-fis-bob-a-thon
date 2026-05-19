# Java Unit Test Writing Workflow

Follow this workflow when writing unit tests for the order-service application.

## Step 1: Read Existing Tests First

**CRITICAL**: Before writing any new test, read the existing tests to understand the repository's conventions.

```
Read these files:
- order-service/src/test/java/com/example/orders/controller/OrderControllerTest.java
- order-service/src/test/java/com/example/orders/service/OrderServiceTest.java
```

Look for:
- Test class annotations (@WebMvcTest, @ExtendWith)
- Mock setup patterns (@Mock, @MockBean, @InjectMocks)
- Assertion style (AssertJ vs JUnit assertions)
- Test naming conventions
- Fixture setup in @BeforeEach
- How exceptions are tested

## Step 2: Identify What Needs Testing

Analyze the source code to identify:
- Untested methods
- Missing edge cases in existing tests
- Error handling paths not covered
- Business logic branches

## Step 3: Plan Test Cases

For each method, plan tests for:

### Happy Path
- Normal successful execution with valid inputs
- Expected return values or state changes

### Edge Cases
- Boundary values (empty lists, zero amounts, null optionals)
- Minimum and maximum values
- Empty strings, null values (where allowed)

### Error Cases
- Invalid inputs
- Constraint violations
- Exception scenarios
- State transition violations

### Example: Testing `updateOrderStatus(Long id, String newStatus)`

```
Test cases:
1. updateOrderStatus_validTransition_succeeds
   - PENDING -> CONFIRMED (valid)
   
2. updateOrderStatus_invalidTransition_throwsException
   - PENDING -> DELIVERED (invalid, skips CONFIRMED)
   
3. updateOrderStatus_cancelFromAnyStatus_succeeds
   - Any status -> CANCELLED (always allowed)
   
4. updateOrderStatus_fromTerminalStatus_throwsException
   - DELIVERED -> SHIPPED (terminal status cannot change)
   
5. updateOrderStatus_nonExistingOrder_throwsException
   - Order ID doesn't exist
```

## Step 4: Write Tests Following Conventions

### Service Layer Test Template

```java
@ExtendWith(MockitoExtension.class)
class YourServiceTest {
    
    @Mock
    private YourRepository repository;
    
    @InjectMocks
    private YourService service;
    
    private YourEntity testEntity;
    
    @BeforeEach
    void setUp() {
        testEntity = new YourEntity();
        // Initialize test data
    }
    
    @Test
    void methodName_scenario_expectedResult() {
        // Arrange
        when(repository.someMethod()).thenReturn(expectedValue);
        
        // Act
        var result = service.methodUnderTest();
        
        // Assert
        assertThat(result).isEqualTo(expectedValue);
    }
}
```

### Controller Layer Test Template

```java
@WebMvcTest(YourController.class)
class YourControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private YourService service;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    void methodName_scenario_expectedResult() throws Exception {
        // Arrange
        when(service.someMethod()).thenReturn(expectedValue);
        
        // Act & Assert
        mockMvc.perform(get("/api/endpoint"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.field").value("expectedValue"));
    }
}
```

## Step 5: Follow AAA Pattern

Structure each test with clear sections:

```java
@Test
void createOrder_validOrder_returnsCreatedOrder() {
    // Arrange - Set up test data and mock behavior
    Order newOrder = new Order();
    newOrder.setCustomerName("Jane");
    newOrder.setProduct("Gadget");
    newOrder.setAmount(new BigDecimal("49.99"));
    
    when(orderRepository.save(any(Order.class))).thenReturn(newOrder);
    
    // Act - Execute the method under test
    Order created = orderService.createOrder(newOrder);
    
    // Assert - Verify the results
    assertThat(created.getStatus()).isEqualTo("PENDING");
    assertThat(created.getCustomerName()).isEqualTo("Jane");
}
```

## Step 6: Test Exception Scenarios

Use AssertJ's `assertThatThrownBy()` for exception testing:

```java
@Test
void updateOrderStatus_invalidTransition_throwsException() {
    // Arrange
    when(orderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
    
    // Act & Assert
    assertThatThrownBy(() -> orderService.updateOrderStatus(1L, "DELIVERED"))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("Cannot transition from PENDING to DELIVERED");
}
```

## Step 7: Verify Mock Interactions (When Needed)

For void methods or when interaction verification is important:

```java
@Test
void deleteOrder_callsRepository() {
    // Act
    orderService.deleteOrder(1L);
    
    // Assert
    verify(orderRepository).deleteById(1L);
}
```

## Step 8: Run Tests and Verify

After writing tests:

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=OrderServiceTest

# Run with coverage
mvn test jacoco:report
```

## Common Patterns

### Testing Optional Returns

```java
// Present case
assertThat(result).isPresent();
assertThat(result.get().getField()).isEqualTo("value");

// Empty case
assertThat(result).isEmpty();
```

### Testing Collections

```java
assertThat(orders).hasSize(2);
assertThat(orders).isEmpty();
assertThat(orders.get(0).getCustomerName()).isEqualTo("John");
```

### Testing HTTP Responses

```java
mockMvc.perform(get("/api/orders/1"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.customerName").value("John"));

mockMvc.perform(get("/api/orders/999"))
        .andExpect(status().isNotFound());

mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(order)))
        .andExpect(status().isCreated());
```

## Checklist Before Committing

- [ ] Read existing tests to match conventions
- [ ] Test names follow `methodName_scenario_expectedResult` pattern
- [ ] Used AssertJ assertions (`assertThat()`)
- [ ] Used Mockito correctly (@Mock, @InjectMocks, when/verify)
- [ ] Followed AAA pattern (Arrange, Act, Assert)
- [ ] Tested happy path
- [ ] Tested edge cases
- [ ] Tested error scenarios
- [ ] All tests pass locally
- [ ] No unnecessary imports or commented code