# -*- coding: utf-8 -*-
"""도토리: 잔액 부족 거부, 같은 주문(order_id)은 한 번만 결제(멱등), 선물, 거래내역."""


def test_charge_updates_balance(acorn):
    r = acorn.charge("u1", 100, order_id="pay-1")
    assert r.status == "charged" and r.balance == 100


def test_charge_idempotent_same_order(acorn):
    r1 = acorn.charge("u1", 100, order_id="pay-1")
    r2 = acorn.charge("u1", 100, order_id="pay-1")  # 같은 주문 재실행
    assert r2.replay is True
    assert r1.balance == r2.balance == 100  # 중복 충전 없음


def test_purchase_rejected_when_balance_insufficient(acorn):
    acorn.charge("u1", 50, order_id="pay-1")
    r = acorn.purchase("u1", "skin-1", 100, order_id="order-1")
    assert r.status == "rejected" and r.reason == "insufficient_balance"
    assert "skin-1" not in acorn.inventory.get("u1", set())


def test_purchase_succeeds_and_updates_inventory(acorn):
    acorn.charge("u1", 100, order_id="pay-1")
    r = acorn.purchase("u1", "skin-1", 100, order_id="order-1")
    assert r.status == "purchased" and r.balance == 0
    assert "skin-1" in acorn.inventory["u1"]


def test_purchase_idempotent_same_order(acorn):
    acorn.charge("u1", 100, order_id="pay-1")
    r1 = acorn.purchase("u1", "skin-1", 100, order_id="order-1")
    r2 = acorn.purchase("u1", "skin-1", 100, order_id="order-1")  # 같은 주문 재실행
    assert r2.replay is True
    assert acorn.balances["u1"] == 0  # 두 번 차감되지 않음


def test_gift_transfers_balance(acorn):
    acorn.charge("u1", 100, order_id="pay-1")
    r = acorn.gift("u1", "u2", 30, order_id="gift-1")
    assert r.status == "gifted" and r.balance == 70
    assert acorn.balances["u1"] == 70
    assert acorn.balances["u2"] == 30


def test_gift_rejected_when_exceeds_balance(acorn):
    acorn.charge("u1", 20, order_id="pay-1")
    r = acorn.gift("u1", "u2", 30, order_id="gift-1")
    assert r.status == "rejected" and r.reason == "insufficient_balance"
    assert acorn.balances["u1"] == 20
    assert acorn.balances.get("u2", 0) == 0


def test_gift_idempotent_same_order(acorn):
    acorn.charge("u1", 100, order_id="pay-1")
    r1 = acorn.gift("u1", "u2", 30, order_id="gift-1")
    r2 = acorn.gift("u1", "u2", 30, order_id="gift-1")  # 같은 주문 재실행
    assert r2.replay is True
    assert acorn.balances["u1"] == 70  # 두 번 차감되지 않음
    assert acorn.balances["u2"] == 30  # 두 번 지급되지 않음


def test_ledger_records_all_movements(acorn):
    acorn.charge("u1", 100, order_id="pay-1")
    acorn.purchase("u1", "skin-1", 40, order_id="order-1")
    acorn.gift("u1", "u2", 20, order_id="gift-1")

    sender_ledger = acorn.ledger_for("u1")
    assert [e["type"] for e in sender_ledger] == ["charge", "purchase", "gift_sent"]
    assert [e["amount"] for e in sender_ledger] == [100, -40, -20]
    assert sender_ledger[-1]["balance_after"] == 40  # 100 - 40 - 20

    receiver_ledger = acorn.ledger_for("u2")
    assert [e["type"] for e in receiver_ledger] == ["gift_received"]
    assert receiver_ledger[0]["amount"] == 20
