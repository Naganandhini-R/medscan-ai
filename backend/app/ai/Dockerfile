FROM python:3.11-slim

WORKDIR /ai

RUN pip install torch torchvision matplotlib scikit-learn pillow opencv-python-headless

# We expect the context to be backend root or volume mounted
ENV PYTHONPATH=/ai

CMD ["python", "-m", "app.ai.train.train_siamese"]
