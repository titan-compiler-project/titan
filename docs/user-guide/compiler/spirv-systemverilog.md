The compiled SPIR-V assembly from the previous stage is passed directly to this stage, without reading or writing to an external file first. To prase the SPIR-V assembly, the compiler makes use of PyParsing. Grammar is defined in ``titan.grammar.TitanSPIRVGrammar``.

SPIR-V is returned as a PyParsing object, where each line is then indexed to create a node graph, before generating the SystemVerilog. The graph step is necessary in order to coordinate everything into the correct tick.

Within ``titan.generate.generate_verilog`` the parsed SPIR-V is handled, and the nodes are constructed using the classes within ``titan.dataflow``.

## Anatomy of the Node

The Node (found in ``titan.dataflow``) is a class that contains information about the node itself, and left/right inputs. These inputs help to link the node with other operations, and will allow us to traverse the node tree once all of the SPIR-V is processed.

The node accepts the ``NodeContext`` class upon construction, and this sets up all the relevant information. The tick of the node is automatically calculated by evaluating the ticks of the left and right input node, if present. If not, it is set to 0.