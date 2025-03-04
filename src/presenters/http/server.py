import uvicorn

from infrastructure.workers.celery.app import create_app as celery_create_app

from .app import create_app

if __name__ == '__main__':
    app = create_app(callbacks=[celery_create_app])

    uvicorn.run(
        app=app,
        host=app.container.config.app_host(),
        port=app.container.config.app_port(),
    )
