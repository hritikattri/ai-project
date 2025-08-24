# Project details

### 1. Upload a file to S3.

### 2. Creating Aurora Cluster

- We need Postgres DB engine because it supports the extensions required to use Aurora as a vector store. A vector store is a store for high-dimensional storage and retrieval (eg: embedding vectors).

### 3. Configure RDS cluster for storing Bedrock Knowledge Base

- Create table for embeddings:
- For the user created, add its credential as a secret in AWS Secret Manager (Type: "Credentials for Amazon RDS database")

### 4. Create the Amazon Bedrock Knowledge Base 

TODO: Adding steps here for reference
