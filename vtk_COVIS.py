#!/usr/bin/env vtkpython
import os
import sys
import vtk

import scipy.io as spio
import numpy as np
import matplotlib.pyplot as plt
from load import *
import time
import re


# Colortable for the different plumes in showall
colors = np.array([
    (230, 25, 75),    # Red
    (60, 180, 75),    # Green
    (0, 130, 200),    # Blue
    (255, 127, 14),   # Orange
    (240, 50, 230),   # Purple
    (70, 240, 240),   # Cyan
    (255, 225, 25),   # Yellow
    (170, 110, 40),   # Brown
    (255, 20, 147),   # Pink
    (128, 128, 128),  # Gray
    (128, 128, 0),    # Olive
    (0, 0, 128)       # Navy
])/256

named_colors = [
    'Red',
    'Green',
    'Blue',
    'Orange',
    'Purple',
    'Cyan',
    'Yellow',
    'Brown',
    'Pink',
    'Gray',
    'Olive',
    'Navy'
]


def bathy(grid, zb):
    ''' This function creates the bathy and returns the mapper and contour actor
    '''
    # Create VTK mapper and actor for the first dataset
    mapper1 = vtk.vtkDataSetMapper()
    mapper1.SetInputData(grid)
    mapper1.SetScalarRange(np.nanmin(zb), np.nanmax(zb))

    # Create a color transfer function
    color_function = vtk.vtkColorTransferFunction()
    color_function.SetColorSpaceToDiverging()
    color_function.AddRGBPoint(np.nanmin(zb), 244, 164, 96)  # Dark blue
    color_function.AddRGBPoint(np.nanmax(zb), 255, 245, 238)  # Dark red

    mapper1.SetLookupTable(color_function)

    actor1 = vtk.vtkActor()
    actor1.SetMapper(mapper1)

    # Create a contour filter
    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputData(grid)
    contour_filter.GenerateValues(30, np.nanmin(zb), np.nanmax(zb))  # Adjust the number of contours as needed

    # Create a color transfer function
    color_function1 = vtk.vtkColorTransferFunction()
    color_function1.SetColorSpaceToDiverging()
    color_function1.AddRGBPoint(np.nanmin(zb), 0, 0, 0)
    color_function1.AddRGBPoint(np.nanmax(zb), 0, 0, 0)

    # Create mapper for contour lines
    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputConnection(contour_filter.GetOutputPort())
    contour_mapper.SetLookupTable(color_function1)

    # Create actor for contour lines
    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)

    return actor1, contour_actor


def imaging(vtk_data, c_value, opacity, rgb):
    ''' This function creates the imaging contours and returns both 
        the contour and actor
    '''
    # Create a VTK contour filter on imaging data
    contour = vtk.vtkContourFilter()
    contour.SetInputData(vtk_data)
    contour.SetValue(0, c_value)

    # Create a color transfer function
    color_function = vtk.vtkColorTransferFunction()
    color_function.AddRGBPoint(c_value, rgb[0], rgb[1], rgb[2])

    # Create a mapper 
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour.GetOutputPort())
    mapper.SetLookupTable(color_function)

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(opacity)

    return contour, actor


def animate(contour, frames, c_value, set_iters, render_window, rgb, times):
    ''' This function animates the different timesteps on a single day
    '''
    for i in range(set_iters):
        j = i % len(frames)
        # Update the contour filter imaging data
        contour.SetInputData(frames[j])
        contour.SetValue(0, c_value)

        # Create a color transfer function
        color_function = vtk.vtkColorTransferFunction()
        color_function.AddRGBPoint(c_value, rgb[0], rgb[1], rgb[2])

        render_window.Render()

        print(f'Showing plume {j} at time {times[j]}')
        time.sleep(2)
        

def create_axes(renderer):
    ''' This function adds axes to the visualisation
    '''
    # Add grid axes with ticks
    axes = vtk.vtkCubeAxesActor()
    axes.SetUseTextActor3D(1)
    # axes.SetBounds(grid.GetBounds())
    axes.SetBounds(-2, 15, -20, 1, -8, 12,)
    axes.SetCamera(renderer.GetActiveCamera())

    axes.GetXAxesGridlinesProperty().SetColor(0, 0, 0)
    axes.GetYAxesGridlinesProperty().SetColor(0, 0, 0)
    axes.GetZAxesGridlinesProperty().SetColor(0, 0, 0)

    axes.SetXTitle('Height above COVIS base')   # X axis = Z axis
    axes.SetXUnits('m')
    axes.SetYTitle('Easting of COVIS')          # Y axis = X axis
    axes.SetYUnits('m')
    axes.SetZTitle('Northing of COVIS')         # Z axis = Y axis
    axes.SetZUnits('m')

    axes.GetTitleTextProperty(0).SetColor(0, 0, 0)
    axes.GetLabelTextProperty(0).SetColor(0, 0, 0)

    axes.GetTitleTextProperty(1).SetColor(0, 0, 0)
    axes.GetLabelTextProperty(1).SetColor(0, 0, 0)

    axes.GetTitleTextProperty(2).SetColor(0, 0, 0)
    axes.GetLabelTextProperty(2).SetColor(0, 0, 0)

    axes.DrawXGridlinesOn()
    axes.DrawYGridlinesOn()
    axes.DrawZGridlinesOn()
    axes.SetGridLineLocation(axes.VTK_GRID_LINES_FURTHEST)

    axes.XAxisMinorTickVisibilityOff()
    axes.YAxisMinorTickVisibilityOff()
    axes.ZAxisMinorTickVisibilityOff()

    return axes


