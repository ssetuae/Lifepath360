import os
import openai
from django.conf import settings
from dotenv import load_dotenv
from .models import Question, QuestionOption, QuestionCategory, QuestionType
from users.models import Student

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

class AIQuestionGenerator:
    """
    Class for generating AI-driven questions for assessments.
    """
    
    @staticmethod
    def generate_questions_for_grade(grade, num_questions=10, categories=None):
        """
        Generate a set of questions for a specific grade level.
        
        Args:
            grade (str): Grade level (K, G1, G2, etc.)
            num_questions (int): Number of questions to generate
            categories (list): List of categories to generate questions for
            
        Returns:
            list: List of generated Question objects
        """
        if categories is None:
            categories = list(QuestionCategory.values)
        
        # Get grade display name for better prompting
        grade_display = dict(Student.Grade.choices).get(grade, grade)
        
        questions = []
        
        # Distribute questions across categories
        questions_per_category = num_questions // len(categories)
        remainder = num_questions % len(categories)
        
        for i, category in enumerate(categories):
            # Add an extra question to some categories if there's a remainder
            cat_questions = questions_per_category + (1 if i < remainder else 0)
            
            # Generate questions for this category
            category_questions = AIQuestionGenerator._generate_category_questions(
                grade, grade_display, category, cat_questions
            )
            
            questions.extend(category_questions)
        
        return questions
    
    @staticmethod
    def _generate_category_questions(grade, grade_display, category, num_questions):
        """
        Generate questions for a specific category and grade level.
        
        Args:
            grade (str): Grade level code (K, G1, G2, etc.)
            grade_display (str): Display name of grade level
            category (str): Question category
            num_questions (int): Number of questions to generate
            
        Returns:
            list: List of generated Question objects
        """
        # Get category display name
        category_display = dict(QuestionCategory.choices).get(category, category)
        
        # Determine appropriate question types for this category
        question_types = AIQuestionGenerator._get_question_types_for_category(category)
        
        # Create prompt for OpenAI
        prompt = AIQuestionGenerator._create_question_generation_prompt(
            grade_display, category_display, question_types, num_questions
        )
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational psychologist specializing in K-12 assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            questions_data = AIQuestionGenerator._parse_openai_response(response)
            
            # Create Question objects
            questions = []
            for q_data in questions_data:
                question = Question(
                    text=q_data['question'],
                    category=category,
                    question_type=q_data['type'],
                    grade_level=grade,
                    difficulty=q_data.get('difficulty', 2),  # Default to medium difficulty
                    time_limit=q_data.get('time_limit', 60),  # Default to 60 seconds
                    is_active=True,
                    is_ai_generated=True,
                    ai_prompt=prompt
                )
                question.save()
                
                # Create options for multiple choice questions
                if 'options' in q_data and q_data['type'] in ['MULTIPLE_CHOICE', 'SITUATIONAL']:
                    for opt_data in q_data['options']:
                        option = QuestionOption(
                            question=question,
                            text=opt_data['text'],
                            is_correct=opt_data.get('is_correct', False),
                            learning_style_impact=opt_data.get('learning_style_impact', {}),
                            cognitive_impact=opt_data.get('cognitive_impact', {}),
                            behavior_impact=opt_data.get('behavior_impact', {}),
                            interest_impact=opt_data.get('interest_impact', {})
                        )
                        option.save()
                
                questions.append(question)
            
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return []
    
    @staticmethod
    def _get_question_types_for_category(category):
        """
        Determine appropriate question types for a category.
        
        Args:
            category (str): Question category
            
        Returns:
            list: List of appropriate question types
        """
        # Map categories to appropriate question types
        category_type_map = {
            'LEARNING_STYLE': ['MULTIPLE_CHOICE', 'SITUATIONAL'],
            'BEHAVIOR': ['SITUATIONAL', 'MULTIPLE_CHOICE'],
            'COGNITIVE': ['LOGIC_PUZZLE', 'VISUAL_REASONING', 'VERBAL_REASONING'],
            'CREATIVITY': ['OPEN_ENDED', 'VISUAL_REASONING'],
            'TIME_MANAGEMENT': ['SITUATIONAL', 'MULTIPLE_CHOICE'],
            'COMMUNICATION': ['VERBAL_REASONING', 'OPEN_ENDED'],
            'INTEREST': ['MULTIPLE_CHOICE', 'OPEN_ENDED']
        }
        
        return category_type_map.get(category, list(QuestionType.values))
    
    @staticmethod
    def _create_question_generation_prompt(grade, category, question_types, num_questions):
        """
        Create a prompt for OpenAI to generate questions.
        
        Args:
            grade (str): Grade level display name
            category (str): Question category display name
            question_types (list): List of question types to generate
            num_questions (int): Number of questions to generate
            
        Returns:
            str: Prompt for OpenAI
        """
        # Convert question types to display names
        type_displays = [dict(QuestionType.choices).get(t, t) for t in question_types]
        
        prompt = f"""
        Generate {num_questions} educational assessment questions for {grade} students to evaluate their {category.lower()}.
        
        The questions should be appropriate for the cognitive and emotional development level of {grade} students.
        
        Use the following question types: {', '.join(type_displays)}
        
        For each question, provide:
        1. The question text
        2. The question type
        3. For multiple choice questions, provide 4 options with one correct answer
        4. For each option, provide impact scores for different aspects:
           - Learning style impact (visual, auditory, kinesthetic, logical, social, solitary)
           - Cognitive impact (memory, attention, problem-solving, creativity)
           - Behavior impact (persistence, confidence, independence, collaboration)
           - Interest impact (math, technology, arts, language, science, entrepreneurship)
        
        Format your response as a JSON array of question objects. Example:
        ```json
        [
          {{
            "question": "When you need to learn something new, what do you prefer?",
            "type": "MULTIPLE_CHOICE",
            "difficulty": 1,
            "time_limit": 30,
            "options": [
              {{
                "text": "Reading about it in a book",
                "is_correct": false,
                "learning_style_impact": {{"visual": 8, "auditory": 2}},
                "cognitive_impact": {{"memory": 6}},
                "behavior_impact": {{"independence": 7}},
                "interest_impact": {{"language": 6}}
              }},
              {{
                "text": "Watching a video demonstration",
                "is_correct": true,
                "learning_style_impact": {{"visual": 9, "auditory": 5}},
                "cognitive_impact": {{"attention": 7}},
                "behavior_impact": {{"persistence": 5}},
                "interest_impact": {{"technology": 5}}
              }}
            ]
          }},
          {{
            "question": "Describe how you would solve this problem...",
            "type": "OPEN_ENDED",
            "difficulty": 3,
            "time_limit": 120
          }}
        ]
        ```
        
        Ensure the questions are engaging, culturally sensitive, and free from bias. The questions should help identify the student's learning style, behavior patterns, cognitive strengths, and interests.
        """
        
        return prompt
    
    @staticmethod
    def _parse_openai_response(response):
        """
        Parse the OpenAI API response to extract question data.
        
        Args:
            response: OpenAI API response
            
        Returns:
            list: List of question data dictionaries
        """
        import json
        import re
        
        # Extract the content from the response
        content = response.choices[0].message.content
        
        # Extract JSON from the content (it might be wrapped in markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If not in code blocks, try to extract the entire JSON array
            json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', content)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
        
        try:
            # Parse the JSON
            questions_data = json.loads(json_str)
            return questions_data
        except json.JSONDecodeError:
            print(f"Error parsing JSON from OpenAI response: {content}")
            return []
