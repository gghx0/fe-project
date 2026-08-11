TERMS = [
    {"name": "x",          "identity": "X",  "swap": "y"},
    {"name": "f(x)",       "identity": "X",  "swap": "f(y)"},
    {"name": "y",          "identity": "Y",  "swap": "x"},
    {"name": "f(y)",       "identity": "Y",  "swap": "f(x)"},

    {"name": "x^2",        "identity": "X2", "swap": "y^2"},
    {"name": "xf(x)",      "identity": "X2", "swap": "yf(y)"},
    {"name": "f(x^2)",     "identity": "X2", "swap": "f(y^2)"},

    {"name": "y^2",        "identity": "Y2", "swap": "x^2"},
    {"name": "yf(y)",      "identity": "Y2", "swap": "xf(x)"},
    {"name": "f(y^2)",     "identity": "Y2", "swap": "f(x^2)"},

    {"name": "xf(y)",      "identity": "XY", "swap": "yf(x)"},
    {"name": "yf(x)",      "identity": "XY", "swap": "xf(y)"},
    {"name": "f(x)f(y)",   "identity": "XY", "swap": "f(x)f(y)"},
    {"name": "xy",         "identity": "XY", "swap": "xy"},
]

TERM_ORDER = [term["name"] for term in TERMS]

TERM_BY_NAME = {
    term["name"]: term
    for term in TERMS
}

assert len(TERMS) == 14
assert len(set(TERM_ORDER)) == 14

for term in TERMS:
    swapped = TERM_BY_NAME[term["swap"]]
    assert swapped["swap"] == term["name"]

from itertools import combinations_with_replacement

def term_index(name):
    return TERM_ORDER.index(name)


def canonical_sum(a, b):
    if term_index(a) <= term_index(b):
        return (a, b)
    return (b, a)


def identity_signature(a, b):
    class_a = TERM_BY_NAME[a]["identity"]
    class_b = TERM_BY_NAME[b]["identity"]

    class_order = ["X", "Y", "X2", "Y2", "XY"]

    if class_order.index(class_a) <= class_order.index(class_b):
        return (class_a, class_b)
    return (class_b, class_a)


SUMS = []

for a, b in combinations_with_replacement(TERM_ORDER, 2):
    pair = canonical_sum(a, b)

    SUMS.append({
        "terms": pair,
        "signature": identity_signature(*pair),
    })


from collections import defaultdict

SUMS_BY_SIGNATURE = defaultdict(list)

for item in SUMS:
    SUMS_BY_SIGNATURE[item["signature"]].append(item["terms"])

print("\nSum counts by identity signature:")

for signature, sums in SUMS_BY_SIGNATURE.items():
    print(signature, len(sums))

LITERAL_EQUATIONS = []

for signature, sums in SUMS_BY_SIGNATURE.items():
    for left in sums:
        for right in sums:
            LITERAL_EQUATIONS.append({
                "left": left,
                "right": right,
            })

assert len(SUMS) == 105
assert len(SUMS_BY_SIGNATURE) == 15
assert len(LITERAL_EQUATIONS) == 847

def equation_key(equation):
    return (
        equation["left"][0],
        equation["left"][1],
        equation["right"][0],
        equation["right"][1],
    )

EQUATION_KEYS = [
    equation_key(equation)
    for equation in LITERAL_EQUATIONS
]

UNIQUE_EQUATION_KEYS = set(EQUATION_KEYS)

assert len(EQUATION_KEYS) == 847
assert len(UNIQUE_EQUATION_KEYS) == 847

def display_sum(pair):
    return pair[0] + " + " + pair[1]


def display_equation(equation):
    left = display_sum(equation["left"])
    right = display_sum(equation["right"])

    return "f(" + left + ") = " + right

for equation in LITERAL_EQUATIONS:
    left_signature = identity_signature(*equation["left"])
    right_signature = identity_signature(*equation["right"])

    assert left_signature == right_signature

def swap_sum(pair):
    a, b = pair

    swapped_a = TERM_BY_NAME[a]["swap"]
    swapped_b = TERM_BY_NAME[b]["swap"]

    return canonical_sum(swapped_a, swapped_b)


def swap_equation(equation):
    return {
        "left": swap_sum(equation["left"]),
        "right": swap_sum(equation["right"]),
    }

