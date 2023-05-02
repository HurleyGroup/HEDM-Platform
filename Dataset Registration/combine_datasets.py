# import modules from orix (python-MTEX) and hexrd
from diffpy.structure import Lattice, Structure
import matplotlib.pyplot as plt
import numpy as np
from orix.crystal_map import Phase
from orix.quaternion import Orientation, Rotation, symmetry
from orix.vector import AxAngle, Miller, Vector3d
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.pyplot import figure
from hexrd import rotations as rot
from hexrd import matrixutil as mutil

# Position to centroids from FF to NF
def ff_pos_to_Centroids(x):
    pos_0,pos_1,pos_2 = x['t_vec_c[0]':'t_vec_c[2]'].to_numpy()
    Centroids_0_ff = -pos_0*1000+ 503.06019   # y
    Centroids_1_ff = -pos_2*1000+439.170933   # x
    Centroids_2_ff =  pos_1*1000+ 107.93238   # z
    return Centroids_0_ff, Centroids_1_ff, Centroids_2_ff

#####################
# # The SN OR in angle_au_ep function has been verified by PTCLab calculation
# #PTCLab calculation matrix
# au_matrix_PTC = np.identity(3)
# ep_V1_matrix_PTC = np.array([[0.70711, 0, -0.70711],[0.40825, -0.8165, 0.40825],[-0.57735, -0.57735, -0.57735]])
# au_matrix_PTC_ori = Orientation.from_matrix(au_matrix_PTC)
# ep_V1_matrix_PTC_ori = Orientation.from_matrix(ep_V1_matrix_PTC)
#####################
def angle_au_ep(expMap_a,expMap_e):
    
    expMap_a = expMap_a['exp_map_c[0]':'exp_map_c[2]'].to_numpy().astype(float)
    expMap_e = expMap_e['exp_map_c[0]':'exp_map_c[2]'].to_numpy().astype(float)
    
    # Specify two crystal structures and symmetries
    phase1 = Phase(point_group="m-3m",structure=Structure(lattice=Lattice(3.58, 3.58, 3.58, 90, 90, 90)),)
    phase2 = Phase(point_group="6/mmm",structure=Structure(lattice=Lattice(2.54, 2.54, 4.1, 90, 90, 120)),)
    
    ### Parallel planes
    vec_2 = Miller(hkil=[[0, 0, 0, 2]], phase=phase2) # epsilon-martensite (0, 0, 0, 1)
    #Turn exponential map into an orientation matrix
    Ori_e=rot.rotMatOfExpMap(expMap_e)
    o_e = Orientation.from_matrix(Ori_e)

    vec_1 = Miller(hkl=[[1, 1, 1],[-1, 1, 1],[1, 1, -1],[1, -1, 1]], phase=phase1) # austenite (1, 1, 1)
    #Turn exponential map into an orientation matrix
    Ori_a=rot.rotMatOfExpMap(expMap_a)
    o_a = Orientation.from_matrix(Ori_a)

    v_1_ori = Vector3d(~o_a * vec_1)
    v_2_ori = Vector3d(~o_e * vec_2)

    ang_1 = v_1_ori.unit
    ang_2 = v_2_ori.unit
    comp_1 = abs(ang_1.dot(ang_2)) #cos
    angle_radians_1 = np.arccos(comp_1)
    angle_degrees_1 = np.degrees(angle_radians_1)

    # Find the smallest angle
    min_angle_plane = np.min(angle_degrees_1)
    
    ### Parallel directions
    vec_4 = Miller(UVTW=[[1, 1, -2, 0]], phase=phase2) # epsilon-martensite [1, 1, -2, 0]
    vec_3 = Miller(uvw=[[1, -1, 0], [-1, 0, 1], [0, -1, 1],[1, 1, 0], [1, 0 ,1], [0, 1, 1]], phase=phase1) # austenite [1, 1, 0]
  
    v_3_ori = Vector3d(~o_a * vec_3)
    v_4_ori = Vector3d(~o_e * vec_4)

    ang_3 = v_3_ori.unit
    ang_4 = v_4_ori.unit
    comp_2 = abs(ang_3.dot(ang_4)) #cos
    angle_radians_2 = np.arccos(comp_2)
    angle_degrees_2 = np.degrees(angle_radians_2)

    # Find the smallest angle
    min_angle_direction = np.min(angle_degrees_2)

    max_angle = max(min_angle_plane, min_angle_direction)
    
    return max_angle

