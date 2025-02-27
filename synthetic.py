import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt


def make_var_stationary(beta, radius=0.97):
    '''Rescale coefficients of VAR model to make stable.'''
    p = beta.shape[0]
    lag = beta.shape[1] // p
    bottom = np.hstack((np.eye(p * (lag - 1)), np.zeros((p * (lag - 1), p))))
    beta_tilde = np.vstack((beta, bottom))
    eigvals = np.linalg.eigvals(beta_tilde)
    max_eig = max(np.abs(eigvals))
    nonstationary = max_eig > radius
    if nonstationary:
        return make_var_stationary(0.95 * beta, radius)
    else:
        return beta


def simulate_var(p, T, lag, sparsity=0.2, beta_value=1.0, sd=0.1, seed=0):
    if seed is not None:
        np.random.seed(seed)

    # Set up coefficients and Granger causality ground truth.
    GC = np.eye(p, dtype=int)
    beta = np.eye(p) * beta_value

    num_nonzero = int(p * sparsity) - 1
    for i in range(p):
        choice = np.random.choice(p - 1, size=num_nonzero, replace=False)
        choice[choice >= i] += 1
        beta[i, choice] = beta_value
        GC[i, choice] = 1

    beta = np.hstack([beta for _ in range(lag)])
    beta = make_var_stationary(beta)

    # Generate data.
    burn_in = 100
    errors = np.random.normal(scale=sd, size=(p, T + burn_in))
    X = np.zeros((p, T + burn_in))
    X[:, :lag] = errors[:, :lag]
    for t in range(lag, T + burn_in):
        X[:, t] = np.dot(beta, X[:, (t-lag):t].flatten(order='F'))
        X[:, t] += + errors[:, t-1]

    return X.T[burn_in:], beta, GC


def lorenz(x, t, F):
    '''Partial derivatives for Lorenz-96 ODE.'''
    p = len(x)
    dxdt = np.zeros(p)
    for i in range(p):
        dxdt[i] = (x[(i+1) % p] - x[(i-2) % p]) * x[(i-1) % p] - x[i] + F

    return dxdt


def simulate_lorenz_96_nonstationary(p, T, F=10.0, delta_t=0.1, sd=0.1, burn_in=1000,
                       seed=0):
    if seed is not None:
        np.random.seed(seed)

    # Use scipy to solve ODE.
    x0 = np.random.normal(scale=0.01, size=p)
    t = np.linspace(0, (T + burn_in) * delta_t, T + burn_in)
    global t_max
    t_max = (T + burn_in) * delta_t
    X = odeint(lorenz_nonstationary, x0, t, args=(F,))
    X += np.random.normal(scale=sd, size=(T + burn_in, p))

    # Set up Granger causality ground truth.
    GC = np.zeros((p, p), dtype=int)
    for i in range(p):
        GC[i, i] = 1
        GC[i, (i + 1) % p] = 1
        GC[i, (i - 1) % p] = 1
        GC[i, (i - 2) % p] = 1

    return X[burn_in:], GC

def simulate_lorenz_96(p, T, F=10.0, delta_t=0.1, sd=0.1, burn_in=1000,
                       seed=0):
    if seed is not None:
        np.random.seed(seed)

    # Use scipy to solve ODE.
    x0 = np.random.normal(scale=0.01, size=p)
    t = np.linspace(0, (T + burn_in) * delta_t, T + burn_in)
    X = odeint(lorenz, x0, t, args=(F,))
    X += np.random.normal(scale=sd, size=(T + burn_in, p))

    # Set up Granger causality ground truth.
    GC = np.zeros((p, p), dtype=int)
    for i in range(p):
        GC[i, i] = 1
        GC[i, (i + 1) % p] = 1
        GC[i, (i - 1) % p] = 1
        GC[i, (i - 2) % p] = 1

    return X[burn_in:], GC


def lorenz_nonstationary(x, t, F):
    '''Partial derivatives for Lorenz-96 ODE.'''
    p = len(x)
    global t_max
    if t < t_max * (1/2):
        coff = 1 - t / (t_max * (1/2))
    else:
        coff = 0
    # print(coff)
    dxdt = np.zeros(p)
    for i in range(p):
        dxdt[i] = coff * (x[(i+1) % p] - x[(i-2) % p]) * x[(i-1) % p] - x[i] + F
    return dxdt

