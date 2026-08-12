from itertools import combinations_with_replacement
from collections import defaultdict
import json
import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")


# ============================================================
# 1. Allowed terms
# ============================================================

TERMS = [
    {"name": "x",          "identity": "X",  "swap": "y"},
    {"name": "f(x)",       "identity": "X",  "swap": "f(y)"},
    {"name": "y",          "identity": "Y",  "swap": "x"},
    {"name": "f(y)",       "identity": "Y",  "swap": "f(x)"},

    {"name": "x^2",        "identity": "X2", "swap": "y^2"},
    {"name": "xf(x)",      "identity": "X2", "swap": "yf(y)"},
    {"name": "f(x)^2",     "identity": "X2", "swap": "f(y)^2"},
    {"name": "f(x^2)",     "identity": "X2", "swap": "f(y^2)"},

    {"name": "y^2",        "identity": "Y2", "swap": "x^2"},
    {"name": "yf(y)",      "identity": "Y2", "swap": "xf(x)"},
    {"name": "f(y)^2",     "identity": "Y2", "swap": "f(x)^2"},
    {"name": "f(y^2)",     "identity": "Y2", "swap": "f(x^2)"},

    {"name": "xf(y)",      "identity": "XY", "swap": "yf(x)"},
    {"name": "yf(x)",      "identity": "XY", "swap": "xf(y)"},
    {"name": "f(x)f(y)",   "identity": "XY", "swap": "f(x)f(y)"},
    {"name": "xy",         "identity": "XY", "swap": "xy"},
    {"name": "f(xy)",      "identity": "XY", "swap": "f(xy)"},
]


TERM_ORDER = [
    term["name"]
    for term in TERMS
]


TERM_BY_NAME = {
    term["name"]: term
    for term in TERMS
}


assert len(TERMS) == 17
assert len(set(TERM_ORDER)) == 17


# Check that x <-> y swapping is an involution.
for term in TERMS:
    swapped = TERM_BY_NAME[term["swap"]]
    assert swapped["swap"] == term["name"]


# ============================================================
# 2. Canonical sums
# ============================================================

def term_index(name):
    return TERM_ORDER.index(name)


def canonical_sum(a, b):
    if term_index(a) <= term_index(b):
        return (a, b)

    return (b, a)


def identity_signature(a, b):
    class_a = TERM_BY_NAME[a]["identity"]
    class_b = TERM_BY_NAME[b]["identity"]

    class_order = [
        "X",
        "Y",
        "X2",
        "Y2",
        "XY",
    ]

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


SUMS_BY_SIGNATURE = defaultdict(list)

for item in SUMS:
    SUMS_BY_SIGNATURE[
        item["signature"]
    ].append(item["terms"])


print("\nSum counts by identity signature:")

for signature, sums in SUMS_BY_SIGNATURE.items():
    print(signature, len(sums))


# ============================================================
# 3. Generate all literal equations
# ============================================================

ALL_LITERAL_EQUATIONS = []

for signature, sums in SUMS_BY_SIGNATURE.items():
    for left in sums:
        for right in sums:
            ALL_LITERAL_EQUATIONS.append({
                "left": left,
                "right": right,
            })


# ============================================================
# 4. Require both x and y to occur
# ============================================================

def variables_in_term(term):
    variables = set()

    if "x" in term:
        variables.add("x")

    if "y" in term:
        variables.add("y")

    return variables


def contains_both_variables(equation):
    variables = set()

    for term in equation["left"] + equation["right"]:
        variables.update(
            variables_in_term(term)
        )

    return variables == {"x", "y"}


LITERAL_EQUATIONS = [
    equation
    for equation in ALL_LITERAL_EQUATIONS
    if contains_both_variables(equation)
]


# Counts after adding f(xy).
assert len(SUMS) == 153
assert len(SUMS_BY_SIGNATURE) == 15
assert len(ALL_LITERAL_EQUATIONS) == 1971
assert len(LITERAL_EQUATIONS) == 1625

