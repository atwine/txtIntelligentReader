"""
Workflow Coordinator Agent for txtIntelligentReader

This agent specializes in orchestrating multi-agent text processing workflows.
"""

from crewai import Agent, Crew, Process, Task
from typing import List, Dict, Any


class WorkflowCoordinatorAgent:
    """
    Agent specialized in orchestrating multi-agent text processing workflow.
    
    Role: Project Manager
    Goal: Orchestrate multi-agent text processing workflow
    Backstory: You coordinate teams of specialists to deliver high-quality results efficiently.
    """
    
    def __init__(self, llm, agents: List[Agent]):
        """Initialize the Workflow Coordinator Agent with LLM and agent crew."""
        self.agent = Agent(
            role="Project Manager",
            goal="Orchestrate multi-agent text processing workflow",
            backstory="You coordinate teams of specialists to deliver high-quality results efficiently.",
            llm=llm,
            verbose=True
        )
        self.crew = Crew(
            agents=agents,
            process=Process.sequential,
            verbose=True
        )
    
    def coordinate_processing(self, text_file: str) -> Dict[str, Any]:
        """
        Orchestrate agent workflow for text file processing.
        
        Args:
            text_file: Path to text file to process
            
        Returns:
            Processing results from coordinated workflow
        """
        try:
            # Read and prepare text file
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into segments for processing
            segments = self._split_text_into_segments(content)
            
            # Create processing tasks for each segment
            tasks = self.create_processing_tasks(segments)
            
            # Execute workflow with crew
            results = self._execute_workflow(tasks)
            
            # Aggregate and validate results
            final_results = self._aggregate_results(results)
            
            # Generate workflow metrics
            metrics = self._generate_workflow_metrics(results)
            
            return {
                'processed_segments': len(segments),
                'successful_segments': len([r for r in results if r.get('success', False)]),
                'final_results': final_results,
                'workflow_metrics': metrics,
                'processing_time': metrics.get('total_time', 0),
                'quality_score': metrics.get('average_quality', 0)
            }
            
        except Exception as e:
            return {
                'error': f"Workflow coordination failed: {str(e)}",
                'processed_segments': 0,
                'successful_segments': 0,
                'final_results': [],
                'workflow_metrics': {},
                'processing_time': 0,
                'quality_score': 0
            }
    
    def create_processing_tasks(self, text_segments: List[str]) -> List[Task]:
        """
        Create tasks for each agent in the processing pipeline.
        
        Args:
            text_segments: List of text segments to process
            
        Returns:
            List of CrewAI tasks for the workflow
        """
        tasks = []
        
        for i, segment in enumerate(text_segments):
            # Task 1: Content Classification
            classification_task = Task(
                description=f"Classify text segment {i+1}: '{segment[:50]}...'",
                agent=self.crew.agents[0] if len(self.crew.agents) > 0 else self.agent,
                expected_output="Classification category and confidence score"
            )
            tasks.append(classification_task)
            
            # Task 2: Health Domain Analysis
            health_task = Task(
                description=f"Analyze health relevance of segment {i+1}",
                agent=self.crew.agents[1] if len(self.crew.agents) > 1 else self.agent,
                expected_output="Health relevance score and medical entities"
            )
            tasks.append(health_task)
            
            # Task 3: Grammar Enhancement
            grammar_task = Task(
                description=f"Enhance grammar and readability of segment {i+1}",
                agent=self.crew.agents[2] if len(self.crew.agents) > 2 else self.agent,
                expected_output="Enhanced text with improved grammar"
            )
            tasks.append(grammar_task)
            
            # Task 4: Quality Validation
            validation_task = Task(
                description=f"Validate final quality of segment {i+1}",
                agent=self.crew.agents[3] if len(self.crew.agents) > 3 else self.agent,
                expected_output="Quality score and validation results"
            )
            tasks.append(validation_task)
        
        return tasks
    
    def monitor_workflow_progress(self) -> Dict[str, Any]:
        """
        Monitor progress of the multi-agent workflow.
        
        Returns:
            Workflow progress status and metrics
        """
        try:
            # Get current workflow state
            total_tasks = len(self.crew.tasks) if hasattr(self.crew, 'tasks') else 0
            completed_tasks = 0  # This would be tracked during execution
            
            # Calculate progress metrics
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'progress_percentage': progress_percentage,
                'status': 'in_progress' if completed_tasks < total_tasks else 'completed',
                'active_agents': len(self.crew.agents),
                'workflow_health': 'healthy'  # This would be determined by error rates
            }
            
        except Exception as e:
            return {
                'error': f"Progress monitoring failed: {str(e)}",
                'total_tasks': 0,
                'completed_tasks': 0,
                'progress_percentage': 0,
                'status': 'error',
                'active_agents': 0,
                'workflow_health': 'unhealthy'
            }
    
    def handle_workflow_errors(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors in the workflow with graceful recovery.
        
        Args:
            error: Exception that occurred
            context: Context information about the error
            
        Returns:
            Error handling results and recovery actions
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            # Log error details
            error_details = {
                'error_type': error_type,
                'error_message': error_message,
                'context': context,
                'timestamp': context.get('timestamp', 'unknown'),
                'agent': context.get('agent', 'unknown'),
                'task': context.get('task', 'unknown')
            }
            
            # Determine recovery action based on error type
            recovery_action = self._determine_recovery_action(error_type, context)
            
            return {
                'error_handled': True,
                'error_details': error_details,
                'recovery_action': recovery_action,
                'can_continue': recovery_action != 'abort',
                'retry_recommended': recovery_action == 'retry'
            }
            
        except Exception as handling_error:
            return {
                'error_handled': False,
                'error_details': {'original_error': str(error), 'handling_error': str(handling_error)},
                'recovery_action': 'abort',
                'can_continue': False,
                'retry_recommended': False
            }
    
    def _split_text_into_segments(self, content: str) -> List[str]:
        """
        Split text content into manageable segments for processing.
        
        Args:
            content: Text content to split
            
        Returns:
            List of text segments
        """
        # Split by sentences and paragraphs
        import re
        
        # Split by sentence endings, keeping sentences together
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        
        # Filter out empty segments and very short ones
        segments = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return segments
    
    def _execute_workflow(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Execute the workflow with the given tasks.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of execution results
        """
        results = []
        
        try:
            # For now, simulate task execution
            # In full implementation, this would use crew.kickoff()
            for task in tasks:
                result = {
                    'task_description': task.description,
                    'success': True,
                    'output': f"Processed: {task.description}",
                    'agent': task.agent.role if hasattr(task.agent, 'role') else 'unknown',
                    'execution_time': 1.0  # Mock execution time
                }
                results.append(result)
                
        except Exception as e:
            results.append({
                'success': False,
                'error': str(e),
                'execution_time': 0
            })
        
        return results
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate and process workflow results.
        
        Args:
            results: Raw results from workflow execution
            
        Returns:
            Aggregated and processed results
        """
        aggregated = []
        
        for result in results:
            if result.get('success', False):
                processed_result = {
                    'content': result.get('output', ''),
                    'agent': result.get('agent', 'unknown'),
                    'quality_score': 0.8,  # Mock quality score
                    'processing_time': result.get('execution_time', 0),
                    'status': 'completed'
                }
                aggregated.append(processed_result)
        
        return aggregated
    
    def _generate_workflow_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive workflow metrics.
        
        Args:
            results: Workflow execution results
            
        Returns:
            Workflow metrics and statistics
        """
        successful_results = [r for r in results if r.get('success', False)]
        
        total_time = sum(r.get('execution_time', 0) for r in results)
        success_rate = len(successful_results) / len(results) if results else 0
        average_quality = sum(r.get('quality_score', 0) for r in successful_results) / len(successful_results) if successful_results else 0
        
        return {
            'total_tasks': len(results),
            'successful_tasks': len(successful_results),
            'success_rate': success_rate,
            'total_time': total_time,
            'average_time_per_task': total_time / len(results) if results else 0,
            'average_quality': average_quality,
            'workflow_efficiency': success_rate * average_quality
        }
    
    def _determine_recovery_action(self, error_type: str, context: Dict[str, Any]) -> str:
        """
        Determine appropriate recovery action based on error type.
        
        Args:
            error_type: Type of error that occurred
            context: Error context information
            
        Returns:
            Recovery action to take
        """
        # Define recovery strategies based on error types
        if error_type in ['ConnectionError', 'TimeoutError']:
            return 'retry'
        elif error_type in ['ValueError', 'KeyError']:
            return 'skip_and_continue'
        elif error_type in ['MemoryError', 'SystemError']:
            return 'abort'
        else:
            return 'log_and_continue'
