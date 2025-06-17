import numpy as np
from pylab import plt, mpl

plt.style.use('seaborn-v0_8')
mpl.rcParams['font.family'] = 'serif'

def f(x):
    return np.sin(x) + 0.5 * x

def create_plot(x, y, styles, labels, axlabels):
    plt.figure(figsize=(10, 6))
    for i in range(len(x)):
        plt.plot(x[i], y[i], styles[i], label=labels[i])
        plt.xlabel(axlabels[0])
        plt.ylabel(axlabels[1])
    plt.legend(loc=0)


# Add noise
xn = np.linspace(-2 * np.pi, 2 * np.pi, 50)
xn = xn + 0.25 * np.random.standard_normal(len(xn))
yn = f(xn) + 0.25 * np.random.standard_normal(len(xn))

reg = np.polyfit(xn, yn, 14)
ry = np.polyval(reg, xn)

x = np.linspace(-2 * np.pi, 2 * np.pi, 50)
create_plot([x, x], [f(x), ry], ['b', 'r.'],
            ['f(x)', 'regression'], ['x', 'f(x)'])

plt.show()
