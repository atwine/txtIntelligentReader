#!/usr/bin/env python3
"""
Basic Usage Example for txtIntelligentReader

This example demonstrates how to use the txtIntelligentReader system
to process medical text files and extract translation-ready sentences.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.workflow_coordinator import WorkflowCoordinatorAgent
from agents.content_classifier import ContentClassifierAgent
from agents.health_expert import HealthDomainExpertAgent
from agents.grammar_enhancer import GrammarEnhancementAgent
from agents.quality_validator import QualityValidationAgent

# Mock LLM for demonstration (replace with actual Ollama client)
class MockLLM:
    def __call__(self, prompt):
        return "Mock LLM response for demonstration"

def main():
    """
    Demonstrate basic usage of txtIntelligentReader system.
    """
    print("🩺 txtIntelligentReader - Basic Usage Example")
    print("=" * 50)
    
    # Initialize LLM (replace with actual Ollama client)
    # from ollama import Client
    # llm = Client(host='http://localhost:11434')
    llm = MockLLM()  # For demonstration
    
    print("1. Creating specialist agents...")
    
    # Create specialist agents
    agents = [
        ContentClassifierAgent(llm),
        HealthDomainExpertAgent(llm),
        GrammarEnhancementAgent(llm),
        QualityValidationAgent(llm)
    ]
    
    print(f"   ✅ Created {len(agents)} specialist agents")
    
    # Create workflow coordinator
    print("2. Creating workflow coordinator...")
    coordinator = WorkflowCoordinatorAgent(llm, agents)
    print("   ✅ Workflow coordinator ready")
    
    # Create sample medical text file
    print("3. Creating sample medical text...")
    sample_text = """
    The patient was diagnosed with bacterial pneumonia after chest X-ray examination.
    Antibiotic treatment was prescribed by the attending physician.
    The patient showed significant improvement after 48 hours of treatment.
    Complete recovery was achieved within two weeks of hospitalization.
    Follow-up appointments were scheduled for monitoring progress.
    """
    
    sample_file = "sample_medical_text.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"   ✅ Sample file created: {sample_file}")
    
    # Process the text file
    print("4. Processing medical text...")
    try:
        results = coordinator.coordinate_processing(sample_file)
        
        print("   📊 Processing Results:")
        print(f"      • Processed segments: {results['processed_segments']}")
        print(f"      • Successful segments: {results['successful_segments']}")
        print(f"      • Quality score: {results['quality_score']:.2f}")
        print(f"      • Processing time: {results['processing_time']:.2f}s")
        
        if results['workflow_metrics']:
            metrics = results['workflow_metrics']
            print(f"      • Success rate: {metrics.get('success_rate', 0):.2f}")
            print(f"      • Workflow efficiency: {metrics.get('workflow_efficiency', 0):.2f}")
        
    except Exception as e:
        print(f"   ❌ Error during processing: {e}")
    
    # Clean up
    print("5. Cleaning up...")
    if os.path.exists(sample_file):
        os.remove(sample_file)
        print(f"   ✅ Removed {sample_file}")
    
    print("\n🎉 Example completed successfully!")
    print("\nNext steps:")
    print("• Replace MockLLM with actual Ollama client")
    print("• Configure your .env file with proper settings")
    print("• Process your own medical text files")
    print("• Explore advanced features and filtering options")

if __name__ == "__main__":
    main()