assert (
    len(ALL_LITERAL_EQUATIONS)
    - len(LITERAL_EQUATIONS)
    == 346
)


# ============================================================
# 5. Equation keys and uniqueness
# ============================================================

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


UNIQUE_EQUATION_KEYS = set(
    EQUATION_KEYS
)


assert len(EQUATION_KEYS) == 1625
assert len(UNIQUE_EQUATION_KEYS) == 1625


# ============================================================
# 6. Display
# ============================================================

def display_sum(pair):
    return (
        pair[0]
        + " + "
        + pair[1]
    )


def display_equation(equation):
    left = display_sum(
        equation["left"]
    )

    right = display_sum(
        equation["right"]
    )

    return (
        "f("
        + left
        + ") = "
        + right
    )


# ============================================================
# 7. Verify identity-solution condition
# ============================================================

for equation in LITERAL_EQUATIONS:
    left_signature = identity_signature(
        *equation["left"]
    )

    right_signature = identity_signature(
        *equation["right"]
    )

    assert left_signature == right_signature


# ============================================================
# 8. x <-> y symmetry
# ============================================================

def swap_sum(pair):
    a, b = pair

    swapped_a = TERM_BY_NAME[a]["swap"]
    swapped_b = TERM_BY_NAME[b]["swap"]

    return canonical_sum(
        swapped_a,
        swapped_b,
    )


def swap_equation(equation):
    return {
        "left": swap_sum(
            equation["left"]
        ),
        "right": swap_sum(
            equation["right"]
        ),
    }


# Swapping twice must return the same equation.
for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)

    swapped_twice = swap_equation(
        swapped
    )

    assert (
        equation_key(swapped_twice)
        == equation_key(equation)
    )


EQUATION_BY_KEY = {
    equation_key(equation): equation
    for equation in LITERAL_EQUATIONS
}


# Every x/y-swapped equation must remain in the universe.
for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)

    swapped_key = equation_key(
        swapped
    )

    assert swapped_key in EQUATION_BY_KEY


# ============================================================
# 9. Group equations under x <-> y symmetry
# ============================================================

def equation_sort_key(equation):
    return tuple(
        term_index(term)
        for term in equation_key(equation)
    )


FE_GROUPS = {}

for equation in LITERAL_EQUATIONS:
    swapped = swap_equation(equation)

    original_key = equation_sort_key(
        equation
    )

    swapped_sort_key = equation_sort_key(
        swapped
    )

    if original_key <= swapped_sort_key:
        representative = equation
    else:
        representative = swapped

    representative_key = equation_key(
        representative
    )

    FE_GROUPS.setdefault(
        representative_key,
        set(),
    )

    FE_GROUPS[
        representative_key
    ].add(
        equation_key(equation)
    )


number_of_groups = len(
    FE_GROUPS
)


single_groups = sum(
    1
    for group in FE_GROUPS.values()
    if len(group) == 1
)


double_groups = sum(
    1
    for group in FE_GROUPS.values()
    if len(group) == 2
)


assert number_of_groups == 847
assert single_groups == 69
assert double_groups == 778

assert (
    single_groups
    + 2 * double_groups
    == 1625
)


# ============================================================
# 10. Deterministic ordering
# ============================================================

SORTED_GROUPS = sorted(
    FE_GROUPS.items(),
    key=lambda item:
        equation_sort_key(
            EQUATION_BY_KEY[item[0]]
        )
)


# ============================================================
# 11. Assign FE IDs
# ============================================================

FE_RECORDS = []

for index, (
    representative_key,
    group,
) in enumerate(
    SORTED_GROUPS,
    start=1,
):
    fe_id = f"FE-{index:04d}"

    group_keys = sorted(
        group,
        key=lambda key:
            equation_sort_key(
                EQUATION_BY_KEY[key]
            )
    )

    equations = []

    for key in group_keys:
        equation = EQUATION_BY_KEY[
            key
        ]

        equations.append({
            "left": list(
                equation["left"]
            ),

            "right": list(
                equation["right"]
            ),

            "display": display_equation(
                equation
            ),
        })

    FE_RECORDS.append({
        "id": fe_id,

        "self_symmetric":
            len(equations) == 1,

        "equations":
            equations,
    })


