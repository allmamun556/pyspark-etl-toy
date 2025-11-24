# GitHub Actions CI/CD Tutorial (Detailed and Beginner-Friendly)

Welcome to this complete GitHub Actions CI/CD tutorial. This guide explains how GitHub Actions works, how to create workflows, run tests, build applications, deploy to servers, and automate DevOps pipelines.

---

# 1. What Is GitHub Actions?

GitHub Actions is an automation and CI/CD platform built into GitHub. It lets you:

* Run automated workflows
* Test and build your applications
* Deploy to cloud providers (AWS, Azure, GCP)
* Lint, scan, and package code
* Automate pull requests and issues

GitHub Actions runs directly inside your GitHub repository using YAML workflow files.

---

# 2. Key Concepts

### **Workflow**

A workflow is an automated process defined in YAML.

### **Jobs**

A workflow contains one or more jobs. Each job runs on a virtual machine.

### **Steps**

Actions inside a job. For example:

* Install dependencies
* Run tests
* Build project

### **Actions**

Reusable automation units.

### **Runners**

Machines that run your jobs.
GitHub provides:

* ubuntu-latest
* windows-latest
* macos-latest

---

# 3. Creating Your First GitHub Actions Workflow

Workflows live in this folder:

```
.github/workflows/
```

Create file:

```
.github/workflows/ci.yml
```

### **Example: Simple CI workflow**

```yaml
name: Simple CI

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

---

# 4. Workflow Triggers

You can trigger workflows using:

### **Events:**

* `push`
* `pull_request`
* `schedule` (CRON)
* `workflow_dispatch` (manual run)
* `release`
* `issue_comment`
* `pull_request_review`

### **Example: Trigger on pull request**

```yaml
on:
  pull_request:
    branches: [ main ]
```

### **Example: Scheduled workflow**

```yaml
on:
  schedule:
    - cron: "0 0 * * *"  # daily at midnight
```

---

# 5. Using Marketplace Actions

GitHub Actions marketplace has thousands of pre-built actions.

Example: Setup Node.js

```yaml
- uses: actions/setup-node@v3
  with:
    node-version: 18
```

Example: Upload artifact

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: results/
```

---

# 6. Building a Python Project with CI

Complete Python testing + linting pipeline:

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8

      - name: Lint
        run: flake8 .

      - name: Run tests
        run: pytest --maxfail=1 --disable-warnings
```

---

# 7. Building a Node.js Project

```yaml
name: Node CI
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - run: npm install
      - run: npm test
```

---

# 8. Environment Variables & Secrets

### **Environment variables**

```yaml
env:
  APP_ENV: production
```

### **Secrets**

Store under: Repository → Settings → Secrets

Use secret:

```yaml
- name: Use secret
  run: echo "Secret is ${{ secrets.MY_SECRET }}"
```

---

# 9. Deploying with GitHub Actions

Below are real deployment examples.

---

# 9.1 Deploy to AWS EC2 (SSH)

```yaml
name: Deploy to EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy via SSH
      uses: appleboy/ssh-action@v0.1.10
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.EC2_KEY }}
        script: |
          cd /var/www/myapp
          git pull
          systemctl restart myapp.service
```

---

# 9.2 Deploy to AWS S3 (Static Website)

```yaml
- uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_KEY }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET }}
    aws-region: us-east-1

- run: aws s3 sync . s3://mybucket --delete
```

---

# 9.3 Deploy to Docker Hub

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKER_USER }}
    password: ${{ secrets.DOCKER_PASS }}

- name: Build and push image
  run: |
    docker build -t myuser/myimage:latest .
    docker push myuser/myimage:latest
```

---

# 10. Matrix Builds

Run tests on multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10]
```

---

# 11. Caching Dependencies

Speeds up workflows.

Example: Python cache

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

Example: Node.js cache

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
```

---

# 12. Reusable Workflows

You can reuse workflows across repositories.

In `.github/workflows/build.yml`:

```yaml
name: Build
on:
  workflow_call:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "Reusable build job"
```

Call it from another workflow:

```yaml
jobs:
  call-workflow:
    uses: org/repo/.github/workflows/build.yml@main
```

---

# 13. Workflow Artifacts

Save test reports, build outputs.

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: report
    path: path/to/report.xml
```

Download artifacts:

```yaml
- uses: actions/download-artifact@v3
```

---

# 14. Manual Trigger (workflow_dispatch)

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options:
          - dev
          - prod
```

---

# 15. Advanced Example: Full CI/CD Pipeline

This pipeline:

* Runs tests
* Builds Docker image
* Pushes to Docker Hub
* Deploys to EC2

```yaml
name: Full CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - run: pytest

      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASS }}

      - run: |
          docker build -t myuser/myapp:latest .
          docker push myuser/myapp:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            docker pull myuser/myapp:latest
            docker stop app || true
            docker rm app || true
            docker run -d --name app -p 80:80 myuser/myapp:latest
```

