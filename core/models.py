from django.db import models
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from account.models import Account
# Create your models here.



TRANSACTION_TYPE = (
    ("transfer", "Transfer"),
    ("Received", "Received"),
    ("withdraw", "withdraw"),
    ("refund", "Refund"),
    ("request", "Payment Request"),
    ("none", "None")
)

TRANSACTION_STATUS = (
    ("failed", "failed"),
    ("completed", "completed"),
    ("pending", "pending"),
    ("processing", "processing"),
    ("request_sent", "request_sent"),
    ("request_settled", "request settled"),
    ("request_processing", "request processing"),

)



CARD_TYPE = (
    ("master", "master"),
    ("visa", "visa"),
    ("verve", "verve"),

)


NOTIFICATION_TYPE = (
    ("None", "None"),
    ("Transfer", "Transfer"),
    ("Credit Alert", "Credit Alert"),
    ("Debit Alert", "Debit Alert"),
    ("Sent Payment Request", "Sent Payment Request"),
    ("Received Payment Request", "Received Payment Request"),
    ("Funded Credit Card", "Funded Credit Card"),
    ("Withdrew Credit Card Funds", "Withdrew Credit Card Funds"),
    ("Deleted Credit Card", "Deleted Credit Card"),
    ("Added Credit Card", "Added Credit Card"),

)

class Transaction(models.Model):
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1000, null=True, blank=True)

    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="receiver")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")

    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="receiver_account")
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sender_account")

    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending")
    transaction_type = models.CharField(max_length=100, default="Online")  # e.g. ATM Withdrawal, POS, Bank Transfer

    # ======================
    # ML model-specific fields
    # ======================
    ip_flag = models.BooleanField(default=False)
    device_type = models.CharField(max_length=50, default="Mobile")  # e.g. Mobile, Laptop, Tablet
    location = models.CharField(max_length=100, default="Accra")  # e.g. London, Mumbai
    merchant_category = models.CharField(max_length=50, default="Groceries")  # e.g. Clothing, Electronics
    failed_txn_count_7d = models.IntegerField(default=0)
    card_type = models.CharField(max_length=50, default="Visa")  # e.g. Visa, Mastercard
    auth_method = models.CharField(max_length=50, default="PIN")  # e.g. OTP, Biometric
    txn_distance = models.FloatField(default=0.0)  # Geo distance
    risk_score = models.FloatField(default=0.5)  # Risk score
    is_weekend = models.BooleanField(default=False)  # Sat/Sun flag
    previous_fraudulent_activity = models.BooleanField(default=False)  # From history
    daily_txn_count = models.IntegerField(default=0)  # Daily transaction count
    avg_txn_amount_7d = models.FloatField(default=0.0)  # Avg txn amount in last 7 days
    card_age = models.IntegerField(default=0)  # Age of card in days

    # ======================
    # Fraud detection output
    # ======================
    is_anomalous = models.BooleanField(default=False)
    anomaly_score = models.FloatField(null=True, blank=True)
    anomaly_reason = models.TextField(null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set weekend flag
        if self.date:
            self.is_weekend = self.date.weekday() in [5, 6]  # Saturday or Sunday
        super().save(*args, **kwargs)

    def __str__(self):
        try:
            return f"{self.user}"
        except:
            return f"Transaction"





class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_id = ShortUUIDField(unique=True, length=5, max_length=20, prefix="CARD", alphabet="1234567890")

    name = models.CharField(max_length=100)
    number = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    cvv = models.IntegerField()

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    card_type = models.CharField(choices=CARD_TYPE, max_length=20, default="master")
    card_status = models.BooleanField(default=True)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"
    


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE, default="none")
    amount = models.IntegerField(default=0)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    nid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Notification"

    def __str__(self):
        return f"{self.user} - {self.notification_type}"    
    
from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date, timedelta

class SavingsGoal(models.Model):
    CATEGORY_CHOICES = [
        ("Travel", "Travel"),
        ("Emergency Fund", "Emergency Fund"),
        ("Education", "Education"),
        ("Investment", "Investment"),
        ("Other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)

    def amount_left(self):
        return max(Decimal("0.00"), self.target_amount - self.current_amount)

    def progress_percentage(self):
        if self.target_amount > 0:
            return min(100, (self.current_amount / self.target_amount) * 100)
        return 0

    def days_left(self):
        return max((self.deadline - date.today()).days, 0)

    def daily_saving_needed(self):
        days_left = self.days_left()
        if days_left > 0:
            return self.amount_left() / days_left
        return self.amount_left()

    def projected_completion_date(self):
        """Predicts when the goal will be completed based on current savings rate."""
        days_since_start = (date.today() - self.date_created.date()).days
        if days_since_start <= 0 or self.current_amount <= 0:
            return None
        daily_rate = self.current_amount / days_since_start
        if daily_rate <= 0:
            return None
        days_needed = self.amount_left() / daily_rate
        return date.today() + timedelta(days=int(days_needed))

    def is_falling_behind(self):
        """Checks if user is depositing less than needed daily."""
        days_left = self.days_left()
        if days_left <= 0:
            return True
        avg_daily_needed = self.amount_left() / days_left
        days_since_start = max((date.today() - self.date_created.date()).days, 1)
        avg_daily_saved = self.current_amount / days_since_start
        return avg_daily_saved < avg_daily_needed

    def __str__(self):
        return f"{self.name} - {self.user}"
