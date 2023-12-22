import scipy.io as spio

lib = spio.loadmat('master_program\Inputs\covis_bathy_2019b.mat')

print(type(lib["covis"]["grid"]))

# print(lib["covis"]["grid"]["x"])