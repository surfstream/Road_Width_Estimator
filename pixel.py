class Pixel:
    def __init__(self,coord):
        self._coord = coord
        self._is_road = False

    def __repr__(self):
        return "\n(Top,Left): " +str(self._coord) +"\nIs Road: " + str(self._is_road)

    @property
    def coord(self):
        return self._coord

    @property
    def is_road(self):
        return self._is_road

    @is_road.setter
    def is_road(self, value):
        self._is_road = value