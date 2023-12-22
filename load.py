import scipy.io as spio
import numpy as np
import vtk


def limit(v, X, Y, Z, xmin, xmax, ymin, ymax, zmin, zmax):
    ''' limits the data points to those inside the bathymetry grid
    '''
    m = (X >= xmin) & (X <= xmax) & (Y >= ymin) & (Y <= ymax) & (Z >= zmin) & (Z <= zmax)
    v[~m] = np.nan
    return v


def load_bathy(file):
    ''' This function reads the gridded data for the bathy
    '''
    lib = spio.loadmat(file)

    xb = lib["covis"]["grid"][0][0][0]["x"][0]
    yb = lib["covis"]["grid"][0][0][0]["y"][0]
    zb = lib["covis"]["grid"][0][0][0]["v"][0]
    rb = np.sqrt(xb**2 + yb**2)
    zb[(rb < 4)] = np.NaN

    zb = limit(zb, xb, yb, zb, -20, 1, -8, 12, -2, 15)
    print('Loaded bathy')

    return xb, yb, zb


def vtk_bathy(x, y, z):
    ''' This function creates the vtk Points for the bathy
    '''
    points = vtk.vtkPoints()
    grid = vtk.vtkStructuredGrid()
    colors = vtk.vtkFloatArray()
    colors.SetNumberOfComponents(1)

    # Populate points and colors
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            points.InsertNextPoint(z[i, j], x[i, j], y[i, j])
            colors.InsertNextValue(z[i, j])

    grid.SetDimensions(1, x.shape[1], x.shape[0])
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(colors)

    print('Created visual of bathy')

    return grid


def load_imaging(file):
    ''' This function reads the gridded data for the imaging
        mode of COVIS
    '''
    covis = spio.loadmat(file)

    xg = covis["imaging"]["grid"][0][0][0]["x"][0]
    yg = covis["imaging"]["grid"][0][0][0]["y"][0]
    zg = covis["imaging"]["grid"][0][0][0]["z"][0]
    vg = covis["imaging"]["grid"][0][0][0]["Id_filt"][0]

    v = vg.copy()
    eps = np.nan
    m = np.where(v == 0)
    v[m] = eps  # remove zeros
    v = 10 * np.log10(v)

    v = limit(v, xg, yg, zg, -20, 1, -8, 12, -2, 15)

    print(f'Loaded imaging of file {file.split("/")[-1]}')

    return xg, yg, zg, v


def vtk_imaging(x, y, z, v):
    ''' This function creates the VTK StructuredPoints
        for the imaging data
    '''

    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()

    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            for k in range(x.shape[2]):
                points.InsertNextPoint(z[i, j, k], y[i, j, k], x[i, j, k])
                scalars.InsertNextValue(v[i, j, k])

    vtk_data = vtk.vtkStructuredPoints()
    vtk_data.SetDimensions(x.shape[2], x.shape[1], x.shape[0])
    vtk_data.GetPointData().SetScalars(scalars)

    vtk_data.SetExtent(0, x.shape[2]-1, -x.shape[1]+1, 0, 0, x.shape[0]-1)
    vtk_data.SetSpacing(0.25,0.25,0.25)
    vtk_data.SetOrigin(-2,20, -40)

    print('Created structured points')

    return vtk_data