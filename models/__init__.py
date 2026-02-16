from .db import db

# 1. NIVEL BASE: Modelos que no dependen de casi nadie (o solo de sí mismos)
from .User import User
from .Location import Location

# 2. NIVEL INTERMEDIO: Dependen de User o Location
from .Cruise import Cruise
from .Flight import Flight
from .BusTrain import BusTrain
from .CarRenting import CarRenting
from .CulinaryExperience import CulinaryExperience
from .Tour import Tour
from .Accommodation import Accommodation

# 3. NIVEL CRUCEROS (Jerarquía específica):
# CruiseRoute depende de Cruise y Location
from .CruiseRoute import CruiseRoute 
# CruiseStops depende de CruiseRoute y Location
from .CruiseStops import CruiseStops
# CruiseSegment depende de CruiseRoute y CruiseStops
from .CruiseSegment import CruiseSegment

# 4. NIVEL ALOJAMIENTO:
# Room depende de Accommodation
from .Room import Room
# AccommodationBookingLine depende de Room/Accommodation y User
from .AccommodationBookingLine import AccommodationBookingLine

# 5. NIVEL TRANSACCIONAL Y SOCIAL: Dependen de casi todos los anteriores
from .Review import Review
from .Trip import Trip