def update_dataframe(df, df_ep, grain_index, filtered_indices):
    df.loc[filtered_indices, 'Transformed_epsilon'] = 1
    df.loc[filtered_indices, 'grain_id_ep'] = df_ep.iloc[grain_index]['# grain']
    df.loc[filtered_indices, 'completeness_ep'] = df_ep.iloc[grain_index]['completeness']
    df.loc[filtered_indices, 'chi^2_ep'] = df_ep.iloc[grain_index]['chi^2']
    df.loc[filtered_indices, 'exp_map_c0_ep'] = df_ep.iloc[grain_index]['exp_map_c[0]']
    df.loc[filtered_indices, 'exp_map_c1_ep'] = df_ep.iloc[grain_index]['exp_map_c[1]']
    df.loc[filtered_indices, 'exp_map_c2_ep'] = df_ep.iloc[grain_index]['exp_map_c[2]']
    df.loc[filtered_indices, 'Centroids_0_ep'] = df_ep.iloc[grain_index]['Centroids_0_ep']
    df.loc[filtered_indices, 'Centroids_1_ep'] = df_ep.iloc[grain_index]['Centroids_1_ep']
    df.loc[filtered_indices, 'Centroids_2_ep'] = df_ep.iloc[grain_index]['Centroids_2_ep']
    df.loc[filtered_indices, ['strain_0_ep', 'strain_1_ep', 'strain_2_ep', 'strain_3_ep', 'strain_4_ep', 'strain_5_ep']] = [df_ep.iloc[grain_index]['ln(V_s)[0,0]':'ln(V_s)[0,1]']]
    return df

def combine_datasets_with_condition(df, df_ep, mis, layer, grain_size, deformation):
    for grain_index in range(df_ep.shape[0]):
        base_conditions = get_base_conditions(df, layer, grain_size, deformation)
        filter1_conditions = get_filter1_conditions(df, df_ep, grain_index, base_conditions)
        filtered_df = df[filter1_conditions].copy()

        filtered_df['mis_au_ep_temp'] = filtered_df.apply(angle_au_ep, expMap_e=df_ep.iloc[grain_index][['exp_map_c[0]', 'exp_map_c[1]', 'exp_map_c[2]']], axis=1)
        filter2_conditions = (filtered_df.mis_au_ep_temp < mis)
        filtered_indices = filtered_df[filter2_conditions].index

        df = update_dataframe(df, df_ep, grain_index, filtered_indices)
        print(grain_index)
    return df

def get_base_conditions(df, layer, grain_size, deformation):
    if layer == 0:
        Centroids_2_cond = (df.Centroids_2 >= 123.5)
    elif layer == 1:
        Centroids_2_cond = (df.Centroids_2 < 123.5) & (df.Centroids_2 >= 23.5)
    else:
        Centroids_2_cond = (df.Centroids_2 < 23.5)
    return (Centroids_2_cond) & (df.EquivalentDiameters >= grain_size) & (df.Deformation == deformation)

def get_filter1_conditions(df, df_ep, grain_index, base_conditions):
    return base_conditions \
           & (df_ep.iloc[grain_index]['Centroids_0_ep'] >= df.Centroids_0 - 80) & (df_ep.iloc[grain_index]['Centroids_0_ep'] <= df.Centroids_0 + 80) \
           & (df_ep.iloc[grain_index]['Centroids_1_ep'] >= df.Centroids_1 - 80) & (df_ep.iloc[grain_index]['Centroids_1_ep'] <= df.Centroids_1 + 80)