---

# 16. Summary

You learned:

* How GitHub Actions works
* How to create workflows, jobs, steps
* How to test, build, and deploy apps
* How to use secrets, caching, matrices, and reusable workflows
* Real CI/CD examples for AWS, Docker, and static websites

If you'd like, I can also create:

* GitHub Actions cheat sheet
* CI/CD pipeline for Python, Node, Java, or Docker
* A full DevOps roadmap guide
* GitHub Actions interview questions
Below are **GitHub Actions interview questions (with detailed answers)** and a **complete GitHub Actions cheat sheet** — both written in clean, professional English.

---

# ✅ **1. GitHub Actions Interview Questions (With Answers)**

These cover **beginner → senior** levels.

---

## **Q1. What is GitHub Actions?**

**Answer:**
GitHub Actions is a CI/CD automation platform built into GitHub.
It allows you to create workflows that automatically build, test, and deploy your code.

---

## **Q2. What is a Workflow in GitHub Actions?**

A **workflow** is an automated procedure defined using YAML inside `.github/workflows`.

It contains:

* Triggers (events)
* Jobs
* Steps
* Actions

---

## **Q3. Where do GitHub workflow files live?**

Inside the repository:

```
.github/workflows/
```

Each `.yml` file represents a workflow.

---

## **Q4. What is a Runner?**

A machine that executes the job.

Types:

* **GitHub-hosted runners** (ubuntu, windows, macOS)
* **Self-hosted runners** (your own server)

---

## **Q5. What triggers a workflow?**

Workflows can be triggered by events:

* push
* pull_request
* workflow_dispatch (manual)
* schedule (CRON)
* release
* issues
* repository_dispatch

Example:

```yaml
on: [push, pull_request]
```

---

## **Q6. What is the difference between Jobs and Steps?**

* **Job**: A collection of steps executed on a runner
* **Step**: A single task inside a job (install, build, test, deploy)

---

## **Q7. How do you pass environment variables?**

Globally:

```yaml
env:
  ENV: production
```

Inside a step:

```yaml
run: echo $ENV
```

From secrets:

```yaml
${{ secrets.MY_SECRET }}
```

---

## **Q8. What are GitHub Secrets?**

Encrypted values stored in:

**Settings → Secrets → Actions**

Used for:

* API keys
* Passwords
* Server SSH keys
* Cloud credentials

---

## **Q9. What is caching in GitHub Actions?**

Speeds up workflows by caching dependencies.

Example for Python:

```yaml
uses: actions/cache@v3
with:
  path: ~/.cache/pip
  key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

## **Q10. How do you create a matrix build?**

```yaml
strategy:
  matrix:
    python: [3.8, 3.9, 3.10]
```

---

## **Q11. What is a reusable workflow?**

A workflow that can be called by other workflows.

In reusable workflow:

```yaml
on:
  workflow_call:
```

Call it:

```yaml
jobs:
  call:
    uses: org/repo/.github/workflows/build.yml@main
```

---

## **Q12. What is an artifact?**

A file or folder uploaded after workflow execution.

Upload example:

```yaml
uses: actions/upload-artifact@v3
with:
  name: report
  path: results/
```

---

## **Q13. How do you deploy to AWS/GCP/Azure using GitHub Actions?**

Using cloud provider CLI or dedicated marketplace actions:

Example (AWS):

```yaml
uses: aws-actions/configure-aws-credentials@v2
```

---

## **Q14. What is the difference between `uses:` and `run:`?**

* `uses:` executes pre-made actions (like setup-python)
* `run:` executes shell commands

Example:

```yaml
uses: actions/checkout@v3
run: npm install
```

---

## **Q15. What are some common GitHub-hosted runner images?**

* ubuntu-latest
* windows-latest
* macos-latest

---

## **Q16. What is concurrency in GitHub Actions?**

It prevents multiple runs from executing simultaneously.

```yaml
concurrency: ci-pipeline
```

---

## **Q17. How do you handle dependent jobs?**

Using `needs:`:

```yaml
jobs:
  build:
  test:
    needs: build
```

---

## **Q18. How do you manually trigger a workflow?**

```yaml
on:
  workflow_dispatch:
