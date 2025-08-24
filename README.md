# Project details

Build a Bedrock Agent that can answer user questions based on some input document (here: smartphone user manual). For this, we will use Bedrock Knowledge Base using Amazon Aurora as the vector store and Amazon’s Titan Text Embeddings model for document processing. The agent, powered by Amazon’s Nova Micro model, will depend on this knowledge base to generate answers.

<img width="1888" height="1004" alt="image" src="https://github.com/user-attachments/assets/01ea3b6b-5d89-4216-943d-f39159a8dd09" />

### 1. Upload a file to S3.

### 2. Creating Aurora Cluster

- We need Postgres DB engine because it supports the extensions required to use Aurora as a vector store. A vector store is a store for high-dimensional storage and retrieval (eg: embedding vectors).

Details about creating Aurora cluster:
- "Templates" has 2 values - Production, Dev/Test. Choose Dev/Test.
- Under "Settings" -> "DB cluster identifier" -> Set Aurora cluster name/identifier (will setup endpoint based on this).
- Under "Settings" -> "Credentials Mgmt" -> Choose store password in AWS Secret Manager.
- Under "Instance Configuration" -> "DB Instance Class" -> Choose "Serverless V2". (scales up/down, manages resources efficiently).
  - Serverless V2
  - Memory optimized (r class)
  - Burstable class (t class)
- Set scaling range of DB (Min, Max ACU). Note - 1 ACU (Aurora Capacity Unit) - 2 GiB.
- Set DB name under "Additional configuration" -> "Initial DB name".
- Wait for the cluster and all of its instances (Reader(s), Writer) to become "Available" status.

### 3. Configure RDS cluster for storing Bedrock Knowledge Base


Create table for embeddings:

```sql
-- Create table for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA bedrock_integration;
CREATE TABLE bedrock_integration.bedrock_kb (
    id UUID PRIMARY KEY,
    embedding VECTOR(256),
    chunks TEXT,
    metadata JSON
);


-- Create a text search index in Postgres on "chunks" column using GIN (Generalized Inverted Index), which enables text search capability
CREATE INDEX ON bedrock_integration.bedrock_kb USING gin (to_tsvector('simple', chunks));

-- Create a index on embedding column using HNSW (Hierarchical Navigable Small World) algorithm, which optimizes high-dimensional similarity search
CREATE INDEX ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops) WITH (ef_construction=256);

-- Create user and access for these tables
CREATE ROLE bedrock_user WITH PASSWORD 'bedrock_user' LOGIN;
GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;
ALTER TABLE bedrock_integration.bedrock_kb OWNER TO bedrock_user;

```


- For the user created, add its credential as a secret in AWS Secret Manager (Type: "Credentials for Amazon RDS database")

### 4. Create the Amazon Bedrock Knowledge Base 


**Procure embedding built-in models from AWS:**
  - Amazon Bedrock" -> "Bedrock Configurations" -> "Model access" -> "Enable specific models" -> Enable if access status if available: 
    - `Nova Micro` - Good for high-volume text processing at low cost
    - `Titan Text Embeddings V2`: Produces embeddings which capture semantic meaning of sentence, helpful for text classification, similarity searching, etc.

**Create `Knowledge Base`:**
  - "Builder Tools" -> "Knowledge Bases" -> "Create" -> "Knowledge Base with vector store"
    - Create IAM role for Knowledge Base with following accesses:
      - Invoke Bedrock model policy
      - Access to query RDS DB
      - Access for S3 data retrieval
      - Access to securely fetch secrets from AWS Secrets Manager

  - "Configure `Data Source`" -> "S3"
    - Pass s3 bucket name and prefix to file source.
    - "Embedding model" -> Select `Titan Text Embeddings V2`.
    - "Vector dimensions" -> 256 (same as vector attribute length in DB table)
    - "Vector store" -> "Use existing" -> Select RDS Aurora DB and provide table. Map individual fields to correct attributes of table.
  
  - Create Knowledge Base. Select -> "Data Source" -> `Sync`.

**Create `Bedrock Agent` and `Bedrock Guardrails`**: 
  - Bedrock Agent: Responsible for responding to user queries by using knowledge base through ML models, leveraging RAG
  - Bedrock Guardrails: Responsible for sanitizing output if input is one of unallowed category
  - "Agents" -> "Select model" -> "Nova Micro". Attach correct Knowledge base, guardrail. Create alias and store alias ID.

Deploy backend (Lambda + API GW):
  - Update lambda timeout to be 1-2m based on Bedrock response time.
  - Ensure the lambda execution IAM role has `bedrock:InvokeAgent` permission policy to invoke the Bedrock agent.
  - Invoke the Bedrock agent through AWS SDK (Boto3)

Deploy frontend:

```bash
amplify init

# Select Amplify hosting, manual deployment
amplify add hosting
