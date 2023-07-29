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

Earth_mu = 3.986004418e14
debris_data = pd.read_csv("cosmos1408.csv")

def meanmotion_to_semimajoraxis(mm, mu):
    return mu**(1/3)/((mm*2*np.pi/84600)**(2/3))


def meananomaly_to_trueanomaly(ma, e):
    return 2*np.arctan(np.sqrt((1+e)/(1-e))*np.tan(ma/2))


class MainHandler(RequestHandler):
    def get(self):
        # Get the orbital elements
        params = {}
        for param in ["a", "e", "i", "raan", "aop", "ta"]:
            argument = self.get_argument(param, None)
            if argument == None:
                self.set_status(422)
                self.write(json.dumps({"error": "Missing orbital elements"}))
                return
            params[param] = float(argument)
        result = {}
        for n, row in debris_data[1:5].iterrows():
            result[n] = {"semimajoraxis": meanmotion_to_semimajoraxis(row["MEAN_MOTION"], Earth_mu),
                         "eccentricity": row["ECCENTRICITY"],
                         "inclination": row["INCLINATION"],
                         "raan": row["RA_OF_ASC_NODE"],
                         "aop": row["ARG_OF_PERICENTER"],
                         "ta": meananomaly_to_trueanomaly(row["MEAN_ANOMALY"], row["ECCENTRICITY"])}
        self.set_status(200)
        self.write(json.dumps(result))


if __name__ == "__main__":
    app = Application([
        (r"/", MainHandler),
    ])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()