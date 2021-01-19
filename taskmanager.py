from task import Task


class Tasks:
    def __init__(self):
        self.tasks = {}
        self._last_task_key = 0
        self.url = ""
        self.role = ""

    def add_task(self, task):
        self._last_task_key += 1
        self.tasks[self._last_task_key] = task
        return self._last_task_key

    def delete_task(self, task_key):
        if task_key in self.tasks:
            del self.tasks[task_key]

    def get_task(self, task_key):
        task = self.tasks.get(task_key)
        if task is None:
            return None
        task_ = Task(task.title, url=task.url,role=task.role)
        return task_

    def get_tasks(self):
        tasks = []
        for task_key, task in self.tasks.items():
            task_ = Task(task.title, url=task.url,role=task.role)
            tasks.append((task_key, task_))
        return tasks

    def set_task(self,task_key,new_title,new_url):
        task = self.tasks.get(task_key)
        task.title = new_title
        task.url = new_url

    def get_last_task_key(self):
        return self._last_task_key

    def clear_tasks(self):
        for task_key, task in self.get_tasks():
            self.delete_task(task_key)

    def add_all_tasks(self):
        self.add_task(Task("All Employees", "all_persons", "admin"))
        self.add_task(Task("My profile", "my_profile", "admin"))
        self.add_task(Task("Enroll Project", "enroll_project", "admin"))
        self.add_task(Task("Projects", "my_projects", "admin"))
        self.add_task(Task("Add team", "add_team", "admin"))
        self.add_task(Task("Teams", "my_teams", "admin"))
        self.add_task(Task("My projects", "my_projects", "team_leader"))
        self.add_task(Task("My Team", "my_teams", "team_leader"))
        self.add_task(Task("Enroll Project", "enroll_project", "team_leader"))
        self.add_task(Task("My profile", "my_profile", "team_leader"))
        self.add_task(Task("Enroll Project", "enroll_project", "employee"))
        self.add_task(Task("My profile", "my_profile", "employee"))
        self.add_task(Task("My Team", "my_teams", "employee"))
        self.add_task(Task("My projects", "my_projects", "employee"))
        self.add_task(Task("Enroll Project", "enroll_project", "project_manager"))
        self.add_task(Task("My profile", "my_profile", "project_manager"))
        self.add_task(Task("My Team", "my_teams", "project_manager"))
        self.add_task(Task("My projects", "my_projects", "project_manager"))
