# Index

1. Details of AWS Bedrock
2. Code Generation using Bedrock model

# 1. Details of AWS Bedrock

Models preferred for tasks (later reference):

| Task | Best model |
| ---- | ---------- |
| Text generation | Amazon Titan, AI21 Jurassic |
| Code generation | Anthropic Claude |
| Image generation | Stability AI Stable Diffusion |
| Sentiment analysis | Amazon Titan |
| Conversational AI |Anthropic Claude, AI21 Jurassic |
| Semantic search | Cohere Command |

- Have used Claude 3 Sonnet for code generation in this project

# 2. Using Bedrock model

- "Bedrock Configurations" -> "Model Access" -> "Claude 3 Sonnet". If "Available to Request" is the status, click "Request model access". Fill form and submit.
- "Bedrock Providers" -> "Anthropic" -> "Claude Sonnet 3" -> Save `modelID`.

***Using AWS SDK for Bedrock code generation***:

- `boto.client('bedrock-runtime')` -> Get Bedrock client from aws sdk.
- `client.converse(modelID, message, inferenceConfig={"maxTokens":4096,"temperature":0.5}, additionalModelRequestFields={"top_k":250})`:
  - `maxTokens` - Maximum number of tokens for model's response (embedding size) - 4096 here.
  - `temperature` - Controls amount of creativity/novelty in the response.
  - `top_k` - Used as a filter to give more priority to specific tokens. (Here, top 250 tokens).
