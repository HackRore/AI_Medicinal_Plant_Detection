import os
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, models

def test_training_loop():
    print("Testing training loop (TensorFlow)...")
    num_classes = 5
    img_size = (224, 224)
    
    # Create a simple model
    model = models.Sequential([
        layers.Input(shape=(*img_size, 3)),
        layers.Conv2D(16, 3, activation='relu'),
        layers.GlobalAveragePooling2D(),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Create mock data
    num_samples = 4
    x_train = np.random.random((num_samples, *img_size, 3)).astype(np.float32)
    y_train = np.random.randint(0, num_classes, size=(num_samples,))
    
    # Train
    history = model.fit(x_train, y_train, epochs=2, batch_size=2, verbose=1)
    
    print(f"Final loss: {history.history['loss'][-1]}")
    print("Training loop test passed!")

if __name__ == "__main__":
    test_training_loop()
