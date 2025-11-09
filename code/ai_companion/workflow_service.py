import logging
from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.apps import apps
from transformers import pipeline

def get_model(model_name):
    """
    Safely get a model from the ai_companion app
    
    Args:
        model_name (str): Name of the model to retrieve
    
    Returns:
        Model class
    """
    return apps.get_model('ai_companion', model_name)

# Now import or define models using get_model
Thread = get_model('Thread')

from .workflow_models import (
    Workflow, 
    WorkflowStep, 
    WorkflowType, 
    WorkflowState, 
    WorkflowTemplate
)
from .groq_client import GroqClient

logger = logging.getLogger(__name__)

def summarize_text_locally(text, max_length=80, min_length=20):
    """
    Local summarization method using transformers pipeline
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum summary length
        min_length (int): Minimum summary length
    
    Returns:
        str: Summarized text
    """
    try:
        # Use the same summarizer as in views
        local_summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        
        # Perform summarization
        result = local_summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        
        return result[0]["summary_text"]
    except Exception as e:
        logger.error(f"Local summarization error: {e}")
        return ' '.join(text.split()[:max_length]) + '...'

class SummarizationAgent:
    """
    Agent responsible for summarizing AI responses
    """
    def __init__(self, groq_client=None):
        """
        Initialize summarization agent
        
        Args:
            groq_client (GroqClient, optional): Fallback client for summarization
        """
        self.groq_client = groq_client
    
    def summarize(self, original_response, max_length=80, min_length=20):
        """
        Summarize the AI response
        
        Args:
            original_response (str): Full AI response
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
        
        Returns:
            str: Summarized response
        """
        try:
            # First, try local summarization
            summary = summarize_text_locally(
                original_response, 
                max_length=max_length, 
                min_length=min_length
            )
            
            # If local summarization fails, fallback to Groq
            if not summary and self.groq_client:
                system_prompt = f"""
                You are a professional summarizer. 
                Summarize the following text concisely, capturing the key points.
                Limit the summary to approximately {max_length} words.
                Maintain the original tone and key information.
                """
                
                conversation_history = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Summarize this text: {original_response}"}
                ]
                
                summary = self.groq_client.get_chat_response(conversation_history)
            
            # Final fallback to truncation
            if not summary:
                summary = ' '.join(original_response.split()[:max_length]) + '...'
            
            return summary
        
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            # Absolute fallback
            return ' '.join(original_response.split()[:max_length]) + '...'

class WorkflowAgent:
    """Base class for workflow-specific agents"""
    def __init__(self, workflow):
        """
        Initialize workflow agent
        
        Args:
            workflow (Workflow): The workflow instance
        """
        self.workflow = workflow
        self.groq_client = GroqClient()

    def process_input(self, user_input):
        """
        Process user input and generate response
        
        Args:
            user_input (str): User's message
        
        Returns:
            dict: Response with AI output and workflow update
        """
        raise NotImplementedError("Subclasses must implement this method")

class GeneralWorkflowAgent(WorkflowAgent):
    """
    Default agent for general conversations
    Provides a flexible, context-aware response generation with summarization
    """
    def process_input(self, user_input):
        """
        Generate a generic, context-aware response with summarization
        
        Args:
            user_input (str): User's message
        
        Returns:
            dict: Response with AI output, summary, and workflow update
        """
        # Prepare context-aware prompt
        system_prompt = """
        You are a helpful AI assistant. 
        Provide supportive, informative, and contextually relevant responses.
        Be empathetic, clear, and aim to be genuinely helpful.
        """
        
        # Generate response using Groq
        conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            # Generate full response
            full_response = self.groq_client.get_chat_response(conversation_history)
            
            # Summarize response
            summarization_agent = SummarizationAgent(self.groq_client)
            summary = summarization_agent.summarize(full_response)
            
            return {
                'response': full_response,
                'summary': summary,
                'stage': 'default_conversation'
            }
        except Exception as e:
            logger.error(f"Error in general workflow agent: {str(e)}")
            return {
                'response': "I'm having trouble processing your message right now. Could you please try again?",
                'summary': "Unable to generate a summary.",
                'stage': 'error'
            } 

