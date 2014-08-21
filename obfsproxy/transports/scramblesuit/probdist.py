"""
This module provides code to generate and sample probability distributions.

The class RandProbDist provides an interface to randomly generate probability
distributions.  Random samples can then be drawn from these distributions.
"""

import random

import const

import obfsproxy.common.log as logging

log = logging.get_obfslogger()


class RandProbDist:

    """
    Provides code to generate, sample and dump probability distributions.
    """

    def __init__( self, genSingleton, genProbSignleton=None, seed=None ):
        """
        Initialise a discrete probability distribution.

        The parameter `genSingleton' is expected to be a function which yields
        singletons for the probability distribution.  The optional `seed' can
        be used to seed the PRNG so that the probability distribution is
        generated deterministically.
        """

        self.prng = random if (seed is None) else random.Random(seed)

        self.sampleList = []
        self.dist = self.genDistribution(genSingleton, genProbSignleton)
        self.dumpDistribution()

    def genDistribution( self, genSingleton, genProbSignleton ):
        """
        Generate a discrete probability distribution.

        The parameter `genSingleton` is a function which is used to generate
        singletons for the probability distribution. `genProbSignleton`
        returns the probabilities for the singletons returned by
        `genSingleton`.
        """

        dist = {}

        # Amount of distinct bins, i.e., packet lengths or inter arrival times.
        bins = self.prng.randint(const.MIN_BINS, const.MAX_BINS)

        # Cumulative probability of all bins.
        cumulProb = 0

        for index in xrange(bins):
            if genProbSignleton:
                prob = genProbSignleton(index, bins, cumulProb)
            else:
                prob = self.prng.uniform(0, (1 - cumulProb))
            cumulProb += prob

            singleton = genSingleton()
            dist[singleton] = prob
            self.sampleList.append((cumulProb, singleton,))

        dist[genSingleton()] = (1 - cumulProb)

        return dist

    def dumpDistribution( self ):
        """
        Dump the probability distribution using the logging object.

        Only probabilities > 0.01 are dumped.
        """

        log.debug("Dumping probability distribution.")

        for singleton in self.dist.iterkeys():
            # We are not interested in tiny probabilities.
            if self.dist[singleton] > 0.01:
                log.debug("P(%s) = %.3f" %
                          (str(singleton), self.dist[singleton]))

    def randomSample( self ):
        """
        Draw and return a random sample from the probability distribution.
        """

        assert len(self.sampleList) > 0

        rand = random.random()

        for cumulProb, singleton in self.sampleList:
            if rand <= cumulProb:
                return singleton

        return self.sampleList[-1][1]


# Alias class name in order to provide a more intuitive API.
new = RandProbDist


def uniform(x):
    return new(lambda: x, lambda i, n, c: 1)
