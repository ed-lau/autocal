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
        :param tm:
        :param dt:
        """
        self.x = tm
        self.y = dt
        self.opt_k = 1
        self.tau = 1
        self.R2 = 0


    def objective_function(self, k):
        """
        This is the cost function we want to minimize
        :return:
        """
        import models
        y0 = self.y[0]
        y1 = self.y[-1]
        y = self.y

        ypred = [models.model(x-self.x[0], k, y0, y1) for x in self.x]

        return sum([(y[i] - ypred[i])**2 for i in range(len(y))])


    def optimize(self):
        """
        Perform optimization to yield best-fitted k (x), tau, SE, and R2, etc.

        :return:
        """
        import scipy.optimize
        res = scipy.optimize.minimize(self.objective_function, 1)

        self.opt_k = res.x
        self.tau = 1/res.x
        print(res.x)

