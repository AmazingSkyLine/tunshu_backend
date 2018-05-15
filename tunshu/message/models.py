from django.db import models
from custom_user.models import User

# Create your models here.


class Notification(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_notify', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_notify', on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return 'Notification <{} to {}>'.format(self.from_user, self.to_user)