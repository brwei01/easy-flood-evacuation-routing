from shapely.geometry import Point, Polygon

# User Input -- returns the study area in shapely shapefile
class User_Input(object):
    def __init__(self):
        pass
    def input(self):
        while True:
            try:
                easting, northing = list(map(int, (input('input easting: '), input('input northing:'))))
                if any([425000 < easting < 430000, 75000 < northing < 80000,
                        465000 < easting < 470000, 95000 < northing < 100000]):
                    raise Out_of_Boundary_Error
                if any([easting < 425000, northing < 75000, easting > 470000, northing > 100000]):
                    raise Out_of_Range_Error
            except ValueError:
                print('wrong input value, please input a numeric number')
            except Out_of_Range_Error:
                print('input location out of study area')
            # this following clause is reserved for task 6
            except Out_of_Boundary_Error:
                return (easting, northing), Study_Area(easting, northing).circle_boundary_intersection()
                break
            else:
                return (easting, northing), Study_Area(easting, northing).circle()
                break


# Error Classes
class Error(Exception):
    pass
class Out_of_Boundary_Error(Error):
    pass
class Out_of_Range_Error(Error):
    pass


# Study area delineation
class Study_Area(object):
    def __init__(self, easting, northing):
        self.easting = easting
        self.northing = northing

    def circle(self):
        client_pt = Point(self.easting, self.northing)
        circle = client_pt.buffer(5000)
        return circle

    def boundary(self):
        x1, x2 = 425000, 470000
        y1, y2 = 75000, 100000
        boundary_polygon = Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
        return boundary_polygon

    def circle_boundary_intersection(self):
        return self.boundary().intersection(self.circle())



