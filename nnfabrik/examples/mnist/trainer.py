from typing import Dict, Tuple, Callable

import numpy as np
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.optim as optim


class ToyTrainer:
    def __init__(self, model, dataloaders, seed, epochs=5):

        self.model = model
        self.trainloader = dataloaders["train"]
        self.seed = seed
        self.epochs = epochs
        self.loss_fn = nn.NLLLoss()
        self.optimizer = optim.Adam(self.model.parameters())

    def train(self):
        if hasattr(tqdm, "_instances"):
            tqdm._instances.clear()  # To have tqdm output without line-breaks between steps
        torch.manual_seed(self.seed)
        accs = []
        for epoch in range(self.epochs):
            predicted_correct = 0
            total = 0
            for x, y in tqdm(self.trainloader):
                # forward:
                self.optimizer.zero_grad()
                x_flat = x.flatten(1, -1)  # treat the images as flat vectors
                y_hat = self.model(x_flat)
                loss = self.loss_fn(y_hat, y)
                # backward:
                loss.backward()
                self.optimizer.step()
                # keep track of accuracy:
                _, predicted = y_hat.max(1)
                predicted_correct += predicted.eq(y).sum().item()
                total += y.shape[0]
            accs.append(100.0 * predicted_correct / total)

        return accs[-1], (accs, self.epochs), self.model.state_dict()


def mnist_trainer_fn(
    model: torch.nn.Module,
    dataloaders: Dict,
    seed: Tuple,
    uid: Tuple,
    cb: Callable,
    **config
) -> Tuple[float, Dict, Dict]:
    """"
    Args:
        model (torch.nn.Module): initialized model to train
        data_loaders (dict): containing "train", "validation" and "test" data loaders
        seed (int): random seed
        uid (tuple): keys that uniquely identify this trainer call
        cb : callback function to ping the database and potentially save the checkpoint
    Returns:
        score: performance score of the model
        output: user specified validation object based on the 'stop function'
        model_state: the full state_dict() of the trained model
    """
    trainer = ToyTrainer(model, dataloaders, seed, epochs=config.get("epochs", 2))
    out = trainer.train()

    return out
