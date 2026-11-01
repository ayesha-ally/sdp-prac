from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AssignmentForm, ModuleForm
from .models import Assignment, Module


def home(request):
    assignments = list(Assignment.objects.filter(archived=False))
    return render(
        request,
        "tracker/home.html",
        {
            "total_count": len(assignments),
            "completed_count": sum(
                1 for assignment in assignments if assignment.status == Assignment.Status.COMPLETED
            ),
            "pending_count": sum(
                1 for assignment in assignments if assignment.status != Assignment.Status.COMPLETED
            ),
            "overdue_count": sum(1 for assignment in assignments if assignment.is_overdue),
        },
    )


def module_list(request):
    modules = Module.objects.all()
    return render(request, "tracker/module_list.html", {"modules": modules})


def module_create(request):
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("module_list")
    else:
        form = ModuleForm()
    return render(request, "tracker/module_form.html", {"form": form, "title": "Add module"})


def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect("module_list")
    else:
        form = ModuleForm(instance=module)
    return render(
        request,
        "tracker/module_form.html",
        {"form": form, "title": "Edit module", "module": module},
    )


def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    assignments = module.assignments.filter(archived=False)
    archived_assignments = module.assignments.filter(archived=True)
    return render(
        request,
        "tracker/module_detail.html",
        {
            "module": module,
            "assignments": assignments,
            "archived_assignments": archived_assignments,
        },
    )


def _apply_assignment_filters(request, queryset):
    query = request.GET.get("q", "").strip()
    module_id = request.GET.get("module", "").strip()
    priority = request.GET.get("priority", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        queryset = queryset.filter(title__icontains=query)
    if module_id:
        queryset = queryset.filter(module_id=module_id)
    if priority:
        queryset = queryset.filter(priority=priority)
    if status:
        queryset = queryset.filter(status=status)
    return queryset


def assignment_list(request):
    assignments = list(
        _apply_assignment_filters(
            request,
            Assignment.objects.filter(archived=False).select_related("module"),
        )
    )
    archived_assignments = _apply_assignment_filters(
        request,
        Assignment.objects.filter(archived=True).select_related("module"),
    )
    overdue_assignments = [assignment for assignment in assignments if assignment.is_overdue]
    return render(
        request,
        "tracker/assignment_list.html",
        {
            "assignments": assignments,
            "archived_assignments": archived_assignments,
            "overdue_assignments": overdue_assignments,
            "modules": Module.objects.all(),
            "priorities": Assignment.Priority.choices,
            "statuses": Assignment.Status.choices,
            "search_q": request.GET.get("q", ""),
            "filter_module": request.GET.get("module", ""),
            "filter_priority": request.GET.get("priority", ""),
            "filter_status": request.GET.get("status", ""),
        },
    )


def assignment_create(request):
    initial = {}
    module_id = request.GET.get("module")
    if module_id:
        initial["module"] = module_id
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("assignment_list")
    else:
        form = AssignmentForm(initial=initial)
    return render(
        request,
        "tracker/assignment_form.html",
        {"form": form, "title": "Add assignment"},
    )


def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related("module"), pk=pk)
    return render(request, "tracker/assignment_detail.html", {"assignment": assignment})


def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)
    return render(
        request,
        "tracker/assignment_form.html",
        {"form": form, "title": "Edit assignment", "assignment": assignment},
    )


@require_POST
def assignment_archive(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    assignment.archived = True
    assignment.save(update_fields=["archived"])
    return redirect("assignment_list")
