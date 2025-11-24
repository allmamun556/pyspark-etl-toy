# Python Tutorial (Detailed, Beginner-Friendly, English)

Welcome to this complete Python tutorial designed for beginners and intermediate learners. This guide will teach you everything you need to know to start writing Python programs—from basic syntax to functions, classes, modules, file handling, and more.

---

# 1. What Is Python?

Python is a popular, high-level programming language known for its readability and versatility. It is used in:

* Web development
* Data science & machine learning
* Automation & scripting
* Software development
* Artificial intelligence
* Game development

Python's simple syntax makes it ideal for beginners.

---

# 2. Installing Python

Download Python from the official website:

* [https://www.python.org/downloads](https://www.python.org/downloads)

Check installation:

```bash
python --version
```

---

# 3. Your First Python Program

Create a file named `hello.py`:

```python
print("Hello, world!")
```

Run it:

```bash
python hello.py
```

---

# 4. Python Basics

## 4.1 Variables

```python
x = 10
name = "Alice"
```

Variables do not require explicit declaration.

## 4.2 Data Types

Common built-in types:

* `int` (integer)
* `float` (decimal numbers)
* `str` (strings)
* `bool` (True/False)
* `list`
* `tuple`
* `dict`
* `set`

## 4.3 Type Checking

```python
print(type(x))
```

## 4.4 Type Casting

```python
int("5")
float(3)
str(100)
```

---

# 5. Operators

## 5.1 Arithmetic Operators

```python
+  -  *  /  //  %  **
```

Example:

```python
print(3 + 2)
print(10 // 3) # integer division
```

## 5.2 Comparison Operators

```python
== != > < >= <=
```

## 5.3 Logical Operators

```python
and  or  not
```

---

# 6. Conditional Statements

## If/Else

```python
x = 10
if x > 5:
    print("Greater than 5")
elif x == 5:
    print("Equal to 5")
else:
    print("Less than 5")
```

---

# 7. Loops

## 7.1 For Loop

```python
for i in range(5):
    print(i)
```

## 7.2 While Loop

```python
count = 0
while count < 3:
    print(count)
    count += 1
```

## Loop Control

* `break`
* `continue`
* `pass`

---

# 8. Data Structures

## 8.1 Lists

```python
fruits = ["apple", "banana", "cherry"]
```

Indexing:

```python
fruits[0]
```

Add/remove:

```python
fruits.append("mango")
fruits.remove("banana")
```

## 8.2 Tuples

Immutable sequences:

```python
coords = (10, 20)
```

## 8.3 Dictionaries

Key/value storage:

```python
person = {"name": "Alice", "age": 25}
```

Access:

```python
person["name"]
```

## 8.4 Sets

Unique unordered items:

```python
nums = {1, 2, 3}
```

---

# 9. Functions

## Defining a Function

```python
def greet(name):
    return f"Hello {name}"
```

## Default Parameters

```python
def power(x, y=2):
    return x ** y
```

## Arguments vs Keyword Arguments

```python
power(3, y=4)
```

---

# 10. Lambda (Anonymous Functions)

```python
square = lambda x: x * x
print(square(5))
```

---

# 11. Map, Filter, Reduce

## Map

```python
nums = [1, 2, 3]
print(list(map(lambda x: x * 2, nums)))
```

## Filter

```python
print(list(filter(lambda x: x > 1, nums)))
```

## Reduce

```python
from functools import reduce
print(reduce(lambda a, b: a + b, nums))
```

---

# 12. Exception Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("Done.")
```

---

# 13. File Handling

## Reading a File

```python
with open("data.txt", "r") as f:
    content = f.read()
```

## Writing to a File

```python
with open("output.txt", "w") as f:
    f.write("Hello!")
```

---

# 14. Object-Oriented Programming (OOP)

## Creating a Class

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hello, I am {self.name}")

p = Person("Alice", 25)
p.greet()
```

---

# 15. Modules and Packages

## Importing Modules

```python
import math
math.sqrt(16)
```

## Creating Your Own Module

Create file: `mymodule.py`

```python
def hello():
    print("Hi!")
```

Use it:

```python
import mymodule
mymodule.hello()
```

---

# 16. Virtual Environments

Create:

```bash
python -m venv venv
```

Activate:

* Windows: `venv\Scripts\activate`
* Mac/Linux: `source venv/bin/activate`

Deactivate:

```bash
deactivate
```

---

# 17. Working With Libraries

Popular libraries:

* NumPy
* Pandas
* Matplotlib
* Scikit-Learn

Install:

```bash
pip install numpy pandas
```

---

# 18. Python Tips & Best Practices

* Follow PEP 8 style guidelines
* Use meaningful variable names
* Avoid deeply nested code
* Use list comprehensions when possible

Example:

```python
squares = [x*x for x in range(10)]
```

---

# 19. Summary

This tutorial covered:

* Python basics
* Data structures
* Functions & lambda
* OOP
* Modules
* File handling
* Error handling
* Virtual environments

If you'd like, I can add:

* Python cheat sheet
* Practice exercises
* Advanced Python concepts
* Python interview questions
* Real-world Python projects
Your full OOP tutorial is ready!

If you’d like, I can also create:

✅ Advanced OOP tutorial (design patterns, SOLID, decorators, metaclasses)
✅ OOP interview questions
✅ OOP exercises with solutions
✅ A complete real-world OOP project (bank system, ecommerce system, employee management, etc.)

Just tell me what you want next!
# Object-Oriented Programming (OOP) in Python – Detailed Tutorial (with Examples)

Welcome to this complete OOP tutorial in Python. This guide will teach you everything you need to know—from classes and objects to advanced OOP concepts like inheritance, polymorphism, abstraction, and encapsulation.

---

# 1. What Is OOP?

**Object-Oriented Programming (OOP)** is a programming paradigm based on the concept of **objects**, which contain:

* **State** (attributes / variables)
* **Behavior** (methods / functions)

OOP helps make code more:

* Organized
* Reusable
* Scalable
* Maintainable

Python is a fully object-oriented language.

---

# 2. Classes and Objects

A **class** is a blueprint for creating objects.
An **object** is an instance of a class.

## Example: Creating a Class and Object

```python
class Person:
    def __init__(self, name, age):  # Constructor
        self.name = name
        self.age = age

    def greet(self):  # Method
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

p1 = Person("Alice", 25)
p1.greet()
```

---

# 3. The `__init__` Method (Constructor)

The `__init__` method initializes the object's attributes.

```python
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

car = Car("Toyota", "Corolla")
```

---

# 4. Attributes

There are two types of attributes:

* **Instance attributes** (unique to each object)
* **Class attributes** (shared by all objects)

## Example:

```python
class Dog:
    species = "Canine"   # Class attribute

    def __init__(self, name):
        self.name = name  # Instance attribute

rex = Dog("Rex")
print(rex.species)  # Canine
print(rex.name)      # Rex
```

---

# 5. Methods

Three types:

* **Instance methods** (most common)
* **Class methods** (`@classmethod`)
* **Static methods** (`@staticmethod`)

## 5.1 Instance Method

```python
class Example:
    def instance_method(self):
        print("This is an instance method.")
```

## 5.2 Class Method

```python
class Example:
    @classmethod
    def class_method(cls):
        print("This is a class method.")
```

## 5.3 Static Method

```python
class Example:
    @staticmethod
    def static_method():
        print("This is a static method.")
```

---

# 6. Encapsulation

Encapsulation restricts direct access to variables.

Python does not have true private variables, but uses naming conventions:

* `_variable` → protected (convention only)
* `__variable` → private (name-mangled)

## Example:

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Private

    def deposit(self, amount):
        self.__balance += amount

    def get_balance(self):
        return self.__balance

acc = BankAccount(100)
acc.deposit(50)
print(acc.get_balance())
```

---

# 7. Inheritance

Inheritance allows one class to take properties of another.

```python
class Animal:
    def speak(self):
        return "Some sound"

class Dog(Animal):  # Dog inherits from Animal
    def speak(self):
        return "Bark!"

d = Dog()
print(d.speak())
```

---

# 8. Types of Inheritance

* **Single inheritance** (one parent)
* **Multiple inheritance** (multiple parents)
* **Multilevel inheritance** (grandparent → parent → child)
* **Hierarchical inheritance** (one parent → many children)
* **Hybrid inheritance** (combination)

## Example: Multilevel

```python
class A:
    pass
class B(A):
    pass
class C(B):
    pass
```

---

# 9. Polymorphism

Polymorphism lets different classes use the same method name.

## Example:

```python
class Cat:
    def sound(self):
        return "Meow"

class Cow:
    def sound(self):
        return "Moo"

for animal in [Cat(), Cow()]:
    print(animal.sound())
```

---

# 10. Method Overriding

A child class replaces a parent class method.

```python
class Parent:
    def show(self):
        print("Parent class")

class Child(Parent):
    def show(self):
        print("Child class")

Child().show()
```

---

# 11. Method Overloading (Python Style)

Python does **not** support traditional overloading.
Instead, use default arguments:

```python
def add(a, b=0, c=0):
    return a + b + c
```

---

# 12. Abstraction

Abstraction means hiding complex logic using simple interfaces.
Python uses the `abc` module.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius * self.radius

c = Circle(5)
print(c.area())
```

---

# 13. "super()" Function

Used to call parent class methods.

```python
class Parent:
    def __init__(self):
        print("Parent constructor")

class Child(Parent):
    def __init__(self):
        super().__init__()
        print("Child constructor")

Child()
```

---

# 14. Magic Methods / Dunder Methods

Special methods that start and end with `__`.

Common ones:

* `__str__`
* `__repr__`
* `__len__`
* `__add__`
* `__eq__`

## Example:

```python
class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __str__(self):
        return f"{self.title} has {self.pages} pages"

b = Book("Python 101", 300)
print(b)
```

---

# 15. Composition (Has-A Relationship)

Objects contain other objects.

```python
class Engine:
    def start(self):
        print("Engine starts")

class Car:
    def __init__(self):
        self.engine = Engine()  # Car has an engine

    def run(self):
        self.engine.start()
        print("Car is running")

Car().run()
```

---

# 16. OOP Project Example

Let's create a small project: a library system.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

class Library:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)

    def list_books(self):
        for b in self.books:
            print(f"{b.title} by {b.author}")

