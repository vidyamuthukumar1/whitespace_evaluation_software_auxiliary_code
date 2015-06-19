from ruleset_industrycanada2015 import RulesetIndustryCanada2015
from west.device import Device

import unittest

class UnitRulesetIndustryCanada2015TestCase(unittest.TestCase):

    """This class contains a bunch of tests to check whether the correct separation distances are being used
    in RulesetIndustryCanada2015. Since these values were manually entered while writing the code for the ruleset,
    one can easily make errors and this is a sort of sanity check.

    #TODO: Compress all code to avoid repeated blocks.
    """

    def setUp(self):
        self.ruleset = RulesetIndustryCanada2015()
        self.uhf_center_frequency = 479
        self.hvhf_center_frequency = 213
        self.lvhf_center_frequency = 85
        self.list_of_haats = [0, 4, 12, 32, 55, 81, 100, 151, 213]

    def test_cochannel_sep_distances_fixed_devices(self):

        """This test checks whether the correct cochannel separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m."""

        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                1), 18.7)
        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                0), 14.7)

        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                1), 30.2)
        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                0), 25.1)

        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                1), 47.9)
        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                0), 36.5)

    def test_cochannel_far_side_sep_distances_fixed_devices(self):

        """This test checks whether the correct cochannel far side separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct far side separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m."""

        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                1), 42.2)
        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                0), 21.1)

        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                1), 63.3)
        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                0), 36.3)

        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                1), 90.3)
        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                0), 55.4)

    def test_adjchannel_sep_distances_fixed_devices(self):

        """This test checks whether the correct adjacent channel separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m."""

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         1), 1.4)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         0), 1.0)

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         1), 1.7)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         0), 2.0)

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         1), 2.5)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         0), 2.2)


    def test_adjchannel_far_side_sep_distances_fixed_devices(self):

        """This test checks whether the correct adjacent channel far side separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct far side separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m."""

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         1), 2.5)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         0), 1.8)

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         1), 3.4)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         0), 2.2)

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         1), 4.5)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         0), 3.0)

    def test_taboo_channel_sep_distances_fixed_devices(self):

        """This test checks whether the correct taboo channel separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m.

        .. note:: Since no taboo channel restrictions apply for digital TV, we restrict this test to analog TV."""

        self.assertEqual(self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         0), 1.0)

        self.assertEqual(self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         0), 2.0)

        self.assertEqual(self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         0), 2.2)

    def test_taboo_channel_far_side_sep_distances_fixed_devices(self):

        """This test checks whether the correct taboo channel separation distances were used for a fixed device of HAAT 30 meters.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This is by no means the best or most complete method of testing. We have restricted ourselves to this test for
        now, in the interest of time, to at least check if the correct separation distances were used for the device we are considering
        for our whitespace evaluation. That is, a fixed device of HAAT 30 m.

        ..note:: Since no taboo channel restrictions apply for digital TV, we restrict this test to analog TV."""

        self.assertEqual(self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(30, self.uhf_center_frequency,
                                                                                                         0), 1.8)

        self.assertEqual(self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(30, self.hvhf_center_frequency,
                                                                                                         0), 2.2)

        self.assertEqual(self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(30, self.lvhf_center_frequency,
                                                                                                         0), 3.0)

    def test_cochannel_sep_distances_portable_devices(self):

        """This test checks whether the correct cochannel separation distances were used for a portable device.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
        class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_portable_devices(1), 14.4)
        self.assertEqual(self.ruleset.get_tv_cochannel_separation_distance_km_for_portable_devices(0), 11.4)

    def test_cochannel_far_side_sep_distances_portable_devices(self):

        """This test checks whether the correct cochannel far side separation distances were used for a portable device.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
        class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_portable_devices(1), 35.1)
        self.assertEqual(self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_portable_devices(0), 21.1)

    def test_adjchannel_sep_distances_portable_devices(self):

        """This test checks whether the correct adjacent channel separation distances were used for a portable device.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
        class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_portable_devices(1), 1.1)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_portable_devices(0), 1.0)

    def test_adjchannel_far_side_sep_distances_portable_devices(self):

        """This test checks whether the correct adjacent channel far side separation distances were used for a portable device.
         Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

         .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
         class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_portable_devices(1), 1.9)
        self.assertEqual(self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_portable_devices(0), 1.8)

    def test_taboo_channel_sep_distances_portable_devices(self):

        """This test checks whether the correct taboo channel separation distances were used for a portable device.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
        class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_taboo_channel_separation_distance_km_for_portable_devices(0), 1.0)

    def test_taboo_channel_far_side_sep_distances_portable_devices(self):

        """This test checks whether the correct taboo channel far side separation distances were used for a portable device.
        Separation distances obtained from http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf10928.html.

        .. note:: This test was written only to make sure we did not make typos while writing the RulesetIndustryCanada2015
        class. The rationale is that we're not likely to mis-type sep distance values more than once :)"""

        self.assertEqual(self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_portable_devices(0), 1.8)

    def test_monotonicity_with_haat_cochannel_sep_distances_fixed_devices(self):

        """This test was written to check whether the required cochannel separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Passes for all cases."""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

    def test_monotonicity_with_haat_cochannel_far_side_sep_distances_fixed_devices(self):

        """This test was written to check whether the required cochannel separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Passes for all cases."""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

    def test_monotonicity_with_haat_adjchannel_sep_distances_fixed_devices(self):

        """This test was written to check whether the required adjacent channel separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Does not pass for one case as it is not monotonic in the original table for this case!"""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        #This test does not pass because, for some reason, the adjacent channel sep distances DO NOT increase with HAAT for high VHF frequencies and analog TV
        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance


    def test_monotonicity_with_haat_adjchannel_far_side_sep_distances_fixed_devices(self):

        """This test was written to check whether the required adjacent channel far side separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Passes for all cases."""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 1)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

    def test_monotonicity_with_haat_taboo_channel_sep_distances_fixed_devices(self):

        """This test was written to check whether the required taboo channel separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Does not pass for one case as it is not monotonic in the original table for this case!"""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        #This test does not pass because, for some reason, the adjacent channel sep distances DO NOT increase with HAAT for high VHF frequencies and analog TV,
        # and the taboo channel function simply calls the adjacent channel function.
        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

    def test_monotonicity_with_haat_taboo_channel_far_side_sep_distances_fixed_devices(self):

        """This test was written to check whether the required taboo channel far side separation distance increases with device HAAT,
        keeping all other parameters constant. This is a natural sanity check.
        Passes for all cases."""

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.uhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.hvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance

        current_sep_distance = 0
        for haat in self.list_of_haats:
            next_sep_distance = self.ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(haat, self.lvhf_center_frequency, 0)
            self.assertLessEqual(current_sep_distance, next_sep_distance)
            current_sep_distance = next_sep_distance



unittest.main()
