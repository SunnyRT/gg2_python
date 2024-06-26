# these are the imports you are likely to need
import numpy as np
from material import *
from source import *
from fake_source import *
from ct_phantom import *
from ct_lib import *
from scan_and_reconstruct import *
from create_dicom import *

# create object instances
material = Material()
source = Source()

p = ct_phantom(material.name, 256, 3)
s = fake_source(source.mev, 0.1, method='ideal')
s_1 = source.photon('80kVp, 3mm Al')
# convert phantom where each pixel stores material index to attenuation coefficient mu at the peak energy value
peak_energy = 0.07 # MeV
p_mu = phantom_mu(p, material, peak_energy)

mas=10000
scale = 0.01
angles = [256]
photons = s * mas * (scale ** 2)

	# TODO: by YQ
	# create sinogram from phantom data, with received detector values
#for a in angles: 
    #sinogram = ct_scan(photons, material, p, scale, a, mas)
    #draw(sinogram)

y = scan_and_reconstruct(s, material, p, 0.01, 256, hounsfield=True)
#print(y)
print(y.max())
#y_1 = scan_and_reconstruct(s_1, material, p, 0.01, 256, hounsfield=True)

#soft_tissue
c = 0
w = 200
reconstruction = ((y - c)/w)*128 + 128

c = 3000
w = 200
reconstruction_1 = ((y - c)/w)*128 + 128

draw(y)

draw(reconstruction)

draw(reconstruction, caxis=[-100, 100])
draw(reconstruction_1, caxis=[-200, 200])



#draw(y_1)
#draw(y_1, caxis=[-1, 2])
#create_dicom(y, 'ct_data', 0.1)


def test_yq():
	"""Output the mean value of the scanned and reconstructed image of a simple disc with different materials 
	using an ideal source packet"""

	# initial conditions
	s = fake_source(source.mev, 0.1, method='ideal')
	mat_test = ["Water", "Soft Tissue", "Bone"]
	alphas = [0, 0.0001, 0.001, 0.1, 0.2, 0.4, 0.6, 0.8]
	results = np.empty(len(mat_test))
	
	# get the attenuation coefficient energy index for each material at 0.07MeV
	energy_idx = np.nonzero(material.mev==0.07)[0][0]
	mu = np.empty(len(mat_test))
	per_error = np.empty(len(mat_test))

	for (i,mat_name) in enumerate(mat_test):
		p =  ct_phantom(material.name, 256, 3)
		y = scan_and_reconstruct(s, material, p, 0.1, 256, alpha = 5)
		draw(y, caxis=[-1, 2])
		results[i] = np.mean(y[64:192, 64:192])
		print("measured attenuation coefficient for ", mat_name, " is ", results[i])

		mu[i] = material.coeff(mat_name)[energy_idx]
		per_error[i] = (results[i] - mu[i]) / mu[i] * 100
	
	f = open('results/test_yq_output.txt', mode='a')
	f.write(f'----------- \n')
	f.write(f'alpha = 5 \n')
	f.write(f'Detected mean attenuation coefficient for {mat_test} are {results}.\n')

	# assume ideal fake_source with peak at 0.07MeV
	f.write(f'Expected mean attenuation coefficient for {mat_test} are {mu}.\n') 
	# f.write(f'Expected mean attenuation coefficient for {mat_test} are [0.204, 0.194, 0.502]\n') # assume ideal fake_source peak at 0.07MeV
	f.write(f'Percentage error for {mat_test} are {per_error}%.\n')

	f.close()
	
#test_yq()