lib = Library()
lib.add_book(Book("1984", "George Orwell"))
lib.add_book(Book("Python Basics", "John Doe"))
lib.list_books()
```

---

# 17. OOP Best Practices

* Use descriptive class names
* Keep methods short and focused
* Avoid deep inheritance trees
* Prefer composition over inheritance
* Encapsulate data when possible

---

# 18. Summary

You learned:

* Classes & objects
* Constructor (`__init__`)
* Methods (instance, class, static)
* Encapsulation
* Inheritance
* Polymorphism
* Abstraction
* Magic methods
* Composition
* OOP best practices

If you'd like, I can add:

* OOP interview questions
* Advanced OOP concepts
* A full OOP project
* A cheat sheet for OOP
Absolutely — here is **everything you requested**, organized clearly and written in full detail:

# ✅ 1. OOP Interview Questions (with detailed answers)

Below are **real interview questions** that companies ask for Python and OOP roles (data, software, backend, QA, etc.), each with detailed answers.

---

## **Q1. What is OOP and why is it used?**

**Answer:**
Object-Oriented Programming (OOP) is a programming paradigm based on *objects* that bundle **data (attributes)** and **behavior (methods)**.
It helps with:

* Reusability
* Modularity
* Maintainability
* Reducing code duplication

---

## **Q2. What is the difference between a class and an object?**

* **Class** → blueprint for creating objects
* **Object** → instance of a class

**Example:**

```python
class Dog:
    pass

d = Dog()  # Object
```

---

## **Q3. What is the purpose of the `__init__` method?**

It’s the **constructor**, automatically called when creating an object.

```python
class Person:
    def __init__(self, name):
        self.name = name
```

---

## **Q4. What is the difference between instance, class, and static methods?**

### **Instance Method**

* Takes `self`
* Can access instance variables

### **Class Method**

* Takes `cls`
* Accesses class variables

### **Static Method**

* No `self` or `cls`
* Utility function inside class

**Example:**

```python
class Test:
    @classmethod
    def cmethod(cls): pass

    @staticmethod
    def smethod(): pass
```

---

## **Q5. What is inheritance? What types does Python support?**

Inheritance allows classes to acquire attributes/methods of others.
Python supports:

* Single
* Multiple
* Multilevel
* Hierarchical
* Hybrid

---

## **Q6. What is polymorphism?**

Same method name, different behavior across classes.

---

## **Q7. What is method overriding?**

Child class replaces parent’s implementation.

```python
class A:
    def show(self): print("A")

