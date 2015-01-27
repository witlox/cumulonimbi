__author__ = 'Johannes'

import sys
import logging
import mock
import unittest
import networkx as nx

from job_manager.runner import Runner
from job_manager.task import Task


class TestRunner(unittest.TestCase):

    def test_dag_execution(self):
        # build a DAG
        g = nx.Graph()
        t1 = Task("hello")
        t2 = Task("world")
        t3 = Task("!")
        g.add_edge(t1, t2)
        g.add_edge(t2, t3)

        # Arrange
        runner = Runner(g)
        with mock.patch('job_manager.runner.Runner.__execute__') as me:
            for edge in nx.dfs_edges(g):
                logging.warning("left: %s, right: %s", edge[0].label, edge[1].label)
            # Act
            runner.run()
            # Assert
            me.assert_any_call(t1.label, t1.executable, t1.parameters)
            me.assert_any_call(t2.label, t2.executable, t2.parameters)
            me.assert_any_call(t3.label, t3.executable, t3.parameters)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
