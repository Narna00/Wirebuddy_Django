import requests
import uuid
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Transaction
from account.models import Account

# Use the key from settings if set there, else fallback (not recommended for prod)
PAYSTACK_SECRET_KEY = getattr(settings, "PAYSTACK_SECRET_KEY",
                              "sk_test_db3ef49c1f56e6a6891a8d6ed871f16e31485f3c")

@login_required
def DepositAmountView(request):
    if request.method == "POST":
        # 1) Validate amount input
        raw = request.POST.get("amount")
        try:
            amount = Decimal(raw)
            assert amount > 0
        except:
            messages.warning(request, "Enter a valid amount.")
            return redirect("core:deposit")

        # 2) Create a pending transaction record
        txn = Transaction.objects.create(
            user=request.user,
            amount=amount,
            description=request.POST.get("description", "") or "Paystack Deposit",
            sender=None,
            receiver=request.user,
            sender_account=None,
            receiver_account=request.user.account,
            transaction_type="deposit",
            status="initiated",
            transaction_id=uuid.uuid4()
        )

        # 3) Initialize Paystack payment
        init_data = {
            "email": request.user.email,
            "amount": int(amount * 100),  # kobo
            "reference": str(txn.transaction_id),
            "callback_url": request.build_absolute_uri(
                f"/deposit/verify/{txn.transaction_id}/"
            ),
        }
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post("https://api.paystack.co/transaction/initialize",
                             json=init_data, headers=headers)
        js = resp.json()

        if resp.status_code == 200 and js.get("status"):
            return redirect(js["data"]["authorization_url"])
        messages.error(request, "Could not start payment. Try again.")
        return redirect("core:deposit")

    # GET → show form
    return render(request, "deposit/deposit.html")


@login_required
def verify_deposit(request, transaction_id):
    # 1) Lookup the initiated transaction
    try:
        txn = Transaction.objects.get(transaction_id=transaction_id, status="initiated")
    except Transaction.DoesNotExist:
        messages.error(request, "Invalid or already processed transaction.")
        return redirect("core:transactions")

    # 2) Verify with Paystack
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    resp = requests.get(
        f"https://api.paystack.co/transaction/verify/{txn.transaction_id}/",
        headers=headers,
    )
    js = resp.json()

    if js.get("status") and js["data"].get("status") == "success":
        txn.status = "completed"
        txn.save()
        acct = txn.receiver_account
        acct.account_balance += txn.amount
        acct.save()

        messages.success(request, f"Deposit of ₵{txn.amount} successful!")
        return redirect("core:deposit-completed", transaction_id=txn.transaction_id)

    messages.error(request, "Payment failed or not verified.")
    return redirect("core:deposit")


@login_required
def deposit_completed(request, transaction_id):
    txn = Transaction.objects.get(transaction_id=transaction_id)
    return render(request, "deposit/deposit-completed.html", {"transaction": txn})