class B(A):
    def show(self): print("B")
```

---

## **Q8. Does Python support method overloading?**

Not officially.
You simulate with **default arguments**.

---

## **Q9. What is encapsulation?**

Restricting access to variables using:

* `_protected`
* `__private` (name-mangling)

---

## **Q10. What is abstraction?**

Hiding implementation using abstract classes:

```python
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self): pass
```

---

## **Q11. What is composition? (HAS-A relationship)**

A class that contains another class.

---

## **Q12. Difference between composition and inheritance?**

* **Inheritance** → IS-A
* **Composition** → HAS-A
  (Composition is preferred for cleaner design.)

---

## **Q13. What are magic methods?**

Built-in dunder methods:

* `__str__`, `__repr__`, `__add__`, `__eq__`, etc.

---

## **Q14. What is a metaclass?**

A class that creates classes (advanced OOP).

---

## **Q15. SOLID principles?**

Widely used in OOP design (explained in the next section).

---

# ✅ 2. Advanced OOP Concepts (with explanations)

These topics are asked in higher-level interviews.

---

# **2.1 SOLID Design Principles**

### **S – Single Responsibility**

A class should do *one thing only*.

### **O – Open/Closed Principle**

Open for extension, closed for modification.

### **L – Liskov Substitution Principle**

Subclass should replace parent without breaking logic.

### **I – Interface Segregation**

Classes should not depend on methods they don't use.

### **D – Dependency Inversion**

Depend on abstractions, not concrete classes.

---

# **2.2 Composition over Inheritance**

Inheritance can lead to tightly coupled code.
Composition is more flexible.

---

# **2.3 Mixins**

Small classes used to add reusable features.

```python
class LoggerMixin:
    def log(self, msg):
        print(f"[LOG] {msg}")

class User(LoggerMixin):
    pass
```

---

# **2.4 Magic Methods / Operator Overloading**

Example of overloading `+`:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
```

---

# **2.5 Abstract Base Classes**

Using Python’s `abc` module.

---

# **2.6 Metaclasses (Very Advanced)**

A metaclass defines how a class behaves.

```python
class Meta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_by"] = "MetaClass"
        return super().__new__(cls, name, bases, attrs)

class Test(metaclass=Meta):
    pass
```

---

# **2.7 Decorators as OOP tools**

Decorators modify behavior, often acting like wrappers for objects.

---

# **2.8 Property Decorators (Getters & Setters)**

```python
class Person:
    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, val):
        if val < 0:
            raise ValueError("Age cannot be negative")
        self._age = val
```

---

# **2.9 Multiple Inheritance & MRO (Method Resolution Order)**

MRO uses C3 linearization.
Check it with:

```python
ClassName.__mro__
```

---

# **2.10 Interfaces in Python**

Python doesn't support interfaces but uses ABC (Abstract Base Class) instead.

---

# ✅ 3. Full OOP Project (Real-World Example)

## **Project: Library Management System**

### **Goal:**

Create a system that manages:

* Books
* Members
* Book loans
* Book availability

---

## **3.1 Project Structure**

```
Library
 ├── Book
 ├── Member
 ├── Library
 └── Loan
```

---

## **3.2 Code Implementation**

### **Book Class**

```python
class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = True

    def __str__(self):
        return f"{self.title} by {self.author}"
```

---

### **Member Class**

```python
class Member:
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id

    def __str__(self):
        return f"{self.name} (ID: {self.member_id})"
```

---

### **Loan Class**

```python
class Loan:
    def __init__(self, book, member):
        self.book = book
        self.member = member

    def __str__(self):
        return f"{self.book.title} loaned to {self.member.name}"
```

---

### **Library Class**

```python
class Library:
    def __init__(self):
        self.books = []
        self.members = []
        self.loans = []

    def add_book(self, book):
        self.books.append(book)

    def register_member(self, member):
        self.members.append(member)

    def loan_book(self, isbn, member_id):
        book = next((b for b in self.books if b.isbn == isbn and b.available), None)
        member = next((m for m in self.members if m.member_id == member_id), None)

        if not book:
            print("Book not available.")
            return

        loan = Loan(book, member)
        self.loans.append(loan)
        book.available = False
        print(f"Loan created: {loan}")

    def return_book(self, isbn):
        loan = next((l for l in self.loans if l.book.isbn == isbn), None)
        if loan:
            loan.book.available = True
            self.loans.remove(loan)
            print(f"Returned: {loan.book.title}")
```

---

### **Usage**

```python
lib = Library()

lib.add_book(Book("1984", "George Orwell", "123"))
lib.add_book(Book("Python 101", "John Doe", "456"))

lib.register_member(Member("Alice", 1))
lib.register_member(Member("Bob", 2))

lib.loan_book("123", 1)
lib.return_book("123")
```

---

# ✅ 4. OOP Cheat Sheet (Quick Reference)

### **Creating a Class**

```python
class MyClass:
    pass
```

### **Constructor**

```python
def __init__(self): pass
```

### **Instance Attribute**

```python
self.name = name
```

### **Class Attribute**

```python
class Dog:
    species = "Canine"
```

### **Instance Method**

```python
def method(self): pass
```

### **Class Method**

```python
@classmethod
def m(cls): pass
```

### **Static Method**

```python
@staticmethod
def s(): pass
```

### **Inheritance**

```python
class B(A): pass
```

### **Super()**

```python
super().__init__()
```

### **Polymorphism**

```python
def sound(self): pass
```

### **Encapsulation**

```python
self.__private
```

### **Abstraction**

```python
from abc import ABC, abstractmethod
```

### **Magic Methods**

* `__init__`
* `__str__`
* `__repr__`
* `__len__`
* `__eq__`
* `__add__`

### **Composition**

```python
self.engine = Engine()
```

### **Property**

```python
@property
def age(self): pass
```

---

# 🎉 All Done!

Would you like:

📘 OOP practice exercises?
🤖 A full OOP exam with answers?
📚 Additional real-world OOP projects (Bank System, ATM, HR System, etc.)?

Just tell me!
Absolutely — here are **three full real-world OOP projects** written clearly and in detail:

# ✅ Project 1 — Bank Account System (Realistic & Fully OOP)

## 🎯 Goal

Build a system that manages:

