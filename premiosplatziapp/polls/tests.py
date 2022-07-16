
from urllib.request import urlretrieve
from django.test import TestCase
from django.utils import timezone
import datetime
from django.urls import reverse

from .models import Question

# models
# views


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """was_published_recently returns false for questions who pub_date is in the future"""
        time = timezone.now()+datetime.timedelta(days=30)
        future_question = Question(
            question_text="¿Quien es el mejor CD de platzi?", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


def create_question(question_text, days):
    """
    create a question with the given "question text", 
    and publish the given number of days offset yo now(netagtive for questions published in the paste, 
    positive for question taht have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """if no question exist an appropiate massege is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are avaible")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        question with teh pub date in the future arent display on index page
        """
        create_question("future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are avaible")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        question with teh pub date in the past arent display on index page
        """
        question = create_question("past question", days=-30)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(
            response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """display only the past question"""

        future_question = create_question("future question", days=30)
        past_question = create_question("future question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question])

    def test_two_past_questions(self):
        """the question index page may display multiple"""
        past_question1 = create_question("future question", days=-30)
        past_question2 = create_question("future question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], [past_question1, past_question2])


class QuestionDetailView(TestCase):
    def test_future_question(self):
        """the detail of a quest with a pub date in tyhe future return 404 error not found"""
        future_question = create_question("future question", days=30)
        url = reverse("polls:detail", args=(future_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """the detail view of a querstion with a pub_date in the past displays the questions text"""
        past_question = create_question("future question", days=-30)
        url = reverse("polls:detail", args=(past_question.pk,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
