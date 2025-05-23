# Solar Annotator
[![CodeFactor](https://www.codefactor.io/repository/github/jmbhughes/solarannotator/badge)](https://www.codefactor.io/repository/github/jmbhughes/solarannotator)
[![PyPI version](https://badge.fury.io/py/solarannotator.svg)](https://badge.fury.io/py/solarannotator)
[![DOI](https://zenodo.org/badge/286337290.svg)](https://zenodo.org/badge/latestdoi/286337290)
[![CI](https://github.com/jmbhughes/solarannotator/actions/workflows/ci.yaml/badge.svg?event=pull_request)](https://github.com/jmbhughes/solarannotator/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/jmbhughes/solarannotator/graph/badge.svg?token=3YGLITGX6L)](https://codecov.io/gh/jmbhughes/solarannotator)

A tool for annotating solar images with themes. 
![](screenshot.png)

## Install
It's best to install in a clean virtual environment to avoid package conflicts or incorrect versions. Below are the instructions for setting up a new virtual environment using python.

On a Mac or Linux machine:
```
python -m venv venv
source venv/bin/activate
pip install solarannotator
```

On a Windows machine:
```
py -m venv venv
.\venv\Scripts\activate
py -m pip install solarannotator
```

For more details [visit the Packaging guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).


For setting up an environment using conda - not necessary, but an alternative method:
```
conda env create -f environment.yml
```

## Running and usage
Execute from the terminal after installing by running inside your virtual environment.
```SolarAnnotator```

On the left hand side, you will see a preview that can be maniuplated with the controls below. 
It allows for viewing different SUVI channels with different configurations, e.g. one color versus three color. 
The preview controls allow you to select the minimum and maximum percentile shown as well as scale
the image by raising all pixels to the selected power.

You interact by drawing on the preview image to create new regions in the thematic map. You can also
relabel those patches by left-clicking in the thematic map with a new theme selected. Finally, you can see
boundaries of regions from the thematic map back in the preview image by right clicking the thematic map. 

Updates [2025-05-14]:
A few updates have been implemented into the code base, these includes: 

 - Ability to load data from a local directory 
 - Ability to select the satellite to pull SUVI data for (both for local and remote access)

## Future
This tool is still under development. There are many features coming. 
- [x] Ability to scale a single color image
- [x] Ability to scale in a three color image   
- [x] Right click on a region in the thematic map and see its boundary in the preview
- [x] Left click on a region in the thematic map to re-annotate all the contiguous pixels
- [x] Undo annotations
- [x] Differentiate save and save as
- [x] Add color legend to radio buttons
- [ ] Redo annotations, after ctrl-z
- [ ] Overlay HEK and other pre-determined annotations
- [ ] Multiple normalization options
- [ ] Robustify the thematic map io for better metadata passing, also use SunPy maps
- [ ] Add a help guide
- [x] Add an ability to load a template when you create a new date
