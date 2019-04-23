# This Python file uses the following encoding: utf-8

import sys

import dimod

from circuit_fault_diagnosis.gates import gate_model, GATES

_PY2 = sys.version_info.major == 2

if _PY2:
    def iteritems(d):
        return d.iteritems()

    def itervalues(d):
        return d.itervalues()

else:
    def iteritems(d):
        return d.items()

    def itervalues(d):
        return d.values()


# adapted from dwave_constraint_compilers.stitch()
def stitch(models):
    """
    Take a list of :class:`pm.PenaltyModel` models, and 'stitch' them together:
    The variable set of the new model is the additive union of the variable sets of the models,
    the relations set of the new model is the additive union of the relation sets of the models.

    That is, the new widget contains every variable and coupler that is in any widget,
    and the bias of a variable or relation is the sum of the biases in of the variable
    or relation in all models that contain it.

    Similarly, the offset is summed across all models.

    All constraints are converted to :class:`pm.Vartype.SPIN`.

    Args:
        models (list[pm.PenaltyModel]): A list of penalty models to be stiched together.

    Returns:
        :class:`dimod.BinaryQuadraticModel`: The resulting :class:`BinaryQuadraticModel`.

    """
    linear = {}
    quadratic = {}
    offset = 0
    for widget in models:
        for variable, bias in iteritems(widget.model.linear):
            linear[variable] = linear.get(variable, 0) + bias

        for relation, bias in iteritems(widget.model.quadratic):
            quadratic[relation] = quadratic.get(relation, 0) + bias

        offset += widget.model.offset

    return dimod.BinaryQuadraticModel(linear, quadratic, offset, dimod.SPIN)


def new_pmodel(pmodel, old_labels, new_labels):
    def new_aux():
        new_pmodel.counter += 1
        return "aux%i" % new_pmodel.counter

    mapping = dict(zip(old_labels, new_labels))
    mapping.update({x: new_aux() for x in pmodel.graph.nodes if x not in old_labels})
    return pmodel.relabel_variables(mapping, inplace=False)
new_pmodel.counter = 0


def three_bit_multiplier(fault=True):
    ####################################################################################################
    # get basic gate fault models
    ####################################################################################################

    # print("AND gate fault model")
    pmodel_and = gate_model('AND', fault)

    # print("half adder fault model")
    pmodel_half_add = gate_model('HALF_ADD', fault)

    # print("full adder fault model")
    pmodel_full_add = gate_model('FULL_ADD', fault)

    ####################################################################################################
    # wire the whole thing up
    ####################################################################################################

    models = []
    labels = {}

    #                            a2 & b0  a1 & b0  a0 & b0
    #                   a2 & b1  a1 & b1  a0 & b1
    #          a2 & b2  a1 & b2  a0 & b2
    # ────────────────────────────────────────────────────
    #    p5       p4       p3       p2       p1       p0

    #                      and20  and10  and00
    #               and21  and11  and01
    #        and22  and12  and02
    # ────────────────────────────────────────
    #   p5     p4     p3     p2     p1     p0

    labels_and, _ = GATES['AND']
    labels['AND'] = {}

    labels['AND']['and00'] = ('a0', 'b0', 'p0')
    labels['AND']['and01'] = ('a0', 'b1', 'and01')
    labels['AND']['and02'] = ('a0', 'b2', 'and02')
    labels['AND']['and10'] = ('a1', 'b0', 'and10')
    labels['AND']['and11'] = ('a1', 'b1', 'and11')
    labels['AND']['and12'] = ('a1', 'b2', 'and12')
    labels['AND']['and20'] = ('a2', 'b0', 'and20')
    labels['AND']['and21'] = ('a2', 'b1', 'and21')
    labels['AND']['and22'] = ('a2', 'b2', 'and22')

    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and00']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and01']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and02']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and10']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and11']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and12']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and20']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and21']))
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']['and22']))

    #                                         and20         and10         and00
    #                                           |             |             |
    #                           and21         add11──and11  add01──and01    |
    #                             |┌───────────┘|┌───────────┘|             |
    #             and22         add12──and12  add02──and02    |             |
    #               |┌───────────┘|┌───────────┘|             |             |
    #             add13─────────add03           |             |             |
    #  ┌───────────┘|             |             |             |             |
    # p5            p4            p3            p2            p1            p0

    labels_half_add, _ = GATES['HALF_ADD']
    labels['HALF_ADD'] = {}

    labels['HALF_ADD']['add01'] = ('and01', 'and10', 'p1', 'carry01')
    labels['HALF_ADD']['add03'] = ('carry02', 'sum12', 'p3', 'carry03')
    labels['HALF_ADD']['add11'] = ('and11', 'and20', 'sum11', 'carry11')

    models.append(new_pmodel(pmodel_half_add, labels_half_add, labels['HALF_ADD']['add01']))
    models.append(new_pmodel(pmodel_half_add, labels_half_add, labels['HALF_ADD']['add03']))
    models.append(new_pmodel(pmodel_half_add, labels_half_add, labels['HALF_ADD']['add11']))

    labels_full_add, _ = GATES['FULL_ADD']
    labels['FULL_ADD'] = {}

    labels['FULL_ADD']['add02'] = ('and02', 'sum11', 'carry01', 'p2', 'carry02')
    labels['FULL_ADD']['add12'] = ('and12', 'and21', 'carry11', 'sum12', 'carry12')
    labels['FULL_ADD']['add13'] = ('carry03', 'and22', 'carry12', 'p4', 'p5')

    models.append(new_pmodel(pmodel_full_add, labels_full_add, labels['FULL_ADD']['add02']))
    models.append(new_pmodel(pmodel_full_add, labels_full_add, labels['FULL_ADD']['add12']))
    models.append(new_pmodel(pmodel_full_add, labels_full_add, labels['FULL_ADD']['add13']))

    ####################################################################################################
    # combine into one binary quadratic model
    ####################################################################################################

    bqm = stitch(models)
    # print("three-bit multiplier fault model")
    # print('h: {}'.format(bqm.linear))
    # print('J: {}\n'.format(bqm.quadratic))
    return (bqm, labels)