* Bank accounts
* Deposits
* Withdrawals
* Transfers
* Account statements
* Multiple account types

---

## 🧩 Class Structure

```
Bank
 ├── Account (Base Class)
 │      ├── SavingsAccount
 │      └── CheckingAccount
 ├── Transaction
 └── Customer
```

---

## 🧱 Code Implementation

### **Account Base Class**

```python
class Account:
    def __init__(self, account_number, owner, balance=0):
        self.account_number = account_number
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited ${amount}. New balance: ${self.balance}")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds!")
            return
        self.balance -= amount
        print(f"Withdrew ${amount}. New balance: ${self.balance}")

    def __str__(self):
        return f"{self.owner} - Account {self.account_number} - Balance ${self.balance}"
```

---

### **Savings Account Class**

```python
class SavingsAccount(Account):
    INTEREST_RATE = 0.02

    def add_interest(self):
        interest = self.balance * SavingsAccount.INTEREST_RATE
        self.balance += interest
        print(f"Interest added: ${interest}. New balance: ${self.balance}")
```

---

### **Checking Account Class**

```python
class CheckingAccount(Account):
    OVERDRAFT_LIMIT = 200

    def withdraw(self, amount):
        if amount > self.balance + CheckingAccount.OVERDRAFT_LIMIT:
            print("Overdraft limit exceeded.")
            return
        self.balance -= amount
        print(f"Withdrew ${amount}. New balance: ${self.balance}")
```

---

### **Customer Class**

```python
class Customer:
    def __init__(self, name, customer_id):
        self.name = name
        self.customer_id = customer_id
        self.accounts = []

    def open_account(self, account):
        self.accounts.append(account)

    def list_accounts(self):
        for acc in self.accounts:
            print(acc)
```

---

### **Bank Class**

```python
class Bank:
    def __init__(self):
        self.customers = []

    def add_customer(self, customer):
        self.customers.append(customer)

    def find_account(self, account_number):
        for customer in self.customers:
            for account in customer.accounts:
                if account.account_number == account_number:
                    return account
        return None
```

---

### **Usage**

```python
bank = Bank()

cust1 = Customer("Alice", 1)
cust2 = Customer("Bob", 2)

acc1 = SavingsAccount("ACC100", "Alice", 1000)
acc2 = CheckingAccount("ACC200", "Bob", 500)

cust1.open_account(acc1)
cust2.open_account(acc2)

bank.add_customer(cust1)
bank.add_customer(cust2)

acc1.deposit(500)
acc1.add_interest()

acc2.withdraw(600)
```

---

# 🎉 Features You Can Add

* ATM interface
* Login system
* Card PIN validation
* Transaction logs
* Monthly statements

---

# ✅ Project 2 — ATM Machine System (OOP Simulation)

## 🎯 Goal

Simulate:

* Insert card
* Enter PIN
* Check balance
* Withdraw money
* Transfer funds
* Print receipt

---

## 🧩 Class Structure

```
ATM
 ├── Card
 ├── Customer
 └── BankAccount
```

---

## 🧱 Code Implementation

### **BankAccount Class**

```python
class BankAccount:
    def __init__(self, acc_no, pin, balance=0):
        self.acc_no = acc_no
        self.pin = pin
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds.")
            return False
        self.balance -= amount
        print(f"Withdrawn: ${amount}. New balance: ${self.balance}")
        return True

    def check_balance(self):
        print(f"Balance: ${self.balance}")
```

---

### **ATM Class**

```python
class ATM:
    def __init__(self, accounts):
        self.accounts = accounts

    def authenticate(self, acc_no, pin):
        account = self.accounts.get(acc_no)
        if account and account.pin == pin:
            print("Authentication successful!")
            return account
        print("Invalid credentials.")
        return None
```

---

### **Usage**

```python
acc1 = BankAccount("1111", "1234", 800)
acc2 = BankAccount("2222", "5678", 1200)

atm = ATM({"1111": acc1, "2222": acc2})

account = atm.authenticate("1111", "1234")
if account:
    account.check_balance()
    account.withdraw(200)
```

---

# 🎉 Features You Can Add

* Incorrect PIN lockout
* Transfer between accounts
* Receipts
* Admin interface

---

# ✅ Project 3 — HR Management System (Employee Management)

## 🎯 Goal

Manage:

* Employees
* Departments
* Salaries
* Promotions
* Performance scores

---

## 🧩 Class Structure

```
HRSystem
 ├── Employee
 ├── Manager
 └── Department
```

---

## 🧱 Code Implementation

### **Employee Class**

```python
class Employee:
    def __init__(self, name, emp_id, salary):
        self.name = name
        self.emp_id = emp_id
        self.salary = salary

    def apply_raise(self, percent):
        self.salary += self.salary * percent
        print(f"{self.name}'s new salary: {self.salary}")
```

---

### **Manager (Inheritance)**

```python
class Manager(Employee):
    def __init__(self, name, emp_id, salary, team=None):
        super().__init__(name, emp_id, salary)
        self.team = team if team else []

    def add_to_team(self, employee):
        self.team.append(employee)
```

---

### **Department Class**

```python
class Department:
    def __init__(self, name):
        self.name = name
        self.employees = []

    def add_employee(self, employee):
        self.employees.append(employee)

    def list_employees(self):
        for emp in self.employees:
            print(f"{emp.name} - ${emp.salary}")
```

---

### **Usage**

```python
dept = Department("IT")

emp1 = Employee("Alice", 101, 5000)
emp2 = Employee("Bob", 102, 4500)
mgr = Manager("Carol", 200, 8000)

dept.add_employee(emp1)
dept.add_employee(emp2)
dept.add_employee(mgr)

mgr.add_to_team(emp1)

dept.list_employees()
```

---

# 🎯 Features You Can Add

* Attendance system
* Performance reviews
* Payroll system
* Employee login portal
* Promotion rules
* Reporting hierarchies

---

# 🎉 BONUS: OOP Cheat Sheet

## **🔹 Class Definition**

```python
class A:
    pass
```

## **🔹 Constructor**

```python
def __init__(self, x): self.x = x
```

## **🔹 Instance Method**

```python
def method(self): pass
```

## **🔹 Class Method**

```python
@classmethod
def m(cls): pass
```

## **🔹 Static Method**

```python
@staticmethod
def s(): pass
```

## **🔹 Inheritance**

