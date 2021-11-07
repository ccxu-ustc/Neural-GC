import numpy as np
import matplotlib.pyplot as plt

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