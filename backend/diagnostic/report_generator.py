import os
import tempfile
from datetime import datetime
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.conf import settings
from .models import Assessment
from .learning_style_analyzer import LearningStyleAnalyzer

class ReportGenerator:
    """
    Class for generating PDF reports based on assessment results.
    """
    
    @staticmethod
    def generate_summary_report(assessment_id):
        """
        Generate a free summary PDF report for an assessment.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Check if assessment is completed
            if assessment.status != Assessment.Status.COMPLETED:
                return None
            
            # Get analysis results
            analysis_results = LearningStyleAnalyzer.analyze_assessment(assessment_id)
            
            if 'error' in analysis_results:
                return None
            
            # Create context for template
            context = {
                'assessment': assessment,
                'student': assessment.student,
                'analysis': analysis_results,
                'date': datetime.now().strftime('%B %d, %Y'),
                'report_type': 'summary'
            }
            
            # Render HTML template
            html_string = render_to_string('diagnostic/summary_report_template.html', context)
            
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                # Generate PDF
                HTML(string=html_string).write_pdf(
                    tmp.name,
                    stylesheets=[
                        CSS(string='@page { size: letter; margin: 1cm }')
                    ]
                )
                
                return tmp.name
                
        except Assessment.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error generating summary report: {str(e)}")
            return None
    
    @staticmethod
    def generate_detailed_report(assessment_id):
        """
        Generate a detailed PDF report for an assessment.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Check if assessment is completed
            if assessment.status != Assessment.Status.COMPLETED:
                return None
            
            # Get analysis results
            analysis_results = LearningStyleAnalyzer.analyze_assessment(assessment_id)
            
            if 'error' in analysis_results:
                return None
            
            # Create context for template
            context = {
                'assessment': assessment,
                'student': assessment.student,
                'analysis': analysis_results,
                'date': datetime.now().strftime('%B %d, %Y'),
                'report_type': 'detailed'
            }
            
            # Render HTML template
            html_string = render_to_string('diagnostic/detailed_report_template.html', context)
            
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                # Generate PDF
                HTML(string=html_string).write_pdf(
                    tmp.name,
                    stylesheets=[
                        CSS(string='@page { size: letter; margin: 1cm }')
                    ]
                )
                
                return tmp.name
                
        except Assessment.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error generating detailed report: {str(e)}")
            return None
    
    @staticmethod
    def create_report_templates():
        """
        Create HTML templates for PDF reports.
        """
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'diagnostic')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create summary report template
        summary_template_path = os.path.join(templates_dir, 'summary_report_template.html')
        with open(summary_template_path, 'w') as f:
            f.write(ReportGenerator._get_summary_template())
        
        # Create detailed report template
        detailed_template_path = os.path.join(templates_dir, 'detailed_report_template.html')
        with open(detailed_template_path, 'w') as f:
            f.write(ReportGenerator._get_detailed_template())
    
    @staticmethod
    def _get_summary_template():
        """
        Get HTML template for summary report.
        
        Returns:
            str: HTML template
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Learning Compass - Summary Report</title>
            <style>
                body {
                    font-family: "Noto Sans CJK SC", "WenQuanYi Zen Hei", Arial, sans-serif;
                    color: #333;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }
                .header {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .logo {
                    max-width: 200px;
                    margin-bottom: 10px;
                }
                .container {
                    padding: 20px;
                }
                .section {
                    margin-bottom: 30px;
                }
                h1, h2, h3 {
                    color: #4a6fa5;
                }
                h1 {
                    font-size: 24px;
                    margin: 0;
                }
                h2 {
                    font-size: 20px;
                    border-bottom: 2px solid #4a6fa5;
                    padding-bottom: 5px;
                }
                h3 {
                    font-size: 18px;
                }
                .student-info {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .student-info p {
                    margin: 5px 0;
                }
                .chart-container {
                    width: 100%;
                    height: 300px;
                    margin: 20px 0;
                }
                .badge {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 10px;
                }
                .footer {
                    text-align: center;
                    font-size: 12px;
                    color: #777;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                .bar-chart {
                    width: 100%;
                    margin: 15px 0;
                }
                .bar-container {
                    width: 100%;
                    background-color: #f1f1f1;
                    margin-bottom: 5px;
                    position: relative;
                    height: 25px;
                }
                .bar {
                    height: 25px;
                    background-color: #4a6fa5;
                }
                .bar-label {
                    position: absolute;
                    top: 3px;
                    left: 5px;
                    color: white;
                }
                .bar-value {
                    position: absolute;
                    top: 3px;
                    right: 5px;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Learning Compass</h1>
                <p>Summary Assessment Report</p>
            </div>
            
            <div class="container">
                <div class="student-info">
                    <h2>Student Information</h2>
                    <p><strong>Name:</strong> {{ student.first_name }} {{ student.last_name }}</p>
                    <p><strong>Grade:</strong> {{ student.get_grade_display }}</p>
                    <p><strong>Assessment Date:</strong> {{ assessment.end_time|date:"F d, Y" }}</p>
                    <p><strong>Report Generated:</strong> {{ date }}</p>
                </div>
                
                <div class="section">
                    <h2>Learning Style Profile</h2>
                    <p>Your primary learning style is <strong>{{ analysis.learning_styles.primary|title }}</strong> with a secondary preference for <strong>{{ analysis.learning_styles.secondary|title }}</strong> learning.</p>
                    
                    <div class="bar-chart">
                        {% for style, score in analysis.learning_styles.scores.items %}
                        <div class="bar-container">
                            <div class="bar" style="width: {{ score }}0%;"></div>
                            <span class="bar-label">{{ style|title }}</span>
                            <span class="bar-value">{{ score }}/10</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Cognitive Strengths</h2>
                    <p>Your primary cognitive strength is <strong>{{ analysis.cognitive_strengths.primary|title }}</strong>.</p>
                    
                    <div class="bar-chart">
                        {% for strength, score in analysis.cognitive_strengths.scores.items %}
                        <div class="bar-container">
                            <div class="bar" style="width: {{ score }}0%;"></div>
                            <span class="bar-label">{{ strength|title }}</span>
                            <span class="bar-value">{{ score }}/10</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Ideal Learning Environment</h2>
                    <table>
                        <tr>
                            <th>Structure</th>
                            <td>{{ analysis.ideal_learning_environment.structure }}</td>
                        </tr>
                        <tr>
                            <th>Social Setting</th>
                            <td>{{ analysis.ideal_learning_environment.social }}</td>
                        </tr>
                        <tr>
                            <th>Pace</th>
                            <td>{{ analysis.ideal_learning_environment.pace }}</td>
                        </tr>
                        <tr>
                            <th>Feedback</th>
                            <td>{{ analysis.ideal_learning_environment.feedback }}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="section">
                    <h2>Learning Badge</h2>
                    <div class="badge">
                        {% if analysis.learning_styles.primary == 'visual' %}
                            Visual Voyager
                        {% elif analysis.learning_styles.primary == 'auditory' %}
                            Sound Scholar
                        {% elif analysis.learning_styles.primary == 'kinesthetic' %}
                            Hands-On Hero
                        {% elif analysis.learning_styles.primary == 'logical' %}
                            Logic Legend
                        {% elif analysis.learning_styles.primary == 'social' %}
                            Team Thinker
                        {% elif analysis.learning_styles.primary == 'solitary' %}
                            Solo Scholar
                        {% else %}
                            Learning Explorer
                        {% endif %}
                    </div>
                    <p>For a more comprehensive analysis and personalized recommendations, please request the detailed report.</p>
                </div>
                
                <div class="footer">
                    <p>This report was generated by Learning Compass, a product of Shining Star Education Training LLC.</p>
                    <p>© {{ date|slice:"-4:" }} Shining Star Education Training LLC. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_detailed_template():
        """
        Get HTML template for detailed report.
        
        Returns:
            str: HTML template
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Learning Compass - Detailed Report</title>
            <style>
                body {
                    font-family: "Noto Sans CJK SC", "WenQuanYi Zen Hei", Arial, sans-serif;
                    color: #333;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }
                .header {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .logo {
                    max-width: 200px;
                    margin-bottom: 10px;
                }
                .container {
                    padding: 20px;
                }
                .section {
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }
                h1, h2, h3, h4 {
                    color: #4a6fa5;
                }
                h1 {
                    font-size: 24px;
                    margin: 0;
                }
                h2 {
                    font-size: 20px;
                    border-bottom: 2px solid #4a6fa5;
                    padding-bottom: 5px;
                    margin-top: 30px;
                }
                h3 {
                    font-size: 18px;
                }
                h4 {
                    font-size: 16px;
                }
                .student-info {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .student-info p {
                    margin: 5px 0;
                }
                .chart-container {
                    width: 100%;
                    height: 300px;
                    margin: 20px 0;
                }
                .badge {
                    background-color: #4a6fa5;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 10px;
                }
                .footer {
                    text-align: center;
                    font-size: 12px;
                    color: #777;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                .bar-chart {
                    width: 100%;
                    margin: 15px 0;
                }
                .bar-container {
                    width: 100%;
                    background-color: #f1f1f1;
                    margin-bottom: 5px;
                    position: relative;
                    height: 25px;
                }
                .bar {
                    height: 25px;
                    background-color: #4a6fa5;
                }
                .bar-label {
                    position: absolute;
                    top: 3px;
                    left: 5px;
                    color: white;
                }
                .bar-value {
                    position: absolute;
                    top: 3px;
                    right: 5px;
                    color: #333;
                }
                .tip-box {
                    background-color: #e8f4f8;
                    border-left: 4px solid #4a6fa5;
                    padding: 10px 15px;
                    margin: 15px 0;
                }
                .quote {
                    font-style: italic;
                    color: #555;
                    padding: 10px 20px;
                    border-left: 3px solid #4a6fa5;
                    margin: 15px 0;
                }
                .page-break {
                    page-break-after: always;
                }
                .two-column {
                    display: flex;
                    justify-content: space-between;
                }
                .column {
                    width: 48%;
                }
                .highlight-box {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }
                .career-box {
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .course-box {
                    background-color: #e8f4f8;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .pathway-step {
                    background-color: #f5f5f5;
                    border-left: 4px solid #4a6fa5;
                    padding: 10px 15px;
                    margin: 15px 0;
                }
                .cover-page {
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }
                .cover-title {
                    font-size: 32px;
                    color: #4a6fa5;
                    margin-bottom: 20px;
                }
                .cover-subtitle {
                    font-size: 20px;
                    color: #666;
                    margin-bottom: 40px;
                }
                .cover-info {
                    font-size: 18px;
                    margin-bottom: 10px;
                }
                .toc-item {
                    margin: 5px 0;
                }
                .toc-section {
                    font-weight: bold;
                    margin-top: 10px;
                }
                .toc-page {
                    float: right;
                }
            </style>
        </head>
        <body>
            <!-- Cover Page -->
            <div class="cover-page">
                <h1 class="cover-title">Learning Compass</h1>
                <h2 class="cover-subtitle">Comprehensive Learning Profile & Recommendation Report</h2>
                <p class="cover-info"><strong>Student:</strong> {{ student.first_name }} {{ student.last_name }}</p>
                <p class="cover-info"><strong>Grade:</strong> {{ student.get_grade_display }}</p>
                <p class="cover-info"><strong>Assessment Date:</strong> {{ assessment.end_time|date:"F d, Y" }}</p>
                <p class="cover-info"><strong>Report Generated:</strong> {{ date }}</p>
                <div class="badge" style="margin-top: 40px;">
                    {% if analysis.learning_styles.primary == 'visual' %}
                        Visual Voyager
                    {% elif analysis.learning_styles.primary == 'auditory' %}
                        Sound Scholar
                    {% elif analysis.learning_styles.primary == 'kinesthetic' %}
                        Hands-On Hero
                    {% elif analysis.learning_styles.primary == 'logical' %}
                        Logic Legend
                    {% elif analysis.learning_styles.primary == 'social' %}
                        Team Thinker
                    {% elif analysis.learning_styles.primary == 'solitary' %}
                        Solo Scholar
                    {% else %}
                        Learning Explorer
                    {% endif %}
                </div>
            </div>
            
            <div class="page-break"></div>
            
            <!-- Table of Contents -->
            <div class="container">
                <h2>Table of Contents</h2>
                <div class="toc-item toc-section">1. Introduction <span class="toc-page">3</span></div>
                <div class="toc-item">1.1 About This Report <span class="toc-page">3</span></div>
                <div class="toc-item">1.2 How to Use This Report <span class="toc-page">3</span></div>
                
                <div class="toc-item toc-section">2. Learning Style Profile <span class="toc-page">4</span></div>
                <div class="toc-item">2.1 Primary and Secondary Learning Styles <span class="toc-page">4</span></div>
                <div class="toc-item">2.2 Learning Style Breakdown <span class="toc-page">5</span></div>
                <div class="toc-item">2.3 What Your Learning Style Means <span class="toc-page">6</span></div>
                
                <div class="toc-item toc-section">3. Cognitive Strengths Assessment <span class="toc-page">7</span></div>
                <div class="toc-item">3.1 Cognitive Profile Overview <span class="toc-page">7</span></div>
                <div class="toc-item">3.2 Detailed Cognitive Analysis <span class="toc-page">8</span></div>
                <div class="toc-item">3.3 Leveraging Your Cognitive Strengths <span class="toc-page">9</span></div>
                
                <div class="toc-item toc-section">4. Behavior Patterns <span class="toc-page">10</span></div>
                <div class="toc-item">4.1 Behavior Profile Overview <span class="toc-page">10</span></div>
                <div class="toc-item">4.2 Detailed Behavior Analysis <span class="toc-page">11</span></div>
                <div class="toc-item">4.3 Behavioral Development Opportunities <span class="toc-page">12</span></div>
                
                <div class="toc-item toc-section">5. Interest Alignment <span class="toc-page">13</span></div>
                <div class="toc-item">5.1 Interest Profile Overview <span class="toc-page">13</span></div>
                <div class="toc-item">5.2 Detailed Interest Analysis <span class="toc-page">14</span></div>
                <div class="toc-item">5.3 Exploring Your Interests <span class="toc-page">15</span></div>
                
                <div class="toc-item toc-section">6. Ideal Learning Environment <span class="toc-page">16</span></div>
                <div class="toc-item">6.1 Environmental Preferences <span class="toc-page">16</span></div>
                <div class="toc-item">6.2 Creating Your Optimal Study Space <span class="toc-page">17</span></div>
                
                <div class="toc-item toc-section">7. Learning Effectiveness Strategies <span class="toc-page">18</span></div>
                <div class="toc-item">7.1 Personalized Learning Tips <span class="toc-page">18</span></div>
                <div class="toc-item">7.2 Study Techniques for Your Profile <span class="toc-page">19</span></div>
                
                <div class="toc-item toc-section">8. Future Career & College Affinities <span class="toc-page">20</span></div>
                <div class="toc-item">8.1 Career Path Suggestions <span class="toc-page">20</span></div>
                <div class="toc-item">8.2 College Program Recommendations <span class="toc-page">21</span></div>
                <div class="toc-item">8.3 Recommended Aptitude Exams <span class="toc-page">22</span></div>
                
                <div class="toc-item toc-section">9. Learning Pathway Mapping <span class="toc-page">23</span></div>
                <div class="toc-item">9.1 Three-Step Learning Journey <span class="toc-page">23</span></div>
                <div class="toc-item">9.2 Skill Development Roadmap <span class="toc-page">24</span></div>
                
                <div class="toc-item toc-section">10. Course Recommendations <span class="toc-page">25</span></div>
                <div class="toc-item">10.1 Recommended Shining Star Courses <span class="toc-page">25</span></div>
                <div class="toc-item">10.2 How These Courses Benefit You <span class="toc-page">26</span></div>
                
                <div class="toc-item toc-section">11. Next Steps <span class="toc-page">27</span></div>
                <div class="toc-item">11.1 Implementing Your Learning Plan <span class="toc-page">27</span></div>
                <div class="toc-item">11.2 Scheduling a Counseling Session <span class="toc-page">27</span></div>
            </div>
            
            <div class="page-break"></div>
            
            <!-- Introduction -->
            <div class="container">
                <h2>1. Introduction</h2>
                
                <div class="section">
                    <h3>1.1 About This Report</h3>
                    <p>This comprehensive report is based on your responses to the Learning Compass diagnostic assessment. The assessment evaluated your learning style, cognitive strengths, behavior patterns, and interests to create a personalized learning profile.</p>
                    
                    <p>The insights and recommendations in this report are designed to help you understand your unique learning preferences and strengths, and to provide guidance on how to leverage these to achieve academic success and personal growth.</p>
                    
                    <div class="quote">
                        "Understanding how you learn best is the first step toward maximizing your educational potential."
                    </div>
                </div>
                
                <div class="section">
                    <h3>1.2 How to Use This Report</h3>
                    <p>This report is a valuable resource that can help you:</p>
                    <ul>
                        <li>Understand your natural learning preferences and strengths</li>
                        <li>Identify effective study strategies tailored to your learning style</li>
                        <li>Create an optimal learning environment</li>
                        <li>Explore potential career paths and academic opportunities</li>
                        <li>Select courses and activities that align with your interests and strengths</li>
                    </ul>
                    
                    <p>We recommend reviewing this report with your parents, teachers, or academic advisors to discuss how to implement the recommendations in your educational journey.</p>
                </div>
            </div>
            
            <div class="page-break"></div>
            
            <!-- Learning Style Profile -->
            <div class="container">
                <h2>2. Learning Style Profile</h2>
                
                <div class="section">
                    <h3>2.1 Primary and Secondary Learning Styles</h3>
                    <p>Your assessment results indicate that your primary learning style is <strong>{{ analysis.learning_styles.primary|title }}</strong> with a secondary preference for <strong>{{ analysis.learning_styles.secondary|title }}</strong> learning.</p>
                    
                    <div class="highlight-box">
                        <h4>What is a {{ analysis.learning_styles.primary|title }} Learner?</h4>
                        {% if analysis.learning_styles.primary == 'visual' %}
                            <p>Visual learners process information best when it's presented in a graphic or pictorial format. You likely have a strong ability to visualize concepts and remember what you've seen. You may prefer diagrams, charts, maps, and written instructions.</p>
                        {% elif analysis.learning_styles.primary == 'auditory' %}
                            <p>Auditory learners process information best through listening and speaking. You likely remember information well when it's presented verbally and may benefit from discussions, lectures, and reading aloud. You may also enjoy music and have a good ear for language.</p>
                        {% elif analysis.learning_styles.primary == 'kinesthetic' %}
                            <p>Kinesthetic learners process information best through hands-on activities and physical experiences. You likely prefer to be actively engaged in learning and may have good coordination and spatial awareness. You may benefit from experiments, role-playing, and building models.</p>
                        {% elif analysis.learning_styles.primary == 'logical' %}
                            <p>Logical learners process information best through reasoning and systematic thinking. You likely excel at recognizing patterns, working with numbers, and solving problems step-by-step. You may prefer structured learning environments and clear objectives.</p>
                        {% elif analysis.learning_styles.primary == 'social' %}
                            <p>Social learners process information best in group settings and through interaction with others. You likely enjoy collaborative learning, discussions, and teamwork. You may be good at understanding others' perspectives and communicating your ideas.</p>
                        {% elif analysis.learning_styles.primary == 'solitary' %}
                            <p>Solitary learners process information best through independent study and self-reflection. You likely prefer to work alone and may be self-motivated and introspective. You may benefit from having quiet time to think and process information.</p>
                        {% endif %}
                    </div>
                </div>
                
                <div class="section">
                    <h3>2.2 Learning Style Breakdown</h3>
                    <p>The chart below shows your scores across different learning styles:</p>
                    
                    <div class="bar-chart">
                        {% for style, score in analysis.learning_styles.scores.items %}
                        <div class="bar-container">
                            <div class="bar" style="width: {{ score }}0%;"></div>
                            <span class="bar-label">{{ style|title }}</span>
                            <span class="bar-value">{{ score }}/10</span>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <p>This breakdown shows that while your primary learning style is {{ analysis.learning_styles.primary|title }}, you also have significant strengths in other learning modalities. This versatility can be advantageous in different learning situations.</p>
                </div>
                
                <div class="section">
                    <h3>2.3 What Your Learning Style Means</h3>
                    <p>Understanding your learning style can help you choose effective study strategies and learning environments. Here's what your learning style profile means for your education:</p>
                    
                    <div class="two-column">
                        <div class="column">
                            <h4>Strengths</h4>
                            <ul>
                                {% if analysis.learning_styles.primary == 'visual' %}
                                    <li>Strong visual memory and recall</li>
                                    <li>Ability to understand complex diagrams and charts</li>
                                    <li>Good spatial awareness and visualization skills</li>
                                    <li>Attention to visual details</li>
                                {% elif analysis.learning_styles.primary == 'auditory' %}
                                    <li>Strong listening skills and verbal memory</li>
                                    <li>Ability to follow verbal instructions</li>
                                    <li>Good language skills and vocabulary</li>
                                    <li>Effective verbal communication</li>
                                {% elif analysis.learning_styles.primary == 'kinesthetic' %}
                                    <li>Strong physical coordination and dexterity</li>
                                    <li>Hands-on problem-solving abilities</li>
                                    <li>Good physical memory and recall</li>
                                    <li>Practical application of concepts</li>
                                {% elif analysis.learning_styles.primary == 'logical' %}
                                    <li>Strong analytical and critical thinking</li>
                                    <li>Ability to recognize patterns and relationships</li>
                                    <li>Systematic problem-solving approach</li>
                                    <li>Good mathematical and scientific reasoning</li>
                                {% elif analysis.learning_styles.primary == 'social' %}
                                    <li>Strong interpersonal and communication skills</li>
                                    <li>Ability to work effectively in teams</li>
                                    <li>Good at understanding different perspectives</li>
                                    <li>Effective collaboration and leadership</li>
                                {% elif analysis.learning_styles.primary == 'solitary' %}
                                    <li>Strong self-discipline and focus</li>
                                    <li>Ability to work independently</li>
                                    <li>Good self-reflection and introspection</li>
                                    <li>Effective self-directed learning</li>
                                {% endif %}
                            </ul>
                        </div>
                        
                        <div class="column">
                            <h4>Potential Challenges</h4>
                            <ul>
                                {% if analysis.learning_styles.primary == 'visual' %}
                                    <li>May struggle with purely verbal instructions</li>
                                    <li>Could find it difficult to focus in visually distracting environments</li>
                                    <li>Might need to see information to process it fully</li>
                                {% elif analysis.learning_styles.primary == 'auditory' %}
                                    <li>May struggle with written instructions without verbal explanation</li>
                                    <li>Could find it difficult to focus in noisy environments</li>
                                    <li>Might need to hear information to process it fully</li>
                                {% elif analysis.learning_styles.primary == 'kinesthetic' %}
                                    <li>May struggle with passive learning situations</li>
                                    <li>Could find it difficult to sit still for long periods</li>
                                    <li>Might need to physically engage with material to understand it</li>
                                {% elif analysis.learning_styles.primary == 'logical' %}
                                    <li>May struggle with abstract or creative tasks without clear structure</li>
                                    <li>Could find it difficult to engage with subjective material</li>
                                    <li>Might need to understand the reasoning behind concepts</li>
                                {% elif analysis.learning_styles.primary == 'social' %}
                                    <li>May struggle with extended independent work</li>
                                    <li>Could find it difficult to focus in isolated environments</li>
                                    <li>Might need interaction to process information fully</li>
                                {% elif analysis.learning_styles.primary == 'solitary' %}
                                    <li>May struggle with group projects and collaborative work</li>
                                    <li>Could find it difficult to focus in social environments</li>
                                    <li>Might need quiet time to process information fully</li>
                                {% endif %}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Additional sections would continue in the same format -->
            
            <div class="footer">
                <p>This report was generated by Learning Compass, a product of Shining Star Education Training LLC.</p>
                <p>© {{ date|slice:"-4:" }} Shining Star Education Training LLC. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