```python
class B(A): pass
```

## **🔹 Polymorphism**

```python
def sound(self): pass
```

## **🔹 Abstraction**

```python
from abc import ABC, abstractmethod
```

## **🔹 Encapsulation**

```python
self.__private
```

## **🔹 Composition**

```python
self.engine = Engine()
```

## **🔹 Magic Methods**

```python
def __str__(self): pass
def __add__(self, other): pass
```

---

# ⭐ Want More Projects?

I can create professional, complete OOP systems such as:

* 🚕 **Uber Ride System**
* 🛒 **E-commerce Shopping Cart System**
* 🍔 **Restaurant Ordering System**
* 🎓 **University Student Management System**
* 🚚 **Logistics / Delivery Tracking System**
* 🏦 **ATM + Banking System with Database**
* 📚 **Library + Membership + Fine Calculation System**

Just tell me which one you'd like!
Absolutely — here is a **complete, detailed, and professional-level Python interview question set**.
All questions are written in **clear English** and include **explanations and examples**.

These cover all levels:
✅ Beginner
✅ Intermediate
✅ Advanced
✅ Real-world / practical questions
✅ Trick questions

---

# 🟦 **PYTHON INTERVIEW QUESTIONS (With Detailed Answers)**

---

# 🔹 **SECTION 1 — BASIC PYTHON INTERVIEW QUESTIONS**

---

## **1. What is Python, and what are its main features?**

**Answer:**
Python is a high-level, interpreted, general-purpose programming language known for:

* Simple and readable syntax
* Dynamic typing
* Large standard library
* Cross-platform compatibility
* Support for multiple programming paradigms (OOP, functional, procedural)

Used in data science, AI, web development, DevOps, automation, etc.

---

## **2. What are Python’s built-in data types?**

* **Numbers:** int, float, complex
* **Sequence:** list, tuple, range
* **Text:** str
* **Mapping:** dict
* **Set types:** set, frozenset
* **Boolean:** bool
* **Binary types:** bytes, bytearray, memoryview

---

## **3. What is the difference between list and tuple?**

| List                 | Tuple                     |
| -------------------- | ------------------------- |
| Mutable (can change) | Immutable (cannot change) |
| Slower               | Faster                    |
| Uses []              | Uses ()                   |

Example:

```python
lst = [1, 2, 3]
tup = (1, 2, 3)
```

---

## **4. What is the difference between `==` and `is`?**

* `==` checks **value equality**
* `is` checks **object identity (memory address)**

```python
a = [1,2]
b = [1,2]

a == b   # True
a is b   # False
```

---

## **5. What is PEP8?**

PEP8 is Python's official **style guideline**, covering naming conventions, indentation, line length, etc.

---

## **6. What are Python namespaces?**

Namespaces store variable names. Types:

* **Local**
* **Enclosed**
* **Global**
* **Built-in**

Order: **LEGB**.

---

# 🔹 **SECTION 2 — INTERMEDIATE PYTHON INTERVIEW QUESTIONS**

---

## **7. What is a decorator in Python?**

A decorator modifies the behavior of a function without changing its code.

Example:

```python
def my_decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@my_decorator
def hello():
    print("Hello")

hello()
```

---

## **8. What is the difference between an iterator and an iterable?**

* **Iterable**: object that can return an iterator (list, string, dict).
* **Iterator**: object with `__next__()` method.

Example:

```python
iter_obj = iter([1,2,3])
print(next(iter_obj))
```

---

## **9. What are list comprehensions?**

Short syntax for creating lists.

```python
squares = [x*x for x in range(10)]
```

---

## **10. Explain *args and **kwargs**

* `*args` → variable-length positional arguments
* `**kwargs` → variable-length keyword arguments

```python
def func(*args, **kwargs):
    print(args, kwargs)

func(1, 2, name="John")
```

---

## **11. What is the difference between `append()` and `extend()`?**

```python
lst = [1,2]
lst.append([3,4])  # [1,2,[3,4]]
lst.extend([3,4])  # [1,2,3,4]
```

---

## **12. Explain the concept of shallow vs deep copy.**

```python
import copy

shallow = copy.copy(obj)
deep = copy.deepcopy(obj)
```

Shallow copy copies references; deep copy copies full objects recursively.

---

## **13. What is a lambda function?**

Anonymous inline function:

```python
square = lambda x: x * x
```

---

## **14. What are generators?**

Functions using `yield`.
Used for large datasets because they save memory.

```python
def gen():
    yield 1
    yield 2

g = gen()
next(g)
```

---

# 🔹 **SECTION 3 — ADVANCED PYTHON INTERVIEW QUESTIONS**

---

## **15. What is GIL (Global Interpreter Lock)?**

GIL allows only **one thread** to execute Python bytecode at a time.

Effects:

* Good for I/O-bound tasks
* Bad for CPU-heavy tasks
* Multiprocessing can bypass it

---

## **16. How does memory management work in Python?**

* Automatic garbage collection
* Reference counting
* Generational garbage collector

---

## **17. What is monkey patching?**

Changing behavior of modules/classes at runtime.

```python
class A:
    def show(self): print("Original")

def new_show(self): print("Modified")

A.show = new_show
```

---

## **18. What is the difference between multiprocessing and multithreading?**

| Multithreading     | Multiprocessing    |
| ------------------ | ------------------ |
| Shares memory      | Separate memory    |
| Limited by GIL     | Not limited        |
| Good for I/O tasks | Good for CPU tasks |

---

## **19. What is a context manager?**

Allows setup and cleanup using `with`.

```python
with open("file.txt") as f:
    data = f.read()
```

You can create your own with:

```python
class MyContext:
    def __enter__(self): print("start")
    def __exit__(self, exc, val, tb): print("end")
```

---

## **20. What is the difference between `@classmethod` and `@staticmethod`?**

* `classmethod(cls)` → works with class
* `staticmethod()` → simple utility function inside class

---

## **21. What are metaclasses?**

A class that creates classes.

```python
class Meta(type):
    pass

class MyClass(metaclass=Meta):
    pass
```

---

## **22. Explain duck typing.**

“If it looks like a duck and quacks like a duck, it is a duck.”

Python cares about **behavior**, not type.

---

# 🔹 **SECTION 4 — PYTHON CODING INTERVIEW QUESTIONS**

---

## **23. Reverse a string**

```python
s = "hello"
print(s[::-1])
```

