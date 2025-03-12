from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'rational'

urlpatterns = [
    path('', login_required(views.ProposalView.as_view()), name='index'),
    path('<int:proposal_id>/', views.single_proposal, name='single_proposal'),
    path('proposal-new/', views.proposal_new, name='proposal_new'),
    path('plans/', login_required(views.AnnualPlanView.as_view()), name='index_plan'),
    path('plans/<int:plan_id>/', views.single_plan, name='single_plan'),
]
