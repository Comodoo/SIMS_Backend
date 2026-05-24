"""
GraphQL URL Configuration
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView
from sims_backend.schema import schema

urlpatterns = [
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema)), name='graphql'),
]
