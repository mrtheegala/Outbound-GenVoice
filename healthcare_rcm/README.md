# Healthcare RCM Intelligence Layer

Production-ready, modular, configuration-driven RCM automation system.

## 🏗️ Architecture

```
healthcare_rcm/
├── config/                      # ZERO HARDCODING - All logic in YAML
│   ├── procedures.yaml          # Procedure definitions
│   ├── denial_codes.yaml        # Denial code mappings
│   └── conversation_templates.yaml  # Conversation flows
├── core/
│   └── analyzers/               # Business logic
│       ├── base_analyzer.py     # Abstract base class
│       └── prior_auth_analyzer.py  # Prior auth intelligence
├── models/                      # Pydantic data models
│   └── prior_auth.py            # Type-safe models
└── utils/                       # Utilities
    └── config_loader.py         # Configuration management
```

## ✨ Key Features

### 1. **Zero Hardcoding**
All business logic lives in YAML configuration files. Add new procedures, denial codes, or conversation flows without touching code.

### 2. **Type Safety**
Pydantic models ensure data validation and type safety throughout the system.

### 3. **Modular Design**
Abstract base classes enforce consistent interfaces. Easy to extend with new use cases.

### 4. **Production Ready**
- Comprehensive logging
- Input validation
- Error handling
- Caching for performance
- Singleton patterns

## 🚀 Quick Start

### Analyze a Prior Authorization Request

```python
from healthcare_rcm.core.analyzers.prior_auth_analyzer import PriorAuthAnalyzer

analyzer = PriorAuthAnalyzer()

# Your request data
request_data = {
    "procedure_code": "72148",
    "diagnosis_code": "M54.5",
    "patient_name": "John Doe",
    "patient_dob": "1975-06-15",
    "member_id": "ABC123456789",
    "provider_name": "Dr. Smith",
    "provider_npi": "1234567890",
    "clinical_notes": "Chronic back pain x 8 weeks, failed PT",
    "urgency_level": "routine"
}

# Analyze
analysis = analyzer.analyze(request_data)

# Results
print(f"Success Probability: {analysis.success_probability:.0%}")
print(f"Documentation Complete: {analysis.documentation_complete}")
print(f"Needs Escalation: {analysis.needs_escalation}")
print(f"Call Strategy: {len(analysis.call_strategy_steps)} steps")
```

## 📝 Adding New Procedures

Edit `config/procedures.yaml`:

```yaml
procedures:
  "12345":  # Your CPT code
    name: "New Procedure"
    category: "surgical_procedure"
    requires_prior_auth: true
    
    documentation_requirements:
      - type: "clinical_notes"
        description: "Clinical documentation"
        mandatory: true
        keywords:
          - "keyword1"
          - "keyword2"
    
    approval_criteria:
      primary: "Medical necessity established"
    
    standard_questions:
      - "What is the medical necessity?"
      - "What documentation is available?"
    
    turnaround_time:
      routine: "3-5 business days"
```

That's it! No code changes needed.

## 🔧 Configuration Files

### procedures.yaml
- Procedure definitions
- Documentation requirements
- Approval criteria
- Standard questions
- Escalation triggers

### denial_codes.yaml
- Denial code mappings
- Resolution strategies
- Success probabilities
- Escalation rules

### conversation_templates.yaml
- Conversation stage definitions
- Escalation protocols
- Success indicators

## 🎯 Design Principles

1. **Configuration over Code**: Business logic in YAML, not Python
2. **Type Safety**: Pydantic models prevent runtime errors
3. **Single Responsibility**: Each class has one job
4. **Open/Closed**: Open for extension, closed for modification
5. **Dependency Injection**: Easy to test and mock

## 📊 Data Flow

```
Input Data
    ↓
Pydantic Model (validation)
    ↓
Analyzer (business logic from YAML)
    ↓
Analysis Result (type-safe output)
    ↓
Agent Configuration
    ↓
Voice AI Agent (existing framework)
```

## 🧪 Testing

```python
# Run analyzer tests
python -m healthcare_rcm.core.analyzers.prior_auth_analyzer

# Run config loader tests
python -m healthcare_rcm.utils.config_loader
```

## 🔮 Next Steps

1. **Add Denial Analyzer** (same pattern as prior auth)
2. **Add Insurance Verification Analyzer**
3. **Create Orchestrator** (routes to correct analyzer)
4. **Integrate with Voice Agent** (existing framework)

## 💡 Why This Architecture?

### For Hackathon:
- ✅ Fast to demo (change YAML, not code)
- ✅ Easy to add scenarios
- ✅ Professional quality
- ✅ Impresses judges

### For Production:
- ✅ Maintainable (business users can edit YAML)
- ✅ Testable (mock config loader)
- ✅ Scalable (add use cases without refactoring)
- ✅ Type-safe (catch errors at development time)

## 📚 Documentation

Each module has comprehensive docstrings. Use Python's help():

```python
from healthcare_rcm.core.analyzers.prior_auth_analyzer import PriorAuthAnalyzer
help(PriorAuthAnalyzer)
```

## 🎓 Learn More

- **Base Analyzer**: Abstract interface for all analyzers
- **Config Loader**: Centralized configuration management with caching
- **Pydantic Models**: Type-safe data structures
- **YAML Configs**: Business logic without code changes
