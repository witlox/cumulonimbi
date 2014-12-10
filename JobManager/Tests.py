__author__ = 'Johannes'

import unittest, Job


class MyTestCase(unittest.TestCase):
    def test_job_init(self):
        name = "test name"
        job = Job.Job({'name': name})

        self.assertEqual(job.name, name)


if __name__ == '__main__':
    unittest.main()