def half_adder(fault=True):
    ####################################################################################################
    # get basic gate fault models
    ####################################################################################################

    # print("XOR gate fault model")
    pmodel_xor = gate_model('XOR', fault)

    # print("AND gate fault model")
    pmodel_and = gate_model('AND', fault)

    ####################################################################################################
    # wire the whole thing up
    ####################################################################################################

    models = []
    labels = {}

    labels_xor, _ = GATES['XOR']
    labels['XOR'] = ('augend', 'addend', 'sum')
    models.append(new_pmodel(pmodel_xor, labels_xor, labels['XOR']))

    labels_and, _ = GATES['AND']
    labels['AND'] = ('augend', 'addend', 'carry_out')
    models.append(new_pmodel(pmodel_and, labels_and, labels['AND']))

    ####################################################################################################
    # combine into one binary quadratic model
    ####################################################################################################

    bqm = stitch(models)
    # print("half adder fault model")
    # print('h: {}'.format(bqm.linear))
    # print('J: {}\n'.format(bqm.quadratic))
    return (bqm, labels)


def full_adder(fault=True):
    ####################################################################################################
    # get basic gate fault models
    ####################################################################################################

    # print("half adder fault model")
    pmodel_half_add = gate_model('HALF_ADD', fault)

    # print("OR gate fault model")
    pmodel_or = gate_model('OR', fault)

    ####################################################################################################
    # wire the whole thing up
    ####################################################################################################

    models = []
    labels = {}

    labels_half_add, _ = GATES['HALF_ADD']
    labels['HALF_ADD'] = {}

    labels['HALF_ADD']['add1'] = ('augend', 'addend', 'sum1', 'carry_out1')
    labels['HALF_ADD']['add2'] = ('sum1','carry_in','sum','carry_out2')

    models.append(new_pmodel(pmodel_half_add, labels_half_add, labels['HALF_ADD']['add1']))
    models.append(new_pmodel(pmodel_half_add, labels_half_add, labels['HALF_ADD']['add2']))

    labels_or, _ = GATES['OR']
    labels['OR'] = {}
    labels['OR']['or'] = ('carry_out1', 'carry_out2', 'carry_out')
    models.append(new_pmodel(pmodel_or, labels_or, labels['OR']['or']))

    ####################################################################################################
    # combine into one binary quadratic model
    ####################################################################################################

    bqm = stitch(models)
    # print("full adder fault model")
    # print('h: {}'.format(bqm.linear))
    # print('J: {}\n'.format(bqm.quadratic))
    return (bqm, labels)
