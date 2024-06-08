import boto3
from botocore.exceptions import NoCredentialsError
from PIL import Image
from io import BytesIO
import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader

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

def get_image_keys(bucket_name, prefix='images/'):
    s3_client = boto3.client('s3')
    keys = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in response.get('Contents', []):
        keys.append(obj['Key'])
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

# Iterar sobre el dataloader
for images in dataloader:
    # Aquí puedes entrenar tu modelo con las imágenes cargadas
    print(images.shape)