def main(argv):
    # Load data
    bathy_file = 'data/bathy/covis_bathy_2019b.mat'
    imaging_files = os.listdir("data/fullimaging")
    imaging_files.sort()
    times = []

    # Load data for all times on day
    frames = []
    for f in imaging_files:
        xg, yg, zg, v = load_imaging(f'data/fullimaging/{f}/{f}.mat')
        time = re.findall("T\d{6}", f)[0][1:]
        times.append(time)

        # Create histogram of backscatter values
        if argv[1] == 'hist':
            plt.hist(v.flatten(), bins=100, range=[-89,0], alpha=0.4, label=f't = {time}')
        else:
            frames.append(vtk_imaging(xg, yg, zg, v))

    # Plot histogram
    if argv[1] == 'hist':
        plt.ylabel('Frequency')
        plt.xlabel('Backscatter (dB)')
        plt.title('Histogram of backscatter frequency for imaging on a single day')
        plt.legend()
        plt.show()
        exit()
    
    xb, yb, zb = load_bathy(bathy_file)

    # Create bathy and actors for bathy
    grid = vtk_bathy(xb, yb, zb)
    actor_bathy, actor_bathy_contour = bathy(grid, zb)

    ## COVIS
    # Create a line source
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(0, 0, 0)
    line_source.SetPoint2(4.2, 0, 0)

    # Create a mapper
    mapper_COVIS = vtk.vtkPolyDataMapper()
    mapper_COVIS.SetInputConnection(line_source.GetOutputPort())

    # Create an actor
    actor_COVIS = vtk.vtkActor()
    actor_COVIS.SetMapper(mapper_COVIS)
    actor_COVIS.GetProperty().SetColor(1, 1, 0)  # Yellow color
    actor_COVIS.GetProperty().SetLineWidth(4)   # Set line width

    # Create a renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Add actors to the renderer
    renderer.AddActor(actor_bathy)
    renderer.AddActor(actor_bathy_contour)
    renderer.AddActor(actor_COVIS)

    # Create axes and add to renderer
    axes = create_axes(renderer)
    renderer.AddActor(axes)

    renderer.GetActiveCamera().Azimuth(-55)
    renderer.GetActiveCamera().Elevation(130)
    renderer.GetActiveCamera().SetViewUp(1, 0, 0)

    renderer.ResetCamera()
    renderer.GetActiveCamera().Zoom(2.5)

    # Decide the type of visualisation
    if argv[1] == 'animate':
        try:
            c_value = -int(argv[2])
            opacity = float(argv[3])
            set_iters = int(argv[4])
            assert -90 <= c_value <= 0 and 0 <= opacity <= 1 
            print(f'Animating all plumes with contour value {c_value} and opacity {opacity}')
        except:
            print('Invalid values, using defaults c_value=-40, opacity=0.5, iterations=20')
            c_value = -40
            opacity = 0.5
            set_iters = 20
        color = np.array([77,153,204])/256
        # create initial contour:
        contour, actor = imaging(frames[0], c_value, opacity, color)
        renderer.AddActor(actor)
        animate(contour, frames, c_value, set_iters, render_window, color, times)
    elif argv[1] == 'show':
        # Variables for different contour values
        c_values = [-60,-50,-40]
        opacities = [0.1,0.2,0.3]
        rgbs = np.array([[77,153,204],[128,77,128],[153,5,13]])/256

        try:
            f_num = int(argv[2])
            assert 0 <= f_num <= 11
            print(f'Showing imaging data of data file {f_num}')
        except:
            print('Invalid value, using first data file as default')
            f_num = 0

        for i in range(3):
            print(f'Added contour {i}')
            contour, actor = imaging(frames[f_num], c_values[i], opacities[i], rgbs[i])
            renderer.AddActor(actor)
    elif argv[1] == 'compare':
        # Set contour value and opacity
        try:
            c_value = -int(argv[2])
            opacity = float(argv[3])
            plumes = []
            
            for i in range(4, len(argv)):
                plumes.append(int(argv[i]))

            assert -90 <= c_value <= 0 and 0.0 <= opacity <= 1.0 and all([0 <= p <= 11 for p in plumes])
            print(f'Showing plumes {plumes} with contour value {c_value} and opacity {opacity}')
        except:
            print('Invalid values, using defaults c_value=-40, opacity=0.5 for plumes 0 and 1')
            plumes = [0,1]
            c_value = -40
            opacity = 0.5

        for i in plumes:
            print(f'Added plume {i}, datapoint at time {times[i]} with color {named_colors[i]}')
            contour, actor = imaging(frames[i], c_value, opacity, colors[i])
            renderer.AddActor(actor)

    render_window_interactor.Initialize()
    render_window_interactor.Start()

main(sys.argv)