---

## **24. Find duplicates in a list**

```python
lst = [1,2,3,2,1]
duplicates = [x for x in lst if lst.count(x) > 1]
```

---

## **25. Count frequency of characters**

```python
from collections import Counter

Counter("banana")
```

---

## **26. Fibonacci generator**

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
```

---

## **27. Check if a string is a palindrome**

```python
s == s[::-1]
```

---

## **28. Flatten a list**

```python
flat = [item for sub in lst for item in sub]
```

---

# 🔹 **SECTION 5 — REAL-WORLD PYTHON INTERVIEW QUESTIONS**

---

## **29. How do you handle large files in Python?**

Use generators + incremental reads:

```python
with open("large.txt") as f:
    for line in f:
        process(line)
```

---

## **30. How do you make Python code faster?**

* Use built-in functions
* Use list comprehensions
* Avoid global variables
* Use `multiprocessing`
* Use NumPy
* Use PyPy interpreter

---

## **31. How do you debug Python code?**

* Using `pdb`
* Using `logging` module
* Using IDE debugger
* Adding print statements

---

## **32. How do you handle errors?**

Using try-except:

```python
try:
    a = 1 / 0
except ZeroDivisionError:
    print("error")
finally:
    print("done")
```

---

## **33. What are design patterns you've used in Python?**

* Singleton
* Factory
* Strategy
* Observer
* Adapter
* Repository pattern

---

# 🔹 **SECTION 6 — TRICK / COMMON TRAP QUESTIONS**

---

## **34. What will this print?**

```python
x = [[]] * 3
x[0].append(1)
print(x)
```

**Answer:**
`[[1], [1], [1]]`
Because all inner lists refer to the SAME object.

---

## **35. What is the output?**

```python
def func(a, L=[]):
    L.append(a)
    return L

print(func(1))
print(func(2))
```

**Answer:**

```
[1]
[1,2]
```

Default arguments are evaluated **once**.

---

If you'd like, I can also prepare:

✅ 40 more Python interview questions
✅ A PDF version
✅ Coding test challenges with solutions
✅ Senior-level Python system design questions
Just tell me!
Perfect — here is EVERYTHING you requested, written clearly and professionally:

# ✅ **1. Senior-Level Python System Design Interview Questions**

# ✅ **2. +40 More Python Interview Questions (All Levels)**

# ✅ **3. Coding Test Challenges + Full Solutions**

This is a **complete preparation package** used in real company interviews.

---

# 🧩 **1. SENIOR-LEVEL PYTHON SYSTEM DESIGN INTERVIEW QUESTIONS**

These questions are asked for senior Python, backend, data engineer, ML engineer, and architect roles.

---

## **Q1 — Design a scalable web crawler in Python.**

**Key points you must mention:**

* Use `asyncio` or `concurrent.futures` for concurrency
* Use `requests` + `aiohttp`
* Use `queue` for scheduling new URLs
* Prevent revisits using Bloom filters or Redis SET
* Handle robots.txt
* Store crawl results in DB
* Use rate limiting per host
* Fault tolerance with retries
* Horizontal scaling using message queues (Kafka, RabbitMQ)

---

## **Q2 — Design a high-performance logging system in Python.**

You should mention:

* Use Python’s `logging` module with multiple handlers
* Use non-blocking logging with queues
* Use rotating log files
* Batch logs to S3 or DB
* For large-scale:

  * Python app → Kafka → Logstash → Elasticsearch
* Use correlation IDs for distributed tracing
* Implement async logging for speed

---

## **Q3 — Design a REST API in Python for managing millions of users.**

Expected answer components:

* Use **FastAPI** or **Flask**
* Use **Pydantic** for validation
* Use **Gunicorn + Uvicorn** workers
* Use caching: Redis (for sessions, caching)
* DB sharding / partitioning strategies
* JWT authentication
* Load balancer (NGINX)
* Rate limiting
* Asynchronous I/O to handle concurrency

---

## **Q4 — How would you design an ETL pipeline in Python for large datasets?**

Components to mention:

* Use Airflow or Prefect
* Extract from sources (S3, MySQL, API)
* Transform using Pandas / PySpark
* Load to warehouse (Snowflake, BigQuery, Redshift)
* Use schema validation
* Add checkpointing
* Partitioned data storage
* Orchestration + retries + alerting

---

## **Q5 — Design an event-driven microservices architecture using Python.**

Mention:

* Services communicate via Kafka / RabbitMQ
* Use FastAPI for endpoints
* Use Celery for async tasks
* Docker + Kubernetes for deployment
* CI/CD pipelines
* Logging + metrics + tracing
* API gateway + rate limiting

---

## **Q6 — Design an in-memory cache system in Python.**

Options:

* Use `functools.lru_cache` for small apps
* Use Redis for distributed apps
* TTL support, cache invalidation strategy
* Write caching middleware
* Support for LFU / LRU eviction

---

## **Q7 — Design a Python-based machine learning feature store.**

Include:

* Data ingestion pipelines
* Feature versioning
* Feature storage (Parquet, Delta Lake)
* Online store (Redis)
* Offline store (S3 + Spark)
* API endpoints for serving features
* Metadata tracking

---

## **Q8 — Design a pub-sub chat server using Python.**

Include:

* Asyncio WebSockets
* Rooms & channels
* Redis pub-sub backend
* Load balancing
* Token authentication
* Persistence of message history

---

## **Q9 — How would you structure a large Python project?**

Answer should include:

* Clean folder structure:

  ```
  src/
    api/
    core/
    models/
    services/
    utils/
  tests/
  requirements.txt
  config/
  ```
* Use dependency injection
* Avoid circular imports
* Modularize code
* Use environment configs
* Unit tests + separation of concerns

---

## **Q10 — How do you optimize Python performance in a production system?**

Mention:

* Use PyPy for faster execution
* Use multiprocessing for CPU-heavy tasks
* Use Cython or Numba
* Use vectorized NumPy operations
* Avoid GIL bottleneck with process pools
* Cache results
* Replace Python loops
* Profile bottlenecks with `cProfile`
* Rewrite hot code paths in Rust/C++

---

If you want, I can produce **answers + sample architecture diagrams** for each one.

---

# 🟦 **2. +40 More Python Interview Questions (Medium + Advanced)**

Here are **40 additional questions**, grouped by difficulty.

---

# 🔸 **BEGINNER / JUNIOR (10 Questions)**

1. What is Python and why is it popular?
2. What is the difference between Python 2 and Python 3?
3. What are mutable and immutable types?
4. What is type casting in Python?
5. Explain the role of `self`.
6. What are Python modules and packages?
7. How do you handle exceptions?
8. What are docstrings?
9. What does `*args` and `**kwargs` mean?
10. Explain list slicing.

---

# 🔸 **INTERMEDIATE (15 Questions)**

11. Explain decorators with examples.
12. What is a generator?
13. What are context managers?
14. Difference between list, set, tuple, dict.
15. What is a closure?
16. What is the difference between `deepcopy` and `copy`?
17. What is the GIL?
18. What are Python iterators?
19. How does garbage collection work?
20. What is monkey patching?
21. Difference between `__str__` and `__repr__`.
22. Explain the MRO (Method Resolution Order).
23. What is duck typing?
24. Difference between multiprocessing and multithreading.
25. Explain virtual environments.

---

# 🔸 **ADVANCED (15 Questions)**

26. Explain metaclasses.
27. What are data classes?
28. What are slots (`__slots__`)?
29. How does async/await work?
30. Explain the event loop in asyncio.
31. How do you avoid race conditions?
32. What are weak references?
33. Explain `functools.lru_cache`.
34. How do you optimize Python speed?
35. What is memoization?
36. Explain the Singleton pattern in Python.
37. What is the difference between multiprocessing.Queue and queue.Queue?
38. How does Python handle memory allocation?
39. Explain the difference between pickling and JSON serialization.
40. What is marshaling?

---

# 🧪 **3. CODING CHALLENGES (With Full Solutions)**

These are commonly asked in real coding tests.

---

# ⭐ **Challenge 1 — Two Sum Problem**

### ❓ **Problem**

Given an array and a target, return indices of two numbers that add to the target.

### ✅ Solution

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return (seen[diff], i)
        seen[num] = i

print(two_sum([2,7,11,15], 9))  # (0,1)
```

