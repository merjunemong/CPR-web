from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .functions.resume_to_skills import getSkillsFromResume
from .functions.answers_to_skills import getSkillsFromAnswers
from .functions.CPR_GraphDB import *
import json
import subprocess
import glob
import os

# Create your views here.

def index(request): # main page
    return render(request, 'index.html')

def contact(request): # contact page
    return render(request, 'contact.html')

def resume(request): # CPR project page
    form = UploadFileForm(request.POST, request.FILES)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'requestAPI':
            skills = []
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)
                request.session['uploaded_file_name'] = uploaded_file.name
                skills = getSkillsFromResume(fs.path(filename) if file_url else None)

            answers = [request.POST.get(f'answer{i}', None) for i in range(1, 11)]
            if not all(answer is None for answer in answers):
                skills = skills + getSkillsFromAnswers(answers)


            request.session['skills'] = skills
            request.session['answers'] = answers

            return redirect('resume')
    else:
        form = UploadFileForm()
        skills = request.session.pop('skills', None)
        answers = request.session.pop('answers', ['']*10)

    return render(request, 'resume.html', {'form': form, 'skills': skills, 'answers': answers})

def resume_result(request): # CPR project result output page
    if request.method == 'POST':
        jobs = None
        body = json.loads(request.body)
        form = ListForm(body)
        if form.is_valid():
            skills = body.get('skills')
            jobs = getSimilarJob(skills)
            request.session['jobs'] = jobs
        return render(request, 'resume-result.html', {'form':form, 'jobs':jobs})
    else:
        form = ListForm()
    jobs = request.session.pop('jobs', None)
    return render(request, 'resume-result.html', {'form':form, 'jobs':jobs})

def viewdb(request): # graphDB edit page
    return render(request, 'viewdb.html')

def community(request): # community page
    return render(request, 'community/community.html')

def community_create(request): # community create page
    return render(request, 'community/create.html')

def community_post(request): # community post page
    return render(request, 'community/post.html')

def draw_graph(request): # display job-skill graph
    if request.method == 'POST':
        body = json.loads(request.body)
        form = JobForm(body)
        if form.is_valid():
            job = body.get('job')
            skills = getSkills(job)
            request.session['job_name'] = job
            request.session['skills'] = skills
            return render(request, 'graph/graph.html', {'job_name': job, 'skills': skills})
    else:
        form = JobForm()
    job = request.session.pop('job_name', None)
    skills = request.session.pop('skills', None)
    return render(request, 'graph/graph.html', {'job_name': job, 'skills': skills})

def graph_extend(request): # display extended job-skill graph
    if request.method == 'POST':
        body = json.loads(request.body)
        skill = body.get('skill')
        if skill:
            jobs = getJobs(skill)
            request.session['skill'] = skill
            request.session['jobs'] = jobs
            return render(request, 'graph/graph-extend.html', {'skill': skill, 'jobs': jobs})
    skill = request.session.pop('skill', None)
    jobs = request.session.pop('jobs', None)
    return render(request, 'graph/graph-extend.html', {'skill': skill, 'jobs': jobs})

def graph_editable(request): # display job-skill graph that can editable
    if request.method == 'POST':
        body = json.loads(request.body)
        form = JobForm(body)
        if form.is_valid():
            job = body.get('job')
            skills = getSkills(job)
            request.session['job_name'] = job
            request.session['skills'] = skills
            return render(request, 'graph/graph-editable.html', {'job_name': job, 'skills': skills})
    else:
        form = SkillForm()
    job = request.session.pop('job_name', None)
    skills = request.session.pop('skills', None)
    return render(request, 'graph/graph-editable.html', {'job_name': job, 'skills': skills})

def add_to_database(request): # add data api
    if request.method == 'POST':
        body = json.loads(request.body)
        job = body.get('job_name')
        skill = body.get('skill')
        skills_list = body.get('skills_list')
        addData(job, skill)
        skills_list.append(skill)
        request.session['job_name'] = job
        request.session['skills'] = skills_list
        return redirect('graph_editable')
    job = request.session.pop('job_name', None)
    skills = request.session.pop('skills', None)
    return render(request, 'graph/graph-editable.html', {'job_name': job, 'skills': skills})

def delete_from_database(request): # delete data api
    if request.method == 'POST':
        body = json.loads(request.body)
        job = body.get('job_name')
        skill = body.get('skill')
        skills_list = body.get('skills_list')
        deleteData(job, skill)
        skills_list.remove(skill)
        request.session['job_name'] = job
        request.session['skills'] = skills_list
        return redirect('graph_editable')
    job = request.session.pop('job_name', None)
    skills = request.session.pop('skills', None)
    return render(request, 'graph/graph-editable.html', {'job_name': job, 'skills': skills})
