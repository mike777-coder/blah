# -*- coding: utf-8 -*-
"""ic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xD9D96nCKJyyOABoNwexZmA_sqxpD0_2
"""

import numpy as np
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Add

# Load Pre-trained VGG16 Model
vgg = VGG16(weights='imagenet', include_top=False)
model_vgg = Model(inputs=vgg.input, outputs=vgg.layers[-1].output)

# Simplified Feature Extraction
def extract_features(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    features = model_vgg.predict(image)
    return features.flatten()

# Image Paths and Captions
images = ["1.jpg", "2.jpg", "3.jpg", "4.jpg"]
captions = [
    "A dog running on grass",
    "A cat sitting on a table",
    "A car driving on a road",
    "A person riding a bicycle"
]

# Extract Features for Images
image_features = np.array([extract_features(img) for img in images])

# Tokenize Captions
tokenizer = Tokenizer()
tokenizer.fit_on_texts(captions)
tokenized_captions = tokenizer.texts_to_sequences(captions)
vocab_size = len(tokenizer.word_index) + 1
max_length = max(len(cap) for cap in tokenized_captions)

# Pad Captions and Convert to NumPy Array
tokenized_captions = pad_sequences(tokenized_captions, maxlen=max_length, padding='post')
tokenized_captions = np.array(tokenized_captions)

# Prepare Inputs and Outputs
X_images = np.repeat(image_features, max_length - 1, axis=0)
X_captions = pad_sequences(tokenized_captions[:, :-1].flatten().reshape(-1, 1), maxlen=1)
y = tokenized_captions[:, 1:].flatten()

# Define the Encoder-Decoder Model
image_input = Input(shape=(X_images.shape[1],))
image_dense = Dense(256, activation='relu')(image_input)

caption_input = Input(shape=(1,))
caption_embedding = Embedding(vocab_size, 256)(caption_input)
caption_lstm = LSTM(256)(caption_embedding)

combined = Add()([image_dense, caption_lstm])
output = Dense(vocab_size, activation='softmax')(combined)

model = Model(inputs=[image_input, caption_input], outputs=output)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Train the Model
model.fit([X_images, X_captions], y, epochs=5, verbose=1)

# Generate Caption for an Image
def generate_caption(image_path):
    features = extract_features(image_path).reshape(1, -1)
    caption = []
    for _ in range(max_length - 1):
        seq = pad_sequences([caption], maxlen=1)
        pred = model.predict([features, seq], verbose=0)
        word = tokenizer.index_word.get(np.argmax(pred), '<end>')
        if word == '<end>':
            break
        caption.append(np.argmax(pred))
    return ' '.join(tokenizer.index_word[i] for i in caption)

# Test with a New Image
print("Generated Caption:", generate_caption("2.jpg"))

