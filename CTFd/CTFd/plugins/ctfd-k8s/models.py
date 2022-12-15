import random
import uuid
from datetime import datetime

from jinja2 import Template

from CTFd.utils import get_config
from CTFd.models import db, Challenges


class KubernetesConfig(db.Model):
    key = db.Column(db.String(length=128), primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return "<KubernetesConfig {0} {1}>".format(self.key, self.value)


class KubernetesRedirectTemplate(db.Model):
    key = db.Column(db.String(20), primary_key=True)
    frp_template = db.Column(db.Text)
    access_template = db.Column(db.Text)

    def __init__(self, key, access_template, frp_template):
        self.key = key
        self.access_template = access_template
        self.frp_template = frp_template

    def __repr__(self):
        return "<KubernetesRedirectTemplate {0}>".format(self.key)

class DynamicKubernetesChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "dynamic_kubernetes"}
    id = db.Column(None, db.ForeignKey("challenges.id",
                                       ondelete="CASCADE"), primary_key=True)

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    memory_limit = db.Column(db.Text, default="128m")
    cpu_limit = db.Column(db.Float, default=0.5)
    dynamic_score = db.Column(db.Integer, default=0)

    kubernetes_config = db.Column(db.Text, default=0)
    connection_format = db.Column(db.Text, default="nc {host} {port}")

    def __init__(self, *args, **kwargs):
        super(DynamicKubernetesChallenge, self).__init__(**kwargs)
        self.initial = kwargs["value"]

class KubernetesContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(None, db.ForeignKey("users.id"))
    challenge_id = db.Column(None, db.ForeignKey("challenges.id"))
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    renew_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, default=1)
    uuid = db.Column(db.String(256))
    host = db.Column(db.Text, nullable=True, default="0.0.0.0")
    ports = db.Column(db.JSON, nullable=True, default=[])
    flag = db.Column(db.String(128), nullable=False)

    # Relationships
    user = db.relationship(
        "Users", foreign_keys="KubernetesContainer.user_id", lazy="select")
    challenge = db.relationship(
        "DynamicKubernetesChallenge", foreign_keys="KubernetesContainer.challenge_id", lazy="select"
    )

    @property
    def http_subdomain(self):
        return Template(get_config(
            'kubernetes:template_http_subdomain', '{{ container.uuid }}'
        )).render(container=self)

    def __init__(self, user_id, challenge_id):
        self.user_id = user_id
        self.challenge_id = challenge_id
        self.start_time = datetime.now()
        self.renew_count = 0
        self.uuid = str(uuid.uuid4())
        self.flag = Template(get_config(
            'kubernetes:template_chall_flag', '{{ "flag{"+uuid.uuid4()|string+"}" }}'
        )).render(container=self, uuid=uuid, random=random, get_config=get_config)

    @property
    def user_access(self):
        return Template(KubernetesRedirectTemplate.query.filter_by(
            key=self.challenge.redirect_type
        ).first().access_template).render(container=self, get_config=get_config)

    @property
    def frp_config(self):
        return Template(KubernetesRedirectTemplate.query.filter_by(
            key=self.challenge.redirect_type
        ).first().frp_template).render(container=self, get_config=get_config)

    def __repr__(self):
        return "<KubernetesContainer ID:{0} {1} {2} {3} {4}>".format(self.id, self.user_id, self.challenge_id,
                                                                self.start_time, self.renew_count)
