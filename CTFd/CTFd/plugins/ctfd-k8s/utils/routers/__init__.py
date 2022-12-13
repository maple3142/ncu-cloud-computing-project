from CTFd.utils import get_config

from .k8s import K8sRouter

_routers = {
    'k8s': K8sRouter,
}


def instanciate(cls):
    return cls()


@instanciate
class Router:
    _name = ''
    _router = None

    def __getattr__(self, name: str):
        router_conftype = get_config("kubernetes:router_type", "k8s")
        if Router._name != router_conftype:
            Router._router = _routers[router_conftype]()
            Router._name = router_conftype
        return getattr(Router._router, name)

    @staticmethod
    def reset():
        Router._name = ''
        Router._router = None


__all__ = ["Router"]
