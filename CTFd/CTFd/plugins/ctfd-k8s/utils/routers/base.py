import typing

from ...models import KubernetesContainer


class BaseRouter:
    name = None

    def __init__(self):
        pass

    def access(self, container: KubernetesContainer):
        pass

    def register(self, container: KubernetesContainer):
        pass

    def unregister(self, container: KubernetesContainer):
        pass

    def reload(self):
        pass

    def check_availability(self) -> typing.Tuple[bool, str]:
        pass
