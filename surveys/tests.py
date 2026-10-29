from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Attempt, Choice, Question, Survey, SurveyStatistic


class SurveyApiTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(username='author')
        self.survey = Survey.objects.create(title='Овощи', author=self.author)
        self.first = Question.objects.create(
            survey=self.survey, text='Первый?', order=1
        )
        self.second = Question.objects.create(
            survey=self.survey, text='Второй?', order=2,
            allow_custom_answer=True
        )
        self.yes = Choice.objects.create(
            question=self.first, text='Да', order=1
        )
        self.client = APIClient()

    def test_next_question_respects_order(self):
        url = reverse('api-next-question', args=[self.survey.id])
        response = self.client.get(url, {'user': 'ivan'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['question']['id'], self.first.id)
        self.assertEqual(response.data['progress'], {'answered': 0, 'total': 2})

    def test_submit_answers_and_complete_attempt(self):
        answer_url = reverse('api-submit-answer', args=[self.survey.id])
        first_response = self.client.post(answer_url, {
            'user': 'ivan', 'question_id': self.first.id,
            'choice_id': self.yes.id,
        }, format='json')
        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(first_response.data['next_question_id'], self.second.id)

        second_response = self.client.post(answer_url, {
            'user': 'ivan', 'question_id': self.second.id,
            'custom_answer': 'Иногда',
        }, format='json')
        self.assertEqual(second_response.status_code, 201)
        self.assertTrue(second_response.data['completed'])
        self.assertIsNotNone(Attempt.objects.get().completed_at)
        self.assertEqual(SurveyStatistic.objects.get().completed_count, 1)

    def test_choice_from_another_question_is_rejected(self):
        wrong = Choice.objects.create(
            question=self.second, text='Нет', order=1
        )
        url = reverse('api-submit-answer', args=[self.survey.id])
        response = self.client.post(url, {
            'user': 'ivan', 'question_id': self.first.id,
            'choice_id': wrong.id,
        }, format='json')
        self.assertEqual(response.status_code, 400)


class SurveyPageTests(TestCase):
    def test_list_page_opens(self):
        response = self.client.get(reverse('survey-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Поделитесь своим мнением')


class SurveyAdminEditorTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_superuser(
            username='editor', password='test', email='editor@example.com'
        )
        self.client.login(username='editor', password='test')
        self.survey = Survey.objects.create(title='Новый опрос', author=self.author)

    def test_admin_can_add_question_and_choice(self):
        editor_url = reverse('admin:surveys_survey_editor', args=[self.survey.id])
        self.client.post(editor_url, {
            'action': 'add_question', 'text': 'Новый вопрос',
            'allow_custom_answer': 'on',
        })
        question = self.survey.questions.get()
        self.assertTrue(question.allow_custom_answer)

        self.client.post(editor_url, {
            'action': 'add_choice', 'question_id': question.id, 'text': 'Да',
        })
        self.assertEqual(question.choices.get().text, 'Да')
