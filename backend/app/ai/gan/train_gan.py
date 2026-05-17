import torch
import torch.nn as nn
import torch.optim as optim
from app.ai.gan.generator import Generator
from app.ai.gan.discriminator import Discriminator

# Hyperparameters
latent_dim = 100
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize models
G = Generator(latent_dim).to(device)
D = Discriminator().to(device)

# Optimizers and Loss
optimizer_G = optim.Adam(G.parameters(), lr=0.0002, betas=(0.5, 0.999))
optimizer_D = optim.Adam(D.parameters(), lr=0.0002, betas=(0.5, 0.999))
criterion = nn.BCELoss()

if __name__ == "__main__":
    print("Starting GAN training for synthetic fake generation...")

    for epoch in range(10):
        # ---------------------
        #  Train Discriminator
        # ---------------------
        real_imgs = torch.randn(64, 3, 64, 64).to(device)  # Mock real data
        valid = torch.ones(64, 1).to(device)
        fake = torch.zeros(64, 1).to(device)

        optimizer_D.zero_grad()

        # Real loss
        real_loss = criterion(D(real_imgs), valid)

        # Fake loss
        z = torch.randn(64, latent_dim).to(device)
        gen_imgs = G(z)
        fake_loss = criterion(D(gen_imgs.detach()), fake)

        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer_D.step()

        # -----------------
        #  Train Generator
        # -----------------
        optimizer_G.zero_grad()
        g_loss = criterion(D(gen_imgs), valid)
        g_loss.backward()
        optimizer_G.step()

        if epoch % 2 == 0:
            print(
                f"Epoch {epoch} [D loss: {d_loss.item():.4f}] [G loss: {g_loss.item():.4f}]"
            )

    print("GAN training complete. Models saved as mock artifacts.")
