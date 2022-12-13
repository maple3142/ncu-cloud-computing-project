from docker.errors import DockerException, TLSParameterError, APIError, requests

from CTFd.utils import get_config

# from .docker import get_docker_client
from .routers import Router


class KubernetesChecks:
    @staticmethod
    def check_docker_api():
        pass

    @staticmethod
    def check_frp_connection():
        pass

    @staticmethod
    def perform():
        errors = []
        for attr in dir(KubernetesChecks):
            if attr.startswith('check_'):
                err = getattr(KubernetesChecks, attr)()
                if err:
                    errors.append(err)
        return errors
