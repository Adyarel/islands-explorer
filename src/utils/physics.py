import math
from typing import Tuple


class Force:

    def __init__(self, x_force: float, y_force: float):
        self.x: float = x_force
        self.y: float = y_force

    def __add__(self, other):
        """somme de deux forces, si type différents: erreur"""
        if type(other) is not Force:
            raise TypeError("unsupported operand type(s) for +: " + str(type(self)) + " and " + str(type(other)))
        return Force(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        """multiplication d'une force par un scalaire"""
        if (type(other) is not int) and (type(other) is not float):
            raise TypeError("unsupported operand type(s) for +: " + str(type(self)) + " and " + str(type(other)))
        return Force(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __str__(self) -> str:
        return str(self.__class__) + ": \n" \
               + "\tx= " + str(self.x) + "\n" \
               + "\ty= " + str(self.y)


class Acceleration:

    def __init__(self, x_acc: float, y_acc: float):
        self.x: float = x_acc
        self.y: float = y_acc

    def __str__(self) -> str:
        return str(self.__class__) + ": \n" \
               + "\tx= " + str(self.x) + "\n" \
               + "\ty= " + str(self.y)


class Speed:

    def __init__(self, x_speed: float, y_speed: float):
        self.x: float = x_speed
        self.y: float = y_speed

    def get_norm(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def get_orientation(self) -> float | None:
        norm = self.get_norm()
        if not norm == 0:
            if self.x >= 0:
                return math.asin(self.y / norm)
            else:
                if self.y >= 0:
                    return math.acos(self.x / norm)
                else:
                    return - math.acos(self.x / norm)
        else:
            return None

    def __mul__(self, other):
        """multiplication de la vitesse par un scalaire"""
        if (type(other) is not int) and (type(other) is not float):
            raise TypeError("unsupported operand type(s) for +: " + str(type(self)) + " and " + str(type(other)))
        return Speed(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __str__(self) -> str:
        return str(self.__class__) + ": \n" \
               + "\tx= " + str(self.x) + "\n" \
               + "\ty= " + str(self.y)


class Pos:

    def __init__(self, x_pos, y_pos):
        self.x = x_pos
        self.y = y_pos

    def __str__(self) -> str:
        return "x= " + str(self.x) + "\ty= " + str(self.y)

    def get_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def __add__(self, other):
        if not isinstance(other, Pos):
            raise TypeError(str(other) + " must be the same type as " + str(self.__class__))
        return Pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Pos):
            raise TypeError(str(other) + " must be the same type as " + str(self.__class__))
        return Pos(self.x - other.x, self.y - other.y)

    def __copy__(self):
        return Pos(self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, Pos):
            return False
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        return True


class Dot:
    """Point mobile en mécanique classique"""

    def __init__(self, pos: Pos, speed: Speed, mass: float):
        self.pos: Pos = pos
        self.speed: Speed = speed
        self.mass: float = mass

    def run(self, resultant: Force, time_step) -> None:
        """calcule le déplacement du point mobile"""
        acceleration: Acceleration = Acceleration(resultant.x / self.mass,
                                    resultant.y / self.mass)

        self.pos.x += 0.5 * acceleration.x * time_step ** 2 + self.speed.x * time_step
        self.pos.y += 0.5 * acceleration.y * time_step ** 2 + self.speed.y * time_step

        self.speed.x += acceleration.x * time_step
        self.speed.y += acceleration.y * time_step

    def __str__(self) -> str:
        return str(self.__class__) + ": \n" \
               + "\tpos.x= " + str(self.pos.x) + "\n" \
               + "\tpos.y= " + str(self.pos.y) + "\n" \
               + "\tspeed.y= " + str(self.speed.y) + "\n" \
               + "\tspeed.y= " + str(self.speed.y) + "\n" \
               + "\tmass= " + str(self.mass) + "\n"
