# Unreal Editor BEDLAM2 Asset Filesystem Hierarchy

## BEDLAM2 Core
```
UE_5.3/Engine/Content/PS/Bedlam/Core/
.
├── BE_CameraOperator.uasset
├── BE_CineCameraActor_Blueprint.uasset
├── BE_GroundTruthLogger.uasset
├── Camera
│   └── ShakeVariations
│       ├── BE_CameraShake_HighFrequency
│       │   ├── BE_CameraShake_HighFrequency_000.uasset
│       │   ├── ...
│       │   └── BE_CameraShake_HighFrequency_249.uasset
│       └── BE_CameraShake_LowFrequency
│           ├── BE_CameraShake_LowFrequency_000.uasset
│           ├── ...
│           └── BE_CameraShake_LowFrequency_249.uasset
├── EditorScripting
│   └── BEDLAM.uasset
├── LICENSE.md
├── Materials
│   ├── BE_ClothingOverlayActor.uasset
│   ├── Hair
│   │   ├── MI_Hair_0.uasset
│   │   ├── MI_Hair_1.uasset
│   │   ├── MI_Hair_2.uasset
│   │   ├── MI_Hair_3.uasset
│   │   ├── MI_Hair_30.uasset
│   │   ├── MI_Hair_33.uasset
│   │   ├── MI_Hair_36.uasset
│   │   ├── MI_Hair_4.uasset
│   │   ├── MI_Hair_5.uasset
│   │   ├── MI_Hair_6.uasset
│   │   ├── MI_Hair_7.uasset
│   │   ├── MI_Hair_8.uasset
│   │   ├── MI_Hair_9.uasset
│   │   ├── MI_Hair_gray50.uasset
│   │   └── M_Hair.uasset
│   ├── LightProbe
│   │   ├── BE_LightProbe.uasset
│   │   ├── BE_LightProbe_Black.uasset
│   │   ├── BE_LightProbe_Chrome.uasset
│   │   ├── BE_LightProbe_Gray.uasset
│   │   ├── BE_LightProbe_White.uasset
│   │   ├── BE_Skin1.uasset
│   │   └── BE_Skin6.uasset
│   ├── M_Clothing.uasset
│   ├── M_SMPLX.uasset
│   ├── M_SMPLX_Clothing.uasset
│   ├── M_SMPLX_Hidden.uasset
│   ├── M_SMPLX_White.uasset
│   ├── MovieRenderQueue
│   │   └── MovieRenderQueue_CameraNormal.uasset
│   └── Textures
│       ├── Meshcapade_CC_BY-NC_4_0
│       │   ├── SMPLX_eye.uasset
│       │   └── skin_m_white_01_ALB.uasset
│       ├── T_rp_aaron_posed_002_texture_01_diffuse.uasset
│       ├── T_rp_aaron_posed_002_texture_01_normal.uasset
│       └── rp_aaron_posed_002_texture_01.uasset
├── MovieRenderQueue
│   └── MRQ_Template.uasset
├── Python
│   ├── create_level_sequences_csv.py
│   ├── create_movie_render_queue.py
│   ├── render_movie_render_queue.py
│   ├── render_movie_render_queue_batch.py
│   ├── render_status.py
│   └── tools
│       ├── create_camerashake_variations.py
│       ├── export_stage_locations.py
│       └── export_vcam.py
├── README.md
├── SMPLX
│   ├── smplx_lh_n.uasset
│   └── smplx_lh_n_abc.uasset
```

## SMPL-X Animated Bodies
Assets ending with `0000` denote body in static T-pose which is needed for generating hair groom bindings for individual head shapes.

```
UE_5.3/Engine/Content/PS/Bedlam/SMPLX_LH
├── it_4001_XL
│   ├── it_4001_XL_0000.uasset
│   ├── it_4001_XL_2400.uasset
│   ├── it_4001_XL_2403.uasset
│   └── it_4001_XL_2404.uasset
├── ...
```

## SMPL-X Imported FBX Animations
Needed for targeting specific body parts with camera.

```
UE_5.3/Engine/Content/PS/Bedlam/SMPLX_LH_animations
├── it_4001_XL
│   ├── it_4001_XL_2400.uasset
│   ├── it_4001_XL_2400_Anim.uasset
│   ├── it_4001_XL_2400_PhysicsAsset.uasset
│   ├── it_4001_XL_2400_Skeleton.uasset
│   ├── ...
├── ...
```

