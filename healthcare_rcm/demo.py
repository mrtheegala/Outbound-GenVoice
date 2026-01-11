"""
Demo Script - Shows Production-Ready Architecture
Run this to see the system in action!
"""

import logging
from datetime import date
from healthcare_rcm import PriorAuthAnalyzer, PriorAuthRequest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def demo_prior_auth_analysis():
    """Demonstrate prior authorization analysis"""
    
    print_section("PRIOR AUTHORIZATION ANALYSIS DEMO")
    
    # Initialize analyzer (loads all config from YAML)
    print("\n📋 Initializing analyzer...")
    analyzer = PriorAuthAnalyzer()
    print("✓ Analyzer ready (all config loaded from YAML)")
    
    # Test Case 1: MRI with complete documentation
    print_section("Test Case 1: MRI Lumbar Spine - Complete Documentation")
    
    request_data_1 = {
        "procedure_code": "72148",
        "diagnosis_code": "M54.5",
        "patient_name": "John Doe",
        "patient_dob": date(1975, 6, 15),
        "member_id": "ABC123456789",
        "provider_name": "Dr. Sarah Smith",
        "provider_npi": "1234567890",
        "clinical_notes": """
            Patient presents with chronic lower back pain for 8 weeks.
            Conservative treatment attempted including:
            - Physical therapy for 6 weeks (failed to improve)
            - NSAIDs (minimal relief)
            - Muscle relaxants (no significant improvement)
            
            Physical examination reveals:
            - Positive straight leg raise test
            - Radicular symptoms present in left leg
            - Decreased sensation in L5 distribution
            
            Duration of symptoms: 8 weeks
            Red flag symptoms ruled out (no bowel/bladder dysfunction)
        """,
        "urgency_level": "routine"
    }
    
    analysis_1 = analyzer.analyze(request_data_1)
    
    print(f"\n📊 Analysis Results:")
    print(f"  Procedure: {analysis_1.request.procedure_name}")
    print(f"  Category: {analysis_1.procedure_category}")
    print(f"  Typical Cost: ${analysis_1.typical_cost:,.2f}" if analysis_1.typical_cost else "  Typical Cost: N/A")
    
    print(f"\n📄 Documentation Status:")
    print(f"  Complete: {'✓ YES' if analysis_1.documentation_complete else '✗ NO'}")
    if analysis_1.missing_documentation:
        print(f"  Missing: {', '.join(analysis_1.missing_documentation)}")
    else:
        print(f"  All required documentation present")
    
    print(f"\n✅ Approval Criteria:")
    print(f"  Criteria Met: {'✓ YES' if analysis_1.criteria_met else '✗ NO'}")
    print(f"  Primary Criterion: {analysis_1.approval_criteria.get('primary', 'N/A')}")
    
    print(f"\n🎯 Success Prediction:")
    print(f"  Probability: {analysis_1.success_probability:.0%}")
    print(f"  Expected Turnaround: {analysis_1.expected_turnaround_time}")
    
    print(f"\n⚠️  Escalation:")
    print(f"  Needs Escalation: {'YES' if analysis_1.needs_escalation else 'NO'}")
    if analysis_1.needs_escalation:
        print(f"  Reason: {analysis_1.escalation_reason}")
        print(f"  Type: {analysis_1.escalation_type}")
    
    print(f"\n❓ Questions to Ask ({len(analysis_1.questions_to_ask)}):")
    for i, question in enumerate(analysis_1.questions_to_ask, 1):
        print(f"  {i}. {question}")
    
    print(f"\n📞 Call Strategy ({len(analysis_1.call_strategy_steps)} steps):")
    for step in analysis_1.call_strategy_steps[:7]:
        print(f"  {step}")
    print(f"  ... and {len(analysis_1.call_strategy_steps) - 7} more steps")
    
    # Test Case 2: Knee Surgery with missing documentation
    print_section("Test Case 2: Knee Arthroscopy - Incomplete Documentation")
    
    request_data_2 = {
        "procedure_code": "29881",
        "diagnosis_code": "M23.205",
        "patient_name": "Jane Smith",
        "patient_dob": date(1980, 3, 22),
        "member_id": "XYZ987654321",
        "provider_name": "Dr. Michael Johnson",
        "provider_npi": "9876543210",
        "clinical_notes": """
            Patient has knee pain and swelling.
            Positive McMurray test.
        """,
        "urgency_level": "routine"
    }
    
    analysis_2 = analyzer.analyze(request_data_2)
    
    print(f"\n📊 Analysis Results:")
    print(f"  Procedure: {analysis_2.request.procedure_name}")
    print(f"  Success Probability: {analysis_2.success_probability:.0%}")
    
    print(f"\n📄 Documentation Status:")
    print(f"  Complete: {'✓ YES' if analysis_2.documentation_complete else '✗ NO'}")
    if analysis_2.missing_documentation:
        print(f"  ⚠️  Missing Documentation:")
        for doc in analysis_2.missing_documentation:
            print(f"    • {doc}")
    
    # Test Case 3: Urgent/Stat Request
    print_section("Test Case 3: Emergency ED Visit - STAT Priority")
    
    request_data_3 = {
        "procedure_code": "99285",
        "diagnosis_code": "R07.9",
        "patient_name": "Robert Williams",
        "patient_dob": date(1965, 11, 8),
        "member_id": "DEF456789012",
        "provider_name": "Dr. Emergency Room",
        "provider_npi": "5555555555",
        "clinical_notes": """
            Emergency department visit for acute chest pain.
            High complexity medical decision making.
            Multiple diagnoses considered including MI, PE, aortic dissection.
            Extensive workup: EKG, troponin, D-dimer, CT angiography.
            High risk of complications - admission considered.
        """,
        "urgency_level": "stat"
    }
    
    analysis_3 = analyzer.analyze(request_data_3)
    
    print(f"\n📊 Analysis Results:")
    print(f"  Procedure: {analysis_3.request.procedure_name}")
    print(f"  Urgency: {analysis_3.request.urgency_level.upper()}")
    print(f"  Contact: {analysis_3.payer_contact_department}")
    print(f"  Turnaround: {analysis_3.expected_turnaround_time}")
    
    # Show configuration-driven nature
    print_section("CONFIGURATION-DRIVEN ARCHITECTURE")
    
    print("""
✨ Key Features Demonstrated:

1. ZERO HARDCODING
   • All procedure details loaded from procedures.yaml
   • All conversation logic from conversation_templates.yaml
   • Add new procedures without touching code!

2. TYPE SAFETY
   • Pydantic models validate all input data
   • Catch errors at development time, not runtime
   • Auto-generated documentation

3. MODULAR DESIGN
   • BaseAnalyzer enforces consistent interface
   • Easy to add DenialAnalyzer, VerificationAnalyzer
   • Each component has single responsibility

4. PRODUCTION READY
   • Comprehensive logging
   • Input validation
   • Error handling
   • Configuration caching
   • Singleton patterns

5. EASY TO EXTEND
   • Want to add a new procedure? Edit YAML
   • Want to change questions? Edit YAML
   • Want to modify strategy? Edit YAML
   • NO CODE CHANGES NEEDED!
    """)
    
    print_section("NEXT STEPS FOR HACKATHON")
    
    print("""
📅 Day 1-2: ✓ DONE
   • Production-ready prior auth analyzer
   • Configuration system
   • Data models
   
📅 Day 3-4: TODO
   • Create DenialAnalyzer (same pattern)
   • Add denial_stages.py
   • Create agent configs
   
📅 Day 5: TODO
   • Create Orchestrator
   • Integrate with existing voice agent
   • Test end-to-end
   
📅 Day 6-7: TODO
   • Demo scenarios
   • Dashboard
   • Practice presentation
    """)
    
    print_section("DEMO COMPLETE")
    print("\n✓ Production-ready architecture demonstrated")
    print("✓ Zero hardcoding - all config in YAML")
    print("✓ Type-safe with Pydantic models")
    print("✓ Modular and extensible")
    print("✓ Ready for hackathon! 🚀\n")


if __name__ == "__main__":
    demo_prior_auth_analysis()
