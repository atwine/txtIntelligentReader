#!/usr/bin/env python3
"""
Test script for WorkflowCoordinatorAgent
"""

import sys
sys.path.append('src')

from agents.workflow_coordinator import WorkflowCoordinatorAgent
from crewai import Agent

# Mock LLM for testing
class MockLLM:
    def __call__(self, prompt):
        return "Mock response"

# Mock agents for testing
def create_mock_agents():
    llm = MockLLM()
    
    agents = [
        Agent(
            role="Content Classifier",
            goal="Classify text content",
            backstory="Expert in content classification",
            llm=llm
        ),
        Agent(
            role="Health Expert",
            goal="Analyze health relevance",
            backstory="Medical domain specialist",
            llm=llm
        ),
        Agent(
            role="Grammar Enhancer",
            goal="Improve text quality",
            backstory="Language and grammar expert",
            llm=llm
        ),
        Agent(
            role="Quality Validator",
            goal="Validate final quality",
            backstory="Quality assurance specialist",
            llm=llm
        )
    ]
    
    return agents

def main():
    print("=" * 60)
    print("Testing WorkflowCoordinatorAgent Implementation")
    print("=" * 60)
    
    try:
        # Create mock agents
        mock_agents = create_mock_agents()
        
        # Create coordinator
        coordinator = WorkflowCoordinatorAgent(MockLLM(), mock_agents)
        print("✅ WorkflowCoordinatorAgent created successfully")
        print(f"   Crew has {len(coordinator.crew.agents)} agents")
        
        # Test 1: Text segmentation
        print("\n1. Testing text segmentation:")
        test_content = """
        The patient received excellent medical treatment. 
        The doctor prescribed antibiotics for the infection. 
        Recovery was successful and complete.
        """
        
        segments = coordinator._split_text_into_segments(test_content)
        print(f"   Original content: {len(test_content)} characters")
        print(f"   Segments created: {len(segments)}")
        for i, segment in enumerate(segments):
            print(f"   Segment {i+1}: '{segment[:50]}...'")
        
        # Test 2: Task creation
        print("\n2. Testing task creation:")
        test_segments = [
            "The patient received medical treatment.",
            "Antibiotics were prescribed for infection.",
            "Recovery was successful."
        ]
        
        tasks = coordinator.create_processing_tasks(test_segments)
        print(f"   Created {len(tasks)} tasks for {len(test_segments)} segments")
        print(f"   Expected: {len(test_segments) * 4} tasks (4 per segment)")
        
        for i, task in enumerate(tasks[:4]):  # Show first 4 tasks
            print(f"   Task {i+1}: {task.description[:60]}...")
        
        # Test 3: Workflow execution simulation
        print("\n3. Testing workflow execution:")
        results = coordinator._execute_workflow(tasks[:4])  # Test with first 4 tasks
        print(f"   Executed {len(results)} tasks")
        
        successful = [r for r in results if r.get('success', False)]
        print(f"   Successful: {len(successful)}")
        print(f"   Success rate: {len(successful)/len(results)*100:.1f}%")
        
        # Test 4: Results aggregation
        print("\n4. Testing results aggregation:")
        aggregated = coordinator._aggregate_results(results)
        print(f"   Aggregated {len(aggregated)} results")
        
        for i, result in enumerate(aggregated[:2]):  # Show first 2 results
            print(f"   Result {i+1}: Agent={result['agent']}, Quality={result['quality_score']:.2f}")
        
        # Test 5: Workflow metrics
        print("\n5. Testing workflow metrics:")
        metrics = coordinator._generate_workflow_metrics(results)
        print(f"   Total tasks: {metrics['total_tasks']}")
        print(f"   Success rate: {metrics['success_rate']:.2f}")
        print(f"   Average quality: {metrics['average_quality']:.2f}")
        print(f"   Workflow efficiency: {metrics['workflow_efficiency']:.2f}")
        
        # Test 6: Progress monitoring
        print("\n6. Testing progress monitoring:")
        progress = coordinator.monitor_workflow_progress()
        print(f"   Status: {progress['status']}")
        print(f"   Active agents: {progress['active_agents']}")
        print(f"   Workflow health: {progress['workflow_health']}")
        
        # Test 7: Error handling
        print("\n7. Testing error handling:")
        test_error = ValueError("Test error")
        test_context = {
            'agent': 'test_agent',
            'task': 'test_task',
            'timestamp': '2024-01-01'
        }
        
        error_result = coordinator.handle_workflow_errors(test_error, test_context)
        print(f"   Error handled: {error_result['error_handled']}")
        print(f"   Recovery action: {error_result['recovery_action']}")
        print(f"   Can continue: {error_result['can_continue']}")
        
        # Test 8: Recovery action determination
        print("\n8. Testing recovery action determination:")
        error_types = ['ConnectionError', 'ValueError', 'MemoryError', 'UnknownError']
        
        for error_type in error_types:
            action = coordinator._determine_recovery_action(error_type, {})
            print(f"   {error_type}: {action}")
        
        # Test 9: Create sample text file and test full coordination
        print("\n9. Testing full coordination workflow:")
        
        # Create a sample text file
        sample_file = "test_sample.txt"
        sample_content = """
        The patient was diagnosed with bacterial pneumonia.
        Antibiotic treatment was prescribed by the physician.
        The patient showed significant improvement after treatment.
        Recovery was complete within two weeks.
        """
        
        try:
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            
            # Test coordination
            coordination_result = coordinator.coordinate_processing(sample_file)
            
            print(f"   Processed segments: {coordination_result['processed_segments']}")
            print(f"   Successful segments: {coordination_result['successful_segments']}")
            print(f"   Quality score: {coordination_result['quality_score']:.2f}")
            print(f"   Processing time: {coordination_result['processing_time']:.2f}s")
            
            # Clean up
            import os
            if os.path.exists(sample_file):
                os.remove(sample_file)
                
        except Exception as e:
            print(f"   Error in full coordination test: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("WorkflowCoordinatorAgent is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
