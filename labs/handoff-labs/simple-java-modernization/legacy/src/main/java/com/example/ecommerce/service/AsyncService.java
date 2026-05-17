package com.example.ecommerce.service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Legacy AsyncService (Java 8)
 * 
 * Issues:
 * - Uses fixed thread pool (can be replaced with virtual threads in Java 21)
 * - Traditional CompletableFuture patterns
 * - Manual executor management
 * - Verbose error handling
 */
public class AsyncService {
    private final ExecutorService executor;
    private final int threadPoolSize;

    public AsyncService() {
        this(100);
    }

    public AsyncService(int threadPoolSize) {
        this.threadPoolSize = threadPoolSize;
        this.executor = Executors.newFixedThreadPool(threadPoolSize);
    }

    /**
     * Process items asynchronously (legacy implementation)
     * Can be modernized with virtual threads in Java 21
     */
    public <T> CompletableFuture<List<T>> processItemsAsync(List<T> items, 
                                                             ItemProcessor<T> processor) {
        List<CompletableFuture<T>> futures = new ArrayList<>();
        
        for (T item : items) {
            CompletableFuture<T> future = CompletableFuture.supplyAsync(
                () -> processor.process(item),
                executor
            );
            futures.add(future);
        }
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                List<T> results = new ArrayList<>();
                for (CompletableFuture<T> future : futures) {
                    try {
                        results.add(future.get());
                    } catch (Exception e) {
                        // Legacy error handling
                        throw new RuntimeException("Error processing item", e);
                    }
                }
                return results;
            });
    }

    /**
     * Execute task asynchronously with timeout (legacy implementation)
     */
    public <T> CompletableFuture<T> executeWithTimeout(Task<T> task, long timeoutSeconds) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.execute();
            } catch (Exception e) {
                throw new RuntimeException("Task execution failed", e);
            }
        }, executor)
        .orTimeout(timeoutSeconds, TimeUnit.SECONDS)
        .exceptionally(ex -> {
            System.err.println("Task failed or timed out: " + ex.getMessage());
            return null;
        });
    }

    /**
     * Chain multiple async operations (legacy implementation)
     */
    public <T, R> CompletableFuture<R> chainOperations(T input,
                                                        Operation<T, R> operation1,
                                                        Operation<R, R> operation2) {
        return CompletableFuture.supplyAsync(() -> input, executor)
            .thenApplyAsync(operation1::apply, executor)
            .thenApplyAsync(operation2::apply, executor)
            .exceptionally(ex -> {
                System.err.println("Operation chain failed: " + ex.getMessage());
                return null;
            });
    }

    /**
     * Execute multiple tasks in parallel (legacy implementation)
     */
    public <T> CompletableFuture<List<T>> executeParallel(List<Task<T>> tasks) {
        List<CompletableFuture<T>> futures = new ArrayList<>();
        
        for (Task<T> task : tasks) {
            CompletableFuture<T> future = CompletableFuture.supplyAsync(() -> {
                try {
                    return task.execute();
                } catch (Exception e) {
                    throw new RuntimeException("Task execution failed", e);
                }
            }, executor);
            futures.add(future);
        }
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                List<T> results = new ArrayList<>();
                for (CompletableFuture<T> future : futures) {
                    try {
                        results.add(future.join());
                    } catch (Exception e) {
                        System.err.println("Error getting result: " + e.getMessage());
                    }
                }
                return results;
            });
    }

    /**
     * Execute with retry logic (legacy implementation)
     */
    public <T> CompletableFuture<T> executeWithRetry(Task<T> task, int maxRetries) {
        return executeWithRetryInternal(task, maxRetries, 0);
    }

    private <T> CompletableFuture<T> executeWithRetryInternal(Task<T> task, 
                                                               int maxRetries, 
                                                               int attempt) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.execute();
            } catch (Exception e) {
                throw new RuntimeException("Task execution failed", e);
            }
        }, executor)
        .exceptionally(ex -> {
            if (attempt < maxRetries) {
                System.out.println("Retry attempt " + (attempt + 1) + " of " + maxRetries);
                try {
                    return executeWithRetryInternal(task, maxRetries, attempt + 1).join();
                } catch (Exception e) {
                    throw new RuntimeException("Retry failed", e);
                }
            } else {
                throw new RuntimeException("Max retries exceeded", ex);
            }
        });
    }

    /**
     * Combine results from multiple async operations (legacy implementation)
     */
    public <T, U, R> CompletableFuture<R> combineResults(
            CompletableFuture<T> future1,
            CompletableFuture<U> future2,
            ResultCombiner<T, U, R> combiner) {
        
        return future1.thenCombineAsync(future2, combiner::combine, executor)
            .exceptionally(ex -> {
                System.err.println("Error combining results: " + ex.getMessage());
                return null;
            });
    }

    /**
     * Shutdown executor (legacy implementation)
     */
    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    public int getThreadPoolSize() {
        return threadPoolSize;
    }
}

@FunctionalInterface
interface ItemProcessor<T> {
    T process(T item);
}

@FunctionalInterface
interface Task<T> {
    T execute() throws Exception;
}

@FunctionalInterface
interface Operation<T, R> {
    R apply(T input);
}

@FunctionalInterface
interface ResultCombiner<T, U, R> {
    R combine(T first, U second);
}

// Made with Bob