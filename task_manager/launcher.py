from task_manager.azureworker import AzureWorker


def start():
    """
    Run the Task Manager from here with the configured settings
    This is a blocking call
    """

    worker = AzureWorker()
    worker.start()
