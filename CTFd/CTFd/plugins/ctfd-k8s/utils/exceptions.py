class KubernetesError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class KubernetesWarning(Warning):
    pass
