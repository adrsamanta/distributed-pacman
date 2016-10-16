from deap import base


class Team(object):
    def __init__(self, off, defe):
        self.offense = off
        self.defense = defe

        # def __copy__(self):
        #     return Team(self.offense, self.defense)
        #
        # def __deepcopy__(self, memodict={}):
        #     return Team(copy.deepcopy(self.offense), copy.deepcopy(self.defense))
        # defined for safety, to make sure copying will work properly


# redefine the getter so that 0 weights are allowed
class Fitness0(base.Fitness):
    def getValues(self):
        ###Need to make this not fuck up when a weight is 0
        def div2(v1, v2):
            if v1 == 0 or v2 == 0:
                return 0
            else:
                return v1 / v2

        return tuple(map(div2, self.wvalues, self.weights))

    values = property(getValues, base.Fitness.setValues, base.Fitness.delValues,
                      ("Fitness values. Use directly ``individual.fitness.values = values`` "
                       "in order to set the fitness and ``del individual.fitness.values`` "
                       "in order to clear (invalidate) the fitness. The (unweighted) fitness "
                       "can be directly accessed via ``individual.fitness.values``."))
