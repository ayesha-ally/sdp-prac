from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment, Module


class ModuleTests(TestCase):
    def test_create_module(self):
        response = self.client.post(
            reverse("module_create"),
            {"code": "COMS1018", "name": "Introduction to Algorithms"},
        )
        self.assertRedirects(response, reverse("module_list"))
        self.assertTrue(Module.objects.filter(code="COMS1018").exists())

    def test_module_code_must_be_unique(self):
        Module.objects.create(code="COMS1018", name="Introduction to Algorithms")
        response = self.client.post(
            reverse("module_create"),
            {"code": "COMS1018", "name": "Duplicate module"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(Module.objects.filter(code="COMS1018").count(), 1)

    def test_required_fields_are_validated(self):
        response = self.client.post(reverse("module_create"), {"code": "  ", "name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Module.objects.count(), 0)

    def test_view_and_edit_module(self):
        module = Module.objects.create(code="COMS1018", name="Old name")
        list_response = self.client.get(reverse("module_list"))
        self.assertContains(list_response, "COMS1018")
        detail_response = self.client.get(reverse("module_detail", args=[module.pk]))
        self.assertContains(detail_response, "Old name")
        edit_response = self.client.post(
            reverse("module_edit", args=[module.pk]),
            {"code": "COMS1018", "name": "Updated name"},
        )
        self.assertRedirects(edit_response, reverse("module_list"))
        module.refresh_from_db()
        self.assertEqual(module.name, "Updated name")


class AssignmentTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(code="COMS1018", name="Introduction to Algorithms")
        self.assignment_data = {
            "module": self.module.pk,
            "title": "Lab 1",
            "description": "Complete the worksheet",
            "due_date": "2026-11-15",
            "priority": Assignment.Priority.MEDIUM,
            "status": Assignment.Status.NOT_STARTED,
        }

    def test_create_assignment_belongs_to_one_module(self):
        response = self.client.post(reverse("assignment_create"), self.assignment_data)
        self.assertRedirects(response, reverse("assignment_list"))
        assignment = Assignment.objects.get(title="Lab 1")
        self.assertEqual(assignment.module, self.module)
        self.assertEqual(assignment.status, Assignment.Status.NOT_STARTED)

    def test_edit_assignment(self):
        assignment = Assignment.objects.create(
            module=self.module,
            title="Lab 1",
            due_date=date(2026, 11, 15),
            priority=Assignment.Priority.LOW,
            status=Assignment.Status.NOT_STARTED,
        )
        response = self.client.post(
            reverse("assignment_edit", args=[assignment.pk]),
            {
                **self.assignment_data,
                "title": "Lab 1 updated",
                "status": Assignment.Status.IN_PROGRESS,
            },
        )
        self.assertRedirects(response, reverse("assignment_detail", args=[assignment.pk]))
        assignment.refresh_from_db()
        self.assertEqual(assignment.title, "Lab 1 updated")
        self.assertEqual(assignment.status, Assignment.Status.IN_PROGRESS)

    def test_archive_does_not_delete_assignment(self):
        assignment = Assignment.objects.create(
            module=self.module,
            title="Lab 1",
            due_date=date(2026, 11, 15),
            priority=Assignment.Priority.MEDIUM,
            status=Assignment.Status.NOT_STARTED,
        )
        response = self.client.post(reverse("assignment_archive", args=[assignment.pk]))
        self.assertRedirects(response, reverse("assignment_list"))
        assignment.refresh_from_db()
        self.assertTrue(assignment.archived)
        self.assertTrue(Assignment.objects.filter(pk=assignment.pk).exists())
        list_response = self.client.get(reverse("assignment_list"))
        self.assertContains(list_response, "Lab 1")
        self.assertContains(list_response, "Archived")

    def test_required_fields_and_status_choices_are_validated(self):
        response = self.client.post(
            reverse("assignment_create"),
            {
                "module": "",
                "title": "  ",
                "description": "",
                "due_date": "",
                "priority": "Urgent",
                "status": "Overdue",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Assignment.objects.count(), 0)


class OverdueTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(code="COMS1018", name="Introduction to Algorithms")
        self.today = timezone.localdate()

    def _make_assignment(self, title, due_date, status):
        return Assignment.objects.create(
            module=self.module,
            title=title,
            due_date=due_date,
            priority=Assignment.Priority.MEDIUM,
            status=status,
        )

    def test_overdue_is_derived_and_completed_is_never_overdue(self):
        past_open = self._make_assignment(
            "Late lab",
            self.today - timedelta(days=1),
            Assignment.Status.NOT_STARTED,
        )
        past_done = self._make_assignment(
            "Finished lab",
            self.today - timedelta(days=1),
            Assignment.Status.COMPLETED,
        )
        due_today = self._make_assignment(
            "Due today",
            self.today,
            Assignment.Status.IN_PROGRESS,
        )
        future = self._make_assignment(
            "Upcoming lab",
            self.today + timedelta(days=1),
            Assignment.Status.NOT_STARTED,
        )

        self.assertTrue(past_open.is_overdue)
        self.assertFalse(past_done.is_overdue)
        self.assertFalse(due_today.is_overdue)
        self.assertFalse(future.is_overdue)
        self.assertNotEqual(past_open.status, "Overdue")

        response = self.client.get(reverse("assignment_list"))
        self.assertContains(response, "Late lab")
        self.assertContains(response, "Overdue")
        html = response.content.decode()
        finished_index = html.index("Finished lab")
        self.assertNotIn("Overdue", html[finished_index : finished_index + 80])


class SearchFilterTests(TestCase):
    def setUp(self):
        self.algorithms = Module.objects.create(code="COMS1018", name="Algorithms")
        self.networks = Module.objects.create(code="COMS3007", name="Networks")
        Assignment.objects.create(
            module=self.algorithms,
            title="Sorting lab",
            due_date=date(2026, 11, 15),
            priority=Assignment.Priority.HIGH,
            status=Assignment.Status.NOT_STARTED,
        )
        Assignment.objects.create(
            module=self.networks,
            title="Routing worksheet",
            due_date=date(2026, 11, 20),
            priority=Assignment.Priority.LOW,
            status=Assignment.Status.IN_PROGRESS,
        )

    def test_search_assignments_by_title(self):
        response = self.client.get(reverse("assignment_list"), {"q": "sorting"})
        self.assertContains(response, "Sorting lab")
        self.assertNotContains(response, "Routing worksheet")

    def test_filter_by_module_priority_or_status(self):
        by_module = self.client.get(
            reverse("assignment_list"),
            {"module": str(self.networks.pk)},
        )
        self.assertContains(by_module, "Routing worksheet")
        self.assertNotContains(by_module, "Sorting lab")

        by_priority = self.client.get(
            reverse("assignment_list"),
            {"priority": Assignment.Priority.HIGH},
        )
        self.assertContains(by_priority, "Sorting lab")
        self.assertNotContains(by_priority, "Routing worksheet")

        by_status = self.client.get(
            reverse("assignment_list"),
            {"status": Assignment.Status.IN_PROGRESS},
        )
        self.assertContains(by_status, "Routing worksheet")
        self.assertNotContains(by_status, "Sorting lab")


class DashboardTests(TestCase):
    def test_dashboard_counts_total_completed_pending_and_overdue(self):
        module = Module.objects.create(code="COMS1018", name="Algorithms")
        today = timezone.localdate()
        Assignment.objects.create(
            module=module,
            title="Done",
            due_date=today - timedelta(days=2),
            priority=Assignment.Priority.LOW,
            status=Assignment.Status.COMPLETED,
        )
        Assignment.objects.create(
            module=module,
            title="Late",
            due_date=today - timedelta(days=1),
            priority=Assignment.Priority.HIGH,
            status=Assignment.Status.NOT_STARTED,
        )
        Assignment.objects.create(
            module=module,
            title="Upcoming",
            due_date=today + timedelta(days=3),
            priority=Assignment.Priority.MEDIUM,
            status=Assignment.Status.IN_PROGRESS,
        )
        Assignment.objects.create(
            module=module,
            title="Old archived",
            due_date=today - timedelta(days=5),
            priority=Assignment.Priority.LOW,
            status=Assignment.Status.NOT_STARTED,
            archived=True,
        )

        response = self.client.get(reverse("home"))
        self.assertContains(response, "Total: 3")
        self.assertContains(response, "Completed: 1")
        self.assertContains(response, "Pending: 2")
        self.assertContains(response, "Overdue: 1")