class WorkflowService:
    """
    Central service for managing complex AI workflows
    """
    
    @classmethod
    def create_workflow(cls, user, thread, workflow_type):
        """
        Create a new workflow for a specific interaction type
        
        Args:
            user (User): User initiating the workflow
            thread (Thread): Associated conversation thread
            workflow_type (str): Type of workflow
        
        Returns:
            Workflow: Newly created workflow instance
        """
        with transaction.atomic():
            workflow = Workflow.objects.create(
                user=user,
                thread=thread,
                type=workflow_type,
                state=WorkflowState.INITIALIZED
            )
            
            # Fetch template for predefined workflow
            try:
                template = WorkflowTemplate.objects.get(
                    type=workflow_type, 
                    is_active=True
                )
                workflow.total_steps = len(template.steps_config)
                workflow.save()
            except WorkflowTemplate.DoesNotExist:
                logger.warning(f"No template found for workflow type: {workflow_type}")
            
            return workflow
    
    @classmethod
    def process_workflow_step(cls, workflow, user_input):
        """
        Process a single step in the workflow
        
        Args:
            workflow (Workflow): Current workflow
            user_input (str): User's input message
        
        Returns:
            dict: Workflow processing result
        """
        # Expanded agent map with default agent
        agent_map = {
            WorkflowType.MENTAL_HEALTH: GeneralWorkflowAgent,
            WorkflowType.NUTRITION: GeneralWorkflowAgent,
            WorkflowType.FITNESS: GeneralWorkflowAgent,
            WorkflowType.THERAPY: GeneralWorkflowAgent,
            WorkflowType.GENERAL: GeneralWorkflowAgent  # Default agent for general conversations
        }
        
        # Fallback to GeneralWorkflowAgent if no specific agent is found
        AgentClass = agent_map.get(workflow.type, GeneralWorkflowAgent)
        agent = AgentClass(workflow)
        
        # Process input and get response
        result = agent.process_input(user_input)
        
        # Record workflow step
        WorkflowStep.objects.create(
            workflow=workflow,
            step_number=workflow.current_step,
            user_input=user_input,
            ai_response=result['response']
        )
        
        # Advance workflow
        workflow.advance_step()
        
        return result

def initialize_workflow_templates():
    """
    Initialize default workflow templates
    """
    default_templates = [
        {
            'name': 'Basic Mental Health Assessment',
            'type': WorkflowType.MENTAL_HEALTH,
            'steps_config': [
                {'stage': 'initial_screening', 'description': 'Understand current mental state'},
                {'stage': 'mood_evaluation', 'description': 'Detailed mood analysis'},
                {'stage': 'coping_strategies', 'description': 'Recommend coping mechanisms'},
                {'stage': 'progress_tracking', 'description': 'Monitor and track progress'}
            ],
            'description': 'Comprehensive mental health assessment workflow',
            'is_active': True
        },
        {
            'name': 'General Conversation',
            'type': WorkflowType.GENERAL,
            'steps_config': [
                {'stage': 'initial_interaction', 'description': 'Understand user intent'},
                {'stage': 'context_gathering', 'description': 'Collect relevant context'},
                {'stage': 'response_generation', 'description': 'Generate helpful response'},
                {'stage': 'follow_up', 'description': 'Offer additional support or clarification'}
            ],
            'description': 'Flexible conversation workflow for general interactions',
            'is_active': True
        }
        # Add more default templates
    ]
    
    for template_data in default_templates:
        WorkflowTemplate.objects.get_or_create(
            name=template_data['name'],
            type=template_data['type'],
            defaults=template_data
        )

# Placeholder agents for other workflow types
class NutritionWorkflowAgent(GeneralWorkflowAgent):
    """Placeholder for nutrition-specific workflow agent"""
    pass

class FitnessWorkflowAgent(GeneralWorkflowAgent):
    """Placeholder for fitness-specific workflow agent"""
    pass

class TherapyWorkflowAgent(GeneralWorkflowAgent):
    """Placeholder for therapy-specific workflow agent"""
    pass 