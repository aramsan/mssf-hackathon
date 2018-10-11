from django.db import models

class Tweet(models.Model):
    id = models.AutoField(primary_key=True)
    status_id = models.BigIntegerField(default = 0,db_index=True)
    screen_name = models.CharField(max_length=128,db_index=True)
    user_id = models.BigIntegerField(default = 0)
    user_name = models.TextField(default = "")
    text = models.TextField()
    created_at = models.DateTimeField(db_index=True)

