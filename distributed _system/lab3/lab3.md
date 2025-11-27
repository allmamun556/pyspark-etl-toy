
#  **1. Explanation of What the Sample Code Does (Part a)**

## **Single-threaded program (`single_threading.py`)**

### **What it does**

* It executes **10 tasks sequentially**.
* Each task:

  * Prints a “START” message with a timestamp.
  * Sleeps for **5 seconds** (simulating work).
  * Prints an “END” message.
* After each task, the main loop waits **0.1 seconds** before starting the next one.

### **Timing**

* Each task takes 5 seconds → 10 tasks = **50 seconds**, plus the small delays.

### **Characteristics**

* **No overlap** between tasks.
* **CPU usage:** close to **0%**, because `sleep()` does not use CPU time.
* **Total runtime:** approx. **51 seconds**.

---

## **Multithreaded program (`multi_threading.py`)**

### **What it does**

* Creates 10 threads.
* Each thread runs `task(id)`:

  * Prints “START”
  * Sleeps 5 seconds
  * Prints “END”
* Threads are started with a **0.1 second delay** between each.

### **Timing**

* All threads sleep **in parallel**.
* Total execution time ≈ **5 seconds + small overhead** (≈ 6 seconds)

### **Characteristics**

* Tasks **overlap**.
* CPU usage:

  * Still very low (because threads only sleep).
  * Python threads do *not* improve CPU performance for CPU-heavy tasks because of the **GIL**.
  * But they *do* benefit I/O-bound tasks like sleeping.

---

# 📊 **2. Timing Diagrams + CPU Utilization (Part b)**

### **Case: 10 tasks, each 5 seconds**

## **Single-threaded Timing Diagram**

```
Time (s) →
Task 1: [=====5s=====]
Task 2:              [=====5s=====]
Task 3:                            [=====5s=====]
...
Task 10:                                               [=====5s=====]

Total time ≈ 50–51 seconds
```

### **CPU Utilization**

* `sleep()` means CPU is idle.
* CPU usage stays around **0–1%** the whole time.

---

## **Multithreaded Timing Diagram**

```
Time (s) →
Task 1: [=====5s=====]
Task 2:   [=====5s=====]
Task 3:     [=====5s=====]
...
Task 10:      [=====5s=====]

All finish around t ≈ 5–6 seconds
```

### **CPU Utilization**

* Again very low (~1–3% depending on print statements).
* Sleeping threads do not increase CPU load.

---

# 📁 **3. Larger Experiments (Part c)**

You must test:

| #tasks | duration |
| ------ | -------- |
| 10     | 5 sec    |
| 100    | 1 sec    |
| 500    | 1 sec    |

Below is the expected behavior.

---

## ✔️ **Expected Timing Results Table**

Assuming the 0.1s delay between thread starts:

### **Single-threaded results**

| Tasks | Duration per task | Total sleep time | Overhead (print + loop) | **Total time (expected)** |
| ----- | ----------------- | ---------------- | ----------------------- | ------------------------- |
| 10    | 5s                | 50s              | ~1s                     | **≈ 51s**                 |
| 100   | 1s                | 100s             | ~10s                    | **≈ 110s**                |
| 500   | 1s                | 500s             | ~50s                    | **≈ 550s**                |

**Reason:** all tasks run sequentially. CPU still idle.

---

### **Multithreaded results**

| Tasks | Duration per task | Time to start threads (0.1s each) | Task duration | **Total time (expected)** |
| ----- | ----------------- | --------------------------------- | ------------- | ------------------------- |
| 10    | 5s                | 1.0s                              | 5s            | **≈ 6s**                  |
| 100   | 1s                | 10s                               | 1s            | **≈ 11s**                 |
| 500   | 1s                | 50s                               | 1s            | **≈ 51s**                 |

**Notice the key pattern:**

* Runtime ≈ **thread startup time + task duration**
* Tasks run in parallel, but **thread creation becomes the bottleneck** with many tasks.

---

# 🧠 **Discussion**

### **1. Single-threaded**

* Very predictable: runtime grows **linearly** with the number of tasks.
* CPU usage remains low because the core activity is sleeping.
* Total time = N * duration.

### **2. Multithreaded**

* Tasks run **concurrently**, so sleep times overlap.
* Thread creation delay (0.1s) becomes the limiting factor.
* For large task counts (100 or 500), **startup delay dominates**.
* CPU usage slightly higher due to thread scheduling and printing.

### **3. Threading effectiveness**

* This workload is **I/O-bound** (sleep is considered I/O-like).
* Python’s GIL does *not* matter, so threading is effective.
* If tasks were CPU-bound, multithreading would not help.

---

# 🎯 **Final Summary**

* **Single-threading:**
  Slow, tasks run one after another. Runtime scales linearly.

* **Multithreading:**
  Very fast for few tasks. For many tasks, performance is limited by thread creation delay.

* **CPU Utilization:**
  Always low, because tasks only sleep.

* **Best observation:**
  Multithreading dramatically reduces total execution time for I/O-bound tasks.

---


