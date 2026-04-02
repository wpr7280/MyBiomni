# Bioimaging

生物成像工具集。

## 可用工具

- **split_modalities**: Split a 4D NIfTI file into separate modality files for nnUNet processing. Handle
- **prepare_input_for_nnunet**: Prepare input data for nnUNet by handling both 4D and pre-split modality files
- **segment_with_nn_unet**: Segment images using nnUNet with proper environment setup. Supports brain tumor
- **create_segmentation_visualization**: Create and save visualization of segmentation results using nilearn. Generates o
- **quick_rigid_registration**: Perform rigid image registration between two medical images using SimpleITK. Rig
- **quick_affine_registration**: Perform affine image registration between two medical images using SimpleITK. Af
- **quick_deformable_registration**: Perform deformable (B-spline) image registration between two medical images usin
- **batch_register_images**: Perform batch registration of multiple images to a single reference image. Autom
- **calculate_similarity_metrics**: Calculate similarity metrics between two medical images. Supports mutual informa
- **create_registration_visualization**: Create visualization plots for registration results. Generates comparison plots

## 使用示例

调用 `split_modalities` 进行生物成像相关分析。
