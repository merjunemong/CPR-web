from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('graph/extend/', views.graph_extend, name='graph_extend'),
    path('graph/editable/', views.graph_editable, name='graph_editable'),
    path('graph/', views.draw_graph, name='draw_graph'),
    path('resume/', views.resume, name='resume'),
    path('resume/result/', views.resume_result, name='resume_result'),
    path('viewdb/', views.viewdb, name='viewdb'),
    path('contact/', views.contact, name='contact'),
    path('api/skill/add/', views.add_to_database, name='add_to_database'),
    path('api/skill/delete/', views.delete_from_database, name='delete_from_database'),
]

