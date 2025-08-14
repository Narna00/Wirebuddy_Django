from django.contrib import admin
from .models import Transaction, CreditCard, Notification
from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount', 'status', 'transaction_type',
        'receiver', 'sender', 'is_anomalous_col', 'anomaly_score'
    ]
    list_editable = ['status', 'transaction_type']
    list_filter = ['is_anomalous', 'status', 'transaction_type', 'date']

    def is_anomalous_col(self, obj):
        if obj.is_anomalous:
            return format_html('<span style="color:red; font-weight:bold;">YES ⚠</span>')
        return format_html('<span style="color:green;">No</span>')
    is_anomalous_col.short_description = "Fraudulent?"


class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'card_type']
    list_display = ['user', 'amount', 'card_type']    
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'amount' ,'date']



admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(Notification, NotificationAdmin)

