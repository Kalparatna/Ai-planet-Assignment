# Pinecone Integration Setup Guide

This guide will help you migrate from the previous embedding model to Pinecone embeddings for the Math Routing Agent.

## Prerequisites

1. **Pinecone Account**: Sign up at [pinecone.io](https://pinecone.io)
2. **API Key**: Get your Pinecone API key from the dashboard
3. **Python Environment**: Ensure you have Python 3.8+ installed

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

The key new packages for Pinecone integration are:
- `pinecone-client==3.0.0`
- `langchain-pinecone==0.1.0`

### 2. Environment Configuration

Update your `.env` file with Pinecone configuration:

```env
# Existing keys
GOOGLE_API_KEY="your_google_api_key"
TAVILY_API_KEY="your_tavily_api_key"

# Pinecone Configuration
PINECONE_API_KEY="your_pinecone_api_key"
PINECONE_INDEX_NAME="math-routing-agent"
PINECONE_ENVIRONMENT="us-east-1"
PINECONE_CLOUD="aws"
PINECONE_EMBEDDING_MODEL="llama-text-embed-v2"
```

### 3. Automated Setup

Run the setup script to automatically configure everything:

```bash
python setup_pinecone.py
```

This script will:
- ✅ Check if all required packages are installed
- ✅ Verify environment variables are set
- ✅ Test Pinecone connection
- ✅ Create sample data file
- ✅ Set up Pinecone index
- ✅ Load initial data to Pinecone

### 4. Manual Setup (Alternative)

If you prefer manual setup:

#### Step 1: Test Pinecone Connection
```bash
python test_pinecone.py
```

#### Step 2: Load Sample Data
```bash
python load_sample_data.py
```

## Key Changes Made

### 1. Updated Dependencies
- Added `pinecone-client` and `langchain-pinecone` to `requirements.txt`

### 2. Modified Knowledge Base Service
- Replaced `Chroma` with `PineconeVectorStore`
- Updated initialization to use Pinecone index
- Maintained same API interface for seamless integration

### 3. Updated Data Loading
- Modified `load_sample_data.py` to use Pinecone instead of Chroma
- Added automatic index creation with proper configuration

### 4. Environment Configuration
- Added Pinecone-specific environment variables
- Updated `.env.example` with new configuration

## Configuration Details

### Pinecone Index Settings
- **Dimension**: 384 (for sentence-transformers/all-MiniLM-L6-v2)
- **Metric**: cosine
- **Cloud**: AWS (configurable)
- **Region**: us-east-1 (configurable)

### Embedding Model
The system uses `sentence-transformers/all-MiniLM-L6-v2` for local embeddings, which are then stored in Pinecone. This provides:
- Fast local embedding generation
- Scalable cloud vector storage
- High-performance similarity search

## Usage

### Starting the Server
```bash
python main.py
```

### Testing the API
```bash
curl -X POST "http://localhost:8000/math/solve" \
  -H "Content-Type: application/json" \
  -d '{"query": "Solve x^2 - 5x + 6 = 0"}'
```

### Adding New Problems
The system automatically adds new problems to Pinecone when they're processed and validated.

## Troubleshooting

### Common Issues

1. **"Index not found" error**
   - Run `python setup_pinecone.py` to create the index
   - Check your `PINECONE_INDEX_NAME` in `.env`

2. **Authentication errors**
   - Verify your `PINECONE_API_KEY` is correct
   - Check if your Pinecone account is active

3. **Dimension mismatch**
   - Ensure you're using the correct embedding model
   - Delete and recreate the index if needed

4. **Connection timeout**
   - Check your internet connection
   - Verify the `PINECONE_ENVIRONMENT` setting

### Monitoring

Check your Pinecone dashboard to monitor:
- Index usage and performance
- Vector count and storage
- Query performance metrics

## Migration from Chroma

If you were previously using Chroma:

1. **Backup existing data** (if needed):
   ```bash
   # Your existing Chroma data is in data/chroma_db/
   cp -r data/chroma_db data/chroma_db_backup
   ```

2. **Run the setup script**:
   ```bash
   python setup_pinecone.py
   ```

3. **Test the new system**:
   ```bash
   python test_pinecone.py
   python main.py
   ```

The migration is seamless - your API endpoints remain the same!

## Performance Benefits

Pinecone offers several advantages over local vector storage:

- **Scalability**: Handle millions of vectors
- **Performance**: Sub-100ms query latency
- **Reliability**: Managed infrastructure with high availability
- **Features**: Advanced filtering, metadata search, and analytics

## Support

For issues specific to this integration:
1. Check the troubleshooting section above
2. Review Pinecone documentation: [docs.pinecone.io](https://docs.pinecone.io)
3. Ensure all environment variables are correctly set

## Next Steps

After successful setup:
1. Add more mathematical problems to your knowledge base
2. Customize the embedding model if needed
3. Implement advanced filtering using Pinecone metadata
4. Monitor performance through Pinecone dashboard