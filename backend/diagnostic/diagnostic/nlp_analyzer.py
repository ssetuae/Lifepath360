import os
import openai
from dotenv import load_dotenv
from .models import Response, Question, Assessment

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

class NLPResponseAnalyzer:
    """
    Class for analyzing open-ended responses using NLP techniques.
    """
    
    @staticmethod
    def analyze_open_response(response_id):
        """
        Analyze an open-ended response using NLP.
        
        Args:
            response_id: ID of the response to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            response = Response.objects.get(id=response_id)
            
            # Check if response is for an open-ended question
            if response.question.question_type != 'OPEN_ENDED':
                return {
                    'error': 'This is not an open-ended response.',
                    'response_id': response_id
                }
            
            # Check if response has text
            if not response.open_response:
                return {
                    'error': 'No text found in response.',
                    'response_id': response_id
                }
            
            # Get question context
            question = response.question
            
            # Analyze response using OpenAI
            analysis = NLPResponseAnalyzer._analyze_with_openai(
                question.text,
                response.open_response,
                question.category,
                question.grade_level
            )
            
            return {
                'response_id': response_id,
                'question_id': question.id,
                'question_text': question.text,
                'response_text': response.open_response,
                'analysis': analysis
            }
            
        except Response.DoesNotExist:
            return {
                'error': f'Response with ID {response_id} not found.'
            }
        except Exception as e:
            return {
                'error': f'Error analyzing response: {str(e)}'
            }
    
    @staticmethod
    def analyze_assessment_open_responses(assessment_id):
        """
        Analyze all open-ended responses for an assessment.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            dict: Analysis results for all open-ended responses
        """
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Get all open-ended responses for this assessment
            responses = Response.objects.filter(
                assessment=assessment,
                question__question_type='OPEN_ENDED'
            )
            
            if not responses:
                return {
                    'error': 'No open-ended responses found for this assessment.',
                    'assessment_id': assessment_id
                }
            
            # Analyze each response
            analyses = []
            for response in responses:
                if response.open_response:
                    analysis = NLPResponseAnalyzer.analyze_open_response(response.id)
                    if 'error' not in analysis:
                        analyses.append(analysis)
            
            return {
                'assessment_id': assessment_id,
                'student_id': assessment.student.id,
                'student_name': f"{assessment.student.first_name} {assessment.student.last_name}",
                'analyses': analyses
            }
            
        except Assessment.DoesNotExist:
            return {
                'error': f'Assessment with ID {assessment_id} not found.'
            }
        except Exception as e:
            return {
                'error': f'Error analyzing assessment responses: {str(e)}'
            }
    
    @staticmethod
    def _analyze_with_openai(question, response, category, grade_level):
        """
        Analyze an open-ended response using OpenAI.
        
        Args:
            question: Question text
            response: Response text
            category: Question category
            grade_level: Student's grade level
            
        Returns:
            dict: Analysis results
        """
        # Create prompt for OpenAI
        prompt = f"""
        Analyze the following student response to an open-ended question.
        
        Grade Level: {grade_level}
        Category: {category}
        
        Question: {question}
        
        Student Response: {response}
        
        Please provide a comprehensive analysis of the response, including:
        1. Creativity and originality (score 1-10)
        2. Critical thinking and depth of analysis (score 1-10)
        3. Communication clarity and expression (score 1-10)
        4. Subject knowledge and understanding (score 1-10)
        5. Learning style indicators (visual, auditory, kinesthetic, logical, social, solitary)
        6. Cognitive strengths demonstrated
        7. Behavior patterns indicated
        8. Interest areas suggested
        9. Specific insights about the student's thinking process
        10. Recommendations for further development
        
        Format your response as a JSON object with these categories.
        """
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational psychologist specializing in K-12 assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract JSON from the content
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If not in code blocks, try to extract the entire JSON object
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            try:
                # Parse the JSON
                analysis = json.loads(json_str)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw content
                return {
                    'raw_analysis': content
                }
                
        except Exception as e:
            return {
                'error': f'Error calling OpenAI API: {str(e)}'
            }
    
    @staticmethod
    def get_sentiment_scores(text):
        """
        Get sentiment scores for a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Sentiment scores
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Analyze the sentiment and emotional tone of the following text:
            
            {text}
            
            Please provide scores (1-10) for the following emotions/sentiments:
            1. Positivity
            2. Negativity
            3. Confidence
            4. Uncertainty
            5. Enthusiasm
            6. Frustration
            7. Curiosity
            8. Creativity
            
            Format your response as a JSON object with these categories.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in sentiment analysis and emotional intelligence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract JSON from the content
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If not in code blocks, try to extract the entire JSON object
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            try:
                # Parse the JSON
                sentiment_scores = json.loads(json_str)
                return sentiment_scores
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw content
                return {
                    'raw_analysis': content
                }
                
        except Exception as e:
            return {
                'error': f'Error analyzing sentiment: {str(e)}'
            }
    
    @staticmethod
    def extract_keywords(text):
        """
        Extract keywords and topics from a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Keywords and topics
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Extract the main keywords, topics, and concepts from the following text:
            
            {text}
            
            Please provide:
            1. A list of the top 10 keywords
            2. A list of the main topics discussed
            3. A list of any specialized terminology or concepts
            
            Format your response as a JSON object with these categories.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in natural language processing and text analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract JSON from the content
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If not in code blocks, try to extract the entire JSON object
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            try:
                # Parse the JSON
                keywords = json.loads(json_str)
                return keywords
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw content
                return {
                    'raw_analysis': content
                }
                
        except Exception as e:
            return {
                'error': f'Error extracting keywords: {str(e)}'
            }
