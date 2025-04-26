import numpy as np
from collections import defaultdict
from .models import Response, Assessment, Question, QuestionOption

class LearningStyleAnalyzer:
    """
    Class for analyzing student responses to determine learning styles,
    cognitive strengths, behavior patterns, and interests.
    """
    
    # Learning style categories
    LEARNING_STYLES = [
        'visual', 'auditory', 'kinesthetic', 'logical', 'social', 'solitary'
    ]
    
    # Cognitive strength categories
    COGNITIVE_STRENGTHS = [
        'memory', 'attention', 'problem_solving', 'creativity', 'critical_thinking',
        'spatial_reasoning', 'verbal_reasoning', 'numerical_reasoning'
    ]
    
    # Behavior pattern categories
    BEHAVIOR_PATTERNS = [
        'persistence', 'confidence', 'independence', 'collaboration',
        'organization', 'adaptability', 'focus', 'risk_taking'
    ]
    
    # Interest categories
    INTERESTS = [
        'math', 'technology', 'arts', 'language', 'science', 'entrepreneurship',
        'humanities', 'sports', 'music', 'nature'
    ]
    
    @staticmethod
    def analyze_assessment(assessment_id):
        """
        Analyze an assessment to determine learning styles, cognitive strengths,
        behavior patterns, and interests.
        
        Args:
            assessment_id: ID of the assessment to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Check if assessment is completed
            if assessment.status != Assessment.Status.COMPLETED:
                return {
                    'error': 'Assessment is not completed yet.',
                    'status': assessment.status
                }
            
            # Get all responses for this assessment
            responses = Response.objects.filter(assessment=assessment)
            
            if not responses:
                return {
                    'error': 'No responses found for this assessment.',
                    'assessment_id': assessment_id
                }
            
            # Initialize scores
            learning_style_scores = defaultdict(float)
            cognitive_strength_scores = defaultdict(float)
            behavior_pattern_scores = defaultdict(float)
            interest_scores = defaultdict(float)
            
            # Analyze each response
            for response in responses:
                # Skip responses without selected options (open-ended questions)
                if not response.selected_option:
                    continue
                
                option = response.selected_option
                
                # Add learning style impacts
                if option.learning_style_impact:
                    for style, score in option.learning_style_impact.items():
                        learning_style_scores[style] += float(score)
                
                # Add cognitive impacts
                if option.cognitive_impact:
                    for cognitive, score in option.cognitive_impact.items():
                        cognitive_strength_scores[cognitive] += float(score)
                
                # Add behavior impacts
                if option.behavior_impact:
                    for behavior, score in option.behavior_impact.items():
                        behavior_pattern_scores[behavior] += float(score)
                
                # Add interest impacts
                if option.interest_impact:
                    for interest, score in option.interest_impact.items():
                        interest_scores[interest] += float(score)
            
            # Normalize scores
            learning_style_scores = LearningStyleAnalyzer._normalize_scores(learning_style_scores)
            cognitive_strength_scores = LearningStyleAnalyzer._normalize_scores(cognitive_strength_scores)
            behavior_pattern_scores = LearningStyleAnalyzer._normalize_scores(behavior_pattern_scores)
            interest_scores = LearningStyleAnalyzer._normalize_scores(interest_scores)
            
            # Determine primary and secondary types
            primary_learning_style, secondary_learning_style = LearningStyleAnalyzer._get_primary_secondary(learning_style_scores)
            primary_cognitive_strength, secondary_cognitive_strength = LearningStyleAnalyzer._get_primary_secondary(cognitive_strength_scores)
            primary_behavior_pattern, secondary_behavior_pattern = LearningStyleAnalyzer._get_primary_secondary(behavior_pattern_scores)
            primary_interest, secondary_interest = LearningStyleAnalyzer._get_primary_secondary(interest_scores)
            
            # Create analysis results
            analysis_results = {
                'assessment_id': assessment_id,
                'student_id': assessment.student.id,
                'student_name': f"{assessment.student.first_name} {assessment.student.last_name}",
                'grade': assessment.student.grade,
                'learning_styles': {
                    'scores': learning_style_scores,
                    'primary': primary_learning_style,
                    'secondary': secondary_learning_style
                },
                'cognitive_strengths': {
                    'scores': cognitive_strength_scores,
                    'primary': primary_cognitive_strength,
                    'secondary': secondary_cognitive_strength
                },
                'behavior_patterns': {
                    'scores': behavior_pattern_scores,
                    'primary': primary_behavior_pattern,
                    'secondary': secondary_behavior_pattern
                },
                'interests': {
                    'scores': interest_scores,
                    'primary': primary_interest,
                    'secondary': secondary_interest
                },
                'ideal_learning_environment': LearningStyleAnalyzer._determine_ideal_environment(
                    learning_style_scores, behavior_pattern_scores
                ),
                'learning_effectiveness_tips': LearningStyleAnalyzer._generate_learning_tips(
                    primary_learning_style, primary_cognitive_strength
                )
            }
            
            return analysis_results
            
        except Assessment.DoesNotExist:
            return {
                'error': f'Assessment with ID {assessment_id} not found.'
            }
        except Exception as e:
            return {
                'error': f'Error analyzing assessment: {str(e)}'
            }
    
    @staticmethod
    def _normalize_scores(scores_dict):
        """
        Normalize scores to a scale of 0-10.
        
        Args:
            scores_dict: Dictionary of scores
            
        Returns:
            dict: Normalized scores
        """
        if not scores_dict:
            return {}
        
        # Get max score
        max_score = max(scores_dict.values())
        
        # If max score is 0, return empty dict
        if max_score == 0:
            return scores_dict
        
        # Normalize scores
        normalized_scores = {}
        for key, value in scores_dict.items():
            normalized_scores[key] = round((value / max_score) * 10, 1)
        
        return normalized_scores
    
    @staticmethod
    def _get_primary_secondary(scores_dict):
        """
        Get primary and secondary types based on scores.
        
        Args:
            scores_dict: Dictionary of scores
            
        Returns:
            tuple: (primary_type, secondary_type)
        """
        if not scores_dict:
            return (None, None)
        
        # Sort scores by value in descending order
        sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Get primary and secondary types
        primary = sorted_scores[0][0] if len(sorted_scores) > 0 else None
        secondary = sorted_scores[1][0] if len(sorted_scores) > 1 else None
        
        return (primary, secondary)
    
    @staticmethod
    def _determine_ideal_environment(learning_style_scores, behavior_pattern_scores):
        """
        Determine ideal learning environment based on learning styles and behavior patterns.
        
        Args:
            learning_style_scores: Dictionary of learning style scores
            behavior_pattern_scores: Dictionary of behavior pattern scores
            
        Returns:
            dict: Ideal learning environment characteristics
        """
        environment = {}
        
        # Structure preference (structured vs. unstructured)
        structure_score = 0
        if 'logical' in learning_style_scores:
            structure_score += learning_style_scores['logical'] * 0.7
        if 'organization' in behavior_pattern_scores:
            structure_score += behavior_pattern_scores['organization'] * 0.3
        
        if structure_score > 7:
            environment['structure'] = 'Highly structured'
        elif structure_score > 5:
            environment['structure'] = 'Moderately structured'
        else:
            environment['structure'] = 'Flexible and unstructured'
        
        # Social preference (independent vs. group)
        social_score = 0
        if 'social' in learning_style_scores:
            social_score += learning_style_scores['social'] * 0.6
        if 'collaboration' in behavior_pattern_scores:
            social_score += behavior_pattern_scores['collaboration'] * 0.4
        
        if social_score > 7:
            environment['social'] = 'Collaborative group settings'
        elif social_score > 5:
            environment['social'] = 'Balance of group and independent work'
        else:
            environment['social'] = 'Independent study'
        
        # Pace preference (self-paced vs. scheduled)
        pace_score = 0
        if 'independence' in behavior_pattern_scores:
            pace_score += behavior_pattern_scores['independence'] * 0.5
        if 'adaptability' in behavior_pattern_scores:
            pace_score += behavior_pattern_scores['adaptability'] * 0.5
        
        if pace_score > 7:
            environment['pace'] = 'Self-paced learning'
        elif pace_score > 5:
            environment['pace'] = 'Flexible deadlines with guidance'
        else:
            environment['pace'] = 'Structured schedule with clear deadlines'
        
        # Feedback preference (immediate vs. reflective)
        feedback_score = 0
        if 'confidence' in behavior_pattern_scores:
            feedback_score += (10 - behavior_pattern_scores['confidence']) * 0.7
        if 'risk_taking' in behavior_pattern_scores:
            feedback_score += behavior_pattern_scores['risk_taking'] * 0.3
        
        if feedback_score > 7:
            environment['feedback'] = 'Frequent, immediate feedback'
        elif feedback_score > 5:
            environment['feedback'] = 'Regular check-ins with constructive feedback'
        else:
            environment['feedback'] = 'Space for self-reflection with periodic guidance'
        
        return environment
    
    @staticmethod
    def _generate_learning_tips(primary_learning_style, primary_cognitive_strength):
        """
        Generate learning effectiveness tips based on primary learning style and cognitive strength.
        
        Args:
            primary_learning_style: Primary learning style
            primary_cognitive_strength: Primary cognitive strength
            
        Returns:
            list: Learning effectiveness tips
        """
        tips = []
        
        # Learning style tips
        if primary_learning_style == 'visual':
            tips.append("Use diagrams, charts, and mind maps to visualize concepts")
            tips.append("Color-code notes and study materials")
            tips.append("Watch educational videos and demonstrations")
        elif primary_learning_style == 'auditory':
            tips.append("Record lectures and listen to them again")
            tips.append("Read material aloud or use text-to-speech")
            tips.append("Discuss concepts with others to reinforce understanding")
        elif primary_learning_style == 'kinesthetic':
            tips.append("Use hands-on activities and experiments")
            tips.append("Take breaks for physical movement during study sessions")
            tips.append("Create physical models or use manipulatives")
        elif primary_learning_style == 'logical':
            tips.append("Organize information in logical sequences or hierarchies")
            tips.append("Look for patterns and relationships between concepts")
            tips.append("Break complex problems into smaller, manageable steps")
        elif primary_learning_style == 'social':
            tips.append("Form or join study groups")
            tips.append("Teach concepts to others to reinforce understanding")
            tips.append("Engage in class discussions and collaborative projects")
        elif primary_learning_style == 'solitary':
            tips.append("Create a quiet, distraction-free study environment")
            tips.append("Set personal goals and track progress")
            tips.append("Use self-paced learning resources")
        
        # Cognitive strength tips
        if primary_cognitive_strength == 'memory':
            tips.append("Use spaced repetition techniques for memorization")
            tips.append("Create mnemonic devices for complex information")
        elif primary_cognitive_strength == 'attention':
            tips.append("Use the Pomodoro technique (focused work with short breaks)")
            tips.append("Minimize distractions in your study environment")
        elif primary_cognitive_strength == 'problem_solving':
            tips.append("Practice with a variety of problem types")
            tips.append("Analyze worked examples before attempting new problems")
        elif primary_cognitive_strength == 'creativity':
            tips.append("Explore multiple approaches to assignments")
            tips.append("Connect concepts across different subjects")
        elif primary_cognitive_strength == 'critical_thinking':
            tips.append("Question assumptions and evaluate evidence")
            tips.append("Compare and contrast different perspectives")
        
        return tips
