from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .forms import *
from .functions.resume_to_skills import getSkillsFromResume
from .functions.CPR_GraphDB import *
import json

# Create your views here.

def index(request): # main page
    return render(request, 'index.html')

def contact(request): # contact page
    return render(request, 'contact.html')

def resume(request): # CPR project page
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'uploadPDF':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)

                skills = getSkillsFromResume(fs.path(filename))
                request.session['skills'] = skills
            return redirect('resume')
    else:
        form = UploadFileForm()
    skills = request.session.pop('skills', None)
    return render(request, 'resume.html', {'form':form, 'skills':skills})

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

def graph_extend(request):
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

def graph_editable(request):
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

def add_to_database(request):
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

def delete_from_database(request):
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


