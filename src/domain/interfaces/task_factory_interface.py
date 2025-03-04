from abc import ABC, abstractmethod

from domain.interfaces.task_interface import ITask


class ITaskFactory(ABC):
    @abstractmethod
    def create_task(task_name: str) -> ITask:
        ...
