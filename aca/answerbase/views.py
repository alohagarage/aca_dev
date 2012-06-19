from django.shortcuts import render_to_response
from answerbase.models import Question, Post, Answer
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

# Create your views here.
def index(request):
    question_list = Question.objects.all()
    return render_to_response('answerbase/answerbaseindex.html', {'question_list': question_list })

def newquestion(request):
    user = request.user
    return render_to_response('answerbase/newquestion.html', {'user':user}, context_instance=RequestContext(request))

def newquestionsubmit(request):
    askedBy = User.objects.get(pk=request.user.id)
    p = Question(question = request.POST['questionTitle'], explanation = request.POST['questionBody'], askedBy = askedBy)
    p.save()
    return HttpResponseRedirect(reverse('answerbase.views.index'))

def question(request, q_id):
    question = Question.objects.get(id=q_id)
    answers = question.answer_set.all()
    user = request.user
    return render_to_response('answerbase/question.html', {'question':question, 'answers': answers}, context_instance=RequestContext(request))

def newanswersubmit(request, q_id):
    answeredBy = User.objects.get(pk=request.user.id)
    p = request.POST['newanswer']
    a = Answer(question = Question.objects.get(pk=q_id), answer = p, answeredBy = answeredBy)
    a.save()
    return HttpResponseRedirect(reverse('answerbase.views.question', args = q_id))

def post(request):
    posts = Post.objects.all() 
    return render_to_response('answerbase/post.html', {'posts': posts}, context_instance=RequestContext(request))

def post_submit(request):
    p = Post(post = request.POST['post'])
    p.save()
    return HttpResponseRedirect(reverse('answerbase.views.post'))
