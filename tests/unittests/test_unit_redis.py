import unittest
import time
import rom

class TestRedis(unittest.TestCase):
    def test_redis_insert(self):
        rom.util.set_connection_settings(host='localhost', db=7)

        name = "ABC12345"
        temp_obj = TestObject.get_by(name=name)
        if temp_obj:
            temp_obj.delete()

        test_object = TestObject(name="ABC12345", extra="OK dan")
        test_object.save()

        get_object = TestObject.get_by(name="ABC12345")
        self.assertEqual(test_object.extra, get_object.extra)


class TestObject(rom.Model):
    name = rom.String(required=True, unique=True, suffix=True, keygen=rom.FULL_TEXT)
    extra = rom.String()
    created_on = rom.Float(default=time.time)
