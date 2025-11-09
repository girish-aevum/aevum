"""
Groq API Client for AI Companion
Handles all interactions with Groq API for health-focused conversations
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GROQ_API_KEY', '')
        self.model = getattr(settings, 'GROQ_MODEL', 'llama3-70b-8192')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def get_chat_response(self, messages: List[Dict]) -> str:
        """
        Get a simple chat response from Groq API
        
        Args:
            messages: List of conversation messages with role and content
            
        Returns:
            AI response content as string
        """
        if not self.api_key:
            return "I'm sorry, but the AI service is not configured properly. Please contact support."
        
        try:
            # Add system prompt
            system_prompt = """You are Aevum, a helpful health companion AI assistant. You provide supportive, informative responses about health and wellness topics. Always be encouraging, empathetic, and remind users to consult healthcare professionals for serious medical concerns."""
            
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": full_messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content'].strip()
                else:
                    logger.error("No choices in Groq API response")
                    return "I'm having trouble generating a response right now. Please try again."
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return "I'm experiencing some technical difficulties. Please try again in a moment."
                
        except requests.exceptions.Timeout:
            logger.error("Groq API request timeout")
            return "I'm taking too long to respond. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request error: {str(e)}")
            return "I'm having connection issues. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in Groq API call: {str(e)}")
            return "I encountered an unexpected error. Please try again."

    def summarize_response(self, original_response: str, max_length: int = 200) -> str:
        """
        Summarize an AI response to make it more concise while preserving key information
        
        Args:
            original_response: The original AI response to summarize
            max_length: Maximum word count for the summary (default: 200 words)
            
        Returns:
            Summarized response as string
        """
        if not self.api_key:
            # If no API key, just truncate the response
            words = original_response.split()
            if len(words) <= max_length:
                return original_response
            return ' '.join(words[:max_length]) + "..."
        
        # If the response is already short enough, return as-is
        word_count = len(original_response.split())
        if word_count <= max_length:
            return original_response
        
        try:
            summarization_prompt = f"""Please summarize the following AI response to be more concise while preserving all key information, actionable advice, and important details. Keep it under {max_length} words but maintain the helpful and supportive tone.

Original response:
{original_response}

