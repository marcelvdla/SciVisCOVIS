# %%
import scipy.io as spio
import numpy as np
import vtk

# Load data
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
zb[(rb < 4)] = np.NaN

v = vg.copy()
eps = np.nan
m = np.where(v == 0)
v[m] = eps  # remove zeros
v = 10 * np.log10(v)

# Create VTK data structures
points = vtk.vtkPoints()
grid = vtk.vtkStructuredGrid()
colors = vtk.vtkFloatArray()
colors.SetNumberOfComponents(1)

# Populate points and colors
for i in range(xb.shape[0]):
    for j in range(xb.shape[1]):
        points.InsertNextPoint(zb[i, j], xb[i, j], yb[i, j])
        colors.InsertNextValue(zb[i, j])

grid.SetDimensions(1, xb.shape[1], xb.shape[0])
grid.SetPoints(points)

# Create VTK mapper and actor for the first dataset
mapper1 = vtk.vtkDataSetMapper()
mapper1.SetInputData(grid)
mapper1.SetScalarRange(np.nanmin(zb), np.nanmax(zb))

actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

# Create a VTK structured points object for the second dataset
points2 = vtk.vtkPoints()
scalars2 = vtk.vtkFloatArray()

for i in range(xg.shape[0]):
    for j in range(xg.shape[1]):
        for k in range(xg.shape[2]):
            points2.InsertNextPoint(zg[i, j, k], yg[i, j, k], xg[i, j, k])
            scalars2.InsertNextValue(v[i, j, k])

vtk_data2 = vtk.vtkStructuredPoints()
vtk_data2.SetDimensions(xg.shape[2], xg.shape[1], xg.shape[0])
vtk_data2.GetPointData().SetScalars(scalars2)

vtk_data2.SetExtent(0, xg.shape[2]-1, -xg.shape[1]+1, 0, 0, xg.shape[0]-1)
vtk_data2.SetSpacing(0.25,0.25,0.25)
vtk_data2.SetOrigin(-2,20, -40)

# Create a VTK contour filter
contour2 = vtk.vtkContourFilter()
contour2.SetInputData(vtk_data2)
contour2.SetValue(0, (np.nanmax(v) + np.nanmin(v))/2)

# Create a mapper for the second dataset
mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(contour2.GetOutputPort())

# Create an actor for the second dataset
actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)

# Create a renderer and render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create a render window interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Add actors to the renderer
renderer.AddActor(actor1)
renderer.AddActor(actor2)

# Create a slider to set the isovalue
slider_rep = vtk.vtkSliderRepresentation2D()
slider_rep.SetMinimumValue(np.nanmin(v))
slider_rep.SetMaximumValue(np.nanmax(v))
slider_rep.SetValue((np.nanmax(v) + np.nanmin(v)) / 2)
slider_rep.SetTitleText("Contour")
slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
slider_rep.GetPoint1Coordinate().SetValue(0.3, 0.2)
slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
slider_rep.GetPoint2Coordinate().SetValue(0.7, 0.2)
slider_rep.SetSliderLength(0.02)
slider_rep.SetSliderWidth(0.03)
slider_rep.SetEndCapLength(0.01)
slider_rep.SetEndCapWidth(0.03)
slider_rep.SetTubeWidth(0.005)
slider_rep.SetLabelFormat("%3.0lf")
slider_rep.SetTitleHeight(0.02)
slider_rep.SetLabelHeight(0.02)

# Set the color of the slider to black
slider_rep.GetSliderProperty().SetColor(0, 0, 0)
# Set the color of the slider rail (entire slider) to black
slider_rep.GetTubeProperty().SetColor(0, 0, 0)

# The slider (see https://vtk.org/doc/nightly/html/classvtkSliderWidget.html):
slider = vtk.vtkSliderWidget()
slider.SetInteractor(render_window_interactor)
slider.SetRepresentation(slider_rep)
slider.KeyPressActivationOff()
slider.SetAnimationModeToAnimate()
slider.SetEnabled(True)

# Define what to do if the slider value changed:
def processEndInteractionEvent(obj, event):
    value2 = int(obj.GetRepresentation().GetValue())
    contour2.SetValue(0, value2)

slider.AddObserver("InteractionEvent", processEndInteractionEvent)

# # Add 2D axes using vtkAxisActor2D
# axis_actor_x = vtk.vtkAxisActor2D()
# axis_actor_x.SetPoint1(0, -40, 0)
# axis_actor_x.SetPoint2(20, 0)
# axis_actor_x.SetNumberOfLabels(6)
# axis_actor_x.SetLabelFormat("%4.0f")
# axis_actor_x.SetTitle("X Axis")

# axis_actor_y = vtk.vtkAxisActor2D()
# axis_actor_y.SetPoint1(0, -40)
# axis_actor_y.SetPoint2(0, 20)
# axis_actor_y.SetNumberOfLabels(6)
# axis_actor_y.SetLabelFormat("%4.0f")
# axis_actor_y.SetTitle("Y Axis")

# axis_actor_z = vtk.vtkAxisActor2D()
# axis_actor_z.SetPoint1(0, 0)
# axis_actor_z.SetPoint2(20, 0)
# axis_actor_z.SetNumberOfLabels(6)
# axis_actor_z.SetLabelFormat("%4.0f")
# axis_actor_z.SetTitle("Z Axis")
# # axis_actor_z.SetAxisLabelTextProperty(axis_actor_z.GetTitleTextProperty())  # Use the same property for axis labels

# # Add the axes to the renderer
# renderer.AddActor(axis_actor_x)
# renderer.AddActor(axis_actor_y)
# renderer.AddActor(axis_actor_z)

# # Add axes
# axes = vtk.vtkAxesActor()
# axes.SetTotalLength(30, 60, 60)
# axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
# axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
# axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()

# # Add the axes to the renderer
# renderer.AddActor(axes)

# # Add grid axes with ticks
# axes = vtk.vtkCubeAxesActor()
# # axes.SetInputData(grid)
# axes.SetXTitle("X")
# axes.SetYTitle("Y")
# axes.SetZTitle("Z")
# axes.GetXAxesGridlinesProperty().SetColor(0, 0, 0)
# axes.GetYAxesGridlinesProperty().SetColor(0, 0, 0)
# axes.GetZAxesGridlinesProperty().SetColor(0, 0, 0)
# axes.GetXAxesLinesProperty().SetColor(0, 0, 0)
# axes.GetYAxesLinesProperty().SetColor(0, 0, 0)
# axes.GetZAxesLinesProperty().SetColor(0, 0, 0)
# # axes.SetGridLineLocation(vtk.VTK_GRID_LINES_FURTHEST)
# axes.SetFlyModeToStaticEdges()
# axes.SetTickLocationToBoth()
# axes.SetCamera(renderer.GetActiveCamera())
# axes.PickableOff()

# # Add the axes to the renderer
# renderer.AddActor(axes)

# Set camera position
renderer.GetActiveCamera().Azimuth(30)
renderer.GetActiveCamera().Elevation(30)

# Reset camera and render
renderer.ResetCamera()
render_window.Render()

# Start the interactive visualization
render_window_interactor.Start()

#%%

# %%