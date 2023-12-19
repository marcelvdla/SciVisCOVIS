#!/usr/bin/env vtkpython

import os
import sys
import vtk

import scipy.io as spio
import numpy as np
from load import *

def main(argv):
    # Load data
    bathy_file = 'data/covis_bathy_2019b.mat'
    imaging_files = os.listdir("data/fullimaging")
    data_file = f'data/fullimaging/{imaging_files[0]}/{imaging_files[0]}.mat'

    xg, yg, zg, v = load_imaging(data_file)
    xb, yb, zb = load_bathy(bathy_file)

    # Load initial imaging data and bathy
    vtk_data2 = vtk_imaging(xg, yg, zg, v)
    grid = vtk_bathy(xb, yb, zb)

    # Create VTK mapper and actor for the bathy
    mapper1 = vtk.vtkDataSetMapper()
    mapper1.SetInputData(grid)
    mapper1.SetScalarRange(np.nanmin(zb), np.nanmax(zb))

    actor1 = vtk.vtkActor()
    actor1.SetMapper(mapper1)

    # Create a VTK contour filter on imaging data
    contour2 = vtk.vtkContourFilter()
    contour2.SetInputData(vtk_data2)
    contour2.SetValue(0, (np.nanmax(v) + np.nanmin(v))/2)

    # Create a mapper and actor for the imaging data
    mapper2 = vtk.vtkPolyDataMapper()
    mapper2.SetInputConnection(contour2.GetOutputPort())
    actor2 = vtk.vtkActor()
    actor2.SetMapper(mapper2)

    # Create a renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800,800)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Add actors to the renderer
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)

    # Set camera position
    # renderer.GetActiveCamera().Azimuth(30)
    # renderer.GetActiveCamera().Elevation(30)

    # Reset camera and render
    # renderer.ResetCamera()
    # render_window.Render()

    # Start the interactive visualization
    # render_window_interactor.Start()

    # Set up the animation scene
    # animation_scene = vtk.vtkAnimationScene()
    # animation_scene.SetPlayMode(vtk.vtkAnimationScene.Play)

    # Add the cone actor to the scene
    # animation_scene.AddRenderer(renderer)
    # animation_scene.AddActor(actor2)
    # animation_scene.SetModeToSequence()

    # Set up the animation
    for f in imaging_files:
                            
        # Load initial imaging data
        xg, yg, zg, v = load_imaging(f'data/fullimaging/{f}/{f}.mat')
        new_frame = vtk_imaging(xg, yg, zg, v)

        # Update the contour filter imaging data
        contour2.SetInputData(new_frame)
        contour2.SetValue(0, (np.nanmax(v) + np.nanmin(v))/2)

        render_window.Render()

        # Add the current frame to the scene
        # animation_scene.AddKeyFrame()

    # Set up the interactor for the animation
    # animation_scene.SetFrameRate(1)  # Set the frame rate
    # animation_scene.Play()
    render_window_interactor.Initialize()
    render_window_interactor.Start()

main(sys.argv)