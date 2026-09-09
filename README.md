# Internship Project 3: Data Ingestion from S3 to RDS with Fallback to AWS Glue

## 📌 Objective
This project implements a Dockerized Python application that automates data ingestion:
- Reads a CSV file from an Amazon S3 bucket
- Pushes the data to an RDS (MySQL-compatible) database
- Automatically falls back to AWS Glue Data Catalog if the RDS push fails

## 🏗️ Architecture / Data Flow

S3 Bucket (CSV file)
      |
      v
Python Script (boto3 + pandas)
      |
      v
Try: Push to RDS MySQL ---- Success ----> Data stored in RDS table
      |
      v (on failure)
Fallback: Register dataset in AWS Glue Data Catalog
      |
      v
Glue Table created, pointing to S3 location

## 🛠️ Tools & Services Used
- AWS S3 – storage for source CSV file
- AWS RDS (MySQL) – primary database target
- AWS Glue Data Catalog – fallback data registry
- AWS IAM – access control and credentials
- Docker – containerization of the Python application
- Python Libraries – boto3, pandas, SQLAlchemy, PyMySQL

## 📁 Repository Structure
- app.py -- Main Python script (S3 to RDS to Glue fallback logic)
- Dockerfile -- Docker image definition
- requirements.txt -- Python dependencies
- students.csv -- Sample dataset uploaded to S3
- README.md -- Project documentation
- screenshots/ -- Proof of execution and configuration

## ⚙️ Setup & Execution

### 1. Upload sample data to S3
aws s3 cp students.csv s3://your-bucket-name/students.csv

### 2. Create RDS database and table
CREATE DATABASE studentdb;
USE studentdb;
CREATE TABLE student_data (
    col1 VARCHAR(50),
    col2 VARCHAR(100)
);

### 3. Build the Docker image
docker build -t s3-rds-glue-app .

### 4. Run container — Success case (RDS reachable)
docker run --rm -e AWS_ACCESS_KEY_ID="<your-access-key>" -e AWS_SECRET_ACCESS_KEY="<your-secret-key>" -e AWS_REGION="us-east-1" -e S3_BUCKET="<your-bucket-name>" -e S3_KEY="students.csv" -e RDS_HOST="<your-rds-endpoint>" -e RDS_PORT="3306" -e RDS_USER="admin" -e RDS_PASSWORD="<your-rds-password>" -e RDS_DB_NAME="studentdb" -e RDS_TABLE_NAME="student_data" s3-rds-glue-app

### 5. Run container — Fallback case (RDS unreachable)
docker run --rm -e AWS_ACCESS_KEY_ID="<your-access-key>" -e AWS_SECRET_ACCESS_KEY="<your-secret-key>" -e AWS_REGION="us-east-1" -e S3_BUCKET="<your-bucket-name>" -e S3_KEY="students.csv" -e RDS_HOST="wrong-endpoint.rds.amazonaws.com" -e RDS_PORT="3306" -e RDS_USER="admin" -e RDS_PASSWORD="<your-rds-password>" -e RDS_DB_NAME="studentdb" -e GLUE_DB_NAME="fallback_db" -e GLUE_TABLE_NAME="fallback_table" -e GLUE_S3_LOCATION="s3://<your-bucket-name>/data/" s3-rds-glue-app

## 📸 Screenshots
All proof screenshots (RDS setup, MySQL data verification, Docker success/fallback logs, AWS Glue Catalog table, S3 bucket, IAM permissions, and GitHub repository) are available in the /screenshots folder of this repository.

## 🧩 Challenges Faced & Solutions

1. RDS connection timeout from local machine
   - Issue: Publicly accessible was set to No, and the Security Group did not allow inbound traffic from the local IP.
   - Fix: Enabled public accessibility and added an inbound rule for MySQL/Aurora (port 3306) with the correct source IP.

2. Docker Desktop engine not starting on Windows
   - Issue: WSL 2 was not installed, causing the Docker daemon to fail.
   - Fix: Installed WSL 2 (wsl --install), restarted the system, and Docker Desktop started successfully.

3. S3 NoSuchKey error
   - Issue: The script was looking for the file at data/students.csv, but the file was actually located at the bucket root.
   - Fix: Corrected the S3_KEY environment variable to match the actual object key in S3.

4. Simulating RDS failure for Glue fallback
   - Issue: Needed a controlled way to trigger the fallback logic.
   - Fix: Passed an intentionally incorrect RDS_HOST value to force a connection failure and trigger the Glue fallback path.

## ✅ Outcome
- Successfully inserted records into RDS under normal conditions.
- Successfully triggered and verified AWS Glue Data Catalog fallback when RDS was unreachable.
- Fully containerized using Docker for portability and reproducibility.

## 👤 Author
Lokesh Dharasange — Internship Project 3
