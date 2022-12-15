import warnings

from flask import current_app
from requests import session, RequestException

from CTFd.models import db
from CTFd.utils import get_config, set_config, logging

from .base import BaseRouter
from ..cache import CacheProvider
from ..db import DBContainer
from ..kubernetes import KubernetesUtils, get_templated_yaml
from ..exceptions import KubernetesError, KubernetesWarning
from ...models import KubernetesContainer


class K8sRouter(BaseRouter):
    name = "k8s"

    def reload(self, exclude=None):
        pass

    def access(self, container: KubernetesContainer):
        return f'host={container.host} ports={container.ports}'

    def register(self, container: KubernetesContainer):
        external_ip, ports = KubernetesUtils.get_container_connection_info(container)
        container.host = external_ip
        container.ports = ports
        db.session.commit()
        return True, 'success'

    def unregister(self, container: KubernetesContainer):
        return True, 'success'

    def check_availability(self):
        return True, 'Available'
