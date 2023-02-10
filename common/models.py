from django.db import models

# Create your models here.


class CommonModel(models.Model):
    # 다른 필드에서 재사용하려고 만드는 모델

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True  # 장고가 DB에 저장하지 말라는 의미
