import numpy as np
from sklearn.neighbors import KDTree


class VoiceRecognition():
    def __init__(self, calibration_vectors_dict):
        calibration_vectors = []
        self.all_names = []
        for name in calibration_vectors_dict:
            self.all_names.append(name)
            calibration_vectors += calibration_vectors_dict[name]
        self.kd_tree = KDTree(np.array(calibration_vectors))

    def predict(self, voice_vector):
        dist, ind = self.kd_tree.query([voice_vector])
        ind_1 = ind[0][0]
        dist_1 = dist[0][0]
        if ind_1 % 2 == 0:
            ind_1 = ind_1 // 2
        else:
            ind_1 = (ind_1 - 1) // 2
        if dist_1 <= 10:
            return self.all_names[ind_1]
        return 'Suggested: ' + self.all_names[ind_1]
