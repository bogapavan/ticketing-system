# Architectural & Design Decisions

This document explains the key technical decisions made while designing the ticket booking system, with a focus on correctness under concurrency, simplicity, and interview-level clarity.

---

## 1. Why This Database Structure?

### Tables Used
- **Event**
  - `id`
  - `total_tickets`
  - `available_tickets`
- **Booking**
  - `event_id`
  - `user_id`
  - `tickets_booked`
  - Unique constraint on `(event_id, user_id)`

### Reasoning

### a) One Booking Row per User per Event
A booking represents an **aggregate** of tickets booked by a user for a given event.

This design:
- Enforces the “max 2 tickets per user” constraint naturally
- Avoids row explosion under high traffic
- Simplifies concurrency handling (fewer rows to lock)

### b) `available_tickets` as a Column
Instead of calculating availability dynamically from bookings:
- We store `available_tickets` directly on the `Event` row
- This allows O(1) availability checks
- Avoids expensive aggregation queries during peak traffic

### c) Database-Level Constraints
- Unique constraint ensures business invariants are enforced even if application logic fails
- Shifts correctness guarantees closer to the data layer

### Why PostgreSQL?
- Strong transactional guarantees (ACID)
- Native support for row-level locking (`SELECT FOR UPDATE`)
- Mature behavior under concurrent write workloads

---

## 2. Race Condition Handling: Alternatives Considered

### Chosen Approach
**Pessimistic locking using database transactions**
- `SELECT ... FOR UPDATE`
- Wrapped inside `transaction.atomic()`

This guarantees:
- Only one request can modify ticket availability at a time
- No overselling of tickets
- Strong consistency during booking and cancellation

---

### Alternative 1: In-Memory Locks (Rejected)
**Why considered:**
- Simple to implement

**Why rejected:**
- Fails in multi-instance deployments
- Does not work across containers or machines
- Unsafe in real distributed systems

---

### Alternative 2: Optimistic Locking (Version Columns)
**Why considered:**
- Reduces lock contention

**Why rejected:**
- High retry rate under heavy contention (popular events)
- Adds complexity for retry logic
- Worse user experience during peak traffic

---

### Alternative 3: Redis / Distributed Locks
**Why considered:**
- Scales better horizontally

**Why rejected for this assignment:**
- Adds operational complexity
- Requires careful TTL handling and failure recovery
- Overkill for a 2–4 hour take-home assignment

---

### Alternative 4: Queue-Based Booking (Async)
**Why considered:**
- Very scalable
- Handles bursts well

**Why rejected:**
- Introduces eventual consistency
- Booking confirmation becomes asynchronous
- Not aligned with simple REST API requirement

---

## 3. Scaling to 1 Million Requests per Second

### Primary Bottleneck in Current Design
**Row-level locking on the `Event` table**

When tickets are almost sold out:
- All booking requests contend for the same event row
- Requests become serialized
- Database throughput becomes the limiting factor

---

### Why This Is Acceptable Here
- Strong consistency is more important than throughput for ticket booking
- Overselling is unacceptable
- This is a deliberate trade-off

---

### How This Would Be Scaled in Production

To reach ~1M RPS, the design would evolve:

#### a) Event Partitioning
- Shard events across databases
- Hot events isolated from cold events

#### b) Cache + Write-Through Model
- Maintain ticket counters in Redis
- Periodically sync to DB
- Use Lua scripts for atomic operations

#### c) Queue-Based Booking
- Requests placed into a queue (Kafka/SQS)
- Workers process bookings sequentially per event
- Client receives async confirmation

#### d) Reservation + Expiry Model
- Temporary ticket holds with expiration
- Final confirmation after payment
- Reduces contention on final inventory

---

## Final Note

This system intentionally prioritizes:
- Correctness over throughput
- Simplicity over premature optimization
- Clear transactional guarantees

The architecture is designed to be **easy to reason about, easy to test, and safe under concurrency**, while leaving clear paths for future scalability.

