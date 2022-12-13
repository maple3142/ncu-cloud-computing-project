from subprocess import run
from tempfile import NamedTemporaryFile
from kubernetes import client, config
import sys

template_file = sys.argv[1]
chal_id = sys.argv[2]
action = sys.argv[3]

with NamedTemporaryFile("w", suffix=".yaml") as tmpf:
    with open(template_file) as f:
        content = f.read()
        tmpf.write(content.format(id=chal_id))
        tmpf.flush()
    if action == "apply":
        run(["kubectl", "apply", "-f", tmpf.name])

        config.load_kube_config()
        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(
            namespace="default", label_selector=f"chal-id={chal_id}"
        ).items
        if len(services) > 0:
            service = services[0]
            print(
                f"{service.metadata.name} {[(p.node_port, p.port, p.target_port) for p in service.spec.ports]}"
            )
            node_port = service.spec.ports[0].node_port
            pods = v1.list_namespaced_pod(
                namespace="default", label_selector=f"chal-id={chal_id}"
            ).items
            target_node_name = pods[0].spec.node_name
            nodes = v1.list_node()
            node = [n for n in nodes.items if n.metadata.name == target_node_name][0]
            external_ip = [
                addr.address
                for addr in node.status.addresses
                if addr.type == "ExternalIP"
            ][0]
            print(f"nc {external_ip} {node_port}")
        else:
            print("Failed to apply service")
    elif action == "delete":
        run(["kubectl", "delete", "-f", tmpf.name])
    else:
        print("Unknown action: {}".format(action))
