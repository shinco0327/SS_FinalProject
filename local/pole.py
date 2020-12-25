import numpy as np
import matplotlib.pyplot as plt



z=np.roots([1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11, 1/11,1/11, 1/11])
p=np.roots([1,0,0,0,0,0,0,0,0,0,0])
angle = np.linspace(-np.pi, np.pi, 50)
cirx = np.sin(angle)
ciry = np.cos(angle)
plt.figure(figsize=(8,8))
plt.plot(cirx, ciry,'k-')
plt.plot(np.real(z), np.imag(z), 'o', markersize=12)
plt.plot(np.real(p), np.imag(p), 'x', markersize=12)
plt.grid()

plt.xlim((-2, 2))
plt.xlabel('Real')
plt.ylim((-2, 2))
plt.ylabel('Imag')