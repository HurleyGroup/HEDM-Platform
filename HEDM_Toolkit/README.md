---

# HEDM-Toolkit

HEDM-Toolkit is a comprehensive tool designed to integrate major HEDM resources available in the market. Its main objective is to streamline the pre-processing, intermediate processing, and post-processing steps of HEDM data. This toolkit was developed from the perspective of an experienced user, aiming to address the inconsistency of data standards across different synchrotron radiation sources. It facilitates users in comparing the strengths and weaknesses of mainstream software. One of the most significant features of this toolkit is the integration of AI capabilities (currently utilizing ilastik; future upgrades may incorporate or extend to deep learning). This aids in tackling challenging issues, especially AI-enhanced processing of data characterized by relatively high strain, streak-like patterns, and highly overlapping data.

<img src="data/image_test.png" alt="Test_image" width="200"/>

Currently, the toolkit amalgamates and builds upon various open-source software, including HEXRD, ImageD11, HEXOMAP, and ilastik. The corresponding links are:
- [HEXRD](https://github.com/HEXRD)
- [ImageD11](https://github.com/FABLE-3DXRD/ImageD11)
- [HEXOMAP](https://github.com/HeLiuCMU/HEXOMAP)
- [ilastik](https://www.ilastik.org/)

## Prerequisites
Before installing HEDM-Toolkit, you must install HEXRD, ImageD11, and ilastik (advanced usage; optional, can be skipped if not needed). For installation instructions, please refer to the respective URLs provided above. It's recommended to create a conda environment, e.g., `HEDM_Toolkit`.

## Installing HEDM-Toolkit
You can easily install the HEDM-Toolkit using pip:
```
pip install HEDM-Toolkit
```

## Getting Started

### Demo Setup
To start with the toolkit, first, copy the demo folder for testing purposes. Navigate to the working directory where you wish to process data and execute the `copy_demo` command within the `HEDM_Toolkit` environment. Upon execution, you'll notice the addition of several files in your directory, including:
```
config.yml
nugget_2_frames_for_test.h5
nugget_layer0_det0_50bg_ilastik_proc_t1.flt
nugget_layer0_det0_50bg_t1.flt
nugget_layer0_det0_50bg.par
```
**Note**: Due to the need for manual completion of the ilastik project file within the ilastik visual interface, and the large size of the project file making it unsuitable for packaging within this toolkit, users are required to export it on their own and place it in the appropriate directory. Necessary paths should be updated in the `config.yml` file accordingly.

### Testing Main Features
- **Standardizing Original Files**: 
  ```
  HEDM_Toolkit stand config.yml
  ```
  
- **Background Noise Reduction on Standardized Files**: Perform pixel-based median background noise reduction.
  ```
  HEDM_Toolkit sub config.yml
  ```
  
- **Machine Learning Processing**: Process the noise-reduced files through machine learning to extract key spots information. Note: Manual extraction of *.ilp files from ilastik output is required.
  ```
  HEDM_Toolkit ilastik config.yml
  ```
  
- **Format Conversion**: Convert files processed in steps 'b' or 'c' for subsequent HEDM software import and calibration.
  ```
  HEDM_Toolkit hedm_formats config.yml
  ```

- **Preparation for testing Indexing Grains**: As the original files are quite large, previous steps utilized a slice file with only 2 frames for testing. Therefore, before proceeding to the next step of indexing grains, it's necessary to execute the `copy_demo` command again to replace the earlier generated .flt file with only two frames.
  ```
  copy_demo
  ```

- **Index Grains and Fit**: Test to find grains and fit to obtain information like strain tensor, position, orientation, etc.
  ```
  HEDM_Toolkit ff_HEDM_process config.yml
  ```

### Additional Useful Features
(Description of other features can be added here)

---

For any questions, please contact ytian37@jhu.edu/ytian6688@hotmail.com or rhurley6@jhu.edu.

License: HEDM-Toolkit is distributed under the terms of the BSD 3-Clause license. All new contributions must be made under this license.

This software package was developed within Prof. Ryan Hurley's research group at Johns Hopkins University (JHU). Author: Ye Tian.

---