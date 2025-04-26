from django.db import models
from users.models import Student

class QuestionCategory(models.TextChoices):
    LEARNING_STYLE = 'LEARNING_STYLE', 'Learning Style'
    BEHAVIOR = 'BEHAVIOR', 'Behavior'
    COGNITIVE = 'COGNITIVE', 'Cognitive Strengths'
    CREATIVITY = 'CREATIVITY', 'Creativity & Innovation'
    TIME_MANAGEMENT = 'TIME_MANAGEMENT', 'Time Management'
    COMMUNICATION = 'COMMUNICATION', 'Communication'
    INTEREST = 'INTEREST', 'Interest Alignment'

class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice'
    SITUATIONAL = 'SITUATIONAL', 'Situational Judgment'
    LOGIC_PUZZLE = 'LOGIC_PUZZLE', 'Logic Puzzle'
    VISUAL_REASONING = 'VISUAL_REASONING', 'Visual Reasoning'
    VERBAL_REASONING = 'VERBAL_REASONING', 'Verbal Reasoning'
    OPEN_ENDED = 'OPEN_ENDED', 'Open-Ended Reflection'

class Question(models.Model):
    """
    Model for diagnostic questions.
    """
    text = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=QuestionCategory.choices,
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
    )
    grade_level = models.CharField(
        max_length=3,
        choices=Student.Grade.choices,
    )
    difficulty = models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    time_limit = models.PositiveIntegerField(help_text="Time limit in seconds", default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For AI-generated questions
    is_ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.text[:50]}... ({self.get_category_display()} - {self.get_grade_level_display()})"

class QuestionOption(models.Model):
    """
    Model for multiple choice question options.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    # Scoring impact for different categories
    learning_style_impact = models.JSONField(default=dict, blank=True)
    cognitive_impact = models.JSONField(default=dict, blank=True)
    behavior_impact = models.JSONField(default=dict, blank=True)
    interest_impact = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.text[:30]}... ({self.question.text[:20]}...)"

class Assessment(models.Model):
    """
    Model for student assessments.
    """
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='assessments')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ABANDONED = 'ABANDONED', 'Abandoned'
    
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Assessment for {self.student} - {self.get_status_display()}"

class Response(models.Model):
    """
    Model for student responses to questions.
    """
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    open_response = models.TextField(null=True, blank=True)
    response_time = models.PositiveIntegerField(help_text="Response time in seconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.selected_option:
            return f"Response to {self.question.text[:30]}... - {self.selected_option.text[:20]}..."
        else:
            return f"Response to {self.question.text[:30]}... - {self.open_response[:20]}..."

class QuestionnaireTemplate(models.Model):
    """
    Model for predefined questionnaire templates.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    grade_level = models.CharField(
        max_length=3,
        choices=Student.Grade.choices,
    )
    questions = models.ManyToManyField(Question, through='TemplateQuestion')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_grade_level_display()})"

class TemplateQuestion(models.Model):
    """
    Through model for questionnaire templates and questions.
    """
    template = models.ForeignKey(QuestionnaireTemplate, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']
        unique_together = ['template', 'order']
    
    def __str__(self):
        return f"{self.template.name} - Q{self.order}: {self.question.text[:30]}..."