for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)
    swapped_twice = swap_equation(swapped)

    assert equation_key(swapped_twice) == equation_key(equation)

EQUATION_BY_KEY = {
    equation_key(equation): equation
    for equation in LITERAL_EQUATIONS
}

for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)
    swapped_key = equation_key(swapped)

    assert swapped_key in EQUATION_BY_KEY

def equation_sort_key(equation):
    return tuple(
        term_index(term)
        for term in equation_key(equation)
    )

FE_GROUPS = {}

for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)

    original_key = equation_sort_key(equation)
    swapped_key = equation_sort_key(swapped)

    if original_key <= swapped_key:
        representative = equation
    else:
        representative = swapped

    representative_key = equation_key(representative)

    FE_GROUPS.setdefault(representative_key, set())

    FE_GROUPS[representative_key].add(
        equation_key(equation)
    )

number_of_groups = len(FE_GROUPS)

single_groups = sum(
    1 for group in FE_GROUPS.values()
    if len(group) == 1
)

double_groups = sum(
    1 for group in FE_GROUPS.values()
    if len(group) == 2
)


assert number_of_groups == 438
assert single_groups == 29
assert double_groups == 409

assert single_groups + 2 * double_groups == 847

SORTED_GROUPS = sorted(
    FE_GROUPS.items(),
    key=lambda item: equation_sort_key(EQUATION_BY_KEY[item[0]])
)

FE_RECORDS = []

for index, (representative_key, group) in enumerate(SORTED_GROUPS, start=1):
    fe_id = f"FE-{index:04d}"

    group_keys = sorted(
        group,
        key=lambda key: equation_sort_key(EQUATION_BY_KEY[key])
    )

    equations = []

    for key in group_keys:
        equation = EQUATION_BY_KEY[key]

        equations.append({
            "left": list(equation["left"]),
            "right": list(equation["right"]),
            "display": display_equation(equation),
        })

    FE_RECORDS.append({
        "id": fe_id,
        "self_symmetric": len(equations) == 1,
        "equations": equations,
    })

assert len(FE_RECORDS) == 438
assert FE_RECORDS[0]["id"] == "FE-0001"
assert FE_RECORDS[-1]["id"] == "FE-0438"

import json
import os

os.makedirs("data", exist_ok=True)

with open("data/fe_database.json", "w", encoding="utf-8") as file:
    json.dump(
        FE_RECORDS,
        file,
        indent=2,
        ensure_ascii=False
    )

print("Exported database to data/fe_database.json")

assert len({fe["id"] for fe in FE_RECORDS}) == 438

literal_count = sum(
    len(fe["equations"])
    for fe in FE_RECORDS
)

self_symmetric_count = sum(
    fe["self_symmetric"]
    for fe in FE_RECORDS
)

paired_count = sum(
    not fe["self_symmetric"]
    for fe in FE_RECORDS
)

assert literal_count == 847
assert self_symmetric_count == 29
assert paired_count == 409

with open("data/fe_index.txt", "w", encoding="utf-8") as file:
    for fe in FE_RECORDS:
        file.write(fe["id"] + "\n")

        for equation in fe["equations"]:
            file.write("  " + equation["display"] + "\n")

        file.write("\n")


for fe in FE_RECORDS:
    equations = fe["equations"]

    if len(equations) == 1:
        equation = {
            "left": tuple(equations[0]["left"]),
            "right": tuple(equations[0]["right"]),
        }

        assert equation_key(swap_equation(equation)) == equation_key(equation)

    elif len(equations) == 2:
        first = {
            "left": tuple(equations[0]["left"]),
            "right": tuple(equations[0]["right"]),
        }

        second = {
            "left": tuple(equations[1]["left"]),
            "right": tuple(equations[1]["right"]),
        }

        assert equation_key(swap_equation(first)) == equation_key(second)
        assert equation_key(swap_equation(second)) == equation_key(first)

    else:
        raise AssertionError(
            fe["id"] + " has an invalid number of equations."
        )

all_keys_in_groups = []

for fe in FE_RECORDS:
    for item in fe["equations"]:
        equation = {
            "left": tuple(item["left"]),
            "right": tuple(item["right"]),
        }

        all_keys_in_groups.append(equation_key(equation))

assert len(all_keys_in_groups) == 847
assert len(set(all_keys_in_groups)) == 847
assert set(all_keys_in_groups) == set(EQUATION_KEYS)
