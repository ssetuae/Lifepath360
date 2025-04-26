import os
import openai
from dotenv import load_dotenv
from .models import Assessment
from .learning_style_analyzer import LearningStyleAnalyzer

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

class CourseRecommender:
    """
    Class for recommending courses based on assessment results.
    """
    
    # Course categories
    COURSE_CATEGORIES = [
        'math', 'coding', 'robotics', 'ai', 'entrepreneurship', 
        'communication', 'creative_arts', 'science', 'language',
        'vedic_math', 'abacus'
    ]
    
    @staticmethod
    def get_course_recommendations(assessment_id, num_recommendations=3):
        """
        Get course recommendations based on assessment results.
        
        Args:
            assessment_id: ID of the assessment
            num_recommendations: Number of recommendations to return
            
        Returns:
            dict: Course recommendations
        """
        try:
            # Get analysis results
            analysis_results = LearningStyleAnalyzer.analyze_assessment(assessment_id)
            
            if 'error' in analysis_results:
                return {
                    'error': analysis_results['error'],
                    'assessment_id': assessment_id
                }
            
            # Get student information
            student = analysis_results['student_name']
            grade = analysis_results['grade']
            
            # Get learning styles, cognitive strengths, and interests
            learning_styles = analysis_results['learning_styles']['scores']
            cognitive_strengths = analysis_results['cognitive_strengths']['scores']
            interests = analysis_results['interests']['scores']
            
            # Generate recommendations using AI
            recommendations = CourseRecommender._generate_ai_recommendations(
                student, grade, learning_styles, cognitive_strengths, interests, num_recommendations
            )
            
            return {
                'assessment_id': assessment_id,
                'student_name': student,
                'grade': grade,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'error': f'Error generating course recommendations: {str(e)}',
                'assessment_id': assessment_id
            }
    
    @staticmethod
    def _generate_ai_recommendations(student, grade, learning_styles, cognitive_strengths, interests, num_recommendations):
        """
        Generate course recommendations using AI.
        
        Args:
            student: Student name
            grade: Student grade
            learning_styles: Learning style scores
            cognitive_strengths: Cognitive strength scores
            interests: Interest scores
            num_recommendations: Number of recommendations to return
            
        Returns:
            list: Course recommendations
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Generate {num_recommendations} personalized course recommendations for a student based on their assessment results.
            
            Student: {student}
            Grade: {grade}
            
            Learning Style Scores:
            {learning_styles}
            
            Cognitive Strength Scores:
            {cognitive_strengths}
            
            Interest Scores:
            {interests}
            
            For each recommendation, provide:
            1. Course name
            2. Course category (from: math, coding, robotics, ai, entrepreneurship, communication, creative_arts, science, language, vedic_math, abacus)
            3. Description of the course
            4. Why it's a good fit for this student (based on their learning style, cognitive strengths, and interests)
            5. Learning outcomes
            6. Difficulty level (beginner, intermediate, advanced)
            7. Recommended age range
            8. Duration (in weeks)
            
            Format your response as a JSON array of course objects.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational advisor specializing in K-12 course recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
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
                # If not in code blocks, try to extract the entire JSON array
                json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', content)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = content
            
            try:
                # Parse the JSON
                recommendations = json.loads(json_str)
                
                # Add three-step learning journey for each recommendation
                for recommendation in recommendations:
                    recommendation['learning_journey'] = CourseRecommender._generate_learning_journey(
                        recommendation['course_name'], 
                        recommendation['category'], 
                        grade
                    )
                
                # Add future career and college affinities
                career_college_affinities = CourseRecommender._generate_career_college_affinities(
                    interests, cognitive_strengths
                )
                
                # Add global examination recommendations
                global_exams = CourseRecommender._generate_global_exam_recommendations(
                    grade, interests, cognitive_strengths
                )
                
                # Combine all recommendations
                result = {
                    'courses': recommendations,
                    'career_college_affinities': career_college_affinities,
                    'global_exams': global_exams
                }
                
                return result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default recommendation
                return CourseRecommender._generate_default_recommendations(grade)
                
        except Exception as e:
            print(f"Error generating AI recommendations: {str(e)}")
            return CourseRecommender._generate_default_recommendations(grade)
    
    @staticmethod
    def _generate_learning_journey(course_name, category, grade):
        """
        Generate a three-step learning journey for a course.
        
        Args:
            course_name: Name of the course
            category: Course category
            grade: Student grade
            
        Returns:
            dict: Three-step learning journey
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Generate a 3-step learning journey for a student in grade {grade} taking a course in {category} called "{course_name}".
            
            For each step, provide:
            1. Step name/title
            2. Description of what will be learned
            3. Skills that will be developed
            4. Approximate duration
            5. How this step builds toward the next
            
            Step 1 should be entry-level to build strength.
            Step 2 should be intermediate skill-expansion.
            Step 3 should be advanced or specialized with real-world application.
            
            Format your response as a JSON object with three steps.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational curriculum designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
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
                journey = json.loads(json_str)
                return journey
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default journey
                return {
                    "step1": {
                        "title": "Introduction to " + course_name,
                        "description": "Foundational concepts and basic skills",
                        "skills": ["Basic understanding", "Fundamental techniques", "Core principles"],
                        "duration": "4 weeks",
                        "progression": "Builds a strong foundation for more advanced concepts"
                    },
                    "step2": {
                        "title": "Expanding " + course_name + " Skills",
                        "description": "Intermediate concepts and applied techniques",
                        "skills": ["Problem-solving", "Applied knowledge", "Project work"],
                        "duration": "6 weeks",
                        "progression": "Develops practical application of foundational knowledge"
                    },
                    "step3": {
                        "title": "Advanced " + course_name + " Mastery",
                        "description": "Specialized techniques and real-world applications",
                        "skills": ["Advanced techniques", "Independent projects", "Real-world application"],
                        "duration": "8 weeks",
                        "progression": "Culminates in mastery and practical application"
                    }
                }
                
        except Exception as e:
            print(f"Error generating learning journey: {str(e)}")
            return {
                "step1": {
                    "title": "Introduction to " + course_name,
                    "description": "Foundational concepts and basic skills",
                    "skills": ["Basic understanding", "Fundamental techniques", "Core principles"],
                    "duration": "4 weeks",
                    "progression": "Builds a strong foundation for more advanced concepts"
                },
                "step2": {
                    "title": "Expanding " + course_name + " Skills",
                    "description": "Intermediate concepts and applied techniques",
                    "skills": ["Problem-solving", "Applied knowledge", "Project work"],
                    "duration": "6 weeks",
                    "progression": "Develops practical application of foundational knowledge"
                },
                "step3": {
                    "title": "Advanced " + course_name + " Mastery",
                    "description": "Specialized techniques and real-world applications",
                    "skills": ["Advanced techniques", "Independent projects", "Real-world application"],
                    "duration": "8 weeks",
                    "progression": "Culminates in mastery and practical application"
                }
            }
    
    @staticmethod
    def _generate_career_college_affinities(interests, cognitive_strengths):
        """
        Generate career and college affinities based on interests and cognitive strengths.
        
        Args:
            interests: Interest scores
            cognitive_strengths: Cognitive strength scores
            
        Returns:
            dict: Career and college affinities
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Based on the student's interests and cognitive strengths, suggest potential future career paths and college program affinities.
            
            Interest Scores:
            {interests}
            
            Cognitive Strength Scores:
            {cognitive_strengths}
            
            Please provide:
            1. 5 potential career paths that align with these interests and strengths
            2. 3 types of college programs that would be a good fit
            3. A brief explanation of why each is recommended
            
            Format your response as a JSON object with "careers" and "college_programs" arrays.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor and educational advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
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
                affinities = json.loads(json_str)
                return affinities
            except json.JSONDecodeError:
                # If JSON parsing fails, return default affinities
                return {
                    "careers": [
                        {
                            "title": "Software Developer",
                            "description": "Creating computer applications and systems"
                        },
                        {
                            "title": "Data Scientist",
                            "description": "Analyzing and interpreting complex data"
                        },
                        {
                            "title": "Robotics Engineer",
                            "description": "Designing and building robots and robotic systems"
                        },
                        {
                            "title": "AI Specialist",
                            "description": "Developing artificial intelligence solutions"
                        },
                        {
                            "title": "Entrepreneur",
                            "description": "Starting and running innovative businesses"
                        }
                    ],
                    "college_programs": [
                        {
                            "name": "Computer Science",
                            "description": "Study of computation, programming, and algorithm design"
                        },
                        {
                            "name": "Engineering",
                            "description": "Application of scientific and mathematical principles to solve problems"
                        },
                        {
                            "name": "Business and Entrepreneurship",
                            "description": "Study of business management and entrepreneurial skills"
                        }
                    ]
                }
                
        except Exception as e:
            print(f"Error generating career and college affinities: {str(e)}")
            return {
                "careers": [
                    {
                        "title": "Software Developer",
                        "description": "Creating computer applications and systems"
                    },
                    {
                        "title": "Data Scientist",
                        "description": "Analyzing and interpreting complex data"
                    },
                    {
                        "title": "Robotics Engineer",
                        "description": "Designing and building robots and robotic systems"
                    },
                    {
                        "title": "AI Specialist",
                        "description": "Developing artificial intelligence solutions"
                    },
                    {
                        "title": "Entrepreneur",
                        "description": "Starting and running innovative businesses"
                    }
                ],
                "college_programs": [
                    {
                        "name": "Computer Science",
                        "description": "Study of computation, programming, and algorithm design"
                    },
                    {
                        "name": "Engineering",
                        "description": "Application of scientific and mathematical principles to solve problems"
                    },
                    {
                        "name": "Business and Entrepreneurship",
                        "description": "Study of business management and entrepreneurial skills"
                    }
                ]
            }
    
    @staticmethod
    def _generate_global_exam_recommendations(grade, interests, cognitive_strengths):
        """
        Generate recommendations for global examinations and aptitude tests.
        
        Args:
            grade: Student grade
            interests: Interest scores
            cognitive_strengths: Cognitive strength scores
            
        Returns:
            list: Global examination recommendations
        """
        try:
            # Create prompt for OpenAI
            prompt = f"""
            Based on the student's grade ({grade}), interests, and cognitive strengths, recommend appropriate global examinations and aptitude tests they could participate in.
            
            Interest Scores:
            {interests}
            
            Cognitive Strength Scores:
            {cognitive_strengths}
            
            Please provide 3-5 recommended examinations or aptitude tests, including:
            1. Name of the examination/test
            2. Brief description
            3. Appropriate age/grade level
            4. Why it's recommended for this student
            5. Benefits of participating
            
            Format your response as a JSON array of examination objects.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in educational assessment and global examinations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
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
                # If not in code blocks, try to extract the entire JSON array
                json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', content)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = content
            
            try:
                # Parse the JSON
                exams = json.loads(json_str)
                return exams
            except json.JSONDecodeError:
                # If JSON parsing fails, return default exams
                return [
                    {
                        "name": "International Mathematics Olympiad (IMO)",
                        "description": "Global mathematics competition for pre-university students",
                        "grade_level": "Grade 7-12",
                        "recommendation_reason": "Excellent for students with strong logical and mathematical abilities",
                        "benefits": "Develops problem-solving skills, provides international recognition, and opens doors to scholarships"
                    },
                    {
                        "name": "Scratch Coding Competition",
                        "description": "Programming competition using the Scratch platform",
                        "grade_level": "Grade 3-8",
                        "recommendation_reason": "Great for students interested in coding and creative technology",
                        "benefits": "Develops computational thinking, creativity, and programming skills"
                    },
                    {
                        "name": "International Science Olympiad",
                        "description": "Competition testing knowledge in various scientific disciplines",
                        "grade_level": "Grade 1-12",
                        "recommendation_reason": "Ideal for students with strong scientific interests and analytical abilities",
                        "benefits": "Enhances scientific knowledge, critical thinking, and problem-solving skills"
                    }
                ]
                
        except Exception as e:
            print(f"Error generating global exam recommendations: {str(e)}")
            return [
                {
                    "name": "International Mathematics Olympiad (IMO)",
                    "description": "Global mathematics competition for pre-university students",
                    "grade_level": "Grade 7-12",
                    "recommendation_reason": "Excellent for students with strong logical and mathematical abilities",
                    "benefits": "Develops problem-solving skills, provides international recognition, and opens doors to scholarships"
                },
                {
                    "name": "Scratch Coding Competition",
                    "description": "Programming competition using the Scratch platform",
                    "grade_level": "Grade 3-8",
                    "recommendation_reason": "Great for students interested in coding and creative technology",
                    "benefits": "Develops computational thinking, creativity, and programming skills"
                },
                {
                    "name": "International Science Olympiad",
                    "description": "Competition testing knowledge in various scientific disciplines",
                    "grade_level": "Grade 1-12",
                    "recommendation_reason": "Ideal for students with strong scientific interests and analytical abilities",
                    "benefits": "Enhances scientific knowledge, critical thinking, and problem-solving skills"
                }
            ]
    
    @staticmethod
    def _generate_default_recommendations(grade):
        """
        Generate default course recommendations based on grade level.
        
        Args:
            grade: Student grade
            
        Returns:
            dict: Default course recommendations
        """
        # Convert grade to numeric value for age approximation
        grade_map = {
            'K': 5,
            'G1': 6,
            'G2': 7,
            'G3': 8,
            'G4': 9,
            'G5': 10,
            'G6': 11,
            'G7': 12,
            'G8': 13,
            'G9': 14,
            'G10': 15,
            'G11': 16,
            'G12': 17
        }
        
        age = grade_map.get(grade, 10)
        
        # Default recommendations based on age/grade
        if age <= 7:  # K-G2
            courses = [
                {
                    "course_name": "Junior Coding Adventures",
                    "category": "coding",
                    "description": "An introductory coding course for young learners using block-based programming.",
                    "fit_reason": "Perfect for developing logical thinking and creativity in early learners.",
                    "learning_outcomes": ["Basic coding concepts", "Problem-solving skills", "Sequential thinking"],
                    "difficulty": "beginner",
                    "age_range": "5-7 years",
                    "duration": "8 weeks"
                },
                {
                    "course_name": "Math Explorers",
                    "category": "math",
                    "description": "A fun, hands-on approach to early mathematics concepts.",
                    "fit_reason": "Builds a strong foundation in mathematical thinking through play-based learning.",
                    "learning_outcomes": ["Number sense", "Basic operations", "Spatial reasoning"],
                    "difficulty": "beginner",
                    "age_range": "5-7 years",
                    "duration": "10 weeks"
                },
                {
                    "course_name": "Creative Storytelling",
                    "category": "creative_arts",
                    "description": "A course that develops imagination and communication through storytelling.",
                    "fit_reason": "Enhances creativity and language skills in a supportive environment.",
                    "learning_outcomes": ["Narrative skills", "Vocabulary development", "Creative expression"],
                    "difficulty": "beginner",
                    "age_range": "5-7 years",
                    "duration": "6 weeks"
                }
            ]
        elif age <= 10:  # G3-G5
            courses = [
                {
                    "course_name": "Scratch Programming Fundamentals",
                    "category": "coding",
                    "description": "Learn to code using Scratch to create interactive stories and games.",
                    "fit_reason": "Develops computational thinking and creativity through visual programming.",
                    "learning_outcomes": ["Basic programming concepts", "Game design", "Interactive storytelling"],
                    "difficulty": "beginner",
                    "age_range": "8-10 years",
                    "duration": "12 weeks"
                },
                {
                    "course_name": "Abacus Math Mastery",
                    "category": "abacus",
                    "description": "Learn mental math techniques using the abacus method.",
                    "fit_reason": "Enhances calculation speed, concentration, and numerical fluency.",
                    "learning_outcomes": ["Mental calculation", "Number manipulation", "Concentration skills"],
                    "difficulty": "intermediate",
                    "age_range": "8-10 years",
                    "duration": "16 weeks"
                },
                {
                    "course_name": "Junior Robotics",
                    "category": "robotics",
                    "description": "Introduction to robotics using LEGO WeDo or similar platforms.",
                    "fit_reason": "Combines coding with hands-on building to develop STEM skills.",
                    "learning_outcomes": ["Basic robotics concepts", "Simple programming", "Engineering principles"],
                    "difficulty": "beginner",
                    "age_range": "8-10 years",
                    "duration": "10 weeks"
                }
            ]
        elif age <= 13:  # G6-G8
            courses = [
                {
                    "course_name": "Python Programming for Beginners",
                    "category": "coding",
                    "description": "Introduction to text-based programming using Python.",
                    "fit_reason": "Transitions from block-based to text-based coding with a versatile language.",
                    "learning_outcomes": ["Python syntax", "Program structure", "Basic algorithms"],
                    "difficulty": "intermediate",
                    "age_range": "11-13 years",
                    "duration": "14 weeks"
                },
                {
                    "course_name": "Vedic Mathematics",
                    "category": "vedic_math",
                    "description": "Ancient Indian mathematical techniques for rapid calculation.",
                    "fit_reason": "Enhances mathematical fluency and provides alternative problem-solving approaches.",
                    "learning_outcomes": ["Speed mathematics", "Mental calculation", "Alternative algorithms"],
                    "difficulty": "intermediate",
                    "age_range": "11-13 years",
                    "duration": "12 weeks"
                },
                {
                    "course_name": "LEGO Robotics Engineering",
                    "category": "robotics",
                    "description": "Design, build, and program robots using LEGO Mindstorms.",
                    "fit_reason": "Develops engineering skills and computational thinking through hands-on projects.",
                    "learning_outcomes": ["Mechanical design", "Sensor integration", "Programming logic"],
                    "difficulty": "intermediate",
                    "age_range": "11-13 years",
                    "duration": "16 weeks"
                }
            ]
        else:  # G9-G12
            courses = [
                {
                    "course_name": "Advanced Programming with Python",
                    "category": "coding",
                    "description": "Develop sophisticated applications and algorithms using Python.",
                    "fit_reason": "Builds on programming fundamentals to create complex, real-world applications.",
                    "learning_outcomes": ["Object-oriented programming", "Data structures", "Algorithm design"],
                    "difficulty": "advanced",
                    "age_range": "14-17 years",
                    "duration": "16 weeks"
                },
                {
                    "course_name": "Introduction to AI and Machine Learning",
                    "category": "ai",
                    "description": "Explore the fundamentals of artificial intelligence and machine learning.",
                    "fit_reason": "Introduces cutting-edge technology concepts with practical applications.",
                    "learning_outcomes": ["AI concepts", "Basic ML algorithms", "Ethical considerations"],
                    "difficulty": "advanced",
                    "age_range": "14-17 years",
                    "duration": "14 weeks"
                },
                {
                    "course_name": "Young Entrepreneurs",
                    "category": "entrepreneurship",
                    "description": "Learn to develop business ideas and create a business plan.",
                    "fit_reason": "Develops business acumen, creativity, and presentation skills.",
                    "learning_outcomes": ["Business planning", "Marketing basics", "Financial literacy"],
                    "difficulty": "intermediate",
                    "age_range": "14-17 years",
                    "duration": "12 weeks"
                }
            ]
        
        # Add learning journeys to each course
        for course in courses:
            course['learning_journey'] = {
                "step1": {
                    "title": "Introduction to " + course['course_name'],
                    "description": "Foundational concepts and basic skills",
                    "skills": ["Basic understanding", "Fundamental techniques", "Core principles"],
                    "duration": "4 weeks",
                    "progression": "Builds a strong foundation for more advanced concepts"
                },
                "step2": {
                    "title": "Expanding " + course['course_name'] + " Skills",
                    "description": "Intermediate concepts and applied techniques",
                    "skills": ["Problem-solving", "Applied knowledge", "Project work"],
                    "duration": "6 weeks",
                    "progression": "Develops practical application of foundational knowledge"
                },
                "step3": {
                    "title": "Advanced " + course['course_name'] + " Mastery",
                    "description": "Specialized techniques and real-world applications",
                    "skills": ["Advanced techniques", "Independent projects", "Real-world application"],
                    "duration": "8 weeks",
                    "progression": "Culminates in mastery and practical application"
                }
            }
        
        # Default career and college affinities
        career_college_affinities = {
            "careers": [
                {
                    "title": "Software Developer",
                    "description": "Creating computer applications and systems"
                },
                {
                    "title": "Data Scientist",
                    "description": "Analyzing and interpreting complex data"
                },
                {
                    "title": "Robotics Engineer",
                    "description": "Designing and building robots and robotic systems"
                },
                {
                    "title": "AI Specialist",
                    "description": "Developing artificial intelligence solutions"
                },
                {
                    "title": "Entrepreneur",
                    "description": "Starting and running innovative businesses"
                }
            ],
            "college_programs": [
                {
                    "name": "Computer Science",
                    "description": "Study of computation, programming, and algorithm design"
                },
                {
                    "name": "Engineering",
                    "description": "Application of scientific and mathematical principles to solve problems"
                },
                {
                    "name": "Business and Entrepreneurship",
                    "description": "Study of business management and entrepreneurial skills"
                }
            ]
        }
        
        # Default global exams
        global_exams = [
            {
                "name": "International Mathematics Olympiad (IMO)",
                "description": "Global mathematics competition for pre-university students",
                "grade_level": "Grade 7-12",
                "recommendation_reason": "Excellent for students with strong logical and mathematical abilities",
                "benefits": "Develops problem-solving skills, provides international recognition, and opens doors to scholarships"
            },
            {
                "name": "Scratch Coding Competition",
                "description": "Programming competition using the Scratch platform",
                "grade_level": "Grade 3-8",
                "recommendation_reason": "Great for students interested in coding and creative technology",
                "benefits": "Develops computational thinking, creativity, and programming skills"
            },
            {
                "name": "International Science Olympiad",
                "description": "Competition testing knowledge in various scientific disciplines",
                "grade_level": "Grade 1-12",
                "recommendation_reason": "Ideal for students with strong scientific interests and analytical abilities",
                "benefits": "Enhances scientific knowledge, critical thinking, and problem-solving skills"
            }
        ]
        
        return {
            'courses': courses,
            'career_college_affinities': career_college_affinities,
            'global_exams': global_exams
        }
