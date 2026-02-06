"""
Management command to populate dummy data for academics app.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Skills, Lesson, Units, Course, Class, QuizQuestion, Quiz

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate academics app with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to populate academics data...'))

        # Create or get users
        teacher_user, created = User.objects.get_or_create(
            email='teacher@edututor.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'teacher',
                'is_email_verified': True,
                'is_active': True,
            }
        )
        if created:
            teacher_user.set_password('password123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created teacher user: {teacher_user.email}'))

        admin_user, created = User.objects.get_or_create(
            email='admin@edututor.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'school_admin',
                'is_email_verified': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('password123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.email}'))

        # Create Skills
        skills_data = [
            {'name': 'Critical Thinking', 'description': 'Ability to analyze and evaluate information'},
            {'name': 'Problem Solving', 'description': 'Finding solutions to complex problems'},
            {'name': 'Mathematics', 'description': 'Mathematical and numerical skills'},
            {'name': 'Reading Comprehension', 'description': 'Understanding written text'},
            {'name': 'Writing', 'description': 'Effective written communication'},
            {'name': 'Scientific Method', 'description': 'Understanding scientific processes'},
        ]

        skills = []
        for skill_data in skills_data:
            skill, created = Skills.objects.get_or_create(
                name=skill_data['name'],
                defaults={'description': skill_data['description']}
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'Created skill: {skill.name}')

        # Create Lessons
        lessons_data = [
            {
                'title': 'Introduction to Algebra',
                'description': 'Basic concepts of algebra including variables and equations',
                'duration': 45,
                'skills': [skills[0], skills[2]]
            },
            {
                'title': 'Advanced Algebra',
                'description': 'Complex algebraic expressions and problem solving',
                'duration': 60,
                'skills': [skills[1], skills[2]]
            },
            {
                'title': 'Geometry Basics',
                'description': 'Introduction to shapes, angles, and geometric principles',
                'duration': 50,
                'skills': [skills[0], skills[2]]
            },
            {
                'title': 'Reading Strategies',
                'description': 'Techniques for effective reading and comprehension',
                'duration': 40,
                'skills': [skills[3], skills[4]]
            },
            {
                'title': 'Essay Writing',
                'description': 'Structured approach to writing essays',
                'duration': 55,
                'skills': [skills[0], skills[4]]
            },
            {
                'title': 'Scientific Investigation',
                'description': 'Understanding the scientific method and experimentation',
                'duration': 65,
                'skills': [skills[0], skills[5]]
            },
        ]

        lessons = []
        for lesson_data in lessons_data:
            lesson_skills = lesson_data.pop('skills')
            lesson, created = Lesson.objects.get_or_create(
                title=lesson_data['title'],
                defaults=lesson_data
            )
            if created:
                lesson.skills.set(lesson_skills)
                self.stdout.write(f'Created lesson: {lesson.title}')
            lessons.append(lesson)

        # Create Units
        units_data = [
            {
                'name': 'Algebra Fundamentals',
                'description': 'Foundation of algebraic thinking',
                'lessons': [lessons[0], lessons[1]]
            },
            {
                'name': 'Geometry and Shapes',
                'description': 'Understanding geometric concepts',
                'lessons': [lessons[2]]
            },
            {
                'name': 'Language Arts Essentials',
                'description': 'Core reading and writing skills',
                'lessons': [lessons[3], lessons[4]]
            },
            {
                'name': 'Science Foundations',
                'description': 'Basic scientific principles',
                'lessons': [lessons[5]]
            },
        ]

        units = []
        for unit_data in units_data:
            unit_lessons = unit_data.pop('lessons')
            unit, created = Units.objects.get_or_create(
                name=unit_data['name'],
                defaults=unit_data
            )
            if created:
                unit.lessons.set(unit_lessons)
                self.stdout.write(f'Created unit: {unit.name}')
            units.append(unit)

        # Create Courses
        courses_data = [
            {
                'name': 'Mathematics Grade 8',
                'description': 'Comprehensive mathematics curriculum for 8th grade',
                'units': [units[0], units[1]]
            },
            {
                'name': 'English Language Arts',
                'description': 'Reading and writing skills development',
                'units': [units[2]]
            },
            {
                'name': 'General Science',
                'description': 'Introduction to scientific concepts',
                'units': [units[3]]
            },
        ]

        courses = []
        for course_data in courses_data:
            course_units = course_data.pop('units')
            course, created = Course.objects.get_or_create(
                name=course_data['name'],
                defaults=course_data
            )
            if created:
                course.units.set(course_units)
                self.stdout.write(f'Created course: {course.name}')
            courses.append(course)

        # Create Classes
        classes_data = [
            {
                'name': 'Class 8A',
                'learning_objectives': 'Develop strong foundation in core subjects',
                'courses': [courses[0], courses[1]]
            },
            {
                'name': 'Class 8B',
                'learning_objectives': 'Advanced learning with focus on STEM',
                'courses': [courses[0], courses[2]]
            },
        ]

        classes = []
        for class_data in classes_data:
            class_courses = class_data.pop('courses')
            class_obj, created = Class.objects.get_or_create(
                name=class_data['name'],
                defaults=class_data
            )
            if created:
                class_obj.course.set(class_courses)
                self.stdout.write(f'Created class: {class_obj.name}')
            classes.append(class_obj)

        # Create Quiz Questions for Mathematics
        math_questions_data = [
            {
                'question_point': 1,
                'question_text': 'What is 2 + 2?',
                'course': courses[0],
                'option_a': '3',
                'option_b': '4',
                'option_c': '5',
                'option_d': '6',
                'correct_option': 'B'
            },
            {
                'question_point': 2,
                'question_text': 'Solve for x: 2x + 5 = 13',
                'course': courses[0],
                'option_a': 'x = 2',
                'option_b': 'x = 3',
                'option_c': 'x = 4',
                'option_d': 'x = 5',
                'correct_option': 'C'
            },
            {
                'question_point': 2,
                'question_text': 'What is the area of a rectangle with length 5 and width 3?',
                'course': courses[0],
                'option_a': '8',
                'option_b': '12',
                'option_c': '15',
                'option_d': '18',
                'correct_option': 'C'
            },
            {
                'question_point': 3,
                'question_text': 'What is the value of π (pi) approximately?',
                'course': courses[0],
                'option_a': '2.14',
                'option_b': '3.14',
                'option_c': '4.14',
                'option_d': '5.14',
                'correct_option': 'B'
            },
        ]

        math_questions = []
        for q_data in math_questions_data:
            question, created = QuizQuestion.objects.get_or_create(
                question_text=q_data['question_text'],
                course=q_data['course'],
                defaults=q_data
            )
            if created:
                self.stdout.write(f'Created question: {question.question_text[:50]}...')
            math_questions.append(question)

        # Create Quiz Questions for English
        english_questions_data = [
            {
                'question_point': 1,
                'question_text': 'What is a noun?',
                'course': courses[1],
                'option_a': 'A describing word',
                'option_b': 'A person, place, or thing',
                'option_c': 'An action word',
                'option_d': 'A connecting word',
                'correct_option': 'B'
            },
            {
                'question_point': 2,
                'question_text': 'Which sentence is grammatically correct?',
                'course': courses[1],
                'option_a': 'She dont like apples',
                'option_b': 'She doesnt like apples',
                'option_c': "She doesn't like apples",
                'option_d': 'She not like apples',
                'correct_option': 'C'
            },
        ]

        english_questions = []
        for q_data in english_questions_data:
            question, created = QuizQuestion.objects.get_or_create(
                question_text=q_data['question_text'],
                course=q_data['course'],
                defaults=q_data
            )
            if created:
                self.stdout.write(f'Created question: {question.question_text[:50]}...')
            english_questions.append(question)

        # Create Quiz Questions for Science
        science_questions_data = [
            {
                'question_point': 1,
                'question_text': 'What is the chemical symbol for water?',
                'course': courses[2],
                'option_a': 'O2',
                'option_b': 'H2O',
                'option_c': 'CO2',
                'option_d': 'HO',
                'correct_option': 'B'
            },
            {
                'question_point': 2,
                'question_text': 'What is the process by which plants make food?',
                'course': courses[2],
                'option_a': 'Respiration',
                'option_b': 'Digestion',
                'option_c': 'Photosynthesis',
                'option_d': 'Fermentation',
                'correct_option': 'C'
            },
        ]

        science_questions = []
        for q_data in science_questions_data:
            question, created = QuizQuestion.objects.get_or_create(
                question_text=q_data['question_text'],
                course=q_data['course'],
                defaults=q_data
            )
            if created:
                self.stdout.write(f'Created question: {question.question_text[:50]}...')
            science_questions.append(question)

        # Create Quizzes
        quizzes_data = [
            {
                'name': 'Math Mid-Term Quiz',
                'class_name': classes[0],
                'course': courses[0],
                'questions': math_questions,
                'passing_score': 70,
                'created_by': teacher_user
            },
            {
                'name': 'Algebra Basics Quiz',
                'class_name': classes[1],
                'course': courses[0],
                'questions': math_questions[:2],
                'passing_score': 60,
                'created_by': teacher_user
            },
            {
                'name': 'English Grammar Quiz',
                'class_name': classes[0],
                'course': courses[1],
                'questions': english_questions,
                'passing_score': 75,
                'created_by': teacher_user
            },
            {
                'name': 'Science Fundamentals Quiz',
                'class_name': classes[1],
                'course': courses[2],
                'questions': science_questions,
                'passing_score': 65,
                'created_by': admin_user
            },
        ]

        for quiz_data in quizzes_data:
            questions = quiz_data.pop('questions')
            quiz, created = Quiz.objects.get_or_create(
                name=quiz_data['name'],
                course=quiz_data['course'],
                defaults=quiz_data
            )
            if created:
                quiz.questions.set(questions)
                self.stdout.write(f'Created quiz: {quiz.name}')

        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Skills: {Skills.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Lessons: {Lesson.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Units: {Units.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Courses: {Course.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Classes: {Class.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Quiz Questions: {QuizQuestion.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Quizzes: {Quiz.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\nDummy data populated successfully!'))
