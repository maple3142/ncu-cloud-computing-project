from docker.errors import DockerException, TLSParameterError, APIError, requests

from CTFd.utils import get_config

from .docker import get_docker_client
from .routers import Router


class KubernetesChecks:
    @staticmethod
    def check_docker_api():
        try:
            client = get_docker_client()
        except TLSParameterError as e:
            return f'Kubernetes TLS Parameters incorrect ({e})'
        except DockerException as e:
            return f'Kubernetes API url incorrect ({e})'
        try:
            client.ping()
        except (APIError, requests.RequestException):
            return f'Unable to connect to Kubernetes API, check your API connectivity'

        credentials = get_config("kubernetes:docker_credentials")
        if credentials and credentials.count(':') == 1:
            try:
                client.login(*credentials.split(':'))
            except DockerException:
                return f'Unable to log into docker registry, check your credentials'
        swarm = client.info()['Swarm']
        if not swarm['ControlAvailable']:
            return f'Kubernetes swarm not available. You should initialize a swarm first. ($ docker swarm init)'

    @staticmethod
    def check_frp_connection():
        ok, msg = Router.check_availability()
        if not ok:
            return msg

    @staticmethod
    def perform():
        errors = []
        for attr in dir(KubernetesChecks):
            if attr.startswith('check_'):
                err = getattr(KubernetesChecks, attr)()
                if err:
                    errors.append(err)
        return errors
