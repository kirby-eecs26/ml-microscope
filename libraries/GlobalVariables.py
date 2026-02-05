#temp global variable lib to keep track of what will be used repeatedly - danny

API_BASE = "http://microscope.local:5000/"
XY_STEPSIZE: int = 500
Z_STEPSIZE: int = 50
NEG_X_BOUND: int = -85000           #left
POS_X_BOUND: int = 85000            #right
POS_Y_BOUND: int = 85000            #up
NEG_Y_BOUND: int = -85000           #dowm
POS_Z_BOUND: int = -80000           #closer to slide
NEG_Z_BOUND: int = 70000            #farther from slide
#CENTER_POINT: int = "center point"
MAX_DURATION_SEC: float = 15.0