import unittest

from ml.profiles import Profile, OT, CT, RT, CounterKey

class TestProfiles(unittest.TestCase):
    def test_serialization(self):
        user_profile = Profile(1, OT.USER)
        user_profile.counters.set(OT.AUTHOR, CT.HAS, RT.SUM, object_id=42, value=1, ts=9000)
        user_profile.counters.set(OT.RUBRIC, CT.HAS, RT.SUM, object_id=1337, value=10, ts=1234)
        user_profile.counters.set(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', value=93.6, ts=1234)
        key = CounterKey(OT.AUTHOR, CT.HAS, RT.SUM)
        assert user_profile.counters.data[key][42].value == 1
        assert vars(user_profile)["counters"][key][0] == (42, 1, 9000)
        user_profile_2 = Profile.loads(user_profile.dumps())
        assert str(vars(user_profile)) == str(vars(user_profile_2))
