import datetime
import io
import numpy as np
from sklearn.neighbors import KDTree


class VoiceRecognition():
    def __init__(self, calibration_vectors_dict):
        calibration_vectors = []
        for name in calibration_vectors_dict:
            calibration_vectors += calibration_vectors_dict[name]
        self.kd_tree = KDTree(np.array(calibration_vectors))

    def predict(self, voice_vector):
        dist, ind = self.kd_tree.query([voice_vector], k=2)
        ind_1 = ind[0][0]
        ind_2 = ind[0][1]
        dist_1 = dist[0][0]
        dist_2 = dist[0][1]
        if abs(dist_1 - dist_2) <= 0.5:
            return 'Suggested: ' + self.all_names[ind_1] + ' ' + self.all_names[ind_2]
        if dist_1 <= 10:
            return self.all_names[ind_1]
        return 'Suggested: ' + self.all_names[ind_1]