assert len(FE_RECORDS) == 847

assert FE_RECORDS[0]["id"] == "FE-0001"

assert FE_RECORDS[-1]["id"] == "FE-0847"


# ============================================================
# 12. Export JSON database
# ============================================================

os.makedirs(
    DATA_DIR,
    exist_ok=True,
)


with open(
    os.path.join(
        DATA_DIR,
        "fe_database.json",
    ),
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        FE_RECORDS,
        file,
        indent=2,
        ensure_ascii=False,
    )


print(
    "\nExported database to "
    "data/fe_database.json"
)


# ============================================================
# 13. Database verification
# ============================================================

assert len(
    {
        fe["id"]
        for fe in FE_RECORDS
    }
) == 847


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


assert literal_count == 1625
assert self_symmetric_count == 69
assert paired_count == 778


# ============================================================
# 14. Human-readable index
# ============================================================

with open(
    os.path.join(
        DATA_DIR,
        "fe_index.txt",
    ),
    "w",
    encoding="utf-8",
) as file:

    for fe in FE_RECORDS:
        file.write(
            fe["id"] + "\n"
        )

        for equation in fe["equations"]:
            file.write(
                "  "
                + equation["display"]
                + "\n"
            )

        file.write("\n")


# ============================================================
# 15. Verify every FE symmetry group
# ============================================================

for fe in FE_RECORDS:
    equations = fe["equations"]

    if len(equations) == 1:

        equation = {
            "left": tuple(
                equations[0]["left"]
            ),

            "right": tuple(
                equations[0]["right"]
            ),
        }

        assert (
            equation_key(
                swap_equation(
                    equation
                )
            )
            ==
            equation_key(
                equation
            )
        )

    elif len(equations) == 2:

        first = {
            "left": tuple(
                equations[0]["left"]
            ),

            "right": tuple(
                equations[0]["right"]
            ),
        }

        second = {
            "left": tuple(
                equations[1]["left"]
            ),

            "right": tuple(
                equations[1]["right"]
            ),
        }

        assert (
            equation_key(
                swap_equation(
                    first
                )
            )
            ==
            equation_key(
                second
            )
        )

        assert (
            equation_key(
                swap_equation(
                    second
                )
            )
            ==
            equation_key(
                first
            )
        )

    else:
        raise AssertionError(
            fe["id"]
            + " has an invalid number "
            + "of equations."
        )


# ============================================================
# 16. Verify all literal equations appear exactly once
# ============================================================

all_keys_in_groups = []

for fe in FE_RECORDS:
    for item in fe["equations"]:

        equation = {
            "left": tuple(
                item["left"]
            ),

            "right": tuple(
                item["right"]
            ),
        }

        all_keys_in_groups.append(
            equation_key(
                equation
            )
        )


assert len(
    all_keys_in_groups
) == 1625


assert len(
    set(
        all_keys_in_groups
    )
) == 1625


assert (
    set(
        all_keys_in_groups
    )
    ==
    set(
        EQUATION_KEYS
    )
)


# ============================================================
# 17. Summary
# ============================================================

print("\nDatabase summary:")

print(
    "Allowed terms:",
    len(TERMS),
)

print(
    "Canonical sums:",
    len(SUMS),
)

print(
    "All literal equations:",
    len(ALL_LITERAL_EQUATIONS),
)

print(
    "Both-variable literal equations:",
    len(LITERAL_EQUATIONS),
)

print(
    "FE classes:",
    len(FE_RECORDS),
)

print(
    "Self-symmetric FE classes:",
    self_symmetric_count,
)

print(
    "Paired FE classes:",
    paired_count,
)