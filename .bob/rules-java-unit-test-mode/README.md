# Java Unit Test Mode - Instruction Files

This directory contains instruction files for the `java-unit-test-mode` custom mode.

## Purpose

The `java-unit-test-mode` helps Bob write high-quality JUnit 5 tests for the Spring Boot order-service application, following the repository's established conventions.

## Instruction Files

### 1. [Test Conventions](1_test_conventions.md)
Documents the testing conventions used in this repository:
- Test framework stack (JUnit 5, Mockito, AssertJ)
- Naming conventions (`methodName_scenario_expectedResult`)
- Test class structure for services and controllers
- Assertion patterns (AssertJ fluent assertions)
- Mocking patterns
- Test fixture setup with `@BeforeEach`
- Test coverage guidelines

### 2. [Workflow](2_workflow.md)
Step-by-step workflow for writing unit tests:
1. Read existing tests first (CRITICAL)
2. Identify what needs testing
3. Plan test cases (happy path, edge cases, errors)
4. Write tests following conventions
5. Follow AAA pattern (Arrange, Act, Assert)
6. Test exception scenarios
7. Verify mock interactions
8. Run tests and verify

Includes templates, common patterns, and a pre-commit checklist.

### 3. [Spring Boot Testing](3_spring_boot_testing.md)
Specific guidance for Spring Boot testing:
- Controller testing with `@WebMvcTest`
- Service testing with `@ExtendWith(MockitoExtension.class)`
- MockMvc testing patterns (GET, POST, PUT, DELETE)
- Repository mocking patterns
- Testing business logic (state transitions, defaults, null safety)
- Test data management
- Common pitfalls to avoid

## Quick Reference

### Test Naming Pattern
```
methodName_scenario_expectedResult
```

### Service Test Template
```java
@ExtendWith(MockitoExtension.class)
class YourServiceTest {
    @Mock
    private YourRepository repository;
    
    @InjectMocks
    private YourService service;
    
    @BeforeEach
    void setUp() {
        // Initialize test fixtures
    }
    
    @Test
    void methodName_scenario_expectedResult() {
        // Arrange
        when(repository.method()).thenReturn(value);
        
        // Act
        var result = service.method();
        
        // Assert
        assertThat(result).isEqualTo(expected);
    }
}
```

### Controller Test Template
```java
@WebMvcTest(YourController.class)
class YourControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private YourService service;
    
    @Test
    void methodName_scenario_expectedResult() throws Exception {
        // Arrange
        when(service.method()).thenReturn(value);
        
        // Act & Assert
        mockMvc.perform(get("/api/endpoint"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.field").value("value"));
    }
}
```

## Key Principles

1. **Read existing tests first** - Always understand the repository's conventions before writing new tests
2. **Use AssertJ** - Prefer `assertThat()` over JUnit assertions
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Test comprehensively** - Happy path, edge cases, and error scenarios
5. **Name tests clearly** - Test names should document behavior
6. **Mock appropriately** - Use `@Mock` for services, `@MockBean` for controllers

## Mode Configuration

The mode is configured in `.bob/custom_modes.yaml` with:
- **Slug**: `java-unit-test-mode`
- **Name**: 🧪 Java Unit Test Specialist
- **Tool Groups**: read, edit
- **Source**: project

## Usage

Activate this mode when:
- Writing new JUnit tests for Java classes
- Analyzing Maven Surefire test failures
- Improving test coverage
- Refactoring or fixing broken tests
- Adding missing test cases for edge conditions

The mode will automatically read existing tests to understand conventions before writing new tests.