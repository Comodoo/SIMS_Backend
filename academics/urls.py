from django.urls import path
from academics.views import UploadFileView

urlpatterns = [
    path('upload/', UploadFileView.as_view(), name='file-upload'),
]
