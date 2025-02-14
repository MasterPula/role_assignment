from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Week(models.Model):
    week_number = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Settimana {self.week_number}"

class Assignment(models.Model):
    ROLE_CHOICES = [(i, f"Ruolo {i}") for i in range(1, 6)]
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='assignments')
    role = models.IntegerField(choices=ROLE_CHOICES)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.week} - Ruolo {self.role}: {self.person}"
