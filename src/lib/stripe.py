import bpy
from dataclasses import dataclass
from . import node_group as node_group_lib, float as float_lib

if "_LOADED" in locals():
    import importlib

    for mod in (node_group_lib, float_lib,):
        importlib.reload(mod)
_LOADED = True

# Use reverse paint order, because that is more intuitive when editing
_PAINT_ORDER = -1


@dataclass
class Stripe:
    rgba: tuple[float, float, float, float]
    center: float
    width: float


@dataclass
class StripeSet:
    background_rgba: tuple[float, float, float, float]
    stripes: list[Stripe]


@dataclass
class ColorStop:
    rgba: tuple[float, float, float, float]
    position: float


def add_stop(stops: list[ColorStop], position: float, rgba: tuple[float, float, float, float],
             overwrite: bool = False) -> list[ColorStop]:

    print("Add stop", position, [c for c in rgba])

    existing_index = next((index for index, stop in enumerate(stops) if float_lib.equal(stop.position, position)), None)
    if existing_index is not None and not overwrite:
        print("Add stop fail")
        return stops
    if existing_index is not None:
        print("Replace stop", existing_index)
        stops[existing_index] = ColorStop(position=position, rgba=rgba)
        return stops

    print("Add add stop", position, [c for c in rgba])
    new_index = next((index for index, stop in enumerate(stops) if float_lib.gte(stop.position, position)), len(stops))
    stops.insert(new_index, ColorStop(position=position, rgba=rgba))
    return stops


def get_color_at(stops: list[ColorStop], position: float) -> tuple[float, float, float, float]:
    last_stop_before = next((s for s in stops[::-1] if s.position < position or float_lib.equal(s.position, position)),
                            None)
    return last_stop_before.rgba if last_stop_before else (0, 0, 0, 1)


def stripe_set_to_stops(stripe_set: StripeSet) -> list[ColorStop]:
    stops: list[ColorStop] = [
        ColorStop(position=0, rgba=stripe_set.background_rgba)
    ]

    print("Stops to start", stops)

    filtered_stripes = [s for s in stripe_set.stripes if not float_lib.equal(s.width, 0)]

    for stripe in filtered_stripes[::_PAINT_ORDER]:
        start = max(0.0, stripe.center - stripe.width / 2)
        end = min(1.0, stripe.center + stripe.width / 2)

        # Stop is between start and end
        overpainted_stops = [s for s in stops if float_lib.gte(s.position, start) and float_lib.lte(s.position, end)]

        if overpainted_stops:
            # Remove overpainted stops and add end
            stops = [s for s in stops if s not in overpainted_stops]
            print("Stops after remove", [s for s in stops])
            add_stop(stops, end, overpainted_stops[-1].rgba, True)
        elif not float_lib.gte(end, 1):
            print("Normal add stop", end)
            add_stop(stops, end, get_color_at(stops, end))

        # Add starting stop
        stops = add_stop(stops, start, stripe.rgba, True)

    return stops


def verify_color_ramp(node: bpy.types.ShaderNodeValToRGB, stops: list[ColorStop]) -> bool:
    sorted_stops = sorted(stops, key=lambda s: s.position)
    sorted_elements = sorted([e for e in node.color_ramp.elements], key=lambda s: s.position)
    for index, stop in enumerate(sorted_stops):
        element = sorted_elements[index]
        element_color = tuple(c for c in element.color)
        if element_color != stop.rgba or not float_lib.equal(element.position, stop.position):
            return False
    return True


def update_color_ramp(node: bpy.types.ShaderNodeValToRGB):
    elements = node.color_ramp.elements
    stripe_set = get_stripes(node)

    if not stripe_set:
        raise Exception("No plaidiator data")

    stops = stripe_set_to_stops(get_stripes(node))

    # Since we can't delete all stops, the cleanest way is to just ensure the number of stops we need in one pass,
    # then set those stops' positions and colors in a second pass.
    while len(elements) > 1:
        elements.remove(elements[0])

    for stop in stops[1:]:
        elements.new(stop.position)

    for index, stop in enumerate(stops):
        elements[index].position = stop.position
        elements[index].color = stop.rgba

    if len(stops) > 1:
        for stop in stops[1:]:
            new_elem = elements.new(stop.position)
            new_elem.color = stop.rgba


def set_stripes(node: bpy.types.ShaderNodeValToRGB, stripe_set: StripeSet) -> None:
    node.plaidiator_component.background_rgba = stripe_set.background_rgba
    for stripe in stripe_set.stripes:
        node_stripe = node.plaidiator_component.stripes.new()
        node_stripe.rgba = stripe.rgba
        node_stripe.center = stripe.center
        node_stripe.width = stripe.width


def get_stripes(node: bpy.types.ShaderNodeValToRGB) -> StripeSet | None:
    if not node.plaidiator_component:
        return None
    return StripeSet(
        background_rgba=node.plaidiator_component.background_rgba,
        stripes=[Stripe(rgba=stripe.rgba, center=stripe.center, width=stripe.width) for stripe in
                 node.plaidiator_component.stripes]
    )
