from django.contrib import admin
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from django.urls import path
from .workflow_models import Workflow, WorkflowStep, WorkflowType, WorkflowState

@staff_member_required
def workflow_analytics_view(request):
    """
    Comprehensive workflow analytics dashboard
    """
    # Overall workflow statistics
    total_workflows = Workflow.objects.count()
    workflows_by_type = Workflow.objects.values('type').annotate(
        count=Count('id'),
        avg_steps=Avg('current_step')
    )
    
    # State distribution
    state_distribution = Workflow.objects.values('state').annotate(
        count=Count('id')
    )
    
    # Most active workflow types
    most_active_types = Workflow.objects.values('type').annotate(
        total_workflows=Count('id'),
        avg_duration=Avg('current_step')
    ).order_by('-total_workflows')
    
    # Workflow step insights
    step_insights = WorkflowStep.objects.values('workflow__type').annotate(
        total_steps=Count('id'),
        avg_relevance=Avg('relevance_score')
    )
    
    context = {
        'title': 'Workflow Analytics',
        'total_workflows': total_workflows,
        'workflows_by_type': list(workflows_by_type),
        'state_distribution': list(state_distribution),
        'most_active_types': list(most_active_types),
        'step_insights': list(step_insights)
    }
    
    return render(request, 'admin/workflow_analytics.html', context)

def get_admin_urls(admin_site):
    """
    Generate custom admin URLs
    """
    custom_urls = [
        path(
            'workflow-analytics/', 
            admin_site.admin_view(workflow_analytics_view), 
            name='workflow_analytics'
        )
    ]
    return custom_urls 