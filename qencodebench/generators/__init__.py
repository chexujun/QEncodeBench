"""Task generator registry."""

from qencodebench.generators.f1_sat import SatGenerator
from qencodebench.generators.f2_coloring import ColoringGenerator
from qencodebench.generators.f3_vertex_cover import VertexCoverGenerator
from qencodebench.generators.f4_subset_sum import SubsetSumGenerator
from qencodebench.generators.f5_latin_square import LatinSquareGenerator
from qencodebench.generators.f6_string_match import StringMatchGenerator
from qencodebench.generators.f7_sat_card import SatCardGenerator

GENERATORS = {
    g.family: g for g in (
        SatGenerator, ColoringGenerator, VertexCoverGenerator,
        SubsetSumGenerator, LatinSquareGenerator, StringMatchGenerator,
        SatCardGenerator,
    )
}


def get_generator(family: str):
    return GENERATORS[family]()