---

# ⭐ **Challenge 2 — Reverse a Linked List**

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev
```

---

# ⭐ **Challenge 3 — Implement LRU Cache**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

---

# ⭐ **Challenge 4 — Check Anagram**

```python
from collections import Counter

def is_anagram(a, b):
    return Counter(a) == Counter(b)
```

---

# ⭐ **Challenge 5 — Find Missing Number (0 to n)**

```python
def missing(lst):
    n = len(lst)
    return n * (n + 1) // 2 - sum(lst)
```

---

# ⭐ **Challenge 6 — String Compression**

```
aaabb → a3b2
```

```python
def compress(s):
    res = ""
    count = 1
    for i in range(1, len(s)+1):
        if i < len(s) and s[i] == s[i-1]:
            count += 1
        else:
            res += s[i-1] + str(count)
            count = 1
    return res
```

---

# ⭐ **Challenge 7 — Longest Common Prefix**

```python
def lcp(strs):
    if not strs: 
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if prefix == "":
                return ""
    return prefix
```

---

# ⭐ **Challenge 8 — Detect Loop in Linked List**

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

---

# ⭐ **Challenge 9 — Balanced Parentheses**

```python
def is_balanced(s):
    stack = []
    mapping = {')':'(', ']':'[', '}':'{'}
    for ch in s:
        if ch in mapping.values():
            stack.append(ch)
        else:
            if not stack or mapping[ch] != stack.pop():
                return False
    return not stack
```

---

# ⭐ **Challenge 10 — Top K Frequent Elements**

```python
from collections import Counter

def top_k(nums, k):
    freq = Counter(nums)
    return [x for x, _ in freq.most_common(k)]
```

---

# 🎉 **DONE! You now have:**

✅ Senior Python system-design interview questions
✅ +40 more Python interview questions
✅ 10 coding challenges with complete solutions

If you want, I can also provide:

📌 A **Python coding interview workbook (PDF)**
📌 Mock interview questions
📌 System design diagrams for each design problem
📌 More coding challenges (medium + hard)
📌 A full Python interview prep roadmap

Just tell me!

Natürlich!
Below are **all 40 questions**, each with **clear, complete, detailed answers in English**, written professionally so you can use them for interview preparation.

---

# 🔹 **BEGINNER / JUNIOR (10 Questions + Detailed Answers)**

---

### **1. What is Python and why is it popular?**

**Answer:**
Python is a high-level, interpreted programming language known for its clear syntax and readability.
It is popular because:

* Easy to learn (English-like syntax)
* Large standard library
* Multi-paradigm (OOP, functional, procedural)
* Huge ecosystem (NumPy, Pandas, Django, Flask, etc.)
* Strong community support
* Used in AI, data science, web development, automation

---

### **2. What is the difference between Python 2 and Python 3?**

**Answer:**

* Python 3 is the modern version; Python 2 is deprecated since 2020.
* `print` is a function in Python 3 (`print()`), but a statement in Python 2.
* Better Unicode support in Python 3.
* Division operator behaves differently:

  * Python 2 → `3/2 = 1`
  * Python 3 → `3/2 = 1.5`
* Python 3 has improved standard libraries and performance.

---

### **3. What are mutable and immutable types?**

**Answer:**

* **Mutable:** can be modified after creation
  → list, dict, set, bytearray
* **Immutable:** cannot be changed
  → int, float, str, tuple, frozenset, bytes

---

### **4. What is type casting in Python?**

**Answer:**
Converting one data type into another.

Example:

```python
int("5")      # 5
float("3.14") # 3.14
str(100)      # "100"
```

---

### **5. Explain the role of `self`.**

**Answer:**
`self` refers to the **current object instance**.
It is used to access:

* instance variables
* instance methods

It must be the first parameter of any instance method.

---

### **6. What are Python modules and packages?**

**Answer:**

* **Module:** a single Python file (`.py`)
* **Package:** a folder containing modules + `__init__.py`

Example:

```
my_app/
    __init__.py
    users.py
    models.py
```

---

### **7. How do you handle exceptions?**

Using `try–except–finally`.

```python
try:
    x = 1 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
finally:
    print("Done")
```

---

### **8. What are docstrings?**

**Answer:**
Documentation strings describing modules, classes, and functions.

```python
def add(a, b):
    """Returns the sum of a and b."""
    return a + b
