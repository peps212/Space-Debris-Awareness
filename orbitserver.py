#/usr/bin/env python3

'''
    Space debris REST API
    OrionHack 29/07/2023
'''

import tornado.ioloop
from tornado.web import RequestHandler, Application
import json
import pandas as pd
import numpy as np


def meanmotion_to_semimajoraxis(mm, mu):
    return mu**(1/3)/((mm*2*np.pi/84600)**(2/3))


def meananomaly_to_trueanomaly(ma, e):
    return 2*np.arctan(np.sqrt((1+e)/(1-e))*np.tan(ma/2))


def find_nodes(orbit0, orbit1,direction=1):
    '''
        Finds the nodes of two orbits
        Not always correct, but good enough for now
    '''
    i = orbit0["INCLINATION"]
    argperi = orbit0["ARG_OF_PERICENTER"]
    rx, ry, rz =  np.cos(argperi)*np.cos(i), np.sin(argperi)*np.cos(i), np.sin(i)
    i = orbit1["INCLINATION"]
    argperi = orbit1["ARG_OF_PERICENTER"]
    x, y, z = np.cos(argperi)*np.cos(i), np.sin(argperi)*np.cos(i), np.sin(i)
    # cross product with reference vector
    x, y, z = np.cross([rx, ry, rz], [x, y, z])
    x, y, z = x*direction, y*direction, z*direction
    # find angle with periapsis vector
    px, py, pz = np.cos(argperi), np.sin(argperi), 0
    ta = np.arccos(np.dot([x, y, z], [px, py, pz])/(np.linalg.norm([x, y, z])*np.linalg.norm([px, py, pz])))
    # get radius from true anomaly
    r = orbit1["a"]*(1-orbit1["ECCENTRICITY"]**2)/(1+orbit1["ECCENTRICITY"]*np.cos(ta))
    # convert to cartesian
    x, y, z = r*np.cos(ta), r*np.sin(ta), 0  
    return x, y, z

# Set up global constants
Earth_mu = 3.986004418e14
debris_data = pd.read_csv("https://celestrak.org/NORAD/elements/gp.php?GROUP=1982-092&FORMAT=csv")
debris_data["a"] = meanmotion_to_semimajoraxis(debris_data["MEAN_MOTION"], Earth_mu)


class MainHandler(RequestHandler):
    def get(self):
        global debris_data, Earth_mu
        # Get the orbital elements
        params = {}
        if self.get_argument("mm", None) != None:
            paramset = ["mm", "e", "i", "raan", "aop", "ma"]
            params["a"] = meanmotion_to_semimajoraxis(float(self.get_argument("mm")), Earth_mu)
        else:
            paramset = ["a", "e", "i", "raan", "aop", "ta"]
        for param in paramset:
            argument = self.get_argument(param, None)
            if argument == None:
                self.set_status(422)
                self.write(json.dumps({"error": "Missing orbital elements"}))
                return
            params[param] = float(argument)
        params["INCLINATION"] = params["i"]
        params["ECCENTRICITY"] = params["e"]
        params["ARG_OF_PERICENTER"] = params["aop"]
        dists = []
        for n, row in debris_data.iterrows():
                nodes = []
                for direction in [-1,1]:
                    x,y,z = find_nodes(row, params, direction)
                    nodes.append(np.array([x,y,z]))
                    x,y,z = find_nodes(params, row, direction)
                    nodes.append(np.array([x,y,z]))
                # find the closest nodes
                dists.append(np.min([np.linalg.norm(nodes[0]-nodes[1]),
                            np.linalg.norm(nodes[2]-nodes[3]),
                            np.linalg.norm(nodes[0]-nodes[3]),
                            np.linalg.norm(nodes[1]-nodes[2])]))  
        debris_data["dist"] = dists                              
        sorted_data = debris_data.sort_values(by="dist")
        result = {}
        for n, row in sorted_data[:5].iterrows():
            result[n] = {"semimajoraxis": meanmotion_to_semimajoraxis(row["MEAN_MOTION"], Earth_mu),
                            "eccentricity": row["ECCENTRICITY"],
                            "inclination": row["INCLINATION"],
                            "raan": row["RA_OF_ASC_NODE"],
                            "aop": row["ARG_OF_PERICENTER"],
                            "ta": meananomaly_to_trueanomaly(row["MEAN_ANOMALY"], row["ECCENTRICITY"])}
        self.set_status(200)
        self.write(json.dumps(result))


def make_app():
    return Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()