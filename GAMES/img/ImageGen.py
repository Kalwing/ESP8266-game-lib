import matplotlib.pyplot as plt
import numpy as np
import sys

filename = sys.argv[-1]
print(F"Treating {filename}\n")

img = plt.imread(filename)
img = img/img.max()
img = np.where(img < 0.5, 1, 0)[:,:,0].astype('str')
r = ["".join(line) for line in img]
r = "\n".join(r)

print(r)
