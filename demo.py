from __future__ import division
import os

import dwave_structural_imbalance_demo as sbdemo


def diagramDateRange(gssn, graph_name, start, end, subarea_name=None):
    # Create directories
    directory_path = os.path.join('Results', graph_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Write .csv header line
    csv_name = 'Structural Imbalance.csv'
    csv_path = os.path.join(directory_path, 'Structural Imbalance.csv')
    csv = open(csv_path, 'w')
    csv.write('year,total groups,total edges,imbalanced edges,structural imbalance')
    if subarea_name is not None:
        csv.write(',%s groups,%s edges,%s imbalanced edges,%s structural imbalance' % tuple([subarea_name] * 4))
    csv.write('\n')

    for year in range(start, end):
        # Compute structural imbalance up to and including year
        nld_subrange = gssn.get_node_link_data(graph_name, year)
        nld_subrange_solved = gssn.solve_structural_imbalance(graph_name, year)

        # Write stats to .csv
        num_nodes = len(nld_subrange['nodes'])
        num_edges = len(nld_subrange['links'])
        num_imbalanced = sum([edge['frustrated'] for edge in nld_subrange_solved['links']])
        ratio = num_imbalanced / num_edges
        csv.write('%s,%s,%s,%s,%s' % (year, num_nodes, num_edges, num_imbalanced, ratio))
        if subarea_name is not None:
            nld_subarea = gssn.get_node_link_data(subarea_name, year)
            num_nodes = len([node for node in nld_subrange['nodes'] if node in nld_subarea['nodes']])
            event_ids = [edge['event_id'] for edge in nld_subrange['links'] if edge in nld_subarea['links']]
            num_edges = len(event_ids)
            num_imbalanced = len([edge['event_id'] for edge in nld_subrange_solved['links'] if edge['event_id'] in event_ids])
            if num_edges != 0:
                ratio = num_imbalanced / num_edges
            else:
                ratio = '-'
            csv.write(',%s,%s,%s,%s' % (num_nodes, num_edges, num_imbalanced, ratio))
        csv.write('\n')

        # Draw graph
        file_name = 'Structural Imbalance %s.png' % year
        file_path = os.path.join(directory_path, file_name)
        sbdemo.draw(file_path, nld_subrange_solved)
        print('Output %s\n' % file_path)

    print('Output %s' % csv_path)
    csv.close()


if __name__ == '__main__':
    # get the graphs
    gssn = sbdemo.GlobalSignedSocialNetwork()

    # draw Global graph before solving; save node layout for reuse
    nld_global = gssn.get_node_link_data()
    position = sbdemo.draw('global.png', nld_global)
    print('Output %s' % 'global.png')

    # calculate the imbalance of Global
    nld_global_solved = gssn.solve_structural_imbalance()

    # draw the Global graph; reusing the above layout, and calculating a new grouped layout
    sbdemo.draw('global_imbalance.png', nld_global_solved, position)
    print('Output %s' % 'global_imbalance.png')
    sbdemo.draw('global_imbalance_grouped', nld_global_solved)
    print('Output %s' % 'global_imbalance_grouped\n')

    # Images of the structural imbalance in the local Syrian SSN
    # for years 2010-2016 showing frustrated and unfrustrated edges.
    diagramDateRange(gssn, 'Syria', 2010, 2016 + 1)

    # Images of the structural imbalance in the world SSN for
    # years 2007-2016 showing frustrated and unfrustrated edges.
    diagramDateRange(gssn, 'Global', 2007, 2016 + 1, 'Syria')
