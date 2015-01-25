__author__ = 'Johannes'

import unittest, Job


class MyTestCase(unittest.TestCase):
    def test_job_init(self):
        name = "test name"
        job = Job.Job({'name': name})

        self.assertEqual(job.name, name)

    def test_failure(self):
        name = "test name"
        job = Job.Job({'name': name})

        self.assertEqual(job.name, "abc")

if __name__ == '__main__':
    unittest.main()
