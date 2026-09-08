# Internship Project 3: S3 to RDS with Glue Fallback

## Overview
This Dockerized Python application reads a CSV file from S3, attempts to push the data to an RDS MySQL database, and automatically falls back to registering the data in AWS Glue Data Catalog if the RDS push fails.

## Files
- `app.py` - Main Python script
- `Dockerfile` - Container definition
- `requirements.txt` - Python dependencies
- `students.csv` - Sample data file

## How to Run

### 1. Build the Docker image
docker build -t s3-rds-glue-app .

### 2. Run (Success case - RDS reachable)
docker run --rm -e AWS_ACCESS_KEY_ID=xxx -e AWS_SECRET_ACCESS_KEY=xxx -e AWS_REGION=us-east-1 -e S3_BUCKET=your-bucket -e S3_KEY=students.csv -e RDS_HOST=your-rds-endpoint -e RDS_USER=admin -e RDS_PASSWORD=xxx -e RDS_DB_NAME=studentdb -e RDS_TABLE_NAME=student_data s3-rds-glue-app

### 3. Run (Fallback case - RDS unreachable)
Same command with wrong RDS_HOST, plus GLUE_DB_NAME, GLUE_TABLE_NAME, GLUE_S3_LOCATION env vars.

## Technologies Used
AWS S3, RDS (MySQL), AWS Glue, Docker, Python (boto3, pandas, sqlalchemy, pymysql)
