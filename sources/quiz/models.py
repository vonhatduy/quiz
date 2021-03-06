# coding:utf8
from django.contrib.auth.models import User
from questions.models import QuestionSet, Answer, Question

__author__ = 'djud'

from django.db import models


class QuizQuestion(models.Model):
    question = models.ForeignKey(Question)
    index = models.IntegerField()
    answered = models.BooleanField(default=False)
    next = models.ForeignKey('self', null=True, related_name='qnext')
    previous = models.ForeignKey('self', null=True, related_name='qprev')
    testing = models.ForeignKey('quiz.Quiz')
    # TODO: нужно ли позволять переотвечать на вопросы?

    @property
    def is_last(self):
        last = QuizQuestion.objects.filter(
            testing=self.testing, answered=False).order_by('-index')[:1].get()
        return self.id == last.id


class Quiz(models.Model):
    user = models.ForeignKey(User)
    question_set = models.ForeignKey(QuestionSet)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, default=None)
    deadline = models.DateTimeField()
    current_question = models.ForeignKey(QuizQuestion, null=True,
                                         related_name='cur_testing')

    def next_question(self):
        if self.current_question.next:
            self.current_question = self.current_question.next
            if self.current_question.answered:
                return self.next_question()
        else:
            questions = list(
                self.quizquestion_set.all().filter(answered=False))
            if len(questions) > 0:
                self.current_question = questions[0]
            else:
                self.current_question = None

    @property
    def unanswered_questions(self):
        return list(self.quizquestion_set.all().filter(
            testing=self, answered=False).order_by('index'))

    @property
    def num_right_answers(self):
        right = len([log.answer for log in QuizLog.objects.filter(quiz=self)
                     if log.answer and log.answer.is_right])
        return right or 0

    @property
    def num_questions(self):
        return Question.objects.filter(question_set=self.question_set).count()

    @property
    def percent_right_answers(self):
        return int(self.num_right_answers * 100 / self.num_questions)



class QuizLog(models.Model):
    question_set = models.ForeignKey(QuestionSet)
    quiz = models.ForeignKey(Quiz)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer, null=True, default=None)
    question_dt = models.DateTimeField()
    answer_dt = models.DateTimeField(null=True, default=None)
