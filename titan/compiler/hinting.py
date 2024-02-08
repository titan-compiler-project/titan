from __future__ import annotations

from typing import NamedTuple, TypedDict, List, Union


from compiler.node import NodeTypeContext, NodeModuleData, Node
from common.type import DataType, StorageType

class spirv_id_and_type_context(TypedDict):
    spirv_id: str
    type_context: NodeTypeContext

class spirv_id_and_node(TypedDict):
    id: str
    node: List[Node]

class module_name_and_data(TypedDict):
    name: str
    data: NodeModuleData

class symbol_and_type(TypedDict):
    symbol: str
    type: Union[int, float, bool, None]


class declared_types(TypedDict):
    type: DataType
    spirv_id: str
