# %%

import numpy as np

results_100 = np.array([7,
12,
17,
22,
28])


results_200 = np.array([33,
39,
45,
50,
56])


results_500 = np.array([62,
69,
75,
82,
88])


results_1000 = np.array([97,
60 + 45,
60 + 53,
2*60 + 2,
2*60 + 10])




results_10000 = np.array([5*60 + 33,
8*60 + 53])

# %%

duration_100 = results_100 - np.concat([[0], results_100[:-1]])
# %%

duration_200 = results_200 - np.concat([results_100[-1:], results_200[:-1]])

# %%

duration_500 = results_500 - np.concat([results_200[-1:], results_500[:-1]])
duration_500

# %%

duration_1000 = results_1000 - np.concat([results_500[-1:], results_1000[:-1]])
duration_1000

# %%

duration_10000 = results_10000 - np.concat([results_1000[-1:], results_10000[:-1]])
duration_10000


##################################################################################
#### SECOND EXPERIMENT
##################################################################################

results_2000 = np.array([
13,
25,
37,
49,
61])

results_5000 = np.array([
60 + 37,
120 + 11,
180 + 7,
240 + 44])
# %%

duration_2000 = results_2000 - np.concat([[0], results_2000[:-1]])
duration_2000
# %%

duration_5000 = results_5000 - np.concat([results_2000[-1:], results_5000[:-1]])
duration_5000

# %%


import matplotlib.pyplot as plt

nodes = [100, 200, 500, 1000, 2000, 5000, 10000]
durations = [duration_100.mean(), duration_200.mean(), duration_500.mean(),
             duration_1000.mean(),duration_2000.mean(), duration_5000.mean(),
             duration_10000.mean()]

plt.plot(nodes, durations)
plt.xlabel("Topology size (Number of hosts)")
plt.ylabel("Simulation Time (s)")
# %%