```

Access with:

```python
help(add)
```

---

### **9. What does *args and **kwargs mean?**

**Answer:**
They allow **variable number of arguments**.

* `*args` → positional arguments
* `**kwargs` → keyword arguments

```python
def func(*args, **kwargs):
    print(args)
    print(kwargs)
```

---

### **10. Explain list slicing.**

**Answer:**
Extracting parts of a list or string.

```python
lst = [1,2,3,4,5]
lst[1:4]  # [2,3,4]
lst[::-1] # reversed list
```

---

# 🔹 **INTERMEDIATE (15 Questions + Detailed Answers)**

---

### **11. Explain decorators with examples.**

Decorators modify the behavior of a function **without changing its code**.

```python
def decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@decorator
def greet():
    print("Hello")

greet()
```

---

### **12. What is a generator?**

A generator returns items **one at a time** using `yield`, saving memory.

```python
def gen():
    yield 1
    yield 2
```

---

### **13. What are context managers?**

They handle setup and cleanup automatically (enter/exit).

```python
with open("file.txt") as f:
    data = f.read()
```

Custom:

```python
class MyContext:
    def __enter__(self): print("Start")
    def __exit__(self, *args): print("End")
```

---

### **14. Difference between list, set, tuple, dict.**

| Type  | Ordered    | Mutable | Allows Duplicates   |
| ----- | ---------- | ------- | ------------------- |
| List  | Yes        | Yes     | Yes                 |
| Tuple | Yes        | No      | Yes                 |
| Set   | No         | Yes     | No                  |
| Dict  | Yes (keys) | Yes     | Keys must be unique |

---

### **15. What is a closure?**

A closure remembers variables from its enclosing scope.

```python
def outer(x):
    def inner():
        return x
    return inner
```

---

### **16. What is the difference between deepcopy and copy?**

* `copy.copy()` → shallow copy (references nested objects)
* `copy.deepcopy()` → full recursive copy

---

### **17. What is the GIL?**

Global Interpreter Lock:
Only **one thread** executes Python bytecode at a time.

Impact:

* Good for I/O
* Bad for CPU-bound tasks
* Use multiprocessing to bypass GIL

---

### **18. What are Python iterators?**

An object with:

* `__iter__()`
* `__next__()`

---

### **19. How does garbage collection work?**

* Reference counting
* Cyclic garbage collector
* Automatically frees unused objects

---

### **20. What is monkey patching?**

Modifying a class or module at runtime.

```python
import math
math.sqrt = lambda x: 100
```

---

### **21. Difference between `__str__` and `__repr__`.**

* `__str__` → user-friendly string
* `__repr__` → developer/debug representation

---

### **22. Explain MRO (Method Resolution Order).**

Order Python uses to search for methods in multiple inheritance.
Uses **C3 linearization**.

Check via:

```python
Class.__mro__
```

---

### **23. What is duck typing?**

“If it walks like a duck, it’s a duck.”
Python checks **behavior**, not type.

---

### **24. Difference between multiprocessing and multithreading.**

| Multithreading  | Multiprocessing |
| --------------- | --------------- |
| Shares memory   | Separate memory |
| Affected by GIL | No GIL issues   |
| Good for I/O    | Good for CPU    |

---

### **25. Explain virtual environments.**

They isolate Python dependencies for a project.

Commands:

```bash
python -m venv venv
source venv/bin/activate
```

---

# 🔹 **ADVANCED (15 Questions + Detailed Answers)**

---

### **26. Explain metaclasses.**

A metaclass is the **class of a class**.
It controls class creation.

```python
class Meta(type):
    pass

class Test(metaclass=Meta):
    pass
```

---

### **27. What are data classes?**

Introduced in Python 3.7
Automatically generates:

* `__init__`
* `__repr__`
* `__eq__`

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

---

### **28. What are slots (`__slots__`)?**

Limits attributes and saves memory.

```python
class A:
    __slots__ = ['x', 'y']
```

---

### **29. How does async/await work?**

They allow asynchronous programming using cooperative multitasking.

```python
import asyncio

async def task():
    await asyncio.sleep(1)
```

---

### **30. Explain the event loop in asyncio.**

* Manages asynchronous tasks
* Schedules coroutines
* Runs callbacks and I/O events

Start loop:

```python
asyncio.run(task())
```

---

### **31. How do you avoid race conditions?**

* Use Locks (threading.Lock)
* Use Queues instead of shared state
* Use atomic operations

---

### **32. What are weak references?**

References that do not increase the object’s reference count.
Used to avoid memory leaks.

```python
import weakref
```

---

### **33. Explain `functools.lru_cache`.**

Caches function results to speed up repeated calls.

```python
from functools import lru_cache

@lru_cache()
def fib(n):
    ...
```

---

### **34. How do you optimize Python speed?**

* Use profiling (`cProfile`)
* Use NumPy (vectorized operations)
* Use Cython / PyPy
* Use multiprocessing for CPU-heavy tasks
* Avoid Python loops
* Use caching

---

### **35. What is memoization?**

Caching function results to avoid recomputation.

---

### **36. Explain the Singleton pattern in Python.**

Only one instance allowed.

```python
class Singleton:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

### **37. Difference between multiprocessing.Queue and queue.Queue?**

| queue.Queue     | multiprocessing.Queue |
| --------------- | --------------------- |
| For threads     | For processes         |
| Shared memory   | Separate memory       |
| Affected by GIL | Not affected          |

---

### **38. How does Python handle memory allocation?**

Uses Python Memory Manager:

* Private heap
* Reference counting
* Garbage collection (cyclic GC)
* Memory pooling for small objects

---

### **39. Explain difference between pickling and JSON serialization.**

| JSON           | Pickle             |
| -------------- | ------------------ |
| Text-based     | Binary             |
| Human-readable | Not human-readable |
| Cross-language | Python-specific    |
| Slower         | Faster             |

---

### **40. What is marshaling?**

Marshaling = process of **transforming an object into a byte stream** so it can be:

* transmitted across networks
* stored
* reconstructed later

Similar to serialization, but often used in RPC (remote procedure calls).

---

# 🎉 **DONE!**

You now have **full detailed answers for all 40 questions**, covering:

* Beginner
* Intermediate
* Advanced

If you'd like, I can also prepare:

✅ 50 Python coding tasks (easy → hard)
✅ Python + SQL interview package
✅ A full PDF version
✅ Python mock interview practice
Just tell me!
