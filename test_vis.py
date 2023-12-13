import scipy.io as spio
import numpy as np
import os

# path = '../data/Processed/2021/01/01'

# files = [folder for folder in os.listdir(path)]

lib = spio.loadmat('master_program\Inputs\covis_bathy_2019b.mat')
covis = spio.loadmat("../data/Processed/2021/01/03/COVIS-20210103T000002-fullimaging1/COVIS-20210103T000002-imaging1.mat")

xg = covis["imaging"]["grid"][0][0][0]["x"][0]
yg = covis["imaging"]["grid"][0][0][0]["y"][0]
zg = covis["imaging"]["grid"][0][0][0]["z"][0]
vg = covis["imaging"]["grid"][0][0][0]["Id_filt"][0]

xb = lib["covis"]["grid"][0][0][0]["x"][0]
yb = lib["covis"]["grid"][0][0][0]["y"][0]
zb = lib["covis"]["grid"][0][0][0]["v"][0]
rb = np.sqrt(xb**2 + yb**2)
zb[(rb<4)] = np.NaN

v = vg.copy()
eps = np.nan
m = np.where(v == 0)
v[m] = eps  # remove zeros
v = 10 * np.log10(v)


import plotly.graph_objects as go

fig = go.Figure(go.Surface(
    contours = {
        "x": {"show": True, "start": -2, "end": 4, "size": 0.2, "color":"black"},
        "z": {"show": True, "start": -2, "end": 4, "size": 0.2}
    },
    x = xb[0,:],
    y = yb[:,0],
    z = zb,
    colorscale='earth'
    ))

fig.add_trace(go.Scatter3d(
    x=[0, 0],
    y=[0, 0],
    z=[0, 4.2],
    mode='lines',
    line=dict(color='yellow', width=4)
))

fig.add_trace(go.Isosurface(
    x=xg.flatten(),
    y=yg.flatten(),
    z=zg.flatten(),
    value=v.flatten(),
    isomax=np.nanmax(v),
    isomin=np.nanmin(v),
    opacity=0.5,
    colorscale='thermal'
))

# Update the layout to set axis labels
fig.update_layout(scene=dict(
    xaxis_title='Easting of COVIS (m)',
    yaxis_title='Northing of COVIS (m)',
    zaxis_title='Height above COVIS base (m)',
    xaxis_range=[-20, 1],
    yaxis_range=[-8,12],
    zaxis_range=[-2, 15],
))

fig.show()