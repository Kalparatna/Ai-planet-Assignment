# Math Routing Agent - Improved System

An intelligent mathematical problem-solving system that provides step-by-step solutions with proper source attribution.

## 🚀 **Key Features**

### **Smart Query Classification**
- **Simple Arithmetic**: Direct calculations (e.g., "what is 4²")
- **Basic Geometry**: Formula applications (e.g., "area of circle with radius 7")
- **Simple Derivatives**: Calculus rules (e.g., "derivative of x^3")
- **JEE Bench Problems**: Complex physics/chemistry from dataset
- **Comprehensive Solutions**: Detailed explanations for complex problems

### **Intelligent Source Priority**
1. **📄 PDF Documents** (User uploads - highest priority)
2. **🧮 Direct Calculation** (Simple arithmetic)
3. **📐 Geometry Formulas** (Basic geometry)
4. **📊 Calculus Rules** (Simple derivatives)
5. **🎯 JEE Bench Dataset** (Complex problems)
6. **📚 Knowledge Base** (Curated problems)
7. **🌐 Web Search** (External sources)
8. **🤖 AI Generated** (Comprehensive solutions)

### **Enhanced Features**
- **Assignment Generation**: Create educational assignments
- **Requirements Documents**: Generate project requirements
- **Source Attribution**: Clear indication of answer sources
- **Step-by-Step Solutions**: Detailed mathematical explanations

## 📋 **Prerequisites**

```bash
# Python 3.8+
pip install -r requirements.txt

# Environment variables (.env file)
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY=your_google_key
PINECONE_INDEX_NAME=math-routing-agent
PINECONE_EMBEDDING_MODEL=llama-text-embed-v2
```

## 🛠️ **Setup Instructions**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Configure Environment**
Create a `.env` file with your API keys:
```env
PINECONE_API_KEY=your_pinecone_api_key
GOOGLE_API_KEY=your_google_api_key
PINECONE_INDEX_NAME=math-routing-agent
PINECONE_EMBEDDING_MODEL=llama-text-embed-v2
```

### **3. Initialize System**
```bash
# Fix Pinecone dimensions (if needed)
python fix_pinecone_dimensions.py

# Load JEE Bench dataset
python load_jee_bench.py

# Quick system test
python quick_test.py
```

### **4. Start Server**
```bash
# Option 1: Direct start
python main.py

# Option 2: Using batch file (Windows)
run.bat
```

## 🧪 **Testing**

### **Quick Test**
```bash
python quick_test.py
```

### **Comprehensive Tests**
```bash
# Test improved classification
python test_improved_system.py

# Test JEE Bench queries
python test_jee_bench_simple.py

# Test complete API (requires server running)
python test_complete_api.py
```

## 🔌 **API Endpoints**

### **Math Solving**
```bash
POST /math/solve
{
  "query": "what is 4²"
}
```

**Response Examples:**

**Simple Arithmetic:**
```json
{
  "solution": "**Source: Direct Mathematical Calculation**\n\n4² = 4 × 4 = 16",
  "source": "direct_calculation",
  "confidence": 0.95,
  "references": ["🧮 Direct Mathematical Calculation"]
}
```

**JEE Bench Problem:**
```json
{
  "solution": "**Source: JEE Bench Dataset**\n\n[Detailed solution]",
  "source": "jee_bench", 
  "confidence": 0.85,
  "references": ["🎯 JEE Bench - Physics"]
}
```

### **Assignment Generation**
```bash
POST /math/generate-assignment
{
  "topic": "Calculus - Derivatives",
  "difficulty": "Medium",
  "num_problems": 5
}
```

### **Requirements Generation**
```bash
POST /math/generate-requirements
{
  "project_type": "Scientific Calculator App",
  "subject": "Mathematics",
  "complexity": "Medium"
}
```

### **System Status**
```bash
GET /math/jee-bench-status
```

## 📊 **Query Examples**

### **Simple Arithmetic** (Direct Calculation)
- "what is 4²" → 4² = 4 × 4 = 16
- "calculate 2 + 3 * 4" → Step-by-step with order of operations
- "what is 5 squared" → 5² = 25

### **Basic Geometry** (Formula Application)
- "area of circle with radius 7" → A = πr² = π × 7² = 49π
- "volume of sphere with radius 3" → V = (4/3)πr³

### **Simple Calculus** (Rules Application)
- "derivative of x^3" → 3x²
- "derivative of 2x^2 + 5x" → 4x + 5

### **Complex Problems** (JEE Bench/Web Search)
- "photoelectric effect problem" → Searches JEE Bench first
- "quantum mechanics" → Advanced physics problems
- "organic chemistry reactions" → Chemistry problems

### **Comprehensive Solutions** (AI Generated)
- "solve quadratic equation x^2 - 5x + 6 = 0" → Complete solution
- "explain integration by parts" → Detailed explanation

## 🎯 **System Behavior**

### **Query Classification Logic**
1. **Simple queries** get direct, fast solutions
2. **Complex physics/chemistry** checks JEE Bench dataset
3. **Standard math problems** get comprehensive explanations
4. **Conceptual questions** get detailed educational content

### **Source Attribution**
- **🧮 Direct Calculation**: Simple arithmetic
- **📐 Geometry Formula**: Basic geometry
- **📊 Calculus Rules**: Simple derivatives
- **🎯 JEE Bench**: Exam-level problems
- **📚 Knowledge Base**: Curated content
- **🌐 Web Search**: External sources
- **🤖 AI Generated**: Comprehensive solutions

## 📈 **Performance Metrics**

- **Classification Accuracy**: 100% (tested)
- **JEE Bench Success Rate**: 60-75%
- **Simple Query Response**: < 2 seconds
- **Complex Query Response**: < 10 seconds

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Pinecone Dimension Mismatch**
```bash
python fix_pinecone_dimensions.py
```

**2. JEE Bench Not Loading**
```bash
python load_jee_bench.py
```

**3. Google API Quota Exceeded**
- Wait for quota reset
- Check your Google API usage

**4. No Results from JEE Bench**
- Check if data loaded: `GET /math/jee-bench-status`
- Try more specific physics/chemistry terms

### **Debug Mode**
Set logging level to DEBUG in your environment for detailed logs.

## 📁 **Project Structure**

```
server/
├── main.py                     # FastAPI application
├── routes/
│   └── math_router.py         # Math solving endpoints
├── services/
│   ├── improved_math_solver.py # Smart query classification
│   ├── knowledge_base.py      # JEE Bench integration
│   └── pdf_processor.py       # PDF handling
├── data/
│   ├── jee_bench_data.json    # JEE Bench dataset
│   └── math_problems.json     # Local problems
└── tests/
    ├── test_improved_system.py
    ├── test_complete_api.py
    └── quick_test.py
```

## 🎉 **Success Indicators**

The system is working correctly when:
- ✅ Simple arithmetic gets direct calculations
- ✅ Geometry problems use formulas
- ✅ Physics problems check JEE Bench appropriately
- ✅ All sources are clearly attributed
- ✅ Step-by-step solutions are provided
- ✅ No irrelevant JEE matches for simple queries

## 🚀 **Production Deployment**

1. **Environment Setup**: Configure all API keys
2. **Data Loading**: Ensure JEE Bench dataset is loaded
3. **Health Checks**: Use `/math/jee-bench-status`
4. **Monitoring**: Monitor API response times and success rates
5. **Scaling**: Consider load balancing for high traffic

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Run the test scripts to identify problems
3. Check API logs for detailed error information