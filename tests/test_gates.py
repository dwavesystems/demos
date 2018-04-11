import unittest

from factoring.gates import gate_model

import dimod


class TestGates(unittest.TestCase):

    def test_and(self):
        pm = gate_model('AND', False)
        es = dimod.ExactSolver()
        resp = es.sample(pm.model)

        min_energy = min(resp.data(['energy'])).energy
        for sample, energy in resp.data(['sample', 'energy']):
            if energy == min_energy:
                self.assertEqual(sample['in1'] and sample['in2'], sample['out'])
            else:
                self.assertNotEqual(sample['in1'] and sample['in2'], sample['out'])

    @unittest.skip("Penalty model not in pre-populated cache")
    def test_or(self):
        pm = gate_model('OR', False)
        es = dimod.ExactSolver()
        resp = es.sample(pm.model)

        min_energy = min(resp.data(['energy'])).energy
        for sample, energy in resp.data(['sample', 'energy']):
            if energy == min_energy:
                self.assertEqual(sample['in1'] or sample['in2'], sample['out'])
            else:
                self.assertNotEqual(sample['in1'] or sample['in2'], sample['out'])

    @unittest.skip("Penalty model not in pre-populated cache")
    def test_xor(self):
        pm = gate_model('XOR', False)
        es = dimod.ExactSolver()
        resp = es.sample(pm.model)

        min_energy = min(resp.data(['energy'])).energy
        for sample, energy in resp.data(['sample', 'energy']):
            if energy == min_energy:
                self.assertEqual(sample['in1'] != sample['in2'], sample['out'])
            else:
                self.assertNotEqual(sample['in1'] != sample['in2'], sample['out'])

    def test_half_add(self):
        pm = gate_model('HALF_ADD', False)
        es = dimod.ExactSolver()
        resp = es.sample(pm.model)

        min_energy = min(resp.data(['energy'])).energy
        for sample, energy in resp.data(['sample', 'energy']):
            if energy == min_energy:
                self.assertEqual(sample['augend'] + sample['addend'], sample['sum'] + (sample['carry_out'] << 1))
            else:
                self.assertNotEqual(sample['augend'] + sample['addend'], sample['sum'] + (sample['carry_out'] << 1))

    def test_full_add(self):
        pm = gate_model('FULL_ADD', False)
        es = dimod.ExactSolver()
        resp = es.sample(pm.model)

        min_energy = min(resp.data(['energy'])).energy
        for sample, energy in resp.data(['sample', 'energy']):
            if energy == min_energy:
                self.assertEqual(sample['augend'] + sample['addend'] + sample['carry_in'],
                                 sample['sum'] + (sample['carry_out'] << 1))
            else:
                self.assertNotEqual(sample['augend'] + sample['addend'] + sample['carry_in'],
                                    sample['sum'] + (sample['carry_out'] << 1))