## Body Materials/Textures
```
UE_5.3\Engine\Content\PS\Meshcapade\SMPLX
├── M_SMPLX_Clothing.uasset
├── M_SMPLX_Clothing_MOYO.uasset
├── Materials
│   ├── MI_SMPLX_NoHair_female.uasset
│   ├── MI_SMPLX_NoHair_female_clothing.uasset
│   ├── MI_SMPLX_NoHair_male.uasset
│   ├── MI_SMPLX_NoHair_male_clothing.uasset
│   ├── MI_moyo.uasset
│   ├── MI_moyo_skin_f_african_01b_ALB.uasset
│   ├── ...
│   ├── MI_skin_f_african_01b_ALB.uasset
│   ├── ...
│   └── MI_skin_m_white_07b_ALB.uasset
├── Outfits
│   ├── MI_moyo_outfit_0000.uasset
│   ├── ...
│   └── MI_moyo_outfit_0021.uasset
└── Textures
    ├── Female_Bottom_ALB_0001.uasset
    ├── ...
    ├── Male_Top_ALB_0016.uasset
    └── bald
        ├── skin_f_african_01b_ALB.uasset
        ├── ...
        └── skin_m_white_07b_ALB.uasset
```

## Clothing Simulation/Materials/Textures
```
UE_5.3/Engine/Content/PS/Bedlam/Clothing/
├── Materials
│   ├── gr_aaron_009_2XL
│   │   ├── MI_gr_aaron_009_2XL_texture_10.uasset
│   │   ├── ...
│   │   ├── T_gr_aaron_009_2XL_texture_01_diffuse.uasset
│   │   ├── T_gr_aaron_009_2XL_texture_01_normal.uasset
│   │   ├── ...
│   │   ├── T_gr_aaron_009_2XL_texture_10_diffuse.uasset
│   │   └── T_gr_aaron_009_2XL_texture_10_normal.uasset
│   ├── ...
├── it_4001_XL
│   ├── it_4001_XL_2400_clo.uasset
│   ├── it_4001_XL_2403_clo.uasset
│   └── it_4001_XL_2404_clo.uasset
├── ...
```

## HDRI
```
UE_5.3/Engine/Content/PS/Bedlam/HDRI/
└── 8k
    ├── abandoned_church_8k.uasset
    ├── ...
    └── zhengyang_gate_8k.uasset
```

## Hair
```
UE_5.3/Engine/Content/PS/Bedlam/Hair/
└── VineFX
    ├── Bindings
    │   └── GeometryCache
    │       ├── it_4001_XL
    │       │   ├── vinefx_groom_01-1_curly-M_it_4001_XL.uasset
    │       │   ├── vinefx_groom_01-2_curly-M_it_4001_XL.uasset
    │       │   ├── ...
    │       │   └── vinefx_groom_20-2_low-afro-F_it_4001_XL.uasset
    │       ├── ...
    ├── vinefx_groom_01-1_curly-M.uasset
    ├── vinefx_groom_01-2_curly-M.uasset
    ├── ...
    └── vinefx_groom_20-2_low-afro-F.uasset
```

## Shoes
```
UE_5.3/Engine/Content/PS/Bedlam/Shoes/
├── Materials
│   ├── shoe_gso_000
│   │   ├── MI_skin_f_african_01b_ALB_shoe_gso_000.uasset
│   │   ├── ...
│   │   └── MI_skin_m_white_07b_ALB_shoe_gso_000.uasset
│   ├── ...
│   └── shoe_gso_254
│       ├── MI_skin_f_african_01b_ALB_shoe_gso_254.uasset
│       ├── ...
│       └── MI_skin_m_white_07b_ALB_shoe_gso_254.uasset
└── Textures
    ├── shoe_gso_000
    │   ├── T_shoe_gso_000_color.uasset
    │   ├── T_shoe_gso_000_displacement.uasset
    │   └── T_shoe_gso_000_normal.uasset
    ├── ...
    └── shoe_gso_254
        ├── T_shoe_gso_254_color.uasset
        ├── T_shoe_gso_254_displacement.uasset
        └── T_shoe_gso_254_normal.uasset

```
