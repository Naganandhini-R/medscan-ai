FROM python:3.11-slim

WORKDIR /ai

RUN pip install torch torchvision matplotlib scikit-learn pillow opencv-python-headless

COPY train ./train

CMD ["python", "train/train_siamese.py"]
