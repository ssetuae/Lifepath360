from rest_framework import serializers
from .models import (
    Question, 
    QuestionOption, 
    Assessment, 
    Response, 
    QuestionnaireTemplate,
    TemplateQuestion
)
from users.models import Student

class QuestionOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for question options.
    """
    class Meta:
        model = QuestionOption
        fields = (
            'id', 'text', 'is_correct', 
            'learning_style_impact', 'cognitive_impact', 
            'behavior_impact', 'interest_impact'
        )


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for questions.
    """
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = (
            'id', 'text', 'category', 'question_type', 
            'grade_level', 'difficulty', 'time_limit', 
            'is_active', 'is_ai_generated', 'options'
        )


class QuestionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating questions with options.
    """
    options = QuestionOptionSerializer(many=True)
    
    class Meta:
        model = Question
        fields = (
            'id', 'text', 'category', 'question_type', 
            'grade_level', 'difficulty', 'time_limit', 
            'is_active', 'is_ai_generated', 'ai_prompt', 'options'
        )
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)
        
        return question
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update options if provided
        if options_data is not None:
            # Delete existing options
            instance.options.all().delete()
            
            # Create new options
            for option_data in options_data:
                QuestionOption.objects.create(question=instance, **option_data)
        
        return instance


class ResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for student responses.
    """
    class Meta:
        model = Response
        fields = (
            'id', 'assessment', 'question', 'selected_option', 
            'open_response', 'response_time', 'created_at'
        )


class ResponseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating student responses.
    """
    class Meta:
        model = Response
        fields = (
            'id', 'assessment', 'question', 'selected_option', 
            'open_response', 'response_time'
        )
    
    def validate(self, data):
        """
        Validate that either selected_option or open_response is provided based on question type.
        """
        question = data.get('question')
        selected_option = data.get('selected_option')
        open_response = data.get('open_response')
        
        if question.question_type == 'OPEN_ENDED' and not open_response:
            raise serializers.ValidationError(
                {"open_response": "Open response is required for open-ended questions."}
            )
        
        if question.question_type != 'OPEN_ENDED' and not selected_option:
            raise serializers.ValidationError(
                {"selected_option": "Selected option is required for this question type."}
            )
        
        if selected_option and selected_option.question.id != question.id:
            raise serializers.ValidationError(
                {"selected_option": "Selected option does not belong to the specified question."}
            )
        
        return data


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for student assessments.
    """
    responses = ResponseSerializer(many=True, read_only=True)
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = (
            'id', 'student', 'student_name', 'start_time', 
            'end_time', 'status', 'responses', 'created_at'
        )
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"


class AssessmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating student assessments.
    """
    class Meta:
        model = Assessment
        fields = ('id', 'student')
    
    def validate_student(self, value):
        """
        Check if student already has an in-progress assessment.
        """
        existing_assessment = Assessment.objects.filter(
            student=value, 
            status=Assessment.Status.IN_PROGRESS
        ).first()
        
        if existing_assessment:
            raise serializers.ValidationError(
                "Student already has an in-progress assessment."
            )
        
        return value


class TemplateQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for template questions.
    """
    question_detail = QuestionSerializer(source='question', read_only=True)
    
    class Meta:
        model = TemplateQuestion
        fields = ('id', 'question', 'question_detail', 'order')


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for questionnaire templates.
    """
    template_questions = TemplateQuestionSerializer(
        source='templatequestion_set', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = QuestionnaireTemplate
        fields = (
            'id', 'name', 'description', 'grade_level', 
            'is_active', 'template_questions', 'created_at'
        )


class QuestionnaireTemplateCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating questionnaire templates with ordered questions.
    """
    questions_order = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    
    class Meta:
        model = QuestionnaireTemplate
        fields = (
            'id', 'name', 'description', 'grade_level', 
            'is_active', 'questions_order'
        )
    
    def create(self, validated_data):
        questions_order = validated_data.pop('questions_order')
        template = QuestionnaireTemplate.objects.create(**validated_data)
        
        # Create template questions with order
        for index, question_id in enumerate(questions_order, start=1):
            try:
                question = Question.objects.get(id=question_id)
                TemplateQuestion.objects.create(
                    template=template,
                    question=question,
                    order=index
                )
            except Question.DoesNotExist:
                pass
        
        return template
    
    def update(self, instance, validated_data):
        questions_order = validated_data.pop('questions_order', None)
        
        # Update template fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update template questions if provided
        if questions_order is not None:
            # Delete existing template questions
            instance.templatequestion_set.all().delete()
            
            # Create new template questions with order
            for index, question_id in enumerate(questions_order, start=1):
                try:
                    question = Question.objects.get(id=question_id)
                    TemplateQuestion.objects.create(
                        template=instance,
                        question=question,
                        order=index
                    )
                except Question.DoesNotExist:
                    pass
        
        return instance
