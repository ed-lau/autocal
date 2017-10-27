"""
calctau
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""


class Tracelet(object):
    """
    Object to hold each downward slope of a trace for optimization.

    """

    def __init__(self, tm, dt):
        """
        Initialize, using time as x axis and data as y axis.

        :param tm: list  median time within the tracelet (x axis in optimiztaion)
        :param dt: list data point (340/380 ratio) within the tracelet (y axis in optimization)

        """
        self.x = tm
        self.y = dt

        # Private
        self.opt_k = 1  # Optimized k value
        self.opt_y1 = 0.5 # Optimized plateau value
        self.tau = 1    # Optimized tau (1/k)
        self.R2 = 0     # R2 of optimization


    def objective_function_o1p1(self, para):
        """
        This is the cost function we want to minimize for first-order (o1), one-parameter (p1) fitting

        :param para: Parameters, here only one parameter (k) with initial guess
        :return: Sums of squares of differences between predicted and actual
        """

        import models

        k = para

        y0 = self.y[0]
        y1 = self.y[-1]
        y = self.y

        ypred = [models.model_first(x-self.x[0], k, y0, y1) for x in self.x]
        #ypred = [models.model_zero(x - self.x[0], k, y0, y1) for x in self.x]

        return sum([(y[i] - ypred[i])**2 for i in range(len(y))])


    def objective_function_o1p2(self, para):
        """
        This is the cost function we want to minimize for first-order (o1), one-parameter (p2) fitting

        :param para: nparray para[0] is k, para[1] is the plateau (y1)

        :return: Sums of squares of differences between predicted and actual
        """

        import models

        k = para[0]
        y1 = para[1]

        y0 = self.y[0]
        #y1 = self.y[-1]
        y = self.y

        ypred = [models.model_first(x-self.x[0], k, y0, y1) for x in self.x]
        #ypred = [models.model_zero(x - self.x[0], k, y0, y1) for x in self.x]

        return sum([(y[i] - ypred[i])**2 for i in range(len(y))])


    def optimize(self, parameter):
        """
        Perform optimization to yield best-fitted k (x) as well as y1, tau, SE, and R2, etc.

        :return:
        """
        import scipy.optimize
        import numpy as np

        # Single parameter first-order fitting (only optimizing for k)
        if parameter == 1:
            res = scipy.optimize.minimize(self.objective_function_o1p1, 2)
            self.opt_k = res.x
            self.tau = 1/res.x
            print(res.x)

        # Two-parameter first-order fitting (only optimizing for k)
        elif parameter == 2:
            res = scipy.optimize.minimize(trcelt.objective_function_o1p2, np.array([2, 0.5]),
                                          method='Nelder-Mead',
                                          options={'maxiter': 100})
            self.opt_k = res.x[0]
            self.tau = 1 / res.x[0]
            self.opt_y1 = res.x[1]
            print(res.x)
