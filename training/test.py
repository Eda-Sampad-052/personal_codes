"""Train an image classifier for human, cat, and dog images."""

from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


DATA_DIR = Path(__file__).parent / "data"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
MODEL_PATH = Path(__file__).parent / "human_dog.keras"


def main():
	if not DATA_DIR.is_dir():
		raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

	train_data = keras.utils.image_dataset_from_directory(
		DATA_DIR,
		validation_split=0.2,
		subset="training",
		seed=123,
		image_size=IMAGE_SIZE,
		batch_size=BATCH_SIZE,
		label_mode="categorical",
	)
	validation_data = keras.utils.image_dataset_from_directory(
		DATA_DIR,
		validation_split=0.2,
		subset="validation",
		seed=123,
		image_size=IMAGE_SIZE,
		batch_size=BATCH_SIZE,
		label_mode="categorical",
	)

	expected = {"human", "dog"}
	if set(train_data.class_names) != expected:
		raise ValueError(
			f"Expected folders named {sorted(expected)}, found {train_data.class_names}"
		)

	autotune = tf.data.AUTOTUNE
	train_data = train_data.prefetch(autotune)
	validation_data = validation_data.prefetch(autotune)

	base_model = keras.applications.MobileNetV2(
		input_shape=(*IMAGE_SIZE, 3), include_top=False, weights="imagenet"
	)
	base_model.trainable = False

	inputs = keras.Input(shape=(*IMAGE_SIZE, 3))
	x = layers.RandomFlip("horizontal")(inputs)
	x = layers.RandomRotation(0.1)(x)
	x = layers.RandomZoom(0.1)(x)
	x = keras.applications.mobilenet_v2.preprocess_input(x)
	x = base_model(x, training=False)
	x = layers.GlobalAveragePooling2D()(x)
	x = layers.Dropout(0.2)(x)
	outputs = layers.Dense(2, activation="softmax")(x)
	model = keras.Model(inputs, outputs)

	model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
	model.fit(
		train_data,
		validation_data=validation_data,
		epochs=EPOCHS,
		callbacks=[keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)],
	)
	model.save(MODEL_PATH)
	print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
	main()
