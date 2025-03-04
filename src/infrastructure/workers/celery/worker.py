from .app import create_app

if __name__ == '__main__':
    app = create_app()

    worker = app.Worker(loglevel='INFO')
    worker.start()
