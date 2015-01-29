__author__ = 'Johannes'

import subprocess as p
import networkx as nx


class Runner:

    """
    This runner will run
    """

    def __init__(self, execution_graph):
        """
        :param execution_graph: graph (DAG) of the execution flow (networkx)
        :return: instance of Runner
        """
        self.execution_graph = execution_graph

    def run(self):
        done = []
        for task in nx.dfs_edges(self.execution_graph):
            if not task[0] in done:
                self.__execute__(task[0].label, task[0].executable, task[0].parameters)
            done.append(task[0])
            if not task[1] in done:
                self.__execute__(task[1].label, task[1].executable, task[1].parameters)
            done.append(task[1])

    def __execute__(name, exe, args):
        if name and exe:
            p.call(executable=exe, args=args)
