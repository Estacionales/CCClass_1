# -*- coding: utf-8 -*-
"""도토리: 충전·구매·선물. 잔액 부족은 거부, 같은 주문(order_id)은 한 번만 처리(멱등).

AC-1~AC-6 전부 구현: 충전+멱등, 구매(잔액검증+인벤토리), 선물(양도), 거래내역(ledger).
충전·구매·선물 모든 증감은 `ledger`에 기록된다.
"""
from dataclasses import dataclass

from server.shared.idem import IdempotencyStore


@dataclass
class AcornResult:
    status: str  # charged | purchased | gifted | rejected
    reason: str = ""
    balance: int = 0
    replay: bool = False


class AcornService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self.balances = {}
        self.inventory = {}  # user -> set(item_id)
        self.ledger = []  # [{"user","type","amount","order_id","balance_after"}]

    def _record(self, user, entry_type, amount, order_id):
        self.ledger.append({
            "user": user, "type": entry_type, "amount": amount,
            "order_id": order_id, "balance_after": self.balances.get(user, 0),
        })

    def ledger_for(self, user):
        """시간(기록)순 거래내역 목록."""
        return [entry for entry in self.ledger if entry["user"] == user]

    def charge(self, user, amount, *, order_id):
        def _charge():
            self.balances[user] = self.balances.get(user, 0) + amount
            self._record(user, "charge", amount, order_id)
            return AcornResult("charged", "ok", balance=self.balances[user])

        result, replay = self.idem.issue_once(f"charge:{order_id}", _charge)
        if replay:
            result = AcornResult("charged", "replay",
                                  balance=self.balances.get(user, 0), replay=True)
        return result

    def purchase(self, user, item_id, price, *, order_id):
        def _purchase():
            balance = self.balances.get(user, 0)
            if balance < price:
                return AcornResult("rejected", "insufficient_balance", balance=balance)
            self.balances[user] = balance - price
            self.inventory.setdefault(user, set()).add(item_id)
            self._record(user, "purchase", -price, order_id)
            return AcornResult("purchased", "ok", balance=self.balances[user])

        result, replay = self.idem.issue_once(f"purchase:{order_id}", _purchase)
        if replay:
            result = AcornResult(result.status, "replay",
                                  balance=result.balance, replay=True)
        return result

    def gift(self, sender, receiver, amount, *, order_id):
        def _gift():
            balance = self.balances.get(sender, 0)
            if balance < amount:
                return AcornResult("rejected", "insufficient_balance", balance=balance)
            self.balances[sender] = balance - amount
            self.balances[receiver] = self.balances.get(receiver, 0) + amount
            self._record(sender, "gift_sent", -amount, order_id)
            self._record(receiver, "gift_received", amount, order_id)
            return AcornResult("gifted", "ok", balance=self.balances[sender])

        result, replay = self.idem.issue_once(f"gift:{order_id}", _gift)
        if replay:
            result = AcornResult(result.status, "replay",
                                  balance=result.balance, replay=True)
        return result