def simulate_lorenz_96_mine_nonstationary(p, T, F=2.5, delta_t=0.1, sd=0.1, burn_in=1000, scale=0.01, seed=0):
    if seed is not None:
        np.random.seed(seed)

    # Use scipy to solve ODE.
    x0 = np.random.normal(scale=scale, size=p)
    t = np.linspace(0, (T + burn_in) * delta_t, T + burn_in)
    # X = odeint(lorenz, x0, t, args=(F,))
    X = np.zeros([T + burn_in, p])
    X[0] = x0
    for i in range(1,T // 2 + burn_in):
        x = X[i-1]
        for j in range(p):
            X[i][j] = delta_t * (x[(j + 1) % p] - x[(j - 2) % p]) * x[(j - 1) % p] + (1 - delta_t) * x[j % p] + delta_t * F
    for i in range(T // 2 + burn_in, T + burn_in):
        X[i] = X[i - 1]
        
    X += np.random.normal(scale=sd, size=(T + burn_in, p))

    # Set up Granger causality ground truth.
    GC = np.zeros((p, p), dtype=int)
    for i in range(p):
        GC[i, i] = 1
        GC[i, (i + 1) % p] = 1
        GC[i, (i - 1) % p] = 1
        GC[i, (i - 2) % p] = 1

    return X[burn_in:], GC

def simulate_lorenz_96_mine(p, T, F=2.5, delta_t=0.1, sd=0.1, burn_in=1000, scale=0.01, seed=0):
    if seed is not None:
        np.random.seed(seed)

    # Use scipy to solve ODE.
    x0 = np.random.normal(scale=scale, size=p)
    t = np.linspace(0, (T + burn_in) * delta_t, T + burn_in)
    # X = odeint(lorenz, x0, t, args=(F,))
    X = np.zeros([T + burn_in, p])
    X[0] = x0
    for i in range(1,T + burn_in):
        x = X[i-1]
        for j in range(p):
            X[i][j] = delta_t * (x[(j + 1) % p] - x[(j - 2) % p]) * x[(j - 1) % p] + (1 - delta_t) * x[j % p] + delta_t * F
        
    X += np.random.normal(scale=sd, size=(T + burn_in, p))

    # Set up Granger causality ground truth.
    GC = np.zeros((p, p), dtype=int)
    for i in range(p):
        GC[i, i] = 1
        GC[i, (i + 1) % p] = 1
        GC[i, (i - 1) % p] = 1
        GC[i, (i - 2) % p] = 1

    return X[burn_in:], GC

def Causal_Figure(GC, GC_est):
    fig, axarr = plt.subplots(1, 2, figsize=(16, 5))
    axarr[0].imshow(GC, cmap='Blues')
    axarr[0].set_title('GC actual')
    axarr[0].set_ylabel('Affected series')
    axarr[0].set_xlabel('Causal series')
    axarr[0].set_xticks([])
    axarr[0].set_yticks([])

    im = axarr[1].imshow(GC_est, cmap='Blues')
    axarr[1].set_title('GC estimated')
    axarr[1].set_ylabel('Affected series')
    axarr[1].set_xlabel('Causal series')
    axarr[1].set_xticks([])
    axarr[1].set_yticks([])
    plt.colorbar(im, cax=None, ax=None, shrink=0.8)
    
def standardise(X, axis=0, keepdims=True, copy=False):
    if copy:
        X = np.copy(X)
    # X -= X.mean(axis=axis, keepdims=keepdims)
    # X /= X.std(axis=axis, keepdims=keepdims)
    X -= X.mean(keepdims=keepdims)
    X /= X.std(keepdims=keepdims)
    return X

def generator1(T=1000, alpha=0.05,B_self=1):
    np.random.seed(0)
    X = np.zeros([T,3])
    X[:,2] = np.random.randint(-1,2,size=T)
    for i in range(1,T):
        X[i,0] = X[i-1,0] + X[i-1,2]
        X[i,1] = B_self * X[i-1,1] + alpha * X[i-1,2] * X[i-1,0]
    # plt.plot(X)
    GC = np.array([[1,0,1],[1,B_self,1],[0,0,0]])
    return X, GC

def generator1_nonstationary(T=200, alpha=0.5,seed=0):
    np.random.seed(seed)
    GC1 = np.array([[1,0,1],[1,1,1],[0,0,0]])
    GC2 = np.array([[1,0,1],[0,1,0],[0,0,0]])
    GC_l = np.zeros([T,3,3])
    GC_l[0] = GC1
    alpha_l = np.zeros(T)
    X = np.zeros([T,3])
    X[:,2] = np.random.randint(-1,2,size=T)
    alpha_l[T//4:3*T//4] = alpha
    for i in range(1,T):
        X[i,0] = X[i-1,0] + X[i-1,2]
        X[i,1] = alpha_l[i] * X[i-1,2] * X[i-1,0]
        if alpha_l[i] == 0:
            GC_l[i] = GC2
        else:
            GC_l[i] = GC1
    return X, GC_l

def generator2(T=1000, alpha=1, beta=1, sd=0.01, scale=1):
    np.random.seed(0)
    X = np.zeros([T,4])
    X[:,0] = scale * np.random.randint(-1,2,size=T)
    X[:,1] = scale * np.random.randint(-1,2,size=T)
    for i in range(1,T):
        X[i,2] = alpha * (X[i-1,0] + X[i-1,1])
        X[i,3] = beta * X[i-1,0] * X[i-1,1]
    # plt.plot(X)
    GC = np.array([[0,0,0,0],[0,0,0,0],[1*(alpha>0),1*(alpha>0),0,0],[1*(beta>0),1*(beta>0),0,0]])
    X += np.random.normal(scale=sd, size=(T, 4))
    return X, GC

def generator2_nonstationary(T=1000, alpha=1, beta=1, sd=0.01, scale=1):
    np.random.seed(0)
    X = np.zeros([T,4])
    alpha_l = np.zeros(T)
    beta_l = np.zeros(T)
    GC_l = np.zeros([T,4,4])
    alpha_l[T//8:5*T//8] = alpha
    beta_l[3*T//8:7*T//8] = beta
    X[:,0] = scale * np.random.randint(-1,2,size=T)
    X[:,1] = scale * np.random.randint(-1,2,size=T)
    for i in range(1,T):
        X[i,2] = alpha_l[i] * (X[i-1,0] + X[i-1,1])
        X[i,3] = beta_l[i] * X[i-1,0] * X[i-1,1]
        if alpha_l[i] > 0:
            GC_l[i,2,0:2] = 1
        if beta_l[i] > 0:
            GC_l[i,3,0:2] = 1
    # plt.plot(X)
    X += np.random.normal(scale=sd, size=(T, 4))
    return X, GC_l