```

---

## **Q19. How do you deploy a Docker container using GitHub Actions?**

```yaml
docker build -t myapp .
docker push myapp
```

Or via marketplace actions.

---

## **Q20. How do you secure GitHub Actions pipelines?**

* Use secrets
* Avoid printing secrets
* Use least privilege cloud credentials
* Verify actions via hash or pinned versions
* Restrict permissions (permissions: read-all)

---

If you want, I can add **senior-level architecture interview questions** too.

---

# ✅ **2. GitHub Actions Cheat Sheet (Quick Reference)**

This is a compact, practical cheat sheet for daily use.

---

# **📁 Folder Structure**

Workflow files go inside:

```
.github/workflows/
```

---

# **📌 Basic Workflow Template**

```yaml
name: CI

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - run: echo "Hello CI"
```

---

# **🟦 Common Triggers**

```yaml
on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * *"
```

---

# **🟧 Runner Types**

```
ubuntu-latest
windows-latest
macos-latest
self-hosted
```

---

# **📦 Built-in Marketplace Actions**

### Checkout repo

```yaml
uses: actions/checkout@v3
```

### Setup Python

```yaml
uses: actions/setup-python@v4
with:
  python-version: '3.10'
```

### Setup Node

```yaml
uses: actions/setup-node@v3
```

---

# **🔑 Using Secrets**

```yaml
env:
  DB_PASS: ${{ secrets.DB_PASS }}
```

---

# **🧪 Test Example (Python)**

```yaml
- name: Run tests
  run: pytest
```

---

# **📌 Install Dependencies**

Python:

```yaml
- run: pip install -r requirements.txt
```

Node.js:

```yaml
- run: npm install
```

---

# **🔄 Matrix Build**

```yaml
strategy:
  matrix:
    python: [3.8, 3.9, 3.10]
```

---

# **🚀 Deploy to EC2**

```yaml
- uses: appleboy/ssh-action@v0.1.10
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ubuntu
    key: ${{ secrets.EC2_KEY }}
    script: |
      git pull
      systemctl restart app
```

---

# **🐳 Docker Build & Push**

```yaml
- name: Login
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.USER }}
    password: ${{ secrets.PASS }}

- run: |
    docker build -t myapp .
    docker push myapp
```

---

# **💨 Caching Dependencies**

```yaml
uses: actions/cache@v3
with:
  path: ~/.cache/pip
  key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

# **📥 Upload Artifacts**

```yaml
uses: actions/upload-artifact@v3
with:
  name: reports
  path: reports/
```

---

# **📤 Download Artifacts**

```yaml
uses: actions/download-artifact@v3
```

---

# **♻ Reusable Workflow**

Workflow:

```yaml
on:
  workflow_call:
```

Call it:

```yaml
jobs:
  call:
    uses: org/repo/.github/workflows/ci.yml@main
```

---

# **🚦 Job Dependencies**

```yaml
jobs:
  test:
    needs: build
```

---

# **⛔ Limit Concurrency**

```yaml
concurrency: deploy-production
```

---

# **🧹 Cancel Previous Workflow Runs**

```yaml
concurrency:
  group: ci
  cancel-in-progress: true
```

---

# 🎉 You're all set!

If you want, I can also generate:

✅ GitHub Actions CI/CD Roadmap
✅ Real DevOps project using GitHub Actions (Docker + AWS + DB)
✅ GitHub Actions deployment for Django, Flask, React, Node, FastAPI
Just tell me!
Absolutely! Here's a **complete and professional DevOps learning package** covering:

# ✅ 1. GitHub Actions CI/CD Roadmap

# ✅ 2. Real DevOps CI/CD Project (Docker + AWS + Database)

# ✅ 3. GitHub Actions Deployment Pipelines for Django & Flask

Everything is written in **clear English, step-by-step, and suitable for job preparation or real production work**.

---

# 🌟 **1. GitHub Actions CI/CD Roadmap (From Beginner → Advanced DevOps)**

This roadmap will take you from beginner to advanced GitHub Actions and DevOps engineering.

---

## **📌 Phase 1 — Foundations (Beginner)**

### ✔ Learn GitHub Basics

* Git commits, branches, merges
* Pull Requests
* Issues & discussions
* Git workflows (GitFlow, trunk-based)

### ✔ Understand YAML

* Key-value
* Indentation rules
* Lists and dictionaries
* Anchors & references

### ✔ Learn GitHub Actions Basics

* What is a workflow?
* Jobs, steps, runners
* Events (push, PR, schedule, dispatch)

Practice:

* Create `.github/workflows/hello.yml`
* Add basic echo commands
* Trigger on push

---

## **📌 Phase 2 — Intermediate Level**

### ✔ Use Marketplace Actions

Learn to use built-in actions:

* `actions/checkout`
* `actions/setup-python`
* `actions/setup-node`
* `docker/login-action`

### ✔ Use workflow caching

* Speed up builds
* Cache pip, npm, Docker layers

### ✔ Create CI pipelines

Practice:

* Linting
* Unit testing
* Type checking

---

## **📌 Phase 3 — CI/CD Concepts**

### ✔ Build artifacts

* Test reports
* Build files
* Docker images

### ✔ Upload artifacts

* From CI to store results

### ✔ Matrix builds

Run multiple versions of:

