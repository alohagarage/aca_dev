from django.shortcuts import render_to_response
from answerbase.models import Question, Post, Answer, UserProfile
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from haystack.query import SearchQuerySet

# Create your views here.
def index(request):
    user = request.user
    question_list = Question.objects.all()
    return render_to_response('answerbase/answerbaseindex.html', {'user': user, 'question_list': question_list })

def profile(request):
    user = request.user
    userprofile = UserProfile.objects.get(user=request.user.id)
    return render_to_response('answerbase/profile.html', {'user':user, 'userprofile': userprofile})
    #return HttpResponse(UserProfile.objects.get(user=request.user.id))

def newquestion(request):
    user = request.user
    return render_to_response('answerbase/newquestion.html', {'user':user}, context_instance=RequestContext(request))

def newquestionsubmit(request):
    askedBy = User.objects.get(pk=request.user.id)
    p = Question(question = request.POST['questionTitle'], explanation = request.POST['questionBody'], askedBy = askedBy)
    try:
        if request.POST['subscribe'] == 'subscribe':
            followers = p.followers
            p.followers = followers + str(request.user.id)
    except:
        pass
    p.save()
    return HttpResponseRedirect(reverse('answerbase.views.index'))

def follow(request, q_id):
    #write the follow function here, should just need q_id and .user
    return HttpResponse("You followed")

def question(request, q_id):
    question = Question.objects.get(id=q_id)
    answers = question.answer_set.all().order_by('-votes')
    user = request.user
    return render_to_response('answerbase/question.html', {'question':question, 'answers': answers}, context_instance=RequestContext(request))

def newanswersubmit(request, q_id):
    answeredBy = User.objects.get(pk=request.user.id)
    p = request.POST['newanswer']
    a = Answer(question = Question.objects.get(pk=q_id), answer = p, answeredBy = answeredBy)
    a.save()
    return HttpResponseRedirect(reverse('answerbase.views.question', args = q_id))

def autocomplete(request):
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'term'):
            value = request.GET[u'term']
            if len(value) > 2:
                model_results =SearchQuerySet().autocomplete(content_auto=value)
            #results = [ { 'label': str(x.object.__unicode__()), 'value': x.object.get_absolute_url() } for x in model_results ]
                results = [ str(x.object.__unicode__()) for x in model_results ]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


def searchjson(request):
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'q'):
            value = request.GET[u'q']
            if len(value) > 2:
                ## Could probably just use the non-autocomplete ver of SearchQuerySet, because this might return too many results
                #model_results =SearchQuerySet().filter(content=value)
                model_results = SearchQuerySet().autocomplete(content_auto=value) ##Heres where you define the format of JSON
                results = [ { 'title': str(x.object.__unicode__()), 'url': x.object.get_absolute_url() } for x in model_results ]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')


def post(request):
    posts = Post.objects.all() 
    return render_to_response('answerbase/post.html', {'posts': posts}, context_instance=RequestContext(request))

def post_submit(request):
    p = Post(post = request.POST['post'])
    p.save()
    return HttpResponseRedirect(reverse('answerbase.views.post'))

#VOTES

def vote(request):
    user = request.user
    return render_to_response('answerbase/vote.html',{'user':user}, context_instance=RequestContext(request))

def votesubmit(request):
    dest = request.POST['dest']
    a_id = request.POST['a_id']
    direction = request.POST['direction']
    user = str(request.user.id)
    #TODO logic to check if user has already voted
    a = Answer.objects.get(pk=a_id)
    if user not in a.voted.split(','):
        if dest == "answer":
            if direction == "up":

                a.voteup()
                a.voted += user + ','
                a.save()
            else:
                a.votedown()
                a.voted += user + ','
                a.save()
    else:
        """
        if direction == "up":
            Question.objects.get(pk=a_id).voteup()
        else:
            Question.objects.get(pk=a_id).votedown()
            """

    return HttpResponse('hey, %s, you successfully voted %s %s %s ' % (request.user, dest, a_id, direction))
