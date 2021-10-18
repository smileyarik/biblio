import unittest

from ml.profiles import Profile, ONE_DAY_SECONDS, OT, CT, RT, CounterKey, Counters

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

    def test_counter_single_add(self):
        counters = Counters()
        counters.add(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', delta=1000, ts=1)
        self.assertAlmostEqual(counters.get(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', ts=1+30*ONE_DAY_SECONDS), 500, places=5)

    def test_counter_multiple_straight_add(self):
        counters = Counters()
        counters.add(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', delta=1000, ts=1)
        counters.add(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', delta=2000, ts=1)
        self.assertAlmostEqual(counters.get(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', ts=1+30*ONE_DAY_SECONDS), 1500, places=5)

    def test_counter_multiple_reverse_add(self):
        counters = Counters()
        counters.add(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', delta=1000, ts=1+30*ONE_DAY_SECONDS)
        counters.add(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', delta=2000, ts=1)
        self.assertAlmostEqual(counters.get(OT.GLOBAL, CT.VALUE, RT.D30, object_id='', ts=1+30*ONE_DAY_SECONDS), 2000, places=5)
