from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note_list'),
    path('note/<int:pk>/', views.NoteDetailView.as_view(),
         name='note_detail'),
    path('note/create/', views.NoteCreateView.as_view(),
         name='note_create'),
    path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(),
         name='note_edit'),
    path('note/<int:pk>/delete/', views.NoteDeleteView.as_view(),
         name='note_delete'),
]
