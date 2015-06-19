import unittest

from hybrid_rulesets import RulesetIndustryCanada2015, RulesetFcc2012WithIndustryCanada2015ProtectedContourRadii, RulesetIndustryCanada2015WithoutFarSideSeparationDistanceConditionsOrTabooChannelExclusions, \
                            RulesetIndustryCanada2015WithoutFarSideSeparationDistanceConditions

from west.ruleset_fcc2012 import RulesetFcc2012

class UnitTestOfHybridRulesets(unittest.TestCase):

    def setUp(self):

        self.ruleset_industry_canada = RulesetIndustryCanada2015()
        self.ruleset_fcc = RulesetFcc2012()
        self.hybrid_ruleset_1 = RulesetFcc2012WithIndustryCanada2015ProtectedContourRadii()
        self.hybrid_ruleset_2 = RulesetIndustryCanada2015WithoutFarSideSeparationDistanceConditionsOrTabooChannelExclusions()
        self.hybrid_ruleset_3 = RulesetIndustryCanada2015WithoutFarSideSeparationDistanceConditions()

        self.uhf_center_frequency = 479
        self.hvhf_center_frequency = 213
        self.lvhf_center_frequency = 85
        self.list_of_haats = [0, 4, 12, 32, 55, 81, 100, 151, 213]

    def test_hybrid_ruleset_1(self):

        """This test is written to assert that this hybrid ruleset has the same target field strengths as the IC ruleset."""

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(1, self.uhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(1, self.uhf_center_frequency))

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(1, self.hvhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(1, self.hvhf_center_frequency))

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(1, self.lvhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(1, self.lvhf_center_frequency))

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(0, self.uhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(0, self.uhf_center_frequency))

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(0, self.hvhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(0, self.hvhf_center_frequency))

        self.assertEqual(self.hybrid_ruleset_1.get_tv_target_field_strength_dBu(0, self.lvhf_center_frequency),
                         self.ruleset_industry_canada.get_tv_target_field_strength_dBu(0, self.lvhf_center_frequency))


    def test_hybrid_ruleset_2(self):

        """This test is written to assert that far side separation distance conditions and taboo channel exclusions
        are not applied for this hybrid ruleset."""

        self.assertEqual(self.hybrid_ruleset_2._apply_far_side_separation_distance_conditions, False)
        self.assertEqual(self.hybrid_ruleset_2._apply_taboo_channel_exclusions, False)

        self.assertEqual(self.ruleset_industry_canada._apply_far_side_separation_distance_conditions, True)
        self.assertEqual(self.ruleset_industry_canada._apply_taboo_channel_exclusions, True)


    def test_hybrid_ruleset_3(self):

        """This test is written to assert that far side separation distances are not applied, but taboo channel
        exclusions are applied for this hybrid ruleset."""

        self.assertEqual(self.hybrid_ruleset_3._apply_far_side_separation_distance_conditions, False)
        self.assertEqual(self.hybrid_ruleset_3._apply_taboo_channel_exclusions, True)

        self.assertEqual(self.ruleset_industry_canada._apply_far_side_separation_distance_conditions, True)
        self.assertEqual(self.ruleset_industry_canada._apply_taboo_channel_exclusions, True)


unittest.main()




