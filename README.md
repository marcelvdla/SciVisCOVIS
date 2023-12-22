# SciVisCOVIS
Repository for the SVVR project on COVIS data

Members:

* Marcel van de Lagemaat (10886699)
* Jonathan Meeng (14074036)

# Python Setup

The necessary packages for this project are listed in the file requirements.txt, to make sure you have the right versions run the following:

```shell
pip install -r requirements.txt
```
# Run the code

The visualisations can be created by running the file `vtk_COVIS.py`. There are multiple options for running this code:
- Histogram

This shows the histogram of the backscatter frequencies for all data in the fullimaging folder and can be run with:
```shell
python3 vtk_COVIS.py hist
```

- Single imaging file

To show the visualisation of a single observation time run with:
``` shell
python3 vtk_COVIS.py show num
```
Where num is an integer for the data file, which for the data present has to be between 0 and 11. 

- Compare

To show the visualisation of more then one observation run with:
``` shell
python3 vtk_COVIS.py compare contour opacity plume_num_1 plume_num_2 
```
Where contour has to be an integer between 0 and 90, opacity a float between 0.0 and 1.0 and plume_num_x the data point you want in the visualisation. This can be any number of datapoints up to all the datapoints present in the data folder (so any value between 0 and 11)

- Animation

To show the animation of all observations run with:
``` shell
python3 vtk_COVIS.py animation contour opacity num_frames
```
Again contour has to be an integer between 0 and 90, opacity a float between 0.0 and 1.0. num_frames has to be an integer that determines the number of frames that the animation will have before pausing. 
For all visualisation modes, if any invalid values have been entered it will default back to set values, which will be printed to the terminal.

# Description of Codebase

Here we briefly describe relevant files to the project.

## `data`

Contains the data is stored that is used to create the visualisation. This is both the data for the seafloor bathymetry and the imaging data of the hydrothermal plumes. 

## `legacy`

Contains Python Notebooks that have been used for data exploration and the Matlab2Python folder where the Matlab code was used to recreate the original visualisation. 

## `results`

Contains the visualisations made during the project and are used in the final report. 

# References

(1) [SciVis Contest website](https://sciviscontest2024.github.io/) 

(2) [Bemis et al (2015): The path to COVIS: A review of acoustic imaging of hydrothermal flow regimes](https://www.sciencedirect.com/science/article/abs/pii/S0967064515002027?via%3Dihub) 

(3) [D. R. Palmer, P. A. Rona, and M. J. Mottl. 1986. Acoustic imaging of high-temperature hydrothermal plumes at seafloor spreading centers. The Journal of the Acoustical Society of America 80, 3 (09 1986)](https://pubs.aip.org/asa/jasa/article-abstract/80/3/888/680648/Acoustic-imaging-of-high-temperature-hydrothermal?redirectedFrom=fulltext)
