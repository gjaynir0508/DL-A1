# -*- coding: utf-8 -*-
"""DL A1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Gqu0J92pbP05HYzeYrA39mlSLUHBDjbL

# DL Assignment 1 Case Study - weight Initialization Techniques

Submitted by:

|   | Name | Roll No. |
|---|---|---|
| 1 | C. Rithesh Reddy | 160122771034 |
| 2 | G. Jayanth       | 160122771041 |
| 3 | J. Pavan Kumar   | 160122771045 |

## Importing required libraries and modules
"""

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Flatten, Conv2D, MaxPooling2D, Dropout, Normalization
from tensorflow.keras.initializers import Zeros, RandomNormal, GlorotUniform, HeNormal, LecunNormal, Orthogonal
from tensorflow.keras.datasets import mnist, fashion_mnist, cifar10, cifar100
from tensorflow.keras.datasets import california_housing
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

"""## Loading datasets"""

# Load datasets
def load_dataset(name):
    if name in ["MNIST", "Fashion-MNIST", "CIFAR-10", "CIFAR-100"]:
        datasets = {
            "MNIST": mnist.load_data(),
            "Fashion-MNIST": fashion_mnist.load_data(),
            "CIFAR-10": cifar10.load_data(),
            "CIFAR-100": cifar100.load_data()
        }
        (x_train, y_train), (x_test, y_test) = datasets[name]
        x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize data
        return (x_train, y_train), (x_test, y_test)
    elif name == "California Housing":
        (x_train, y_train), (x_test, y_test) = california_housing.load_data()
        normalizer = Normalization()
        normalizer.adapt(x_train)
        return (normalizer(x_train), y_train), (normalizer(x_test), y_test)

"""## Defining the weight initializers"""

# Different weight initializations
initializers = {
    "Zero Initialization": Zeros(),
    "Random Initialization": RandomNormal(mean=0.0, stddev=0.05),
    "Xavier Initialization": GlorotUniform(),
    "He Initialization": HeNormal(),
    "Lecun Initialization": LecunNormal(),
    "Orthogonal Initialization": Orthogonal()
}

"""## Functions to create different models

### MLP Classifier
"""

def create_mlp(input_shape, output_units, initializer, activation="softmax"):
    inputs = Input(shape=input_shape)
    x = Flatten()(inputs)
    x = Dense(256, activation='sigmoid', kernel_initializer=initializer)(x)
    x = Dense(128, activation='tanh', kernel_initializer=initializer)(x)
    outputs = Dense(output_units, activation=activation, kernel_initializer=initializer)(x)
    return Model(inputs, outputs)

"""### CNN"""

def create_cnn(input_shape, output_units, initializer, activation="softmax"):
    inputs = Input(shape=input_shape)
    x = Conv2D(32, (3, 3), activation='relu', kernel_initializer=initializer)(inputs)
    x = MaxPooling2D((2, 2))(x)
    x = Conv2D(64, (3, 3), activation='relu', kernel_initializer=initializer)(x)
    x = MaxPooling2D((2, 2))(x)
    x = Flatten()(x)
    x = Dense(128, activation='relu', kernel_initializer=initializer)(x)
    x = Dropout(0.5)(x)
    outputs = Dense(output_units, activation=activation, kernel_initializer=initializer)(x)
    return Model(inputs, outputs)

"""### MLP Regressor"""

def create_regression_model(input_shape, initializer):
    inputs = Input(shape=(input_shape,))
    x = Normalization()(inputs)  # Apply Normalization layer
    x = Dense(64, activation='relu', kernel_initializer=initializer)(x)
    x = Dense(32, activation='relu', kernel_initializer=initializer)(x)
    outputs = Dense(1, kernel_initializer=initializer)(x)
    return Model(inputs, outputs)

"""## Function to train a model given dataset and initializer"""

# Training function
def train_model(model, dataset_name, initializer_name, model_type, epochs=50):
    (x_train, y_train), (x_test, y_test) = load_dataset(dataset_name)

    loss_fn = 'sparse_categorical_crossentropy' if model_type != 'Regression' else 'mse'
    metrics = ['accuracy'] if model_type != 'Regression' else ['mae']
    model.compile(optimizer='adam', loss=loss_fn, metrics=metrics)

    model_dir = f'models/{model_type}/{dataset_name}/{initializer_name}/'
    os.makedirs(model_dir, exist_ok=True)
    checkpoint_path = os.path.join(model_dir, 'best_model.keras')

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint(filepath=checkpoint_path, save_best_only=True, monitor='val_loss')
    ]

    history = model.fit(x_train, y_train, epochs=epochs, batch_size=64, validation_data=(x_test, y_test), callbacks=callbacks, verbose=0)

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    return history.history, test_acc, test_loss

"""## Running experiments for all possible scenarios"""

# Run experiments
results = {}
for model_type in ["MLP", "CNN", "Regression"]:
    for dataset_name in ["MNIST", "Fashion-MNIST", "CIFAR-10", "CIFAR-100"] if model_type != "Regression" else ["California Housing"]:
        output_units = 10 if dataset_name in ["MNIST", "Fashion-MNIST", "CIFAR-10"] else 100 if dataset_name == "CIFAR-100" else 1
        activation = "softmax" if model_type != "Regression" else None

        for initializer_name, initializer in initializers.items():
            print(f"Training {model_type} on {dataset_name} with {initializer_name}...")

            if model_type == "MLP":
                model = create_mlp((28, 28) if "MNIST" in dataset_name else (32, 32, 3), output_units, initializer, activation)
            elif model_type == "CNN":
                model = create_cnn((28, 28, 1) if "MNIST" in dataset_name else (32, 32, 3), output_units, initializer, activation)
            else:
                model = create_regression_model(8, initializer)

            history, test_acc, test_loss = train_model(model, dataset_name, initializer_name, model_type)
            results[(model_type, dataset_name, initializer_name)] = {
                "history": history,
                "test_acc": test_acc,
                "test_loss": test_loss
            }
            print(f"{model_type} on {dataset_name} with {initializer_name}: Test Accuracy = {test_acc:.4f}")

"""## DataFrame of results"""

# Print results in table format
df_results = pd.DataFrame([
    {
        "Model": model_type,
        "Dataset": dataset_name,
        "Initializer": initializer_name,
        "Validation Accuracy": round(max(result["history"]["val_acc"]), 4) if model_type != "Regression" else "N/A",
        "Test Accuracy": round(result["test_acc"], 4) if model_type != "Regression" else "N/A",
        "Regression MAE": round(result["test_acc"], 4) if model_type == "Regression" else "N/A",
        "Test Loss": round(result["test_loss"], 4),
        "Epochs": len(result["history"]["val_loss"])
    }
    for (model_type, dataset_name, initializer_name), result in results.items()
])

df_results

"""## Visualizing training curves (loss and accuracy)"""

# Function to plot training curves
def plot_training_curves(history, model_type, dataset_name, initializer_name):
    plt.figure(figsize=(12, 5))

    # Plot loss curve
    plt.subplot(1, 2, 1)
    plt.plot(history['loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title(f'Loss Curve - {model_type} on {dataset_name} ({initializer_name})')
    plt.legend()

    # Plot accuracy curve if available
    if 'accuracy' in history:
        plt.subplot(1, 2, 2)
        plt.plot(history['accuracy'], label='Train Accuracy')
        plt.plot(history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.title(f'Accuracy Curve - {model_type} on {dataset_name} ({initializer_name})')
        plt.legend()

    plt.show()

for (model_type, dataset_name, initializer_name), result in results.items():
    plot_training_curves(result["history"], model_type, dataset_name, initializer_name)