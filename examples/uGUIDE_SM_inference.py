#%%
import numpy as np
import pandas as pd

from uGUIDE.config_utils import create_config_uGUIDE, save_config_uGUIDE
from uGUIDE.data_utils import preprocess_data, postprocess_SM
from uGUIDE.inference import run_inference
from uGUIDE.estimation import estimate_microstructure

#%%
theta_train = pd.read_csv('simulations_SM_train_10000__f_Da_ODI_u0_u1.csv', header=None).values
x_train = pd.read_csv(f'simulations_SM_train_10000__S_snr_50.csv', header=None).values

bvals = np.loadtxt('bvals.bval')
theta_train, x_train = preprocess_data(theta_train, x_train, bvals,
                                       normalize=True)

#%%
prior = {'f': [0.0, 1.0],
         'Da': [0.1, 3.0],
         'ODI': [0.03, 0.95],
         'u0': [0.0, 1.0],
         'u1': [0.0, 1.0]}
prior_postprocessing = {'f': [0.0, 1.0],
                        'Da': [0.1, 3.0],
                        'ODI': [0.03, 0.95],
                        'De_par': [0.1, 3.0],
                        'De_perp': [0.1, 3.0]}
config = create_config_uGUIDE(microstructure_model_name='Standard_Model',
                              size_x=x_train.shape[1],
                              prior=prior,
                              prior_postprocessing=prior_postprocessing,
                              use_MLP=True,
                              nf_features=6,
                              max_epochs=200,
                              n_epochs_no_change=10,
                              nb_samples=50_000,
                              random_seed=1234)
save_config_uGUIDE(config, savefile='config_postprocessing.pkl')
print(f'Device used for computations: {config["device"]}')

#%%
run_inference(theta_train, x_train, config=config,
              plot_loss=True, load_state=False)

#%%
theta_test = pd.read_csv('simulations_SM_test_1000__f_Da_ODI_u0_u1.csv', header=None).values
x_test = pd.read_csv(f'simulations_SM_test_1000__S_snr_50.csv', header=None).values
theta_test, x_test = preprocess_data(theta_test, x_test, bvals, normalize=True)

#%%
# Without postprocessing
_ = estimate_microstructure(x_test[1,:], config, plot=True,
                            theta_gt=theta_test[1,:])

# %%
# With postprocessing
# Convert u0 and u1 to De_par and De_perp and plot results
_ = estimate_microstructure(x_test[1,:], config, postprocessing=postprocess_SM,
                            plot=True)

# %%
