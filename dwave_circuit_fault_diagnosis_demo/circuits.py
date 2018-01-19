import sys

import dimod

from dwave_circuit_fault_diagnosis_demo.gates import *

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
def stitch(widgets):
    """
    Take a list of :class:`pm.PenaltyModel` widgets, and 'stitch' them together:
    The variable set of the new model is the additive union of the variable sets of the widgets,
    the relations set of the new model is the additive union of the relation sets of the widgets.

    That is, the new widget contains every variable and coupler that is in any widget,
    and the bias of a variable or relation is the sum of the biases in of the variable
    or relation in all widgets that contain it.

    Similarly, the offset is summed across all widgets.

    All constraints are converted to :class:`pm.Vartype.SPIN`.

    Args:
        widgets (list[pm.PenaltyModel]): A list of penalty models to be stiched together.

    Returns:
        :class:`dimod.BinaryQuadraticModel`: The resulting :class:`BinaryQuadraticModel`.

    """
    linear = {}
    quadratic = {}
    offset = 0
    for widget in widgets:
        for variable, bias in iteritems(widget.model.linear):
            linear[variable] = linear.get(variable, 0) + bias

        for relation, bias in iteritems(widget.model.quadratic):
            quadratic[relation] = quadratic.get(relation, 0) + bias

        offset += widget.model.offset

    return dimod.BinaryQuadraticModel(linear, quadratic, offset, dimod.SPIN)


def three_bit_multiplier():
    ####################################################################################################
    # get basic gate fault models
    ####################################################################################################

    print("AND gate fault model")
    pmodel_and = fault_model(AND)

    print("half adder fault model")
    pmodel_half_add = fault_model(HALF_ADD)

    print("full adder fault model")
    pmodel_full_add = fault_model(FULL_ADD)

    ####################################################################################################
    # wire the whole thing up
    ####################################################################################################

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

    and00 = pmodel_and.relabel_variables({0: 'a0', 1: 'b0', 2: 'p0', 3: 'aux1'}, copy=True)
    and01 = pmodel_and.relabel_variables({0: 'a0', 1: 'b1', 2: 'and01', 3: 'aux2'}, copy=True)
    and02 = pmodel_and.relabel_variables({0: 'a0', 1: 'b2', 2: 'and02', 3: 'aux3'}, copy=True)
    and10 = pmodel_and.relabel_variables({0: 'a1', 1: 'b0', 2: 'and10', 3: 'aux4'}, copy=True)
    and11 = pmodel_and.relabel_variables({0: 'a1', 1: 'b1', 2: 'and11', 3: 'aux5'}, copy=True)
    and12 = pmodel_and.relabel_variables({0: 'a1', 1: 'b2', 2: 'and12', 3: 'aux6'}, copy=True)
    and20 = pmodel_and.relabel_variables({0: 'a2', 1: 'b0', 2: 'and20', 3: 'aux7'}, copy=True)
    and21 = pmodel_and.relabel_variables({0: 'a2', 1: 'b1', 2: 'and21', 3: 'aux8'}, copy=True)
    and22 = pmodel_and.relabel_variables({0: 'a2', 1: 'b2', 2: 'and22', 3: 'aux9'}, copy=True)

    #                                         and20         and10         and00
    #                                           |             |             |
    #                           and21         add11──and11  add01──and01    |
    #                             |┌───────────┘|┌───────────┘|             |
    #             and22         add12──and12  add02──and02    |             |
    #               |┌───────────┘|┌───────────┘|             |             |
    #             add13─────────add03           |             |             |
    #  ┌───────────┘|             |             |             |             |
    # p5            p4            p3            p2            p1            p0

    add01 = pmodel_half_add.relabel_variables({0: 'and01', 1: 'and10', 2: 'p1', 3: 'carry01', 4: 'aux10'}, copy=True)
    add02 = pmodel_full_add.relabel_variables(
        {0: 'and02', 1: 'sum11', 2: 'carry01', 3: 'p2', 4: 'carry02', 5: 'aux11'}, copy=True)
    add03 = pmodel_half_add.relabel_variables({0: 'carry02', 1: 'sum12', 2: 'p3', 3: 'carry03', 4: 'aux12'}, copy=True)
    add11 = pmodel_half_add.relabel_variables({0: 'and11', 1: 'and20', 2: 'sum11', 3: 'carry11', 4: 'aux13'}, copy=True)
    add12 = pmodel_full_add.relabel_variables(
        {0: 'and12', 1: 'and21', 2: 'carry11', 3: 'sum12', 4: 'carry12', 5: 'aux14'}, copy=True)
    add13 = pmodel_full_add.relabel_variables(
        {0: 'carry03', 1: 'and22', 2: 'carry12', 3: 'p4', 4: 'p5', 5: 'aux15'}, copy=True)

    ####################################################################################################
    # combine into one binary quadratic model
    ####################################################################################################

    bqm = stitch([and00, and01, and02, and10, and11, and12, and20,
                  and21, and22, add01, add02, add03, add11, add12, add13])
    return bqm
