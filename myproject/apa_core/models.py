from django.db import models

# Create your models here.
class Embedding(models.Model):
    topic = models.CharField(max_length=255)
    prompt = models.TextField()
    value=models.TextField()
    match_with=models.TextField()
    embedding = models.BinaryField()  # Store the vector as binary

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic