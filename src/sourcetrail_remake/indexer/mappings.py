"""Mapping helpers between Python analysis output and Sourcetrail enums."""

from __future__ import annotations

from sourcetrail_remake.core.types import EdgeType, NodeType, ParsedSymbol

JEDI_TYPE_TO_NODE_TYPE: dict[str, NodeType] = {
    "class": NodeType.NODE_CLASS,
    "function": NodeType.NODE_FUNCTION,
    "instance": NodeType.NODE_GLOBAL_VARIABLE,
    "module": NodeType.NODE_MODULE,
    "namespace": NodeType.NODE_NAMESPACE,
    "param": NodeType.NODE_GLOBAL_VARIABLE,
    "path": NodeType.NODE_FILE,
    "property": NodeType.NODE_FIELD,
    "statement": NodeType.NODE_GLOBAL_VARIABLE,
}


def map_name_type(name_type: str, *, parent: ParsedSymbol | None = None, is_builtin: bool = False) -> NodeType:
    """Map Jedi's name types onto Sourcetrail-compatible node types."""
    if is_builtin:
        return NodeType.NODE_BUILTIN_TYPE
    if name_type == "function" and parent is not None and parent.node_type == NodeType.NODE_CLASS:
        return NodeType.NODE_METHOD
    if name_type == "statement" and parent is not None and parent.node_type == NodeType.NODE_CLASS:
        return NodeType.NODE_FIELD
    return JEDI_TYPE_TO_NODE_TYPE.get(name_type, NodeType.NODE_SYMBOL)


def classify_edge_type(line_text: str, *, column: int, name: str) -> EdgeType:
    """Infer a Sourcetrail edge type from a textual reference context."""
    start = max(column, 0)
    end = start + len(name)
    stripped = line_text.lstrip()
    before = line_text[:start].rstrip()
    after = line_text[end:].lstrip()
    if stripped.startswith("import ") or stripped.startswith("from "):
        return EdgeType.EDGE_IMPORT
    if after.startswith("("):
        return EdgeType.EDGE_CALL
    if before.endswith("."):
        return EdgeType.EDGE_MEMBER
    return EdgeType.EDGE_USAGE
