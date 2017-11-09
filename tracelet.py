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
        self.opt_y1 = 0.5  # Optimized plateau value
        self.opt_tau = 1  # Optimized tau (1/k)
        self.R2 = 0  # R2 of optimization
        self.opt_success = False

    def objective_function_o0p1(self, para):
        """
        This is the cost function we want to minimize for zeroth-order (o0), one-parameter (p1) fitting

        :param para: Parameters, here only one parameter (k) with initial guess
        :return: Sums of squares of differences between predicted and actual
        """

        import models

        k = para

        y0 = self.y[0]
        y1 = self.y[-1]
        y = self.y

        # Predict y from t usint zeroth order model
        y_hat = [models.model_zero(x - self.x[0], k, y0, y1) for x in self.x]

        # Use sums of square as cost
        ss = sum([(y[i] - y_hat[i]) ** 2 for i in range(len(y))])

        return ss


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

        # Predict y from t using first order model
        y_hat = [models.model_first(x-self.x[0], k, y0, y1) for x in self.x]

        # Use sums of square as cost
        ss = sum([(y[i] - y_hat[i]) ** 2 for i in range(len(y))])

        return ss


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
        y = self.y

        # Predict y from t using first order model
        y_hat = [models.model_first(x-self.x[0], k, y0, y1) for x in self.x]

        # Use sums of square as cost
        ss = sum([(y[i] - y_hat[i]) ** 2 for i in range(len(y))])

        return ss


    def optimize(self, model):
        """
        Perform optimization to yield best-fitted k (x) as well as y1, tau, SE, and R2, etc.

        :param model: Int - the kinetic model to use. 0: zeroth order one parameter; 1: first order one parameter;
        2: first order two parameter

        :return: True
        """
        import scipy.optimize
        import numpy as np

        assert model in [0, 1, 2], "Check specification of kinetic model."

        # Single parameter zeroth-order fitting (only optimizing for k)
        if model == 0:
            res = scipy.optimize.minimize(self.objective_function_o0p1, 2)

            if res.success:
                self.opt_success = True
                self.opt_k = res.x
                print(res.x)

            else:
                print("Optimization unsuccessful")  # Throw error later


        # Single parameter first-order fitting (only optimizing for k)
        elif model == 1:
            res = scipy.optimize.minimize(self.objective_function_o1p1, 2)

            if res.success:
                self.opt_success = True
                self.opt_k = res.x
                self.opt_y1 = self.y[-1]
                print(res.x)

            else:
                print("Optimization unsuccessful")  # Throw error later

        # Two-parameter first-order fitting (only optimizing for k)
        elif model == 2:
            maxiter = 500
            res = scipy.optimize.minimize(self.objective_function_o1p2, np.array([2, self.y[-1]]),
                                          method='Nelder-Mead',  # Use Nelder-Mead simplex for multivariate
                                          options={'maxiter': maxiter})

            print(res.message)

            if res.success or res.nit == maxiter:
                self.opt_success = True
                self.opt_k = res.x[0]
                self.opt_y1 = res.x[1]
                print(res.x)

            else:
                print("Optimization unsuccessful")  # Throw error later

        # Calculate Tau (1/k) from the optimized k
        if not res.success:
            print("Optimization unsuccessful")  # Throw error later

        self.opt_tau = 1. / self.opt_k

        print(res.fun)
        print(sum((self.y - np.mean(self.y)) ** 2))
        print((res.fun/sum((self.y - np.mean(self.y)) ** 2)))
        # Calculate coefficient of determination as one minus residual sum of squares over total sum of squares
        self.R2 = 1. - (res.fun/sum((self.y - np.mean(self.y)) ** 2))
        print(self.R2)

        return True