* Python
* Node
* Operating systems

---

## **📌 Phase 4 — Advanced DevOps**

### ✔ Secrets & environment management

* Repository secrets
* Environment-level secrets
* OpenID Connect (OIDC) for AWS & Azure

### ✔ Deployments

Deploy using GitHub Actions to:

* AWS EC2
* AWS ECS
* AWS S3
* GCP
* Azure
* DigitalOcean
* Kubernetes (EKS, AKS, GKE)

---

## **📌 Phase 5 — Production-Level CI/CD**

### ✔ Advanced workflows

* Reusable workflows
* Composite actions
* Monorepo pipelines

### ✔ Security

* Least-privilege permissions
* Code scanning (Dependabot, SAST)
* Hash-pinned actions
* Concurrency control

### ✔ Monitoring & Observability

* GitHub Actions logs
* Deployment status
* Slack notifications

---

# 🌟 **2. Real DevOps Project Using GitHub Actions (Docker + AWS + DB)**

Here is a **complete real-world CI/CD project architecture**, suitable for interviews AND real production work.

---

# 🚀 **Project Overview**

We will build:

* A Python or Node app
* End-to-end CI/CD pipeline
* Docker image build + push
* Deploy to AWS EC2
* PostgreSQL database
* Automated migrations
* Auto-scaling infrastructure

---

# 📦 **Technologies Used**

| Component      | Technology            |
| -------------- | --------------------- |
| CI/CD          | GitHub Actions        |
| Container      | Docker                |
| Hosting        | AWS EC2               |
| Database       | PostgreSQL            |
| Secrets        | GitHub Secrets        |
| Infrastructure | Terraform (optional)  |
| Monitoring     | CloudWatch (optional) |

---

# 🏗 Step A: CI Pipeline

Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
```

---

# 🏗 Step B: Build Docker Image & Push to Docker Hub / ECR

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASS }}

      - name: Build & push image
        run: |
          docker build -t myuser/myapp:latest .
          docker push myuser/myapp:latest
```

---

# 🏗 Step C: Deploy to AWS EC2 (SSH)

```yaml
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            docker pull myuser/myapp:latest
            docker stop app || true
            docker rm app || true
            docker run -d --name app -p 80:80 myuser/myapp:latest
```

---

# 🗂 Database Integration (PostgreSQL)

### Environment variables stored in GitHub Secrets:

```
DB_HOST
DB_USER
DB_PASS
DB_NAME
```

### Pass to Docker container:

```bash
docker run -d \
  -e DB_HOST=${{ secrets.DB_HOST }} \
  -e DB_USER=${{ secrets.DB_USER }} \
  -e DB_PASS=${{ secrets.DB_PASS }} \
  -e DB_NAME=${{ secrets.DB_NAME }} \
  myuser/myapp:latest
```

---

# 🌟 **3. GitHub Actions Deployment for Django & Flask**

Below are ready-to-use CI/CD pipelines for **Django** and **Flask**.

---

# 🔶 **Django Deployment using GitHub Actions (Docker + AWS)**

### Folder structure example:

```
project/
  manage.py
  requirements.txt
  Dockerfile
  app/
```

---

# 🧪 Step 1: CI (Test Django)

```yaml
name: Django CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - run: pip install -r requirements.txt
      - run: python manage.py test
```

---

# 🐳 Step 2: Docker build for Django

**Dockerfile example:**

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

# 🚀 Step 3: Deploy Django to EC2

```yaml
jobs:
  deploy:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            docker pull myuser/django-app:latest
            docker stop django || true
            docker rm django || true
            docker run -d -p 8000:8000 myuser/django-app:latest
```

---

# 🔷 **Flask Deployment (GitHub Actions + Docker + AWS)**

### CI Test Pipeline

```yaml
name: Flask CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      
      - run: pip install -r requirements.txt
      - run: pytest
```

---

### Dockerfile for Flask

```dockerfile
FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

---

### Deployment Pipeline: GitHub → Docker Hub → EC2

```yaml
jobs:
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASS }}

      - run: |
          docker build -t myuser/flask-app:latest .
          docker push myuser/flask-app:latest

      - uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            docker pull myuser/flask-app:latest
            docker stop flask || true
            docker rm flask || true
            docker run -d -p 5000:5000 myuser/flask-app:latest
```

---

# 🎉 You're done!

You now have:

### ✔ Full GitHub Actions CI/CD Roadmap

### ✔ Real DevOps project (Docker + AWS + DB)

### ✔ Complete Django and Flask CI/CD pipelines

If you want, I can also create:

🔥 Kubernetes Deployment (GitOps with GitHub Actions)
🔥 Terraform IaC pipeline with GitHub Actions
🔥 CI/CD pipeline for FastAPI or React
🔥 A complete DevOps résumé based on these skills

Just tell me!
