from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .functions.resume_to_skills import getSkillsFromResume
from .functions.CPR_GraphDB import *
import json
import subprocess
import os

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

@csrf_exempt
def dump_neo4j_db(request): # dump Neo4j DB
    if request.method == "POST":
        print(1)
        try:
            dump_path = "/var/lib/neo4j/backups/neo4j.dump"
            command = [
                "sudo", "-u", "neo4j", "neo4j-admin", "database", "dump",
                "--overwrite-destination=true", "--to-path=/var/lib/neo4j/backups/", "neo4j"
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            print(2)

            if result.returncode == 0:
                if os.path.exists(dump_path):
                    print(3)
                    return JsonResponse({'status': 'success', 'file_url': '/download_neo4j_dump/'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Dump file not found'})
            else:
                return JsonResponse({'status': 'error', 'message': result.stderr})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid_method'}, status=405)

def download_neo4j_dump(request): # download dump file
    file_path = "/var/lib/neo4j/backups/neo4j.dump"
    print(4)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        print(5)
        response['Content-Disposition'] = 'attachment; filename="neo4j.dump"'
        return response
    else:
        return JsonResponse({'status': 'error', 'message': 'File not found'})

