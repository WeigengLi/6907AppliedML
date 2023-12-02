import math
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm
import numpy as np
import argparse

from dataset.Datasets import EEGEyeNetDataset, MTLPupilDataset
# TODO: ADD COMMIT about possible models and instructions
from models.STL import EEGViT_pretrained, InceptionViT_pretrained, EEGViT_pretrained_hierachical
from models.MTL_pretrained import ViT_reconstruct
from models.ViT_reconstruct_v8 import ViT_reconstruct_v8
from models.ViT_reconstruct_v9 import ViT_reconstruct_v9
from models.ViT_reconstruct_v10 import ViT_reconstruct_v10
from models.ViT_reconstruct_v11 import ViT_reconstruct_v11
from models.ModelTrainer import STL_Trainer, MTL_RE_Trainer, MTL_PU_Trainer

# region Global Config
STL_STR = 'STL'
MTL_RE_STR = 'MTL_RE'
MTL_PU_STR = 'MTL_PU'

TASKS_HELP = {
    STL_STR: 'Single Task Learning: predict fixtion postion ((x,y) value) using EEG data ',
    MTL_RE_STR: 'Multi-Task Learning: STL with a subtask that reconstruct EEG data',
    MTL_PU_STR: 'Multi-Task Learning: STL with a subtask that predict pupil size'
}

TASKS_DATA = {
    STL_STR: EEGEyeNetDataset,
    MTL_RE_STR: EEGEyeNetDataset,
    MTL_PU_STR: MTLPupilDataset
}
TASKS_TRAINER = {
    STL_STR: STL_Trainer,
    MTL_RE_STR: MTL_RE_Trainer,
    MTL_PU_STR: MTL_PU_Trainer
}
# endregion

# region Task Config
DEFAULT_TASK = MTL_RE_STR
DEFAULT_MODEL = ViT_reconstruct_v8
NEW_DATA_PATH = False
NUM_ITER = 3
# endregion

# model names
MODEL_NAME = {
    'ViT_reconstruct_v8': ViT_reconstruct_v8,
    'ViT_reconstruct_v9': ViT_reconstruct_v9,
    'ViT_reconstruct_v10': ViT_reconstruct_v10,
    'ViT_reconstruct_v11': ViT_reconstruct_v11
}


def main():
    data_path = './dataset/Position_task_with_dots_synchronised_min.npz' if not NEW_DATA_PATH else NEW_DATA_PATH
    Dataset = TASKS_DATA[DEFAULT_TASK](data_path)
    for key, val in MODEL_NAME.items():
        for i in range(NUM_ITER):
            model = val()
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
            scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=6, gamma=0.1)
            mt = TASKS_TRAINER[DEFAULT_TASK](model, Dataset, optimizer, scheduler, batch_size=64, n_epoch=15,
                                             weight=100, Trainer_name=f'{key}_{str(i + 1)}')
            mt.run()


if __name__ == '__main__':
    main()