from build123d import *
from ocp_vscode import *
import math

test_gear0 = {
    'name': 'TEST_GEAR',
    'numTeeth': 20,
    'module': 2.5,
    'pressureAngle' : 20.0,
    'thickness': 10.0,
    'boreDiameter': 5.0,
    'filletRadius': 0.5
}

test_gear = {
    'name': 'TEST_GEAR',
    'numTeeth': 20,
    'module': 2.5,
    'pressureAngle' : 20.0,
    'thickness': 10.0,
    'boreDiameter': 5.0,
    'filletRadius': 0.5
}


# Vale function apo edw kai katw ksrgw 
module = test_gear['module']
num_teeth = test_gear['numTeeth']
pressure_angle_rad = math.radians(test_gear['pressureAngle'])
thickness = test_gear['thickness']
bore_diameter = test_gear['boreDiameter']

# Calculate crucial data 
pitch_dia = num_teeth * module
base_dia = pitch_dia * math.cos(pressure_angle_rad)
addendum_dia = module * (num_teeth + 2)
dedendum_dia = module * (num_teeth - 2.5)

# Create the blank gear based on the addendum diameter
gear = Cylinder(addendum_dia / 2, height=thickness)

# calculate at which angle the involute should stop and 
# calculate at which angle the pitch diameter is 
phi_max = math.sqrt((addendum_dia / base_dia)**2 - 1)
phi_pitch = math.sqrt((pitch_dia / base_dia)**2 -1)

# Calculate the involute
num_points = 15
involute_points = []
for i in range(num_points):

    phi = (i / (num_points - 1)) * phi_max

    # Involute equations
    x = base_dia / 2 * (math.sin(phi) - phi * math.cos(phi))
    y = base_dia / 2 * (math.cos(phi)  + phi * math.sin(phi))

    involute_points.append((x, y))
involute = Spline(involute_points)

# Find intersection point of pitch circle and involute to calculate angular bias
involute_at_pitch = involute.intersect(Circle(pitch_dia / 2))[0].position_at(1)
d = math.sqrt(involute_at_pitch.X ** 2 + (involute_at_pitch.Y - pitch_dia/2) ** 2) / 2
theta_bias = 2 * math.asin(d / pitch_dia)

# Create rotated involute points for the other side
z_rotation_rad = theta_bias - math.pi / (2 * num_teeth)

# Rotate each point
involute_points_rotated = []
for x, y in involute_points:
    # Rotation matrix for 2D rotation
    x_rot = x * math.cos(z_rotation_rad) - y * math.sin(z_rotation_rad)
    y_rot = x * math.sin(z_rotation_rad) + y * math.cos(z_rotation_rad)
    involute_points_rotated.append((x_rot, y_rot))

involute_rotated = Spline(involute_points_rotated)
root_line = Line(involute_rotated @ 0, (-dedendum_dia/2 * math.sin(z_rotation_rad), dedendum_dia/2 * math.cos(z_rotation_rad)))

cut = Curve() + [root_line, involute_rotated]

rotation_plane = Plane.ZY
cut += mirror(cut, rotation_plane)

cut += RadiusArc(cut[0] @ 1, cut[1] @ 1, -dedendum_dia/2.0)
cut += RadiusArc(cut[0] @ 0, cut[1] @ 0, -addendum_dia/2.5)

tooth_profile_wire = Wire(cut.edges())
tooth_face = Face(tooth_profile_wire)
tooth_cutter = extrude(tooth_face, amount=thickness, both=True)

gear -= PolarLocations(radius=0, count=num_teeth) * tooth_cutter

# for debugging 
debug_circles = []
debug_circles.append(["addendum_circle", Circle(addendum_dia / 2)])
debug_circles.append(["pitch_circle", Circle(pitch_dia / 2)])
debug_circles.append(["base_circle", Circle(base_dia / 2)])
debug_circles.append(["dedendum_circle", Circle(dedendum_dia / 2)])
debug_sketch = [(name, Plane(gear.faces().sort_by().last) * circle) for name, circle in debug_circles]

# Show with names
#for name, sketch in debug_sketch:
#    show_object(sketch, name=name)
show_object(gear)
#show_object(involute_rotated)
show_object(cut)