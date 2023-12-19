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

def limit(v, X, Y, Z, xmin, xmax, ymin, ymax, zmin, zmax):
    if len(v.shape) == 3:
        m = (X >= xmin) & (X <= xmax) & (Y >= ymin) & (Y <= ymax) & (Z >= zmin) & (Z <= zmax)
        v[~m] = np.nan
    elif len(v.shape) == 2:
        m = (X >= xmin) & (X <= xmax) & (Y >= ymin) & (Y <= ymax)
        v[~m] = np.nan
    return v

v = limit(v, xg, yg, zg, -20, 1, -8, 12, -2, 15)
zb = limit(zb, xb, yb, zb, -20, 1, -8, 12, -2, 15)


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
grid.GetPointData().SetScalars(colors)

# Create VTK mapper and actor for the first dataset
mapper1 = vtk.vtkDataSetMapper()
mapper1.SetInputData(grid)
mapper1.SetScalarRange(np.nanmin(zb), np.nanmax(zb))

# Create a color transfer function
color_function = vtk.vtkColorTransferFunction()
color_function.SetColorSpaceToDiverging()
color_function.AddRGBPoint(np.nanmin(zb), 0.0, 0.0, 0.5)  # Dark blue
color_function.AddRGBPoint(np.nanmax(zb), 0.5, 0.0, 0.0)  # Dark red

mapper1.SetLookupTable(color_function)

actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

# Create a contour filter
contour_filter = vtk.vtkContourFilter()
contour_filter.SetInputData(grid)
contour_filter.GenerateValues(30, np.nanmin(zb), np.nanmax(zb))  # Adjust the number of contours as needed

# Create mapper for contour lines
contour_mapper = vtk.vtkPolyDataMapper()
contour_mapper.SetInputConnection(contour_filter.GetOutputPort())

# Create actor for contour lines
contour_actor = vtk.vtkActor()
contour_actor.SetMapper(contour_mapper)
contour_actor.GetProperty().SetColor(0.4, 0.4, 0.4)  # Set contour line color

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
vtk_data2.SetOrigin(0 ,20, -40)

# Create a VTK contour filter
contour2 = vtk.vtkContourFilter()
contour2.SetInputData(vtk_data2)
contour2.SetValue(0, -60)

# Create a mapper for the second dataset
mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(contour2.GetOutputPort())

# Create an actor for the second dataset
actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)
actor2.GetProperty().SetOpacity(0.1)
actor2.GetProperty().SetColor(77/255, 153/255, 204/255)

# Create a VTK contour filter
contour3 = vtk.vtkContourFilter()
contour3.SetInputData(vtk_data2)
contour3.SetValue(0, -50)

# Create a mapper for the second dataset
mapper3 = vtk.vtkPolyDataMapper()
mapper3.SetInputConnection(contour3.GetOutputPort())

actor3 = vtk.vtkActor()
actor3.SetMapper(mapper3)
actor3.GetProperty().SetOpacity(0.2)
actor3.GetProperty().SetColor(128/255, 77/255, 128/255)

# Create a VTK contour filter
contour4 = vtk.vtkContourFilter()
contour4.SetInputData(vtk_data2)
contour4.SetValue(0, -40)

# Create a mapper for the second dataset
mapper4 = vtk.vtkPolyDataMapper()
mapper4.SetInputConnection(contour4.GetOutputPort())

actor4 = vtk.vtkActor()
actor4.SetMapper(mapper4)
actor4.GetProperty().SetOpacity(0.3)
actor4.GetProperty().SetColor(153/255 ,5/255, 13/255)

# Create a line source
line_source = vtk.vtkLineSource()
line_source.SetPoint1(0, 0, 0)
line_source.SetPoint2(4.2, 0, 0)

# Create a mapper
mapper5 = vtk.vtkPolyDataMapper()
mapper5.SetInputConnection(line_source.GetOutputPort())

# Create an actor
actor5 = vtk.vtkActor()
actor5.SetMapper(mapper5)
actor5.GetProperty().SetColor(1, 1, 0)  # Yellow color
actor5.GetProperty().SetLineWidth(4)   # Set line width


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
renderer.AddActor(actor3)
renderer.AddActor(actor4)
renderer.AddActor(actor5)
renderer.AddActor(contour_actor)

# # Create a slider to set the isovalue
# slider_rep = vtk.vtkSliderRepresentation2D()
# slider_rep.SetMinimumValue(np.nanmin(v))
# slider_rep.SetMaximumValue(np.nanmax(v))
# slider_rep.SetValue((np.nanmax(v) + np.nanmin(v)) / 2)
# slider_rep.SetTitleText("Contour")
# slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
# slider_rep.GetPoint1Coordinate().SetValue(0.3, 0.2)
# slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
# slider_rep.GetPoint2Coordinate().SetValue(0.7, 0.2)
# slider_rep.SetSliderLength(0.02)
# slider_rep.SetSliderWidth(0.03)
# slider_rep.SetEndCapLength(0.01)
# slider_rep.SetEndCapWidth(0.03)
# slider_rep.SetTubeWidth(0.005)
# slider_rep.SetLabelFormat("%3.0lf")
# slider_rep.SetTitleHeight(0.02)
# slider_rep.SetLabelHeight(0.02)

# # Set the color of the slider to black
# slider_rep.GetSliderProperty().SetColor(0, 0, 0)
# # Set the color of the slider rail (entire slider) to black
# slider_rep.GetTubeProperty().SetColor(0, 0, 0)

# # The slider (see https://vtk.org/doc/nightly/html/classvtkSliderWidget.html):
# slider = vtk.vtkSliderWidget()
# slider.SetInteractor(render_window_interactor)
# slider.SetRepresentation(slider_rep)
# slider.KeyPressActivationOff()
# slider.SetAnimationModeToAnimate()
# slider.SetEnabled(True)

# # Define what to do if the slider value changed:
# def processEndInteractionEvent(obj, event):
#     value2 = int(obj.GetRepresentation().GetValue())
#     contour2.SetValue(0, value2)

# slider.AddObserver("InteractionEvent", processEndInteractionEvent)

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

renderer.AddActor(axes)

renderer.GetActiveCamera().Azimuth(-55)
renderer.GetActiveCamera().Elevation(130)
renderer.GetActiveCamera().SetViewUp(1, 0, 0)

renderer.ResetCamera()
renderer.GetActiveCamera().Zoom(2.5)

# Add the axes to the renderer
renderer.AddActor(axes)

# Reset camera and render
render_window.Render()

# Start the interactive visualization
render_window_interactor.Start()

#%%

# %%