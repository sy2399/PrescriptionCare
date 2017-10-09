import math
import pandas as pd
import numpy as np
import random

from networkx import *

from networkx.algorithms import approximation as approx
from networkx.algorithms.approximation import clique
from itertools import combinations
from collections import Counter
import operator

from matching.models import Disease

dxcode_input = []

