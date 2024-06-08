import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from PIL import Image
from io import BytesIO
import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim

# Definición del Dataset para S3
class S3Dataset(Dataset):
    def __init__(self, bucket_name, keys, transform=None):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.keys = keys
        self.transform = transform

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, idx):
        key = self.keys[idx]
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            img_data = response['Body'].read()
            img = Image.open(BytesIO(img_data))

            if self.transform:
                img = self.transform(img)

            return img
        except NoCredentialsError:
            print("Credentials not available")
            return None
        except ClientError as e:
            print(f"Client error: {e}")
            return None

# Función para obtener las claves de las imágenes en S3
def get_image_keys(bucket_name, prefix='images/'):
    s3_client = boto3.client('s3')
    keys = []
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        for obj in response.get('Contents', []):
            keys.append(obj['Key'])
    except ClientError as e:
        print(f"Client error: {e}")
    return keys

# Configuración
bucket_name = 'obligatoriomlprodmmmbfm'
keys = get_image_keys(bucket_name)

# Definir transformaciones para las imágenes
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

# Crear dataset y dataloader
dataset = S3Dataset(bucket_name, keys, transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Definición del modelo simple de CNN
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(16 * 64 * 64, 2)  # Assuming binary classification

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = x.view(-1, 16 * 64 * 64)
        x = self.fc1(x)
        return x

model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Suponiendo que tienes etiquetas predefinidas para cada imagen
# Aquí solo se usan etiquetas de ejemplo
# Debes reemplazar esto con tus etiquetas reales
example_labels = [0] * 32 + [1] * 4  # Ejemplo de etiquetas, ajusta esto según tu dataset

# Función para obtener las etiquetas correspondientes a cada lote
def get_labels(batch_size):
    return torch.tensor(example_labels[:batch_size])

# Ciclo de entrenamiento
num_epochs = 10
for epoch in range(num_epochs):
    running_loss = 0.0
    for i, inputs in enumerate(dataloader):
        labels = get_labels(inputs.size(0))  # Obtén las etiquetas correspondientes
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        if i % 10 == 9:  # Imprimir cada 10 mini-lotes
            print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 10:.3f}")
            running_loss = 0.0

print('Finished Training')