def main():
    df = df_nf_ff_overlap_combined_combine_dups.copy() # df austenite
    # Layer0
    layer = 0
    df_ep_layer0[['Centroids_0_ep','Centroids_1_ep','Centroids_2_ep']]=df_ep_layer0.apply(ff_pos_to_Centroids, axis=1, result_type ='expand')
    df_ep = df_ep_layer0.loc[(df_ep_layer0['chi^2']<0.025) & (df_ep_layer0.completeness>0.6)].reset_index(drop=True).copy()  # other completeness>0.9
    df = combine_datasets_with_condition(df, df_ep, mis, layer, grain_size, deformation)
    # Layer1
    layer = 1
    df_ep_layer1[['Centroids_0_ep','Centroids_1_ep','Centroids_2_ep']]=df_ep_layer1.apply(ff_pos_to_Centroids, axis=1, result_type ='expand')
    df_ep = df_ep_layer1.loc[(df_ep_layer1['chi^2']<0.025) & (df_ep_layer1.completeness>0.6)].reset_index(drop=True).copy()  # other completeness>0.9
    df = combine_datasets_with_condition(df, df_ep, mis, layer, grain_size, deformation)
    # Layer2
    layer = 2
    df_ep_layer2[['Centroids_0_ep','Centroids_1_ep','Centroids_2_ep']]=df_ep_layer2.apply(ff_pos_to_Centroids, axis=1, result_type ='expand')
    df_ep = df_ep_layer2.loc[(df_ep_layer2['chi^2']<0.025) & (df_ep_layer2.completeness>0.6)].reset_index(drop=True).copy()  # other completeness>0.9
    df = combine_datasets_with_condition(df, df_ep, mis, layer, grain_size, deformation)
    # Save fcc + hcp dataframe
    df.to_csv(df_output, sep='\t', encoding='utf-8', header='true',index=False)

if __name__ == '__main__':
    # Do not need to change
    mis = 10   # saved as a column in the dataframe
    grain_size = 5 # austenite grain size
    #########################
    # Variables to be change
    for deformation in [1]:  # [1, 2, 3, 4]
        if deformation == 1:
            folder_name = 's7'
        elif deformation == 2:
            folder_name = 's8'
        elif deformation == 3:
            folder_name = 's9'
        elif deformation == 4:
            folder_name = 's10'
        
        df_ep_layer0 = pd.read_fwf(f'/Users/yetian/Dropbox/My Mac (Ye’s MacBook Pro)/Desktop/APS_2021Feb_RAMS/sam3_ff_{folder_name}_fit_hcp_220120_layer0/grains.out')
        df_ep_layer1 = pd.read_fwf(f'/Users/yetian/Dropbox/My Mac (Ye’s MacBook Pro)/Desktop/APS_2021Feb_RAMS/sam3_ff_{folder_name}_fit_hcp_220120_layer1/grains.out') 
        df_ep_layer2 = pd.read_fwf(f'/Users/yetian/Dropbox/My Mac (Ye’s MacBook Pro)/Desktop/APS_2021Feb_RAMS/sam3_ff_{folder_name}_fit_hcp_220120_layer2/grains.out')
        df_nf_ff_overlap_combined_combine_dups = pd.read_csv(f'/Users/yetian/Dropbox/My Mac (Ye’s MacBook Pro)/Desktop/APS_2021Feb_RAMS/Pre_CSV_files/df_nf_ff_overlap_combined_{folder_name}_combine_dups.csv', sep='\t', encoding='utf-8')
        df_output = f'/Users/yetian/Dropbox/My Mac (Ye’s MacBook Pro)/Desktop/APS_2021Feb_RAMS/Pre_CSV_files/df_fcc_hcp_combined_{folder_name}_new.csv'
        main()
