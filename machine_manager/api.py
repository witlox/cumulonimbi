from flask import Flask
from machine_manager.azurelistener import AzureListener
from settings import Settings

app = Flask(__name__)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


def start():
    settings = Settings()
    settings.configure_logging('../logs/machine_manager.log', 'MachineManager')

    listener = AzureListener()
    listener.start()

    app.run("0.0.0.0", settings.machine_manager_api_port, debug=False)

    listener.quit()
    listener.join()
