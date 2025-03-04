from celery import Celery


def create_app() -> Celery:
    from containers import Container

    container = Container()
    container.wire(
        packages=[
            'infrastructure.tasks.celery_implementation',
        ]
    )

    app = Celery()
    app.container = container
    app.config_from_object({
        'CELERY_BROKER_URL': container.config.broker_url(),
        'CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP': True,
    }, namespace='CELERY')
    app.conf.task_serializer = 'pickle'
    app.conf.task_always_eager = False
    app.conf.accept_content = (
        'application/x-python-serialize',
    )
    app.autodiscover_tasks(
        packages=[
            'infrastructure.tasks.celery_implementation',
        ],
    )

    return app
