import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4
NUM_IMAGES = 30000
actual_categories = set()


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")
        # root_dir = "/Users/jbarrameda/Library/CloudStorage/GoogleDrive-jagbarrameda@gmail.com/My Drive/documents/24.03-ai-course-cs50-harvard/l5/traffic/.gtsrb-small"
    else:
        root_dir = sys.argv[1]
    # Get image arrays and labels for all image files
    images, labels = load_data(root_dir)

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    for category in range(0, NUM_CATEGORIES):
        category = str(category)
        sub_dir = os.path.join(data_dir, category)
        if not os.path.isdir(sub_dir):
            continue
        # print("loading dir " + sub_dir)
        for file2 in os.listdir(sub_dir):
            file_path = os.path.join(sub_dir, file2)
            if not os.path.isfile(file_path):
                continue
            images.append(load_image(file_path))
            labels.append(category)
            actual_categories.add(category)
            if len(labels) >= NUM_IMAGES:
                break
        if len(labels) >= NUM_IMAGES:
            break

    return (images, labels)


def load_image(file_path) -> np.ndarray:
    if not os.path.isfile(file_path):
        print(f"Error loading image, file_path is not a file: {file_path}")
    image: np.ndarray = cv2.imread(file_path)
    # resize
    image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
    return image


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential(
        [
            # input layer
            tf.keras.layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
            # convolution layer
            tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
            # Max-pooling layer
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
            # Flatten
            tf.keras.layers.Flatten(),
            # hidden layer with dropout
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            # output layer
            tf.keras.layers.Dense(len(actual_categories), activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    model.summary()
    return model


if __name__ == "__main__":
    main()
