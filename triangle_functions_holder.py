class triangleFunctionHolder:

    def __init__(self, firstPoint, secondPoint, thirdPoint):
        self.firstPoint = firstPoint
        self.secondPoint = secondPoint
        self.thirdPoint = thirdPoint
        self.result = None

    def calculate(self, argument):
        if (argument < self.firstPoint):
            return [("low", 1), ("medium", 0), ("high", 0)]
        elif (argument > self.thirdPoint):
            return [("low", 0), ("medium", 0), ("high", 1)]
        elif (argument <= self.secondPoint and argument >= self.firstPoint):
            a = -1.0/(self.secondPoint - self.firstPoint)
            b = -1 * a *self.secondPoint
            low = a*argument + b
            a2 = 1.0/(self.secondPoint - self.firstPoint)
            b2 = 1.0 - a2 * self.secondPoint
            medium = a2 * argument + b2
            return [("low", low), ("medium", medium), ("high", 0)]
        elif (argument <= self.thirdPoint and argument >= self.secondPoint):
            a = -1.0 / (self.thirdPoint - self.secondPoint)
            b = -1 * a * self.thirdPoint
            medium = a * argument + b
            a2 = 1.0 / (self.thirdPoint - self.secondPoint)
            b2 = 1.0 - a2 * self.thirdPoint
            high = a2 * argument + b2
            return [("low", 0), ("medium", medium), ("high", high)]