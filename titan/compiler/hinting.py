from __future__ import annotations

from typing import NamedTuple, TypedDict, List, Union

import dataflow
from compiler.node import NodeTypeContext, NodeModuleData
# from compiler.spirv import SPIRVAssembler
from common.type import DataType, StorageType

class spirv_id_and_type_context(TypedDict):
    spirv_id: str
    type_context: NodeTypeContext

class spirv_id_and_node(TypedDict):
    id: str
    node: List[dataflow.Node]

class module_name_and_data(TypedDict):
    name: str
    data: NodeModuleData

class symbol_and_type(TypedDict):
    symbol: str
    type: Union[int, float, bool, None]

# class constant_context_and_id(TypedDict):
#     type: SPIRVAssembler.ConstContext
#     spirv_id: str

class declared_types(TypedDict):
    type: DataType
    spirv_id: str

# class symbol_info(TypedDict):
#     symbol_id: str
#     info: SPIRVAssembler.SymbolInfo

class intermediate_id_type(TypedDict):
    intermediate_id: str
    type: DataType