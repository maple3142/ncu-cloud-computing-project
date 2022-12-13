import json
import random
import uuid
from collections import OrderedDict

from kubernetes import client, config
import subprocess
from flask import current_app

from CTFd.utils import get_config, logging
from CTFd.models import db

from ..models import KubernetesContainer
from .cache import CacheProvider
from .exceptions import KubernetesError

from tempfile import NamedTemporaryFile
from hashlib import sha256
from contextlib import contextmanager


def get_challenge_id(container: KubernetesContainer):
    chal_id = f"{container.user_id}-{container.uuid}"
    short_id = sha256(chal_id.encode()).hexdigest()[:16]
    return chal_id, short_id


@contextmanager
def get_templated_yaml(container: KubernetesContainer):
    chal_id, short_id = get_challenge_id(container)
    flag = container.flag
    with NamedTemporaryFile("w", suffix=".yaml") as tmpf:
        formatted_yaml = container.challenge.kubernetes_config.format(
            id=chal_id, short_id=short_id, flag=container.flag
        )
        if f"chal-id: '{chal_id}'" not in formatted_yaml:
            # some sanity check
            raise KubernetesError(
                "Kubernetes Config Error\n"
                "The challenge config must contain templated chal-id as label"
            )
        tmpf.write(formatted_yaml)
        tmpf.flush()
        yield tmpf


class KubernetesUtils:
    @staticmethod
    def init():
        try:
            config.load_kube_config()
            KubernetesUtils.v1 = client.CoreV1Api()
            subprocess.run(["kubectl", "version"], check=True)
        except Exception:
            raise KubernetesError("Kubernetes Connection Error\n")

    @staticmethod
    def add_container(container: KubernetesContainer):
        chal_id, short_id = get_challenge_id(container)
        chal_selector = f"chal-id={chal_id}"
        with get_templated_yaml(container) as tmpf:
            proc = subprocess.run(
                ["kubectl", "apply", "-f", tmpf.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if proc.returncode != 0:
                raise KubernetesError(
                    "Kubernetes Apply Error\n"
                    f"{proc.stdout.decode()}\n{proc.stderr.decode()}"
                )
            services = KubernetesUtils.v1.list_namespaced_service(
                namespace="default", label_selector=chal_selector
            ).items
            if len(services) == 0:
                raise KubernetesError(
                    "Kubernetes Service Error\n" "Failed to apply service"
                )
            service = services[0]
            logging.log(
                'kubernetes',
                f"Created {service.metadata.name} {[(p.node_port, p.port, p.target_port) for p in service.spec.ports]}"
            )
    
    @staticmethod
    def get_container_connection_info(container: KubernetesContainer):
        chal_id, short_id = get_challenge_id(container)
        chal_selector = f"chal-id={chal_id}"
        services = KubernetesUtils.v1.list_namespaced_service(
                namespace="default", label_selector=chal_selector
            ).items
        service = services[0]
        node_port = service.spec.ports[0].node_port
        pods = KubernetesUtils.v1.list_namespaced_pod(
                namespace="default", label_selector=chal_selector
            ).items
        target_node_name = pods[0].spec.node_name
        nodes = KubernetesUtils.v1.list_node()
        node = [n for n in nodes.items if n.metadata.name == target_node_name][0]
        external_ip = [
                addr.address
                for addr in node.status.addresses
                if addr.type == "ExternalIP"
            ][0]
        return external_ip, node_port

    @staticmethod
    def remove_container(container):
        chal_id, short_id = get_challenge_id(container)
        chal_selector = f"chal-id={chal_id}"
        with get_templated_yaml(container) as tmpf:
            subprocess.run(["kubectl", "delete", "-f", tmpf.name])