Provide a concise summary that:
1. Keeps all essential information and advice
2. Maintains the supportive and encouraging tone
3. Preserves any important warnings or disclaimers
4. Is easy to read and understand
5. Stays under {max_length} words"""

            messages = [
                {"role": "user", "content": summarization_prompt}
            ]
            
            full_messages = [
                {"role": "system", "content": "You are an expert at creating concise, helpful summaries while preserving important information."}
            ] + messages
            
            payload = {
                "model": self.model,
                "messages": full_messages,
                "temperature": 0.3,  # Lower temperature for more focused summarization
                "max_tokens": max_length * 2,  # Allow some buffer for the summary
                "top_p": 0.8,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    summary = data['choices'][0]['message']['content'].strip()
                    
                    # Ensure the summary is actually shorter
                    if len(summary.split()) < len(original_response.split()):
                        return summary
                    else:
                        # If summarization didn't make it shorter, truncate intelligently
                        return self._truncate_intelligently(original_response, max_length)
                else:
                    logger.error("No choices in summarization response")
                    return self._truncate_intelligently(original_response, max_length)
            else:
                logger.error(f"Summarization API error: {response.status_code}")
                return self._truncate_intelligently(original_response, max_length)
                
        except Exception as e:
            logger.error(f"Error in response summarization: {str(e)}")
            return self._truncate_intelligently(original_response, max_length)
    
    def _truncate_intelligently(self, text: str, max_words: int) -> str:
        """
        Intelligently truncate text at sentence boundaries when possible
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Try to find a good sentence boundary near the limit
        truncated_words = words[:max_words]
        truncated_text = ' '.join(truncated_words)
        
        # Look for the last sentence ending within the limit
        sentence_endings = ['.', '!', '?']
        for i in range(len(truncated_text) - 1, -1, -1):
            if truncated_text[i] in sentence_endings:
                # Found a sentence ending, truncate there
                return truncated_text[:i + 1]
        
        # No sentence ending found, just truncate and add ellipsis
        return truncated_text + "..."
    
    def create_health_system_prompt(self, personality_type: str = "FRIENDLY", user_context: Dict = None) -> str:
        """Create a comprehensive system prompt for health conversations"""
        
        base_prompt = """You are Aevum, an intelligent health companion AI assistant for the Aevum Health platform. You provide personalized health guidance, support, and insights to users on their wellness journey.

        CORE IDENTITY:
        - You are knowledgeable, empathetic, and supportive
        - You focus on holistic health: physical, mental, and emotional wellness
        - You provide evidence-based information while being encouraging
        - You respect user privacy and maintain professional boundaries

        CAPABILITIES:
        - Analyze health patterns and provide insights
        - Offer personalized wellness recommendations
        - Support mental health and emotional wellbeing
        - Guide users through health goal setting and tracking
        - Provide nutrition and lifestyle advice
        - Help interpret health data and trends

        IMPORTANT GUIDELINES:
        - NEVER provide specific medical diagnoses or replace professional medical care
        - Always encourage users to consult healthcare providers for serious concerns
        - Be supportive and non-judgmental in all interactions
        - Respect user privacy and data confidentiality
        - Provide actionable, practical advice
        - Use encouraging and positive language

        RESPONSE STYLE:
        - Be conversational and friendly
        - Use emojis appropriately to enhance communication
        - Keep responses helpful but concise
        - Ask follow-up questions to better understand user needs
        - Provide specific, actionable recommendations when possible"""

        # Customize based on personality type
        personality_prompts = {
            "FRIENDLY": "\nCOMMUNICATION STYLE: Be warm, friendly, and supportive. Use casual language and show genuine care for the user's wellbeing.",
            "PROFESSIONAL": "\nCOMMUNICATION STYLE: Maintain a professional, medical-informed tone while being approachable. Use appropriate medical terminology when helpful.",
            "MOTIVATIONAL": "\nCOMMUNICATION STYLE: Be energetic, encouraging, and motivational. Focus on empowering the user and celebrating their progress.",
            "EMPATHETIC": "\nCOMMUNICATION STYLE: Be deeply understanding, compassionate, and emotionally supportive. Validate feelings and provide comfort.",
            "ANALYTICAL": "\nCOMMUNICATION STYLE: Focus on data, patterns, and evidence-based insights. Provide detailed analysis and logical recommendations.",
            "CASUAL": "\nCOMMUNICATION STYLE: Be relaxed, informal, and like a knowledgeable friend. Use everyday language and relatable examples."
        }
        
        prompt = base_prompt + personality_prompts.get(personality_type, personality_prompts["FRIENDLY"])
        
        # Add user context if available
        if user_context:
            context_info = []
            if user_context.get('health_goals'):
                context_info.append(f"Health Goals: {', '.join(user_context['health_goals'])}")
            if user_context.get('health_conditions'):
                context_info.append(f"Health Conditions: {', '.join(user_context['health_conditions'])}")
            if user_context.get('communication_style'):
                context_info.append(f"Preferred Communication: {user_context['communication_style']}")
            
            if context_info:
                prompt += f"\n\nUSER CONTEXT:\n" + "\n".join(context_info)
        
        return prompt
    
    def send_message(
        self, 
        messages: List[Dict], 
        personality_type: str = "FRIENDLY",
        user_context: Dict = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Tuple[Optional[str], Dict]:
        """
        Send message to Groq API and get response
        
        Args:
            messages: List of conversation messages
            personality_type: AI personality type
            user_context: User's health context
            temperature: AI creativity level
            max_tokens: Maximum response length
            
        Returns:
            Tuple of (response_content, metadata)
        """
        start_time = time.time()
        
        try:
            # Create system prompt
            system_prompt = self.create_health_system_prompt(personality_type, user_context)
            
            # Prepare the full message list
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9,
                "stream": False
            }
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response content
                ai_response = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract usage information
                usage = data.get('usage', {})
                
                metadata = {
                    'success': True,
                    'model_used': self.model,
                    'processing_time_ms': processing_time,
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0),
                    'temperature': temperature,
                    'response_id': data.get('id', ''),
                    'created': data.get('created', 0)
                }
                
                logger.info(f"Groq API success - Tokens: {metadata['total_tokens']}, Time: {processing_time}ms")
                
                return ai_response, metadata
                
            else:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                metadata = {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'processing_time_ms': processing_time
                }
                
                return None, metadata
                
        except requests.exceptions.Timeout:
            error_msg = "Groq API request timed out"
            logger.error(error_msg)
            
            metadata = {
                'success': False,
                'error': error_msg,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
            
            return None, metadata
            
        except Exception as e:
            error_msg = f"Groq API client error: {str(e)}"
            logger.error(error_msg)
            
            metadata = {
                'success': False,
                'error': error_msg,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
            
            return None, metadata
    
    def get_health_insights(self, user_data: Dict, question: str) -> Tuple[Optional[str], Dict]:
        """
        Get health insights based on user data and specific question
        
        Args:
            user_data: User's health data summary
            question: Specific health question or topic
            
        Returns:
            Tuple of (insights, metadata)
        """
        
        # Create specialized prompt for health insights
        insights_prompt = f"""Based on the user's health data, provide personalized insights and recommendations for: {question}

        USER HEALTH DATA:
        {json.dumps(user_data, indent=2)}

        Please provide:
        1. Key insights based on the data patterns
        2. Personalized recommendations
        3. Areas for improvement
        4. Potential health considerations
        5. Next steps or actions to take

        Keep the response practical, actionable, and encouraging."""

        messages = [
            {"role": "user", "content": insights_prompt}
        ]
        
        return self.send_message(
            messages=messages,
            personality_type="ANALYTICAL",
            temperature=0.3,  # Lower temperature for more focused insights
            max_tokens=800
        )
    
    def analyze_conversation_sentiment(self, conversation_messages: List[str]) -> Tuple[Optional[Dict], Dict]:
        """
        Analyze the sentiment and emotional tone of a conversation
        
        Args:
            conversation_messages: List of user messages from the conversation
            
        Returns:
            Tuple of (sentiment_analysis, metadata)
        """
        
        messages_text = "\n".join(conversation_messages)
        
        sentiment_prompt = f"""Analyze the emotional tone and sentiment of these user messages from a health conversation:

        MESSAGES:
        {messages_text}

        Please provide a JSON response with:
        {{
        "overall_sentiment": "positive/neutral/negative",
        "emotional_state": "description of user's emotional state",
        "health_concerns": ["list of health concerns mentioned"],
        "urgency_level": "low/medium/high",
        "recommended_follow_up": "suggested next steps",
        "sentiment_score": 0.85
        }}

Focus on understanding the user's health and emotional state to provide better support."""

        messages = [
            {"role": "user", "content": sentiment_prompt}
        ]
        
        response, metadata = self.send_message(
            messages=messages,
            personality_type="ANALYTICAL",
            temperature=0.2,
            max_tokens=400
        )
        
        # Try to parse JSON response
        if response:
            try:
                sentiment_data = json.loads(response)
                return sentiment_data, metadata
            except json.JSONDecodeError:
                logger.warning("Failed to parse sentiment analysis JSON response")
                return None, metadata
        
        return None, metadata


class HealthBotService:
    """High-level service for health bot interactions"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def get_user_health_context(self, user) -> Dict:
        """Gather user's health context from all apps"""
        context = {}
        
        try:
            # Get user profile data
            if hasattr(user, 'profile'):
                profile = user.profile
                context.update({
                    'age': self._calculate_age(profile.date_of_birth) if profile.date_of_birth else None,
                    'sex': profile.sex,
                    'health_conditions': [],
                    'lifestyle': {
                        'smoking_status': profile.smoking_status,
                        'alcohol_use': profile.alcohol_use,
                        'physical_activity_level': profile.physical_activity_level,
                        'diet_type': profile.diet_type,
                        'sleep_hours': profile.sleep_hours
                    }
                })
            
            # Get AI context if exists
            if hasattr(user, 'ai_context'):
                ai_context = user.ai_context
                context.update({
                    'health_goals': ai_context.health_goals,
                    'health_conditions': ai_context.health_conditions,
                    'medications': ai_context.medications,
                    'allergies': ai_context.allergies,
                    'communication_style': ai_context.communication_style
                })
            
            # Get recent mood data if allowed
            if hasattr(user, 'ai_context') and user.ai_context.allow_mood_data_access:
                from mental_wellness.models import MoodEntry
                recent_moods = MoodEntry.objects.filter(
                    user=user
                ).order_by('-entry_date')[:7]
                
                if recent_moods:
                    avg_mood = sum(entry.mood_rating for entry in recent_moods) / len(recent_moods)
                    context['recent_mood_average'] = round(avg_mood, 2)
            
        except Exception as e:
            logger.error(f"Error gathering user health context: {e}")
        
        return context
    
    def _calculate_age(self, birth_date):
        """Calculate age from birth date"""
        from datetime import date
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def process_user_message(
        self, 
        user, 
        conversation, 
        user_message: str,
        message_type: str = "TEXT"
    ) -> Tuple[Optional[str], Dict]:
        """
        Process user message and generate AI response
        
        Args:
            user: Django User instance
            conversation: Conversation instance
            user_message: User's message content
            message_type: Type of message
            
        Returns:
            Tuple of (ai_response, metadata)
        """
        
        try:
            # Get user health context
            user_context = self.get_user_health_context(user)
            
            # Get conversation history (last 10 messages for context)
            recent_messages = conversation.messages.order_by('-created_at')[:10]
            
            # Build message history for API
            messages = []
            for msg in reversed(recent_messages):
                role = "user" if msg.sender == "USER" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Get AI personality settings
            personality_type = "FRIENDLY"
            temperature = 0.7
            max_tokens = 500
            
            if conversation.ai_personality:
                personality_type = conversation.ai_personality.personality_type
                temperature = conversation.ai_personality.temperature
                max_tokens = conversation.ai_personality.max_response_length
            
            # Send to Groq API
            ai_response, metadata = self.groq_client.send_message(
                messages=messages,
                personality_type=personality_type,
                user_context=user_context,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return ai_response, metadata
            
        except Exception as e:
            error_msg = f"Error processing user message: {str(e)}"
            logger.error(error_msg)
            
            metadata = {
                'success': False,
                'error': error_msg
            }
            
            return None, metadata
    
    def generate_health_summary(self, user) -> Tuple[Optional[str], Dict]:
        """Generate a comprehensive health summary for the user"""
        
        user_context = self.get_user_health_context(user)
        
        summary_prompt = """Based on the user's health data, provide a comprehensive but concise health summary that includes:

        1. Overall health status assessment
        2. Key strengths in their health profile
        3. Areas that might need attention
        4. Personalized recommendations
        5. Suggested next steps

        Keep it encouraging and actionable. Focus on empowering the user to take positive steps."""

        messages = [
            {"role": "user", "content": summary_prompt}
        ]
        
        return self.groq_client.send_message(
            messages=messages,
            personality_type="PROFESSIONAL",
            user_context=user_context,
            temperature=0.4,
            max_tokens=600
        )
    
    def get_personalized_recommendations(self, user, focus_area: str) -> Tuple[Optional[str], Dict]:
        """Get personalized health recommendations for a specific focus area"""
        
        user_context = self.get_user_health_context(user)
        
        recommendation_prompt = f"""Provide personalized health recommendations for: {focus_area}

        Consider the user's health profile and provide:
        1. 3-5 specific, actionable recommendations
        2. Why each recommendation is beneficial for this user
        3. How to implement these recommendations practically
        4. Potential challenges and how to overcome them
        5. Timeline for seeing results

        Make the recommendations realistic and achievable."""

        messages = [
            {"role": "user", "content": recommendation_prompt}
        ]
        
        return self.groq_client.send_message(
            messages=messages,
            personality_type="MOTIVATIONAL",
            user_context=user_context,
            temperature=0.5,
            max_tokens=700
        )
    
    def analyze_health_patterns(self, user, data_summary: Dict) -> Tuple[Optional[str], Dict]:
        """Analyze health patterns and provide insights"""
        
        analysis_prompt = f"""Analyze the following health patterns and provide insights:

        HEALTH DATA SUMMARY:
        {json.dumps(data_summary, indent=2)}

        Please provide:
        1. Key patterns you notice in the data
        2. Positive trends to celebrate
        3. Areas of concern or improvement
        4. Correlations between different health metrics
        5. Actionable insights and recommendations

        Focus on helping the user understand their health journey and make informed decisions."""

        messages = [
            {"role": "user", "content": analysis_prompt}
        ]
        
        return self.groq_client.send_message(
            messages=messages,
            personality_type="ANALYTICAL",
            user_context=self.get_user_health_context(user),
            temperature=0.3,
            max_tokens=800
        )


# Singleton instance
health_bot_service = HealthBotService() 