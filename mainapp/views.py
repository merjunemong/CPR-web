from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .functions.resume_to_skills import getSkillsFromResume
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

def community(request): # community page
    return render(request, 'community/community.html')

def SelfDiscovery(request): # SelfDiscovery page
    return render(request, 'SelfDiscovery.html')

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

@csrf_exempt
def dump_neo4j_db(request): # dump Neo4j DB
    if request.method == "POST":
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dump_folder_path = base_dir  # 'neo4j_dump_db' 파일이 저장된 디렉토리 경로 설정

        # dump_로 시작하는 가장 최근의 .dump 파일을 찾음
        dump_files = glob.glob(os.path.join(dump_folder_path, 'dump_*.dump'))
        
        if dump_files:
            # 가장 최근에 생성된 dump 파일을 선택
            latest_dump_file = max(dump_files, key=os.path.getctime)
            file_name = os.path.basename(latest_dump_file)  # 파일명 추출

            response = FileResponse(open(latest_dump_file, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        else:
            return JsonResponse({"status": "error", "message": "No dump file found."}, status=404)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
# Error
# @csrf_exempt
# def dump_neo4j_db(request): # dump Neo4j DB
#     if request.method == "POST":
#         try:
#             dump_path = "/var/lib/neo4j/backups/neo4j.dump"
#             from django.conf import settings
#             dump_file_path = os.path.join(settings.BASE_DIR, 'neo4j.dump')
#             command = [
#                 'C:\\Program Files\\Neo4j Desktop\\resources\\offline\\neo4j\\neo4j-enterprise-5.12.0-windows.zip\\neo4j-enterprise-5.12.0\\bin\\neo4j-admin.bat',
#                 'dump',
#                 '--database=neo4j',
#                 f'--to={dump_file_path}'  # .dump 파일로 지정
#             ]
            
#             result = subprocess.run(command, capture_output=True, text=True)

#             if result.returncode == 0:
#                 if os.path.exists(dump_path):
#                     return JsonResponse({'status': 'success', 'file_url': '/download_neo4j_dump/'})
#                 else:
#                     return JsonResponse({'status': 'error', 'message': 'Dump file not found'})
#             else:
#                 return JsonResponse({'status': 'error', 'message': result.stderr})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'invalid_method'}, status=405)

# def download_neo4j_dump(request): # download dump file
#     file_path = "/var/lib/neo4j/backups/neo4j.dump"
#     if os.path.exists(file_path):
#         response = FileResponse(open(file_path, 'rb'))
#         response['Content-Disposition'] = 'attachment; filename="neo4j.dump"'
#         return response
#     else:
#         return JsonResponse({'status': 'error', 'message': 'File not found'})

