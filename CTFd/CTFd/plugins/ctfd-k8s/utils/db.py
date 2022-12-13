import datetime

from CTFd.models import db
from CTFd.utils import get_config
from ..models import KubernetesContainer, KubernetesRedirectTemplate


class DBContainer:
    @staticmethod
    def create_container_record(user_id, challenge_id):
        container = KubernetesContainer(user_id=user_id, challenge_id=challenge_id)
        db.session.add(container)
        db.session.commit()

        return container

    @staticmethod
    def get_current_containers(user_id):
        q = db.session.query(KubernetesContainer)
        q = q.filter(KubernetesContainer.user_id == user_id)
        return q.first()

    @staticmethod
    def get_container_by_port(port):
        q = db.session.query(KubernetesContainer)
        q = q.filter(KubernetesContainer.port == port)
        return q.first()

    @staticmethod
    def remove_container_record(user_id):
        q = db.session.query(KubernetesContainer)
        q = q.filter(KubernetesContainer.user_id == user_id)
        q.delete()
        db.session.commit()

    @staticmethod
    def get_all_expired_container():
        timeout = int(get_config("kubernetes:docker_timeout", "3600"))

        q = db.session.query(KubernetesContainer)
        q = q.filter(
            KubernetesContainer.start_time <
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_alive_container():
        timeout = int(get_config("kubernetes:docker_timeout", "3600"))

        q = db.session.query(KubernetesContainer)
        q = q.filter(
            KubernetesContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_container():
        q = db.session.query(KubernetesContainer)
        return q.all()

    @staticmethod
    def get_all_alive_container_page(page_start, page_end):
        timeout = int(get_config("kubernetes:docker_timeout", "3600"))

        q = db.session.query(KubernetesContainer)
        q = q.filter(
            KubernetesContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        q = q.slice(page_start, page_end)
        return q.all()

    @staticmethod
    def get_all_alive_container_count():
        timeout = int(get_config("kubernetes:docker_timeout", "3600"))

        q = db.session.query(KubernetesContainer)
        q = q.filter(
            KubernetesContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.count()


class DBRedirectTemplate:
    @staticmethod
    def get_all_templates():
        return KubernetesRedirectTemplate.query.all()

    @staticmethod
    def create_template(name, access_template, frp_template):
        if KubernetesRedirectTemplate.query.filter_by(key=name).first():
            return  # already existed
        db.session.add(KubernetesRedirectTemplate(
            name, access_template, frp_template
        ))
        db.session.commit()

    @staticmethod
    def delete_template(name):
        KubernetesRedirectTemplate.query.filter_by(key=name).delete()
        db.session.commit()
