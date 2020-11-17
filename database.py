from task import Task


class Database:
    def __init__(self):
        self.tasks = {}
        self._last_task_key = 0
        self.url = ""

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
        task_ = Task(task.title, url=task.url)
        return task_

    def get_tasks(self):
        tasks = []
        for task_key, task in self.tasks.items():
            task_ = Task(task.title, url=task.url)
            tasks.append((task_key, task_))
        return tasks

    def set_task(self,task_key,new_title,new_url):
        task = self.tasks.get(task_key)
        task.title = new_title
        task.url = new_url

